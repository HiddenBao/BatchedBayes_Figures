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
    # Design Space Figure Suite

    **Two figures, one argument, one shared cube.** Act 1's opening pair:

    | export | slide | what it says |
    | --- | --- | --- |
    | `Design_Space_DoE.svg` | one | what the Box-Behnken design produced, against the Table 2 targets |
    | `Design_Space_Expansion.svg` | two | that design as one system of a hundred, and its three settings as ranges |

    **Slide one draws no cube.** The design's geometry is drawn by hand in the deck, from the
    spec the suite asserts here — see `DOE_CODED` and the `cube_traces()` projection below, which
    slide two still uses. Slide one is the measurements and nothing else: two panels, five rows,
    two targets.

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
    return Path, go, np, pd


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

    Both cubes and the 5 × 20 field are schematics, so they sit on `pixel_axes()`: hidden axes
    whose range spans exactly as many data units as the domain spans exported pixels, origin top
    left. One data unit is one pixel, so a 6 px marker is 6 px on the slide and the isometric
    projection keeps its angles whatever the domain is.
    """)
    return


@app.cell
def _(FIG_HEIGHT, FIG_WIDTH):
    DOE_COLOR = '#E69F00'      # orange  -- the Box-Behnken design and its runs
    BEST_COLOR = '#D55E00'     # red     -- DoEOPT, the mark to beat
    SPACE_COLOR = '#2067F4'    # blue    -- Campaign 1's reachable space; the family, not a batch

    INK = 'black'
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    RULE = 'rgba(0, 0, 0, 0.22)'
    WIRE = 'rgba(0, 0, 0, 0.30)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    MARKER_SIZE = 13
    MARKER_RING = 2
    ERROR_WIDTH = 1.4
    FRAME_WIDTH = 2

    LEGEND_MARGIN = 96   # bottom gutter the horizontal legend sits in

    # Paper Table 2, response targets for formulation optimisation.
    SPEC_SIZE_NM = 100.0
    SPEC_PDI = 0.3

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

    # Display-only column heads for the 5 x 20 field: twenty columns leave about 42 px each, and
    # a rotated 'Propylene Glycol' needs more headroom than the five rows can spare. The figure
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

    # The CSV's `DoEOPT` is an id; the deck spells the row DoE-OPT, as Campaign1_Progress and
    # both leaderboards already do.
    ROW_LABEL = {'DoEOPT': 'DoE-OPT'}


    def fade(hex_color, alpha):
        """Convert '#RRGGBB' to an rgba() string at the given alpha."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return 'rgba({}, {}, {}, {})'.format(r, g, b, alpha)


    def pixel_axes(x_domain, y_domain):
        """Axis pair whose data units are exported pixels, origin top left.

        The range spans exactly as many units as the domain spans pixels on the 1280 x 720
        canvas, so a schematic drawn in these coordinates keeps its proportions and its
        stroke weights whatever domain it is given.
        """
        width = (x_domain[1] - x_domain[0]) * FIG_WIDTH
        height = (y_domain[1] - y_domain[0]) * FIG_HEIGHT
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
        BEST_COLOR,
        COSURFACTANTS,
        COSURF_SHORT,
        DOE_COLOR,
        DOE_SYSTEM,
        ERROR_WIDTH,
        FONT_FAMILY,
        INK,
        INK_SOFT,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        MARKER_RING,
        MARKER_SIZE,
        OILS,
        OIL_V_RANGE,
        ROW_LABEL,
        RULE,
        SMIX_RATIO_LABELS,
        SONICATION_RANGE,
        SPACE_COLOR,
        SPEC_PDI,
        SPEC_SIZE_NM,
        SURFACTANTS,
        TITLE_SIZE,
        WIRE,
        fade,
        pixel_axes,
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
    ## The cube

    One projection function, used by both figures. A three-factor Box-Behnken design is a cube
    sampled at its **twelve edge midpoints plus its centre**, so `BBD_POINTS` is generated from
    that rule rather than typed out — a point has exactly one coordinate at zero and the other two
    at ±1.

    ### Orientation and depth — the two things that were wrong first

    The projection is **trimetric, not isometric**, and that is a correctness choice rather than
    a stylistic one.

    ```
    VIEW = (-1.00, -0.62, 0.78)        # (oil, Smix, sonication), viewer toward low-low, above
    right = normalise(z_hat x VIEW);  up = normalise(VIEW x right)
    x =  (p · right) * S
    y = -(p · up)    * S               # y increases DOWNWARD
    ```

    **Why not isometric.** Equal view components give equal foreshortening, a regular-hexagon
    silhouette, and two opposite corners landing on the same point — so a reader cannot tell a
    near sample point from a far one, and it is not a matter of taste: under isometric, `DoE-OPT`
    projected exactly on top of one of the design's own runs. Three *unequal* components separate
    every corner, foreshorten the three axes differently so they are told apart by length as well
    as direction, and leave a well-defined `HIDDEN_CORNER` whose three edges are drawn dotted.
    The cell asserts a minimum separation of 0.25 half-edges over every position it draws, so a
    future change to `VIEW` cannot quietly reintroduce a collapse. Current worst case: **0.331**.

    **Which way the axes run.** The origin corner `(−1, −1, −1)` sits at the bottom front and
    every factor increases away from it — `+oil` up-right, `+Smix` up-left, `+sonication`
    straight up. The first version had the `(oil + Smix)` term positive against a downward screen
    y, which put the *high-high* corner at the bottom and ran both horizontal factors backwards.
    It looked right and read wrong, which is the worst combination.

    **Label sonication on the right-hand silhouette edge**, `(+1, −1, −1)` → `(+1, −1, +1)`, where
    the oil axis ends. A vertical edge nearer the middle carries its label across the drawing.

    Sample points are drawn **back to front with a white halo**, so a near point occludes a far
    one instead of merging with it. Between the dotted hidden edges and the halo, depth is
    readable without a legend.

    `cube_traces()` returns the hidden and visible wireframes, the sampled points, the three
    labelled factor edges and `DoEOPT`'s face-centre marker as one list, at whatever centre and
    scale it is handed. Slide two draws it at `S = 44`; slide one draws no cube at all.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    BEST_COLOR,
    DOE_CODED,
    DOE_COLOR,
    DOE_OPT_ID,
    INK,
    OIL_V_RANGE,
    RULE,
    SMIX_RATIO_LABELS,
    SONICATION_RANGE,
    WIRE,
    fade,
    go,
    np,
):
    # A Box-Behnken point: exactly one coded zero, the other two coordinates at +/-1.
    BBD_POINTS = []
    for _zero in range(3):
        for _a in (-1, 1):
            for _b in (-1, 1):
                _p = [0, 0, 0]
                _rest = [i for i in range(3) if i != _zero]
                _p[_rest[0]], _p[_rest[1]] = _a, _b
                BBD_POINTS.append(tuple(_p))
    BBD_CENTRE = (0, 0, 0)

    assert len(BBD_POINTS) == 12, 'a three-factor Box-Behnken has twelve edge midpoints'
    assert all(sum(1 for v in p if v == 0) == 1 for p in BBD_POINTS)
    assert set(DOE_CODED[e] for e in ('DoE1', 'DoE4', 'DoE10', 'DoE11')) <= set(BBD_POINTS), \
        'a run in data/ is not an edge midpoint of the design'

    CUBE_CORNERS = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    CUBE_EDGES = [(a, b) for a in CUBE_CORNERS for b in CUBE_CORNERS
                  if sum(1 for i in range(3) if a[i] != b[i]) == 1 and a < b]

    # The view direction, and it is deliberately NOT isometric.
    #
    # An isometric view of a cube -- equal components, equal foreshortening -- draws a regular
    # hexagon in which two opposite corners project to exactly the same point, so a reader
    # cannot tell a near sample point from a far one. That degeneracy is not a stylistic
    # problem, it is a wrong drawing: under isometric, DoE-OPT landed on top of one of the
    # design's own runs.
    #
    # Three unequal components give a trimetric view instead: every corner projects
    # separately, the three axes foreshorten differently so they are told apart by length as
    # well as direction, and there is a well-defined hidden corner whose edges can be drawn
    # as hidden. The viewer sits toward low oil and low Smix and above, which puts the origin
    # corner (-1, -1, -1) at the bottom front, carrying the three factor labels.
    VIEW = np.array([-1.00, -0.62, 0.78])

    _v = VIEW / np.linalg.norm(VIEW)
    _right = np.cross(np.array([0.0, 0.0, 1.0]), _v)
    _right /= np.linalg.norm(_right)
    _up = np.cross(_v, _right)
    _up /= np.linalg.norm(_up)

    ORIGIN_CORNER = (-1, -1, -1)
    HIDDEN_CORNER = min(CUBE_CORNERS, key=lambda c: float(np.asarray(c, float) @ _v))


    def project(coded, cx, cy, s):
        """Trimetric projection into top-left pixel coordinates, y increasing downward.

        Sonication is kept vertical; +oil runs up-right and +Smix up-left, both increasing
        away from the origin corner at the bottom. Returns pixels, so `s` is the cube's
        half-edge on screen.
        """
        _p = np.asarray(coded, dtype=float)
        return (cx + float(_p @ _right) * s, cy - float(_p @ _up) * s)


    def depth(coded):
        """How near the viewer a position is; larger is nearer."""
        return float(np.asarray(coded, dtype=float) @ _v)


    def cube_traces(cx, cy, s, point_size=11, wire_width=1.4, label_axes=True,
                    ring_runs=(), show_opt=True):
        """The design cube as a list of traces, at the given centre and scale.

        Hidden edges -- the three meeting `HIDDEN_CORNER` -- are drawn dashed and pale, the
        standard convention, so the cube reads as a solid with a front and a back. Sample
        points are drawn back to front with a ground-coloured halo, so a near point occludes
        a far one rather than merging with it.
        """
        traces, annotations = [], []

        for _hidden in (True, False):
            _wx, _wy = [], []
            for _a, _b in CUBE_EDGES:
                if (HIDDEN_CORNER in (_a, _b)) != _hidden:
                    continue
                _pa, _pb = project(_a, cx, cy, s), project(_b, cx, cy, s)
                _wx += [_pa[0], _pb[0], None]
                _wy += [_pa[1], _pb[1], None]
            traces.append(go.Scatter(
                x=_wx, y=_wy, mode='lines', hoverinfo='skip', showlegend=False,
                line=dict(color=RULE if _hidden else WIRE,
                          width=wire_width * (0.8 if _hidden else 1.0),
                          dash='dot' if _hidden else 'solid'),
            ))

        # The three factor axes, on cube edges leaving the origin corner -- except sonication,
        # which is labelled on the right-hand silhouette vertical where the oil axis ends.
        # A vertical edge through the drawing's middle would run its label across the cube.
        if label_axes:
            _axes = [
                (ORIGIN_CORNER, (1, -1, -1), 'Oil volume',
                 '{:g} &#8211; {:g} %'.format(*OIL_V_RANGE), (28, 30), 0),
                (ORIGIN_CORNER, (-1, 1, -1), 'Smix ratio',
                 '{} &#8211; {}'.format(SMIX_RATIO_LABELS[0], SMIX_RATIO_LABELS[2]),
                 (-16, 40), 0),
                ((1, -1, -1), (1, -1, 1), 'Sonication',
                 '{:g} &#8211; {:g} min'.format(*SONICATION_RANGE), (38, 0), -90),
            ]
            _ax, _ay = [], []
            for _from, _to, _name, _range_text, _offset, _angle in _axes:
                _pa, _pb = project(_from, cx, cy, s), project(_to, cx, cy, s)
                _ax += [_pa[0], _pb[0], None]
                _ay += [_pa[1], _pb[1], None]
                annotations.append(dict(
                    x=(_pa[0] + _pb[0]) / 2.0 + _offset[0],
                    y=(_pa[1] + _pb[1]) / 2.0 + _offset[1],
                    showarrow=False, xanchor='center', yanchor='middle',
                    textangle=_angle, align='center',
                    font=dict(size=ANNOTATION_SIZE, color=INK),
                    text='<b>{}</b><br><span style="font-size:{}px">{}</span>'.format(
                        _name, ANNOTATION_SIZE - 3, _range_text),
                ))
            traces.append(go.Scatter(
                x=_ax, y=_ay, mode='lines', hoverinfo='skip', showlegend=False,
                line=dict(color=INK, width=wire_width + 0.8),
            ))

        # Sample points, back to front. The halo is what makes the depth order visible.
        _sampled = BBD_POINTS + [BBD_CENTRE]
        _order = sorted(_sampled, key=depth)
        _pts = [project(p, cx, cy, s) for p in _order]
        traces.append(go.Scatter(
            x=[p[0] for p in _pts], y=[p[1] for p in _pts], mode='markers',
            name='Box-Behnken run  ·  12 edge midpoints + centre', hoverinfo='skip',
            marker=dict(size=point_size, color=DOE_COLOR, symbol='circle',
                        line=dict(width=2.0, color='white')),
        ))

        if ring_runs:
            _ring = [project(DOE_CODED[e], cx, cy, s) for e in ring_runs]
            traces.append(go.Scatter(
                x=[p[0] for p in _ring], y=[p[1] for p in _ring], mode='markers',
                hoverinfo='skip', showlegend=False,
                marker=dict(size=point_size + 10, color='rgba(0,0,0,0)', symbol='circle',
                            line=dict(width=1.6, color=fade(DOE_COLOR, 0.85))),
            ))

        # DoE-OPT, on a face the design never sampled.
        if show_opt:
            _po = project(DOE_CODED[DOE_OPT_ID], cx, cy, s)
            traces.append(go.Scatter(
                x=[_po[0]], y=[_po[1]], mode='markers',
                name='DoE-OPT  ·  face centre, predicted then confirmed', hoverinfo='skip',
                marker=dict(size=point_size + 5, color=BEST_COLOR, symbol='diamond',
                            line=dict(width=2.0, color='white')),
            ))

        return traces, annotations


    # The view must separate every position it draws, or the drawing is lying about depth.
    _all = BBD_POINTS + [BBD_CENTRE, DOE_CODED[DOE_OPT_ID]]
    _sep = min(
        float(np.hypot(*(np.subtract(project(_a, 0, 0, 1), project(_b, 0, 0, 1)))))
        for _i, _a in enumerate(_all) for _b in _all[_i + 1:]
    )
    assert _sep > 0.25, \
        'view direction {} collapses two positions ({:.4f} half-edges apart)'.format(VIEW, _sep)
    print('trimetric view {} -- hidden corner {}, minimum separation {:.3f} half-edges'.format(
        list(VIEW), HIDDEN_CORNER, _sep))
    return (cube_traces,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Slide one — the design of experiments

    Three panels on one canvas, sharing a row order:

    - **left**, the cube on a pixel grid: the design space, its thirteen sampled positions, its
      three labelled factor edges, and `DoEOPT` on a face it never sampled;
    - **centre**, measured droplet size against the Table 2 target of 100 nm;
    - **right**, measured PDI against the Table 2 target of 0.3.

    The two results panels are real axes with the house 2 px mirrored box; the cube is a schematic
    and gets no box at all, because a frame around a projection reads as a fourth face.

    Rows run `DoE1` · `DoE4` · `DoE10` · `DoE11` · `DoEOPT` — file order, with `DoEOPT` last and set
    off by a rule, exactly the way `Campaign1_Progress` separates it as its own section. The four
    design runs are ringed on the cube in the same order, so a reader can carry a row back to a
    position.

    Both targets are drawn as **dashed ink verticals with a shaded miss-side**. Nothing crosses
    either: the campaign's best droplet size is 184.6 nm against a target of 100, and its best PDI
    0.325 against 0.3. That is the slide.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
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
    ROW_LABEL,
    RULE,
    SPEC_PDI,
    SPEC_SIZE_NM,
    TITLE_SIZE,
    go,
):
    def build_doe_slide():
        _rows = DOE_RUNS
        _y = list(range(len(_rows), 0, -1))          # first row at the top
        _labels = [ROW_LABEL.get(e, e) for e in _rows['Exp']]
        _is_opt = [e == DOE_OPT_ID for e in _rows['Exp']]

        def _results(axis_suffix, values, errors):
            _t = []
            for _opt in (False, True):
                _idx = [i for i, o in enumerate(_is_opt) if o == _opt]
                if not _idx:
                    continue
                _t.append(go.Scatter(
                    x=[values[i] for i in _idx], y=[_y[i] for i in _idx],
                    xaxis='x' + axis_suffix, yaxis='y' + axis_suffix,
                    mode='markers', hoverinfo='skip', showlegend=False,
                    error_x=dict(type='data', array=[errors[i] for i in _idx],
                                 color=BEST_COLOR if _opt else DOE_COLOR,
                                 thickness=ERROR_WIDTH, width=6),
                    marker=dict(
                        size=MARKER_SIZE + (4 if _opt else 0),
                        color=BEST_COLOR if _opt else DOE_COLOR,
                        symbol='diamond' if _opt else 'circle',
                        line=dict(width=MARKER_RING, color='white')),
                ))
            return _t

        _traces = (_results('', list(_rows['size_nm']), list(_rows['size_sd']))
                   + _results('2', list(_rows['pdi']), list(_rows['pdi_sd'])))

        for _name, _colour, _symbol in (
            ('Box-Behnken run', DOE_COLOR, 'circle'),
            ('DoE-OPT  ·  the optimum the design pointed at', BEST_COLOR, 'diamond'),
        ):
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='markers', name=_name,
                marker=dict(size=MARKER_SIZE, color=_colour, symbol=_symbol,
                            line=dict(width=1.4, color=INK))))

        _size_max = 540.0
        _pdi_max = 0.90
        _panel_top, _panel_bottom = 0.80, 0.19

        # The Table 2 target zone is shaded on the *pass* side. Nothing reached either target, so
        # the shaded band is the empty stretch of each panel -- which is the whole reading.
        _shapes = []
        for _ref, _spec in (('x', SPEC_SIZE_NM), ('x2', SPEC_PDI)):
            _shapes.append(dict(
                type='rect', xref=_ref, yref='paper', x0=0, x1=_spec,
                y0=_panel_bottom, y1=_panel_top,
                fillcolor='rgba(0, 0, 0, 0.055)', line=dict(width=0), layer='below'))
            _shapes.append(dict(
                type='line', xref=_ref, yref='paper', x0=_spec, x1=_spec,
                y0=_panel_bottom, y1=_panel_top,
                line=dict(color=INK, width=1.8, dash='dash')))
        # DoE-OPT sits below a rule, as its own section -- as on Campaign1_Progress.
        _shapes.append(dict(
            type='line', xref='paper', yref='y', x0=0.08, x1=0.97, y0=1.5, y1=1.5,
            line=dict(color=RULE, width=1.2, dash='dot')))

        _annotations = [
            dict(xref='paper', yref='paper', x=0.5, y=1.0, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK),
                 text='<b>The design of experiments, and what it produced</b>'),
            dict(xref='paper', yref='paper', x=0.5, y=0.955, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text='{} &#8212; one system, fixed before the first experiment'.format(
                     '&#8195;·&#8195;'.join(DOE_SYSTEM))),
            dict(xref='paper', yref='paper', x=0.08, y=0.855, xanchor='left', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK),
                 text='<b>Droplet size</b>, nm'),
            dict(xref='paper', yref='paper', x=0.62, y=0.855, xanchor='left', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK),
                 text='<b>PDI</b>'),
            dict(xref='x', yref='paper', x=SPEC_SIZE_NM, y=0.82, xanchor='left',
                 yanchor='bottom', showarrow=False,
                 font=dict(size=ANNOTATION_SIZE - 2, color=INK),
                 text='&#8592; target &lt; {:g} nm'.format(SPEC_SIZE_NM)),
            dict(xref='x2', yref='paper', x=SPEC_PDI, y=0.82, xanchor='left',
                 yanchor='bottom', showarrow=False,
                 font=dict(size=ANNOTATION_SIZE - 2, color=INK),
                 text='&#8592; target &lt; {:g}'.format(SPEC_PDI)),
            dict(xref='paper', yref='paper', x=0.08, y=0.095, xanchor='left', yanchor='top',
                 showarrow=False, align='left',
                 font=dict(size=ANNOTATION_SIZE - 2, color=INK_SOFT),
                 text='Mean of three replicates; bars are their standard deviation. These are '
                      'the runs the design left comparable &#8212; the rest of<br>the box '
                      'phase-separated or predate a standardised protocol, and are not scored '
                      'against these targets.'),
        ]

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=dict(l=10, r=10, t=104, b=LEGEND_MARGIN),
            xaxis=dict(AXIS_COMMON, domain=[0.08, 0.56], anchor='y',
                       range=[0, _size_max], dtick=100),
            yaxis=dict(AXIS_COMMON, domain=[_panel_bottom, _panel_top], anchor='x',
                       range=[0.4, len(_rows) + 0.6],
                       tickmode='array', tickvals=_y, ticktext=_labels, ticks=''),
            xaxis2=dict(AXIS_COMMON, domain=[0.62, 0.97], anchor='y2',
                        range=[0, _pdi_max], dtick=0.3),
            yaxis2=dict(AXIS_COMMON, domain=[_panel_bottom, _panel_top], anchor='x2',
                        range=[0.4, len(_rows) + 0.6],
                        tickmode='array', tickvals=_y, ticktext=['' for _ in _labels],
                        ticks=''),
            shapes=_shapes, annotations=_annotations,
            legend=dict(orientation='h', xanchor='center', x=0.5, yanchor='top', y=-0.04,
                        font=dict(size=LEGEND_SIZE), itemsizing='constant',
                        bgcolor='rgba(0,0,0,0)'),
        )
        return go.Figure(data=_traces, layout=_layout)


    doe_figure = build_doe_slide()
    doe_figure
    return (doe_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Slide two — where the design ran out of room

    The same cube, at `S = 40` and without its results, then two moves:

    **One system of a hundred.** The field on the right is Campaign 1's categorical space drawn in
    full: five oils down, twenty surfactant / cosurfactant pairs across, grouped into four
    surfactant blocks — 5 × 4 × 5 = 100. The DoE's single system, Oleic acid / Tween 80 / PEG 400,
    is one cell in it, outlined in its own hue and pointed at. The cell it occupies is *found* by
    matching `DOE_SYSTEM` against the grid, not positioned by hand, so it stays correct if the
    category order is ever edited.

    Two of the twenty columns are the same molecule in both roles — Tween 80 / Tween 80 and
    PEG 400 / PEG 400. Table 1 offers PEG 400 and Tween 80 as both surfactant and cosurfactant
    candidates, and the paper says so explicitly, so those columns are real cells and are tinted
    rather than excluded. `D3`, one of the campaign's three in-specification formulations, is in one
    of them.

    **Three settings become ranges.** The strip along the bottom draws each factor twice: the
    design's three stops, and Campaign 1's continuous range beneath. The ranges are the same
    intervals — Table 1 did not widen the dials, it removed the stops between them.

    Nothing on this slide is a result. It is the space, before any experiment.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    COSURFACTANTS,
    COSURF_SHORT,
    DOE_COLOR,
    DOE_SYSTEM,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    MARKER_SIZE,
    OILS,
    OIL_V_RANGE,
    SMIX_RATIO_LABELS,
    SONICATION_RANGE,
    SPACE_COLOR,
    SURFACTANTS,
    TITLE_SIZE,
    cube_traces,
    fade,
    go,
    pixel_axes,
):
    def build_expansion_slide():
        _traces, _annotations, _shapes = [], [], []

        # ---- left: the cube of slide one, smaller and without its results ---------------
        # Same projection, same point rule, a quarter the scale. The axes are left unlabelled:
        # slide one taught them, and repeating them here would compete with the field.
        _cube_x, _cube_y, _cw, _ch = pixel_axes((0.015, 0.205), (0.30, 0.86))
        _ct, _cn = cube_traces(cx=_cw * 0.52, cy=_ch * 0.32, s=44,
                               point_size=7, wire_width=1.1, label_axes=False,
                               show_opt=False)
        for _t in _ct:
            _t.showlegend = False
        _traces += _ct
        _annotations += _cn
        _annotations += [
            dict(xref='x', yref='y', x=_cw * 0.52, y=_ch * 0.32 + 112,
                 xanchor='center', yanchor='top', showarrow=False, align='center',
                 font=dict(size=ANNOTATION_SIZE, color=DOE_COLOR),
                 text='<b>13 runs, one system</b>'),
            dict(xref='x', yref='y', x=_cw * 0.52, y=_ch * 0.32 + 138,
                 xanchor='center', yanchor='top', showarrow=False, align='center',
                 font=dict(size=ANNOTATION_SIZE - 2, color=INK_SOFT),
                 text='{}<br><br>three settings per dial,<br>nothing in between'.format(
                     '<br>'.join(DOE_SYSTEM))),
        ]

        # ---- right: Campaign 1's 100 systems, 5 oils x 20 role pairs --------------------
        _grid_x, _grid_y, _gw, _gh = pixel_axes((0.235, 0.985), (0.30, 0.86))
        _pairs = [(s, c) for s in SURFACTANTS for c in COSURFACTANTS]
        _n_col, _n_row = len(_pairs), len(OILS)
        assert _n_col * _n_row == 100, 'Table 1 declares 5 x 4 x 5 = 100 systems'

        # Header zone, top to bottom: the block rule and its surfactant name, then the rotated
        # cosurfactant heads rising off the top of the cells. _top is where the cells begin.
        _left, _top, _foot = 112.0, 118.0, 108.0
        _HEAD_RULE = 30.0
        _cell_w = (_gw - _left - 4.0) / _n_col
        _cell_h = (_gh - _top - _foot) / _n_row
        _pad = 1.6

        _doe_cell = None
        for _r, _oil in enumerate(OILS):
            for _c, (_s, _cs) in enumerate(_pairs):
                _x0 = _left + _c * _cell_w
                _y0 = _top + _r * _cell_h
                _same = _s == _cs
                _is_doe = (_oil, _s, _cs) == DOE_SYSTEM
                if _is_doe:
                    _doe_cell = (_x0 + _cell_w / 2.0, _y0 + _cell_h / 2.0)
                _shapes.append(dict(
                    type='rect', xref='x2', yref='y2',
                    x0=_x0 + _pad, x1=_x0 + _cell_w - _pad,
                    y0=_y0 + _pad, y1=_y0 + _cell_h - _pad,
                    fillcolor=(fade(DOE_COLOR, 0.35) if _is_doe
                               else fade(SPACE_COLOR, 0.24 if _same else 0.11)),
                    line=dict(color=DOE_COLOR if _is_doe else fade(SPACE_COLOR, 0.55),
                              width=2.4 if _is_doe else 0.8),
                    layer='below',
                ))
        assert _doe_cell is not None, 'DOE_SYSTEM is not a cell of the Table 1 grid'

        # Column heads: the surfactant blocks spelled out, the cosurfactant columns abbreviated.
        # Twenty columns is about 42 px each, so a rotated full name needs more headroom than the
        # rows can spare. The abbreviations are display-only and are checked against Table 1's own
        # list, so a rename in COSURFACTANTS fails here rather than silently mislabelling a column.
        assert set(COSURF_SHORT) == set(COSURFACTANTS), \
            'COSURF_SHORT does not cover Table 1 cosurfactants'
        for _si, _s in enumerate(SURFACTANTS):
            _bx0 = _left + _si * len(COSURFACTANTS) * _cell_w
            _bx1 = _bx0 + len(COSURFACTANTS) * _cell_w
            _shapes.append(dict(
                type='line', xref='x2', yref='y2',
                x0=_bx0 + _pad, x1=_bx1 - _pad, y0=_HEAD_RULE, y1=_HEAD_RULE,
                line=dict(color=INK, width=1.4)))
            _annotations.append(dict(
                xref='x2', yref='y2', x=(_bx0 + _bx1) / 2.0, y=_HEAD_RULE - 6,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=INK), text='<b>{}</b>'.format(_s)))
            for _ci, _c in enumerate(COSURFACTANTS):
                _same = _c == _s
                _annotations.append(dict(
                    xref='x2', yref='y2',
                    x=_bx0 + (_ci + 0.5) * _cell_w, y=_top - 6,
                    xanchor='center', yanchor='bottom', showarrow=False, textangle=-90,
                    font=dict(size=ANNOTATION_SIZE - 5, color=INK if _same else INK_SOFT),
                    text='<b>{}</b>'.format(COSURF_SHORT[_c]) if _same else COSURF_SHORT[_c]))
        for _r, _oil in enumerate(OILS):
            _annotations.append(dict(
                xref='x2', yref='y2', x=_left - 10, y=_top + (_r + 0.5) * _cell_h,
                xanchor='right', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=INK), text=_oil))
        # The pointer at the DoE's one cell, aimed from below so it never crosses the headers.
        _annotations.append(dict(
            xref='x2', yref='y2', x=_doe_cell[0], y=_doe_cell[1] + _cell_h * 0.45,
            ax=_doe_cell[0] + 78, ay=_doe_cell[1] + _cell_h * 2.7,
            axref='x2', ayref='y2',
            xanchor='left', yanchor='middle', showarrow=True, arrowhead=2, arrowsize=1,
            arrowwidth=1.6, arrowcolor=DOE_COLOR,
            font=dict(size=ANNOTATION_SIZE - 1, color=DOE_COLOR),
            bgcolor='white', borderpad=3,
            text='<b>the whole Box-Behnken campaign</b>'))

        _grid_bottom = _top + _n_row * _cell_h
        _annotations += [
            dict(xref='x2', yref='y2', x=_left, y=_grid_bottom + 24,
                 xanchor='left', yanchor='top', showarrow=False,
                 font=dict(size=ANNOTATION_SIZE + 3, color=SPACE_COLOR),
                 text='<b>100 systems &#8212; 5 oils × 4 surfactants × 5 cosurfactants</b>'),
            dict(xref='x2', yref='y2', x=_left, y=_grid_bottom + 52,
                 xanchor='left', yanchor='top', showarrow=False, align='left',
                 font=dict(size=ANNOTATION_SIZE - 1, color=INK_SOFT),
                 text='Bold column heads are the two tinted columns: Table 1 offers PEG 400 '
                      'and Tween 80 in <i>both</i> roles, so one molecule<br>can do both jobs. '
                      'Not a technicality &#8212; <i>D3</i>, one of the three '
                      'in-specification formulations, is in one of them.'),
        ]

        # ---- bottom: three settings become ranges ---------------------------------------
        _dial_x, _dial_y, _dw, _dh = pixel_axes((0.015, 0.985), (0.050, 0.278))
        _dials = [
            ('Oil volume', ['{:g} %'.format(OIL_V_RANGE[0]),
                            '{:g} %'.format(sum(OIL_V_RANGE) / 2),
                            '{:g} %'.format(OIL_V_RANGE[1])]),
            ('Smix ratio', list(SMIX_RATIO_LABELS)),
            ('Sonication', ['{:g} min'.format(SONICATION_RANGE[0]),
                            '{:g}'.format(sum(SONICATION_RANGE) / 2),
                            '{:g} min'.format(SONICATION_RANGE[1])]),
        ]
        _dial_left, _track_w = 132.0, 244.0
        _gap = (_dw - _dial_left - 3 * _track_w - 24.0) / 2.0
        for _di, (_name, _ticks) in enumerate(_dials):
            _x0 = _dial_left + _di * (_track_w + _gap)
            _y_stop, _y_range = 86.0, 128.0
            _annotations.append(dict(
                xref='x3', yref='y3', x=_x0 + _track_w / 2.0, y=54,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE, color=INK), text='<b>{}</b>'.format(_name)))
            _shapes.append(dict(type='line', xref='x3', yref='y3',
                                x0=_x0, x1=_x0 + _track_w, y0=_y_stop, y1=_y_stop,
                                line=dict(color=fade(DOE_COLOR, 0.45), width=1.4)))
            _traces.append(go.Scatter(
                x=[_x0, _x0 + _track_w / 2.0, _x0 + _track_w],
                y=[_y_stop] * 3, xaxis='x3', yaxis='y3', mode='markers',
                hoverinfo='skip', showlegend=False,
                marker=dict(size=MARKER_SIZE - 2, color=DOE_COLOR,
                            line=dict(width=1.3, color=INK))))
            _shapes.append(dict(type='rect', xref='x3', yref='y3',
                                x0=_x0, x1=_x0 + _track_w, y0=_y_range - 9, y1=_y_range + 9,
                                fillcolor=fade(SPACE_COLOR, 0.28),
                                line=dict(color=SPACE_COLOR, width=1.6)))
            for _ti, _t in enumerate(_ticks):
                _annotations.append(dict(
                    xref='x3', yref='y3', x=_x0 + (_ti / 2.0) * _track_w, y=_y_range + 20,
                    xanchor='center', yanchor='top', showarrow=False,
                    font=dict(size=ANNOTATION_SIZE - 3, color=INK_SOFT), text=_t))
            if _di == 0:
                for _y, _label, _colour in (
                    (_y_stop, 'Box-Behnken<br>3 settings', DOE_COLOR),
                    (_y_range, 'Campaign 1<br>a range', SPACE_COLOR),
                ):
                    _annotations.append(dict(
                        xref='x3', yref='y3', x=_x0 - 16, y=_y, xanchor='right',
                        yanchor='middle', showarrow=False, align='right',
                        font=dict(size=ANNOTATION_SIZE - 3, color=_colour), text=_label))
        _annotations.append(dict(
            xref='x3', yref='y3', x=_dial_left - 16, y=6, xanchor='left', yanchor='top',
            showarrow=False, font=dict(size=ANNOTATION_SIZE - 1, color=INK_SOFT),
            text='&#8230; and inside <i>every one</i> of the hundred, the three dials lose their '
                 'stops. Table 1 did not widen them &#8212; it removed the settings in between.'))

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
            dict(xref='paper', yref='paper', x=0.5, y=1.0, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK),
                 text='<b>One system of a hundred &#8212; and three settings become ranges</b>'),
            dict(xref='paper', yref='paper', x=0.5, y=0.955, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text='Everything the Box-Behnken design could reach, against everything '
                      'Campaign 1 could propose'),
        ]

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=dict(l=10, r=10, t=96, b=LEGEND_MARGIN),
            xaxis=_cube_x, yaxis=_cube_y,
            xaxis2=_grid_x, yaxis2=_grid_y,
            xaxis3=_dial_x, yaxis3=_dial_y,
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

    Each figure at its native 1280 × 720, one data unit to one exported pixel. `EXPORT_FORMATS`
    writes a 2× raster alongside if `png` is added to it.
    """)
    return


@app.cell
def _(
    EXPORT_FORMATS,
    FIG_HEIGHT,
    FIG_WIDTH,
    OUTPUT_DIR,
    PNG_SCALE,
    doe_figure,
    expansion_figure,
):
    FIGURES = {
        'Design_Space_DoE': (doe_figure, FIG_WIDTH, FIG_HEIGHT),
        'Design_Space_Expansion': (expansion_figure, FIG_WIDTH, FIG_HEIGHT),
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
