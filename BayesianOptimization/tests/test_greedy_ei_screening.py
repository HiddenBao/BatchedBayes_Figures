# BayesianOptimization/tests/test_greedy_ei_screening.py
from __future__ import annotations

import logging

import numpy as np
import pytest
from unittest.mock import MagicMock

from BayesianOptimization.batch_selection import (
    GreedyEIScreeningBatchSelector,
    get_batch_selector,
    BatchResult,
)


def _make_args(batch_size=3, max_per_category=1, top_k_categories=10):
    args = MagicMock()
    args.batch_size = batch_size
    args.max_per_category = max_per_category
    args.top_k_categories = top_k_categories
    return args


def _make_fine_inputs_and_acq():
    """3 categories × 3 candidates each, d_cont=2.

    Cat 0 one-hot [1,0,0]: EI = [0.1, 0.5, 0.3]  -> per-cat best = 0.5
    Cat 1 one-hot [0,1,0]: EI = [0.9, 0.2, 0.4]  -> per-cat best = 0.9
    Cat 2 one-hot [0,0,1]: EI = [0.6, 0.7, 0.8]  -> per-cat best = 0.8
    """
    cats = np.eye(3)
    rows = []
    for i in range(3):
        for j in range(3):
            cont = np.array([float(j), float(j + 1)])
            rows.append(np.concatenate([cats[i], cont]))
    fine_inputs = np.array(rows)   # shape (9, 5)
    acq_fine = np.array([
        0.1, 0.5, 0.3,   # cat 0
        0.9, 0.2, 0.4,   # cat 1
        0.6, 0.7, 0.8,   # cat 2
    ])
    return fine_inputs, acq_fine


def test_selects_best_ei_per_category():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    args = _make_args(batch_size=3, max_per_category=1)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    assert isinstance(result, BatchResult)
    assert len(result.selected_inputs) == 3
    # Per-cat bests are 0.9 (cat1), 0.8 (cat2), 0.5 (cat0)
    np.testing.assert_array_almost_equal(
        np.sort(result.acquisition_values)[::-1], [0.9, 0.8, 0.5],
    )
    # Each selected point must come from a distinct category (unique one-hot prefix)
    cat_blocks = result.selected_inputs[:, :-2]
    assert len(np.unique(cat_blocks, axis=0)) == 3


def test_batch_size_limits_output():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    args = _make_args(batch_size=2, max_per_category=1)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    assert len(result.selected_inputs) == 2
    # Top 2 per-cat bests: 0.9 (cat1), 0.8 (cat2)
    np.testing.assert_array_almost_equal(
        np.sort(result.acquisition_values)[::-1], [0.9, 0.8],
    )
    # Both selected points must come from distinct categories
    cat_blocks = result.selected_inputs[:, :-2]
    assert len(np.unique(cat_blocks, axis=0)) == 2


def test_max_per_category_zero_treated_as_one():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    args = _make_args(batch_size=3, max_per_category=0)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    # max_per_category=0 -> effective_max=1: same result as max_per_category=1
    assert len(result.selected_inputs) == 3
    np.testing.assert_array_almost_equal(
        np.sort(result.acquisition_values)[::-1], [0.9, 0.8, 0.5],
    )
    # 0 treated as 1: each selected point must be from a distinct category
    cat_blocks = result.selected_inputs[:, :-2]
    assert len(np.unique(cat_blocks, axis=0)) == 3


def test_max_per_category_two():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    # 2 per cat × 3 cats = 6 winners; batch_size=6 takes all
    args = _make_args(batch_size=6, max_per_category=2)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    assert len(result.selected_inputs) == 6
    # Cat0 top2: [0.5, 0.3], Cat1 top2: [0.9, 0.4], Cat2 top2: [0.8, 0.7]
    # All 6 sorted desc: [0.9, 0.8, 0.7, 0.5, 0.4, 0.3]
    np.testing.assert_array_almost_equal(
        np.sort(result.acquisition_values)[::-1],
        [0.9, 0.8, 0.7, 0.5, 0.4, 0.3],
    )


def test_method_used_label():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    args = _make_args(batch_size=1, max_per_category=1)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    assert result.method_used == "greedy_ei_screening"


def test_total_candidates_is_fine_mesh_length():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    args = _make_args(batch_size=3, max_per_category=1)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    assert result.total_candidates == 9


def test_warns_when_top_k_less_than_batch_size(caplog):
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    # top_k_categories=3 < batch_size=5 with max_per_category=1 -> warning
    args = _make_args(batch_size=5, max_per_category=1, top_k_categories=3)
    with caplog.at_level(logging.WARNING, logger="BayesianOptimization.batch_selection"):
        sel.select_batch(
            fine_inputs, acq_fine, model=None, args=args,
            application=None, d_cont=2,
        )
    assert any("top_k_categories" in msg for msg in caplog.messages)


def test_no_warning_at_boundary_when_top_k_equals_batch_size(caplog):
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    # top_k_categories == batch_size: exactly sufficient, no warning expected
    args = _make_args(batch_size=3, max_per_category=1, top_k_categories=3)
    with caplog.at_level(logging.WARNING, logger="BayesianOptimization.batch_selection"):
        sel.select_batch(
            fine_inputs, acq_fine, model=None, args=args,
            application=None, d_cont=2,
        )
    assert not any("top_k_categories" in msg for msg in caplog.messages)


def test_no_warning_when_top_k_sufficient(caplog):
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    args = _make_args(batch_size=3, max_per_category=1, top_k_categories=10)
    with caplog.at_level(logging.WARNING, logger="BayesianOptimization.batch_selection"):
        sel.select_batch(
            fine_inputs, acq_fine, model=None, args=args,
            application=None, d_cont=2,
        )
    assert not any("top_k_categories" in msg for msg in caplog.messages)


def test_batch_size_larger_than_available_categories_caps_gracefully():
    sel = GreedyEIScreeningBatchSelector()
    fine_inputs, acq_fine = _make_fine_inputs_and_acq()
    # 3 cats, max_per_category=1 -> only 3 winners possible; batch_size=5
    args = _make_args(batch_size=5, max_per_category=1, top_k_categories=3)
    result = sel.select_batch(
        fine_inputs, acq_fine, model=None, args=args,
        application=None, d_cont=2,
    )
    # Pool has only 3 winners; slicing [:5] on 3-element array returns 3
    assert len(result.selected_inputs) == 3


def test_factory_returns_greedy_ei_screening():
    selector = get_batch_selector("greedy_ei_screening")
    assert isinstance(selector, GreedyEIScreeningBatchSelector)
