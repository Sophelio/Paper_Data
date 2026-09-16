# S7 workflow

The dependency graph, the chronology, and the difference between them.
Machine-readable: `CANONICAL_INDEX.json`.

---

## 1. Four orderings, not one

They do not coincide, and conflating them is the commonest way to misread this
directory.

| Ordering | What it is | Where to read it |
|---|---|---|
| **scientific dependency** | what each stage needs from upstream | §2, `parent_stages` in each `MANIFEST.json` |
| **branch lineage** | which claim branch and operational epoch each stage belongs to | §2b, `claim_branch` in each `MANIFEST.json` |
| **historical chronology** | the order in which the work actually happened, including failures and corrections | §3 |
| **manuscript presentation** | the order a reader should meet it | §4 |

The dependency graph and the branch lineage are different views of the same
stages: dependency says what a stage *needs*, lineage says which claim it is
*evidence for*. Neither replaces the other.

The most consequential divergence: **S7.10 is a failure**, and in dependency
terms it is a leaf of Epoch 1. In the historical order it is the pivot of the
whole branch, and in the manuscript it is the second thing the reader should
meet.

## 2. Scientific dependency graph

```
                        S7.1  scientific object O
                          │   62 discharges · 95 quantities
                          ▼
                        S7.2  contract skeleton  ──►  S7.2C  contract V2
                          │                              │
                          └──────────────┬───────────────┘
                                         ▼
                        S7.3 ──► S7.3V2   O_q   y* = density · 78 predictors
                                    │
                                    ▼
                                 S7.4V2   X_q   trajectory ensemble
                                    │
                                    ▼
                        S7.5 ──► S7.5H    G_q   70 primitives · C0–C8
                                    │
                                    ▼
                        S7.6 ──► S7.6R    𝔄_q   10,778 admissible atoms
                                    │
                                    ▼
                        S7.7 ──► S7.7R    Σ_q, 𝔄̂_q   162,845 supports explored
                                    │
                                    ▼
                                  S7.8    U_q, V_q made executable
                                    │
                                    ▼
                                  S7.9    (C*,R*)   C_dev_star, frozen
                                    │
                                    ▼
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  S7.10   EXTERNAL QUALIFICATION FAILED  (QREC-B1 negative)        ║
    ║          V3 FAIL · V6 FAIL · Ω*_rec EMPTY · max NRMSE 11.95        ║
    ╚═══════════════════════════════════════════════════════════════════╝
                                    │
                                    ▼
                                 S7.11    the failure is family-wide
                                    │
                                    ▼
                                 S7.R1    δ: state hypothesis REFUTED
                                    │     j_min = NONE_OF_THE_INSTANTIATED_OBJECTS
                                    ▼
                                 S7.K2    ρ: P_rec revised · τ = 1 · 3,451 atoms
                                    │
                                    ▼
                              S7.E2.0     six folds · budget · stop rule
                                    │
                                    ▼
                              S7.E2.0A    boundary reconciled · tau_train retired
                                    │
                                    ▼
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  S7.E2.1  CROSS-FITTED QUALIFICATION PASSED                       ║
    ║           Δ₀ −0.764 · Δ₁ −0.027 · V3 PASS · six distinct supports ║
    ╚═══════════════════════════════════════════════════════════════════╝
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              S7.E2.2  descriptive              S7.12  Q_rec*
              C_E2_ALL_DESC                     branch closed
```

Replay after the K2 revision re-enters at `𝔄_q`: the admissible candidate set
changes, so everything from the universe forward is re-derived. Stages S7.1
through S7.8 are **not** replayed — they were never invalidated.

## 2b. Branch lineage

The same stages, grouped by what they are evidence *for*. `q_rec` is the
scientific **task**; a claim branch fixes `(q, I_q, U_q, V_q, Ω_q)`; an
operational epoch revises `(P_q, B_q, H_q)`.

```
q_rec  (scientific task)
│
├── QREC-B1  sealed-external claim branch
│     ├── operational epoch 1   S7.2 … S7.10   → QUALIFICATION FAILED
│     │      versioned Case-B corrections inside it: S7.2C, S7.7R
│     ├── audit                 S7.11, S7.R1
│     └── operational epoch 2   S7.K2          Case B, branch unchanged
│
└── QREC-B2  cross-fitted finite-object DESCENDANT branch (parent QREC-B1)
      └── operational epoch 1   S7.E2.0 … S7.12   (S7's label: "Epoch 2")
            ├── S7.E2.0   Case C — constitutes the descendant branch
            ├── S7.E2.0A  Case B version inside the pending epoch
            ├── S7.E2.1   FORMAL PASS
            ├── S7.E2.2   descriptive realization
            └── S7.12     Q_rec*, branch CLOSED
```

An operational-contract **version** change is not automatically an
operational-**epoch** advance: the epoch advances only when the superseded
contract had already governed an executed realization. `S7.K2` is the one epoch
advance here; `S7.2C`, `S7.7R` and `S7.E2.0A` are versioned corrections inside
their pending epochs.

The branch changes at **S7.E2.0**, not at S7.K2. K2 revised the operational
admissibility contract and advanced the epoch inside QREC-B1; the branch changed
one stage later, when the evidentiary commitment `V_rec` was materially narrowed
because the Epoch-1 evaluation evidence had been spent. `Ω_rec`, the intended
claim domain, is unchanged throughout. Full classification in
`REVISION_LEDGER.md`.

`vsurf → density` changed neither the task nor the branch: it corrected a target
**instance** under rules the contract already carried.

## 3. Historical chronology

Six corrections happened along the way. All are preserved; none was overwritten.

| when | what | preserved as |
|---|---|---|
| before instantiation | nine contract clauses corrected | `02_.../correction_v1/` alongside V1 |
| before external access | target reselected on source-supported cadence | `03_.../reconciliation_source_resolution/` alongside V1 |
| before external access | `X_rec` re-derived | `04_.../retry_source_resolution_v2/` alongside V1 |
| before external access | ontology hardened; 6,034 → 10,778 atoms | `06_.../hardened_v2/` alongside V1 |
| before external access | search budget unblocked; frontier re-explored | `07_.../one_seed_primary_v2/` alongside V1 |
| **after** external access | operational contract revised (S7.K2), then a descendant claim branch constituted (S7.E2.0) | S7.K2, E2.0, E2.0A, E2.1, E2.2 |

Only the last one happened after protected evidence was spent, and it is the only
one that required an evidentiary reconciliation — which is also the only one that
changed the claim branch. See `REVISION_LEDGER.md`.

**Before S7 began**, an earlier reconstruction branch targeting `I_p` was retired
for target-provenance leakage and for having no skill over a persistence
baseline. S7 was built as the corrective rebuild, and deliberately did not
consult the retired branch's admissible set, supports, comparators, performance
numbers or target — see `_legacy_reference/LEGACY_QREC_STATUS.md`.

## 4. Manuscript presentation order

Not the dependency order. The reader should meet the mechanism, not the audit
tree:

1. the scientific object and the two contracts on it (S7.1–S7.3V2)
2. **the Epoch-1 failure** (S7.9 → S7.10) — this is where the story starts
3. the refutation (S7.11 → S7.R1) — the most load-bearing episode
4. the minimal contract revision (S7.K2)
5. the evidential reconciliation (S7.E2.0A)
6. the qualified result and its two limits (S7.E2.1, S7.12)
7. support non-uniqueness (S7.E2.1 + S7.E2.2)

## 5. Reading the stage table

`CANONICAL_INDEX.json` carries all 21 canonical stages with, for each: SIR
mapping, scientific question, verdict, parents, children, key numbers, and the
governing freeze with its hash. Each stage directory carries the same record as
`MANIFEST.json` and a static `index.html`.

| status | meaning |
|---|---|
| `CANONICAL` | the authoritative version of that stage |
| `CANONICAL_SUPERSEDED_BY_…` | correct at the time, superseded by a named successor, preserved unmodified |
| `CANONICAL_NEGATIVE_RESULT` | a preserved failure; scientific evidence, not a defect |
| `CANONICAL_PRIMARY_RESULT` | the qualification evidence |
| `CANONICAL_DESCRIPTIVE_ONLY` | exposition only; carries no validation weight |
| `CANONICAL_FINAL` | the assembled qualified result |

## 6. What lives outside the stage tree

| path | role |
|---|---|
| `_audit/` | this audit's registry, build scripts, independent recomputations and Phase-A inventory |
| `_legacy_reference/` | the retired `I_p` branch status and the firewall against it |
| `_manifests/INITIAL_STATE_MANIFEST.json` | the state of the tree when S7 began |
| `_logs/` | empty; retained as a declared location |
| `figures/` | generated summary figures with provenance |
| `SIGNAL_UNITS.json` | the units registry; hashed into the S7.1 freeze |
| `STATUS.md` | the living stage index maintained across the work |

## 7. The other branch

`q_desc` — the descriptive contract on the same 62 discharges — is a **different
scientific task**, and therefore a different lineage entirely: not a branch of
`q_rec` and not an operational epoch of it. Different information policy
(target-containing coordinates are admissible), different utility, different
validation structure.

Its canonical artifacts are **not in this directory**. They are at

```
D:\sir-web\Paper Examples\Relational Coordinates for Multimodal Plasma Observations\
    canonical_d3d_62_shot_run_v1\
    Coefficient_conditioning\  (+ Correction_audit\)
    Implicit_elimination_and_denominator_conditioning\
    Conditioning_repair\
```

run id `D3D-SIR-62-ALIGNED-V1`. This audit verified them read-only and did not
modify or relocate them; results are in `AUDIT_REPORT.md` §5. A reader auditing
`q_desc` from this folder alone **cannot** do so — that is a real limitation of
the package and is recorded as such.
