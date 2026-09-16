# S7.1R-FINAL — Backend loading and parity audit

Machine-readable form: `DALIA_SIGNAL_PARITY.csv` (95 rows).

> Implementation detail. The backend is named here because this is the internal
> audit record. Manuscript-facing prose says only "the analysis backend".

## Verdict

```
DALIA_ACCESSIBLE_SIGNALS = 95 / 95
```

All 95 signals return `EXACT_IDENTITY`. No signal is `ALIAS_ONLY`, `MISMATCH`,
or `UNRESOLVED`; no signal required a `DOCUMENTED_TRANSFORMATION` verdict,
because the backend returns native arrays with no common-grid transformation
applied.

## What changed

The backend previously exposed **12** signals and, separately, hard-restricted
the SIR path to **8** through an allow-list in `_common_grid_fetch` that raised
`KeyError` for anything else. Two independent limits, both now removed. The
8-signal restriction was historical convention, not a documented scientific
decision.

Backend provider updated to v164; catalog reloaded and re-read.

## Method

Pulling all 5890 arrays through the backend RPC is not feasible, so parity rests
on three legs. The third is what makes the first two more than an assertion.

**1 — Catalog parity.** The backend catalog returns exactly 95 signal names, and
the ordering is identical to the frozen manifest, position for position
(verified by list equality, not set equality).

**2 — Code-path identity.** The backend provider's `_load_signal` is identical
to the reference implementation in `diiid_sir_data_provider.py`, and both open
the same `.npz` files. Cleaning is the same: cast to float64, drop non-finite,
stable sort by time, drop non-increasing timestamps.

**3 — Numerical spot checks.** 12 signal × discharge fetches through the live
backend, compared against the reference loader on **length, minimum and
maximum**. All 12 agree **exactly**.

| Discharge | Era | Signals checked |
|---|---|---|
| `195659` | later (≥189646, decimate) | `ip`, `pcdiamag3`, `q95`, `betan`, `prmtan_neped`, `gasa`, `cerqrott3`, `cerqtit13` |
| `155537` | earlier (≤187024, spline) | `ece40`, `cerqtit13`, `prmtan_neped`, `q95` |

The sample deliberately spans **both upstream processing eras** (see U009) and
all eight signal groups, including the ECE group whose units were assigned at
this stage and the two uncalibrated magnetics channels.

Example, `195659 / ip` — backend `length=4205, min=4010.3764468775485,
max=1301667.9171618985`; reference `4205, 4010.376447, 1301667.917`.

## Full-cohort loadability

Independently of the backend, all 95 signals were loaded from all 62 discharges
through the reference provider: **5890/5890 pairs load**, every one with
`finite_fraction = 1.0`. The signal set is identical in all 62 archives.

## Caveat on aggregate statistics

The backend caps its returned `count` at 20000 samples for long signals, so its
`mean` and `std` are computed on a capped subset and are **not** comparable
element-for-element for signals longer than that. `length`, `min` and `max` are
exact, and those are what the comparison used. This is a property of the stats
RPC, not of the loaded data.
