# S7.2 — Preprocessing and leakage policy

Machine-readable: `leakage_matrix.csv` (25 operations).

## The rule

> **Every fitted transform is estimated from the allowed calibration data only,
> then applied unchanged to the protected interval.**

Applies to development folds and to external calibration/test blocks alike.

### Fitted quantities covered

mean · standard deviation · min/max · clipping thresholds · imputation
parameters · scaler parameters · learned smoothing parameters · regularization
hyperparameters · dimensional-reduction maps · model coefficients.

If a number is *estimated from data*, it is a fitted quantity and this rule
binds it. The list is illustrative, not exhaustive.

---

## The predictor asymmetry

This is the subtle point of the whole protocol.

| | Inside the protected block |
|---|---|
| **Predictor values** | **ALLOWED** |
| **Target values** | **FORBIDDEN** |

Using predictor values inside the protected block is not leakage, because this
is **contemporaneous reconstruction**: the predictors are observed at the same
instants as the target being reconstructed. That is the task.

Using protected **target** values for anything except final scoring is leakage.

The asymmetry is why the task is reconstruction and not forecasting, and why the
predictor rule is permissive while the target rule is strict.

---

## Whole-discharge z-scoring is FORBIDDEN for primary evaluation

S7.1 recorded that the historical pipeline applied within-discharge z-scoring
(`ddof=0`, no pooled statistics). For **target** standardisation that is a
leak under this protocol: the discharge-wide mean and standard deviation are
computed over samples that include the protected intervals.

> **No whole-discharge z-scoring may be used for the primary protected
> evaluation if its statistics include protected target values.**

Permitted instead:

- **calibration-fitted** target standardisation — statistics from the
  calibration interval only, applied unchanged to the protected block;
- whole-discharge standardisation of **predictors** only, if declared — though
  calibration-fitted is preferred for consistency;
- whole-discharge z-scoring in an explicitly labelled **historical-comparability
  run**, never as the primary evidential path.

This has a concrete consequence: **RMSE is reported in calibration-normalised
units**, so it is comparable across discharges without any protected-interval
statistic entering the normalisation.

---

## Numerical realizations

The three realizations (unsmoothed, spline `k=5 s=0.1`, RTS `R=1 Q=1e-4`) are
**analyst-defined numerical choices**, not observational uncertainty — `E` is
not instantiated.

- The primary realization is declared **before** search and frozen.
- Smoothing parameters are **not** selected using protected intervals.
- Alternative realizations are reported at S7.11 as a **sensitivity study**,
  explicitly labelled as an analyst-defined qualification procedure.

---

## Audit requirement

Every fitted quantity used in external evaluation records: what was fitted, from
which interval, at what stage, and confirmation that no protected sample entered
it. This audit is a precondition for gate **V1**.

## Deferred

- **S7.9:** the instantiated list of fitted transforms and their freeze hashes.
- **S7.10:** the executed leakage audit against that list.
