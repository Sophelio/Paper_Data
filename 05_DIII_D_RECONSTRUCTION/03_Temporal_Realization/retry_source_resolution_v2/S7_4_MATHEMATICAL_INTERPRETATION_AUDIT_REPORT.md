# S7.4 retry — Mathematical interpretation: internal audit

**Freeze:** `D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2`
**Status:** `FROZEN_READY_FOR_S7.5` · acceptance **44/44** · 2026-09-03
**Supersedes:** S7.4 V1 (stopped at the temporal gate; preserved unmodified)

---

## 1. Executive verdict

`X_rec` is instantiated: a **finite discharge-indexed ensemble of typed sampled
trajectories** over 62 realizations, with a 78-component typed predictor
trajectory across 7 broad scientific families and 8 mathematical type blocks, and
the line-averaged electron density as target.

The §4 temporal gate that stopped S7.4 V1 now **passes**: `density` is
upstream-upsampled in **0 of 62** discharges, no admitted quantity forces a grid
finer than its resolution estimate, all 62 discharges are validation-feasible,
and `vsurf` remains excluded.

**Zero archives opened.** Every quantity is metadata-derived. No model, no
baseline, no correlation, no coordinate.

Two things are worth flagging up front. First, the grids are **deliberately
discharge-specific** — 53 distinct spacings across 62 discharges — and this is a
property of the object, not a defect to be normalised away. Second, **four of the
eight type blocks are dimensionally heterogeneous**, which S7.5 must respect at
component rather than block level.

## 2. Parent verification — `PARENTS_VERIFIED`, 0 drift

S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1 and S7.3R V2 all verify under the
canonical raw-byte convention with self-referential files excluded.

All ten substantive checks pass: corrected target is `density`; canonical unit
`m^-3`; 78 predictors; 7 broad families; S7.3R supersedes S7.3 V1; `vsurf`
numerically excluded and absent from the primary boundary; external cohort 42
and sealed; S7.4 V1 did **not** instantiate `X_rec` and its
`TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED` status is preserved; S7.3R
is `FROZEN_READY_TO_RETRY_S7.4`.

## 3. Temporal gate — `TEMPORAL_GATE_SATISFIED`

| Check | Result |
|---|---|
| every admitted quantity satisfies the corrected numerical-support rule | **pass**, 0 violations |
| no admitted quantity forces a grid finer than its resolution estimate | **pass** |
| all 62 discharges validation-feasible | **pass** |
| `vsurf` remains excluded | **pass** |
| no external signal value needed | **pass** |

Target `density`: archived cadence 1.0 ms, source-supported estimate 1.0 ms,
**upstream-upsampled in 0/62 discharges** — archived and estimated cadence
coincide, which is precisely what failed for `vsurf`.

## 4. Temporal semantics

**Two parameters, kept apart.** Physical time `t` in seconds is the independent
parameter and the only derivative parameter. Normalized `tau ∈ [0,1]` exists
solely for the frozen block fractions. `d/dtau` is **forbidden** for primary
coordinate construction — durations span 3.780–5.360 s, a factor of 1.42, so a
`tau`-derivative would be rescaled differently per discharge.

**Cadence terminology corrected.** `Δt_src_hat(i,s) = archived_support /
(original_length − 1)` is a **source-supported average cadence estimate**, not an
exact native cadence. Recorded qualifications: support/count based, original
timestamps unavailable, nonuniform original sampling unreconstructable, upstream
generator absent (U001).

The claim made is exactly: *the primary analysis grid is no finer than the
provenance-supported temporal-resolution estimate used by the frozen
numerical-admissibility policy.* The claims **not** made are enumerated in
`temporal_semantics.json`: not "every analysis sample is an observation", not
"every sample is source-supported", not "the grid recovers native sampling".

This is a semantic tightening of the language only. The S7.3R admissibility
computation is unchanged and was not reopened.

**16 vs 22 distinguished.** `n_upsampled_any_discharge = 22` is operative
downstream. The historical 16 used a per-signal **median** ratio, which cannot
detect a signal upsampled in a minority of discharges. Different measurements,
not contradictory figures; 22 supersedes 16 and the relationship is recorded.

## 5–6. `X_rec` and discharge-specific grids

```
X_rec = { (T_s, x_s, y_s, a_s) : s ∈ S_rec },   |S_rec| = 62
```

| | Value |
|---|---|
| `Δt_s` | **5.853 – 14.187 ms**, median 6.824, **53 distinct values** |
| `N_s` | 325 – 833, total 40 572 samples |
| durations | 3.780 – 5.360 s |
| binding signal | `prmtan_teped` (26), `cerqrott3` (25), `cerqrott8` (10), `cerqrott13` (1) |
| development | `Δt` 5.853 – 14.144, `N_s` 326 – 782 |
| external | `Δt` 5.859 – 14.187, `N_s` 325 – 833 |

Neither cohort is systematically coarser. Recorded explicitly:
`global_fixed_dt_required = false`,
`common_coordinate_support_required = true`,
`common_time_grid_across_discharges_required = false`.

The contract stays coherent because validation windows live in `tau`,
coefficients are discharge-specific, comparisons use identical support *within* a
discharge, and gate V7 requires common scored samples per discharge — not
identical timestamps across them.

## 7. Typed predictor blocks — 7 families, 8 blocks

| Block | Dim | Canonical unit | Homogeneous |
|---|---|---|---|
| `X_ECE` | 40 | eV | **yes** |
| `X_CER_v` | 7 | m/s | **yes** |
| `X_CER_Ti` | 7 | eV | **yes** |
| `X_NBI` | 10 | W, N·m | **no** |
| `X_mag` | 4 | T, A, 2× uncalibrated | **no** |
| `X_fs` | 4 | ph/(sr m² s) | **yes** |
| `X_gas` | 4 | V | **yes** |
| `X_density_aux` | 2 | m⁻³, eV | **no** |

Eight blocks over seven families: CER splits because rotation is a velocity and
ion temperature is a temperature.

**Four blocks are dimensionally heterogeneous** — flagged in
`typed_signal_blocks.csv` and in `X_REC.json`. S7.5's dimensional rules must
apply at component level; a sum within `X_NBI` or `X_mag` is not automatically
admissible.

Canonicalization applied: 40 keV→eV, 7 km/s→m/s, 4 cm⁻²→m⁻², 1 kW→W.
`pcbcoil` and `pcdiamag3` keep no unit and stay `UNCALIBRATED_SIGNAL`.

Channel index is **not** asserted spatial for any of the 78 — no geometry is
documented in the frozen object.

## 8. Target space

`Y_rec` = electron number density, **m⁻³** (archived cm⁻³, ×10⁶).
`DIAGNOSTIC_RECONSTRUCTION`, provenance class carried forward unchanged and not
upgraded. No `dy/dt` constructed. Target and target history both excluded from
`X_pred`; persistence remains a baseline defined in `K_rec`.

## 9. Regularity

Three levels separated in `interpretation_constraints.json`: **A** observational
sampled trajectory (what we possess) · **B** numerical realization (a declared
analyst choice) · **C** latent physical trajectory (not assumed recoverable).

No differentiability, `C¹` smoothness, or ODE-solution structure is assumed. A
later derivative coordinate is a constructor acting through a declared numerical
realization — load-bearing for the SIR phase and trajectory-relational
derivatives at S7.5.

## 10. Numerical representation

`X_s^num ∈ ℝ^{N_s×78}`, `y_s^num ∈ ℝ^{N_s}`, marked
`IMPLEMENTATION_REPRESENTATION_ONLY`. ℝ⁷⁸ does not carry the scientific
semantics of `X_pred`. `X_rec` is defined in canonical units, never z-scored;
standardization remains a fitted transform under the leakage firewall.

## 11. Predictor dependency metadata

One exact edge retained: **`pinj = Σ pinj_*`**, `EXACT_DETERMINISTIC_SUM`,
evidence `LOCAL_DOCUMENTED` (units registry description plus the S7.1R
additivity check in canonical units, per-beam W against aggregate kW).

Not target leakage for `density`. It matters because generating both the
aggregate and all eight components as independent primitives risks duplicate
ontology terms, exact redundancy and rank deficiency. **Nothing was removed
here** — S7.5 decides how `G_rec` handles the restatement.

## 12. Aliasing and upsampling

**6 `UPSTREAM_UPSAMPLED`** predictors: `prmtan_neped`, `prmtan_teped`, `fs03da`,
`fs04`, `fs04da`, `fs05da`. Admissible **as levels**; derivative status
`NUMERICAL_SENSITIVITY_ONLY`.

**18 `ALIASING_RISK`** predictors: the 14 CER channels plus `bt`, `ip`,
`prmtan_neped`, `prmtan_teped`.

The flags are **independent** and carried separately; `prmtan_neped` and
`prmtan_teped` carry both. Recorded explicitly:
`coarse_grid_does_not_erase_upstream_aliasing = true`. Aliasing is already
embedded in the archived signal.

## 13. Access audit

**Zero archives opened.** All quantities derived from the S7.1 quality summary,
the S7.3R corrected boundary, and the S7.3R per-discharge grid requirements.
No signal value read — development or external. External cohort sealed.

## 14. Assumptions explicitly not made

differentiability · `C¹` smoothness · ODE-solution structure · Markov property ·
complete physical state · latent-state recovery · dynamical closure · causal
ordering · channel index as spatial coordinate · cross-discharge concatenation ·
iid pooling of discharges.

## 15. Files produced

5 Markdown, 4 CSV, 7 JSON, 1 script — all hashed in `S7_4_FREEZE_V2.json`.

## 16. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\04_mathematical_interpretation\retry_source_resolution_v2\scripts\s7_4_build_x_rec.py
```

Deterministic; no seeds; opens no archive. Exits non-zero on parent drift or if
the temporal gate fails.

## 17. Recommendation for S7.5

**`READY_FOR_S7.5`.**

S7.5 inherits: the typed ensemble with 78 primitives in 8 blocks; per-discharge
grids `T_s`; physical time `t` as the sole derivative parameter with `d/dtau`
forbidden; the sampled-vs-realization-vs-latent distinction, which governs how a
derivative coordinate may be described; four dimensionally heterogeneous blocks
requiring component-level dimensional checks; the `pinj = Σ pinj_*` exact edge;
6 `NUMERICAL_SENSITIVITY_ONLY` and 18 `ALIASING_RISK` qualifications; and an
external cohort still sealed until S7.10.

**S7.5 is not authorised by this document.**
