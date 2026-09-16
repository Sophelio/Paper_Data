# S7.7 — Frozen search policy and explored frontier: internal audit

**Freeze:** `D3D-SIR-S7.7-FROZEN-SEARCH-POLICY-AND-EXPLORED-FRONTIER-V1`
**Status:** `BLOCKED_SEARCH_BUDGET` · 2026-09-04
**Acceptance:** 34/34 reached · 6 not reached (gated by the block)

---

## 1. Executive verdict

`Sigma_rec` is **fully specified, frozen and hashed**. `Ahat_rec` is **not
constructed**.

The stage stopped at the §16 search-budget preflight. The deterministic policy
of §§12–15 projects **363,900** candidate support evaluations at maximum and
**346,484** at a strict lower bound, against `MAX_SUPPORT_EVALUATIONS =
300,000`. §16 requires an unconditional STOP before target access in that case,
with no silent truncation and no policy adjustment. That is what happened.

```
archives opened            0
density values opened      0
external values opened     0
atoms scored               0
baselines run              0
```

Everything metadata-only is complete: parent verification, the two pre-search
contract completions, stratification of all 10,778 atoms, the full policy
specification, the §13 cap-sufficiency gate, and the opportunity-side
multiplicity audit. Only the budget decision is outstanding, and it is a human
decision by construction.

## 2. Parent verification

`PARENTS_VERIFIED` — **0 hash drift** across all eleven lineage records: S7.1,
S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1, S7.3R V2, S7.4 V2, S7.5, S7.5H, historical
S7.6 V1, and S7.6R hardened V2.

All 19 substantive checks pass: `A_REC_DENSITY_HARDENED_V2` authoritative,
`C_rec_hard^atom` = 10,778, symbolic 23,861, target `density` in `m^-3`,
external cohort 42 sealed, **C4 = 0**, **C8 = 0**, family counts
66/59/2080/2457/0/39/3776/2301/0, support bound 1–12, denominator rule hash
`6d4004eb…` unchanged, `T_REC_V1` unchanged, `P_hard` = 70, historical S7.6 V1
preserved, search priority not yet assigned, estimator not yet run.

## 3. Pre-search contract completion

Both items frozen in stage A, which opens no archive, and hashed at
`1b8df4c0…` — before any density value could be opened by any stage.

**`S_PERS_V1`** — required reporting.
`S_pers(M,s,b) = 1 − MSE(M,s,b)/MSE(B1,s,b)` on identical protected samples;
`UNDEFINED_ZERO_PERSISTENCE_ERROR` when the denominator is zero, **no epsilon**;
discharge level `1 − mean_b MSE(M,s,b) / mean_b MSE(B1,s,b)`; cohort summaries
operate on discharge-level values. It does **not** replace frozen NRMSE, does
**not** change V3 — whose mandatory gate remains exactly the already-frozen
paired NRMSE condition — and was **not** used to guide search.

**`B1A_AR1`** — diagnostic baseline, required to report.
Calibration-interval OLS `y_k = a + φ y_{k−1} + ε_k`; on the protected block
initialise with the final calibration target value and predict recursively;
never update the recursion with protected target values; `a` and `φ` frozen over
that block. Lag order 1, no additional lags, no hyperparameter selection, no
teacher forcing. Not a replacement for B1 persistence, not added to mandatory V3
thresholds.

**Neither baseline was run.** Both belong to S7.9/S7.10 with B0–B3 and
`H0_RAW_HARDENED`.

## 4. Pre-value policy freeze

`SEARCH_POLICY_PREVALUE.json`, sha `a97e690e414da7a0…`, frozen in stage B, which
also opens no archive. It contains every decision of §§5–15: the multiplicity
statement, the stratum definition and role semantics, `SEARCH_PROXY_OLS_V1`,
`J_search`, the atomic-scoring scope, within-stratum ranking, the 96-atom
constructor cap and its interpretation, the seed and proposal rules, the
raw-only lane, the explored/unsearched definitions, the no-selection and
no-baseline rules, and the external seal.

The ordering is structural, not a matter of discipline: **stages A and B contain
no data-loading code path at all.** The scoring stage was never reached, so the
hash cannot have been influenced by any value.

## 5. Target-access firewall

**Not reached.** No density value was opened. The first target-dependent
operation of the q_rec pipeline (§10 atomic scoring) has not occurred.

## 6. Search strata

All 10,778 atoms assigned to **exactly one** of **127** active strata, from
frozen metadata alone. No atom carries multiple counting memberships.

| constructor | atoms | strata | signature |
|---|---|---|---|
| C0 | 66 | 7 | `(family_i)` |
| C1 | 59 | 5 | `(family_i)` |
| C2 | 2 080 | 28 | `{family_i, family_j}` unordered |
| C3 | 2 457 | 28 | `(numerator \| denominator)` |
| C5 | 39 | 4 | `(family_i)` |
| C6 | 3 776 | 35 | `(level \| rate)` |
| C7 | 2 301 | 20 | `(rate \| denominator level)` |

Two strata contain a single atom. C4 and C8 have no active strata.

Scientific-family reach across strata: ECE 39, CER 39, magnetics 39, density-aux
29, NBI 28, gas 28, filterscope 17. (Sums exceed 127: a pairwise stratum touches
two families.)

## 7. Atomic navigation scoring

**Not reached.** `SEARCH_PROXY_OLS_V1` and `J_search` are frozen but were never
executed. 0 of 10,778 atoms scored.

The specification is complete: calibration-only standardisation applied
unchanged to protected predictors, affine OLS via
`numpy.linalg.lstsq(..., rcond=None)`, never fitted jointly across discharges,
frozen NRMSE against `std(y_cal, ddof=0)`, rank deficiency flagged
`SEARCH_PROXY_RANK_DEFICIENT` with navigation score `+∞` and **explicitly not**
a declaration of scientific inadmissibility.
`J_search(C) = mean_s mean_b NRMSE_{s,b}(C)` over the 20 development discharges,
with no parsimony, conditioning, family-bonus, baseline-skill, or persistence
term, and canonical-ID tie-breaking.

## 8. Constructor-balanced shortlist

Structure fixed and gate passed; membership not instantiated (it requires
within-stratum ranks).

Projected sizes: C0 66, C1 59, C2 96, C3 96, C5 39, C6 96, C7 96 — **548**
total, against `MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION = 96`.

**§13 sufficiency gate: PASS.** The largest per-constructor stratum count is 35
(C6), well under 96, so round 1 of the round-robin gives every nonempty stratum
at least one slot. No STOP on this ground.

## 9. Seed registry

**Not instantiated.** Seeds are the top two atoms *by within-stratum rank*,
which requires `J_search`. The seed **count** is metadata-determined: **252**
main-lane seeds (`Σ_strata min(2, n_atoms)`) and **14** raw-only-lane seeds.

## 10. Greedy search

**Not executed.** The rule is frozen: grow each seed over `m = 2…12`; at each
step every stratum represented in the shortlist proposes exactly one atom — its
highest-ranked shortlisted atom not already in the support; discard only
extensions violating frozen `Φ_set`; take the lowest `J_search`, tie-broken by
canonical support ID. Opportunity set stratum-balanced, expansion choice
performance-guided.

## 11. Raw-only control lane

**Not executed.** `C0_ONLY_GREEDY` is frozen: the 66 admissible C0 atoms, seven
scientific-family strata, top two per family as seeds (14), same greedy rule,
support ≤ 12. Its purpose — guaranteeing compact raw-only representations in the
frontier — stands. It is **not** B2; B2 remains the frozen full-information raw
Ridge comparator and was not run.

## 12. Search budget — **the block**

```
atomic scoring                                                10,778
main lane      252 x 11 x 127                             =  352,044
raw-only lane   14 x 11 x   7                             =    1,078
maximum projected                                            363,900
strict lower bound                                           346,484
MAX_SUPPORT_EVALUATIONS                                      300,000
overrun: 63,900 at maximum, 46,484 at strict lower bound
```

The strict lower bound assumes the most favourable stratum exhaustion the policy
allows — that at proposal time for size `m` each of the `m−1` atoms already in
the support has exhausted a distinct stratum. **It still overruns.** No
execution of this policy can come in under 300,000, so the block does not turn
on which reading of "maximum projected" is taken.

The binding term is the 127 proposals per growth step, and it is
metadata-determined: round 1 of the round-robin gives every stratum a slot, so
all 127 strata propose at every step.

Remedies were **computed and not chosen** — choosing is a policy change, and
policy changes belong to the human, prospectively:

| option | max projected | fits |
|---|---|---|
| `SEEDS_PER_STRATUM = 1` | 188,736 | yes |
| `SEEDS_PER_STRATUM = 2` (current) | 363,900 | no |
| raise `MAX_SUPPORT_EVALUATIONS` ≥ 363,900 | 363,900 | redefines the gate |

Non-levers, with reasons, are recorded in `search_budget_block.json`: lowering
the 96 cap (proposals scale with strata, not atoms), reducing the support bound
(forbidden), counting deduplicated supports (not computable from metadata, so it
cannot certify the budget *before* target access), and pruning coordinates
(inverts `ADMISSIBLE ≠ PRIORITIZED`).

## 13. Explored frontier

**`Ahat_rec` is NOT CONSTRUCTED.** Cardinality 0. No support of any size was
evaluated. There is no lowest-`J_search` support, no retained path, and no
frontier registry, because nothing was scored.

Stating this plainly matters more than producing a placeholder: an empty
`Ahat_rec` means the entire admissible universe remains `ADMISSIBLE_UNSEARCHED`.
**No negative scientific claim of any kind may be made about any coordinate or
support.**

## 14. Multiplicity audit

§§22A and 22B are computable from metadata and were computed. §§22C–E require
the search to run and are recorded as not reached.

| family | primitives | atom ancestry | projected seed share | amplification removed |
|---|---|---|---|---|
| **ECE** | 33 | **0.842** | **0.310** | **−0.532** |
| CER | 14 | 0.347 | 0.310 | −0.037 |
| NBI | 10 | 0.144 | 0.222 | +0.078 |
| gas | 4 | 0.097 | 0.222 | +0.125 |
| magnetics | 4 | 0.071 | 0.310 | +0.238 |
| filterscope | 3 | 0.045 | 0.135 | +0.090 |
| density-aux | 2 | 0.041 | 0.222 | +0.181 |

The §22 success criterion — *initial search opportunity is not proportional to
raw atomic multiplicity* — is **met by construction**, demonstrably and before
any value is read. ECE falls from 84.2% of atomic ancestry to 31.0% of projected
seed opportunity.

Whether ECE still dominates *after* equalized opportunity is **unknown and
unknowable from this stage**, because that question is answered by retained
paths and no path was run.

## 15. Constructor audit

| constructor | atoms | atom share | strata | shortlist | shortlist share | seeds | seed share |
|---|---|---|---|---|---|---|---|
| C0 | 66 | 0.006 | 7 | 66 | 0.120 | 14 | 0.056 |
| C1 | 59 | 0.005 | 5 | 59 | 0.108 | 10 | 0.040 |
| C2 | 2 080 | 0.193 | 28 | 96 | 0.175 | 56 | 0.222 |
| C3 | 2 457 | 0.228 | 28 | 96 | 0.175 | 55 | 0.218 |
| C5 | 39 | 0.004 | 4 | 39 | 0.071 | 7 | 0.028 |
| C6 | 3 776 | 0.350 | 35 | 96 | 0.175 | 70 | 0.278 |
| C7 | 2 301 | 0.213 | 20 | 96 | 0.175 | 40 | 0.159 |

C6's 35.0% of atoms becomes 17.5% of shortlist slots; C0's 0.6% of atoms becomes
12.0%. Explored-support participation is not reached.

**C4 and C8:** `DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS /
ZERO_SEARCH_OPPORTUNITY`. This is an inherited S7.6R admissibility outcome, not
a search exclusion, and it was not rescued, shifted, or bounded.

## 16. Searched versus unsearched boundary

```
admissible atomic coordinates               10,778
Ahat_rec size-1 supports                         0
unique multivariate supports scored              0
total unique supports in Ahat_rec                0
```

Every admissible support — of every size — is `ADMISSIBLE_UNSEARCHED`. The terms
*global optimum*, *exhaustive search* and *complete search* do not apply and are
not used.

## 17. External firewall

External signal values **0**, external target values **0**, external discharges
opened **0**. The 42-discharge external cohort remains sealed through S7.9. No
archive of any kind was opened by this stage.

## 18. Files

4 Markdown, 4 CSV, 5 JSON, 3 scripts, 4 manifest records — hashed in
`S7_7_FREEZE.json` (the freeze and acceptance files are self-referentially
excluded).

**`S7_7_SEARCH_POLICY_AND_FRONTIER_FINAL.md` was deliberately not written.** The
§25 manuscript section is structured around the explored frontier — how many
admissible supports were actually scored, and how they differ from the wider
universe. There is no explored frontier. Writing that section now would describe
exploration that did not happen. It is the first thing to produce on re-run.

## 19. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\07_search_policy_and_frontier\scripts"
& $P $S\s7_7_a_precontract.py            # parents + S_pers + AR(1); no archive
& $P $S\s7_7_b_policy_and_preflight.py   # strata + policy + budget; no archive
& $P $S\s7_7_c_block_and_freeze.py       # block record, audits, freeze
```

Deterministic; no seeds; no archive opened by any of the three.

## 20. Recommendation for S7.8

**`BLOCKED`.** S7.8 must not start. There is no explored frontier for it to
apply the utility and qualification rules to.

The block is narrow and the fix is a single decision:

1. **Decide the budget question** — `SEEDS_PER_STRATUM = 1` (188,736, fits) or
   raise `MAX_SUPPORT_EVALUATIONS` to at least 363,900 (no change to search
   semantics). The second is the smaller intervention; the first is the smaller
   computation. Either is defensible; neither is mine to choose.
2. **Re-freeze prospectively.** The amended constant must be hashed into a new
   `SEARCH_POLICY_PREVALUE` before any density value is opened. Amending after
   target outcomes would make the stage `SEARCH_POLICY_CONTAMINATED`.
3. **Re-run S7.7 from stage B.** Stage A's artifacts carry forward unchanged —
   parents verified, `S_pers` and `B1A_AR1` frozen at `1b8df4c0…`.

One thing worth deciding at the same time. The 252-seed figure is driven by
having 127 strata, which is itself a consequence of the ordered pair signatures
for C3, C6 and C7 — the price of *not* collapsing role-directional relations.
That was the right call in S7.5H and remains right; it simply means this search
is intrinsically wider than a five-family grammar would have made it. If the
budget is raised, raise it knowing that is why.
