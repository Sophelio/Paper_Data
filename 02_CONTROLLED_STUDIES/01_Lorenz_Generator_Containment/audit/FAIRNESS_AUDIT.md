# Fairness audit

**Date:** 2026-08-27 · **Verdict: PASS**

## Information boundary

Every method sees the same retrospective local information set

    I_k = { x[k−2 … k+2],  y[k−2 … k+2] }

Two raw baselines are therefore reported:

- **C0-center** (2 coordinates) — `x_k, y_k` only. Reference point, *not* the
  fairness control.
- **C0 information-matched** (10 coordinates) — the full stencil, i.e. exactly
  the samples from which every derivative and relational coordinate is built.
  **This is the primary control.**

The matched baseline is the honest comparison: it denies the expanded
representation any raw-information advantage, leaving only the difference in how
that information is *organised*. Its importance is visible in the numbers — the
MLP improves from 1.319 (center) to 0.248 (matched) on raw inputs alone, so
reporting only the center baseline would have overstated the representation
effect by roughly 5×.

## Retrospective, not forecasting

Centered stencils are used deliberately. The task reconstructs z(t_k) from
observations **around** t_k; it never predicts forward. Declared in
`benchmark_config.yaml` (`task.kind: retrospective_reconstruction`) and stated in
the figure and report. A causal backward-difference variant was *not* substituted
for the primary benchmark.

## Equal treatment

- Identical trajectory splits for all learners.
- One shared sample-support mask per trajectory, computed once from C_all and
  applied to every representation, so all methods score on identical rows.
- Identical metric definitions (`run_benchmark.metrics`).
- MLP architecture, optimiser and training settings fixed across
  representations; only input width changes. Five predeclared seeds.
- STLSQ threshold selected on validation independently per representation from
  the same declared grid.
- `test_identical_feature_columns_across_learners` pins column identity and
  order, so the claim that SIR/PySINDy/MLP receive the same matrix is tested,
  not asserted.

## Known asymmetry, disclosed

C_all (38) and C* (12) have more columns than C0 (10), so the MLP gains
first-layer parameters. This is inherent to any representation comparison. It is
bounded and reported: 4 929 parameters for C0 vs 5 057 for C* — a **2.6%**
increase for an **8.6×** RMSE reduction. The sparse estimator, whose capacity does
not grow the same way, shows the same ordering, which is the main reason to
believe the effect is representational rather than capacity-driven.
