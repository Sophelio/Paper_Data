# DIII-D Coefficient Conditioning Correction Audit

## 1. Executive verdict

**D3D-MIXED-COEFFICIENT-IDENTIFIABILITY**

Correction audit: `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1`  
Original audit: `D3D-SIR-62-COEFFICIENT-CONDITIONING-V1`  
Canonical run: `D3D-SIR-62-ALIGNED-V1`  
Seed: `20260805`

After correcting non-diagnostic truncation thresholds, REML labeling, block-length
and leave-one-out heterogeneity confirmation, and multivariate eigenvalue
uncertainty testing:

- robustly resolved coefficients: **5**
- partially resolved: **0**
- within-discharge uncertainty dominates: **2**
- indeterminate: **0**
- original positive multivariate directions: **5**
- corrected robust multivariate directions: **2**

Reconstruction remains stable (pooled RMSE = 0.05758467247445343).
Coefficient identifiability is **not** uniformly resolved across all seven terms.

## 2. Reason for the correction audit

The original audit established exact RMSE reproduction and mild spectral
conditioning, but four limitations required correction:

1. Original truncated-SVD thresholds (≤1e-6) removed **no** singular directions.
2. Heterogeneity labels used descriptive thresholds without full interval/block/LOO confirmation.
3. Positive eigenvalues of Σ_B−Σ_W were counted without sampling/null uncertainty.
4. A stale `outputs/CONTRADICTION_REPORT.txt` remained after successful validation.

## 3. Canonical and original-audit input validation

| Check | Result |
|-------|--------|
| Pass | True |
| Discharges | 62 |
| Samples/discharge | 1000 |
| Features | 7 |
| Reproduced pooled RMSE | 0.05758467247445343 |
| Mean-vector RMSE | 0.4125238315775986 |
| Max \|Δcoef\| | 2.220e-16 |

All input artifacts used by this correction audit were SHA-256 hashed
(`outputs/correction_input_validation.json`).

## 4. Why the original truncation test removed no directions

Original truncation thresholds retained rank 7 for every discharge; coefficient changes near machine precision reflect recomputation of the unchanged full-rank solution, not genuine singular-direction removal.

Minimum normalized σ₇ across discharges: **0.014022**  
(median ≈ 0.0242013).  
All original thresholds retained rank 7:
**True**.

Therefore near-machine-precision coefficient changes in the original truncation
table reflect recomputation of the unchanged full-rank solution.

Table: `tables/original_truncation_effectiveness.csv`.

## 5. Fixed-threshold spectral truncation results

Meaningful relative thresholds were applied to the centered-feature SVD used by
the canonical OLS-equivalent solver.

Median relative coefficient change by τ:

| τ | median relative \|Δc\| |
|---|----------------------:|
| 0.001 | 2.79177e-15 |
| 0.005 | 2.79177e-15 |
| 0.01 | 2.79177e-15 |
| 0.02 | 3.70604e-15 |
| 0.05 | 0.823449 |
| 0.1 | 0.827509 |

At τ=0.05 and 0.1, coefficient vectors move substantially. At τ≤0.02 most
discharges remain near the full-rank solution because σ₇/σ₁ typically exceeds 0.014.

Figure: `figures/actual_singular_direction_removal.*`.

## 6. Fixed-rank truncation results

Rank-7 reproduces canonical coefficients
(max relative change 8.619e-15).

| retained rank | median rel. coef. change | median \|ΔRMSE\| |
|--------------:|-------------------------:|------------------:|
| 7 | 2.79177e-15 | 1.38778e-17 |
| 6 | 0.799315 | 0.0310296 |
| 5 | 0.827509 | 0.0413436 |
| 4 | 0.885688 | 0.189173 |

Rank-6 class counts: `{"LARGE_COEFFICIENT_MOVEMENT_CHANGED_RECONSTRUCTION": 40, "LARGE_COEFFICIENT_MOVEMENT_STABLE_RECONSTRUCTION": 18, "STABLE_COEFFICIENTS_STABLE_RECONSTRUCTION": 4}`.

Median rank-6 relative coefficient change:
**0.7993**;  
median absolute RMSE change:
**0.03103**.

Removing the weakest direction typically produces **large coefficient movement**
with a **moderate reconstruction change** (median \|ΔRMSE\|≈0.031), confirming
that reconstruction stability does not imply coefficient uniqueness along the
weakest singular direction.

Figure: `figures/coefficient_change_vs_rank_removed.*`.

## 7. Ridge-path sensitivity

Ridge on column-standardized features (intercept unpenalized;
λ = λ_rel · σ₁²) produces continuous coefficient shrinkage.

Median relative coefficient change by λ_rel:  
`{"0.0": 2.5615596024309465e-15, "1e-06": 0.0011569985572081527, "1e-05": 0.011433555896960962, "0.0001": 0.10227625254308229, "0.001": 0.48023147170337804, "0.01": 0.7791576518226064, "0.1": 0.8715477695177771, "1.0": 0.9607738974200898}`

Figure: `figures/ridge_path_coefficient_stability.*`.  
Ridge is a sensitivity analysis only; canonical OLS coefficients are retained.

## 8. Random-effects estimator audit

Inspection of `profile_tau2` shows a **profile maximum-likelihood** objective,
not REML. The original columns labeled `tau2_REML` were therefore misnamed.

See `RANDOM_EFFECTS_ESTIMATOR_AUDIT.md`.

Corrected primary estimator: heteroscedastic **REML** random-intercept
meta-analysis with known discharge-specific bootstrap variances. ML is retained
as sensitivity. Profile-likelihood intervals and 5,000-replicate discharge
bootstraps are reported.

## 9. Corrected coefficient-wise heterogeneity

| display | source feature | original | corrected | H | τ²_REML | profile interval | short τ² | long τ² | LOO frac(τ²>0) |
|---------|----------------|----------|-----------|--:|--------:|------------------:|---------:|--------:|---------------:|
| `D_kappa W_dia` | `d[pcdiamag3]/d[kappa]` | WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES | **WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES** | 0.184 | 0 | [0, 0.00577] | 0.000619 | 0 | 0.00 |
| `dot kappa` | `d[kappa]/d[t]` | BETWEEN_DISCHARGE_VARIATION_RESOLVED | **ROBUSTLY_RESOLVED** | 10.1 | 0.184 | [0.124, 0.254] | 0.184 | 0.17 | 1.00 |
| `q95 / kappa` | `r[q95]/r[kappa]` | WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES | **WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES** | 0.446 | 2.37e-05 | [0, 7.8e-05] | 1.22e-05 | 1.95e-05 | 0.98 |
| `D_betaN W_dia` | `d[pcdiamag3]/d[betan]` | BETWEEN_DISCHARGE_VARIATION_PARTIALLY_RESOLVED | **ROBUSTLY_RESOLVED** | 1.2 | 0.0697 | [0.0371, 0.121] | 0.0884 | 0.0644 | 1.00 |
| `D_betaN kappa` | `d[kappa]/d[betan]` | BETWEEN_DISCHARGE_VARIATION_RESOLVED | **ROBUSTLY_RESOLVED** | 2.64 | 0.267 | [0.164, 0.4] | 0.289 | 0.246 | 1.00 |
| `dot beta_N` | `d[betan]/d[t]` | BETWEEN_DISCHARGE_VARIATION_RESOLVED | **ROBUSTLY_RESOLVED** | 11.4 | 0.208 | [0.151, 0.31] | 0.225 | 0.208 | 1.00 |
| `D_betaN l_i` | `d[li]/d[betan]` | BETWEEN_DISCHARGE_VARIATION_RESOLVED | **ROBUSTLY_RESOLVED** | 3.75 | 7.84e-05 | [3.2e-05, 0.000167] | 9e-05 | 7.84e-05 | 1.00 |

## 10. Block-length robustness

Primary (B=1000), short and long (B=300) within-discharge variances were
compared. Cohort median variance ratios and feature-level block dependence are
in `outputs/block_length_robustness_summary.json` and
`tables/block_length_robustness_summary.csv`.

Monte Carlo uncertainty for B=300 variance estimates is quantified; no
near-boundary coefficient required a forced 1,000-replicate sensitivity re-run
beyond the existing files for the final classifications above.

## 11. Leave-one-discharge-out robustness

LOO τ² ranges and positivity fractions are in
`tables/corrected_coefficient_heterogeneity_leave_one_out.csv`.  
No robust classification is driven by a single discharge
(`single_discharge_driver=False` for all robust terms).

Figure: `figures/leave_one_out_heterogeneity.*`.

## 12. Multivariate eigenvalue uncertainty

Discharge-level bootstrap (B=5000) of ordered
eigenvalues of Σ_B−mean(Σ_W):

| index | observed | bootstrap 95% | null 95% | status |
|------:|---------:|--------------:|---------:|--------|
| 1 | 0.777 | [0.5777, 0.9218] | 0.1331 | ROBUSTLY_RESOLVED_DIRECTION |
| 2 | 0.002895 | [0.001304, 0.00478] | 0.01567 | POSITIVE_POINT_ESTIMATE_ONLY |
| 3 | 0.0008894 | [0.0003604, 0.001452] | 0.0005816 | ROBUSTLY_RESOLVED_DIRECTION |
| 4 | 0.0001491 | [-4.312e-06, 0.0004096] | 0.0001113 | POSITIVE_POINT_ESTIMATE_ONLY |
| 5 | 5.097e-05 | [-0.0003179, 7.832e-05] | -1.326e-05 | POSITIVE_POINT_ESTIMATE_ONLY |
| 6 | -0.0004341 | [-0.0007402, -0.0002819] | -0.00015 | NOT_RESOLVED |
| 7 | -0.1753 | [-0.2229, -0.1383] | -0.0006509 | NOT_RESOLVED |

## 13. No-heterogeneity null results

Under a null with common latent coefficient mean and resampled within-discharge
bootstrap deviations (B=5000), only directions whose observed
eigenvalue exceeds the null 95th percentile **and** whose bootstrap lower bound
is positive are labeled robust.

Result: **2** robust directions
(indices [1, 3]), versus
**5** positive point estimates originally.

Subspace stability: `{"n_directions": 2, "median_principal_angles_deg": [1.5823026543634462, 20.191697061003428], "q95_max_principal_angle_deg": 38.08768262919187}`.

## 14. Conditioning associations

Spearman associations between conditioning diagnostics and coefficient
uncertainty/influence, with BH-FDR control, are in
`tables/corrected_conditioning_heterogeneity_associations_fdr.csv`.  
These are associative, not causal.

Median κ₂ remains mild (~41); heterogeneity is **not** classified as
conditioning-dominated.

## 15. Corrected individual coefficient classifications

- **ROBUSTLY_RESOLVED** (5):
  dot kappa, D_betaN W_dia, D_betaN kappa, dot beta_N, D_betaN l_i
- **WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES** (2):
  D_kappa W_dia, q95 / kappa

## 16. Corrected multivariate classification

Robust directions: 2  
Positive point estimates only: 3  
Not resolved: 2

## 17. Corrected overall verdict

**D3D-MIXED-COEFFICIENT-IDENTIFIABILITY**

Sub-verdicts: `{
  "design_matrix_rank": "FULL_RANK_7_ALL_DISCHARGES",
  "numerical_conditioning": "MILD_MEDIAN_KAPPA_LT_100",
  "reconstruction_stability": "STABLE_DISCHARGE_SPECIFIC_RMSE",
  "individual_coefficient_identifiability": "ROBUST=5, PARTIAL=0, WITHIN=2, INDET=0",
  "multivariate_coefficient_identifiability": "ROBUST_DIRECTIONS=2",
  "robustness_to_block_length": "SEE_BLOCK_LENGTH_SUMMARY",
  "robustness_to_singular_direction_removal": "SEE_FIXED_RANK_TSVD"
}`

The previous verdict `D3D-COEFFICIENT-FAMILY-RESOLVED` is **not** retained.
Not all seven coefficients are robustly resolved, and two terms remain
uncertainty-dominated.

## 18. Supported interpretation

Conditional on the frozen seven-coordinate support:

1. Discharge-specific reconstructions are numerically stable.
2. Design matrices are full rank with mild spectral condition numbers.
3. Several coefficients exhibit between-discharge variation exceeding
   within-discharge block-bootstrap uncertainty after REML-based confirmation.
4. At least two coefficients are not resolved beyond within-discharge uncertainty.
5. Only a subset of multivariate coefficient directions survives bootstrap and
   null testing.
6. Removing the weakest singular direction can move coefficients materially
   while changing RMSE only moderately — reconstruction stability ≠ coefficient uniqueness.

## 19. Explicit nonclaims

- Support uniqueness / structural selection uniqueness: **not tested**.
- Mechanistic or causal interpretation of coefficients: **not established**.
- Predictive generalization to held-out discharges: **not claimed**.
- Near-null singular directions are **not** physical laws.
- Original `tau2_REML` labels were **not** true REML.

## 20. Remaining limitations

- Conditional on selected support; support uniqueness not tested.
- Block bootstrap approximates temporal dependence.
- REML assumes Gaussian sampling distributions of coefficient estimates.
- Eigenvalue ordering can switch for poorly separated eigenvalues.

Unresolved: EXACT_SHIFT_VALUE_UNKNOWN inherited from canonical package, Structural-search hyperparameters UNKNOWN

## 21. Stale-artifact resolution

Status: **ARCHIVED_AND_REMOVED_FROM_ACTIVE_OUTPUTS**  
See `STALE_ARTIFACT_RESOLUTION.md` and
`archived_artifacts/superseded_CONTRADICTION_REPORT.txt`.

## 22. Machine-readable outputs

Primary summary: `outputs/coefficient_conditioning_correction_summary.json`

## 23. Reproduction commands

```bat
cd /d D:\sir-web
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\Correction_audit\run_correction_audit.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\Correction_audit\generate_correction_figures.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\Correction_audit\write_correction_report.py"
```

## 24. Completion gates

| Gate | Status |
|------|--------|
| Correction_audit path | PASS |
| Canonical/manuscript unmodified | PASS |
| RMSE reproduction | PASS |
| Original truncation non-diagnostic | PASS |
| Meaningful TSVD + ridge | PASS |
| REML naming corrected | PASS |
| Block/LOO heterogeneity | PASS |
| 5000 eigen bootstrap + null | PASS |
| Robust MV vs point estimate | PASS |
| Stale artifact archived | PASS |
| Corrected verdict framework | PASS |
| Figures/LaTeX/hashes | PASS (after figure/report scripts) |
