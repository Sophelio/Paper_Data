# S7.2 — Reconstruction contract `K_rec^pre`

**Freeze:** `D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V1`
**Status:** `FROZEN_READY_FOR_S7.3` · acceptance **31/31**
**Parent:** `D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1` (9/9 hashes verified)

> **No reconstruction target has been selected.** This stage freezes the
> target-blind contract skeleton that will govern target selection, boundary
> construction, ontology generation, search, validation and qualification.

## Start here

| File | What it is |
|---|---|
| `S7_2_RECONSTRUCTION_CONTRACT_FINAL.md` | manuscript-ready prose |
| `S7_2_RECONSTRUCTION_CONTRACT_AUDIT_REPORT.md` | the full internal audit |
| `K_REC_PRE.md` / `.json` | the contract, human- and machine-readable |
| `CONTRACT_DECISION_LEDGER.md` | 20 decisions, each with what was *not* consulted |
| `CLAIM_BOUNDARY.md` | one-screen claim card |
| `S7_2_FREEZE.json` | freeze record and all artifact hashes |

## The contract

```
K_rec = (q, I, P, B, H, U, V, Omega)
```

| | Status |
|---|---|
| **q** task class | **FROZEN** — continuous reconstruction, structural transfer with local calibration |
| **I** information boundary | **PARTIAL** — rules frozen, instantiation deferred to S7.3 |
| **P** admissibility | **PARTIAL** — 8 invariant classes frozen |
| **B** search bounds | **PARTIAL** — depth 1, support 1–12 |
| **H** knowledge | **FROZEN** — including the seeding firewall |
| **U** utility | **FROZEN** — lexicographic, equivalence rule declared |
| **V** validation | **PARTIAL** — geometry, 4 baselines, 10 gates frozen |
| **Ω** domain | **PARTIAL** — 62-discharge candidate; 20/42 partition frozen |

## Cohorts

**Development 20** · **External 42** · deterministic, target-blind, no seed.
External sealed until S7.10 (`EXTERNAL_COHORT_FIREWALL.md`).

## Validation geometry

Three rolling-origin blocks per discharge — calibration `[0,0.4)`/`[0,0.6)`/
`[0,0.8)`, protected `[0.4,0.5)`/`[0.6,0.7)`/`[0.8,0.9)`. Feasible at every
native cadence (186/186); worst case 20 ms gives ≥18 protected, ≥75 calibration
samples.

## Layout

```
02_reconstruction_contract/
  README.md                              INHERITED_S7_1_CONSTRAINTS.md
  RECONSTRUCTION_TASK_DEFINITION.md      RELATION_AND_TRANSFER_POLICY.md
  TARGET_ELIGIBILITY_POLICY.md           target_eligibility_schema.json
  INFORMATION_BOUNDARY_POLICY.md         leakage_matrix.csv
  ADMISSIBILITY_POLICY.md                UNIT_AND_TYPE_POLICY.md
  NUMERICAL_RESOLUTION_POLICY.md         KNOWLEDGE_POLICY.md
  SEARCH_BOUND_POLICY.md                 UTILITY_AND_QUALIFICATION_POLICY.md
  VALIDATION_PROTOCOL.md                 validation_windows.json
  PREPROCESSING_AND_LEAKAGE_POLICY.md    BASELINE_PROTOCOL.md
  STATISTICAL_INFERENCE_PLAN.md
  COHORT_PARTITION_POLICY.md             COHORT_PARTITION.json
  EXTERNAL_COHORT_FIREWALL.md
  CLAIM_BOUNDARY.md                      DOMAIN_AND_CLAIM_BOUNDARY.md
  CONTRACT_DECISION_LEDGER.md
  K_REC_PRE.json                         K_REC_PRE.md
  S7_2_ACCEPTANCE_CHECKS.json            S7_2_FREEZE.json
  S7_2_RECONSTRUCTION_CONTRACT_FINAL.md
  S7_2_RECONSTRUCTION_CONTRACT_AUDIT_REPORT.md
  scripts/    verify_s7_1_input.py
              build_partition_and_validation.py
              build_contract_and_freeze.py
  manifests/  S7_1_INPUT_VERIFICATION.json
              COHORT_PARTITION_FREEZE.json
              validation_feasibility_audit.csv
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\02_reconstruction_contract\scripts"

& $P $S\verify_s7_1_input.py              # STOPs on drift
& $P $S\build_partition_and_validation.py
& $P $S\build_contract_and_freeze.py
```

Deterministic; no seeds. `verify_s7_1_input.py` exits non-zero if the parent
freeze fails verification.

## Stage gate

No target selected · no targets ranked · no coordinates · no `G_rec` · no
`A_rec` · no `Ahat_rec` · no SIR run · no regression · no performance inspected ·
**no external signal value inspected** · S7.3 not started.
