# S7.8 — Development selection protocol

The exact rule S7.9 will execute. **S7.8 does not execute it.** No candidate is
selected here, no utility quantity is computed over `Ahat_rec`, and the external
cohort stays sealed.

Machine-readable form: `development_selection_algorithm.json`,
`U_REC_OPERATIONAL_V1.json`.

---

## 0. Domain

| | |
|---|---|
| selection domain | `AHAT_REC_DENSITY_ONE_SEED_V2` |
| cardinality | 162 845 (10 778 singleton + 152 067 multivariate, sizes 1–12) |
| search policy | `SIGMA_REC_ONE_SEED_PRIMARY_V2` |
| global optimality claim | **false** |

Selection happens **within the frozen explored frontier**. `A_rec \ Ahat_rec`
— roughly 5.1 × 10³⁹ admissible support combinations — remains
`ADMISSIBLE_UNSEARCHED` and carries no negative finding.

## 1. Canonical identity — read this before writing any code

Support identity comes from `explored_support_registry.csv`. Atom membership is
recovered by splitting `support_id` on pipe characters **at parenthesis depth 0
only**.

The C4/C6/C7/C8 signatures — `PHASE(i|j)`, `LEVEL_RATE(i|j)`,
`RATE_OVER_LEVEL(i|j)`, `LEVEL_OVER_RATE(i|j)` — embed a pipe **inside their own
parentheses**. A naive `split('|')` returns the wrong atom count for **116 608
of the 162 845 rows (71.6 %)**.

> **Mandatory checksum.** The depth-aware parse must reproduce registry
> `support_size` for all 162 845 rows before any utility computation begins.
> Verified in S7.8; S7.9 must re-verify.

Final tie-break at every rank: lexicographic ascending byte order of the
canonical `support_id`. Support ids are unique across `Ahat_rec`, so it always
resolves to exactly one candidate.

## 2. Estimator — `DEVELOPMENT_RELATION_OLS_V1`

Per discharge/block cell:

1. fit predictor means and standard deviations on the **calibration interval only**;
2. standardize coordinates with those calibration values;
3. apply them **unchanged** to the protected predictor values;
4. fit an intercept;
5. solve affine OLS on the standardized design;
6. coefficients are **discharge/block local** — never shared across discharges.

`sd <= 0` → the divisor is exactly `1.0` (inherited verbatim from S7.7R). No
epsilon. Ridge is **not** the primary estimator; it may return later only as a
separately labelled *conditioning* sensitivity, never chosen on performance.

## 3. Primary metric

```
scale_{s,b}  = std(y_calibration_{s,b}, ddof=0)          # zero -> INVALID
NRMSE_{s,b}  = RMSE(y_protected, yhat_protected) / scale_{s,b}
NRMSE_s(C)   = mean over blocks A,B,C
FIT(C)       = mean over the 20 development discharges
```

Raw RMSE in physical units is retained for reporting and is **not** the primary
utility measure.

## 4. Practical equivalence — authoritative rule

```
delta_equiv = max(SE_delta, 0.01)
A ~ B  iff  |NRMSE_A - NRMSE_B| <= delta_equiv      # NRMSE units
```

`SE_delta = sd(delta_s, ddof=1) / sqrt(20)` where
`delta_s = mean_b NRMSE_{A,s,b} - mean_b NRMSE_{B,s,b}`.

The **0.01 floor is immutable**. No epsilon. No raw-RMSE reading. The S7.2 V1
conjunction (`1 SE` **AND** `0.01`) is `SUPERSEDED_BY_S7.2C_C01` and must not be
used.

## 5. The lexicographic ladder

No weighted sum. No Pareto-weight tuning. No family bonus or penalty.

### E0 → E1 · Rank 1 · primary fit quality

```
FIT_best = min_C FIT(C)
E1 = { C : |FIT(C) - FIT_best| <= max(SE_delta(C, best), 0.01) }
```

This is the frozen practical-equivalence set — **not** "take top K". No
candidate outside `E1` advances. Equivalence is tested pairwise **against the
best**, not closed transitively. The best is always a member
(`SE_delta(best,best) = 0`, `|0| <= 0.01`).

A candidate with any non-finite cell has `FIT = +inf` and cannot enter `E1`. All
162 845 × 60 cells of the frozen frontier are finite, so this branch is
defensive only.

### E1 → E2 · Rank 2 · development generalization / stability

```
BLOCK_WORST(C) = max over b in {A,B,C} of ( mean_s NRMSE_{s,b}(C) )
SHOT_P90(C)    = numpy.percentile( NRMSE_s(C) over 20 discharges, 90, method='linear' )
```

Applied lexicographically inside `E1`: first minimize `BLOCK_WORST` under
practical equivalence; then, among those, minimize `SHOT_P90` **exactly** — no
new epsilon, ties retained and resolved by later ranks.

`BLOCK_WORST` equivalence uses the same immutable floor,
`delta = max(SE_delta_worst, 0.01)`, with each candidate contributing **its own
worst block**:

```
b_star(C) = argmax_b ( mean_s NRMSE_{s,b}(C) )     # ties -> earliest of A < B < C
d_s(A,B)  = NRMSE_{s, b_star(A)}(A) - NRMSE_{s, b_star(B)}(B)
SE_delta_worst = sd(d_s, ddof=1) / sqrt(20)
```

This is coherent because `mean_s d_s(A,B) = BLOCK_WORST(A) − BLOCK_WORST(B)`
**exactly** — the paired discharge-level differences average to precisely the
candidate-level quantity being compared. Verified to 2.7 × 10⁻¹⁶ in
`manifests/ALGORITHM_DRY_RUN.json`.

> Because a discretion-free paired SE **was** implementable, the fallback
> permitted in the S7.8 instruction — "use the fixed 0.01 floor only for
> `BLOCK_WORST` and record the qualification" — is **NOT_REQUIRED** and is not
> invoked. No new tunable threshold was introduced.

### E2 → E3 · Rank 3 · parsimony

Minimize `|C|` (registry `support_size`), then `ACTIVE_TERMS(C)`.

`ACTIVE_TERMS(C)` counts explanatory columns whose OLS coefficient is **not
exactly zero** under ordinary floating arithmetic. No magnitude threshold, no
p-value pruning, intercept not counted. A column is active if it is non-zero in
**at least one** of the 60 calibration fits (coefficients are cell-local, so the
criterion needs a candidate-level integer; the union is the conservative reading
and needs no threshold).

Under full-rank OLS an exactly-zero coefficient essentially never occurs, so
`ACTIVE_TERMS(C) = |C|` and this subcriterion is non-binding — as the parent
policy anticipates.

### E3 → E4 · Rank 4 · conditioning

`Z_{s,b}(C)`: the **calibration rows** of the cell, columns standardized by that
cell's calibration mean and sd, **intercept excluded**. Because standardization
subtracts the calibration mean, `Z` on the calibration rows is already exactly
column-centred, so the centred and standardized readings coincide.

```
kappa_{s,b}(C) = sigma_max(Z) / sigma_min(Z)        # singular values, SVD
sigma_min == 0  ->  kappa = +inf
COND_MEDIAN(C) = median over the 60 cells of log10(kappa)
COND_P90(C)    = percentile(..., 90, method='linear')
COND_MAX(C)    = max over the 60 cells
```

**Do not** use the normal-equation condition number — it is the square (dry-run
ratio exactly 1.0). Order: minimize `COND_MEDIAN`, tie-break `COND_P90`, then
`COND_MAX`.

No condition-number cutoff is introduced. Conditioning is a **utility
criterion**, not an admissibility rule: a candidate is never declared
inadmissible merely because another is better conditioned.

For `|C| = 1` the design has one singular value, so `kappa = 1` and
`log10(kappa) = 0` exactly. Recorded here in advance rather than discovered
later.

### E4 → E5 · Rank 5 · support stability

Maximize `BOOT_SELECTION_FREQ`, then `FOLD_SELECTION_FREQ`, then canonical
support id. Full specification in `SUPPORT_STABILITY_PROTOCOL.md`.

## 6. Output S7.9 must produce

- one deterministic development-selected candidate;
- the full survivor set at every rank (`E0`…`E5`);
- an elimination ledger with one row per eliminated candidate:
  `support_id, support_size, rank_eliminated, criterion, reason,
  comparison_quantity, candidate_value, reference_value, threshold_applied`.

The only source of randomness in the whole algorithm is the Rank-5 discharge
bootstrap, seeded `2026090501`.

## 7. Reusing the S7.7R arrays

S7.9 may reuse the frozen per-cell NRMSE arrays only after verifying **all
five**: artifact hashes · estimator equivalence · metric equivalence · support
identity · block identity. Otherwise it recomputes. All five were verified in
S7.8; S7.9 must re-verify at execution time.

Reuse is a **numerical** convenience. `J_search` determined *where the search
looked*; `FIT` is *one criterion inside U_rec*. The distinction survives even
where the numbers coincide exactly.

## 8. Forbidden during execution

Selecting before the ranks run in order · introducing an undefined tolerance ·
reordering ranks · pruning a constructor family · penalizing ECE ancestry ·
removing uncalibrated primitives.
