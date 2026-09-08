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

On the **Campaign 2** board the id's API tag comes off as well, because each panel is one API from
top to bottom and the panel title already carries it: `A-B3` and `F-B3` are both `B3`, `B4_A` and
`B4_F` are both `Campaign 1 · B4`. What the label carries instead is the campaign, which is the one
thing the panel cannot say — a bare id is Campaign 2's own, `Campaign 1 · ` is a revalidated
Campaign 1 formulation, and `DoE-OPT` is neither. `build_board` asserts the labels stay unique.

The prefix is **spelled out, not abbreviated**. `C1` was the obvious short form and it is the one
thing that board cannot use: `C1` is already a row on it — Campaign 2's batch C, proposal 1 — and a
token that means two things on one figure is worth the 40 px of left margin it saves. Only three of
seventeen rows carry the prefix, and those three are what the whole board is a comparison against.

One formulation carries **four names**, and the boards resolve them to one. The dataset calls the
blank `Ran5` and its loaded re-measurements `F5_A` / `F5_F`; the paper's Table 3 calls it `F5`. Both
boards call it **`S5`** — `S5` on the Campaign 1 board as a screen row, `Campaign 1 · S5` on the Campaign 2
board — because a reader has to be able to follow one row from slide to slide, so the deck name
beats the id. `Campaign1_Leaderboard` asserts `Ran5` and `F5_A` are the same composition, so the
naming fails loudly if the data ever moves under it.

Keep the DLL guard above `import marimo` — see **Environment** in [CLAUDE.md](../CLAUDE.md).

## Suites

| Folder | Slide | Paper figure |
|---|---|---|
| `Campaign1_Leaderboard/` | The optimiser batches and the quasi-random screen against DoE-OPT | — |
| `Campaign1_Leaderboard/` (`_Top5`) | The same board, second animation state: the top five, split by whether it reached drug loading | — |
| `Campaign2_Leaderboard/` | Both API tracks ranked, with the Campaign 1 champions and DoE-OPT | — |
| `Design_Space/` (`_DoE`) | What the Box-Behnken design produced, against the Table 2 targets | Tables 1–2 |
| `Design_Space/` (`_Expansion`) | That design as one system of a hundred, and its three settings as ranges | Table 1 |
| `Design_Space_Transition/` (`_Explored`) | Of Table 1's hundred systems, the twenty-four Campaign 1 made | Table 1 |
| `Design_Space_Transition/` (`_Narrowed`) | The same field cut to the forty-eight Campaign 2 can propose | — |
| `Loaded_Champions/` (`_Physicochemical`) | Campaign 1's three champions and DoE-OPT, blank and drug-loaded — size, PDI and ζ, no boundaries | — |
| `Loaded_Champions/` (`_Barriers`) | The same rows against Campaign 2's objective barriers, plus drug loading and permeability | — |
| `Champions_Head_to_Head/` | Campaign 2's best three per track against Campaign 1's three revalidated champions — the objective and every output it reads | — |
| `Campaign1_Progress/` | Objective per formulation in campaign order, running best | Fig. 2 |
| `Campaign2_Progress/` | The same, for Campaign 2's two API tracks side by side | — |
| `Surrogate_Performance/` | Parity plots per target across the five batches | Fig. 1 |
| `Stability/` | 30-day storage stability, blank and loaded | Figs. 3–4 |
| `Permeability/` | Effective permeability, A190- and fenofibrate-loaded | Fig. 5 |

The two leaderboards, `Campaign1_Progress/`, `Campaign2_Progress/`, `Design_Space/`,
`Design_Space_Transition/`, `Loaded_Champions/` and `Champions_Head_to_Head/` are built; the rest
are not.

### `Loaded_Champions/` — one slide built up, and barriers probed rather than restated

Four rows — `B4`, `S5`, `E2` (the three champions `Campaign1_Leaderboard` marks as `CARRIED`) and
`DoE-OPT` — each carrying up to three marks: the blank measurement and one per API.

**Every hue is a leaderboard token.** `#2067F4` is the blank Campaign 1 measurement (the
revalidated-champion hue, for the same three rows in the same role), `#5A2E8C` A190 and `#00572B`
fenofibrate — the darkest, lightness-matched step of each track's ramp — and `#D55E00` DoE-OPT,
as everywhere else in the deck. So **hue is the API, except on DoE-OPT**, which keeps the one
colour this project holds constant across every figure rather than turning purple to say "A190";
the Campaign 2 board runs that same licence. Shape is the second channel — circle blank, diamond
A190, square fenofibrate — and DoE-OPT keeps the A190 diamond, so on that row shape says which
API while hue says which role.

**Two exports, one builder.** `build_slide()` takes the panel list and a `barriers` flag, so the
rows, offsets, rules, gutter and type are shared by construction:

| export | panels | barriers |
|---|---|---|
| `_Physicochemical` | size · PDI · \|ζ\| | none — nothing on it is a pass or a fail |
| `_Barriers` | those three, plus drug loading and permeability | Campaign 2's |

Two of the three shared panels keep the same range in both, so a reader who sees both reads one
scale. Only the PDI ticks and the zeta range differ, and both differences are the barriers' doing:
the PDI panel is ticked at 0.1 and 0.3 *because* they are boundaries, and zeta runs to 12 only to
leave room for one at 10. The suite asserts the physicochemical panels are the barrier figure's
first three, in order, and that none of them carries a `pass_range`, a `line` or a `soft_line`.

**Each formulation's band is closed by a hairline rule.** Offsets alone group the marks only while
a reader trusts the spacing, and on a panel where one row's marks are spread and its neighbour's
are clustered, the spacing stops being obvious — so the grouping is structural: three marks between
two rules are one formulation.

The rules are drawn **one segment per panel**, not once across the canvas. A paper-width rule is
the obvious implementation and the wrong drawing: it runs on through the gaps between panels and
through the label gutter, turning the white space that separates five boxes into ruled space.
Every rule is also the **same weight, colour and dash**, DoE-OPT's included — that section break
is already said twice, by its hue and by its band height. **Bands are not all one height**: a
champion's holds three marks and is a full unit, DoE-OPT's holds one and is `DOE_BAND` of a unit.
Band edges are computed once and the rules, row labels and axis range all come off them.

`AXIS_COMMON` aside, one more type departure: **axis titles are set on the body face**, not the
display face the other suites use. Five panel names in a row is a lot of display type for a set of
labels, and at 18 pt its heavier strokes crowded the ticks. Ticks stay display.

**Every boundary it draws is probed out of `objectives.py`, not read off it.** The cell sweeps one
output at a time through `campaign2` and asserts the kink is where the constant says — size 100 nm,
PDI 0.1, |ζ| 10 mV, loading 100 ± 5 %, permeability 20 × 10⁻⁶ — and separately asserts `campaign1`
does *not* read loading or permeability, which is the barrier slide's "two new axes" claim. Campaign 1's
superseded PDI hinge at 0.3 is drawn dotted behind the dashed 0.1, and is probed against
`campaign1` as the quartering **step** it is rather than as a slope change.

**DoE-OPT is one mark, and that is a decision.** `data/` carries two different `DoEOPT`
measurements — the comprehensive CSV's, tagged `A190` with loading and permeability, and the
per-API CSVs', tagged `blank` — and reading them as a blank/loaded pair is the trap. They are one
row before and after upstream's `2cba4f2` rebuild, which re-tagged all five `DoE*` rows and which
the per-API files never received; the other four were re-tagged `A190` with no loading number at
all. The comprehensive file is this suite's ground truth, it is the only file opened, and the
suite asserts `DoEOPT` there is still the `A190`-tagged row. See **`DoEOPT`** in
[CLAUDE.md](../CLAUDE.md). There is no fenofibrate DoE-OPT in any file either.

Its `AXIS_COMMON` pins `tickangle=0`, which the other suites do not need. Five panels at 18 pt is
tight enough that plotly silently rotates a crowded tick row to vertical — which on one panel of
five reads as a different kind of axis and drops that panel's title out of line. Pinning the angle
turns a silent re-layout into a visible collision; the fix for a collision is fewer ticks, which is
why drug loading is ticked at its two dead-zone edges and not at 100.

### `Champions_Head_to_Head/` — the Campaign 2 board opened up

`Loaded_Champions_Barriers`' grammar with different rows: six panels — **the objective, then the
five outputs it is made of** — drawn twice, once per API, as **two closed axis boxes** rather than
one box with a rule across it. Each box holds **Campaign 2's best three on that track and the three
Campaign 1 champions revalidated with that API**, ranked together by the objective, both campaigns
interleaved. Where the Campaign 1 rows land is the point, so grouping them would make the slide
take two readings instead of one.

The two boxes are two rankings that share a scale, not one ranking split in half — a formulation's
objective depends on which API it was loaded with, so the twelve rows are not one ordering. Both
carry their own x ticks so either reads alone; the axis titles are under the bottom box only,
because a column is one scale and naming it twice would claim two. Each box's caption is
left-aligned over the row-label gutter: it names the rows, and a caption centred over six panels
reads as a title for whichever one it lands on.

Campaign 2's three are **computed from the data**, not typed — score-then-average over that track's
own proposals — and then asserted against the set the slide was drawn for, so a data change fails
rather than quietly redrawing the comparison. Campaign 1's three are `Loaded_Champions`' rows and
are named against `Campaign1_Leaderboard`'s `CARRIED`; they are *not* the Campaign 1 board's top
three, because `D3` ranks second there and was never loaded.

**Hue is the campaign here, and that is the Campaign 2 board's palette, not `Loaded_Champions`'.**
On that suite purple and green mean *loaded with this API*; here every mark is loaded and the
section already says which API, so hue carries the one thing a section cannot — `#2067F4` a
revalidated Campaign 1 champion, `#5A2E8C` Campaign 2's A190 track, `#00572B` its fenofibrate
track. That is exactly what the Campaign 2 board does with the same rows. The track ramps are used
at **one step, not three**: a ramp claims a batch order, and three rows of a track are not the
track. Shape stays `Loaded_Champions`' — diamond A190, square fenofibrate — so hue says whose a
formulation is and shape says which API.

The objective panel carries **no barrier and no shaded band**: `campaign2` is a loss with no pass
mark, and shading a side of it would invent a specification the optimiser does not have. Its axis
starts below zero, because the PDI and permeability terms both have a bonus side. Four of the five
measurement panels keep `Loaded_Champions`' ranges exactly, so a value sits in the same place on
both slides.

**Size is the fifth, and it is the one panel in the deck that draws a goal rather than a barrier.**
`campaign2` charges nothing below 100 nm; the project is aiming at 10, where 11 nm is better than
24 and 24 better than 87 — and neither the objective nor a flat pass band can say so. Two changes
carry it. The band is **graded**, deepening from the `PASS_BAND` tone at the 100 nm barrier to its
darkest at 10 and staying there below it, so the shading says *further in is better* rather than
just *inside*; the dashed barrier at 100 is untouched, so what the objective charges and what the
project wants are two marks. And the axis is **logarithmic**, because on the barrier slide's linear
0–270 nine of these twelve rows fall inside the first tenth of the box and 10 nm sits four pixels
off the axis line — there is nowhere to draw a goal, and no way to see 11 against 24.

The 10 nm goal is **the one number on the slide that is not in `objectives.py`**, so the barriers
cell probes it the other way round: it asserts the size score is *flat* at 10, 50 and 100 nm.
Everything else there is checked to show the objective bends; the goal is checked to show it does
not. Two plotly traps come with the log axis and both fail silently — `range` is in log10 while
data, `tickvals` and shape coordinates are in data units (an older contract put shapes in log10,
under which every band and barrier on that panel lands off-axis and simply does not draw), and a
log axis cannot draw an error bar through zero, so the lower whisker is clamped to the axis
minimum. `SHAPES_IN_LOG_UNITS` names the first and an assertion checks it.

**It carries no subtitle, its title is a question, and neither the graded band nor the top box's
scale is spelled out.** A grey line under the title is where a slide states its conclusion, and the
things such a line would carry — which rows these are, what they are ranked on — are already in the
row labels, the box captions and the axis titles. The graded band gets no legend swatch, because a
swatch is a caption for one tone deepening across one panel with its goal ticked underneath. And
the top box shows no x ticks: both boxes share a range by construction, so a second tick row is the
same numbers twice and an invitation to check they match.

Two things the sixth panel costs. **Panel widths are not equal** — each panel's `width` is the
share of the row it takes, set by the title and tick set it has to carry; there is no shared scale
between panels, so a width claims nothing about the values. And **row labels are set at 14 pt**,
the one type departure: twelve of them at the tick 18 would give the gutter a third of the canvas.
Two titles are shortened for the same reason — `Objective` and `Zeta, |ζ| mV`. Shortened rather
than set smaller: once past the house scale is enough. `Objective` is unambiguous because there is
one score column and every row on both boxes is ranked on it; the only other objective on the
figure is the dotted PDI hinge, which the legend names as Campaign 1's.

### `Design_Space/` is two slides, one suite

It owns **two slides** rather than one, because both rest on the same asserted design — the same
coded positions, the same Table 1 ranges, the same five rows. Splitting them would duplicate that
spec, and the spec is the part that must not drift.

`BBD_POINTS` is generated from the design's own rule — exactly one coded zero, the other two
coordinates at ±1 — never typed out. A three-factor Box-Behnken design *is* a cube sampled at its
twelve edge midpoints plus its centre; `cube_traces()` projects it, and slide two draws it.

**Slide one draws no cube.** That geometry is drawn by hand in the deck. Slide one is the
measurements and nothing else: two panels, five rows, two targets, one footnote.

#### Drawing the cube: trimetric, not isometric

```
VIEW = (-1.00, -0.62, 0.78)        # (oil, Smix, sonication), viewer toward low-low, above
right = normalise(z_hat x VIEW);  up = normalise(VIEW x right)
x =  (p · right) * S
y = -(p · up)    * S               # y increases DOWNWARD
```

**Isometric is the wrong drawing here, not merely a plainer one.** Equal view components give
equal foreshortening, a regular-hexagon silhouette, and two opposite corners on the same point —
so front and back are formally indistinguishable, and `DoE-OPT` landed exactly on one of the
design's own runs. Three *unequal* components separate every corner, foreshorten the three axes
differently, and leave a well-defined hidden corner. The suite asserts a minimum separation of
0.25 half-edges across every position drawn, so a future edit to `VIEW` cannot quietly collapse
two points again. Current worst case is 0.331.

Depth is then carried two ways: the three edges meeting the hidden corner are **dotted**, and
sample points are drawn **back to front with a white halo**, so a near point occludes a far one.

The origin corner `(−1, −1, −1)` is at the bottom front and every factor increases away from it:
`+oil` up-right, `+Smix` up-left, `+sonication` straight up. Sonication is labelled on the
right-hand silhouette edge `(+1, −1, −1)` → `(+1, −1, +1)`, where the oil axis ends — a vertical
edge nearer the middle would carry its label across the drawing.

**Smix runs 3:1 → 1:1 → 1:3**, low coded level to high, as Table 1 writes the range: the low end
is surfactant-heavy. The sign is a labelling convention rather than a measurement, so the data
cell resolves each run's coded level from its actual `Surfactant_V` / `Cosurfactant_V` and asserts
it, rather than trusting a hand-written table.

**`data/` holds 4 of the design's 12 edge runs, and that is experimental, not clerical.** The rest
of the box phase-separated, and the ones that did not were made before a standardised protocol. The
four here are the design's comparable survivors — the only runs that can go on one axis against the
Table 2 targets at all. Slide one's footnote says so, because a reader will otherwise ask where the
other rows went.

### `Design_Space_Transition/` — one slide, two states

Campaign 1's design space becoming Campaign 2's. Two exports, one move each: mark what
Campaign 1 made, then cut the field to what Campaign 2 can propose. **It reuses
`Design_Space_Expansion`'s 5 × 20 field on purpose** — slide two of Act 1 already taught the reader that grid, and re-teaching it in a new
geometry to make a *different* point would spend the slide on the frame.

**Both states are one builder, two category lists.** `build_grid_state()` computes the cell
pitch, the origin and the dial strip from Campaign 1's full lists *whatever it is asked to draw*,
so state 2's cells sit on state 1's pixels and the two exports lay over each other without a mark
moving. The dropped row, block and column simply go. This is the `Campaign1_Leaderboard` pattern
from **Animation states** below, applied to a schematic instead of a bar chart.

The strip under the grid is `Design_Space_Expansion`'s, kept whole: each dial drawn twice, the
Box-Behnken design's three stops above Campaign 1's continuous range. Table 1 did not widen the
dials — it removed the stops between them, and that reading needs both rows. It is **identical
in both states**: a strip that also moved would give the reader two things to track in one
step. `#E69F00` is the design, as it is in
`Design_Space/` and `Campaign1_Progress/`.

**The claim the cut rests on is asserted, not asserted-looking.** For all three roles the mesh is
a subset of Table 1's list, one name lighter each (Oleic acid · PEG 400 · Tween 80), and every
meshed name is one Campaign 1 actually measured — `mesh - measured` is empty everywhere. So the
optimiser proposes only from ingredients that had already been in a vial, and the five names
Campaign 2 *declares* but never meshes (Kolliphor RH 40, Pluronic F-68, Glycerin, Cremophor EL,
Safflower oil) have zero rows in every dataset in either repo. Of the 24 explored systems 19
survive and 5 fall out, and the suite checks that each of the five falls out because of one of
those three dropped names: **the cut lands on the vocabulary, not on the evidence.**

`EXPLORED` is read out of `data/`, never listed. Explored means *measured*, not *liked* — a phase
separation counts as much as a champion, because the state is about reach.

**Purple is the borrowing that needs saying.** `#5A2E8C` is the A190 track's darkest step on the
Campaign 2 board; here it means Campaign 2 as a whole. That would be wrong on a slide that drew
either track — this one draws neither, and no green appears on it, so the hue cannot be read as
"A190 rather than fenofibrate". The alternative was to draw Campaign 2 as an ink boundary, the
device `Design_Space/` uses for the Table 2 targets; the hue won because the deck asked for one
colour to carry across both states, and ink already belongs to the grid's labels. `#2067F4` runs under the
same licence `Design_Space/` states: no batches on the slide, so the blue is the family.

**`pixel_axes()` takes an `anchor` pair here**, unlike `Design_Space/`'s. Every plotly axis after
the first anchors to `x` / `y` by default, which puts a second pair's line — and on a *visible*
pair its ticks and its title — in the first pair's panel. `Design_Space/` never noticed because
both of its pairs are invisible. Neither state here has a visible axis either, so nothing goes
wrong today; the argument is threaded through from the start so the first visible axis added does
not have to find the bug.

### Animation states

A suite may export more than one SVG of **one slide** when the slide is built up in PowerPoint.
`Campaign1_Leaderboard` is the case to copy: both states come out of a single `build_leaderboard`
that takes the row-to-series map as an argument, so rows, order, bar lengths, axis range and type
are shared by construction and the exports lay over each other without a mark moving. A state that
also re-ranks or re-labels is a different chart wearing the same title, not an animation step.

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
phase separations park at 104 while the stable campaign lives between 0.13 and 2.98, so
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
