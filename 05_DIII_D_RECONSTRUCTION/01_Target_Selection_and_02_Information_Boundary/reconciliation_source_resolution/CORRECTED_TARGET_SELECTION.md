# S7.3R — corrected target selection

Machine-readable: `TARGET_SELECTION_RESULT_V2.json`,
`corrected_target_ranking.csv`, `corrected_target_eligibility_matrix.csv`

**The ranking rule, the thresholds, the class policy and the cohort are all
unchanged.** Only the numerical-support instantiation was corrected, and it was
corrected uniformly for every candidate.

---

## Corrected primary target

```
y* = density        (line-averaged electron density)
```

| | |
|---|---|
| **Signal** | `density` |
| **Scientific meaning** | Line-averaged electron density |
| **Archived unit** | cm⁻³ |
| **Canonical unit** | **m⁻³** (×10⁶) |
| **Origin class** | `DIAGNOSTIC_RECONSTRUCTION` |
| **Family** | density |
| **Archived cadence** | 1.0 ms |
| **Source-supported cadence** | 1.0 ms — **never upsampled, in any discharge** |
| **Inventory index** | 21 |
| **Target-side MAJOR flags** | **none** |

## Why it wins — unchanged lexicographic rule

| Level | Key | `density` | Runner-up `fs05da` |
|---|---|---|---|
| 1 | target-side major flags (fewer) | **0** | 0 — tie |
| 2 | certified primary predictors (more) | **78** | 75 → **resolved here** |
| 3 | distinct surviving families (more) | 7 | 6 |
| 4 | RRV margin (larger) | 0.0506 | 0.4094 |
| 5 | inventory index (lower) | 21 | 27 |

**Resolved at Level 2**, on predictor count.

Note what the rule did *not* do, again. `fs05da` has a variation margin eight
times larger (0.409 vs 0.051) and would win any variation-weighted score. It
ranks second because, as a filterscope target, it loses its three siblings —
75 predictors across 6 families against `density`'s 78 across 7. Level 2
outranks Level 4, exactly as in V1. **No weighted score, no manual promotion.**

| Rank | Candidate | Flags | Predictors | Families | RRV_dev | Margin | Index | Resolved |
|---|---|---|---|---|---|---|---|---|
| **1** | **`density`** | 0 | **78** | **7** | 0.1006 | 0.0506 | 21 | — |
| 2 | `fs05da` | 0 | 75 | 6 | 0.4594 | 0.4094 | 27 | L2 |
| 3 | `fs04` | 0 | 75 | 6 | 0.3588 | 0.3088 | 24 | L2 |
| 4 | `fs04da` | 0 | 75 | 6 | 0.3588 | 0.3088 | 26 | L2 |
| 5 | `fs03da` | 0 | 75 | 6 | 0.2645 | 0.2145 | 25 | L2 |
| 6 | `ece7` | 0 | 39 | 6 | 0.2659 | 0.2159 | 48 | L2 |

## Eligibility — 64 candidates → 61 eligible

| Criterion | Failures | Which |
|---|---|---|
| C10 meaningful variation (`RRV_dev` ≥ 0.05) | 2 | `bt` (0.0037), `ip` (0.0042) — unchanged from V1 |
| **C13 target source resolution** *(new instantiation)* | **1** | **`vsurf`** |
| all others | 0 | |

C13 is not a new criterion. It is the frozen `P_rec` numerical-support
admissibility and no-super-resolution rule, instantiated against
source-supported rather than archived cadence.

## Corrected development-only feasibility for `density`

Recomputed on the corrected per-discharge grid, same 20 development discharges,
same frozen formulas.

| | |
|---|---|
| `RRV_dev` (median) | **0.1006** — passes, margin 0.0506 |
| `RRV` range | 0.0299 – 0.2621 |
| Distinct-value fraction (min) | 1.000 |
| Identically-zero discharges | 0 |
| Invalid NRMSE blocks | **0 of 60** |
| Both processing eras | yes |
| Calibration samples (min) | **130** (floor 30) |
| Evaluation samples (min) | **33** (floor 10) |

One honesty note: `density`'s `RRV` falls to 0.0299 in its weakest development
discharge, below the floor. The frozen criterion is on the **median** across
discharges, which is 0.1006, so it passes as specified. The per-discharge spread
is recorded rather than smoothed over.

Its margin is the smallest of the top six. It wins on predictor breadth, not on
variability — which is what the rule was built to do.

---

## Status of the retired V1 selection

```
S7.3 V1 target : vsurf
status         : RETIRED_BY_SOURCE_RESOLUTION_RECONCILIATION
```

**Reason.** Archived cadence had been mistaken for source-supported cadence. The
downstream temporal audit exposed an incompatibility with the already-frozen
no-super-resolution rule.

`vsurf` fails as a target under the corrected rule at discharge `165027`
(external), where its source-supported cadence is **82.909 ms**. The resulting
grid holds 48 samples, giving blocks A(cal=22, eval=5), B(cal=33, eval=5),
C(cal=44, eval=5) — **all three evaluation blocks below the frozen minimum of
10**, and block A's calibration below 30. Recorded reason
`TARGET_SOURCE_RESOLUTION_FAIL`.

**This is not a failed scientific result and not outcome tuning.** No
reconstruction was ever attempted, on `vsurf` or anything else. The V1 selection
was legitimate on the metadata available at S7.3; S7.4 then surfaced a
previously unresolved provenance fact, the study stopped, and the defect was
generalised into the existing rule and re-applied uniformly.

S7.3 V1 and S7.4 V1 are preserved unmodified as audit history.

## What was *not* done

- `vsurf` was not special-cased. The identical rule was applied to all 64
  candidates; it is simply the only one that fails it.
- The cohort was **not** restricted. Discharge `165027` remains in the external
  cohort; the 20/42 partition is untouched.
- The experiment was **not** degraded to 82.9 ms to retain `vsurf`. Under §14 the
  bottleneck signal is removed by rule instead.
- No accept-and-qualify exception was created.
- `density` was **not** manually promoted. It won the unchanged rule.
