import types

import numpy as np
import pandas as pd
import pytest

from BayesianOptimization.applications import MicroemulsionFormulation
from BayesianOptimization.mesh_utils import (
    build_category_matrix,
    build_coarse_mesh,
    build_fine_mesh_per_winner,
    generate_isotropic_coarse_candidates,
)


# ---------------------------------------------------------------------------
# Test 5: continuous headers are in the expected order and positions
# ---------------------------------------------------------------------------

def test_continuous_headers_column_order():
    app = MicroemulsionFormulation()
    inputs, outputs = app.get_dataset()

    assert app.continuous_headers == [
        "Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"
    ], f"Unexpected continuous_headers: {app.continuous_headers}"

    # 23 one-hot + 9 descriptors + 4 continuous = 36
    assert inputs.shape == (147, 36), f"Expected (147, 36), got {inputs.shape}"

    # Columns 32–35 are continuous and should be scaled to [0, 1]
    cont_cols = inputs[:, 32:36]
    assert np.all(cont_cols >= -1e-9), "Continuous columns contain values below 0"
    assert np.all(cont_cols <= 1.0 + 1e-9), "Continuous columns contain values above 1"


# ---------------------------------------------------------------------------
# Test 1: Oil_V filtering still works after parameter rename (regression)
# ---------------------------------------------------------------------------

def test_per_cat_cont_bounds_oil_filtering():
    # 2 categories (identity matrix), d_cont=4, Oil_V capped at [0.0, 0.5] on dim 0
    categories = np.eye(2)
    mesh_size = 5
    d_cont = 4

    per_cat_cont_bounds = [
        [(0.0, 0.5), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)],
        [(0.0, 0.5), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)],
    ]

    coarse_inputs, cat_indices, cont_points = generate_isotropic_coarse_candidates(
        categories, mesh_size, d_cont,
        per_cat_cont_bounds=per_cat_cont_bounds,
    )

    d_cat = categories.shape[1]
    oil_v_col = d_cat + 0  # dim 0 of continuous block
    assert np.all(coarse_inputs[:, oil_v_col] <= 0.5 + 1e-10), \
        "Oil_V candidates exceed upper bound of 0.5"


# ---------------------------------------------------------------------------
# Test 2: Surfactant_V and Cosurfactant_V filtering works independently
# ---------------------------------------------------------------------------

def test_per_cat_cont_bounds_surf_cosurf_filtering():
    categories = np.eye(2)
    mesh_size = 5
    d_cont = 4

    # global Surfactant_V (20,40): cap at (20,30) -> scaled hi = (30-20)/(40-20) = 0.5
    # global Cosurfactant_V (5,20): cap at (5,10)  -> scaled hi = (10-5)/(20-5)  = 0.333
    per_cat_cont_bounds = [
        [(0.0, 1.0), (0.0, 0.5), (0.0, 0.333), (0.0, 1.0)],
        [(0.0, 1.0), (0.0, 0.5), (0.0, 0.333), (0.0, 1.0)],
    ]

    coarse_inputs, cat_indices, cont_points = generate_isotropic_coarse_candidates(
        categories, mesh_size, d_cont,
        per_cat_cont_bounds=per_cat_cont_bounds,
    )

    d_cat = categories.shape[1]
    surf_v_col   = d_cat + 1
    cosurf_v_col = d_cat + 2

    assert np.all(coarse_inputs[:, surf_v_col]   <= 0.5   + 1e-10), \
        "Surfactant_V candidates exceed upper bound 0.5"
    assert np.all(coarse_inputs[:, cosurf_v_col] <= 0.333 + 1e-10), \
        "Cosurfactant_V candidates exceed upper bound 0.333"


# ---------------------------------------------------------------------------
# Test 3: build_coarse_mesh produces correct scaled bounds for Transcutol_HP
# ---------------------------------------------------------------------------

def test_build_coarse_mesh_generates_correct_bounds_transcutol():
    app = MicroemulsionFormulation()
    app.get_dataset()  # fits _ct

    categories, grids, combos = build_category_matrix(app)
    d_cont = len(app.continuous_headers)

    # Transcutol_HP cosurfactant_v_ranges: (10, 20); global Cosurfactant_V: (5, 20)
    g_lo, g_hi = app.ranges["Cosurfactant_V"]       # (5, 20)
    p_lo, p_hi = app.cosurfactant_v_ranges["Transcutol_HP"]  # (10, 20)
    expected_lo = (p_lo - g_lo) / (g_hi - g_lo)    # (10-5)/15 = 0.3333
    expected_hi = (p_hi - g_lo) / (g_hi - g_lo)    # (20-5)/15 = 1.0

    args = types.SimpleNamespace(mesh_size=5)
    coarse_inputs, cat_indices, cont_points = build_coarse_mesh(
        categories, args, d_cont, app, combos=combos,
    )

    cosurf_v_dim = app.continuous_headers.index("Cosurfactant_V")
    tc_cat_ids = combos.index[combos["Cosurfactant"] == "Transcutol_HP"].tolist()
    assert tc_cat_ids, "No Transcutol_HP categories found in combos"

    for cat_id in tc_cat_ids:
        mask = cat_indices == cat_id
        if mask.any():
            vals = cont_points[mask, cosurf_v_dim]
            assert np.all(vals >= expected_lo - 1e-10), \
                f"Cosurfactant_V below {expected_lo:.4f} for Transcutol_HP cat {cat_id}: min={vals.min():.4f}"
            assert np.all(vals <= expected_hi + 1e-10), \
                f"Cosurfactant_V above {expected_hi:.4f} for Transcutol_HP cat {cat_id}: max={vals.max():.4f}"


# ---------------------------------------------------------------------------
# Test 4: No crash and full-range fallback when per-component dict is absent
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Test 6: Fine mesh clips to per-ingredient floor (regression for Surfactant_V)
# ---------------------------------------------------------------------------

def test_fine_mesh_respects_per_ingredient_bounds():
    app = MicroemulsionFormulation()
    app.get_dataset()  # fits _ct

    categories, grids, combos = build_category_matrix(app)
    d_cont = len(app.continuous_headers)
    surf_v_dim = app.continuous_headers.index("Surfactant_V")

    # Tween_20 surfactant_v_ranges: (20, 40); global Surfactant_V: (10, 40)
    # scaled floor = (20 - 10) / (40 - 10) = 1/3 ≈ 0.3333
    surf_v_floor = (20.0 - 10.0) / (40.0 - 10.0)

    tween_rows = combos.index[combos["Surfactant"] == "Tween_20"].tolist()
    assert tween_rows, "No Tween_20 categories found in combos"
    cat_id = tween_rows[0]

    # Center at 0.35 — raw fine window [0.30, 0.40] (mesh_size=11, half=0.05)
    # bleeds below 0.3333 without the fix
    center = np.zeros(d_cont)
    center[surf_v_dim] = 0.35

    winner = (cat_id, 0, 1.0, center)
    args = types.SimpleNamespace(mesh_size=11, fine_mesh_size=5)

    fine_mesh = build_fine_mesh_per_winner(
        [winner], categories, args, None, app, combos=combos,
    )

    d_cat = categories.shape[1]
    surf_v_col = d_cat + surf_v_dim

    assert np.all(fine_mesh[:, surf_v_col] >= surf_v_floor - 1e-10), (
        f"Fine mesh Surfactant_V falls below floor {surf_v_floor:.4f}: "
        f"min={fine_mesh[:, surf_v_col].min():.4f}"
    )


def test_no_bounds_when_no_ranges_attr():
    # Mock application without surfactant_v_ranges or cosurfactant_v_ranges
    mock_app = types.SimpleNamespace(
        continuous_headers=["Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"],
        ranges={
            "Oil_V":          (5.0, 22.5),
            "Surfactant_V":   (20.0, 40.0),
            "Cosurfactant_V": (5.0, 20.0),
            "Sonication":     (0, 3),
        },
        # Intentionally NO surfactant_v_ranges or cosurfactant_v_ranges
    )

    combos = pd.DataFrame([{
        "Oil": "Capmul_MCM", "Surfactant": "Labrasol", "Cosurfactant": "Ethanol",
    }])
    categories = np.zeros((1, 10))
    args = types.SimpleNamespace(mesh_size=5)

    # Must not raise
    coarse_inputs, cat_indices, cont_points = build_coarse_mesh(
        categories, args, 4, mock_app, combos=combos,
    )

    # Surfactant_V dim (1) should span full [0, 1] — unconstrained
    surf_dim = 1
    assert cont_points[:, surf_dim].min() == pytest.approx(0.0, abs=0.01), \
        "Surfactant_V should start at 0.0 when no range dict present"
    assert cont_points[:, surf_dim].max() == pytest.approx(1.0, abs=0.01), \
        "Surfactant_V should reach 1.0 when no range dict present"
