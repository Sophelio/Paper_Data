# S7.7R — One-seed primary search and explored frontier

**Freeze:** `D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2`
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance **43/43**

```
Sigma_rec   SIGMA_REC_ONE_SEED_PRIMARY_V2   FROZEN_AND_EXECUTED   sha 2049cf99...
Ahat_rec    AHAT_REC_DENSITY_ONE_SEED_V2    162,845 supports, sizes 1-12
```

**Zero external values. Zero baselines. No `C*`. No validation claim.**

---

## What changed from the blocked V1

Exactly one substantive constant, by prospective human decision:

```
SEEDS_PER_STRATUM   2 -> 1        raw-only lane   top 2 -> top 1 per C0 family
```

`ONLY_SEED_MULTIPLICITY_CHANGED` — machine-diffed over the flattened policy
trees, **0 unauthorised changes**. Unchanged and verified: allowance 300,000 ·
cap 96 · support 1–12 · 10,778 atoms scored · 127 strata · signature semantics ·
`SEARCH_PROXY_OLS_V1` · `J_search` · greedy proposal rule · `Φ_set`.

Historical S7.7 V1 (`BLOCKED_SEARCH_BUDGET`) is preserved
**byte-for-byte unchanged**.

## The budget, and the run

```
metadata projection   10,778 + 127x11x127 + 7x11x7  =  188,736   (matches spec)
actual                                                 188,142
allowance                                              300,000
```
Frozen at `2026-09-05T00:17:10Z`; first density value opened at `00:27:42Z`.
Ordering verified, and structural — stages A and C contain no data-loading code
path at all.

## The frontier

| m | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| supports | 10 778 | 8 126 | 12 462 | 14 376 | 14 423 | 14 366 | 14 568 | 14 507 | 14 784 | 14 855 | 14 857 | 14 743 |
| lowest J | .4801 | .3390 | .2555 | .2249 | .2059 | .2012 | .1922 | .1860 | .1822 | .1759 | .1690 | **.1663** |

All 127 main paths and all 7 raw-only paths reached size 12. **0 rank-deficient
designs.** The single-coordinate leader is `RATIO(ece16,cerqtit10)`; by size
eight the leading support spans all seven scientific families.

These are `LOWEST_NAVIGATION_SCORE_SUPPORT_AT_SIZE_m` — descriptive properties
of `Ahat_rec`. **Not optimal, not qualified, not final, not `C*`.**
→ `EXPLORED_FRONTIER_SUMMARY.md`

## Multiplicity control: opportunity balanced, outcome reported

| family | P_hard | atoms | shortlist | **seeds** | retained | lowest-J |
|---|---|---|---|---|---|---|
| **ECE** | 0.471 | **0.842** | 0.420 | **0.307** | 0.854 | 1.000 |
| CER | 0.200 | 0.347 | 0.310 | 0.307 | 0.709 | 0.833 |
| NBI | 0.143 | 0.144 | 0.172 | 0.220 | 0.382 | 0.250 |
| gas | 0.057 | 0.097 | 0.173 | 0.220 | 0.376 | 0.500 |
| magnetics | 0.057 | 0.071 | 0.232 | 0.307 | 0.705 | 0.917 |
| filterscope | 0.043 | 0.045 | 0.102 | 0.134 | 0.604 | 0.583 |
| density-aux | 0.029 | 0.041 | 0.181 | 0.228 | 0.831 | 0.917 |

**Opportunity was balanced** — ECE falls 0.842 → 0.420 → **0.307**, below even
its 0.471 share of the primitive basis, while magnetics rises 0.071 → 0.307 and
density-aux 0.041 → 0.228. The §22 criterion is met.

**ECE nonetheless dominates the outcome** — 85.4% of retained paths, 100% of the
lowest-J supports. Recorded as an empirical development-search finding and
**not rebalanced**; no family term exists anywhere in `J_search`. The
counterpart is equally real: magnetics appears in 91.7% of the leading supports
on 5.7% of the basis. → `MULTIPLICITY_CONTROL_AUDIT.md`

## Three qualifications

1. **ECE dominance after balanced opportunity** — above. Reported, not corrected.
2. **One-seed depth.** Broad in scientific opportunity, shallow in multi-start
   depth. Reduced protection against greedy-start sensitivity, accepted
   prospectively. A two-seed search is `DECLARED_OPTIONAL / NOT_EXECUTED`, may
   only ever be a separately labelled **search-depth sensitivity analysis**, has
   **no outcome trigger**, and may never replace this primary frontier.
3. **Coverage.** `Ahat_rec` is 3.19 × 10⁻³⁵ of the ~5.1 × 10³⁹ size-1..12
   support space. Everything else is `ADMISSIBLE_UNSEARCHED` and carries **no
   negative finding**. *Global optimum*, *exhaustive* and *complete* are not
   used.

## One thing S7.8 should look at deliberately

C6 and C7 — the level–rate constructors S7.5H added — hold **56.3%** of all
admissible atoms, received **43.3%** of seed opportunity, and were retained on
**4.6%** and **2.6%** of path supports. Neither appears in any lowest-J support.
The grammar broadening that made the ontology 1.75× larger contributed almost
none of the retained structure on this target under this proxy.

## Start here

| File | What it is |
|---|---|
| `S7_7R_SEARCH_POLICY_AND_FRONTIER_FINAL.md` | manuscript-ready prose |
| `S7_7R_SEARCH_POLICY_AND_FRONTIER_AUDIT_REPORT.md` | full internal audit, 23 sections |
| `EXPLORED_FRONTIER_SUMMARY.md` | `Ahat_rec`, lowest-J tables, raw lane, boundary |
| `MULTIPLICITY_CONTROL_AUDIT.md` | opportunity vs outcome, kept apart |

## Machine-readable

```
SEARCH_POLICY_PREVALUE_V2.json     complete policy, hashed pre-density
SEARCH_BUDGET_PREFLIGHT_V2.json    metadata projection
SIGMA_REC_V2.json                  the executed policy
AHAT_REC_V2.json                   the explored frontier
two_seed_sensitivity_declaration.json
S7_7R_ACCEPTANCE_CHECKS.json       43 checks
S7_7R_FREEZE.json

search_strata.csv                  127 strata (carried unchanged)
atomic_navigation_scores.csv       all 10,778 atoms, J_search + per-discharge
constructor_shortlist.csv          548 atoms, round-robin order
search_seed_registry.csv           127 main + 7 raw-only seeds
search_candidate_evaluations.csv   152,067 unique multivariate supports
search_proposal_provenance.csv     177,364 proposals: path, step, stratum
search_retained_paths.csv          127 paths x 12 sizes
raw_only_search_paths.csv          7 paths x 12 sizes
explored_support_registry.csv      Ahat_rec, 162,845 rows
lowest_navigation_score_by_size.csv
raw_only_lowest_navigation_by_size.csv
multiplicity_audit.csv             sections 20A-G
constructor_audit.csv              section 21
unsearched_boundary_summary.csv    section 24
proxy_equivalence_check.csv        48 supports vs numpy.linalg.lstsq

atomic_per_cell_nrmse.npz          10,778 x 60 per-cell NRMSE
explored_per_cell_nrmse.npz        152,067 x 60 per-cell NRMSE

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/HISTORICAL_S7_7_V1_RECORD.json      snapshot taken before the re-run
manifests/HISTORICAL_V1_PRESERVATION.json     re-verified after it
manifests/PRE_SEARCH_CONTRACT_CARRY_FORWARD.json
manifests/SEARCH_POLICY_DIFF.json
manifests/POLICY_FREEZE_V2.json
manifests/SEARCH_BUDGET_RUNTIME_AUDIT.json
manifests/SEARCHED_UNSEARCHED_BOUNDARY.json
manifests/PROXY_EQUIVALENCE.json
manifests/ACCESS_AUDIT.json
manifests/DATA_ACCESS_LOG.csv
```

## Numerical provenance

`SEARCH_PROXY_OLS_V1` is solved in partitioned (Frisch–Waugh) form and verified
against `numpy.linalg.lstsq(..., rcond=None)` on 48 random supports across sizes
2/5/9/12: **max relative deviation 1.72 × 10⁻¹³** (tolerance 10⁻⁹). Rank
deficiency is detected from the centred Gram eigenvalues and scored `+infinity`
with `SEARCH_PROXY_RANK_DEFICIENT` — **never** as inadmissibility.

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\07_search_policy_and_frontier\one_seed_primary_v2\scripts"
& $P $S\s7_7r_a_policy.py     # no archive opened
& $P $S\s7_7r_b_search.py     # development-only search, ~48 s
& $P $S\s7_7r_c_frontier.py   # Ahat_rec, audits, freeze
```

## Stage gate

No external value · no baseline (B0, B1, B1A_AR1, B2, B3, `H0_RAW_HARDENED`) ·
no `S_pers` in search · no `U_rec` · no `C*`, `R*`, `Q_rec*` · no qualified
candidate · no validation claim · no two-seed search · C4 not rescued · C8 not
rescued · no shifted or bounded constructors · no `q_desc` or retired `q_rec`
seeding · `A_rec`, `G_rec`, `P_hard`, C0–C8, denominator rule, support bound,
`T_REC_V1`, strata and `Φ_set` all unchanged · **S7.8 not started.**
