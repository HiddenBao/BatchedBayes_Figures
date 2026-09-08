# --- Windows + conda DLL guard: must run before *any* other import --------------------------
# The numeric wheels delay-load their DLLs (MKL, OpenBLAS, libstdc++) from <env>/Library/bin,
# which is only on PATH once the environment is *activated*. PyCharm runs the configured conda
# interpreter directly rather than through `conda activate`, so a Run/Debug launch -- and a
# notebook kernel started the same way -- dies with exit code 0xC06D007F / 3228369023,
# STATUS_DELAY_LOAD_FAILED and no traceback.
#
# This sits above `import marimo` on purpose: marimo pulls in the numeric stack itself, so a
# guard inside a cell runs too late to save a plain `python <file>` launch.
#
# marimo's serialiser rewrites this module on every save and drops top-level statements that
# are not cells, so this block has been stripped before. If a kernel dies with 0xC06D007F and
# no traceback, check that the four lines below are still here before debugging anything else.
import os as _os
import sys as _sys

if _os.name == 'nt':
    _dll_dir = _os.path.join(_sys.prefix, 'Library', 'bin')
    if _os.path.isdir(_dll_dir):
        _os.add_dll_directory(_dll_dir)
        _os.environ['PATH'] = _dll_dir + _os.pathsep + _os.environ.get('PATH', '')
# --------------------------------------------------------------------------------------------

import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # Champions Head to Head Figure Suite

    One slide: **Campaign 1's champions against Campaign 2's best, on Campaign 2's objective and
    on every output that objective reads.**

    It is `Campaign2_Leaderboard`'s question opened up. That board ranks each track by one number;
    this slide takes the top three of each track and the three Campaign 1 champions revalidated on
    that track, and shows the readings the number came from -- against the barriers `campaign2`
    charges against, in `Loaded_Champions`' grammar.

    **Two sections, one per API.** A190 and fenofibrate were separate optimisations, and a
    formulation's objective depends on which API it was loaded with, so `B4` loaded with A190 and
    `B4` loaded with fenofibrate are two rows, not one row measured twice. Every panel is shared,
    so a value means the same thing top to bottom.

    **Campaign 1 is represented by `B4`, `S5` and `E2`** -- the three champions that were
    re-measured drug-loaded, which is the only reason they can carry a Campaign 2 score at all.
    They are *not* the top three of the Campaign 1 board: `D3` ranks second there and was never
    loaded, so it has no drug loading and no permeability and would be scored on three of five
    terms. `Campaign2_Leaderboard` states the same exclusion for the same reason.

    **Campaign 2's three are computed, not typed** -- the best three of each track by
    score-then-average, taken from the data and asserted against what this slide was drawn for.

    Scoring is **score-then-average**, as on both leaderboards: each replicate scored on its own,
    the mark is the mean of the three, the bar its standard deviation. The measurement panels are
    the other way round -- a mean of measurements -- and the objective panel is the mean of
    scores. The two are not the same quantity, so the objective panel is the one that matches the
    board.
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
    the wrong tree. The canvas is the house 1280 x 720.

    **One file.** Every row on this slide is drug-loaded and lives in the comprehensive dataset,
    which is this project's ground truth; the per-API CSVs are not opened. See **The `DoE*` rows**
    in [CLAUDE.md](../../CLAUDE.md) for why that matters.
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Champions_Head_to_Head' / 'Output'
    DATA_CSV = REPO_ROOT / 'data' / 'MicroemulsionFormulation_Comprehensive.csv'

    # The objective lives in Figures/objectives.py and is imported, never restated.
    if str(REPO_ROOT / 'Figures') not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / 'Figures'))
    from objectives import campaign1, campaign2

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
        campaign2,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shared chrome

    House style -- the `Breaking-the-Boundaries` suites', value for value: white ground, a 2 px
    black mirrored axis box, no gridlines, five type sizes (20 / 18 / 18 / 14 / 14), a centred
    title, a horizontal legend in a bottom gutter. `Loaded_Champions`' chrome, since this slide is
    its grammar with different rows.

    **Hue is the campaign here, and that is `Campaign2_Leaderboard`'s palette rather than
    `Loaded_Champions`'.** Every token still means what it means on the board it comes from:

    | token | hex | what it means | where else |
    | --- | --- | --- | --- |
    | `C1_COLOR` | `#2067F4` | a revalidated Campaign 1 champion | the Campaign 2 board, same rows, same role |
    | `A190_COLOR` | `#5A2E8C` | Campaign 2's A190 track | the A190 ramp's darkest step |
    | `FENO_COLOR` | `#00572B` | Campaign 2's fenofibrate track | that ramp's darkest step |

    On `Loaded_Champions` purple and green mean *loaded with this API* and blue means the blank
    Campaign 1 measurement. Here every mark is loaded and the API is already carried by the
    section, so hue is free to carry the one thing a section cannot say: **which campaign
    produced the formulation.** That is exactly the licence the Campaign 2 board runs on -- it
    puts the three champions in `#2067F4` beside Campaign 2's own rows in their track ramps -- and
    this slide is that board's rows, so it is the same figure's palette rather than a new reading.

    **The track ramps are used at one step, not three.** A batch ramp claims an ordering, and this
    slide draws three of a track's rows rather than the track, so two of three steps present would
    claim an order it does not show. Each track gets its darkest step -- the step
    `Loaded_Champions` already uses for that API, at matched lightness (L\* ~ 30 for both) so
    neither track reads as deeper than the other.

    Shape is the second channel and it carries the **API**, as on `Loaded_Champions`: diamond
    A190, square fenofibrate. So a blue diamond is a Campaign 1 champion loaded with A190, and a
    purple diamond is Campaign 2's own row on the same track -- hue says whose it is, shape says
    which API, and neither channel does the other's job.

    Boundaries are drawn in **ink**, never in a hue: dashed for a barrier `campaign2` charges
    against, dotted for the Campaign 1 hinge it replaced. A specification is not a series.
    """)
    return


@app.cell
def _(FIG_HEIGHT, FIG_WIDTH, go):
    C1_COLOR = '#2067F4'       # blue    -- a revalidated Campaign 1 champion; the deck primary
    A190_COLOR = '#5A2E8C'     # purple  -- Campaign 2's A190 track; that ramp's darkest step
    FENO_COLOR = '#00572B'     # green   -- Campaign 2's fenofibrate track; its darkest step

    INK = 'black'
    # Subtitles only. Everything that labels the geometry -- row names, section headers, tick
    # values -- is full black, because on a projector a grey label reads as washed out rather
    # than as quieter.
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    # The hairline between one row and the next. One weight, one colour, one dash for every rule
    # on the figure, section breaks included -- `Loaded_Champions`' value.
    ROW_RULE = 'rgba(0, 0, 0, 0.16)'
    # The pass side of every barrier, and the `Breaking-the-Boundaries` SCREEN_BAND value.
    PASS_BAND = 'rgba(0, 0, 0, 0.055)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    # Row labels and section headers sit in the y-tick gutter, and twelve of them at 18 pt would
    # take a third of the canvas width for `Campaign 1 - S5` alone. They are the one text on the
    # figure set below the house scale, at the legend size, because they label a table rather
    # than read a scale. The x ticks, which *are* the scales, keep 18.
    ROW_LABEL_SIZE = 14

    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    # --- The deck's own faces ------------------------------------------------------------
    # An SVG *references* a font, it does not embed one, so these render as themselves only
    # where both faces are installed and fall back to the house stack everywhere else. That is
    # why the figure is exported twice rather than switched over: the plain export stays the
    # portable one. Family names are exactly as Windows reports them -- 'Gmarket' has a
    # lowercase m, and the face is the Medium weight, so it is named, not asked for via
    # font-weight.
    BODY_FAMILY = 'Pretendard, ' + FONT_FAMILY
    HEADING_FAMILY = 'Gmarket Sans TTF Medium, Pretendard, ' + FONT_FAMILY

    # suffix -> (body face, heading face, tick face). '' is the default export, and it must
    # stay first: it is the one that survives being opened on a machine without the two faces.
    FONT_SCHEMES = {
        '': (FONT_FAMILY, FONT_FAMILY, FONT_FAMILY),
        '_Pretendard': (BODY_FAMILY, HEADING_FAMILY, HEADING_FAMILY),
    }

    # Sizes do NOT change between schemes, so the two exports are drop-in swaps for each other.

    MARKER_SIZE = 11
    MARKER_RING = 2
    ERROR_WIDTH = 1.4
    FRAME_WIDTH = 2

    LEGEND_MARGIN = 96   # bottom gutter the horizontal legend sits in


    def with_font_scheme(fig, body, heading, tick):
        """A copy of `fig` re-fonted: `heading` on the title and the frame, `body` elsewhere.

        Applied after the figure is built rather than threaded through the builder, so the two
        exports cannot drift: there is one figure, drawn once, wearing two type schemes. Heading
        text is tagged where it is written with `name='heading'`; everything else is body by
        definition, which is the safe default -- a new annotation joins the reading face rather
        than silently claiming to be a title.

        The **y axis is exempt from the tick face**: its ticks are the row names and the section
        headers, which are prose, not numbers. Only the x axes -- the value scales -- take the
        display face on their ticks, as in `Loaded_Champions`.
        """
        out = go.Figure(fig.to_dict())
        out.layout.font.family = body
        out.layout.title.font.family = heading
        out.layout.legend.font.family = body
        for _ann in out.layout.annotations:
            _ann.font.family = heading if _ann.name == 'heading' else body
        for _axis in out.select_xaxes():
            _axis.tickfont.family = tick
            _axis.title.font.family = heading
        for _axis in out.select_yaxes():
            _axis.tickfont.family = body
            _axis.title.font.family = heading
        return out


    AXIS_COMMON = dict(
        showline=True, linecolor=INK, linewidth=FRAME_WIDTH, mirror=True,
        tickcolor=INK, color=INK, ticks='outside',
        showgrid=False, zeroline=False,
        # tickangle=0 is not cosmetic. Six panels at 18 pt is tighter than the five
        # `Loaded_Champions` already had to pin, and plotly's response to tick labels it thinks
        # will collide is to rotate them to vertical -- which on one panel out of six reads as a
        # different kind of axis and pushes that panel's title down out of line with its
        # neighbours'. Pinning the angle turns a silent re-layout into a visible collision, and
        # the fix for a collision is fewer ticks.
        tickangle=0,
        tickfont=dict(size=TICK_SIZE), title_font=dict(size=AXIS_TITLE_SIZE),
    )

    print('canvas {} x {}'.format(FIG_WIDTH, FIG_HEIGHT))
    return (
        A190_COLOR,
        ANNOTATION_SIZE,
        AXIS_COMMON,
        AXIS_TITLE_SIZE,
        C1_COLOR,
        ERROR_WIDTH,
        FENO_COLOR,
        FONT_FAMILY,
        FONT_SCHEMES,
        INK,
        INK_SOFT,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        MARKER_RING,
        MARKER_SIZE,
        PASS_BAND,
        ROW_LABEL_SIZE,
        ROW_RULE,
        TITLE_SIZE,
        with_font_scheme,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The barriers, probed out of `objectives.campaign2`

    The same probe `Loaded_Champions` runs, and for the same reason: each constant below is a
    **kink** in one of `campaign2`'s component scores -- the value at which the component stops
    improving, starts being charged, or changes slope. They are stated here because a figure needs
    numbers to draw lines at, and then every one of them is checked against the function itself by
    evaluating `campaign2` either side of the claimed kink.

    That is the difference between importing a barrier and restating one. If upstream retunes the
    PDI hinge or the permeability knee, this cell raises rather than the slide quietly drawing a
    boundary the optimiser no longer uses.

    `PDI_HINGE_C1` is the exception: it is Campaign 1's hinge, probed against `campaign1`, and it
    is on the slide precisely because `campaign2` no longer has it -- this is the boundary the
    Campaign 1 champions were selected under, on a slide that ranks them under the one that
    replaced it.
    """)
    return


@app.cell
def _(campaign1, campaign2, np, pd):
    # Every value here is a kink in a `campaign2` component score. Asserted below, not trusted.
    SPEC_SIZE_NM = 100.0        # size_score is 0 at or below this and climbs above it
    PDI_HINGE_C2 = 0.1          # pdi_score crosses 0 here; below it the score is a bonus
    PDI_HINGE_C1 = 0.3          # Campaign 1's hinge -- superseded, and drawn to say so
    SPEC_ZETA_ABS = 10.0        # |zeta| below this is free
    DL_TARGET = 100.0           # drug loading is a V about 100 %
    DL_DEAD_ZONE = 5.0          # ... with a forgiving zone inside +/- this, then a steeper charge
    PERM_KNEE = 20e-6           # perm_score crosses 0 here; above it the score is a bonus

    # The neutral formulation: every component score is exactly 0 at these values, which is what
    # makes it a usable probe base -- one output is moved at a time and nothing else contributes.
    _BASE = dict(Droplet_Size=SPEC_SIZE_NM, PDI=PDI_HINGE_C2, Zeta_P=0.0, Phase_Sep=0.0,
                 Drug_Loading=DL_TARGET, Permeability=PERM_KNEE)


    def _probe(column, values, objective=campaign2):
        """`objective`'s component scores for the neutral formulation, one output swept."""
        frame = pd.DataFrame({k: np.full(len(values), v) for k, v in _BASE.items()})
        frame[column] = np.asarray(values, dtype=float)
        return objective(frame)


    _eps = 1e-9
    _zero = _probe('Droplet_Size', [SPEC_SIZE_NM])
    assert float(_zero['objective'].iloc[0]) == 0.0, \
        'the probe base is no longer the neutral formulation: {}'.format(_zero.iloc[0].to_dict())

    # Droplet size: flat below the barrier, climbing above it.
    _s = _probe('Droplet_Size',
                [SPEC_SIZE_NM - 50, SPEC_SIZE_NM, SPEC_SIZE_NM + 50])['size_score (w=3)']
    assert _s.iloc[0] == 0.0 and _s.iloc[1] == 0.0 and _s.iloc[2] > 0.0, \
        'size barrier is not at {} nm'.format(SPEC_SIZE_NM)

    # PDI: campaign 2 crosses zero at 0.1, campaign 1 changed slope at 0.3.
    _p = _probe('PDI', [PDI_HINGE_C2 - 0.05, PDI_HINGE_C2, PDI_HINGE_C2 + 0.05])['pdi_score (w=2)']
    assert _p.iloc[0] < 0.0 and abs(_p.iloc[1]) < _eps and _p.iloc[2] > 0.0, \
        'campaign2 PDI hinge is not at {}'.format(PDI_HINGE_C2)
    # Campaign 1's hinge is a *step*, not a slope change: below 0.3 the penalty is quartered, so
    # crossing it jumps the score by three quarters of the hinge value. Bracket it tightly and
    # check the size of that jump -- a slope change alone could not produce one.
    _p1 = _probe('PDI', [PDI_HINGE_C1 - 0.001, PDI_HINGE_C1 + 0.001],
                 objective=campaign1)['pdi_score (w=1)']
    assert abs((_p1.iloc[1] - _p1.iloc[0]) - 0.75 * PDI_HINGE_C1) < 0.01, \
        'campaign1 PDI hinge is not a quartering step at {}'.format(PDI_HINGE_C1)

    # |zeta|: free inside the boundary, charged outside it, and symmetric about zero.
    _z = _probe('Zeta_P', [-SPEC_ZETA_ABS, SPEC_ZETA_ABS, SPEC_ZETA_ABS + 5])['zeta_score (w=1)']
    assert _z.iloc[0] == 0.0 and _z.iloc[1] == 0.0 and _z.iloc[2] > 0.0, \
        '|zeta| barrier is not at {} mV'.format(SPEC_ZETA_ABS)

    # Drug loading: a shallow V inside the dead zone, a steeper one outside it, both edges alike.
    _d = _probe('Drug_Loading',
                [DL_TARGET - DL_DEAD_ZONE, DL_TARGET, DL_TARGET + DL_DEAD_ZONE])['dl_score (w=2)']
    assert abs(_d.iloc[0] - _d.iloc[2]) < _eps and _d.iloc[1] < _d.iloc[0], \
        'drug loading is not a V about {} %'.format(DL_TARGET)
    _inner = _probe('Drug_Loading', [DL_TARGET + DL_DEAD_ZONE - 1.0,
                                     DL_TARGET + DL_DEAD_ZONE])['dl_score (w=2)']
    _outer = _probe('Drug_Loading', [DL_TARGET + DL_DEAD_ZONE,
                                     DL_TARGET + DL_DEAD_ZONE + 1.0])['dl_score (w=2)']
    assert (_outer.iloc[1] - _outer.iloc[0]) > 3.0 * (_inner.iloc[1] - _inner.iloc[0]), \
        'the drug loading dead zone does not end at +/- {} %'.format(DL_DEAD_ZONE)

    # Permeability: charged below the knee, a bonus above it.
    _m = _probe('Permeability', [PERM_KNEE / 2, PERM_KNEE, PERM_KNEE * 2])['perm_score (w=3)']
    assert _m.iloc[0] > 0.0 and abs(_m.iloc[1]) < _eps and _m.iloc[2] < 0.0, \
        'permeability knee is not at {}'.format(PERM_KNEE)

    # This slide ranks Campaign 1 formulations on Campaign 2's objective, which is only worth
    # drawing because the two objectives read different outputs: campaign 1 reads three, campaign
    # 2 reads five. Checked rather than asserted in prose.
    for _col in ('Drug_Loading', 'Permeability'):
        _c1 = _probe(_col, [_BASE[_col] * 0.5, _BASE[_col] * 1.5], objective=campaign1)['objective']
        assert _c1.nunique() == 1, \
            'campaign1 reads {} -- the two-objective claim on this slide is wrong'.format(_col)

    print('barriers probed against objectives.py: size {:g} nm | PDI {:g} (was {:g}) | '
          '|zeta| {:g} mV | loading {:g} +/- {:g} % | perm {:g}'.format(
              SPEC_SIZE_NM, PDI_HINGE_C2, PDI_HINGE_C1, SPEC_ZETA_ABS,
              DL_TARGET, DL_DEAD_ZONE, PERM_KNEE))
    return (
        DL_DEAD_ZONE,
        DL_TARGET,
        PDI_HINGE_C1,
        PDI_HINGE_C2,
        PERM_KNEE,
        SPEC_SIZE_NM,
        SPEC_ZETA_ABS,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The data

    Twelve rows in two sections, six per API: **Campaign 2's best three on that track, and the
    three Campaign 1 champions revalidated with that API.** Each row is three replicates.

    **Campaign 2's three are computed.** Each of a track's own proposals is scored replicate by
    replicate with `objectives.campaign2`, averaged, and the best three taken -- then asserted
    against the set this slide was drawn for, so a change in the data fails here rather than
    silently redrawing the comparison. A track's proposals are the rows whose `Exp` carries its
    prefix, `A-` or `F-`; `CLAUDE.md` warns that the tag is the thing to check against `API_Name`
    rather than to trust, so the cell checks it.

    **Campaign 1's three are `Loaded_Champions`' rows**, and the set is named so this slide fails
    if that set moves: `CARRIED` is `Campaign1_Leaderboard`'s top-five rows that reached drug
    loading. They are not the Campaign 1 board's top three -- `D3` ranks second there and was
    never loaded, so it has no Campaign 2 score at all.

    **Rows are ordered by the objective inside each section, best first, both campaigns
    interleaved.** That is the whole comparison: if the Campaign 1 rows were grouped together the
    slide would have to be read twice to see where they land, and where they land is the point.
    Hue says which campaign a row came from, so the interleaving costs nothing.

    Five claims the cell asserts rather than assumes:

    - **every row is tagged with the API of the section it is drawn in** -- a hue and a shape both
      say which track, and neither is inferred from the id.
    - **every row has three replicates and none phase-separated** -- the `+50` term is not on this
      slide, and a separated row would put a mark 50 units off the objective panel.
    - **zeta is negative throughout**, so plotting \|z\| against a barrier on \|z\| is a flip and
      never a fold.
    - **every row label is unique**, including across the `Campaign 1` prefix -- `B4` the Campaign
      2 batch-B proposal 4 and `B4` the Campaign 1 champion are both on this figure, which is
      exactly why the prefix is spelled out rather than abbreviated to `C1`.
      `Campaign2_Leaderboard` makes the same argument for the same collision.
    - **no mark's mean is off its panel**, checked against the axis ranges in the figure cell.

    ### Two kinds of average, and they are not the same number

    The **objective panel is score-then-average** -- each replicate scored on its own, the mark is
    the mean of those scores -- which is what both leaderboards rank on, so a row's mark here is
    its bar there. The **measurement panels are means of measurements**, which is what a
    measurement panel can be. Scoring the means instead would give a different objective wherever
    a component is non-linear across a row's spread, and `Loaded_Champions` prints that quantity
    under its own name for exactly this reason. The two are never mixed.
    """)
    return


@app.cell
def _(DATA_CSV, campaign2, pd):
    # Campaign 1's three revalidated champions, per track: loaded id -> the deck name.
    #
    # `Ran5` is the paper's `F5` and both leaderboards render it `S5`; a row has to wear one name
    # across the deck or a reader cannot follow it from slide to slide, so the deck name wins over
    # the id -- see Figures/README.md.
    CHAMPION_IDS = {
        'A190': {'B4_A': 'B4', 'F5_A': 'S5', 'E2_A': 'E2'},
        'Feno': {'B4_F': 'B4', 'F5_F': 'S5', 'E2_F': 'E2'},
    }
    # `Campaign1_Leaderboard`'s CARRIED, by blank id: the top-five Campaign 1 rows that were
    # reformulated drug-loaded. Named so this slide fails if that set moves.
    CARRIED = {'B4', 'Ran5', 'E2'}
    _BLANK_OF = {'B4': 'B4', 'S5': 'Ran5', 'E2': 'E2'}

    SECTIONS = ('A190', 'Feno')
    SECTION_TITLE = {'A190': 'A190-Loaded', 'Feno': 'Fenofibrate-Loaded'}
    # A Campaign 2 proposal's id is `<track>-<batch><n>`; CLAUDE.md warns to check that prefix
    # against API_Name rather than trust it, which the assertion below does.
    TRACK_PREFIX = {'A190': 'A-', 'Feno': 'F-'}
    TOP_N = 3

    # What the computation below is expected to produce. It is not the input -- the top three are
    # taken from the data -- but a change in the data should fail here rather than quietly redraw
    # a slide whose title claims a comparison.
    EXPECTED_TOP = {'A190': ('A-B4', 'A-C5', 'A-B5'), 'Feno': ('F-B1', 'F-C3', 'F-B5')}

    # Spelled out rather than abbreviated to `C1`, because `C1` is also a Campaign 2 id -- batch
    # C, proposal 1 -- and a token that means two things on one figure is worth the left margin.
    # `Campaign2_Leaderboard` resolves the same collision the same way.
    C1_PREFIX = 'Campaign 1 &#183; '

    _MEASURED = ['Droplet_Size', 'PDI', 'Zeta_P', 'Drug_Loading', 'Permeability']

    ALL_ROWS = pd.read_csv(DATA_CSV)
    # Score-then-average, as on both leaderboards: every replicate scored on its own, first.
    ALL_ROWS['objective'] = campaign2(ALL_ROWS)['objective']

    assert set(_BLANK_OF) == {n for _ids in CHAMPION_IDS.values() for n in _ids.values()}, \
        'the deck names and the blank ids have drifted apart'
    assert set(_BLANK_OF.values()) == CARRIED, \
        'the champions are no longer Campaign1_Leaderboard CARRIED'
    assert set(ALL_ROWS['Exp']).issuperset(CARRIED), \
        'the blank champions are missing from the dataset'


    def _campaign2_top(api):
        """The best `TOP_N` of `api`'s own proposals, by score-then-average. Computed, not typed."""
        own = ALL_ROWS[ALL_ROWS['API_Name'].eq(api)
                       & ALL_ROWS['Exp'].str.startswith(TRACK_PREFIX[api])]
        ranked = own.groupby('Exp')['objective'].mean().sort_values()
        return list(ranked.index[:TOP_N])


    def _aggregate(exp):
        """One record for `exp`: measurement means and SDs, and its score-then-average objective."""
        rows = ALL_ROWS[ALL_ROWS['Exp'].eq(exp)]
        assert len(rows) == 3, '{}: expected 3 replicates, found {}'.format(exp, len(rows))
        assert (rows['Phase_Sep'] == 0).all(), \
            '{}: phase separated -- its +50 is off the objective panel'.format(exp)
        out = {'Exp': exp, 'api_name': rows['API_Name'].iloc[0],
               'objective': rows['objective'].mean(), 'objective_sd': rows['objective'].std()}
        for col in _MEASURED:
            out[col] = rows[col].mean()
            out[col + '_sd'] = rows[col].std()
        return out


    records = []
    for _api in SECTIONS:
        _top = _campaign2_top(_api)
        assert tuple(_top) == EXPECTED_TOP[_api], \
            "{}'s best {} are now {}, not {} -- the slide's comparison has moved".format(
                _api, TOP_N, tuple(_top), EXPECTED_TOP[_api])
        for _exp in _top:
            _rec = _aggregate(_exp)
            # A Campaign 2 row drops its track prefix: the section is one API top to bottom and
            # its header already carries that, as on the Campaign 2 board.
            _rec.update(section=_api, campaign='c2',
                        label=_exp[len(TRACK_PREFIX[_api]):])
            records.append(_rec)
        for _exp, _name in CHAMPION_IDS[_api].items():
            _rec = _aggregate(_exp)
            _rec.update(section=_api, campaign='c1', label=C1_PREFIX + _name)
            records.append(_rec)

    RUNS = pd.DataFrame(records)

    # The section a mark is drawn in is its API -- checked against the file, not read off the id.
    for _r in RUNS.itertuples():
        assert _r.api_name == _r.section, \
            '{} is tagged {} but is drawn in the {} section'.format(
                _r.Exp, _r.api_name, _r.section)

    # |zeta| is plotted against a boundary on |zeta|, which is only a sign flip while every
    # reading is negative. A positive one would fold onto the wrong side of that boundary.
    assert (RUNS['Zeta_P'] < 0).all(), \
        'zeta is positive for {} -- the |zeta| panel would fold it'.format(
            sorted(RUNS.loc[RUNS['Zeta_P'] >= 0, 'Exp']))

    # --- row order: the objective, inside each section, both campaigns interleaved -----------
    RUNS['_section_rank'] = RUNS['section'].map(SECTIONS.index)
    RUNS = RUNS.sort_values(['_section_rank', 'objective']).drop(columns='_section_rank')
    ROW_ORDER = {api: list(RUNS.loc[RUNS['section'].eq(api), 'label']) for api in SECTIONS}

    # `B4` the Campaign 2 proposal and `B4` the Campaign 1 champion are both on this figure. The
    # prefix is what keeps them apart, so check that it does.
    for _api in SECTIONS:
        assert len(set(ROW_ORDER[_api])) == len(ROW_ORDER[_api]), \
            '{}: two rows share a label -- {}'.format(_api, ROW_ORDER[_api])

    print(RUNS[['section', 'campaign', 'label', 'Exp', 'objective', 'objective_sd',
                'Droplet_Size', 'PDI', 'Zeta_P', 'Drug_Loading', 'Permeability']].to_string(
                    index=False, float_format=lambda v: '{:.4g}'.format(v)))
    for _api in SECTIONS:
        print('\n{} order (campaign2, best first): {}'.format(
            _api, '  >  '.join(ROW_ORDER[_api])))
    return ROW_ORDER, RUNS, SECTIONS, SECTION_TITLE


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The figure

    Six panels: **the objective, then the five outputs it is made of.** `Loaded_Champions`' five
    measurement panels keep their ranges exactly, so a value sits at the same place on both slides
    and a reader who has seen that one arrives knowing the scales.

    | panel | range | ticks | barrier |
    | --- | --- | --- | --- |
    | objective | -0.5 - 2.6 | 0 / 1 / 2 | none -- it is a score, not a measurement |
    | droplet size, nm | 0 - 270 | 0 / 100 / 200 | 100 nm |
    | PDI | 0 - 0.5 | 0 / 0.1 / 0.3 / 0.5 | 0.1, with Campaign 1's 0.3 dotted behind it |
    | zeta, \|z\| mV | 0 - 12 | 0 / 5 / 10 | 10 mV |
    | drug loading, % | 88 - 116 | 95 / 105 | 100 +/- 5 |
    | permeability, x10^-6 | 0 - 36 | 0 / 10 / 20 / 30 | 20 |

    **The panels are not equally wide, and that is what the sixth panel costs.** An even split
    makes every box narrower than `Permeability, x10^-6` set at the axis-title size, while leaving
    the objective -- three ticks and a nine-letter title -- with width it does not use. Each
    panel's `width` is the share of the row it takes, and it is set by what that panel has to
    carry: a title and a tick set. There is no shared scale between panels, so a width claims
    nothing about the values inside it.

    Two titles are shorter than `Loaded_Champions`' for the same reason -- `Objective` rather than
    `Campaign 2 objective`, which the subtitle says instead, and `Zeta, \|z\| mV` rather than
    `Zeta potential, \|z\| mV`. Shortened rather than set smaller: the house type scale is already
    departed from once on this slide, for the row labels, and once is enough.

    **The objective panel carries no barrier and no shaded band**, because there is no bar to
    clear on it: `campaign2` is a loss with no pass mark, and shading a side of it would invent a
    specification the optimiser does not have. It is drawn first because it is the answer and the
    other five are the working. Its axis starts **below zero** -- the PDI and permeability terms
    both have a bonus side, so a score can be slightly negative, and one row's spread reaches
    there.

    Every other panel shades the side that **satisfies** its barrier, which is why the shading is
    a range rather than a direction: below 100 nm, below a PDI of 0.1, inside \|z\| < 10,
    *between* 95 and 105 % loading, and *above* a permeability of 20 x 10^-6 -- the one output
    where more is better, and `campaign2` pays a bonus for it.

    **No boundary is labelled.** Its value is an axis tick instead, so a reader takes it off the
    same scale as the data rather than from a caption floating beside the line -- and every
    barrier is asserted to be one of that panel's ticks.

    Permeability is drawn in units of 10^-6, stated in the axis title, because the raw column is
    in the 10^-6 - 10^-5 decade and six panels have no width for exponent tick labels. **No unit
    is named beyond the magnitude**, and deliberately: `data/` records none, and neither
    `objectives.py` nor anything else in this repo states one.

    ### Rows, sections and rules

    Twelve rows of one mark each, in two sections. A **section header sits in the label gutter**
    in its own band -- `A190-Loaded`, `Fenofibrate-Loaded` -- rather than floating above the
    panels, because the panels are shared and a header over one of six would look like that
    panel's caption. The gutter is the one column that is not a value scale, so it is where the
    table's structure goes.

    **Every row is closed by a hairline**, one segment per panel, at one weight and one colour
    throughout -- the section break included. A paper-width rule is the obvious implementation and
    the wrong drawing: it runs on through the gaps between the panels and through the label
    gutter, turning the white space that separates six boxes into ruled space. With six panels to
    read across, the rules are doing more work here than on `Loaded_Champions`, where a band held
    three marks and the offsets grouped them.

    Row labels are set at **14 pt, not the tick 18** -- the one departure from the house scale.
    They are twelve labels on a table rather than a reading of a scale, and `Campaign 1 - S5` at
    18 pt takes a third of the canvas width for the gutter alone. The x ticks, which *are* the
    scales, keep 18.

    ### Error bars, and the one that runs off the axis

    Every mark is a mean of three replicates with their standard deviation. One of them,
    fenofibrate-loaded `S5`, has a droplet-size standard deviation larger than its mean -- its
    three replicates came in at 193.9, 12.7 and 13.0 nm -- so its bar reaches the left edge of the
    size panel and stops there. That is the axis clipping a bar, not the bar ending: the
    formulation is bimodal across replicates, and a spread that wide *is* the reading for that
    row. It is the same row `Loaded_Champions` says this about, and it is the reason the objective
    panel's spreads are worth drawing at all.
    """)
    return


@app.cell
def _(
    A190_COLOR,
    ANNOTATION_SIZE,
    AXIS_COMMON,
    AXIS_TITLE_SIZE,
    C1_COLOR,
    DL_DEAD_ZONE,
    DL_TARGET,
    ERROR_WIDTH,
    FENO_COLOR,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    MARKER_RING,
    MARKER_SIZE,
    PASS_BAND,
    PDI_HINGE_C1,
    PDI_HINGE_C2,
    PERM_KNEE,
    ROW_LABEL_SIZE,
    ROW_ORDER,
    ROW_RULE,
    RUNS,
    SECTIONS,
    SECTION_TITLE,
    SPEC_SIZE_NM,
    SPEC_ZETA_ABS,
    TITLE_SIZE,
    go,
):
    # Hue is the campaign; shape is the API. Both tokens are already in the deck: `#2067F4` is a
    # revalidated Campaign 1 champion on the Campaign 2 board -- these same rows in this same
    # role -- and the two track hues are the darkest step of each track's ramp, which is what
    # `Loaded_Champions` uses for the two APIs.
    #
    # The ramps are used at ONE step rather than three. A batch ramp claims an ordering, and this
    # slide draws three rows of a track rather than the track, so two of three steps present
    # would claim an order it does not show.
    CAMPAIGN_COLOR = {
        ('c1', 'A190'): C1_COLOR, ('c1', 'Feno'): C1_COLOR,
        ('c2', 'A190'): A190_COLOR, ('c2', 'Feno'): FENO_COLOR,
    }
    # `Loaded_Champions`' shapes, unchanged: diamond A190, square fenofibrate.
    SECTION_SYMBOL = {'A190': 'diamond', 'Feno': 'square'}

    # Four hue/shape combinations, three legend entries: the Campaign 1 champions are one series
    # across both sections and take the shape of the section they are drawn in, so the entry
    # shows the diamond and the row's own mark says which API. Prose belongs in the subtitle.
    LEGEND_ENTRIES = [
        ('Campaign 1 champion', C1_COLOR, 'diamond'),
        ('Campaign 2 &#183; A190', A190_COLOR, 'diamond'),
        ('Campaign 2 &#183; Fenofibrate', FENO_COLOR, 'square'),
    ]

    # One entry per panel, left to right: the objective, then the five outputs it reads.
    #
    # `pass_range` is the interval that SATISFIES the barrier, shaded. It is a range rather than
    # a direction because the barriers do not all point the same way: size, PDI and |zeta| pass
    # below, drug loading passes *between* two edges, and permeability passes *above*.
    #
    # `lines` are the barriers themselves, dashed. `soft_lines` is the one superseded boundary in
    # the deck: Campaign 1's PDI hinge at 0.3, dotted, so a reader can see where the bar was
    # before Campaign 2 moved it. No line is labelled -- every value in `lines` and `soft_lines`
    # is in `ticks` instead, read off the same scale as the data.
    #
    # `absolute` plots |value|; `scale` divides before plotting, for an axis whose raw column is
    # in a decade six panels have no width to tick in exponents.
    #
    # The objective panel has neither `pass_range` nor `lines`: `campaign2` is a loss with no
    # pass mark, and shading a side of it would invent a specification the optimiser lacks.
    PANELS = [
        # `Objective` alone, not `Campaign 2 objective`: the subtitle names whose objective
        # this is, and the panel is the narrowest on the slide. See `width` below.
        dict(key='objective', title='Objective', width=0.60,
             axis_range=(-0.5, 2.6), ticks=(0, 1, 2)),
        dict(key='Droplet_Size', title='Droplet size, nm', width=1.00,
             axis_range=(0, 270), ticks=(0, 100, 200),
             pass_range=(0, SPEC_SIZE_NM), lines=(SPEC_SIZE_NM,)),
        dict(key='PDI', title='PDI', width=0.92,
             axis_range=(0, 0.5), ticks=(0, 0.1, 0.3, 0.5),
             pass_range=(0, PDI_HINGE_C2), lines=(PDI_HINGE_C2,),
             soft_lines=(PDI_HINGE_C1,)),
        # `Loaded_Champions` writes this `Zeta potential, |&#950;| mV`; at six panels that
        # title is wider than its own box. Shortened rather than set smaller -- the house scale
        # is already departed from once on this slide, for the row labels.
        dict(key='Zeta_P', title='Zeta, |&#950;| mV', absolute=True, width=0.86,
             axis_range=(0, 12), ticks=(0, 5, 10),
             pass_range=(0, SPEC_ZETA_ABS), lines=(SPEC_ZETA_ABS,)),
        # Ticked at the two dead-zone edges and NOT at 100, as on `Loaded_Champions`: three
        # labels inside a sixth of the canvas collide at 18 pt, and 100 is the one of the three
        # that is not a barrier -- the target is the shaded band, which the band draws better.
        dict(key='Drug_Loading', title='Drug loading, %', width=1.00,
             axis_range=(88, 116), ticks=(95, 105),
             pass_range=(DL_TARGET - DL_DEAD_ZONE, DL_TARGET + DL_DEAD_ZONE),
             lines=(DL_TARGET - DL_DEAD_ZONE, DL_TARGET + DL_DEAD_ZONE)),
        dict(key='Permeability',
             title='Permeability, &#215;10<sup>&#8722;6</sup>', scale=1e-6, width=1.30,
             axis_range=(0, 36), ticks=(0, 10, 20, 30),
             pass_range=(PERM_KNEE / 1e-6, 36), lines=(PERM_KNEE / 1e-6,)),
    ]

    # Every barrier has to be readable off its own panel's ticks and has to be inside its own
    # axis. Both are easy to break by nudging a range; neither is easy to see.
    for _panel in PANELS:
        for _line in tuple(_panel.get('lines', ())) + tuple(_panel.get('soft_lines', ())):
            # Compared with a tolerance, not for equality: a barrier divided by its panel's
            # `scale` lands a few ulps off the round number it is meant to be (20e-6 / 1e-6 is
            # 20.000000000000004), which is invisible on the slide and fatal to an `in` test.
            assert any(abs(_line - _t) < 1e-9 for _t in _panel['ticks']), \
                '{}: the barrier at {} is not an axis tick'.format(_panel['key'], _line)
            assert _panel['axis_range'][0] <= _line <= _panel['axis_range'][1], \
                '{}: the barrier at {} is off the axis'.format(_panel['key'], _line)
    assert [p['key'] for p in PANELS[1:]] == ['Droplet_Size', 'PDI', 'Zeta_P',
                                              'Drug_Loading', 'Permeability'], \
        'the panels after the objective no longer cover the five outputs campaign2 reads'
    assert not (set(PANELS[0]) & {'pass_range', 'lines', 'soft_lines'}), \
        'the objective panel draws a barrier -- campaign2 has no pass mark'
    # Widths are shares of one row, so a panel without one would silently take a share of nothing.
    assert all(_p.get('width', 0) > 0 for _p in PANELS), \
        'every panel declares the share of the row it takes'

    # No mark's mean is off its panel. An error bar may run off -- one does, and the prose above
    # says which -- but a clipped *mean* is a value the slide silently does not show.
    for _panel in PANELS:
        _scale = _panel.get('scale', 1.0)
        _v = RUNS[_panel['key']].abs() if _panel.get('absolute') else RUNS[_panel['key']]
        _v = _v / _scale
        assert _v.between(*_panel['axis_range']).all(), \
            '{}: {} is off the panel'.format(
                _panel['key'], sorted(RUNS.loc[~_v.between(*_panel['axis_range']), 'Exp']))


    def build_slide(title, subtitle):
        """The one figure. Rows, sections, rules and panels all come off the band edges below."""
        panels = [dict(p) for p in PANELS]

        # --- row bands ----------------------------------------------------------------------
        # Bands are stacked downward from the top: a header band, that section's rows, the next
        # header band, its rows. The header is a band rather than a floating annotation because
        # it lives in the y-tick gutter, which is the one column that is not a value scale.
        #
        # The rules, the tick positions and the axis range are all computed from these edges, so
        # a change to one height moves everything together.
        HEADER_BAND = 0.9   # the section header's own band, in units of a data row's

        _bands = []
        for _api in SECTIONS:
            _bands.append(('header', _api, HEADER_BAND))
            for _label in ROW_ORDER[_api]:
                _bands.append(('row', (_api, _label), 1.0))

        _edges, _e = [], sum(_h for _, _, _h in _bands)
        for _kind, _what, _h in _bands:
            _edges.append((_kind, _what, _e, _e - _h))
            _e -= _h

        _y_of = {}
        for _kind, _what, _top, _bot in _edges:
            _key = _what if _kind == 'row' else ('header', _what)
            _y_of[_key] = (_top + _bot) / 2.0
        # A rule under every band but the last. The section break is one of them and wears the
        # same weight, colour and dash: it is already said by the header above it.
        _rule_ys = [_bot for _, _, _, _bot in _edges[:-1]]
        # The box closes the outer bands exactly as the rules close the inner ones -- no pad, so
        # the first header sits the same distance below the frame as it does above its rule.
        _y_range = [_edges[-1][3], _edges[0][2]]

        _tick_vals, _tick_text = [], []
        for _kind, _what, _top, _bot in _edges:
            if _kind == 'header':
                _tick_vals.append(_y_of[('header', _what)])
                _tick_text.append('<b>{}</b>'.format(SECTION_TITLE[_what]))
            else:
                _tick_vals.append(_y_of[_what])
                _tick_text.append(_what[1])

        # The panels run across the house width, sharing one row-label gutter. The gutter fits
        # `Fenofibrate-Loaded` at ROW_LABEL_SIZE, which is the longest thing in it.
        #
        # The panels split what is left in the proportions their `width` gives, NOT evenly.
        # Six panels is one more than `Loaded_Champions` carries, and an even split makes every
        # box narrower than `Permeability, x10^-6` set at the axis-title size while leaving the
        # objective -- three ticks and a nine-letter title -- with width it does not use. There
        # is no shared scale between panels, so a panel's width claims nothing about its values;
        # what it has to carry is a title and a tick set, and that is what sets it.
        #
        # The gap has to clear two tick labels, not one: every panel's last tick sits on its own
        # right edge and its neighbour's first tick on the left edge, so a gap sized for one
        # label runs them together.
        _gutter, _right, _gap = 0.128, 0.988, 0.028
        _avail = _right - _gutter - _gap * (len(panels) - 1)
        _unit = _avail / sum(_p['width'] for _p in panels)
        _x0 = _gutter
        for _i, _panel in enumerate(panels):
            _span = _unit * _panel['width']
            _panel['domain'] = [_x0, _x0 + _span]
            _panel['suffix'] = '' if _i == 0 else str(_i + 1)
            _x0 += _span + _gap

        _panel_top, _panel_bottom = 0.875, 0.165

        def _panel_traces(panel):
            """One marker trace per (campaign, section) for one panel: one trace, one hue."""
            _scale = panel.get('scale', 1.0)
            _out = []
            for _campaign in ('c2', 'c1'):
                for _api in SECTIONS:
                    _sub = RUNS[RUNS['campaign'].eq(_campaign) & RUNS['section'].eq(_api)]
                    if _sub.empty:
                        continue
                    _x, _y, _e = [], [], []
                    for _r in _sub.itertuples():
                        _v = getattr(_r, panel['key'])
                        if _v != _v:                 # NaN -- the measurement was never made
                            continue
                        _sd = getattr(_r, panel['key'] + '_sd')
                        _x.append((abs(_v) if panel.get('absolute') else _v) / _scale)
                        _y.append(_y_of[(_api, _r.label)])
                        _e.append((0.0 if _sd != _sd else _sd) / _scale)
                    _c = CAMPAIGN_COLOR[(_campaign, _api)]
                    _out.append(go.Scatter(
                        x=_x, y=_y, xaxis='x' + panel['suffix'], yaxis='y' + panel['suffix'],
                        mode='markers', hoverinfo='skip', showlegend=False,
                        error_x=dict(type='data', array=_e, color=_c,
                                     thickness=ERROR_WIDTH, width=5),
                        marker=dict(size=MARKER_SIZE, color=_c, symbol=SECTION_SYMBOL[_api],
                                    line=dict(width=MARKER_RING, color='white')),
                    ))
            return _out

        _traces = []
        for _panel in panels:
            _traces += _panel_traces(_panel)

        # --- legend proxies -----------------------------------------------------------------
        # Three series, then the two barrier strokes. The lines are in the legend rather than
        # annotated on the PDI panel because both appear on more than one panel between them,
        # and a caption beside one line would read as belonging to that panel alone.
        for _name, _colour, _symbol in LEGEND_ENTRIES:
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='markers', name=_name,
                marker=dict(size=MARKER_SIZE, color=_colour, symbol=_symbol,
                            line=dict(width=1.4, color=INK))))
        for _name, _dash in (("Campaign 2&#8217;s target", 'dash'),
                             ('Campaign 1 target', 'dot')):
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='lines', name=_name,
                line=dict(color=INK, width=1.8, dash=_dash)))

        _shapes = []
        for _panel in panels:
            _ref = 'x' + _panel['suffix']
            if 'pass_range' in _panel:
                _shapes.append(dict(
                    type='rect', xref=_ref, yref='paper',
                    x0=_panel['pass_range'][0], x1=_panel['pass_range'][1],
                    y0=_panel_bottom, y1=_panel_top,
                    fillcolor=PASS_BAND, line=dict(width=0), layer='below'))
            for _line in _panel.get('soft_lines', ()):
                _shapes.append(dict(
                    type='line', xref=_ref, yref='paper', x0=_line, x1=_line,
                    y0=_panel_bottom, y1=_panel_top,
                    line=dict(color=INK_SOFT, width=1.6, dash='dot')))
            for _line in _panel.get('lines', ()):
                _shapes.append(dict(
                    type='line', xref=_ref, yref='paper', x0=_line, x1=_line,
                    y0=_panel_bottom, y1=_panel_top,
                    line=dict(color=INK, width=1.8, dash='dash')))

        # --- row rules ----------------------------------------------------------------------
        # Drawn ONE SEGMENT PER PANEL, against that panel's own x axis, rather than as a single
        # paper-width line: a paper-width rule runs on through the gaps between the panels and
        # through the label gutter, which turns the white space that separates the panels into
        # ruled space and makes six boxes read as one table with gaps cut out of it.
        for _rule_y in _rule_ys:
            for _panel in panels:
                _shapes.append(dict(
                    type='line', xref='x' + _panel['suffix'], yref='y' + _panel['suffix'],
                    x0=_panel['axis_range'][0], x1=_panel['axis_range'][1],
                    y0=_rule_y, y1=_rule_y,
                    line=dict(color=ROW_RULE, width=1.0), layer='below'))

        _annotations = [
            dict(xref='paper', yref='paper', x=0.5, y=1.0, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK), name='heading',
                 text='<b>{}</b>'.format(title)),
            dict(xref='paper', yref='paper', x=0.5, y=0.955, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text=subtitle),
        ]

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=dict(l=10, r=10, t=104, b=LEGEND_MARGIN),
            shapes=_shapes, annotations=_annotations,
            legend=dict(orientation='h', xanchor='center', x=0.5, yanchor='top', y=-0.04,
                        font=dict(size=LEGEND_SIZE), itemsizing='constant',
                        bgcolor='rgba(0,0,0,0)'),
        )
        # Only the leftmost panel carries the row labels; the rest share its scale with blank
        # ticks, so the panels read as one table rather than as six separate charts.
        for _i, _panel in enumerate(panels):
            _s = _panel['suffix']
            _layout['xaxis' + _s] = dict(
                AXIS_COMMON, domain=_panel['domain'], anchor='y' + _s,
                title=dict(text=_panel['title'], font=dict(size=AXIS_TITLE_SIZE)),
                range=list(_panel['axis_range']),
                tickmode='array', tickvals=list(_panel['ticks']))
            _layout['yaxis' + _s] = dict(
                AXIS_COMMON, domain=[_panel_bottom, _panel_top], anchor='x' + _s,
                range=list(_y_range), tickmode='array', tickvals=_tick_vals,
                ticktext=_tick_text if _i == 0 else ['' for _ in _tick_vals],
                tickfont=dict(size=ROW_LABEL_SIZE), ticks='')
        return go.Figure(data=_traces, layout=_layout)


    showdown_figure = build_slide(
        title='Campaign 2&#8217;s best against the champions it inherited',
        subtitle='Top three per API track and Campaign 1&#8217;s three revalidated champions, '
                 'ranked on Campaign 2&#8217;s objective &#8212; lower is better &#8212; and on '
                 'every output it reads')
    showdown_figure
    return (showdown_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export

    The house 1280 x 720, one data unit to one exported pixel. `EXPORT_FORMATS` writes a 2x raster
    alongside if `png` is added to it.

    **Exported twice, once per entry in `FONT_SCHEMES`.**

    | file | body | headings |
    | --- | --- | --- |
    | `Champions_Head_to_Head.svg` | `Open Sans` | `Open Sans` |
    | `Champions_Head_to_Head_Pretendard.svg` | Pretendard | Gmarket Sans TTF Medium |

    Headings are the slide title, the axis titles and the x-axis ticks; body is everything else --
    the subtitle, the legend, the row names and the section headers. The y axis is body on
    purpose: its ticks are prose, not a scale.

    **Sizes are identical in both**, so a `_Pretendard` export is a drop-in replacement for its
    plain twin and nothing has to be re-checked for fit.

    The plain export exists because **an SVG references a font rather than embedding one**. The
    `_Pretendard` file renders as itself only where both faces are installed; anywhere else it
    falls back and the metrics shift.
    """)
    return


@app.cell
def _(
    EXPORT_FORMATS,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_SCHEMES,
    OUTPUT_DIR,
    PNG_SCALE,
    showdown_figure,
    with_font_scheme,
):
    FIGURES = {
        'Champions_Head_to_Head': (showdown_figure, FIG_WIDTH, FIG_HEIGHT),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for _stem, (_fig, _w, _h) in FIGURES.items():
        for _suffix, (_body, _heading, _tick) in FONT_SCHEMES.items():
            _themed = with_font_scheme(_fig, _body, _heading, _tick)
            for _fmt in EXPORT_FORMATS:
                _path = OUTPUT_DIR / '{}{}.{}'.format(_stem, _suffix, _fmt)
                _themed.write_image(
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
