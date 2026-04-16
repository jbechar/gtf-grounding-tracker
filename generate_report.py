"""
GTF Grounding Tracker — single-command report generator.
Run: python generate_report.py
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "grounding_counts.csv"
DOCS_DIR = ROOT / "docs"
REPORT_FILE = DOCS_DIR / "index.html"

DOCS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
PALETTE = {
    "primary": "#1a6fb5",
    "accent":  "#e85d26",
    "mid":     "#2eaa6e",
    "muted":   "#8da9c4",
    "bg":      "#f7f9fc",
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading data …")
df = pd.read_csv(DATA_FILE, parse_dates=["date"])
df["airline"] = df["airline"].str.strip()
df_global   = df[df["airline"] == "Global"].sort_values("date").copy()
df_airlines = df[df["airline"] != "Global"].copy()


# ---------------------------------------------------------------------------
# Shared layout defaults
# ---------------------------------------------------------------------------
BASE_LAYOUT = dict(
    paper_bgcolor=PALETTE["bg"],
    plot_bgcolor=PALETTE["bg"],
    font=dict(family="system-ui, -apple-system, sans-serif", color="#333"),
    margin=dict(l=60, r=40, t=60, b=60),
    hoverlabel=dict(bgcolor="white", font_size=13),
)


def fig_to_div(fig: go.Figure, first: bool = False) -> str:
    """Return an HTML <div> string for embedding. CDN script included on first chart only."""
    include_js = "cdn" if first else False
    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=include_js,
        config={"displayModeBar": True, "responsive": True},
    )


# ---------------------------------------------------------------------------
# Chart 1 — Global grounding trend over time
# ---------------------------------------------------------------------------
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
        fillcolor="rgba(26,111,181,0.10)",
        text=df_global["grounded_aircraft"].astype(int).astype(str),
        textposition="top center",
        textfont=dict(color=PALETTE["primary"], size=11),
        hovertemplate="<b>%{x|%b %Y}</b><br>Grounded: %{y}<extra></extra>",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="GTF Aircraft Grounded Globally Over Time", font=dict(size=15, color="#222")),
        xaxis=dict(title="Date", tickformat="%b %Y", showgrid=True, gridcolor="#e0e0e0"),
        yaxis=dict(title="Aircraft Grounded", range=[600, 920], dtick=50,
                   showgrid=True, gridcolor="#e0e0e0"),
        showlegend=False,
    )

    print("  Built chart 1")
    return fig_to_div(fig, first=True)


# ---------------------------------------------------------------------------
# Chart 2 — Most affected airlines (latest snapshot per airline)
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
        PALETTE["accent"] if p >= 40 else
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
        hovertemplate="<b>%{y}</b><br>Grounded: %{x:.1f}%<extra></extra>",
        name="",
    ))

    # Global-avg reference line
    fig.add_vline(x=30, line_dash="dash", line_color=PALETTE["muted"],
                  line_width=1.5,
                  annotation_text="Global avg ~34%",
                  annotation_position="top right",
                  annotation_font=dict(size=11, color=PALETTE["muted"]))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="% of GTF Fleet Grounded by Airline (Latest Data)", font=dict(size=15, color="#222")),
        xaxis=dict(title="% of GTF Fleet Grounded", range=[0, 60],
                   showgrid=True, gridcolor="#e0e0e0"),
        yaxis=dict(title=""),
        showlegend=False,
    )

    print("  Built chart 2")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Chart 3 — Groundings vs MRO Recovery (dual axis)
# ---------------------------------------------------------------------------
def chart3() -> str:
    mro_data = pd.DataFrame({
        "date":      pd.to_datetime(["2024-01-01", "2025-01-01", "2025-10-01"]),
        "mro_index": [100, 126, 139],
    })

    fig = go.Figure()

    # Groundings (left y-axis)
    fig.add_trace(go.Scatter(
        x=df_global["date"],
        y=df_global["grounded_aircraft"],
        mode="lines+markers",
        name="Aircraft Grounded",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=9, color=PALETTE["primary"]),
        fill="tozeroy",
        fillcolor="rgba(26,111,181,0.08)",
        yaxis="y1",
        hovertemplate="<b>%{x|%b %Y}</b><br>Grounded: %{y}<extra></extra>",
    ))

    # MRO index (right y-axis)
    fig.add_trace(go.Scatter(
        x=mro_data["date"],
        y=mro_data["mro_index"],
        mode="lines+markers+text",
        name="P&W MRO Output Index",
        line=dict(color=PALETTE["accent"], width=2.5, dash="dash"),
        marker=dict(size=9, symbol="square", color=PALETTE["accent"]),
        text=mro_data["mro_index"].astype(int).astype(str),
        textposition="top center",
        textfont=dict(color=PALETTE["accent"], size=11),
        yaxis="y2",
        hovertemplate="<b>%{x|%b %Y}</b><br>MRO Index: %{y}<extra></extra>",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Groundings vs MRO Recovery", font=dict(size=15, color="#222")),
        xaxis=dict(title="Date", tickformat="%b %Y", showgrid=True, gridcolor="#e0e0e0"),
        yaxis=dict(
            title=dict(text="Aircraft Grounded", font=dict(color=PALETTE["primary"])),
            tickfont=dict(color=PALETTE["primary"]),
            range=[600, 920],
            dtick=50,
            showgrid=True,
            gridcolor="#e0e0e0",
        ),
        yaxis2=dict(
            title=dict(text="MRO Output Index (2024 = 100)", font=dict(color=PALETTE["accent"])),
            tickfont=dict(color=PALETTE["accent"]),
            overlaying="y",
            side="right",
            range=[80, 160],
            showgrid=False,
        ),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)", borderwidth=1),
    )

    print("  Built chart 3")
    return fig_to_div(fig)


# ---------------------------------------------------------------------------
# Generate chart HTML snippets
# ---------------------------------------------------------------------------
print("Generating charts …")
div_chart1 = chart1()
div_chart2 = chart2()
div_chart3 = chart3()


# ---------------------------------------------------------------------------
# Plain-English summary
# ---------------------------------------------------------------------------
latest_global  = df_global.sort_values("date").iloc[-1]
first_global   = df_global.sort_values("date").iloc[0]
delta          = int(latest_global["grounded_aircraft"]) - int(first_global["grounded_aircraft"])
last_updated   = df["date"].max().strftime("%B %d, %Y").lstrip("0")
latest_date_str = latest_global["date"].strftime("%B %Y")
worst_airline  = (
    df_airlines.sort_values("date").groupby("airline").last()
    .sort_values("pct_grounded", ascending=False).iloc[0]
)

summary = (
    f"As of {latest_date_str}, <strong>{int(latest_global['grounded_aircraft'])} GTF-powered aircraft</strong> "
    f"({latest_global['pct_grounded']:.1f}% of the global GTF fleet) remain on the ground awaiting "
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


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
SOURCES = [
    ("FlightGlobal / Cirium", "Fleet data and grounding counts, various dates 2024–2025"),
    ("RTX / Pratt &amp; Whitney Earnings Calls", "MRO output index and JetBlue fleet data (Q1 2025, Q1 2026)"),
    ("FlightGlobal", "Wizz Air, Volaris, VivaAerobus airline-level grounding figures"),
]

sources_rows = "\n".join(
    f"<tr><td>{s}</td><td>{d}</td></tr>" for s, d in SOURCES
)


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GTF Grounding Tracker</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #f0f4f8;
    color: #222;
    line-height: 1.65;
  }}
  .container {{ max-width: 980px; margin: 0 auto; padding: 36px 24px 64px; }}
  header {{ margin-bottom: 36px; border-bottom: 3px solid #1a6fb5; padding-bottom: 20px; }}
  header h1 {{ font-size: 2rem; color: #1a6fb5; letter-spacing: -0.5px; }}
  header .subtitle {{ font-size: 1.05rem; color: #555; margin-top: 6px; }}
  .meta {{ font-size: 0.85rem; color: #888; margin-top: 8px; }}
  .summary-box {{
    background: #fff;
    border-left: 4px solid #1a6fb5;
    border-radius: 6px;
    padding: 18px 22px;
    margin-bottom: 36px;
    font-size: 0.97rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .chart-section {{ margin-bottom: 40px; }}
  .chart-section h2 {{
    font-size: 1.1rem;
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid #ddd;
  }}
  .chart-section .plotly-chart {{
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    background: #f7f9fc;
    overflow: hidden;
  }}
  .sources-section {{ margin-top: 48px; }}
  .sources-section h2 {{ font-size: 1.1rem; color: #333; margin-bottom: 14px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th, td {{ text-align: left; padding: 10px 14px; border-bottom: 1px solid #e4e8ee; }}
  th {{ background: #e8f0fa; color: #1a6fb5; font-weight: 600; }}
  tr:last-child td {{ border-bottom: none; }}
  footer {{ margin-top: 48px; font-size: 0.8rem; color: #aaa; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>GTF Grounding Tracker</h1>
    <p class="subtitle">Tracking the Pratt &amp; Whitney GTF crisis — supply chain drag, fleet impact, and recovery signals</p>
    <p class="meta">Last updated: {last_updated}</p>
  </header>

  <div class="summary-box">
    <p>{summary}</p>
  </div>

  <div class="chart-section">
    <h2>Chart 1 — Global Grounding Trend</h2>
    <div class="plotly-chart">
      {div_chart1}
    </div>
  </div>

  <div class="chart-section">
    <h2>Chart 2 — Most Affected Airlines</h2>
    <div class="plotly-chart">
      {div_chart2}
    </div>
  </div>

  <div class="chart-section">
    <h2>Chart 3 — Groundings vs MRO Recovery</h2>
    <div class="plotly-chart">
      {div_chart3}
    </div>
  </div>

  <div class="sources-section">
    <h2>Data Sources</h2>
    <table>
      <thead><tr><th>Source</th><th>Coverage</th></tr></thead>
      <tbody>
        {sources_rows}
      </tbody>
    </table>
  </div>

  <footer>
    <p>Data is updated manually. See <code>data/grounding_counts.csv</code> to add new entries.</p>
  </footer>
</div>
</body>
</html>
"""

print("Writing report …")
REPORT_FILE.write_text(html, encoding="utf-8")
print(f"  Saved {REPORT_FILE.relative_to(ROOT)}")
print()
print("Done. Open docs/index.html to view the report.")
