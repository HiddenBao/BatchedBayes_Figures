# BatchedBayes_Personal

Analysis and figure work for the BatchedBayes microemulsion campaigns. **This repo does not
contain the optimiser.** It holds the measured data, the scoring and analysis pipeline, and the
figure suites built on top of them.

## Upstream: where the optimiser lives

The Bayesian optimisation code was pruned from this repo. It lives in the upstream repository,
which is the **single source of truth** for anything about how the optimiser works:

| | |
|---|---|
| Remote | `https://github.com/mcgillresearchgroup/BatchedBayes.git` |
| Local clone | `C:/PyCharmProjects/BatchedBayes` |
| Default branch | `main` |
| Branch this repo was forked from | `Analysis-Cleanup` |

Branches on `origin`: `main`, `Analysis-Cleanup`, `ME-Part2-Clean`, `MEPart2`,
`Phase1and2_uses_Get_dataset`, `Surrogate_model_testing`, `HydrogenationCat`, `cercas`.
Run `git -C <clone> branch -a` rather than trusting this list.

The per-API Campaign 2 tracks `Part2_A190` and `Part2_Feno` are **not** on this remote — if you
need them, ask where they were pushed rather than assuming `ME-Part2-Clean` is the same thing.

### Query upstream instead of guessing

**When you need to know anything about the optimiser — the design space, the mesh, the
acquisition function, the surrogate models, the batch selection strategies, the constraint
handling, or how any of it changed — read it out of the upstream repo or its git history. Do not
infer it from this repo, and do not reconstruct it from memory.**

Things that only exist upstream:

- `BayesianOptimization/applications.py` — `MicroemulsionFormulation`: the design space
  (`ranges`, `category_values`, `mesh_categories`, the per-ingredient volume bounds),
  the descriptor tables, and the objective wiring.
- `BayesianOptimization/mesh_utils.py`, `acq_func.py`, `batch_selection.py`, `qmc.py` — the
  coarse/fine mesh, MC-EI over Sobol samples, and the three batch selectors.
- `BayesianOptimization/surrogate_models/` — the per-target surrogate architectures.
- `BayesianOptimization/tests/` — the constraint and selector tests.
- `results/` — the optimiser's own proposal CSVs.
- All history before this repo's `Import BatchedBayes Analysis-Cleanup branch` squash.

Useful commands, run against the local clone:

```bash
UP=/c/PyCharmProjects/BatchedBayes

git -C $UP log --oneline --all -- BayesianOptimization/applications.py
git -C $UP show <rev>:BayesianOptimization/applications.py
git -C $UP log -S"mesh_categories" --oneline --all      # when did this change?
git -C $UP diff main Analysis-Cleanup -- BayesianOptimization/
git -C $UP branch -a
```

If the local clone is stale or missing, `git -C $UP fetch --all` first, or clone the remote.

### The two constants mirrored here

`score_dataset.py` used to import `MicroemulsionFormulation`. With the optimiser gone it restates
the only two values it needed — `DATASET_PATH` and `OUTPUT_HEADERS` — as module constants. If the
upstream output column order or dataset filename ever changes, these drift silently. Check them
against upstream `applications.py` before trusting a score.

### Scripts that reference upstream history

`analysis/build_ranking_history.py` reads its "before" state from `git show 71893ac:...`. That
commit is **upstream only** — this repo's history does not reach it. Run that script against a
clone of the upstream repo, or re-point `PREV_REV`.

## What this repo does contain

```
data/                 measured formulation data + descriptor lookup tables
score_dataset.py      compute_component_scores() -- the objective, and a CLI report
average_dataset_scores.py
analysis/
  build_score_datasets.py     data/ -> analysis/datasets/*.csv        (run first)
  export_leaderboard_data.py  leaderboard CSVs
  build_ranking_history.py    needs upstream history, see above
  campaign_comparison.py      marimo notebook -- the analysis document
  datasets/                   generated; regenerate, don't hand-edit
  figures/                    generated SVGs
Figures/              slide figure suites -- see Figures/README.md for the folder convention
docs/paper/           the published Campaign 1 paper
```

Pipeline order: `analysis/build_score_datasets.py` → `average_dataset_scores.py` →
`analysis/export_leaderboard_data.py`.

## Campaigns — do not mix them up

The repo spans two campaigns with **different design spaces**, and upstream `main` carries
Campaign 2's code. Deriving a Campaign 1 figure from Campaign 2's constants is the easy mistake.

- **Campaign 1** — published as `docs/paper/s41120-026-00176-0.pdf` (Gunawardena, Chau et al.,
  *AAPS Open* 2026;12:34). **Table 1 of that paper is the authoritative design space** — read it
  rather than inferring ranges from code. Three continuous dials: oil volume 7.5–22.5 %, Smix
  **ratio** 3:1–1:3, sonication 0–3 min. It is a ratio because
  `Surfactant_V + Cosurfactant_V = 40.0` in every Campaign 1 row. 5 oils × 4 surfactants ×
  5 cosurfactants. 22 seed experiments (5 prior optima + 10 quasi-random + 7 repeats) then 25
  proposals in five batches of five. Its objective is Eq. 1–4: equal weights, ×10 phase-separation
  term, PDI hinged at 0.3 — implemented as `original_objective` in
  `analysis/build_score_datasets.py`, **not** by `score_dataset.py`.
- **Campaign 2** — per-API transfer tracks (`Part2_A190`, `Part2_Feno`). Independent surfactant
  and cosurfactant volumes, wider oil range, a different objective and a tighter PDI hinge (0.1
  here vs the paper's 0.3).

Experiment-stage prefixes in `Exp`: `DoE*` (prior optima) · `Misc*` (repeats) · `Ran*`
(quasi-random screen) · `A`–`E` (Campaign 1 batches) · `F` (Campaign 2).

## Environment

Conda env **`BatchedBayes`**. On Windows the numeric wheels delay-load DLLs from
`<env>/Library/bin`, so an unactivated launch dies with `0xC06D007F` and no traceback — the
notebooks carry a DLL guard above their first import. Keep it.

```bash
conda run -n BatchedBayes python analysis/build_score_datasets.py
conda run -n BatchedBayes marimo edit analysis/campaign_comparison.py
```

## Agent skills

### Issue tracker

Issues live as GitHub issues in `HiddenBao/BatchedBayes_Personal`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, using their default label strings. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
