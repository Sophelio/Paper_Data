# S7.R1 — Operational-state reconciliation audit

Freeze **`D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1`**
Status **`NO_CLEAN_OPERATIONAL_STATE_PARTITION`** → **`STOP_OPERATIONAL_STATE_ROUTE`**
34/34 acceptance · lineage 13/13 · zero drift

> **Epoch 1 is intact and unchanged.** `C_dev_star` unchanged · V3 **FAIL** ·
> V6 **FAIL** · V9 **FAIL** (non-mandatory) · `Omega_rec` **EMPTY** ·
> primary verdict `NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`.

---

## The question, and the answer

**Did qualification expose observational organization that the pooled `X_rec`
failed to represent?**

**No.** The hypothesis was tested against predictor-side evidence and **refuted**.

## Why it was refuted

**The strong-gas condition was already in development.**

| | development (20) | external (42) |
|---|---|---|
| `gasa` range | −0.0185 … **7.5056** | −0.0183 … 7.9821 |

Development discharge **195650 reaches `gasa` 7.447 — higher than either
catastrophic discharge** (187019: 5.937, 187022: 5.923).

**No actuator-space state separates the failures.** The primary 1D audit finds no
isolated high-command group; the largest gap is interior to development. The
single permitted multivariate fallback puts both catastrophic blocks in a cluster
of **25 development + 50 external** blocks. External discharge **187018** lies
*further* from development in actuator space than 187022/B and **reconstructs
normally** (REL NRMSE 0.309).

**The one separating quantity is not a state.**

| | dev max | next external | 187019/B | 187022/B |
|---|---|---|---|---|
| `gasa_pro_max / gasa_cal_max` | 1.018 | 1.35 | **40.18** | **41.01** |

That ratio measures **where the frozen validation boundary falls relative to an
actuator transition**, not the operational condition. Within both failing
discharges: block A gas off → block B **puff onset inside the protected window**
→ block C gas fully on (highest of the discharge, 5.94) and **reconstructs
normally**, because calibration has absorbed it.

## Gates

| Gate | Result |
|---|---|
| **R1-A** state identification | **FAIL** |
| **R1-B** support coverage | **FAIL** — the state *was* represented |
| **R1-C** failure alignment | **NOT_REACHED** — no rule frozen |

## Where the defect actually is

```
earliest_invalidated_stage = NONE_OF_THE_INSTANTIATED_OBJECTS
K_REC_REVISION_REQUIRED    = true
minimal component          = P_rec
```

No instantiated SIR object was invalidated. `A_rec` admitted `PROD(gasa,gasa)`
**by rule** — S7.6R states that C0/C1/C2/C6 have no denominator and no gate. The
gap is in `K_rec`: **mathematical domain support is not observational range
support**. A future epoch should add a range-support admissibility condition for
total nonlinear constructors, declared prospectively. **Not applied here.**

## Provenance defect found

`gasa` unit is `Torr*L/s` in the provider and S7.1, but `V` in S7.3/S7.5H.
**No numerical impact** — the `CANON` scale is exactly 1.0 under either label —
but the frozen `output_dimension = (V)*(V)` on `PROD(gasa,gasa)` may be wrong.
Logged `K-R1-02`; must be resolved before any dimensional claim.

**`PELLET_STATUS_UNRESOLVED`** — no pellet signal or metadata exists in the
95-signal object. `gasa` is a gas-puff valve command and is **not** described as
pellet injection.

## Start here

| Document | Purpose |
|---|---|
| `S7_R1_OPERATIONAL_STATE_RECONCILIATION_FINAL.md` | manuscript-ready section |
| `S7_R1_OPERATIONAL_STATE_RECONCILIATION_AUDIT_REPORT.md` | full internal audit |
| `OPERATIONAL_STATE_EVIDENCE.md` | the predictor-side evidence |
| `SIR_ARROW_RECONCILIATION.md` | arrow-by-arrow, `K_rec` audit |
| `RECOMMENDATION_FOR_R2.md` | recommendation and paper utility |

## Governance

Parent artifacts modified: **0** (S7.9 45/45, S7.10 31/31, S7.11 26/26 reproduce)
· `C_dev_star` unchanged · `PROD(gasa,gasa)` not removed · no model rerun · no V3
recomputation · no search rerun · two-seed `NOT_EXECUTED` · 0 shots removed · 0
blocks removed · no support promoted · target used to define state: **false** ·
error used to define state: **false** · shot-id rule: **false** · `K_rec`
modified: **false**.

Target-blind firewall: **`target_reads = 0`, `model_error_reads = 0`** during
state construction.

## Reproduce

```bash
python scripts/s7_r1_b_actuator_audit.py        # target-blind actuator audit
python scripts/s7_r1_c_fallback.py              # single multivariate fallback
python scripts/s7_r1_d_reconcile_and_freeze.py  # lineage, arrows, K_rec, freeze
```

**`PAPER_UTILITY = MEDIUM`. S7.R2 not authorised. S7.12 remains paused.**
