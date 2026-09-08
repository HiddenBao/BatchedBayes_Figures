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
    # Loaded Champions Figure Suite

    **Two figures, one set of rows.** The three champions Act 1 finished with, each measured blank
    and again with both APIs, above the DoE-OPT baseline the project started from:

    | export | slide | what it asks |
    | --- | --- | --- |
    | `Loaded_Champions_Physicochemical.svg` | one | did loading an API change the measurement? Size, dispersity and charge, no boundary drawn |
    | `Loaded_Champions_Barriers.svg` | two | and does it still clear the bar — **Campaign 2's** bar, which reads two outputs no blank formulation has |

    They stay one suite because both rest on the same resolved row set: the same four
    formulations, the same Campaign 1 ranking, and the same reading of `DoEOPT` across two
    disagreeing files. That resolution is the part that must not drift, and splitting the suite
    would duplicate it.

    Slide one is the plain observation. Slide two lays Campaign 2's objective over it.

    ## The rows: what Act 1 handed over

    Four formulations, and every one of them is prior work rather than a Campaign 2 proposal:

    | row | what it is | blank | A190 | fenofibrate |
    | --- | --- | --- | --- | --- |
    | `B4` | Campaign 1's best-scoring formulation | `B4` | `B4_A` | `B4_F` |
    | `S5` | the quasi-random screen row the paper calls `F5` | `Ran5` | `F5_A` | `F5_F` |
    | `E2` | Campaign 1's batch-E champion | `E2` | `E2_A` | `E2_F` |
    | `DoE-OPT` | the response surface's predicted optimum — where the project started | — | `DoEOPT` | — |

    The three champions are exactly `Campaign1_Leaderboard`'s `CARRIED`: the top-five rows that
    were reformulated drug-loaded and carried into the 30-day study. The order is **the Campaign 1
    objective's**, best first, and it is computed here from `objectives.campaign1` rather than
    typed out, so the rows cannot drift from the board two slides earlier.

    `Ran5` is drawn as `S5`. It carries four names across the project — `Ran5` in the dataset,
    `F5_A` / `F5_F` loaded, `F5` in the paper's Table 3 — and both leaderboards resolve them to
    `S5`. A reader has to be able to follow one row from slide to slide, so the deck name wins over
    the id. The suite asserts `Ran5` and `F5_A` are the same composition, exactly as
    `Campaign1_Leaderboard` does.

    ### DoE-OPT is one mark, and the second one is a trap

    **`data/` carries two different `DoEOPT` measurements under one id, in two different files** —
    and only one of them is drawn.

    | file | `API_Name` | what it is |
    | --- | --- | --- |
    | `MicroemulsionFormulation_Comprehensive.csv` | `A190` | the current measurement, with drug loading and permeability |
    | `MicroemulsionFormulation_A190.csv`, `..._Feno.csv` | `blank` | the **superseded** copy of the same three replicates |

    The numbers differ — 179.9 nm / PDI 0.337 against 184.6 / 0.325 — so it is tempting to read
    them as a blank and its loaded counterpart and draw DoE-OPT with two marks. **They are not a
    pair.** Upstream rebuilt the comprehensive dataset at `2cba4f2` and re-tagged *all five*
    `DoE*` rows from `blank` to `A190`, replacing their measurements; the per-API files were never
    rebuilt and still hold the pre-`2cba4f2` version.

    Two things say revision rather than second experiment. `DoE1`, `DoE4`, `DoE10` and `DoE11`
    were re-tagged in the same sweep and carry **no drug loading at all** — a row that had really
    been loaded with A190 would have a loading number. And the commit rebuilt the whole file
    rather than adding a run.

    **The comprehensive dataset is this suite's ground truth**, so it is the only file opened, and
    DoE-OPT's row is one A190 mark. That resolution is also why `Campaign2_Progress` says DoE-OPT
    has no drug loading while `Design_Space` plots it: the two read different files, and the
    per-API one is stale.

    **There is no fenofibrate DoE-OPT**, in any file, as on the Campaign 2 board and for the same
    reason.

    ## The barriers, and which of them moved

    Every boundary drawn here is a **kink in `objectives.campaign2`** — the point where a component
    score stops improving, starts being charged, or changes slope. None of them is retyped from a
    reading of the formula: the cell below probes `campaign2` itself and asserts the kink is where
    the constant says it is, so a change upstream fails here rather than mislabelling a slide.

    | panel | barrier | Campaign 1 | Campaign 2 |
    | --- | --- | --- | --- |
    | droplet size | 100 nm | 100 nm | **unchanged** |
    | PDI | hinge | 0.3 | **0.1** |
    | \|ζ\| | 10 mV | 10 mV | **unchanged** |
    | drug loading | 100 % ± 5 dead zone | *not in the objective* | **new** |
    | permeability | 20 × 10⁻⁶ | *not in the objective* | **new** |

    So the reading is three-part, and the panels are ordered to tell it left to right: two barriers
    that did not move, one that tightened threefold, and two axes that did not exist when these
    formulations were chosen. **A blank formulation cannot report the last two at all** — its cells
    are empty because the measurement was never made, and that absence is the point rather than a
    gap in the file.

    The superseded PDI hinge is drawn too, as a **dotted** line at 0.3 against the dashed 0.1. It is
    the one barrier on the slide that a reader has already seen — `Design_Space`'s first slide draws
    it as the Table 2 target — so showing where it went is worth one more stroke.

    ### What the panels are not

    **There is no objective panel.** The totals for these very rows are `Campaign2_Leaderboard`'s
    whole subject, and a sixth panel here would be that board a second time at a fifth of the
    width. These slides are the components and the boundaries; the ranking is the next one.

    ## Environment

    A [marimo](https://marimo.io) notebook, so it is a plain Python module and the interpreter that
    launches it *is* the kernel. Run it from the **`BatchedBayes`** conda environment:

    ```
    conda run -n BatchedBayes marimo edit Figures/Loaded_Champions/Loaded_Champions_Figures.py
    conda run -n BatchedBayes python Figures/Loaded_Champions/Loaded_Champions_Figures.py
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
    the wrong tree. The canvas is the house 1280 × 720.

    **Two data files, on purpose.** `DATA_CSV` is the comprehensive dataset and is where every row
    on the slide comes from except one: the blank DoE-OPT, which exists only in the per-API files.
    See the trap noted above — both per-API paths are read and asserted equal before either is used.
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Loaded_Champions' / 'Output'
    # The one dataset this suite reads. The per-API CSVs are deliberately NOT opened -- their
    # `DoEOPT` is the superseded pre-2cba4f2 copy of these same replicates, not a blank
    # counterpart. See the data cell.
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

    House style — the `Breaking-the-Boundaries` suites', value for value: white ground, a 2 px
    black mirrored axis box, no gridlines, five type sizes (20 / 18 / 18 / 14 / 14), a centred
    title, a horizontal legend in a bottom gutter.

    **Every hue is a leaderboard token, carrying the meaning it already carries there.** Nothing
    on these slides invents a colour, so a reader who has seen either board arrives knowing the
    palette.

    | token | hex | what it means | where else |
    | --- | --- | --- | --- |
    | `BLANK_COLOR` | `#2067F4` | the blank Campaign 1 measurement | the revalidated champions on the Campaign 2 board |
    | `A190_COLOR` | `#5A2E8C` | loaded with A190 | the A190 ramp's darkest step |
    | `FENO_COLOR` | `#00572B` | loaded with fenofibrate | the fenofibrate ramp's darkest step |
    | `DOE_COLOR` | `#D55E00` | DoE-OPT, the screening baseline | both leaderboards, `Campaign1_Progress`, `Design_Space` |

    `#2067F4` is the revalidated-champion hue on the Campaign 2 board — the same three
    formulations, in the same role — and here it marks their blank half, which is the Campaign 1
    measurement the board's blue stands for. The two API hues are the **darkest step of each
    track's ramp**, taken at matched lightness (L\* ≈ 30 for both) so that neither API reads as
    deeper than the other; there are no batches on these slides, so the ramps are not in play and
    each hue carries the one thing its family means — which API.

    **Hue is the API, except on the one row where the deck says otherwise.** For the three
    champions a mark's colour says which of the three measurements it is, because the comparison
    runs *along* a row rather than between rows. DoE-OPT breaks that and wears `#D55E00`, which is
    what it wears on every other figure in the project — painting it purple to say "A190" would
    trade the one hue the deck keeps constant everywhere for a local rule. The Campaign 2 board
    runs the same licence: it groups by what a row is *doing* on the figure, not by where it came
    from.

    Marks carry a **second channel as well**: circle for blank, diamond for A190, square for
    fenofibrate. DoE-OPT keeps the A190 diamond, so on that row shape says which API while hue
    says which role. The two API hues separate at ΔE 98 and the blue is a third family again, so
    shape is redundancy rather than the only signal — but three series interleaved within one row
    is exactly the case where a reader should not have to resolve a hue to read a group.

    Boundaries are drawn in **ink**, never in a hue: dashed for a barrier `campaign2` charges
    against, dotted for the Campaign 1 hinge it replaced. A specification is not a series, and
    giving one a colour would put it in competition with the measurements for the reader's
    category sense. That dash/dot pair is the figure's **only** line distinction — the row rules
    are one weight, one colour, one dash throughout.
    """)
    return


@app.cell
def _(FIG_HEIGHT, FIG_WIDTH, go):
    BLANK_COLOR = '#2067F4'    # blue    -- the blank Campaign 1 measurement
    A190_COLOR = '#5A2E8C'     # purple  -- loaded with A190; the A190 ramp's darkest step
    FENO_COLOR = '#00572B'     # green   -- loaded with fenofibrate; that ramp's darkest step
    DOE_COLOR = '#D55E00'      # red     -- DoE-OPT, the screening baseline; its hue deck-wide

    INK = 'black'
    # Subtitles only. Everything that labels the geometry -- row names, tick values -- is full
    # black, because on a projector a grey label reads as washed out rather than as quieter.
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    # The hairline closing each formulation's band. One weight, one colour, one dash for every
    # rule on the figure -- DoE-OPT's included. It used to be dotted and darker, to say "section
    # break rather than row break"; that distinction is now carried by DoE-OPT's own hue and by
    # its shorter band, and a second marker for it made the rules read as two kinds of line.
    ROW_RULE = 'rgba(0, 0, 0, 0.16)'
    # The pass side of every barrier, and the `Breaking-the-Boundaries` SCREEN_BAND value.
    PASS_BAND = 'rgba(0, 0, 0, 0.055)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

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

    # Sizes do NOT change between schemes. The house 20/18/18/14/14 is the same in both, so the
    # two exports are drop-in swaps for each other and a slide can be re-fonted without
    # re-checking that anything still fits.

    MARKER_SIZE = 12
    MARKER_RING = 2
    ERROR_WIDTH = 1.4
    FRAME_WIDTH = 2

    LEGEND_MARGIN = 96   # bottom gutter the horizontal legend sits in


    def with_font_scheme(fig, body, heading, tick):
        """A copy of `fig` re-fonted: `heading` on the slide title, `body` on everything else.

        Applied after the figure is built rather than threaded through the builder, so the two
        exports cannot drift: there is one figure, drawn once, wearing two type schemes. Heading
        text is tagged where it is written with `name='heading'`; everything else is body by
        definition, which is the safe default -- a new annotation joins the reading face rather
        than silently claiming to be a title.

        The **axis titles are body**, unlike the other suites', which set them on the display
        face. Five panel names in a row is a lot of display type for what is really a set of
        labels, and the display face's heavier strokes at 18 pt crowded the ticks under them.
        Ticks keep their own slot and stay on the display face, so the numbers still read as
        frame rather than as prose.
        """
        out = go.Figure(fig.to_dict())
        out.layout.font.family = body
        out.layout.title.font.family = heading
        out.layout.legend.font.family = body
        for _ann in out.layout.annotations:
            _ann.font.family = heading if _ann.name == 'heading' else body
        for _axis in list(out.select_xaxes()) + list(out.select_yaxes()):
            _axis.tickfont.family = tick
            _axis.title.font.family = body
        return out


    AXIS_COMMON = dict(
        showline=True, linecolor=INK, linewidth=FRAME_WIDTH, mirror=True,
        tickcolor=INK, color=INK, ticks='outside',
        showgrid=False, zeroline=False,
        # tickangle=0 is not cosmetic. Five panels at 18 pt is tight, and plotly's response to
        # tick labels it thinks will collide is to rotate them to vertical -- which on one panel
        # out of five reads as a different kind of axis and pushes that panel's title down out of
        # line with its neighbours'. Pinning the angle turns a silent re-layout into a visible
        # collision, and the fix for a collision is fewer ticks.
        tickangle=0,
        tickfont=dict(size=TICK_SIZE), title_font=dict(size=AXIS_TITLE_SIZE),
    )

    print('canvas {} x {}'.format(FIG_WIDTH, FIG_HEIGHT))
    return (
        A190_COLOR,
        ANNOTATION_SIZE,
        AXIS_COMMON,
        AXIS_TITLE_SIZE,
        BLANK_COLOR,
        DOE_COLOR,
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
        ROW_RULE,
        TITLE_SIZE,
        with_font_scheme,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The barriers, probed out of `objectives.campaign2`

    Each constant below is a **kink** in one of `campaign2`'s component scores: the value at which
    the component stops improving, starts being charged, or changes slope. They are stated here
    because a figure needs numbers to draw lines at — and then every one of them is checked against
    the function itself, by evaluating `campaign2` either side of the claimed kink.

    That is the difference between importing a barrier and restating one. If upstream retunes the
    PDI hinge or the permeability knee, this cell raises rather than the slide quietly drawing a
    boundary the optimiser no longer uses.

    `PDI_HINGE_C1` is the exception: it is Campaign 1's hinge, probed against `campaign1`, and it
    is on the slide precisely because `campaign2` no longer has it.
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
    _s = _probe('Droplet_Size', [SPEC_SIZE_NM - 50, SPEC_SIZE_NM, SPEC_SIZE_NM + 50])['size_score (w=3)']
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

    # Campaign 1 reads three outputs; campaign 2 reads five. That is the slide's last two panels,
    # so check it rather than assert it in prose: moving loading or permeability must not move a
    # campaign 1 score.
    for _col in ('Drug_Loading', 'Permeability'):
        _c1 = _probe(_col, [_BASE[_col] * 0.5, _BASE[_col] * 1.5], objective=campaign1)['objective']
        assert _c1.nunique() == 1, \
            'campaign1 reads {} -- the "new axis" claim on this slide is wrong'.format(_col)

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

    Ten measurements, in four rows: three each for `B4`, `S5` and `E2`, and one for DoE-OPT. Each
    is the mean of its three replicates with their standard deviation, measured -- not scored.

    **Row order is computed, not typed.** The three champions are ranked by
    `objectives.campaign1` on their *blank* rows, which is the objective they were actually
    selected against and the order `Campaign1_Leaderboard` puts them in. DoE-OPT is last and set
    off by a rule, as it is on that board and on `Design_Space`'s first slide — it is the screening
    baseline, not a campaign result.

    Four claims the cell asserts rather than assumes:

    - **the champions are `Campaign1_Leaderboard`'s `CARRIED`** — the top-five rows that reached
      drug loading. If the ranking moves, this fails here.
    - **`Ran5` and `F5_A` are one composition**, so `S5` really does name one formulation across
      the blank and loaded halves of its row.
    - **`DoEOPT` in the comprehensive file is the A190-tagged measurement** — the one this suite
      treats as current. If a future export puts the `blank` rows back, this fails rather than
      quietly redrawing DoE-OPT as something else.
    - **only loaded rows carry drug loading and permeability**, and every blank row carries
      neither. The last two panels are empty for the blanks because the measurement does not
      exist, and that has to be a fact about the file rather than a NaN that happened to plot.
    """)
    return


@app.cell
def _(DATA_CSV, campaign1, campaign2, pd):
    # (deck name, blank id, A190 id, fenofibrate id). `None` is a measurement that was never made.
    #
    # `Ran5` is the paper's `F5` and both leaderboards render it `S5`; a row has to wear one name
    # across the deck or a reader cannot follow it from slide to slide, so the deck name wins over
    # the id -- see Figures/README.md.
    #
    # DoE-OPT has NO blank id, and that is a decision rather than a gap in the file. See the note
    # below: the per-API CSVs do carry a `blank`-tagged DoEOPT, but it is the superseded version of
    # the same three replicates rather than a blank counterpart, so it is not drawn. Its
    # fenofibrate cell is empty because no such measurement exists in any file, as on the
    # Campaign 2 board.
    FORMULATIONS = [
        ('B4', 'B4', 'B4_A', 'B4_F'),
        ('S5', 'Ran5', 'F5_A', 'F5_F'),
        ('E2', 'E2', 'E2_A', 'E2_F'),
    ]
    DOE_ROW = ('DoE-OPT', None, 'DoEOPT', None)

    # `Campaign1_Leaderboard`'s CARRIED: the top-five Campaign 1 rows that were reformulated
    # drug-loaded and carried into the 30-day study. Named so this slide fails if that set moves.
    CARRIED = {'B4', 'Ran5', 'E2'}

    STATES = ('blank', 'A190', 'Feno')

    _MEASURED = ['Droplet_Size', 'PDI', 'Zeta_P', 'Drug_Loading', 'Permeability']
    _COMPOSITION = ['Oil', 'Surfactant', 'Cosurfactant',
                    'Oil_V', 'Surfactant_V', 'Cosurfactant_V', 'Sonication']

    _raw = pd.read_csv(DATA_CSV)

    # --- one file, and why the other two are not opened -------------------------------------
    # The comprehensive dataset is the ground truth for this suite. The per-API CSVs carry their
    # own `DoEOPT` -- three replicates tagged `blank`, with no drug loading or permeability -- and
    # it is tempting to draw it as DoE-OPT's blank half. It is not one.
    #
    # Upstream rebuilt the comprehensive dataset at 2cba4f2 and re-tagged ALL FIVE DoE* rows from
    # `blank` to `A190`, replacing their measurements; the per-API files were never rebuilt and so
    # still hold the pre-2cba4f2 version. Two things say that is a revision rather than a second
    # experiment: DoE1 / DoE4 / DoE10 / DoE11 were re-tagged in the same sweep and carry no drug
    # loading at all -- a row that had really been loaded would have a loading number -- and the
    # commit rebuilt the whole file rather than adding a run.
    #
    # So DoE-OPT is one mark, not two, and its row is the A190-loaded measurement the current
    # dataset holds. Asserted, not assumed.
    ALL_ROWS = pd.read_csv(DATA_CSV)
    assert (ALL_ROWS.loc[ALL_ROWS['Exp'].eq('DoEOPT'), 'API_Name'] == 'A190').all(), \
        "the comprehensive file's DoE-OPT is no longer the A190-loaded measurement"

    # --- one aggregated record per measurement ---------------------------------------------
    def _aggregate(exp):
        rows = ALL_ROWS[ALL_ROWS['Exp'].eq(exp)]
        assert len(rows) == 3, '{}: expected 3 replicates, found {}'.format(exp, len(rows))
        assert (rows['Phase_Sep'] == 0).all(), '{}: phase separated'.format(exp)
        out = {'Exp': exp, 'api_name': rows['API_Name'].iloc[0]}
        for col in _MEASURED:
            out[col] = rows[col].mean()
            out[col + '_sd'] = rows[col].std()
        return out


    def _composition(exp):
        rows = ALL_ROWS.loc[ALL_ROWS['Exp'].eq(exp), _COMPOSITION].drop_duplicates()
        assert len(rows) == 1, '{} has {} compositions'.format(exp, len(rows))
        return rows.iloc[0].tolist()


    # --- row order: the Campaign 1 objective on the blank rows ------------------------------
    assert {blank for _, blank, _, _ in FORMULATIONS} == CARRIED, \
        'the champions are no longer Campaign1_Leaderboard CARRIED'
    _blanks = ALL_ROWS[ALL_ROWS['Exp'].isin(CARRIED)].copy()
    _blanks['objective'] = campaign1(_blanks)['objective']
    _ORDER = list(_blanks.groupby('Exp')['objective'].mean().sort_values().index)
    FORMULATIONS = sorted(FORMULATIONS, key=lambda f: _ORDER.index(f[1]))

    records = []
    for _name, _blank_id, _a190_id, _feno_id in FORMULATIONS + [DOE_ROW]:
        _ids = {'blank': _blank_id, 'A190': _a190_id, 'Feno': _feno_id}
        for _state in STATES:
            _exp = _ids[_state]
            if _exp is None:
                continue
            _rec = _aggregate(_exp)
            _rec['formulation'] = _name
            _rec['state'] = _state
            records.append(_rec)

    RUNS = pd.DataFrame(records)
    ROW_ORDER = [name for name, *_ in FORMULATIONS] + [DOE_ROW[0]]
    DOE_NAME = DOE_ROW[0]

    # Each mark's API tag has to match the state it is drawn as, or a hue means the wrong thing.
    _EXPECTED_API = {'blank': 'blank', 'A190': 'A190', 'Feno': 'Feno'}
    for _r in RUNS.itertuples():
        assert _r.api_name == _EXPECTED_API[_r.state], \
            '{} is tagged {} but is drawn as {}'.format(_r.Exp, _r.api_name, _r.state)

    # `S5` names one formulation across its row, not two that happen to share a rank.
    assert _composition('Ran5') == _composition('F5_A'), \
        "Ran5 is no longer the paper's F5 -- the loaded rows have drifted from the blank"

    # The last two panels are empty for the blanks because the measurement was never made. That
    # is a fact about the file, so check it here rather than letting a NaN decide the slide.
    for _col in ('Drug_Loading', 'Permeability'):
        _have = set(RUNS.loc[RUNS[_col].notna(), 'state'])
        assert _have == {'A190', 'Feno'}, \
            '{} is measured for states {}, expected the two loaded ones'.format(_col, sorted(_have))

    # The |zeta| panel plots the magnitude against a boundary on the magnitude, which is only a
    # sign flip while every reading is negative. If a positive one ever lands here, abs() would
    # fold it onto the wrong side of that boundary, so fail instead.
    assert (RUNS['Zeta_P'] < 0).all(), \
        'zeta is positive for {} -- the |zeta| panel would fold it'.format(
            sorted(RUNS.loc[RUNS['Zeta_P'] >= 0, 'Exp']))

    # Not drawn -- printed, as an orientation column while reading the notebook.
    #
    # It is the objective OF THE MEANS, which is not what either leaderboard ranks: those score
    # each replicate and average the scores, and the two differ wherever a component is non-linear
    # across a row's spread (B4_A comes out 0.89 here against the board's 0.98). Named for what it
    # is so the two numbers are never read as the same quantity disagreeing.
    RUNS['c2_of_means'] = campaign2(RUNS.assign(Phase_Sep=0.0))['objective']

    print(RUNS[['formulation', 'state', 'Exp', 'Droplet_Size', 'PDI', 'Zeta_P',
                'Drug_Loading', 'Permeability', 'c2_of_means']].to_string(
                    index=False, float_format=lambda v: '{:.4g}'.format(v)))
    print('\nrow order (campaign1 on the blanks, best first): {}'.format(' > '.join(ROW_ORDER)))
    return DOE_NAME, ROW_ORDER, RUNS, STATES


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The two figures

    **One builder, two panel lists.** `build_slide()` takes the panels and a flag for whether to
    draw barriers, so the rows, the offsets, the row rules and the type are shared by
    construction and the two exports cannot drift apart.

    | export | panels | barriers | the question it answers |
    | --- | --- | --- | --- |
    | `Loaded_Champions_Physicochemical.svg` | size · PDI · \|ζ\| | **none** | did the measurement move when the formulation was loaded? |
    | `Loaded_Champions_Barriers.svg` | those three, plus drug loading and permeability | Campaign 2's | and did it still clear the bar — the new bar? |

    The physicochemical figure comes **first in the deck**. It is the plain observation, on the
    three outputs both campaigns measure and neither API changes the meaning of, with no boundary
    drawn at all: nothing on it is a pass or a fail, it is three properties measured twice. The
    barrier figure is that same reading with Campaign 2's objective laid over it, and two axes
    added that only the loaded rows can report.

    ### The panels

    | panel | physicochemical | barrier figure | barrier |
    | --- | --- | --- | --- |
    | droplet size, nm | 0 – 270 | 0 – 270 | 100 nm |
    | PDI | 0 – 0.5, ticked 0 / 0.2 / 0.4 | 0 – 0.5, ticked 0 / **0.1** / 0.3 / 0.5 | 0.1, with Campaign 1's 0.3 dotted behind it |
    | \|ζ\|, mV | **0 – 8** | 0 – 12 | 10 mV |
    | drug loading, % | — | 88 – 116 | 100 ± 5 |
    | permeability, ×10⁻⁶ | — | 0 – 36 | 20 |

    Two of the three shared panels are **identical between the figures**, so a reader who sees both
    reads one scale. Only the ticks and the zeta range differ, and both differences are the
    barriers' doing: the PDI panel is ticked at 0.1 and 0.3 *because* they are boundaries, and once
    they are gone an even 0 / 0.2 / 0.4 is the honest set. Zeta runs to 12 to make room for a
    boundary at 10; with no boundary to clear, half that panel would be empty, so the
    physicochemical figure stops at 8 — every reading is inside 6.3.

    Each panel is named by its **x-axis title**, at the house axis-title size, rather than by a
    header floating above the box — the label sits with the scale it describes.

    **No boundary is labelled.** Its value is an axis tick instead, so a reader takes it off the
    same scale as the data rather than from a caption floating beside the line. That is why each
    panel names its ticks explicitly and every barrier is asserted to be one of them.

    Every panel shades the side that **satisfies** its barrier, which is why the shading is a
    range rather than a direction: below 100 nm, below a PDI of 0.1, inside \|ζ\| < 10, *between*
    95 and 105 % loading, and *above* a permeability of 20 × 10⁻⁶ — the one output where more is
    better, and `campaign2` pays a bonus for it.

    Permeability is drawn in units of 10⁻⁶, stated in the axis title, because the raw column is
    in the 10⁻⁶–10⁻⁵ decade and five panels do not have the width for exponent tick labels. **No
    unit is named beyond the magnitude**, and deliberately: `data/` records none, and neither
    `objectives.py` nor anything else in this repo states one. Writing `cm s⁻¹` on the axis would
    be a guess printed at 18 pt.

    ### Error bars, and the one that runs off the axis

    Every mark is a mean of three replicates with their standard deviation. One of them,
    fenofibrate-loaded `S5`, has a standard deviation larger than its mean — its three replicates
    came in at 193.9, 12.7 and 13.0 nm — so its bar reaches the left edge of the size panel and
    stops there. That is the axis clipping a bar, not the bar ending: the formulation is bimodal
    across replicates, and a spread that wide *is* the reading for that row.

    Zeta plots the **magnitude**. It is measured negative throughout and the barrier is on \|ζ\|,
    so the panel runs left to right on \|ζ\| rather than −12 → 0; the data cell asserts the sign,
    so that is a flip and never a fold.

    ### Bands, not rows

    Within a band the three measurements sit at fixed offsets — blank above, A190 on the band's
    centre line, fenofibrate below — so the same state is always in the same place and a band
    reads as one group.

    **Each formulation's band is closed by a hairline rule.** Offsets alone group the marks only as
    long as a reader trusts the spacing, and on a panel where one row's marks are spread across the
    axis and its neighbour's are clustered, the spacing stops being obvious. The rules make the
    grouping structural rather than perceptual: three marks between two rules are one formulation,
    whatever the values do.

    **They are drawn one segment per panel, not once across the canvas.** A single paper-width rule
    is the obvious implementation and the wrong drawing: it runs on through the gaps between the
    panels and through the label gutter, so the white space that separates five boxes becomes ruled
    space and the figure reads as one table with gaps cut out of it. Inside the boxes the rules
    divide bands; between them, nothing is drawn.

    **Every rule is the same weight, colour and dash.** DoE-OPT's used to be dotted and darker, to
    say section break rather than row break. Two kinds of hairline read as two systems, and the
    distinction is already carried twice over — DoE-OPT wears its own hue and sits in a band of its
    own height.

    **The bands are not all the same height.** A champion's holds three marks and is a full unit;
    DoE-OPT's holds one, and at full height its row was a third of the panel given over to white
    space around a single diamond.

    `DOE_BAND` is **derived rather than chosen**: inside a champion band the three marks are
    pitched `max|dy|` apart, so one mark occupies exactly that much of it. DoE-OPT holds one mark
    and gets one pitch — 0.26 of a unit, the space the diamond already takes where it sits beside
    two neighbours, with the marker still clear of both rules. Band edges are computed
    once, and the rules, the row labels and the axis range all come off them, so a change to the
    offsets moves everything together.

    A missing measurement leaves **no mark**, and there are three such gaps: DoE-OPT is a single
    A190 mark (no blank counterpart, no fenofibrate run), and no blank formulation has drug loading
    or permeability. Nothing is drawn at zero and nothing is drawn as a hollow placeholder — an
    absent measurement is absent.
    """)
    return


@app.cell
def _(
    A190_COLOR,
    ANNOTATION_SIZE,
    AXIS_COMMON,
    AXIS_TITLE_SIZE,
    BLANK_COLOR,
    DOE_COLOR,
    DL_DEAD_ZONE,
    DL_TARGET,
    DOE_NAME,
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
    ROW_ORDER,
    ROW_RULE,
    RUNS,
    SPEC_SIZE_NM,
    SPEC_ZETA_ABS,
    STATES,
    TITLE_SIZE,
    go,
):
    # How each state is drawn. Hue is the API, not the formulation -- the comparison the slide
    # makes runs *along* a row. Shape is a second channel for the same distinction: three series
    # interleaved inside one row is exactly the case where a reader should not have to resolve a
    # hue to read a group. `dy` is the offset from the row line, in row units.
    # `legend` is kept SHORT on purpose: the barrier figure carries six entries and the house
    # legend is one horizontal row at 14 pt. Prose belongs in the subtitle, which already says
    # these are Campaign 1's formulations measured blank and with each API.
    STATE_STYLE = {
        'blank': dict(color=BLANK_COLOR, symbol='circle', dy=0.26,
                      legend='Blank'),
        'A190':  dict(color=A190_COLOR, symbol='diamond', dy=0.00,
                      legend='A190-loaded'),
        'Feno':  dict(color=FENO_COLOR, symbol='square', dy=-0.26,
                      legend='Fenofibrate-loaded'),
    }

    # DoE-OPT is the one row whose hue is NOT its API, and that is the deck's rule rather than an
    # exception to it. `#D55E00` is DoE-OPT on Campaign1_Progress, both leaderboards and
    # Design_Space's first slide, so a reader arriving here has already learned it; painting the
    # row purple to say "A190" would break the one hue this project keeps constant across every
    # figure. The Campaign 2 board runs the same licence -- it groups by what a row is *doing* on
    # the figure, not by where it came from.
    #
    # The API is still on the mark: DoE-OPT keeps the A190 diamond, so shape says which API while
    # hue says which role. It is also the only row below the last rule and the only one in a short
    # band, so nothing rests on the colour alone.
    ROW_STYLE = {DOE_NAME: dict(color=DOE_COLOR,
                                legend='DoE-OPT baseline')}

    # DoE-OPT's band height, in units of a champion's -- derived, not chosen.
    #
    # Inside a champion band the three marks are pitched `max|dy|` apart, so one mark occupies
    # exactly that much of the band. DoE-OPT holds one mark, so its band is one pitch: 0.26 of a
    # unit. That is the space the diamond already takes where it sits beside two neighbours, and
    # the marker (MARKER_SIZE + MARKER_RING) still clears both rules.
    DOE_BAND = max(abs(_s['dy']) for _s in STATE_STYLE.values())

    # One entry per panel, left to right. `BARRIER_PANELS` is one per output `campaign2` reads;
    # `PHYSCHEM_PANELS` is the three both campaigns measure, with every barrier taken off.
    #
    # `pass_range` is the interval that SATISFIES the barrier, shaded. It is a range rather than a
    # direction because the five barriers do not all point the same way: size, PDI and |zeta| pass
    # below, drug loading passes *between* two edges, and permeability passes *above* -- more is
    # better there, and campaign2 pays a bonus for it.
    #
    # `lines` are the barriers themselves, dashed. `soft_lines` is the one superseded boundary in
    # the deck: Campaign 1's PDI hinge at 0.3, dotted, so a reader can see where the bar was
    # before Campaign 2 moved it. No line is labelled -- every value in `lines` and `soft_lines`
    # is in `ticks` instead, read off the same scale as the data.
    #
    # `absolute` plots |value|; `scale` divides before plotting, for an axis whose raw column is
    # in a decade five panels have no width to tick in exponents.
    BARRIER_PANELS = [
        dict(key='Droplet_Size', title='<b>Droplet size</b>, nm',
             axis_range=(0, 270), ticks=(0, 100, 200),
             pass_range=(0, SPEC_SIZE_NM), lines=(SPEC_SIZE_NM,)),
        dict(key='PDI', title='<b>PDI</b>',
             axis_range=(0, 0.5), ticks=(0, 0.1, 0.3, 0.5),
             pass_range=(0, PDI_HINGE_C2), lines=(PDI_HINGE_C2,),
             soft_lines=(PDI_HINGE_C1,)),
        dict(key='Zeta_P', title='<b>Zeta potential</b>, |&#950;| mV', absolute=True,
             axis_range=(0, 12), ticks=(0, 5, 10),
             pass_range=(0, SPEC_ZETA_ABS), lines=(SPEC_ZETA_ABS,)),
        # Ticked at the two dead-zone edges and NOT at 100. Three labels inside a fifth of the
        # canvas collide at 18 pt, and 100 is the one of the three that is not a barrier -- the
        # target is the shaded band between 95 and 105, which the band draws better than a tick.
        dict(key='Drug_Loading', title='<b>Drug loading</b>, %',
             axis_range=(88, 116), ticks=(95, 105),
             pass_range=(DL_TARGET - DL_DEAD_ZONE, DL_TARGET + DL_DEAD_ZONE),
             lines=(DL_TARGET - DL_DEAD_ZONE, DL_TARGET + DL_DEAD_ZONE)),
        dict(key='Permeability',
             title='<b>Permeability</b>, &#215;10<sup>&#8722;6</sup>', scale=1e-6,
             axis_range=(0, 36), ticks=(0, 10, 20, 30),
             pass_range=(PERM_KNEE / 1e-6, 36), lines=(PERM_KNEE / 1e-6,)),
    ]

    # The three physicochemical outputs, with no barrier of any kind: no shaded pass band, no
    # dashed line, no dotted hinge. Nothing on that figure is a pass or a fail.
    #
    # Two of the three keep their barrier-figure range exactly, so a reader who sees both figures
    # reads one scale. The two differences are the barriers' own doing:
    #
    #   PDI     ticked 0 / 0.2 / 0.4. The barrier figure's 0.1 and 0.3 are ticks BECAUSE they are
    #           boundaries; with the boundaries gone, an uneven tick set would be arbitrary.
    #   |zeta|  0 -> 8 rather than 0 -> 12. The wider axis exists to leave room for a boundary at
    #           10. With no boundary to clear, it would be four fifths of a panel of white space:
    #           every reading on the slide is inside 6.3 mV.
    PHYSCHEM_PANELS = [
        dict(key='Droplet_Size', title='<b>Droplet size</b>, nm',
             axis_range=(0, 270), ticks=(0, 100, 200)),
        dict(key='PDI', title='<b>PDI</b>',
             axis_range=(0, 0.5), ticks=(0, 0.2, 0.4)),
        dict(key='Zeta_P', title='<b>Zeta potential</b>, |&#950;| mV', absolute=True,
             axis_range=(0, 8), ticks=(0, 2, 4, 6, 8)),
    ]

    # Every barrier a panel draws has to be readable off that panel's own ticks, and has to be
    # inside its own axis. Both are easy to break by nudging a range; neither is easy to see.
    for _panel in BARRIER_PANELS:
        for _line in tuple(_panel['lines']) + tuple(_panel.get('soft_lines', ())):
            # Compared with a tolerance, not for equality: a barrier divided by its panel's
            # `scale` lands a few ulps off the round number it is meant to be (20e-6 / 1e-6 is
            # 20.000000000000004), which is invisible on the slide and fatal to an `in` test.
            assert any(abs(_line - _t) < 1e-9 for _t in _panel['ticks']), \
                '{}: the barrier at {} is not an axis tick'.format(_panel['key'], _line)
            assert _panel['axis_range'][0] <= _line <= _panel['axis_range'][1], \
                '{}: the barrier at {} is off the axis'.format(_panel['key'], _line)
    assert [p['key'] for p in BARRIER_PANELS] == ['Droplet_Size', 'PDI', 'Zeta_P',
                                                  'Drug_Loading', 'Permeability'], \
        'the panels no longer cover exactly the five outputs campaign2 reads'
    # The physicochemical figure is the barrier figure's first three panels, in the same order and
    # for the same outputs -- not a second, parallel selection that could drift from it.
    assert [p['key'] for p in PHYSCHEM_PANELS] == [p['key'] for p in BARRIER_PANELS[:3]], \
        "the physicochemical panels are no longer the barrier figure's first three"
    # ... and no barrier survives on it, in any of the three forms a panel can carry one.
    for _panel in PHYSCHEM_PANELS:
        assert not (set(_panel) & {'pass_range', 'lines', 'soft_lines'}), \
            '{}: the physicochemical figure draws no barriers'.format(_panel['key'])


    def build_slide(panels, title, subtitle, barriers=True):
        """One figure. `panels` is the layout; `barriers` draws the bands, lines and their legend.

        Both exports come through here, so the rows, the offsets, the row rules, the gutter and
        the type are shared by construction rather than by two builders agreeing.
        """
        # Copied, because the layout below writes `domain` and `suffix` into each panel and the
        # two figures are given different numbers of panels. Mutating the module-level lists would
        # leave whichever figure was built first wearing the other's domains.
        panels = [dict(p) for p in panels]

        # --- row bands ----------------------------------------------------------------------
        # Rows are laid out as BANDS with explicit heights rather than as evenly spaced lines,
        # because they no longer hold the same number of marks. A champion band holds three and
        # is a full unit; DoE-OPT holds one and is `DOE_BAND` of a unit, so its row is not a
        # third of the panel of white space around a single diamond.
        #
        # Bands are stacked downward from the top, and both the row rules and the row labels are
        # computed from the same edges, so a change to one height moves everything together.
        _heights = [DOE_BAND if _name == DOE_NAME else 1.0 for _name in ROW_ORDER]
        _edges, _e = [], sum(_heights)
        for _h in _heights:
            _edges.append((_e, _e - _h))          # (top, bottom) of the band
            _e -= _h
        _y_of = {name: (top + bottom) / 2.0 for name, (top, bottom) in zip(ROW_ORDER, _edges)}
        # The rule between one band and the next; the outer two edges are the axis box itself.
        _rule_ys = [bottom for _, bottom in _edges[:-1]]
        # The box closes the outer two bands exactly as the rules close the inner ones: no extra
        # margin. A pad would be invisible on a champion band, whose marks are 0.24 of a unit
        # clear of its edges either way, but it hangs off the bottom of DoE-OPT's short band and
        # puts its single diamond high in the space a reader sees below the last rule. Without it
        # that diamond is centred in its band on the page as well as in the coordinates.
        _y_range = [_edges[-1][1], _edges[0][0]]

        # The panels run across the house width, sharing one row-label gutter. The gutter is a
        # fixed ~98 px -- 'DoE-OPT' at 18 pt -- and the panels split what is left evenly.
        #
        # The gap has to clear two tick labels, not one: every panel's last tick sits on its own
        # right edge and its neighbour's first tick on the left edge, so a gap sized for one
        # label runs them together. It is widened for the three-panel figure, which has the room
        # and would otherwise read as five panels with two missing.
        _gutter, _right = 0.078, 0.988
        _gap = 0.030 if len(panels) > 3 else 0.055
        _span = (_right - _gutter - _gap * (len(panels) - 1)) / len(panels)
        for _i, _panel in enumerate(panels):
            _x0 = _gutter + _i * (_span + _gap)
            _panel['domain'] = [_x0, _x0 + _span]
            _panel['suffix'] = '' if _i == 0 else str(_i + 1)

        _panel_top, _panel_bottom = 0.865, 0.175

        def _colour_of(formulation, state):
            """The hue a mark wears: its row's, where the row overrides, else its API's.

            Only DoE-OPT overrides, and it keeps the deck's meaning of `#D55E00` rather than the
            API meaning of purple. See ROW_STYLE.
            """
            if formulation in ROW_STYLE:
                return ROW_STYLE[formulation]['color']
            return STATE_STYLE[state]['color']


        def _panel_traces(panel):
            """One marker trace per (state, hue) for one panel. A missing value leaves no mark."""
            _scale = panel.get('scale', 1.0)
            _out = []
            for _state in STATES:
                _style = STATE_STYLE[_state]
                _sub = RUNS[RUNS['state'].eq(_state)]
                # Grouped by hue as well as state, because DoE-OPT's A190 mark is not the A190
                # hue: one trace carries one colour, so a row override splits the state's trace.
                _by_colour = {}
                for _r in _sub.itertuples():
                    _v = getattr(_r, panel['key'])
                    if _v != _v:                     # NaN -- the measurement was never made
                        continue
                    _sd = getattr(_r, panel['key'] + '_sd')
                    _c = _colour_of(_r.formulation, _state)
                    _x, _y, _e = _by_colour.setdefault(_c, ([], [], []))
                    _x.append((abs(_v) if panel.get('absolute') else _v) / _scale)
                    _y.append(_y_of[_r.formulation] + _style['dy'])
                    _e.append((0.0 if _sd != _sd else _sd) / _scale)
                for _c, (_x, _y, _e) in _by_colour.items():
                    _out.append(go.Scatter(
                        x=_x, y=_y, xaxis='x' + panel['suffix'], yaxis='y' + panel['suffix'],
                        mode='markers', hoverinfo='skip', showlegend=False,
                        error_x=dict(type='data', array=_e, color=_c,
                                     thickness=ERROR_WIDTH, width=5),
                        marker=dict(size=MARKER_SIZE, color=_c, symbol=_style['symbol'],
                                    line=dict(width=MARKER_RING, color='white')),
                    ))
            return _out

        _traces = []
        for _panel in panels:
            _traces += _panel_traces(_panel)

        # --- legend proxies -----------------------------------------------------------------
        # Three states, then DoE-OPT -- which is a fourth entry because it is the one mark whose
        # hue is not its API. On the barrier figure two lines follow. The lines are in the legend
        # rather than annotated on the PDI panel because both strokes appear on more than one
        # panel between them, and a caption beside one line would read as belonging to that
        # panel alone.
        for _state in STATES:
            _style = STATE_STYLE[_state]
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='markers', name=_style['legend'],
                marker=dict(size=MARKER_SIZE, color=_style['color'], symbol=_style['symbol'],
                            line=dict(width=1.4, color=INK))))
        for _name, _row in ROW_STYLE.items():
            _traces.append(go.Scatter(
                x=[None], y=[None], mode='markers', name=_row['legend'],
                marker=dict(size=MARKER_SIZE, color=_row['color'],
                            symbol=STATE_STYLE['A190']['symbol'],
                            line=dict(width=1.4, color=INK))))
        if barriers:
            for _name, _dash in (("Campaign 2's barrier", 'dash'),
                                 ('Campaign 1 PDI hinge, superseded', 'dot')):
                _traces.append(go.Scatter(
                    x=[None], y=[None], mode='lines', name=_name,
                    line=dict(color=INK, width=1.8, dash=_dash)))

        _shapes = []
        if barriers:
            for _panel in panels:
                _ref = 'x' + _panel['suffix']
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
                for _line in _panel['lines']:
                    _shapes.append(dict(
                        type='line', xref=_ref, yref='paper', x0=_line, x1=_line,
                        y0=_panel_bottom, y1=_panel_top,
                        line=dict(color=INK, width=1.8, dash='dash')))

        # --- row rules ----------------------------------------------------------------------
        # One hairline under every band but the last, so a formulation's marks are a band between
        # two rules rather than a group a reader has to infer from spacing.
        #
        # Drawn ONE SEGMENT PER PANEL, against that panel's own x axis, rather than as a single
        # paper-width line: a paper-width rule runs on through the gaps between the panels and
        # through the label gutter, which turns the white space that separates the panels into
        # ruled space and makes five boxes read as one table with gaps cut out of it. Inside the
        # boxes only, the rules divide rows; between them, nothing is drawn.
        #
        # Every rule is the same weight, colour and dash -- DoE-OPT's included. It used to be
        # dotted and darker to mark a section break; that is now said by DoE-OPT's own hue and by
        # its shorter band, and two kinds of hairline for one distinction read as two systems.
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
        # ticks, so the panels read as one table rather than as separate charts.
        _ticks = [_y_of[name] for name in ROW_ORDER]
        for _i, _panel in enumerate(panels):
            _s = _panel['suffix']
            _layout['xaxis' + _s] = dict(
                AXIS_COMMON, domain=_panel['domain'], anchor='y' + _s,
                title=dict(text=_panel['title'], font=dict(size=AXIS_TITLE_SIZE)),
                range=list(_panel['axis_range']),
                tickmode='array', tickvals=list(_panel['ticks']))
            _layout['yaxis' + _s] = dict(
                AXIS_COMMON, domain=[_panel_bottom, _panel_top], anchor='x' + _s,
                range=list(_y_range), tickmode='array', tickvals=_ticks,
                ticktext=list(ROW_ORDER) if _i == 0 else ['' for _ in ROW_ORDER], ticks='')
        return go.Figure(data=_traces, layout=_layout)


    # The physicochemical figure first: it is the plain observation, and the barrier figure is
    # that same reading with Campaign 2's objective laid over it.
    physchem_figure = build_slide(
        PHYSCHEM_PANELS, barriers=False,
        title='Does loading an API change the formulation?',
        subtitle='Campaign 1&#8217;s three best formulations blank and with each API, above '
                 'the DoE-OPT baseline &#8212; size, dispersity and charge')
    barriers_figure = build_slide(
        BARRIER_PANELS, barriers=True,
        title='The bar moved, and then the champions were loaded',
        subtitle='The same rows against Campaign 2&#8217;s objective, which reads two outputs '
                 'no blank formulation can report')
    physchem_figure
    return barriers_figure, physchem_figure


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

    Headings are the slide title and the tick labels; body is everything else — the subtitle, the
    legend, the row names and **the axis titles**. That last one differs from the other suites,
    which set axis titles on the display face: five panel names in a row is a lot of display type
    for what is really a set of labels, and at 18 pt the display face's heavier strokes crowded the
    ticks under them. The ticks stay display, so the numbers still read as frame rather than as
    prose. The split otherwise follows the deck: the reading face sets prose, the
    display face labels the frame.

    **Sizes are identical in both.** The house 20/18/18/14/14 does not move, so a `_Pretendard`
    export is a drop-in replacement for its plain twin and nothing has to be re-checked for fit.

    The plain export exists because **an SVG references a font rather than embedding one**. The
    `_Pretendard` file renders as itself only where both faces are installed; anywhere else it
    falls back and the metrics shift. Use it on the machine that has them, and keep the plain one
    for anything that leaves.
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
    barriers_figure,
    physchem_figure,
    with_font_scheme,
):
    FIGURES = {
        'Loaded_Champions_Physicochemical': (physchem_figure, FIG_WIDTH, FIG_HEIGHT),
        'Loaded_Champions_Barriers': (barriers_figure, FIG_WIDTH, FIG_HEIGHT),
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
