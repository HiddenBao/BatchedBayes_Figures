"""
Average each formulation's repeat measurements, then score the averages
(average-then-score) — one row per formulation.

The per-rep score files score each repeat individually; because the scoring
functions are nonlinear (hinges at size = 100 nm, |zeta| = 10 mV, drug-loading
bands, ...), the mean of per-rep objectives differs from the objective of the
mean measurements. Campaign 1's revalidated champions exist only as
pre-averaged 'avg' rows, so averaging measurements before scoring puts every
formulation on the same footing.

Reads  analysis/datasets/<name>.csv   (see SOURCES)
Writes analysis/datasets/<name>_avg.csv
"""

import os
import pandas as pd
from score_dataset import compute_component_scores

HERE = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(HERE, "analysis", "datasets")

OUTPUTS = ["Droplet_Size", "PDI", "Zeta_P", "Phase_Sep", "Drug_Loading", "Permeability"]
ID_COLS = ["Oil", "Surfactant", "Cosurfactant", "API_Name",
           "Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"]


def average_scores(per_rep: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for exp, grp in per_rep.groupby("Exp", sort=False):
        reps = grp[grp["Rep"].astype(str).str.lower() != "avg"]
        # Revalidated Campaign 1 champions exist only as a pre-averaged row.
        use = reps if len(reps) else grp
        row = {"Exp": exp, "n_reps": len(reps) if len(reps) else "pre-avg"}
        for c in ID_COLS:
            if c in use.columns:
                row[c] = use[c].iloc[0] if use[c].dtype == object else use[c].mean()
        for c in OUTPUTS:
            row[c] = use[c].mean()
        rows.append(row)
    out = pd.DataFrame(rows)
    scores = compute_component_scores(out[OUTPUTS].to_numpy(dtype=float))
    return (pd.concat([out, scores], axis=1)
            .sort_values("objective", ascending=True)
            .reset_index(drop=True))


SOURCES = ["campaign1_scores", "campaign2_scores",
           "campaign2_scores_A190", "campaign2_scores_Feno"]


def main():
    for stem in SOURCES:
        src = os.path.join(DATADIR, f"{stem}.csv")
        dst = os.path.join(DATADIR, f"{stem}_avg.csv")
        per_rep = pd.read_csv(src)
        out = average_scores(per_rep)
        out.to_csv(dst, index=False)
        print(f"{stem}: {len(per_rep)} per-rep rows -> {len(out)} formulations -> {dst}")
        print(out[["Exp", "n_reps", "objective"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
