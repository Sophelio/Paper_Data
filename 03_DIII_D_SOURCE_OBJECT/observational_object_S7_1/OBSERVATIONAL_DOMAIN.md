# Observational domain

| Property | Value | Evidence |
|---|---|---|
| Device | DIII-D | provider documentation |
| Discharges | 62 | `ADMISSIBLE_SHOTS`; corroborated by ledger and export inventories |
| Quantities per discharge | 95 | direct inspection of all 62 archives |
| Completeness | every quantity present in every discharge | `availability_matrix.csv` |
| Time units | milliseconds | provider docstrings, provenance doc §2.1 |
| Native spacing | ~0.02 ms (filterscopes) to ~20 ms (equilibrium) | provider docstring |
| Common-support duration | 4.08 / 4.96 / 6.02 s (min/median/max) | discharge ledger |
| Analysis grid | 1000 points, dt 4.1–6.0 ms, varies by discharge | ledger `grid_dt_seconds` |
| Date range | **UNRESOLVED** | no date field in any artifact |
| Operating regimes | **NOT_DOCUMENTED** | no regime label in any artifact |
| Event preselection | ELM-study library; exact criterion unknown | provenance doc §3.2 |
| Inclusion criterion | common-grid viability across all 95 signals | provenance doc §3.1 |
| Exclusion log | **UNRESOLVED** | no candidate list or exclusion record in-repo |

## What may and may not be said

**May:** the object is 62 DIII-D discharges drawn from an ELM-study library, each
carrying 95 quantities on per-signal millisecond time bases, complete in the
signal × discharge sense.

**May not:** that the cohort is representative of any operating regime, that it
is a random sample, that it spans a stated campaign or date range, or that
regime labels can be attached. None of these are supported. Regime labels in
particular must not be inferred from the traces.
