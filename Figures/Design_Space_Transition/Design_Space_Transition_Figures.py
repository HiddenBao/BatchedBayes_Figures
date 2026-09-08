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
    # Design Space Transition Figure Suite

    **One slide, built up in three states.** Campaign 1's hundred declared systems become the
    forty-eight Campaign 2 can propose from, and then the settings and the score change under
    them.

    | export | state | the one move it makes |
    | --- | --- | --- |
    | `Design_Space_Transition_Explored.svg` | 1 | of the hundred, mark the twenty-four ever made |
    | `Design_Space_Transition_Narrowed.svg` | 2 | drop the row, the block and the column Campaign 2 cannot propose |
    | `Design_Space_Transition_Boundaries.svg` | 3 | one volume range per ingredient, and two more scored properties |

    States 1 and 2 are the **same figure with a different category list**: both come out of one
    `build_grid_state()`, and the cell pitch, the origin and the dial strip are computed from
    Campaign 1's full 5 x 20 field in both. So state 2's cells sit exactly where state 1 left
    them and the two exports lay over each other in PowerPoint without a mark moving — the row,
    the block and the column simply go.

    This is `Design_Space/Design_Space_Expansion.svg`'s field, deliberately. Slide two of Act 1
    already taught the reader that grid; re-teaching it in a new geometry to make a *different*
    point would spend the slide on the frame rather than on the change.

    ## What each state claims, and where it comes from

    ### State 1 — twenty-four of a hundred

    Table 1's space is 5 oils x 4 surfactants x 5 cosurfactants = **100 declared systems**.
    Campaign 1 measured **24** of them: the Box-Behnken system, the `Misc*` repeat, ten from the
    quasi-random screen, and the fifteen the optimiser proposed across batches A-E. The set is
    read out of `data/`, not listed here, so it cannot drift from the file.

    Explored is *measured*, not *proposed and liked*: every row the campaign holds counts, a
    phase separation as much as a champion. The slide is about reach, not about success.

    ### State 2 — forty-eight of the twenty-four's neighbourhood

    Campaign 2's proposal mesh is `mesh_categories` in upstream's
    `BayesianOptimization/applications.py`: 4 oils x 3 surfactants x 4 cosurfactants = **48**.
    Against Campaign 1's lists it drops exactly three names, one per role:

    | role | dropped | why, as far as the record shows |
    | --- | --- | --- |
    | Oil | Oleic acid | 8 formulations, 3 of them separated, best rank 26 of 53 |
    | Surfactant | PEG 400 | it is also a cosurfactant candidate — the role duplication goes |
    | Cosurfactant | Tween 80 | likewise; it is also a surfactant candidate |

    **Nothing on the mesh is unmeasured.** For all three roles `mesh - measured` is empty: the
    optimiser proposes only from ingredients Campaign 1 had already put in a vial. The five
    ingredients Campaign 2 *declares* but never meshes — Kolliphor RH 40, Pluronic F-68,
    Glycerin, Cremophor EL, Safflower oil — have zero rows in every dataset in either repo, so
    they are additions to the vocabulary rather than incumbents that were cut.

    Of the 24 explored systems, **19 survive** into the narrowed field and **5 fall outside it**
    — and all five fall outside because of one of those three dropped names. The suite asserts
    that, because it is the state's whole reading: the cut lands on the vocabulary, not on the
    evidence.

    ### State 3 — the dials and the score

    Two panels, and both are transcriptions rather than restatements:

    - **Volumes** come from upstream's `oil_v_ranges`, `surfactant_v_ranges` and
      `cosurfactant_v_ranges`. Campaign 1 ran three dials over one shared oil range with
      surfactant and cosurfactant *coupled* (`Surfactant_V + Cosurfactant_V = 40.0` in every
      Campaign 1 row, which is why Table 1 writes an S<sub>mix</sub> **ratio**). Campaign 2 gives
      each of the eleven mesh ingredients its own interval and lets the two volumes move
      independently, so three continuous dials become four.
    - **The score** comes from `Figures/objectives.py`. The weights are *parsed out of the
      returned column names* (`'size_score (w=3)'`), never typed here, so a change to either
      objective moves this panel rather than contradicting it.

    The honest reading of the volume panel is not "wider". Campaign 2's oil floor drops from
    7.5 % to 5 %, but its per-oil ceiling is **15 % or 10 %**, well under Table 1's 22.5 %. What
    grew is the number of independent knobs and the specificity of each one, not the envelope.

    ## Colour

    | token | hex | what it means here |
    | --- | --- | --- |
    | `SPACE_COLOR` | `#2067F4` | Campaign 1 — the declared field, and its three dials |
    | `NEW_COLOR` | `#5A2E8C` | Campaign 2 — the systems it inherits, the ranges and scores it adds |

    Both hues are borrowed, and both borrowings need saying out loud.

    `#2067F4` is batch C's step on the Campaign 1 blue ramp elsewhere in the deck. **There are no
    batches on this slide** — nothing here is a campaign result — so the ramp is not in play and
    the blue carries the meaning the README gives the family as a whole. That is the same licence
    `Design_Space` already runs under.

    `#5A2E8C` is the **A190 track's darkest step** on the Campaign 2 board. Here it means
    Campaign 2 as a whole, which on a slide that draws either track would be wrong. This slide
    draws neither: it is the space before the two tracks split, and no green appears anywhere on
    it, so the hue cannot be read as "A190 rather than fenofibrate". `Design_Space_Growth/` took
    the other way out of the same problem and drew Campaign 2 in ink; this suite takes the hue
    because the deck asked for a colour that carries across three states, and ink already belongs
    to the grid's labels.

    ## Environment

    A [marimo](https://marimo.io) notebook, so it is a plain Python module and the interpreter that
    launches it *is* the kernel. Run it from the **`BatchedBayes`** conda environment:

    ```
    conda run -n BatchedBayes marimo edit Figures/Design_Space_Transition/Design_Space_Transition_Figures.py
    conda run -n BatchedBayes python Figures/Design_Space_Transition/Design_Space_Transition_Figures.py
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
    return Path, go, pd, sys


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Paths, canvas and export

    `REPO_ROOT` is found by looking for `Figures/objectives.py` above this file rather than by
    counting `..`, so the suite survives being moved and fails loudly rather than silently reading
    the wrong tree. The canvas is the house 1280 x 720.
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Design_Space_Transition' / 'Output'
    C1_CSV = REPO_ROOT / 'data' / 'MicroemulsionFormulation_Comprehensive.csv'

    # objectives.py is the single source of both objectives; never restate a formula here.
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
        C1_CSV,
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

    House style, value for value with `Design_Space/`: white ground, a 2 px black mirrored axis
    box where an axis is visible at all, no gridlines, five type sizes (20 / 18 / 18 / 14 / 14),
    a centred title, a horizontal legend in a bottom gutter.

    ### Pixel-grid panels

    Every panel in this suite is a schematic, so all of them sit on `pixel_axes()`: hidden axes
    whose range spans exactly as many data units as the domain spans exported pixels, origin top
    left. One data unit is one pixel, so a cell asked to be square is square whatever domain it is
    given, and a 3 px rule is 3 px on the slide.

    `pixel_axes()` takes an `anchor`. Plotly anchors every axis after the first to `x` / `y` by
    default, which would draw a third pair's box and ticks across the whole canvas rather than
    inside its own domain. It costs nothing while both pairs are invisible — which is why
    `Design_Space/` never had to pass it — but state 3 has a visible scale, so the argument is
    here from the start rather than added the first time something goes wrong.
    """)
    return


@app.cell
def _(FIG_HEIGHT, FIG_WIDTH, go):
    SPACE_COLOR = '#2067F4'   # blue    -- Campaign 1: the declared field and its three dials
    NEW_COLOR = '#5A2E8C'     # purple  -- Campaign 2: what it inherits, and what it adds
    DOE_COLOR = '#E69F00'     # orange  -- the Box-Behnken design and its three stops per dial

    INK = 'black'
    # Subtitles only. Everything that labels the geometry -- heads, row names, tick values --
    # is full black, because on a projector a grey label reads as washed out rather than as
    # quieter. A subtitle is prose under a title, and there the step down still does its job.
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'

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

    # suffix -> (body face, heading face, tick face). '' is the default export, and it must
    # stay first: it is the one that survives being opened on a machine without the two faces.
    FONT_SCHEMES = {
        '': (FONT_FAMILY, FONT_FAMILY, FONT_FAMILY),
        '_Pretendard': (BODY_FAMILY, HEADING_FAMILY, HEADING_FAMILY),
    }

    # Sizes do NOT change between schemes. The house 20/18/18/14/14 is the same in both, so the
    # two exports are drop-in swaps for each other and a slide can be re-fonted without
    # re-checking that anything still fits.

    MARKER_SIZE = 13
    FRAME_WIDTH = 2
    # The 5 x 20 field's cell edge, matched to Design_Space_Expansion so the two slides read as
    # the same grid. Full strength rather than a wash: the grid *is* the reachable space.
    CELL_EDGE = 3.2

    LEGEND_MARGIN = 96   # bottom gutter the horizontal legend sits in


    def fade(hex_color, alpha):
        """Convert '#RRGGBB' to an rgba() string at the given alpha."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return 'rgba({}, {}, {}, {})'.format(r, g, b, alpha)


    def pretty(name):
        """'Capmul_MCM' -> 'Capmul MCM'. The CSVs and upstream both spell names with underscores."""
        return name.replace('_', ' ')


    def with_font_scheme(fig, body, heading, tick):
        """A copy of `fig` re-fonted: `heading` on the title and axes, `body` on everything else.

        Applied after a figure is built rather than threaded through the builders, so the two
        exports cannot drift: there is one figure, drawn once, wearing two type schemes. Heading
        text is tagged where it is written with `name='heading'`; everything else is body by
        definition, which is the safe default -- a new annotation joins the reading face rather
        than silently claiming to be a title.
        """
        out = go.Figure(fig.to_dict())
        out.layout.font.family = body
        out.layout.title.font.family = heading
        out.layout.legend.font.family = body
        for _ann in out.layout.annotations:
            _ann.font.family = heading if _ann.name == 'heading' else body
        for _axis in list(out.select_xaxes()) + list(out.select_yaxes()):
            _axis.tickfont.family = tick
            _axis.title.font.family = heading
        return out


    # An axis domain is a fraction of the *plot area*, not of the canvas, so pixel_axes() is
    # only truthful if it knows the margins. Every layout below reads this one dict, so the
    # panels and their pixel axes cannot disagree.
    SCHEMATIC_MARGIN = dict(l=10, r=10, t=96, b=LEGEND_MARGIN)


    def pixel_axes(x_domain, y_domain, anchor=('x', 'y'), margin=SCHEMATIC_MARGIN):
        """Axis pair whose data units are exported pixels, origin top left.

        The range spans exactly as many units as the domain spans pixels of the plot area --
        the 1280 x 720 canvas less `margin` -- so a schematic drawn in these coordinates keeps
        its proportions and its stroke weights whatever domain it is given.

        `anchor` is the (x, y) pair this axis pair anchors against. Plotly defaults every axis
        after the first to 'x' / 'y', which puts a later pair's box and ticks on the first
        pair's domain instead of its own.
        """
        plot_w = FIG_WIDTH - margin['l'] - margin['r']
        plot_h = FIG_HEIGHT - margin['t'] - margin['b']
        width = (x_domain[1] - x_domain[0]) * plot_w
        height = (y_domain[1] - y_domain[0]) * plot_h
        x_axis = dict(domain=list(x_domain), range=[0, width], visible=False,
                      fixedrange=True, anchor=anchor[1])
        y_axis = dict(domain=list(y_domain), range=[height, 0], visible=False,
                      fixedrange=True, anchor=anchor[0])
        return x_axis, y_axis, width, height
    return (
        ANNOTATION_SIZE,
        CELL_EDGE,
        DOE_COLOR,
        FONT_FAMILY,
        FONT_SCHEMES,
        INK,
        INK_SOFT,
        LEGEND_SIZE,
        MARKER_SIZE,
        NEW_COLOR,
        SCHEMATIC_MARGIN,
        SPACE_COLOR,
        TITLE_SIZE,
        fade,
        pixel_axes,
        pretty,
        with_font_scheme,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The two spaces

    Campaign 1's lists are the paper's **Table 1**, stated once. Campaign 2's are transcribed from
    upstream `BayesianOptimization/applications.py` at `c4d3398` — `mesh_categories`,
    `oil_v_ranges`, `surfactant_v_ranges`, `cosurfactant_v_ranges` — because the optimiser does not
    live in this repo and nothing here imports it. Transcription is the exposure: the cell below
    checks every transcribed name and bound against `data/`, so a drift upstream shows up as a
    failed assertion rather than as a wrong slide.

    `EXPLORED` is **read**, never listed: the distinct `(Oil, Surfactant, Cosurfactant)` triples of
    every Campaign 1 row in `MicroemulsionFormulation_Comprehensive.csv`. Campaign 2's own batches
    carry an `A-` / `F-` prefix on `Exp` and are excluded; the six `_A` / `_F` revalidation runs are
    Campaign 1 formulations remade with an API, so they stay in and, as it happens, add no system
    the plain rows do not already have.

    The counts the states rest on — 100 declared, 24 explored, 48 meshed, 19 surviving, 5 lost —
    are all derived here and asserted, so no number is typed into a figure.
    """)
    return


@app.cell
def _(C1_CSV, pd, pretty):
    # --- Campaign 1: the paper's Table 1, the authoritative design space ------------------
    # Order is the grid's order, and Design_Space_Expansion's: it is what makes the two slides
    # read as the same field.
    C1_OILS = ['Oleic Acid', 'Capryol 90', 'Soybean Oil', 'Maisine Oil', 'Capmul MCM']
    C1_SURFACTANTS = ['PEG 400', 'Tween 80', 'Tween 20', 'Labrasol']
    C1_COSURFACTANTS = ['Tween 80', 'Transcutol HP', 'Propylene Glycol', 'Ethanol', 'PEG 400']

    C1_OIL_V_RANGE = (7.5, 22.5)
    C1_SONICATION_RANGE = (0.0, 3.0)
    # Low to high as Table 1 writes the range, '3:1--1:3': the low end is surfactant-heavy.
    C1_SMIX_RATIO_LABELS = ('3:1', '1:1', '1:3')
    # Campaign 1's one coupling, and the reason Table 1 can write a ratio at all.
    C1_SMIX_TOTAL = 40.0

    # Display-only column heads for the 5 x 20 field: twenty columns leave about 56 px each, and
    # 'Propylene Glycol' set diagonally still overruns its neighbours at that pitch. Asserted
    # against C1_COSURFACTANTS below, so a rename fails loudly rather than mislabelling a column.
    COSURF_SHORT = {
        'Tween 80': 'Tween 80',
        'Transcutol HP': 'Transcutol',
        'Propylene Glycol': 'Prop. glycol',
        'Ethanol': 'Ethanol',
        'PEG 400': 'PEG 400',
    }

    # --- Campaign 2: upstream applications.py at c4d3398 ----------------------------------
    # mesh_categories -- what the optimiser may actually propose. category_values is wider
    # (6 / 7 / 7) but five of those names have zero rows anywhere, so they are vocabulary
    # rather than space and this slide does not draw them.
    C2_MESH_CATEGORIES = {
        'Oil': ['Capmul_MCM', 'Capryol_90', 'Maisine_Oil', 'Soybean_Oil'],
        'Surfactant': ['Labrasol', 'Tween_20', 'Tween_80'],
        'Cosurfactant': ['Ethanol', 'PEG_400', 'Propylene_Glycol', 'Transcutol_HP'],
    }
    # Per-ingredient volume ranges, % v/v. Campaign 1 had one oil range for all five oils and no
    # per-ingredient surfactant or cosurfactant range at all.
    C2_OIL_V_RANGES = {
        'Capmul_MCM': (5.0, 15.0), 'Capryol_90': (5.0, 15.0),
        'Maisine_Oil': (5.0, 10.0), 'Soybean_Oil': (5.0, 10.0),
    }
    C2_SURF_V_RANGES = {
        'Labrasol': (20.0, 40.0), 'Tween_20': (20.0, 40.0), 'Tween_80': (20.0, 40.0),
    }
    C2_COSURF_V_RANGES = {
        'Ethanol': (5.0, 15.0), 'PEG_400': (5.0, 20.0),
        'Propylene_Glycol': (5.0, 15.0), 'Transcutol_HP': (10.0, 20.0),
    }
    C2_V_RANGES = {'Oil': C2_OIL_V_RANGES, 'Surfactant': C2_SURF_V_RANGES,
                   'Cosurfactant': C2_COSURF_V_RANGES}
    C2_SONICATION_RANGE = (0.0, 3.0)

    ROLES = ('Oil', 'Surfactant', 'Cosurfactant')

    # --- what Campaign 1 actually made ----------------------------------------------------
    _raw = pd.read_csv(C1_CSV)
    _is_c2 = _raw['Exp'].astype(str).str.match(r'^[AF]-')
    C1_ROWS = _raw[~_is_c2].copy()
    C2_ROWS = _raw[_is_c2].copy()

    EXPLORED = {
        (pretty(_o), pretty(_s), pretty(_c))
        for _o, _s, _c in C1_ROWS[['Oil', 'Surfactant', 'Cosurfactant']].itertuples(index=False)
    }

    C2_LISTS = {_r: [pretty(_n) for _n in C2_MESH_CATEGORIES[_r]] for _r in ROLES}
    C1_LISTS = {'Oil': C1_OILS, 'Surfactant': C1_SURFACTANTS, 'Cosurfactant': C1_COSURFACTANTS}

    def in_mesh(system):
        oil, surf, cosurf = system
        return (oil in C2_LISTS['Oil'] and surf in C2_LISTS['Surfactant']
                and cosurf in C2_LISTS['Cosurfactant'])

    SURVIVING = {_t for _t in EXPLORED if in_mesh(_t)}
    LOST = EXPLORED - SURVIVING
    DROPPED = {_r: [_n for _n in C1_LISTS[_r] if _n not in C2_LISTS[_r]] for _r in ROLES}

    N_DECLARED = len(C1_OILS) * len(C1_SURFACTANTS) * len(C1_COSURFACTANTS)
    N_MESH = len(C2_LISTS['Oil']) * len(C2_LISTS['Surfactant']) * len(C2_LISTS['Cosurfactant'])

    # --- assertions: every claim the three states make --------------------------------------
    assert set(COSURF_SHORT) == set(C1_COSURFACTANTS), \
        'COSURF_SHORT does not cover Table 1 cosurfactants'
    assert N_DECLARED == 100, 'Table 1 declares 5 x 4 x 5 = 100 systems'
    assert N_MESH == 48, 'mesh_categories is 4 x 3 x 4 = 48 systems'

    # The mesh is a *subset* of Table 1's lists, one name lighter in each role. If upstream ever
    # meshes a name Table 1 never listed, state 2 stops being a narrowing and this fails.
    for _role in ROLES:
        assert set(C2_LISTS[_role]) <= set(C1_LISTS[_role]), \
            '{}: mesh has names Table 1 does not list: {}'.format(
                _role, sorted(set(C2_LISTS[_role]) - set(C1_LISTS[_role])))
        assert len(DROPPED[_role]) == 1, \
            '{}: expected exactly one dropped name, found {}'.format(_role, DROPPED[_role])

    # Nothing on the mesh is unmeasured: the optimiser proposes only from ingredients Campaign 1
    # had already put in a vial. This is the strongest claim on the slide, so it is checked.
    for _role, _col in zip(ROLES, ('Oil', 'Surfactant', 'Cosurfactant')):
        _measured = {pretty(_n) for _n in C1_ROWS[_col].unique()}
        assert set(C2_LISTS[_role]) <= _measured, \
            '{}: mesh contains names Campaign 1 never measured: {}'.format(
                _role, sorted(set(C2_LISTS[_role]) - _measured))

    # Every explored system that falls out of state 2 does so because of one of the three
    # dropped names -- the cut lands on the vocabulary, not on the evidence.
    for _sys in LOST:
        assert any(_sys[_i] in DROPPED[_role] for _i, _role in enumerate(ROLES)), \
            '{} left the mesh for a reason the slide does not draw'.format(_sys)

    assert EXPLORED <= {(_o, _s, _c) for _o in C1_OILS
                        for _s in C1_SURFACTANTS for _c in C1_COSURFACTANTS}, \
        'data/ holds a Campaign 1 system that is not a cell of the Table 1 grid'

    # Campaign 1's Smix coupling, which is what makes its two volumes one dial. Campaign 2's own
    # rows break it, which is what makes them two.
    assert (C1_ROWS['Surfactant_V'] + C1_ROWS['Cosurfactant_V'] == C1_SMIX_TOTAL).all(), \
        'a Campaign 1 row does not have Surfactant_V + Cosurfactant_V = {}'.format(C1_SMIX_TOTAL)
    assert not (C2_ROWS['Surfactant_V'] + C2_ROWS['Cosurfactant_V'] == C1_SMIX_TOTAL).all(), \
        'Campaign 2 rows still satisfy the Smix coupling -- state 3 has nothing to show'

    # The per-ingredient bounds, against the rows Campaign 2 actually ran.
    for _role, _col in zip(ROLES, ('Oil_V', 'Surfactant_V', 'Cosurfactant_V')):
        for _name, (_lo, _hi) in C2_V_RANGES[_role].items():
            _sel = C2_ROWS[C2_ROWS[_role] == _name][_col]
            assert _sel.between(_lo, _hi).all(), \
                '{} {}: rows outside the transcribed bound {}-{}'.format(
                    _role, _name, _lo, _hi)

    print('declared  {}'.format(N_DECLARED))
    print('explored  {}'.format(len(EXPLORED)))
    print('meshed    {}'.format(N_MESH))
    print('surviving {}   lost {}'.format(len(SURVIVING), len(LOST)))
    print('dropped   {}'.format({_k: _v[0] for _k, _v in DROPPED.items()}))
    return (
        C1_COSURFACTANTS,
        C1_LISTS,
        C1_OILS,
        C1_OIL_V_RANGE,
        C1_SMIX_RATIO_LABELS,
        C1_SMIX_TOTAL,
        C1_SONICATION_RANGE,
        C1_SURFACTANTS,
        C2_LISTS,
        C2_SONICATION_RANGE,
        C2_V_RANGES,
        COSURF_SHORT,
        DROPPED,
        EXPLORED,
        LOST,
        N_DECLARED,
        N_MESH,
        ROLES,
        SURVIVING,
        C1_ROWS,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## States 1 and 2 — the field, and the field narrowed

    One builder, two calls. `build_grid_state()` takes the three category lists it should *draw*
    and computes every coordinate from Campaign 1's full lists, so state 2's surviving cells sit
    on state 1's pixels exactly. Passing Campaign 1's own lists gives state 1; passing Campaign 2's
    mesh gives state 2, with the dropped row, block and column absent rather than moved.

    Everything below the grid is identical in both states on purpose. The dial strip is Campaign
    1's three settings in both, because the settings do not change until state 3 — a strip that
    also moved would give the reader two things to track in one step.

    **The strip is measured off the grid above it**, not off its own axis: the two share a paper
    domain, so equal data values land on equal exported pixels. Oil Volume opens on the leftmost
    cell's left edge and Sonication closes on the rightmost cell's right edge, so the strip is
    visibly as wide as the space it describes.

    Two details are inherited from `Design_Space_Expansion` and are measured constants, not
    formulas — re-measure them if `HEAD_SIZE` moves. `HEAD_DX` / `HEAD_DY` absorb the padding a
    -45 degree rotation lifts up and to the right of a text box's anchor, so the head's *first*
    letter centres on its column; `_HEAD_RULE` sets the gap above the rotated heads equal to the
    gap below them.

    The three band tags — Oil, Surfactant, Cosurfactant — are in soft ink a size down: they
    describe a band of names rather than being a name in it.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    C1_COSURFACTANTS,
    C1_OILS,
    C1_OIL_V_RANGE,
    C1_SMIX_RATIO_LABELS,
    C1_SONICATION_RANGE,
    C1_SURFACTANTS,
    CELL_EDGE,
    COSURF_SHORT,
    DOE_COLOR,
    EXPLORED,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEGEND_SIZE,
    MARKER_SIZE,
    NEW_COLOR,
    SCHEMATIC_MARGIN,
    SPACE_COLOR,
    TITLE_SIZE,
    fade,
    go,
    pixel_axes,
):
    # Header zone of the grid panel, top to bottom: the block rule and its surfactant name, then
    # the rotated cosurfactant heads rising off the top of the cells. GRID_TOP is where the cells
    # begin. All four are Design_Space_Expansion's, so the two slides draw one field.
    GRID_LEFT, GRID_TOP = 112.0, 96.0
    HEAD_RULE = 13.0
    HEAD_SIZE = ANNOTATION_SIZE - 1   # the row labels' size: both name a grid edge
    HEAD_DX = 15.5   # px left of the column centre, so the FIRST letter centres on it
    HEAD_DY = -4.0   # px from the cell top; negative lifts the heads clear of the block
    CELL_PAD = 4.5
    TAG_SIZE = ANNOTATION_SIZE - 2
    COS_TAG_OFF = 3.0
    COS_TAG_DX = 17.0


    def build_grid_state(oils, surfactants, cosurfactants, title, subtitle):
        """The 5 x 20 field, drawing only the categories given, on Campaign 1's full geometry.

        `oils` / `surfactants` / `cosurfactants` are the lists to *draw*; the cell pitch, the
        origin and the dial strip are computed from Campaign 1's full lists whatever is passed,
        which is what lets the two states lay over each other unmoved.
        """
        _traces, _annotations, _shapes = [], [], []

        _grid_x, _grid_y, _gw, _gh = pixel_axes((0.015, 0.985), (0.250, 1.000))
        _pairs = [(s, c) for s in C1_SURFACTANTS for c in C1_COSURFACTANTS]
        _n_col, _n_row = len(_pairs), len(C1_OILS)

        # Cells are SQUARE. One number for width and height, the smaller of what each direction
        # can spare, so a hundred equal slots read as a hundred equal slots. Twenty columns
        # against five rows means width binds on the 1280 canvas; the block is centred in the
        # space the squares do not fill.
        _cell = min((_gw - GRID_LEFT - 4.0) / _n_col, (_gh - GRID_TOP - 6.0) / _n_row)
        _x_off = (_gw - (GRID_LEFT + _n_col * _cell)) / 2.0
        _y_off = (_gh - (GRID_TOP + _n_row * _cell)) / 2.0

        _drawn = 0
        for _r, _oil in enumerate(C1_OILS):
            if _oil not in oils:
                continue
            for _c, (_s, _cs) in enumerate(_pairs):
                if _s not in surfactants or _cs not in cosurfactants:
                    continue
                _drawn += 1
                _x0 = _x_off + GRID_LEFT + _c * _cell
                _y0 = _y_off + GRID_TOP + _r * _cell
                _made = (_oil, _s, _cs) in EXPLORED
                _shapes.append(dict(
                    type='rect', xref='x', yref='y',
                    x0=_x0 + CELL_PAD, x1=_x0 + _cell - CELL_PAD,
                    y0=_y0 + CELL_PAD, y1=_y0 + _cell - CELL_PAD,
                    fillcolor=fade(NEW_COLOR, 0.35) if _made else fade(SPACE_COLOR, 0.11),
                    line=dict(color=NEW_COLOR if _made else SPACE_COLOR, width=CELL_EDGE),
                    layer='below'))
        assert _drawn == len(oils) * len(surfactants) * len(cosurfactants), \
            'drew {} cells for a {} x {} x {} space'.format(
                _drawn, len(oils), len(surfactants), len(cosurfactants))

        # Column heads: the surfactant blocks spelled out, the cosurfactant columns abbreviated.
        # A block whose surfactant is not drawn loses its rule, its name and its five heads --
        # the whole block goes, not just its cells.
        for _si, _s in enumerate(C1_SURFACTANTS):
            if _s not in surfactants:
                continue
            _bx0 = _x_off + GRID_LEFT + _si * len(C1_COSURFACTANTS) * _cell
            _live = [_c for _c in C1_COSURFACTANTS if _c in cosurfactants]
            # The rule spans the columns that survive, not the block's original five, so it
            # cannot overhang a gap where a dropped column used to be.
            _first = C1_COSURFACTANTS.index(_live[0])
            _last = C1_COSURFACTANTS.index(_live[-1])
            _shapes.append(dict(
                type='line', xref='x', yref='y',
                x0=_bx0 + _first * _cell + CELL_PAD, x1=_bx0 + (_last + 1) * _cell - CELL_PAD,
                y0=_y_off + HEAD_RULE, y1=_y_off + HEAD_RULE,
                line=dict(color=INK, width=1.4)))
            _annotations.append(dict(
                xref='x', yref='y',
                x=_bx0 + ((_first + _last + 1) / 2.0) * _cell, y=_y_off + HEAD_RULE - 6,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=INK), text=_s))
            for _ci, _c in enumerate(C1_COSURFACTANTS):
                if _c not in cosurfactants:
                    continue
                # -45, not -90: a diagonal head is read at a glance where an upright one has to
                # be tilted into. xanchor='left' anchors the text's START and plotly rotates
                # about the anchor, so the first letter sits over the column and the name runs
                # up and away to the right.
                _annotations.append(dict(
                    xref='x', yref='y',
                    x=_bx0 + (_ci + 0.5) * _cell - HEAD_DX,
                    y=_y_off + GRID_TOP + HEAD_DY,
                    xanchor='left', yanchor='bottom', showarrow=False, textangle=-45,
                    font=dict(size=HEAD_SIZE, color=INK), text=COSURF_SHORT[_c]))
        for _r, _oil in enumerate(C1_OILS):
            if _oil not in oils:
                continue
            _annotations.append(dict(
                xref='x', yref='y', x=_x_off + GRID_LEFT - 10,
                y=_y_off + GRID_TOP + (_r + 0.5) * _cell,
                xanchor='right', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=INK), text=_oil))

        # Which list is which. Three bands of names and nothing says an oil from a surfactant,
        # so each band is tagged in soft ink a size down -- a descriptor of the band, not an
        # entry in it. All three are pinned to the FIRST surviving name of their band, so they
        # move with the field rather than hanging over a gap.
        _first_surf = next(_i for _i, _s in enumerate(C1_SURFACTANTS) if _s in surfactants)
        _first_cos = next(_i for _i, _c in enumerate(C1_COSURFACTANTS) if _c in cosurfactants)
        _first_oil = next(_i for _i, _o in enumerate(C1_OILS) if _o in oils)
        _last_oil = max(_i for _i, _o in enumerate(C1_OILS) if _o in oils)
        # Set to the LEFT of the first rule rather than on its left end. On the full field the
        # block name is centred over five columns and there is room for both; once a block loses
        # columns its name slides left onto exactly that spot, so the tag sits clear in the
        # gutter above the oil names, where nothing else is drawn in either state.
        _annotations.append(dict(
            xref='x', yref='y',
            x=_x_off + GRID_LEFT + _first_surf * len(C1_COSURFACTANTS) * _cell
              + _first_cos * _cell + CELL_PAD - 8,
            y=_y_off + HEAD_RULE - 6,
            xanchor='right', yanchor='bottom', showarrow=False,
            font=dict(size=TAG_SIZE, color=INK_SOFT), text='Surfactant'))
        # Cosurfactant is set at the heads' own -45 and placed ON the first head's line, not
        # beside it: equal steps left and down walk back along the diagonal, and anchoring the
        # text's END there runs the tag away down-left, so the two read as one line whose tail
        # names what the rest of it lists.
        _annotations.append(dict(
            xref='x', yref='y',
            x=_x_off + GRID_LEFT + _first_surf * len(C1_COSURFACTANTS) * _cell
              + (_first_cos + 0.5) * _cell - HEAD_DX - COS_TAG_OFF + COS_TAG_DX,
            y=_y_off + GRID_TOP + HEAD_DY + COS_TAG_OFF,
            xanchor='right', yanchor='bottom', showarrow=False, textangle=-45,
            font=dict(size=TAG_SIZE, color=INK_SOFT), text='Cosurfactant'))
        _annotations.append(dict(
            xref='x', yref='y', x=_x_off + 10,
            y=_y_off + GRID_TOP + (_first_oil + _last_oil + 1) / 2.0 * _cell,
            xanchor='center', yanchor='middle', showarrow=False, textangle=-90,
            font=dict(size=TAG_SIZE, color=INK_SOFT), text='Oil'))

        # ---- bottom: the three settings, twice each -------------------------------------
        # Design_Space_Expansion's strip, kept whole: the Box-Behnken design's three stops, and
        # Campaign 1's continuous range beneath them. Table 1 did not widen the dials -- it
        # removed the stops between them, and that reading is only available if both rows are
        # drawn.
        #
        # Identical in both states. The settings do not change until state 3, and a strip that
        # moved under a narrowing grid would give the reader two things to track in one step.
        _dial_x, _dial_y, _dw, _dh = pixel_axes(
            (0.015, 0.985), (0.000, 0.215), anchor=('x2', 'y2'))
        _dials = [
            ('Oil Volume', ['{:g} %'.format(C1_OIL_V_RANGE[0]),
                            '{:g} %'.format(sum(C1_OIL_V_RANGE) / 2),
                            '{:g} %'.format(C1_OIL_V_RANGE[1])]),
            ('S<sub>mix</sub> Ratio', list(C1_SMIX_RATIO_LABELS)),
            ('Sonication', ['{:g} min'.format(C1_SONICATION_RANGE[0]),
                            '{:g}'.format(sum(C1_SONICATION_RANGE) / 2),
                            '{:g} min'.format(C1_SONICATION_RANGE[1])]),
        ]
        # Measured off the grid above it, not off its own axis: the two axes share a paper
        # domain, so a cell edge and a track end at the same data value land on the same
        # exported pixel. Only the two gaps between tracks are free.
        _dial_x0 = _x_off + GRID_LEFT + CELL_PAD
        _dial_x1 = _x_off + GRID_LEFT + _n_col * _cell - CELL_PAD
        _dial_gap = 56.0
        _track_w = (_dial_x1 - _dial_x0 - 2 * _dial_gap) / 3.0
        _legend_x = None
        for _di, (_name, _ticks) in enumerate(_dials):
            _tx0 = _dial_x0 + _di * (_track_w + _dial_gap)
            if _name.startswith('S<sub>mix</sub>'):
                # Paper x of this track's centre, so the legend hangs under the middle dial
                # rather than under the canvas.
                _legend_x = (_dial_x['domain'][0]
                             + (_tx0 + _track_w / 2.0) / _dw
                             * (_dial_x['domain'][1] - _dial_x['domain'][0]))
            # Two rows per dial: the design's stops at _y_stop, the campaign's range at
            # _y_range. Both measured off Design_Space_Expansion, so the two slides' strips
            # sit on the same pixels.
            _y_stop, _y_range = 44.0, 78.0
            _annotations.append(dict(
                xref='x2', yref='y2', x=_tx0 + _track_w / 2.0, y=_y_stop - 20,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE, color=INK), text='<b>{}</b>'.format(_name)))
            # The design's three levels: low, centre, high. The rail is faded so the three
            # stops read as the mark and the line only as what joins them.
            _shapes.append(dict(type='line', xref='x2', yref='y2',
                                x0=_tx0, x1=_tx0 + _track_w, y0=_y_stop, y1=_y_stop,
                                line=dict(color=fade(DOE_COLOR, 0.45), width=1.4)))
            _traces.append(go.Scatter(
                x=[_tx0, _tx0 + _track_w / 2.0, _tx0 + _track_w],
                y=[_y_stop] * 3, xaxis='x2', yaxis='y2', mode='markers',
                hoverinfo='skip', showlegend=False,
                marker=dict(size=MARKER_SIZE - 2, color=DOE_COLOR,
                            line=dict(width=1.3, color=INK))))
            _shapes.append(dict(type='rect', xref='x2', yref='y2',
                                x0=_tx0, x1=_tx0 + _track_w, y0=_y_range - 9, y1=_y_range + 9,
                                fillcolor=fade(SPACE_COLOR, 0.28),
                                line=dict(color=SPACE_COLOR, width=1.6)))
            for _ti, _t in enumerate(_ticks):
                _annotations.append(dict(
                    xref='x2', yref='y2', x=_tx0 + (_ti / 2.0) * _track_w, y=_y_range + 18,
                    xanchor='center', yanchor='top', showarrow=False,
                    font=dict(size=ANNOTATION_SIZE - 3, color=INK), text=_t))

        # ---- legend proxies -------------------------------------------------------------
        # The same three entries in both states, in the same order, so the legend does not jump
        # between exports. Box-Behnken leads, as it does on Design_Space_Expansion's legend --
        # the two slides sit next to each other in the deck and a reordered legend under the
        # same strip reads as a different chart. The circle names the strip's mark, the two
        # squares the grid's.
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Box-Behnken',
            marker=dict(size=MARKER_SIZE, color=DOE_COLOR, symbol='circle',
                        line=dict(width=1.4, color=INK))))
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Possible',
            marker=dict(size=MARKER_SIZE, color=fade(SPACE_COLOR, 0.11), symbol='square',
                        line=dict(width=1.4, color=SPACE_COLOR))))
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Explored',
            marker=dict(size=MARKER_SIZE, color=fade(NEW_COLOR, 0.35), symbol='square',
                        line=dict(width=1.4, color=NEW_COLOR))))

        _annotations += [
            # Both live in the top margin, not in the plot area: the grid runs to the very top
            # of its axis, and a subtitle at paper 0.955 would land on the block rules.
            dict(xref='paper', yref='paper', x=0.5, y=1.100, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK), name='heading',
                 text='<b>{}</b>'.format(title)),
            dict(xref='paper', yref='paper', x=0.5, y=1.045, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text=subtitle),
        ]

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=SCHEMATIC_MARGIN,
            xaxis=_grid_x, yaxis=_grid_y,
            xaxis2=_dial_x, yaxis2=_dial_y,
            shapes=_shapes, annotations=_annotations,
            legend=dict(orientation='h', xanchor='center', x=_legend_x, yanchor='top', y=-0.02,
                        font=dict(size=LEGEND_SIZE), itemsizing='constant',
                        bgcolor='rgba(0,0,0,0)'),
        )
        return go.Figure(data=_traces, layout=_layout)
    return (build_grid_state,)


@app.cell
def _(
    C1_COSURFACTANTS,
    C1_OILS,
    C1_SURFACTANTS,
    EXPLORED,
    N_DECLARED,
    build_grid_state,
):
    explored_figure = build_grid_state(
        C1_OILS, C1_SURFACTANTS, C1_COSURFACTANTS,
        'Which of the hundred did Campaign 1 ever make?',
        'Table 1 declares {} systems; the campaign measured {}'.format(
            N_DECLARED, len(EXPLORED)),
    )
    explored_figure
    return (explored_figure,)


@app.cell
def _(C2_LISTS, DROPPED, EXPLORED, LOST, N_MESH, ROLES, build_grid_state):
    narrowed_figure = build_grid_state(
        C2_LISTS['Oil'], C2_LISTS['Surfactant'], C2_LISTS['Cosurfactant'],
        'Which of them can Campaign 2 propose?',
        'One name goes from each role — {} — leaving {} systems and {} of the {} '
        'already made'.format(
            ', '.join(DROPPED[_r][0] for _r in ROLES),
            N_MESH, len(EXPLORED) - len(LOST), len(EXPLORED)),
    )
    narrowed_figure
    return (narrowed_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## State 3 — the dials and the score

    The categorical field has done its work by now, so state 3 drops it and spends the canvas on
    the two changes that are not about *which* ingredients: what each one may be dosed at, and
    what the optimiser is scoring.

    **Left — one range per ingredient.** Campaign 1 ran a single oil range for all five oils, and
    its surfactant and cosurfactant volumes were not free at all: they summed to
    `C1_SMIX_TOTAL = 40` in every row, which is why Table 1 can write an S<sub>mix</sub> *ratio*
    and why the campaign has three continuous dials rather than four. Campaign 2 gives each of the
    eleven mesh ingredients its own interval and lets the two volumes move independently.

    Campaign 1's range is drawn as a pale band running the width of each role group, and each
    ingredient's own interval as a purple bar on top of it. The comparison the eye makes is
    therefore the right one: not "which is longer" but "how many bars are there, and do they
    agree". They do not — and Campaign 2's oil bars stop at 15 % and 10 % where Campaign 1's band
    runs to 22.5 %, so the honest word for this panel is *specific*, not *wider*.

    **Right — the score.** Six measured properties, and for each the weight the two objectives put
    on it. Weights are **parsed out of the column names** `Figures/objectives.py` returns
    (`'size_score (w=3)'`), so this panel is a view of the objective rather than a second copy of
    it. Phase separation is the one row that is not a weight in the same sense — Campaign 1 adds
    `10 x sep`, Campaign 2 divides by `1 - sep` — so it is set apart below a rule and written as
    the operator rather than as a number.

    Drug loading and permeability are the two rows Campaign 1 has no entry for at all: they are
    scored for the first time in Campaign 2, and are marked in purple with the ranges panel.

    Both panels sit on `pixel_axes()` with explicit anchors — see the chrome cell for why.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    C1_OIL_V_RANGE,
    C1_ROWS,
    C1_SMIX_TOTAL,
    C2_LISTS,
    C2_V_RANGES,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEGEND_SIZE,
    MARKER_SIZE,
    NEW_COLOR,
    ROLES,
    SCHEMATIC_MARGIN,
    SPACE_COLOR,
    TITLE_SIZE,
    campaign1,
    campaign2,
    fade,
    go,
    pixel_axes,
    pretty,
):
    def _weights(scores):
        """{'size': 3, ...} from the '<stem>_score (w=N)' column names an objective returns.

        Parsed rather than restated: objectives.py writes each weight into the name of the
        column it produces, so reading it back is the closest this suite can get to importing
        the number.
        """
        out = {}
        for _col in scores.columns:
            if '_score (w=' not in _col:
                continue
            _stem, _rest = _col.split('_score (w=')
            out[_stem] = float(_rest.rstrip(')'))
        return out


    # Called on the real rows rather than an empty frame: an objective that starts depending on
    # the data would otherwise be parsed from a shape it never sees in anger.
    C1_W = _weights(campaign1(C1_ROWS))
    C2_W = _weights(campaign2(C1_ROWS))

    # stem -> display name, in the order the panel reads them. Physicochemical first, then the
    # two Campaign 2 adds; phase separation is handled apart, below the rule.
    SCORE_ROWS = [
        ('size', 'Droplet size'),
        ('pdi', 'PDI'),
        ('zeta', 'Zeta potential'),
        ('dl', 'Drug loading'),
        ('perm', 'Permeability'),
    ]
    assert set(C1_W) | set(C2_W) == {_s for _s, _ in SCORE_ROWS} | {'sep'}, \
        'objectives.py returns a component this panel does not name: {}'.format(
            sorted((set(C1_W) | set(C2_W)) - ({_s for _s, _ in SCORE_ROWS} | {'sep'})))
    NEW_STEMS = {_s for _s, _ in SCORE_ROWS if _s not in C1_W}
    assert NEW_STEMS == {'dl', 'perm'}, \
        'expected drug loading and permeability to be the Campaign 2 additions, got {}'.format(
            sorted(NEW_STEMS))


    def build_boundaries_state():
        _traces, _annotations, _shapes = [], [], []

        # ---- left: one volume range per ingredient --------------------------------------
        _vx, _vy, _vw, _vh = pixel_axes((0.015, 0.575), (0.000, 1.000))

        # A shared % scale for all three role groups, so a bar's length means the same thing
        # wherever it sits. Rounded out from the widest bound either campaign declares.
        _SCALE_MAX = 45.0
        _LABEL_W = 132.0
        _sx0, _sx1 = _LABEL_W, _vw - 14.0

        def _at(value, x0=_sx0, x1=_sx1, top=_SCALE_MAX):
            return x0 + (value / top) * (x1 - x0)

        # Campaign 1's band per role. Oil is Table 1's one range for all five oils; the two Smix
        # volumes are not free -- they run 10..30 *coupled*, which the note under the group says.
        _c1_band = {
            'Oil': C1_OIL_V_RANGE,
            'Surfactant': (C1_SMIX_TOTAL / 4.0, 3.0 * C1_SMIX_TOTAL / 4.0),
            'Cosurfactant': (C1_SMIX_TOTAL / 4.0, 3.0 * C1_SMIX_TOTAL / 4.0),
        }
        _c1_note = {
            'Oil': 'one range, all five oils',
            'Surfactant': 'coupled: S + C = {:g}'.format(C1_SMIX_TOTAL),
            'Cosurfactant': 'coupled: S + C = {:g}'.format(C1_SMIX_TOTAL),
        }

        _ROW_H = 26.0
        _HEAD_H = 26.0
        _GROUP_GAP = 16.0
        _BAR_H = 11.0
        _y = 6.0
        for _role in ROLES:
            _names = C2_LISTS[_role]
            _n = len(_names)
            _group_h = _HEAD_H + (_n + 1) * _ROW_H

            _annotations.append(dict(
                xref='x', yref='y', x=0.0, y=_y + _HEAD_H - 8,
                xanchor='left', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE, color=INK), text='<b>{}</b>'.format(_role)))

            # Campaign 1's band, its own row at the top of the group.
            _by = _y + _HEAD_H + _ROW_H / 2.0
            _lo, _hi = _c1_band[_role]
            _shapes.append(dict(
                type='rect', xref='x', yref='y',
                x0=_at(_lo), x1=_at(_hi), y0=_by - _BAR_H / 2.0, y1=_by + _BAR_H / 2.0,
                fillcolor=fade(SPACE_COLOR, 0.28),
                line=dict(color=SPACE_COLOR, width=1.6)))
            _annotations.append(dict(
                xref='x', yref='y', x=_LABEL_W - 10, y=_by,
                xanchor='right', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 2, color=INK), text='Campaign 1'))
            _annotations.append(dict(
                xref='x', yref='y', x=_at(_hi) + 8, y=_by,
                xanchor='left', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 3, color=INK_SOFT), text=_c1_note[_role]))

            for _i, _name in enumerate(_names):
                _ry = _y + _HEAD_H + (_i + 1.5) * _ROW_H
                _rlo, _rhi = C2_V_RANGES[_role][
                    [_k for _k in C2_V_RANGES[_role] if pretty(_k) == _name][0]]
                _shapes.append(dict(
                    type='rect', xref='x', yref='y',
                    x0=_at(_rlo), x1=_at(_rhi), y0=_ry - _BAR_H / 2.0, y1=_ry + _BAR_H / 2.0,
                    fillcolor=fade(NEW_COLOR, 0.35),
                    line=dict(color=NEW_COLOR, width=1.6)))
                _annotations.append(dict(
                    xref='x', yref='y', x=_LABEL_W - 10, y=_ry,
                    xanchor='right', yanchor='middle', showarrow=False,
                    font=dict(size=ANNOTATION_SIZE - 2, color=INK), text=_name))
                _annotations.append(dict(
                    xref='x', yref='y', x=_at(_rhi) + 8, y=_ry,
                    xanchor='left', yanchor='middle', showarrow=False,
                    font=dict(size=ANNOTATION_SIZE - 3, color=INK),
                    text='{:g}–{:g} %'.format(_rlo, _rhi)))

            _y += _group_h + _GROUP_GAP

        # The scale, once, under all three groups. Drawn as a rule and annotations rather than
        # by a visible axis, so it stays on the pixel grid with everything else.
        _axis_y = _y + 2.0
        _shapes.append(dict(type='line', xref='x', yref='y',
                            x0=_at(0.0), x1=_at(_SCALE_MAX), y0=_axis_y, y1=_axis_y,
                            line=dict(color=INK, width=1.4)))
        for _t in (0, 10, 20, 30, 40):
            _shapes.append(dict(type='line', xref='x', yref='y',
                                x0=_at(_t), x1=_at(_t), y0=_axis_y, y1=_axis_y + 5,
                                line=dict(color=INK, width=1.4)))
            _annotations.append(dict(
                xref='x', yref='y', x=_at(_t), y=_axis_y + 8,
                xanchor='center', yanchor='top', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 3, color=INK), text='{:g}'.format(_t)))
        _annotations.append(dict(
            xref='x', yref='y', x=_at(_SCALE_MAX), y=_axis_y + 8,
            xanchor='right', yanchor='top', showarrow=False,
            font=dict(size=ANNOTATION_SIZE - 3, color=INK_SOFT), text='% v/v'))

        # ---- right: the score ------------------------------------------------------------
        _sx, _sy, _sw, _sh = pixel_axes((0.640, 0.985), (0.000, 1.000), anchor=('x2', 'y2'))
        _NAME_W = 168.0
        _COL = (_NAME_W + 46.0, _NAME_W + 132.0)   # centres of the two weight columns
        _sy0 = 6.0

        _annotations.append(dict(
            xref='x2', yref='y2', x=0.0, y=_sy0 + 18,
            xanchor='left', yanchor='bottom', showarrow=False,
            font=dict(size=ANNOTATION_SIZE, color=INK), text='<b>What the score reads</b>'))
        for _cx, _head, _col in zip(_COL, ('Campaign 1', 'Campaign 2'),
                                    (SPACE_COLOR, NEW_COLOR)):
            _annotations.append(dict(
                xref='x2', yref='y2', x=_cx, y=_sy0 + 46,
                xanchor='center', yanchor='bottom', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 2, color=_col), text=_head))

        # The five rows are set at a generous pitch on purpose: the panel carries far less ink
        # than the ranges beside it, so an airy right column balances the two rather than
        # leaving a tight block floating at the top of the canvas.
        _CHIP_W, _CHIP_H = 40.0, 26.0
        _row_h = 58.0
        _ry0 = _sy0 + 66.0
        for _i, (_stem, _label) in enumerate(SCORE_ROWS):
            _cy = _ry0 + (_i + 0.5) * _row_h
            _is_new = _stem in NEW_STEMS
            _annotations.append(dict(
                xref='x2', yref='y2', x=_NAME_W - 12, y=_cy,
                xanchor='right', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 1, color=NEW_COLOR if _is_new else INK),
                text='<b>{}</b>'.format(_label) if _is_new else _label))
            for _cx, _w, _col in zip(_COL, (C1_W.get(_stem), C2_W.get(_stem)),
                                     (SPACE_COLOR, NEW_COLOR)):
                if _w is None:
                    # Not scored at all, which is the panel's point for two of the rows. An
                    # en dash rather than an empty cell: a blank reads as an oversight.
                    _annotations.append(dict(
                        xref='x2', yref='y2', x=_cx, y=_cy,
                        xanchor='center', yanchor='middle', showarrow=False,
                        font=dict(size=ANNOTATION_SIZE - 1, color=INK_SOFT), text='—'))
                    continue
                _shapes.append(dict(
                    type='rect', xref='x2', yref='y2',
                    x0=_cx - _CHIP_W / 2.0, x1=_cx + _CHIP_W / 2.0,
                    y0=_cy - _CHIP_H / 2.0, y1=_cy + _CHIP_H / 2.0,
                    fillcolor=fade(_col, 0.28), line=dict(color=_col, width=1.6)))
                _annotations.append(dict(
                    xref='x2', yref='y2', x=_cx, y=_cy,
                    xanchor='center', yanchor='middle', showarrow=False,
                    font=dict(size=ANNOTATION_SIZE - 1, color=INK), text='{:g}'.format(_w)))

        # Phase separation, apart. It is not a weight in the same sense as the five above --
        # Campaign 1 adds 10 x sep to the loss, Campaign 2 divides the loss by 1 - sep -- so it
        # is written as the operator and ruled off rather than set as a number in the column.
        _rule_y = _ry0 + len(SCORE_ROWS) * _row_h + 6.0
        _shapes.append(dict(type='line', xref='x2', yref='y2',
                            x0=0.0, x1=_COL[1] + _CHIP_W, y0=_rule_y, y1=_rule_y,
                            line=dict(color=INK, width=1.2)))
        _sep_y = _rule_y + 24.0
        _annotations.append(dict(
            xref='x2', yref='y2', x=_NAME_W - 12, y=_sep_y,
            xanchor='right', yanchor='middle', showarrow=False,
            font=dict(size=ANNOTATION_SIZE - 1, color=INK), text='Phase separation'))
        for _cx, _txt, _col in zip(_COL,
                                   ('+ {:g} × sep'.format(C1_W['sep']),
                                    '÷ (1 − sep)'),
                                   (SPACE_COLOR, NEW_COLOR)):
            _annotations.append(dict(
                xref='x2', yref='y2', x=_cx, y=_sep_y,
                xanchor='center', yanchor='middle', showarrow=False,
                font=dict(size=ANNOTATION_SIZE - 2, color=_col), text=_txt))

        _annotations.append(dict(
            xref='x2', yref='y2', x=0.0, y=_sep_y + 30,
            xanchor='left', yanchor='top', showarrow=False, align='left',
            font=dict(size=ANNOTATION_SIZE - 3, color=INK_SOFT),
            text='PDI is hinged at 0.3 in Campaign 1 and at 0.1 in Campaign 2.'))
        _annotations.append(dict(
            xref='x2', yref='y2', x=0.0, y=_sep_y + 52,
            xanchor='left', yanchor='top', showarrow=False, align='left',
            font=dict(size=ANNOTATION_SIZE - 3, color=INK_SOFT),
            text='Both objectives are losses, so lower is better and a heavier<br>'
                 'weight is a property the optimiser is less willing to trade away.'))

        # ---- legend proxies -------------------------------------------------------------
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Campaign 1',
            marker=dict(size=MARKER_SIZE, color=fade(SPACE_COLOR, 0.28), symbol='square',
                        line=dict(width=1.4, color=SPACE_COLOR))))
        _traces.append(go.Scatter(
            x=[None], y=[None], mode='markers', name='Campaign 2',
            marker=dict(size=MARKER_SIZE, color=fade(NEW_COLOR, 0.35), symbol='square',
                        line=dict(width=1.4, color=NEW_COLOR))))

        _annotations += [
            dict(xref='paper', yref='paper', x=0.5, y=1.100, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=TITLE_SIZE, color=INK), name='heading',
                 text='<b>And what changed underneath them?</b>'),
            dict(xref='paper', yref='paper', x=0.5, y=1.045, xanchor='center', yanchor='bottom',
                 showarrow=False, font=dict(size=ANNOTATION_SIZE, color=INK_SOFT),
                 text='Every ingredient carries its own volume range, and the score reads '
                      'two properties Campaign 1 never scored'),
        ]

        _layout = go.Layout(
            width=FIG_WIDTH, height=FIG_HEIGHT,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            margin=SCHEMATIC_MARGIN,
            xaxis=_vx, yaxis=_vy,
            xaxis2=_sx, yaxis2=_sy,
            shapes=_shapes, annotations=_annotations,
            legend=dict(orientation='h', xanchor='center', x=0.5, yanchor='top', y=-0.02,
                        font=dict(size=LEGEND_SIZE), itemsizing='constant',
                        bgcolor='rgba(0,0,0,0)'),
        )
        return go.Figure(data=_traces, layout=_layout)


    boundaries_figure = build_boundaries_state()
    boundaries_figure
    return (boundaries_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export

    Three states at the house 1280 x 720, one data unit to one exported pixel. `EXPORT_FORMATS`
    writes a 2x raster alongside if `png` is added to it.

    **Every figure is exported twice, once per entry in `FONT_SCHEMES`.** Sizes are identical in
    both, so a `_Pretendard` export is a drop-in replacement for its plain twin. The plain export
    exists because an SVG *references* a font rather than embedding one: the `_Pretendard` pair
    renders as itself only where both faces are installed.

    Stems carry the state name rather than a number alone, so a file that turns up on its own in a
    deck folder still says what it shows.
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
    boundaries_figure,
    explored_figure,
    narrowed_figure,
    with_font_scheme,
):
    FIGURES = {
        'Design_Space_Transition_Explored': (explored_figure, FIG_WIDTH, FIG_HEIGHT),
        'Design_Space_Transition_Narrowed': (narrowed_figure, FIG_WIDTH, FIG_HEIGHT),
        'Design_Space_Transition_Boundaries': (boundaries_figure, FIG_WIDTH, FIG_HEIGHT),
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
