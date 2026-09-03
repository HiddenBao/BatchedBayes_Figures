"""Simple GP surrogate: one GaussianProcess per output target.

Phase_Sep uses GaussianProcessClassifier (Matern nu=2.5).
All other targets use GaussianProcessRegressor
(Matern nu=2.5 + WhiteKernel).

Training masks applied per target:
  - Phase_Sep  (GPC): all rows
  - Droplet_Size, PDI, Zeta_P (GPR): stable rows (y[:, 3] == 0)
  - Drug_Loading, Permeability  (GPR): non-NaN rows

This model fixes the hallucinated liar batch method: fit() uses
only the passed X, y arrays (never reloads from disk).
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.gaussian_process import (
    GaussianProcessClassifier,
    GaussianProcessRegressor,
)
from sklearn.gaussian_process.kernels import Matern, WhiteKernel

logger = logging.getLogger(__name__)

OUTPUT_HEADERS: list[str] = [
    "Droplet_Size",  # 0 — physical, stable rows
    "PDI",           # 1 — physical, stable rows
    "Zeta_P",        # 2 — physical, stable rows
    "Phase_Sep",     # 3 — GPC, all rows
    "Drug_Loading",  # 4 — drug, non-NaN rows
    "Permeability",  # 5 — drug, non-NaN rows
]
_PHASE_SEP_IDX: int = 3
_PHYSICAL_IDXS: tuple[int, ...] = (0, 1, 2)
_DRUG_IDXS: tuple[int, ...] = (4, 5)
# GPR order: physical (0,1,2) then drug (4,5) — matches self._gprs index
_GPR_IDXS: tuple[int, ...] = _PHYSICAL_IDXS + _DRUG_IDXS


def _make_gpr(seed: int) -> GaussianProcessRegressor:
    """Create a GPR with Matern(nu=2.5) + WhiteKernel.

    Args:
        seed: Random seed for reproducibility.

    Returns:
        Configured GaussianProcessRegressor.
    """
    kernel = Matern(nu=2.5) + WhiteKernel(noise_level=1e-3)
    return GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        random_state=seed,
        n_restarts_optimizer=3,
    )


class SimpleGPModel(BaseEstimator):
    """One GP per output target surrogate model.

    Uses GaussianProcessClassifier for Phase_Sep and
    GaussianProcessRegressor (Matern(2.5) + WhiteKernel) for all
    other targets. Training masks applied per target to respect the
    data availability structure of the microemulsion dataset.

    Critically, fit(X, y) uses only the passed arrays — it never
    reloads data from disk. This allows the hallucinated liar batch
    selector to retrain the model on augmented data containing
    fabricated worst-case rows.

    Args:
        application: Application object (used for output_headers).
        args: CLI argument namespace; seed read from args.seed.
        random_generator: NumPy random generator (accepted for
            interface compatibility; seed sourced from args.seed).
    """

    def __init__(
        self,
        application: Any,
        args: Any | None = None,
        random_generator: Any | None = None,
    ) -> None:
        self.application = application
        self.args = args
        self.random_generator = random_generator

        seed = int(getattr(args, "seed", 42))
        self._gpc = GaussianProcessClassifier(
            kernel=Matern(nu=2.5),
            random_state=seed,
        )
        # One GPR per non-classification target in _GPR_IDXS order
        self._gprs: list[GaussianProcessRegressor] = [
            _make_gpr(seed + i) for i in range(len(_GPR_IDXS))
        ]
        self.is_fitted_: bool = False

    # ---------------------------------------------------------------- #
    #  Private helpers                                                   #
    # ---------------------------------------------------------------- #

    def _gpc_p_sep(self, X: np.ndarray) -> np.ndarray:
        """Return P(phase_sep=1 | X), handling the single-class edge case.

        When all training rows belong to one Phase_Sep class, sklearn's
        GPC stores only that class in classes_ and predict_proba returns
        a single column. This method guards against the resulting
        IndexError.

        Args:
            X: Input array, shape (n, d).

        Returns:
            P(Phase_Sep=1 | X), shape (n,). Returns an array of the
            single observed class value when only one class was seen.
        """
        if len(self._gpc.classes_) == 1:
            single = float(self._gpc.classes_[0])
            return np.full(len(X), single)
        # classes_ is sorted; for binary {0, 1} labels index 1 is class 1.
        return self._gpc.predict_proba(X)[:, 1]

    # ---------------------------------------------------------------- #
    #  sklearn API                                                       #
    # ---------------------------------------------------------------- #

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> SimpleGPModel:
        """Fit each GP on its appropriate training subset.

        Args:
            X: Input array, shape (n, d).
            y: Output array, shape (n, 6). Columns ordered as
                OUTPUT_HEADERS. NaN allowed in Drug_Loading and
                Permeability columns for blank-formulation rows.

        Returns:
            self
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)

        # Phase_Sep GPC — train on all rows.
        # Guard: GPC requires ≥2 classes. When all training rows share
        # one Phase_Sep value, set classes_ directly so _gpc_p_sep()
        # can return the correct constant without calling predict_proba.
        labels = y[:, _PHASE_SEP_IDX].astype(int)
        if len(np.unique(labels)) > 1:
            self._gpc.fit(X, labels)
            logger.debug("GPC fitted on %d rows.", len(X))
        else:
            self._gpc.classes_ = np.unique(labels)
            logger.debug(
                "GPC skipped: only class %d present in %d rows.",
                int(self._gpc.classes_[0]),
                len(X),
            )

        # Physical GPRs — stable rows only (Phase_Sep == 0)
        stable = y[:, _PHASE_SEP_IDX] == 0
        if not stable.any():
            raise ValueError(
                "No stable rows (Phase_Sep == 0) found in training data. "
                "Physical GPRs cannot be fitted."
            )
        X_stable = X[stable]
        for i, col in enumerate(_PHYSICAL_IDXS):
            self._gprs[i].fit(X_stable, y[stable, col])
            logger.debug(
                "GPR[%s] fitted on %d stable rows.",
                OUTPUT_HEADERS[col],
                int(stable.sum()),
            )

        # Drug GPRs — non-NaN rows per target
        for j, col in enumerate(_DRUG_IDXS):
            valid = ~np.isnan(y[:, col])
            self._gprs[len(_PHYSICAL_IDXS) + j].fit(
                X[valid], y[valid, col],
            )
            logger.debug(
                "GPR[%s] fitted on %d non-NaN rows.",
                OUTPUT_HEADERS[col],
                int(valid.sum()),
            )

        self.is_fitted_ = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict mean for all 6 targets.

        Args:
            X: Input array, shape (n, d).

        Returns:
            Mean predictions, shape (n, 6). Phase_Sep column is
            P(phase_separated | X) from the GPC.
        """
        X = np.asarray(X, dtype=float)
        n = len(X)
        mu = np.full((n, 6), np.nan, dtype=float)

        mu[:, _PHASE_SEP_IDX] = self._gpc_p_sep(X)

        for i, col in enumerate(_GPR_IDXS):
            mu[:, col] = self._gprs[i].predict(X)

        return mu

    def predict_std(self, X: np.ndarray) -> np.ndarray:
        """Predict standard deviation for all 6 targets.

        Args:
            X: Input array, shape (n, d).

        Returns:
            Standard deviations, shape (n, 6). Phase_Sep column uses
            Bernoulli std: sqrt(p * (1 - p)).
        """
        X = np.asarray(X, dtype=float)
        n = len(X)
        std = np.zeros((n, 6), dtype=float)

        p_sep = self._gpc_p_sep(X)
        std[:, _PHASE_SEP_IDX] = np.sqrt(p_sep * (1.0 - p_sep))

        for i, col in enumerate(_GPR_IDXS):
            _, s = self._gprs[i].predict(X, return_std=True)
            std[:, col] = s

        return std
