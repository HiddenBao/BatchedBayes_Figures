"""Tests for remove_nearby_matches (replaces remove_exact_matches).

Convention: input rows are [cat+desc block | continuous block].
The continuous block is the last d_cont columns.
"""
from __future__ import annotations

import numpy as np
import pytest

from BayesianOptimization.mesh_utils import remove_nearby_matches


# Shared toy setup: d_cat = 3 (a 3-wide categorical block), d_cont = 4.
# We construct rows by horizontally stacking a cat block and a cont block.

D_CAT = 3
D_CONT = 4


def _row(cat: list[float], cont: list[float]) -> np.ndarray:
    assert len(cat) == D_CAT and len(cont) == D_CONT
    return np.array(cat + cont, dtype=float)


def test_empty_training_data_keeps_all_candidates():
    cands = np.stack([
        _row([1, 0, 0], [0.1, 0.2, 0.3, 0.4]),
        _row([0, 1, 0], [0.5, 0.5, 0.5, 0.5]),
    ])
    out = remove_nearby_matches(cands, None, d_cont=D_CONT)
    assert out.shape == cands.shape
    np.testing.assert_array_equal(out, cands)

    out = remove_nearby_matches(cands, np.empty((0, D_CAT + D_CONT)), d_cont=D_CONT)
    assert out.shape == cands.shape


def test_same_combo_far_apart_continuous_is_kept():
    """Same categorical combo but continuous block is well outside threshold."""
    train = np.stack([
        _row([1, 0, 0], [0.1, 0.1, 0.1, 0.1]),
    ])
    cands = np.stack([
        _row([1, 0, 0], [0.9, 0.9, 0.9, 0.9]),  # same combo, far in continuous
    ])
    out = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.075)
    assert out.shape == (1, D_CAT + D_CONT), (
        "Candidate with same combo but far continuous block should be kept"
    )


def test_same_combo_all_dims_within_threshold_is_dropped():
    """Same categorical combo and every continuous dim within 0.075 — dropped."""
    train = np.stack([
        _row([1, 0, 0], [0.5, 0.5, 0.5, 0.5]),
    ])
    cands = np.stack([
        _row([1, 0, 0], [0.55, 0.45, 0.50, 0.52]),  # max delta 0.05 < 0.075
        _row([1, 0, 0], [0.50, 0.50, 0.50, 0.50]),  # exact match (delta 0)
    ])
    out = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.075)
    assert out.shape == (0, D_CAT + D_CONT), (
        "Both candidates within L_inf threshold of training point should be dropped"
    )


def test_same_combo_one_dim_outside_threshold_is_kept():
    """L_inf gate: a single dim exceeding threshold means the candidate is kept."""
    train = np.stack([
        _row([1, 0, 0], [0.5, 0.5, 0.5, 0.5]),
    ])
    cands = np.stack([
        # 3 dims close, but dim 2 is 0.5 -> 0.6 (delta 0.10 > 0.075)
        _row([1, 0, 0], [0.55, 0.45, 0.60, 0.52]),
    ])
    out = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.075)
    assert out.shape == (1, D_CAT + D_CONT), (
        "One dim outside threshold should keep the candidate (L_inf gate)"
    )


def test_different_combo_identical_continuous_is_kept():
    """Different categorical combo always means 'not nearby', regardless of cont."""
    train = np.stack([
        _row([1, 0, 0], [0.5, 0.5, 0.5, 0.5]),
    ])
    cands = np.stack([
        _row([0, 1, 0], [0.5, 0.5, 0.5, 0.5]),  # different combo, identical cont
    ])
    out = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.075)
    assert out.shape == (1, D_CAT + D_CONT), (
        "Different categorical combo should always be kept"
    )


def test_threshold_parameter_is_respected():
    """Same candidate, two thresholds — outcome differs."""
    train = np.stack([
        _row([1, 0, 0], [0.5, 0.5, 0.5, 0.5]),
    ])
    # Max delta = 0.06 across all dims
    cands = np.stack([
        _row([1, 0, 0], [0.56, 0.44, 0.50, 0.52]),
    ])

    # threshold 0.05: 0.06 > 0.05 -> kept
    out_strict = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.05)
    assert out_strict.shape == (1, D_CAT + D_CONT), (
        "At threshold 0.05, candidate with max delta 0.06 should be kept"
    )

    # threshold 0.10: 0.06 < 0.10 -> dropped
    out_loose = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.10)
    assert out_loose.shape == (0, D_CAT + D_CONT), (
        "At threshold 0.10, candidate with max delta 0.06 should be dropped"
    )


def test_multiple_training_points_only_one_combo_matches():
    """Two training points; only one shares the candidate's combo and is close."""
    train = np.stack([
        _row([0, 1, 0], [0.50, 0.50, 0.50, 0.50]),  # different combo
        _row([1, 0, 0], [0.30, 0.30, 0.30, 0.30]),  # same combo, far
        _row([1, 0, 0], [0.55, 0.45, 0.50, 0.52]),  # same combo, close
    ])
    cands = np.stack([
        _row([1, 0, 0], [0.52, 0.48, 0.50, 0.50]),
    ])
    out = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.075)
    assert out.shape == (0, D_CAT + D_CONT), (
        "Candidate should be dropped because at least one same-combo training "
        "point is within L_inf threshold"
    )


def test_threshold_zero_only_drops_exact_continuous_matches():
    """At threshold 0, only candidates with identical continuous blocks are dropped."""
    train = np.stack([
        _row([1, 0, 0], [0.50, 0.50, 0.50, 0.50]),
    ])
    cands = np.stack([
        _row([1, 0, 0], [0.50, 0.50, 0.50, 0.50]),  # exact match -> dropped
        _row([1, 0, 0], [0.50, 0.50, 0.50, 0.51]),  # one dim off by 0.01 -> kept
    ])
    out = remove_nearby_matches(cands, train, d_cont=D_CONT, threshold=0.0)
    assert out.shape == (1, D_CAT + D_CONT), (
        "At threshold 0, only exact-continuous-match candidates should drop. "
        "Expected 1 kept, got "
        f"{out.shape[0]}"
    )
    # The kept candidate is the one with the 0.51 in dim 3.
    np.testing.assert_array_almost_equal(out[0, -D_CONT:], [0.50, 0.50, 0.50, 0.51])
