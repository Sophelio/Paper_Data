# S7.E2.0 — Discovery Epoch 2 protocol: internal audit report

Stage **S7.E2.0** · Freeze `D3D-SIR-S7.E2.0-DISCOVERY-EPOCH2-PROTOCOL-V1`
Parent `D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1`

---

## 1. Executive verdict

**`FROZEN_WITH_QUALIFICATIONS`** · 34/34 acceptance · no search, no fit, no
baseline, no scoring.

A discharge-grouped, cross-fitted validation architecture is frozen: six
deterministic outer folds over the 62 discharges, a thirteen-step per-fold access
ordering, a two-role application of the K_REC_V2 range-support condition, a frozen
search budget, and unchanged utility and gates.

**The dominant finding is a disclosed risk, not a design flaw.** Prospective
target-blind analysis puts the `FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT` gate at
roughly **1 in 5** under random support draws. Epoch 2 is more likely to fail on
applicability than on reconstruction skill. The standard was **not** weakened.

## 2. Parent verification

Fifteen authoritative freezes through S7.K2. **S7.9 45/45, S7.10 31/31, S7.11
26/26, S7.R1 21/21, S7.K2 29/29 reproduce byte-for-byte.** `K_REC_V2` hash matches
the K2 freeze; `K_REC_V1` preserved; `tau = 1`; `U_rec` UNCHANGED; V-RANGE does
not replace V3; Epoch-1 verdict and gate table unchanged; no S7.12; no Epoch-2
result. Zero substantive drift.

## 3. Protocol firewall

`target_reads = 0` · `model_error_reads = 0` · `residual_reads = 0` ·
`epoch1_performance_reads_for_partition = 0`, asserted in code.

Partition variables actually used: **processing era and discharge id (sort key
only)**. Coordinate values were opened solely to evaluate the frozen range-support
predicate, never to partition.

## 4. Outer-fold design

Algorithm `E2_OUTER_FOLD_ASSIGNMENT_V1`: sort by `(era in [earlier, later], then
discharge id)`, assign `fold = position mod 6`. Deterministic; **no random seed**;
**one partition generated**; no trial-and-selection.

| fold | n | earlier | later | E1 dev | E1 ext | discovery |
|---|---|---|---|---|---|---|
| 0 | 11 | 6 | 5 | 7 | 4 | 51 |
| 1 | 11 | 6 | 5 | 2 | 9 | 51 |
| 2 | 10 | 6 | 4 | 2 | 8 | 52 |
| 3 | 10 | 6 | 4 | 6 | 4 | 52 |
| 4 | 10 | 6 | 4 | 2 | 8 | 52 |
| 5 | 10 | 5 | 5 | 1 | 9 | 52 |

62 total; every discharge held out exactly once; sizes in {10, 11}; era totals
35/27. Epoch-1 cohort membership is recorded for reference only and was **not** a
balancing variable.

Balance is achieved *by construction* — systematic assignment within an
era-sorted ordering — rather than by optimising any balance criterion, so no
partition was ever scored.

## 5. Information boundary

Thirteen steps, machine-auditable, with step 6 the hinge: **the support is hashed
before any held-out predictor is opened.** Held-out predictor ranges may not
influence candidate filtering; held-out targets may not influence support
discovery; protected targets open last, for scoring only. Each fold must emit an
access log recording what was opened at each step.

## 6. Range support in two roles

| | threshold | source | role |
|---|---|---|---|
| training admissibility | **tau_train = 0.5** | `D_train` predictors only | search-side, frozen at E2.0 under section 11A |
| held-out qualification | **tau = 1.0** | `D_test` predictors, after support hash | contractual, K_REC_V2, unchanged |

The stricter training requirement does **not** alter K_REC_V2. Its reading is
half a calibration range of headroom, leaving a further half range before the
contractual threshold. It exists because a coordinate admitted at exactly tau on
training has no headroom on unseen discharges.

Per-fold training-admissible basis at `tau_train = 0.5`: **2 217–2 352
coordinates**, all seven constructor families present in every fold.

No global pre-filter over all 62 is performed; the basis is rebuilt per fold from
that fold's training discharges alone.

## 7. Applicability feasibility — measured before committing

`manifests/APPLICABILITY_FEASIBILITY.json`, target-blind, 4 000 random
12-coordinate draws per fold:

| tau_train | basis (min–max) | smallest family | P(12 held-out supported), per fold | six-fold product |
|---|---|---|---|---|
| 0.25 | 1 072–1 293 | 5 | 0.578–1.000 | **0.352** |
| 0.40 | 1 869–1 980 | 5 | 0.626–0.970 | 0.304 |
| **0.50** | **2 217–2 352** | **5** | **0.604–0.930** | **0.200** |
| 0.60 | 2 550–2 678 | 6 | 0.557–0.896 | 0.152 |
| 0.75 | 3 022–3 184 | 6 | 0.419–0.748 | 0.050 |
| 1.00 | 3 653–3 817 | 8 | 0.299–0.510 | 0.004 |

**`tau_train = 0.5` was chosen on interpretability and basis adequacy, explicitly
not by maximising the pass probability.** `tau_train = 0.25` gives a higher joint
estimate (0.35) on a thinner basis; that trade-off is recorded rather than
silently resolved in favour of better odds.

**No hostile discharge exists.** Per-discharge retention of its fold's basis
ranges 0.938–1.000, median 0.998; none below 0.80. The difficulty is compounding
attrition across 12 coordinates and ~10 unseen discharges — not a pathological
shot. The Epoch-1 culprit, `PROD(gasa,gasa)`, is excluded from every training
basis by K_REC_V2 itself.

**Caveat recorded:** the real search selects by utility, not at random. Whether
utility-selected supports carry over better or worse than random draws cannot be
determined without running the search, which this stage may not do.

## 8. Search policy and budget

Fresh search per fold under the `SIGMA_REC_ONE_SEED_PRIMARY_V2` family, adapted
mechanically to the fold basis. One seed per stratum. Support bound 1–12.
Shortlist cap 96 per constructor. **300 000 support evaluations per fold,
1 800 000 total**, frozen before any target access; no outcome-triggered
expansion. **The Epoch-1 frontier is not reused or re-ranked.** Two-seed remains
outside the primary protocol.

## 9. Utility, gates and baselines — unchanged

`U_rec` UNCHANGED: no tail penalty, Rank 1 unchanged, practical-equivalence
unchanged, range support **not** rewarded inside the utility. V3 unchanged
(`Delta_0 <= -0.01 AND Delta_1 <= -0.01`). V6 logic frozen now with the 0.01
practical-direction threshold and no era rescuing another. All six baselines
carried; hyperparameters re-estimated from `D_train` only, per fold; identical
protected rows for comparable methods.

## 10. Aggregation

Discharge is the inference unit; three blocks aggregated per discharge as frozen;
62 out-of-fold results, one per discharge, each from the support of the fold in
which it was held out. **In-fold development scores contribute nothing** to the
final metric.

## 11. Positive-result tiers

`FORMAL_PASS` — the frozen gates, exactly as written.

`CLEAN_DEMO_PASS` — `FORMAL_PASS` **and** `Delta_1 <= -0.05` **and** full
cross-fitted range support **and** no out-of-fold discharge above NRMSE 1.0
**and** both eras `MATERIAL_IMPROVEMENT` against B1.

The −0.05 threshold is **five times the frozen practical-equivalence floor**,
which S7.2 declared before any result existed as lying *below* any scientifically
meaningful difference. Derived from the floor, not from an outcome. Recorded as
context afterwards: S7.11 found no Epoch-1 support beat persistence by more than
0.0287, so this is a demanding standard, not a flattering one.

`CLEAN_DEMO_PASS` is a **reporting tier**. It cannot change the scientific gate
and cannot retrospectively fail a formal pass.

## 12. Support stability and the optional all-data support

Six supports are expected. Exact overlap, coordinate recurrence, constructor
recurrence and primitive-family recurrence are predeclared as **descriptive**
reports. **No minimum agreement is required and no exact-support gate is
created** — stable utility with non-unique supports is a legitimate outcome and
is consistent with the S7.9/S7.11 lesson.

The optional all-data descriptive representation is **permitted**, only after the
cross-fitted qualification is frozen, labelled
`FULL_OBJECT_DESCRIPTIVE_REPRESENTATION`, never called externally validated, and
unable to alter the verdict.

## 13. Claim boundary and stop rule

Claim type
`CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION_WITHIN_THE_FROZEN_62_DISCHARGE_OBSERVATIONAL_OBJECT`.
Five forms of wording are explicitly forbidden. `EPOCH2_IS_FINAL_QREC_ATTEMPT =
true`; failure closes `q_rec` as a qualified iterative case study with `q_desc` as
the positive headline. See `EPOCH2_CLAIM_BOUNDARY.md` and `EPOCH2_STOP_RULE.md`.

## 14. Paper utility

**`MEDIUM_HIGH`.** The seven-step story remains compact and the protocol is
explainable in a short supplementary section: six deterministic folds, one access
ordering, one threshold in two roles, unchanged gates. The reservation is the
one-in-five applicability estimate — a protocol that probably ends on a technical
gate is a weaker demonstration than one that ends on the science, even though
stopping honestly there would still be a legitimate result.

## 15. Files

5 Markdown (limit 20) · 2 CSV · 7 JSON · 5 manifests · 3 scripts.

## 16. Recommendation

**`READY_FOR_EPOCH2_SEARCH`**, with the applicability risk disclosed and
requiring human acknowledgement before E2.1 is launched.

Two decision points belong to the human, not to me:

1. **Accept `tau_train = 0.5`, or switch to 0.25** for roughly double the
   applicability odds on a basis half the size. I chose 0.5 on interpretability
   and recorded the alternative rather than optimising for odds.
2. **Accept that Epoch 2 will probably end on the applicability gate.** That is a
   legitimate outcome under the stop rule, but it should be a decision taken with
   open eyes rather than discovered in E2.1.

Discovery Epoch 2 not started. S7.12 remains paused.
