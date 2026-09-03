"""Acquisition functions for the Bayesian optimization loop."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _compute_candidate_ei(
        i: int,
        pred_i: np.ndarray,
        std_i: np.ndarray,
        qmc_samples: np.ndarray,
        current_best: float,
        minimize_objective: bool,
        application: Any,
        args: Any,
        debug_sample_idx: int,
        ei_by_candidate: np.ndarray,
) -> None:
    """Compute EI for candidate i and write result into ei_by_candidate.

    Args:
        i: Index of the current candidate.
        pred_i: Predicted mean for candidate i, shape (n_outputs,).
        std_i: Predicted std for candidate i, shape (n_outputs,).
        qmc_samples: QMC normal samples, shape (n_qmc, n_outputs).
        current_best: Current best observed objective value.
        minimize_objective: If True, improvement = current_best - obj.
        application: Application object with objective_function method.
        args: Experiment configuration namespace.
        debug_sample_idx: Index at which to emit a debug log line.
        ei_by_candidate: Output array mutated in place; shape
            (n_candidates,).
    """
    samples_i = qmc_samples * std_i + pred_i
    sample_objs = application.objective_function(samples_i, args)

    if minimize_objective:
        improvement = current_best - sample_objs
    else:
        improvement = sample_objs - current_best
    improvement[improvement < 0] = 0
    ei_by_candidate[i] = improvement.mean()

    if i == debug_sample_idx:
        logger.debug(
            "EI sample candidate %d — objs [%.4f/%.4f/%.4f], "
            "best=%.4f, impr [%.4f/%.4f/%.4f], "
            "frac_pos=%.2f%%, EI=%.6f",
            i,
            sample_objs.min(), sample_objs.mean(), sample_objs.max(),
            current_best,
            improvement.min(), improvement.mean(), improvement.max(),
            (improvement > 0).mean() * 100,
            ei_by_candidate[i],
        )


def expected_improvement_components_choice(
        inputs: np.ndarray,
        preds: np.ndarray,
        stds: np.ndarray,
        current_best: float,
        minimize_objective: bool,
        random_generator: np.random.Generator,
        qmc_samples: np.ndarray | None,
        args: Any,
        application: Any,
        **kwargs: Any,
) -> np.ndarray:
    """Compute a scalar EI for every candidate.

    Args:
        inputs: Candidate input points, shape (n_candidates, d).
        preds: Predicted means, shape (n_candidates, n_outputs).
        stds: Predicted stds, shape (n_candidates, n_outputs).
        current_best: Current best observed objective value.
        minimize_objective: If True, improvement = current_best - obj.
        random_generator: NumPy random generator for debug index.
        qmc_samples: QMC normal samples, shape (n_qmc, n_outputs).
        args: Experiment configuration namespace.
        application: Application object with objective_function method.
        **kwargs: Ignored; accepted for forward-compatibility.

    Returns:
        Array of EI values, shape (n_candidates,).
    """
    n_candidates = len(inputs)
    ei_by_candidate = np.zeros(n_candidates)
    debug_sample_idx = int(
        random_generator.integers(0, min(5, n_candidates))
    )

    logger.debug(
        "EI debug — pred shape: %s, std shape: %s, "
        "qmc shape: %s, current_best: %s",
        preds[0].shape, stds[0].shape,
        qmc_samples.shape if qmc_samples is not None else None,
        current_best,
    )

    for i in range(n_candidates):
        try:
            _compute_candidate_ei(
                i, preds[i], stds[i], qmc_samples,
                current_best, minimize_objective,
                application, args, debug_sample_idx, ei_by_candidate,
            )
        except Exception as e:
            logger.warning(
                "Error in EI calculation for candidate %d: %s", i, e,
            )
            ei_by_candidate[i] = np.nan

    return ei_by_candidate


def get_choice_function(
        choice_method: str,
        surrogate_model_type: str,
        surrogate_model_target: str,
        application: Any,
        args: Any,
) -> Any:
    """Return the acquisition function callable.

    Args:
        choice_method: Acquisition method name (e.g. 'expected_improvement').
        surrogate_model_type: Surrogate model identifier string.
        surrogate_model_target: Target type, e.g. 'components'.
        application: Application object.
        args: Experiment configuration namespace.

    Returns:
        The acquisition function callable. Currently only
        EI/components is supported.
    """
    return expected_improvement_components_choice
