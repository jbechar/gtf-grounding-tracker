"""
GTF Grounding Tracker — single-command report generator.
Run: python generate_report.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

 
# Paths
# ---------------------------------------------------------------------------
ROOT             = Path(__file__).parent
DATA_FILE        = ROOT / "data" / "grounding_counts.csv"
COMMS_FILE       = ROOT / "data" / "wizz_air_comms.csv"
GROUND_DAY_FILE  = ROOT / "data" / "ground_day_comparison.csv"
VARIANT_FILE     = ROOT / "data" / "variant_split.csv"
REPORT_FILE      = ROOT / "index.html"

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
PALETTE = {
    "base_bg":  "#0E1116",
    "card_bg":  "#161B22",
    "border":   "#21262D",
    "primary":  "#3D7A99",
    "accent":   "#E8743B",
    "muted":    "#8B93A1",
    "text":     "#E6E9EE",
    "mid":      "#2eaa6e",
}

 
# Load data
 
print("Loading data …")
df          = pd.read_csv(DATA_FILE, parse_dates=["date"])
df["airline"] = df["airline"].str.strip()
df_global   = df[df["airline"] == "Global"].sort_values("date").copy()
df_airlines = df[df["airline"] != "Global"].copy()

df_comms = pd.read_csv(COMMS_FILE, parse_dates=["date"])
df_comms = df_comms.sort_values("date").reset_index(drop=True)
df_wizz  = df_airlines[df_airlines["airline"] == "Wizz Air"].sort_values("date").copy()

df_ground_day = pd.read_csv(GROUND_DAY_FILE, parse_dates=["as_of_date"]) if GROUND_DAY_FILE.exists() else None
df_variant    = pd.read_csv(VARIANT_FILE,    parse_dates=["as_of_date"]) if VARIANT_FILE.exists()    else None


 
# Shared layout defaults
 
BASE_LAYOUT = dict(
    paper_bgcolor=PALETTE["card_bg"],
    plot_bgcolor=PALETTE["card_bg"],
    font=dict(
        family="'IBM Plex Sans', system-ui, -apple-system, sans-serif",
        color=PALETTE["text"],
    ),
    margin=dict(l=60, r=40, t=60, b=60),
    hoverlabel=dict(
        bgcolor=PALETTE["border"],
        font_size=13,
        font_color=PALETTE["text"],
        bordercolor=PALETTE["primary"],
    ),
)

DARK_AXIS = dict(
    showgrid=True,
    gridcolor=PALETTE["border"],
    zerolinecolor=PALETTE["border"],
    tickfont=dict(family="'JetBrains Mono', monospace", size=11),
)

MONO = "'JetBrains Mono', monospace"


def fig_to_div(fig: go.Figure, first: bool = False) -> str:
    include_js = "cdn" if first else False
    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=include_js,
        config={"displayModeBar": True, "responsive": True},
    )


 
# Chart 1 — Global grounding trend over time
 
def chart1() -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_global["date"],
        y=df_global["grounded_aircraft"],
        mode="lines+markers+text",
        name="Aircraft Grounded",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=9, color=PALETTE["primary"]),
        fill="tozeroy",
        fillcolor="rgba(61,122,153,0.15)",
        text=df_global["grounded_aircraft"].astype(int).astype(str),
        textposition="top center",
        textfont=dict(color=PALETTE["primary"], size=11, family=MONO),
        hovertemplate="<b>%{x|%b %Y}</b><br>Grounded: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="GTF Aircraft Grounded Globally Over Time", font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(title="Aircraft Grounded", range=[600, 920], dtick=50, **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart 1")
    return fig_to_div(fig, first=True)


# ---------------------------------------------------------------------------
# Chart 2 — Most affected airlines (% grounded, latest per airline)
# ---------------------------------------------------------------------------
def chart2() -> str:
    latest = (
        df_airlines
        .sort_values("date")
        .groupby("airline", as_index=False)
        .last()
        .sort_values("pct_grounded", ascending=True)
    )
    bar_colors = [
        PALETTE["accent"]  if p >= 40 else
        PALETTE["primary"] if p >= 20 else
        PALETTE["mid"]
        for p in latest["pct_grounded"]
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=latest["airline"],
        x=latest["pct_grounded"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v:.1f}%" for v in latest["pct_grounded"]],
        textposition="outside",
        textfont=dict(family=MONO, color=PALETTE["text"]),
        hovertemplate="<b>%{y}</b><br>Grounded: %{x:.1f}%<extra></extra>",
        name="",
    ))
    fig.add_vline(
        x=30, line_dash="dash", line_color=PALETTE["muted"], line_width=1.5,
        annotation_text="Global avg ~34%",
        annotation_position="top right",
        annotation_font=dict(size=11, color=PALETTE["muted"]),
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="% of GTF Fleet Grounded by Airline (Latest Data)", font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="% of GTF Fleet Grounded", range=[0, 65], **DARK_AXIS),
        yaxis=dict(title="", **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart 2")
    return fig_to_div(fig)


 
# Chart 3 — Groundings vs MRO Recovery (dual axis)
 
def chart3() -> str:
    mro_data = pd.DataFrame({
        "date":      pd.to_datetime(["2024-01-01", "2025-01-01", "2025-10-01"]),
        "mro_index": [100, 126, 139],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_global["date"],
        y=df_global["grounded_aircraft"],
        mode="lines+markers",
        name="Aircraft Grounded",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=9, color=PALETTE["primary"]),
        fill="tozeroy",
        fillcolor="rgba(61,122,153,0.12)",
        yaxis="y1",
        hovertemplate="<b>%{x|%b %Y}</b><br>Grounded: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=mro_data["date"],
        y=mro_data["mro_index"],
        mode="lines+markers+text",
        name="P&W MRO Output Index",
        line=dict(color=PALETTE["accent"], width=2.5, dash="dash"),
        marker=dict(size=9, symbol="square", color=PALETTE["accent"]),
        text=mro_data["mro_index"].astype(int).astype(str),
        textposition="top center",
        textfont=dict(color=PALETTE["accent"], size=11, family=MONO),
        yaxis="y2",
        hovertemplate="<b>%{x|%b %Y}</b><br>MRO Index: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Groundings vs MRO Recovery", font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(
            title=dict(text="Aircraft Grounded", font=dict(color=PALETTE["primary"])),
            tickfont=dict(color=PALETTE["primary"], family=MONO, size=11),
            range=[600, 920], dtick=50,
            showgrid=True, gridcolor=PALETTE["border"],
            zerolinecolor=PALETTE["border"],
        ),
        yaxis2=dict(
            title=dict(text="MRO Output Index (2024 = 100)", font=dict(color=PALETTE["accent"])),
            tickfont=dict(color=PALETTE["accent"], family=MONO, size=11),
            overlaying="y", side="right",
            range=[80, 160], showgrid=False,
        ),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(22,27,34,0.9)",
            borderwidth=1, bordercolor=PALETTE["border"],
        ),
    )
    print("  Built chart 3")
    return fig_to_div(fig)


 
# Sentiment helpers
 
SENTIMENT_COLOR = {
    1: "#d62728",
    2: "#ff7f0e",
    3: "#bcbd22",
    4: "#2eaa6e",
    5: "#17becf",
}
SENTIMENT_LABEL = {
    1: "Very Pessimistic",
    2: "Pessimistic",
    3: "Neutral",
    4: "Optimistic",
    5: "Very Optimistic",
}


 
# Chart 4 — Wizz Air grounding trajectory vs PR moments
 
def chart4() -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_wizz["date"],
        y=df_wizz["grounded_aircraft"],
        mode="lines+markers",
        name="Aircraft Grounded (actual)",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=9, color=PALETTE["primary"]),
        fill="tozeroy",
        fillcolor="rgba(61,122,153,0.12)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Grounded: %{y}<extra></extra>",
    ))
    for _, row in df_comms.iterrows():
        score = int(row["sentiment_score"])
        color = SENTIMENT_COLOR.get(score, "#888")
        label = SENTIMENT_LABEL.get(score, "")
        short_headline = row["headline"][:55] + ("…" if len(row["headline"]) > 55 else "")
        fig.add_trace(go.Scatter(
            x=[row["date"]], y=[0],
            mode="markers",
            name=short_headline,
            marker=dict(size=14, color=color, symbol="star",
                        line=dict(color=PALETTE["text"], width=1)),
            hovertemplate=(
                f"<b>{row['date'].strftime('%b %Y')}</b><br>"
                f"<b>{row['source_type'].replace('_', ' ').title()}</b><br>"
                f"{row['headline']}<br>"
                f"Sentiment: {label}<br>"
                f"<i>{row['key_claim'][:120]}…</i><extra></extra>"
            ),
            showlegend=False,
        ))
    timeline_claims = [
        (pd.Timestamp("2026-01-01"), "Original target: end-2026", PALETTE["mid"]),
        (pd.Timestamp("2027-01-01"), "Revised target: end-2027", PALETTE["accent"]),
    ]
    for ts, label_text, color in timeline_claims:
        x_ms = ts.value // 10 ** 6
        fig.add_shape(
            type="line", x0=x_ms, x1=x_ms, y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(dash="dot", color=color, width=1.5),
        )
        fig.add_annotation(
            x=x_ms, y=0.98, xref="x", yref="paper",
            text=label_text, showarrow=False,
            font=dict(size=10, color=color),
            xanchor="left", yanchor="top",
            bgcolor="rgba(22,27,34,0.85)",
        )
    for score, label in SENTIMENT_LABEL.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=SENTIMENT_COLOR[score], symbol="star"),
            name=f"PR: {label}", showlegend=True,
        ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Wizz Air: Grounding Trajectory vs Public Narrative Moments",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(title="Wizz Air Aircraft Grounded", range=[0, 65], **DARK_AXIS),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(22,27,34,0.9)",
            borderwidth=1, bordercolor=PALETTE["border"],
            font=dict(size=10),
        ),
    )
    print("  Built chart 4")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart 5 — Ground-day rate: GTF vs competing engine families
# (requires data/ground_day_comparison.csv; falls back to airline timeline if absent)
# ---------------------------------------------------------------------------
def chart5() -> str:
    if df_ground_day is not None:
        df_gd = df_ground_day.copy()
        df_gd["mid"] = (df_gd["ground_day_pct_low"] + df_gd["ground_day_pct_high"]) / 2
        df_gd["range_label"] = df_gd.apply(
            lambda r: f"{r['ground_day_pct_low']:.0f}%"
            if r["ground_day_pct_low"] == r["ground_day_pct_high"]
            else f"{r['ground_day_pct_low']:.0f}–{r['ground_day_pct_high']:.0f}%",
            axis=1,
        )
        bar_colors = [PALETTE["accent"], PALETTE["mid"], PALETTE["muted"]]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_gd["engine_family"],
            x=df_gd["mid"],
            orientation="h",
            marker_color=bar_colors[: len(df_gd)],
            text=df_gd["range_label"],
            textposition="outside",
            textfont=dict(family=MONO, color=PALETTE["text"]),
            error_x=dict(
                type="data", symmetric=False,
                array=df_gd["ground_day_pct_high"] - df_gd["mid"],
                arrayminus=df_gd["mid"] - df_gd["ground_day_pct_low"],
                color=PALETTE["muted"], thickness=1.2,
            ),
            hovertemplate="<b>%{y}</b><br>Ground-day rate: %{text}<extra></extra>",
        ))
        as_of = df_gd["as_of_date"].max().strftime("%b %Y")
        fig.update_layout(
            **BASE_LAYOUT,
            title=dict(text="Ground-Day Rate: GTF vs Competing Engine Families",
                       font=dict(size=15, color=PALETTE["text"])),
            xaxis=dict(title="% of days fleet is grounded (ground-day rate)",
                       range=[0, 45], **DARK_AXIS),
            yaxis=dict(title="", **DARK_AXIS),
            showlegend=False,
            annotations=[dict(
                text=f"Source: Aviation Week Fleet Discovery / Tracked Aircraft Utilization, as of {as_of}",
                xref="paper", yref="paper", x=0, y=-0.18, showarrow=False,
                font=dict(size=10, color=PALETTE["muted"]), xanchor="left",
            )],
        )
        print("  Built chart 5 (ground-day rate)")
        return fig_to_div(fig)

    # Fallback: multi-airline grounding rate timeline
    airlines_with_series = (
        df_airlines.groupby("airline")
        .filter(lambda g: len(g) >= 2)["airline"].unique()
    )
    color_cycle = [PALETTE["primary"], PALETTE["accent"], PALETTE["mid"], "#a78bfa"]
    fig = go.Figure()
    for i, airline in enumerate(airlines_with_series):
        sub = df_airlines[df_airlines["airline"] == airline].sort_values("date")
        fig.add_trace(go.Scatter(
            x=sub["date"], y=sub["pct_grounded"],
            mode="lines+markers", name=airline,
            line=dict(color=color_cycle[i % len(color_cycle)], width=2.5),
            marker=dict(size=8),
            hovertemplate=f"<b>{airline}</b><br>%{{x|%b %Y}}<br>Grounded: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Grounding Rate Over Time — Airline Comparison",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(title="% of GTF Fleet Grounded", **DARK_AXIS),
        legend=dict(bgcolor="rgba(22,27,34,0.9)", borderwidth=1, bordercolor=PALETTE["border"]),
    )
    print("  Built chart 5 (airline timeline fallback)")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart 6 — A320neo vs A321neo variant-level grounding severity
# (requires data/variant_split.csv; falls back to bubble scatter if absent)
# ---------------------------------------------------------------------------
def chart6() -> str:
    if df_variant is not None:
        df_v = df_variant.copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_v["variant"], y=df_v["pct_parked_or_stored"],
            name="% parked or stored",
            marker_color=PALETTE["primary"],
            text=[f"{v:.0f}%" for v in df_v["pct_parked_or_stored"]],
            textposition="outside",
            textfont=dict(family=MONO, color=PALETTE["text"]),
            hovertemplate="<b>%{x}</b><br>Parked/stored: %{y:.0f}%<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            x=df_v["variant"], y=df_v["ground_day_pct_sep2025"],
            name="Ground-day % (Sep 2025)",
            marker_color=PALETTE["accent"],
            text=[f"{v:.0f}%" for v in df_v["ground_day_pct_sep2025"]],
            textposition="outside",
            textfont=dict(family=MONO, color=PALETTE["text"]),
            hovertemplate="<b>%{x}</b><br>Ground-day (Sep 2025): %{y:.0f}%<extra></extra>",
        ))
        as_of = df_v["as_of_date"].max().strftime("%b %Y")
        fig.update_layout(
            **BASE_LAYOUT,
            title=dict(text="A320neo vs A321neo: Variant-Level Grounding Severity",
                       font=dict(size=15, color=PALETTE["text"])),
            xaxis=dict(title="", **DARK_AXIS),
            yaxis=dict(title="%", range=[0, 60], **DARK_AXIS),
            barmode="group",
            legend=dict(bgcolor="rgba(22,27,34,0.9)", borderwidth=1, bordercolor=PALETTE["border"]),
            annotations=[dict(
                text=f"Source: Aviation Week Fleet Discovery, as of {as_of}",
                xref="paper", yref="paper", x=0, y=-0.18, showarrow=False,
                font=dict(size=10, color=PALETTE["muted"]), xanchor="left",
            )],
        )
        print("  Built chart 6 (variant split)")
        return fig_to_div(fig)

    # Fallback: fleet size vs grounded bubble scatter
    latest = df_airlines.sort_values("date").groupby("airline", as_index=False).last()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=latest["total_gtf_fleet"], y=latest["grounded_aircraft"],
        mode="markers+text", text=latest["airline"],
        textposition="top center",
        textfont=dict(color=PALETTE["muted"], size=11),
        marker=dict(
            size=latest["pct_grounded"] * 1.8,
            color=latest["pct_grounded"],
            colorscale=[[0, PALETTE["primary"]], [0.5, "#c0a000"], [1, PALETTE["accent"]]],
            showscale=True,
            colorbar=dict(
                title=dict(text="% Grounded", font=dict(color=PALETTE["muted"])),
                tickfont=dict(family=MONO, color=PALETTE["muted"]),
                bgcolor=PALETTE["card_bg"], bordercolor=PALETTE["border"],
            ),
            line=dict(color=PALETTE["border"], width=1),
        ),
        hovertemplate="<b>%{text}</b><br>Fleet: %{x}<br>Grounded: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Fleet Size vs Aircraft Grounded (bubble = % grounded)",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Total GTF Fleet", **DARK_AXIS),
        yaxis=dict(title="Aircraft Grounded", **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart 6 (bubble scatter fallback)")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart 7 — Wizz Air public-sentiment score over time
# ---------------------------------------------------------------------------
def chart7() -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_comms["date"],
        y=df_comms["sentiment_score"],
        mode="lines+markers",
        name="Sentiment Score",
        line=dict(color=PALETTE["primary"], width=2),
        marker=dict(
            size=12,
            color=[SENTIMENT_COLOR.get(s, "#888") for s in df_comms["sentiment_score"]],
            line=dict(color=PALETTE["border"], width=1),
        ),
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>"
            "Score: %{y}/5<br>"
            "<extra></extra>"
        ),
        text=[SENTIMENT_LABEL.get(int(s), "") for s in df_comms["sentiment_score"]],
        textposition="top center",
        textfont=dict(size=10, color=PALETTE["muted"]),
    ))
    fig.add_hrect(y0=0, y1=2.5, fillcolor="rgba(232,116,59,0.06)", line_width=0)
    fig.add_hrect(y0=2.5, y1=5, fillcolor="rgba(61,122,153,0.06)", line_width=0)
    fig.add_hline(y=3, line_dash="dash", line_color=PALETTE["muted"], line_width=1,
                  annotation_text="Neutral", annotation_position="right",
                  annotation_font=dict(color=PALETTE["muted"], size=10))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Wizz Air Public Communication Sentiment Over Time",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(
            title="Sentiment Score (1=Very Pessimistic, 5=Very Optimistic)",
            range=[0.5, 5.5], dtick=1, **DARK_AXIS,
        ),
        showlegend=False,
    )
    print("  Built chart 7")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart 8 — Grounded vs flying fleet for all airlines (stacked bar)
# ---------------------------------------------------------------------------
def chart8() -> str:
    latest = (
        df_airlines
        .sort_values("date")
        .groupby("airline", as_index=False)
        .last()
        .sort_values("grounded_aircraft", ascending=False)
    )
    flying = latest["total_gtf_fleet"] - latest["grounded_aircraft"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Grounded",
        x=latest["airline"],
        y=latest["grounded_aircraft"],
        marker_color=PALETTE["accent"],
        hovertemplate="<b>%{x}</b><br>Grounded: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Flying",
        x=latest["airline"],
        y=flying,
        marker_color=PALETTE["primary"],
        marker_opacity=0.5,
        hovertemplate="<b>%{x}</b><br>Flying: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        barmode="stack",
        title=dict(text="GTF Fleet — Grounded vs Flying by Airline (Latest Snapshot)",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="", **DARK_AXIS),
        yaxis=dict(title="Aircraft", **DARK_AXIS),
        legend=dict(
            bgcolor="rgba(22,27,34,0.9)", borderwidth=1, bordercolor=PALETTE["border"],
        ),
    )
    print("  Built chart 8")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart fleet context — SVG density field (hero element)
# ---------------------------------------------------------------------------
def chart_fleet_context() -> str:
    latest    = df_global.sort_values("date").iloc[-1]
    grounded  = int(latest["grounded_aircraft"])
    fleet_tot = int(latest["total_gtf_fleet"])
    flying    = fleet_tot - grounded
    pct       = grounded / fleet_tot * 100

    cols  = 70
    rows  = 35          # 70 × 35 = 2450
    dot_r = 4
    gap   = 3
    step  = dot_r * 2 + gap   # 11 px

    dots = []
    for i in range(fleet_tot):
        # Bresenham-style even distribution of grounded aircraft
        prev = ((i - 1) * grounded) // fleet_tot if i > 0 else -1
        curr = (i * grounded) // fleet_tot
        is_grounded = curr > prev
        col = i % cols
        row = i // cols
        cx  = col * step + dot_r + 1
        cy  = row * step + dot_r + 1
        if is_grounded:
            dots.append(f'<circle cx="{cx}" cy="{cy}" r="{dot_r}" fill="#E8743B"/>')
        else:
            dots.append(f'<circle cx="{cx}" cy="{cy}" r="{dot_r}" fill="#3D7A99" fill-opacity="0.35"/>')

    svg_w = cols * step + dot_r + 2
    svg_h = rows * step + dot_r + 2

    svg = (
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" '
        f'aria-label="{grounded} of {fleet_tot} GTF aircraft grounded" '
        f'style="display:block;max-width:100%">'
        + "".join(dots)
        + "</svg>"
    )

    print("  Built chart_fleet_context (density field)")
    return f"""
<div class="fleet-density-wrap">
  <div class="fleet-density-header">
    <span class="accent-num">{grounded:,}</span>
    <span class="fleet-label"> of </span>
    <span class="primary-num">{fleet_tot:,}</span>
    <span class="fleet-label"> GTF aircraft grounded &mdash; </span>
    <span class="accent-num">{pct:.1f}%</span>
    <span class="fleet-label"> of global fleet</span>
  </div>
  <div class="fleet-density-legend">
    <span class="legend-item">
      <span class="legend-dot" style="background:#E8743B"></span>
      {grounded:,} grounded
    </span>
    <span class="legend-item">
      <span class="legend-dot" style="background:#3D7A99;opacity:0.5"></span>
      {flying:,} flying
    </span>
  </div>
  {svg}
</div>"""


# ---------------------------------------------------------------------------
# Chart fleet breakdown — absolute grounded counts by airline
# ---------------------------------------------------------------------------
def chart_fleet_breakdown() -> str:
    latest = (
        df_airlines
        .sort_values("date")
        .groupby("airline", as_index=False)
        .last()
        .sort_values("grounded_aircraft", ascending=True)
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=latest["airline"],
        x=latest["grounded_aircraft"],
        orientation="h",
        marker_color=PALETTE["accent"],
        text=latest["grounded_aircraft"].astype(int).astype(str),
        textposition="outside",
        textfont=dict(family=MONO, color=PALETTE["text"]),
        hovertemplate="<b>%{y}</b><br>Aircraft grounded: %{x}<extra></extra>",
        name="",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Aircraft Grounded by Airline — Absolute Count",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Aircraft Grounded", **DARK_AXIS),
        yaxis=dict(title="", **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart_fleet_breakdown")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart F1 — Wizz Air compensation received over reporting periods
# (Sourced from wizz_air_comms.csv key_claims: FY2024 annual results, H1 FY2025)
# ---------------------------------------------------------------------------
def chart_f1() -> str:
    comp_data = pd.DataFrame({
        "period": ["FY2024\n(to Mar 2024)", "H1 FY2025\n(to Sep 2024)"],
        "compensation_eur_m": [198.6, 146.0],
        "source": [
            "FY2024 Annual Results (May 2024)",
            "H1 FY2025 Earnings Call (Nov 2024)",
        ],
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=comp_data["period"],
        y=comp_data["compensation_eur_m"],
        marker_color=PALETTE["primary"],
        text=[f"€{v:.1f}M" for v in comp_data["compensation_eur_m"]],
        textposition="outside",
        textfont=dict(family=MONO, color=PALETTE["text"], size=13),
        hovertemplate="<b>%{x}</b><br>Compensation: €%{y:.1f}M<extra></extra>",
        name="",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Wizz Air — P&W Compensation Received by Reporting Period",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Reporting Period", **DARK_AXIS),
        yaxis=dict(title="Compensation (€M)", **DARK_AXIS),
        showlegend=False,
        annotations=[dict(
            text="Source: Wizz Air FY2024 Annual Results; H1 FY2025 Earnings Call",
            xref="paper", yref="paper", x=0, y=-0.18,
            showarrow=False, font=dict(size=10, color=PALETTE["muted"]),
            xanchor="left",
        )],
    )
    print("  Built chart_f1")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart F2 — Resolution-target slippage timeline (scatter drift chart)
# ---------------------------------------------------------------------------
def chart_f2() -> str:
    slippage = pd.DataFrame({
        "statement_date": pd.to_datetime([
            "2024-05-01", "2024-11-01", "2025-06-01", "2025-07-01", "2026-01-01",
        ]),
        "target_date": pd.to_datetime([
            "2026-12-31", "2027-03-31", "2027-12-31", "2027-03-31", "2027-12-31",
        ]),
        "label": [
            "FY2024 results", "H1 FY2025", "FY2025 results", "Q1 FY2026", "Q3 FY2026",
        ],
    })
    # Drift in months from first stated target
    base_target = slippage["target_date"].iloc[0]
    slippage["drift_months"] = (
        (slippage["target_date"] - base_target).dt.days / 30.44
    ).round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=slippage["statement_date"],
        y=slippage["target_date"],
        mode="lines+markers+text",
        text=slippage["label"],
        textposition="top right",
        textfont=dict(size=10, color=PALETTE["muted"]),
        line=dict(color=PALETTE["accent"], width=2, dash="dot"),
        marker=dict(size=10, color=PALETTE["accent"], symbol="diamond"),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Statement: %{x|%b %Y}<br>"
            "Stated target: %{y|%b %Y}<extra></extra>"
        ),
        name="Stated resolution target",
    ))
    # Reference line: original target
    fig.add_hline(
        y=slippage["target_date"].iloc[0].timestamp() * 1000,
        line_dash="dash", line_color=PALETTE["muted"], line_width=1,
        annotation_text="Original target (Dec 2026)",
        annotation_position="right",
        annotation_font=dict(size=10, color=PALETTE["muted"]),
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Wizz Air: Stated Resolution Target Drift Over Time",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date of Public Statement", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(title="Claimed Resolution Date", tickformat="%b %Y", **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart_f2")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart F3 — Wizz Air grounding rate (%) over time
# ---------------------------------------------------------------------------
def chart_f3() -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_wizz["date"],
        y=df_wizz["pct_grounded"],
        mode="lines+markers+text",
        name="% Fleet Grounded",
        line=dict(color=PALETTE["accent"], width=2.5),
        marker=dict(size=9, color=PALETTE["accent"]),
        fill="tozeroy",
        fillcolor="rgba(232,116,59,0.10)",
        text=[f"{v:.1f}%" for v in df_wizz["pct_grounded"]],
        textposition="top center",
        textfont=dict(family=MONO, size=10, color=PALETTE["accent"]),
        hovertemplate="<b>%{x|%b %Y}</b><br>Grounded: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(
        y=df_wizz["pct_grounded"].mean(), line_dash="dash",
        line_color=PALETTE["muted"], line_width=1,
        annotation_text=f"Period avg {df_wizz['pct_grounded'].mean():.1f}%",
        annotation_position="right",
        annotation_font=dict(size=10, color=PALETTE["muted"]),
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Wizz Air — % of GTF Fleet Grounded Over Time",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(title="% of GTF Fleet Grounded", **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart_f3")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart F4 — Global grounding rate (%) over time
# ---------------------------------------------------------------------------
def chart_f4() -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_global["date"],
        y=df_global["pct_grounded"],
        mode="lines+markers+text",
        name="% GTF Fleet Grounded (Global)",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=9, color=PALETTE["primary"]),
        fill="tozeroy",
        fillcolor="rgba(61,122,153,0.12)",
        text=[f"{v:.1f}%" for v in df_global["pct_grounded"]],
        textposition="top center",
        textfont=dict(family=MONO, size=11, color=PALETTE["primary"]),
        hovertemplate="<b>%{x|%b %Y}</b><br>Global grounded: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Global GTF Fleet — % Grounded Over Time",
                   font=dict(size=15, color=PALETTE["text"])),
        xaxis=dict(title="Date", tickformat="%b %Y", **DARK_AXIS),
        yaxis=dict(title="% of GTF Fleet Grounded", range=[25, 40], **DARK_AXIS),
        showlegend=False,
    )
    print("  Built chart_f4")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Structural vs Bridge section
# Uses ground_day / variant data when available; falls back to slippage table.
# ---------------------------------------------------------------------------
def structural_vs_bridge_section() -> str:
    if df_ground_day is not None and df_variant is not None:
        mro_latest    = 139
        mro_growth    = mro_latest - 100
        gtf_gd        = df_ground_day.loc[df_ground_day["engine_family"].str.contains("PW1000G"), "ground_day_pct_low"].iloc[0]
        leap_low, leap_high = df_ground_day.loc[df_ground_day["engine_family"] == "CFM Leap", ["ground_day_pct_low", "ground_day_pct_high"]].iloc[0]
        leg_low,  leg_high  = df_ground_day.loc[df_ground_day["engine_family"].str.contains("legacy"), ["ground_day_pct_low", "ground_day_pct_high"]].iloc[0]
        a320_pct = df_variant.loc[df_variant["variant"].str.contains("A320neo"), "pct_parked_or_stored"].iloc[0]
        a321_pct = df_variant.loc[df_variant["variant"].str.contains("A321neo"), "pct_parked_or_stored"].iloc[0]
        return f"""
<div class="card" style="margin-top:16px;border-left:3px solid {PALETTE['primary']}">
  <h3 class="card-label" style="color:{PALETTE['primary']}">Reading Charts 5 &amp; 6: Structural Backlog, Not a Short Bridge</h3>
  <div style="color:{PALETTE['muted']};font-size:0.93rem;line-height:1.7">
    <p>
      P&amp;W's own MRO output index rose from a baseline of 100 to roughly {mro_latest}
      (+{mro_growth}%) by late 2025 — genuine progress, and worth taking at face value.
      But a {mro_growth}% throughput improvement against a backlog this large is a rate of
      clearance, not a resolution date, and it has to be read against the fleet's actual
      availability: the GTF-powered fleet's ground-day rate sits around <span class="mono accent-text">{gtf_gd:.0f}%</span>,
      well above the {leap_low:.0f}–{leap_high:.0f}% rate of its closest rival (CFM Leap) and even
      above the {leg_low:.0f}–{leg_high:.0f}% rate of the older, more maintenance-hungry
      engines (CFM56, V2500) that GTF-powered aircraft were meant to retire.
    </p>
    <p style="margin-top:12px">
      That comparison is the tell. An engine family running less available than the aircraft it
      replaces, more than two years into a stated three-year inspection programme, points to a
      multi-year structural backlog rather than a bridge that clears on its own. The variant split
      sharpens this further: A320neo aircraft show <span class="mono accent-text">{a320_pct:.0f}%</span> parked or stored,
      against <span class="mono">{a321_pct:.0f}%</span> for the A321neo — recovery is uneven by variant, which
      argues against treating the backlog as a single countdown with one end date.
    </p>
    <p style="margin-top:12px">
      <strong style="color:{PALETTE['text']}">Working assumption:</strong> this should be modelled as a multi-year structural
      cost, not a short-term bridge that resolves cleanly once MRO throughput catches up.
    </p>
  </div>
</div>"""

    # Fallback: slippage table
    slippage_items = [
        ("May 2024", "End of calendar 2026", "Initial P&W compensation agreement horizon"),
        ("Nov 2024", "F27 (≈ Mar 2027)",     "H1 FY2025 results — quietly pushed 3 months"),
        ("Jun 2025", "End of calendar 2027", "FY2025 annual results — full 12-month slip acknowledged"),
        ("Jul 2025", "March 2027",            "Q1 FY2026 results — reiterated, no improvement"),
        ("Jan 2026", "End of calendar 2027", "Q3 FY2026 — P&W compensation now extended to match"),
    ]
    rows_html = "\n".join(
        f'<tr><td><span class="mono">{d}</span></td>'
        f'<td><span class="mono accent-text">{t}</span></td>'
        f'<td style="color:{PALETTE["muted"]};font-size:0.88rem">{n}</td></tr>'
        for d, t, n in slippage_items
    )
    return f"""
<div class="card" style="margin-top:16px">
  <h3 class="card-label" style="color:{PALETTE['accent']}">Structural vs Bridge: Resolution Timeline Slippage</h3>
  <p style="color:{PALETTE['muted']};font-size:0.92rem;margin:8px 0 16px">
    Each public guidance update moved the stated resolution date further out.
    Net slip: <span class="mono accent-text">12 months</span>.
  </p>
  <div style="overflow-x:auto">
    <table class="data-table">
      <thead><tr><th>Statement Date</th><th>Claimed Resolution</th><th>Context</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Wizz Air Narrative vs Reality section
# ---------------------------------------------------------------------------
def _nearest_grounding(target_date: pd.Timestamp) -> str:
    if df_wizz.empty:
        return "n/a"
    idx      = (df_wizz["date"] - target_date).abs().idxmin()
    row      = df_wizz.loc[idx]
    days_off = abs((row["date"] - target_date).days)
    count    = int(row["grounded_aircraft"])
    if days_off > 120:
        return f"{count} ⚠️ ({row['date'].strftime('%b %Y')} data)"
    return str(count)


def wizz_narrative_section() -> str:
    rows_html = []
    for _, row in df_comms.iterrows():
        score       = int(row["sentiment_score"])
        badge_color = SENTIMENT_COLOR.get(score, "#888")
        badge_label = SENTIMENT_LABEL.get(score, "")
        actual      = _nearest_grounding(row["date"])
        src_label   = row["source_type"].replace("_", " ").title()
        url         = row["url"]
        rows_html.append(f"""
        <tr>
          <td style="white-space:nowrap"><span class="mono">{row['date'].strftime('%b %Y')}</span></td>
          <td><span class="src-badge">{src_label}</span></td>
          <td><a href="{url}" target="_blank" rel="noopener" style="color:{PALETTE['primary']}">{row['headline']}</a></td>
          <td style="font-size:0.85rem;color:{PALETTE['muted']}">{row['key_claim']}</td>
          <td style="text-align:center;font-weight:700;font-family:{MONO}">{actual}</td>
          <td><span class="sentiment-badge" style="background:{badge_color}">{badge_label}</span></td>
        </tr>""")
    timeline_table = "\n".join(rows_html)

    scores    = df_comms["sentiment_score"].tolist()
    dates     = [d.strftime("%b %Y") for d in df_comms["date"]]
    avg       = sum(scores) / len(scores)
    trend_dir = "slightly more pessimistic" if scores[-1] < scores[0] else "broadly stable"
    trend_pips = "".join(
        f'<div class="sent-pip" style="background:{SENTIMENT_COLOR[s]}" title="{dates[i]}: {SENTIMENT_LABEL[s]}"></div>'
        for i, s in enumerate(scores)
    )

    return f"""
<div class="card wizz-narrative-card">
  <h3 class="card-label" style="color:{PALETTE['accent']}">Public Narrative vs Reality</h3>

  <div class="narrative-lede">
    <p>
      Wizz Air is the world's largest operator of Pratt &amp; Whitney GTF-powered aircraft and
      has been one of the hardest-hit airlines in the engine crisis. This section tracks their
      public statements — earnings calls, press releases, and CEO interviews — and compares them
      against the actual grounding numbers on or near those same dates.
    </p>
    <p style="margin-top:12px">
      <strong style="color:{PALETTE['text']}">Key finding:</strong> Wizz Air's stated resolution
      timeline has slipped by at least <strong style="color:{PALETTE['accent']}">12 months</strong>
      (from end-2026 to end-2027), while language in public communications turned noticeably more
      pessimistic through late 2025 before stabilising as grounding counts finally began to fall.
    </p>
    <p style="margin-top:12px;color:{PALETTE['muted']};font-size:0.9rem">
      <em>Note: Data before May 2024 is a gap — Wizz Air did not disclose specific grounded-aircraft
      counts in public statements prior to their FY2024 annual results.</em>
    </p>
  </div>

  <h4 class="subsection-label">Communications Timeline vs Actual Grounding Count</h4>
  <div style="overflow-x:auto">
    <table class="data-table wizz-table">
      <thead>
        <tr>
          <th>Date</th><th>Type</th><th>Headline / Source</th>
          <th>Key Claim</th><th>Actual Grounded</th><th>Sentiment</th>
        </tr>
      </thead>
      <tbody>
{timeline_table}
      </tbody>
    </table>
  </div>
  <p class="table-note">⚠️ flag = nearest available data point is &gt;120 days from statement date.</p>

  <h4 class="subsection-label" style="margin-top:28px">Sentiment Tracker</h4>
  <p style="font-size:0.9rem;color:{PALETTE['muted']};margin-bottom:10px">
    Each pip = one public communication, left-to-right chronologically.
    Trend is <strong style="color:{PALETTE['text']}">{trend_dir}</strong>
    (avg <span class="mono">{avg:.1f}</span>/5; 1 = Very Pessimistic, 5 = Very Optimistic).
  </p>
  <div class="sent-row">{trend_pips}</div>
  <div class="sent-legend">
    {"".join(
        f'<span><span class="sent-pip" style="background:{c};display:inline-block"></span> {l}</span>'
        for c, l in zip(SENTIMENT_COLOR.values(), SENTIMENT_LABEL.values())
    )}
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Derived summary values
# ---------------------------------------------------------------------------
print("Generating charts …")
div_chart1               = chart1()
div_chart2               = chart2()
div_chart3               = chart3()
div_chart4               = chart4()
div_chart5               = chart5()
div_chart6               = chart6()
div_chart7               = chart7()
div_chart8               = chart8()
div_fleet_context        = chart_fleet_context()
div_fleet_breakdown      = chart_fleet_breakdown()
div_chart_f1             = chart_f1()
div_chart_f2             = chart_f2()
div_chart_f3             = chart_f3()
div_chart_f4             = chart_f4()
div_structural_bridge    = structural_vs_bridge_section()
div_wizz_narrative       = wizz_narrative_section()

latest_global   = df_global.sort_values("date").iloc[-1]
first_global    = df_global.sort_values("date").iloc[0]
delta           = int(latest_global["grounded_aircraft"]) - int(first_global["grounded_aircraft"])
last_updated    = df["date"].max().strftime("%B %d, %Y").lstrip("0")
latest_date_str = latest_global["date"].strftime("%B %Y")
worst_airline   = (
    df_airlines.sort_values("date").groupby("airline").last()
    .sort_values("pct_grounded", ascending=False).iloc[0]
)
total_grounded  = int(latest_global["grounded_aircraft"])
total_fleet     = int(latest_global["total_gtf_fleet"])
pct_grounded    = latest_global["pct_grounded"]

summary = (
    f"As of {latest_date_str}, <strong>{total_grounded:,} GTF-powered aircraft</strong> "
    f"({pct_grounded:.1f}% of the global GTF fleet) remain on the ground awaiting "
    f"Pratt &amp; Whitney PW1000G engine inspections or repair — up from "
    f"{int(first_global['grounded_aircraft'])} ({first_global['pct_grounded']:.1f}%) in "
    f"{first_global['date'].strftime('%B %Y')}, a net increase of {delta} aircraft. "
    f"At the airline level, <strong>{worst_airline.name}</strong> is the hardest hit with "
    f"{worst_airline['pct_grounded']:.1f}% of its GTF fleet grounded. "
    f"On the supply-chain side, P&amp;W MRO throughput has improved — the internal output index "
    f"rose from 100 in 2024 to an estimated 139 by Q4 2025 — yet the grounded count continues "
    f"to climb, reflecting ongoing delivery of new aircraft that themselves require inspection "
    f"before entering service. The data suggests the crisis is not yet over."
)

SOURCES = [
    ("FlightGlobal / Cirium",                 "Fleet data and grounding counts, various dates 2024–2025"),
    ("RTX / Pratt &amp; Whitney Earnings Calls", "MRO output index and JetBlue fleet data (Q1 2025, Q1 2026)"),
    ("FlightGlobal",                           "Wizz Air, Volaris, VivaAerobus airline-level grounding figures"),
    ("Wizz Air Earnings Calls (FY2024–Q3 FY2026)", "Wizz Air grounded-aircraft counts and forward guidance — see <code>data/wizz_air_comms.csv</code> for full citation list"),
    ("Simple Flying / Aerotime / ch-aviation", "Wizz Air GTF communications tracking; interview quotes from CEO József Váradi and CFO Ian Malin"),
    ("Wizz Air RNS / SEC Filings",             "FY2025 Annual Results (5 Jun 2025); Q1 FY2026 Results (24 Jul 2025)"),
]
sources_rows = "\n".join(
    f"<tr><td>{s}</td><td>{d}</td></tr>" for s, d in SOURCES
)

# ---------------------------------------------------------------------------
# HTML report
 
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GTF Grounding Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* ── Reset & base ─────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
  background: #0E1116;
  color: #E6E9EE;
  line-height: 1.65;
  font-size: 15px;
}}
a {{ color: #3D7A99; text-decoration: none; }}
a:hover {{ color: #5aa0bf; text-decoration: underline; }}
code, .mono {{ font-family: 'JetBrains Mono', monospace; font-size: 0.9em; }}

/* ── Dashboard shell ─────────────────────────────────────────────────── */
.dashboard {{
  display: flex;
  min-height: 100vh;
}}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
.sidebar {{
  width: 220px;
  min-width: 220px;
  background: #161B22;
  border-right: 1px solid #21262D;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 28px 0 24px;
  flex-shrink: 0;
}}
.sidebar-brand {{
  padding: 0 20px 24px;
  border-bottom: 1px solid #21262D;
}}
.sidebar-brand .brand-name {{
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #8B93A1;
}}
.sidebar-brand .brand-title {{
  font-size: 1rem;
  font-weight: 600;
  color: #E6E9EE;
  margin-top: 4px;
  line-height: 1.3;
}}
.nav-section {{
  padding: 20px 0 0;
  flex: 1;
}}
.nav-label {{
  padding: 0 20px 6px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #8B93A1;
}}
.nav-list {{
  list-style: none;
  margin-bottom: 20px;
}}
.nav-list li a {{
  display: block;
  padding: 7px 20px;
  font-size: 0.88rem;
  color: #8B93A1;
  border-left: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}}
.nav-list li a:hover {{
  color: #E6E9EE;
  background: rgba(61,122,153,0.08);
  border-left-color: #3D7A99;
  text-decoration: none;
}}
.sidebar-meta {{
  padding: 16px 20px 0;
  border-top: 1px solid #21262D;
  font-size: 0.75rem;
  color: #8B93A1;
  line-height: 1.5;
}}

/* ── Content area ────────────────────────────────────────────────────── */
.content {{
  flex: 1;
  min-width: 0;
  padding: 36px 40px 80px;
  max-width: 1100px;
}}

/* ── Page header ─────────────────────────────────────────────────────── */
.dash-header {{
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #21262D;
}}
.dash-header h1 {{
  font-size: 1.75rem;
  font-weight: 600;
  color: #E6E9EE;
  letter-spacing: -0.3px;
}}
.dash-header .subtitle {{
  font-size: 0.95rem;
  color: #8B93A1;
  margin-top: 6px;
  font-weight: 300;
}}
.dash-header .meta {{
  font-size: 0.78rem;
  color: #8B93A1;
  margin-top: 8px;
  font-family: 'JetBrains Mono', monospace;
}}

/* ── Stat card row ───────────────────────────────────────────────────── */
.stat-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 28px;
}}
.stat-card {{
  background: #161B22;
  border: 1px solid #21262D;
  border-radius: 8px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
}}
.stat-card .stat-val {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.7rem;
  font-weight: 500;
  line-height: 1.1;
  color: #E6E9EE;
}}
.stat-card .stat-val.accent  {{ color: #E8743B; }}
.stat-card .stat-val.primary {{ color: #3D7A99; }}
.stat-card .stat-lbl {{
  font-size: 0.75rem;
  color: #8B93A1;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 500;
}}

/* ── Cards ───────────────────────────────────────────────────────────── */
.card {{
  background: #161B22;
  border: 1px solid #21262D;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 16px;
}}
.card-label {{
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 10px;
  color: #8B93A1;
}}
.chart-card {{
  padding: 8px 4px 4px;
  overflow: hidden;
}}

/* ── Two-column chart grid ───────────────────────────────────────────── */
.chart-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}}
.chart-grid .chart-card {{
  margin-bottom: 0;
}}
.chart-full {{ margin-bottom: 16px; }}

/* ── Section headings ────────────────────────────────────────────────── */
.section {{ margin-bottom: 48px; }}
.section-title {{
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #3D7A99;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #21262D;
}}
.subsection-label {{
  font-size: 0.85rem;
  font-weight: 600;
  color: #8B93A1;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 24px 0 10px;
}}

/* ── Fleet density field ─────────────────────────────────────────────── */
.fleet-density-wrap {{
  padding: 4px 0 8px;
}}
.fleet-density-header {{
  font-size: 1.5rem;
  font-weight: 500;
  margin-bottom: 10px;
  line-height: 1.3;
}}
.accent-num  {{ color: #E8743B; font-family: 'JetBrains Mono', monospace; }}
.primary-num {{ color: #3D7A99; font-family: 'JetBrains Mono', monospace; }}
.accent-text {{ color: #E8743B; }}
.fleet-label {{ color: #8B93A1; font-size: 0.9em; }}
.fleet-density-legend {{
  display: flex;
  gap: 20px;
  margin-bottom: 14px;
  font-size: 0.82rem;
  color: #8B93A1;
  font-family: 'JetBrains Mono', monospace;
}}
.legend-item {{ display: flex; align-items: center; gap: 7px; }}
.legend-dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}}

/* ── Summary box ─────────────────────────────────────────────────────── */
.summary-card {{
  border-left: 3px solid #3D7A99;
  font-size: 0.93rem;
  color: #8B93A1;
  line-height: 1.7;
}}
.summary-card strong {{ color: #E6E9EE; }}

/* ── Tables ───────────────────────────────────────────────────────────── */
.data-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}}
.data-table th, .data-table td {{
  text-align: left;
  padding: 9px 12px;
  border-bottom: 1px solid #21262D;
  vertical-align: top;
}}
.data-table th {{
  background: rgba(61,122,153,0.08);
  color: #3D7A99;
  font-weight: 600;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.data-table tr:last-child td {{ border-bottom: none; }}
.data-table tr:hover td {{ background: rgba(255,255,255,0.02); }}
.wizz-table tr:hover td {{ background: rgba(232,116,59,0.04); }}

/* ── Badges ───────────────────────────────────────────────────────────── */
.src-badge {{
  background: rgba(61,122,153,0.15);
  color: #3D7A99;
  font-size: 0.75rem;
  padding: 2px 7px;
  border-radius: 10px;
  white-space: nowrap;
  border: 1px solid rgba(61,122,153,0.25);
}}
.sentiment-badge {{
  color: #fff;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
  font-weight: 500;
}}

/* ── Wizz narrative card ─────────────────────────────────────────────── */
.wizz-narrative-card {{ border-left: 3px solid #E8743B; }}
.narrative-lede {{
  color: #8B93A1;
  font-size: 0.93rem;
  margin-bottom: 16px;
  line-height: 1.7;
}}

/* ── Sentiment tracker ───────────────────────────────────────────────── */
.sent-row {{
  display: flex;
  gap: 6px;
  margin: 6px 0 10px;
  flex-wrap: wrap;
}}
.sent-pip {{
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: inline-block;
  cursor: default;
}}
.sent-legend {{
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  font-size: 0.8rem;
  color: #8B93A1;
  margin-top: 4px;
  align-items: center;
}}
.sent-legend span {{
  display: flex;
  align-items: center;
  gap: 5px;
}}
.table-note {{ font-size: 0.78rem; color: #8B93A1; margin-top: 4px; }}

/* ── Sources section ─────────────────────────────────────────────────── */
.sources-section {{ margin-top: 48px; }}

/* ── Footer ──────────────────────────────────────────────────────────── */
footer {{
  margin-top: 48px;
  font-size: 0.78rem;
  color: #8B93A1;
  text-align: center;
  border-top: 1px solid #21262D;
  padding-top: 20px;
}}

/* ── Responsive ───────────────────────────────────────────────────────── */
@media (max-width: 900px) {{
  .stat-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .chart-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 768px) {{
  .dashboard {{ flex-direction: column; }}
  .sidebar {{
    width: 100%; min-width: 0; height: auto;
    position: static; border-right: none;
    border-bottom: 1px solid #21262D;
    padding: 16px 0;
  }}
  .nav-list li a {{ padding: 6px 16px; }}
  .sidebar-brand {{ padding: 0 16px 16px; }}
  .sidebar-meta {{ display: none; }}
  .content {{ padding: 20px 16px 60px; }}
  .fleet-density-header {{ font-size: 1.1rem; }}
}}
</style>
</head>
<body>
<div class="dashboard">

  <!-- ── Sidebar ────────────────────────────────────────────────────── -->
  <nav class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-name">Live Monitoring</div>
      <div class="brand-title">GTF Grounding Tracker</div>
    </div>
    <div class="nav-section">
      <div class="nav-label">Sections</div>
      <ul class="nav-list">
        <li><a href="#overview">Overview</a></li>
        <li><a href="#fleet">Fleet Breakdown</a></li>
        <li><a href="#financial">Financial Lens</a></li>
        <li><a href="#wizz">Wizz Air</a></li>
        <li><a href="#sources">Data Sources</a></li>
      </ul>
    </div>
    <div class="sidebar-meta">
      Last updated<br>
      <span class="mono" style="color:#E6E9EE">{last_updated}</span>
    </div>
  </nav>

  <!-- ── Main content ───────────────────────────────────────────────── -->
  <main class="content">

    <header class="dash-header">
      <h1>GTF Grounding Tracker</h1>
      <p class="subtitle">Tracking the Pratt &amp; Whitney PW1000G crisis — fleet impact, supply-chain drag, and recovery signals</p>
      <p class="meta">Last updated: {last_updated}</p>
    </header>

    <!-- Stat cards -->
    <div class="stat-grid">
      <div class="stat-card">
        <span class="stat-val accent">{total_grounded:,}</span>
        <span class="stat-lbl">Aircraft Grounded</span>
      </div>
      <div class="stat-card">
        <span class="stat-val primary">{total_fleet:,}</span>
        <span class="stat-lbl">Total GTF Fleet</span>
      </div>
      <div class="stat-card">
        <span class="stat-val accent">{pct_grounded:.1f}%</span>
        <span class="stat-lbl">Global Grounding Rate</span>
      </div>
      <div class="stat-card">
        <span class="stat-val primary">€198.6M</span>
        <span class="stat-lbl">Wizz Air P&amp;W Compensation (FY2024)</span>
      </div>
    </div>

    <!-- ── SECTION: Overview ─────────────────────────────────────────── -->
    <section id="overview" class="section">
      <h2 class="section-title">Overview</h2>

      <!-- Density field hero -->
      <div class="card">
        <div class="card-label">Fleet Status — {latest_date_str}</div>
        {div_fleet_context}
      </div>

      <!-- Summary -->
      <div class="card summary-card">
        <p>{summary}</p>
      </div>

      <!-- Charts -->
      <div class="chart-grid">
        <div class="card chart-card">{div_chart1}</div>
        <div class="card chart-card">{div_chart_f4}</div>
      </div>
      <div class="chart-full card chart-card">{div_chart5}</div>
    </section>

    <!-- ── SECTION: Fleet Breakdown ─────────────────────────────────── -->
    <section id="fleet" class="section">
      <h2 class="section-title">Fleet Breakdown</h2>
      <div class="chart-grid">
        <div class="card chart-card">{div_chart2}</div>
        <div class="card chart-card">{div_fleet_breakdown}</div>
      </div>
      <div class="chart-grid">
        <div class="card chart-card">{div_chart8}</div>
        <div class="card chart-card">{div_chart6}</div>
      </div>
    </section>

    <!-- ── SECTION: Financial Lens ──────────────────────────────────── -->
    <section id="financial" class="section">
      <h2 class="section-title">Financial Lens</h2>
      <div class="chart-grid">
        <div class="card chart-card">{div_chart3}</div>
        <div class="card chart-card">{div_chart_f1}</div>
      </div>
      <div class="chart-grid">
        <div class="card chart-card">{div_chart_f2}</div>
        <div class="card chart-card">{div_chart_f3}</div>
      </div>
      {div_structural_bridge}
    </section>

    <!-- ── SECTION: Wizz Air Deep Dive ─────────────────────────────── -->
    <section id="wizz" class="section">
      <h2 class="section-title">Wizz Air Deep Dive</h2>
      <div class="chart-grid">
        <div class="card chart-card">{div_chart4}</div>
        <div class="card chart-card">{div_chart7}</div>
      </div>
      {div_wizz_narrative}
    </section>

    <!-- ── SECTION: Data Sources ────────────────────────────────────── -->
    <section id="sources" class="sources-section section">
      <h2 class="section-title">Data Sources</h2>
      <div class="card">
        <table class="data-table">
          <thead><tr><th>Source</th><th>Coverage</th></tr></thead>
          <tbody>
            {sources_rows}
          </tbody>
        </table>
      </div>
    </section>

    <footer>
      <p>Data updated manually. See <code>data/grounding_counts.csv</code> to add new entries. |
         All figures validated against cited sources — do not edit inline.</p>
    </footer>

  </main>
</div>
</body>
</html>
"""

print("Writing report …")
REPORT_FILE.write_text(html, encoding="utf-8")
print(f"  Saved {REPORT_FILE.relative_to(ROOT)}")
print()
print("Done. Open index.html to view the report.")
