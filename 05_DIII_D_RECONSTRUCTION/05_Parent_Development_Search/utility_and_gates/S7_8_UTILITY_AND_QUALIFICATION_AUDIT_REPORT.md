# S7.8 — Utility and qualification rule operationalization: internal audit report

Stage: **S7.8** · Freeze: `D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1`
Parent: `D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2`

---

## 1. Executive verdict

**`FROZEN_READY_FOR_S7.9`.**

S7.8 instantiated the operational meaning of the already-frozen `U_rec` and
`V_rec` policies and stopped. It selected no representation, opened no external
value, ran no baseline, and executed no utility computation over `Ahat_rec`.

Twelve operational resolutions were required to make the inherited rules
executable. Each is a definition needed to run a frozen policy, each is
outcome-independent, and none alters an inherited quantity. **No
`UTILITY_SPECIFICATION_CONFLICT` was found**, and no inherited rule proved
mathematically impossible to execute.

Two findings are worth the reader's attention before S7.9:

- The Rank-2 `BLOCK_WORST` paired standard error **is** implementable without
  discretion (§8). The fallback the instruction permitted — dropping to a
  0.01-only floor — is **not invoked**.
- The canonical support identifier **cannot be parsed by splitting on the pipe
  character**. Four constructor families embed a pipe inside their own
  signatures, and a naive split mis-parses **71.6 %** of the frontier (§4).
  This is a live implementation hazard for S7.9 and is now a mandatory
  pre-computation checksum.

## 2. Parent verification

All thirteen required lineage entries were located, hashed and read.

| Stage | Freeze ID | Status |
|---|---|---|
| S7.1 | `D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1` | `FROZEN_WITH_QUALIFICATIONS` |
| S7.2 V1 | `…-RECONSTRUCTION-CONTRACT-PRETARGET-V1` | `FROZEN_READY_FOR_S7.3` |
| S7.2 V2 | `…-RECONSTRUCTION-CONTRACT-PRETARGET-V2` | `FROZEN_READY_FOR_S7.3` |
| S7.3 V1 historical | `…-TARGET-AND-INFORMATION-BOUNDARY-V1` | `FROZEN_READY_FOR_S7.4` |
| S7.4 V1 historical | `…-MATHEMATICAL-INTERPRETATION-V1` | `TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED` |
| S7.3R V2 | `…-SOURCE-RESOLUTION-V2` | `FROZEN_READY_TO_RETRY_S7.4` |
| S7.4 V2 | `…-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2` | `FROZEN_READY_FOR_S7.5` |
| S7.5 V1 | `D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1` | `FROZEN_READY_FOR_S7.6` |
| S7.5H V1 | `…-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1` | `FROZEN_WITH_QUALIFICATIONS` |
| S7.6 V1 historical | `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1` | `FROZEN_READY_FOR_S7.7` |
| S7.6R V2 | `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2` | `FROZEN_WITH_QUALIFICATIONS` |
| S7.7 V1 historical | `…-FROZEN-SEARCH-POLICY-AND-EXPLORED-FRONTIER-V1` | `BLOCKED_SEARCH_BUDGET` (preserved as audit history) |
| S7.7R V2 **primary** | `…-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2` | `FROZEN_WITH_QUALIFICATIONS` |

**All 41 artifacts recorded in the S7.7R manifest reproduce byte-for-byte from
disk.** Required confirmations:

| Claim | Verified |
|---|---|
| `target == density` | ✔ |
| `|Ahat_rec| == 162 845` | ✔ (registry rows and unique ids) |
| singleton supports `== 10 778` | ✔ |
| multivariate supports `== 152 067` | ✔ |
| support sizes `== 1…12` | ✔ (histogram identical to the S7.7R freeze) |
| external cohort `== 42` sealed | ✔ (24 earlier + 18 later) |
| search policy `== ONE_SEED_PRIMARY` | ✔ (`SEEDS_PER_STRATUM 2 → 1`, only seed multiplicity changed) |
| two-seed sensitivity `== NOT_EXECUTED` | ✔ |
| `B0/B1/B1A/B2/B3/H0 == NOT_RUN` | ✔ |

Additional integrity checks: the two per-cell NRMSE arrays cover exactly
152 067 + 10 778 = 162 845 rows over an identical 60-cell axis with zero id
overlap; all 9 770 700 cells are finite; the 20 discharges in the cell axis
match the frozen development cohort exactly.

**Verdict: `ZERO_SUBSTANTIVE_DRIFT`.**

## 3. Stage semantics

The S7.2 division is preserved exactly:

| Stage | Owns |
|---|---|
| **S7.8** | execution **rules** |
| S7.9 | instantiated utility computation on development |
| S7.10 | qualification-gate evaluation |
| S7.11 | sensitivity |
| S7.12 | `Q_rec*` |

S7.9 was **not** moved into S7.8. Concretely: no `FIT`, `BLOCK_WORST`,
`SHOT_P90`, `COND_*`, `BOOT_SELECTION_FREQ` or `FOLD_SELECTION_FREQ` value was
computed for any member of `Ahat_rec`. The frozen NRMSE arrays were opened only
to check shape, finiteness and identity.

To demonstrate executability without executing selection, the algorithm was dry
run on a **synthetic fixture** of the correct shape
(`manifests/ALGORITHM_DRY_RUN.json`). That fixture contains no frontier value.

## 4. Authoritative contract reconciliation

Three pieces of superseded wording were located and are recorded rather than
silently repeated.

| Location | V1 wording | Status |
|---|---|---|
| `UTILITY_AND_QUALIFICATION_POLICY.md`; `K_REC_PRE.json` | practical equivalence = within 1 SE **AND** within 0.01 | **`SUPERSEDED_BY_S7.2C_C01`** |
| `UTILITY_AND_QUALIFICATION_POLICY.md` gate V6; `STATISTICAL_INFERENCE_PLAN.md` item 10 | report separately for **35 earlier / 27 later** | **`SUPERSEDED_FOR_V6_BY_S7.2C_C07`** |
| `UTILITY_AND_QUALIFICATION_POLICY.md` gate V3 | "beats B0 and B1 in the predeclared aggregate sense" | defined by `S7.2C C-06` |

**A live implementation hazard was found in the frontier identifiers.** The
canonical `support_id` joins atoms with a pipe, but the C4/C6/C7/C8 signatures
`PHASE(i|j)`, `LEVEL_RATE(i|j)`, `RATE_OVER_LEVEL(i|j)` and `LEVEL_OVER_RATE(i|j)`
contain a pipe *inside their own parentheses*. A naive `split('|')` returns the
wrong atom count for **116 608 of 162 845 rows (71.6 %)** — and, because C6 and
C7 are exactly the families under scrutiny in §13, the corruption would fall
disproportionately on them.

Resolution: atom membership is recovered by splitting at **parenthesis depth 0
only**, and the parse must reproduce registry `support_size` for all 162 845
rows as a **mandatory pre-computation checksum**. Verified in S7.8; S7.9 must
re-verify.

## 5. Practical equivalence

Authoritative and instantiated as:

```
delta_equiv = max(SE_delta, 0.01)                        # NRMSE units
A ~ B  iff  |NRMSE_A − NRMSE_B| ≤ delta_equiv
SE_delta = sd(delta_s, ddof=1) / sqrt(20)
delta_s  = mean_b NRMSE_{A,s,b} − mean_b NRMSE_{B,s,b}
```

Floor immutable at 0.01. No epsilon. No raw-RMSE interpretation. Blocks are
aggregated **within** each development discharge before the difference is taken,
so the inferential unit is the discharge (gate V8).

**Resolution OR-02.** `E_fit` is defined by pairwise comparison **against the
Rank-1 best**, not as a transitive equivalence class. Transitive closure would
be a different — and strictly larger — object, and the parent wording does not
license it. The best candidate is always a member, since
`SE_delta(best, best) = 0` and `|0| ≤ 0.01`.

**Resolution OR-11.** A candidate with any non-finite cell takes `FIT = +inf`
and cannot enter `E_fit`; it is never re-labelled inadmissible. Zero such
candidates exist in the frozen frontier, so the rule is defensive.

## 6. Primary estimator

Frozen as **`DEVELOPMENT_RELATION_OLS_V1`**. The inherited contract permitted
"ordinary least squares, or ridge with a development-selected penalty"; S7.8
narrows that to OLS. This is a narrowing of a permission, not a change of rule.

Reasons recorded prospectively: support size ≤ 12; the claim must be
attributable to the representation rather than estimator complexity; OLS is
transparent and hyperparameter-free; it is already the frozen search proxy;
S7.7R found zero rank-deficient explored designs; and no hyperparameter
selection means no selection discretion.

**This is an estimator-policy freeze, not a performance comparison. No ridge
fit was run to decide it.** Ridge may return later only as a separately
labelled *conditioning* sensitivity, justified by conditioning evidence on
development data, never chosen on performance, and granted equally to B2.

Procedure: calibration-only standardization → unchanged application to protected
rows → fitted intercept → affine OLS → discharge/block-local coefficients, never
shared. `sd ≤ 0` uses an exact divisor of `1.0`, inherited verbatim from S7.7R;
no epsilon is introduced.

## 7. Rank 1 — fit

```
FIT(C) = mean over 20 development discharges of ( mean over blocks A,B,C of NRMSE_{s,b}(C) )
E1     = { C : |FIT(C) − FIT_best| ≤ max(SE_delta(C,best), 0.01) }
```

This is the frozen practical-equivalence set, **not** a top-*K* rule. No
candidate outside `E1` advances to Rank 2. S7.9 executes it; S7.8 froze it.

Raw RMSE in physical units is retained for reporting and is not the primary
utility measure.

## 8. Rank 2 — stability

Operationalized without a weighted score:

```
BLOCK_WORST(C) = max over b of ( mean_s NRMSE_{s,b}(C) )
SHOT_P90(C)    = 90th percentile over the 20 values NRMSE_s(C)
```

applied lexicographically inside `E1`: minimize `BLOCK_WORST` under practical
equivalence, then minimize `SHOT_P90` exactly.

**Parent-conflict check (required by the instruction).** The section-11
operationalization was compared against the only machine-readable parent
definition, `K_REC_PRE_V2.json → U_rec.criteria_in_order`, and against
`UTILITY_AND_QUALIFICATION_POLICY.md`. The parent fixes the criterion's *name*,
its *rank* and its *data scope* ("aggregated across development discharges and
all three predeclared temporal blocks"); it supplies no stronger operational
formula. All three parent constraints are honoured. **No conflict; nothing was
overridden.**

**Resolution OR-03 — the paired SE is implementable.** Define
`b_star(C) = argmax_b (mean_s NRMSE_{s,b}(C))`, ties broken by the earliest
block in the canonical order `A < B < C`. Let each candidate contribute its
**own** worst block:

```
d_s(A,B) = NRMSE_{s, b_star(A)}(A) − NRMSE_{s, b_star(B)}(B)
```

Then `mean_s d_s(A,B) = BLOCK_WORST(A) − BLOCK_WORST(B)` **exactly**, because
`BLOCK_WORST(C) = mean_s NRMSE_{s, b_star(C)}(C)` by definition of the argmax.
The paired discharge-level differences therefore average to precisely the
candidate-level quantity under comparison, so
`SE_delta_worst = sd(d_s, ddof=1)/sqrt(20)` is the standard error *of that
difference*. Nothing is chosen; `b_star` is determined by the frozen formula and
a canonical tie-break.

The identity was verified numerically over all candidate pairs in the synthetic
dry run: maximum absolute deviation **2.67 × 10⁻¹⁶**.

**Consequence:** the fallback permitted by the instruction — "use the fixed
absolute 0.01 NRMSE floor only for `BLOCK_WORST` equivalence and record that
qualification" — is **`NOT_REQUIRED`** and is not invoked. No new tunable
threshold was introduced.

**Resolution OR-04.** The percentile estimator is frozen as
`numpy.percentile(..., method='linear')` for both `SHOT_P90` and `COND_P90`.
Percentile conventions differ; fixing the library default makes the quantity
reproducible. It was fixed before any value was computed and not chosen to
favour an outcome.

## 9. Rank 3 — parsimony

Minimize `|C|`, then `ACTIVE_TERMS(C)`. Intercept not counted. No magnitude
threshold, no coefficient-significance test, no p-value pruning.

**Resolution OR-05.** Coefficients are discharge/block local, so "active" needs
a candidate-level integer. A column is **ACTIVE** iff its OLS coefficient is not
exactly `0.0` in **at least one** of the 60 calibration fits; `ACTIVE_TERMS(C)`
counts active columns. The union is the conservative reading — a term counts as
used if it is used anywhere — and requires no threshold.

Under full-rank OLS an exactly-zero coefficient essentially never occurs, so in
practice `ACTIVE_TERMS(C) = |C|` and the second subcriterion is non-binding,
exactly as the parent anticipates.

## 10. Rank 4 — conditioning

`Z_{s,b}(C)` is the **calibration rows** of the cell, columns standardized by
that cell's calibration mean and sd, intercept excluded.

**Resolution OR-06.** Because standardization subtracts the calibration mean,
`Z` restricted to the calibration rows is already exactly column-centred, so the
"centred design" and "standardized design" readings coincide and no ambiguity
survives.

```
kappa_{s,b}(C) = sigma_max(Z) / sigma_min(Z)     # singular values
sigma_min == 0 → kappa = +inf
COND_MEDIAN = median over 60 cells of log10(kappa)
COND_P90, COND_MAX also reported
```

Order: `COND_MEDIAN`, then `COND_P90`, then `COND_MAX`.

**Resolution OR-07.** The normal-equation condition number is explicitly
forbidden; the dry run confirms it equals `kappa²` to a ratio of exactly 1.0.
`log10(+inf)` propagates; `COND_MEDIAN` remains defined unless at least half the
cells are infinite.

Recorded in advance: for `|C| = 1` the design has a single singular value, so
`kappa = 1` and `log10(kappa) = 0` exactly. Singletons are therefore perfectly
conditioned by construction. This is an arithmetic consequence of the frozen
definition, noted now rather than discovered as a surprise at Rank 4.

**No condition-number cutoff is introduced.** Conditioning ranks candidates; it
never declares one inadmissible. This is distinct from the S7.7R search
rank-deficiency rule (eigenvalues of the centred Gram, setting `J_search = +inf`
and labelling `SEARCH_PROXY_RANK_DEFICIENT`, never inadmissibility). Different
quantities, different purposes; neither was changed.

## 11. Rank 5 — support stability

Discharge bootstrap: **1000** replicates, 20 discharges with replacement, seed
**2026090501**, `numpy.random.default_rng`, replicates drawn in sequence.
Discharge indices only are resampled; blocks are never resampled. Multiplicities
enter every discharge-level aggregation as integer weights (verified: unit
weights reproduce the plain computation exactly).

Fold perturbation: exactly three — omit A, omit B, omit C — recomputing Ranks
1–4 over the remaining two blocks (40 cells).

```
BOOT_SELECTION_FREQ(C) = fraction of 1000 replicates in which C is the Rank-4 winner
FOLD_SELECTION_FREQ(C) = fraction of 3 perturbations in which C is the Rank-4 winner
```

**Resolution OR-08.** "Rank-4 winner" = the canonical-first element of `E4`
under that replicate, i.e. the unique candidate Ranks 1–4 plus the canonical
tie-break resolve to. No circularity: the winner is a function of Ranks 1–4
only.

Ordering: maximize `BOOT_SELECTION_FREQ`, then `FOLD_SELECTION_FREQ`, then
canonical support id. **No pass/fail threshold**; stability is a ranking
quantity, not a gate. The replicate count may not be reduced after inspecting
outcomes.

Labelled throughout as an **analyst-defined qualification procedure**. `E` is
not instantiated, so no numerical perturbation is described as observational
uncertainty and no measurement-error weight enters `U_rec`.

**Resolution OR-12.** The 1000-replicate Rank-5 procedure is distinct from the
`≥ 10 000`-replicate paired discharge bootstrap that
`STATISTICAL_INFERENCE_PLAN.md` requires for gate confidence intervals at S7.10
(`K_REC_PRE_V2 → V_rec.bootstrap_replicates = 10000`). Different procedures,
different stages, different purposes. Both stand; the parent count is not
modified.

## 12. Deterministic S7.9 selection algorithm

```
E0 = Ahat_rec                                    162 845
E1 = Rank-1 practical-fit-equivalent set
E2 = Rank-2 stability survivor set
E3 = Rank-3 minimum-parsimony survivor set
E4 = Rank-4 best-conditioning survivor set
E5 = Rank-5 support-stability survivor / final deterministic candidate
```

Canonical support id is the final tie-break. Every elimination is recorded with
`support_id, support_size, rank_eliminated, criterion, reason,
comparison_quantity, candidate_value, reference_value, threshold_applied`.

The dry run confirms the pipeline is deterministic across repeated runs, that
survivor sets nest monotonically `E4 ⊆ E3 ⊆ E2 ⊆ E1`, and that the bootstrap
stream is reproducible from the frozen seed.

**S7.8 did not execute this algorithm. S7.9 owns execution.**

Preconditions for reusing the S7.7R per-cell arrays — hashes, estimator
equivalence, metric equivalence, support identity, block identity — are recorded
in `manifests/S7_9_REUSE_PRECONDITIONS.json`. All five were verified here; S7.9
must re-verify at execution time, or recompute.

## 13. C6/C7 carry-forward

Carried forward, **not acted on**:

| | C6 `LEVEL_RATE` | C7 `RATE_OVER_LEVEL` |
|---|---|---|
| admissible atoms | 3 776 (35.03 %) | 2 301 (21.35 %) — together **56.38 %** |
| seed share | 27.6 % | 15.7 % |
| explored participation | 51.1 % | 36.8 % |
| **retained participation** | **4.63 %** | **2.65 %** |
| in the lowest-`J` support at any size 1…12 | none | none |

**`NO_CONSTRUCTOR_FAMILY_PRUNING` is declared.** C6 and C7 are not removed from
`Ahat_rec`, and no penalty is attached to them. If the utility procedure
naturally eliminates them, that is reported later as an outcome. If a C6/C7
candidate survives, it is accepted.

This is precisely why navigation and utility are separate stages: a family that
the performance-guided expansion abandoned during navigation retains full
standing under the utility rule.

## 14. ECE multiplicity carry-forward

Carried forward, **not acted on**: ECE seed opportunity was balanced to 30.7 %
against an atom-ancestry share of 84.2 %, yet ECE ancestry appears in 85.4 % of
retained-path supports and **100 %** of the lowest-navigation-score supports.

No ECE penalty, family quota, diversity bonus or family balancing enters
`U_rec`. The fairness condition was on **opportunity**, and it was met; what the
performance-guided expansion did with that balanced opportunity is an empirical
development-search outcome, reported as found. Utility now evaluates the found
representations as they are.

## 15. Uncalibrated coordinates

`pcbcoil` and `pcdiamag3` are recorded in S7.1 as uncalibrated digitiser output
for which no unit exists. Coordinates containing them as C0 primitive levels
**remain valid** if already in `Ahat_rec` and are **not removed**.

The label `UNCALIBRATED_SIGNAL` is carried into coefficient interpretation: if a
selected representation contains one, its fitted coefficient has **no certified
physical-dimensional interpretation**. This is an interpretation qualification,
not a selection exclusion.

The point is live rather than hypothetical: `ID(pcdiamag3)` appears in the
lowest-navigation-score support at **11 of the 12 sizes** (every size except
`m = 1`). A representation containing it is a realistic S7.9 outcome, and the
interpretation qualification must travel with it rather than be recalled
afterwards.

## 16. Qualification gates

`V_REC_OPERATIONAL_V1.json` records, for each of V1–V10: authoritative
definition, mandatory flag, authoritative corrections, stage owner, current
status, evidence required and failure meaning. Mandatory: V1, V2, V3, V4, V5,
V6, V7, V8, V10. Non-mandatory: V9.

Statuses at S7.8 are confined to `PROTOCOL_VERIFIED`, `PENDING_S7.9`,
`PENDING_S7.10`, `PENDING_S7.11`. **No external gate is marked `PASS`.**
V3, V4 and V5 are **not evaluated**; V6 is **not evaluated**; V9 belongs to
S7.11 and remains non-mandatory.

Mandatory failure meaning is recorded explicitly: a mandatory gate failure
prevents presenting `Q_rec` as a successful structural-transfer result.

## 17. V6 correction

The gate operates on the **external cohort**: **24 earlier / 18 later**,
total 42. The V1 wording "35 earlier / 27 later" refers to *parent-object*
counts and is recorded as **`SUPERSEDED_FOR_V6_BY_S7.2C_C07`**. It is not
repeated as current anywhere in the S7.8 artifacts. Verified independently from
`COHORT_PARTITION.json`, which reports `external.by_era = {earlier: 24,
later: 18}`.

## 18. Baseline ownership

`B0` calibration mean · `B1` persistence · `B1A_AR1` diagnostic · `B2` raw ridge
· `B3` `HistGradientBoostingRegressor` · `H0_RAW_HARDENED` diagnostic. Carried
forward as definitions. **None run in S7.8.**

S7.9 freezes the complete instantiated configurations; S7.10 evaluates them
externally. V3 requires actual skill against B0 and B1; V4 requires *fair*
comparison with B2 and B3 and does **not** require beating them. `S_pers`
remains required reporting and does **not** guide S7.9 selection.

## 19. Search-depth sensitivity

`TWO_SEED_SEARCH_DEPTH_SENSITIVITY` remains `DECLARED_OPTIONAL` and
`NOT_EXECUTED`. It was not run, and **no outcome trigger was defined** — it may
later be executed as a separately labelled S7.11 sensitivity regardless of
whether the primary result is good or bad, and it may never replace the one-seed
primary frontier.

## 20. Search boundary

Every utility and qualification artifact carries
`selection_domain = AHAT_REC_DENSITY_ONE_SEED_V2` and
`global_optimality_claim = false`.

`Ahat_rec` covers ≈ 3.19 × 10⁻³³ % of the unconstrained size-1…12 support space.
Approximately **5.1 × 10³⁹** admissible support combinations remain
`ADMISSIBLE_UNSEARCHED`, and **no negative conclusion attaches to them**. The
candidate S7.9 selects will mean *selected from the frozen explored frontier* —
not *best representation in `A_rec`*.

## 21. External firewall

| | |
|---|---|
| external signal values opened | **0** |
| external target values opened | **0** |
| external cohort state | `SEALED` |
| baselines run | **0** |
| search rerun | no |
| `Ahat_rec` / `A_rec` / `G_rec` modified | no |
| two-seed sensitivity executed | no |
| `C*` selected | **no** |
| final support frozen | no |
| S7.9 started | **no** |

Development-side reads were confined to shape, finiteness and identity checks on
the frozen arrays plus the synthetic dry-run fixture. **No utility quantity was
computed over `Ahat_rec`.** `FIREWALL_INTACT`.

Because no outcome was produced, no outcome-based revision was possible — the
strongest available guarantee for §24 of the stage instruction, recorded in
`manifests/OUTCOME_BASED_REVISION_AUDIT.json`.

## 22. Files

6 Markdown (limit 20, preference ≤ 8) · 9 policy JSON · 7 manifests · 3 scripts.

| Kind | Files |
|---|---|
| Markdown | `README.md`, `S7_8_UTILITY_AND_QUALIFICATION_RULES_FINAL.md`, `S7_8_UTILITY_AND_QUALIFICATION_AUDIT_REPORT.md`, `DEVELOPMENT_SELECTION_PROTOCOL.md`, `QUALIFICATION_GATE_PROTOCOL.md`, `SUPPORT_STABILITY_PROTOCOL.md` |
| Policies | `U_REC_OPERATIONAL_V1.json`, `V_REC_OPERATIONAL_V1.json`, `estimator_policy.json`, `practical_equivalence_policy.json`, `stability_metric_policy.json`, `conditioning_policy.json`, `support_stability_policy.json`, `development_selection_algorithm.json`, `gate_stage_ownership.json` |
| Manifests | `PARENT_FREEZE_VERIFICATION.json`, `ACCESS_AUDIT.json`, `ALGORITHM_DRY_RUN.json`, `S7_9_REUSE_PRECONDITIONS.json`, `SEMANTIC_SEPARATION.json`, `CARRY_FORWARD_FINDINGS.json`, `OUTCOME_BASED_REVISION_AUDIT.json` |
| Scripts | `s7_8_a_verify_parents.py`, `s7_8_b_build_policies.py`, `s7_8_d_algorithm_dryrun.py`, `s7_8_c_freeze.py` |

## 23. Recommendation for S7.9

**`READY_FOR_S7.9`.**

Before computing anything, S7.9 must:

1. re-verify the five array-reuse preconditions
   (`manifests/S7_9_REUSE_PRECONDITIONS.json`);
2. run the **canonical-parse checksum** — the depth-aware split must reproduce
   registry `support_size` for all 162 845 rows. A naive pipe split silently
   corrupts 71.6 % of the frontier and would fall hardest on exactly the C6/C7
   families §13 protects;
3. execute `E0 → E5` in order, recording the full survivor set and elimination
   ledger at every rank;
4. hash the selected support, the estimator and all remaining model state
   **before** any external access, which is the precondition for V5;
5. freeze the instantiated B0/B1/B1A/B2/B3/H0 configurations without running
   them.

S7.9 must not open the external cohort, must not run any baseline, and must not
alter any quantity frozen here.
