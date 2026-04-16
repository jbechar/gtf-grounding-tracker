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
1. Load `data/grounding_counts.csv`
2. Generate three charts and save them as PNGs in `charts/`
3. Produce a self-contained HTML report at `output/report.html` with all charts embedded inline
4. Print `Done. Open output/report.html to view the report.`

Open `output/report.html` in any browser — no internet connection required.

---

## Updating the data

All data lives in **`data/grounding_counts.csv`**. Add a new row each month (or whenever a new public figure is available) and re-run `python generate_report.py`. The report rebuilds automatically.

Column reference:

| Column | Description |
|---|---|
| `date` | YYYY-MM-DD snapshot date |
| `airline` | Airline name, or `Global` for the worldwide total |
| `grounded_aircraft` | Number of aircraft grounded on that date |
| `total_gtf_fleet` | Total GTF-powered aircraft in that airline's fleet (or global fleet) |
| `pct_grounded` | `grounded_aircraft / total_gtf_fleet × 100` |
| `source` | Publication or earnings call this data point comes from |

---

## Project structure

```
gtf-grounding-tracker/
├── data/
│   └── grounding_counts.csv   ← add new rows here
├── charts/                    ← auto-generated PNGs
├── output/
│   └── report.html            ← auto-generated report
├── generate_report.py         ← single entry point
├── requirements.txt
├── README.md
└── sources.md
```

---

## Why this matters

The GTF crisis is the largest simultaneous grounding event in commercial aviation history. Airlines have lost billions in revenue and capacity, lessors are owed deferred lease payments, and Pratt & Whitney's parent RTX has set aside billions in reserves. The situation directly affects airfares, aircraft availability, and the near-term order books of Airbus and its customers.
