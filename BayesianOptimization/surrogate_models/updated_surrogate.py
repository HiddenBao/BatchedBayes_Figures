"""updated_surrogate.py

Rigorous-winner replacement for the legacy ``simple_gp.py`` placeholder.

This module preserves the **exact public interface** expected by the
downstream Bayesian optimisation pipeline:

  - ``OUTPUT_HEADERS``  — same column order, same 6 targets
  - ``SimpleGPModel(BaseEstimator)`` — same class name and signature
  - ``fit(X, y)``           → self
  - ``predict(X)``          → ndarray shape (n, 6)  [mean predictions]
  - ``predict_std(X)``      → ndarray shape (n, 6)  [std / uncertainty]

Winner assignments from the rigorous surrogate evaluation
(``rigorous_surrogate_results_phase12_all_targets_fullschema_v2_with_preds.json``):

  Phase_Sep     → GradientBoostingClassifier  (GBT_Uncalibrated)
  Droplet_Size  → GPR Matern(nu=1.5) + WhiteKernel      (GPR_Matern15_White)
  PDI           → GPR RationalQuadratic + WhiteKernel    (GPR_RatQuad_White)
  Zeta_P        → GPR Matern(nu=2.5) + RBF + WhiteKernel (GPR_Composite_M25_RBF)
  Drug_Loading  → GPR Matern(nu=2.5) + RBF + WhiteKernel (GPR_Composite_M25_RBF)
  Permeability  → ARD Matern GPR with Optuna-tuned hyperparameters
                  (GPR_ARD_Tuned; loaded from JSON if args.hyperopt_path is set)

Phase_Sep uncertainty proxy
    Bernoulli std = sqrt(p * (1 - p)).
    Derived from the predicted phase-separation probability; interpretable
    and well-suited to BO acquisition functions that consume scalar std.

Training masks (identical to legacy simple_gp.py):
    Phase_Sep     : all rows
    Droplet_Size, PDI, Zeta_P : stable rows (y[:, 3] == 0)
    Drug_Loading, Permeability: non-NaN rows per target

``fit(X, y)`` uses **only** the supplied arrays — it never reloads data
from disk.  This is critical for the hallucinated-liar batch BO method,
which retrains the surrogate on augmented data containing fabricated rows.
"""
from __future__ import annotations

import json
import logging
import warnings
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (
    Matern,
    RBF,
    RationalQuadratic,
    WhiteKernel,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Public constants — must remain identical to simple_gp.py           #
# ------------------------------------------------------------------ #

OUTPUT_HEADERS: list[str] = [
    "Droplet_Size",   # 0 — stable rows only,  GPR_Matern15_White
    "PDI",            # 1 — stable rows only,  GPR_RatQuad_White
    "Zeta_P",         # 2 — stable rows only,  GPR_Composite_M25_RBF
    "Phase_Sep",      # 3 — all rows,           GBT_Uncalibrated classifier
    "Drug_Loading",   # 4 — non-NaN rows,      GPR_Composite_M25_RBF
    "Permeability",   # 5 — non-NaN rows,      GPR_ARD_Tuned
]

_PHASE_SEP_IDX: int = 3
_PHYSICAL_IDXS: tuple[int, ...] = (0, 1, 2)
_DRUG_IDXS: tuple[int, ...] = (4, 5)
# GPR list order: physical targets (0,1,2) then drug targets (4,5)
_GPR_IDXS: tuple[int, ...] = _PHYSICAL_IDXS + _DRUG_IDXS

# ------------------------------------------------------------------ #
#  Internal defaults                                                   #
# ------------------------------------------------------------------ #

# GBT_Uncalibrated hyperparameters matching the evaluated candidate
_GBT_N_ESTIMATORS: int = 200
_GBT_MAX_DEPTH: int = 3
_GBT_LEARNING_RATE: float = 0.05

# Lower bound on reported predictive std — prevents degenerate zero std
# from causing division-by-zero in EI / Thompson sampling
_STD_CLIP_LOW: float = 1e-8


# ------------------------------------------------------------------ #
#  JSON winner-config loader                                           #
# ------------------------------------------------------------------ #

def _load_winner_config(path: str) -> dict[str, dict]:
    """Load per-target winner configs from a rigorous surrogate eval JSON.

    Accepts the JSON written by ``rigorous_surrogate_eval.py``.

    Resolution order per target:
      1. ``report["targets"][target]["winner_full"]`` — contains
         ``tuning_details`` with exact Optuna-tuned hyperparameters.
      2. ``report["pipeline_config"][target]`` — summary block;
         may include ``lengthscales`` and ``alpha`` for ARD targets.

    ``winner_full`` is preferred when present because it carries the
    full ``tuning_details`` sub-dict.

    Args:
        path: Filesystem path to the rigorous surrogate results JSON.

    Returns:
        Dict mapping target name → config dict.
        Returns an empty dict on any read / parse error (safe fallback).
    """
    try:
        with open(path, encoding="utf-8") as fh:
            report = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(
            "Could not load hyperopt JSON '%s': %s — using family defaults.",
            path, exc,
        )
        return {}

    configs: dict[str, dict] = {}
    targets_block = report.get("targets", {})
    pipeline_block = report.get("pipeline_config", {})

    for target in OUTPUT_HEADERS:
        tgt_data = targets_block.get(target, {})
        winner_full = tgt_data.get("winner_full")
        if winner_full is not None:
            configs[target] = winner_full
            logger.debug(
                "Loaded winner_full config for '%s' (model=%s).",
                target, winner_full.get("name", "?"),
            )
        elif target in pipeline_block:
            configs[target] = pipeline_block[target]
            logger.debug(
                "Loaded pipeline_config for '%s' (model=%s).",
                target, pipeline_block[target].get("model_name", "?"),
            )

    return configs


# ------------------------------------------------------------------ #
#  Per-family GPR builders                                             #
# ------------------------------------------------------------------ #

def _make_matern15_white_gpr(seed: int) -> GaussianProcessRegressor:
    """GPR_Matern15_White — Matern(nu=1.5) + WhiteKernel.

    Winner for Droplet_Size.  Matern(1.5) is once-differentiable:
    a good prior for particle sizes that change smoothly with formulation
    but may exhibit moderate local roughness.
    """
    kernel = Matern(nu=1.5) + WhiteKernel(noise_level=1e-3)
    return GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        random_state=seed,
        n_restarts_optimizer=3,
    )


def _make_ratquad_white_gpr(seed: int) -> GaussianProcessRegressor:
    """GPR_RatQuad_White — RationalQuadratic + WhiteKernel.

    Winner for PDI.  RationalQuadratic is a scale-mixture of RBF kernels
    and can model multi-scale variation; well-calibrated for PDI in eval.
    """
    kernel = RationalQuadratic() + WhiteKernel(noise_level=1e-3)
    return GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        random_state=seed,
        n_restarts_optimizer=3,
    )


def _make_composite_m25_rbf_gpr(seed: int) -> GaussianProcessRegressor:
    """GPR_Composite_M25_RBF — Matern(nu=2.5) + RBF + WhiteKernel.

    Winner for Zeta_P and Drug_Loading.

    Kernel interpretation:
      Matern(2.5):  captures moderate roughness at short range
                    (twice-differentiable; appropriate for zeta potential
                     / drug loading response surfaces).
      RBF:          captures smooth long-range variation.
      WhiteKernel:  isotropic observation noise.
    The additive structure lets the GP attribute variance at different
    length-scales independently.
    """
    kernel = Matern(nu=2.5) + RBF() + WhiteKernel(noise_level=1e-3)
    return GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        random_state=seed,
        n_restarts_optimizer=3,
    )


def _make_ard_tuned_gpr(
    seed: int,
    d: int,
    tuning_details: dict | None,
) -> GaussianProcessRegressor:
    """GPR_ARD_Tuned — ARD Matern with per-feature lengthscales.

    Winner for Permeability.  Permeability has very few training rows
    (n ≈ 6) and extremely small absolute values (~1e-5); ARD allows
    the GP to automatically down-weight uninformative features.

    Two modes:

    Tuned mode (``tuning_details`` is not None):
        Kernel hyperparameters are fixed to Optuna-tuned values from the
        rigorous eval JSON.  The sklearn optimizer is disabled
        (``optimizer=None``) to avoid costly and potentially ill-conditioned
        re-optimisation on tiny datasets.

    Fallback mode (``tuning_details`` is None):
        Trainable ARD Matern(nu=1.5) with one lengthscale per feature,
        n_restarts_optimizer=2 to keep fitting tractable at small n.

    Args:
        seed:           Random seed.
        d:              Input dimensionality (number of features).
        tuning_details: Dict with keys 'lengthscales', 'alpha', 'kernel'
                        from winner_full["tuning_details"], or None.

    Returns:
        Configured GaussianProcessRegressor.
    """
    if tuning_details is not None:
        try:
            ls = np.array(tuning_details["lengthscales"], dtype=float)
            alpha = float(tuning_details.get("alpha", 1e-6))
            kernel_name = tuning_details.get("kernel", "Matern15")
            nu = 1.5 if "15" in kernel_name else 2.5

            if len(ls) != d:
                logger.warning(
                    "ARD: stored lengthscales length %d != feature dim %d. "
                    "Using mean lengthscale as scalar fallback.",
                    len(ls), d,
                )
                ls = np.full(d, float(np.mean(ls)))

            kernel = Matern(
                nu=nu,
                length_scale=ls,
                length_scale_bounds="fixed",   # do not re-optimise
            )
            return GaussianProcessRegressor(
                kernel=kernel,
                alpha=alpha,
                normalize_y=True,
                random_state=seed,
                optimizer=None,   # hyperparams fixed; skip MLL optimisation
            )

        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(
                "ARD: failed to parse tuning_details (%s). "
                "Falling back to trainable ARD default.", exc,
            )

    # ── Fallback: trainable ARD Matern(nu=1.5) ─────────────────────
    ls_init = np.ones(d)
    kernel = Matern(nu=1.5, length_scale=ls_init)
    return GaussianProcessRegressor(
        kernel=kernel,
        alpha=1e-6,
        normalize_y=True,
        random_state=seed,
        n_restarts_optimizer=2,   # low — Permeability has ~6 rows
    )


# ------------------------------------------------------------------ #
#  Phase_Sep classifier builder                                        #
# ------------------------------------------------------------------ #

def _make_gbt_classifier(seed: int) -> GradientBoostingClassifier:
    """GBT_Uncalibrated — winner for Phase_Sep classification.

    Hyperparameters match the evaluated GBT_Uncalibrated candidate from
    ``model_builders.build_classifier_candidates()``.

    Note: GradientBoostingClassifier natively provides ``predict_proba``,
    so no isotonic / Platt wrapper is needed.  The non-calibrated variant
    outperformed the calibrated version on this dataset (lower log_loss
    at score = 0.00268).
    """
    return GradientBoostingClassifier(
        n_estimators=_GBT_N_ESTIMATORS,
        max_depth=_GBT_MAX_DEPTH,
        learning_rate=_GBT_LEARNING_RATE,
        random_state=seed,
    )


# ------------------------------------------------------------------ #
#  SimpleGPModel                                                       #
# ------------------------------------------------------------------ #

class SimpleGPModel(BaseEstimator):
    """Rigorous-winner surrogate: one model per output target.

    Drop-in replacement for ``simple_gp.SimpleGPModel``.

    Model assignments
    -----------------
    Phase_Sep     GradientBoostingClassifier (GBT_Uncalibrated)
    Droplet_Size  GPR Matern(nu=1.5) + WhiteKernel
    PDI           GPR RationalQuadratic + WhiteKernel
    Zeta_P        GPR Matern(nu=2.5) + RBF + WhiteKernel
    Drug_Loading  GPR Matern(nu=2.5) + RBF + WhiteKernel
    Permeability  ARD GPR (Optuna-tuned if JSON supplied; otherwise default)

    Training masks
    --------------
    Phase_Sep                   all rows
    Droplet_Size, PDI, Zeta_P   stable rows (y[:, 3] == 0)
    Drug_Loading, Permeability  non-NaN rows per target

    Phase_Sep uncertainty
    ---------------------
    Bernoulli std = sqrt(p * (1 - p)) where p = P(Phase_Sep=1 | X).
    This is a closed-form, BO-compatible uncertainty proxy derived
    directly from the predicted probability.

    Hyperparameter loading
    ----------------------
    If ``args.hyperopt_path`` points to a rigorous surrogate eval JSON,
    tuned lengthscales and alpha for the Permeability ARD GPR are loaded
    automatically.  Missing or malformed JSON falls back to sensible
    family defaults without raising.

    Args:
        application: Application object (for interface compatibility).
        args:        CLI argument namespace.  Uses ``args.seed`` (int,
                     default 42) and optionally ``args.hyperopt_path``
                     (str, path to rigorous eval JSON).
        random_generator: NumPy random generator; accepted for API
                          compatibility.  Seed is sourced from args.seed.
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

        self._seed: int = int(getattr(args, "seed", 42))

        # ── Phase_Sep classifier ───────────────────────────────────
        self._gbt: GradientBoostingClassifier = _make_gbt_classifier(
            self._seed,
        )
        # None  → GBT was fitted normally on ≥2 classes.
        # float → only one class seen; predict returns this constant.
        self._gbt_single_class: float | None = None

        # ── Optional tuned hyperparameters from rigorous eval JSON ─
        hyperopt_path: str | None = getattr(args, "hyperopt_path", None)
        self._winner_configs: dict[str, dict] = {}
        if hyperopt_path is not None:
            self._winner_configs = _load_winner_config(hyperopt_path)
            if self._winner_configs:
                logger.info(
                    "Loaded winner configs from '%s' for: %s",
                    hyperopt_path,
                    list(self._winner_configs.keys()),
                )

        # ── GPR list (built lazily at fit() once d is known) ──────
        # Order follows _GPR_IDXS = (0, 1, 2, 4, 5):
        #   gprs[0] → Droplet_Size  (col 0)
        #   gprs[1] → PDI           (col 1)
        #   gprs[2] → Zeta_P        (col 2)
        #   gprs[3] → Drug_Loading  (col 4)
        #   gprs[4] → Permeability  (col 5)
        self._gprs: list[GaussianProcessRegressor] = []
        self._d: int = 0          # feature dim; resolved at first fit()

        self.is_fitted_: bool = False

    # ---------------------------------------------------------------- #
    #  Private helpers                                                   #
    # ---------------------------------------------------------------- #

    def _build_gprs(self, d: int) -> list[GaussianProcessRegressor]:
        """Instantiate all 5 per-target GPRs, applying tuned configs.

        Called once at fit() time when the feature dimensionality is known.

        Args:
            d: Input dimensionality.

        Returns:
            List of 5 GPRs in _GPR_IDXS order.
        """
        s = self._seed
        perm_config = self._winner_configs.get("Permeability", {})
        tuning = perm_config.get("tuning_details")

        return [
            _make_matern15_white_gpr(s),            # gprs[0] → Droplet_Size
            _make_ratquad_white_gpr(s + 1),          # gprs[1] → PDI
            _make_composite_m25_rbf_gpr(s + 2),     # gprs[2] → Zeta_P
            _make_composite_m25_rbf_gpr(s + 3),     # gprs[3] → Drug_Loading
            _make_ard_tuned_gpr(s + 4, d, tuning),  # gprs[4] → Permeability
        ]

    def _gpc_p_sep(self, X: np.ndarray) -> np.ndarray:
        """Return P(Phase_Sep=1 | X), handling the single-class edge case.

        When all training rows share one Phase_Sep label, the GBT is not
        fitted.  ``_gbt_single_class`` holds the constant value to return.

        For a fitted GBT, resolves the column for class label 1 from
        ``predict_proba``.  Handles the edge case where class 1 never
        appeared in training (returns zeros).

        Args:
            X: Input array, shape (n, d).

        Returns:
            P(Phase_Sep=1 | X), shape (n,).  Values in [0, 1].
        """
        if self._gbt_single_class is not None:
            return np.full(len(X), self._gbt_single_class)

        classes = list(self._gbt.classes_)
        if 1 not in classes:
            # Only class 0 seen at training; P(sep=1) is effectively 0.
            return np.zeros(len(X))

        proba = self._gbt.predict_proba(X)
        return proba[:, classes.index(1)]

    # ---------------------------------------------------------------- #
    #  sklearn public API                                                #
    # ---------------------------------------------------------------- #

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SimpleGPModel":
        """Fit each model on its appropriate training subset.

        Uses **only** the supplied arrays.  No disk I/O is performed.

        Args:
            X: Input array, shape (n, d).
            y: Output array, shape (n, 6).  Column order follows
               OUTPUT_HEADERS.  NaN is permitted in columns 4
               (Drug_Loading) and 5 (Permeability).

        Returns:
            self

        Raises:
            ValueError: If no stable rows (Phase_Sep == 0) exist, making
                        it impossible to fit the physical GPRs.
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n, d = X.shape

        # Build GPRs the first time we know d, or if d changed.
        if d != self._d or not self._gprs:
            self._d = d
            self._gprs = self._build_gprs(d)

        # ── Phase_Sep: GBT classifier ──────────────────────────────
        labels = y[:, _PHASE_SEP_IDX].astype(int)
        unique_labels = np.unique(labels)

        if len(unique_labels) > 1:
            self._gbt.fit(X, labels)
            self._gbt_single_class = None
            logger.debug("GBT fitted on %d rows.", n)
        else:
            # Single-class guard: record the constant; skip fit().
            self._gbt_single_class = float(unique_labels[0])
            logger.debug(
                "GBT skipped: only class %d present in %d rows.",
                int(unique_labels[0]), n,
            )

        # ── Physical GPRs: stable rows only (Phase_Sep == 0) ──────
        stable_mask = y[:, _PHASE_SEP_IDX] == 0
        n_stable = int(stable_mask.sum())
        if n_stable == 0:
            raise ValueError(
                "No stable rows (Phase_Sep == 0) found in training data. "
                "Cannot fit Droplet_Size, PDI, or Zeta_P GPRs."
            )

        X_stable = X[stable_mask]
        for i, col in enumerate(_PHYSICAL_IDXS):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._gprs[i].fit(X_stable, y[stable_mask, col])
            logger.debug(
                "GPR[%s] fitted on %d stable rows.",
                OUTPUT_HEADERS[col], n_stable,
            )

        # ── Drug GPRs: non-NaN rows per target ─────────────────────
        for j, col in enumerate(_DRUG_IDXS):
            valid_mask = ~np.isnan(y[:, col])
            n_valid = int(valid_mask.sum())

            if n_valid == 0:
                logger.warning(
                    "GPR[%s]: no non-NaN rows; model not updated.",
                    OUTPUT_HEADERS[col],
                )
                continue

            if n_valid < 3:
                logger.warning(
                    "GPR[%s]: very few training rows (n=%d); "
                    "fit may be ill-conditioned.",
                    OUTPUT_HEADERS[col], n_valid,
                )

            gpr_idx = len(_PHYSICAL_IDXS) + j
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._gprs[gpr_idx].fit(X[valid_mask], y[valid_mask, col])
            logger.debug(
                "GPR[%s] fitted on %d non-NaN rows.",
                OUTPUT_HEADERS[col], n_valid,
            )

        self.is_fitted_ = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict mean for all 6 output targets.

        Args:
            X: Input array, shape (n, d).

        Returns:
            ndarray, shape (n, 6).  Column order follows OUTPUT_HEADERS.
            Phase_Sep column holds P(phase_separated | X) ∈ [0, 1].
        """
        X = np.asarray(X, dtype=float)
        n = len(X)
        mu = np.full((n, 6), np.nan, dtype=float)

        # Phase_Sep probability from GBT
        mu[:, _PHASE_SEP_IDX] = self._gpc_p_sep(X)

        # Continuous targets from GPRs
        for i, col in enumerate(_GPR_IDXS):
            try:
                mu[:, col] = self._gprs[i].predict(X)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "GPR[%s] predict failed (%s); column left as NaN.",
                    OUTPUT_HEADERS[col], exc,
                )

        return mu

    def predict_std(self, X: np.ndarray) -> np.ndarray:
        """Predict uncertainty for all 6 output targets.

        Phase_Sep:
            Bernoulli std = sqrt(p * (1 - p)).
            This is a closed-form uncertainty proxy computed from
            the GBT's predicted probability.

        Continuous targets:
            Posterior standard deviation from GaussianProcessRegressor
            with ``return_std=True``.

        All std values are clipped to a minimum of ``_STD_CLIP_LOW``
        (1e-8) to prevent division-by-zero in downstream EI / Thompson
        computations.

        Args:
            X: Input array, shape (n, d).

        Returns:
            ndarray, shape (n, 6).  Non-negative.
        """
        X = np.asarray(X, dtype=float)
        n = len(X)
        std = np.zeros((n, 6), dtype=float)

        # Phase_Sep: Bernoulli std proxy
        p_sep = self._gpc_p_sep(X)
        std[:, _PHASE_SEP_IDX] = np.sqrt(np.maximum(p_sep * (1.0 - p_sep), 0.0))

        # Continuous targets: GPR posterior std
        for i, col in enumerate(_GPR_IDXS):
            try:
                _, s = self._gprs[i].predict(X, return_std=True)
                std[:, col] = np.maximum(s, _STD_CLIP_LOW)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "GPR[%s] predict_std failed (%s); returning zero std.",
                    OUTPUT_HEADERS[col], exc,
                )

        return std


# ------------------------------------------------------------------ #
#  Self-test                                                           #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import logging as _logging

    _logging.basicConfig(
        level=_logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )

    print("=" * 60)
    print("updated_surrogate.py — self-test")
    print("=" * 60)

    rng = np.random.default_rng(0)

    N_TRAIN, N_TEST, D = 40, 8, 33

    # ── Synthetic training data ────────────────────────────────────
    X_train = rng.uniform(0.0, 1.0, (N_TRAIN, D))
    y_train = rng.standard_normal((N_TRAIN, 6))

    # Phase_Sep: binary labels in column 3 (~30 % positive)
    y_train[:, 3] = (rng.uniform(size=N_TRAIN) > 0.70).astype(float)
    # Stable rows: Physical targets only for Phase_Sep==0
    # Drug_Loading: 30 valid rows, 10 NaN
    y_train[30:, 4] = np.nan
    # Permeability: only 6 valid rows (mimics real data scarcity)
    y_train[:6, 5] = rng.standard_normal(6) * 1e-5
    y_train[6:, 5] = np.nan

    class _FakeArgs:  # minimal stand-in for argparse Namespace
        seed = 42
        hyperopt_path = None

    model = SimpleGPModel(application=None, args=_FakeArgs())
    print(f"\nFitting on {N_TRAIN} rows, d={D} features ...")
    model.fit(X_train, y_train)

    # ── Predictions ────────────────────────────────────────────────
    X_test = rng.uniform(0.0, 1.0, (N_TEST, D))
    mu = model.predict(X_test)
    sigma = model.predict_std(X_test)

    print(f"\npredict()     shape : {mu.shape}   (expected ({N_TEST}, 6))")
    print(f"predict_std() shape : {sigma.shape}   (expected ({N_TEST}, 6))")
    print(f"\nMean predictions (first 2 rows):\n{mu[:2]}")
    print(f"\nStd predictions (first 2 rows):\n{sigma[:2]}")
    print(f"\nGlobal std stats — min: {sigma.min():.2e}  max: {sigma.max():.2e}")

    assert mu.shape == (N_TEST, 6), "predict() shape mismatch"
    assert sigma.shape == (N_TEST, 6), "predict_std() shape mismatch"
    assert (sigma >= 0.0).all(), "negative std detected"
    assert not np.isnan(sigma).any(), "NaN in predict_std output"
    assert (
        mu[:, _PHASE_SEP_IDX] >= 0.0
    ).all() and (
        mu[:, _PHASE_SEP_IDX] <= 1.0
    ).all(), "Phase_Sep predict out of [0, 1]"

    print("\nAll assertions passed.")
    print("=" * 60)
