# S7.E2.0A — Predictor-side admissibility reconciliation: internal audit report

Stage **S7.E2.0A** · Freeze `D3D-SIR-S7.E2.0A-PREDICTOR-SIDE-ADMISSIBILITY-RECONCILIATION-V1`
Contract parent `S7.K2` · Protocol parent `S7.E2.0`

---

## 1. Executive verdict

**`FROZEN_READY_FOR_EPOCH2_SEARCH`** · 35/35 acceptance · protocol reconciliation
only: no search, no fit, no baseline, no target read.

The conceptual mismatch flagged in review is **confirmed**, and on
contract-internal grounds rather than on convenience. `E2_0A_PROTOCOL` becomes
authoritative for Epoch-2 execution; `E2_0_PROTOCOL_V1` is preserved byte-for-byte
as its historical parent.

## 2. Parent integrity

**S7.K2 29/29** and **S7.E2.0 22/22** artifacts reproduce byte-for-byte.
`PARENT_ARTIFACTS_MODIFIED = 0`. `E2_0_OVERWRITTEN = false`.

## 3. The mismatch — confirmed

E2.0 imposed *"held-out predictor ranges may not influence candidate filtering."*
That is appropriate to an inductive-transfer task. The frozen Epoch-2 claim is a
**finite-object** reconstruction claim. Two independent parts of the lineage show
the restriction was stronger than the contract asks:

**(a) The sibling rule is an application-time predicate.** S7.6R
`PARTIAL_MAP_ADMISSIBILITY.md`: a finally selected support containing a partial-map
coordinate *"must satisfy the **same** rule on each external local-calibration
block."* Denominator admissibility was never required to be forecastable from
development data — it is evaluated where the relation is applied. `P-RANGE` is its
sibling under the same partial-map semantics.

**(b) K2's own architecture presumed full-object applicability.** `K_REC_V2`'s
`coverage_policy` records `FULL_DOMAIN_RANGE_SUPPORT` as *"feasible
target-blindly"* with evidence of **3 451 full-domain atoms computed over all 62
discharges**, and its `A_rec_architecture_decision` reasons that *"a search
restricted to full-domain coordinates yields full-domain supports by
construction."*

E2.0 therefore imposed a blinding that the parent contract it was implementing did
not ask for. The mismatch is real, and the amendment is justified on claim
semantics and contract precedent — **not** on success odds.

## 4. Claim and guarantee

Claim type **unchanged**:
`CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION_WITHIN_THE_FROZEN_62_DISCHARGE_OBSERVATIONAL_OBJECT`.
Not strengthened; no inductive-transfer task substituted.

Guarantee tested: **no discharge's own target values influenced the support used
to reconstruct it.**

Principle: `PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION`.

## 5. `tau` — definition and status

```
E(c) = max( L − min(c_app), 0, max(c_app) − U ) / (U − L),   L = min(c_cal), U = max(c_cal)
```

Distance outside the observed calibration hull, in units of the calibration-range
width. **`τ = 1`, unchanged**: application values may extend beyond the hull by no
more than one complete calibration-range width.

Worked example, calibration range `[2, 6]`, width 4:

| application reaches | 2–6 | 7 | 8 | 10 | 11 |
|---|---|---|---|---|---|
| `E` | 0 | 0.25 | 0.50 | 1.00 | **1.25 → NOT APPLICABLE** |

`τ` is **not** a regression parameter, regularisation parameter, performance
threshold, learned constant, physical constant, confidence level, or train/test
tuning knob. It **is** an observational-applicability bound in `P_rec`. Degenerate
calibration handling unchanged.

## 6. `tau_train` — retired

`tau_train = 0.5` is **retired**, on **conceptual** grounds: predictor-side support
of the intended finite object may be instantiated from the predictor side of that
object, so a headroom margin was only ever needed under the stronger
predictor-blinded reading.

**No replacement training-only threshold** was created — not 0.25, not 0.40, not
under another name. There is exactly one threshold in the contract.

The E2.0 feasibility table (roughly 1-in-5 six-fold applicability) is **preserved
historically** at
`E2_0_protocol_and_resampling_freeze/manifests/APPLICABILITY_FEASIBILITY.json` and
is explicitly recorded as `HISTORICAL_CONTEXT_ONLY_NOT_JUSTIFICATION`.

## 7. Information roles

| | Role A — predictor-side | Role B — target-side |
|---|---|---|
| what | all admissible non-target predictor observations, all 62 | held-out targets excluded |
| may influence | `P-RANGE` applicability | nothing in fold `k`'s search |
| only source | — | `D_train⁽ᵏ⁾` targets |
| properties | target-blind, error-blind, performance-blind | cross-fitted |

Not target leakage: `density` remains unavailable to the held-out fold during
support discovery; the applicability calculation uses only non-target predictors,
frozen coordinate definitions, frozen block geometry and frozen `τ = 1`.

## 8. Candidate basis — verified against K2

| | |
|---|---|
| `C_E2_FULL_DOMAIN` | **3 451** of 10 778 |
| matches K2 freeze | **yes** |
| C0 / C1 / C2 / C3 / C5 / C6 / C7 | 51 / 18 / 1 488 / 382 / 8 / 965 / 539 |
| constructor counts match K2 | **yes** |
| different ontology generated | no |

Recomputed from the K2 frozen score matrix at `τ = 1`; listing at
`manifests/C_E2_FULL_DOMAIN.csv`; id-set hash recorded.

## 9. Closure property — verified, not assumed

Claim: any support assembled solely from `C_E2_FULL_DOMAIN` is
`FULL_DOMAIN_RANGE_SUPPORTED` by construction, because the support predicate is a
conjunction of coordinate predicates over the same cells.

Verified at support sizes **1, 2, 5, 8, 12**, 2 000 random draws each — **all pass**.

**Adversarial control:** 11 full-domain coordinates plus one non-full-domain
coordinate, 2 000 draws → **0.0** full-domain, exactly as expected. The check is
therefore not vacuous: a single unsupported coordinate always breaks a support.

## 10. Revised access order

Five **global pre-search** steps in which **no target value opens** (verify,
open all 62 predictors, instantiate `P-RANGE`, load and verify the 3 451, hash the
basis), then ten **per-fold** steps: expose `D_train` targets → search → `U_rec` →
select → **write and hash `C_k*`** → freeze estimators/baselines → open `D_test`
calibration targets → fit local coefficients → open `D_test` protected targets
**last** → score.

Held-out targets may never cause support reselection, coordinate replacement, a
`τ` change, a fold change, or a search extension.

## 11. `V-RANGE`

**Not deleted.** Expected to pass **by construction** for supports drawn only from
the certified basis. It must still be recomputed during execution as an
**integrity check**.

An unexpected failure is classified `PROTOCOL_OR_IMPLEMENTATION_INCONSISTENCY` and
must **stop execution for audit** — it must not be recorded as ordinary scientific
failure before the lineage is checked, because the closure property has now been
verified twice.

## 12. `A_rec` / `G_rec` / `P_rec`

`G_rec` unchanged · `A_rec` unchanged, the 7 327 locally partial atoms **not
erased** · `P_rec` unchanged from `K_REC_V2`. `C_E2_FULL_DOMAIN` is a subset of
`Coord(G_rec)` selected by the frozen `P_rec` predicate; it constrains the Epoch-2
**search frontier**, it does not redefine `A_rec`.

## 13. Everything else — unchanged

`U_rec` UNCHANGED · `V3` = `Δ₀ ≤ −0.01 AND Δ₁ ≤ −0.01` · `V6` threshold 0.01 ·
six baselines · 300 000 per fold / 1 800 000 total · one-seed, two-seed outside
the primary study · `CLEAN_DEMO_PASS` at `Δ₁ ≤ −0.05`, reporting tier only ·
`EPOCH2_IS_FINAL_QREC_ATTEMPT = true` · support-stability reporting · optional
all-data descriptive support · forbidden claim wording **not weakened**.

**The six outer folds are byte-identical to the frozen parent** — membership
checked discharge-by-discharge; sizes 11/11/10/10/10/10; every discharge held out
exactly once; no repartition, no new seed, no optimisation.

## 14. The epistemic cost — recorded, not hidden

E2.0's stricter rule would have tested **two** things on held-out data: whether the
target relationship transfers, **and** whether the support's predictor geometry
survives discharges whose ranges were never consulted. E2.0A tests **only the
first**; the second is now true by construction.

**A positive Epoch-2 result is therefore a weaker statement than E2.0 would have
produced.** This is written into the claim boundary and must appear in the
manuscript alongside any positive result, not only in the audit trail.

One consequence is worth stating plainly: under E2.0 the most likely failure was
the applicability gate. That route is now closed by construction, so **Epoch 2 will
succeed or fail on the science** — which is the point, and which also removes any
excuse that a technical gate ended the branch.

## 15. `I_q` audit

**No notation revision required.** `I_rec` is defined as `O_rec = I_rec(O)` — a
**variable-set** boundary whose six exclusion rules concern **ancestry relative to
the target**. It never governed which *observations* of an admitted variable are
available at which *stage*; in Epoch 1 that already lived in `P_rec`
(calibration-only preprocessing) and `V_rec` (block-local protection, external
sealing).

**Manuscript clarification recommended** (one sentence, no redefinition):

> The information boundary is transition-specific: observations admissible for
> coordinate construction or applicability need not be admissible for relation
> selection. In the reconstruction example, non-target observations across the
> finite scientific object determine range-support applicability, while held-out
> target values remain unavailable to support discovery.

## 16. Firewall

`target_reads = 0` · `model_error_reads = 0` · `residual_reads = 0` ·
`epoch1_performance_reads_for_decision = 0` · `epoch2_performance_reads = 0`,
asserted in code. No search, no fit, no baseline, no support selection.

## 17. Files

5 Markdown (limit 20) · 7 JSON · 3 manifests · 2 scripts.

## 18. Recommendation

**`READY_FOR_EPOCH2_SEARCH`.**

No further protocol work is needed, and none should be done: additional protocol
iteration before E2.1 would begin to look like tuning the rules until the answer
is agreeable. The amendment is narrow, justified on the contract's own precedent,
costs something that has been written down, and leaves every scientific gate and
the stop rule exactly where they were.

Epoch 2 not started. S7.12 remains paused.
