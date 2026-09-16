# S7.12 — final qualified reconstruction result: internal audit report

Stage **S7.12** · Freeze `D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1`
**Assembly and qualification only.**

---

## 1. Verdict

**`Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT`** · 36/36 acceptance checks.

Subsidiary: `FORMAL_PASS` · `CLEAN_DEMO_NOT_MET` ·
`NON_UNIQUE_RELATIONAL_SUPPORTS` · `BRANCH_CLOSED`.

## 2. Lineage — thirteen parents

| stage | manifest | | stage | manifest |
|---|---|---|---|---|
| S7.2 | 35/35 | | S7.K2 | 29/29 |
| S7.3 | 33/33 | | S7.E2.0 | 22/22 |
| S7.6 | 27/27 | | S7.E2.0A | 14/14 |
| S7.7 | 19/19 | | **S7.E2.1** | **39/39** |
| S7.9 | 45/45 | | **S7.E2.2** | **20/20** |
| S7.10 | 31/31 | | | |
| S7.11 | 26/26 | | | |
| S7.R1 | 21/21 | | | |

Every artifact reproduces byte-for-byte. The stage specification required S7.9
through S7.E2.1 at minimum; four earlier contract and ontology stages were
verified as well.

**One convention note.** Self-referential manifest entries — a freeze's own file
and its acceptance-checks file — cannot reproduce by construction, because a
freeze cannot contain the hash of itself. Stages from S7.9 onward declare these
in `self_referential_excluded`; the earliest stages listed them inline without
that key. They are excluded from the reproduction test on the same basis in both
cases, and the exclusions are recorded per stage in
`manifests/S7_12_PARENT_VERIFICATION.json`. Every non-self-referential artifact
of every parent matches. No parent artifact was modified by this stage.

**Ordering verified**: E2.1 frozen (2026-09-06T05:24:38Z) before E2.2
(2026-09-07T04:51:42Z) before S7.12.

## 3. E2.1 result carried unchanged

`Delta_0` and `Delta_1` in `Q_REC_STAR.json` are read from
`E2_1_CROSSFITTED_METRICS.json` and checked equal to the values in
`E2_1_FREEZE.json` — no re-derivation, no rounding drift. Status, tiers, gate
table, era result and all six support hashes carried verbatim.

## 4. What E2.2 could and could not do

E2.2 was frozen **before** S7.12 began and is recorded in `Q_rec*` only as
`REPRESENTATIVE_FULL_OBJECT_DESCRIPTIVE_REALIZATION`, with
`is_externally_validated`, `is_held_out`, `is_canonical` and
`is_the_support_that_produced_the_cross_fitted_metric` all false, and
`cannot_alter_the_qualified_outcome` true. An acceptance check verifies that
`Q_REC_STATUS` equals E2.1's status, so the descriptive stage demonstrably did
not move the verdict.

Had E2.2 failed, `DESCRIPTIVE_REPRESENTATION_NOT_AVAILABLE` would have been
frozen and S7.12 would have proceeded on the six validated fold supports alone.
It did not fail; the contingency was implemented, not exercised.

## 5. Support non-uniqueness is structural in `Q_rec*`

`Q_rec*` does not name one `(C*, R*)`. It carries the procedure and contract, the
six fold representations with their hashes and per-fold utility quantities, the
aggregate out-of-fold evidence, the explicit non-uniqueness statement, and the
optional descriptive realization. `non_unique_supports = true` and
`canonical_equation = false` are fields of the record, not prose.

The conceptual family notation `{(C_k*, R_k*)}_{k=1..6}` is recorded with an
explicit note that it must **not** be imported into the manuscript
automatically — prose should be tried first. The canonical SIR chain was not
rewritten.

## 6. Gates

Carried unchanged from E2.1: V1 INHERITED_PASS · V2 PASS · **V3 PASS** · V4 PASS ·
V5 PASS · **V6 PASS_WITH_QUALIFICATION** · V7 PASS · V8 PASS · **V-RANGE PASS** ·
V10 INHERITED_PASS. No mandatory gate failed.

`no_new_gate_created` and `no_threshold_moved` are asserted in
`Q_REC_GATE_TABLE.json` and checked. The Epoch-1 gate table (V3 FAIL, V6 FAIL,
V9 FAIL) is preserved in the same record, unmodified.

V-RANGE is recorded as
`APPLICABILITY_PROPERTY_NOT_A_PERFORMANCE_RESULT`, with `pass_by_construction`
true — 2 232 checks, 0 failures, exactly as the K2 closure property predicts.

## 7. Language discipline, enforced mechanically

Acceptance checks verify, in the frozen records rather than only in prose:

- the era asymmetry is carried with both directions (`PRACTICAL_TIE` earlier,
  `MATERIAL_IMPROVEMENT` later), and "both eras improve materially" is listed as
  a forbidden statement;
- the persistence margin is labelled `MODEST`, with "SIR dramatically beats
  persistence" listed as a forbidden headline;
- the raw-baseline margins (−0.0960, −0.1573, −0.0951) are present to four
  decimal places;
- the forbidden causal claim "K2 proved the range-support rule caused the
  improvement" is recorded as forbidden, alongside the two permitted
  formulations;
- every entry of the not-supported claim list is present, including "virgin
  external validation" and "untouched external validation";
- τ = 1 carries its exact meaning — *application may extend beyond the
  calibration hull by no more than one complete calibration-range width*;
- the information-boundary statement is flagged as a clarification, with
  `I_q_notation_change_required = false`;
- `pcdiamag3` retains `UNCALIBRATED_SIGNAL` and the universal-coefficient claim
  is false.

## 8. Provenance preserved

`Q_REC_PROVENANCE_CHAIN.json` carries the nine-step arc with each step's source
freeze, including the Epoch-1 negative marked `IMMUTABLE`, the R1 hypothesis
verdict `REFUTED` with its target-blind evidence, the K2 revision class
`MINIMAL_P_ONLY`, and the E2.0A principle. Acceptance checks verify each of these
four survives.

## 9. What S7.12 did not do

No search. No fit. No gate evaluation. No metric recomputation. No threshold
moved, no support rescued, no budget increased, no seed added, no fold changed,
no discharge or block deleted, no baseline or utility altered. Zero parent
artifacts modified. No Epoch 3. No S7.13. `q_desc` untouched.

`EPOCH2_IS_FINAL_QREC_ATTEMPT` remains true and
`NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED` is now recorded alongside
`Q_REC_BRANCH_CLOSED`.

## 10. Files

6 Markdown (limit 8; combined with E2.2's 3, that is 9 against the combined limit
of 14) · 9 JSON · manifests · 1 script.

## 11. Recommendation

Report the formal positive result, with editorial caution on the accuracy claim.

The methodological arc is the strongest thing this example produces and belongs
in the main text; the reconstruction accuracy claim should be stated with both
limits attached and should not be the headline number. `Δ₁ = −0.027` sits almost
exactly at the ceiling S7.11 independently found in Epoch 1, where no support in
the development-equivalent family beat persistence by more than 0.0287 — which
suggests the margin is a property of the object and task, not of any
representation.

`PAPER_UTILITY = MEDIUM_HIGH` — high for the method demonstration, moderate for
the reconstruction claim itself.
