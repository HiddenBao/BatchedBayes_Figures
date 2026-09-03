"""Tests for ThompsonBatchSelector.

Covers:
  - select_batch returns correct shape and type (BatchResult)
  - All selected points come from the candidate mesh
  - No duplicate indices in the batch
  - Cholesky fallback to independent sampling on singular covariance
  - batch_size > len(candidates) returns all candidates
  - batch_size = 1 (default case)
  - Deterministic output with fixed seed
"""
from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from BayesianOptimization.batch_selection import (
    BatchResult,
    ThompsonBatchSelector,
)
from BayesianOptimization.surrogate_models.simple_gp import (
    SimpleGPModel,
    _PHASE_SEP_IDX,
)


N_ROWS = 20
N_FEATURES = 5
N_CANDIDATES = 50
BATCH_SIZE = 5


class _FakeApplication:
    """Minimal application stub with objective_function.

    Uses a simple sum-of-columns objective, not the real microemulsion
    objective. Tests verify shape/structure, not objective correctness.
    """

    output_headers: list[str] = [
        "Droplet_Size", "PDI", "Zeta_P",
        "Phase_Sep", "Drug_Loading", "Permeability",
    ]

    def objective_function(self, preds, args=None):
        """Simple sum-of-columns objective (minimization)."""
        return np.nansum(preds, axis=1)


class _FakeArgs:
    """Minimal args stub."""
    seed: int = 0
    batch_size: int = BATCH_SIZE


def _make_y(n, n_stable, rng=None):
    """Create synthetic output array with NaN structure."""
    if rng is None:
        rng = np.random.default_rng(0)
    y = rng.random((n, 6))
    y[:n_stable, _PHASE_SEP_IDX] = 0.0
    y[n_stable:, _PHASE_SEP_IDX] = 1.0
    y[n_stable:, 4] = np.nan
    y[n_stable:, 5] = np.nan
    return y


@pytest.fixture()
def fitted_model():
    """Return a fitted SimpleGPModel on synthetic data."""
    rng = np.random.default_rng(0)
    X = rng.random((N_ROWS, N_FEATURES))
    y = _make_y(N_ROWS, n_stable=15, rng=rng)
    m = SimpleGPModel(application=_FakeApplication(), args=_FakeArgs())
    m.fit(X, y)
    return m


@pytest.fixture()
def candidates():
    """Return synthetic candidate mesh."""
    return np.random.default_rng(42).random((N_CANDIDATES, N_FEATURES))


@pytest.fixture()
def selector():
    """Return a ThompsonBatchSelector."""
    return ThompsonBatchSelector()


class TestSelectBatchShape:
    """select_batch returns correct output structure."""

    def test_returns_batch_result(self, selector, fitted_model, candidates):
        """select_batch returns a BatchResult instance."""
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert isinstance(result, BatchResult)

    def test_correct_batch_size(self, selector, fitted_model, candidates):
        """Batch contains exactly batch_size points."""
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert len(result.selected_inputs) == BATCH_SIZE

    def test_correct_feature_dimension(self, selector, fitted_model, candidates):
        """Each selected point has correct feature dimension."""
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert result.selected_inputs.shape == (BATCH_SIZE, N_FEATURES)

    def test_method_used_is_thompson(self, selector, fitted_model, candidates):
        """method_used is 'thompson'."""
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert result.method_used == "thompson"


class TestSelectBatchValidity:
    """Selected points are valid and non-redundant."""

    def test_selected_points_from_mesh(self, selector, fitted_model, candidates):
        """Every selected point exists in the candidate mesh."""
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        for point in result.selected_inputs:
            distances = np.linalg.norm(candidates - point, axis=1)
            assert distances.min() < 1e-10, (
                "Selected point not found in candidate mesh"
            )

    def test_no_duplicate_indices(self, selector, fitted_model, candidates):
        """No two batch points are the same candidate."""
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert len(set(result.indices)) == BATCH_SIZE


class TestEdgeCases:
    """Edge cases: small mesh, batch_size=1, determinism, Cholesky fallback."""

    def test_batch_size_exceeds_candidates(self, selector, fitted_model):
        """When batch_size > N candidates, return all candidates."""
        small_mesh = np.random.default_rng(99).random((3, N_FEATURES))
        args = _FakeArgs()
        args.batch_size = 10
        result = selector.select_batch(
            fine_inputs=small_mesh,
            acq_fine=np.zeros(3),
            model=fitted_model,
            args=args,
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert len(result.selected_inputs) == 3

    def test_batch_size_one(self, selector, fitted_model, candidates):
        """batch_size=1 (the default case) works correctly."""
        args = _FakeArgs()
        args.batch_size = 1
        result = selector.select_batch(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=args,
            application=_FakeApplication(),
            rng=np.random.default_rng(0),
        )
        assert result.selected_inputs.shape == (1, N_FEATURES)

    def test_deterministic_with_same_seed(self, selector, fitted_model, candidates):
        """Same seed produces same batch."""
        kwargs = dict(
            fine_inputs=candidates,
            acq_fine=np.zeros(len(candidates)),
            model=fitted_model,
            args=_FakeArgs(),
            application=_FakeApplication(),
        )
        result1 = selector.select_batch(**kwargs, rng=np.random.default_rng(42))
        result2 = selector.select_batch(**kwargs, rng=np.random.default_rng(42))
        np.testing.assert_array_equal(
            result1.selected_inputs, result2.selected_inputs,
        )

    def test_cholesky_fallback_still_produces_batch(
        self, selector, fitted_model, candidates,
    ):
        """When Cholesky fails, falls back to independent sampling."""
        def _always_fail(*args, **kwargs):
            raise np.linalg.LinAlgError("forced failure")

        with patch("numpy.linalg.cholesky", side_effect=_always_fail):
            result = selector.select_batch(
                fine_inputs=candidates,
                acq_fine=np.zeros(len(candidates)),
                model=fitted_model,
                args=_FakeArgs(),
                application=_FakeApplication(),
                rng=np.random.default_rng(0),
            )
        assert len(result.selected_inputs) == BATCH_SIZE
