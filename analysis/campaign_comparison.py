# --- Windows + conda DLL guard: must run before *any* other import --------------------------
# The existing guard in the imports cell below runs too late for a plain `python <file>` launch:
# `import marimo` pulls in the numeric stack first, so the process is already dead. PyCharm runs
# the configured conda interpreter directly rather than through `conda activate`, which is exactly
# that launch -- exit code 0xC06D007F / 3228369023, STATUS_DELAY_LOAD_FAILED, no traceback.
# See Figures/Blank_Campaign/Blank_Campaign_Figures.py for the same block and its caveats.
import os as _os
import sys as _sys

if _os.name == "nt":
    _dll_dir = _os.path.join(_sys.prefix, "Library", "bin")
    if _os.path.isdir(_dll_dir):
        _os.add_dll_directory(_dll_dir)
        _os.environ["PATH"] = _dll_dir + _os.pathsep + _os.environ.get("PATH", "")
# --------------------------------------------------------------------------------------------

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
    # Microemulsion Campaign Comparison — Formulation Improvement Analysis

    How much did Bayesian optimization improve the microemulsion across two campaigns,
    **analyzed separately for each API (A190 and Feno)?**

    **The DoE baseline is A190-only.** The initial Design-of-Experiments screening (its
    optimum, `DoE-OPT`) was run with the A190 drug, so it is a meaningful baseline *only
    for the A190 analysis*. The **Feno analysis therefore compares Campaign 1 vs
    Campaign 2 directly** — no DoE bar.

    Each analysis is presented four ways:

    1. **Leaderboard** — every formulation ranked by its objective, with the individual
       repeats overlaid (Sections 1/1c), plus per-repeat rankings that average nothing
       at all (Sections 1b/1d). `DoE-OPT` now sits on the A190 board alongside both
       campaigns.
    2. **Champion comparison** — the single best formulation at each stage.
       - *A190:* `DoE-OPT` → Best Campaign 1 (`E2_A`) → Best Campaign 2 (`A-B4`)
       - *Feno:* Best Campaign 1 (`F5_F`) → Best Campaign 2 (`F-B1`)
    3. **Top-3 comparison** — the three best formulations from each campaign, so
       consistency (not just the single winner) is visible.
    4. **Ranking history** (Section 6) — how the leaderboard moved when the Campaign 1
       champions gained real repeats and `DoE-OPT` gained a full measurement set.

    **Campaign 1 uses the API-revalidated champions.** Campaign 1 optimized on *blank*
    formulations; its three best candidates (`B4`, `E2`, `F5`) were later re-made and
    re-measured **with each API present** (`_A` = A190, `_F` = Feno), which is when drug
    loading and permeability were measured. Using those rows keeps Campaign 1 and
    Campaign 2 on the same six outputs.

    **Every formulation has three repeats.** `DoE-OPT` and the six revalidated
    Campaign 1 champions used to exist as single pre-averaged rows; the dataset now
    carries all three repeats for each, so every view here — the per-repeat rankings
    included — applies to *every* entity rather than to Campaign 2 alone. Section 6
    quantifies what that did to the standings.

    **Objective = a loss (lower is better):**

    $$\text{objective}=\frac{3\,s_\text{size}+2\,s_\text{PDI}+1\,s_\text{zeta}+2\,s_\text{DL}+3\,s_\text{perm}}{\max(1-\text{phase\_sep},\,0.01)}$$

    **Everything here is scored *score-then-average*:** each of a formulation's three
    repeats is scored on its own, and the reported objective is the **mean of those
    per-repeat objectives**. Because the score terms are nonlinear (hinges at 100 nm,
    |zeta| = 10 mV, the ±5 % drug-loading band, PDI = 0.3), this differs from averaging
    the measurements first and scoring once — and it is the order that rewards
    *reproducibility* rather than a lucky mean, which is why the alternative
    (average-then-score) is no longer carried here. Raw measurements are still
    rep-averaged for identity and per-parameter views: measurements are linear, so
    averaging order does not change them.

    The **physical-quality objective** (size/PDI/zeta only) is retained in Sections
    1c/1d and 7, because it is the metric Campaign 1 was actually optimized on.
    """)
    return


@app.cell
def _(get_ipython):
    import os
    import sys

    # Windows + conda: the numeric wheels delay-load their DLLs (MKL, OpenBLAS,
    # libstdc++) from <env>/Library/bin, which is only on PATH once the environment
    # is *activated*. A kernel launched without activation -- e.g. marimo started
    # from an unactivated shell or an IDE plugin -- therefore dies on `import numpy`
    # with no traceback: exit code 0xC06D007F / 3228369023, STATUS_DELAY_LOAD_FAILED.
    # Putting the directory back before the first numeric import makes the notebook
    # run under either launch path.
    if os.name == "nt":
        _dll_dir = os.path.join(sys.prefix, "Library", "bin")
        if os.path.isdir(_dll_dir):
            os.add_dll_directory(_dll_dir)
            os.environ["PATH"] = _dll_dir + os.pathsep + os.environ.get("PATH", "")

    import re
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots

    # Embed plotly.js in each figure's output so the notebook renders interactively
    # offline (JupyterLab / VS Code / nbviewer) without a CDN round-trip. marimo
    # supplies its own plotly renderer, so only override the default under IPython --
    # forcing "notebook" outside Jupyter makes fig display write raw HTML to stdout.
    try:
        get_ipython()          # noqa: F821 -- only defined by IPython / Jupyter
        pio.renderers.default = "notebook"
    except NameError:
        pass

    # Repo root. __file__ exists when this runs as a script or a marimo notebook;
    # in Jupyter it does not, so fall back to the working directory.
    try:
        _HERE = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        _HERE = os.getcwd()
    REPO = os.path.dirname(_HERE) if os.path.basename(_HERE) == "analysis" else _HERE

    # ---- Design tokens (validated categorical palette: blue / aqua / yellow) ----
    COL = {"DoE-OPT": "#2a78d6", "Best Campaign 1": "#1baf7a", "Best Campaign 2": "#eda100"}
    INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"

    # ---- Uniform typography + spacing shared by every figure ----
    FONT_FAMILY = "sans-serif"
    TITLE_SIZE, SUBTITLE_SIZE, PANEL_TITLE_SIZE = 16, 11, 12   # main title / gray subtitle / subplot title
    AXIS_TITLE_SIZE, TICK_SIZE, ANNOT_SIZE, LEGEND_SIZE = 12, 11, 10, 11
    AXIS_STANDOFF = 12        # gap between an axis line and its title
    YLABEL_STANDOFF = 10      # gap between y tick labels and the axis (matches the leaderboard)

    def axis_style(**over):
        a = dict(gridcolor=GRID, gridwidth=0.8, zeroline=False, linecolor="#c3c2b7",
                 ticks="outside", tickcolor=MUTED, tickfont=dict(size=TICK_SIZE, color=MUTED),
                 title_font=dict(size=AXIS_TITLE_SIZE, color=SECOND), title_standoff=AXIS_STANDOFF)
        a.update(over)
        return a

    def legend_below(height, top, bottom, gap_px=60):
        '''Horizontal legend a uniform gap_px below the plot area — identical look on every figure.'''
        plot_h = max(height - top - bottom, 120)
        return dict(orientation="h", x=0.5, y=-(gap_px / plot_h), xanchor="center",
                    yanchor="top", font=dict(size=LEGEND_SIZE, color=SECOND))

    def plotly_layout(**over):
        lay = dict(
            template="none", font=dict(family=FONT_FAMILY, size=12, color=INK),
            paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
            xaxis=axis_style(), yaxis=axis_style(),
            legend=dict(font=dict(size=LEGEND_SIZE, color=SECOND), bgcolor="rgba(0,0,0,0)"),
            title=dict(font=dict(size=TITLE_SIZE, color=INK)),
            margin=dict(l=90, r=120, t=70, b=60),
            hoverlabel=dict(font=dict(family=FONT_FAMILY, size=12)),
        )
        lay.update(over)
        return lay

    # ---- Figure export: each figure is saved to analysis/figures/<name>.svg ----
    FIGDIR = os.path.join(REPO, "analysis", "figures")
    os.makedirs(FIGDIR, exist_ok=True)

    # Every save_svg() call hands the figure to kaleido, which renders it in a
    # headless browser -- roughly 8 s per figure here, and there are 20 of them, so a
    # full run with export on costs a few minutes, almost entirely in SVG export.
    # Export is therefore OFF by default: a full run takes well under a minute and the
    # figures still render inline. Turn it on only when analysis/figures/ needs
    # refreshing -- set EXPORT_SVG = True here, or EXPORT_SVG=1 in the environment.
    EXPORT_SVG = os.environ.get("EXPORT_SVG", "0") not in ("0", "false", "False")

    def save_svg(fig, name):
        '''Write the figure to analysis/figures/<name>.svg (vector; uses the figure's own
        width/height). No-op when EXPORT_SVG is False -- the figure still renders inline.'''
        if not EXPORT_SVG:
            return
        fig.write_image(os.path.join(FIGDIR, f"{name}.svg"))

    print("Palette + plotly theme ready.  SVG export:",
          "ON (slow -- ~8 s per figure)" if EXPORT_SVG else "OFF (figures/ not refreshed)")
    return (
        ANNOT_SIZE,
        COL,
        INK,
        MUTED,
        PANEL_TITLE_SIZE,
        REPO,
        SECOND,
        SUBTITLE_SIZE,
        SURFACE,
        TICK_SIZE,
        YLABEL_STANDOFF,
        axis_style,
        go,
        legend_below,
        make_subplots,
        np,
        os,
        pd,
        plotly_layout,
        re,
        save_svg,
    )


@app.cell
def _(COL, REPO, os, pd, re):
    # ---- Load scored datasets; normalize whitespace in score-column names ----
    DATADIR = os.path.join(REPO, "analysis", "datasets")
    c1 = pd.read_csv(os.path.join(DATADIR, "campaign1_scores.csv"))       # per-rep scores
    c2 = pd.read_csv(os.path.join(DATADIR, "campaign2_scores.csv"))
    # The *_avg files hold rep-averaged *measurements* (linear, so the averaging order
    # does not change them) plus formulation identity -- used for the identity table and
    # the per-parameter panels. Their pre-averaged objective column is used only to
    # detect the fully phase-separated formulations that every leaderboard drops.
    c1a = pd.read_csv(os.path.join(DATADIR, "campaign1_scores_avg.csv"))
    c2a = pd.read_csv(os.path.join(DATADIR, "campaign2_scores_avg.csv"))
    for d in (c1, c2, c1a, c2a):
        d.columns = [re.sub(r"\s+", " ", c.strip()) for c in d.columns]

    DOE, DOE_LABEL = "DoEOPT", "DoE-OPT"        # dataset id vs. display name
    PREFIX = {"A190": "A-", "Feno": "F-"}

    # Per-rep rows for any formulation. Campaign 2 and the revalidated Campaign 1
    # champions live in c2; the DoE-OPT baseline lives in c1. Every formulation in
    # the dataset has three real repeats -- no pre-averaged placeholder rows remain --
    # so the score-then-average treatment applies to every entity in the comparison.
    def reps_of(exp):
        for source in (c2, c1):
            r = source[source["Exp"] == exp.replace(DOE_LABEL, DOE)]
            if len(r):
                return r
        return c2.iloc[:0]

    SCORE_W = [("size_score (w=3)", 3), ("pdi_score (w=2)", 2), ("zeta_score (w=1)", 1),
               ("dl_score (w=2)", 2), ("perm_score (w=3)", 3)]

    def summarize(exp):
        '''One formulation, scored **score-then-average**: identity and raw measurements
        are rep-averaged (measurements are linear, so averaging order does not change
        them), while the objective is the mean of the per-rep objectives. Each score
        column is rewritten to mean(score/stability) across reps and stability_factor
        set to 1, so Section 3's contribution formula (score x weight / stability)
        reproduces the mean per-rep contribution and the contributions still sum
        exactly to the objective.'''
        df_avg = c2a if (c2a["Exp"] == exp).any() else c1a
        s = df_avg[df_avg["Exp"] == exp].iloc[0].to_dict()
        r = reps_of(exp)
        stab = r["stability_factor"].clip(lower=0.01)
        for col, _ in SCORE_W:
            s[col] = (r[col] / stab).mean()
        s["stability_factor"] = 1.0
        s["objective"] = r["objective"].mean()
        s["phys_objective"] = (3 * s["size_score (w=3)"] + 2 * s["pdi_score (w=2)"]
                               + 1 * s["zeta_score (w=1)"])
        return s

    def _mean_obj(exp):
        return float(reps_of(exp)["objective"].mean())

    def _best3(prefix):
        '''Three lowest mean per-rep objectives; phase-separated means excluded.'''
        m = c2[c2["Exp"].str.startswith(prefix)].groupby("Exp")["objective"].mean()
        return list(m[m < 100].nsmallest(3).index)

    # Top-3 per campaign per API. Campaign 1 = the three revalidated champions (fixed
    # set, ranked here by their own mean per-rep objective); Campaign 2 = the three
    # lowest mean per-rep objectives.
    TOP3 = {
        "A190": {"c1": sorted(["E2_A", "F5_A", "B4_A"], key=_mean_obj), "c2": _best3("A-")},
        "Feno": {"c1": sorted(["E2_F", "F5_F", "B4_F"], key=_mean_obj), "c2": _best3("F-")},
    }

    # ---- Leaderboard membership ------------------------------------------------
    # One helper feeds all four leaderboards: the per-repeat rows of everything that
    # belongs on a board -- Campaign 2, the Campaign 1 champions, and (A190 only, since
    # the DoE screening was run with A190) the DoE-OPT baseline. Exp is renamed to the
    # display label so DoE-OPT reads properly on the axis.
    def board_reps(_api, shown=None):
        r = c2[(c2["Exp"].str.startswith(PREFIX[_api]))
               & (c2["Rep"].astype(str).str.lower() != "avg")]
        if shown is not None:
            r = r[r["Exp"].isin(shown)]
        parts = [r, c2[c2["Exp"].isin(TOP3[_api]["c1"])]]
        if _api == "A190":
            parts.append(c1[c1["Exp"] == DOE])
        out = pd.concat(parts, ignore_index=True)
        out["Exp"] = out["Exp"].replace({DOE: DOE_LABEL})
        return out

    def series_of(_api, exp):
        '''Which of the three leaderboard series a row belongs to.'''
        if exp == DOE_LABEL:
            return "doe"
        return "c1" if exp in TOP3[_api]["c1"] else "c2"

    SERIES_COLOR = {"c2": COL["Best Campaign 2"], "c1": COL["Best Campaign 1"],
                    "doe": COL["DoE-OPT"]}

    def phase_separated(_api):
        '''Formulations whose repeats include a full phase separation — one separated
        repeat sends the mean objective off-scale, so they are named in the subtitle
        rather than drawn.'''
        avg = c2a[c2a["Exp"].str.startswith(PREFIX[_api])]
        return (avg.loc[avg["objective"] < 100, "Exp"].tolist(),
                avg.loc[avg["objective"] >= 100, "Exp"].tolist())

    SUM = {"DoE-OPT": summarize(DOE)}
    for _api in TOP3:
        for _e in TOP3[_api]["c1"] + TOP3[_api]["c2"]:
            SUM[_e] = summarize(_e)

    # Champions = rank 1 of each campaign's top-3
    BEST_C1 = {_api: SUM[TOP3[_api]["c1"][0]] for _api in TOP3}
    BEST_C2 = {_api: SUM[TOP3[_api]["c2"][0]] for _api in TOP3}

    # Champion-comparison entities. Feno omits DoE-OPT (DoE was A190-only).
    ENTITIES = {
        "DoE-OPT":     SUM["DoE-OPT"],
        "BestC1_A190": BEST_C1["A190"], "BestC2_A190": BEST_C2["A190"],
        "BestC1_Feno": BEST_C1["Feno"], "BestC2_Feno": BEST_C2["Feno"],
    }
    ANALYSES = {
        "A190": ["DoE-OPT", "BestC1_A190", "BestC2_A190"],
        "Feno": ["BestC1_Feno", "BestC2_Feno"],
    }
    BASELINE  = {"A190": "DoE-OPT",  "Feno": "BestC1_Feno"}     # reference for % change
    BASELABEL = {"A190": "DoE-OPT",  "Feno": "Campaign 1"}
    LABEL = {
        "DoE-OPT":     "DoE-OPT",
        "BestC1_A190": f"Best Campaign 1\n({BEST_C1['A190']['Exp']})",
        "BestC2_A190": f"Best Campaign 2\n({BEST_C2['A190']['Exp']})",
        "BestC1_Feno": f"Best Campaign 1\n({BEST_C1['Feno']['Exp']})",
        "BestC2_Feno": f"Best Campaign 2\n({BEST_C2['Feno']['Exp']})",
    }
    COLOR_OF = {"DoE-OPT": COL["DoE-OPT"],
                "BestC1_A190": COL["Best Campaign 1"], "BestC1_Feno": COL["Best Campaign 1"],
                "BestC2_A190": COL["Best Campaign 2"], "BestC2_Feno": COL["Best Campaign 2"]}
    print("Champions -> A190:", BEST_C1['A190']['Exp'], "/", BEST_C2['A190']['Exp'],
          "| Feno:", BEST_C1['Feno']['Exp'], "/", BEST_C2['Feno']['Exp'])
    print("Top-3 C1  -> A190:", TOP3["A190"]["c1"], "| Feno:", TOP3["Feno"]["c1"])
    print("Top-3 C2  -> A190:", TOP3["A190"]["c2"], "| Feno:", TOP3["Feno"]["c2"])
    return (
        ANALYSES,
        BASELABEL,
        BASELINE,
        COLOR_OF,
        DATADIR,
        ENTITIES,
        LABEL,
        SERIES_COLOR,
        SUM,
        TOP3,
        board_reps,
        phase_separated,
        series_of,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Top-3 scaffold — entities for the top-3 subsections
    """)
    return


@app.cell
def _(COL, COLOR_OF, SUM, TOP3):
    # ---- Top-3 scaffold: entities/labels/colors for the top-3 subsections ----
    # Within a campaign, rank 1 keeps the full campaign color, ranks 2-3 fade toward white.
    def _shade(hex_color, f):
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return "#%02x%02x%02x" % tuple(round(v + (255 - v) * f) for v in (r, g, b))

    ENTITIES_TOP3 = {"DoE-OPT": SUM["DoE-OPT"]}
    LABEL_TOP3 = {"DoE-OPT": "DoE-OPT"}
    ANALYSES_TOP3 = {}
    for _api in TOP3:
        keys = ["DoE-OPT"] if _api == "A190" else []
        for camp, exps in (("1", TOP3[_api]["c1"]), ("2", TOP3[_api]["c2"])):
            for rank, _e in enumerate(exps, 1):
                # Rank-1 keys reuse the champion names so BASELINE/COLOR_OF work unchanged
                k = f"BestC{camp}_{_api}" if rank == 1 else f"C{camp}r{rank}_{_api}"
                ENTITIES_TOP3[k] = SUM[_e]
                LABEL_TOP3[k] = _e
                COLOR_OF[k] = _shade(COL[f"Best Campaign {camp}"], (0.0, 0.35, 0.6)[rank - 1])
                keys.append(k)
        ANALYSES_TOP3[_api] = keys

    # Bars are labeled by formulation ID; campaign identity comes from color, so the
    # top-3 figures carry a bottom legend with one swatch per campaign.
    LEGEND_TOP3 = [("Campaign 1", COL["Best Campaign 1"]), ("Campaign 2", COL["Best Campaign 2"])]
    for _api, ks in ANALYSES_TOP3.items():
        print(_api, "->", [LABEL_TOP3[k] for k in ks])
    return ANALYSES_TOP3, ENTITIES_TOP3, LABEL_TOP3, LEGEND_TOP3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Leaderboard — mean per-repeat objective

    Every formulation ranked by its **mean per-repeat objective** (bars, lower is
    better): each of the three repeats is scored on its own and the bar sits exactly at
    their mean. The dots are those individual repeats, so bar vs dots reads directly as
    mean vs spread. Campaign 1's revalidated champions (green) are scored the same way
    from their own three repeats, and **`DoE-OPT` (blue) is now on the A190 board** —
    it was re-measured with A190 loaded, so it finally has drug-loading and
    permeability data and can be scored on the same five terms as everything else.
    Fully phase-separated formulations are named in the figure subtitle rather than
    drawn — one separated repeat pushes the mean off-scale.

    **A190 — the consistent formulations lead, and the DoE optimum comes last.**
    `A-B4` (0.232) and `A-C5` (0.309) take the top two, with Campaign 1's `E2_A` third
    (0.323) and `F5_A` fourth (0.413). `A-A2` sits at #6 (0.686): its drug-loading
    repeats scatter around the 100 % target (111.7 / 117.4 / 85.4), so each repeat pays
    its own out-of-band penalty — the dots show the spread that costs it. `DoE-OPT`
    (3.494) finishes **last of all 16 entries**, behind every Campaign 2 formulation
    including the ones both campaigns would reject, because its permeability
    (3.07×10⁻⁶ cm/s) is roughly a seventh of target.

    **Feno:** `F-B1` leads (0.675) ahead of `F-C3` (0.836) and `F-B5` (0.912), with
    Campaign 1's `F5_F` (0.917) and `E2_F` (0.970) just behind; `F-A2` (2.15) and
    `F-A3` (2.40) are the worst of the non-separated set, again on scattered drug
    loading.

    *Interactive:* hover any bar for the mean per-repeat objective, or a dot for that
    repeat's own objective; use the legend to toggle series.
    """)
    return


@app.cell
def _(
    INK,
    MUTED,
    SERIES_COLOR,
    SUBTITLE_SIZE,
    SURFACE,
    TICK_SIZE,
    YLABEL_STANDOFF,
    board_reps,
    go,
    legend_below,
    mo,
    phase_separated,
    plotly_layout,
    save_svg,
    series_of,
):
    SERIES_ORDER = (("c2", "Campaign 2"), ("c1", "Campaign 1 Champion"), ("doe", "DoE-OPT Baseline"))

    def fig_leaderboard(_api):
        _, offscale = phase_separated(_api)
        reps = board_reps(_api)
        mean_obj = reps.groupby("Exp")["objective"].mean()
        mean_obj = mean_obj[mean_obj < 100]
        entries = sorted(((_e, float(o), series_of(_api, _e)) for _e, o in mean_obj.items()),
                         key=lambda t: t[1])            # best (lowest) first
        order = [_e for _e, _, _ in entries][::-1]        # plotly y: bottom->top, so best on top
        plot_reps = reps[reps["Exp"].isin(mean_obj.index)]

        fig = go.Figure()
        for s, sname in SERIES_ORDER:
            sel = [(_e, o) for _e, o, ss in entries if ss == s]
            if not sel:
                continue
            fig.add_bar(y=[_e for _e, _ in sel], x=[o for _, o in sel], orientation="h",
                        marker_color=SERIES_COLOR[s], width=0.62,
                        name=f"{sname} (Bar = Mean Of Per-Rep Objectives)",
                        hovertemplate="%{y}<br>mean per-rep objective %{x:.3f}<extra></extra>")

        # Per-rep dots — each bar is exactly the mean of its dots.
        fig.add_scatter(x=plot_reps["objective"].tolist(), y=plot_reps["Exp"].tolist(),
                        mode="markers", name="Individual Rep",
                        marker=dict(size=9, color=INK, opacity=0.7,
                                    line=dict(color=SURFACE, width=1.2)),
                        customdata=plot_reps["Rep"].astype(str).tolist(),
                        hovertemplate="%{y} — rep %{customdata}<br>per-rep objective %{x:.3f}<extra></extra>")

        xmax = max([o for _, o, _ in entries] + [plot_reps["objective"].max()])
        xmin = min([0.0] + [o for _, o, _ in entries] + plot_reps["objective"].tolist())
        height, top, bottom = 44 * len(entries) + 210, 70, 130
        title = f"<b>{_api} — Leaderboard</b>  (score-then-average)"
        if offscale:
            title += f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>" \
                     f"Not Shown (Phase-Separated): {', '.join(offscale)}</span>"
        fig.update_layout(plotly_layout(
            barmode="overlay", height=height, width=1000,
            margin=dict(l=90, r=60, t=top, b=bottom),
            title=dict(text=title, x=0.01, xanchor="left"),
            legend=legend_below(height, top, bottom),
        ))
        fig.update_xaxes(title_text="Mean Objective Of Individually-Scored Repeats  (Lower Is Better)",
                         range=[xmin * 1.4 - 0.03, xmax * 1.1])
        fig.update_yaxes(categoryorder="array", categoryarray=order, showgrid=False,
                         ticklabelstandoff=YLABEL_STANDOFF, tickfont=dict(size=TICK_SIZE, color=INK))
        fig.add_vline(x=0, line=dict(color="#c3c2b7", width=1))
        save_svg(fig, f"{_api}_leaderboard")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_leaderboard(_api)
    return (SERIES_ORDER,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1b. Leaderboard — each repeat ranked on its own

    Section 1 with nothing grouped: **every repeat is scored individually and gets its
    own bar** (`Formulation · Rep`), ranked across all repeats. Section 1's bars are the
    means of these values; here the individual repeats compete directly, so a
    formulation's spread is visible as the distance between its three bars rather than
    as dots around one.

    `A-B5` takes the top two slots (−0.07, 0.02) and `A-B4`'s R3 is third (0.103) —
    the same reproducibility that puts `A-B4` first in Section 1. Campaign 1 `E2_A`'s
    best repeat (0.134) is fourth, though its other two (0.363, 0.472) show `E2_A` is
    far from uniform — and that best repeat is exactly the single pre-averaged number
    `E2_A` used to be represented by (see Section 6). `A-A2`'s repeats land mid-pack
    (0.41 / 0.57 / 1.08), each paying the drug-loading penalty its scattered value
    earns. `DoE-OPT`'s three repeats (3.19 / 3.25 / 4.03) sit at the very bottom.

    For Feno the top slot goes to a **Campaign 1** repeat: `F5_F` R2 (0.212), ahead of
    `F-B1` R1 (0.343); `F-B1`'s repeats then span 0.34 / 0.60 / 1.08 and `E2_F`'s best
    sits at 0.676.

    *Interactive:* hover any bar for its formulation, repeat, and individually-scored
    objective; use the legend to toggle the series.
    """)
    return


@app.cell
def _(
    ANNOT_SIZE,
    INK,
    MUTED,
    SERIES_COLOR,
    SERIES_ORDER,
    SUBTITLE_SIZE,
    TICK_SIZE,
    YLABEL_STANDOFF,
    board_reps,
    go,
    legend_below,
    mo,
    phase_separated,
    plotly_layout,
    save_svg,
    series_of,
):
    def fig_leaderboard_indiv(_api):
        shown, offscale = phase_separated(_api)
        # One bar per individual repeat; drop phase-separated repeats and any fully
        # phase-separated formulation, exactly as Section 1 drops them.
        reps = board_reps(_api, shown=shown)
        reps = reps[reps["objective"] < 100]
        entries = [(f"{r['Exp']} · {r['Rep']}", r["Exp"], str(r["Rep"]), r["objective"],
                    series_of(_api, r["Exp"])) for _, r in reps.iterrows()]
        entries.sort(key=lambda t: t[3])                 # best (lowest) first
        order = [t[0] for t in entries][::-1]            # plotly y bottom->top: best on top

        fig = go.Figure()
        for s, sname in SERIES_ORDER:
            sel = [t for t in entries if t[4] == s]
            if not sel:
                continue
            fig.add_bar(y=[t[0] for t in sel], x=[t[3] for t in sel], orientation="h",
                        marker_color=SERIES_COLOR[s], width=0.66,
                        name=f"{sname} Repeat (Scored Individually)", cliponaxis=False,
                        customdata=[[t[1], t[2]] for t in sel],
                        hovertemplate="%{customdata[0]} — rep %{customdata[1]}<br>per-rep objective %{x:.3f}<extra></extra>")

        # Value labels: annotations anchored just right of each bar end (or of zero, for
        # the negative bars) so they never collide with the y tick labels.
        for lbl, _, _, v, _ in entries:
            fig.add_annotation(x=max(v, 0.0), y=lbl, text=f"{v:.3f}", showarrow=False,
                               xanchor="left", xshift=6, font=dict(size=ANNOT_SIZE, color=INK))

        xmax = max(t[3] for t in entries)
        xmin = min(0.0, min(t[3] for t in entries))
        height, top, bottom = 30 * len(entries) + 210, 70, 130
        title = f"<b>{_api} — Leaderboard</b>  (each repeat scored separately)"
        if offscale:
            title += f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>" \
                     f"Not Shown (Phase-Separated): {', '.join(offscale)}</span>"
        fig.update_layout(plotly_layout(
            barmode="overlay", height=height, width=1000,
            margin=dict(l=110, r=70, t=top, b=bottom),
            title=dict(text=title, x=0.01, xanchor="left"),
            legend=legend_below(height, top, bottom),
        ))
        fig.update_xaxes(title_text="Objective Of Each Individually-Scored Repeat  (Lower Is Better)",
                         range=[xmin * 1.4 - 0.03, xmax * 1.12])
        fig.update_yaxes(categoryorder="array", categoryarray=order, showgrid=False,
                         ticklabelstandoff=YLABEL_STANDOFF, tickfont=dict(size=TICK_SIZE, color=INK))
        fig.add_vline(x=0, line=dict(color="#c3c2b7", width=1))
        save_svg(fig, f"{_api}_leaderboard_indiv")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_leaderboard_indiv(_api)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1c. Leaderboard — Campaign 1's *original* objective

    Sections 1/1b rank on the **full** objective (six outputs, including drug loading
    and permeability). But Campaign 1 was optimized on an earlier, **physicochemical-only**
    objective — size, PDI, |zeta|, and a phase-separation penalty, additive, no drug
    loading or permeability:

    $$\text{objective}_\text{orig}=s_\text{size}+s_\text{PDI}+s_\text{zeta}+10\cdot\text{phase\_sep}$$

    This leaderboard re-scores every repeat with **that original metric** and takes the
    mean per formulation — Campaign 1's champions and `DoE-OPT` included, on exactly the
    same footing as Campaign 2. It answers: *how would the field look if we still only
    cared about physical quality?* Same non-phase-separated set as Section 1; the dots
    are the individual repeats under this metric.

    - **A190 — the ranking survives the metric change, and DoE-OPT stops being last.**
      Campaign 2 sweeps the front: `A-A5` (0.029), `A-A2` (0.040), `A-B4` (0.040),
      ahead of Campaign 1's `E2_A`. `A-A2`, which the *full* objective demotes to #6,
      is near the top here — its repeat-to-repeat variability comes almost entirely
      from **drug loading**, not physical quality. `DoE-OPT` climbs off the bottom
      to #11 of 16 — its size and PDI were never the real problem — but still sits
      behind all three Campaign 1 champions and the Campaign 2 leaders.
    - **Feno — the winner is metric-dependent.** The full-objective champion `F-B1`
      falls deep into the pack: its win came from on-target drug loading and
      above-target permeability, exactly the terms this metric ignores. On physical
      quality alone `F-B5` leads (0.016), and Campaign 1's `E2_F` is competitive — its
      strength was always PDI.
    - The original objective is linear below its hinges, so most formulations move
      little between orders; the movers are the ones whose repeats straddle the
      **PDI = 0.3 hinge** (below 0.3 the objective charges 0.25·PDI; at or above, the
      full PDI). `A-C5` (0.168) pays for an R3 PDI of 0.38, and Campaign 1's `F5_F`
      (0.228) is dragged up by a size-outlier third repeat.

    *Interactive:* hover any bar for the mean per-repeat original objective, or a dot
    for that repeat's value; toggle the series in the legend.
    """)
    return


@app.cell
def _(
    ANNOT_SIZE,
    INK,
    MUTED,
    SERIES_COLOR,
    SERIES_ORDER,
    SUBTITLE_SIZE,
    SURFACE,
    TICK_SIZE,
    YLABEL_STANDOFF,
    board_reps,
    go,
    legend_below,
    mo,
    np,
    phase_separated,
    plotly_layout,
    save_svg,
    series_of,
):
    def orig_objective(size, pdi, zeta, sep):
        '''Campaign 1's original objective (additive, weight 1 each; +10*phase_sep; no
        drug loading / permeability). Verified to reproduce every score column in
        campaign1_scores_original_objective.csv.'''
        ss = np.maximum(0.0, (size - 100.0) / 900.0)
        ps = np.where(pdi < 0.3, 0.25 * pdi, pdi)
        zs = np.maximum(0.0, (np.abs(zeta) - 10.0) / 10.0)
        sc = np.clip(sep, 0.0, 1.0)
        return ss + ps + zs + 10.0 * sc

    def fig_leaderboard_orig(_api):
        shown, offscale = phase_separated(_api)
        # Each repeat scored on its own with the original objective, then averaged
        # per formulation -- the same order of operations as Section 1.
        reps = board_reps(_api, shown=shown).copy()
        reps["orig"] = orig_objective(reps["Droplet_Size"], reps["PDI"],
                                      reps["Zeta_P"], reps["Phase_Sep"])
        mean_orig = reps.groupby("Exp")["orig"].mean()
        entries = sorted(((_e, float(o), series_of(_api, _e)) for _e, o in mean_orig.items()),
                         key=lambda t: t[1])            # best (lowest) first
        order = [_e for _e, _, _ in entries][::-1]        # plotly y bottom->top: best on top

        fig = go.Figure()
        for s, sname in SERIES_ORDER:
            sel = [(_e, o) for _e, o, ss in entries if ss == s]
            if not sel:
                continue
            fig.add_bar(y=[_e for _e, _ in sel], x=[o for _, o in sel], orientation="h",
                        marker_color=SERIES_COLOR[s], width=0.62,
                        name=f"{sname} (Mean Of Per-Rep Original Objectives)", cliponaxis=False,
                        hovertemplate="%{y}<br>mean per-rep original objective %{x:.3f}<extra></extra>")
        fig.add_scatter(x=reps["orig"].tolist(), y=reps["Exp"].tolist(), mode="markers",
                        name="Individual Rep",
                        marker=dict(size=9, color=INK, opacity=0.7,
                                    line=dict(color=SURFACE, width=1.2)),
                        customdata=reps["Rep"].astype(str).tolist(),
                        hovertemplate="%{y} — rep %{customdata}<br>per-rep original objective %{x:.3f}<extra></extra>")

        # Value labels: annotations right of each bar end — or of the outermost rep dot,
        # so labels never collide with the dots (all values >= 0).
        rep_max = reps.groupby("Exp")["orig"].max()
        for _e, o, s in entries:
            fig.add_annotation(x=max(o, rep_max.get(_e, o)), y=_e, text=f"{o:.3f}",
                               showarrow=False, xanchor="left", xshift=6,
                               font=dict(size=ANNOT_SIZE, color=INK))

        xmax = max([o for _, o, _ in entries] + [reps["orig"].max()])
        height, top, bottom = 40 * len(entries) + 210, 95, 130
        title = (f"<b>{_api} — Under Campaign 1's Original Objective</b>"
                 f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>"
                 f"Physicochemical-Only (Size + PDI + |Zeta| + 10·Phase-Sep) — Each Repeat Scored, Objectives Then Averaged")
        if offscale:
            title += f"; Not Shown (Phase-Separated): {', '.join(offscale)}"
        title += "</span>"
        fig.update_layout(plotly_layout(
            barmode="overlay", height=height, width=1000,
            margin=dict(l=90, r=70, t=top, b=bottom),
            title=dict(text=title, x=0.01, xanchor="left"),
            legend=legend_below(height, top, bottom),
        ))
        fig.update_xaxes(title_text="Mean Original (Physicochem-Only) Objective Of Individually-Scored Repeats  (Lower Is Better)",
                         range=[0, xmax * 1.12])
        fig.update_yaxes(categoryorder="array", categoryarray=order, showgrid=False,
                         ticklabelstandoff=YLABEL_STANDOFF, tickfont=dict(size=TICK_SIZE, color=INK))
        fig.add_vline(x=0, line=dict(color="#c3c2b7", width=1))
        save_svg(fig, f"{_api}_leaderboard_orig")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_leaderboard_orig(_api)
    return (orig_objective,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1d. Leaderboard — individual repeats under Campaign 1's *original* objective

    Section 1b's per-repeat treatment applied to Section 1c's metric: every repeat —
    Campaign 1's revalidated champions and `DoE-OPT` included — is scored on its own
    with Campaign 1's **original physicochemical-only** objective (size + PDI + |zeta|
    + 10·phase_sep; no drug loading / permeability).

    The contrast with **1b** is the payoff. Under the *full* objective (1b), `A-A2`'s
    repeats scattered from 0.41 to 1.08 and fell to mid-pack. Here they cluster tightly
    near the top (0.027 / 0.036 / 0.057) — so the repeat-to-repeat variability that
    demoted `A-A2` came almost entirely from **drug loading**, not physical quality: on
    physicochemistry its repeats are consistent and excellent. `A-A5`'s repeats take the
    top two slots, and Campaign 1's `E2_A` (0.061 / 0.062 / 0.065) is out-scored by most
    Campaign 2 repeats — tightly clustered, but clustered below the leaders.

    For Feno, the full-objective champion `F-B1` sits deep mid-pack (0.31 / 0.35 / 0.36)
    with its three repeats *tightly clustered* — its physicochemistry is consistently
    mediocre, and its win in Sections 1 / 1c came from drug loading + permeability.
    `F-B5`'s repeats sweep the top three (0.015–0.017). The repeats also expose a split
    in Campaign 1: `E2_F` is consistent (0.045–0.065) while `F5_F` is not — two strong
    repeats (0.042, 0.050) and one at 0.593, a spread invisible when it was a single
    averaged row.

    *Interactive:* hover any bar for its formulation, repeat, and original-objective
    value; toggle the series in the legend.
    """)
    return


@app.cell
def _(
    ANNOT_SIZE,
    INK,
    MUTED,
    SERIES_COLOR,
    SERIES_ORDER,
    SUBTITLE_SIZE,
    TICK_SIZE,
    YLABEL_STANDOFF,
    board_reps,
    go,
    legend_below,
    mo,
    orig_objective,
    phase_separated,
    plotly_layout,
    save_svg,
    series_of,
):
    def fig_leaderboard_orig_indiv(_api):
        shown, offscale = phase_separated(_api)
        # Same repeat set as Section 1b, re-scored with Campaign 1's original objective
        # (orig_objective is defined in the Section 1c cell above).
        reps = board_reps(_api, shown=shown).copy()
        reps = reps[reps["objective"] < 100]
        reps["orig"] = orig_objective(reps["Droplet_Size"], reps["PDI"],
                                      reps["Zeta_P"], reps["Phase_Sep"])
        entries = [(f"{r['Exp']} · {r['Rep']}", r["Exp"], str(r["Rep"]), r["orig"],
                    series_of(_api, r["Exp"])) for _, r in reps.iterrows()]
        entries.sort(key=lambda t: t[3])                 # best (lowest) first
        order = [t[0] for t in entries][::-1]            # plotly y bottom->top: best on top

        fig = go.Figure()
        for s, sname in SERIES_ORDER:
            sel = [t for t in entries if t[4] == s]
            if not sel:
                continue
            fig.add_bar(y=[t[0] for t in sel], x=[t[3] for t in sel], orientation="h",
                        marker_color=SERIES_COLOR[s], width=0.66,
                        name=f"{sname} Repeat (Original Objective)", cliponaxis=False,
                        customdata=[[t[1], t[2]] for t in sel],
                        hovertemplate="%{customdata[0]} — rep %{customdata[1]}<br>per-rep original objective %{x:.3f}<extra></extra>")
        # Value labels: annotations right of each bar end (all values >= 0).
        for lbl, _, _, v, _ in entries:
            fig.add_annotation(x=v, y=lbl, text=f"{v:.3f}", showarrow=False,
                               xanchor="left", xshift=6, font=dict(size=ANNOT_SIZE, color=INK))

        xmax = max(t[3] for t in entries)
        height, top, bottom = 30 * len(entries) + 210, 95, 130
        title = (f"<b>{_api} — Repeats Under Campaign 1's Original Objective</b>"
                 f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>"
                 f"Physicochemical-Only (Size + PDI + |Zeta| + 10·Phase-Sep), Each Repeat Scored Separately")
        if offscale:
            title += f"; Not Shown (Phase-Separated): {', '.join(offscale)}"
        title += "</span>"
        fig.update_layout(plotly_layout(
            barmode="overlay", height=height, width=1000,
            margin=dict(l=110, r=70, t=top, b=bottom),
            title=dict(text=title, x=0.01, xanchor="left"),
            legend=legend_below(height, top, bottom),
        ))
        fig.update_xaxes(title_text="Original (Physicochem-Only) Objective Of Each Individually-Scored Repeat  (Lower Is Better)",
                         range=[0, xmax * 1.12])
        fig.update_yaxes(categoryorder="array", categoryarray=order, showgrid=False,
                         ticklabelstandoff=YLABEL_STANDOFF, tickfont=dict(size=TICK_SIZE, color=INK))
        fig.add_vline(x=0, line=dict(color="#c3c2b7", width=1))
        save_svg(fig, f"{_api}_leaderboard_orig_indiv")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_leaderboard_orig_indiv(_api)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Formulation identity — components & continuous variables

    The "what changed" reference for each champion comparison: which oil / surfactant /
    cosurfactant, at what volume fractions, and how long it was sonicated. (Feno has no
    DoE row — the A190-based DoE is not a valid Feno baseline.)
    """)
    return


@app.cell
def _(ANALYSES, ENTITIES, LABEL, pd):
    def identity_table(_api):
        rows = []
        for k in ANALYSES[_api]:
            _e = ENTITIES[k]
            rows.append({"Formulation": LABEL[k].replace("\n", " "),
                         "Oil": _e["Oil"], "Surfactant": _e["Surfactant"], "Cosurfactant": _e["Cosurfactant"],
                         "Oil_V (%)": round(_e["Oil_V"], 2), "Surf_V (%)": round(_e["Surfactant_V"], 2),
                         "Cosurf_V (%)": round(_e["Cosurfactant_V"], 2), "Sonication (min)": round(_e["Sonication"], 2)})
        return pd.DataFrame(rows).set_index("Formulation")

    for _api in ("A190", "Feno"):
        print(f"\n=== {_api} analysis — formulation identity ===")
        print(identity_table(_api).to_string())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Champion comparison — overall scoring

    Lower objective = better; bars annotated with **% change versus the baseline**
    (DoE-OPT for A190, Campaign 1 for Feno; negative = improvement). Left = the
    **full objective** (all five weighted terms — size, PDI, zeta, drug loading,
    permeability); right = the weighted component breakdown of that objective (where
    each score comes from). Every bar is the mean of three individually-scored repeats,
    and the component bars are the mean per-repeat weighted contributions, so they
    still sum exactly to the objective.

    - **A190.** Campaign 2's `A-B4` (0.232) improves on DoE-OPT's 3.494 by **−93 %**
      and finishes ahead of revalidated Campaign 1 `E2_A` (0.323). The breakdown shows
      `A-B4` pays a drug-loading penalty (+0.25) that its permeability bonus (−0.16)
      does not fully cancel. `DoE-OPT` now has drug-loading and permeability data, so
      it carries a full five-term bar; its permeability (3.07×10⁻⁶ cm/s, far under the
      20×10⁻⁶ target) dominates its score and is the clearest single gap the campaigns
      closed.
    - **Feno.** `F-B1` (0.675) beats Campaign 1's `F5_F` (0.917) by **−26 %**. PDI
      remains the dominant cost (0.52 of the 0.675) — Feno's main remaining lever.
    """)
    return


@app.cell
def _(
    ANALYSES,
    ANNOT_SIZE,
    BASELABEL,
    BASELINE,
    COLOR_OF,
    ENTITIES,
    INK,
    LABEL,
    MUTED,
    PANEL_TITLE_SIZE,
    SECOND,
    SUBTITLE_SIZE,
    SURFACE,
    TICK_SIZE,
    YLABEL_STANDOFF,
    axis_style,
    legend_below,
    make_subplots,
    mo,
    plotly_layout,
    save_svg,
):
    def fig_objective(_api, entities=None, label=None, suffix="", note=None,
                      keys=None, heading="Champion Objective Comparison", legend_entries=None):
        entities, label = entities or ENTITIES, label or LABEL
        keys = keys or ANALYSES[_api]
        labels = [label[k].replace("\n", "<br>") for k in keys]
        order = labels[::-1]                       # plotly y: bottom->top, so first key on top
        ref = entities[BASELINE[_api]]["objective"]
        full = [entities[k]["objective"] for k in keys]

        fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.17,
                            subplot_titles=("Overall Score — Full Objective",
                                            "Where The Score Comes From"))

        # Left panel: full objective, one bar per champion, colored by entity.
        # Value labels are annotations anchored to the RIGHT of the bar end (or of
        # zero, for a negative bar) so they never collide with the y labels.
        fig.add_bar(y=labels, x=full, orientation="h", width=0.6, showlegend=False,
                    marker_color=[COLOR_OF[k] for k in keys], cliponaxis=False,
                    hovertemplate="%{y}<br>full objective %{x:.3f}<extra></extra>", row=1, col=1)
        for k, lab, v in zip(keys, labels, full):
            delta = "Baseline" if k == BASELINE[_api] else f"{(v-ref)/ref*100:+.0f}% Vs {BASELABEL[_api]}"
            fig.add_annotation(x=max(v, 0.0), y=lab, text=f"{v:.3f}  ({delta})", showarrow=False,
                               xanchor="left", xshift=6, font=dict(size=ANNOT_SIZE, color=INK), row=1, col=1)

        # Campaign swatches ranked ahead of the component legend — dataless markers,
        # so they cannot disturb bar orientation or category layout.
        for rank, (name, c) in enumerate(legend_entries or [], start=10):
            fig.add_scatter(x=[None], y=[None], mode="markers", name=name, legendrank=rank,
                            marker=dict(size=10, symbol="square", color=c),
                            hoverinfo="skip", showlegend=True, row=1, col=1)

        # Right panel: weighted component breakdown, stacked (relative handles +/-).
        comp_keys = [("size_score (w=3)", 3, "Size", "#2a78d6"), ("pdi_score (w=2)", 2, "PDI", "#1baf7a"),
                     ("zeta_score (w=1)", 1, "Zeta", "#4a3aa7"), ("dl_score (w=2)", 2, "Drug Loading", "#e87ba4"),
                     ("perm_score (w=3)", 3, "Permeability", "#eb6834")]
        def contrib(k, col, w):
            return entities[k][col] * w / max(entities[k]["stability_factor"], 0.01)
        for col, w, name, c in comp_keys:
            vals = [contrib(k, col, w) for k in keys]
            fig.add_bar(y=labels, x=vals, orientation="h", width=0.6, name=name,
                        marker=dict(color=c, line=dict(color=SURFACE, width=1.2)),
                        hovertemplate="%{y}<br>" + name + " %{x:.3f}<extra></extra>", row=1, col=2)
        for k, lab in zip(keys, labels):          # Σ label past the right end of the positive stack
            pos = sum(max(contrib(k, col, w), 0.0) for col, w, _, _ in comp_keys)
            fig.add_annotation(x=pos, y=lab, text=f"Σ={entities[k]['objective']:.3f}", showarrow=False,
                               xanchor="left", xshift=6, font=dict(size=ANNOT_SIZE, color=SECOND), row=1, col=2)
        fig.add_vline(x=0, line=dict(color="#c3c2b7", width=1), row=1, col=2)

        height, top, bottom = 190 + 120 * len(keys), 95, 150
        title = f"<b>{_api} — {heading}</b>  (score-then-average)"
        if note:
            title += f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>{note}</span>"
        fig.update_layout(plotly_layout(
            barmode="relative", height=height, width=1150,
            margin=dict(l=150, r=70, t=top, b=bottom),
            title=dict(text=title, x=0.01, xanchor="left"),
            legend=legend_below(height, top, bottom),
        ))
        fig.update_xaxes(**axis_style())
        fig.update_xaxes(title_text="Full Objective  (All 5 Terms, Lower Is Better)",
                         range=[min(min(full), 0) * 1.15 - 0.02, max(full) * 1.55], row=1, col=1)
        pos_max = max(sum(max(contrib(k, col, w), 0.0) for col, w, _, _ in comp_keys) for k in keys)
        neg_min = min(sum(min(contrib(k, col, w), 0.0) for col, w, _, _ in comp_keys) for k in keys)
        fig.update_xaxes(title_text="Weighted Contribution To Full Objective",
                         range=[min(neg_min, 0.0) * 1.1 - 0.02, pos_max * 1.4], row=1, col=2)
        # Match the leaderboard's y labels: INK, size 11, standoff 10.
        fig.update_yaxes(**axis_style(categoryorder="array", categoryarray=order, showgrid=False,
                                      ticklabelstandoff=YLABEL_STANDOFF, tickfont=dict(size=TICK_SIZE, color=INK)))
        for ann in fig.layout.annotations[:2]:    # subplot titles -> uniform panel-title size
            ann.update(font=dict(size=PANEL_TITLE_SIZE, color=INK))
        save_svg(fig, f"{_api}_objective{suffix}")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_objective(_api, note="Every Bar Is The Mean Of Three Individually-Scored Repeats")
    return (fig_objective,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3b. Top-3 comparison — overall scoring

    Same two-panel view as Section 3, but every top-3 formulation per campaign gets a bar
    (A190 also keeps DoE-OPT as the baseline).
    """)
    return


@app.cell
def _(ANALYSES_TOP3, ENTITIES_TOP3, LABEL_TOP3, LEGEND_TOP3, fig_objective):
    for _api in ("A190", "Feno"):
        fig_objective(_api, ENTITIES_TOP3, LABEL_TOP3, suffix="_top3",
                      keys=ANALYSES_TOP3[_api], heading="Top-3 Objective Comparison", legend_entries=LEGEND_TOP3,
                      note="Top 3 Per Campaign, Both Ranked By Mean Per-Rep Objective; "
                           "Every Bar Is The Mean Of Three Individually-Scored Repeats")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Champion comparison — each measured parameter

    Small multiples, one per output. Measurements are rep-averaged (they are linear, so
    the scoring order does not change them). Dashed lines mark the objective's targets
    (size → 100 nm; PDI → 0.3, the scoring hinge below which the penalty drops to
    0.25·PDI; |zeta| threshold → 10 mV; drug loading → 100 %; permeability →
    20×10⁻⁶ cm/s), and each line's label points to the side the objective rewards
    (▼ below, ≈ near, ▲ above). **Phase separation was 0 (fully stable) for all**,
    noted in the title. `DoE-OPT` was re-measured with A190 loaded, so it now has
    drug-loading (104.9 %) and permeability (3.07×10⁻⁶ cm/s) bars — the permeability
    one falling well short of target is the clearest single gap the campaigns closed.
    """)
    return


@app.cell
def _(
    ANALYSES,
    ANNOT_SIZE,
    BASELINE,
    COLOR_OF,
    ENTITIES,
    INK,
    LABEL,
    MUTED,
    PANEL_TITLE_SIZE,
    SECOND,
    SUBTITLE_SIZE,
    TICK_SIZE,
    axis_style,
    legend_below,
    make_subplots,
    mo,
    pd,
    plotly_layout,
    save_svg,
):
    def fig_parameters(_api, entities=None, label=None, suffix="",
                       keys=None, heading="Champion Per-Parameter Comparison", width=1600,
                       legend_entries=None):
        entities, label = entities or ENTITIES, label or LABEL
        keys = keys or ANALYSES[_api]
        # (column, panel title, target, side of the target the objective rewards)
        panels = [("Droplet_Size", "Droplet Size (nm)", 100.0, "below"),
                  ("PDI", "PDI", 0.3, "below"),                  # 0.3 = the scoring hinge
                  ("Zeta_P", "|Zeta Potential| (mV)", 10.0, "below"),
                  ("Drug_Loading", "Drug Loading (%)", 100.0, "near"),
                  ("Permeability", "Permeability (cm/s)", 20e-6, "above")]
        want = {"below": ("▼ Below", "top"), "near": ("≈ Near", "middle"),
                "above": ("▲ Above", "bottom")}
        ref = entities[BASELINE[_api]]
        fig = make_subplots(rows=1, cols=5, horizontal_spacing=0.055,
                            subplot_titles=[t for _, t, _, _ in panels])
        for ci, (col, title, target, side) in enumerate(panels, start=1):
            vals, cols, labs, kk = [], [], [], []
            for k in keys:
                v = abs(entities[k][col]) if col == "Zeta_P" else entities[k][col]
                if pd.isna(v):
                    continue
                vals.append(v); cols.append(COLOR_OF[k]); kk.append(k)
                labs.append(label[k].split("\n")[0].replace("Best ", ""))
            base = abs(ref[col]) if col == "Zeta_P" else ref[col]
            txt = []
            for k, v in zip(kk, vals):
                note = (f"<br><span style='color:{MUTED}'>{(v-base)/base*100:+.0f}%</span>"
                        if (not pd.isna(base) and base != 0 and k != BASELINE[_api]) else "")
                fmt = f"{v:.2e}" if col == "Permeability" else (f"{v:.2f}" if v < 100 else f"{v:.0f}")
                txt.append(fmt + note)
            fig.add_bar(x=labs, y=vals, width=0.62, marker_color=cols, showlegend=False,
                        text=txt, textposition="outside", textfont=dict(size=ANNOT_SIZE, color=INK),
                        cliponaxis=False, hovertemplate="%{x}<br>" + title + " %{y}<extra></extra>",
                        row=1, col=ci)
            vmax = max(vals) if vals else 1
            # Keep the target inside the y-range so its dashed line stays visible
            # (Feno droplet sizes ~12 nm vs the 100 nm target).
            top = max(vmax, target) if target is not None else vmax
            fig.update_yaxes(range=[0, top * 1.32], row=1, col=ci)
            if target is not None:
                fig.add_hline(y=target, line=dict(color=INK, width=1.2, dash="dash"), row=1, col=ci)
                # Direction tag in the gutter right of the panel, anchored to the
                # side of the target line the objective rewards - never over a bar.
                wtext, wanchor = want[side]
                fig.add_annotation(x=1, xref="x domain", y=target, yref="y", row=1, col=ci,
                                   text=wtext, showarrow=False, xanchor="left", xshift=3,
                                   yanchor=wanchor, font=dict(size=ANNOT_SIZE, color=SECOND))
        # Campaign swatches: dataless markers, so bars stay centered on their ticks.
        for name, c in (legend_entries or []):
            fig.add_scatter(x=[None], y=[None], mode="markers", name=name,
                            marker=dict(size=10, symbol="square", color=c),
                            hoverinfo="skip", showlegend=True, row=1, col=1)
        bottom = 130 if legend_entries else 95
        extra = dict(legend=legend_below(460, 110, bottom)) if legend_entries else {}
        fig.update_layout(plotly_layout(
            height=460, width=width, margin=dict(l=70, r=70, t=110, b=bottom),
            title=dict(text=f"<b>{_api} — {heading}</b>  (score-then-average)"
                            f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>"
                            f"Phase Separation = 0 (Fully Stable) For All</span>",
                       x=0.01, xanchor="left"),
            **extra,
        ))
        fig.update_xaxes(**axis_style(tickangle=-25, tickfont=dict(size=TICK_SIZE, color=INK)))
        fig.update_yaxes(**axis_style(tickfont=dict(size=TICK_SIZE, color=MUTED)))
        for ann in fig.layout.annotations[:len(panels)]:   # subplot titles -> uniform panel-title size
            ann.update(font=dict(size=PANEL_TITLE_SIZE, color=INK))
        save_svg(fig, f"{_api}_parameters{suffix}")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_parameters(_api)
    return (fig_parameters,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4b. Top-3 per-parameter comparison
    """)
    return


@app.cell
def _(ANALYSES_TOP3, ENTITIES_TOP3, LABEL_TOP3, LEGEND_TOP3, fig_parameters):
    for _api in ("A190", "Feno"):
        fig_parameters(_api, ENTITIES_TOP3, LABEL_TOP3, suffix="_top3",
                       keys=ANALYSES_TOP3[_api], heading="Top-3 Per-Parameter Comparison", width=2000,
                       legend_entries=LEGEND_TOP3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Top-3 comparison — Campaign 1 vs Campaign 2

    Beyond the single champion, the three best formulations from each campaign, both
    ranked by mean per-repeat objective. The dotted line is each campaign's **top-3
    mean objective** — a read on *consistency*, not just the best pick.
    (Campaign-vs-campaign, both measured with API — no DoE.)

    **A190:** Campaign 2's `A-B4` / `A-C5` / `A-B5` average 0.34 against Campaign 1's
    0.57. **Feno:** `F-B1` / `F-C3` / `F-B5` average 0.81 against Campaign 1's 1.41,
    and Campaign 1's own order is `F5_F` / `E2_F` / `B4_F`.
    """)
    return


@app.cell
def _(
    ANNOT_SIZE,
    COL,
    INK,
    PANEL_TITLE_SIZE,
    SUM,
    TOP3,
    axis_style,
    go,
    mo,
    np,
    pd,
    plotly_layout,
    save_svg,
):
    def fig_top3(_api):
        c1 = [SUM[_e] for _e in TOP3[_api]["c1"]]
        c2 = [SUM[_e] for _e in TOP3[_api]["c2"]]
        names = [s["Exp"] for s in c1] + [s["Exp"] for s in c2]
        objs = [s["objective"] for s in c1] + [s["objective"] for s in c2]
        cols = [COL["Best Campaign 1"]] * len(c1) + [COL["Best Campaign 2"]] * len(c2)
        fig = go.Figure()
        fig.add_bar(x=names, y=objs, width=0.7, marker_color=cols, showlegend=False,
                    text=[f"{o:.3f}" for o in objs], textposition="outside",
                    textfont=dict(size=ANNOT_SIZE, color=INK), cliponaxis=False,
                    hovertemplate="%{x}<br>full objective %{y:.3f}<extra></extra>")

        n1, n2 = len(c1), len(c2)
        m1 = float(np.mean([s["objective"] for s in c1]))
        m2 = float(np.mean([s["objective"] for s in c2]))
        # x are categorical positions 0..n-1; draw each campaign's mean over its own span.
        fig.add_shape(type="line", x0=-0.45, x1=n1 - 0.55, y0=m1, y1=m1,
                      line=dict(color=COL["Best Campaign 1"], width=1.6, dash="dot"))
        fig.add_shape(type="line", x0=n1 - 0.45, x1=n1 + n2 - 0.55, y0=m2, y1=m2,
                      line=dict(color=COL["Best Campaign 2"], width=1.6, dash="dot"))
        fig.add_annotation(x=n1 - 0.55, y=m1, text=f"Mean {m1:.2f}", showarrow=False,
                           xanchor="left", xshift=4, font=dict(size=ANNOT_SIZE, color="#0f7a55"))
        fig.add_annotation(x=n1 + n2 - 0.55, y=m2, text=f"Mean {m2:.2f}", showarrow=False,
                           xanchor="left", xshift=4, font=dict(size=ANNOT_SIZE, color="#a06f00"))
        fig.add_annotation(x=(n1 - 1) / 2, y=1.05, yref="paper", text="<b>Campaign 1 (Top 3)</b>",
                           showarrow=False, font=dict(size=PANEL_TITLE_SIZE, color="#0f7a55"))
        fig.add_annotation(x=n1 + (n2 - 1) / 2, y=1.05, yref="paper", text="<b>Campaign 2 (Top 3)</b>",
                           showarrow=False, font=dict(size=PANEL_TITLE_SIZE, color="#a06f00"))

        ymin = min(0.0, min(objs) * 2.1 - 0.03)
        ymax = max(objs) * 1.18
        fig.update_layout(plotly_layout(
            height=520, width=950, margin=dict(l=80, r=70, t=95, b=60),
            title=dict(text=f"<b>{_api} — Top-3 Formulations Per Campaign</b>  (score-then-average)",
                       x=0.01, xanchor="left"),
            yaxis=axis_style(title_text="Full Objective  (Lower Is Better)", range=[ymin, ymax]),
        ))
        save_svg(fig, f"{_api}_top3")
        mo.output.append(fig)

    def top3_table(_api):
        rows = []
        for camp, key in [("Campaign 1", "c1"), ("Campaign 2", "c2")]:
            for rank, _e in enumerate(TOP3[_api][key], 1):
                s = SUM[_e]
                rows.append({"Campaign": camp, "Rank": rank, "Formulation": _e,
                             "Oil": s["Oil"], "Surfactant": s["Surfactant"], "Cosurfactant": s["Cosurfactant"],
                             "Droplet (nm)": round(s["Droplet_Size"], 1), "PDI": round(s["PDI"], 3),
                             "Drug loading (%)": round(s["Drug_Loading"], 1),
                             "Permeability": f"{s['Permeability']:.2e}", "objective": round(s["objective"], 4)})
        return pd.DataFrame(rows).set_index(["Campaign", "Rank"])

    for _api in ("A190", "Feno"):
        fig_top3(_api)
        print(f"\n=== {_api} — top-3 per campaign ===")
        print(top3_table(_api).to_string())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Ranking history — what the new data points changed

    The dataset gained two things since the previous analysis, both of which move the
    standings without any Campaign 2 measurement changing:

    1. **The six revalidated Campaign 1 champions went from one pre-averaged row each
       to three real repeats.** Their objective is no longer a single number but the
       mean of three individually-scored repeats.
    2. **`DoE-OPT` was re-measured with A190 loaded**, gaining drug-loading and
       permeability data. Before that it could only be scored on three of the five
       terms (objective 0.792, not comparable to anything); now it carries the full
       objective (3.494) and joins the A190 leaderboard.

    Campaign 2's own numbers are unchanged (a few values move in the fourth decimal
    from a spreadsheet resave), so **every Campaign 2 rank shift below is caused by the
    entries around it moving**. The slope chart reads left (before) → right (after);
    lines that fall moved down the board, lines that rise moved up.

    **A190 — Campaign 2 takes the lead it did not previously hold.** `E2_A` was **#1
    overall** on the strength of its single pre-averaged row (0.134). With three real
    repeats it scores 0.323 and drops to **#3**, handing the top spot to `A-B4` (0.232,
    unchanged) with `A-C5` (0.309) second. That single change is the difference between
    "Campaign 1 still holds the best A190 formulation" and "Campaign 2 does."  `B4_A`
    improves a lot in absolute terms (1.351 → 0.976) without moving rank. `DoE-OPT`
    enters at the very bottom (#16 of 16).

    **Feno — the Campaign 1 champion swaps.** `F5_F` was the *ninth* entry at 1.916;
    its three repeats average **0.917**, moving it to **#4** and past `E2_F`, which
    slips from #3 to #5 (0.892 → 0.970). So Campaign 1's Feno champion is now `F5_F`,
    not `E2_F` — a reversal driven entirely by the added repeats, and one that 1b/1d
    immediately qualify: `F5_F`'s three repeats are far *less* uniform than `E2_F`'s.
    Four mid-board Campaign 2 formulations (`F-C1`, `F-C5`, `F-B3`, `F-A5`) each slide
    one place purely because `F5_F` moved up past them.

    *Source:* `analysis/datasets/ranking_history.csv`, rebuilt by
    `python analysis/build_ranking_history.py` (it reads the previous state directly
    out of git, so nothing is hand-maintained).
    """)
    return


@app.cell
def _(
    ANNOT_SIZE,
    COL,
    DATADIR,
    INK,
    MUTED,
    SECOND,
    SUBTITLE_SIZE,
    SURFACE,
    axis_style,
    go,
    legend_below,
    mo,
    os,
    pd,
    plotly_layout,
    save_svg,
):
    hist = pd.read_csv(os.path.join(DATADIR, "ranking_history.csv"))
    CAMP_COLOR = {"Campaign 1": COL["Best Campaign 1"], "Campaign 2": COL["Best Campaign 2"],
                  "DoE": COL["DoE-OPT"]}

    def fig_rank_change(_api):
        d = hist[hist["api"] == _api].sort_values("rank_after")
        n = len(d)
        fig = go.Figure()

        # One connector per formulation, before-rank -> after-rank. Entries with no
        # "before" (DoE-OPT) get a single marker on the right instead.
        seen = set()
        for _, r in d.iterrows():
            c = CAMP_COLOR[r["campaign"]]
            moved = pd.notna(r["rank_before"]) and r["rank_before"] != r["rank_after"]
            show = r["campaign"] not in seen
            seen.add(r["campaign"])
            if pd.notna(r["rank_before"]):
                fig.add_scatter(x=[0, 1], y=[r["rank_before"], r["rank_after"]],
                                mode="lines+markers", name=r["campaign"], legendgroup=r["campaign"],
                                showlegend=show, line=dict(color=c, width=3 if moved else 1.4),
                                opacity=1.0 if moved else 0.45,
                                marker=dict(size=10, color=c, line=dict(color=SURFACE, width=1.2)),
                                customdata=[[r["exp"], r["objective_before"], r["objective_after"]]] * 2,
                                hovertemplate="%{customdata[0]}<br>before: rank %{y}, "
                                              "objective %{customdata[1]:.3f}<extra></extra>")
            else:
                fig.add_scatter(x=[1], y=[r["rank_after"]], mode="markers",
                                name=r["campaign"], legendgroup=r["campaign"], showlegend=show,
                                marker=dict(size=12, color=c, symbol="diamond",
                                            line=dict(color=SURFACE, width=1.2)),
                                hovertemplate=f"{r['exp']} — new entry<br>"
                                              f"objective {r['objective_after']:.3f}<extra></extra>")

            # Names at both ends; the "after" label carries the objective and the move.
            if pd.notna(r["rank_before"]):
                fig.add_annotation(x=0, y=r["rank_before"], text=f"{r['exp']}  ",
                                   showarrow=False, xanchor="right",
                                   font=dict(size=ANNOT_SIZE, color=INK if moved else SECOND))
            delta = ""
            if pd.notna(r["rank_delta"]) and r["rank_delta"]:
                delta = f"  ({int(r['rank_delta']):+d})"
            elif pd.isna(r["rank_before"]):
                delta = "  (new)"
            fig.add_annotation(x=1, y=r["rank_after"],
                               text=f"  {r['exp']} {r['objective_after']:.3f}{delta}",
                               showarrow=False, xanchor="left",
                               font=dict(size=ANNOT_SIZE, color=INK if (moved or delta) else SECOND))

        height, top, bottom = 34 * n + 210, 95, 130
        # DoE was A190-only, so only that board gains the baseline as a new entry.
        sub = ("Before = Campaign 1 Champions As Single Pre-Averaged Rows, No DoE-OPT; "
               "After = Three Repeats Each, DoE-OPT Included" if _api == "A190" else
               "Before = Campaign 1 Champions As Single Pre-Averaged Rows; "
               "After = Three Repeats Each")
        fig.update_layout(plotly_layout(
            height=height, width=980, margin=dict(l=130, r=210, t=top, b=bottom),
            title=dict(text=f"<b>{_api} — Leaderboard Rank: Before vs After The Added Data</b>"
                            f"<br><span style='font-size:{SUBTITLE_SIZE}px;color:{MUTED}'>{sub}</span>",
                       x=0.01, xanchor="left"),
            legend=legend_below(height, top, bottom),
            xaxis=axis_style(range=[-0.28, 1.28], tickmode="array", tickvals=[0, 1],
                             ticktext=["Before", "After"], showgrid=False),
            # Descending range == a reversed axis, but bounded: rank 1 on top with a
            # little padding, no empty 0 / n+1 gridlines.
            yaxis=axis_style(title_text="Leaderboard Rank  (1 = Best)",
                             range=[n + 0.6, 0.4], dtick=1, showgrid=True),
        ))
        save_svg(fig, f"{_api}_rank_change")
        mo.output.append(fig)

    for _api in ("A190", "Feno"):
        fig_rank_change(_api)
        _d = hist[hist["api"] == _api].sort_values("rank_after")
        movers = _d[(_d["rank_delta"].fillna(0) != 0) | _d["rank_before"].isna()]
        print(f"\n=== {_api} — entries that moved (of {len(_d)}) ===")
        print(movers[["exp", "campaign", "rank_before", "objective_before",
                      "rank_after", "objective_after", "rank_delta"]].to_string(index=False))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Quantified summary (champions)

    Machine-readable table: every parameter plus both objective flavors (full and
    physical-quality-only), with % change versus each analysis's baseline. Objectives
    are means of the per-repeat objectives; measurements are rep-averaged.
    """)
    return


@app.cell
def _(ANALYSES, BASELABEL, BASELINE, ENTITIES, LABEL, np, pd):
    def improvement_table(_api):
        keys = ANALYSES[_api]; base = ENTITIES[BASELINE[_api]]
        metrics = [("Droplet_Size", "Droplet size (nm)"), ("PDI", "PDI"), ("Zeta_P", "Zeta potential (mV)"),
                   ("Phase_Sep", "Phase separation"), ("Drug_Loading", "Drug loading (%)"),
                   ("Permeability", "Permeability (cm/s)"), ("phys_objective", "Physical objective"),
                   ("objective", "Full objective")]
        out = {}
        for k in keys:
            _e = ENTITIES[k]; col = {}
            for m, lab in metrics:
                v = _e[m]; col[lab] = v
                if k != BASELINE[_api]:
                    col[lab + " Δ%"] = ((v - base[m]) / abs(base[m]) * 100
                                        if not pd.isna(base[m]) and not pd.isna(v) and base[m] != 0 else np.nan)
            out[LABEL[k].replace("\n", " ")] = col
        return pd.DataFrame(out)

    for _api in ("A190", "Feno"):
        print(f"\n============  {_api} — champions vs {BASELABEL[_api]}  ============")
        with pd.option_context("display.float_format", lambda v: f"{v:,.4g}", "display.width", 200):
            print(improvement_table(_api).to_string())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key findings

    *(Every objective below is score-then-average: each repeat scored on its own, the
    per-repeat objectives then averaged. Measurements are rep-averaged.)*

    **A190** (baseline = DoE-OPT, now re-measured with A190 loaded)
    - Champion: Campaign 2's `A-B4` reaches **0.232, a −93 % improvement on DoE-OPT's
      3.494**, and beats revalidated Campaign 1 `E2_A` (0.323). Its edge is
      reproducibility — its three repeats are tight (1b), where the flashier `A-A2`
      splits 0.41 / 0.57 / 1.08 on scattered drug loading and lands at #6 (0.686).
    - **This lead is new.** Before the Campaign 1 champions had real repeats, `E2_A`
      topped the A190 board on a single pre-averaged row (0.134). Three repeats put it
      at 0.323 and #3 (Section 6) — the added data is what moves the best A190
      formulation from Campaign 1 to Campaign 2.
    - **DoE-OPT's real gap is permeability.** Now that it has drug-loading and
      permeability data, its objective is dominated by a permeability of
      3.07×10⁻⁶ cm/s — roughly a seventh of the target — and it finishes **last on the
      board**, behind every Campaign 2 formulation. On physical quality alone (1c) the
      gap is far smaller: size and PDI were never the problem.
    - Top-3: Campaign 2 is **better and more consistent** — `A-B4` / `A-C5` / `A-B5`,
      mean 0.34, vs Campaign 1's 0.57.

    **Feno** (no DoE baseline — compared Campaign 1 → Campaign 2)
    - Champion: Campaign 2 `F-B1` wins at **0.675 vs Campaign 1's `F5_F` 0.917
      (−26 %)**, with drug loading on target and permeability past target. **PDI
      remains Feno's main lever** — 0.52 of `F-B1`'s 0.675.
    - **Campaign 1's own champion changed with the added repeats:** `F5_F` jumped from
      the 9th entry (1.916) to 4th (0.917), overtaking `E2_F` (0.892 → 0.970). But
      1b/1d show `F5_F` is the *less* reproducible of the two — two strong repeats and
      one bad one — so treat that swap as provisional.
    - Top-3: Campaign 2 is **decisively more consistent** — `F-B1` / `F-C3` / `F-B5`,
      mean 0.81, vs Campaign 1's 1.41.

    **Metric dependence.** Under Campaign 1's *original* physicochemical-only objective
    (1c/1d) the A190 ordering survives — Campaign 2 still sweeps the front — but Feno's
    winner changes: `F-B1` falls deep into the pack because its win rests on drug
    loading and permeability, exactly the terms that metric ignores, and `F-B5` leads
    on physical quality instead.

    **Overall.** Campaign 2 produced the champion for both APIs (`A-B4` and `F-B1`) and
    is the more consistent campaign by top-3 mean, with ~94 % smaller droplets than the
    A190 DoE optimum, far higher permeability, and drug-delivery targets met or
    exceeded. Scoring each repeat before averaging is what makes that claim safe: it
    prices repeat-to-repeat variability instead of hiding it inside a mean, which is
    why the formulations that win here are the ones that win *repeatedly* — and
    Section 6 shows that the moment Campaign 1's champions were held to the same
    three-repeat standard, the A190 lead changed hands.
    """)
    return


if __name__ == "__main__":
    app.run()
