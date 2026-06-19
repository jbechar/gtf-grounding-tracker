# GTF Grounding Tracker

Tracks how many **Pratt & Whitney GTF-powered aircraft** (A220, A320neo-family, A220) are grounded globally over time, which airlines are most affected, and whether the supply-chain situation is improving.

The GTF crisis began in 2023 when P&W identified a manufacturing defect in powder metal used in high-pressure turbine discs, forcing a large-scale inspection and replacement programme that is still ongoing. At peak (late 2025), more than 835 aircraft — roughly a third of the entire global GTF fleet — were simultaneously out of service.

---

## How to run

```bash
pip install -r requirements.txt
python generate_report.py
```

That's it. The script will:
1. Load `data/grounding_counts.csv`, `data/wizz_air_comms.csv`, `data/ground_day_comparison.csv`, and `data/variant_split.csv`
2. Build six interactive Plotly charts
3. Produce a self-contained HTML report at `index.html` with all charts embedded inline
4. Print `Done. Open index.html to view the report.`

Open `index.html` in any browser (requires an internet connection on first load, to pull the Plotly JS library from CDN). This is also the file published via GitHub Pages.

---

## Charts

1. **Global Grounding Trend** — total GTF-powered aircraft grounded worldwide over time
2. **Most Affected Airlines** — % of each airline's GTF fleet grounded (latest snapshot)
3. **Groundings vs MRO Recovery** — grounding count against P&W's internal MRO output index
4. **Wizz Air: Grounding Trajectory vs PR Moments** — Wizz Air's actual grounding numbers plotted against its own public statements, with a sentiment score per statement
5. **Ground-Day Rate: GTF vs Competing Engines** — PW1000G ground-day rate vs CFM Leap and older engines (CFM56/V2500), via `data/ground_day_comparison.csv`
6. **A320neo vs A321neo Variant Split** — grounding severity by aircraft variant, via `data/variant_split.csv`

Charts 5 and 6 use Aviation Week Fleet Discovery data (≥30-day grounding threshold), a different methodology from the FlightGlobal/Cirium-based Charts 1–4. See `sources.md` for details — don't directly compare percentages across that boundary.

---

## Updating the data

All core data lives in **`data/grounding_counts.csv`**. Add a new row each month (or whenever a new public figure is available) and re-run `python generate_report.py`. The report rebuilds automatically.

Column reference:

| Column | Description |
|---|---|
| `date` | YYYY-MM-DD snapshot date |
| `airline` | Airline name, or `Global` for the worldwide total |
| `grounded_aircraft` | Number of aircraft grounded on that date |
| `total_gtf_fleet` | Total GTF-powered aircraft in that airline's fleet (or global fleet) |
| `pct_grounded` | `grounded_aircraft / total_gtf_fleet × 100` |
| `source` | Publication or earnings call this data point comes from |

`data/wizz_air_comms.csv`, `data/ground_day_comparison.csv`, and `data/variant_split.csv` feed Charts 4, 5, and 6 respectively — see each file's header row for its own column reference.

---

## Project structure

```
gtf-grounding-tracker/
├── data/
│   ├── grounding_counts.csv        ← core series, add new rows here
│   ├── wizz_air_comms.csv          ← Wizz Air public statements vs reality (Chart 4)
│   ├── ground_day_comparison.csv   ← GTF vs Leap vs legacy engines (Chart 5)
│   └── variant_split.csv           ← A320neo vs A321neo (Chart 6)
├── index.html                   ← auto-generated report (published via GitHub Pages, root)
├── charts/                      ← legacy static PNGs, superseded by interactive charts in index.html
├── generate_report.py           ← single entry point
├── requirements.txt
├── README.md
└── sources.md
```

---

## Why this matters

The GTF crisis is the largest simultaneous grounding event in commercial aviation history. Airlines have lost billions in revenue and capacity, lessors are owed deferred lease payments, and Pratt & Whitney's parent RTX has set aside billions in reserves. The situation directly affects airfares, aircraft availability, and the near-term order books of Airbus and its customers.
