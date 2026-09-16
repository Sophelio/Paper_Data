# S7.10 — External validation and gate evaluation

Freeze **`D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1`**
Parent `D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1`

| | |
|---|---|
| **Stage execution** | `EXECUTED_AS_FROZEN` · 57/57 acceptance · artifacts `COMPLETE_AND_VERIFIED` |
| **Primary scientific result** | **`NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`** |
| **Stage status** | **`PRIMARY_EXTERNAL_GATE_FAILURE`** |

The two verdicts are reported separately on purpose. The stage ran correctly.
The science failed.

---

## The result

```
Delta_0 = mean(NRMSE_REL − NRMSE_B0) = −0.180095    meets  ≤ −0.01
Delta_1 = mean(NRMSE_REL − NRMSE_B1) = +0.532091    FAILS  ≤ −0.01
V3 requires BOTH  →  FAIL
```

**Persistence beats the frozen relational representation on the external
cohort.** This is the same failure that retired the previous `q_rec` attempt —
discovered then after the fact, and here by a gate frozen before the target
existed.

Mandatory gates failed: **V3**, **V6**. Seven mandatory gates pass; V9 is
pending S7.11.

## What the numbers actually look like

| Method | mean | median |
|---|---|---|
| **REL** | **0.7424** | **0.1699** |
| B0 calibration mean | 0.9225 | 0.9100 |
| **B1 persistence** | 0.2103 | 0.1765 |
| B1A AR(1) | 0.3504 | 0.3329 |
| B2 raw ridge (78) | 0.2804 | 0.1893 |
| B3 HistGB (78) | 0.3060 | 0.1806 |
| H0 hardened ridge (70) | 0.2828 | 0.1846 |

The median external NRMSE, **0.1699**, is essentially the development FIT of
0.1664 — **40 of 42 discharges transfer at development level**. Two earlier-era
discharges reach NRMSE ≈ 11.9 and drag the mean to 0.74.

**The frozen gate uses the mean. The median was not substituted for it.** The
failure is robust: **0 of 42** leave-one-discharge-out cohorts satisfy V3.

## Why

`PROD(gasa,gasa)` — the gas-injection valve command, squared.

On discharge 187019 block B, `gasa` spans 5.3 × 10⁻³ … 4.1 × 10⁻² across
calibration and reaches **1.63** inside the protected window. Squared, that puts
the coordinate ~**8 979 calibration standard deviations** out, and the affine
relation extrapolates linearly into failure. The next-largest excursion anywhere
in the cohort is 13 σ. Log–log correlation between protected excursion and
discharge error: **0.930**.

The frozen `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1` rule could not catch it: it
guards **denominators**, and the S7.6R policy states that C0, C1, C2 and C6 have
no denominator and no gate. All 378 denominator checks passed. A squared
actuator command is unguarded by construction.

**Recorded, not repaired.** No coordinate removed, no range rule added, no
discharge deleted, no threshold moved.

## Firewall and ordering

```
PRE_EXTERNAL_MODEL_FREEZE    2026-09-05T20:32:08.992754+00:00   13/13 hashes verified
S7.11 predeclaration hashed  da24fbe38141f0c7…                  before external access
inference policy hashed      812920c4edecd844…                  before external access
FIRST_EXTERNAL_VALUE_ACCESS  2026-09-05T22:48:51.998142+00:00
```

All 42 discharges, all 126 blocks evaluated. Zero blocks `NOT_APPLICABLE`. Every
method scored on identical protected rows.

## Nothing was repaired after the result appeared

`C_dev_star` unchanged · `FIT_best` not substituted · no bootstrap winner swapped
in · no coordinate added or removed · `B2 α` unchanged · `H0 α` unchanged · `B3`
untuned · metric unchanged · threshold unchanged · bootstrap count unchanged · no
discharge deleted · no era dropped · no search rerun · two-seed not run · no
S7.11 sensitivity executed.

## Start here

| Document | Purpose |
|---|---|
| `S7_10_EXTERNAL_VALIDATION_FINAL.md` | manuscript-ready section |
| `S7_10_EXTERNAL_VALIDATION_AUDIT_REPORT.md` | full internal audit, 31 sections |
| `QUALIFICATION_GATE_RESULTS.md` | V1–V10, rules, evidence, consequences |
| `EXTERNAL_BASELINE_COMPARISON.md` | all seven methods, paired stats, LODO |
| `EXTERNAL_DOMAIN_AND_ERA_RESULTS.md` | 24/18 eras, domain audit, `Omega_rec` |

## Files

**Results (CSV)** — `external_block_metrics`, `external_discharge_metrics`,
`external_paired_differences`, `external_bootstrap_intervals`,
`external_win_tie_loss`, `external_lodo_results`, `external_era_results`,
`external_denominator_audit`, `common_support_audit`,
`external_extrapolation_audit`

**Frozen objects** — `EXTERNAL_INFERENCE_POLICY_PREVALUE.json`,
`S7_11_SENSITIVITY_PREDECLARATION.json`, `V_REC_EXTERNAL_RESULTS.json`,
`OMEGA_REC_EXTERNAL.json`, `S7_10_ACCEPTANCE_CHECKS.json`, `S7_10_FREEZE.json`

**Manifests** — preflight, first external access, external access log,
statistical-inference parent audit, external failure-mode diagnostic

## Reproduce

```bash
python scripts/s7_10_a_preflight.py           # gates; opens no external value
python scripts/s7_10_b_external_eval.py       # FIRST EXTERNAL ACCESS; evaluation
python scripts/s7_10_c_inference.py           # paired stats, bootstrap, gates
python scripts/s7_10_d_failure_diagnostic.py  # failure mode (reporting only)
python scripts/s7_10_e_freeze.py              # Omega_rec, acceptance, freeze
```

Python 3.13.5 · numpy 2.5.2 · pandas 3.0.5 · scikit-learn 1.9.0.

## Claim boundary

`Omega_rec` supported claim domain: **EMPTY**. No structural-transfer claim, no
accuracy claim, no unique-support claim, no global-optimality claim. The later
era meets the V3 thresholds on its own; that is **evidence, not a claim**, and
the domain was not narrowed to it.

**Next stage: S7.11 — predeclared sensitivities. NOT AUTHORISED.**
