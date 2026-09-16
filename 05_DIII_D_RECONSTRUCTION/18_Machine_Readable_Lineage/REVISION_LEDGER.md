# Revision ledger

Every S7 transition that changed something, classified so that four different
things cannot be confused.

## The hierarchy

```
scientific task q
    └── provenance-linked claim branch      fixes (q, I_q, U_q, V_q, Ω_q)
            └── operational epoch(s)        revises (P_q, B_q, H_q)
```

A scientific task can be pursued deeply without inventing a new `q` every time an
implementation or an operational contract is corrected. The point of the
hierarchy is **no silent drift**: what was originally asked, what changed, why,
and what each qualified claim actually establishes must all remain legible.

## The four dispositions

| | disposition | what was wrong | consequence |
|---|---|---|---|
| **Case A** | incorrect instantiation | an object was instantiated incorrectly; the contract semantics were already adequate | replay the constructed objects from `j_min`. Same task, same claim branch, same contract semantics. |
| **Case B** | incomplete operational contract | every object satisfied the contract *as written*, but `P_q`, `B_q` or `H_q` was insufficient | revise the operational contract and replay from `j_min`. Same task, same claim branch. Whether this **advances the operational epoch** depends on execution — see below. |
| **Case C** | material claim revision | a claim-defining commitment (`I_q`, `U_q`, `V_q`, `Ω_q`) must materially change | a provenance-linked **descendant claim branch** under the **same task `q`**. |
| **new q** | changed scientific task | the scientific question itself changes | a new task, and a new lineage under it. |

Case C creates a descendant branch, **not** a new `q` — unless the task itself
changes. Reconciliation `ρ_q(K_q^(e), Z_q^(e), δ^(e)) ↦ (K_q^(e+1), j_min)`
describes **same-branch** reconciliation (Cases A and B); a Case-C disposition is
a different response to the same audit, producing a descendant branch rather than
another same-branch replay.

`j_min` is the earliest stage that must be replayed. Where the defect touches
only the instantiated construction, `K_q^(e+1)` may equal `K_q^(e)`; the epoch
and replay record still preserve provenance.

### Contract version is not the same as operational epoch

A Case-B revision produces a new operational-contract **version**. It advances
the operational **epoch** only when the superseded contract had already governed
an **executed** operational realization. A pre-execution correction, or the
completion of an as-yet-unexecuted contract, is recorded as a **versioned
correction within the pending epoch**, provenance preserved.

> operational-contract **version** change ≠ operational-**epoch** advance

"Epoch" therefore identifies a materially executed operational regime, not every
contract correction. In this lineage:

| stage | Case B revision | epoch |
|---|---|---|
| **S7.2C** | nine contract clauses, before any object existed | versioned correction inside epoch 1 |
| **S7.7R** | search budget `B_rec`, before the qualification it governed had completed | versioned correction inside epoch 1 |
| **S7.K2** | `P_rec` gains range support, **after** epoch 1 had executed and failed qualification | **advances to epoch 2** |
| **S7.E2.0A** | `tau_train` retired, before any Epoch-2 search executed | versioned correction inside the pending epoch |

`revision_level` in the stage metadata marks every contract version; the `epoch`
field marks only executed regimes. Every version remains identifiable, so nothing
is lost by not numbering it.

---

## The table

| # | Stage | Defect record δ | What was invalid | Claim core changed? | Operational contract changed? | Constructed object changed? | j_min | Evidence status after | Case | Justification |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **S7.2C** | nine contract clauses ambiguous or wrong on inspection | contract text, before any instantiation | **no** — clarified, not redefined | yes (`P`, `B` wording) | no | `K^op` | untouched; nothing had been evaluated | **B — pre-instantiation versioned correction** | The defect was in the operational contract *text*, not in an instantiated object, so it is Case B. Its pre-instantiation timing explains why it did not advance the operational epoch — it does not make it Case A. Corrected before any object existed, so no evidence could have been contaminated. V1 preserved byte-for-byte. |
| 2 | **S7.3 → S7.3V2** | target temporal resolution not source-supported | the instantiated target and boundary | **no** | no | **yes** — target reselected, boundary recomputed | `O_q` | untouched; external cohort still sealed | **A** | An instantiation error: the contract already required source-supported cadence. Replay from `O_q`. |
| 3 | **S7.4 → S7.4V2** | derived from #2 | the instantiated `X_rec` | no | no | yes | `X_q` | untouched | **A** | Consequence of #2. |
| 4 | **S7.6 → S7.6R** | ontology hardening changed the primitive space | the instantiated universe | no | no | yes — 6,034 → 10,778 atoms | `𝔄_q` | untouched | **A** | Development-stage refinement, before any external access. Both versions preserved. |
| 5 | **S7.7 → S7.7R** | search budget block | the explored frontier | no | yes (`B_q`) | yes — frontier re-explored | `𝔄̂_q` | untouched | **B** | V1 status `BLOCKED_SEARCH_BUDGET` preserved as audit history. |
| 6 | **S7.10** | **the external qualification failed** | *nothing was invalidated* | no | no | no | — | **protected evidence spent**: the 42 external discharges are now inspected | — | This is not a revision. It is the result. Recorded, preserved, and never repaired: `C_dev_star_changed = false`, `metric_changed = false`, `threshold_changed = false`. |
| 7 | **S7.11** | is the failure specific to the representative? | nothing | no | no | no | — | development-equivalent family now inspected too | — | Predeclared: the sensitivity plan was hashed **100.6 s before** the first external value was read. No new support was promoted. |
| 8 | **S7.R1** | candidate explanation: pooled operational states | **the explanation itself** | no | no | no | `NONE_OF_THE_INSTANTIATED_OBJECTS` | target-blind predictor evidence only | **refutation** | The hypothesis was *tested*, not assumed, and rejected: development covers the external actuation range and one development discharge exceeds both failing discharges. Case A is therefore ruled out and Case B established. |
| 9 | **S7.K2** | a fitted relation may be applied arbitrarily far outside its calibration range, and no clause forbids it | the **operational admissibility contract** `P_rec` | **no** — `q`, `I_rec`, `U_rec`, `Ω_rec` unchanged | **yes** — `P_rec` gains `P-RANGE-SUPPORT`; the operational qualification procedure is correspondingly extended with the `V-RANGE` check that tests satisfaction of the new admissibility condition | no (nothing re-instantiated here) | `𝔄_q` — the candidate set changes, so search must be replayed | Epoch-1 evaluation evidence is now **development evidence** | **B** | `revision_class = MINIMAL_P_ONLY`. Rule generic, dimensionless, target-blind; τ grid hashed before any survivor count. **Same claim branch QREC-B1, new operational epoch.** |
| 10 | **S7.E2.0** | the sealed-external claim can no longer be evidenced, because the evidence that would have qualified it has been spent | the **evidentiary commitment** `V_rec` | **yes — `V_rec` materially narrowed; `Ω_rec` unchanged** | yes — folds, budget, stop rule declared | no | — | design frozen before any Epoch-2 search | **C — descendant branch** | This stage **constitutes descendant claim branch QREC-B2** under the same task `q_rec`. The narrowing is conservative and forced, not chosen for advantage. Applicability risk (~1 in 5) disclosed **prospectively**, before committing. |
| 11 | **S7.E2.0A** | predictor-side blinding is stronger than the finite-object claim requires | the **Epoch-2 protocol**, not any object | no — a **clarification** of `I_rec`, not a redefinition | yes — `tau_train` retired with no replacement | no | `𝔄_q` (basis definition) | unchanged | **B** | Grounded on the contract's own precedent: S7.6R's partial-map rule is an *application-time* predicate. E2.0 preserved as historical parent. |
| 12 | **S7.E2.1** | none — execution | — | no | no | yes — six new `(C*,R*)` | — | held-out targets opened only after each support was hashed | — | One frozen policy, one non-interactive run. Six folds, no fold inspected to decide how to run another. |
| 13 | **S7.E2.2** | none — exposition | — | no | no | yes — one descriptive `(C*,R*)` | — | all targets open, explicitly, for description only | — | Run **after** the verdict was frozen; cannot alter it, and every flag says so. |
| 14 | **S7.12** | none — assembly | — | no | no | no | — | unchanged | — | No search, no fit, no gate, no metric. |

## The Epoch-1 → Epoch-2 transition

Rows 6 → 9 → 10 → 11 → 12 are the transition, and they are **two different
dispositions in sequence**, not one.

### Step one — S7.K2 is Case B, and stays inside QREC-B1

The claim-defining core is untouched. `q` is the same reconstruction task.
`I_rec` is unchanged in semantic meaning. `U_rec` is unchanged and hash-pinned.
`Ω_rec` is still the frozen 62-discharge object. `V_rec` is unchanged **as a
semantic commitment**: the branch still intends to qualify structural transfer on
a sealed external cohort at this point.

What changed is the operational admissibility rule `P_rec`, which gained one
clause. The `V-RANGE` check that accompanies it is the *operational* procedure
for testing satisfaction of that revised admissibility condition — it is not
evidence that the claim-defining `V_rec` changed. This is exactly what the frozen
record means by `revision_class = MINIMAL_P_ONLY`.

So K2 advances the **operational epoch** within QREC-B1. **K2 did not create the
descendant branch.**

### Step two — S7.E2.0 is Case C, and constitutes QREC-B2

The descendant branch arises one stage later, and for a different reason.

Epoch-1 evaluation evidence had been inspected, and then used to diagnose the
defect and motivate the revision. Under the protected-evidence rule it thereby
became **development evidence for the revised procedure**. It could no longer
serve as untouched validation evidence for anything downstream of K2.

Of the three admissible responses to spent protected evidence — new protected
evidence, a valid cross-fitted qualification design, or an explicitly narrowed
claim — Epoch 2 took the **second and third together**. That is a *material*
revision of the evidentiary commitment `V_rec`:

| | QREC-B1 | QREC-B2 |
|---|---|---|
| evidentiary design | frozen support, sealed 42-discharge external cohort | six-fold discharge-grouped target cross-fitting over all 62 |
| claim | external structural transfer to a sealed cohort | target-cross-fitted reconstruction over a predictor-qualified finite object |
| strength | stronger | **strictly weaker** |

**`Ω_rec` did not change.** The intended claim domain — a member of
`K_q^claim` — is the frozen 62-discharge observational object in both branches.
What changed is `V_rec`, the evidentiary commitment. The **supported** domain
`Ω*_rec` narrows downstream as a consequence, but `Ω*_rec` belongs to `Q*_q`, not
to `K_q^claim`, so it is an *outcome* of the revision rather than a second
claim-defining revision alongside it.

A material change to a claim-defining commitment is a **Case-C disposition**, and
a Case-C disposition under an unchanged task produces a **provenance-linked
descendant claim branch**. So QREC-B2 is a descendant of QREC-B1 under the same
`q_rec`, constituted at S7.E2.0 and carrying the qualified result assembled in
S7.12.

Two things this is not. It is **not a new `q`** — the scientific task never
changed, and inventing a new task for a narrowed evidentiary commitment would
lose exactly the lineage that makes the failure legible. And it is **not
external validation** — under either the branch reading or any other, nothing in
QREC-B2 may be described that way.

### Why the narrowing is the honest direction

The claim got weaker, not stronger, and it got weaker because the evidence budget
had been spent rather than because a weaker claim was easier to support. The
Epoch-1 negative result stands unmodified in QREC-B1; the Epoch-2 positive result
stands in QREC-B2 with its narrower claim attached to it in `Q_REC_STAR.json`,
not appended as a footnote.

### A note on the earlier reading

The original forensic audit recorded this transition as an unresolved tension and
preserved two defensible readings, because the manuscript architecture had not
yet finalized the task / branch / epoch hierarchy. It was right to do so at the
time. With §1.1 finalized, the hierarchy resolves it: the transition is a
**Case-C descendant claim branch under the same task**. That reading is now
canonical throughout this package, and the earlier two-reading discussion is
retained only as this historical note.

## What was never done

Across every row above: the scientific task `q_rec` never changed, no threshold
moved after seeing an outcome, no support was repaired or substituted, no
discharge or block was deleted, no baseline was retuned, no metric was redefined,
no era was dropped, no second seed was run as a rescue, no search budget was
extended as a rescue, and no parent artifact was modified. Each is asserted in the corresponding stage freeze under `governance`
or `no_repair_after_external_results`, and every one of those freezes reproduces
byte-for-byte.
