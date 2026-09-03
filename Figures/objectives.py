"""The two microemulsion objectives, for figure suites to import.

A suite reads raw measurements from ``data/MicroemulsionFormulation_*.csv`` and
scores them here. Nothing else in this repo computes an objective; a suite that
restates one of these formulas has drifted by construction.

    from objectives import campaign1, campaign2, OUTPUTS

    df = pd.read_csv(DATA / "MicroemulsionFormulation_Comprehensive.csv")
    scores = campaign2(df)          # DataFrame, aligned to df's index
    df["objective"] = scores["objective"]

Both return a DataFrame of the intermediate component scores alongside the final
``objective`` column, so a suite can plot the breakdown without recomputing it.
Lower is better in both.

The two are NOT interchangeable -- they belong to different campaigns with
different design spaces. See CLAUDE.md.

Provenance
----------
Both are transcribed from the upstream optimiser repo,
https://github.com/mcgillresearchgroup/BatchedBayes (local clone at
C:/PyCharmProjects/BatchedBayes), which is the source of truth:

  campaign1  <- Analysis-Cleanup:analysis/build_score_datasets.py
                (``original_objective``); the paper's Eq. 1-4.
  campaign2  <- Analysis-Cleanup:score_dataset.py
                (``compute_component_scores``).

Known split in Campaign 2's phase-separation term, present upstream as well:
the optimiser's own objective (``BayesianOptimization/applications.py``,
``objective_function``, since 3a3df18 / 3cba64f, 2026-05-13) adds
``50 * clip(sep, 0, 1)`` to the loss, while the analysis side -- upstream's
``score_dataset.py`` and this file -- divides by the stability factor. The five
component scores are identical between them; only the phase-separation handling
differs. The divisive form is what every published ranking in this project was
computed with, so it is what stays here. Do not "reconcile" the two without
deciding which numbers you are willing to move.
"""
import numpy as np
import pandas as pd

#: Raw measurement columns both objectives read, in this order.
OUTPUTS = ["Droplet_Size", "PDI", "Zeta_P", "Phase_Sep",
           "Drug_Loading", "Permeability"]


def campaign1(df: pd.DataFrame) -> pd.DataFrame:
    """Campaign 1's objective, as published (paper Eq. 1-4).

    Additive, weight 1 on each of size / PDI / zeta, weight 10 on phase
    separation. Physicochemical only -- no drug loading, no permeability.
    PDI is hinged at 0.3: below it the penalty is quartered.

    Act 1 figures use this one. It is the objective the campaign was actually
    optimised against, so it is the only fair yardstick for Campaign 1 rows.
    """
    size = df["Droplet_Size"].to_numpy(float)
    pdi = df["PDI"].to_numpy(float)
    zeta = df["Zeta_P"].to_numpy(float)
    sep = df["Phase_Sep"].to_numpy(float)

    size_score = np.maximum(0.0, (size - 100.0) / 900.0)
    pdi_score = np.where(pdi < 0.3, 0.25 * pdi, pdi)
    zeta_score = np.maximum(0.0, (np.abs(zeta) - 10.0) / 10.0)
    sep_score = 10.0 * np.clip(sep, 0.0, 1.0)

    return pd.DataFrame({
        "size_score (w=1)": size_score,
        "pdi_score (w=1)": pdi_score,
        "zeta_score (w=1)": zeta_score,
        "sep_score (w=10)": sep_score,
        "objective": size_score + pdi_score + zeta_score + sep_score,
    }, index=df.index)


def campaign2(df: pd.DataFrame) -> pd.DataFrame:
    """Campaign 2's weighted objective.

    ``(3*size + 2*pdi + 1*zeta + 2*drug_loading + 3*permeability)`` divided by
    the stability factor ``1 - phase_sep`` (floored at 0.01, so a fully
    separated formulation lands around 100x its stable-side loss rather than at
    infinity -- which is why leaderboards cut at ``objective < 100``).

    Differences from Campaign 1 beyond the weights: PDI is hinged at 0.1 rather
    than 0.3, and PDI and permeability both have a gentle bonus side at one
    fifth the penalty slope, so the loss can go slightly negative for an ideal
    formulation. Drug loading is a V around 100% with a forgiving dead zone
    inside +/-5%. Missing drug loading or permeability contributes 0, not NaN.
    """
    preds = df[OUTPUTS].to_numpy(dtype=float)
    size, pdi, zeta, sep, dl, perm = (preds[:, i] for i in range(6))

    size_score = np.maximum(0.0, (size - 100.0) / 900.0)

    pdi_score = np.where(
        pdi >= 0.1,
        (pdi - 0.1) / 0.9,
        -(0.1 - pdi) / (0.9 * 5.0),
    )

    zeta_score = np.maximum(0.0, (np.abs(zeta) - 10.0) / 10.0)

    dl_dist = np.abs(dl - 100.0)
    dl_score = np.where(
        np.isnan(dl), 0.0,
        np.where(
            dl_dist <= 5.0,
            dl_dist / 130.0,
            5.0 / 130.0 + (dl_dist - 5.0) / 26.0,
        ),
    )

    perm_score = np.where(
        np.isnan(perm), 0.0,
        np.where(
            perm <= 20e-6,
            (20e-6 - perm) / 20e-6,
            -(perm - 20e-6) / (20e-6 * 5.0),
        ),
    )

    formulation_loss = (
        3.0 * size_score
        + 2.0 * pdi_score
        + 1.0 * zeta_score
        + 2.0 * dl_score
        + 3.0 * perm_score
    )
    stability = 1.0 - np.clip(sep, 0.0, 1.0)

    return pd.DataFrame({
        "size_score (w=3)": size_score,
        "pdi_score (w=2)": pdi_score,
        "zeta_score (w=1)": zeta_score,
        "dl_score (w=2)": dl_score,
        "perm_score (w=3)": perm_score,
        "formulation_loss": formulation_loss,
        "stability_factor": stability,
        "objective": formulation_loss / np.maximum(stability, 0.01),
    }, index=df.index)
