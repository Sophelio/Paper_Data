# Selected reconstruction target

Machine-readable: `TARGET_SELECTION_RESULT.json`

```
y* = vsurf
```

| | |
|---|---|
| **Signal** | `vsurf` |
| **Scientific meaning** | Surface loop voltage |
| **Archived unit** | V |
| **Canonical unit** | V (already canonical; no conversion) |
| **Origin class** | `DIRECT_MEASUREMENT` |
| **Origin evidence class** | `STRONGLY_INFERRED` |
| **Family** | magnetics |
| **Native cadence** | 20.0 ms |
| **Frozen inventory index** | 5 |
| **Target-side MAJOR flags** | **none** |

## How it won

Selected automatically by the frozen S7.2C deterministic lexicographic rule. No
human preference, no model, no baseline, no correlation.

| Level | Key | `vsurf` | Runner-up `density` |
|---|---|---|---|
| 1 | target-side major flags (fewer) | **0** | 0 — tie |
| 2 | certified primary predictors (more) | **79** | 79 — tie |
| 3 | distinct surviving families (more) | **7** | 7 — tie |
| 4 | RRV margin (larger) | **0.1297** | 0.0483 → **resolved here** |
| 5 | inventory index (lower) | 5 | not reached |

**Resolved at Level 4.** `vsurf` and `density` were identical through the first
three levels; the target-variation margin separated them.

Of 62 eligible candidates, 46 tied at Level 1 with zero flags. Level 2 cut that
to `vsurf` and `density` (79 predictors each), the filterscopes falling to 76
and the ECE channels to 40.

## Target-side qualifications

**None of the five S7.1 MAJOR issues attaches specifically to `vsurf`.** It
carries neither U009 (era-varying resampling method) nor U010 (downsampled
without anti-aliasing) nor U003 (EFIT). The two global object limitations —
U001 (upstream generator absent) and U004 (no uncertainty metadata) — attach to
every quantity in the object equally and do not discriminate.

One property is recorded for downstream stages and is **not** a MAJOR flag:
S7.1 found `vsurf` among the 16 quantities that were **upstream-upsampled**.
Its boundary row carries `resolution_flag = UPSTREAM_UPSAMPLED`. This bears on
derivative construction at S7.5 under the frozen numerical-resolution policy; it
did not enter selection, because inventing a new flag class after seeing
candidates is forbidden.

## Development-only feasibility

Computed on the 20 development discharges, on the candidate's own 20.0 ms
primary grid. **No model, no baseline, no predictor-target statistic.**

| Criterion | Threshold | Result |
|---|---|---|
| Robust relative variation `RRV_dev` | ≥ 0.05 | **0.1797** — passes with margin 0.1297 |
| `RRV` range across 20 discharges | — | 0.1057 – 0.3610 (every discharge clears the floor) |
| Distinct-value fraction | ≥ 0.10 | **1.000** (minimum across discharges) |
| Identically-zero discharges | = 0 | **0** |
| Invalid NRMSE blocks | = 0 | **0 of 60** (20 discharges × 3 blocks) |
| Both processing eras | required | **earlier and later both present** |

Calibration blocks hold 75–140+ samples and evaluation blocks 19–23 samples at
the 20 ms cadence, comfortably above the frozen minima of 30 and 10.

## Why this is a defensible choice — and what it is not

It won because its scientific identity is clean (a directly measured,
well-understood electromagnetic quantity in volts), its provenance carries no
signal-specific major defect, 79 provenance-certified predictors across 7
scientific families survive the boundary, and it varies enough on development
discharges to make a trivial baseline a real test.

**Nothing here says it will reconstruct well.** No reconstruction of any kind has
been attempted. If SIR fails on `vsurf` under the frozen contract, that is the
scientific result.

## Sanity audit

`TARGET_SELECTION_CONFIRMED`. Identity, description, unit, origin class,
provenance and target-side flags were checked; no new documentation or
provenance defect was found. Reconstructability, predictor correlation,
reconstructions and baselines were **not** inspected.
