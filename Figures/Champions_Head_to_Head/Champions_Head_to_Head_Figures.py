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

    **Two boxes, one per API.** A190 and fenofibrate were separate optimisations, and a
    formulation's objective depends on which API it was loaded with, so `B4` loaded with A190 and
    `B4` loaded with fenofibrate are two rows, not one row measured twice -- and two rankings, not
    one list with a divider in it. Each API gets its own closed axis box with its own ticks. Every
    panel column is one scale across both, so a value means the same thing in either.

    **Droplet size carries a goal as well as a barrier.** `campaign2` stops charging below 100 nm;
    the project is aiming at 10. That panel is drawn on a log axis with a band that deepens toward
    the goal, and the goal is the one number on the slide that is *not* in `objectives.py` -- so
    it is probed for the objective's flatness rather than for a kink.

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

    `SIZE_GOAL_NM` is the other exception, and the opposite kind. It is the **formulation's own
    goal** -- a droplet size heading for 10 nm rather than merely one under the 100 nm the
    objective stops charging at -- and `campaign2` does not encode it. So it is probed for
    **flatness**: the cell asserts the size score is zero at 10, 50 and 100 nm alike. Every other
    value here is checked to show the objective bends there; this one is checked to show it does
    not, which is what keeps the graded band the size panel draws from being mistaken for
    something read out of the code.
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

    # --- the one number on this slide that is NOT in the objective ---------------------------
    # The formulation goal: a droplet size heading for 10 nm, not merely one under the 100 nm
    # the objective stops charging at. It is a target the project holds, and `campaign2` does
    # not encode it -- which is exactly why the check below is a check for FLATNESS rather than
    # for a kink. Every other boundary on this slide is probed to show the objective bends
    # there; this one is probed to show it does not, so the graded band that draws it can never
    # be mistaken for something read out of objectives.py.
    SIZE_GOAL_NM = 10.0
    _g = _probe('Droplet_Size', [SIZE_GOAL_NM, SPEC_SIZE_NM / 2, SPEC_SIZE_NM])['size_score (w=3)']
    assert (_g == 0.0).all(), \
        'campaign2 now pays for size below {} nm -- the goal is a barrier and should be probed ' \
        'as one'.format(SPEC_SIZE_NM)
    assert SIZE_GOAL_NM < SPEC_SIZE_NM, 'the size goal is not inside the size barrier'

    print('barriers probed against objectives.py: size {:g} nm | PDI {:g} (was {:g}) | '
          '|zeta| {:g} mV | loading {:g} +/- {:g} % | perm {:g}'.format(
              SPEC_SIZE_NM, PDI_HINGE_C2, PDI_HINGE_C1, SPEC_ZETA_ABS,
              DL_TARGET, DL_DEAD_ZONE, PERM_KNEE))
    print('formulation goal, NOT in the objective: size {:g} nm (campaign2 is flat below '
          '{:g} nm)'.format(SIZE_GOAL_NM, SPEC_SIZE_NM))
    return (
        DL_DEAD_ZONE,
        DL_TARGET,
        PDI_HINGE_C1,
        PDI_HINGE_C2,
        PERM_KNEE,
        SIZE_GOAL_NM,
        SPEC_SIZE_NM,
        SPEC_ZETA_ABS,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The data

    Twelve rows in two boxes, six per API: **Campaign 2's best three on that track, and the three
    Campaign 1 champions revalidated with that API.** Each row is three replicates.

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

    **Rows are ordered by the objective inside each box, best first, both campaigns interleaved.**
    That is the whole comparison: if the Campaign 1 rows were grouped together the slide would
    have to be read twice to see where they land, and where they land is the point. Hue says which
    campaign a row came from, so the interleaving costs nothing.

    Five claims the cell asserts rather than assumes:

    - **every row is tagged with the API of the box it is drawn in** -- a hue and a shape both say
      which track, and neither is inferred from the id.
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

    Six panels: **the objective, then the five outputs it is made of**, each drawn twice -- once
    per API box. Four of the five measurement panels keep `Loaded_Champions`' ranges exactly, so a
    value sits at the same place on both slides; size is the exception, and the next section says
    why.

    | panel | range | ticks | barrier |
    | --- | --- | --- | --- |
    | objective | -0.5 - 2.6 | 0 / 1 / 2 | none -- it is a score, not a measurement |
    | droplet size, nm | 8 - 260, **log** | 10 / 30 / 100 | 100 nm, over a band deepening to the 10 nm goal |
    | PDI | 0 - 0.5 | 0 / 0.1 / 0.3 / 0.5 | 0.1, with Campaign 1's 0.3 dotted behind it |
    | zeta, \|z\| mV | 0 - 12 | 0 / 5 / 10 | 10 mV |
    | drug loading, % | 88 - 116 | 95 / 105 | 100 +/- 5 |
    | permeability, x10^-6 | 0 - 36 | 0 / 10 / 20 / 30 | 20 |

    ### Size: a goal, not just a barrier -- and a log axis to draw it on

    `campaign2` charges nothing for droplet size below 100 nm. The project's own goal is smaller
    than that: **toward 10 nm**, where 11 nm is meaningfully better than 24 and 24 better than 87.
    The objective cannot say so, and the barrier slide's flat pass band cannot either -- it marks
    a threshold, and every row on this figure is already inside it.

    Two changes carry it, and each fixes half the problem:

    - **The band is graded.** Instead of one flat tone across the pass side, the size panel's
      shading deepens from the `PASS_BAND` value at the 100 nm barrier to its darkest at 10 nm,
      and stays there below it. A flat band says *inside or outside*; a graded one says *and
      further in is better*, which is the claim. The dashed barrier at 100 stays exactly as it is
      on every other panel, so what the objective charges and what the project is aiming at are
      two marks, not one.
    - **The axis is logarithmic.** On the linear 0-270 axis the barrier slide uses, nine of these
      twelve rows fall inside the first tenth of the box and 10 nm sits four pixels off the axis
      line -- there is nowhere on that panel to draw a goal, and nowhere to see the difference
      between 11 nm and 24. On a log axis equal ratios are equal distances, so the three-way split
      between Campaign 2's 11-14 nm cluster, `E2`'s 87 and `B4`'s 212 is the panel's main feature
      rather than a crowd at the left edge.

    **This is the one number on the slide that is not in `objectives.py`**, so the barriers cell
    probes it the other way round: it asserts `campaign2`'s size score is *flat* at 10 nm, at
    50 nm and at 100 nm. Every other boundary here is checked to show the objective bends there;
    the goal is checked to show it does not, which is what makes the graded band a statement of
    intent rather than a boundary invented and then drawn as if it had been read off the code.

    Two plotly details, because both fail silently. On a log axis `range` is in log10 while marker
    data, `tickvals` and shape coordinates are in data units -- an older contract put shapes in
    log10 too, and under it every band and barrier on this panel lands left of the axis minimum
    and simply does not draw. `SHAPES_IN_LOG_UNITS` names the convention and an assertion checks
    it. And a log axis cannot draw an error bar through zero, so the lower whisker is clamped to
    the axis minimum; the one bar that needs it is named below.

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
    a range rather than a direction: below a PDI of 0.1, inside \|z\| < 10, *between* 95 and 105 %
    loading, and *above* a permeability of 20 x 10^-6 -- the one output where more is better, and
    `campaign2` pays a bonus for it. Size is the panel that shades a *direction* as well, and it
    is the only one with a goal to point at.

    **No boundary is labelled.** Its value is an axis tick instead, so a reader takes it off the
    same scale as the data rather than from a caption floating beside the line -- and every
    barrier is asserted to be one of that panel's ticks.

    Permeability is drawn in units of 10^-6, stated in the axis title, because the raw column is
    in the 10^-6 - 10^-5 decade and six panels have no width for exponent tick labels. **No unit
    is named beyond the magnitude**, and deliberately: `data/` records none, and neither
    `objectives.py` nor anything else in this repo states one.

    ### Two boxes, not one box with a rule across it

    **Each API gets its own axis box**, so the figure is six panel columns by two boxes -- twelve
    axis pairs. The two halves are two rankings that happen to share a scale, not one ranking with
    a divider in it: a formulation's objective depends on which API it was loaded with, so `B4`
    loaded with A190 and `B4` loaded with fenofibrate are not comparable rows in one list. A
    closed box says that; a hairline across a single box only implied it, and left the reader to
    decide whether the twelve rows were one ordering.

    **Both boxes carry their own x ticks**, so either can be read on its own — which is the point
    of separating them. The **axis titles are under the bottom box only**: a column is one scale,
    and naming it twice would claim there are two.

    Each box's caption sits **left-aligned over the row-label gutter** rather than centred over
    the panels. It names the rows, and a caption centred over six boxes reads as a title for
    whichever panel it happens to land on.

    Row bands are identical in the two boxes -- six unit bands, top first -- so a rank sits on the
    same pixel in either and the two rankings can be read against each other.

    **Every row is closed by a hairline**, one segment per panel, at one weight and one colour
    throughout. A paper-width rule is the obvious implementation and the wrong drawing: it runs on
    through the gaps between the panels and through the label gutter, turning the white space that
    separates the boxes into ruled space. With six panels to read across, the rules are doing more
    work here than on `Loaded_Champions`, where a band held three marks and the offsets grouped
    them.

    Row labels are set at **14 pt, not the tick 18** -- the one departure from the house scale.
    They are twelve labels on a table rather than a reading of a scale, and `Campaign 1 - S5` at
    18 pt takes a third of the canvas width for the gutter alone. The x ticks, which *are* the
    scales, keep 18.

    ### Error bars, and the one that runs off the axis

    Every mark is a mean of three replicates with their standard deviation. One of them,
    fenofibrate-loaded `S5`, has a droplet-size standard deviation larger than its mean -- its
    three replicates came in at 193.9, 12.7 and 13.0 nm -- so its lower whisker would end below
    zero, which a log axis cannot draw at all. It is **clamped to the axis minimum**, so the bar
    reaches the left edge of the size panel and stops there: the axis clipping a bar, not the bar
    ending. The formulation is bimodal across replicates, and a spread that wide *is* the reading
    for that row. It is the same row `Loaded_Champions` says this about, and it is the reason the
    objective panel's spreads are worth drawing at all.
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
    SIZE_GOAL_NM,
    SPEC_SIZE_NM,
    SPEC_ZETA_ABS,
    TITLE_SIZE,
    go,
    np,
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
        # The one panel on a LOG axis, and the one that draws a goal rather than a barrier.
        #
        # On a linear 0-270 axis the whole live range of this slide -- 11 to 24 nm for nine of
        # the twelve rows -- is squashed into the first tenth of the box, and 10 nm sits four
        # pixels off the axis line. There is nowhere on that panel to say `smaller is better`,
        # because the difference between 11 nm and 24 nm is invisible on it. On a log axis
        # equal ratios are equal distances, so 11 against 24 against 212 reads as what it is.
        #
        # `grade` replaces `pass_range` here: the band deepens from the barrier at 100 nm down
        # to the goal at 10 and stays at its deepest below it. See SIZE_GOAL_NM.
        dict(key='Droplet_Size', title='Droplet size, nm', width=1.05, log=True,
             axis_range=(8, 260), ticks=(10, 30, 100),
             grade=dict(frm=SPEC_SIZE_NM, to=SIZE_GOAL_NM), lines=(SPEC_SIZE_NM,)),
        dict(key='PDI', title='PDI', width=0.92,
             axis_range=(0, 0.5), ticks=(0, 0.1, 0.3, 0.5),
             pass_range=(0, PDI_HINGE_C2), lines=(PDI_HINGE_C2,),
             soft_lines=(PDI_HINGE_C1,)),
        # `Loaded_Champions` writes this `Zeta potential, |&#950;| mV`; at six panels that
        # title is wider than its own box. Shortened rather than set smaller -- the house scale
        # is already departed from once on this slide, for the row labels.
        dict(key='Zeta_P', title='Zeta, |&#950;| mV', absolute=True, width=0.83,
             axis_range=(0, 12), ticks=(0, 5, 10),
             pass_range=(0, SPEC_ZETA_ABS), lines=(SPEC_ZETA_ABS,)),
        # Ticked at the two dead-zone edges and NOT at 100, as on `Loaded_Champions`: three
        # labels inside a sixth of the canvas collide at 18 pt, and 100 is the one of the three
        # that is not a barrier -- the target is the shaded band, which the band draws better.
        dict(key='Drug_Loading', title='Drug loading, %', width=0.98,
             axis_range=(88, 116), ticks=(95, 105),
             pass_range=(DL_TARGET - DL_DEAD_ZONE, DL_TARGET + DL_DEAD_ZONE),
             lines=(DL_TARGET - DL_DEAD_ZONE, DL_TARGET + DL_DEAD_ZONE)),
        dict(key='Permeability',
             title='Permeability, &#215;10<sup>&#8722;6</sup>', scale=1e-6, width=1.22,
             axis_range=(0, 36), ticks=(0, 10, 20, 30),
             pass_range=(PERM_KNEE / 1e-6, 36), lines=(PERM_KNEE / 1e-6,)),
    ]

    # How the size panel's graded band is drawn: `GRADE_STEPS` rects in equal log-space slices
    # between the goal and the barrier, alpha ramping from the flat `PASS_BAND` value at 100 nm
    # to `GRADE_ALPHA[1]` at 10, then one flat rect at that deepest tone below the goal.
    #
    # The lightest slice is exactly PASS_BAND, so the size panel's band starts where every other
    # panel's band sits and only then deepens: the grammar is the same one, with a direction
    # added. The steps are small enough (0.004 of alpha apiece) that the seams do not read.
    GRADE_STEPS = 24
    GRADE_ALPHA = (0.055, 0.15)

    def _grade_colour(t):
        """The band's fill at `t` in [0, 1], 0 at the barrier and 1 at the goal."""
        _a = GRADE_ALPHA[0] + (GRADE_ALPHA[1] - GRADE_ALPHA[0]) * t
        return 'rgba(0, 0, 0, {:.4f})'.format(_a)

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
    assert not (set(PANELS[0]) & {'pass_range', 'lines', 'soft_lines', 'grade'}), \
        'the objective panel draws a barrier -- campaign2 has no pass mark'
    # Widths are shares of one row, so a panel without one would silently take a share of nothing.
    assert all(_p.get('width', 0) > 0 for _p in PANELS), \
        'every panel declares the share of the row it takes'

    # The goal is drawn on one panel only, it is read off that panel's ticks like every other
    # value on the slide, and it is inside the barrier it deepens towards.
    _graded = [_p for _p in PANELS if 'grade' in _p]
    assert [_p['key'] for _p in _graded] == ['Droplet_Size'], \
        'the graded band is the size panel only -- it is a goal, and size is where one is stated'
    for _panel in _graded:
        assert 'pass_range' not in _panel, \
            '{}: a graded band replaces the flat one, it does not sit under it'.format(
                _panel['key'])
        assert any(abs(_panel['grade']['to'] - _t) < 1e-9 for _t in _panel['ticks']), \
            '{}: the goal at {} is not an axis tick'.format(
                _panel['key'], _panel['grade']['to'])
        assert _panel['axis_range'][0] < _panel['grade']['to'] < _panel['grade']['frm'], \
            '{}: the goal is not inside the barrier it deepens towards'.format(_panel['key'])

    # No mark's mean is off its panel. An error bar may run off -- one does, and the prose above
    # says which -- but a clipped *mean* is a value the slide silently does not show.
    for _panel in PANELS:
        _scale = _panel.get('scale', 1.0)
        _v = RUNS[_panel['key']].abs() if _panel.get('absolute') else RUNS[_panel['key']]
        _v = _v / _scale
        assert _v.between(*_panel['axis_range']).all(), \
            '{}: {} is off the panel'.format(
                _panel['key'], sorted(RUNS.loc[~_v.between(*_panel['axis_range']), 'Exp']))


    # Only `range` is in log10 on a log axis. Marker data, `tickvals` and -- in this plotly --
    # shape coordinates are all in data units, so 100 nm is written as 100 everywhere but there.
    #
    # This is worth stating because the older plotly.js contract was the opposite: shapes were
    # positioned in log10 and everything else in data units. Under that contract every band and
    # every barrier on the size panel silently lands left of the axis minimum and simply does
    # not draw -- no error, no warning, just a panel with no specification on it. The assertion
    # below is what turns that back into a failure.
    SHAPES_IN_LOG_UNITS = False


    def _axis_units(panel, value):
        """`value` where a *shape* on `panel` wants it."""
        if panel.get('log') and SHAPES_IN_LOG_UNITS:
            return float(np.log10(value))
        return value


    # A shape must land inside its own axis, or it is drawn off-panel and reads as absent. The
    # size panel is the only one where the two conventions differ, so check it there.
    for _panel in PANELS:
        if not _panel.get('log'):
            continue
        _lo, _hi = _panel['axis_range']
        for _v in tuple(_panel['ticks']) + tuple(_panel.get('lines', ())):
            assert _lo <= _axis_units(_panel, _v) <= _hi, \
                ('{}: a shape at {} lands outside the axis -- plotly wants shape coordinates in '
                 'the other units on a log axis'.format(_panel['key'], _v))


    def build_slide(title, subtitle):
        """The one figure: six panel columns by two API boxes, drawn from the tables above."""
        panels = [dict(p) for p in PANELS]

        # --- two boxes, one per API ----------------------------------------------------------
        # Each API gets its own axis box rather than a section of one. A formulation's objective
        # depends on which API it was loaded with, so the two halves are two rankings that share
        # a scale, not one ranking with a rule across it -- and a closed box says that where a
        # hairline only implied it.
        #
        # Both boxes carry their own x ticks, so either can be read on its own. The axis titles
        # are under the bottom box only: the column is one scale and naming it twice would say
        # there are two.
        BOX_DOMAIN = {'A190': (0.565, 0.865), 'Feno': (0.140, 0.440)}
        CAPTION_LIFT = 0.010   # the section caption sits this far above its box

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
        for _panel in panels:
            _span = _unit * _panel['width']
            _panel['domain'] = [_x0, _x0 + _span]
            _x0 += _span + _gap

        # One axis pair per (box, panel). The suffix is plotly's: '' for the first, then '2', '3'
        # ... in one flat sequence, so a box is a stride through it rather than a second family.
        def _suffix(section_index, panel_index):
            _n = section_index * len(panels) + panel_index
            return '' if _n == 0 else str(_n + 1)

        # --- rows inside a box ---------------------------------------------------------------
        # Six unit bands per box, top first, so a row sits on the same pixel in either box and
        # the two rankings can be read against each other. The rules and the tick positions come
        # off the same numbers.
        ROWS = len(ROW_ORDER[SECTIONS[0]])
        assert all(len(ROW_ORDER[_a]) == ROWS for _a in SECTIONS), \
            'the two boxes hold different numbers of rows -- they would not line up'
        _y_of = {(_api, _label): ROWS - _i - 0.5
                 for _api in SECTIONS for _i, _label in enumerate(ROW_ORDER[_api])}
        _rule_ys = [float(_k) for _k in range(1, ROWS)]

        def _panel_traces(panel, api, suffix):
            """One marker trace per campaign for one panel of one box: one trace, one hue."""
            _scale = panel.get('scale', 1.0)
            _lo = panel['axis_range'][0]
            _out = []
            for _campaign in ('c2', 'c1'):
                _sub = RUNS[RUNS['campaign'].eq(_campaign) & RUNS['section'].eq(api)]
                _x, _y, _plus, _minus = [], [], [], []
                for _r in _sub.itertuples():
                    _v = getattr(_r, panel['key'])
                    if _v != _v:                     # NaN -- the measurement was never made
                        continue
                    _sd = getattr(_r, panel['key'] + '_sd')
                    _sd = 0.0 if _sd != _sd else _sd / _scale
                    _v = (abs(_v) if panel.get('absolute') else _v) / _scale
                    _x.append(_v)
                    _y.append(_y_of[(api, _r.label)])
                    _plus.append(_sd)
                    # A log axis cannot draw a whisker through zero, and one row's spread is
                    # wider than its own mean. Clamped to the axis minimum so the bar ends at
                    # the box edge -- which is what a clipped bar looks like on a linear panel
                    # too -- rather than being dropped without a mark.
                    _minus.append(min(_sd, _v - _lo) if panel.get('log') else _sd)
                _c = CAMPAIGN_COLOR[(_campaign, api)]
                _out.append(go.Scatter(
                    x=_x, y=_y, xaxis='x' + suffix, yaxis='y' + suffix,
                    mode='markers', hoverinfo='skip', showlegend=False,
                    error_x=dict(type='data', symmetric=False, array=_plus, arrayminus=_minus,
                                 color=_c, thickness=ERROR_WIDTH, width=5),
                    marker=dict(size=MARKER_SIZE, color=_c, symbol=SECTION_SYMBOL[api],
                                line=dict(width=MARKER_RING, color='white')),
                ))
            return _out

        def _panel_shapes(panel, suffix):
            """The bands, the graded band and the barrier lines for one panel of one box."""
            _xr, _yr = 'x' + suffix, 'y' + suffix
            _lo, _hi = panel['axis_range']
            _out = []

            def _rect(x0, x1, colour):
                return dict(type='rect', xref=_xr, yref=_yr,
                            x0=_axis_units(panel, x0), x1=_axis_units(panel, x1),
                            y0=0, y1=ROWS, fillcolor=colour,
                            line=dict(width=0), layer='below')

            if 'pass_range' in panel:
                _out.append(_rect(panel['pass_range'][0], panel['pass_range'][1], PASS_BAND))
            if 'grade' in panel:
                # Deepest below the goal, then one slice per equal step of log space up to the
                # barrier. Drawn goal-first so the flat part is under the ramp's lightest end.
                _goal, _frm = panel['grade']['to'], panel['grade']['frm']
                _out.append(_rect(_lo, _goal, _grade_colour(1.0)))
                _edges = np.geomspace(_goal, _frm, GRADE_STEPS + 1)
                for _i in range(GRADE_STEPS):
                    _out.append(_rect(_edges[_i], _edges[_i + 1],
                                      _grade_colour(1.0 - _i / (GRADE_STEPS - 1.0))))
            for _line in panel.get('soft_lines', ()):
                _out.append(dict(
                    type='line', xref=_xr, yref=_yr,
                    x0=_axis_units(panel, _line), x1=_axis_units(panel, _line), y0=0, y1=ROWS,
                    line=dict(color=INK_SOFT, width=1.6, dash='dot')))
            for _line in panel.get('lines', ()):
                _out.append(dict(
                    type='line', xref=_xr, yref=_yr,
                    x0=_axis_units(panel, _line), x1=_axis_units(panel, _line), y0=0, y1=ROWS,
                    line=dict(color=INK, width=1.8, dash='dash')))
            # --- row rules ---------------------------------------------------------------
            # Drawn ONE SEGMENT PER PANEL, against that panel's own axes, rather than as a
            # single paper-width line: a paper-width rule runs on through the gaps between the
            # panels and through the label gutter, which turns the white space that separates
            # the boxes into ruled space.
            for _rule_y in _rule_ys:
                _out.append(dict(
                    type='line', xref=_xr, yref=_yr,
                    x0=_axis_units(panel, _lo), x1=_axis_units(panel, _hi),
                    y0=_rule_y, y1=_rule_y,
                    line=dict(color=ROW_RULE, width=1.0), layer='below'))
            return _out

        _traces, _shapes = [], []
        for _si, _api in enumerate(SECTIONS):
            for _pi, _panel in enumerate(panels):
                _s = _suffix(_si, _pi)
                _traces += _panel_traces(_panel, _api, _s)
                _shapes += _panel_shapes(_panel, _s)

        # --- legend proxies -----------------------------------------------------------------
        # Three series, then the specification vocabulary: the size goal's tone, then the two
        # barrier strokes. The lines are in the legend rather than annotated on a panel because
        # both appear on more than one panel between them, and a caption beside one line would
        # read as belonging to that panel alone.
        for _name, _colour, _symbol in LEGEND_ENTRIES:
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='markers', name=_name,
                marker=dict(size=MARKER_SIZE, color=_colour, symbol=_symbol,
                            line=dict(width=1.4, color=INK))))
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Size goal, 10 nm',
            # Set a shade deeper than the band's own deepest tone and given an outline: at
            # legend size a 0.15 alpha square on white is a blank, and a legend key that cannot
            # be seen is not a key. It still reads as the dark end of that band and nothing
            # else on the figure wears it.
            marker=dict(size=MARKER_SIZE, symbol='square', color='rgba(0, 0, 0, 0.20)',
                        line=dict(width=1.0, color=INK_SOFT))))
        for _name, _dash in (("Campaign 2&#8217;s target", 'dash'),
                             ('Campaign 1 target', 'dot')):
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='lines', name=_name,
                line=dict(color=INK, width=1.8, dash=_dash)))

        _annotations = [
            dict(xref='paper', yref='paper', x=0.5, y=1.0, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK), name='heading',
                 text='<b>{}</b>'.format(title)),
            dict(xref='paper', yref='paper', x=0.5, y=0.955, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text=subtitle),
        ]
        # One caption per box, left-aligned over the row-label gutter rather than centred over
        # the panels: it names the rows, and a caption centred over six boxes would read as a
        # title for the panel it happened to land on.
        for _api in SECTIONS:
            _annotations.append(dict(
                xref='paper', yref='paper', x=0.0, xanchor='left',
                y=BOX_DOMAIN[_api][1] + CAPTION_LIFT, yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE, color=INK), name='heading',
                text='<b>{}</b>'.format(SECTION_TITLE[_api])))

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=dict(l=10, r=10, t=104, b=LEGEND_MARGIN),
            shapes=_shapes, annotations=_annotations,
            legend=dict(orientation='h', xanchor='center', x=0.5, yanchor='top', y=-0.02,
                        font=dict(size=LEGEND_SIZE), itemsizing='constant',
                        bgcolor='rgba(0,0,0,0)'),
        )
        _bottom = SECTIONS[-1]
        for _si, _api in enumerate(SECTIONS):
            for _pi, _panel in enumerate(panels):
                _s = _suffix(_si, _pi)
                # `range` is the one field that IS log10 on a log axis. See SHAPES_IN_LOG_UNITS.
                _range = ([float(np.log10(_v)) for _v in _panel['axis_range']]
                          if _panel.get('log') else list(_panel['axis_range']))
                _title = _panel['title'] if _api == _bottom else ''
                _layout['xaxis' + _s] = dict(
                    AXIS_COMMON, domain=_panel['domain'], anchor='y' + _s,
                    type='log' if _panel.get('log') else 'linear',
                    title=dict(text=_title, font=dict(size=AXIS_TITLE_SIZE)),
                    range=_range, tickmode='array', tickvals=list(_panel['ticks']))
                # Only the leftmost panel of each box carries the row labels; the rest share its
                # scale with blank ticks, so a box reads as one table rather than six charts.
                _labels = ROW_ORDER[_api] if _pi == 0 else ['' for _ in ROW_ORDER[_api]]
                _layout['yaxis' + _s] = dict(
                    AXIS_COMMON, domain=list(BOX_DOMAIN[_api]), anchor='x' + _s,
                    range=[0, ROWS], tickmode='array',
                    tickvals=[_y_of[(_api, _l)] for _l in ROW_ORDER[_api]],
                    ticktext=list(_labels), tickfont=dict(size=ROW_LABEL_SIZE), ticks='')
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
