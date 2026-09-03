# Figures

Slide figure suites. One folder per suite:

```
objectives.py                 campaign1() / campaign2() — import, never restate
<Suite_Name>/
├── <Suite_Name>_Figures.py   marimo notebook — the figure source
├── Output/                   exported SVGs, committed
└── __marimo__/               session cache, gitignored
```

```bash
conda run -n BatchedBayes marimo edit Figures/<Suite_Name>/<Suite_Name>_Figures.py
```

A suite reads raw measurements straight from `data/`, scores them with `objectives.py`,
and draws. There are no intermediate datasets.

```python
sys.path.insert(0, str(REPO / "Figures"))
from objectives import campaign1, campaign2
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

A `Blank_Campaign/` suite existed at `20600d7` and was deleted at `762e87c` — it
imported the pruned optimiser package. Recover it from history if it is wanted back,
but rewire it onto `objectives.py` and `data/`.

Conventions and the numbers a suite must use are in [CLAUDE.md](../CLAUDE.md) — read
**Campaigns** and **Figure suites** before building one.
