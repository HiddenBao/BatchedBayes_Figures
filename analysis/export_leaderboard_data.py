"""Exports the underlying data for the Section 1b–1d leaderboards to CSV.

Every objective in the notebook is score-then-average: each repeat is scored on its
own and the reported value is the mean of those per-repeat objectives.  Section 1 is
already backed by campaign2_scores.csv (group by Exp, mean the objective), so only
the derived views need saving:

  1b  leaderboard_individual_reps.csv   — every repeat scored on its own (from
      campaign2_scores.csv), Campaign 1's revalidated champions and the DoE-OPT
      baseline included, ranked together per API.

  1c  leaderboard_original_objective.csv — every repeat re-scored with Campaign 1's
      ORIGINAL physicochemical-only objective and averaged per formulation, with the
      weighted component scores of the rep-averaged measurements, ranked per API.

  1d  leaderboard_original_objective_reps.csv — Section 1b's per-repeat treatment
      applied to 1c's metric: every repeat scored on its own with the original
      objective.

DoE-OPT joins the A190 boards only — the DoE screening was run with A190.

Re-run any time:  python export_leaderboard_data.py
"""
import os
import re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(HERE, "datasets")

def _load(name):
    d = pd.read_csv(os.path.join(DATADIR, name))
    d.columns = [re.sub(r"\s+", " ", c.strip()) for c in d.columns]
    return d

c1 = _load("campaign1_scores.csv")             # per-rep scores (holds DoE-OPT)
c2 = _load("campaign2_scores.csv")             # per-rep scores
c2a = _load("campaign2_scores_avg.csv")        # rep-averaged measurements

TOP3 = {"A190": ["E2_A", "F5_A", "B4_A"], "Feno": ["E2_F", "F5_F", "B4_F"]}
PREFIX = {"A190": "A-", "Feno": "F-"}
DOE, DOE_LABEL = "DoEOPT", "DoE-OPT"

def orig_objective(size, pdi, zeta, sep):
    """Campaign 1's original objective (additive, weight 1 each; +10*phase_sep; no
    drug loading / permeability). Reproduces campaign1_scores_original_objective.csv."""
    ss = np.maximum(0.0, (size - 100.0) / 900.0)
    ps = np.where(pdi < 0.3, 0.25 * pdi, pdi)
    zs = np.maximum(0.0, (np.abs(zeta) - 10.0) / 10.0)
    sc = np.clip(sep, 0.0, 1.0)
    return ss + ps + zs + 10.0 * sc

def board_reps(api):
    """Per-repeat rows of everything on one API's leaderboard: Campaign 2 (minus the
    fully phase-separated formulations), the Campaign 1 champions, and — for A190 —
    the DoE-OPT baseline.  Mirrors board_reps() in the notebook."""
    avg = c2a[c2a["Exp"].str.startswith(PREFIX[api])]
    shown = avg.loc[avg["objective"] < 100, "Exp"].tolist()
    reps = c2[(c2["Exp"].str.startswith(PREFIX[api]))
              & (c2["Rep"].astype(str).str.lower() != "avg")
              & (c2["Exp"].isin(shown))]
    parts = [reps, c2[c2["Exp"].isin(TOP3[api])]]
    if api == "A190":
        parts.append(c1[c1["Exp"] == DOE])
    out = pd.concat(parts, ignore_index=True)
    out["Exp"] = out["Exp"].replace({DOE: DOE_LABEL})
    return out[out["objective"] < 100].copy()

def campaign_of(api, exp):
    if exp == DOE_LABEL:
        return "DoE"
    return "Campaign 1" if exp in TOP3[api] else "Campaign 2"

# ---- 1b: individual repeats, full objective --------------------------------
rows_1b = []
for api in PREFIX:
    reps = board_reps(api).sort_values("objective")
    for rank, (_, r) in enumerate(reps.iterrows(), 1):
        rows_1b.append({"api": api, "rank": rank, "campaign": campaign_of(api, r["Exp"]),
                        "exp": r["Exp"], "rep": str(r["Rep"]),
                        "objective": round(float(r["objective"]), 6)})
df_1b = pd.DataFrame(rows_1b)

# ---- 1c: original (physicochem-only) objective, score-then-average ---------
rows_1c = []
for api in PREFIX:
    reps = board_reps(api).copy()
    reps["orig"] = orig_objective(reps["Droplet_Size"], reps["PDI"], reps["Zeta_P"], reps["Phase_Sep"])
    # Objective: mean of the per-rep original objectives. Measurements and the
    # component scores are rep-averaged (they are linear, so the order is moot).
    agg = reps.groupby("Exp").agg(
        orig_objective=("orig", "mean"),
        Droplet_Size=("Droplet_Size", "mean"), PDI=("PDI", "mean"),
        Zeta_P=("Zeta_P", "mean"), Phase_Sep=("Phase_Sep", "mean"),
    ).sort_values("orig_objective")
    for rank, (exp, r) in enumerate(agg.iterrows(), 1):
        size, pdi, zeta, sep = r["Droplet_Size"], r["PDI"], r["Zeta_P"], r["Phase_Sep"]
        d = {"api": api, "rank": rank, "exp": exp, "campaign": campaign_of(api, exp),
             "Droplet_Size": size, "PDI": pdi, "Zeta_P": zeta, "Phase_Sep": sep,
             "size_score (w=1)": float(np.maximum(0.0, (size - 100.0) / 900.0)),
             "pdi_score (w=1)": float(pdi * 0.25 if pdi < 0.3 else pdi),
             "zeta_score (w=1)": float(np.maximum(0.0, (abs(zeta) - 10.0) / 10.0)),
             "sep_score (w=10)": float(10.0 * np.clip(sep, 0.0, 1.0)),
             "orig_objective": float(r["orig_objective"])}
        for k in ("Droplet_Size", "PDI", "Zeta_P", "Phase_Sep", "size_score (w=1)",
                  "pdi_score (w=1)", "zeta_score (w=1)", "sep_score (w=10)", "orig_objective"):
            d[k] = round(float(d[k]), 6)
        rows_1c.append(d)
df_1c = pd.DataFrame(rows_1c)

# ---- 1d: original objective, per repeat ------------------------------------
rows_1d = []
for api in PREFIX:
    reps = board_reps(api).copy()
    reps["orig"] = orig_objective(reps["Droplet_Size"], reps["PDI"], reps["Zeta_P"], reps["Phase_Sep"])
    reps = reps.sort_values("orig")
    for rank, (_, r) in enumerate(reps.iterrows(), 1):
        rows_1d.append({"api": api, "rank": rank, "campaign": campaign_of(api, r["Exp"]),
                        "exp": r["Exp"], "rep": str(r["Rep"]),
                        "orig_objective": round(float(r["orig"]), 6)})
df_1d = pd.DataFrame(rows_1d)

out_1b = os.path.join(DATADIR, "leaderboard_individual_reps.csv")
out_1c = os.path.join(DATADIR, "leaderboard_original_objective.csv")
out_1d = os.path.join(DATADIR, "leaderboard_original_objective_reps.csv")
df_1b.to_csv(out_1b, index=False)
df_1c.to_csv(out_1c, index=False)
df_1d.to_csv(out_1d, index=False)
print(f"Wrote {out_1b}  ({len(df_1b)} rows)")
print(f"Wrote {out_1c}  ({len(df_1c)} rows)")
print(f"Wrote {out_1d}  ({len(df_1d)} rows)")
