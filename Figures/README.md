# Figures

Slide figure suites. Distinct from `analysis/figures/`, which holds plots the
`campaign_comparison.py` notebook emits for reading on screen — these are for projecting.

One folder per suite:

```
<Suite_Name>/
├── <Suite_Name>_Figures.py   marimo notebook — the figure source
├── Output/                   exported SVGs, committed
└── __marimo__/               session cache, gitignored
```

```bash
conda run -n BatchedBayes marimo edit Figures/<Suite_Name>/<Suite_Name>_Figures.py
```

## Suites

| Folder | Slide | Paper figure |
|---|---|---|
| `Design_Space/` | DoE → Batched Bayes: what the optimiser could search that the screening design could not | Table 1 |
| `Campaign_Progress/` | Objective per formulation in campaign order, running best | Fig. 2 |
| `Surrogate_Performance/` | Parity plots per target across the five batches | Fig. 1 |
| `Stability/` | 30-day storage stability, blank and loaded | Figs. 3–4 |
| `Permeability/` | Effective permeability, A190- and fenofibrate-loaded | Fig. 5 |

None built yet; `Design_Space/` is next.

Conventions and the numbers a suite must use are in [CLAUDE.md](../CLAUDE.md) — read
**Campaigns** and **Figure suites** before building one.
