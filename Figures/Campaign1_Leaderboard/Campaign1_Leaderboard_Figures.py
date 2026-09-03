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
    give different numbers. The dark dots are the individual repeats, so every bar is visibly the
    mean of its own dots.

    The objective is Campaign 1's **as published** — paper Eq. 1–4, equal weights, ×10 phase
    separation, PDI hinged at 0.3, imported from `Figures/objectives.py` rather than restated. It
    is physicochemical only, which is what makes blank formulations and the A190-loaded DoE-OPT
    baseline comparable at all: neither drug loading nor permeability enters the score.

    Phase-separated formulations score around 31 and would flatten everything else, so they are
    named in the subtitle rather than plotted.

    The chrome is upstream's — `BatchedBayes:analysis/campaign_comparison.py` — not this repo's
    usual `Breaking-the-Boundaries` house style. See **Shared chrome** below.
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

    Transcribed from upstream's own leaderboards — `BatchedBayes:analysis/campaign_comparison.py`,
    `plotly_layout` / `axis_style` / `legend_below` and `fig_leaderboard`. Warm off-white ground,
    faint horizontal gridlines behind the bars, a hairline `#c3c2b7` axis with no mirror, flat
    unoutlined bars and dark repeat dots. Deliberately *not* this repo's usual
    `Breaking-the-Boundaries` chrome: these slides sit beside the upstream analysis figures.

    Hues carry **campaign stage** rather than formulation identity, using upstream's three-colour
    palette:

    | token | hex | what it means |
    | --- | --- | --- |
    | `BO_COLOR` | `#1baf7a` | an optimiser-chosen batch, A–E — upstream's Campaign 1 green |
    | `SCREEN_COLOR` | `#898781` | the quasi-random screen that seeded the surrogate |
    | `PRELIM_COLOR` | `#c3c2b7` | repeats of prior optima — present, deliberately quiet |
    | `BEST_COLOR` | `#2a78d6` | DoE-OPT, the baseline the campaign had to beat |

    Five BO rounds are **one** colour on purpose. They are one campaign under one policy, and
    giving each round its own hue would claim a distinction the method does not make.
    """)
    return


@app.cell
def _():
    # Upstream's palette, value for value: DoE-OPT blue, Campaign 1 green, Campaign 2 amber.
    BO_COLOR = '#1baf7a'
    SCREEN_COLOR = '#898781'
    PRELIM_COLOR = '#c3c2b7'
    BEST_COLOR = '#2a78d6'

    INK = '#0b0b0b'
    SECOND = '#52514e'
    MUTED = '#898781'
    GRID = '#e1e0d9'
    SURFACE = '#fcfcfb'
    AXIS_LINE = '#c3c2b7'

    # Upstream's type scale: title / axis title / tick / legend / annotation.
    TITLE_SIZE = 16
    AXIS_TITLE_SIZE = 12
    TICK_SIZE = 11
    LEGEND_SIZE = 11
    ANNOTATION_SIZE = 10
    SUBTITLE_SIZE = 11

    FONT_FAMILY = 'sans-serif'

    MARKER_SIZE = 9
    MARKER_RING = 1.2
    BAR_WIDTH = 0.62

    AXIS_STANDOFF = 12
    YLABEL_STANDOFF = 10

    LEFT_MARGIN = 90
    RIGHT_MARGIN = 60
    TOP_MARGIN = 70
    LEGEND_MARGIN = 130   # bottom gutter the horizontal legend sits in

    # Thirty rows will not read at 720 px in one column, so the ranking runs down the left panel
    # and continues down the right. Both panels share one x range, so a bar's length means the
    # same thing on either side.
    PANEL_DOMAIN = {'left': (0.0, 0.42), 'right': (0.58, 1.0)}

    # Upstream `axis_style`: hairline axis, outside ticks, no mirror, gridlines from GRID.
    AXIS_COMMON = dict(
        gridcolor=GRID, gridwidth=0.8, zeroline=False, linecolor=AXIS_LINE,
        showline=True, mirror=False, ticks='outside', tickcolor=MUTED,
    )
    return (
        AXIS_COMMON,
        AXIS_LINE,
        AXIS_STANDOFF,
        AXIS_TITLE_SIZE,
        BAR_WIDTH,
        BEST_COLOR,
        BO_COLOR,
        FONT_FAMILY,
        INK,
        LEFT_MARGIN,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        MARKER_RING,
        MARKER_SIZE,
        MUTED,
        PANEL_DOMAIN,
        PRELIM_COLOR,
        RIGHT_MARGIN,
        SCREEN_COLOR,
        SECOND,
        SUBTITLE_SIZE,
        SURFACE,
        TICK_SIZE,
        TITLE_SIZE,
        TOP_MARGIN,
        YLABEL_STANDOFF,
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
    AXIS_COMMON,
    AXIS_LINE,
    AXIS_STANDOFF,
    AXIS_TITLE_SIZE,
    BAR_WIDTH,
    BEST_COLOR,
    BO_COLOR,
    FIG_HEIGHT,
    FIG_WIDTH,
    FONT_FAMILY,
    INK,
    LEFT_MARGIN,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    MARKER_RING,
    MARKER_SIZE,
    MUTED,
    PANEL_DOMAIN,
    PRELIM_COLOR,
    RIGHT_MARGIN,
    ROW_LABEL,
    SCREEN_COLOR,
    SECOND,
    STAGE,
    STAGE_LABEL,
    SUBTITLE_SIZE,
    SURFACE,
    TICK_SIZE,
    TITLE_SIZE,
    TOP_MARGIN,
    YLABEL_STANDOFF,
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

    AXIS_TITLE = 'Mean Objective Of Individually-Scored Repeats  (Lower Is Better)'


    def build_leaderboard():
        """Two-panel horizontal leaderboard: bars are means, dots are the repeats behind them."""
        order = list(ranked.index)
        half = (len(order) + 1) // 2
        columns = (('left', order[:half], 'x', 'y'),
                   ('right', order[half:], 'x2', 'y2'))

        shown_reps = board[board['Exp'].isin(ranked.index)]
        x_range = [0.0, float(max(ranked.max(), shown_reps['objective'].max())) * 1.1]

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
                    marker_color=STAGE_COLOR[stage],
                    name=STAGE_LABEL[stage], legendgroup=stage,
                    legendrank=1000 + STAGE_RANK[stage],
                    showlegend=stage not in legended,
                    xaxis=x_axis, yaxis=y_axis,
                    hovertemplate='%{y}<br>mean per-rep objective %{x:.3f}<extra></extra>',
                ))
                legended.add(stage)

            repeats = board[board['Exp'].isin(column)]
            traces.append(go.Scatter(
                x=repeats['objective'], y=repeats['row_label'], mode='markers',
                marker=dict(size=MARKER_SIZE, color=INK, opacity=0.7,
                            line=dict(color=SURFACE, width=MARKER_RING)),
                name='Individual Rep', legendgroup='repeat_dot',
                legendrank=1100,
                showlegend='repeat_dot' not in legended,
                xaxis=x_axis, yaxis=y_axis,
                customdata=repeats['Rep'].astype(str),
                hovertemplate='%{y} — rep %{customdata}'
                              '<br>per-rep objective %{x:.3f}<extra></extra>',
            ))
            legended.add('repeat_dot')

        def x_axis_spec(panel, anchor):
            return dict(title=AXIS_TITLE, range=x_range, domain=PANEL_DOMAIN[panel],
                        anchor=anchor, showgrid=True,
                        tickfont=dict(size=TICK_SIZE, color=MUTED),
                        title_font=dict(size=AXIS_TITLE_SIZE, color=SECOND),
                        title_standoff=AXIS_STANDOFF, **AXIS_COMMON)

        def y_axis_spec(column, anchor):
            # Half a slot of padding top and bottom keeps the end bars off the axis.
            return dict(type='category', categoryorder='array',
                        categoryarray=[ROW_LABEL[exp] for exp in column][::-1],
                        range=[-0.5, len(column) - 0.5], anchor=anchor, showgrid=False,
                        ticklabelstandoff=YLABEL_STANDOFF,
                        tickfont=dict(size=TICK_SIZE, color=INK), **AXIS_COMMON)

        # Upstream draws the zero reference as a per-panel vline; as shapes, one per x axis.
        zero_lines = [dict(type='line', x0=0, x1=0, y0=0, y1=1,
                           xref=x_axis, yref='{} domain'.format(y_axis),
                           line=dict(color=AXIS_LINE, width=1))
                      for _p, _c, x_axis, y_axis in columns]

        layout = go.Layout(
            template='none',
            title=dict(
                text='<b>Campaign 1 — Leaderboard</b>  (score-then-average)<br>'
                     '<span style="font-size:{}px;color:{}">Every Blank Formulation Against The '
                     'DoE-OPT Screening Optimum, Ranked 1–{}'
                     '  ·  Not Shown (Phase-Separated): {}</span>'.format(
                         SUBTITLE_SIZE, MUTED, len(ranked), ', '.join(separated)),
                font=dict(size=TITLE_SIZE, color=INK),
                x=0.01, xanchor='left'),
            xaxis=x_axis_spec('left', 'y'), xaxis2=x_axis_spec('right', 'y2'),
            yaxis=y_axis_spec(order[:half], 'x'),
            yaxis2=y_axis_spec(order[half:], 'x2'),
            shapes=zero_lines,
            barmode='overlay',
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font=dict(family=FONT_FAMILY, size=12, color=INK),
            width=FIG_WIDTH, height=FIG_HEIGHT,
            margin=dict(l=LEFT_MARGIN, r=RIGHT_MARGIN, t=TOP_MARGIN, b=LEGEND_MARGIN),
            showlegend=True,
            # Upstream `legend_below`: a fixed 60 px gap under the plot area, in paper units.
            legend=dict(orientation='h', x=0.5, xanchor='center', yanchor='top',
                        y=-(60 / max(FIG_HEIGHT - TOP_MARGIN - LEGEND_MARGIN, 120)),
                        bgcolor='rgba(0, 0, 0, 0)',
                        font=dict(size=LEGEND_SIZE, color=SECOND)),
            hoverlabel=dict(font=dict(family=FONT_FAMILY, size=12)),
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
