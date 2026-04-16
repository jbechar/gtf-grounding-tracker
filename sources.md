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

## Notes on accuracy

- Fleet sizes (denominator in `pct_grounded`) are approximate and vary by source.
- Grounding counts represent aircraft awaiting inspection or awaiting return of inspected/repaired engines, and may include aircraft newly delivered with uninspected engines.
- "Global" totals combine GTF variants: PW1100G (A320neo), PW1500G (A220), PW1900G (E2), and PW1400G (MC-21).
- All figures are point-in-time snapshots; the actual grounded count fluctuates daily.
