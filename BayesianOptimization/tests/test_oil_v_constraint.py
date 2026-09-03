"""Tests for per-oil Oil_V constraint in mesh generation."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from argparse import Namespace

from BayesianOptimization.applications import MicroemulsionFormulation
from BayesianOptimization.mesh_utils import (
    build_category_matrix,
    build_coarse_mesh,
    generate_isotropic_coarse_candidates,
)
from BayesianOptimization.utils import get_inputs_grid


def test_oil_v_ranges_present():
    """MicroemulsionFormulation must define oil_v_ranges for all mesh oils."""
    app = MicroemulsionFormulation()
    assert hasattr(app, 'oil_v_ranges'), "oil_v_ranges not defined"
    for oil in app.mesh_categories["Oil"]:
        assert oil in app.oil_v_ranges, f"{oil} missing from oil_v_ranges"


def test_oil_v_global_lower_bound():
    """Global Oil_V lower bound must be 5.0 to enable full collaborator range."""
    app = MicroemulsionFormulation()
    assert app.ranges["Oil_V"][0] == 5.0, (
        f"Expected lower bound 5.0, got {app.ranges['Oil_V'][0]}"
    )


def test_oil_v_ranges_values():
    """Capmul/Capryol cap at 15%, Maisine/Soybean cap at 10%."""
    app = MicroemulsionFormulation()
    for oil in ["Capmul_MCM", "Capryol_90"]:
        assert app.oil_v_ranges[oil] == (5.0, 15.0), (
            f"{oil} expected (5.0, 15.0), got {app.oil_v_ranges[oil]}"
        )
    for oil in ["Maisine_Oil", "Soybean_Oil"]:
        assert app.oil_v_ranges[oil] == (5.0, 10.0), (
            f"{oil} expected (5.0, 10.0), got {app.oil_v_ranges[oil]}"
        )


def test_build_category_matrix_returns_combos():
    """build_category_matrix must return a third value: the raw combos DataFrame."""
    app = MicroemulsionFormulation()
    app.get_dataset()  # fits _ct

    result = build_category_matrix(app)
    assert len(result) == 3, f"Expected 3 return values, got {len(result)}"

    categories, grids, combos = result
    assert isinstance(combos, pd.DataFrame), "Third return value must be a DataFrame"
    assert "Oil" in combos.columns, "combos must have an 'Oil' column"
    assert len(combos) == len(categories), (
        f"combos rows ({len(combos)}) must match categories rows ({len(categories)})"
    )


def test_per_cat_cont_bounds_filters_continuous_grid():
    """generate_isotropic_coarse_candidates must respect per_cat_cont_bounds."""
    # 3 categories, 2 continuous dims, mesh_size=5 -> 5^2=25 cont points per cat
    n_cats = 3
    d_cat = 4
    d_cont = 2
    mesh_size = 5
    categories = np.zeros((n_cats, d_cat))

    # Category 0: unconstrained on dim 0
    # Category 1: dim 0 capped at 0.5
    # Category 2: dim 0 capped at 0.3
    # dim 1 is unconstrained for all categories
    oil_v_bounds = [(0.0, 1.0), (0.0, 0.5), (0.0, 0.3)]
    per_cat_cont_bounds = [
        [(lo, hi), (0.0, 1.0)] for (lo, hi) in oil_v_bounds
    ]

    coarse, cat_idx, cont_pts = generate_isotropic_coarse_candidates(
        categories, mesh_size, d_cont, per_cat_cont_bounds=per_cat_cont_bounds
    )

    for ci, (lo, hi) in enumerate(oil_v_bounds):
        mask = cat_idx == ci
        oil_v = cont_pts[mask, 0]
        assert np.all(oil_v >= lo - 1e-10), f"cat {ci}: Oil_V below lo={lo}"
        assert np.all(oil_v <= hi + 1e-10), f"cat {ci}: Oil_V above hi={hi}"


def test_coarse_mesh_respects_per_oil_bounds():
    """End-to-end: coarse mesh must not propose Oil_V outside per-oil limits."""
    app = MicroemulsionFormulation()
    app.get_dataset()  # fits _ct

    categories, _, combos = build_category_matrix(app)
    d_cont = len(app.continuous_headers)
    args = Namespace(mesh_size=11)

    coarse_input, cat_idx, cont_pts = build_coarse_mesh(
        categories, args, d_cont, app, combos=combos,
    )

    oil_lo, oil_hi = app.ranges["Oil_V"]   # (5.0, 22.5)

    for oil, (per_min, per_max) in app.oil_v_ranges.items():
        expected_lo = (per_min - oil_lo) / (oil_hi - oil_lo)
        expected_hi = (per_max - oil_lo) / (oil_hi - oil_lo)

        oil_cats = combos.index[combos["Oil"] == oil].tolist()
        for cat_id in oil_cats:
            pts = cont_pts[cat_idx == cat_id]
            assert len(pts) > 0, f"No candidates for oil={oil}, cat_id={cat_id}"
            assert np.all(pts[:, 0] >= expected_lo - 1e-10), (
                f"{oil}: Oil_V below {expected_lo:.3f}"
            )
            assert np.all(pts[:, 0] <= expected_hi + 1e-10), (
                f"{oil}: Oil_V above {expected_hi:.3f}"
            )
