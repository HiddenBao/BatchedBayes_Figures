"""Tests for SimpleGPModel.

Covers:
  - fit() uses the passed X, y (not application.get_dataset)
  - predict() and predict_std() return (n, 6) arrays
  - Phase_Sep column is a valid probability / Bernoulli std
  - Single-class edge case (all rows stable or all separated)
  - Hallucinated rows change model predictions (regression test for
    the hallucinated liar batch method)
"""
from __future__ import annotations

import numpy as np
import pytest

from BayesianOptimization.surrogate_models.simple_gp import (
    SimpleGPModel,
    _DRUG_IDXS,
    _PHASE_SEP_IDX,
    _PHYSICAL_IDXS,
)

N_ROWS = 20
N_FEATURES = 5


class _FakeApplication:
    """Minimal application stub for testing."""

    output_headers: list[str] = [
        "Droplet_Size",
        "PDI",
        "Zeta_P",
        "Phase_Sep",
        "Drug_Loading",
        "Permeability",
    ]


class _FakeArgs:
    """Minimal args stub for testing."""

    seed: int = 0


def _make_y(
    n: int,
    n_stable: int,
    *,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Create a synthetic output array with realistic NaN structure.

    Args:
        n: Total number of rows.
        n_stable: Rows where Phase_Sep == 0; remaining rows have
            Phase_Sep == 1 and NaN for Drug_Loading / Permeability.
        rng: Random generator. Uses default_rng(0) if None.

    Returns:
        Output array of shape (n, 6).
    """
    if rng is None:
        rng = np.random.default_rng(0)
    y = rng.random((n, 6))
    y[:n_stable, _PHASE_SEP_IDX] = 0.0
    y[n_stable:, _PHASE_SEP_IDX] = 1.0
    y[n_stable:, 4] = np.nan  # Drug_Loading
    y[n_stable:, 5] = np.nan  # Permeability
    return y


@pytest.fixture()
def model() -> SimpleGPModel:
    """Return an unfitted SimpleGPModel."""
    return SimpleGPModel(
        application=_FakeApplication(),
        args=_FakeArgs(),
    )


@pytest.fixture()
def fitted_model() -> SimpleGPModel:
    """Return a fitted SimpleGPModel on N_ROWS synthetic rows."""
    rng = np.random.default_rng(0)
    X = rng.random((N_ROWS, N_FEATURES))
    y = _make_y(N_ROWS, n_stable=15)
    m = SimpleGPModel(
        application=_FakeApplication(), args=_FakeArgs()
    )
    m.fit(X, y)
    return m


# ------------------------------------------------------------------ #
#  fit() uses passed data                                             #
# ------------------------------------------------------------------ #

class TestFitUsesPassedData:
    """Verify fit() trains on the passed X, y."""

    def test_is_fitted_after_fit(self, model: SimpleGPModel) -> None:
        """fit() sets is_fitted_ flag."""
        rng = np.random.default_rng(0)
        X = rng.random((N_ROWS, N_FEATURES))
        y = _make_y(N_ROWS, n_stable=15)
        model.fit(X, y)
        assert model.is_fitted_

    def test_fit_with_hallucinated_rows_does_not_raise(
        self,
        model: SimpleGPModel,
    ) -> None:
        """fit() accepts hallucinated worst-case rows appended to data."""
        rng = np.random.default_rng(0)
        X = rng.random((N_ROWS, N_FEATURES))
        y = _make_y(N_ROWS, n_stable=15)
        worst = np.array([[10000.0, 1.0, 100.0, 1.0, 0.0, 0.0]])
        X_aug = np.vstack([X, np.tile(X[:1], (3, 1))])
        y_aug = np.vstack([y, np.tile(worst, (3, 1))])
        model.fit(X_aug, y_aug)
        assert model.is_fitted_


# ------------------------------------------------------------------ #
#  predict / predict_std output shapes and validity                   #
# ------------------------------------------------------------------ #

class TestPredictShape:
    """predict() and predict_std() return correct shapes and ranges."""

    def test_predict_shape(
        self, fitted_model: SimpleGPModel
    ) -> None:
        """predict() returns (n, 6)."""
        X = np.random.default_rng(2).random((5, N_FEATURES))
        assert fitted_model.predict(X).shape == (5, 6)

    def test_predict_std_shape(
        self, fitted_model: SimpleGPModel
    ) -> None:
        """predict_std() returns (n, 6)."""
        X = np.random.default_rng(3).random((5, N_FEATURES))
        assert fitted_model.predict_std(X).shape == (5, 6)

    def test_phase_sep_predict_is_probability(
        self, fitted_model: SimpleGPModel
    ) -> None:
        """Phase_Sep column of predict() is in [0, 1]."""
        X = np.random.default_rng(4).random((10, N_FEATURES))
        p_sep = fitted_model.predict(X)[:, _PHASE_SEP_IDX]
        assert np.all(p_sep >= 0.0)
        assert np.all(p_sep <= 1.0)

    def test_phase_sep_std_bounded_by_bernoulli_max(
        self, fitted_model: SimpleGPModel
    ) -> None:
        """Phase_Sep std <= 0.5 (max Bernoulli std)."""
        X = np.random.default_rng(5).random((10, N_FEATURES))
        std = fitted_model.predict_std(X)[:, _PHASE_SEP_IDX]
        assert np.all(std <= 0.5 + 1e-9)

    def test_gpr_std_nonnegative(
        self, fitted_model: SimpleGPModel
    ) -> None:
        """GPR columns of predict_std() are non-negative."""
        X = np.random.default_rng(6).random((10, N_FEATURES))
        std = fitted_model.predict_std(X)
        for col in list(_PHYSICAL_IDXS) + list(_DRUG_IDXS):
            assert np.all(std[:, col] >= 0.0), (
                f"Negative std in output column {col}"
            )


# ------------------------------------------------------------------ #
#  Single-class GPC edge case                                         #
# ------------------------------------------------------------------ #

class TestSingleClassEdgeCase:
    """GPC must not crash when only one Phase_Sep class is present."""

    def test_all_stable_rows_predict_does_not_raise(
        self, model: SimpleGPModel
    ) -> None:
        """predict() returns 0.0 for Phase_Sep when all rows stable."""
        rng = np.random.default_rng(8)
        X = rng.random((N_ROWS, N_FEATURES))
        y = _make_y(N_ROWS, n_stable=N_ROWS, rng=rng)
        y[:, 4] = rng.random(N_ROWS)  # no NaN in drug columns
        y[:, 5] = rng.random(N_ROWS)
        model.fit(X, y)
        mu = model.predict(X[:3])
        assert mu.shape == (3, 6)
        assert np.all(mu[:, _PHASE_SEP_IDX] == 0.0)

    def test_all_stable_rows_predict_std_does_not_raise(
        self, model: SimpleGPModel
    ) -> None:
        """predict_std() returns 0.0 for Phase_Sep when all rows stable."""
        rng = np.random.default_rng(9)
        X = rng.random((N_ROWS, N_FEATURES))
        y = _make_y(N_ROWS, n_stable=N_ROWS, rng=rng)
        y[:, 4] = rng.random(N_ROWS)
        y[:, 5] = rng.random(N_ROWS)
        model.fit(X, y)
        std = model.predict_std(X[:3])
        assert std.shape == (3, 6)
        assert np.all(std[:, _PHASE_SEP_IDX] == 0.0)


# ------------------------------------------------------------------ #
#  Hallucination data flow (regression test for the core bug)         #
# ------------------------------------------------------------------ #

class TestHallucinationDataFlow:
    """Hallucinated rows must change model predictions.

    This is the key regression test: if fit() ignores its arguments
    (the old MultiPhaseModel bug), the two models below will produce
    identical predictions. If fit() uses passed data, augmenting with
    Phase_Sep=1 copies of a stable point must shift its predicted
    p(phase_sep) upward.
    """

    def test_hallucinated_fit_raises_phase_sep_at_selected_point(
        self,
    ) -> None:
        """p(phase_sep) rises at a point after hallucinating it as sep."""
        rng = np.random.default_rng(7)
        X = rng.random((N_ROWS, N_FEATURES))
        y = _make_y(N_ROWS, n_stable=15)

        # Base model: X[0] is labelled stable (Phase_Sep == 0)
        base = SimpleGPModel(
            application=_FakeApplication(), args=_FakeArgs()
        )
        base.fit(X, y)
        p_before = base.predict(X[:1])[0, _PHASE_SEP_IDX]

        # Augmented model: 3 copies of X[0] labelled as phase-separated
        worst = np.array([[10000.0, 1.0, 100.0, 1.0, 0.0, 0.0]])
        X_aug = np.vstack([X, np.tile(X[:1], (3, 1))])
        y_aug = np.vstack([y, np.tile(worst, (3, 1))])
        aug = SimpleGPModel(
            application=_FakeApplication(), args=_FakeArgs()
        )
        aug.fit(X_aug, y_aug)
        p_after = aug.predict(X[:1])[0, _PHASE_SEP_IDX]

        assert p_after > p_before, (
            f"p(phase_sep) should increase after hallucination. "
            f"Before: {p_before:.4f}, after: {p_after:.4f}. "
            "fit() may be ignoring passed data."
        )
