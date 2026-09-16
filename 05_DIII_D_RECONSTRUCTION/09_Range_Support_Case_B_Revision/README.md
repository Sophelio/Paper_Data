# S7.K2 — Observational range-support contract revision

Freeze **`D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1`**
Status **`FROZEN_READY_FOR_DISCOVERY_EPOCH_2`** · 47/47 acceptance · 7/7 gates
Parent `D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1`

> **Epoch 1 is immutable and unchanged.** `C_dev_star` unchanged · V3 FAIL ·
> V6 FAIL · V9 FAIL · `Omega_rec` EMPTY ·
> `NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`. `K_REC_V1` not overwritten.

---

## The rule

```
L = min(c_cal)     U = max(c_cal)

E = max( L − min(c_app),  0,  max(c_app) − U ) / (U − L)     ≤   τ = 1
```

**Application values may extend no farther beyond the calibration hull than one
full calibration range.**

Dimensionless · unit-scale invariant · sign-symmetric · monotone ·
constructor-generic · no epsilon. Support rule is conservative: **every**
coordinate must pass, score is `max_j E(c_j)`, failing coordinate stays
identifiable. Failure is **local** — `RANGE_SUPPORT_NOT_APPLICABLE` on that
block, never global inadmissibility.

Separate from and additional to `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1`
(unchanged). Confirmed distinct: **zero** non-finite coordinate-cells across all
10 778 × 186, so the denominator condition binds nowhere.

## Contract change — `MINIMAL_P_ONLY`

| Component | Status |
|---|---|
| **`P_rec`** | **REVISED** — gains `P-RANGE-SUPPORT` |
| **`V_rec`** | **CONSEQUENTIAL** — gains `V-RANGE`, a coverage gate; replaces no existing gate |
| `H_rec` | ledger extended |
| `q_rec`, `I_rec`, `B_rec`, `U_rec`, `Omega_rec` | **UNCHANGED** |

`U_rec` was deliberately **not** relaxed to make Epoch 2 easier to pass.
`A_rec` keeps locally unsupported coordinates — **local partial applicability**,
not a global filter.

## Epoch-2 viability

At τ=1, **3 451 / 10 778** atoms (32.0 %) are full-domain, across **all seven**
families (C0 51 · C1 18 · C2 1 488 · C3 382 · C5 8 · C6 965 · C7 539).

**Closure property:** the support predicate is a conjunction over the same
cells, so *any* combination of full-domain coordinates is automatically a
full-domain support → **~10³³** available size-12 supports.

Non-vacuous too: 68 % of atoms lose full-domain support; 1.4 % of cells fail.

## Evidence τ was not outcome-tuned

**τ = 1 is maximally unfavourable to Epoch 1.** 0 of 217 Epoch-1 winners pass;
`C_dev_star` has only 6/12 coordinates supported. Tuning to flatter Epoch 1
would have given τ ≥ 2 (13/217 pass).

Grid `{0, 0.25, 0.5, 1, 2, 5, 10}` hashed `98951146…` **before** any count.
Desiderata hashed `ef505434…` **before** any candidate. Metric chosen on
constructor neutrality (p90 spread ratio **4.3** vs **35.1**). Access log:
`target_reads = 0`, `model_error_reads = 0`, `residual_reads = 0`,
`V3_label_reads = 0`.

## Gas-signal provenance — resolved, and it corrects R1

```
GAS_SIGNAL_UNIT_RESOLVED_COMMAND_VOLTAGE
```

The two records are **not** of equal standing. `S7/SIGNAL_UNITS.json` records the
upstream unit string literally as **`"volt"`** on 51/62 shots (`gasd` 62/62) —
`LOCAL_DOCUMENTED`, the same registry and mechanism that resolved `pcdiamag3` to
`raw`. The provider's `Torr*L/s` is a superseded first-pass hypothesis at **low**
confidence with an **ambiguous** dimensional signature.

The frozen ontology is **correct**; `PROD(gasa,gasa) → (V)*(V)` stands and
**R1's concern is withdrawn**. Zero numerical impact either way. `gasa`…`gasd`
are actuator **command voltages**, not fueling rates. Zero Epoch-1 files edited.

## Retrospective sanity check — after the policy hash

| block | support score | verdict |
|---|---|---|
| 187019/B | **1 641.5** | `NOT_APPLICABLE` |
| 187022/B | **1 705.2** | `NOT_APPLICABLE` |
| 187019/C, 187022/C | 0.81 | PASS |
| ordinary blocks | 0.00–0.27 | PASS |

Three orders of magnitude, with τ=1 cleanly between. **Motivating evidence
only — explicitly not validation.**

## Start here

| Document | Purpose |
|---|---|
| `S7_K2_RANGE_SUPPORT_CONTRACT_FINAL.md` | manuscript-ready section |
| `S7_K2_RANGE_SUPPORT_CONTRACT_AUDIT_REPORT.md` | full internal audit, 28 sections |
| `RANGE_SUPPORT_DEFINITION.md` | concept, desiderata, metric, threshold |
| `GAS_SIGNAL_PROVENANCE_RESOLUTION.md` | the unit supersession |
| `RECOMMENDATION_FOR_EPOCH2.md` | go/no-go and what Epoch 2 must do |

## Reproduce

```bash
python scripts/s7_k2_a_prevalue.py           # lineage, firewall, provenance, concept, desiderata
python scripts/s7_k2_b_stress.py             # 10,778 atoms x 186 cells, target-blind
python scripts/s7_k2_c_threshold.py          # grid frozen first, then metric + sensitivity
python scripts/s7_k2_d_policy_and_freeze.py  # policy, sanity check, K_REC_V2, freeze
```

## Governance

Parent artifacts modified **0** (S7.9 45/45, S7.10 31/31, S7.11 26/26, S7.R1
21/21 reproduce) · Epoch-1 files edited **0** · `K_REC_V1` overwritten **false**
· `C_dev_star` unchanged · `PROD(gasa,gasa)` not removed · no model or baseline
run · no V3 recomputation · no support selected · no `Ahat` extension · two-seed
`NOT_EXECUTED` · `Omega_rec` not outcome-narrowed.

**`PAPER_UTILITY = HIGH`. Discovery Epoch 2 not started. S7.12 remains paused.**
