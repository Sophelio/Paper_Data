# S7.3R — Source-supported temporal admissibility: internal audit

**Freeze:** `D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-SOURCE-RESOLUTION-V2`
**Status:** `FROZEN_READY_TO_RETRY_S7.4` · acceptance **31/31** · 2026-09-02

---

## 1. Executive verdict

One instantiation error was corrected uniformly: S7.3 used **archived** cadence
where the frozen no-super-resolution policy requires **source-supported**
cadence. No rule, threshold, class policy or cohort was changed.

The correction propagates cleanly. Across all 64 candidate boundaries there are
**63 numerical-support removals, and every one is `vsurf`** — it is the only
quantity in the object whose source-supported cadence forces an infeasible grid.
`vsurf` also fails as a target under the same rule.

The corrected primary target is **`density`**, selected at Level 2 of the
unchanged lexicographic rule. **78** admissible primitives across **7** families,
on a corrected per-discharge cadence of **5.85 – 14.19 ms** — *finer* than V1's
flat 20 ms, and now source-supported at every sample.

**Zero external signal values accessed.** No model, no baseline, no correlation,
no coordinate. S7.3 V1 and S7.4 V1 preserved unmodified.

## 2. Parent verification — `PARENTS_VERIFIED`, 0 drift

S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1 all verify. Substantive checks pass:
external cohort still 42 and sealed; development 20; `y*_V1 == vsurf`; S7.4 did
**not** instantiate `X_rec`; S7.4 status is
`TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED`; no model exists.

## 3. Source-supported cadence audit — all 95 signals, all 62 discharges

`source_supported_signal_cadence.csv` (5890 rows),
`source_supported_signal_summary.csv` (95 rows).

```
average_source_supported_dt = archived_support / (original_length - 1)
```

Recorded evidence class `STRONGLY_INFERRED` with an explicit qualification: this
is a **support-based average**, not an exact native sampling interval — original
timestamps are unavailable and the upstream generator is absent (U001). It is a
**lower bound on coarseness**; the true source can only be coarser.

The audit was run on all 95 signals, not just `vsurf`.

### 22 signals are upstream-upsampled in at least one discharge

| Group | n | Source Δt range | Archived Δt | Shots upsampled |
|---|---|---|---|---|
| 15 equilibrium + `vsurf` | 16 | 19.93 – **82.91** ms | 20.0 | 36 each |
| `prmtan_neped`, `prmtan_teped` | 2 | 4.38 – **14.19** ms | 10.0 | 3 each |
| 4 filterscopes | 4 | 0.02 – **0.05** ms | 0.02 | 9 each |

The remaining **73 signals** are never upsampled; their source-supported cadence
never exceeds their archived cadence, and their maximum is 10.0 ms.

## 4. Correction to the historical upsample count — **16 → 22**

Recomputed directly from primary metadata rather than assumed.

The historical figure of 16 used a per-signal **median** length ratio > 1.01,
which cannot see a signal upsampled in only a minority of discharges. The
correct criterion here is "upsampled in **any** discharge", which yields **22**.

The six newly identified: `prmtan_neped`, `prmtan_teped` (3 discharges each) and
`fs03da`, `fs04`, `fs04da`, `fs05da` (9 discharges each).

The earlier count is **corrected, not forced to agree**
(`manifests/UPSAMPLE_COUNT_CORRECTION.json`).

This matters: every source-upsampled explanatory primitive now passes the same
numerical-support logic applied to `vsurf`. Two of the six — the pedestal fits —
turn out to be the binding signals for the corrected grid.

## 5. The numerical-admissibility rule applied

Not a new rule. The frozen `P_rec` class D (numerical support) plus the
no-super-resolution policy plus the frozen validation minima, instantiated
against source-supported cadence.

For each candidate `y` and each discharge `s`:

```
dt_required(y,s) = max over admitted quantities q of source_supported_dt(q,s)
n(s)             = floor(window(y,s) / dt_required(y,s)) + 1
feasible(s)      = every block has cal >= 30 and eval >= 10
```

A predictor is removed as `PRIMARY_NUMERICAL_SUPPORT_FAIL` iff retaining it
makes the frozen validation geometry infeasible on at least one required
discharge. Removal is iterative and deterministic: the coarsest predictor on the
worst infeasible discharge goes first, and the loop stops when feasible or when
the target itself is binding.

A target fails `TARGET_SOURCE_RESOLUTION_FAIL` iff its own source-supported
cadence makes the geometry infeasible.

Applied identically to all 64 candidates. **`vsurf` was not special-cased.**

## 6. `vsurf` — status

**Fails as a target.** At discharge `165027` (external) its source-supported
cadence is 82.909 ms, giving 48 grid samples and blocks A(cal=22, eval=5),
B(cal=33, eval=5), C(cal=44, eval=5). All three evaluation blocks fall below the
minimum of 10; block A calibration falls below 30. → `C13` fail.

**Removed as a predictor** from all 63 other candidate boundaries, same
mechanism (50 samples, evals of 4).

**Retired, not deleted.** V1 status recorded as
`RETIRED_BY_SOURCE_RESOLUTION_RECONCILIATION`. No reconstruction was ever
attempted; the V1 selection was legitimate on the metadata then available.

## 7. Cohort and rule integrity

- **Cohort unchanged.** Discharge `165027` stays in the external cohort. The
  20/42 partition is untouched. No vsurf-compatible subset was constructed.
- **No global 82.9 ms degradation.** Under §14 the bottleneck signal is removed
  by rule rather than coarsening every other measurement to accommodate it.
- **No accept-and-qualify exception.** The S7.4 option of accepting interpolated
  target samples was rejected, as instructed.
- **No `PROVENANCE_RELAXED` branch, no EFIT recovery campaign.**
- **Thresholds unchanged:** RRV floor 0.05, distinct 0.10, min predictors 10,
  cal ≥ 30, eval ≥ 10, block fractions 0.4/0.6/0.8 → 0.1.

## 8. Development feasibility recomputed

Recomputed for **all 64 candidates** on their corrected grids — simpler and more
deterministic than deciding case-by-case which grids moved. Same 20 development
discharges, same frozen formulas, no external access.

Eligibility: **61 of 64**. Failures: `C10` ×2 (`bt` 0.0037, `ip` 0.0042 —
unchanged from V1) and `C13` ×1 (`vsurf`).

## 9. Corrected ranking — rule unchanged

| Rank | Candidate | Flags | Predictors | Families | RRV margin | Index | Resolved |
|---|---|---|---|---|---|---|---|
| **1** | **`density`** | 0 | **78** | **7** | 0.0506 | 21 | — |
| 2 | `fs05da` | 0 | 75 | 6 | 0.4094 | 27 | **L2** |
| 3–5 | `fs04`, `fs04da`, `fs03da` | 0 | 75 | 6 | 0.31–0.21 | — | L2 |
| 6+ | 40 ECE channels | 0 | 39 | 6 | — | — | L2 |

Resolved at **Level 2**. `fs05da` again has the far larger variation margin and
again loses on predictor breadth — the same behaviour as V1, from the same
unchanged rule.

## 10. Corrected boundary and cadence

```
95  ->  1 target + 15 unresolved-ancestry + 1 numerical-support  ->  78 primitives
```

7 families. Corrected cadence **discharge-specific, 5.853 – 14.187 ms**, median
6.824; binding signals `prmtan_teped` (26 discharges), `cerqrott3` (25),
`cerqrott8` (10), `cerqrott13` (1).

**All 62 discharges feasible**, minimum 325 grid samples against a requirement of
100. For `density` on development: 60/60 blocks valid, calibration ≥ 130,
evaluation ≥ 33.

The corrected grid is *finer* than V1's 20 ms, because removing the 20 ms-class
bottleneck lets the remaining admitted quantities support 6–14 ms — and every
sample on it is now source-supported.

## 11. Temporal handoff to S7.4

Per-signal in `corrected_selected_target_boundary.csv`: source-supported cadence
range, archived cadence, upsample count, source temporal status,
numerical-support status, aliasing flag, derivative qualification.

Among the 78 survivors: **6** carry `UPSTREAM_UPSAMPLED` (the two pedestal fits
and the four filterscopes) and are `NUMERICAL_SENSITIVITY_ONLY` for derivatives;
**18** carry `ALIASING_RISK`. All are admissible **as levels**, because the
corrected grid respects their source support — which is the outcome §7 required:
admissibility decided by the existing grid and validation rules, not by a new
categorical ban on interpolated signals.

`X_rec` was **not** instantiated.

## 12. Notation clarification

Recorded in `TARGET_SELECTION_RESULT_V2.json` for downstream inheritance:

```
|NRMSE_A - NRMSE_B| <= max(SE_delta, 0.01)
```

Practical equivalence is in **calibration-normalized** units, not raw
physical-unit RMSE. Historical S7.2 V2 artifacts are **not** rewritten. No model
was evaluated here.

## 13. What this episode demonstrates

The original target-selection procedure was not performance-biased. It selected
`vsurf` legitimately under the metadata available at S7.3. S7.4 then exposed a
previously unresolved provenance fact, the experiment **stopped**, the defect was
generalised into an existing rule, and the rule was re-applied uniformly to every
candidate.

The target changed. Nothing about the standard of evidence did. This is
qualification working as designed.

## 14. Files produced

5 Markdown, 9 CSV, 7 JSON, 1 script — all hashed in `S7_3_FREEZE_V2.json`.

## 15. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\03_target_feasibility_and_boundary\reconciliation_source_resolution\scripts\s7_3r_reconcile.py
```

Deterministic; no seeds. Exits non-zero on parent drift or on any external read.

## 16. Recommendation

**`READY_TO_RETRY_S7.4`.**

S7.4 inherits: `y* = density`; 78 primitives across 7 families; a
**discharge-specific** cadence of 5.85–14.19 ms, source-supported everywhere;
6 predictors `NUMERICAL_SENSITIVITY_ONLY` and 18 `ALIASING_RISK` for S7.5's
derivative rules; and an external cohort still sealed.

The S7.4 §4 gate should now pass: the target `density` is never upsampled in any
discharge, so archived and source-supported cadence coincide for it, and the
analysis grid is no finer than source support for every admitted quantity.

**S7.4 is not re-entered by this document.**
