# Supplementary Figure S1 — coefficient conditioning

Three panels assembled into one Supplement figure, all from the corrected
coefficient-conditioning audit.

| | |
|---|---|
| panel a | `d3d_coefficient_change_vs_rank_removed.pdf` — relative coefficient change and absolute RMSE change after removing the weakest singular directions |
| panel b | `d3d_heterogeneity_interval_by_coefficient.pdf` — REML between-discharge variance with profile-likelihood intervals |
| panel c | `d3d_multivariate_eigenvalue_uncertainty.pdf` — ordered eigenvalues of Σ_B − Σ_W with bootstrap intervals and matched-null thresholds |
| run | `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1` |
| script | `figure_source/generate_correction_figures.py` |
| inputs | `04_DIII_D_DESCRIPTIVE/.../Correction_audit/outputs` and `/tables` |

## Assembly

The three panels are separate PDFs; composition into a single figure happens in
the manuscript, not in the script. **That is a manual step.**

## Note on file variants

Only the `d3d_`-prefixed **PDF** assets exist. PNG and SVG variants exist under
the un-prefixed names (`coefficient_change_vs_rank_removed.png`, etc.), and the
Correction_audit manifest additionally lists three un-prefixed PDFs that are
absent — 74 of its 77 entries reproduce. Recorded in
`90_AUDIT_REPORTS/missing_artifacts.csv`. No numerical result is affected.

## Canonical, not superseded

These panels come from the **Correction_audit**, whose verdict is
`D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`. The original audit in the parent
directory carried the retired verdict `D3D-COEFFICIENT-FAMILY-RESOLVED` and
mislabelled profile-ML as REML. Do not plot from the original.
