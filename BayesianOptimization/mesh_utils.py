from __future__ import annotations

import itertools
import logging
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from BayesianOptimization.utils import get_inputs_grid, remove_existing_training

logger = logging.getLogger(__name__)


def remove_nearby_matches(
        candidates: np.ndarray,
        training_data: np.ndarray | None,
        d_cont: int,
        threshold: float = 0.075,
) -> np.ndarray:
    """Drop candidates near any training point (same combo + L_inf close).

    A candidate is dropped iff there exists a training point with:
      * an identical categorical+descriptor block (every column except
        the last ``d_cont``), and
      * every continuous dim within ``threshold`` in absolute value (L_inf
        / Chebyshev distance).

    The continuous block is assumed to live in [0, 1] scaled space, so
    ``threshold=0.075`` means "within 7.5 % of the global range on every
    continuous dim". Different categorical combos always count as 'far';
    descriptors are deterministic from categories, so a combo mismatch
    implies a cat+desc-block mismatch and the candidate is automatically
    kept against that training row.

    Args:
        candidates: Candidate points array, shape (n_candidates, d_total),
            where d_total = d_cat_desc + d_cont and the continuous block
            occupies the last ``d_cont`` columns.
        training_data: Existing training points, shape (n_train, d_total),
            or None.
        d_cont: Number of continuous dimensions (last d_cont columns of
            each row).
        threshold: L_inf threshold on the continuous block. Default 0.075
            (7.5 % of the [0, 1] scaled global range).

    Returns:
        Filtered candidates array with nearby training duplicates removed.
    """
    if training_data is None or training_data.shape[0] == 0:
        return candidates

    n_cand = len(candidates)
    if n_cand == 0:
        return candidates

    cat_cand = candidates[:, :-d_cont]
    cont_cand = candidates[:, -d_cont:]
    cat_train = training_data[:, :-d_cont]
    cont_train = training_data[:, -d_cont:]

    logger.debug(
        "Checking %d candidates against %d training points "
        "(d_cont=%d, threshold=%.4f).",
        n_cand, len(training_data), d_cont, threshold,
    )

    keep_mask = np.ones(n_cand, dtype=bool)
    for j in range(len(training_data)):
        combo_match = np.all(cat_cand == cat_train[j], axis=1)
        if not combo_match.any():
            continue
        cont_close = np.max(np.abs(cont_cand - cont_train[j]), axis=1) <= threshold
        keep_mask &= ~(combo_match & cont_close)

    filtered = candidates[keep_mask]
    logger.debug(
        "Removed %d nearby duplicates; %d candidates remain.",
        n_cand - len(filtered), len(filtered),
    )
    return filtered


def generate_isotropic_coarse_candidates(
        categories: np.ndarray,
        mesh_size: int,
        d_cont: int,
        application: Any | None = None,
        per_cat_cont_bounds: list[list[tuple[float, float]]] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate the Cartesian-product coarse candidate mesh.

    Args:
        categories: One-hot (+ descriptor) encoded category matrix,
            shape (n_categories, d_cat).
        mesh_size: Number of grid points per continuous dimension.
        d_cont: Number of continuous input dimensions.
        application: Application object (reserved for future use).
        per_cat_cont_bounds: Optional list of length n_categories. Each
            element is a list of (lo, hi) tuples in [0, 1] scaled space,
            one per continuous dimension. When provided, candidates are
            filtered to rows where each continuous dim d satisfies
            lo <= x[d] <= hi. Dimensions without per-component bounds
            should use (0.0, 1.0).

    Returns:
        Tuple of (coarse_inputs, cat_indices, cont_points) where
        coarse_inputs has shape (n_points, d_cat + d_cont),
        cat_indices has shape (n_points,), and cont_points
        has shape (n_points, d_cont).
    """
    num_categories, d_cat = categories.shape
    total_dims = d_cat + d_cont

    logger.debug(
        "Coarse mesh — categories+descriptors shape: %s", categories.shape,
    )
    cont_mesh = get_inputs_grid(mesh_size, d_cont)

    coarse_inputs_list = []
    cat_indices_list = []
    cont_points_list = []

    for ci in range(num_categories):
        c_enc = categories[ci]

        if per_cat_cont_bounds is not None:
            valid = np.ones(len(cont_mesh), dtype=bool)
            for dim, (lo, hi) in enumerate(per_cat_cont_bounds[ci]):
                valid &= (cont_mesh[:, dim] >= lo) & (cont_mesh[:, dim] <= hi)
            cat_cont = cont_mesh[valid]
        else:
            cat_cont = cont_mesh

        n = len(cat_cont)
        cat_block = np.zeros((n, total_dims))
        cat_block[:, :d_cat] = c_enc
        cat_block[:, d_cat:] = cat_cont
        coarse_inputs_list.append(cat_block)
        cat_indices_list.append(np.full(n, ci, dtype=int))
        cont_points_list.append(cat_cont)

    coarse_inputs = np.vstack(coarse_inputs_list)
    cat_indices = np.concatenate(cat_indices_list)
    cont_points = np.vstack(cont_points_list)

    logger.debug("Coarse mesh size: %s", coarse_inputs.shape)

    return coarse_inputs, cat_indices, cont_points


def generate_isotropic_fine_mesh(
        x_center: np.ndarray,
        mesh_size: int,
        fine_mesh_size: int,
        training_data: np.ndarray | None = None,
        cont_bounds: list[tuple[float, float]] | None = None,
) -> np.ndarray:
    """Generate an isotropic fine mesh around a continuous center point.

    The fine mesh spans ±1/(mesh_size-1) in each dimension around
    x_center, clipped to per-ingredient bounds (or [0, 1] globally),
    with duplicates removed.

    Args:
        x_center: Continuous center point, shape (d_cont,).
        mesh_size: Coarse grid size; controls the half-width of the
            fine window.
        fine_mesh_size: Number of fine grid points per dimension.
        training_data: Existing training inputs to exclude, or None.
        cont_bounds: Optional per-dimension bounds as a list of (lo, hi)
            tuples in [0, 1] scaled space. When provided, each dimension
            is clipped to its own [lo, hi] instead of the global [0, 1].
            Asymmetric windows near boundaries are accepted as correct.

    Returns:
        Fine mesh array of shape (n_fine, d_cont), values within bounds.
    """
    d_cont = x_center.shape[0]

    unit_fine = get_inputs_grid(fine_mesh_size, d_cont)

    fine_mesh = (unit_fine - 0.5) / (mesh_size - 1) + x_center

    if cont_bounds is not None:
        for dim, (lo, hi) in enumerate(cont_bounds):
            fine_mesh[:, dim] = np.clip(fine_mesh[:, dim], lo, hi)
    else:
        fine_mesh = np.clip(fine_mesh, 0.0, 1.0)

    fine_mesh = np.unique(fine_mesh, axis=0)

    if training_data is not None and training_data.shape[0] > 0:
        fine_mesh = remove_existing_training(fine_mesh, training_data)

    return fine_mesh


def eval_surrogate(
        model: Any,
        X: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate the surrogate model and return predictions and uncertainties.

    Args:
        model: Trained surrogate model with predict and predict_std
            methods.
        X: Input array of shape (n_candidates, d).

    Returns:
        Tuple of (mu, sigma) where mu is the predicted mean array of
        shape (n_candidates, n_outputs) and sigma is the predicted
        std array of the same shape.
    """
    mu = model.predict(X)
    sigma = model.predict_std(X)

    return mu, sigma


def select_top_categories(
        acq_coarse: np.ndarray,
        cat_indices: np.ndarray,
        cont_points: np.ndarray,
        top_k: int,
) -> list[tuple[int, int, float, np.ndarray]]:
    """Select the top-K categories by their best acquisition score.

    Acquisition scores are assumed to be oriented for maximisation
    before reaching this function — components-based functions
    pre-negate scores for minimisation objectives.

    Args:
        acq_coarse: Acquisition values for every coarse candidate,
            shape (n_candidates,).
        cat_indices: Category index for each coarse candidate,
            shape (n_candidates,).
        cont_points: Continuous coordinates for each coarse candidate,
            shape (n_candidates, d_cont).
        top_k: Number of top categories to return.

    Returns:
        List of (cat_id, global_idx, acq_val, cont_pt) tuples,
        sorted descending by acq_val, length min(top_k, n_categories).
    """
    if cat_indices.size == 0:
        best_idx = int(acq_coarse.argmax())
        return [(0, best_idx, acq_coarse[best_idx], cont_points[best_idx])]

    num_cats = int(cat_indices.max()) + 1
    best = []
    for ci in range(num_cats):
        mask = cat_indices == ci
        if not mask.any():
            continue
        sub = acq_coarse[mask]
        loc = int(sub.argmax())
        global_idx = np.nonzero(mask)[0][loc]
        best.append((ci, global_idx, acq_coarse[global_idx], cont_points[global_idx]))

    best.sort(key=lambda t: t[2], reverse=True)

    for rank, (cat_id, global_idx, acq_val, cont_pt) in enumerate(best, 1):
        cont_str = ', '.join(f"{v:.4f}" for v in cont_pt)
        logger.debug(
            "Category rank %d: cat_id=%d acq=%.6f cont=[%s]",
            rank, cat_id, acq_val, cont_str,
        )

    logger.info(
        "Top %d categories selected: %s",
        top_k, [b[0] for b in best[:top_k]],
    )

    return best[:top_k]


_RANGES_MAP: dict[str, tuple[str, str]] = {
    "Oil_V":          ("Oil",          "oil_v_ranges"),
    "Surfactant_V":   ("Surfactant",   "surfactant_v_ranges"),
    "Cosurfactant_V": ("Cosurfactant", "cosurfactant_v_ranges"),
}


def _get_cont_bounds_for_combo(
        row: pd.Series,
        application: Any,
) -> list[tuple[float, float]]:
    """Return scaled [0, 1] bounds for each continuous dimension for one combo.

    Args:
        row: A single row from the combos DataFrame (one category combination).
        application: Application object with continuous_headers, ranges, and
            optional per-ingredient range dicts (oil_v_ranges, etc.).

    Returns:
        List of (lo, hi) tuples in [0, 1] scaled space, one per continuous
        dimension. Dimensions without a per-ingredient override use (0.0, 1.0).
    """
    bounds: list[tuple[float, float]] = []
    for header in application.continuous_headers:
        lo, hi = 0.0, 1.0
        if header in _RANGES_MAP:
            combo_col, ranges_attr = _RANGES_MAP[header]
            per_ranges = getattr(application, ranges_attr, None)
            if per_ranges and combo_col in row.index:
                component = row[combo_col]
                if component in per_ranges:
                    g_lo, g_hi = application.ranges[header]
                    p_lo, p_hi = per_ranges[component]
                    lo = (p_lo - g_lo) / (g_hi - g_lo)
                    hi = (p_hi - g_lo) / (g_hi - g_lo)
        bounds.append((lo, hi))
    return bounds


def build_coarse_mesh(
        categories: np.ndarray,
        args: Any,
        d_cont: int,
        application: Any | None = None,
        combos: pd.DataFrame | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate coarse candidates from categories and continuous dimensions.

    Args:
        categories: One-hot (+ descriptor) category matrix,
            shape (n_categories, d_cat).
        args: Experiment configuration namespace; must have mesh_size.
        d_cont: Number of continuous input dimensions.
        application: Application object; used to read per-component range
            dicts if present. Must have continuous_headers and ranges attrs.
        combos: Raw category DataFrame returned by build_category_matrix,
            shape (n_categories, n_cat_headers). Required for per-component
            bounds.

    Returns:
        Tuple of (coarse_inputs, cat_indices, cont_points) as returned
        by generate_isotropic_coarse_candidates.
    """
    per_cat_cont_bounds = None

    if (
        combos is not None
        and application is not None
        and hasattr(application, 'continuous_headers')
    ):
        per_cat_cont_bounds = [
            _get_cont_bounds_for_combo(row, application)
            for _, row in combos.iterrows()
        ]

    return generate_isotropic_coarse_candidates(
        categories, args.mesh_size, d_cont,
        per_cat_cont_bounds=per_cat_cont_bounds,
    )


def build_single_fine_mesh(
        winner_info: tuple[int, int, float, np.ndarray],
        categories: np.ndarray,
        args: Any,
        training_data: np.ndarray | None,
        application: Any | None = None,
        combos: pd.DataFrame | None = None,
) -> np.ndarray:
    """Generate a fine mesh around a single top-category winner.

    Args:
        winner_info: Tuple (cat_id, global_idx, acq_val, cont_center)
            as returned by select_top_categories.
        categories: One-hot (+ descriptor) category matrix,
            shape (n_categories, d_cat).
        args: Experiment configuration namespace; must have mesh_size
            and fine_mesh_size.
        training_data: Existing training inputs to exclude, or None.
        application: Application object; used with combos to compute
            per-ingredient bounds for fine mesh clipping.
        combos: Raw category DataFrame from build_category_matrix.
            When provided together with application, per-ingredient
            bounds are enforced by clipping the fine window.

    Returns:
        Fine mesh array of shape (n_fine, d_cat + d_cont), with
        training duplicates removed.
    """
    ci, _, _, center = winner_info

    logger.debug(
        "Fine mesh — category %d, categories+descriptors shape: %s",
        ci, categories.shape,
    )

    cont_bounds = None
    if combos is not None and application is not None:
        cont_bounds = _get_cont_bounds_for_combo(combos.iloc[ci], application)

    fine_cont = generate_isotropic_fine_mesh(
        x_center=center,
        mesh_size=args.mesh_size,
        fine_mesh_size=args.fine_mesh_size,
        training_data=None,
        cont_bounds=cont_bounds,
    )

    repeated_cat = np.tile(categories[ci], (fine_cont.shape[0], 1))

    fine_mesh = np.hstack([repeated_cat, fine_cont])

    if training_data is not None and training_data.shape[0] > 0:
        fine_mesh = remove_nearby_matches(
            fine_mesh, training_data, d_cont=fine_cont.shape[1],
        )

    logger.debug("Fine mesh size for category %d: %s", ci, fine_mesh.shape)

    return fine_mesh


def build_fine_mesh_per_winner(
        winners: list[tuple[int, int, float, np.ndarray]],
        categories: np.ndarray,
        args: Any,
        training_data: np.ndarray | None,
        application: Any | None = None,
        combos: pd.DataFrame | None = None,
) -> np.ndarray:
    """Generate and concatenate fine meshes for all winner categories.

    Args:
        winners: List of (cat_id, global_idx, acq_val, cont_center)
            tuples from select_top_categories.
        categories: One-hot (+ descriptor) category matrix,
            shape (n_categories, d_cat).
        args: Experiment configuration namespace.
        training_data: Existing training inputs to exclude, or None.
        application: Application object; forwarded to build_single_fine_mesh
            for per-ingredient bounds enforcement.
        combos: Raw category DataFrame from build_category_matrix;
            forwarded to build_single_fine_mesh.

    Returns:
        Combined fine mesh of shape (total_fine_pts, d_cat + d_cont).
    """
    fine_meshes = [
        build_single_fine_mesh(winner, categories, args, training_data, application, combos)
        for winner in winners
    ]
    combined = np.vstack(fine_meshes)

    logger.info("Combined fine mesh size: %s", combined.shape)

    return combined


def compute_acquisition(
        choice_fn: Callable[..., np.ndarray],
        inputs: np.ndarray,
        mu: np.ndarray,
        sigma: np.ndarray,
        current_best: float,
        args: Any,
        rng: np.random.Generator,
        application: Any,
        qmc_samples: np.ndarray | None = None,
) -> np.ndarray:
    """Compute acquisition function values for a set of candidate inputs.

    Args:
        choice_fn: Acquisition function with the standard calling
            convention (inputs, preds, stds, current_best,
            minimize_objective, random_generator, qmc_samples, args,
            application).
        inputs: Candidate input points, shape (n_candidates, d).
        mu: Predicted means, shape (n_candidates, n_outputs).
        sigma: Predicted stds, shape (n_candidates, n_outputs).
        current_best: Current best observed objective value.
        args: Experiment configuration namespace.
        rng: NumPy random generator passed to choice_fn.
        application: Application object passed to choice_fn.
        qmc_samples: Pre-generated QMC normal samples, or None.

    Returns:
        Acquisition values array of shape (n_candidates,).
    """
    return choice_fn(
        inputs=inputs,
        preds=mu,
        stds=sigma,
        current_best=current_best,
        minimize_objective=args.minimize_objective,
        random_generator=rng,
        qmc_samples=qmc_samples,
        args=args,
        application=application,
    )


def build_category_matrix(application):
    """Return one-hot array of categories and a list of category encodings.

    If the application defines `fixed_categories`, those categorical
    dimensions are pinned to their fixed value in the mesh — only that
    single value appears in the Cartesian product, not all values seen
    during training.  This is how API_Name is fixed to "A190" (or any
    other drug) without changing the mesh generation logic.

    Args:
        application: Application object with category_headers and
            column transformer (_ct). If the application defines a
            get_descriptor_row method, descriptors are appended to
            the one-hot matrix.

    Returns:
        Tuple of (categories_with_descriptors, grids, combos) where
        combos is a DataFrame of raw category combinations
        (rows = Cartesian product of category values).
    """
    if not hasattr(application, 'category_headers') or not application.category_headers:
        return np.zeros((1, 0)), [], pd.DataFrame()

    cat_enc = application._ct.named_transformers_['cat']
    fixed   = getattr(application, "fixed_categories", {})
    mesh_cats = getattr(application, "mesh_categories", None) or getattr(application, "category_values", {})
    grids = [
        np.array([fixed[h]]) if h in fixed else np.array(mesh_cats.get(h, cat_enc.categories_[i]))
        for i, h in enumerate(application.category_headers)
    ]

    combos = pd.DataFrame(
        list(itertools.product(*grids)),
        columns=application.category_headers,
    )

    logger.debug(
        "Building category matrix — %d combinations.", len(combos)
    )

    categories_onehot = cat_enc.transform(combos).toarray()
    logger.debug("One-hot encoded shape: %s", categories_onehot.shape)

    descriptor_fn = getattr(application, 'get_descriptor_row', None)

    if descriptor_fn is not None:
        descriptors = np.array([
            descriptor_fn(row) for _, row in combos.iterrows()
        ])
        categories_with_descriptors = np.hstack([categories_onehot, descriptors])
        logger.debug(
            "Category matrix: one-hot=%d + descriptors=%d → total=%d",
            categories_onehot.shape[1],
            descriptors.shape[1],
            categories_with_descriptors.shape[1],
        )
    else:
        categories_with_descriptors = categories_onehot
        logger.debug(
            "No descriptors — one-hot only: %s", categories_onehot.shape
        )

    return categories_with_descriptors, grids, combos
