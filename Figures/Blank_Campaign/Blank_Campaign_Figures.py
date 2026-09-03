import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Blank Campaign Figure Suite — Act 1 of the deck

    The **first** campaign: batched Bayesian optimisation run on *blank* microemulsions, with no
    API present. These slides are the setup for everything after them — they establish what the
    optimiser was searching, how it spent its experiments, and what it found before the drug was
    ever loaded.

    Two figures, both exported to `Figures/Blank_Campaign/Output/` as SVG:

    * `Blank_Campaign_Progress` — every blank formulation in campaign order, its objective, and the
      running best. A strip beneath the axis carries the phase-separated runs, which have no
      meaningful objective to plot.
    * `Blank_Batch_Composition` — which oil, surfactant and cosurfactant each batch selected. This
      is the figure that shows `--max_per_category 1` doing its job early and the optimiser
      concentrating late.

    ## The objective is a loss, and on blanks it is the physical-quality loss

    Scoring comes from `score_dataset.compute_component_scores`, imported rather than restated so
    this suite cannot drift from the rest of the repository:

    $$\text{objective}=\frac{3\,s_\text{size}+2\,s_\text{PDI}+1\,s_\text{zeta}+2\,s_\text{DL}+3\,s_\text{perm}}{\max(1-\text{phase\_sep},\,0.01)}$$

    Blank formulations carry **no** `Drug_Loading` and **no** `Permeability` — those cannot be
    measured without an API — so both terms score 0 and the expression collapses to the
    physicochemical objective on size, PDI and zeta. That is exactly the metric Campaign 1 was
    optimised on, so nothing is being retrofitted here: the number on the slide is the number the
    optimiser saw.

    **Every formulation is three repeats, scored then averaged.** Each repeat is scored on its own
    and the reported objective is the mean of the three, matching `analysis/campaign_comparison.py`.
    The score terms hinge (100 nm, |zeta| = 10 mV, PDI = 0.1), so this is not the same as averaging
    the measurements first — and it is the order that prices reproducibility.

    ## Phase separation is drawn, not plotted

    A phase-separated formulation divides by `max(1 - 1, 0.01) = 0.01`, which puts its objective at
    ~4400 — four orders of magnitude above every stable run. Plotting that on the same axis flattens
    the entire campaign into a line at zero, and a log axis buys legibility by making a *failure*
    look like a *value*. Neither is honest on a slide. The main panel therefore shows the stable
    runs on a linear axis, and a strip beneath it marks which experiments separated. The strip is
    the same width as the axis, so a column reads straight down.

    ## Campaign order comes from the file, not from the labels

    `MicroemulsionFormulation_Comprehensive.csv` stores the blank rows in the order they were run,
    which the `Exp` labels do not recover on their own (`B1` precedes `B4`, but `A3` was the fifth
    experiment of round A, not the third). The x-axis is therefore the row order of the file,
    grouped into the stages below.

    > **Confirm before presenting:** the seven `Misc*` rows sit ahead of `Ran1` in the file and are
    > labelled *Preliminary* here. If they were something else — a repeatability check, an
    > unrelated screen — change `STAGE_LABELS` and re-run; nothing else depends on the name.

    ## Environment

    A [marimo](https://marimo.io) notebook, so it is a plain Python module and the interpreter that
    launches it *is* the kernel. Run it from the **`BatchedBayes`** conda environment:

    ```
    conda run -n BatchedBayes marimo edit Figures/Blank_Campaign/Blank_Campaign_Figures.py
    conda run -n BatchedBayes python Figures/Blank_Campaign/Blank_Campaign_Figures.py
    ```

    ## Style

    Palette, type scale, canvas and export conventions follow the `Breaking-the-Boundaries` figure
    suites, value for value — white ground, a 2 px black mirrored axis box, no gridlines, five type
    sizes, horizontal legend in a bottom gutter. This suite does **not** share the muted tokens of
    `analysis/campaign_comparison.py`; that notebook is a scrolling analysis document, these are
    projected slides.
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
    from plotly.subplots import make_subplots

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
    return Path, go, make_subplots, np, pd, sys


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Paths, canvas and export

    `REPO_ROOT` is found by looking for `BayesianOptimization/data` above this file rather than by
    counting `..`, so the notebook survives being moved one level.

    The canvases are the campaign suites' 1000 × 700, except the progress figure, which is 1000 × 800
    — the extra 100 px is the phase-separation strip, the same allowance
    `Complete_Figures.py` makes for its search-space strip.
    """)
    return


@app.cell
def _(Path, sys):
    def _find_repo_root(start):
        for candidate in (start,) + tuple(start.parents):
            if (candidate / 'BayesianOptimization' / 'data').is_dir():
                return candidate
        raise FileNotFoundError(
            'Could not locate BayesianOptimization/data above {}'.format(start))


    try:
        _HERE = Path(__file__).resolve().parent
    except NameError:
        _HERE = Path.cwd()

    REPO_ROOT = _find_repo_root(_HERE)
    OUTPUT_DIR = REPO_ROOT / 'Figures' / 'Blank_Campaign' / 'Output'
    DATA_CSV = REPO_ROOT / 'BayesianOptimization' / 'data' / 'MicroemulsionFormulation_Comprehensive.csv'

    # score_dataset lives at the repository root and is the single source of the objective.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from score_dataset import compute_component_scores

    EXPORT_FORMATS = ('svg',)
    FIG_WIDTH = 1000
    FIG_HEIGHT = 700
    PROGRESS_FIG_HEIGHT = 800   # the campaign, plus the phase-separation strip under it
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
        PROGRESS_FIG_HEIGHT,
        compute_component_scores,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shared chrome

    The type scale, `FONT_FAMILY` and the axis box are the `Breaking-the-Boundaries` campaign
    suites' own, value for value, so a deck that mixes these slides with those reads as one system.

    Hues carry **campaign stage** here rather than campaign variant:

    | token | hex | what it means |
    | --- | --- | --- |
    | `PRELIM_COLOR` | `#C4C4C4` | preliminary runs — present, deliberately quiet |
    | `SCREEN_COLOR` | black | the random screen that seeded the surrogate |
    | `BO_COLOR` | `#2067F4` | every optimiser-chosen batch |
    | `BEST_COLOR` | `#D55E00` | the running best — a derived line, not a run |
    | `FAIL_COLOR` | `#6C3FA0` | phase separation — not a run outcome on the objective scale |

    Five BO rounds are **one** colour on purpose. They are one campaign under one policy; giving
    each round its own hue would claim a distinction the method does not make, and the round
    boundaries are already drawn as rules.
    """)
    return


@app.cell
def _(FIG_HEIGHT, FIG_WIDTH, go, np):
    PRELIM_COLOR = '#C4C4C4'
    SCREEN_COLOR = 'black'
    BO_COLOR = '#2067F4'
    BEST_COLOR = '#D55E00'
    FAIL_COLOR = '#6C3FA0'

    INK = 'black'
    INK_SOFT = 'rgba(0, 0, 0, 0.55)'
    INK_FAINT = 'rgba(0, 0, 0, 0.38)'
    RULE = 'rgba(0, 0, 0, 0.22)'
    SCREEN_BAND = 'rgba(0, 0, 0, 0.055)'

    TITLE_SIZE = 20
    AXIS_TITLE_SIZE = 18
    TICK_SIZE = 18
    LEGEND_SIZE = 14
    ANNOTATION_SIZE = 14

    FONT_FAMILY = 'Open Sans, verdana, arial, sans-serif'

    MARKER_SIZE = 9
    MARKER_RING = 2
    LINE_WIDTH = 2.5
    ROUND_RULE_WIDTH = 1.2
    ROUND_RULE_DASH = 'dot'

    LEFT_MARGIN = 110
    LEGEND_MARGIN = 150
    Y_TARGET_TICKS = 8
    Y_MINOR_SPLIT = 2


    def fade(hex_color, alpha):
        '''Convert '#RRGGBB' to an rgba() string at the given alpha.'''
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return 'rgba({}, {}, {}, {})'.format(r, g, b, alpha)


    def nice_dtick(span, target_ticks=7):
        '''Pick a human-readable tick interval covering `span` in roughly `target_ticks` steps.'''
        raw = span / float(target_ticks)
        magnitude = 10 ** np.floor(np.log10(raw))
        for step in (1, 2, 2.5, 5, 10):
            if raw <= step * magnitude:
                return float(step * magnitude)
        return float(10 * magnitude)


    def axis_range(series_list, pad_fraction=0.08):
        '''Padded [min, max] across several series, so nothing sits on the axis box.'''
        stacked = np.concatenate([np.asarray(s, dtype=float).ravel() for s in series_list])
        stacked = stacked[np.isfinite(stacked)]
        low, high = float(stacked.min()), float(stacked.max())
        pad = (high - low) * pad_fraction
        return [low - pad, high + pad]


    AXIS_COMMON = dict(
        linecolor=INK, tickcolor=INK, color=INK,
        ticks='outside', showline=True, showgrid=False, mirror=True, linewidth=2,
        tickfont=dict(size=TICK_SIZE), title_font=dict(size=AXIS_TITLE_SIZE),
    )


    def blank_layout(width=FIG_WIDTH, height=FIG_HEIGHT):
        '''A fixed pixel grid: one data unit is one exported pixel, origin top left.'''
        hidden = dict(visible=False, showgrid=False, zeroline=False,
                      fixedrange=True, constrain='domain')
        return go.Layout(
            xaxis=dict(range=[0, width], **hidden),
            yaxis=dict(range=[height, 0], **hidden),
            width=width, height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='white', paper_bgcolor='white',
            showlegend=False,
            font=dict(family=FONT_FAMILY, color=INK),
        )


    def text(fig, x, baseline, body, size=ANNOTATION_SIZE, color=INK_SOFT,
             anchor='left', weight=None, angle=0):
        '''Place text at an SVG-style baseline, the way the layout numbers are written.'''
        body = '<b>{}</b>'.format(body) if weight == 'bold' else body
        fig.add_annotation(
            x=x, y=baseline - size * 0.35, text=body, showarrow=False,
            xref='x', yref='y', xanchor=anchor, yanchor='middle', textangle=angle,
            align={'left': 'left', 'right': 'right', 'center': 'center'}[anchor],
            font=dict(size=size, color=color, family=FONT_FAMILY),
        )


    def rule(fig, x0, y0, x1, y1, color=RULE, width=1, dash=None):
        fig.add_shape(type='line', x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=color, width=width, dash=dash), layer='below')


    def box(fig, x0, y0, x1, y1, fill, line=None, width=1, dash=None, layer='below'):
        fig.add_shape(type='rect', x0=x0, y0=y0, x1=x1, y1=y1, fillcolor=fill,
                      line=dict(color=line or 'rgba(0,0,0,0)', width=width if line else 0,
                                dash=dash),
                      layer=layer)
    return (
        ANNOTATION_SIZE,
        AXIS_COMMON,
        AXIS_TITLE_SIZE,
        BEST_COLOR,
        BO_COLOR,
        FAIL_COLOR,
        FONT_FAMILY,
        INK,
        INK_FAINT,
        INK_SOFT,
        LEFT_MARGIN,
        LEGEND_MARGIN,
        LEGEND_SIZE,
        LINE_WIDTH,
        MARKER_RING,
        MARKER_SIZE,
        PRELIM_COLOR,
        ROUND_RULE_DASH,
        ROUND_RULE_WIDTH,
        RULE,
        SCREEN_BAND,
        SCREEN_COLOR,
        TICK_SIZE,
        TITLE_SIZE,
        Y_MINOR_SPLIT,
        Y_TARGET_TICKS,
        axis_range,
        blank_layout,
        box,
        fade,
        nice_dtick,
        rule,
        text,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The campaign

    One row per formulation, in the order the file records them. `stage` is the campaign phase,
    `obj` the score-then-average objective over the formulation's three repeats, and `separated`
    whether all three repeats phase-separated.

    A formulation is called separated when its mean `Phase_Sep` is at least 0.5 — in this dataset
    every one of them is unanimous across the three repeats, so the threshold never actually
    arbitrates anything. It is written as a threshold rather than an equality only so that a future
    partially-separating formulation lands somewhere defined instead of being silently plotted at
    ~2200 in the middle of the panel.
    """)
    return


@app.cell
def _(DATA_CSV, compute_component_scores, pd):
    OUTPUT_COLS = ['Droplet_Size', 'PDI', 'Zeta_P', 'Phase_Sep', 'Drug_Loading', 'Permeability']

    STAGE_PRELIM = 'Preliminary'
    STAGE_SCREEN = 'Random Screen'

    STAGE_LABELS = {
        STAGE_PRELIM: 'Preliminary',
        STAGE_SCREEN: 'Random Screen',
    }


    def _stage(exp):
        if exp.startswith('Misc'):
            return STAGE_PRELIM
        if exp.startswith('Ran'):
            return STAGE_SCREEN
        return 'Round {}'.format(exp[0])


    _raw = pd.read_csv(DATA_CSV)
    _blank = _raw[_raw['API_Name'] == 'blank'].copy()

    # compute_component_scores works row-wise on the six outputs; Drug_Loading and Permeability are
    # NaN on every blank row and score 0, which is what collapses this to the physical objective.
    _scores = compute_component_scores(_blank[OUTPUT_COLS].to_numpy(dtype=float))
    _blank = pd.concat([_blank.reset_index(drop=True), _scores], axis=1)

    # File order is run order. groupby(sort=False) preserves it; first-seen index becomes the x-axis.
    _grouped = _blank.groupby('Exp', sort=False)
    CAMPAIGN = _grouped.agg(
        obj=('objective', 'mean'),
        size_nm=('Droplet_Size', 'mean'),
        pdi=('PDI', 'mean'),
        zeta=('Zeta_P', 'mean'),
        sep=('Phase_Sep', 'mean'),
        reps=('objective', 'size'),
        oil=('Oil', 'first'),
        surfactant=('Surfactant', 'first'),
        cosurfactant=('Cosurfactant', 'first'),
    ).reset_index()

    CAMPAIGN['stage'] = [_stage(e) for e in CAMPAIGN['Exp']]
    CAMPAIGN['separated'] = CAMPAIGN['sep'] >= 0.5
    CAMPAIGN['n'] = range(1, len(CAMPAIGN) + 1)

    # Running best over the stable runs only: a separated formulation is not a candidate best.
    _running = []
    _best = float('inf')
    for _stable, _value in zip(~CAMPAIGN['separated'], CAMPAIGN['obj']):
        if _stable:
            _best = min(_best, float(_value))
        _running.append(_best)
    CAMPAIGN['running_best'] = _running

    STAGE_ORDER = list(dict.fromkeys(CAMPAIGN['stage']))
    BO_ROUNDS = [s for s in STAGE_ORDER if s.startswith('Round')]

    print('{} formulations, {} repeats each'.format(len(CAMPAIGN), CAMPAIGN['reps'].unique()))
    print('stages: {}'.format(STAGE_ORDER))
    print('separated: {} of {}'.format(int(CAMPAIGN['separated'].sum()), len(CAMPAIGN)))
    print('best stable objective: {:.3f} ({})'.format(
        CAMPAIGN.loc[~CAMPAIGN['separated'], 'obj'].min(),
        CAMPAIGN.loc[CAMPAIGN.loc[~CAMPAIGN['separated'], 'obj'].idxmin(), 'Exp']))
    return BO_ROUNDS, CAMPAIGN, STAGE_ORDER, STAGE_PRELIM, STAGE_SCREEN


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Figure 1 — `Blank_Campaign_Progress`

    The campaign as it happened: experiment number across, objective up, running best stepping down
    behind the points. Stage boundaries are dotted rules with the stage named above the panel, so
    the reader can see where the optimiser took over from the random screen without consulting a
    legend.

    The strip beneath carries the phase-separated formulations. They are absent from the main panel
    by construction — no objective they could be drawn at is both on-scale and truthful.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_COMMON,
    BEST_COLOR,
    BO_COLOR,
    CAMPAIGN,
    FAIL_COLOR,
    FONT_FAMILY,
    INK,
    INK_SOFT,
    LEFT_MARGIN,
    LEGEND_MARGIN,
    LEGEND_SIZE,
    LINE_WIDTH,
    MARKER_RING,
    MARKER_SIZE,
    PRELIM_COLOR,
    PROGRESS_FIG_HEIGHT,
    FIG_WIDTH,
    ROUND_RULE_DASH,
    ROUND_RULE_WIDTH,
    RULE,
    SCREEN_BAND,
    SCREEN_COLOR,
    STAGE_ORDER,
    STAGE_PRELIM,
    STAGE_SCREEN,
    TICK_SIZE,
    TITLE_SIZE,
    Y_MINOR_SPLIT,
    Y_TARGET_TICKS,
    axis_range,
    fade,
    go,
    make_subplots,
    nice_dtick,
):
    def _stage_color(stage):
        if stage == STAGE_PRELIM:
            return PRELIM_COLOR
        if stage == STAGE_SCREEN:
            return SCREEN_COLOR
        return BO_COLOR


    def build_progress():
        stable = CAMPAIGN[~CAMPAIGN['separated']]
        failed = CAMPAIGN[CAMPAIGN['separated']]

        x_range = [0.4, len(CAMPAIGN) + 0.6]
        y_range = axis_range([stable['obj']])
        y_range[0] = max(0.0, y_range[0])
        y_dtick = nice_dtick(y_range[1] - y_range[0], Y_TARGET_TICKS)

        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.84, 0.16], vertical_spacing=0.045,
        )

        # --- Stage bands and boundaries -------------------------------------------------------
        for stage in STAGE_ORDER:
            block = CAMPAIGN[CAMPAIGN['stage'] == stage]
            left, right = block['n'].min() - 0.5, block['n'].max() + 0.5
            if stage == STAGE_SCREEN:
                fig.add_shape(type='rect', x0=left, x1=right, y0=y_range[0], y1=y_range[1],
                              fillcolor=SCREEN_BAND, line=dict(width=0), layer='below',
                              row=1, col=1)
            if left > x_range[0]:
                fig.add_shape(type='line', x0=left, x1=left, y0=y_range[0], y1=y_range[1],
                              line=dict(color=RULE, width=ROUND_RULE_WIDTH, dash=ROUND_RULE_DASH),
                              layer='below', row=1, col=1)
            fig.add_annotation(
                x=(left + right) / 2, y=y_range[1], yshift=13, text=stage, showarrow=False,
                xref='x', yref='y', xanchor='center', yanchor='bottom',
                font=dict(size=ANNOTATION_SIZE, color=INK_SOFT, family=FONT_FAMILY),
            )

        # --- Running best ---------------------------------------------------------------------
        fig.add_trace(go.Scatter(
            x=CAMPAIGN['n'], y=CAMPAIGN['running_best'], mode='lines', name='Running Best',
            line=dict(color=BEST_COLOR, width=LINE_WIDTH, shape='hv'),
            hovertemplate='running best<br>Exp %{x}<br>%{y:.3f}<extra></extra>',
        ), row=1, col=1)

        # --- The runs -------------------------------------------------------------------------
        for stage, label in ((STAGE_PRELIM, STAGE_PRELIM), (STAGE_SCREEN, STAGE_SCREEN),
                             ('Round', 'Optimiser Batches')):
            block = stable[stable['stage'].str.startswith(stage)]
            if block.empty:
                continue
            color = _stage_color(stage if stage != 'Round' else 'Round A')
            hollow = stage == STAGE_SCREEN
            fig.add_trace(go.Scatter(
                x=block['n'], y=block['obj'], mode='markers', name=label,
                marker=dict(size=MARKER_SIZE,
                            color='white' if hollow else color,
                            line=dict(color=color, width=MARKER_RING)),
                customdata=block['Exp'],
                hovertemplate='%{customdata}<br>Exp %{x}<br>objective %{y:.3f}<extra></extra>',
            ), row=1, col=1)

        # --- Champion ---------------------------------------------------------------------------
        champion = stable.loc[stable['obj'].idxmin()]
        fig.add_annotation(
            x=float(champion['n']), y=float(champion['obj']),
            text='<b>{}</b>  {:.3f}<br>{:.0f} nm'.format(
                champion['Exp'], champion['obj'], champion['size_nm']),
            showarrow=True, arrowhead=0, arrowwidth=1.1, arrowcolor=INK_SOFT,
            ax=42, ay=-72, xanchor='left',
            font=dict(size=ANNOTATION_SIZE, color=INK, family=FONT_FAMILY),
            row=1, col=1,
        )

        # --- Phase-separation strip -------------------------------------------------------------
        fig.add_trace(go.Scatter(
            x=failed['n'], y=[0] * len(failed), mode='markers', name='Phase Separated',
            marker=dict(size=MARKER_SIZE + 1, symbol='x-thin',
                        line=dict(color=FAIL_COLOR, width=2.2)),
            customdata=failed['Exp'],
            hovertemplate='%{customdata}<br>Exp %{x}<br>phase separated<extra></extra>',
        ), row=2, col=1)

        fig.update_layout(
            title=dict(text='Campaign 1 — Batched Bayesian Optimisation on Blank Formulations',
                       font=dict(size=TITLE_SIZE, color=INK), x=0.5, y=0.96,
                       xanchor='center', yanchor='top'),
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(family=FONT_FAMILY, color=INK),
            width=FIG_WIDTH, height=PROGRESS_FIG_HEIGHT,
            margin=dict(l=LEFT_MARGIN, r=55, t=110, b=LEGEND_MARGIN),
            showlegend=True,
            legend=dict(orientation='h', x=0.5, y=-0.16, xanchor='center', yanchor='top',
                        bgcolor='rgba(0, 0, 0, 0)',
                        font=dict(size=LEGEND_SIZE, color=INK)),
        )

        fig.update_xaxes(range=x_range, tickmode='linear', tick0=0, dtick=5,
                         **AXIS_COMMON, row=1, col=1)
        fig.update_xaxes(title='Experiment Number', range=x_range, tickmode='linear', tick0=0,
                         dtick=5, **AXIS_COMMON, row=2, col=1)
        fig.update_yaxes(title='Objective Function', range=y_range, tick0=0, dtick=y_dtick,
                         zeroline=False,
                         minor=dict(dtick=y_dtick / Y_MINOR_SPLIT, ticks='outside', ticklen=4,
                                    tickcolor=INK, showgrid=False),
                         **AXIS_COMMON, row=1, col=1)
        fig.update_yaxes(title='Phase<br>Separated', title_font=dict(size=ANNOTATION_SIZE),
                         range=[-1, 1], showticklabels=False, ticks='',
                         linecolor=INK, showline=True, mirror=True, linewidth=2,
                         showgrid=False, zeroline=False, color=INK_SOFT, row=2, col=1)
        return fig


    progress_figure = build_progress()
    progress_figure
    return (progress_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Figure 2 — `Blank_Batch_Composition`

    Three blocks — oil, surfactant, cosurfactant — each a grid of category against stage. A cell is
    shaded by how many of that stage's formulations used that ingredient, and carries the count.

    This is what `--max_per_category 1` looks like from the outside: early batches spread across
    the mesh categories because the constraint forbids a batch from spending itself on one
    ingredient, and the concentration that appears later is the surrogate's doing rather than the
    batch policy's.

    Laid out in pixel coordinates against a hidden axis, following the `Design_Space` suite: a grid
    of labelled cells is a composed frame, not data plotted against a measured quantity.
    """)
    return


@app.cell
def _(
    ANNOTATION_SIZE,
    AXIS_TITLE_SIZE,
    BO_COLOR,
    CAMPAIGN,
    FIG_HEIGHT,
    FIG_WIDTH,
    INK,
    INK_FAINT,
    INK_SOFT,
    STAGE_ORDER,
    TITLE_SIZE,
    blank_layout,
    box,
    fade,
    go,
    rule,
    text,
):
    COMPONENTS = (('oil', 'Oil'), ('surfactant', 'Surfactant'), ('cosurfactant', 'Cosurfactant'))


    def build_composition():
        counts = {}
        levels = {}
        for key, _label in COMPONENTS:
            table = (CAMPAIGN.groupby([key, 'stage']).size().unstack(fill_value=0)
                     .reindex(columns=STAGE_ORDER, fill_value=0))
            # Most-used ingredient first, so the row the campaign converged on is at the top.
            table = table.loc[table.sum(axis=1).sort_values(ascending=False).index]
            counts[key] = table
            levels[key] = list(table.index)

        rows_total = sum(len(v) for v in levels.values())

        # --- Pixel frame -----------------------------------------------------------------------
        # The left gutter carries two columns of type: the block name, then the ingredient names
        # right-aligned against the grid. 300 px is what 'Propylene Glycol' needs beside
        # 'Cosurfactant' at these two sizes without the two ever touching.
        left, right = 300, FIG_WIDTH - 40
        block_label_x = 22
        top = 118
        block_gap = 34
        header_h = 26
        row_h = 27
        n_cols = len(STAGE_ORDER)
        col_w = (right - left) / n_cols

        fig = go.Figure(layout=blank_layout(FIG_WIDTH, FIG_HEIGHT))

        text(fig, FIG_WIDTH / 2, 46,
             'Campaign 1 — What Each Batch Selected',
             size=TITLE_SIZE, color=INK, anchor='center', weight='bold')
        text(fig, FIG_WIDTH / 2, 72,
             'Formulations per stage using each ingredient  ·  batch size 5, one per category',
             size=ANNOTATION_SIZE, color=INK_SOFT, anchor='center')

        # Column headers, stacked so 'Random Screen' need not shrink to fit its column.
        for ci, stage in enumerate(STAGE_ORDER):
            cx = left + col_w * (ci + 0.5)
            words = stage.split(' ')
            if len(words) > 1 and col_w < 110:
                text(fig, cx, top - 14, words[0], size=ANNOTATION_SIZE, color=INK_SOFT, anchor='center')
                text(fig, cx, top - 1, ' '.join(words[1:]), size=ANNOTATION_SIZE, color=INK_SOFT,
                     anchor='center')
            else:
                text(fig, cx, top - 4, stage, size=ANNOTATION_SIZE, color=INK_SOFT, anchor='center')

        y = top + header_h
        vmax = max(int(counts[k].to_numpy().max()) for k, _ in COMPONENTS)

        for key, label in COMPONENTS:
            table = counts[key]
            block_h = row_h * len(table)
            text(fig, block_label_x, y + block_h / 2 + 5, label,
                 size=AXIS_TITLE_SIZE, color=INK, anchor='left', weight='bold')

            for ri, level in enumerate(table.index):
                ry = y + row_h * ri
                text(fig, left - 16, ry + row_h / 2 + 5, level.replace('_', ' '),
                     size=ANNOTATION_SIZE, color=INK_SOFT, anchor='right')
                for ci, stage in enumerate(STAGE_ORDER):
                    value = int(table.loc[level, stage])
                    cx = left + col_w * ci
                    box(fig, cx + 1.5, ry + 1.5, cx + col_w - 1.5, ry + row_h - 1.5,
                        fill=fade(BO_COLOR, 0.10 + 0.62 * value / vmax) if value else 'white',
                        line='rgba(0, 0, 0, 0.12)', width=1)
                    if value:
                        text(fig, cx + col_w / 2, ry + row_h / 2 + 5, str(value),
                             size=ANNOTATION_SIZE,
                             color='white' if value / vmax > 0.6 else INK, anchor='center')
            y += block_h + block_gap
            if key != COMPONENTS[-1][0]:
                rule(fig, left, y - block_gap / 2, right, y - block_gap / 2)

        text(fig, block_label_x, FIG_HEIGHT - 42,
             'The optimiser searched a mesh of 4 oils, 3 surfactants and 4 cosurfactants.',
             size=ANNOTATION_SIZE, color=INK_FAINT, anchor='left')
        text(fig, block_label_x, FIG_HEIGHT - 24,
             'Ingredients outside that mesh reached the campaign through the preliminary and '
             'random-screen runs.',
             size=ANNOTATION_SIZE, color=INK_FAINT, anchor='left')
        return fig


    composition_figure = build_composition()
    composition_figure
    return (composition_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Export

    Both figures to `Figures/Blank_Campaign/Output/` as SVG, at the size they were composed at.
    Adding `'png'` to `EXPORT_FORMATS` writes a 2× raster alongside.
    """)
    return


@app.cell
def _(
    EXPORT_FORMATS,
    FIG_HEIGHT,
    FIG_WIDTH,
    OUTPUT_DIR,
    PNG_SCALE,
    PROGRESS_FIG_HEIGHT,
    composition_figure,
    progress_figure,
):
    FIGURES = {
        'Blank_Campaign_Progress': (progress_figure, FIG_WIDTH, PROGRESS_FIG_HEIGHT),
        'Blank_Batch_Composition': (composition_figure, FIG_WIDTH, FIG_HEIGHT),
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


if __name__ == '__main__':
    app.run()
