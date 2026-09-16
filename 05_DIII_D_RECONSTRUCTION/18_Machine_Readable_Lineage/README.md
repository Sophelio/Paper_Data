# S7 — DIII-D task-conditioned relational discovery

Supplementary Note S7 of the SIR manuscript. This directory holds the complete,
independently auditable **`q_rec` reconstruction lineage** on 62 DIII-D
discharges.

**Start with [`index.html`](index.html)** — open it directly from disk. It needs
no network.

```
Q_REC_STATUS        QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS
CLEAN_DEMO_STATUS   CLEAN_DEMO_NOT_MET
Q_REC_BRANCH_CLOSED true
freeze              D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1
```

---

## What this is

Not a result with an audit trail attached. **The audit trail is the result.**

A scientific object and a discovery contract induced a relational discovery. The
first discovery looked good on development evidence and **failed** frozen
external qualification, catastrophically, on two discharges. The obvious
explanation — that the cohort pooled distinct operational states — was tested
against target-blind evidence and **refuted**. What remained was that every
constructed object had satisfied the contract *as written*, and the contract
itself was incomplete: nothing in it forbade applying a fitted relation far
outside the range on which it was calibrated. One clause was added, frozen before
any new search. Because the evaluation evidence had informed that revision, the
evidence design was reconciled: discovery resumed with target cross-fitting and
an explicitly narrower claim. It passed.

That sequence — not either accuracy number — is what the example demonstrates.

In the architecture's own terms: one scientific task `q_rec`, two claim branches.
`QREC-B1` carries the sealed-external claim and its preserved qualification
failure. Because the evidence that would have qualified it was spent diagnosing
the defect, the narrower cross-fitted claim was constituted as a
provenance-linked **descendant branch** `QREC-B2`, which carries the final
qualified result. Both are closed. See `REVISION_LEDGER.md` and
`SIR_ARCHITECTURE_MAP.md`.

## The result

| | |
|---|---|
| task | `q_rec` — contemporaneous reconstruction of an admissible diagnostic quantity; target instance `y* = density` |
| claim branch | `QREC-B2`, the cross-fitted finite-object descendant of `QREC-B1` |
| design | six discharge-grouped folds, target cross-fitted |
| `Δ₀` vs calibration mean | **−0.764489** |
| `Δ₁` vs persistence | **−0.027308** |
| V3 · V6 · V-RANGE | **PASS** · PASS_WITH_QUALIFICATION · **PASS** (2,232 checks, 0 failures) |
| discharges above NRMSE 1 | **0** |
| vs raw ridge / raw HistGB / hardened ridge | −0.0960 / −0.1573 / −0.0951 |
| Epoch 1 → Epoch 2 worst case | **11.95 → 0.92** |

**The claim.** Within the predictor-qualified frozen 62-discharge object,
relational supports discovered *without a discharge's own target values*
reconstruct that discharge nontrivially relative to the frozen baselines.

**Not** external validation · not future-discharge transfer · not zero-shot ·
not a universal DIII-D relation · not a unique equation · not universal
coefficients.

Two limits travel with it, always: the margin over persistence is **modest and
era-asymmetric** (carried by the later era; 32–5–25 at discharge level), and
predictor-side applicability used the **whole finite object**, so what was
tested is transfer of the target relationship, not of predictor geometry.

Six folds produced **six different supports**, none identical; a seventh search
produced a seventh. Stable utility, non-unique representations.

## Where to start

| you want | read |
|---|---|
| the whole thing, visually | [`index.html`](index.html) |
| what depends on what | [`WORKFLOW.md`](WORKFLOW.md) |
| where each stage sits in SIR | [`SIR_ARCHITECTURE_MAP.md`](SIR_ARCHITECTURE_MAP.md) |
| why Epoch 2 is not post hoc tuning | [`REVISION_LEDGER.md`](REVISION_LEDGER.md) |
| whether anything leaked | [`INFORMATION_FLOW_AUDIT.md`](INFORMATION_FLOW_AUDIT.md) |
| what may and may not be written | [`S7_12_qualified_result/S7_12_CLAIM_BOUNDARY.md`](S7_12_qualified_result/S7_12_CLAIM_BOUNDARY.md) |
| manuscript-ready text | [`S7_12_qualified_result/S7_12_MANUSCRIPT_SUMMARY.md`](S7_12_qualified_result/S7_12_MANUSCRIPT_SUMMARY.md) |
| the full audit | [`AUDIT_REPORT.md`](AUDIT_REPORT.md) |
| how to check it yourself | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |

Every canonical stage directory carries a `MANIFEST.json` and an `index.html`
with its scientific question, SIR position, verdict, key numbers and governing
freeze.

## Verify

```bash
cd D:\SIR_paper\DIIID_example\S7
python audit_s7.py
```

Offline. Checks **527 frozen artifacts across 21 stages**, recomputes the
canonical numbers rather than re-reading them, and exits non-zero on any
`BLOCKER` or `MAJOR` failure.

## Two things to know before citing this

**1. The manuscript's `q_rec` result is not this one.** Results §1.5, Fig. 4b and
Supplementary §S7.8 still present an earlier reconstruction branch targeting
`I_p` (141 coordinates, 7 development / 55 external, REL10 / RAW10). That branch
was **retired on 2026-09-02** for target-provenance leakage and for having no
skill over a persistence baseline. S7 is the corrective rebuild that its
retirement record required. See [`MANUSCRIPT_ALIGNMENT.md`](MANUSCRIPT_ALIGNMENT.md).

**2. The other task is not here.** `q_desc` — the descriptive contract on the
same 62 discharges — is a different scientific task, not a branch or epoch of
`q_rec`, and its canonical artifacts live outside this directory. They were audited read-only and verified; see
[`WORKFLOW.md`](WORKFLOW.md) §7.

## Layout

```
index.html  README.md  WORKFLOW.md  SIR_ARCHITECTURE_MAP.md  REVISION_LEDGER.md
INFORMATION_FLOW_AUDIT.md  AUDIT_REPORT.md  MANUSCRIPT_ALIGNMENT.md
REPRODUCIBILITY.md  STATUS.md  audit_s7.py

01_observational_object            O          62 discharges, 95 quantities
02_reconstruction_contract         K          contract; correction_v1 = V2
03_target_feasibility_and_boundary O_q        y* = density, 78 predictors
04_mathematical_interpretation     X_q        trajectory ensemble
05_typed_relational_ontology       G_q        constructors
05H_primitive_space_and_...        G_q        70 primitives, C0–C8
06_admissible_universe             A_q        10,778 atoms
07_search_policy_and_frontier      Σ_q, Â_q   162,845 supports explored
08_utility_and_qualification_rules U_q, V_q   made executable
09_development_selection_and_freeze (C*,R*)   frozen before external access
10_external_validation             δ          EPOCH-1 FAILURE
11_sensitivity_and_interpretation  δ          the failure is family-wide
R1_operational_state_reconciliation δ,ρ,j_min hypothesis REFUTED
K2_observational_range_support_...  K^op       P_rec revised, τ = 1, 3,451 atoms
E2_0_protocol_and_resampling_freeze K          six folds, stop rule
E2_0A_predictor_admissibility_...   K^op       boundary reconciled
E2_1_crossfitted_discovery_and_...  Q*_q       FORMAL PASS
E2_2_full_object_descriptive_...    (C*,R*)    descriptive only
S7_12_qualified_result              Q*_q       Q_rec*, branch closed

figures/  generated, with provenance      _audit/  this audit's tooling
_legacy_reference/  the retired branch    _manifests/  initial state
```

## Ground rules honoured throughout

No frozen artifact was ever modified to agree with a later conclusion. Every
superseded version is preserved unmodified and marked. The Epoch-1 failure is
kept as prominently as the pass. No threshold was moved after an outcome was
seen, no support repaired, no discharge or block deleted, no baseline retuned,
no metric redefined. Where a claim could not be supported, it is not made.
