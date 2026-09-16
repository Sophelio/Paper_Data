# D3D Design-Matrix Contract — D3D-SIR-62-ALIGNED-V1

## Identity

| Field | Value |
|-------|-------|
| canonical_run_id | `D3D-SIR-62-ALIGNED-V1` |
| artifact_status | `HISTORICAL_ORIGINAL` |
| feature export | `FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized/` |
| export manifest SHA-256 | see `d3d_design_matrix_manifest.json` |
| historical model | `RESULTS/output.pcdiamag3.psir` copied to `model_artifact/output.pcdiamag3.psir` |
| equation key | `1_8*` |

## Target and features

| Role | Column |
|------|--------|
| Target | `[d[pcdiamag3]/d[t]]` |
| Features (psir / OLS column order 1..7) | `[d[pcdiamag3]/d[kappa]]`, `[d[kappa]/d[t]]`, `[r[q95]/r[kappa]]`, `[d[pcdiamag3]/d[betan]]`, `[d[kappa]/d[betan]]`, `[d[betan]/d[t]]`, `[d[li]/d[betan]]` |
| Intercept | included (column 0 of coefficient vector) |

Semantic CSV coefficient order (Task B) remaps the same seven terms; see `d3d_discharge_coefficients.csv` header.

## Shapes and ordering

- Per discharge: features `1000 × 7`, target `1000`, time `1000`.
- Cohort: 62 discharges, 62 000 rows.
- `realization_index`: order of `filenames` in the historical `.psir` (matches NPZ shot order used in that run).
- `sample_index`: `0..999` along the provider `TARGET_N=1000` grid.
- Finite-row mask: all 62 000 export/psir samples finite; `prepare_discharge_reconstruction_data` would drop nonfinite rows (none dropped).

## Standardization

Export `manifest.json` records `normalization: "zscore"`. Per-file target mean≈0, std≈1. Feature columns are standardized in the export; they are **not** raw physical units.

## Fitting

- Historical predictions: `OUTPUT_PLOTTER.y_hat` using `1_8*` coefficient matrix `(62, 8)` and `O1_variables[i]` `(8, 1000)`.
- Rank/RSS metadata: `numpy.linalg.lstsq` on `[1 \| X]` from the export columns (matches historical coeffs to ≤1e-6).
- Tolerance: pooled RMSE must match references to `1e-12`.

## Hash representation

`numpy.ascontiguousarray(arr, dtype=float64).tobytes()` → SHA-256. Table: `d3d_design_matrix_hashes.csv`.

Machine-readable twin: `d3d_design_matrix_manifest.json`.
