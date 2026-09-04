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
    # Campaign Progress Figure Suite

    One slide: **the optimisation campaign as it happened.** Experiment order across, objective
    up, every formulation the campaign inherited or produced on the same axis — the paper's
    Fig. 2, *Optimization Progression Plot of the Optimization Campaign*, rebuilt from `data/`.

    Six sections, left to right, in the order the file records them:

    | section | rows | what it is |
    | --- | --- | --- |
    | DoE | `DoE1`, `DoE4`, `DoE10`, `DoE11` | the previous study's design-of-experiments screen |
    | DoE-OPT | `DoEOPT` | that study's optimum — the mark the campaign had to beat |
    | Misc | `Misc12` … `Misc44` | miscellaneous prior formulations, re-measured |
    | Random Screen | `Ran1` … `Ran10` | the quasi-random, constraint-respecting screen that seeded the surrogate |
    | Batches A–E | `A1` … `E5` | five iterations of five, chosen by the optimiser |

    The first four are the **initial dataset**; the last is the **campaign**. The bracket above the
    panel is that split, and it is the comparison the slide exists to make.

    ## Scoring

    Campaign 1's objective **as published** — paper Eq. 1–4, equal weights, ×10 phase separation,
    PDI hinged at 0.3 — imported from `Figures/objectives.py` rather than restated. It is
    physicochemical only, which is what makes the blank campaign rows and the A190-loaded DoE rows
    comparable at all: neither drug loading nor permeability enters the score.

    **Score-then-average.** Each of a formulation's three repeats is scored on its own and the
    marker is the mean of those three; the error bar is their standard deviation. That is not the
    same as averaging the measurements and scoring once — the objective hinges at 100 nm,
    |zeta| = 10 mV and PDI 0.3 — and it is the order that prices reproducibility, which is what
    the bar on `B4` is showing.

    ## Two panels, one axis

    Thirteen formulations phase-separated. The ×10 term puts every one of them at 31, while the
    whole stable campaign lives between 0.04 and 1.04. On one linear axis the campaign collapses
    to a line; on a log axis a *failure* acquires the visual weight of a *value*. Neither is honest
    on a slide.

    So the y axis is broken. The tall panel carries the stable runs on a linear scale; the short
    panel above it carries the separated cluster at its true 31, with a break mark between them.
    Both panels sit on the same x axis, so a column reads straight down and the count at 31 — the
    paper's "13 formulations grouped at an objective score of 31" — is still there to be read.

    ## Triangles are the specification

    The paper's Table 2 response targets: droplet size < 100 nm, PDI < 0.3, zeta potential within
    ±10 mV, no phase separation. A formulation meeting all four is drawn as a triangle, which
    recovers exactly the three the paper names — `B4`, `D3` and `E2` — and all three come from the
    campaign, against zero from the DoE.

    ## Environment

    A [marimo](https://marimo.io) notebook, so it is a plain Python module and the interpreter that
    launches it *is* the kernel. Run it from the **`BatchedBayes`** conda environment:

    ```
    conda run -n BatchedBayes marimo edit Figures/Campaign_Progress/Campaign_Progress_Figures.py
    conda run -n BatchedBayes python Figures/Campaign_Progress/Campaign_Progress_Figures.py
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Campaign_Progress' / 'Output'
    DATA_CSV = REPO_ROOT / 'data' / 'MicroemulsionFormulation_Comprehensive.csv'

    # objectives.py is the single source of the objective; never restate a formula here.
    if str(REPO_ROOT / 'Figures') not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / 'Figures'))
    from objectives import campaign1

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
        campaign1,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shared chrome

    House style — the `Breaking-the-Boundaries` figure suites', value for value: white ground, a
    2 px black mirrored axis box, no gridlines, five type sizes (20 / 18 / 18 / 14 / 14), a centred
    title and a horizontal legend in a bottom gutter. **The legend is never inside the panel.**

    Hue carries **campaign section**, and the two tokens the leaderboards already fixed keep their
    meanings, so a reader who learns a hue on one slide keeps it on the next:

    | token | hex | what it means |
    | --- | --- | --- |
    | `DOE_COLOR` | `#E69F00` | the previous DoE screen — prior art, one level below its own optimum |
    | `BEST_COLOR` | `#D55E00` | DoE-OPT, the baseline the campaign had to beat — the comparator hue, as on both leaderboards |
    | `MISC_COLOR` | `#CC79A7` | miscellaneous prior formulations |
    | `SCREEN_COLOR` | `#C4C4C4` | the quasi-random screen — `TRIAL_COLOR`, as on the Campaign 1 board |
    | `BO_COLOR` | `#2067F4` | every optimiser-chosen batch, A–E — the deck primary |

    Five BO batches are **one** colour on purpose. They are one campaign under one policy; giving
    each batch its own hue would claim a distinction the method does not make. The batches are
    separated instead by the thing that actually separates them — a dotted rule and a name, drawn
    where the optimiser stopped and re-fit.

    The screen wears `SCREEN_BAND` — `rgba(0, 0, 0, 0.055)`, the shaded region the
    `Breaking-the-Boundaries` campaign plots draw screening as. Here it can be a band, which is
    what it wanted to be on the leaderboard and could not.
    """)
    return


@app.cell
def _(np):
    DOE_COLOR = '#E69F00'      # orange  -- the previous DoE screen
    BEST_COLOR = '#D55E00'     # red     -- DoE-OPT, the baseline; shared with both leaderboards
    MISC_COLOR = '#CC79A7'     # magenta -- miscellaneous prior formulations
    SCREEN_COLOR = '#C4C4C4'   # grey    -- quasi-random screen; BtB's TRIAL_COLOR
    BO_COLOR = '#2067F4'       # blue    -- optimiser batches A-E; the deck primary

    INK = 'black'
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    INK_FAINT = 'rgba(0, 0, 0, 0.38)'
    RULE = 'rgba(0, 0, 0, 0.22)'
    ERA_RULE = 'rgba(0, 0, 0, 0.45)'
    SCREEN_BAND = 'rgba(0, 0, 0, 0.055)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    MARKER_SIZE = 10
    SPEC_MARKER_SIZE = 14
    MARKER_RING = 2
    LINE_WIDTH = 2.5
    ERROR_WIDTH = 1.4
    SECTION_RULE_WIDTH = 1.2
    SECTION_RULE_DASH = 'dot'

    LEFT_MARGIN = 105
    RIGHT_MARGIN = 40
    TOP_MARGIN = 150     # title, the era bracket, and a row of section names
    LEGEND_MARGIN = 105  # bottom gutter the horizontal legend sits in

    # The broken axis: the stable campaign gets the tall panel, the separated cluster the short
    # one, and the gap between them is where the break mark goes.
    MAIN_DOMAIN = (0.0, 0.80)
    FAIL_DOMAIN = (0.90, 1.0)


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


    AXIS_COMMON = dict(
        linecolor=INK, tickcolor=INK, color=INK,
        ticks='outside', showline=True, showgrid=False, mirror=True, linewidth=2,
        zeroline=False,
        tickfont=dict(size=TICK_SIZE), title_font=dict(size=AXIS_TITLE_SIZE),
    )
    return (
        ANNOTATION_SIZE,
        AXIS_COMMON,
        AXIS_TITLE_SIZE,
        BEST_COLOR,
        BO_COLOR,
        DOE_COLOR,
        ERA_RULE,
        ERROR_WIDTH,
        FAIL_DOMAIN,
        FONT_FAMILY,
        INK,
        INK_FAINT,
        INK_SOFT,
        LEFT_MARGIN,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        LINE_WIDTH,
        MAIN_DOMAIN,
        MARKER_RING,
        MARKER_SIZE,
        MISC_COLOR,
        RIGHT_MARGIN,
        RULE,
        SCREEN_BAND,
        SCREEN_COLOR,
        SECTION_RULE_DASH,
        SECTION_RULE_WIDTH,
        SPEC_MARKER_SIZE,
        TICK_SIZE,
        TITLE_SIZE,
        TOP_MARGIN,
        fade,
        nice_dtick,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The campaign

    One row per formulation, in the order `MicroemulsionFormulation_Comprehensive.csv` records
    them — which is the order they were run, and which the `Exp` labels do not recover on their
    own. The x axis is that row order.

    `SECTION_SPAN` is derived from the `Exp` prefix and asserted to be contiguous in file order, so
    a re-ordered or extended CSV fails here rather than quietly drawing a band that spans rows not
    in its section.

    `sep >= 0.5` marks a phase-separated formulation. In this dataset every one is unanimous
    across its three repeats, so the threshold never actually arbitrates; it is written as one only
    so a future part-separating formulation lands somewhere defined.

    `in_spec` is the paper's Table 2 target criteria, all four at once, on the repeat means. It
    recovers `B4`, `D3` and `E2` — the three the paper names — and the assertion below holds the
    figure to that.
    """)
    return


@app.cell
def _(DATA_CSV, campaign1, pd):
    import re

    SEP_CUT = 0.5

    # Section label per `Exp` prefix. This list is also the left-to-right order of the x axis, and
    # is asserted against the file's own order below.
    SECTION_ORDER = ['DoE', 'DoE-OPT', 'Misc', 'Random Screen',
                     'Batch A', 'Batch B', 'Batch C', 'Batch D', 'Batch E']

    # The campaign proper begins here; everything before it is the inherited initial dataset.
    CAMPAIGN_START_SECTION = 'Batch A'

    ERA_LABEL = {
        'initial': 'Initial dataset  ·  inherited prior art',
        'campaign': 'Batched Bayesian optimisation  ·  5 batches of 5',
    }

    # Paper Table 2, response targets for formulation optimisation.
    SPEC_SIZE_NM = 100.0
    SPEC_PDI = 0.3
    SPEC_ZETA_MV = 10.0


    def section_of(exp: str):
        """Return the campaign section that produced `exp`, or None if it is not Campaign 1."""
        if exp == 'DoEOPT':
            return 'DoE-OPT'
        if exp.startswith('DoE'):
            return 'DoE'
        if exp.startswith('Misc'):
            return 'Misc'
        if exp.startswith('Ran'):
            return 'Random Screen'
        if re.fullmatch(r'[A-E][1-5]', exp):
            return 'Batch {}'.format(exp[0])
        return None


    _raw = pd.read_csv(DATA_CSV)
    _raw['objective'] = campaign1(_raw)['objective']
    _raw['section'] = _raw['Exp'].map(section_of)
    _rows = _raw[_raw['section'].notna()].copy()

    # File order is run order; groupby(sort=False) keeps it and first-seen order becomes the x axis.
    CAMPAIGN = _rows.groupby('Exp', sort=False).agg(
        section=('section', 'first'),
        obj=('objective', 'mean'),
        obj_sd=('objective', 'std'),
        size_nm=('Droplet_Size', 'mean'),
        pdi=('PDI', 'mean'),
        zeta=('Zeta_P', 'mean'),
        sep=('Phase_Sep', 'mean'),
        reps=('objective', 'size'),
    ).reset_index()

    CAMPAIGN['n'] = range(1, len(CAMPAIGN) + 1)
    CAMPAIGN['separated'] = CAMPAIGN['sep'] >= SEP_CUT
    CAMPAIGN['in_spec'] = (
        (CAMPAIGN['size_nm'] < SPEC_SIZE_NM)
        & (CAMPAIGN['pdi'] < SPEC_PDI)
        & (CAMPAIGN['zeta'].abs() <= SPEC_ZETA_MV)
        & ~CAMPAIGN['separated']
    )

    # Running best over the stable runs only: a separated formulation is not a candidate best.
    _running, _best = [], float('inf')
    for _stable, _value in zip(~CAMPAIGN['separated'], CAMPAIGN['obj']):
        if _stable:
            _best = min(_best, float(_value))
        _running.append(_best)
    CAMPAIGN['running_best'] = _running

    # Sections must be contiguous in file order, or a band would span rows that are not in it.
    SECTION_SPAN = {}
    for _label in SECTION_ORDER:
        _block = CAMPAIGN.loc[CAMPAIGN['section'] == _label, 'n']
        assert not _block.empty, 'section {!r} has no rows'.format(_label)
        assert _block.max() - _block.min() + 1 == len(_block), \
            'section {!r} is not contiguous in file order'.format(_label)
        SECTION_SPAN[_label] = (int(_block.min()), int(_block.max()))
    assert [_s for _, _s in sorted((v[0], k) for k, v in SECTION_SPAN.items())] == SECTION_ORDER, \
        'SECTION_ORDER does not match file order'

    DOE_OPT = CAMPAIGN.loc[CAMPAIGN['section'] == 'DoE-OPT'].iloc[0]
    CHAMPION = CAMPAIGN.loc[CAMPAIGN.loc[~CAMPAIGN['separated'], 'obj'].idxmin()]
    IN_SPEC = CAMPAIGN[CAMPAIGN['in_spec']]

    # The baseline annotation is a claim about the *campaign*, so it counts optimiser-chosen runs
    # only -- the inherited Misc and screen rows are not what beat the previous optimum.
    OPTIMISER = CAMPAIGN[CAMPAIGN['section'].str.startswith('Batch') & ~CAMPAIGN['separated']]
    BEAT_DOE_OPT = OPTIMISER[OPTIMISER['obj'] < DOE_OPT['obj']]

    assert list(IN_SPEC['Exp']) == ['B4', 'D3', 'E2'], \
        'in-spec set drifted from the paper: {}'.format(list(IN_SPEC['Exp']))
    assert len(BEAT_DOE_OPT) == 9, \
        'the paper reports nine optimiser runs beating DoE-OPT, found {}'.format(len(BEAT_DOE_OPT))

    print('{} formulations, {} repeats each'.format(
        len(CAMPAIGN), sorted(CAMPAIGN['reps'].unique())))
    print('phase separated  {} of {}'.format(int(CAMPAIGN['separated'].sum()), len(CAMPAIGN)))
    print('in specification {}'.format(', '.join(IN_SPEC['Exp'])))
    print('champion         {} at {:.4f} ({:.1f} nm)'.format(
        CHAMPION['Exp'], CHAMPION['obj'], CHAMPION['size_nm']))
    print('beat DoE-OPT     {} of {} stable optimiser runs'.format(
        len(BEAT_DOE_OPT), len(OPTIMISER)))
    return (
        BEAT_DOE_OPT,
        CAMPAIGN,
        CAMPAIGN_START_SECTION,
        CHAMPION,
        DOE_OPT,
        ERA_LABEL,
        IN_SPEC,
        OPTIMISER,
        SECTION_ORDER,
        SECTION_SPAN,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The figure — `Campaign_Progress`

    One `go.Layout` with explicit `domain=`s rather than `make_subplots`, per the house workflow.
    Four axes: `x`/`y` are the stable panel, `x2`/`y2` the separated strip above it. `x2` matches
    `x`'s range and hides its tick labels, so the two panels are one column of experiment numbers
    with a break in the value axis.

    Annotation, in the order a reader meets it:

    * the **era bracket** above everything — initial dataset, then campaign;
    * a **section name** per block, with a dotted rule at each boundary and a solid one where the
      campaign starts;
    * the **DoE-OPT baseline** as a dashed horizontal reference, so *better than the previous
      optimum* is a position on the page rather than a claim in the caption;
    * the **running best**, stepping down behind the points;
    * **triangles** for the three in-specification formulations, each named.

    Everything else stays in the legend, which sits in the bottom gutter — never inside the panel.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
    AXIS_TITLE_SIZE,
    BEAT_DOE_OPT,
    BEST_COLOR,
    BO_COLOR,
    CAMPAIGN,
    CAMPAIGN_START_SECTION,
    CHAMPION,
    DOE_COLOR,
    DOE_OPT,
    ERA_LABEL,
    ERA_RULE,
    ERROR_WIDTH,
    FAIL_DOMAIN,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_FAINT,
    INK_SOFT,
    IN_SPEC,
    LEFT_MARGIN,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    LINE_WIDTH,
    MAIN_DOMAIN,
    MARKER_RING,
    MARKER_SIZE,
    MISC_COLOR,
    OPTIMISER,
    RIGHT_MARGIN,
    RULE,
    SCREEN_BAND,
    SCREEN_COLOR,
    SECTION_ORDER,
    SECTION_RULE_DASH,
    SECTION_RULE_WIDTH,
    SECTION_SPAN,
    SPEC_MARKER_SIZE,
    TITLE_SIZE,
    TOP_MARGIN,
    fade,
    go,
    nice_dtick,
):
    # One legend entry per hue, in reading order. 'Batches A-E' is one entry for five sections.
    SERIES = [
        ('DoE', ['DoE'], DOE_COLOR),
        ('DoE-OPT', ['DoE-OPT'], BEST_COLOR),
        ('Misc', ['Misc'], MISC_COLOR),
        ('Random Screen', ['Random Screen'], SCREEN_COLOR),
        ('Optimiser Batches A–E', [s for s in SECTION_ORDER if s.startswith('Batch')], BO_COLOR),
    ]


    def _marker(color, size, symbol='circle'):
        """A filled mark ringed in the ground, so overlapping points stay countable."""
        return dict(size=size, symbol=symbol, color=color,
                    line=dict(color='white', width=MARKER_RING))


    def build_progress():
        stable = CAMPAIGN[~CAMPAIGN['separated']]
        failed = CAMPAIGN[CAMPAIGN['separated']]
        fail_y = float(failed['obj'].max())

        x_range = [0.4, len(CAMPAIGN) + 0.6]
        y_top = float(stable['obj'].max()) * 1.10
        y_dtick = nice_dtick(y_top, 6)
        y_range = [-0.04, y_top]
        # The strip only has to hold one value; a little air either side keeps it off its box.
        fail_range = [fail_y - 0.9, fail_y + 0.9]

        traces, shapes, annotations = [], [], []

        # --- Bands and section rules ----------------------------------------------------------
        screen_lo, screen_hi = SECTION_SPAN['Random Screen']
        for x_axis, y_axis in (('x', 'y'), ('x2', 'y2')):
            shapes.append(dict(
                type='rect', xref=x_axis, yref='{} domain'.format(y_axis),
                x0=screen_lo - 0.5, x1=screen_hi + 0.5, y0=0, y1=1,
                fillcolor=SCREEN_BAND, line=dict(width=0), layer='below'))

        campaign_lo = SECTION_SPAN[CAMPAIGN_START_SECTION][0]
        for label in SECTION_ORDER:
            lo, _hi = SECTION_SPAN[label]
            if lo <= 1:
                continue
            is_era_break = lo == campaign_lo
            for x_axis, y_axis in (('x', 'y'), ('x2', 'y2')):
                shapes.append(dict(
                    type='line', xref=x_axis, yref='{} domain'.format(y_axis),
                    x0=lo - 0.5, x1=lo - 0.5, y0=0, y1=1,
                    line=dict(color=ERA_RULE if is_era_break else RULE,
                              width=2 if is_era_break else SECTION_RULE_WIDTH,
                              dash=None if is_era_break else SECTION_RULE_DASH),
                    layer='below'))

        # --- Section names, above the top panel -----------------------------------------------
        for label in SECTION_ORDER:
            lo, hi = SECTION_SPAN[label]
            annotations.append(dict(
                x=(lo + hi) / 2, y=1, xref='x2', yref='y2 domain', yshift=10,
                text=label, showarrow=False, xanchor='center', yanchor='bottom',
                font=dict(size=ANNOTATION_SIZE, color=INK_SOFT, family=FONT_FAMILY)))

        # --- The era bracket, above the section names -----------------------------------------
        # yref='paper' is the plot area, so y > 1 is above the top panel. The section names take
        # the first band above it; the bracket sits clear of them.
        bracket_y = 1.115
        for key, lo, hi in (('initial', 1, campaign_lo - 1),
                            ('campaign', campaign_lo, len(CAMPAIGN))):
            shapes.append(dict(
                type='line', xref='x2', yref='paper',
                x0=lo - 0.5, x1=hi + 0.5, y0=bracket_y, y1=bracket_y,
                line=dict(color=INK_FAINT, width=1.2)))
            for tick_x in (lo - 0.5, hi + 0.5):
                shapes.append(dict(
                    type='line', xref='x2', yref='paper',
                    x0=tick_x, x1=tick_x, y0=bracket_y, y1=bracket_y - 0.022,
                    line=dict(color=INK_FAINT, width=1.2)))
            annotations.append(dict(
                x=(lo + hi) / 2, y=bracket_y, xref='x2', yref='paper', yshift=6,
                text=ERA_LABEL[key], showarrow=False, xanchor='center', yanchor='bottom',
                font=dict(size=ANNOTATION_SIZE, color=INK, family=FONT_FAMILY)))

        # --- DoE-OPT baseline, across the stable panel ----------------------------------------
        shapes.append(dict(
            type='line', xref='x', yref='y',
            x0=x_range[0], x1=x_range[1], y0=float(DOE_OPT['obj']), y1=float(DOE_OPT['obj']),
            line=dict(color=BEST_COLOR, width=1.6, dash='dash'), layer='below'))
        # The screen band is empty above the baseline; right-anchoring would put this on the
        # batch-C points instead.
        annotations.append(dict(
            x=SECTION_SPAN['Random Screen'][0], y=float(DOE_OPT['obj']), xref='x', yref='y',
            xanchor='left', yanchor='bottom', yshift=5,
            text='DoE-OPT {:.3f}  ·  {} of {} stable optimiser runs beat it'.format(
                DOE_OPT['obj'], len(BEAT_DOE_OPT), len(OPTIMISER)),
            showarrow=False,
            font=dict(size=ANNOTATION_SIZE, color=BEST_COLOR, family=FONT_FAMILY)))

        # --- Running best ----------------------------------------------------------------------
        traces.append(go.Scatter(
            x=CAMPAIGN['n'], y=CAMPAIGN['running_best'], mode='lines', name='Running Best',
            xaxis='x', yaxis='y',
            line=dict(color=INK_SOFT, width=LINE_WIDTH, shape='hv'),
            hovertemplate='running best<br>Exp %{x}<br>%{y:.3f}<extra></extra>'))

        # --- The runs, one legend entry per hue -------------------------------------------------
        for label, sections, color in SERIES:
            in_series = stable['section'].isin(sections)
            block = stable[in_series & ~stable['in_spec']]
            spec_block = stable[in_series & stable['in_spec']]

            traces.append(go.Scatter(
                x=block['n'], y=block['obj'], mode='markers', name=label,
                xaxis='x', yaxis='y', legendgroup=label,
                marker=_marker(color, MARKER_SIZE),
                error_y=dict(type='data', array=block['obj_sd'].fillna(0.0),
                             color=fade(color, 0.75), thickness=ERROR_WIDTH, width=4),
                customdata=block['Exp'],
                hovertemplate='%{customdata}<br>Exp %{x}<br>objective %{y:.3f}<extra></extra>'))

            if not spec_block.empty:
                traces.append(go.Scatter(
                    x=spec_block['n'], y=spec_block['obj'], mode='markers', name=label,
                    xaxis='x', yaxis='y', legendgroup=label, showlegend=False,
                    marker=_marker(color, SPEC_MARKER_SIZE, symbol='triangle-up'),
                    error_y=dict(type='data', array=spec_block['obj_sd'].fillna(0.0),
                                 color=fade(color, 0.75), thickness=ERROR_WIDTH, width=4),
                    customdata=spec_block['Exp'],
                    hovertemplate='%{customdata}<br>Exp %{x}<br>objective %{y:.3f}'
                                  '<br>in specification<extra></extra>'))

            fail_block = failed[failed['section'].isin(sections)]
            if not fail_block.empty:
                traces.append(go.Scatter(
                    x=fail_block['n'], y=fail_block['obj'], mode='markers', name=label,
                    xaxis='x2', yaxis='y2', legendgroup=label, showlegend=False,
                    marker=_marker(color, MARKER_SIZE),
                    customdata=fail_block['Exp'],
                    hovertemplate='%{customdata}<br>Exp %{x}<br>phase separated<extra></extra>'))

        # --- A legend entry for the mark shape, which is a variable of its own --------------------
        traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', xaxis='x', yaxis='y',
            name='In Specification',
            marker=_marker(INK_SOFT, SPEC_MARKER_SIZE, symbol='triangle-up')))

        # --- The champion, and the in-spec names -------------------------------------------------
        for _, row in IN_SPEC.iterrows():
            is_champion = row['Exp'] == CHAMPION['Exp']
            annotations.append(dict(
                x=float(row['n']), y=float(row['obj']), xref='x', yref='y',
                text='<b>{}</b>  {:.3f}<br>{:.1f} nm'.format(
                    row['Exp'], row['obj'], row['size_nm'])
                if is_champion else '<b>{}</b>'.format(row['Exp']),
                showarrow=True, arrowhead=0, arrowwidth=1.1, arrowcolor=INK_SOFT,
                ax=0, ay=-56 if is_champion else -36, xanchor='center',
                font=dict(size=ANNOTATION_SIZE, color=INK, family=FONT_FAMILY)))

        # --- The break mark, and what the strip holds ---------------------------------------------
        annotations.append(dict(
            x=0, y=(MAIN_DOMAIN[1] + FAIL_DOMAIN[0]) / 2, xref='paper', yref='paper',
            xshift=-int(LEFT_MARGIN * 0.40), text='<b>≈</b>', showarrow=False,
            xanchor='center', yanchor='middle',
            font=dict(size=AXIS_TITLE_SIZE, color=INK, family=FONT_FAMILY)))
        annotations.append(dict(
            x=0.5, y=fail_y, xref='x2', yref='y2',
            xanchor='left', yanchor='middle', xshift=10,
            text='{} phase separated'.format(len(failed)), showarrow=False,
            font=dict(size=ANNOTATION_SIZE, color=INK_SOFT, family=FONT_FAMILY)))

        layout = go.Layout(
            title=dict(
                text='Campaign 1 — Optimisation Progression<br>'
                     '<span style="font-size:{}px;color:{}">Objective per formulation in '
                     'campaign order  ·  score-then-average over three repeats  ·  '
                     'lower is better</span>'.format(ANNOTATION_SIZE, INK_SOFT),
                font=dict(size=TITLE_SIZE, color=INK), x=0.5, y=0.975,
                xanchor='center', yanchor='top'),
            xaxis=dict(title='Experiment Number', range=x_range, domain=[0.0, 1.0],
                       anchor='y', tickmode='linear', tick0=0, dtick=5, **AXIS_COMMON),
            xaxis2=dict(range=x_range, domain=[0.0, 1.0], anchor='y2', matches='x',
                        showticklabels=False, ticks='', linecolor=INK, showline=True,
                        showgrid=False, mirror=True, linewidth=2, zeroline=False),
            yaxis=dict(title='Objective Function', range=y_range, domain=list(MAIN_DOMAIN),
                       anchor='x', tick0=0, dtick=y_dtick, **AXIS_COMMON),
            yaxis2=dict(range=fail_range, domain=list(FAIL_DOMAIN), anchor='x2',
                        tickmode='array', tickvals=[fail_y],
                        ticktext=['{:.0f}'.format(fail_y)], **AXIS_COMMON),
            shapes=shapes,
            annotations=annotations,
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            width=FIG_WIDTH, height=FIG_HEIGHT,
            margin=dict(l=LEFT_MARGIN, r=RIGHT_MARGIN, t=TOP_MARGIN, b=LEGEND_MARGIN),
            showlegend=True,
            # The bottom gutter. y < 0 is below the plot area, so the legend is never inside it.
            legend=dict(orientation='h', x=0.5, y=-0.19, xanchor='center', yanchor='top',
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
        'Campaign_Progress': (progress_figure, FIG_WIDTH, FIG_HEIGHT),
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
