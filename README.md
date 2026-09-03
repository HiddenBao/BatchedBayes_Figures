# BatchedBayes_Figures

Slide figures for the BatchedBayes microemulsion campaigns.

The Bayesian optimiser itself is **not** in this repo — it lives upstream at
[mcgillresearchgroup/BatchedBayes](https://github.com/mcgillresearchgroup/BatchedBayes).
This repo keeps the measured data, the two objective functions, and the figure suites
built on them. Nothing here is generated; there is no pipeline to run first.

```
data/                 measured formulation data + descriptor lookup tables
Figures/
  objectives.py       campaign1() and campaign2() — the only scoring code
  <Suite_Name>/       a marimo notebook + its Output/ SVGs
docs/paper/           the published Campaign 1 paper
```

See [CLAUDE.md](CLAUDE.md) for the campaign distinctions and how to query upstream,
and [Figures/README.md](Figures/README.md) for the suite convention.

## Run

```
conda run -n BatchedBayes marimo edit Figures/<Suite_Name>/<Suite_Name>_Figures.py
```
