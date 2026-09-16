# DIII-D descriptive branch — `q_desc`

**Run `D3D-SIR-62-ALIGNED-V1`.** Supports Results 1.5 and Supplement S7.1–S7.7,
and panels a–b of the DIII-D figure.

## The result

A shared **seven-coordinate** relational support organizes standardized
`dW_dia/dt` across 62 discharges, with **discharge-specific** coefficients.

| | |
|---|---|
| pooled RMSE | **0.05758467247445343** |
| pooled MSE | 0.0033159945039900746 |
| cohort-mean-vector RMSE | 0.4125238315775986 |
| samples | 62000 (62 × 1000) |

The gap between those two RMSE values is the point: the reported figure is a
discharge-specific fit on a shared support, **not** one universal equation.

## Qualification

| audit | verdict |
|---|---|
| coefficient identifiability | `D3D-MIXED-COEFFICIENT-IDENTIFIABILITY` — 5 robust, 2 uncertainty-dominated |
| multivariate directions | 2 robust of 5 positive |
| rank-6 truncation | 0.7993 median relative coefficient change, 0.0310 median RMSE change |
| random-effects estimator | `REML_primary_with_ML_sensitivity` |
| implicit closure | `D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED` |

## Canonical vs superseded — read this

`coefficient_conditioning/` contains **both** audits:

- `Correction_audit/` — **CANONICAL**. Verdict `D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`.
- everything above it — **SUPERSEDED**. The original carried the retired verdict
  `D3D-COEFFICIENT-FAMILY-RESOLVED` and mislabelled profile-ML as REML.

The original is retained because the manuscript documents its correction. Do not
quote it as a current result. `Correction_audit/STALE_ARTIFACT_RESOLUTION.md`
records the archival.

## Interpretation limits

Target-containing implicit closure, not an independent predictor. Not causal. The
coefficients are not dimensional physical constants.
