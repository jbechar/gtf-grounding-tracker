# Data Sources

All figures used in `data/grounding_counts.csv` are sourced from publicly available reporting and corporate disclosures. Raw source URLs are not included because fleet data is typically gated behind subscriptions or paginated earnings transcripts; the citations below are sufficient to verify the figures.

---

## FlightGlobal / Cirium

Industry databases that aggregate airline fleet and grounding data from lessors, regulators, and airlines. Used for:
- Global grounded-count totals (Oct 2024, Feb 2025, Jul 2025, Oct 2025)
- Volaris and VivaAerobus airline-level figures (Oct 2025)
- Wizz Air airline-level figures (Jul 2025, Oct 2025)

## RTX / Pratt & Whitney Earnings Calls

Quarterly investor presentations and earnings call transcripts from RTX Corporation (NYSE: RTX). Used for:
- JetBlue grounded-count figures (Q1 2025, Q1 2026 calls)
- MRO output index (2024 baseline = 100; 2025 = 126; Q4 2025 = 139)

The MRO index is derived from RTX disclosures describing the percentage increase in shop-visit throughput relative to 2024 levels. It is not an official RTX-published index; it is computed from verbal disclosures and should be treated as indicative rather than precise.

---

## Wizz Air Public Communications (`data/wizz_air_comms.csv`)

Statements and disclosures used to populate the Wizz Air narrative tracker. All sources are publicly available.

| Date | Source | URL |
|------|--------|-----|
| May 2024 | ch-aviation — "Wizz Air secures PW compensation but groundings persist" | https://www.ch-aviation.com/news/140655-wizz-air-secures-pw-compensation-but-groundings-persist |
| Aug 2024 | Skift — "Wizz Air Reports Drop in Earnings as Aircraft Groundings Bite" | https://skift.com/2024/08/01/wizz-air-reports-drop-in-earnings-as-aircraft-groundings-bite/ |
| Nov 2024 | Simple Flying — "Wizz Air Sees H1 Earnings Drop To $888 Million As P&W GTF Engine Issues Increase Operating Costs" | https://simpleflying.com/wizz-air-h1-earnings-drop-888-million-pratt-whitney-engine-gtf-engine-costs/ |
| Jan 2025 | Simple Flying — "40 Wizz Air Airbus Planes Will Remain Grounded Until 2026 Due To Pratt & Whitney Engine Issues" | https://simpleflying.com/40-wizz-air-airbus-planes-remain-grounded-until-2026-pratt-whitney/ |
| Jun 2025 | Wizz Air RNS — "Results for the 12 Months to 31 March 2025" | https://s204.q4cdn.com/169340705/files/doc_news/Final-Results-2025.pdf |
| Jul 2025 | Aerospace Global News — "GTF engine issues hit Wizz Air profits: Airbus groundings until 2027" | https://aerospaceglobalnews.com/news/wizz-air-gtf-engine-issues-2027-pratt-whitney-advantage/ |
| Aug 2025 | AJ Bell — "Wizz Air strikes compensation deal for grounded aircraft" | https://www.ajbell.co.uk/articles/latestnews/283945/wizz-air-strikes-compensation-deal-grounded-aircraft |
| Oct 2025 | Simple Flying — "Wizz Air Says P&W Engine Issues Will Continue Until End Of 2027" | https://simpleflying.com/wizz-air-engine-issues-end-of-2027/ |
| Jan 2026 | Investing.com — "Earnings call transcript: Wizz Air Q3 2026 sees 10% revenue growth, net loss narrows" | https://www.investing.com/news/transcripts/earnings-call-transcript-wizz-air-q3-2026-sees-10-revenue-growth-net-loss-narrows-93CH-4472487 |

### Data gaps
- Pre-May 2024 Wizz Air earnings calls (FY2023, H1 FY2024) did not include specific grounded-aircraft counts in publicly available summaries. Figures for those periods are not included in `wizz_air_comms.csv` to avoid speculation.
- Sentiment scores (1–5 scale) are editorial assessments based on language tone in the cited source, not a quantitative model. See `generate_report.py` for scoring rationale.

---

## Notes on accuracy

- Fleet sizes (denominator in `pct_grounded`) are approximate and vary by source.
- Grounding counts represent aircraft awaiting inspection or awaiting return of inspected/repaired engines, and may include aircraft newly delivered with uninspected engines.
- "Global" totals combine GTF variants: PW1100G (A320neo), PW1500G (A220), PW1900G (E2), and PW1400G (MC-21).
- All figures are point-in-time snapshots; the actual grounded count fluctuates daily.
