# S7.E2.1 — Cross-fitted relational discovery and qualification

Freeze **`D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1`**
Status **`QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS`** · 38/38 acceptance
Protocol `E2_0A_PROTOCOL` · Contract `K_REC_V2`

```
FORMAL_PASS          — the frozen scientific gates pass
CLEAN_DEMO_NOT_MET   — the prospective reporting tier is not reached
```

---

## The result

| | |
|---|---|
| `Δ₀` vs calibration mean | **−0.764489** |
| `Δ₁` vs persistence | **−0.027308** |
| **V3** (needs both ≤ −0.01) | **PASS** |
| **V6** | **PASS_WITH_QUALIFICATION** |
| **V-RANGE** | **PASS** — 2 232 checks, **0 failures** |
| discharges with NRMSE > 1 | **0** |

## 62 out-of-fold discharges

| method | mean | median | paired mean `Δ` | W/T/L |
|---|---|---|---|---|
| **REL** | **0.1891** | **0.1515** | — | — |
| B0 calibration mean | 0.9536 | 0.9365 | −0.7645 | 62/0/0 |
| **B1 persistence** | 0.2164 | 0.1744 | **−0.0273** | **32/5/25** |
| B1A AR(1) | 0.3563 | 0.3329 | −0.1671 | 55/2/5 |
| B2 raw ridge (78) | 0.2851 | 0.1972 | −0.0960 | 39/7/16 |
| B3 raw HistGB (78) | 0.3464 | 0.1960 | −0.1573 | 37/4/21 |
| H0 hardened ridge (70) | 0.2842 | 0.1914 | −0.0951 | 37/7/18 |

REL p90 0.2959 · **max 0.9199**.

## The contract hardening worked

| | Epoch 1 | **Epoch 2** |
|---|---|---|
| mean | 0.7424 | **0.1891** |
| **max** | **11.95** | **0.92** |
| discharges > 1.0 | 2 | **0** |
| 187019 | 11.95 | **0.297** |
| 187022 | 11.77 | **0.436** |

The catastrophic extrapolation tail is **gone**. The two discharges that
destroyed Epoch 1 now reconstruct unremarkably. This is the clearest evidence
that the failure → refuted-state-hypothesis → `P_rec` → range-support chain
identified the right defect.

## Two limits that travel with the claim

**1. The margin over persistence is modest and era-asymmetric.**

| era | n | `Δ₁` | direction |
|---|---|---|---|
| earlier | 35 | **+0.0076** | `PRACTICAL_TIE` |
| later | 27 | **−0.0726** | `MATERIAL_IMPROVEMENT` |

The pooled pass is carried by the later era. Discharge-level record against
persistence: **32–5–25**.

Against every **raw-coordinate** comparator the margin is wide (−0.096 vs ridge,
−0.157 vs gradient boosting, −0.095 vs hardened ablation). Persistence is simply
a demanding baseline for a slowly varying target.

**2. Predictor-side applicability used the whole object.** Under E2.0A this
tests whether the *target relationship* transfers — not whether the predictor
geometry would survive discharges never observed.

## Why `CLEAN_DEMO_PASS` was not met

`Δ₁ ≤ −0.05` (achieved −0.0273) ✗ · both eras material improvement ✗ ·
the other three criteria ✓. **The threshold was frozen before the run and was not
adjusted.** A formal pass that misses the reporting tier remains a formal pass.

## Support non-uniqueness

Six folds → **six different supports**, all size 12, **none identical**, mean
pairwise Jaccard **0.285**, 35 distinct coordinates. Only `ID(pcdiamag3)` and
`RATIO(ece21,cerqtit10)` appear in all six.

**Stable utility, non-unique supports** — the Epoch-1 lesson, reproduced under a
different contract. Not a canonical DIII-D density equation.

## Execution integrity

Six folds, **one frozen policy, one non-interactive run**. 765 758 proposals of a
1 800 000 budget; ≤ 127 764 per fold against a 300 000 cap. Basis verified at
3 451 with exact constructor counts and matching hash **before any target opened**.
Support hashed **before** held-out target access in all six folds, gated by a
vault that raises `FIREWALL` on premature reads. Protected targets opened last.

## Start here

| Document | Purpose |
|---|---|
| `E2_1_MANUSCRIPT_RESULT.md` | manuscript-ready section |
| `E2_1_FINAL_RESULT.md` | the numbers in full |
| `E2_1_AUDIT_REPORT.md` | internal audit, 18 sections |
| `E2_1_CLAIM_BOUNDARY.md` | what may and may not be written |
| `E2_1_SUPPORT_STABILITY.md` | six supports, descriptive |

## Stop rule

`EPOCH2_IS_FINAL_QREC_ATTEMPT = true` — respected. Epoch 2 passed, so no further
epoch arises. Nothing tuned, no threshold moved, no discharge or block removed, no
support repaired, no two-seed rescue, no budget extension. **The optional all-data
descriptive representation was NOT run** and awaits separate authorisation.

## Reproduce

```bash
python scripts/e2_1_a_verify.py     # lineage, basis, global predictor access
python scripts/e2_1_b_run.py        # six folds, one policy, non-interactive
python scripts/e2_1_c_aggregate.py  # cross-fitted aggregation, gates, freeze
```

**S7.12 remains paused. No further q_rec discovery epoch is authorised.**
