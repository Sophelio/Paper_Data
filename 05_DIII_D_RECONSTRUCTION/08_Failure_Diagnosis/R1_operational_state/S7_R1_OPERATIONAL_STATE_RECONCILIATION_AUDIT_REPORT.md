# S7.R1 — Operational-state reconciliation: internal audit report

Stage **S7.R1** · Freeze `D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1`
Parent `D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1`

---

## 1. Executive verdict

**`NO_CLEAN_OPERATIONAL_STATE_PARTITION`** → **`STOP_OPERATIONAL_STATE_ROUTE`**
· 34/34 acceptance · zero drift.

The motivating hypothesis — that `X_rec⁽¹⁾` pooled at least two physically
meaningful operational states — was **tested and refuted**. Gates R1-A and R1-B
both fail; R1-C was never reached because no state rule was frozen.

The audit nonetheless localizes the Epoch-1 defect precisely, and to a different
object than expected: **no instantiated SIR object was invalidated; `K_rec` is
incomplete**. Minimal component: `P_rec`.

A separate provenance defect was found in the frozen lineage (`gasa` unit
recorded as both `Torr*L/s` and `V`) with **no numerical consequence**.

## 2. Parent verification

Thirteen authoritative freezes through S7.11. **S7.9 45/45, S7.10 31/31, S7.11
26/26 artifacts reproduce byte-for-byte.** Confirmed: target `density`,
development 20, external 42, `C_dev_star` unchanged (size 12), S7.10 verdict
`NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`, V3/V6/V9 all FAIL, two-seed
`NOT_EXECUTED`, no S7.12 directory. Zero substantive drift.

## 3. Epoch-1 immutability

`PRIMARY_EPOCH1_RESULT_IMMUTABLE = true` and `DISCOVERY_EPOCH_1_INTACT = true`
written before any state analysis, pinning `C_dev_star`, the full V1–V10 table,
the S7.10 primary verdict, the S7.11 sensitivity verdict, Epoch-1 `Omega_rec` and
all thirteen parent hashes. `PARENT_ARTIFACTS_MODIFIED = 0`.

## 4. Physical semantics of gas actuation

`gasa`…`gasd`: **gas injection valve command, manifolds A–D**; family
`gas_injection`; origin class `CONTROL_COMMAND_OR_ACTUATION`; provenance
`certified_independent_of_target`; all four `IN_P_HARD`; native cadence 2 ms.

**Provenance defect (`K-R1-02`).** The unit is recorded inconsistently:

| source | unit | reading |
|---|---|---|
| provider `SIGNAL_MANIFEST` | `Torr*L/s` (`STRONGLY_INFERRED`) | flow rate |
| S7.1 `units_sources.md` | "gas injection **flow**" | flow rate |
| S7.3 / S7.5H | `V`, `electric_potential`, "valve **command**" | command voltage |

**No numerical impact:** `CANON` contains neither label, so the scale factor is
exactly 1.0 either way and every archived value is unchanged. The frozen
`output_dimension = (V)*(V)` on `PROD(gasa,gasa)` may nonetheless be wrong and
must be reconciled before any dimensional claim. Recorded, **not repaired**.

## 5. Pellet / gas-puff distinction

**`PELLET_STATUS_UNRESOLVED`.** No pellet-injection signal exists anywhere in
the 95-signal object and no pellet metadata field was found. `gasa` is a gas-puff
valve command and is **not** described as pellet injection. Nothing inferred.

## 6. Audit unit

`discharge × temporal block`, never shot identity — the frozen failure is
localized to block B. The within-discharge structure fully vindicates that
choice: gas off in block A, puff onset inside block B's protected window, gas
fully on in block C (the discharge's highest level, 5.94) with **normal
reconstruction**.

## 7. Target-blind firewall

`target_reads = 0`, `model_error_reads = 0` during state construction; no NRMSE,
residual, failure flag or support-family label was opened. Verdict
`TARGET_BLIND`, logged in `manifests/ACTUATOR_AUDIT_ACCESS_LOG.json` and asserted
in code. Epoch-1 identities were consulted **only after** the state audit had
concluded negative, and only to record the 187018 counterexample.

## 8. Actuator variable inventory

Primary `gasa`, `gasb`, `gasc`, `gasd`; corroborating `pinj`, `tinj`. No
equilibrium output, no target, no reconstruction coordinate, no error diagnostic
entered the state-definition space.

## 9. Block-level actuator summaries

186 blocks (62 × 3): calibration and protected min/max/median, absolute maxima,
the descriptive ratio `protected_max / calibration_max` (undefined rather than
epsilon where the denominator vanishes), and the standardized protected
excursion.

## 10. Development support coverage

| cohort | `gasa` global min | global max | block protected-max max |
|---|---|---|---|
| development | −0.0185 | **7.5056** | 7.4472 |
| external | −0.0183 | 7.9821 | 7.9819 |

Development **covers** the external range. Development discharge **195650
reaches 7.447**, above both catastrophic discharges (5.937, 5.923); 165028
reaches 4.81.

## 11. Primary one-dimensional `gasa` audit

No natural isolated high-command group. The largest sorted gap (1.10, rank 182)
is **interior to development**. Top blocks are 195649 (ext), **195650 (dev)**,
195645, 195648; `187019/C` and `187022/C` rank only 11th–12th, and those are the
**C** blocks, which did not fail. **No separation.**

## 12. Fallback multivariate audit

The single permitted fallback. `[gasa, gasb, gasc, gasd, pinj, tinj]` block-level
**level** summaries; standardization; PCA (variance 0.34/0.22/0.16/0.09 — no
dominant structure); one deterministic two-cluster split on `sign(PC1)`;
nearest-neighbour distance to development. No supervised classifier, no
hyperparameter search, no feature selection, no outcome-guided thresholding.

Both catastrophic blocks land in a cluster of **25 development + 50 external**
blocks. NN percentiles 98.4 and 93.7 — but the furthest external blocks are
`187022/C` (4.54) and `187019/C` (4.51), which reconstruct fine, and **187018**
(three blocks at 3.07–3.46, further than 187022/B at 2.64) reconstructs normally
at REL NRMSE 0.309. **No separation.**

## 13. State-rule freeze

**`STATE_RULE_FROZEN = false`**, `STATE_IDENTIFICATION_GATE = FAIL`. No rule was
written, so nothing was hashed and no post-freeze alignment was performed.

The only separating quantity is `gasa_pro_max / gasa_cal_max` — 40.18 and 41.01
against a development maximum of 1.018 and an external runner-up of 1.35. It was
**not** promoted to a state label, because its value depends on where the frozen
validation boundary falls relative to an actuator transition rather than on the
operational condition. The same discharge under a different block split would not
be flagged.

## 14. Post-freeze alignment

Not applicable — no rule existed to align. The 187018 counterexample is the only
Epoch-1 identity consulted, after the negative conclusion was already reached.

## 15–17. Gates

| Gate | Result | Basis |
|---|---|---|
| **R1-A** | **FAIL** | no simple, physically interpretable, predictor-defined state separates the catastrophic blocks in either the primary or fallback audit |
| **R1-B** | **FAIL** | the strong-gas condition **was** materially represented in development; a development discharge exceeds both failing discharges |
| **R1-C** | **NOT_REACHED** | no state rule was frozen |

## 18. SIR arrow reconciliation

```
earliest_invalidated_stage = NONE_OF_THE_INSTANTIATED_OBJECTS
```

`O → O_q` VALID · `O_q → X_rec` **VALID, NOT INVALIDATED** · `X_rec → G_rec`
VALID · `G_rec → A_rec` VALID under contract as written · `A_rec → Ahat_rec`
VALID · `Ahat_rec → (C*,R*)` VALID · `(C*,R*) → Q_rec` VALID AND INFORMATIVE.

`A_rec` admitted `PROD(gasa,gasa)` **by rule**: S7.6R states that C0/C1/C2/C6
have no denominator and no gate. No object was mis-constructed.

## 19. `K_rec` change audit

```
K_REC_REVISION_REQUIRED = true
revision_class          = MINIMAL_K_REC_REVISION_REQUIRED
minimal component       = P_rec
```

`P_rec` lacks an observational range-support admissibility condition for total
nonlinear constructors (products, powers), analogous to the existing denominator
guard. `V_rec` would carry only the consequential per-block applicability
outcome; no independent `V_rec` defect was found — all ten gates behaved exactly
as frozen. `I_rec`, `B_rec`, `H_rec`, `U_rec`, `Omega_rec`, `q_rec` unchanged.
`I_rec` already admits the actuator variables, which is why the state hypothesis
was testable at all.

**No `K_rec` component was modified in this stage.** The revision belongs to a
future epoch, declared prospectively.

## 20. Revised `X_rec` proposal

**None.** A state-indexed `X_rec⁽²⁾` is **not supported**: the record genuinely
is one operational ensemble with respect to gas actuation. Proposing one would
encode a distinction the evidence refutes.

## 21. Knowledge ledger

Ten entries (`K-R1-01`…`K-R1-10`) in `RECONCILIATION_KNOWLEDGE_LEDGER.json`, each
with statement, stage, evidence class, source, fields used,
`target_used = false`, `model_error_used = false`, confidence, implication, and
whether it changes an instantiated object or `K_rec`. Evidence classes are kept
separate: `FROZEN_SIGNAL_PROVENANCE`, `PREDICTOR_VALUE_EVIDENCE`, `INFERENCE`. No
`SHOT_DOCUMENTARY_CORROBORATION` entries exist — no local or accessible
documentary record for 187019/187022 was found, and none was invented.

## 22. Paper-utility assessment

**`PAPER_UTILITY = MEDIUM`.** Clean, short, manuscript-explainable, no
plasma-physics digression: four command channels, one coverage comparison, one
counterexample. It does not deliver the "revise then requalify" arc, because the
premise was refuted. It delivers instead a demonstration of SIR **rejecting an
attractive post-hoc explanation on evidence**, which is a stronger methodological
claim than confirming one. Not LOW — nothing here is arbitrary, threshold-tuned
or hand-selected.

## 23. Files

5 Markdown (limit 20) · 4 CSV · 6 JSON · 4 manifests · 3 scripts.

## 24. Recommendation

**`STOP_OPERATIONAL_STATE_ROUTE`.** S7.R2 is **not authorised** — there is no
defensible state to condition on. The reconciliation target is a minimal `P_rec`
revision for a future epoch, declared prospectively and never retrofitted.

The existing Epoch-1 result, the S7.11 sensitivity analysis and this refutation
together already constitute a complete and publishable SIR demonstration.
Extending the DIII-D example further risks converting a methods demonstration
into a plasma-physics campaign.

S7.R2 not started. S7.12 remains paused.
