# S7.2 — Statistical inference plan

Frozen now. **No numbers are computed at S7.2.**

## The inferential unit

> **DISCHARGE — never the time sample.**

With 42 external discharges the effective sample size is **42**. Those
discharges contain tens of thousands of time samples, but samples within a
discharge are strongly autocorrelated (many are interpolated from the same
underlying observation), so treating them as independent replicates would
inflate significance by orders of magnitude.

This is the single most common way a study like this overstates itself, and it
is forbidden here.

## Procedure — FROZEN

1. Compute metrics **per protected block** (three per discharge: A, B, C).
2. **Aggregate the three blocks within each discharge** to one value per
   discharge per method.
3. Treat **discharge** as the independent unit.
4. Report **paired differences** against each baseline — paired within
   discharge, since all methods are scored on identical samples (gate V7).
5. **Paired discharge bootstrap**: resample discharges with replacement,
   recomputing the paired difference each replicate.
6. **≥ 10,000 bootstrap replicates.** Seed fixed and recorded.
7. **95% confidence intervals** on every paired difference.
8. **Wins / ties / losses** by discharge, using the practical-equivalence floor
   (0.01 calibration-normalized RMSE) to define a tie.
9. **Leave-one-discharge-out sensitivity** — recompute the headline difference
   with each discharge removed, report the range.
10. **Report separately by processing era** — 35 earlier / 27 later in the
    object; in the external cohort, 24 earlier / 18 later.

## Primary metric

**Calibration-normalized RMSE** on protected blocks. Normalising by the
calibration-interval target scale makes discharges comparable **without any
protected-interval statistic entering the normalisation** — which whole-discharge
standardisation would violate.

## Reported alongside

Raw RMSE in the target's physical unit (interpretability); per-block breakdown
(does skill depend on trajectory position?); per-era breakdown; the LODO range.

## What will not be done

- No time samples treated as independent replicates.
- No unpaired tests where paired data exist.
- No p-value threshold used as a gate — gates are defined in
  `UTILITY_AND_QUALIFICATION_POLICY.md` and are about protocol compliance and
  predeclared effect comparisons, not significance.
- No selective reporting of favourable blocks, eras or discharges. All three
  blocks, both eras and all evaluated discharges are reported.
- No post-hoc metric substitution. The primary metric is fixed here.

## Interaction with the practical-equivalence rule

A difference within the floor is a **tie**, whatever its confidence interval. A
statistically resolvable but scientifically negligible difference does not
support a claim, and with 42 discharges and thousands of samples it is entirely
possible to resolve differences that do not matter.

## Deferred

- **S7.10:** executed bootstrap, CIs, win/tie/loss, era breakdown.
- **S7.11:** LODO and numerical-realization sensitivity.
