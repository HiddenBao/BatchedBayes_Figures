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
    # Campaign 1 Leaderboard Figure Suite

    One slide: **every blank formulation the campaign produced, ranked against the DoE-OPT
    screening optimum.**

    Scoring is **score-then-average** — each of the three repeats is scored on its own and the bar
    is the mean of those three objectives. That is not the same as averaging the measurements and
    scoring once: the objective hinges at 100 nm, |zeta| = 10 mV and PDI 0.3, so the two orders
    give different numbers. The white dots are the individual repeats, so every bar is visibly the
    mean of its own dots.

    The objective is Campaign 1's **as published** — paper Eq. 1–4, equal weights, ×10 phase
    separation, PDI hinged at 0.3, imported from `Figures/objectives.py` rather than restated. It
    is physicochemical only, which is what makes blank formulations and the A190-loaded DoE-OPT
    baseline comparable at all: neither drug loading nor permeability enters the score.

    Phase-separated formulations score around 31 and would flatten everything else, so they are
    named beneath the figure rather than plotted.
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Campaign1_Leaderboard' / 'Output'
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

    The type scale, `FONT_FAMILY` and the 2 px black axis box are the `Breaking-the-Boundaries`
    campaign suites' own, value for value, so a deck that mixes these slides with those reads as
    one system.

    Hues carry **campaign stage** rather than formulation identity:

    | token | hex | what it means |
    | --- | --- | --- |
    | `BO_COLOR` | `#2067F4` | an optimiser-chosen batch, A–E |
    | `SCREEN_COLOR` | black | the quasi-random screen that seeded the surrogate |
    | `PRELIM_COLOR` | `#C4C4C4` | repeats of prior optima — present, deliberately quiet |
    | `BEST_COLOR` | `#D55E00` | DoE-OPT, the baseline the campaign had to beat |

    Five BO rounds are **one** colour on purpose. They are one campaign under one policy, and
    giving each round its own hue would claim a distinction the method does not make.
    """)
    return


@app.cell
def _():
    BO_COLOR = '#2067F4'
    SCREEN_COLOR = 'black'
    PRELIM_COLOR = '#C4C4C4'
    BEST_COLOR = '#D55E00'

    INK = 'black'
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    INK_FAINT = 'rgba(0, 0, 0, 0.38)'

    # The campaign suites' type scale, value for value. Five sizes, no more.
    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    # Plotly's own default, stated rather than inherited, and pinned identically in the
    # Breaking-the-Boundaries suites so the agreement is declared instead of coincidental.
    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    MARKER_SIZE = 7
    MARKER_RING = 1.3
    BAR_WIDTH = 0.62

    LEFT_MARGIN = 96
    RIGHT_MARGIN = 40
    TOP_MARGIN = 104
    LEGEND_MARGIN = 164   # bottom gutter the horizontal legend sits in

    # Thirty rows will not read at 720 px in one column, so the ranking runs down the left panel
    # and continues down the right. Both panels share one x range, so a bar's length means the
    # same thing on either side.
    PANEL_DOMAIN = {'left': (0.0, 0.42), 'right': (0.58, 1.0)}

    AXIS_COMMON = dict(
        linecolor=INK, tickcolor=INK, color=INK,
        ticks='outside', showline=True, showgrid=False, mirror=True, linewidth=2,
    )
    return (
        ANNOTATION_SIZE,
        AXIS_COMMON,
        AXIS_TITLE_SIZE,
        BAR_WIDTH,
        BEST_COLOR,
        BO_COLOR,
        FONT_FAMILY,
        INK,
        INK_FAINT,
        INK_SOFT,
        LEFT_MARGIN,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        MARKER_RING,
        MARKER_SIZE,
        PANEL_DOMAIN,
        PRELIM_COLOR,
        RIGHT_MARGIN,
        SCREEN_COLOR,
        TICK_SIZE,
        TITLE_SIZE,
        TOP_MARGIN,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The board

    Every formulation measured **blank**, plus DoE-OPT. That is the 25 optimiser proposals
    (batches A–E), the 10 quasi-random screen runs and the 7 prior-optimum repeats — 42
    formulations — against the one screening optimum.

    The four DoE screening rows (`DoE1`, `DoE4`, `DoE10`, `DoE11`) are **not** here: they were
    measured A190-loaded and are prior-art points, not campaign output. DoE-OPT earns its place as
    the mark the campaign set out to beat.

    The revalidated champions (`B4_A`, `E2_A`, …) are also excluded — they are loaded
    re-measurements of `B4` and `E2`, which are already on the board as blanks. Including both
    would rank the same formulation twice.

    `SEP_CUT` separates a real score from a phase-separated one: the ×10 phase-separation term puts
    any separated formulation above 10, and no stable one comes close.
    """)
    return


@app.cell
def _(DATA_CSV, campaign1, pd):
    SEP_CUT = 10.0

    STAGE_LABEL = {
        'bo': 'Optimiser Batches A–E',
        'screen': 'Quasi-Random Screen',
        'repeat': 'Prior-Optimum Repeats',
        'doe': 'DoE-OPT (Screening Baseline)',
    }


    def stage_of(exp: str) -> str:
        """Return the campaign stage that produced `exp`; hue carries this."""
        if exp == 'DoEOPT':
            return 'doe'
        if exp.startswith('Ran'):
            return 'screen'
        if exp.startswith('Misc'):
            return 'repeat'
        return 'bo'


    _raw = pd.read_csv(DATA_CSV)
    _raw['objective'] = campaign1(_raw)['objective']

    _is_blank = _raw['API_Name'].astype(str).str.lower().eq('blank')
    board = _raw[_is_blank | _raw['Exp'].eq('DoEOPT')].copy()

    _mean = board.groupby('Exp')['objective'].mean().sort_values()
    ranked = _mean[_mean < SEP_CUT]
    separated = sorted(_mean[_mean >= SEP_CUT].index)

    # Rank prefixes make the two-column split read as one list of 1..N, not two boards.
    ROW_LABEL = {exp: '{}  {}'.format(i, 'DoE-OPT' if exp == 'DoEOPT' else exp)
                 for i, exp in enumerate(ranked.index, 1)}
    board['row_label'] = board['Exp'].map(ROW_LABEL)
    STAGE = {exp: stage_of(exp) for exp in ranked.index}

    print('{} ranked, {} phase-separated: {}'.format(
        len(ranked), len(separated), ', '.join(separated)))
    print('best {:.4f} ({})   DoE-OPT rank {} of {}'.format(
        ranked.iloc[0], ranked.index[0],
        list(ranked.index).index('DoEOPT') + 1, len(ranked)))
    return ROW_LABEL, STAGE, STAGE_LABEL, board, ranked, separated


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The figure
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
    AXIS_TITLE_SIZE,
    BAR_WIDTH,
    BEST_COLOR,
    BO_COLOR,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    INK_FAINT,
    INK_SOFT,
    LEFT_MARGIN,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    MARKER_RING,
    MARKER_SIZE,
    PANEL_DOMAIN,
    PRELIM_COLOR,
    RIGHT_MARGIN,
    ROW_LABEL,
    SCREEN_COLOR,
    STAGE,
    STAGE_LABEL,
    TICK_SIZE,
    TITLE_SIZE,
    TOP_MARGIN,
    board,
    go,
    ranked,
    separated,
):
    STAGE_COLOR = {
        'bo': BO_COLOR,
        'screen': SCREEN_COLOR,
        'repeat': PRELIM_COLOR,
        'doe': BEST_COLOR,
    }
    STAGE_ORDER = ('bo', 'screen', 'repeat', 'doe')
    STAGE_RANK = {stage: i for i, stage in enumerate(STAGE_ORDER)}

    AXIS_TITLE = 'Objective  (Lower Is Better)'


    def build_leaderboard():
        """Two-panel horizontal leaderboard: bars are means, dots are the repeats behind them."""
        order = list(ranked.index)
        half = (len(order) + 1) // 2
        columns = (('left', order[:half], 'x', 'y'),
                   ('right', order[half:], 'x2', 'y2'))

        shown_reps = board[board['Exp'].isin(ranked.index)]
        x_range = [0.0, float(max(ranked.max(), shown_reps['objective'].max())) * 1.07]

        traces = []
        legended = set()
        for _panel, column, x_axis, y_axis in columns:
            for stage in STAGE_ORDER:
                members = [exp for exp in column if STAGE[exp] == stage]
                if not members:
                    continue
                traces.append(go.Bar(
                    y=[ROW_LABEL[exp] for exp in members],
                    x=[float(ranked[exp]) for exp in members],
                    orientation='h', width=BAR_WIDTH,
                    marker=dict(color=STAGE_COLOR[stage],
                                line=dict(color=INK, width=0.8)),
                    name=STAGE_LABEL[stage], legendgroup=stage,
                    legendrank=1000 + STAGE_RANK[stage],
                    showlegend=stage not in legended,
                    xaxis=x_axis, yaxis=y_axis,
                    hovertemplate='%{y}<br>mean objective %{x:.3f}<extra></extra>',
                ))
                legended.add(stage)

            repeats = board[board['Exp'].isin(column)]
            traces.append(go.Scatter(
                x=repeats['objective'], y=repeats['row_label'], mode='markers',
                marker=dict(size=MARKER_SIZE, color='white',
                            line=dict(color=INK, width=MARKER_RING)),
                name='Individual Repeat', legendgroup='repeat_dot',
                legendrank=1100,
                showlegend='repeat_dot' not in legended,
                xaxis=x_axis, yaxis=y_axis,
                customdata=repeats['Rep'].astype(str),
                hovertemplate='%{y} — rep %{customdata}<br>objective %{x:.3f}<extra></extra>',
            ))
            legended.add('repeat_dot')

        def x_axis_spec(panel, anchor):
            return dict(title=AXIS_TITLE, range=x_range, domain=PANEL_DOMAIN[panel],
                        anchor=anchor, zeroline=False,
                        tickfont=dict(size=TICK_SIZE),
                        title_font=dict(size=AXIS_TITLE_SIZE), **AXIS_COMMON)

        def y_axis_spec(column, anchor):
            # Half a slot of padding top and bottom keeps the end bars off the axis box.
            return dict(type='category', categoryorder='array',
                        categoryarray=[ROW_LABEL[exp] for exp in column][::-1],
                        range=[-0.5, len(column) - 0.5], anchor=anchor,
                        tickfont=dict(size=ANNOTATION_SIZE), **AXIS_COMMON)

        layout = go.Layout(
            title=dict(
                text='<b>Campaign 1 Leaderboard</b><br>'
                     '<span style="font-size:{}px;color:{}">Every Blank Formulation, Scored Then '
                     'Averaged Over Three Repeats, Against The DoE-OPT Screening Optimum  ·  '
                     'Ranked 1–{}</span>'.format(ANNOTATION_SIZE, INK_SOFT, len(ranked)),
                font=dict(size=TITLE_SIZE, color=INK),
                x=0.5, y=0.95, xanchor='center', yanchor='top'),
            xaxis=x_axis_spec('left', 'y'), xaxis2=x_axis_spec('right', 'y2'),
            yaxis=y_axis_spec(order[:half], 'x'),
            yaxis2=y_axis_spec(order[half:], 'x2'),
            annotations=[dict(
                x=0.5, y=-0.225, xref='paper', yref='paper',
                xanchor='center', yanchor='top', showarrow=False,
                text='Not Shown — Phase-Separated:  {}'.format(', '.join(separated)),
                font=dict(size=ANNOTATION_SIZE, color=INK_FAINT))],
            barmode='overlay',
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            width=FIG_WIDTH, height=FIG_HEIGHT,
            margin=dict(l=LEFT_MARGIN, r=RIGHT_MARGIN, t=TOP_MARGIN, b=LEGEND_MARGIN),
            showlegend=True,
            legend=dict(orientation='h', x=0.5, y=-0.145, xanchor='center', yanchor='top',
                        bgcolor='rgba(0, 0, 0, 0)',
                        font=dict(size=LEGEND_SIZE, color=INK)),
        )
        return go.Figure(data=traces, layout=layout)


    leaderboard_figure = build_leaderboard()
    leaderboard_figure
    return (leaderboard_figure,)


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
    leaderboard_figure,
):
    FIGURES = {
        'Campaign1_Leaderboard': (leaderboard_figure, FIG_WIDTH, FIG_HEIGHT),
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
