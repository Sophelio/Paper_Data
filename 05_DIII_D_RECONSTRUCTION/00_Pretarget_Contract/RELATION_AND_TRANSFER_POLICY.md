# S7.2 — Relation form and transfer policy

## The transfer statement — FROZEN

> **The scientific coordinate support is shared. Numerical coefficients may be
> discharge-specific.**

A new discharge therefore uses:

```
frozen support  +  calibration-only coefficient estimation  ->  protected reconstruction
```

This is **not** universal fixed-coefficient transfer, and must never be
described as such.

## Operational sequence

1. **Development.** Coordinate support and relation form selected using
   development discharges only (20 shots).
2. **Freeze.** Support, relation form, estimator and all hyperparameters hashed
   and recorded. Nothing after this point may change them.
3. **External calibration.** On each external discharge, coefficients estimated
   from that discharge's calibration interval only.
4. **Protected scoring.** The frozen support, with locally calibrated
   coefficients, scored on protected intervals.

Step 2 is the discipline. Without it, step 3 makes the claim vacuous.

## Estimator — FROZEN

**A transparent linear estimator: ordinary least squares, or ridge with a
development-selected penalty.**

Chosen so that utility is attributable mainly to the **representation** rather
than to estimator sophistication. If a sophisticated estimator were used, a
positive result would be ambiguous between "the coordinates carry the
information" and "the estimator is strong" — and the study is about the former.

Ridge is permitted because the conditioning admissibility rules cannot guarantee
a well-conditioned design on every discharge's calibration interval. If ridge is
used:

- the penalty is selected on **development discharges only**;
- selection uses **calibration-fitted** statistics only, never protected values;
- the chosen penalty is **frozen before external evaluation** and applied
  unchanged;
- the same penalty-selection procedure is granted to baseline **B2**, so the
  comparison stays fair.

An intercept is fitted. (The Lorenz benchmarks in this project established that
a no-intercept estimator silently destroys performance when the target is not
centred — a failure worth not repeating.)

### If conditioning later forces a change

Any departure from a transparent linear estimator must be:

- justified by **numerical conditioning**, not by performance;
- decided on **development data only**;
- recorded in the decision ledger with the conditioning evidence;
- frozen before external evaluation;
- granted equally to baseline B2.

## Relation form

Linear in the **scientific coordinates**. Nonlinearity enters through the
coordinates themselves — products, ratios, derivatives, trajectory-relational
derivatives — not through the estimator. This is what makes the discovered
structure readable: the representation carries the physics and the estimator
carries only scale.

## Per-discharge calibration is granted to every comparator

Identical calibration intervals, identical protected samples, identical
estimator discipline for the relational representation and for **all four
baselines**. The question is never "does local calibration help?" — it helps
everything — but whether the relational support contributes **beyond** trivial
and raw-coordinate alternatives given the same calibration.

## Deferred

- **S7.7:** the selected support and relation form.
- **S7.9:** the frozen estimator, penalty and all hyperparameters, hashed.
- **S7.10:** external calibration and protected scoring.
