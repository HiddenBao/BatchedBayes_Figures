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
    # Design Space Figure Suite

    **Two figures, one argument.** Act 1's opening pair:

    | export | slide | what it says |
    | --- | --- | --- |
    | `Design_Space_DoE.svg` | one | what the Box-Behnken design produced, against the Table 2 targets |
    | `Design_Space_Expansion.svg` | two | that design as one system of a hundred, and its three settings as ranges |

    **Neither figure draws the cube.** The design's geometry is drawn by hand in the deck; what
    the suite keeps of it is `DOE_CODED`, the coded position it asserts every run against. Slide
    one is the measurements and nothing else; slide two is the space and nothing else.

    They stay one suite because both rest on the same asserted design: the same coded positions,
    the same Table 1 ranges, the same five rows. Splitting them would duplicate that spec.

    ## What the design actually was

    A three-factor **Box-Behnken design** is a cube sampled at its twelve *edge midpoints* plus its
    centre — no corner, no interior point, nothing off the box. The paper's introduction names the
    design (Pangeni et al. 2025) and its three dials: oil volume, surfactant-to-cosurfactant ratio,
    and sonication time, with the excipients — Oleic acid, Tween 80, PEG 400 — fixed before any
    experiment ran.

    The four runs `data/` holds confirm the geometry rather than being assumed into it. In coded
    levels, with the centre at 15 % oil / 1:1 Smix / 1.5 min:

    | run | oil | Smix | sonication | position |
    | --- | --- | --- | --- | --- |
    | `DoE1` | − | + | 0 | edge midpoint |
    | `DoE4` | − | − | 0 | edge midpoint |
    | `DoE10` | 0 | − | − | edge midpoint |
    | `DoE11` | 0 | − | + | edge midpoint |
    | `DoEOPT` | − | 0 | 0 | **face centre — not a design run** |

    Smix runs **3:1 → 1:1 → 1:3**, low coded level to high, as Table 1 writes the range. Coded
    `−` is the surfactant-heavy end. The sign is a labelling convention, not a measurement, so
    the data cell resolves it against each row's actual `Surfactant_V` / `Cosurfactant_V`
    rather than trusting the table above.

    All four have exactly one coded zero, which is the defining property of a Box-Behnken point.
    `DoEOPT` has two, so it is a face centre, which this design never samples: it is the response
    surface's *predicted* optimum, made and confirmed after the design closed. The suite asserts
    all five positions against the CSV, so the geometry fails loudly if the data moves under it.

    ### Why four runs and not thirteen

    `data/` carries 4 of the 12 edge points, and the reason is experimental, not clerical. **The
    rest of the box phase-separated, and the ones that did not were made before a standardised
    protocol.** So the four here are the design's comparable survivors — the only runs that can be
    put on one axis against the Table 2 targets at all.

    That is a finding about the design, not a gap in it, and slide one's footnote says so. Scoring
    the excluded runs against a droplet-size target would be scoring a formulation that had
    separated into layers.

    ## Scoring, and why there is none

    Neither figure scores anything. Slide one plots **raw droplet size and PDI** against the
    paper's Table 2 targets, because the point being made is about the design and its measurements,
    not about a ranking. `Campaign1_Progress` is where the objective belongs, and it already draws
    these same rows on it.

    Targets come from Table 2 (`SPEC_SIZE_NM`, `SPEC_PDI`) and the design space from Table 1, both
    named here once and used everywhere below.

    ## Environment

    A [marimo](https://marimo.io) notebook, so it is a plain Python module and the interpreter that
    launches it *is* the kernel. Run it from the **`BatchedBayes`** conda environment:

    ```
    conda run -n BatchedBayes marimo edit Figures/Design_Space/Design_Space_Figures.py
    conda run -n BatchedBayes python Figures/Design_Space/Design_Space_Figures.py
    ```
    """)
    return


@app.cell
def _():
    import importlib.util
    import sys
    from pathlib import Path

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
    return Path, go, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Paths, canvas and export

    `REPO_ROOT` is found by looking for `Figures/objectives.py` above this file rather than by
    counting `..`, so the suite survives being moved and fails loudly rather than silently reading
    the wrong tree. The canvas is the house 1280 × 720.
    """)
    return


@app.cell
def _(Path):
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Design_Space' / 'Output'
    DATA_CSV = REPO_ROOT / 'data' / 'MicroemulsionFormulation_Comprehensive.csv'

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
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shared chrome

    House style — the `Breaking-the-Boundaries` suites', value for value: white ground, a 2 px
    black mirrored axis box, no gridlines, five type sizes (20 / 18 / 18 / 14 / 14), a centred
    title, a horizontal legend in a bottom gutter.

    Three hues, and two of them already mean this elsewhere in the deck:

    | token | hex | what it means | where else |
    | --- | --- | --- | --- |
    | `DOE_COLOR` | `#E69F00` | the Box-Behnken design and its runs | `Campaign1_Progress` |
    | `BEST_COLOR` | `#D55E00` | `DoEOPT`, the mark to beat | both leaderboards, `Campaign1_Progress` |
    | `SPACE_COLOR` | `#2067F4` | Campaign 1's reachable design space | the blue *family* is Campaign 1 |

    `SPACE_COLOR` needs a word. Elsewhere in the deck `#2067F4` is a specific step — batch C on the
    blue ramp, and the revalidated champions on the Campaign 2 board. **There are no batches on
    these two slides**: nothing here is a campaign result, so the ramp is not in play and the blue
    is carrying the one meaning the README gives the family as a whole — *Campaign 1*. The two
    readings never appear together, which is the same licence `#2067F4` already runs under on the
    Campaign 2 board.

    The Table 2 targets are drawn in **ink, dashed** rather than in a hue of their own. A
    specification is not a series; giving it a colour would put it in competition with the two
    campaigns for the reader's category sense.

    ### Pixel-grid panels

    The 5 × 20 field and the dial strip are schematics, so they sit on `pixel_axes()`: hidden
    axes whose range spans exactly as many data units as the domain spans exported pixels, origin
    top left. One data unit is one pixel, so a 6 px marker is 6 px on the slide and a cell asked
    to be square is square whatever domain it is given.
    """)
    return


@app.cell
def _(FIG_HEIGHT, FIG_WIDTH, go):
    DOE_COLOR = '#E69F00'      # orange  -- the Box-Behnken design and its runs
    BEST_COLOR = '#D55E00'     # red     -- DoEOPT, the mark to beat
    SPACE_COLOR = '#2067F4'    # blue    -- Campaign 1's reachable space; the family, not a batch

    INK = 'black'
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    RULE = 'rgba(0, 0, 0, 0.22)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    # --- The deck's own faces ------------------------------------------------------------
    # An SVG *references* a font, it does not embed one, so these render as themselves only
    # where both faces are installed and fall back to the house stack everywhere else. That is
    # why each figure is exported twice rather than switched over: the plain export stays the
    # portable one. Family names are exactly as Windows reports them -- 'Gmarket' has a
    # lowercase m, and the face is the Medium weight, so it is named, not asked for via
    # font-weight.
    BODY_FAMILY = 'Pretendard, ' + FONT_FAMILY
    HEADING_FAMILY = 'Gmarket Sans TTF Medium, Pretendard, ' + FONT_FAMILY

    # suffix -> (body face, heading face). '' is the default export, and it must stay first:
    # it is the one that survives being opened on a machine without the two faces.
    FONT_SCHEMES = {
        '': (FONT_FAMILY, FONT_FAMILY),
        '_Pretendard': (BODY_FAMILY, HEADING_FAMILY),
    }

    # Sizes do NOT change between schemes. The house 20/18/18/14/14 is the same in both, so the
    # two exports are drop-in swaps for each other and a slide can be re-fonted without
    # re-checking that anything still fits.

    MARKER_SIZE = 13
    MARKER_RING = 2
    ERROR_WIDTH = 1.4
    FRAME_WIDTH = 2
    # The 5 x 20 field's cell edge. Full SPACE_COLOR rather than a faded one: the grid *is* the
    # reachable space, so its outline is the deck primary at full strength, and heavy enough to
    # hold the shape when the slide is projected.
    CELL_EDGE = 2.4

    LEGEND_MARGIN = 96   # bottom gutter the horizontal legend sits in

    # Paper Table 2, response targets for formulation optimisation.
    SPEC_SIZE_NM = 100.0
    SPEC_PDI = 0.3
    # NOT from Table 2. The paper sets no zeta target; this is the |zeta| = 10 mV boundary the
    # deck asked for, so a reader can see every run sits inside it. Kept apart from the two above
    # and named for what it is, so it is never mistaken for a published specification.
    SPEC_ZETA_ABS = 10.0

    # Paper Table 1, the Campaign 1 design space. Imported meaning: stated here once, and used
    # for every tick label and every category list below -- never retyped inside a figure.
    OIL_V_RANGE = (7.5, 22.5)
    SONICATION_RANGE = (0.0, 3.0)
    # Low to high as the paper's Table 1 writes the range, '3:1--1:3': the low end of the dial
    # is surfactant-heavy. Coded -1 is therefore 30 parts surfactant to 10 cosurfactant.
    SMIX_RATIO_LABELS = ('3:1', '1:1', '1:3')
    OILS = ['Oleic Acid', 'Capryol 90', 'Soybean Oil', 'Maisine Oil', 'Capmul MCM']
    SURFACTANTS = ['PEG 400', 'Tween 80', 'Tween 20', 'Labrasol']
    COSURFACTANTS = ['Tween 80', 'Transcutol HP', 'Propylene Glycol', 'Ethanol', 'PEG 400']

    # Display-only column heads for the 5 x 20 field: twenty columns leave about 56 px each, and
    # 'Propylene Glycol' set diagonally still overruns its neighbours at that pitch. The figure
    # asserts these keys against COSURFACTANTS, so a rename upstream fails loudly instead of
    # quietly mislabelling a column.
    COSURF_SHORT = {
        'Tween 80': 'Tween 80',
        'Transcutol HP': 'Transcutol',
        'Propylene Glycol': 'Prop. glycol',
        'Ethanol': 'Ethanol',
        'PEG 400': 'PEG 400',
    }

    # The DoE's one system, as it appears in `data/`.
    DOE_SYSTEM = ('Oleic Acid', 'Tween 80', 'PEG 400')

    # The CSV's `DoE1` / `DoEOPT` are ids; the deck spells the rows DoE-1 and DoE-OPT, hyphenated,
    # as Campaign1_Progress and both leaderboards already spell DoE-OPT.
    def row_label(exp):
        """'DoE1' -> 'DoE-1', 'DoEOPT' -> 'DoE-OPT'. Anything else is passed through."""
        return 'DoE-' + exp[3:] if exp.startswith('DoE') and len(exp) > 3 else exp


    def fade(hex_color, alpha):
        """Convert '#RRGGBB' to an rgba() string at the given alpha."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return 'rgba({}, {}, {}, {})'.format(r, g, b, alpha)


    def with_font_scheme(fig, body, heading):
        """A copy of `fig` re-fonted: `heading` on titles and axes, `body` on everything else.

        Applied after a figure is built rather than threaded through the builders, so the two
        exports cannot drift: there is one figure, drawn once, wearing two type schemes. Heading
        text is tagged where it is written with `name='heading'`; everything else is body by
        definition, which is the safe default -- a new annotation joins the reading face rather
        than silently claiming to be a title.
        """
        out = go.Figure(fig.to_dict())
        out.layout.font.family = body
        out.layout.legend.font.family = body
        for _ann in out.layout.annotations:
            _ann.font.family = heading if _ann.name == 'heading' else body
        for _axis in list(out.select_xaxes()) + list(out.select_yaxes()):
            _axis.tickfont.family = heading
            _axis.title.font.family = heading
        return out


    # An axis domain is a fraction of the *plot area*, not of the canvas, so pixel_axes() is
    # only truthful if it knows the margins. Slide two's layout and its pixel axes read this one
    # dict, so the two cannot disagree -- and a cell asked to be square really is square.
    SCHEMATIC_MARGIN = dict(l=10, r=10, t=96, b=LEGEND_MARGIN)


    def pixel_axes(x_domain, y_domain, margin=SCHEMATIC_MARGIN):
        """Axis pair whose data units are exported pixels, origin top left.

        The range spans exactly as many units as the domain spans pixels of the plot area --
        the 1280 x 720 canvas less `margin` -- so a schematic drawn in these coordinates keeps
        its proportions and its stroke weights whatever domain it is given.
        """
        plot_w = FIG_WIDTH - margin['l'] - margin['r']
        plot_h = FIG_HEIGHT - margin['t'] - margin['b']
        width = (x_domain[1] - x_domain[0]) * plot_w
        height = (y_domain[1] - y_domain[0]) * plot_h
        x_axis = dict(domain=list(x_domain), range=[0, width], visible=False,
                      fixedrange=True)
        y_axis = dict(domain=list(y_domain), range=[height, 0], visible=False,
                      fixedrange=True)
        return x_axis, y_axis, width, height


    AXIS_COMMON = dict(
        showline=True, linecolor=INK, linewidth=FRAME_WIDTH, mirror=True,
        tickcolor=INK, color=INK, ticks='outside',
        showgrid=False, zeroline=False,
        tickfont=dict(size=TICK_SIZE), title_font=dict(size=AXIS_TITLE_SIZE),
    )
    return (
        ANNOTATION_SIZE,
        AXIS_COMMON,
        AXIS_TITLE_SIZE,
        BEST_COLOR,
        CELL_EDGE,
        COSURFACTANTS,
        COSURF_SHORT,
        DOE_COLOR,
        DOE_SYSTEM,
        ERROR_WIDTH,
        FONT_FAMILY,
        FONT_SCHEMES,
        INK,
        INK_SOFT,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        MARKER_RING,
        MARKER_SIZE,
        OILS,
        OIL_V_RANGE,
        RULE,
        SCHEMATIC_MARGIN,
        SMIX_RATIO_LABELS,
        SONICATION_RANGE,
        SPACE_COLOR,
        SPEC_PDI,
        SPEC_SIZE_NM,
        SPEC_ZETA_ABS,
        SURFACTANTS,
        TITLE_SIZE,
        fade,
        pixel_axes,
        row_label,
        with_font_scheme,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The data

    Five rows: the four Box-Behnken runs `data/` holds and `DoEOPT`. Each is the mean of its three
    replicates with their standard deviation, measured — not scored.

    `DOE_RUNS` carries each row's **coded position**, and the cell asserts every one of them against
    the CSV's own volumes: a coded `−` on oil must be 7.5 %, a coded `0` on Smix must be 20 / 20,
    and so on. It also asserts that the four design runs each have exactly one coded zero and that
    `DoEOPT` has two, which is the difference between an edge midpoint and a face centre and the
    only reason the notebook is entitled to call this a Box-Behnken design at all.
    """)
    return


@app.cell
def _(DATA_CSV, OIL_V_RANGE, SONICATION_RANGE, pd):
    # Coded levels: -1 / 0 / +1 on (oil volume, Smix ratio, sonication), centred on the design's
    # own centre point. Positions are asserted against the CSV below, never assumed.
    DOE_CODED = {
        'DoE1':   (-1, 1, 0),
        'DoE4':   (-1, -1, 0),
        'DoE10':  (0, -1, -1),
        'DoE11':  (0, -1, 1),
        'DoEOPT': (-1, 0, 0),   # a face centre: two zeros, so not a Box-Behnken run
    }
    DOE_DESIGN_RUNS = ['DoE1', 'DoE4', 'DoE10', 'DoE11']
    DOE_OPT_ID = 'DoEOPT'

    # Coded level -> real setting, from the design space of the paper's Table 1.
    _OIL_LEVEL = {-1: OIL_V_RANGE[0], 0: sum(OIL_V_RANGE) / 2, 1: OIL_V_RANGE[1]}
    _SMIX_LEVEL = {-1: (30.0, 10.0), 0: (20.0, 20.0), 1: (10.0, 30.0)}
    _SONIC_LEVEL = {-1: SONICATION_RANGE[0],
                    0: sum(SONICATION_RANGE) / 2,
                    1: SONICATION_RANGE[1]}

    _raw = pd.read_csv(DATA_CSV)
    _rows = _raw[_raw['Exp'].isin(DOE_CODED)].copy()

    DOE_RUNS = _rows.groupby('Exp', sort=False).agg(
        oil_v=('Oil_V', 'first'),
        surf_v=('Surfactant_V', 'first'),
        cosurf_v=('Cosurfactant_V', 'first'),
        sonication=('Sonication', 'first'),
        oil=('Oil', 'first'),
        surfactant=('Surfactant', 'first'),
        cosurfactant=('Cosurfactant', 'first'),
        size_nm=('Droplet_Size', 'mean'),
        size_sd=('Droplet_Size', 'std'),
        pdi=('PDI', 'mean'),
        pdi_sd=('PDI', 'std'),
        zeta=('Zeta_P', 'mean'),
        zeta_sd=('Zeta_P', 'std'),
        loading=('Drug_Loading', 'mean'),
        loading_sd=('Drug_Loading', 'std'),
        perm=('Permeability', 'mean'),
        perm_sd=('Permeability', 'std'),
        sep=('Phase_Sep', 'max'),
        reps=('Droplet_Size', 'size'),
    ).reset_index()

    assert set(DOE_RUNS['Exp']) == set(DOE_CODED), \
        'data/ is missing one of {}'.format(sorted(DOE_CODED))

    # The coded positions are a claim about the design. Check every one against the file.
    for _r in DOE_RUNS.itertuples():
        _oil_c, _smix_c, _son_c = DOE_CODED[_r.Exp]
        assert _r.oil_v == _OIL_LEVEL[_oil_c], \
            '{}: oil {} is not coded level {}'.format(_r.Exp, _r.oil_v, _oil_c)
        assert (_r.surf_v, _r.cosurf_v) == _SMIX_LEVEL[_smix_c], \
            '{}: Smix {}/{} is not coded level {}'.format(
                _r.Exp, _r.surf_v, _r.cosurf_v, _smix_c)
        assert _r.sonication == _SONIC_LEVEL[_son_c], \
            '{}: sonication {} is not coded level {}'.format(_r.Exp, _r.sonication, _son_c)
        assert _r.reps == 3, '{}: expected 3 replicates, found {}'.format(_r.Exp, _r.reps)
        assert _r.sep == 0, '{}: phase separated -- the DoE campaign reported none'.format(_r.Exp)

    # A Box-Behnken point has exactly one coded zero. A face centre has two.
    for _exp in DOE_DESIGN_RUNS:
        assert sum(1 for _v in DOE_CODED[_exp] if _v == 0) == 1, \
            '{} is not an edge midpoint'.format(_exp)
    assert sum(1 for _v in DOE_CODED[DOE_OPT_ID] if _v == 0) == 2, \
        '{} is not a face centre'.format(DOE_OPT_ID)

    # Drug loading and permeability exist for DoEOPT and nothing else: the four design runs were
    # never loaded with an API, because loading came after the design closed. The two panels that
    # plot them are therefore one marker and four blank rows, and that is the measurement record,
    # not a read error. Assert it, so a later file that *does* carry them fails here instead of
    # quietly filling panels the slide's caption says are empty.
    _loaded = set(DOE_RUNS.loc[DOE_RUNS['loading'].notna(), 'Exp'])
    assert _loaded == {DOE_OPT_ID}, \
        'drug loading is measured for {}, expected {} alone'.format(sorted(_loaded), DOE_OPT_ID)
    assert set(DOE_RUNS.loc[DOE_RUNS['perm'].notna(), 'Exp']) == {DOE_OPT_ID}

    # The zeta panel plots |zeta| against a boundary on the magnitude, which is only a sign
    # flip while every reading is negative. If a positive one ever lands here, abs() would fold
    # it onto the wrong side of that boundary, so fail instead.
    assert (DOE_RUNS['zeta'] < 0).all(), \
        'zeta is positive for {} -- the |zeta| panel would fold it'.format(
            sorted(DOE_RUNS.loc[DOE_RUNS['zeta'] >= 0, 'Exp']))

    # One fixed system, chosen before the campaign ran -- that is the slide's whole left half.
    assert DOE_RUNS['oil'].nunique() == 1
    assert DOE_RUNS['surfactant'].nunique() == 1
    assert DOE_RUNS['cosurfactant'].nunique() == 1

    DOE_RUNS = DOE_RUNS.set_index('Exp').loc[DOE_DESIGN_RUNS + [DOE_OPT_ID]].reset_index()

    print(DOE_RUNS[['Exp', 'oil_v', 'surf_v', 'cosurf_v', 'sonication',
                    'size_nm', 'size_sd', 'pdi']].to_string(index=False))
    return DOE_CODED, DOE_OPT_ID, DOE_RUNS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Slide one — the design of experiments

    **Three panels across the house width**, one per measured output the design runs actually
    carry, sharing a row order and a single row-label gutter so they read as one table rather than
    three charts. `DOE_PANELS` is the whole layout: a panel is a row in that list, and adding or
    dropping an output is an edit to it.

    | panel | axis | boundary | shaded band |
    | --- | --- | --- | --- |
    | droplet size, nm | 0 – 540 | Table 2, 100 nm | empty |
    | PDI | 0 – 0.9 | Table 2, 0.3 | empty |
    | \|ζ\| , mV | 0 – 12 | 10 mV, **not** from Table 2 | holds every run |

    Each panel is named by its **x-axis title**, at the house axis-title size, rather than by a
    header floating above the box — the label sits with the scale it describes.

    Each boundary is a dashed ink vertical, and every panel shades the side that satisfies it. On
    size and PDI that band is **empty** — nothing reached either target, which is the slide's
    whole reading. On zeta it holds all five, because every run sits inside |ζ| < 10.

    **No boundary is labelled.** Its value is an axis tick instead, so a reader takes it off the
    same scale as the data rather than from a caption floating beside the line. That is why each
    panel names its ticks explicitly and every list contains `spec`.

    Zeta plots the **magnitude**. It is measured negative throughout and the deck's boundary is on
    |ζ|, so the panel runs 0 → 12 rather than −12 → 0; the data cell asserts the sign, so that is
    a flip and never a fold. The paper specifies no zeta target at all, so `SPEC_ZETA_ABS` is
    named apart from the two Table 2 constants and commented as the deck's own — it must never be
    read back as published.

    ### No drug loading or permeability panel

    `data/` measures both for `DoEOPT` and nothing else — the four Box-Behnken runs were never
    loaded with an API, because loading came after the design closed. A panel for either would be
    one marker and four blank rows, so neither is drawn. The data cell still asserts the gap, so a
    later file that does carry them fails there rather than quietly filling a panel.

    **There is no cube panel here.** The deck draws the design's geometry by hand, so the canvas
    is the full `FIG_WIDTH` and the cube sits above or below these panels on the slide itself.

    Rows run `DoE1` · `DoE4` · `DoE10` · `DoE11` · `DoEOPT` — file order, with `DoEOPT` last and set
    off by a rule, exactly the way `Campaign1_Progress` separates it as its own section.

    Both targets are drawn as **dashed ink verticals with a shaded miss-side**. Nothing crosses
    either: the campaign's best droplet size is 184.6 nm against a target of 100, and its best PDI
    0.325 against 0.3. That is the slide.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
    AXIS_TITLE_SIZE,
    BEST_COLOR,
    DOE_COLOR,
    DOE_OPT_ID,
    DOE_RUNS,
    DOE_SYSTEM,
    ERROR_WIDTH,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    MARKER_RING,
    MARKER_SIZE,
    RULE,
    SPEC_PDI,
    SPEC_SIZE_NM,
    SPEC_ZETA_ABS,
    TITLE_SIZE,
    go,
    row_label,
):
    # One entry per panel, left to right.
    #
    # Drug loading and permeability are not here. data/ measures both for DoEOPT alone -- the four
    # Box-Behnken runs carried no API, because loading came after the design closed -- so a panel
    # for either is one marker and four blank rows. The data cell still asserts that, so a later
    # file that does carry them fails loudly instead of quietly filling a panel.
    #
    # `spec` is the boundary the panel draws, and every panel shades the side that satisfies it.
    # On size and PDI that shaded band is *empty* -- nothing reached either target, which is the
    # slide's whole reading. On zeta it is full, because every run sits inside |zeta| < 10.
    #
    # No panel labels its boundary. The boundary value is an axis tick instead, so it is read off
    # the same scale as the data rather than from a caption floating beside the line -- which is
    # why `ticks` is an explicit list per panel and always contains `spec`.
    #
    # `absolute` plots |value|. Zeta is measured negative throughout, and the boundary the deck
    # wants is on the magnitude, so the panel runs 0 -> 12 on |zeta| rather than -12 -> 0. The
    # data cell asserts the sign, so this is a flip and never a fold.
    DOE_PANELS = [
        dict(key='size_nm', err='size_sd', title='<b>Droplet size</b>, nm', absolute=False,
             axis_range=(0, 540), ticks=(0, 100, 300, 500), spec=SPEC_SIZE_NM),
        dict(key='pdi', err='pdi_sd', title='<b>PDI</b>', absolute=False,
             axis_range=(0, 0.9), ticks=(0, 0.3, 0.6, 0.9), spec=SPEC_PDI),
        dict(key='zeta', err='zeta_sd', title='<b>Zeta potential</b>, |&#950;| mV',
             absolute=True,
             axis_range=(0, 12), ticks=(0, 5, 10), spec=SPEC_ZETA_ABS),
    ]


    def build_doe_slide():
        _rows = DOE_RUNS
        _y = list(range(len(_rows), 0, -1))          # first row at the top
        _labels = [row_label(e) for e in _rows['Exp']]
        _is_opt = [e == DOE_OPT_ID for e in _rows['Exp']]

        # The panels run across the house width, sharing one row-label gutter. The gutter is a
        # fixed ~100 px -- 'DoE-OPT' at 18 pt -- and the panels split what is left evenly.
        #
        # The gap has to clear two tick labels, not one: every panel's last tick sits on its own
        # right edge and its neighbour's first tick on the left edge, so a gap sized for one
        # label runs them together. 0.034 is 44 px, which clears the widest such pair these
        # ranges produce.
        _gutter, _right, _gap = 0.078, 0.988, 0.034
        _span = (_right - _gutter - _gap * (len(DOE_PANELS) - 1)) / len(DOE_PANELS)
        for _i, _panel in enumerate(DOE_PANELS):
            _x0 = _gutter + _i * (_span + _gap)
            _panel['domain'] = [_x0, _x0 + _span]
            _panel['suffix'] = '' if _i == 0 else str(_i + 1)

        # No headers above the boxes any more -- each panel is named by its x-axis title -- so
        # the panels take the space back at the top. The bottom leaves room for a tick row and a
        # title beneath it, inside the legend's own gutter.
        _panel_top, _panel_bottom = 0.865, 0.175

        def _panel_traces(panel):
            """Marker traces for one panel, split so DoE-OPT keeps its own colour and symbol."""
            _values = [abs(v) if panel['absolute'] else v for v in _rows[panel['key']]]
            _errors = [0.0 if _e != _e else _e for _e in _rows[panel['err']]]
            _t = []
            for _opt in (False, True):
                _idx = [i for i, o in enumerate(_is_opt) if o == _opt]
                if not _idx:
                    continue
                _t.append(go.Scatter(
                    x=[_values[i] for i in _idx], y=[_y[i] for i in _idx],
                    xaxis='x' + panel['suffix'], yaxis='y' + panel['suffix'],
                    mode='markers', hoverinfo='skip', showlegend=False,
                    error_x=dict(type='data', array=[_errors[i] for i in _idx],
                                 color=BEST_COLOR if _opt else DOE_COLOR,
                                 thickness=ERROR_WIDTH, width=6),
                    marker=dict(
                        size=MARKER_SIZE + (4 if _opt else 0),
                        color=BEST_COLOR if _opt else DOE_COLOR,
                        symbol='diamond' if _opt else 'circle',
                        line=dict(width=MARKER_RING, color='white')),
                ))
            return _t

        _traces = []
        for _panel in DOE_PANELS:
            _traces += _panel_traces(_panel)

        for _name, _colour, _symbol in (
            ('Box-Behnken run', DOE_COLOR, 'circle'),
            ('DoE-OPT  ·  the optimum the design pointed at', BEST_COLOR, 'diamond'),
        ):
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='markers', name=_name,
                marker=dict(size=MARKER_SIZE, color=_colour, symbol=_symbol,
                            line=dict(width=1.4, color=INK))))

        # The Table 2 target zone is shaded on the *pass* side. Nothing reached either target, so
        # the shaded band is the empty stretch of each panel -- which is the whole reading.
        _shapes = []
        for _panel in DOE_PANELS:
            if _panel['spec'] is None:
                continue
            _ref = 'x' + _panel['suffix']
            _shapes.append(dict(
                type='rect', xref=_ref, yref='paper', x0=_panel['axis_range'][0],
                x1=_panel['spec'], y0=_panel_bottom, y1=_panel_top,
                fillcolor='rgba(0, 0, 0, 0.055)', line=dict(width=0), layer='below'))
            _shapes.append(dict(
                type='line', xref=_ref, yref='paper', x0=_panel['spec'], x1=_panel['spec'],
                y0=_panel_bottom, y1=_panel_top,
                line=dict(color=INK, width=1.8, dash='dash')))
        # DoE-OPT sits below a rule, as its own section -- as on Campaign1_Progress.
        _shapes.append(dict(
            type='line', xref='paper', yref='y', x0=_gutter, x1=_right, y0=1.5, y1=1.5,
            line=dict(color=RULE, width=1.2, dash='dot')))

        _annotations = [
            dict(xref='paper', yref='paper', x=0.5, y=1.0, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK), name='heading',
                 text='<b>The design of experiments, and what it produced</b>'),
            dict(xref='paper', yref='paper', x=0.5, y=0.955, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text='{} &#8212; one system, fixed before the first experiment'.format(
                     '&#8195;·&#8195;'.join(DOE_SYSTEM))),
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
        # ticks, so the panels read as one table rather than as separate charts.
        for _i, _panel in enumerate(DOE_PANELS):
            _s = _panel['suffix']
            _layout['xaxis' + _s] = dict(
                AXIS_COMMON, domain=_panel['domain'], anchor='y' + _s,
                title=dict(text=_panel['title'], font=dict(size=AXIS_TITLE_SIZE)),
                range=list(_panel['axis_range']),
                tickmode='array', tickvals=list(_panel['ticks']))
            _layout['yaxis' + _s] = dict(
                AXIS_COMMON, domain=[_panel_bottom, _panel_top], anchor='x' + _s,
                range=[0.4, len(_rows) + 0.6], tickmode='array', tickvals=_y,
                ticktext=_labels if _i == 0 else ['' for _ in _labels], ticks='')
        return go.Figure(data=_traces, layout=_layout)


    doe_figure = build_doe_slide()
    doe_figure
    return (doe_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Slide two — where the design ran out of room

    Two moves, and no cube: the deck draws that by hand, so the field takes the whole canvas.

    **One system of a hundred.** Campaign 1's categorical space drawn in full: five oils down,
    twenty surfactant / cosurfactant pairs across, grouped into four surfactant blocks —
    5 × 4 × 5 = 100. The DoE's single system, Oleic acid / Tween 80 / PEG 400, is one cell in it,
    filled and outlined in its own hue. The cell it occupies is *found* by matching `DOE_SYSTEM`
    against the grid, not positioned by hand, so it stays correct if the category order is ever
    edited.

    **The cells are squares, not rectangles.** A cell's width and height are one number,
    `min(width available, height available)`, so the field reads as a hundred equal slots rather
    than as a table whose rows happen to be short. On the 1280 canvas twenty columns is the
    binding constraint, so the block is centred in the space the square cells do not fill.

    Two of the twenty columns are the same molecule in both roles — Tween 80 / Tween 80 and
    PEG 400 / PEG 400. Table 1 offers PEG 400 and Tween 80 as both surfactant and cosurfactant
    candidates, and the paper says so explicitly, so those columns are real cells and are drawn
    exactly like the other ninety. They used to carry a darker tint and a bold column head. Both
    are gone: on a slide whose one claim is that the hundred are alike and one of them was tried,
    a second emphasis invited the reader to look for a meaning that is not there.

    **The column heads sit at −45°, not upright.** A diagonal head is read at a glance where a
    vertical one has to be tilted into, and it costs about a third less headroom, which the block
    takes back. Each head is anchored by its *end*, so it runs up into the column it names — the
    other anchoring starts the text at the column and drifts right, and across twenty 56 px
    columns that is enough to attach a name to its neighbour.

    **The cell edge is `SPACE_COLOR` at full strength**, `CELL_EDGE` wide. The grid is the
    reachable space, so its outline is the deck primary rather than a wash of it, heavy enough to
    survive a projector.

    **Three settings become ranges.** The strip along the bottom draws each factor twice: the
    design's three stops, and Campaign 1's continuous range beneath. The ranges are the same
    intervals — Table 1 did not widen the dials, it removed the stops between them.

    **Labels only.** The slide carries its title, the grid's row and column names, and the dials'
    names and end values — nothing else. Every callout, caption and summary line was cut: the
    reading is the geometry, and the deck says the rest out loud. The two legend entries are what
    is left to say which mark is which.

    Nothing on this slide is a result. It is the space, before any experiment.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    CELL_EDGE,
    COSURFACTANTS,
    COSURF_SHORT,
    DOE_COLOR,
    DOE_SYSTEM,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEGEND_SIZE,
    MARKER_SIZE,
    OILS,
    OIL_V_RANGE,
    SCHEMATIC_MARGIN,
    SMIX_RATIO_LABELS,
    SONICATION_RANGE,
    SPACE_COLOR,
    SURFACTANTS,
    TITLE_SIZE,
    fade,
    go,
    pixel_axes,
):
    def build_expansion_slide():
        _traces, _annotations, _shapes = [], [], []

        # ---- Campaign 1's 100 systems, 5 oils x 20 role pairs ---------------------------
        # The whole canvas: there is no cube panel beside it any more, the deck draws that by
        # hand.
        _grid_x, _grid_y, _gw, _gh = pixel_axes((0.015, 0.985), (0.250, 1.000))
        _pairs = [(s, c) for s in SURFACTANTS for c in COSURFACTANTS]
        _n_col, _n_row = len(_pairs), len(OILS)
        assert _n_col * _n_row == 100, 'Table 1 declares 5 x 4 x 5 = 100 systems'

        # Header zone, top to bottom: the block rule and its surfactant name, then the rotated
        # cosurfactant heads rising off the top of the cells. _top is where the cells begin.
        _left, _top = 112.0, 96.0
        _HEAD_RULE = 30.0

        # Cells are SQUARE. One number for width and height, the smaller of what each direction
        # can spare, so a hundred equal slots read as a hundred equal slots rather than as a
        # table with short rows. Twenty columns against five rows means width binds on the 1280
        # canvas; whichever binds, the block is centred in the space the squares do not fill.
        _cell = min((_gw - _left - 4.0) / _n_col, (_gh - _top - 6.0) / _n_row)
        _x_off = (_gw - (_left + _n_col * _cell)) / 2.0
        _y_off = (_gh - (_top + _n_row * _cell)) / 2.0
        _pad = 4.5

        for _r, _oil in enumerate(OILS):
            for _c, (_s, _cs) in enumerate(_pairs):
                _x0 = _x_off + _left + _c * _cell
                _y0 = _y_off + _top + _r * _cell
                _is_doe = (_oil, _s, _cs) == DOE_SYSTEM
                # Every cell of the hundred is drawn the same. The two same-molecule columns
                # used to carry a darker tint; it read as a third category on a slide whose
                # whole point is that the hundred are alike, so it is gone. The only mark that
                # separates a cell from its neighbours is the DoE's one orange square.
                _shapes.append(dict(
                    type='rect', xref='x', yref='y',
                    x0=_x0 + _pad, x1=_x0 + _cell - _pad,
                    y0=_y0 + _pad, y1=_y0 + _cell - _pad,
                    fillcolor=fade(DOE_COLOR, 0.35) if _is_doe else fade(SPACE_COLOR, 0.11),
                    line=dict(color=DOE_COLOR if _is_doe else SPACE_COLOR,
                              width=2.4 if _is_doe else CELL_EDGE),
                    layer='below',
                ))
        assert any((_o, _s, _c) == DOE_SYSTEM for _o in OILS for _s, _c in _pairs), \
            'DOE_SYSTEM is not a cell of the Table 1 grid'

        # Column heads: the surfactant blocks spelled out, the cosurfactant columns abbreviated.
        # Twenty columns is about 56 px each, so a rotated full name needs more headroom than the
        # rows can spare. The abbreviations are display-only and are checked against Table 1's own
        # list, so a rename in COSURFACTANTS fails here rather than silently mislabelling a column.
        assert set(COSURF_SHORT) == set(COSURFACTANTS), \
            'COSURF_SHORT does not cover Table 1 cosurfactants'
        for _si, _s in enumerate(SURFACTANTS):
            _bx0 = _x_off + _left + _si * len(COSURFACTANTS) * _cell
            _bx1 = _bx0 + len(COSURFACTANTS) * _cell
            _shapes.append(dict(
                type='line', xref='x', yref='y',
                x0=_bx0 + _pad, x1=_bx1 - _pad,
                y0=_y_off + _HEAD_RULE, y1=_y_off + _HEAD_RULE,
                line=dict(color=INK, width=1.4)))
            _annotations.append(dict(
                xref='x', yref='y', x=(_bx0 + _bx1) / 2.0, y=_y_off + _HEAD_RULE - 6,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=INK), text='<b>{}</b>'.format(_s)))
            for _ci, _c in enumerate(COSURFACTANTS):
                # -45, not -90: a diagonal head is read at a glance where an upright one has to
                # be tilted into. The bold-on-same-molecule emphasis went with the cell tint --
                # half a marker for a distinction the slide no longer draws is worse than none.
                _annotations.append(dict(
                    xref='x', yref='y',
                    x=_bx0 + (_ci + 0.5) * _cell, y=_y_off + _top - 6,
                    xanchor='right', yanchor='bottom', showarrow=False, textangle=-45,
                    font=dict(size=ANNOTATION_SIZE - 5, color=INK_SOFT),
                    text=COSURF_SHORT[_c]))
        for _r, _oil in enumerate(OILS):
            _annotations.append(dict(
                xref='x', yref='y', x=_x_off + _left - 10,
                y=_y_off + _top + (_r + 0.5) * _cell,
                xanchor='right', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=INK), text=_oil))

        # ---- bottom: three settings become ranges ---------------------------------------
        _dial_x, _dial_y, _dw, _dh = pixel_axes((0.015, 0.985), (0.000, 0.215))
        _dials = [
            ('Oil volume', ['{:g} %'.format(OIL_V_RANGE[0]),
                            '{:g} %'.format(sum(OIL_V_RANGE) / 2),
                            '{:g} %'.format(OIL_V_RANGE[1])]),
            ('Smix ratio', list(SMIX_RATIO_LABELS)),
            ('Sonication', ['{:g} min'.format(SONICATION_RANGE[0]),
                            '{:g}'.format(sum(SONICATION_RANGE) / 2),
                            '{:g} min'.format(SONICATION_RANGE[1])]),
        ]
        # The side labels that named the two rows are gone with the rest of the prose, so the
        # tracks take the width back and the legend carries which mark is which.
        _dial_edge, _dial_gap = 60.0, 56.0
        _track_w = (_dw - 2 * _dial_edge - 2 * _dial_gap) / 3.0
        for _di, (_name, _ticks) in enumerate(_dials):
            _x0 = _dial_edge + _di * (_track_w + _dial_gap)
            _y_stop, _y_range = 44.0, 78.0
            _annotations.append(dict(
                xref='x2', yref='y2', x=_x0 + _track_w / 2.0, y=_y_stop - 20,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE, color=INK), text='<b>{}</b>'.format(_name)))
            _shapes.append(dict(type='line', xref='x2', yref='y2',
                                x0=_x0, x1=_x0 + _track_w, y0=_y_stop, y1=_y_stop,
                                line=dict(color=fade(DOE_COLOR, 0.45), width=1.4)))
            _traces.append(go.Scatter(
                x=[_x0, _x0 + _track_w / 2.0, _x0 + _track_w],
                y=[_y_stop] * 3, xaxis='x2', yaxis='y2', mode='markers',
                hoverinfo='skip', showlegend=False,
                marker=dict(size=MARKER_SIZE - 2, color=DOE_COLOR,
                            line=dict(width=1.3, color=INK))))
            _shapes.append(dict(type='rect', xref='x2', yref='y2',
                                x0=_x0, x1=_x0 + _track_w, y0=_y_range - 9, y1=_y_range + 9,
                                fillcolor=fade(SPACE_COLOR, 0.28),
                                line=dict(color=SPACE_COLOR, width=1.6)))
            for _ti, _t in enumerate(_ticks):
                _annotations.append(dict(
                    xref='x2', yref='y2', x=_x0 + (_ti / 2.0) * _track_w, y=_y_range + 18,
                    xanchor='center', yanchor='top', showarrow=False,
                    font=dict(size=ANNOTATION_SIZE - 3, color=INK_SOFT), text=_t))

        # ---- legend proxies -------------------------------------------------------------
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers',
            name='Box-Behnken  ·  1 system, 3 settings per dial',
            marker=dict(size=MARKER_SIZE, color=DOE_COLOR, symbol='circle',
                        line=dict(width=1.4, color=INK))))
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers',
            name='Campaign 1  ·  100 systems, continuous within each',
            marker=dict(size=MARKER_SIZE, color=fade(SPACE_COLOR, 0.35), symbol='square',
                        line=dict(width=1.4, color=SPACE_COLOR))))

        _annotations += [
            # Both live in the top margin, not in the plot area: the grid runs to the very
            # top of its axis now, and a subtitle sitting at paper 0.955 would land on the
            # surfactant block rules.
            dict(xref='paper', yref='paper', x=0.5, y=1.100, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK), name='heading',
                 text='<b>One system of a hundred &#8212; and three settings become ranges</b>'),
            dict(xref='paper', yref='paper', x=0.5, y=1.045, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text='Everything the Box-Behnken design could reach, against everything '
                      'Campaign 1 could propose'),
        ]

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=SCHEMATIC_MARGIN,
            xaxis=_grid_x, yaxis=_grid_y,
            xaxis2=_dial_x, yaxis2=_dial_y,
            shapes=_shapes, annotations=_annotations,
            legend=dict(orientation='h', xanchor='center', x=0.5, yanchor='top', y=-0.02,
                        font=dict(size=LEGEND_SIZE), itemsizing='constant',
                        bgcolor='rgba(0,0,0,0)'),
        )
        return go.Figure(data=_traces, layout=_layout)


    expansion_figure = build_expansion_slide()
    expansion_figure
    return (expansion_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export

    Each figure at the house 1280 × 720, one data unit to one exported pixel. `EXPORT_FORMATS`
    writes a 2× raster alongside if `png` is added to it.

    **Every figure is exported twice, once per entry in `FONT_SCHEMES`.**

    | file | body | headings |
    | --- | --- | --- |
    | `<stem>.svg` | `Open Sans` | `Open Sans` |
    | `<stem>_Pretendard.svg` | Pretendard | Gmarket Sans TTF Medium |

    Headings are the slide title, the axis titles and the tick labels; body is everything else —
    subtitles, legends, and the in-plot annotations that carry the row and column names. The
    split follows the deck: the reading face sets prose, the display face labels the frame.

    **Sizes are identical in both.** The house 20/18/18/14/14 does not move, so a `_Pretendard`
    export is a drop-in replacement for its plain twin and nothing has to be re-checked for fit.

    The plain export exists because **an SVG references a font rather than embedding one**. The
    `_Pretendard` pair renders as itself only where both faces are installed; anywhere else it
    falls back and the metrics shift. Use it on the machine that has them, and keep the plain
    one for anything that leaves.
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
    doe_figure,
    expansion_figure,
    with_font_scheme,
):
    FIGURES = {
        'Design_Space_DoE': (doe_figure, FIG_WIDTH, FIG_HEIGHT),
        'Design_Space_Expansion': (expansion_figure, FIG_WIDTH, FIG_HEIGHT),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for _stem, (_fig, _w, _h) in FIGURES.items():
        for _suffix, (_body, _heading) in FONT_SCHEMES.items():
            _themed = with_font_scheme(_fig, _body, _heading)
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
