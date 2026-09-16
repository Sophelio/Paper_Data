# Coefficient Conditioning and Identifiability Audit

## 1. Executive verdict

**D3D-COEFFICIENT-FAMILY-RESOLVED**

Audit run: `D3D-SIR-62-COEFFICIENT-CONDITIONING-V1`  
Canonical run: `D3D-SIR-62-ALIGNED-V1`  
Seed: `20260805`

Conditional on the frozen seven-coordinate support, reconstruction is stable
(pooled RMSE = 0.05758467). Median spectral condition
number is 41.3. Between-discharge coefficient variation exceeds
within-discharge block-bootstrap uncertainty for
4 of 7 coefficients
(2 dominated by within-discharge uncertainty).
Multivariate analysis finds 5 positive
difference-covariance directions.

## 2. Scientific question

This audit asks whether the seven discharge-specific coefficients are
numerically identifiable and whether cross-discharge coefficient variation
exceeds within-discharge estimation uncertainty. It does **not** test unique
support selection, prediction on held-out data, or mechanism.

## 3. Canonical input and reproduction check

| Check | Result |
|-------|--------|
| Discharges | 62 |
| Samples / discharge | 1000 |
| Features | 7 (source_matrix_order) |
| Max \|Δcoef\| vs canonical | 2.220e-16 |
| Reproduced pooled RMSE | 0.05758467247445343 |
| Reference pooled RMSE | 0.05758467247445343 |
| Mean-vector RMSE | 0.4125238315775986 |
| Validation pass | True |

Source order: `['d[pcdiamag3]/d[kappa]', 'd[kappa]/d[t]', 'r[q95]/r[kappa]', 'd[pcdiamag3]/d[betan]', 'd[kappa]/d[betan]', 'd[betan]/d[t]', 'd[li]/d[betan]']`  
Manuscript display order: `['D_kappa W_dia', 'D_betaN W_dia', 'D_betaN kappa', 'D_betaN l_i', 'q95 / kappa', 'dot beta_N', 'dot kappa']`

Artifacts: `outputs/input_validation.json`, `tables/input_validation.csv`.

## 4. Design-matrix rank and singular spectra

Median κ₂ = **41.3202**, max κ₂ = **71.3167**.  
Median σ₇/σ₁ = **0.0242**.

Rank deficiency counts (rank < 7):

| τ | n_rank_lt_7 |
|---|------------:|
| 1e-12 | 0 |
| 1e-10 | 0 |
| 1e-08 | 0 |
| 1e-06 | 0 |

Figure: `figures/singular_spectrum_by_discharge.*`, `figures/condition_number_by_discharge.*`.  
Table: `tables/d3d_conditioning_per_discharge.csv`.

## 5. Correlation and VIF diagnostics

Highest max\|ρ\| feature pairs (cohort):

| feature_1 | feature_2 | max\|ρ\| | median\|ρ\| | frac\|ρ\|>0.9 |
|-----------|-----------|--------:|----------:|-------------:|
| `d[pcdiamag3]/d[betan]` | `d[betan]/d[t]` | 0.952 | 0.828 | 0.31 |
| `d[pcdiamag3]/d[kappa]` | `d[kappa]/d[betan]` | 0.942 | 0.205 | 0.06 |
| `d[kappa]/d[betan]` | `d[li]/d[betan]` | 0.894 | 0.774 | 0.00 |
| `d[betan]/d[t]` | `d[li]/d[betan]` | 0.865 | 0.791 | 0.00 |
| `d[kappa]/d[betan]` | `d[betan]/d[t]` | 0.844 | 0.745 | 0.00 |

VIF maxima by feature (finite values): median across discharges of per-feature VIF
distributions are reported in `tables/d3d_vif_per_discharge.csv`.  
Figures: `feature_correlation_summary.*`, `vif_distributions.*`.

## 6. Near-null coefficient directions

Median absolute loadings on v_min (weakest right singular vector):

| feature | median\|loading\| | freq largest\|loading\| |
|---------|------------------:|------------------------:|
| `d[pcdiamag3]/d[kappa]` | 0.270 | 0.05 |
| `d[kappa]/d[t]` | 0.396 | 0.00 |
| `r[q95]/r[kappa]` | 0.017 | 0.00 |
| `d[pcdiamag3]/d[betan]` | 0.335 | 0.00 |
| `d[kappa]/d[betan]` | 0.743 | 0.77 |
| `d[betan]/d[t]` | 0.332 | 0.18 |
| `d[li]/d[betan]` | 0.015 | 0.00 |

Figure: `near_null_direction_loadings.*`. These are weak-resolution directions, not physical laws.

## 7. Sensitivity to singular-value truncation

At τ = 1e-6, classification counts:

{
  "STABLE_COEFFICIENTS_STABLE_RECONSTRUCTION": 62
}

Median relative coefficient change at τ=1e-6:
2.811e-15;  
median \|ΔRMSE\| = 1.388e-17.

Figure: `coefficient_truncation_sensitivity.*`.

## 8. Temporal dependence and block-length selection

Primary block lengths (samples): median 58,
range [13, 116].  
Tables: `d3d_autocorrelation_summary.csv`, `d3d_bootstrap_block_lengths.csv`.

## 9. Time-block bootstrap coefficient uncertainty

Primary circular moving-block bootstrap: B = 1000 per discharge.  
Sensitivity: B = 300 at short/long blocks.

Across discharges, mean sign stability by feature:

| feature | median sign_stability | median relative bootstrap SD | frac intervals contain 0 |
|---------|----------------------:|-----------------------------:|-------------------------:|
| `d[pcdiamag3]/d[kappa]` | 1.000 | 1.13 | 0.06 |
| `d[kappa]/d[t]` | 1.000 | 0.112 | 0.00 |
| `r[q95]/r[kappa]` | 0.873 | 1.21 | 0.90 |
| `d[pcdiamag3]/d[betan]` | 1.000 | 0.25 | 0.03 |
| `d[kappa]/d[betan]` | 1.000 | 0.275 | 0.03 |
| `d[betan]/d[t]` | 0.992 | 0.335 | 0.27 |
| `d[li]/d[betan]` | 0.889 | 0.814 | 0.85 |

Figure: `bootstrap_coefficients_by_discharge.*`.  
Data: `outputs/d3d_bootstrap_coefficients_primary.parquet`.

## 10. Between-discharge versus within-discharge variation

| feature | s_B² | mean s_W² | H | resolved frac | τ | status |
|---------|-----:|----------:|--:|--------------:|--:|--------|
| `d[pcdiamag3]/d[kappa]` | 1.338e-02 | 7.263e-02 | 0.184 | 0.000 | 0 | WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES |
| `d[kappa]/d[t]` | 2.086e-01 | 2.064e-02 | 10.1 | 0.901 | 0.412 | BETWEEN_DISCHARGE_VARIATION_RESOLVED |
| `r[q95]/r[kappa]` | 2.193e-04 | 4.914e-04 | 0.446 | 0.000 | 0.00455 | WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES |
| `d[pcdiamag3]/d[betan]` | 1.297e-01 | 1.085e-01 | 1.2 | 0.164 | 0.261 | BETWEEN_DISCHARGE_VARIATION_PARTIALLY_RESOLVED |
| `d[kappa]/d[betan]` | 3.818e-01 | 1.448e-01 | 2.64 | 0.621 | 0.511 | BETWEEN_DISCHARGE_VARIATION_RESOLVED |
| `d[betan]/d[t]` | 2.390e-01 | 2.100e-02 | 11.4 | 0.912 | 0.46 | BETWEEN_DISCHARGE_VARIATION_RESOLVED |
| `d[li]/d[betan]` | 9.065e-04 | 2.417e-04 | 3.75 | 0.733 | 0.00869 | BETWEEN_DISCHARGE_VARIATION_RESOLVED |

Figures: `between_vs_within_variance.*`, `resolved_fraction_by_coefficient.*`.

## 11. Random-effects coefficient heterogeneity

Profile-likelihood Gaussian heteroscedastic random-effects estimates are in
`tables/d3d_coefficient_heterogeneity.csv` (columns `tau2_REML`, intervals).  
Diagnostics: `outputs/d3d_random_effects_diagnostics.json`.

## 12. Multivariate identifiable coefficient directions

Difference covariance Σ_B − Σ_W has
**5** positive eigenvalues under the declared threshold.  
Fraction of observed between variance surviving PSD-projected subtraction:
**0.802**.  
Figure: `multivariate_resolved_directions.*`.

## 13. Relationship between conditioning, uncertainty and RMSE

Median κ₂ ≈ 41.3 indicates generally mild ill-conditioning, not
extreme singularity. FDR-significant Spearman associations
(13 rows in `d3d_conditioning_associations_fdr.csv`) should be read as
associations only. Figures: `coefficient_uncertainty_vs_conditioning.*`,
`rmse_vs_conditioning.*`.

## 14. Supported interpretation

- The seven-term linear map reconstructs the standardized target with low error.
- Several coefficients show between-discharge variation larger than block-bootstrap
  within-discharge uncertainty.
- Coefficient uncertainty and reconstruction stability are not equivalent; truncation
  tests separate these notions.
- Near-null loadings identify compensating directions when present.

## 15. Explicit nonclaims

- Support uniqueness / structural selection is not tested.
- Causal or mechanistic meaning of coefficients is not established.
- Out-of-sample predictive validity is not assessed.
- Unshifted symbolic quotients are not claimed (coordinates are shifted/z-scored upstream).

## 16. Limitations

- Conditional on selected seven-term support; support uniqueness not tested.
- Block-bootstrap approximates temporal dependence; block length is estimated.
- Exact historical shift values remain UNKNOWN (inherited from canonical package).
- Random-effects model assumes Gaussian sampling distributions of coefficients.

Unresolved: ['EXACT_SHIFT_VALUE_UNKNOWN inherited from canonical package', 'Original structural-search hyperparameters UNKNOWN']

## 17. Machine-readable outputs

Primary summary: `outputs/coefficient_conditioning_summary.json`.  
See `AUDIT_FILE_INDEX.md` and `audit_manifest.json`.

## 18. Reproduction commands

```bat
cd /d D:\sir-web
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\run_coefficient_conditioning_audit.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\generate_conditioning_figures.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\write_conditioning_report.py"
```

## 19. Completion gates

| Gate | Status |
|------|--------|
| Output directory exact path | PASS |
| Canonical package unmodified | PASS (read-only) |
| 62×1000×7 | PASS |
| Source/manuscript order mapped | PASS |
| RMSE reproduction ≤1e-8 | PASS |
| SVD/rank/κ/VIF/near-null/truncation | PASS |
| Block bootstrap 1000 + sensitivity | PASS |
| Heterogeneity + REML-style τ² | PASS |
| Multivariate directions | PASS |
| FDR associations | PASS |
| Figures PDF/SVG/PNG | PASS (after figure script) |
| Markdown + LaTeX | PASS |
| Hashes | PASS (manifest) |
