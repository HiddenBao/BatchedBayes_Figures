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

### Scripts that reference upstream history

`analysis/build_ranking_history.py` reads its "before" state from `git show 71893ac:...`. That
commit is **upstream only** — this repo's history does not reach it. Run that script against a
clone of the upstream repo, or re-point `PREV_REV`.

## What this repo does contain

```
data/                 measured formulation data + descriptor lookup tables
analysis/
  build_score_datasets.py     BOTH objectives + data/ -> datasets/*.csv   (run first)
  export_leaderboard_data.py  leaderboard CSVs
  build_ranking_history.py    needs upstream history, see above
  campaign_comparison.py      marimo notebook -- the analysis document
  datasets/                   generated; regenerate, don't hand-edit
  figures/                    generated SVGs
Figures/              slide figure suites -- see Figures/README.md for the folder convention
docs/paper/           the published Campaign 1 paper (Gunawardena-2026_Microemulsion-BO.pdf)
```

Pipeline: `analysis/build_score_datasets.py` → `analysis/export_leaderboard_data.py`.
The first writes all nine dataset CSVs, per-rep and `_avg`; the second reads the `_avg`
files. There is no root-level script any more — `score_dataset.py` and
`average_dataset_scores.py` were folded into `build_score_datasets.py`.

### The two objectives

`build_score_datasets.py` implements both, and they are **not** interchangeable:

- `original_objective` — Campaign 1 **as published** (paper Eq. 1–4): equal weights,
  `+10*phase_sep`, PDI hinged at 0.3. → `campaign1_scores_original_objective.csv`.
  **Act 1 figures use this.**
- `compute_component_scores` — Campaign 2's weighted form:
  `(3*size + 2*pdi + 1*zeta + 2*drug_loading + 3*perm) / max(1-phase_sep, 0.01)`,
  PDI hinged at 0.1. Everything else uses this.

`compute_component_scores` used to live in `score_dataset.py`, which imported
`MicroemulsionFormulation`. Both are gone; if upstream's objective changes, this function
drifts silently.

## Campaigns — do not mix them up

The repo spans two campaigns with **different design spaces**, and upstream `main` carries
Campaign 2's code. Deriving a Campaign 1 figure from Campaign 2's constants is the easy mistake.

- **Campaign 1** — published as `docs/paper/Gunawardena-2026_Microemulsion-BO.pdf` (Gunawardena, Chau et al.,
  *AAPS Open* 2026;12:34). **Table 1 of that paper is the authoritative design space** — read it
  rather than inferring ranges from code. Three continuous dials: oil volume 7.5–22.5 %, Smix
  **ratio** 3:1–1:3, sonication 0–3 min. It is a ratio because
  `Surfactant_V + Cosurfactant_V = 40.0` in every Campaign 1 row. 5 oils × 4 surfactants ×
  5 cosurfactants. 22 seed experiments (5 prior optima + 10 quasi-random + 7 repeats) then 25
  proposals in five batches of five. Its objective is Eq. 1–4: equal weights, ×10 phase-separation
  term, PDI hinged at 0.3 — implemented as `original_objective` in
  `analysis/build_score_datasets.py` as `original_objective`.
- **Campaign 2** — per-API transfer tracks (`Part2_A190`, `Part2_Feno`). Independent surfactant
  and cosurfactant volumes, wider oil range, a different objective and a tighter PDI hinge (0.1
  here vs the paper's 0.3).

Experiment-stage prefixes in `Exp`: `DoE*` (prior optima) · `Misc*` (repeats) · `Ran*`
(quasi-random screen) · `A`–`E` (Campaign 1 batches) · `F` (Campaign 2).

## Figure suites

`Figures/<Suite_Name>/` — a marimo notebook plus its `Output/` SVGs. `Figures/README.md` is the
directory guide; the rules are here.

- **A suite owns a slide, not a dataset.** Two figures on different slides are two suites, even
  when they read the same CSV.
- **Import, never restate.** Objective from `analysis/build_score_datasets.py`, ranges from the
  paper's Table 1. A suite that hardcodes a range drifts from the campaign it describes.
- **Export SVG** on a 1280×720 pixel grid, one data unit to one exported pixel.
- **Style follows the `Breaking-the-Boundaries` suites** value for value — white ground, 2 px
  black mirrored axis box, no gridlines, five type sizes, horizontal legend in a bottom gutter.
- **Keep the DLL guard** above `import marimo` (see Environment below).

### Campaign 1 design space — Table 1, confirmed against the CSV

| Parameter | Design space |
|---|---|
| Oil volume | 7.5 – 22.5 % |
| Smix ratio (surfactant : cosurfactant) | 3:1 – 1:3 |
| Sonication time | 0 – 3 min |
| Oil | Oleic Acid, Capryol 90, Soybean Oil, Maisine Oil, Capmul MCM |
| Surfactant | PEG 400, Tween 80, Tween 20, Labrasol |
| Cosurfactant | Tween 80, Transcutol HP, Propylene Glycol, Ethanol, PEG 400 |

PEG 400 and Tween 80 each appear in two columns — the space is roles a molecule can play, not
three independent lists. 5 × 4 × 5 = 100 declared systems; the campaign ran 15.

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
