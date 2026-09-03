# Figures

Slide figure suites, built the same way as the
[`Breaking-the-Boundaries`](https://github.com/HiddenBao/Breaking-the-Boundaries) suites.

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

A suite reads raw measurements straight from `data/`, scores them with `objectives.py`, and
draws. There are no intermediate datasets.

## The workflow

Each notebook runs the same cells in the same order:

1. **Environment check** — `pio.renderers.default = 'plotly_mimetype'`, assert `kaleido` is
   importable, print interpreter / python / pandas / plotly versions.
2. **Paths, canvas and export** — `_find_repo_root` walks up looking for `Figures/objectives.py`
   rather than counting `..`, so a suite survives being moved and fails loudly instead of reading
   the wrong tree. Sets `FIG_WIDTH = 1280`, `FIG_HEIGHT = 720`, `EXPORT_FORMATS`, `PNG_SCALE`.
3. **Shared chrome** — colour tokens, the five type sizes, `FONT_FAMILY`, `AXIS_COMMON`, panel
   domains. A markdown cell above it states what each hue *means*.
4. **The data** — read `data/`, score with `objectives.py`, rank.
5. **The figure** — one `build_*()` returning `go.Figure(data=traces, layout=layout)`. Build a
   single `go.Layout` with explicit `xaxis`/`xaxis2`/`yaxis`/`yaxis2` and `domain=`; do **not**
   use `make_subplots` or scattered `update_xaxes`/`update_layout` calls.
6. **Export** — write each figure to `Output/` at its native size.

Two ways to draw, both in the reference suites:

- **Real axes** for data plots — `AXIS_COMMON` gives the white ground, 2 px black mirrored axis
  box and no gridlines. Both leaderboards use this.
- **Pixel grid** (`blank_layout`) for schematics — hidden axes, `x` in `[0, width]`, `y` in
  `[height, 0]`, so one data unit is one exported pixel with the origin top left.

Gotcha: in an annotation, `xref`/`yref` of `'paper'` is the **plot area**, not the canvas. Above
the axes means `y > 1`; below them means `y < 0`.

## Style

Two chromes live here. The cell workflow above is the same either way — only the tokens differ.

**House (`Breaking-the-Boundaries`)** — the default for a new suite.

| | |
|---|---|
| Canvas | 1280 × 720 |
| Type scale | 20 title · 18 axis title · 18 tick · 14 legend · 14 annotation — five sizes, no more |
| Font | `Open Sans, verdana, arial, sans-serif` |
| Ground | white paper and plot |
| Axes | 2 px black box, `mirror=True`, ticks outside, no gridlines |
| Title | centred, `x=0.5`, with an optional grey subtitle line |
| Legend | horizontal, centred in a bottom gutter (`LEGEND_MARGIN`) |

**Upstream analysis** — both leaderboards, so they sit beside `BatchedBayes:analysis/figures/`.
Transcribed from that notebook's `plotly_layout` / `axis_style` / `legend_below`.

| | |
|---|---|
| Canvas | 1280 × 720 (upstream sizes to content: `44 * rows + 210`) |
| Type scale | 16 title · 11 subtitle · 12 panel title · 12 axis title · 11 tick · 11 legend |
| Font | `sans-serif`, `template='none'` |
| Ground | `#fcfcfb` paper and plot |
| Axes | hairline `#c3c2b7`, no mirror, ticks outside, `#e1e0d9` gridlines on the value axis only |
| Palette | DoE-OPT `#2a78d6` · Campaign 1 `#1baf7a` · Campaign 2 `#eda100` |
| Marks | flat unoutlined bars at `width=0.62`; repeat dots size 9, ink at 70 %, ringed in the ground |
| Title | left, `x=0.01`, grey subtitle carrying the phase-separated names |
| Legend | horizontal, centred, 60 px below the plot area |

Upstream is the source of truth for the second one — read `analysis/campaign_comparison.py` in
`C:/PyCharmProjects/BatchedBayes` rather than inferring it from these suites.

Keep the DLL guard above `import marimo` — see **Environment** in [CLAUDE.md](../CLAUDE.md).

## Suites

| Folder | Slide | Paper figure |
|---|---|---|
| `Campaign1_Leaderboard/` | Every blank formulation ranked against the DoE-OPT screening optimum | — |
| `Campaign2_Leaderboard/` | Both API tracks ranked, with the Campaign 1 champions and DoE-OPT | — |
| `Design_Space/` | DoE → Batched Bayes: what the optimiser could search that the screening design could not | Table 1 |
| `Campaign_Progress/` | Objective per formulation in campaign order, running best | Fig. 2 |
| `Surrogate_Performance/` | Parity plots per target across the five batches | Fig. 1 |
| `Stability/` | 30-day storage stability, blank and loaded | Figs. 3–4 |
| `Permeability/` | Effective permeability, A190- and fenofibrate-loaded | Fig. 5 |

The two leaderboards are built; the rest are not. `Design_Space/` is next.

A `Blank_Campaign/` suite existed at `20600d7` and was deleted at `762e87c` — it imported the
pruned optimiser package. Recover it from history if wanted, but rewire it onto `objectives.py`
and `data/`.

Conventions and the numbers a suite must use are in [CLAUDE.md](../CLAUDE.md) — read **Campaigns**
and **Figure suites** before building one.
