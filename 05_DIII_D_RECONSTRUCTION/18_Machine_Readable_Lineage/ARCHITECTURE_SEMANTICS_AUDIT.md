# S7 architecture-semantics audit

A narrow hardening pass reconciling the S7 documentation and indexing layer with
the finalized SIR §1.1 task / branch / epoch semantics.

**Verdict — `S7_ARCHITECTURE_SEMANTICS_RECONCILED`.**

No scientific artifact was modified. No search was rerun. No numerical result,
gate, threshold, metric or verdict changed. **527/527 frozen artifacts still
reproduce byte-for-byte.** What changed is vocabulary and the lineage metadata
that expresses it.

Machine-readable: `ARCHITECTURE_SEMANTICS_AUDIT.json`.

---

## 1. The authoritative architecture used

```
scientific task q
    └── provenance-linked claim branch      fixes (q, I_q, U_q, V_q, Ω_q)
            └── operational epoch(s)        revises (P_q, B_q, H_q)
```

- **`q`** is the scientific **task**. It is deliberately more stable than any
  single target choice, protocol realization or validation implementation. The
  subscript marks association with a task; it does not imply that only one
  contract or branch may ever exist under it.
- A **claim branch** is a provenance-linked realization of that task under a
  particular set of claim-defining commitments. Those are **semantic**
  commitments, not every implementation detail used to instantiate them.
- An **operational epoch** identifies a materially executed operational regime.
  A Case-B revision of `P_q`, `B_q` or `H_q` **advances** the epoch only when the
  superseded contract had already governed an executed realization; otherwise it
  is a versioned correction within the pending epoch. Contract *version* change ≠
  *epoch* advance.
- A **descendant claim branch** arises when reconciliation requires a *material*
  change to `I_q`, `U_q`, `V_q` or `Ω_q`. Only a material change to the **task**
  requires a new `q`.

`ρ_q(K_q^(e), Z_q^(e), δ^(e)) ↦ (K_q^(e+1), j_min)` describes **same-branch**
reconciliation. A descendant branch is a different disposition of the same audit,
not another same-branch replay.

`I_q` is what information is epistemically **admissible**; `V_q` is what
**evidentiary role** admissible information may play. Evidence roles are
variable- and transition-specific — no datum carries one global
development/validation status for every transition.

**Manuscript status.** The shipped artifact `draft/SIR_paper.pdf`
(sha256 `94ccf533…`) was re-checked at this pass and is **unchanged**: it still
carries the flat 8-tuple §1.1 and none of this vocabulary. The finalized
semantics above are therefore the authority for S7's documentation, and
`MANUSCRIPT_ALIGNMENT.md` now separates *the artifact audited* from *the current
architecture*.

## 2. Files inspected

| layer | scope |
|---|---|
| active canonical documentation | 9 top-level markdown files |
| generated indexing layer | `CANONICAL_INDEX.json`, 21 stage `MANIFEST.json`, 21 stage `index.html`, dashboard |
| machine-readable audits | `AUDIT_REPORT.json`, `MANUSCRIPT_ALIGNMENT.json`, `INFORMATION_FLOW_AUDIT.json`, `CLAIM_EVIDENCE_MATRIX.json` |
| generators | `_audit/stage_registry.py`, `_audit/build_*.py`, `audit_s7.py` |
| **frozen stage artifacts** | **inspected, not edited** — 128 of the 174 markdown files in S7 are inside freeze manifests |

A recursive semantic scan covered the terms listed in the pass specification —
*claim core unchanged*, *V_rec extended*, *new branch*, *same branch*,
*operational epoch*, *descendant branch*, *vsurf*, *Case A/B/C*, *narrowed
claim*, *external validation*, *cross-fitted*, *protected evidence*, *spent*,
*j_min*, *branch closed*, *V-RANGE* and the rest — classified by meaning rather
than replaced by string match.

## 3. Stale semantics found, and what was done

| # | Where | Statement | Class | Disposition |
|---|---|---|---|---|
| 1 | `REVISION_LEDGER.md` | "Case C — the scientific claim itself changed; this is a new branch" | `STALE_SEMANTICS` | Redefined: Case C is a **material claim revision**, producing a descendant branch under the same `q`; a fourth disposition, **new q**, covers a changed task. |
| 2 | `REVISION_LEDGER.md` | §"One tension recorded rather than resolved away" — two competing readings of `V_q` left active | `AMBIGUOUS` | **Resolved.** Replaced by the canonical two-disposition account. Retained as a short historical note explaining why the ambiguity existed. |
| 3 | `REVISION_LEDGER.md`, `SIR_ARCHITECTURE_MAP.md`, stage registry | "`V_rec` gains / is extended by `V-RANGE`" | `AMBIGUOUS` | Reworded so it cannot imply that the claim-defining `V_rec` changed at K2. `P_rec` was revised; the operational qualification procedure was correspondingly extended with the `V-RANGE` check. |
| 4 | `SIR_ARCHITECTURE_MAP.md` | "It is **not Case C**. `q` (reconstruct `density`) …" | `STALE_SEMANTICS` | Removed. `q_rec` is now stated as a **task**, with `y* = density` as the target **instance**; K2 is Case B and the descendant branch is constituted later, at S7.E2.0. |
| 5 | `WORKFLOW.md` | "Three orderings, not one" — no branch-lineage view | `AMBIGUOUS` | Fourth ordering added (§2b **branch lineage**), kept distinct from the dependency graph. |
| 6 | `WORKFLOW.md`, `README.md` | "`q_desc` … is a different **branch**" | `AMBIGUOUS` | `q_desc` is a different **scientific task**, hence a different lineage entirely — not a branch or epoch of `q_rec`. |
| 7 | `AUDIT_REPORT.md` | referred to the unresolved `V_q` tension | `HISTORICAL_BUT_VALID` | Preserved as a record of what the original audit correctly found, with a note on how the finalized §1.1 resolves it. Not rewritten to pretend it was resolved earlier. |
| 8 | `MANUSCRIPT_ALIGNMENT.md` | one undifferentiated "the manuscript" | `AMBIGUOUS` | Split into **manuscript artifact audited** (unchanged PDF) versus **current manuscript architecture**; four new §1.1 entries added (`1.1-f`, `1.1-g`, `1.1-h`, and the hierarchy). |
| 9 | stage `MANIFEST.json` ×21, `CANONICAL_INDEX.json` | no task / branch / epoch metadata | `AMBIGUOUS` | Added `scientific_task_id`, `claim_branch`, `claim_branch_role`, `parent_claim_branch`, `revision_level`; plus `scientific_tasks`, `claim_branches` and `branch_lineage` at the index level. |
| 10 | `INFORMATION_FLOW_AUDIT.md/.json` | `I_q` and `V_q` not explicitly separated | `AMBIGUOUS` | Separation stated at the head of the document and in `policy_separation`; the protected-evidence trigger recorded explicitly. |
| 11 | frozen stage prose, e.g. `E2_0_PROTOCOL_AUDIT_REPORT.md` | epoch/branch vocabulary predating §1.1 | `FROZEN_DO_NOT_EDIT` | **Preserved unmodified.** Mapped to current semantics here and in `SIR_ARCHITECTURE_MAP.md`, never rewritten in place. |

## 4. Statements intentionally preserved

The freeze is evidence. Reproducibility was not traded for terminological
tidiness.

- **128 frozen markdown files** and every frozen JSON keep the vocabulary that
  was in force when they were sealed. Where they say "Epoch 2" or "the branch",
  the mapping to the current hierarchy is given here and in
  `SIR_ARCHITECTURE_MAP.md`, not by editing them.
- `Q_REC_BRANCH_CLOSED = true` and `NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED = true`
  in `S7_12_FREEZE.json` are **unchanged**. Their current reading: *the final
  canonical `q_rec` descendant branch is closed, and the `q_rec` scientific
  lineage has no authorized further discovery epoch on any branch.*
- `revision_class = MINIMAL_P_ONLY` in `S7_K2_FREEZE.json` is **unchanged** and
  remains exactly right.
- The Epoch-1 negative result and every superseded stage version stand
  unmodified.
- The original forensic audit's record of the `V_q` ambiguity is preserved rather
  than retconned. It was correct to record an ambiguity before the architecture
  was finalized.

## 5. The final `q_rec` lineage

```
q_rec  (scientific task)
│
├── QREC-B1   sealed-external claim branch
│     ├── operational epoch 1   S7.2 … S7.10   → QUALIFICATION FAILED
│     │      versioned Case-B corrections inside it: S7.2C, S7.7R
│     ├── audit                 S7.11, S7.R1   → Case A refuted
│     └── operational epoch 2   S7.K2          → Case B, branch unchanged
│
└── QREC-B2   cross-fitted finite-object DESCENDANT branch (parent QREC-B1)
      └── operational epoch 1   (S7's historical label: "Epoch 2")
      ├── S7.E2.0    Case C — V_rec narrowed; constitutes the descendant branch
      ├── S7.E2.0A   Case B version inside the pending epoch — tau_train retired
      ├── S7.E2.1    FORMAL PASS
      ├── S7.E2.2    descriptive realization
      └── S7.12      Q_rec*  —  CLOSED
```

> `q_rec` denotes the scientific reconstruction task. Early source-resolution
> reconciliation corrected its instantiated target from `vsurf` to `density`
> without changing the task or the claim branch. Epoch 1 subsequently failed
> protected qualification. S7.R1 refuted an incorrect-object explanation and
> localized the defect to an incomplete operational admissibility contract.
> S7.K2 therefore revised `P_rec` by adding observational range support,
> advancing the operational epoch while preserving the claim branch. Because
> Epoch-1 evaluation evidence had then become development evidence for the
> revised procedure, the subsequent qualification could no longer support the
> original sealed-external claim. Epoch 2 therefore proceeded as a
> provenance-linked descendant claim branch under the same `q_rec` task, using
> target cross-fitting over the predictor-qualified frozen 62-discharge object
> and an explicitly narrower claim. That descendant branch produced the final
> qualified `Q_rec*` result and is closed.

## 6. Treatment of `V_q`

`V_q` is a **claim-defining commitment**: what evidentiary role admissible
information may play, and what qualification the claim must survive. It is not
every procedural detail used to implement that commitment.

| stage | `V_rec` as a semantic commitment | operational qualification procedure |
|---|---|---|
| S7.2 … S7.10 | qualify structural transfer on a sealed external cohort | block-local prequential geometry, six baselines, gates V1–V10 |
| **S7.K2** | **unchanged** | extended with the `V-RANGE` check |
| **S7.E2.0** | **materially narrowed** → cross-fitted qualification over the finite object | six discharge-grouped folds |

`V_rec` is the **only** claim-defining commitment revised at S7.E2.0. `Ω_rec`,
the intended claim domain and a member of `K_q^claim`, is unchanged — the same
frozen 62-discharge object in both branches. The domain actually **supported** by
qualification, `Ω*_rec`, narrows as a consequence, but `Ω*_rec` belongs to `Q*_q`
rather than to `K_q^claim`; it is an outcome of the revision, not a second
claim-defining revision. This document therefore never says that `V_rec` and
`Ω*_rec` are both claim-defining commitments.

The narrowing at S7.E2.0 is what makes `QREC-B2` a descendant branch rather than
a third operational epoch of `QREC-B1`. It was forced by the protected-evidence
rule, not chosen for advantage, and it made the claim **strictly weaker**.

Under every reading, nothing in `QREC-B2` may be described as external
validation, and the active documentation contains no such description.

## 7. Treatment of S7.K2 and `V-RANGE`

**K2 remains Case B, `revision_class = MINIMAL_P_ONLY`, inside `QREC-B1`.**

- `P-RANGE-SUPPORT` **is** the K2 revision. It lives in `P_rec` and is an
  operational admissibility rule.
- `V-RANGE` is the **operational qualification check** that tests satisfaction of
  that revised admissibility condition. Its existence is not denied anywhere, and
  it is not presented as a change to the claim-defining `V_rec`.
- **K2 did not create the descendant branch.** The descendant branch arises at
  S7.E2.0, because the qualification claim narrowed after the protected-evidence
  reconciliation — a different consequence, one stage later.

## 8. Treatment of `vsurf → density`

**Case A, same task, same claim branch.** The contract already required
source-supported temporal resolution; the first instantiated target violated it;
applying the *same* rule correctly selected `density`. `O_q` and the downstream
`X_q` were regenerated from `j_min`.

`q_rec` is the reconstruction **task**; `y* = density` is the target
**instance** selected under the frozen task rules. Defining `q_rec` as "reconstruct
density" would make this correction impossible to classify as same-task
reconciliation, so the documentation no longer does.

## 9. Treatment of branch closure

Frozen fields untouched. Current reading, stated in the active documentation:

- `QREC-B1` — closed by qualification failure, then superseded. Its
  **negative qualification outcome** stands preserved and unmodified: the branch
  was subjected to qualification and failed it.
- `QREC-B2` — closed by `S7.12` with the qualified positive result `Q_rec*`.
- The `q_rec` **scientific lineage** has no authorized further discovery epoch on
  any branch.

## 10. Integrity confirmations

| | |
|---|---|
| frozen scientific artifacts modified | **0** — 527/527 still reproduce byte-for-byte |
| freeze JSON edited for terminology | **0** |
| searches rerun | **0** |
| models refit, supports recomputed | **0** |
| thresholds, gates, metrics changed | **0** |
| numerical results changed | **0** |
| scientific verdicts changed | **0** |
| new discovery epochs or branches created by analysis | **0** |
| markdown files edited | **7** (`README`, `STATUS`, `WORKFLOW`, `SIR_ARCHITECTURE_MAP`, `REVISION_LEDGER`, `INFORMATION_FLOW_AUDIT`, `MANUSCRIPT_ALIGNMENT`) plus `AUDIT_REPORT` and this new document — 9 of a ≤15 preference |
| files moved, renamed or deleted | **0** |

`S7_AUDIT_PASS_WITH_QUALIFICATIONS` stands unchanged, and both `MAJOR` findings
remain what they were: properties of the manuscript artifact, not of S7.

## 11. Final consistency clarification

A subsequent, tightly scoped documentation pass resolved three residual
ambiguities left by this one. No scientific artifact, result or verdict was
touched.

**Operational-epoch bookkeeping.** The Case-B definition could be read as making
every `P_q`/`B_q`/`H_q` revision a new numbered epoch. It does not. A Case-B
revision advances the operational epoch **only when the superseded contract had
already governed an executed operational realization**; a pre-execution
correction, or completion of an as-yet-unexecuted contract, is a **versioned
correction within the pending epoch**. So `S7.2C`, `S7.7R` and `S7.E2.0A` are
versioned Case-B corrections that advance nothing, and **`S7.K2` is the single
epoch advance** in this lineage, because it follows a regime that had executed
and failed. Counted branch-locally, `QREC-B1` has two operational epochs and
`QREC-B2` has one — its first, retaining S7's historical label "Epoch 2". The
stage metadata already encoded this: `revision_level` marks every contract
version, while `epoch` marks only executed regimes.

**`Ω_q` versus `Ω*_q`.** Earlier wording described S7.E2.0 as materially revising
"`V_rec` and the supported domain `Ω*_rec`", which wrongly implied `Ω*_rec` is a
claim-defining commitment. It is not: `Ω*_rec` belongs to `Q*_q`. **`Ω_rec`, the
intended claim domain, is unchanged** — the same frozen 62-discharge object in
both branches — and `V_rec` is the only member of `K_q^claim` revised. `Ω*_rec`
narrows downstream as a consequence.

**`QREC-B1` outcome wording.** "Its negative result stands as that branch's
qualified outcome" could be misread as a positive qualification. The canonical
phrase is now **negative qualification outcome**, with *preserved qualification
failure* and *failed qualification result* as acceptable variants.

## 12. Remaining ambiguities

Stated rather than papered over.

1. **The shipped manuscript still does not contain this architecture.** The PDF
   is byte-identical to the one originally audited. Until it is regenerated,
   S7's documentation and the manuscript describe the workflow in different
   vocabularies. This is `MANUSCRIPT_ALIGNMENT.md` findings 1.1-a through 1.1-h.
2. **Where exactly a claim branch begins is a judgement.** This package places
   the boundary at S7.E2.0, the stage that froze the cross-fitted design and the
   narrowed claim type. A reader could argue for S7.E2.0A, which reconciled the
   information boundary within that design. Nothing downstream depends on the
   choice: both stages precede any Epoch-2 search, and neither changes the task,
   the numbers or the claim boundary. The choice is recorded rather than hidden.
3. **`QREC-B1`'s second operational epoch produced no qualification of its own.**
   K2 advanced the epoch, and the branch was superseded before that epoch could
   be qualified under the sealed-external commitment. That is an accurate
   description of what happened, not a gap.
4. **Frozen prose predates this vocabulary**, by design. A reader moving between
   a frozen stage document and this layer will meet "Epoch 2" used where the
   current architecture would distinguish an epoch advance from a descendant
   branch. The mapping is here; the frozen text is not edited.
