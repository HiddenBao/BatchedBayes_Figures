"""Regenerates every scored dataset in analysis/datasets/ from the comprehensive CSV.

These files used to be produced ad hoc; this script is their single source of
truth. Run it, then average_dataset_scores.py, then export_leaderboard_data.py.

  campaign1_scores.csv                     every non-Campaign-2 row (blank screening,
                                           the DoE screening rows, and the revalidated
                                           B4/E2/F5 champions), full objective
  campaign1_scores_original_objective.csv  same rows, Campaign 1's original
                                           physicochemical-only objective
  campaign2_scores.csv                     every row with all six outputs measured
  campaign2_scores_A190.csv / _Feno.csv    that file split by API

Campaign 2 experiments are the only ones whose Exp starts with 'A-' or 'F-'.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

from score_dataset import compute_component_scores  # noqa: E402

DATADIR = os.path.join(HERE, "datasets")
SRC = os.path.join(REPO, "data",
                   "MicroemulsionFormulation_Comprehensive.csv")

OUTPUTS = ["Droplet_Size", "PDI", "Zeta_P", "Phase_Sep", "Drug_Loading", "Permeability"]
ID_COLS = ["Exp", "Rep", "Oil", "Surfactant", "Cosurfactant", "API_Name",
           "Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"]
C2_PREFIXES = ("A-", "F-")


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
    return written


if __name__ == "__main__":
    main()
