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
| Ground | white paper and plot |
| Axes | hairline `#c3c2b7`, no mirror, ticks outside, `#e1e0d9` gridlines on the value axis only |
| Palette | Campaign 1 batches: blue ramp `#B4D2FC`→`#0A2455` · Campaign 2 batches, one ramp per API track: A190 purple `#D3B8E8`→`#5A2E8C`, fenofibrate green `#8FCFB3`→`#00572B` · revalidated Campaign 1 champion `#2067F4` · quasi-random screen `#C4C4C4` (`TRIAL_COLOR`) · DoE-OPT `#D55E00` |
| Marks | flat unoutlined bars at `width=0.62`; repeat dots size 9.5, ink at 70 %, ringed in the ground at `MARKER_RING = 2` |
| Title | left, `x=0.01`, grey subtitle carrying the phase-separated names |
| Legend | horizontal, centred, 60 px below the plot area |

Only the **layout** is upstream's — read `analysis/campaign_comparison.py` in
`C:/PyCharmProjects/BatchedBayes` rather than inferring it from these suites. The palette and the
marker come from `Breaking-the-Boundaries` instead, so the leaderboards wear upstream's structure and
the house's colour.

Two of those borrowings carry meaning, not just a hex:

- **The screen is grey** because in the `Breaking-the-Boundaries` campaign plots the screening phase
  is a `SCREEN_BAND` — `rgba(0, 0, 0, 0.055)`, a shaded region the optimisation runs across rather
  than a series competing with it. A bar chart cannot shade a region, so the screen wears that band
  as a fill: present, positioned, visibly not the campaign.
- **Batch order is lightness; hue is family.** Campaign 1's five batches are one blue in five
  steps, `#B4D2FC` (A) → `#0A2455` (E). A *sequential* scale claims order and nothing else, which
  is the one distinction the method makes — each batch was chosen by a surrogate refit on
  everything before it. Five unrelated hues would claim five kinds of experiment, which would be
  false.

  **Campaign 2 runs that device twice, once per API track**, because A190 and fenofibrate were
  separate optimisations and both boards sit on one slide: A190 is purple `#D3B8E8` (A) →
  `#9B6BC8` (B) → `#5A2E8C` (C), fenofibrate green `#8FCFB3` → `#009565` → `#00572B`. So inside
  Campaign 2 hue means **which API**, not which campaign.

  The two ramps are **matched step for step in lightness** — L\* ≈ 78 / 54 / 30 for both — so a
  batch sits at the same depth on either panel and only the hue differs. Depth reads across
  panels, hue reads within one, and neither channel does the other's job. The green is anchored
  on Okabe-Ito's bluish green `#009E73`, the colourblind-safe set `#D55E00` and `#E69F00` already
  come from; purple against green separates at ΔE 53 / 101 / 98 step for step. Under deuteranopia
  the palest step is the weak one (ΔE 14), a pale-tint limit Campaign 1's and Campaign 2's
  A-steps already shared — which is why panel titles and legend entries name the API too.

`Misc*` (prior-optimum repeats) is **not on the Campaign 1 board** — it is prior art the campaign
inherited, not campaign output. It is still in `data/` and still scored.

**A hue means the same thing wherever it appears.** The blue ramp is Campaign 1's batches on
both the progression slide and the Campaign 1 board, step for step, so `B4` is batch-B blue in
either place. `#D55E00` is DoE-OPT on all three. `#2067F4` — the blue ramp's midpoint, batch C —
is also the revalidated-champion hue on the Campaign 2 board, where the three champions are one
category rather than three batches; that is the one hex carrying two readings, and the two slides
never show it in both senses at once.

Note that one of those three, `F5`, is `Ran5` — the same formulation, renamed in the paper. It is
a quasi-random screen row, not optimiser output, and it still wears the champion hue because the
Campaign 2 board groups by *what the row is doing there*, not by where it came from.

Row labels are the formulation id, no rank number: `Ran*` renders as `S*` (screen) and `Misc*` as
`M*` (prior-optimum repeat). Rank is the row order, so it is not spelled out twice.

Keep the DLL guard above `import marimo` — see **Environment** in [CLAUDE.md](../CLAUDE.md).

## Suites

| Folder | Slide | Paper figure |
|---|---|---|
| `Campaign1_Leaderboard/` | The optimiser batches and the quasi-random screen against DoE-OPT | — |
| `Campaign2_Leaderboard/` | Both API tracks ranked, with the Campaign 1 champions and DoE-OPT | — |
| `Design_Space/` | DoE → Batched Bayes: what the optimiser could search that the screening design could not | Table 1 |
| `Campaign1_Progress/` | Objective per formulation in campaign order, running best | Fig. 2 |
| `Campaign2_Progress/` | The same, for Campaign 2's two API tracks side by side | — |
| `Surrogate_Performance/` | Parity plots per target across the five batches | Fig. 1 |
| `Stability/` | 30-day storage stability, blank and loaded | Figs. 3–4 |
| `Permeability/` | Effective permeability, A190- and fenofibrate-loaded | Fig. 5 |

The two leaderboards, `Campaign1_Progress/` and `Campaign2_Progress/` are built; the rest are
not. `Design_Space/` is next.

The two progression suites are the ones with a **spliced value axis**.

In `Campaign1_Progress/`, thirteen Campaign 1 formulations phase-separated, and the objective's
×10 term parks every one of them at 31 while the stable campaign lives below 1.1. It keeps **one** panel: everything at or below
`BREAK_AT = 1.25` is drawn where it falls, the separated cluster is drawn `BREAK_GAP` above that
as **squares** and ticked with its true 31, and the skip is announced on each upright of the axis
box and nowhere else. The uprights are drawn as shapes rather than by the y axis, in two segments
with a real gap between the strokes — an axis line is drawn whole or not at all, and nothing here
is painted over to hide it. Nothing inside the panel is cut by the break — no band, no
section rule, no marker, no error bar — which is what a two-panel break costs and this does not.

It adds two hues to the shared palette, both prior art: `#E69F00` the previous DoE screen and
`#8C6E54` the `Misc*` formulations. `#D55E00` is still DoE-OPT, and the blue ramp is the Campaign
1 board's, step for step. Its screen grey is `#8A8A8A` rather than the board's `#C4C4C4`:
the whole initial dataset — DoE through the random screen — sits on the `rgba(0, 0, 0, 0.055)`
band, and `TRIAL_COLOR` on that ground stops being a mark.

`Campaign2_Progress/` is the same slide for Campaign 2, and **two panels, because Campaign 2 ran
two independent tracks** — A190 and fenofibrate were separate optimisations, so they are two
progressions rather than one series split in half. They share a value axis and its splice (four
phase separations park at 5438 while the stable campaign lives between 0.13 and 2.98, so
`BREAK_AT = 3.75` — the axis runs 0 · 0.5 · … · 3.5 and then skips) and each panel is a closed, separately ticked box; they do not share an x
axis, because experiment 7 on one track has nothing to do with experiment 7 on the other. The
four break marks are placed once against paper coordinates, which is why both value axes take the
same range and the same y domain.

It adds **no hues of its own**: `#D55E00` is DoE-OPT, `#2067F4` a revalidated Campaign 1
champion, and the two track ramps are the Campaign 2 board's, step for step. Two things it does *not*
inherit from the Campaign 1 slide:

- **No specification triangles.** Campaign 2 declares no target table of its own, and carrying
  the paper's Table 2 over would mark 7 of 19 A190 rows and 9 of 18 fenofibrate rows. A mark half
  the field wears distinguishes nothing, so the vocabulary is two shapes: circle and square.
- **Only loaded rows appear**, and only this panel's API. Campaign 2's objective reads drug
  loading and permeability, which the blank Campaign 1 history in the per-API CSVs does not have.
  `section_of` returns `None` for those rows and for the other track's champions, so the filter is
  the section map rather than a hand-written mask in the figure.

`A` is A190 and `F` is fenofibrate, in the batch prefix (`A-B3`) and the revalidation suffix
(`B4_A`) alike. The data cell asserts that against each row's `API_Name`, so the panel a row lands
on is checked against what it was loaded with rather than inferred from its id.

`DoEOPT` is on the A190 panel only, as on the Campaign 2 board and for the same reason — there is
no fenofibrate measurement of it. It also has no drug loading and no permeability, and the
objective scores a missing output as `0`, so its 0.79 is its size and PDI alone. It is the
screening baseline on that slide, not a like-for-like score.

### The band is the prior *optima*, not the whole prior

The band is captioned **Prior optima**, and the distinction is load-bearing: the surrogate trained
on more than the slide draws. Upstream's `MicroemulsionFormulation.get_dataset`
(`BayesianOptimization/applications.py`, `main`) does a plain `pd.read_csv` of the dataset and
returns **every row unfiltered**; `API_Name` is one of `input_headers` and is one-hot encoded, so
the blank Campaign 1 measurements are *training data*, not excluded rows.
`fixed_categories = {"API_Name": ...}  # Change per campaign` pins the proposal mesh to one API —
it does not filter the fit. Upstream's comprehensive CSV is 237 rows (141 blank, 48 A190, 48
fenofibrate), and each per-API file in `data/` is that file minus the other track's fifteen
batches. So a track's prior is all 47 blank Campaign 1 formulations, all six loaded revalidation
runs, and its own earlier batches.

What the band draws is the subset **loaded with that panel's API** — the marks whose objective is
a like-for-like Campaign 2 score. Drawing 47 blank rows with two of six outputs silently zeroed
would be a worse claim than leaving them off and saying so.

A `Blank_Campaign/` suite existed at `20600d7` and was deleted at `762e87c` — it imported the
pruned optimiser package. Recover it from history if wanted, but rewire it onto `objectives.py`
and `data/`.

Conventions and the numbers a suite must use are in [CLAUDE.md](../CLAUDE.md) — read **Campaigns**
and **Figure suites** before building one.
