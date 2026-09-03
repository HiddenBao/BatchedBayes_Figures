from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from BayesianOptimization.args import define_parser
from BayesianOptimization.applications import get_app_class
from BayesianOptimization.acq_func import get_choice_function
from BayesianOptimization.debug_utils import verify_dimensions_simple
from BayesianOptimization.mesh_utils import (
    eval_surrogate,
    select_top_categories,
    build_fine_mesh_per_winner,
    build_coarse_mesh,
    build_category_matrix,
    compute_acquisition
)
from BayesianOptimization.qmc import generate_qmc_normal
from BayesianOptimization.surrogate_models.get_surrogate import get_surrogate_model
from BayesianOptimization.batch_selection import get_batch_selector

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Type aliases
# -----------------------------------------------------------------------------

DatasetBundle = tuple[np.ndarray, np.ndarray]

# -----------------------------------------------------------------------------
# Argument-dependent initialization
# -----------------------------------------------------------------------------

def initialize(args: Any) -> tuple[Any, np.random.Generator, Any]:
    """Initialize the application, random generator, and derived args flags.

    Args:
        args: Parsed CLI namespace with application_class and seed fields.

    Returns:
        Tuple of (application, rng, args) with minimize_objective,
        output_dimensions, and need_qmc populated on args.
    """
    application = get_app_class(args.application_class)
    rng = np.random.default_rng(args.seed)

    args.minimize_objective = application.minimize_objective
    args.output_dimensions = application.get_output_dims()
    args.need_qmc = True

    return application, rng, args


# -----------------------------------------------------------------------------
# Dataset I/O
# -----------------------------------------------------------------------------

def load_dataset(
        application: Any,
        args: Any,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Load training data and compute the current best objective value.

    Args:
        application: Application object with get_dataset and
            objective_function methods.
        args: Experiment configuration namespace.

    Returns:
        Tuple of (inputs, outputs, current_best) where inputs has shape
        (n_train, d), outputs has shape (n_train, n_outputs), and
        current_best is the best objective observed so far.
    """
    inputs, outputs = map(np.asarray, application.get_dataset())
    objectives = application.objective_function(outputs, args)

    fixed = getattr(application, "fixed_categories", {})
    if fixed:
        raw_data = application.get_raw_data()
        campaign_mask = np.ones(len(raw_data), dtype=bool)
        for col, val in fixed.items():
            campaign_mask &= (raw_data[col].astype(str) == str(val)).values
        campaign_objectives = objectives[campaign_mask]
        if campaign_objectives.size > 0:
            best = campaign_objectives.min() if application.minimize_objective else campaign_objectives.max()
        else:
            best = objectives.min() if application.minimize_objective else objectives.max()
    else:
        best = objectives.min() if application.minimize_objective else objectives.max()

    return inputs, outputs, best


# -----------------------------------------------------------------------------
# Surrogate model fit
# -----------------------------------------------------------------------------

def train_surrogate(
        inputs: np.ndarray,
        outputs: np.ndarray,
        args: Any,
        rng: np.random.Generator,
        application: Any,
) -> Any:
    """Train the surrogate model on the current dataset.

    Args:
        inputs: Training input array, shape (n_train, d).
        outputs: Training output array, shape (n_train, n_outputs).
        args: Experiment configuration namespace.
        rng: NumPy random generator for surrogate initialisation.
        application: Application object passed to get_surrogate_model.

    Returns:
        Fitted surrogate model with predict and predict_std methods.
    """
    model = get_surrogate_model(args, rng, application)
    model.fit(inputs, outputs)

    return model


# -----------------------------------------------------------------------------
# Batch / serial proposal
# -----------------------------------------------------------------------------

def propose_batch(
        fine_inputs: np.ndarray,
        acq_fine: np.ndarray,
        mu_fine: np.ndarray,
        sigma_fine: np.ndarray,
        current_best: float,
        model: Any,
        args: Any,
        rng: np.random.Generator,
        application: Any,
        x_train: np.ndarray,
) -> np.ndarray:
    """Propose a batch of candidate inputs from the fine mesh.

    Args:
        fine_inputs: Fine mesh candidate array, shape (n_fine, d).
        acq_fine: Acquisition values over fine candidates,
            shape (n_fine,).
        mu_fine: Surrogate means over fine candidates,
            shape (n_fine, n_outputs).
        sigma_fine: Surrogate stds over fine candidates,
            shape (n_fine, n_outputs).
        current_best: Current best observed objective value.
        model: Fitted surrogate model.
        args: Experiment configuration namespace.
        rng: NumPy random generator.
        application: Application object.
        x_train: Current training inputs, shape (n_train, d).

    Returns:
        Selected input array of shape (batch_size, d).
    """
    batch_selector = get_batch_selector(args.batch_method)

    categories, _, combos = build_category_matrix(application)
    if hasattr(application, "continuous_headers"):
        d_cont = len(application.continuous_headers)
    else:
        d_cont = fine_inputs.shape[1] - categories.shape[1]

    choice_function = get_choice_function(
        args.choice_method, args.surrogate_model_type,
        args.surrogate_model_target, application, args=args,
    )

    batch_result = batch_selector.select_batch(
        fine_inputs=fine_inputs,
        acq_fine=acq_fine,
        model=model,
        args=args,
        application=application,
        categories=categories,
        x_train=x_train,
        choice_function=choice_function,
        current_best=current_best,
        rng=rng,
        d_cont=d_cont,
        mu_fine=mu_fine,
        sigma_fine=sigma_fine,
        combos=combos,
    )

    return batch_result.selected_inputs


# -----------------------------------------------------------------------------
# Write CSV
# -----------------------------------------------------------------------------

def write_results(
        selected_inputs: np.ndarray,
        model: Any,
        application: Any,
        args: Any,
) -> None:
    """Write the proposed batch to CSV.

    The output filename is ``results_linear_{api_suffix}.csv`` where
    ``api_suffix`` is taken from ``application.fixed_categories["API_Name"]``,
    falling back to ``"all"`` when that key is absent (or the attribute is
    missing/None). This keeps A190 and Fenofibrate branch runs from
    overwriting each other.

    Args:
        selected_inputs: Selected input array, shape (batch_size, d).
        model: Fitted surrogate model with predict method.
        application: Application object with input_headers,
            output_headers, objective_function, and unscale_input.
        args: Experiment configuration namespace with output_dir.
    """
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    fixed = getattr(application, "fixed_categories", {}) or {}
    api_suffix = fixed.get("API_Name", "all")
    out_path = Path(args.output_dir) / f"results_linear_{api_suffix}.csv"

    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            application.input_headers + application.output_headers
            + ["Objective Function"]
        )
        for point in selected_inputs:
            output = model.predict(point.reshape(1, -1))[0]
            objective = application.objective_function(
                output.reshape(1, -1), args,
            )[0]
            unscaled = application.unscale_input(point)
            writer.writerow(np.concatenate([unscaled, output, [objective]]))

    logger.info("Saved %d proposal(s) to %s", len(selected_inputs), out_path)


# -----------------------------------------------------------------------------
# Phase helpers
# -----------------------------------------------------------------------------


def _run_coarse_phase(
        model: Any,
        categories: np.ndarray,
        d_cont: int,
        args: Any,
        rng: np.random.Generator,
        application: Any,
        current_best: float,
        combos: pd.DataFrame | None = None,
) -> tuple[np.ndarray, np.ndarray | None, Any, list]:
    """Run the coarse mesh evaluation and return data for the fine phase.

    Builds the coarse Cartesian-product candidate mesh, evaluates the
    surrogate, generates QMC samples, computes acquisition values, and
    selects the top-K categories.

    Args:
        model: Fitted surrogate model.
        categories: One-hot (+ descriptor) category matrix,
            shape (n_categories, d_cat).
        d_cont: Number of continuous input dimensions.
        args: Experiment configuration namespace.
        rng: NumPy random generator.
        application: Application object.
        current_best: Current best observed objective value.

    Returns:
        Tuple of (coarse_input, qmc, choice_fn, winners) where
        coarse_input has shape (n_coarse, d), qmc is an array of shape
        (n_qmc, n_outputs) or None, choice_fn is the acquisition
        function callable, and winners is the list returned by
        select_top_categories.
    """
    logger.debug(
        "Coarse mesh — cat+desc=%s, d_cont=%d, total=%d",
        categories.shape, d_cont, categories.shape[1] + d_cont,
    )
    coarse_input, cat_idx, cont_pts = build_coarse_mesh(
        categories, args, d_cont, application, combos=combos,
    )
    mu_coarse, sigma_coarse = eval_surrogate(model, coarse_input)

    qmc = None
    if args.need_qmc:
        qmc = generate_qmc_normal(args.qmc_samples, args.output_dimensions, rng)
        logger.debug("QMC shape: %s", qmc.shape)

    choice_fn = get_choice_function(
        args.choice_method, args.surrogate_model_type,
        args.surrogate_model_target, application, args=args,
    )
    acq_coarse = compute_acquisition(
        choice_fn, coarse_input, mu_coarse, sigma_coarse,
        current_best, args, rng, application, qmc_samples=qmc,
    )
    winners = select_top_categories(
        acq_coarse,
        cat_indices=cat_idx,
        cont_points=cont_pts,
        top_k=args.top_k_categories,
    )
    return coarse_input, qmc, choice_fn, winners


def _run_fine_phase(
        model: Any,
        winners: list,
        categories: np.ndarray,
        args: Any,
        x_train: np.ndarray,
        rng: np.random.Generator,
        application: Any,
        current_best: float,
        choice_fn: Any,
        qmc: np.ndarray | None,
        combos: pd.DataFrame | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Run the fine mesh evaluation and return data for batch selection.

    Builds fine meshes around winning categories, evaluates the surrogate,
    and computes acquisition values.

    Args:
        model: Fitted surrogate model.
        winners: Top-K category list from select_top_categories.
        categories: One-hot (+ descriptor) category matrix.
        args: Experiment configuration namespace.
        x_train: Current training inputs, shape (n_train, d).
        rng: NumPy random generator.
        application: Application object.
        current_best: Current best observed objective value.
        choice_fn: Acquisition function callable.
        qmc: QMC normal samples, or None.
        combos: Raw category DataFrame from build_category_matrix; forwarded
            to build_fine_mesh_per_winner for per-ingredient bounds enforcement.

    Returns:
        Tuple of (fine_input, mu_fine, sigma_fine, acq_fine).
    """
    fine_input = build_fine_mesh_per_winner(
        winners, categories, args, x_train, application, combos=combos,
    )
    mu_fine, sigma_fine = eval_surrogate(model, fine_input)
    acq_fine = compute_acquisition(
        choice_fn, fine_input, mu_fine, sigma_fine,
        current_best, args, rng, application, qmc_samples=qmc,
    )
    return fine_input, mu_fine, sigma_fine, acq_fine


# -----------------------------------------------------------------------------
# Top-level driver
# -----------------------------------------------------------------------------


def main() -> None:
    """Main function to run the linear optimization."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )
    args = define_parser().parse_args()

    application, rng, args = initialize(args)
    x_train, y_train, current_best = load_dataset(application, args)
    logger.debug("Training inputs shape: %s", x_train.shape)

    model = train_surrogate(x_train, y_train, args, rng, application)

    categories, _, combos = build_category_matrix(application)
    d_cont = (
        len(application.continuous_headers)
        if hasattr(application, "continuous_headers")
        else x_train.shape[1] - categories.shape[1]
    )

    coarse_input, qmc, choice_fn, winners = _run_coarse_phase(
        model, categories, d_cont, args, rng, application, current_best,
        combos=combos,
    )
    fine_input, mu_fine, sigma_fine, acq_fine = _run_fine_phase(
        model, winners, categories, args, x_train, rng, application,
        current_best, choice_fn, qmc, combos=combos,
    )
    verify_dimensions_simple(x_train, coarse_input, fine_input)

    selected_inputs = propose_batch(
        fine_input, acq_fine, mu_fine, sigma_fine, current_best,
        model, args, rng, application, x_train,
    )
    write_results(selected_inputs, model, application, args)

    for point in selected_inputs:
        predicted_target = model.predict(point.reshape(1, -1))
        predicted_std = model.predict_std(point.reshape(1, -1))
        predicted_objective = application.objective_function(predicted_target, args)
        logger.info(
            "Proposal — scaled=%s unscaled=%s target=%s std=%s obj=%s",
            point, application.unscale_input(point),
            predicted_target, predicted_std, predicted_objective,
        )


if __name__ == "__main__":
    main()
