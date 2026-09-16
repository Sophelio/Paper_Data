# Exact Coordinate, Implicit Elimination and Denominator Conditioning Audit

## 1. Executive verdict

**D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED**

Audit: `D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1`  
Canonical: `D3D-SIR-62-ALIGNED-V1`  
Coefficient correction: `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1`

Exact shifted Y-phaseder coordinates were recovered from the historical `.psir`
and reproduced with maximum absolute error **0.0**.
The eliminated target Jacobian coefficient \(A\) has pooled minimum
|2.64e-07|, q01=0.000508, median=0.0297,
with **5444** sign crossings and **19.3%** of rows
having |A|<0.01. Explicit closure RMSE is **187** versus implicit
residual RMSE **0.057585** (coverage 1.000).

## 2. Scientific question

Is the target-containing implicit closure locally well posed after exact
coordinate recovery, and does a small implicit residual amplify into a large
explicit target error through \(1/|A|\)?

## 3. Scope and explicit nonclaims

This audit does **not** test support uniqueness, causal mechanism, predictive
transfer, structural-selection stability, or matched-complexity nulls.

## 4. Canonical input validation

| Check | Value |
|-------|------|
| Pass | True |
| Pooled RMSE | 0.05758467247445343 |
| Mean-vector RMSE | 0.4125238315775986 |
| Discharges × samples | 62 × 1000 |

## 5. Historical coordinate lineage

Status: **D3D-EXACT-COORDINATE-LINEAGE-RESOLVED**

Y-phaseders: `z = ((dy + s)/(dx + s) - μ)/σ` with per-discharge `s` from
`meanSTDinfo.consummer_function[i].shiftval`. See `EXACT_COORDINATE_LINEAGE.md`
and `code_snapshots/`.

## 6. Shift-value recovery

Status: **EXACT_FROM_SERIALIZED_STATE**

Range: [14.643162, 24.242616], mean 19.111050.  
Historical `nmin` UI value: **UNKNOWN**.

## 7. Exact reproduction of the seven selected coordinates

All seven features: **EXACTLY_REPRODUCED** (max abs diff 0 for every feature).

See `tables/feature_reproduction_summary.csv` (all seven features EXACTLY_REPRODUCED, max abs diff 0).


## 8. Algorithmic target-dependence detection

Exactly two selected features contain the target: `d[pcdiamag3]/d[kappa]`,
`d[pcdiamag3]/d[betan]`. Affine second-difference tests pass
(`outputs/target_dependence.json`).

## 9. Exact affine target decomposition

`α = 1/(σ(d+s))`, `β = s/(σ(d+s)) − μ/σ`. Full 62 000-row arrays in
`outputs/target_affine_coefficients.parquet`.

## 10. Exact eliminated implicit relation

`A = 1 − c_κ α_κ − c_β α_β`, `ε = A y − B = y − ŷ`.  
Max identity error: **7.896e-15** (tol 1e-10).

## 11. Primitive denominator conditioning

Implemented denominators are `d + shiftval` (and `r_κ + s` for q95/κ).  
Crossing events and threshold fractions:
`tables/primitive_denominator_*.csv`.

## 12. Conditioning of eliminated A

| Statistic | Value |
|-----------|------:|
| min \|A\| | 2.64282e-07 |
| q01 \|A\| | 0.000507825 |
| median \|A\| | 0.0296846 |
| sign crossings | 5444 |
| frac \|A\|<1e-3 | 0.0201 |
| frac \|A\|<1e-2 | 0.1934 |
| frac \|A\|<1e-1 | 0.9256 |

## 13. Explicit closure and residual amplification

| Metric | Value |
|--------|------:|
| coverage | 1.000000 |
| pooled explicit RMSE | 187.227 |
| pooled implicit RMSE | 0.0575847 |
| median 1/\|A\| | 33.6875 |
| q95 1/\|A\| | 392.083 |
| Spearman(log\|A\|, log\|e\|) | -0.373 |

Identity `y − B/A = ε/A` holds (max error 1.315e-08).

## 14. Pole-like versus jointly degenerate regions

See `tables/local_degeneracy_classification.csv` and
`tables/A_zero_crossing_events.csv`.

## 15. Origin of small A

`A = 1 − F_κ − F_β` with `F = c·α`. Feedback medians and cancellation
diagnostics: `tables/target_feedback_decomposition.csv`.

## 16–17. Shift-policy sensitivity

See frozen/refit CSV tables for the full multiplier path. Key implicit RMSE
values are restated in the console summary and LaTeX section.

Refit coefficient changes: `tables/shift_sensitivity_refit.csv`.

## 18. Time-unit and standardization audit

STANDARDIZED_TEMPORAL_DERIVATIVES_INVARIANT_SHIFTED_RATIOS_REQUIRE_MATCHED_SHIFT_UNITS

## 19. Discharge-level heterogeneity in conditioning

Min \|A\| ranges from 2.64e-07 to 0.00256 across discharges
(`tables/eliminated_A_per_discharge.csv`).

## 20. Supported interpretation

The canonical DIII-D relation is an exact target-containing implicit closure
in historically shifted, doubly standardized Y-phaseders. Reconstruction of
the implicit residual is stable, but eliminating for the standardized target
is frequently ill conditioned: |A| is often small and crosses zero thousands
of times, amplifying residuals into large explicit errors.

## 21. Explicit nonclaims

- Support uniqueness not tested
- Causal/mechanistic interpretation not established
- Predictive transfer not tested
- Matched-complexity nulls not tested

## 22. Remaining limitations

- Historical nmin UI value UNKNOWN (effective shiftval known).
- Shift sensitivity uses canonical pre-zscore mu/sigma for frozen-model branch.
- Level/X-phaseder reconstruction depends on combination ordering matching consumer.

## 23. Implications for the main text

Any claim that the fitted relation “predicts” `dW/dt` explicitly must be
qualified by the A-conditioning results. Low implicit RMSE alone does not
establish a well-posed explicit target map.

## 24. Machine-readable outputs

`outputs/implicit_conditioning_summary.json`

## 25. Reproduction commands

```bat
cd /d D:\sir-web
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\run_implicit_conditioning_audit.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\generate_implicit_conditioning_figures.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\write_implicit_conditioning_report.py"
pytest "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\tests" -q
```

## 26. Completion gates

All required gates for exact lineage, shift recovery, reproduction, elimination
identity, A/denominator diagnostics, sensitivity, figures, LaTeX and hashes
are satisfied by the generated artifacts in this directory.
