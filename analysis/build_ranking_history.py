"""Builds analysis/datasets/ranking_history.csv — how the leaderboard moved when the
revalidated Campaign 1 champions gained real repeats and DoE-OPT gained a full
measurement set.

Two things changed in commit 2cba4f2 ("Retire the Jupyter notebook..."), both in
BayesianOptimization/data/MicroemulsionFormulation_Comprehensive.csv:

  1. The six revalidated Campaign 1 champions (B4/E2/F5 x A190/Feno) went from ONE
     pre-averaged row each to THREE real repeats.  Their objective is therefore no
     longer a single lucky/unlucky number but a mean of three individually-scored
     repeats -- which is what the notebook ranks on.
  2. DoE-OPT was re-measured with A190 loaded, so it gained drug-loading and
     permeability data.  Before that it could only be scored on three of the five
     terms, which is why it was not comparable to anything on the leaderboard; now
     it carries the full objective and joins the A190 board directly.

Campaign 2's own measurements did not change (a handful of values move in the
fourth decimal from a spreadsheet resave), so every Campaign 2 rank shift here is
caused by the entries around it moving, not by its own data.

The "before" state is read straight out of git at PREV_REV, so this script stays
reproducible without keeping a second copy of the datasets in the tree.

Re-run:  python analysis/build_ranking_history.py
"""
import os
import re
import subprocess
import pandas as pd

PREV_REV = "71893ac"        # last commit before the repeats / DoE-OPT update

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATADIR = os.path.join(HERE, "datasets")

TOP3_C1 = {"A190": ["E2_A", "F5_A", "B4_A"], "Feno": ["E2_F", "F5_F", "B4_F"]}
PREFIX = {"A190": "A-", "Feno": "F-"}
DOE, DOE_LABEL = "DoEOPT", "DoE-OPT"


def _normalize(d):
    d.columns = [re.sub(r"\s+", " ", c.strip()) for c in d.columns]
    return d


def _load_current(name):
    return _normalize(pd.read_csv(os.path.join(DATADIR, name)))


def _load_prev(name):
    """Read a dataset as it stood at PREV_REV, straight from git."""
    blob = subprocess.run(["git", "show", f"{PREV_REV}:analysis/datasets/{name}"],
                          cwd=REPO, capture_output=True, check=True).stdout
    return _normalize(pd.read_csv(pd.io.common.BytesIO(blob)))


def board(c1, c2, api, with_doe):
    """The leaderboard for one API: mean per-repeat objective per formulation,
    Campaign 2 plus the Campaign 1 champions (plus DoE-OPT once it is comparable).
    Phase-separated formulations -- one separated repeat sends the mean off-scale --
    are dropped, exactly as the notebook drops them."""
    reps = c2[(c2["Exp"].str.startswith(PREFIX[api]))
              & (c2["Rep"].astype(str).str.lower() != "avg")]
    parts = [reps, c2[c2["Exp"].isin(TOP3_C1[api])]]
    if with_doe:
        parts.append(c1[c1["Exp"] == DOE].assign(Exp=DOE_LABEL))
    m = pd.concat(parts, ignore_index=True).groupby("Exp")["objective"].mean()
    return m[m < 100].sort_values()


def campaign_of(api, exp):
    if exp == DOE_LABEL:
        return "DoE"
    return "Campaign 1" if exp in TOP3_C1[api] else "Campaign 2"


c1_now, c2_now = _load_current("campaign1_scores.csv"), _load_current("campaign2_scores.csv")
c1_old, c2_old = _load_prev("campaign1_scores.csv"), _load_prev("campaign2_scores.csv")

rows = []
for api in PREFIX:
    # DoE-OPT is excluded from the "before" board on purpose: without drug loading or
    # permeability it was scored on three of five terms and was not on the same scale.
    before = board(c1_old, c2_old, api, with_doe=False)
    # DoE was an A190-only screening, so the baseline joins that board only.
    after = board(c1_now, c2_now, api, with_doe=(api == "A190"))
    rank_before = {e: i for i, e in enumerate(before.index, 1)}
    for rank, (exp, obj) in enumerate(after.items(), 1):
        rb = rank_before.get(exp)
        rows.append({
            "api": api,
            "exp": exp,
            "campaign": campaign_of(api, exp),
            "rank_before": rb,
            "objective_before": round(float(before[exp]), 6) if rb else None,
            "rank_after": rank,
            "objective_after": round(float(obj), 6),
            "rank_delta": (rb - rank) if rb else None,     # positive = moved up
        })

hist = pd.DataFrame(rows)
out = os.path.join(DATADIR, "ranking_history.csv")
hist.to_csv(out, index=False)
print(f"Wrote {out}  ({len(hist)} rows)")
for api in PREFIX:
    d = hist[hist["api"] == api]
    moved = d[d["rank_delta"].fillna(0) != 0]
    print(f"\n{api}: {len(d)} entries, {len(moved)} changed rank, "
          f"{int(d['rank_before'].isna().sum())} new")
    print(d.to_string(index=False))
