"""Regenerates every scored dataset in analysis/datasets/ from the comprehensive CSV.

These files used to be produced ad hoc; this script is their single source of
truth. Run it, then export_leaderboard_data.py.

It also carries the objective itself -- `compute_component_scores` -- which used
to live in a root-level score_dataset.py. Two objectives are implemented here and
they are NOT interchangeable:

  compute_component_scores  Campaign 2's weighted form: 3*size + 2*pdi + 1*zeta
                            + 2*drug_loading + 3*permeability, divided by
                            stability, PDI hinged at 0.1.
  original_objective        Campaign 1 AS PUBLISHED (Eq. 1-4 of the paper):
                            equal weights, +10*phase_sep, PDI hinged at 0.3.
                            Act 1 figures use this one.

  campaign1_scores.csv                     every non-Campaign-2 row (blank screening,
                                           the DoE screening rows, and the revalidated
                                           B4/E2/F5 champions), full objective
  campaign1_scores_original_objective.csv  same rows, Campaign 1's original
                                           physicochemical-only objective
  campaign2_scores.csv                     every row with all six outputs measured
  campaign2_scores_A190.csv / _Feno.csv    that file split by API
  <name>_avg.csv                           each of the above averaged per
                                           formulation, then scored

Campaign 2 experiments are the only ones whose Exp starts with 'A-' or 'F-'.
"""
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

DATADIR = os.path.join(HERE, "datasets")
SRC = os.path.join(REPO, "data",
                   "MicroemulsionFormulation_Comprehensive.csv")

OUTPUTS = ["Droplet_Size", "PDI", "Zeta_P", "Phase_Sep", "Drug_Loading", "Permeability"]
ID_COLS = ["Exp", "Rep", "Oil", "Surfactant", "Cosurfactant", "API_Name",
           "Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"]
C2_PREFIXES = ("A-", "F-")


def compute_component_scores(preds: np.ndarray) -> pd.DataFrame:
    """Return a DataFrame of each intermediate score and the final objective."""
    size = preds[:, 0]
    pdi  = preds[:, 1]
    zeta = preds[:, 2]
    sep  = preds[:, 3]
    dl   = preds[:, 4]
    perm = preds[:, 5]

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
    objective = formulation_loss / np.maximum(stability, 0.01)

    return pd.DataFrame({
        "size_score (w=3)":  size_score,
        "pdi_score  (w=2)":  pdi_score,
        "zeta_score (w=1)":  zeta_score,
        "dl_score   (w=2)":  dl_score,
        "perm_score (w=3)":  perm_score,
        "formulation_loss":  formulation_loss,
        "stability_factor":  stability,
        "objective":         objective,
    })


AVG_ID_COLS = ["Oil", "Surfactant", "Cosurfactant", "API_Name",
               "Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"]


def average_scores(per_rep):
    """Average each formulation's repeats, then score the averages.

    Not the same as averaging the per-rep objectives: the score terms hinge
    (100 nm, |zeta| = 10 mV, PDI, drug-loading bands), so the two orders differ.
    Campaign 1's revalidated champions exist only as a pre-averaged row, so
    averaging measurements first puts every formulation on the same footing.
    """
    rows = []
    for exp, grp in per_rep.groupby("Exp", sort=False):
        reps = grp[grp["Rep"].astype(str).str.lower() != "avg"]
        use = reps if len(reps) else grp
        row = {"Exp": exp, "n_reps": len(reps) if len(reps) else "pre-avg"}
        for c in AVG_ID_COLS:
            if c in use.columns:
                row[c] = use[c].iloc[0] if use[c].dtype == object else use[c].mean()
        for c in OUTPUTS:
            row[c] = use[c].mean()
        rows.append(row)
    out = pd.DataFrame(rows)
    scores = compute_component_scores(out[OUTPUTS].to_numpy(dtype=float))
    return (pd.concat([out, scores], axis=1)
            .sort_values("objective", ascending=True).reset_index(drop=True))


AVG_SOURCES = ["campaign1_scores", "campaign2_scores",
               "campaign2_scores_A190", "campaign2_scores_Feno"]


def original_objective(df):
    """Campaign 1's objective: additive, weight 1 each, +10*phase_sep, no DL/perm."""
    size, pdi = df["Droplet_Size"].to_numpy(float), df["PDI"].to_numpy(float)
    zeta, sep = df["Zeta_P"].to_numpy(float), df["Phase_Sep"].to_numpy(float)
    ss = np.maximum(0.0, (size - 100.0) / 900.0)
    ps = np.where(pdi < 0.3, 0.25 * pdi, pdi)
    zs = np.maximum(0.0, (np.abs(zeta) - 10.0) / 10.0)
    sc = np.clip(sep, 0.0, 1.0)
    return pd.DataFrame({"size_score (w=1)": ss, "pdi_score (w=1)": ps,
                         "zeta_score (w=1)": zs, "sep_score (w=10)": 10.0 * sc,
                         "objective": ss + ps + zs + 10.0 * sc})


def _assemble(rows, scores):
    return (pd.concat([rows[ID_COLS].reset_index(drop=True),
                       rows[OUTPUTS].reset_index(drop=True),
                       scores.reset_index(drop=True)], axis=1)
            .sort_values("objective", ascending=True).reset_index(drop=True))


def main(src=SRC, datadir=DATADIR):
    raw = pd.read_csv(src)
    is_c2 = raw["Exp"].str.startswith(C2_PREFIXES)

    # ---- Campaign 1 pool: everything that isn't a Campaign 2 experiment ----
    c1 = raw[~is_c2].reset_index(drop=True)
    c1_full = _assemble(c1, compute_component_scores(c1[OUTPUTS].to_numpy(float)))
    c1_orig = pd.concat([c1[ID_COLS], c1[OUTPUTS[:4]], original_objective(c1)], axis=1) \
                .sort_values("objective").reset_index(drop=True)

    # ---- Campaign 2: all six outputs present. DoE-OPT also has a complete
    # output set now that it has been re-measured with A190, but it is a
    # screening baseline, not a Campaign 2 formulation; it lives in the
    # Campaign 1 pool, where it is scored on the same full objective.
    complete = raw[OUTPUTS].notna().all(axis=1) & ~raw["Exp"].str.startswith("DoE")
    c2 = raw[complete].reset_index(drop=True)
    c2_full = _assemble(c2, compute_component_scores(c2[OUTPUTS].to_numpy(float)))

    written = {"campaign1_scores": c1_full,
               "campaign1_scores_original_objective": c1_orig,
               "campaign2_scores": c2_full,
               "campaign2_scores_A190": c2_full[c2_full["API_Name"] == "A190"].reset_index(drop=True),
               "campaign2_scores_Feno": c2_full[c2_full["API_Name"] == "Feno"].reset_index(drop=True)}
    for stem, df in written.items():
        path = os.path.join(datadir, f"{stem}.csv")
        df.to_csv(path, index=False)
        print(f"{stem}: {len(df)} rows -> {path}")

    # ---- average-then-score companions, consumed by export_leaderboard_data.py ----
    for stem in AVG_SOURCES:
        avg = average_scores(written[stem])
        path = os.path.join(datadir, f"{stem}_avg.csv")
        avg.to_csv(path, index=False)
        written[f"{stem}_avg"] = avg
        print(f"{stem}_avg: {len(written[stem])} per-rep rows -> {len(avg)} formulations -> {path}")
    return written


if __name__ == "__main__":
    main()
