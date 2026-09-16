# S7.10 — External baseline comparison

All seven methods evaluated on **identical scored samples**: 42 external
discharges, 126 blocks, every block comparison-eligible. No external tuning of
any kind.

Sign convention throughout: **negative = relational representation lower error**.
It is never switched.

Machine-readable: `external_discharge_metrics.csv`,
`external_paired_differences.csv`, `external_bootstrap_intervals.csv`,
`external_win_tie_loss.csv`, `external_lodo_results.csv`.

---

## Discharge-level external NRMSE

| Method | Mean | Median | Earlier (24) mean | Later (18) mean |
|---|---|---|---|---|
| **REL** `C_dev_star` | **0.7424** | **0.1699** | 1.1643 | 0.1798 |
| B0 calibration mean | 0.9225 | 0.9100 | 0.8735 | 0.9877 |
| **B1 persistence** | **0.2103** | 0.1765 | 0.2104 | 0.2101 |
| B1A AR(1) | 0.3504 | 0.3329 | 0.3325 | 0.3744 |
| B2 raw ridge (78) | 0.2804 | 0.1893 | 0.2657 | 0.3000 |
| B3 HistGB (78) | 0.3060 | 0.1806 | 0.3566 | 0.2384 |
| H0 hardened ridge (70) | 0.2828 | 0.1846 | 0.2644 | 0.3073 |

The mean and the median tell different stories, and both are reported. **The
frozen V3 gate uses the mean.** The median is not substituted for it.

## Where the relational error lives

| Block | REL | B0 | B1 | B1A | B2 | B3 | H0 |
|---|---|---|---|---|---|---|---|
| A | 0.2089 | 1.0380 | 0.2286 | 0.4394 | 0.3181 | 0.2911 | 0.3287 |
| **B** | **1.8475** | 0.9280 | 0.2284 | 0.3328 | 0.2632 | 0.3211 | 0.2628 |
| C | 0.1708 | 0.8013 | 0.1739 | 0.2791 | 0.2600 | 0.3057 | 0.2569 |

Blocks A and C are competitive with persistence. Block B carries the entire
pooled failure — and within block B, two discharges carry almost all of it.

## Paired differences · pooled 42 discharges

| Comparator | mean `Δ` | median `Δ` | 95 % CI | W / T / L |
|---|---|---|---|---|
| B0 | **−0.1801** | −0.7318 | [−0.7644, +0.6601] | 40 / 0 / 2 |
| **B1** | **+0.5321** | −0.0052 | [−0.0366, +1.3737] | 18 / 7 / 17 |
| B1A | +0.3919 | −0.1693 | [−0.1813, +1.2364] | 35 / 0 / 7 |
| B2 | +0.4620 | −0.0208 | [−0.0991, +1.2768] | 23 / 4 / 15 |
| B3 | +0.4364 | −0.0147 | [−0.1231, +1.2446] | 22 / 2 / 18 |
| H0 | +0.4596 | −0.0192 | [−0.1020, +1.2743] | 23 / 5 / 14 |

10 000 percentile-bootstrap replicates, seed `2026090503`, one shared
discharge-index matrix reused across every comparator so the paired geometry is
preserved. Win/tie/loss uses the already-frozen 0.01 floor and is **reporting
only** — it does not alter V3.

Every comparator shows the same signature: a **positive mean** and a **slightly
negative median**. On the typical external discharge the relational
representation is marginally ahead of or level with the raw comparators; in the
pooled mean it is well behind all of them.

## Leave-one-discharge-out

| Comparator | full-cohort `Δ` | LODO min | LODO max | range | most influential |
|---|---|---|---|---|---|
| B0 | −0.1801 | −0.4475 | −0.1505 | 0.297 | 187022 |
| B1 | +0.5321 | +0.2579 | +0.5514 | 0.294 | 187019 |
| B1A | +0.3919 | +0.1179 | +0.4152 | 0.297 | 187019 |
| B2 | +0.4620 | +0.1990 | +0.4917 | 0.293 | 187019 |
| B3 | +0.4364 | +0.1762 | +0.4822 | 0.306 | 187019 |
| H0 | +0.4596 | +0.1965 | +0.4886 | 0.292 | 187019 |

**0 of 42** LODO cohorts satisfy V3. Removing the single worst discharge leaves
`Δ₁ = +0.258` — still far from the −0.01 threshold, because there are two
catastrophic discharges, not one.

## Persistence skill `S_pers`

Frozen reporting metric, `S_pers(M,s) = 1 − mean_b MSE(M,s,b) / mean_b MSE(B1,s,b)`.

| | |
|---|---|
| defined / undefined | 42 / 0 |
| mean | **−402.52** |
| median | **+0.0943** |
| earlier-era mean | −704.37 |
| later-era mean | −0.0475 |
| positive (improves on persistence) | **24 of 42** |
| range | −11 672.2 … +0.798 |

`S_pers` is required reporting. It is **not** a V3 threshold and does not
replace NRMSE. Its mean is meaningless here — a ratio metric with an
unbounded negative tail — which is exactly why V3 was frozen on NRMSE rather
than on skill scores.

## Reading, under the frozen outcome table

The frozen `BASELINE_PROTOCOL` reading is unambiguous:

> **relational ≤ B0 or B1** → the task is trivial or degenerate; **no claim**.

The relational representation is materially worse than persistence in the frozen
pooled mean. The honest reading is the first row of the frozen table: **no
representational accuracy claim is available from this cohort.**

The relational representation is also materially worse than B2 (raw ridge on 78
primitives), B3 (gradient boosting on the same 78) and H0 (hardened 70-level
ridge) in the pooled mean. B2, B3 and H0 sit within 0.03 NRMSE of one another in
both mean and median, so on this cohort the hardening of the primitive basis and
the choice of linear versus nonlinear raw learner both matter far less than the
relational construction's exposure to out-of-calibration excursions.

None of this is a workflow failure. It is the external answer produced by a
workflow that was frozen before the answer was visible.
