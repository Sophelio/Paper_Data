# S7.R1 — Operational-state evidence

The hypothesis was **tested and refuted**. This document records the predictor-side
evidence that refuted it.

Machine-readable: `actuator_block_summary.csv`, `actuator_support_coverage.csv`,
`OPERATIONAL_STATE_RULE.json`, `manifests/gasa_pro_max_sorted.csv`,
`manifests/MULTIVARIATE_FALLBACK_RESULT.json`.

---

## Physical semantics of the gas actuators

| | frozen record |
|---|---|
| `gasa` … `gasd` | Gas injection valve command, manifolds A–D |
| family | `gas_injection` |
| origin class | `CONTROL_COMMAND_OR_ACTUATION` |
| provenance | `certified_independent_of_target` |
| hardening | `IN_P_HARD` (all four) |
| native cadence | 2 ms |

**`gasa` is a gas-puff actuator channel. It is *not* pellet injection.**

**`PELLET_STATUS_UNRESOLVED`** — no pellet-injection signal exists anywhere in
the 95-signal observational object, and no pellet metadata field was found. Gas
puffing and pellet injection are physically different fueling actuators, and the
object cannot distinguish them. Nothing about pellets is inferred.

### Provenance defect found — recorded, not repaired

The unit of `gasa…gasd` is recorded **inconsistently** across the frozen lineage:

| source | unit | dimension | evidence |
|---|---|---|---|
| provider `SIGNAL_MANIFEST` | **`Torr*L/s`** | flow rate | `STRONGLY_INFERRED` |
| S7.1 `units_sources.md` | "gas injection **flow**" | flow rate | — |
| S7.3 boundary / S7.5H basis | **`V`** | `electric_potential` | "valve **command**" |

A valve command voltage and a gas flow rate are physically different quantities.

**No numerical impact.** The `CANON` scale table contains neither `V` nor
`Torr*L/s`, so the applied scale factor is exactly `1.0` under either label and
every archived value used anywhere in Epoch 1 is unchanged. What is affected is
the *dimensional label*: the frozen coordinate `PROD(gasa,gasa)` carries
`output_dimension = (V)*(V)`, which may be wrong. This must be reconciled before
any dimensional claim is made about that coordinate's coefficient. It is logged
as `K-R1-02` and **not** repaired here.

## Audit unit — block-local, not shot-local

The Epoch-1 failure is localized to **block B** of both discharges, so the audit
unit is `discharge × temporal block`, never shot identity. The within-discharge
structure justifies that choice completely:

| shot | block | `gasa` cal max | `gasa` protected max | ratio |
|---|---|---|---|---|
| 187019 | A | 0.0405 | 0.0406 | 1.00 |
| 187019 | **B** | 0.0406 | **1.6306** | **40.18** |
| 187019 | C | 4.4086 | 5.9373 | 1.35 |
| 187022 | A | 0.0396 | 0.0358 | 0.90 |
| 187022 | **B** | 0.0396 | **1.6236** | **41.01** |
| 187022 | C | 4.4065 | 5.9228 | 1.34 |

Gas is essentially off through block A, the puff **begins inside block B's
protected window**, and by block C the gas is fully on — at the discharge's
highest level, 5.94 — with the calibration window having absorbed it. **Block C
carries the most gas and reconstructs normally.**

## Primary one-dimensional audit — `gasa` · **no separation**

Support coverage, block protected-maxima across all 186 blocks:

| cohort | global min | global max | block protected-max median | block protected-max max |
|---|---|---|---|---|
| **development** (20) | −0.0185 | **7.5056** | 1.817 | 7.4472 |
| external (42) | −0.0183 | 7.9821 | 1.636 | 7.9819 |

**Development covers the external range.** The development discharge **195650
reaches `gasa` 7.447 — higher than either catastrophic discharge (5.937,
5.923)**. Development discharge 165028 reaches 4.81.

Top blocks by `gasa` protected maximum are 195649 (external, later), **195650
(development)**, 195645, 195648. `187019/C` and `187022/C` rank only 11th and
12th — and those are the **C** blocks, which did not fail.

The largest gap in the sorted distribution (1.10) falls at rank 182, **interior
to the development set**. There is no natural isolated high-command group.

> **The strong-gas operational condition was well represented during discovery.**

## Single permitted multivariate fallback — **no separation**

Compact actuator vector `[gasa, gasb, gasc, gasd, pinj, tinj]`, block-level
**level** summaries only. Standardization, PCA, one deterministic two-cluster
split on `sign(PC1)`, nearest-neighbour distance to development. No supervised
classifier, no hyperparameter search, no outcome-guided thresholding.

- PCA explained variance: 0.34 / 0.22 / 0.16 / 0.09 — no dominant structure.
- The two-cluster partition places **both** catastrophic blocks in a cluster
  containing **25 development and 50 external** blocks. No separation.
- Nearest-neighbour distance to development: 187019/B at the 98.4th percentile,
  187022/B at the 93.7th — but the **furthest** external blocks are
  `187022/C` (4.54) and `187019/C` (4.51), which reconstruct fine.

**Decisive counterexample:** external discharge **187018** has three blocks at
NN distance 3.07–3.46 — *further* from development than 187022/B (2.64) — and
reconstructs normally (REL NRMSE 0.309). Actuator unusualness does not predict
failure.

## The only quantity that does separate — and why it is not a state

| | development max | external, next-highest | 187019/B | 187022/B |
|---|---|---|---|---|
| `gasa_pro_max / gasa_cal_max` | **1.018** | 1.35 | **40.18** | **41.01** |

This isolates the two catastrophic blocks perfectly. It is nonetheless **not an
operational state**, and may not be promoted to one:

> Its value depends on **where the frozen validation-block boundary falls
> relative to an actuator transition**, not on the operational condition of the
> discharge. The same discharge under a different block split would not be
> flagged. It is a property of the validation geometry, not of the plasma.

Development's maximum ratio is 1.018 — no development block ever has its
protected window exceed its calibration range **at all**. What development lacks
is not a plasma state but a **block alignment**: a puff onset inside the
protected window following a quiet calibration window.

## Gate outcomes

| Gate | Question | Result |
|---|---|---|
| **R1-A** state identification | does admissible predictor information define a simple, physically interpretable operational state? | **FAIL** |
| **R1-B** support coverage | was the strong-actuation state absent or materially unsupported in development? | **FAIL** — it was well represented |
| **R1-C** failure alignment | do the catastrophic blocks align with a frozen state rule? | **NOT_REACHED** — no rule was frozen |

`STATE_IDENTIFICATION_GATE = FAIL`. No `OPERATIONAL_STATE_RULE` was frozen, so
no post-freeze alignment comparison was performed. The Epoch-1 identities were
consulted only *after* the state audit had already concluded negative, and only
to record the 187018 counterexample.
