# The explored frontier `Ahat_rec`

Machine-readable: `AHAT_REC_V2.json`, `explored_support_registry.csv`,
`lowest_navigation_score_by_size.csv`, `unsearched_boundary_summary.csv`

```
Ahat_rec = Explore(A_rec^H ; Sigma_rec, B_rec)  subset  A_rec^H
membership: a support is in Ahat_rec iff its search proxy was actually evaluated
cardinality: 162,845          rank-deficient designs: 0
```

---

## Coverage by support size

| m | supports | | m | supports |
|---|---|---|---|---|
| 1 | **10 778** (every admissible atom) | | 7 | 14 568 |
| 2 | 8 126 | | 8 | 14 507 |
| 3 | 12 462 | | 9 | 14 784 |
| 4 | 14 376 | | 10 | 14 855 |
| 5 | 14 423 | | 11 | 14 857 |
| 6 | 14 366 | | 12 | 14 743 |

All 127 main-lane paths and all 7 raw-only paths reached size 12. Size 2 is
smaller than the rest because 127 paths proposing from 127 strata collide most
often at the first growth step.

## Lowest navigation score by support size

These are **descriptive properties of `Ahat_rec`**. They are not optimal, not
qualified, not final, and not `C*`.

| m | J_search | families spanned | leading support |
|---|---|---|---|
| 1 | 0.4801 | ECE+CER | `RATIO(ece16,cerqtit10)` |
| 2 | 0.3390 | +density, magnetics | `ID(pcdiamag3) \| RATIO(prmtan_neped,ece22)` |
| 3 | 0.2555 | 3 | adds `PROD(ip,prmtan_neped)` |
| 4 | 0.2249 | 4 | adds `RECIP(cerqtit10)` |
| 5 | 0.2059 | 4 | |
| 6 | 0.2012 | 5 | +filterscope |
| 7 | 0.1922 | 6 | +gas |
| 8 | 0.1860 | **7** | +beams |
| 9 | 0.1822 | 6 | |
| 10 | 0.1759 | 6 | |
| 11 | 0.1690 | 7 | |
| 12 | **0.1663** | 7 | 2×C0, 5×C2, 3×C3, 2×C5 |

Constructor mix in the leading supports is dominated by products (C2) and ratios
(C3), with levels (C0) and reciprocals (C5) appearing throughout. No C1, C6 or
C7 coordinate appears in any of them.

The atomic score distribution for context: minimum 0.4801, median 1.0144,
maximum 27.5496 across all 10,778 coordinates. Best atom per constructor —
C3 0.4801, C2 0.4937, C0 0.4996, C5 0.5563, C7 0.8965, C6 0.9744, C1 0.9814.

## Raw-only control lane

`C0_ONLY_GREEDY` over the 66 admissible primitive levels, one seed per
scientific family, same greedy mechanism.

| m | J_search | | m | J_search |
|---|---|---|---|---|
| 1 | 0.4996 `ID(prmtan_neped)` | | 7 | 0.2369 |
| 2 | 0.3775 | | 8 | 0.2244 |
| 3 | 0.3123 | | 9 | 0.2213 |
| 4 | 0.2849 | | 10 | 0.2204 |
| 5 | 0.2786 | | 11 | 0.2201 |
| 6 | 0.2619 | | 12 | **0.2200** |

At size 12: `bt, ece39, fs03da, fs04, gasa, gasc, gasd, ip, pcdiamag3, pinj,
prmtan_neped, tinj`.

The raw-only lane flattens after about size nine (0.2213 → 0.2200 over the last
three additions) while the relational lane keeps descending. **This is a
navigation observation only.** It is not a comparison claim, not a baseline
result, and not evidence of relational advantage — that comparison belongs to
S7.8/S7.9 with the frozen comparators, and this lane is **not** B2, which
remains the frozen full-information raw Ridge comparator and was not run.

## The searched / unsearched boundary

```
admissible atomic coordinates                                        10,778
Ahat_rec size-1 supports (all scored)                                10,778
unique multivariate supports scored                                 152,067
total unique supports in Ahat_rec                                   162,845

multivariate proposals made (incl. duplicates)                      177,364
  of which duplicate proposals within a step                         25,269
  of which cache hits across steps                                       28
proposals rejected by Phi_set before evaluation                           0

unconstrained admissible supports of size 1..12          ~5.10 x 10^39
ADMISSIBLE_UNSEARCHED                                    ~5.10 x 10^39
fraction of the size-1..12 support space actually scored  3.19 x 10^-35
```

`Φ_set` was enforced on every proposal and rejected none: the frozen exact
dependency constraint has no binding group in this universe (S7.6R found all 400
vacuous), and duplicates and size bounds are excluded by construction.

**Everything outside `Ahat_rec` is `ADMISSIBLE_UNSEARCHED`.** No property was
tested there and no negative claim of any kind attaches to it. The words *global
optimum*, *exhaustive search* and *complete search* do not apply and are not
used anywhere in this stage.

## Budget

| | |
|---|---|
| metadata projection (max) | 188,736 |
| actual proposals + atomic scoring | **188,142** |
| frozen allowance | 300,000 |
| truncated at the limit | no |

The run came in 594 below its own metadata projection, because some strata
exhaust their shortlisted atoms late in a path and stop proposing.

## Numerical provenance of the proxy

`SEARCH_PROXY_OLS_V1` is solved in partitioned (Frisch–Waugh) form — the
intercept absorbed by centring, the slopes from the normal equations of the
centred calibration design. That is algebraically identical to
`numpy.linalg.lstsq` on `[1, Z]` for a full-rank design, and it was verified
against `lstsq` on 48 random supports across sizes 2, 5, 9 and 12:

```
maximum relative deviation   1.72e-13      tolerance 1e-9      PASS
```

Rank deficiency is detected from the eigenvalues of the centred Gram matrix
(`sqrt(min/max) <= max(n_prot, m+1)*eps`) and scored `+infinity` with the flag
`SEARCH_PROXY_RANK_DEFICIENT` — **never** as inadmissibility. **No support in
the frontier was rank deficient**, and no atom was.
