# --- Windows + conda DLL guard: must run before *any* other import --------------------------
# The numeric wheels delay-load their DLLs (MKL, OpenBLAS, libstdc++) from <env>/Library/bin,
# which is only on PATH once the environment is *activated*. PyCharm runs the configured conda
# interpreter directly rather than through `conda activate`, so a Run/Debug launch -- and a
# notebook kernel started the same way -- dies with exit code 0xC06D007F / 3228369023,
# STATUS_DELAY_LOAD_FAILED and no traceback.
#
# This sits above `import marimo` on purpose: marimo pulls in the numeric stack itself, so a
# guard inside a cell runs too late to save a plain `python <file>` launch.

import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # Campaign 2 Progress Figure Suite

    One slide: **the transfer campaign as it happened**, the companion to
    `Campaign1_Progress/`. Experiment order across, objective up, every loaded formulation the
    campaign inherited or produced on the same axis.

    **Two panels, because Campaign 2 ran two independent tracks.** A190 and fenofibrate were
    separate optimisations over the same chemistry — separate surrogates, separate batches,
    separate run orders — so they are two progressions, not one series split in half. They share
    a value axis (and its splice) so a height means the same thing on either side; they do *not*
    share an x axis, because experiment 7 on one track has nothing to do with experiment 7 on the
    other.

    | section | rows | what it is |
    | --- | --- | --- |
    | DoE-OPT | `DoEOPT` | the previous study's optimum — **A190 panel only** |
    | Campaign 1 Champions | `B4_*`, `E2_*`, `F5_*` | Campaign 1's three champions, re-measured with the API loaded |
    | Batches A–C | `A-A1` … `A-C5` / `F-A1` … `F-C5` | three iterations of five, chosen by the optimiser |

    The first two are the **prior optima** the transfer campaign started from and wear the shaded
    band; the batches are the campaign, and the solid rule at `Batch A` is that split.

    `A` is A190 and `F` is fenofibrate, in the batch prefix (`A-B3`) and in the revalidation
    suffix (`B4_A`) alike. The data cell checks that against each row's `API_Name` rather than
    trusting the id, so a mislabelled row fails here instead of landing on the wrong panel.

    ### The band is the prior optima, not the whole prior

    Say what it is: the surrogate trained on **more than this slide draws**. Upstream's
    `MicroemulsionFormulation.get_dataset` (`BayesianOptimization/applications.py`) does a plain
    `pd.read_csv` of the whole dataset and returns every row unfiltered; `API_Name` is one of
    `input_headers` and is one-hot encoded, so the blank Campaign 1 measurements are *training
    data*, not excluded rows. `fixed_categories = {"API_Name": ...}` pins the proposal mesh to one
    API — it does not filter the fit. Upstream's comprehensive CSV is 237 rows (141 blank, 48
    A190, 48 fenofibrate), and each per-API file here is that file minus the other track's fifteen
    batches. So a track's prior is all 47 blank Campaign 1 formulations, all six loaded
    revalidation runs, and its own earlier batches.

    What the band shows is the subset that is **loaded with this panel's API** — the marks whose
    objective is a like-for-like Campaign 2 score. The blank Campaign 1 history is off the slide
    because Campaign 2's objective reads drug loading and permeability and those rows have
    neither; drawing 47 rows scored with two of six outputs silently zeroed would be a worse claim
    than leaving them out and saying so here.

    ## Scoring

    Campaign 2's weighted objective — `3·size + 2·pdi + 1·zeta + 2·drug_loading + 3·perm`,
    divided by the stability factor, PDI hinged at 0.1 — imported from `Figures/objectives.py`
    rather than restated. It reads all six measured outputs, which is why **only loaded rows can
    appear here at all**: the blank Campaign 1 history in these CSVs has no drug loading and no
    permeability, so it has no Campaign 2 objective to plot. That is the difference from the
    Campaign 1 slide, whose objective is physicochemical only.

    **Score-then-average**, as on the Campaign 1 slide: each repeat is scored on its own and the
    marker is the mean, with the standard deviation as the error bar. The three revalidated
    champions were measured **once** each, so they carry no bar — an absent bar here means one
    repeat, not a reproducible one.

    ### DoE-OPT is on the A190 panel only, and it is scored short

    Two caveats travel with that orange mark, both inherited from `Campaign2_Leaderboard/`:

    * The DoE screening was run with A190. There is no fenofibrate measurement of it, and
      inventing a cross-API comparison would be worse than the absence.
    * `DoEOPT` has no `Drug_Loading` and no `Permeability`. The objective scores a missing output
      as `0`, so those two terms — worth roughly −0.1 to +0.6 on the rows that do have them — are
      simply not charged to it. Its 0.79 is its droplet size and PDI alone. Quote it as the
      screening baseline, not as a like-for-like score.

    ## One panel each, one spliced axis

    Four formulations phase-separated — `A-B2`, `A-C1`, `A-C4` on A190 and `F-C4` on fenofibrate.
    Dividing by a stability factor floored at 0.01 parks every one of them at 5438, while the
    whole stable campaign lives between 0.13 and 2.98.

    So the value axis is **spliced**, exactly as on the Campaign 1 slide and for the same reason:
    everything at or below `BREAK_AT` is drawn where it falls, the separated cluster is drawn
    `BREAK_GAP` above that and ticked with its true value, and the skip is announced on each
    upright of each panel's axis box and **nowhere else**. The uprights are shapes rather than the
    y axis's own line, drawn in two segments with a real gap between the strokes — an axis line is
    drawn whole or not at all, and nothing here is painted over to hide it. Nothing inside either
    panel is cut: no band, no section rule, no marker, no error bar.

    The separated runs are **squares**, so a failed formulation does not wear the mark of a value
    on the same scale.

    ### No specification triangles here

    The Campaign 1 slide marks the three formulations meeting the paper's Table 2 response
    targets. Campaign 2 declares no target table of its own, and carrying Table 2 over anyway
    would mark 7 of 19 A190 rows and 9 of 18 fenofibrate rows — half the campaign. A mark that
    half the field wears distinguishes nothing, so the shape vocabulary here is two symbols:
    circle for a measured value, square for a phase separation.

    ## Environment

    A [marimo](https://marimo.io) notebook, so it is a plain Python module and the interpreter
    that launches it *is* the kernel. Run it from the **`BatchedBayes`** conda environment:

    ```
    conda run -n BatchedBayes marimo edit Figures/Campaign2_Progress/Campaign2_Progress_Figures.py
    conda run -n BatchedBayes python Figures/Campaign2_Progress/Campaign2_Progress_Figures.py
    ```
    """)
    return


@app.cell
def _():
    import importlib.util
    import sys
    from pathlib import Path

    import numpy as np
    import pandas as pd
    import plotly
    import plotly.graph_objects as go
    import plotly.io as pio

    pio.renderers.default = 'plotly_mimetype'

    REQUIRED_ENV = 'BatchedBayes'

    _missing = [m for m in ('kaleido',) if importlib.util.find_spec(m) is None]
    if _missing:
        raise ImportError(
            'Missing {}. Run this notebook from the {!r} conda environment.\n'
            'Current interpreter: {}'.format(', '.join(_missing), REQUIRED_ENV, sys.executable)
        )

    print('interpreter  {}'.format(sys.executable))
    print('python       {}'.format(sys.version.split()[0]))
    print('pandas       {}'.format(pd.__version__))
    print('plotly       {}'.format(plotly.__version__))
    return Path, go, np, pd, sys


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Paths, canvas and export

    `REPO_ROOT` is found by looking for `Figures/objectives.py` above this file rather than by
    counting `..`, so the suite survives being moved and fails loudly rather than silently reading
    the wrong tree.

    Two CSVs, one per track — the per-API files, not the Campaign 1 comprehensive one. Each
    carries the whole Campaign 1 history as well; the data cell keeps only what Campaign 2's
    objective can actually score.

    The canvas is the house 1280 × 720.
    """)
    return


@app.cell
def _(Path, sys):
    def _find_repo_root(start):
        for candidate in (start,) + tuple(start.parents):
            if (candidate / 'Figures' / 'objectives.py').is_file():
                return candidate
        raise FileNotFoundError(
            'Could not locate Figures/objectives.py above {}'.format(start))


    try:
        _HERE = Path(__file__).resolve().parent
    except NameError:
        _HERE = Path.cwd()

    REPO_ROOT = _find_repo_root(_HERE)
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Campaign2_Progress' / 'Output'
    DATA_CSV = {
        'A190': REPO_ROOT / 'data' / 'MicroemulsionFormulation_A190.csv',
        'Feno': REPO_ROOT / 'data' / 'MicroemulsionFormulation_Feno.csv',
    }

    # objectives.py is the single source of the objective; never restate a formula here.
    if str(REPO_ROOT / 'Figures') not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / 'Figures'))
    from objectives import campaign2

    EXPORT_FORMATS = ('svg',)
    FIG_WIDTH = 1280
    FIG_HEIGHT = 720
    PNG_SCALE = 2

    print('repo root   {}'.format(REPO_ROOT))
    print('output dir  {}'.format(OUTPUT_DIR))
    return (
        DATA_CSV,
        EXPORT_FORMATS,
        FIG_HEIGHT,
        FIG_WIDTH,
        OUTPUT_DIR,
        PNG_SCALE,
        campaign2,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shared chrome

    House style — the `Breaking-the-Boundaries` figure suites', value for value: white ground, a
    2 px black mirrored axis box, no gridlines, five type sizes (20 / 18 / 18 / 14 / 14), a centred
    title and a horizontal legend in a bottom gutter. **The legend is never inside the panel.**

    Hue carries **campaign section**, and every token here already means the same thing on the
    Campaign 2 leaderboard, so a reader who learns a hue on one slide keeps it on the next:

    | token | hex | what it means |
    | --- | --- | --- |
    | `BEST_COLOR` | `#D55E00` | DoE-OPT, the screening baseline — the comparator hue on all four slides |
    | `C1_COLOR` | `#2067F4` | a revalidated Campaign 1 champion — the Campaign 1 ramp's midpoint |
    | `TRACK_RAMP['A190']` | `#D3B8E8` → `#5A2E8C` | A190's three batches, A palest to C darkest |
    | `TRACK_RAMP['Feno']` | `#8FCFB3` → `#00572B` | fenofibrate's three batches, same three steps |

    **The batches are a ramp, not three hues — and there are two ramps, one per track.** Lightness
    is batch order: a *sequential* encoding claiming exactly one thing, which is the one
    distinction the method makes, since each batch was chosen by a surrogate refit on everything
    before it. Three unrelated hues would claim three kinds of experiment, which would be false.

    Hue is the **API track**. A190 and fenofibrate were separate optimisations, and on a slide that
    puts them side by side the panel title alone was carrying that difference; now the marks carry
    it too. The device is unchanged from the Campaign 1 slide's blue ramp — lightness for order,
    family for identity — but within Campaign 2 the family says *which API*, not which campaign.

    The two ramps are **matched step for step in lightness**, deliberately: `#D3B8E8` and `#8FCFB3`
    are both L\* ≈ 78, `#9B6BC8` and `#009565` both ≈ 54, `#5A2E8C` and `#00572B` both ≈ 30. So
    batch B sits at the same *depth* on either panel and only the hue differs — the reader compares
    depth across panels and hue within one, and neither channel has to do the other's job.

    The green is anchored on Okabe-Ito's bluish green `#009E73`, the colourblind-safe set `#D55E00`
    and `#E69F00` already come from, so it is a sibling of the deck rather than a stranger. Purple
    against green separates at ΔE 53 / 101 / 98 step for step. Under deuteranopia the palest step
    is the weak one, at ΔE 14 — a pale-tint limit the Campaign 1 and Campaign 2 A-steps already
    share — which is why the panel title and the legend name the API as well.

    The prior optima — DoE-OPT and the three revalidated champions — wear `PRIOR_BAND`,
    `rgba(0, 0, 0, 0.055)`: the shaded region the `Breaking-the-Boundaries` campaign plots give a
    screening phase, a ground the optimisation runs *across* rather than a series competing with
    it.
    """)
    return


@app.cell
def _(np):
    BEST_COLOR = '#D55E00'  # red    -- DoE-OPT, the screening baseline; shared with both boards
    C1_COLOR = '#2067F4'    # blue   -- a revalidated Campaign 1 champion; the deck primary

    # Campaign 2's three batches, one ramp per API track: three steps of lightness, A palest to
    # C darkest. Sequential on purpose -- lightness encodes batch order, not kind -- and the two
    # ramps are matched step for step in L*, so a batch sits at the same depth on either panel
    # and only the hue says which API. Shared with the Campaign 2 leaderboard.
    #
    # The green is anchored on Okabe-Ito's bluish green #009E73 -- the colourblind-safe set
    # #D55E00 and #E69F00 already come from -- and built at the purple's own L* and chroma at
    # each step, so 78.4 / 53.7 / 29.5 becomes 78.3 / 54.5 / 31.8.
    TRACK_RAMP = {
        'A190': {'A': '#D3B8E8', 'B': '#9B6BC8', 'C': '#5A2E8C'},   # purple
        'Feno': {'A': '#8FCFB3', 'B': '#009565', 'C': '#00572B'},   # green
    }

    INK = 'black'
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    RULE = 'rgba(0, 0, 0, 0.22)'
    ERA_RULE = 'rgba(0, 0, 0, 0.45)'
    PRIOR_BAND = 'rgba(0, 0, 0, 0.055)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    MARKER_SIZE = 10
    FAIL_MARKER_SIZE = 9
    MARKER_RING = 2
    ERROR_WIDTH = 1.4
    SECTION_RULE_WIDTH = 1.2
    SECTION_RULE_DASH = 'dot'

    LEFT_MARGIN = 92
    RIGHT_MARGIN = 30
    TOP_MARGIN = 150     # title, a panel caption per track, and a row of section names
    LEGEND_MARGIN = 100  # bottom gutter the horizontal legend sits in

    # Two tracks, two panels, side by side. The gap carries the right panel's value-axis ticks:
    # each panel is a closed box with its own ticked axes, so neither has to be read across the
    # other. Both y axes take the same range and the same y domain, which is what lets the four
    # break marks be positioned against one set of paper coordinates.
    PANEL_DOMAIN = {'A190': (0.0, 0.44), 'Feno': (0.56, 1.0)}
    PANEL_TITLE = {'A190': 'A190-Loaded', 'Feno': 'Fenofibrate-Loaded'}

    # The spliced value axis. One panel per track, each with one continuous plot area: values up
    # to BREAK_AT are drawn where they fall, and the phase-separated cluster is drawn BREAK_GAP
    # above that, ticked with its true value. The skip is announced on the axis uprights and
    # nowhere else, so no band, rule, marker or error bar is ever cut by it.
    #
    # BREAK_AT sits a quarter of a tick above the last labelled tick, so the axis reads
    # 0 . 0.5 . ... . 3.5 and then skips: the splice is above 3.5, with air between it and the
    # tick rather than landing on it. That also clears the highest stable run (2.98) and its
    # error bar with room to spare. The gap and the head room above it hold the Campaign 1
    # slide's proportions, 36 % and 17 % of BREAK_AT.
    BREAK_AT = 3.75
    BREAK_GAP = 1.35

    # The break mark: a pair of parallel strokes drawn *across* each upright of each axis box.
    # It cuts the line by crossing it, the way an axis break is drawn on paper -- there is no
    # masking patch, so nothing has to match the ground colour.
    #
    # All three are in **pixels**, because the mark is chrome and must keep its shape whatever
    # the data does to the axis range. The figure converts them against the plot area's own size.
    BREAK_MARK_HALF_PX = 7    # how far either side of the upright a stroke reaches
    BREAK_MARK_RISE_PX = 9    # stroke rise -- roughly 45 degrees at that half-width
    BREAK_MARK_PITCH_PX = 8   # gap between the two strokes
    BREAK_MARK_WIDTH = 1.6
    FRAME_WIDTH = 2


    def fade(hex_color, alpha):
        """Convert '#RRGGBB' to an rgba() string at the given alpha."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return 'rgba({}, {}, {}, {})'.format(r, g, b, alpha)


    def nice_dtick(span, target_ticks=7):
        """Pick a human-readable tick interval covering `span` in roughly `target_ticks` steps."""
        raw = span / float(target_ticks)
        magnitude = 10 ** np.floor(np.log10(raw))
        for step in (1, 2, 2.5, 5, 10):
            if raw <= step * magnitude:
                return float(step * magnitude)
        return float(10 * magnitude)


    # No `showline` / `mirror` for the value axis: the two axes want different answers. The x axes
    # draw each box's horizontals themselves, but the verticals are shapes, because the y axis is
    # spliced and its line has to stop at the break rather than run through it.
    AXIS_COMMON = dict(
        tickcolor=INK, color=INK,
        ticks='outside', showgrid=False, zeroline=False,
        tickfont=dict(size=TICK_SIZE), title_font=dict(size=AXIS_TITLE_SIZE),
    )
    return (
        ANNOTATION_SIZE,
        AXIS_COMMON,
        BEST_COLOR,
        BREAK_AT,
        BREAK_GAP,
        BREAK_MARK_HALF_PX,
        BREAK_MARK_PITCH_PX,
        BREAK_MARK_RISE_PX,
        BREAK_MARK_WIDTH,
        C1_COLOR,
        TRACK_RAMP,
        ERA_RULE,
        ERROR_WIDTH,
        FAIL_MARKER_SIZE,
        FONT_FAMILY,
        FRAME_WIDTH,
        INK,
        INK_SOFT,
        LEFT_MARGIN,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        MARKER_RING,
        MARKER_SIZE,
        PANEL_DOMAIN,
        PANEL_TITLE,
        PRIOR_BAND,
        RIGHT_MARGIN,
        RULE,
        SECTION_RULE_DASH,
        SECTION_RULE_WIDTH,
        TITLE_SIZE,
        TOP_MARGIN,
        fade,
        nice_dtick,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The two campaigns

    One row per formulation per track, in the order that track's CSV records them — which is the
    order they were run, and which the `Exp` labels do not recover on their own. Each panel's x
    axis is that row order, counted from 1 within the track.

    Both per-API CSVs carry the entire Campaign 1 history as well. `section_of` returns `None` for
    every row Campaign 2's objective cannot score — the blank Campaign 1 rows, and the champions
    revalidated with the *other* API — so those drop out here rather than being filtered by hand
    somewhere in the figure.

    `SECTION_SPAN` is derived from the `Exp` prefix and asserted to be contiguous in file order,
    so a re-ordered or extended CSV fails here rather than quietly drawing a band that spans rows
    not in its section.

    `separated` is `Phase_Sep >= 0.5`. In this dataset every separation is unanimous across its
    three repeats, so the threshold never actually arbitrates; it is written as one only so a
    future part-separating formulation lands somewhere defined.
    """)
    return


@app.cell
def _(DATA_CSV, campaign2, pd):
    import re

    SEP_CUT = 0.5

    TRACKS = ('A190', 'Feno')

    # Campaign 2 ids are `<track>-<batch><n>`; the revalidated champions are `<c1 id>_<track>`.
    TRACK_PREFIX = {'A190': 'A-', 'Feno': 'F-'}

    # `A` is A190 and `F` is fenofibrate, in both the batch prefix (`A-B3`) and the revalidation
    # suffix (`B4_A`). That is a naming convention, so it is checked against `API_Name` below
    # rather than trusted: a row kept for a track must actually have been loaded with that API.
    TRACK_API = {'A190': 'A190', 'Feno': 'Feno'}
    CHAMPIONS = {'A190': ('B4_A', 'E2_A', 'F5_A'), 'Feno': ('B4_F', 'E2_F', 'F5_F')}
    DOE_OPT_EXP = 'DoEOPT'

    # DoE-OPT was screened with A190; there is no fenofibrate measurement of it to plot.
    DOE_OPT_TRACK = 'A190'

    C2_BATCHES = ('A', 'B', 'C')

    # Section label per row. This list is also the left-to-right order of a panel's x axis, and is
    # asserted against the file's own order below. Feno simply has no DoE-OPT block.
    SECTION_ORDER = {
        'A190': ['DoE-OPT', 'Campaign 1 Champions']
                + ['Batch {}'.format(b) for b in C2_BATCHES],
        'Feno': ['Campaign 1 Champions']
                + ['Batch {}'.format(b) for b in C2_BATCHES],
    }

    # The campaign proper begins here; everything before it is an inherited prior optimum.
    CAMPAIGN_START_SECTION = 'Batch A'

    # Short names for the row above the panel -- 'Campaign 1 Champions' does not fit over three
    # slots at this width, and the legend already spells every section out in full.
    SECTION_CAPTION = {'DoE-OPT': '', 'Campaign 1 Champions': 'Prior optima'}


    def section_of(track: str, exp: str):
        """Return the section that produced `exp` on `track`, or None if it is not on this board.

        Returning None is the filter: both per-API CSVs carry the whole blank Campaign 1 history
        and both APIs' revalidated champions, and Campaign 2's objective can score neither the
        blank rows nor the other track's champions.
        """
        if exp == DOE_OPT_EXP:
            return 'DoE-OPT' if track == DOE_OPT_TRACK else None
        if exp in CHAMPIONS[track]:
            return 'Campaign 1 Champions'
        if re.fullmatch(re.escape(TRACK_PREFIX[track]) + r'[ABC][1-5]', exp):
            return 'Batch {}'.format(exp[-2])
        return None


    def build_track(track: str):
        """Return one track's per-formulation table, in run order."""
        raw = pd.read_csv(DATA_CSV[track])
        raw['objective'] = campaign2(raw)['objective']
        raw['section'] = raw['Exp'].map(lambda exp: section_of(track, exp))
        rows = raw[raw['section'].notna()].copy()

        # Only the loaded API's own rows survive the section map. DoE-OPT is the one exception --
        # it is a blank measurement, and the sole row here the objective scores with drug loading
        # and permeability missing.
        loaded = rows[rows['Exp'] != DOE_OPT_EXP]
        assert set(loaded['API_Name']) == {TRACK_API[track]},             '{}: kept rows carry API_Name {}, expected {!r}'.format(
                track, sorted(set(loaded['API_Name'])), TRACK_API[track])

        # File order is run order; groupby(sort=False) keeps it and first-seen order is the x axis.
        table = rows.groupby('Exp', sort=False).agg(
            section=('section', 'first'),
            obj=('objective', 'mean'),
            obj_sd=('objective', 'std'),
            size_nm=('Droplet_Size', 'mean'),
            pdi=('PDI', 'mean'),
            zeta=('Zeta_P', 'mean'),
            sep=('Phase_Sep', 'mean'),
            reps=('objective', 'size'),
        ).reset_index()

        table['n'] = range(1, len(table) + 1)
        table['separated'] = table['sep'] >= SEP_CUT

        # Running best over the stable runs only: a separated formulation is not a candidate best.
        running, best = [], float('inf')
        for stable, value in zip(~table['separated'], table['obj']):
            if stable:
                best = min(best, float(value))
            running.append(best)
        table['running_best'] = running
        return table


    def span_of(table, track: str):
        """Map each section to its (first, last) experiment number, asserting contiguity."""
        spans = {}
        for label in SECTION_ORDER[track]:
            block = table.loc[table['section'] == label, 'n']
            assert not block.empty, '{}: section {!r} has no rows'.format(track, label)
            assert block.max() - block.min() + 1 == len(block), \
                '{}: section {!r} is not contiguous in file order'.format(track, label)
            spans[label] = (int(block.min()), int(block.max()))
        assert [s for _, s in sorted((v[0], k) for k, v in spans.items())] == SECTION_ORDER[track], \
            '{}: SECTION_ORDER does not match file order'.format(track)
        return spans


    CAMPAIGN = {track: build_track(track) for track in TRACKS}
    SECTION_SPAN = {track: span_of(CAMPAIGN[track], track) for track in TRACKS}

    # Every track ran three batches of five; anything else means the CSV moved under the figure.
    for _track in TRACKS:
        _batches = CAMPAIGN[_track]['section'].str.startswith('Batch')
        assert int(_batches.sum()) == 15, \
            '{}: expected 15 optimiser runs, found {}'.format(_track, int(_batches.sum()))
        assert len(CAMPAIGN[_track].loc[CAMPAIGN[_track]['section'] == 'Campaign 1 Champions']) == 3, \
            '{}: expected three revalidated champions'.format(_track)

    # The champions and DoE-OPT are the comparators the campaign had to beat, so they are the
    # numbers to quote over the slide -- computed here, and they fail loudly if data/ moves.
    CHAMPION = {track: CAMPAIGN[track].loc[
        CAMPAIGN[track].loc[~CAMPAIGN[track]['separated'], 'obj'].idxmin()] for track in TRACKS}
    PRIOR_BEST = {track: float(CAMPAIGN[track].loc[
        ~CAMPAIGN[track]['section'].str.startswith('Batch'), 'obj'].min()) for track in TRACKS}
    BEAT_PRIOR = {track: CAMPAIGN[track][
        CAMPAIGN[track]['section'].str.startswith('Batch')
        & ~CAMPAIGN[track]['separated']
        & (CAMPAIGN[track]['obj'] < PRIOR_BEST[track])] for track in TRACKS}

    for _track in TRACKS:
        _table = CAMPAIGN[_track]
        print('{:5s} {} formulations, {} repeats each'.format(
            _track, len(_table), sorted(_table['reps'].unique())))
        print('      phase separated  {} -- {}'.format(
            int(_table['separated'].sum()),
            ', '.join(_table.loc[_table['separated'], 'Exp'])))
        print('      best             {} at {:.3f}'.format(
            CHAMPION[_track]['Exp'], CHAMPION[_track]['obj']))
        print('      beat prior best  {} of 15 optimiser runs (prior best {:.3f})'.format(
            len(BEAT_PRIOR[_track]), PRIOR_BEST[_track]))
    return (
        CAMPAIGN,
        CAMPAIGN_START_SECTION,
        SECTION_CAPTION,
        SECTION_ORDER,
        SECTION_SPAN,
        TRACKS,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The figure — `Campaign2_Progress`

    One `go.Layout` with explicit `domain=`s rather than `make_subplots`, per the house workflow.
    Four axes: `x`/`y` are the A190 panel, `x2`/`y2` the fenofibrate one. The two value axes take
    the same range, the same ticks and the same y domain, so a height reads the same on either
    side and one set of paper coordinates positions all four break marks.

    Annotation is deliberately thin — the sections and the marks carry the reading:

    * a **panel caption** per track and a **batch name** per block, with a dotted rule at each
      batch boundary and a solid one where the campaign starts;
    * the prior optima shaded, and captioned once rather than section by section — the legend
      already names DoE-OPT and the champions;
    * **squares** for the phase-separated runs, drawn above the splice.

    The legend sits in the bottom gutter — never inside a panel — and is drawn from the A190
    panel's traces only, since that track carries every series.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
    BEST_COLOR,
    BREAK_AT,
    BREAK_GAP,
    BREAK_MARK_HALF_PX,
    BREAK_MARK_PITCH_PX,
    BREAK_MARK_RISE_PX,
    BREAK_MARK_WIDTH,
    C1_COLOR,
    TRACK_RAMP,
    CAMPAIGN,
    CAMPAIGN_START_SECTION,
    ERA_RULE,
    ERROR_WIDTH,
    FAIL_MARKER_SIZE,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    FRAME_WIDTH,
    INK,
    INK_SOFT,
    LEFT_MARGIN,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    MARKER_RING,
    MARKER_SIZE,
    PANEL_DOMAIN,
    PANEL_TITLE,
    PRIOR_BAND,
    RIGHT_MARGIN,
    RULE,
    SECTION_CAPTION,
    SECTION_ORDER,
    SECTION_RULE_DASH,
    SECTION_RULE_WIDTH,
    SECTION_SPAN,
    TITLE_SIZE,
    TOP_MARGIN,
    TRACKS,
    fade,
    go,
    nice_dtick,
    np,
):
    # One entry per hue, in reading order. The three batches are three steps of one ramp, so they
    # are three entries *per track* -- collapsing them would hide the progression the ramp exists
    # to show, and the two tracks no longer share a hue that could be collapsed onto.
    LEGEND_TRACK_NAME = {'A190': 'A190', 'Feno': 'Fenofibrate'}

    # The two comparators are one series each across both panels, so one panel legends them.
    SHARED_SERIES = [
        ('DoE-OPT (Screening Baseline)', 'DoE-OPT', BEST_COLOR),
        ('Campaign 1 Champion (Revalidated)', 'Campaign 1 Champions', C1_COLOR),
    ]
    LEGEND_TRACK = 'A190'


    def series_for(track):
        """Return (legend label, section, colour) for every series drawn on `track`'s panel."""
        return SHARED_SERIES + [
            ('{} Batch {}'.format(LEGEND_TRACK_NAME[track], letter),
             'Batch {}'.format(letter), TRACK_RAMP[track][letter])
            for letter in sorted(TRACK_RAMP[track])]


    for _track in TRACKS:
        assert set(TRACK_RAMP[_track]) == {_s[-1] for _s in SECTION_ORDER[_track]
                                           if _s.startswith('Batch')},             'TRACK_RAMP[{!r}] does not cover the batches in the data'.format(_track)

    PANEL_AXES = {'A190': ('x', 'y'), 'Feno': ('x2', 'y2')}


    def _marker(color, size, symbol='circle'):
        """A filled mark ringed in the ground, so overlapping points stay countable."""
        return dict(size=size, symbol=symbol, color=color,
                    line=dict(color='white', width=MARKER_RING))


    def build_progress():
        stable_max = max(float(CAMPAIGN[t].loc[~CAMPAIGN[t]['separated'], 'obj'].max())
                         for t in TRACKS)
        fail_value = max(float(CAMPAIGN[t].loc[CAMPAIGN[t]['separated'], 'obj'].max())
                         for t in TRACKS)

        # Everything stable must fit under the splice, or a run would be drawn inside the skip.
        assert stable_max < BREAK_AT, \
            'a stable run scores {:.3f}, above BREAK_AT={}'.format(stable_max, BREAK_AT)

        # The separated cluster is *drawn* here and *ticked* with its true value. Nothing else is
        # displaced, so every mark below the splice sits at its own coordinate.
        fail_drawn_at = BREAK_AT + BREAK_GAP

        # The floor clears the lowest error bar, not the lowest marker: Campaign 2's loss has a
        # bonus side, so a whisker can reach below zero and must not be cut by the frame.
        whisker_low = min(float((CAMPAIGN[t].loc[~CAMPAIGN[t]['separated'], 'obj']
                                 - CAMPAIGN[t].loc[~CAMPAIGN[t]['separated'], 'obj_sd']
                                 .fillna(0.0)).min()) for t in TRACKS)
        y_range = [min(-0.04 * BREAK_AT, whisker_low - 0.04 * BREAK_AT),
                   fail_drawn_at + 0.17 * BREAK_AT]
        # Eight steps over BREAK_AT, not seven: seven rounds the interval up to 1.0 and
        # throws away the half-unit ticks the stable campaign actually lives on.
        y_dtick = nice_dtick(BREAK_AT, 8)
        lower_ticks = np.arange(0.0, BREAK_AT + y_dtick / 2, y_dtick)
        tickvals = list(lower_ticks) + [fail_drawn_at]
        ticktext = ['{:g}'.format(v) for v in lower_ticks] + ['{:.0f}'.format(fail_value)]

        traces, shapes, annotations = [], [], []

        for track in TRACKS:
            table = CAMPAIGN[track]
            spans = SECTION_SPAN[track]
            x_axis, y_axis = PANEL_AXES[track]
            stable = table[~table['separated']]
            failed = table[table['separated']]

            # --- The prior-optima band and the section rules ------------------------------------
            # Everything the transfer campaign inherited sits on the shaded ground the
            # `Breaking-the-Boundaries` campaign plots give a screening phase: a region the
            # optimisation runs across, rather than a series competing with it.
            campaign_lo = spans[CAMPAIGN_START_SECTION][0]
            prior_lo = min(lo for label, (lo, _) in spans.items() if lo < campaign_lo)
            shapes.append(dict(
                type='rect', xref=x_axis, yref='{} domain'.format(y_axis),
                x0=prior_lo - 0.5, x1=campaign_lo - 0.5, y0=0, y1=1,
                fillcolor=PRIOR_BAND, line=dict(width=0), layer='below'))

            for label in SECTION_ORDER[track]:
                lo, _hi = spans[label]
                if lo <= 1:
                    continue
                is_era_break = lo == campaign_lo
                shapes.append(dict(
                    type='line', xref=x_axis, yref='{} domain'.format(y_axis),
                    x0=lo - 0.5, x1=lo - 0.5, y0=0, y1=1,
                    line=dict(color=ERA_RULE if is_era_break else RULE,
                              width=2 if is_era_break else SECTION_RULE_WIDTH,
                              dash=None if is_era_break else SECTION_RULE_DASH),
                    layer='below'))

            # --- Section names, above the panel -------------------------------------------------
            # The prior-optima block is captioned once, across its whole span: 'DoE-OPT' has one
            # slot to sit over and would not fit, and the legend names it anyway.
            captioned = {}
            for label in SECTION_ORDER[track]:
                caption = SECTION_CAPTION.get(label, label)
                if not caption:
                    continue
                lo, hi = spans[label]
                if caption in captioned:
                    lo = min(lo, captioned[caption][0])
                    hi = max(hi, captioned[caption][1])
                captioned[caption] = (lo, hi)
            # The caption spans the whole band, not just the champions block.
            if 'Prior optima' in captioned:
                captioned['Prior optima'] = (prior_lo, campaign_lo - 1)

            for caption, (lo, hi) in captioned.items():
                annotations.append(dict(
                    x=(lo + hi) / 2, y=1, xref=x_axis, yref='{} domain'.format(y_axis), yshift=10,
                    text=caption, showarrow=False, xanchor='center', yanchor='bottom',
                    font=dict(size=ANNOTATION_SIZE, color=INK_SOFT, family=FONT_FAMILY)))

            # --- The panel caption, above the section names --------------------------------------
            annotations.append(dict(
                x=0.5, y=1, xref='{} domain'.format(x_axis),
                yref='{} domain'.format(y_axis), yshift=36,
                text=PANEL_TITLE[track], showarrow=False, xanchor='center', yanchor='bottom',
                font=dict(size=ANNOTATION_SIZE + 2, color=INK, family=FONT_FAMILY)))

            # --- The runs, one legend entry per hue ----------------------------------------------
            for label, section, color in series_for(track):
                # A batch series belongs to this track, so it legends itself; the two comparators
                # are shared, so only one panel legends them.
                shared = (label, section, color) in SHARED_SERIES
                show_legend = track == LEGEND_TRACK or not shared
                block = stable[stable['section'] == section]
                if not block.empty:
                    traces.append(go.Scatter(
                        x=block['n'], y=block['obj'], mode='markers', name=label,
                        xaxis=x_axis, yaxis=y_axis,
                        legendgroup=label, showlegend=show_legend,
                        marker=_marker(color, MARKER_SIZE),
                        error_y=dict(type='data', array=block['obj_sd'].fillna(0.0),
                                     color=fade(color, 0.75), thickness=ERROR_WIDTH, width=4),
                        customdata=block['Exp'],
                        hovertemplate='%{customdata}<br>Exp %{x}<br>objective %{y:.3f}'
                                      '<extra></extra>'))

                fail_block = failed[failed['section'] == section]
                if not fail_block.empty:
                    traces.append(go.Scatter(
                        x=fail_block['n'], y=[fail_drawn_at] * len(fail_block), mode='markers',
                        name=label, xaxis=x_axis, yaxis=y_axis,
                        legendgroup=label, showlegend=False,
                        marker=_marker(color, FAIL_MARKER_SIZE, symbol='square'),
                        customdata=fail_block['Exp'],
                        hovertemplate='%{customdata}<br>Exp %{x}<br>phase separated, objective '
                                      + '{:.0f}<extra></extra>'.format(fail_value)))

        # --- A legend entry for the mark shape, which is a variable of its own --------------------
        traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Phase Separated',
            xaxis='x', yaxis='y',
            marker=_marker(INK_SOFT, FAIL_MARKER_SIZE, symbol='square')))

        # --- The skip, announced on the uprights and nowhere else ---------------------------------
        # Two parallel strokes drawn across each upright of each axis box, over the line rather
        # than instead of it -- so there is no patch to match to the ground, and nothing inside a
        # panel is touched. Shapes take no pixel offsets, so the mark's pixel geometry is
        # converted against the plot area: x into paper units, y into data units. Both value axes
        # share a range and a domain, so `yref='y'` places the marks on both panels alike.
        plot_width_px = FIG_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
        plot_height_px = FIG_HEIGHT - TOP_MARGIN - LEGEND_MARGIN
        per_px = (y_range[1] - y_range[0]) / plot_height_px

        half_w = BREAK_MARK_HALF_PX / plot_width_px
        rise = BREAK_MARK_RISE_PX * per_px
        pitch = BREAK_MARK_PITCH_PX * per_px
        mark_y = BREAK_AT + BREAK_GAP / 2

        # The uprights of each axis box are drawn here rather than by the y axes, in two segments
        # each: the line runs up to the lower stroke, stops, and resumes at the upper one. The
        # break is therefore an actual absence of line between the strokes -- nothing is painted
        # over to hide it.
        uprights = [edge for track in TRACKS for edge in PANEL_DOMAIN[track]]
        for upright_x in uprights:
            for y0, y1 in ((y_range[0], mark_y - pitch / 2),
                           (mark_y + pitch / 2, y_range[1])):
                shapes.append(dict(
                    type='line', xref='paper', yref='y',
                    x0=upright_x, y0=y0, x1=upright_x, y1=y1,
                    line=dict(color=INK, width=FRAME_WIDTH), layer='above'))
            for stroke in (-pitch / 2, pitch / 2):
                shapes.append(dict(
                    type='line', xref='paper', yref='y',
                    x0=upright_x - half_w, y0=mark_y + stroke - rise / 2,
                    x1=upright_x + half_w, y1=mark_y + stroke + rise / 2,
                    line=dict(color=INK, width=BREAK_MARK_WIDTH), layer='above'))

        def x_axis_spec(track, anchor):
            """The panel's x axis. It draws the box's horizontals; the verticals are shapes."""
            return dict(title='Experiment Number', anchor=anchor,
                        domain=list(PANEL_DOMAIN[track]),
                        range=[0.4, len(CAMPAIGN[track]) + 0.6],
                        showline=True, mirror=True, linecolor=INK, linewidth=FRAME_WIDTH,
                        tickmode='linear', tick0=0, dtick=5, **AXIS_COMMON)

        def y_axis_spec(anchor, title):
            """The spliced value axis. Both panels take the same range and the same ticks."""
            return dict(title=title, anchor=anchor, domain=[0.0, 1.0], range=y_range,
                        showline=False, mirror=False,
                        tickmode='array', tickvals=tickvals, ticktext=ticktext, **AXIS_COMMON)

        layout = go.Layout(
            title=dict(
                text='Campaign 2 — Optimisation Progression, Both API Tracks<br>'
                     '<span style="font-size:{}px;color:{}">Objective per loaded formulation in '
                     'campaign order  ·  score-then-average over three repeats  ·  '
                     'lower is better</span>'.format(ANNOTATION_SIZE, INK_SOFT),
                font=dict(size=TITLE_SIZE, color=INK), x=0.5, y=0.975,
                xanchor='center', yanchor='top'),
            xaxis=x_axis_spec('A190', 'y'), xaxis2=x_axis_spec('Feno', 'y2'),
            yaxis=y_axis_spec('x', 'Objective Function'), yaxis2=y_axis_spec('x2', ''),
            shapes=shapes,
            annotations=annotations,
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            width=FIG_WIDTH, height=FIG_HEIGHT,
            margin=dict(l=LEFT_MARGIN, r=RIGHT_MARGIN, t=TOP_MARGIN, b=LEGEND_MARGIN),
            showlegend=True,
            # The bottom gutter. y < 0 is below the plot area, so the legend is never inside it.
            legend=dict(orientation='h', x=0.5, y=-0.155, xanchor='center', yanchor='top',
                        bgcolor='rgba(0, 0, 0, 0)', itemsizing='constant',
                        font=dict(size=LEGEND_SIZE, color=INK)),
            hoverlabel=dict(font=dict(family=FONT_FAMILY, size=12)),
        )
        return go.Figure(data=traces, layout=layout)


    progress_figure = build_progress()
    progress_figure
    return (progress_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export

    SVG at the native 1280 × 720, one data unit to one exported pixel. Adding `'png'` to
    `EXPORT_FORMATS` writes a 2× raster alongside.
    """)
    return


@app.cell
def _(
    EXPORT_FORMATS,
    FIG_HEIGHT,
    FIG_WIDTH,
    OUTPUT_DIR,
    PNG_SCALE,
    progress_figure,
):
    FIGURES = {
        'Campaign2_Progress': (progress_figure, FIG_WIDTH, FIG_HEIGHT),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for _stem, (_fig, _w, _h) in FIGURES.items():
        for _fmt in EXPORT_FORMATS:
            _path = OUTPUT_DIR / '{}.{}'.format(_stem, _fmt)
            _fig.write_image(
                _path, format=_fmt, width=_w, height=_h,
                scale=PNG_SCALE if _fmt == 'png' else 1,
            )
            print('wrote {}'.format(_path))
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
