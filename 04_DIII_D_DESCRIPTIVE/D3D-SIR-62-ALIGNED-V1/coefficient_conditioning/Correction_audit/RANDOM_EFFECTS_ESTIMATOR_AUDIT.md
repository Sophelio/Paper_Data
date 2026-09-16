# Random-effects estimator audit

## Original implementation

Function: `coefficient_conditioning_utils.profile_tau2`

Implemented objective (profiled over the common mean `mu`):

```
ll(tau2) = -0.5 * ( sum_i log(v_i) + sum_i (y_i - mu)^2 / v_i )
v_i = within_var_i + tau2
mu = sum(w_i y_i) / sum(w_i),  w_i = 1/v_i
```

This is the **Gaussian profile maximum-likelihood (ML)** objective for a
one-parameter random-intercept meta-analytic model with known sampling
variances. It does **not** include the REML correction term `log(sum w_i)`.

## Treatment of the mean

The common mean `mu` is profiled in closed form at each candidate `tau2`
(weighted least-squares mean). It is not a free parameter of the grid search.

## Treatment of within-discharge variances

Discharge-specific primary block-bootstrap variances are treated as known
`within_var_i` and held fixed.

## Optimization domain

`tau2 >= 0` on a fixed non-negative grid (including exact zero).

## Interval method

Approximate 95% profile-likelihood interval: values of `tau2` with
`2 (L_max - L) <= chi2_1,0.95 ≈ 3.84146`, evaluated on the same grid.
Additionally, a discharge-level nonparametric bootstrap of the point estimate
was reported.

## Is the original `tau2_REML` label accurate?

**No.** The original label `tau2_REML` / `tau_REML` is mathematically inaccurate.
The implemented estimator is profile **ML**, not restricted maximum likelihood.

## Corrected terminology

| Role | Correct name |
|------|----------------|
| Original estimator | `tau2_ML` / `tau_ML` (compatibility: original `tau2_REML` column) |
| Primary corrected estimator | `tau2_REML` from the REML objective below |
| Sensitivity | report both ML and REML |

## Verified REML objective (primary)

```
l_R(tau2) = -0.5 * ( sum log(v_i) + log(sum w_i) + sum w_i (y_i - mu)^2 )
```

This is the standard REML profile likelihood for the one-parameter
random-intercept meta-analysis model with known within-study variances
(Viechtbauer-type form). Intervals use the same profile-chi-square rule and
a discharge-level bootstrap with >= 5000 replicates.
