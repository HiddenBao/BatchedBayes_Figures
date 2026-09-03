# --- Windows + conda DLL guard: must run before *any* other import --------------------------
# The numeric wheels delay-load their DLLs (MKL, OpenBLAS, libstdc++) from <env>/Library/bin,
# which is only on PATH once the environment is *activated*. PyCharm runs the configured conda
# interpreter directly rather than through `conda activate`, so a Run/Debug launch -- and a
# notebook kernel started the same way -- dies with exit code 0xC06D007F / 3228369023,
# STATUS_DELAY_LOAD_FAILED and no traceback.
#
# This sits above `import marimo` on purpose: marimo pulls in the numeric stack itself, so a
# guard inside a cell runs too late to save a plain `python <file>` launch.
import os as _os
import sys as _sys

if _os.name == 'nt':
    _dll_dir = _os.path.join(_sys.prefix, 'Library', 'bin')
    if _os.path.isdir(_dll_dir):
        _os.add_dll_directory(_dll_dir)
        _os.environ['PATH'] = _dll_dir + _os.pathsep + _os.environ.get('PATH', '')
# --------------------------------------------------------------------------------------------

import marimo

__generated_with = '0.24.0'
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # Campaign 2 Leaderboard Figure Suite

    One slide: **the per-API transfer campaign, ranked against what it had to beat** — the three
    revalidated Campaign 1 champions and the DoE-OPT screening baseline.

    Two panels because Campaign 2 ran two independent tracks, A190 and fenofibrate. They share one
    x range so a bar's length means the same thing on either side, but they are two separate
    rankings: a formulation's objective depends on the API it was loaded with.

    Scoring is **score-then-average**, as on the Campaign 1 slide — each repeat scored on its own,
    the bar is the mean of the three, and the white dots are the repeats themselves.

    The objective is Campaign 2's weighted form — `3·size + 2·pdi + 1·zeta + 2·drug_loading +
    3·permeability`, divided by the stability factor, PDI hinged at 0.1 — imported from
    `Figures/objectives.py` rather than restated. It uses all six measured outputs, so unlike the
    Campaign 1 slide it can only rank formulations that were actually loaded with an API.

    **DoE-OPT appears on the A190 panel only.** The DoE screening was run with A190; there is no
    fenofibrate measurement of it to plot, and inventing a comparison across APIs would be worse
    than its absence.
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
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Campaign2_Leaderboard' / 'Output'
    DATA_CSV = REPO_ROOT / 'data' / 'MicroemulsionFormulation_Comprehensive.csv'

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

    The same tokens as the Campaign 1 slide, so the two read as one pair, and the same type scale,
    `FONT_FAMILY` and 2 px black axis box as the `Breaking-the-Boundaries` campaign suites.

    Hues carry **which campaign produced the formulation**:

    | token | hex | what it means |
    | --- | --- | --- |
    | `BO_COLOR` | `#2067F4` | a Campaign 2 formulation |
    | `C1_COLOR` | black | a revalidated Campaign 1 champion |
    | `BEST_COLOR` | `#D55E00` | DoE-OPT, the screening baseline |

    `BEST_COLOR` means DoE-OPT on both slides, which is what lets a reader carry the baseline from
    one to the other.
    """)
    return


@app.cell
def _():
    BO_COLOR = '#2067F4'
    C1_COLOR = 'black'
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

    LEFT_MARGIN = 104
    RIGHT_MARGIN = 40
    TOP_MARGIN = 126      # room for the title, its subtitle and the two panel captions
    LEGEND_MARGIN = 164   # bottom gutter the horizontal legend sits in

    PANEL_DOMAIN = {'A190': (0.0, 0.42), 'Feno': (0.58, 1.0)}

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
        C1_COLOR,
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
        RIGHT_MARGIN,
        TICK_SIZE,
        TITLE_SIZE,
        TOP_MARGIN,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The boards

    One board per API: every Campaign 2 formulation on that track, the three Campaign 1 champions
    revalidated with that API, and — A190 only — DoE-OPT.

    `B4`, `E2` and `F5` are the three Campaign 1 formulations that were re-measured with an API
    loaded, which is the only reason they can appear here at all. This is **not** the same as the
    top three of the Campaign 1 slide: on a score-then-average blank board `D3` ranks second, but
    it was never loaded, so it has no Campaign 2 objective.

    `SEP_CUT` catches phase separation: dividing by the stability factor floored at 0.01 sends a
    fully separated formulation to roughly 100× its stable-side loss, well clear of anything real.
    """)
    return


@app.cell
def _(DATA_CSV, campaign2, pd):
    SEP_CUT = 100.0

    PANELS = ('A190', 'Feno')
    PANEL_TITLE = {'A190': 'A190-Loaded', 'Feno': 'Fenofibrate-Loaded'}
    PANEL_PREFIX = {'A190': 'A-', 'Feno': 'F-'}
    CHAMPIONS = {'A190': ('E2_A', 'F5_A', 'B4_A'), 'Feno': ('E2_F', 'F5_F', 'B4_F')}
    DOE = 'DoEOPT'

    SERIES_LABEL = {
        'c2': 'Campaign 2',
        'c1': 'Campaign 1 Champion (Revalidated)',
        'doe': 'DoE-OPT (Screening Baseline)',
    }

    _raw = pd.read_csv(DATA_CSV)
    _raw['objective'] = campaign2(_raw)['objective']


    def series_of(api: str, exp: str) -> str:
        """Return the campaign that produced `exp` on `api`'s board; hue carries this."""
        if exp == DOE:
            return 'doe'
        return 'c1' if exp in CHAMPIONS[api] else 'c2'


    def build_board(api: str):
        """Return (ranked, separated, row_label, repeats) for one API's leaderboard."""
        rows = _raw[_raw['Exp'].str.startswith(PANEL_PREFIX[api])
                    | _raw['Exp'].isin(CHAMPIONS[api])
                    | (_raw['Exp'].eq(DOE) & (api == 'A190'))].copy()
        mean_objective = rows.groupby('Exp')['objective'].mean().sort_values()
        ranked = mean_objective[mean_objective < SEP_CUT]
        separated = sorted(mean_objective[mean_objective >= SEP_CUT].index)
        row_label = {exp: '{}  {}'.format(i, 'DoE-OPT' if exp == DOE else exp)
                     for i, exp in enumerate(ranked.index, 1)}
        repeats = rows[rows['Exp'].isin(ranked.index)].copy()
        repeats['row_label'] = repeats['Exp'].map(row_label)
        return ranked, separated, row_label, repeats


    BOARDS = {api: build_board(api) for api in PANELS}

    for _api in PANELS:
        _ranked, _separated, _, _ = BOARDS[_api]
        print('{}: {} ranked, best {:.3f} ({}), {} phase-separated {}'.format(
            _api, len(_ranked), _ranked.iloc[0], _ranked.index[0],
            len(_separated), _separated))
    return BOARDS, PANELS, PANEL_TITLE, SERIES_LABEL, series_of


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## The figure""")
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
    AXIS_TITLE_SIZE,
    BAR_WIDTH,
    BEST_COLOR,
    BO_COLOR,
    BOARDS,
    C1_COLOR,
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
    PANELS,
    PANEL_DOMAIN,
    PANEL_TITLE,
    RIGHT_MARGIN,
    SERIES_LABEL,
    TICK_SIZE,
    TITLE_SIZE,
    TOP_MARGIN,
    go,
    series_of,
):
    SERIES_COLOR = {'c2': BO_COLOR, 'c1': C1_COLOR, 'doe': BEST_COLOR}
    SERIES_ORDER = ('c2', 'c1', 'doe')
    SERIES_RANK = {series: i for i, series in enumerate(SERIES_ORDER)}

    AXIS_TITLE = 'Objective  (Lower Is Better)'
    PANEL_AXES = {'A190': ('x', 'y'), 'Feno': ('x2', 'y2')}


    def build_leaderboard():
        """Two API boards side by side: bars are means, dots are the repeats behind them."""
        # One x range across both panels, spanning bars and repeat dots alike. The objective can
        # go slightly negative -- PDI and permeability both have a bonus side -- so this is not
        # anchored at zero.
        low = min(min(r.min() for r, _, _, _ in BOARDS.values()),
                  min(d['objective'].min() for _, _, _, d in BOARDS.values()))
        high = max(max(r.max() for r, _, _, _ in BOARDS.values()),
                   max(d['objective'].max() for _, _, _, d in BOARDS.values()))
        pad = (high - low) * 0.05
        x_range = [low - pad, high + pad]

        traces = []
        shapes = []
        annotations = []
        legended = set()

        for api in PANELS:
            ranked, _separated, row_label, repeats = BOARDS[api]
            x_axis, y_axis = PANEL_AXES[api]

            for series in SERIES_ORDER:
                members = [exp for exp in ranked.index if series_of(api, exp) == series]
                if not members:
                    continue
                traces.append(go.Bar(
                    y=[row_label[exp] for exp in members],
                    x=[float(ranked[exp]) for exp in members],
                    orientation='h', width=BAR_WIDTH,
                    marker=dict(color=SERIES_COLOR[series],
                                line=dict(color=INK, width=0.8)),
                    name=SERIES_LABEL[series], legendgroup=series,
                    legendrank=1000 + SERIES_RANK[series],
                    showlegend=series not in legended,
                    xaxis=x_axis, yaxis=y_axis,
                    hovertemplate='%{y}<br>mean objective %{x:.3f}<extra></extra>',
                ))
                legended.add(series)

            traces.append(go.Scatter(
                x=repeats['objective'], y=repeats['row_label'], mode='markers',
                marker=dict(size=MARKER_SIZE, color='white',
                            line=dict(color=INK, width=MARKER_RING)),
                name='Individual Repeat', legendgroup='repeat_dot', legendrank=1100,
                showlegend='repeat_dot' not in legended,
                xaxis=x_axis, yaxis=y_axis,
                customdata=repeats['Rep'].astype(str),
                hovertemplate='%{y} — rep %{customdata}<br>objective %{x:.3f}<extra></extra>',
            ))
            legended.add('repeat_dot')

            # Zero is a real landmark here: a bar to its left is a formulation the objective
            # actually rewards rather than merely penalises least.
            shapes.append(dict(type='line', x0=0, x1=0, y0=0, y1=1,
                               xref=x_axis, yref='{} domain'.format(y_axis),
                               line=dict(color=INK_FAINT, width=1), layer='below'))

            # yref='paper' is the plot area, not the canvas -- above it means greater than 1.
            low_x, high_x = PANEL_DOMAIN[api]
            annotations.append(dict(
                x=(low_x + high_x) / 2.0, y=1.035, xref='paper', yref='paper',
                xanchor='center', yanchor='bottom', showarrow=False,
                text='<b>{}</b>'.format(PANEL_TITLE[api]),
                font=dict(size=AXIS_TITLE_SIZE, color=INK)))

        separated_note = '  ·  '.join(
            '{}: {}'.format(api, ', '.join(BOARDS[api][1]))
            for api in PANELS if BOARDS[api][1])
        annotations.append(dict(
            x=0.5, y=-0.225, xref='paper', yref='paper',
            xanchor='center', yanchor='top', showarrow=False,
            text='Not Shown — Phase-Separated:  {}      DoE-OPT Was Screened With A190 '
                 'Only.'.format(separated_note),
            font=dict(size=ANNOTATION_SIZE, color=INK_FAINT)))

        def x_axis_spec(api, anchor):
            return dict(title=AXIS_TITLE, range=x_range, domain=PANEL_DOMAIN[api],
                        anchor=anchor, zeroline=False,
                        tickfont=dict(size=TICK_SIZE),
                        title_font=dict(size=AXIS_TITLE_SIZE), **AXIS_COMMON)

        def y_axis_spec(api, anchor):
            ranked, _separated, row_label, _repeats = BOARDS[api]
            # Half a slot of padding top and bottom keeps the end bars off the axis box.
            return dict(type='category', categoryorder='array',
                        categoryarray=[row_label[exp] for exp in ranked.index][::-1],
                        range=[-0.5, len(ranked) - 0.5], anchor=anchor,
                        tickfont=dict(size=ANNOTATION_SIZE), **AXIS_COMMON)

        layout = go.Layout(
            title=dict(
                text='<b>Campaign 2 Leaderboard</b><br>'
                     '<span style="font-size:{}px;color:{}">Every Loaded Formulation, Scored Then '
                     'Averaged Over Three Repeats, With The Revalidated Campaign 1 Champions And '
                     'The DoE-OPT Baseline</span>'.format(ANNOTATION_SIZE, INK_SOFT),
                font=dict(size=TITLE_SIZE, color=INK),
                x=0.5, y=0.96, xanchor='center', yanchor='top'),
            xaxis=x_axis_spec('A190', 'y'), xaxis2=x_axis_spec('Feno', 'y2'),
            yaxis=y_axis_spec('A190', 'x'), yaxis2=y_axis_spec('Feno', 'x2'),
            shapes=shapes, annotations=annotations,
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
        'Campaign2_Leaderboard': (leaderboard_figure, FIG_WIDTH, FIG_HEIGHT),
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


if __name__ == '__main__':
    app.run()
