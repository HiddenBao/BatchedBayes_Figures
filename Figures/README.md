# Figures

Slide figure suites for the deck. Distinct from `analysis/figures/`, which holds the working
plots the `campaign_comparison.py` analysis notebook emits — those are for reading on screen,
these are for projecting.

## One folder per suite

Each suite is a self-contained marimo notebook plus its exports:

```
Figures/
└── <Suite_Name>/
    ├── <Suite_Name>_Figures.py   marimo notebook — the figure source, a plain Python module
    ├── Output/                   exported SVGs, one per figure, committed
    └── __marimo__/               marimo session cache — gitignored, never committed
```

Rules that keep the suites consistent:

- **A suite owns a slide, not a dataset.** If two figures belong to different slides, they belong
  in different suites, even when they read the same CSV.
- **Import, never restate.** Pull the objective from `score_dataset.compute_component_scores` and
  the ranges from the paper's Table 1 (`docs/paper/`). A suite that hardcodes a range will drift
  from the campaign it claims to describe.
- **Export SVG.** On a 1280×720 pixel grid, one data unit to one exported pixel.
- **Style follows the `Breaking-the-Boundaries` suites**, value for value — white ground, 2 px
  black mirrored axis box, no gridlines, five type sizes, horizontal legend in a bottom gutter.
- **Keep the DLL guard.** Every notebook opens with the Windows conda delay-load guard above
  `import marimo`. Without it a PyCharm launch dies with `0xC06D007F` and no traceback.

Run one with:

```bash
conda run -n BatchedBayes marimo edit Figures/<Suite_Name>/<Suite_Name>_Figures.py
conda run -n BatchedBayes python Figures/<Suite_Name>/<Suite_Name>_Figures.py
```

## Planned suites

Campaign 1 is the published campaign (`docs/paper/s41120-026-00176-0.pdf`); its figure numbers are
given so a suite can be checked against what was published.

| Folder | Slide it carries | Paper figure |
|---|---|---|
| `Design_Space/` | DoE → Batched Bayes: what the optimiser could search that the screening design could not | Table 1 |
| `Campaign_Progress/` | Objective per formulation in campaign order, running best, phase-separated runs on a strip below | Fig. 2 |
| `Surrogate_Performance/` | Parity plots per target across the five batches — does the surrogate hold up as data arrives | Fig. 1 |
| `Stability/` | 30-day storage stability, blank and loaded | Fig. 3, Fig. 4 |
| `Permeability/` | Effective permeability of the A190- and fenofibrate-loaded systems | Fig. 5 |

Nothing here is built yet. `Design_Space/` is next; the concept pitch behind it is a published
artifact, not a file in this repo.

## Campaign 1 design space — the numbers a suite should use

From Table 1 of the paper, and confirmed against `data/MicroemulsionFormulation_Comprehensive.csv`:

| Parameter | Design space |
|---|---|
| Oil volume | 7.5 – 22.5 % |
| Smix ratio (surfactant : cosurfactant) | 3:1 – 1:3 |
| Sonication time | 0 – 3 min |
| Oil | Oleic Acid, Capryol 90, Soybean Oil, Maisine Oil, Capmul MCM |
| Surfactant | PEG 400, Tween 80, Tween 20, Labrasol |
| Cosurfactant | Tween 80, Transcutol HP, Propylene Glycol, Ethanol, PEG 400 |

Two things this table settles, both easy to get wrong:

- **Smix is a ratio, not two volumes.** `Surfactant_V + Cosurfactant_V = 40.0` in every Campaign 1
  row. Campaign 1 is a **three-dial** problem. Do not draw it as four — `applications.py` upstream
  describes Campaign 2, where the two volumes are independent.
- **Campaign 1's objective is not the one in `score_dataset.py`.** The paper weights every response
  equally with a ×10 phase-separation term and hinges PDI at 0.3 (Eq. 1–4); `score_dataset.py`
  implements Campaign 2's weighted form with a 0.1 hinge. `analysis/build_score_datasets.py`
  carries the published version as `original_objective` → `campaign1_scores_original_objective.csv`.
  **Campaign 1 figures use that file.**
