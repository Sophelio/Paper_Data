# S7.11 — V9 sensitivity result

```
V9 = FAIL          (non-mandatory)
```

V9 is the one gate S7.10 left open. It resolves here, under the parent
four-state vocabulary, and it changes nothing mandatory.

Machine-readable: `V9_RESULT.json`, `discharge_sensitivity_summary.csv`,
`block_omission_sensitivity.csv`.

---

## The inherited rule and the auditable criterion

> *no result depends catastrophically on one discharge, one temporal block, or
> one numerical realization* — S7.2 V1, carried into `V_REC_OPERATIONAL_V1`.

All three components were frozen long before any external value existed. No new
scalar "catastrophic" threshold was invented. The auditable criterion is the
direct one: **does removing ONE unit change the frozen V3-style verdict?**

## Component 1 — discharge · clean

Independently recomputed from the frozen S7.10 discharge metrics, reproducing
the recorded result exactly.

| | |
|---|---|
| LODO cohorts satisfying V3 | **0 / 42** |
| S7.10 recorded | 0 — **independently verified** |
| full-cohort `Δ₀` / `Δ₁` | −0.1801 / +0.5321 |
| `Δ₁` range across the 42 cohorts | +0.2579 … +0.5514 |
| `Δ₀` range | −0.4475 … −0.1505 |
| most influential | **187019** (earlier) |
| second most influential | **187022** (earlier) |
| verdict flips | **0** |

**Finding: `NO_SINGLE_DISCHARGE_VERDICT_DEPENDENCE`.**

The two catastrophic discharges are individually insufficient to determine the
verdict precisely because there are two of them: removing either still leaves
`Δ₁ = +0.258` at best, far from the −0.01 threshold. This must not be read as
evidence that the two-discharge tail is unimportant — only that no *single*
discharge decides the outcome.

## Component 2 — temporal block · **dependent**

Three omissions, exactly as the frozen definition contemplates. No new temporal
windows were created. `C_dev_star`, the estimator and the B0/B1 definitions are
all fixed.

| Omitted | Blocks used | `Δ₀` | `Δ₁` | V3-style |
|---|---|---|---|---|
| A | B + C | +0.1444 | +0.8080 | FAIL |
| **B** | **A + C** | **−0.7299** | **−0.0114** | **PASS** |
| C | A + B | +0.0451 | +0.7997 | FAIL |

**Finding: `DIRECT_TEMPORAL_BLOCK_DEPENDENCE`.**

Omitting block B alone flips the V3-style verdict from FAIL to PASS. Block B is
where the protected-window product excursion occurs on both catastrophic
discharges.

Two qualifications on that flip:

- **The margin is narrow.** `Δ₁ = −0.0114` against a threshold of −0.01 — it
  clears by 0.0014 NRMSE.
- **It is not a claim.** The primary V3 remains the three-block frozen result.
  No block may be omitted from `Omega_rec` after seeing this, and none was.

## Component 3 — numerical realization · not instantiated

```
NUMERICAL_REALIZATION_SENSITIVITY_NOT_INSTANTIATED
```

Every coordinate of `C_dev_star` carries `numerical_realization_id = NONE`, and
the support contains only C0 level, C2 product, C3 ratio and C5 reciprocal
constructors — **no derivative coordinate**. The frozen derivative realization
`FD2_PHYSICAL_TIME_V1` therefore never enters this support, and the study never
prospectively froze an alternative realization of level, product, ratio or
reciprocal coordinates.

No alternative realization was invented after seeing the external outcomes — no
smoothing, no alternative interpolation, no different derivative estimation, no
clipping, no log transform, no rescaling, no alternative product definition.

**Robustness may not be inferred from the absence of a test.** This component
is untested, not passed.

## Resolution

**`V9 = FAIL`**, non-mandatory.

The discharge component is clean. The temporal-block component is not: one
block omission changes the verdict, which under the auditable criterion is
direct dependence on one temporal block. The numerical-realization component
was never instantiated, so it supports no robustness claim either.

V9 is non-mandatory precisely because an influential unit is *a finding to
report rather than a disqualification, provided it is reported*. It is reported.

## What V9 does not change

`V3` FAIL · `V6` FAIL · `PRIMARY_EXTERNAL_RESULT`
`NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER` · `Omega_rec` EMPTY ·
`C_dev_star` unchanged.

## Final gate table

| Gate | Mandatory | Result |
|---|---|---|
| V1 information boundary | yes | PASS |
| V2 development-only discovery | yes | PASS |
| **V3 nontrivial skill** | yes | **FAIL** |
| V4 fair raw comparison | yes | PASS |
| V5 external structural transfer | yes | PASS |
| **V6 processing-era robustness** | yes | **FAIL** |
| V7 common support | yes | PASS |
| V8 discharge-level inference | yes | PASS |
| **V9 sensitivity** | **no** | **FAIL** |
| V10 numerical provenance | yes | PASS |

Two mandatory failures, unchanged from S7.10. V9 now closed.
