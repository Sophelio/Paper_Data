# S7.K2 — Observational range-support contract revision: internal audit report

Stage **S7.K2** · Freeze `D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1`
Parent `D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1`

---

## 1. Executive verdict

**`FROZEN_READY_FOR_DISCOVERY_EPOCH_2`** · 47/47 acceptance · all seven go/no-go
gates pass · revision class **`MINIMAL_P_ONLY`**.

A constructor-generic, dimensionless, target-blind observational range-support
predicate was defined, stress-tested over the entire frozen atomic universe,
thresholded from a pre-hashed grid, and frozen into `K_REC_V2` — with `P_rec` the
only normatively revised component, exactly as R1 predicted and here **verified
rather than assumed**.

The gas-signal unit defect is **resolved**, and the resolution **corrects R1**:
the two records were never of equal standing.

## 2. Parent verification

Fourteen authoritative freezes through S7.R1. **S7.9 45/45, S7.10 31/31, S7.11
26/26, S7.R1 21/21 artifacts reproduce byte-for-byte.** Zero substantive drift.

## 3. Epoch-1 / R1 immutability

Pinned before any analysis: `C_dev_star` (size 12), primary verdict
`NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`, the V1–V10 table with V3/V6/V9
FAIL, R1's `STOP_OPERATIONAL_STATE_ROUTE`, `earliest_invalidated_stage =
NONE_OF_THE_INSTANTIATED_OBJECTS`, two-seed `NOT_EXECUTED`, and the absence of
S7.R2 and S7.12. `PARENT_ARTIFACTS_MODIFIED = 0`.

## 4. K2 firewall

Hashed `3d75739ce167b91a` before any metric was computed. Stress-test access log
records `target_reads = 0`, `model_error_reads = 0`, `residual_reads = 0`,
`V3_label_reads = 0`, `support_family_outcome_label_reads = 0`, asserted in code.

Permitted and used: predictor values, coordinate values, frozen coordinate
definitions, frozen block geometry, and the coordinate *identities* of the 217
fixed supports. Historical motivation is recorded as motivation, never as
validation.

## 5. Gas-signal provenance resolution

**`GAS_SIGNAL_UNIT_RESOLVED_COMMAND_VOLTAGE`.**

`S7/SIGNAL_UNITS.json` records `gasa` as `{"units": "V", "upstream_variants":
{"volt": 51, "": 11}, "description": "Gas injection valve command, manifold A"}`;
`gasd` is `{"volt": 62}`. Evidence class `LOCAL_DOCUMENTED (units registry)`,
units source `smallELM_freq_v6_ZL_data/{shot}_metadata.json`, audited over all 62
shots. The eleven non-reporting shots return an empty string, never a conflicting
unit.

The competing `Torr*L/s` entry is a **first-pass external-convention hypothesis**
recorded at `confidence = low`, `dimensional_signature = ambiguous`,
`magnitude_test = NOT_TESTED`, with the explicit note that "external convention
identifies the quantity but the stored scale/units are ambiguous and no local
artifact resolves them."

**This corrects R1's `K-R1-02`**, which treated the two as an unreconciled
inconsistency between equals. They are a supersession, already resolved inside
S7.1's own final pass — by the same registry and mechanism that resolved
`pcdiamag3` to `raw`/uncalibrated, a resolution the whole downstream lineage
(including S7.9 and S7.10) relied on. The frozen ontology is correct; the
provider manifest is stale; `PROD(gasa,gasa) → (V)*(V)` stands.

Numerical impact: none either way — `CANON` contains neither label. `epoch1_files_edited = 0`.

## 6. Conceptual definition

Written and hashed (`f8b5abec1958610c`) **before** any numerical realization.
Range support is a property of the triple (coordinate, calibration interval,
application interval). Three admissibility notions are kept explicitly distinct:
symbolic, mathematical-domain, and observational-range.

Empirical confirmation that the last is not a restatement of the second:
**zero** non-finite coordinate-cells across 10 778 × 186 = 2 004 708 — the
denominator condition binds nowhere in the atomic universe.

## 7. Frozen numerical desiderata

Fourteen criteria hashed `ef5054345f1a2cbc` **before** any candidate was
computed, with the permitted and forbidden selection bases recorded explicitly.

## 8–10. Candidate metrics

Two evaluated; a third was **not needed**.

| | definition | degenerate cells |
|---|---|---|
| **R1** | hull excess / calibration **range** | 263 / 2 004 708 |
| **R2** | hull excess / calibration **RMS** | 263 / 2 004 708 |
| R3 robust (IQR/MAD) | **not evaluated** | — |

R3 was not needed because neither R1 nor R2 is ill-defined over any meaningful
part of the universe — 0.013 % degenerate.

## 11. Atomic-universe stress test

All **10 778** frozen admissible atoms × **186** blocks, target-blind, 14 s
runtime. 2 004 445 cells scored, 263 degenerate, 0 non-finite.

| candidate | p50 | p90 | p99 | max |
|---|---|---|---|---|
| R1 | 0.0 | 0.0945 | 1.3006 | 7.4e13 |
| R2 | 0.0 | 0.3642 | 8.3230 | 8.8e14 |

## 12. Constructor-stratified behaviour — the decisive comparison

| | p90 spread across 7 families | ratio | p99 ratio |
|---|---|---|---|
| **R1** | 0.032 … 0.139 | **4.3** | 4.8 |
| R2 | 0.029 … 1.029 | **35.1** | 13.5 |

R2 systematically inflates rate-bearing families (C1, C6, C7) because dividing
by calibration RMS penalises coordinates whose calibration mean sits near zero —
a property of the constructor, not of range support.

## 13. Threshold sensitivity

Grid `{0, 0.25, 0.5, 1, 2, 5, 10}` hashed `98951146f6ff13a5` **before any count
was inspected**.

| τ | cell rate | full-domain atoms | fraction |
|---|---|---|---|
| 0 | 0.802 | 9 | 0.001 |
| 0.25 | 0.946 | 1 026 | 0.095 |
| 0.5 | 0.971 | 2 099 | 0.195 |
| **1** | **0.986** | **3 451** | **0.320** |
| 2 | 0.994 | 5 957 | 0.553 |
| 5 | 0.998 | 8 722 | 0.809 |
| 10 | 0.999 | 9 559 | 0.887 |

Smooth and monotone; no cliff. Every constructor family has nonzero full-domain
membership at every τ ≥ 0.25.

## 14–15. Metric and threshold selection

**Metric: R1**, on desiderata D6 (constructor-generic) and D10 (auditable). Both
candidates satisfy every other criterion; they separate on constructor
neutrality by a factor of eight.

**Threshold: τ = 1.** `τ = 0` is destructive (9 atoms). Larger values permit more
extrapolation with weaker interpretation. `τ = 1` is the unique grid value with a
one-sentence reading, sits inside a broad monotone stability region, and
preserves all seven families. One significant figure.

Against §16: (A) broad stability ✔ (B) non-vacuous — 68 % of atoms fail ✔
(C) non-destructive — 3 451 atoms, ~10³³ supports ✔ (D) coherent across families
✔ (E) degeneracy 0.013 %, explicit ✔ (F) explainable in one sentence ✔.

## 16–17. Support semantics and local applicability

Support predicate is the **conjunction** over coordinates; no averaging, no
cancellation; score `max_j E(c_j)`; failing coordinate identifiable. Failure is
**local** — `RANGE_SUPPORT_NOT_APPLICABLE` on that block, never global
inadmissibility. `PROD(x,x)` stays in `G_rec` and `A_rec`.

## 18. Global-vs-local `A_rec` decision

**Resolved to `B_LOCAL_PARTIAL_APPLICABILITY`**, not a global filter.

Consistent with existing SIR partial-map semantics, which already keep
denominator-bearing coordinates in the ontology and localize failure. It is also
the sharper representation, because of a closure property: since the support
predicate is a conjunction over the *same* cells, **any combination of
full-domain coordinates is automatically a full-domain support**. A search
restricted to full-domain coordinates therefore yields full-domain supports by
construction, with nothing erased from `A_rec`.

## 19. Full-domain coverage policy

**`FULL_DOMAIN_RANGE_SUPPORT`** required for any primary claim. Abstention cannot
manufacture success: locally inapplicable supports are reported, blocks are never
deleted, scores are never silently computed on fewer blocks. Partial-domain
supports may be inspected diagnostically but cannot become the primary result.

Feasible target-blindly: 3 451 full-domain atoms, all families, ~10³³ size-12
supports.

## 20. `K_rec` component audit

| | |
|---|---|
| `q_rec` | UNCHANGED |
| `I_rec` | UNCHANGED |
| **`P_rec`** | **REVISED** — `P-RANGE-SUPPORT` |
| `B_rec` | UNCHANGED |
| `H_rec` | policy unchanged, ledger extended |
| `U_rec` | UNCHANGED — deliberately not relaxed |
| **`V_rec`** | **CONSEQUENTIAL** — `V-RANGE` |
| `Omega_rec` | UNCHANGED, not outcome-narrowed |

R1's `MINIMAL_P_ONLY` prediction **verified**, not assumed. No additional
normative component required.

## 21–22. The clauses

`P-RANGE-SUPPORT` and `V-RANGE` are given verbatim in `K_REC_V2.json`. `V-RANGE`
is an applicability/coverage gate only: it replaces no existing gate, introduces
no performance threshold, and leaves V1–V10 semantics untouched.

## 23. Knowledge ledger

Ten entries in three separated classes — inherited historical (2), predictor-only
K2 findings (5), normative contract decisions (3) — each recording evidence
class, source, `target_used`, `model_error_used`, normative-or-empirical, and
affected component.

## 24. Post-freeze historical sanity check

Run **after** `RANGE_SUPPORT_POLICY_V1.json` was written and hashed
(recorded in `S7_K2_FREEZE.json` as `policy_sha256`). Nothing was changed afterwards.

| block | support score | verdict |
|---|---|---|
| 187019/B | **1 641.5** (`PROD(gasa,gasa)`) | `NOT_APPLICABLE` |
| 187022/B | **1 705.2** (`PROD(gasa,gasa)`) | `NOT_APPLICABLE` |
| 187019/C | 0.814 | PASS |
| 187022/C | 0.807 | PASS |
| 187019/A, 187022/A | 0.266, 0.019 | PASS |
| 195650/B, 165028/B, 189652/A, 195274/C | 0.000–0.211 | PASS |

Three orders of magnitude of separation, with τ = 1 cleanly between, and the
normally-reconstructing C blocks of the same discharges passing.

**Labelled `RETROSPECTIVE_SANITY_CHECK`, explicitly not validation.** It is
motivating evidence. It cannot establish that `K_REC_V2` improves reconstruction.

## 25. Search-space consequence audit

3 451 / 10 778 full-domain (32.0 %); locally partial 7 327; degenerate cells 263;
cell applicability 0.986. By constructor: C0 51 · C1 18 · C2 1 488 · C3 382 ·
C5 8 · C6 965 · C7 539 — **all families survive**. ~10³³ size-12 full-domain
supports available.

0 of 217 Epoch-1 supports pass at τ ≤ 1; `C_dev_star` has 6/12 coordinates
supported; the 217 have a median of 50 % of their coordinates supported. This is
expected — that frontier was searched under a utility with no range-support
pressure — and is **not** evidence of over-restriction. It does mean **Epoch 2
must search afresh**.

It is simultaneously the strongest available evidence that τ was not
outcome-tuned: the chosen threshold is maximally unfavourable to every Epoch-1
object, where τ ≥ 2 would have been flattering.

## 26. Paper-utility assessment

**`HIGH`.** One equation, one sentence, one threshold with a plain reading. No
constructor exceptions, no arbitrary constants, no special cases, no physics
digression. The eight-step narrative — discovery, qualification failure,
localization, a proposed explanation, its refutation on evidence, reconciliation
to `P_rec`, minimal hardening, resumption — is complete and each step is short.

## 27. Files

6 Markdown (limit 20) · 4 CSV · 7 JSON · 9 manifests · 4 scripts.

## 28. Recommendation

**`READY_FOR_DISCOVERY_EPOCH_2`** under `K_REC_V2`.

Epoch 2 must search afresh, restrict candidates to full-domain coordinates over
the intended domain, carry `U_rec` unchanged, and — the single largest open
question, belonging to the Epoch-2 protocol stage and not to K2 — **decide how to
partition a cohort whose former external set is no longer sealed.**

Discovery Epoch 2 not started. S7.12 remains paused.
