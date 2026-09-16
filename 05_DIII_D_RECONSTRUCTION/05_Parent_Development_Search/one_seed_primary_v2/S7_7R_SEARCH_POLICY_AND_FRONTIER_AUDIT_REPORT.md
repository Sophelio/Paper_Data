# S7.7R — One-seed primary search and explored frontier: internal audit

**Freeze:** `D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2`
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance **43/43** · 2026-09-05

---

## 1. Executive verdict

`Sigma_rec` frozen and **executed**. `Ahat_rec` constructed: **162,845**
evaluated supports — all 10,778 admissible atoms plus 152,067 distinct
multivariate representations across sizes 1–12. Zero external values, zero
baselines, no `C*`, no validation claim.

The one substantive policy change authorised by the human decision —
`SEEDS_PER_STRATUM` 2 → 1 — was made, machine-diffed against the V1 policy, and
confirmed to be the only substantive difference. The metadata projection
(188,736) matched the instruction exactly and fits the unchanged 300,000
allowance; the run used 188,142.

**Three qualifications, all recorded rather than acted on:**

1. ECE ancestry appears in **85.4%** of retained-path supports and **100%** of
   the lowest-navigation-score supports *after* opportunity was balanced to
   30.7%. Reported as found; not rebalanced.
2. The primary search is one-seed — broad in opportunity, shallow in multi-start
   depth. Reduced protection against greedy-start sensitivity was accepted
   prospectively.
3. `Ahat_rec` covers **3.19 × 10⁻³⁵** of the size-1..12 support space. The
   remainder is `ADMISSIBLE_UNSEARCHED` and carries no negative finding.

## 2. Parent verification

`PARENTS_VERIFIED` — **0 hash drift** across all twelve lineage records: S7.1,
S7.2 V1/V2, S7.3 V1, S7.4 V1, S7.3R V2, S7.4 V2, S7.5, S7.5H, historical S7.6
V1, S7.6R hardened V2, and historical blocked S7.7 V1.

All 18 substantive checks pass: target `density`,
`A_REC_DENSITY_HARDENED_V2` authoritative, atomic universe 10,778, active strata
127, support bound 1–12, **C4 = 0**, **C8 = 0**, denominator rule `6d4004eb…`
unchanged, `T_REC_V1` unchanged, external cohort 42 sealed, `P_hard` = 70.

## 3. Historical S7.7 V1 reconciliation

`BLOCKED_SEARCH_BUDGET` / `PRESERVED_AS_AUDIT_HISTORY`. Stage A snapshotted all
21 files before the re-run; stage C re-verified after:
**`HISTORICAL_S7_7_V1_BYTE_FOR_BYTE_UNCHANGED`, 0 changed.**

V1 opened no archive, scored no atom, ran no baseline and constructed no
frontier, so it contains no target-dependent information and nothing it recorded
can bias the policy frozen here. Its stratification and policy structure are
reused *because they were frozen before any value was read*, and the reuse is
hash-verified rather than re-derived.

## 4. Pre-search contract carry-forward

`PRE_SEARCH_CONTRACT_COMPLETION.json`, sha `1b8df4c0672686be…` —
**hash-verified unchanged, not regenerated, not modified.**

`S_PERS_V1` remains required reporting, not used for search, does not replace
frozen NRMSE, does not change V3. `B1A_AR1` remains a diagnostic baseline,
required to report later, **not run**. Neither was run in this stage.

## 5. Search-policy diff

`ONLY_SEED_MULTIPLICITY_CHANGED` — 0 unauthorised changes across all compared
fields.

| | V1 | V2 |
|---|---|---|
| `SEEDS_PER_STRATUM` | 2 | **1** |
| raw-only lane seeds | top 2 per C0 family | **top 1 per C0 family** |
| projected main seeds | 252 | **127** |
| projected raw seeds | 14 | **7** |

Verified unchanged: `MAX_SUPPORT_EVALUATIONS` 300,000 ·
`MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION` 96 · support size 1–12 · all 10,778
atoms scored univariately · 127 active strata · constructor and family-signature
semantics · `SEARCH_PROXY_OLS_V1` · `J_search` · the greedy proposal rule ·
`Φ_set`.

The diff is machine-computed over the flattened policy trees with an explicit
allow-list; anything outside it would have aborted the stage as
`UNAUTHORISED_SEARCH_POLICY_DRIFT`. During development it did exactly that on a
stray provenance field, which is the check working.

Also frozen prospectively in V2 (§6): `ONE_SEED_SEARCH = PRIMARY`,
`TWO_SEED_SEARCH = NOT_EXECUTED / OPTIONAL_FUTURE_SEARCH_DEPTH_SENSITIVITY`,
with no outcome trigger defined.

## 6. Pre-value freeze

```
SEARCH_POLICY_PREVALUE_V2.json   sha 2049cf99...   frozen 2026-09-05T00:17:10Z
parent V1 policy                 sha a97e690e...
```
Stage A contains no data-loading code path. Stage B re-verifies this hash before
opening the first archive and aborts as `SEARCH_POLICY_CONTAMINATED` on
mismatch. The ordering is structural, not procedural.

## 7. Search-budget preflight

```
atomic scoring                                   10,778
main lane      127 seeds x 11 steps x 127 strata = 177,419
raw-only lane    7 seeds x 11 steps x   7 strata =     539
maximum projected                                188,736   <- matches instruction
MAX_SUPPORT_EVALUATIONS                          300,000   headroom 111,264
```
Computed from metadata only, before any density value. §13 cap sufficiency
re-verified: 96 ≥ 35, so every nonempty stratum receives a shortlist slot.

## 8. First target access

```
policy frozen        2026-09-05T00:17:10.479649+00:00
first density access 2026-09-05T00:27:42.757620+00:00     ordering verified True
```
20 development discharges, 70 predictor signals each, target `density` in
canonical `m^-3`. External shots read: none. Every archive open is logged in
`manifests/DATA_ACCESS_LOG.csv`.

## 9. Atomic navigation scoring

**All 10,778 admissible atoms scored. 0 rank deficient.**

`J_search` distribution: minimum **0.4801**, median 1.0144, maximum 27.5496.
Best atom per constructor — C3 0.4801 · C2 0.4937 · C0 0.4996 · C5 0.5563 ·
C7 0.8965 · C6 0.9744 · C1 0.9814.

Per-discharge means are in `atomic_navigation_scores.csv`; the full per-cell
(20 discharges × 3 blocks) detail is in `atomic_per_cell_nrmse.npz`.

**Proxy provenance.** `SEARCH_PROXY_OLS_V1` is solved in partitioned
(Frisch–Waugh) form and verified against `numpy.linalg.lstsq(..., rcond=None)`
on 48 random supports across sizes 2, 5, 9, 12: **max relative deviation
1.72 × 10⁻¹³** against a 10⁻⁹ tolerance. Rank deficiency is detected from the
centred Gram eigenvalues and scored `+infinity` with
`SEARCH_PROXY_RANK_DEFICIENT` — never as inadmissibility.

## 10. Within-stratum ranking

Sorted by `J_search` then canonical coordinate ID, **within each stratum**.
No global top-K list was formed; a `global_rank_reference_only` column exists in
the registry for audit and is used by nothing.

## 11. Constructor shortlist

Round-robin over each constructor's strata, cap 96. **548 atoms.**

| | C0 | C1 | C2 | C3 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|---|
| admissible | 66 | 59 | 2 080 | 2 457 | 39 | 3 776 | 2 301 |
| shortlisted | **66** | **59** | 96 | 96 | **39** | 96 | 96 |

C0, C1 and C5 retained entirely. Every one of the 127 strata is represented
(verified by set equality, not by construction). The 10,230 atoms not
shortlisted are `ADMISSIBLE_NOT_IN_EXPANSION_SHORTLIST`, retained with their
scores in the registry, and are **not** inadmissible.

## 12. One-seed registry

**127 main seeds** — exactly one per active stratum, verified by set equality
against the full stratum set. Seed `J_search` ranges 0.4801 to 1.0192. **No seed
was rank deficient**, so `SEED_PROXY_RANK_DEFICIENT` was never triggered.

**7 raw-only seeds** — one per nonempty C0 scientific family.

## 13. Greedy search

All **127** main paths grew from size 1 to size 12; 1,524 retained path records.
At each step every stratum represented in the shortlist proposed its best unused
atom; the lowest-`J_search` extension was taken, tie-broken by canonical support
ID (coordinate IDs sorted lexicographically).

```
multivariate proposals                177,364
  duplicate proposals within a step    25,269
  cache hits across steps                  28
  rejected by Phi_set                       0
unique multivariate supports scored   152,067
```

`Φ_set` was enforced on every proposal — size, duplicates, atoms-only,
sensitivity-only exclusion, and the exact-dependency predicate. It rejected
none, which is expected: S7.6R found all 400 dependency groups vacuous, and the
other predicates are excluded by construction. The check runs regardless rather
than being assumed.

## 14. Raw-only control lane

`C0_ONLY_GREEDY`, 7 seeds, all reaching size 12. `J_search` falls 0.4996 →
0.2200, flattening after roughly size nine while the relational lane continues
to 0.1663.

**This is a navigation observation, not a comparison claim.** The lane is not
B2; B2 remains the frozen full-information raw Ridge comparator and was not run.
Any relational-versus-raw statement belongs to S7.8/S7.9.

## 15. Search-budget runtime audit

```
projected maximum                        188,736
actual proposals + atomic scoring        188,142
frozen allowance                         300,000
truncated after reaching the limit           no
verdict                    SEARCH_BUDGET_RUNTIME_OK
```
The run came in 594 under its own projection because some strata exhaust their
shortlisted atoms late in a path and stop proposing.

## 16. `Ahat_rec`

**162,845** supports, deduplicated, with full proposal provenance preserved in
`search_proposal_provenance.csv` (177,364 rows: path, step, proposing stratum,
proposed coordinate, resulting support, score).

| m | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| | 10 778 | 8 126 | 12 462 | 14 376 | 14 423 | 14 366 |

| m | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|
| | 14 568 | 14 507 | 14 784 | 14 855 | 14 857 | 14 743 |

Lowest navigation score falls 0.4801 (m=1) → **0.1663** (m=12). Full table in
`EXPLORED_FRONTIER_SUMMARY.md`. These are labelled
`LOWEST_NAVIGATION_SCORE_SUPPORT_AT_SIZE_m` and carry explicit
`is_optimal: false`, `is_qualified: false`, `is_final: false`, `is_C_star:
false` flags in the registry.

## 17. Multiplicity audit

| family | P_hard | atoms | shortlist | **seeds** | explored | retained | lowest-J |
|---|---|---|---|---|---|---|---|
| **ECE** | 0.471 | **0.842** | 0.420 | **0.307** | 0.958 | 0.854 | 1.000 |
| CER | 0.200 | 0.347 | 0.310 | 0.307 | 0.878 | 0.709 | 0.833 |
| NBI | 0.143 | 0.144 | 0.172 | 0.220 | 0.508 | 0.382 | 0.250 |
| gas | 0.057 | 0.097 | 0.173 | 0.220 | 0.552 | 0.376 | 0.500 |
| magnetics | 0.057 | 0.071 | 0.232 | 0.307 | 0.743 | 0.705 | 0.917 |
| filterscope | 0.043 | 0.045 | 0.102 | 0.134 | 0.716 | 0.604 | 0.583 |
| density-aux | 0.029 | 0.041 | 0.181 | 0.228 | 0.860 | 0.831 | 0.917 |

**Opportunity: balanced.** ECE 0.842 → 0.420 → **0.307**, below its own 0.471
share of the primitive basis. Magnetics rises 0.071 → 0.307, density-aux 0.041 →
0.228, gas 0.097 → 0.220. The §22 criterion is met.

**Outcome: ECE still dominates.** 0.854 of retained-path supports, 1.000 of the
lowest-J supports. Recorded as an empirical development-search outcome, **not
rebalanced**, with no family term anywhere in `J_search`.

The complementary half matters as much: magnetics appears in 91.7% of the
lowest-J supports on a 5.7% share of the basis, density-aux likewise, gas in
50%. The single-coordinate leader is a cross-family ratio
`RATIO(ece16,cerqtit10)`, and by size eight the leading support spans all seven
families. A proportional-to-count search would not have looked there.

## 18. Constructor audit

| | atoms | share | shortlist | seeds | seed share | explored | retained |
|---|---|---|---|---|---|---|---|
| C0 | 66 | 0.006 | 66 | 7 | 0.055 | 0.597 | 0.565 |
| C1 | 59 | 0.005 | 59 | 5 | 0.039 | 0.071 | 0.056 |
| C2 | 2 080 | 0.193 | 96 | 28 | 0.220 | 0.765 | 0.706 |
| C3 | 2 457 | 0.228 | 96 | 28 | 0.220 | 0.902 | 0.778 |
| C5 | 39 | 0.004 | 39 | 4 | 0.031 | 0.588 | 0.419 |
| C6 | 3 776 | 0.350 | 96 | 35 | 0.276 | 0.511 | **0.046** |
| C7 | 2 301 | 0.213 | 96 | 20 | 0.157 | 0.368 | **0.026** |

**Worth flagging for S7.8.** C6 and C7 — the level–rate constructors the S7.5H
hardening introduced — hold 56.3% of all admissible atoms between them, received
43.3% of seed opportunity, and were retained on 4.6% and 2.6% of path supports
respectively. Their best single coordinates score 0.974 and 0.897 against 0.480
for the best ratio, and neither appears in any lowest-J support. On this target,
under this proxy, the grammar broadening that made the ontology 1.75× larger
contributed almost none of the retained structure. That is a development-search
observation, not a qualification result.

**C4 and C8:** `DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS /
ZERO_SEARCH_OPPORTUNITY` — inherited from S7.6R, not a search exclusion, not
rescued.

## 19. Searched versus unsearched boundary

```
admissible atomic coordinates                             10,778
Ahat_rec size-1 supports                                  10,778   (all scored)
unique multivariate supports scored                      152,067
total unique supports in Ahat_rec                        162,845
unconstrained admissible supports of size 1..12    ~5.10 x 10^39
ADMISSIBLE_UNSEARCHED                              ~5.10 x 10^39
fraction actually scored                            3.19 x 10^-35
```
Everything outside `Ahat_rec` is `ADMISSIBLE_UNSEARCHED`; no property was tested
there and **no negative claim of any kind attaches to it**. `NOT SEARCHED ≠
INADMISSIBLE`. The words *global optimum*, *exhaustive search* and *complete
search* do not apply and are not used.

## 20. External firewall

External signal values **0**, external target values **0**, external discharges
opened **0**. The 42-discharge cohort remains sealed through S7.9.
`FIREWALL_INTACT`.

## 21. Files

5 Markdown, 14 CSV, 7 JSON, 2 NPZ, 3 scripts, 8 manifest records — hashed in
`S7_7R_FREEZE.json` (freeze and acceptance self-referentially excluded).

## 22. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\07_search_policy_and_frontier\one_seed_primary_v2\scripts"
& $P $S\s7_7r_a_policy.py     # lineage, carry-forward, policy diff, preflight
& $P $S\s7_7r_b_search.py     # development-only search  (~48 s)
& $P $S\s7_7r_c_frontier.py   # Ahat_rec, audits, freeze
```
Stage A opens no archive. Stage B aborts if the policy hash changed. Fully
deterministic; the only RNG use is the fixed-seed sample for the lstsq
equivalence check, which affects nothing downstream.

## 23. Recommendation for S7.8

**`READY_WITH_QUALIFICATIONS`.**

`Ahat_rec` is constructed, complete, auditable, and frozen. Four things belong to
S7.8 rather than here:

**First**, nothing in this stage is a utility result. `J_search` is a navigation
device; the lowest-navigation-score supports are descriptive properties of
`Ahat_rec` and were never compared against a baseline, ranked by `U_rec`, or
qualified.

**Second**, the one-seed depth is the accepted price of the budget. If S7.8's
conclusions turn out to be sensitive to which basin a path started in, the
remedy is a separately labelled two-seed **search-depth sensitivity analysis** —
never a replacement of this primary frontier, and never triggered by the primary
result being disappointing.

**Third**, ECE's persistence through balanced opportunity should be presented as
what it is: a substantive development-search finding that survives the removal of
its channel-count advantage, not an artefact. The counterpart — magnetics and
pedestal quantities appearing in nearly every leading support on a few per cent
of the basis — is the same finding seen from the other side.

**Fourth**, the C6/C7 result deserves an explicit look. The S7.5H hardening
broadened the grammar on a prospective architectural argument, and S7.6R noted
the ontology grew 1.75× as a result. This search gave those families ample
opportunity and they were retained on almost nothing. Whether that survives
utility qualification is S7.8's question, but it should be asked deliberately
rather than noticed later.
