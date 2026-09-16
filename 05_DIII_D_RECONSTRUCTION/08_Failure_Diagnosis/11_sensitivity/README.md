# S7.11 — Sensitivity and failure interpretation

Freeze **`D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1`**
Status **`FROZEN_WITH_QUALIFICATIONS`** · 39/39 acceptance
Parent `D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1`

> **The primary external result is immutable and unchanged:**
> `NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER` · V3 **FAIL** · V6 **FAIL** ·
> `Omega_rec` **EMPTY** · `C_dev_star` **unchanged**.

S7.11 does not ask whether the frozen model qualified. It asks **what kind of
negative result** that was.

---

## Verdict

```
S7_11_DEVELOPMENT_EQUIVALENCE_DOES_NOT_IDENTIFY_EXTERNAL_ROBUSTNESS
  __CANONICAL_REPRESENTATIVE_EXTERNALLY_FRAGILE
  __PRIMARY_FAILURE_UNCHANGED
```

## The three answers

**1. The family is heterogeneous — but uniformly marginal.**
Of the 217 predeclared development-bootstrap winners, 213 are full-domain and
**70 (32.9 %) satisfy the V3-style criterion**. So the failure is *not* a
property of the whole development-equivalent family. But no member anywhere
beats persistence by more than **0.0287** NRMSE, the passers clear the frozen
0.01 floor by at most 0.0187, and the family median `Δ₁` is **−0.0004** —
parity. The family straddles the trivial baseline; it does not beat it.

**2. The canonical representative was externally fragile — and development
selection did not know it.**

| | |
|---|---|
| `C_dev_star` external mean NRMSE percentile | **86.4** (rank 184/213) |
| `C_dev_star` external median NRMSE percentile | 56.8 |
| `C_dev_star` development bootstrap frequency | **0.093 — the family maximum** |
| Spearman(development freq, external mean NRMSE) | **−0.093** |

The support the development bootstrap favoured most strongly is among the worst
seventh of its own family externally, and across the family the correlation is
indistinguishable from zero.

**3. V9 = FAIL** (non-mandatory). Discharge component clean (0/42 flips,
independently verified). **Temporal-block component dependent**: omitting block
B alone flips the V3-style verdict, by 0.0014. Numerical-realization component
`NOT_INSTANTIATED` — untested, not passed.

## What separates passing from failing supports

Not typical accuracy — **the tail**.

| | passers (70) | failures (143) |
|---|---|---|
| any discharge with NRMSE > 1 | **0** | **93** |
| median of worst-discharge NRMSE | 0.536 | 7.543 |

186 of 213 supports beat the persistence *median*; only 107 beat its *mean*.

In the coordinate-participation table required across pass/fail groups,
`PROD(gasa,gasa)` is the top failure association: **0 of 70 passers, 67 of 143
failures**. It shifts the median by 0.005 and the mean by a factor of 3.6. This
fell out of the general table — **no removal test was run, and it remains in
`C_dev_star`.**

## `prmtan_neped` — neither ablation passes

| | `C_dev_star` | minus-prmtan (7) | prmtan-only (1) |
|---|---|---|---|
| mean | 0.7424 | 0.8351 | 0.4632 |
| median | 0.1699 | 0.1764 | **0.4660** |
| `Δ₁` | +0.5321 | +0.6248 | +0.2529 |
| V3-style | FAIL | FAIL | FAIL |

Removing the same-family density ancestry makes the result **worse** — the tail
survives it. The pedestal diagnostic alone has a better mean only because a
single level coordinate cannot extrapolate, and a **2.7× worse median**. The
relational construction genuinely adds typical-case accuracy; neither object
approaches nontrivial skill.

## Start here

| Document | Purpose |
|---|---|
| `S7_11_SENSITIVITY_AND_INTERPRETATION_FINAL.md` | manuscript-ready section |
| `S7_11_SENSITIVITY_AUDIT_REPORT.md` | full internal audit, 23 sections |
| `SUPPORT_FAMILY_SENSITIVITY.md` | all 217 supports, distributions, participation |
| `PRMTAN_NEPED_SENSITIVITY.md` | the two predeclared ablations |
| `V9_SENSITIVITY_RESULT.md` | V9 resolution and final gate table |

## Predeclaration discipline

```
predeclaration sha256   da24fbe38141f0c7…
declared                2026-09-05T22:47:11.395345Z
first external access   2026-09-05T22:48:51.998142Z
lead time               100.6 s
```

Only the three predeclared analyses were run, plus V9's own three components,
whose definition was frozen in S7.2 V1. **No post-hoc `PROD(gasa,gasa)` removal
test and no joint two-discharge removal diagnostic were run** — neither is
predeclared.

## Governance

`S7_10_ARTIFACTS_REWRITTEN = 0` · S7.7/S7.8/S7.9/S7.10 reopened: **false** ·
`C_dev_star_CHANGED = false` · `EXTERNAL_MODEL_RESELECTED = false` ·
`DISCHARGES_DELETED = 0` · `ERA_DROPPED = false` · `METRIC_CHANGED = false` ·
`THRESHOLD_CHANGED = false` · `SEARCH_RERUN = false` ·
`TWO_SEED_EXECUTED = false` · `S7_11_PREDECLARATION_CHANGED = false` ·
`GASA_PRODUCT_REMOVED = false` · `RANGE_GATE_ADDED = false` ·
`CLIPPING_OR_WINSORIZATION = false`

## Future-contract lesson (not a repair)

`OBSERVATIONAL_RANGE_SUPPORT_ADMISSIBILITY` —
`PROSPECTIVE_CONTRACT_RECOMMENDATION`. Mathematical domain support is not
observational range support. `x²` is defined for every finite `x`, yet a
calibration-supported relation involving `x²` becomes numerically unsupported
when `x` leaves the calibration region. The frozen guard covers denominators;
C0/C1/C2/C6 have no gate by design. **Not operationalized here, not added
retrospectively to `P_rec`.**

## Files

**CSV** — `support_family_external_metrics`, `support_family_v3_results`,
`support_family_applicability`, `support_family_coordinate_summary`,
`support_family_distributions`, `prmtan_sensitivity_metrics`,
`block_omission_sensitivity`, `discharge_sensitivity_summary`

**JSON** — `S7_11_PREDECLARATION_VERIFICATION`, `S7_11_SUPPORT_FAMILY_V3_SUMMARY`,
`V9_RESULT`, `S7_11_GATE_RESULTS`, `S7_11_QUALIFICATIONS`, `S7_11_VERDICT`,
`S7_11_ACCEPTANCE_CHECKS`, `S7_11_FREEZE`

**Manifests** — `FAMILY_RUN`, `S7_11_RUN_MANIFEST`

## Reproduce

```bash
python scripts/s7_11_a_verify.py   # lineage, predeclaration, immutability
python scripts/s7_11_b_family.py   # 217 supports + 2 prmtan + block omission
python scripts/s7_11_c_v9.py       # V9 resolution
python scripts/s7_11_d_freeze.py   # summaries, acceptance, freeze
```

**Next stage: S7.12 — qualified result assembly. NOT AUTHORISED.**
