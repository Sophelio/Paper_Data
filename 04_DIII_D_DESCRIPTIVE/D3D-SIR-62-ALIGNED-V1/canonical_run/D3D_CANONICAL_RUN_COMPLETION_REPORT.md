# D3D Canonical Run Completion Report — D3D-SIR-62-ALIGNED-V1

## 1. Executive verdict

**D3D-CANONICAL-62SHOT-RECONSTRUCTION-PACKAGE-CLOSED-WITH-HISTORICAL-LINEAGE-GAPS**

Historical model artifact **found and verified** (`output.pcdiamag3.psir`, equation `1_8*`, 62×1000).  
Structural-search UI hyperparameters and exact `shiftval` numerics remain **UNKNOWN**.  
No manuscript files modified.

## 2. What was already established

- 62 discharges × 1000 samples; ~4.1–6.0 ms grids; eight-signal ontology.
- Seven-term support; per-discharge RMSE ≈ 0.05758467; mean-vector RMSE ≈ 0.41252383.
- Retrospective, target-containing analysis.

## 3. New artifacts generated

See `CANONICAL_RUN_FILE_INDEX.md` under `canonical_d3d_62_shot_run_v1/`.

## 4. Historical model artifact status

| Item | Value |
|------|-------|
| Found | **yes** |
| Original path | `RESULTS/output.pcdiamag3.psir` |
| Package copy | `model_artifact/output.pcdiamag3.psir` |
| Status | `HISTORICAL_ORIGINAL` |
| Equation key | `1_8*` (calibrated); `1_8` also present |
| Realizations | 62 |
| Coeff shape | (62, 8) |
| Verified pooled RMSE | 0.05758467247445343 |

## 5. Numerical reproduction

| Metric | Value | Reference | \|Δ\| |
|--------|------:|----------:|----:|
| Per-discharge pooled RMSE | 0.05758467247445343 | 0.05758467247445343 | 0.0 |
| Mean-vector pooled RMSE | 0.4125238315775986 | 0.4125238315775986 | 0.0 |
| Median-error shot | 165031 | — | — |

## 6. Exact coefficient and prediction lineage

`filenames[i]` → shot → export parquet ↔ `O1_variables[i]` / `output.x[i]` / `1_8*.x[i]` → predictions in `d3d_discharge_predictions.parquet`.  
Coefficient CSV uses semantic column names; values taken from historical `1_8*` rows.

## 7. Coordinate-construction findings

Shifted quotients/phaseders via `get_shiftval` + `make_Quotients(..., add_inverse=True)`; export z-scored. Exact shift numbers: **EXACT_SHIFT_VALUE_UNKNOWN**.

## 8. Structural-search provenance findings

Support and calibrated coeffs **RESOLVED** from `.psir`. Discovery hyperparameters **UNKNOWN**. Current `.bin/settings.json` is **not** claimed as the discovery configuration.

## 9. Remaining UNKNOWN fields

- EXACT_SHIFT_VALUE_UNKNOWN for get_shiftval on the historical export-generating run
- ORIGINAL structural-search checklist / data_processing list at discovery time PARTIALLY UNKNOWN
- Whether discovery used pooled search then per-realization calibration: evidenced by 1_8 vs 1_8* but full UI settings at discovery UNKNOWN
- Random seeds / n_starts for SUBOPTIMAL_SEARCH: UNKNOWN

## 10. Contradictions

None.

## 11. Manuscript implications

- Use **discharge-specific** RMSE ≈ **0.0576** when citing interactive / calibrated reconstruction.
- Use **0.4125** only when citing the cohort-mean coefficient vector applied universally.
- Do not treat unshifted `a/b` identities as the exported coordinates.

## 12. Reproduction commands

```bash
conda activate sir_web
cd D:/sir-web
python "Paper Examples/Relational Coordinates for Multimodal Plasma Observations/canonical_d3d_62_shot_run_v1/build_canonical_run_package.py"
python "Paper Examples/Relational Coordinates for Multimodal Plasma Observations/canonical_d3d_62_shot_run_v1/write_package_docs.py"
```

## 13. Completion gates

| Gate | Status |
|------|--------|
| Permanent run ID assigned | PASS (`D3D-SIR-62-ALIGNED-V1`) |
| 62 discharges | PASS |
| 62 coefficient rows | PASS |
| 62 000 prediction rows | PASS |
| Seven features declared order | PASS |
| Per-discharge RMSE reproduced | PASS |
| Mean-vector RMSE reproduced | PASS |
| Model artifact preserved/declared | PASS (HISTORICAL_ORIGINAL) |
| Export/manifest hashes | PASS |
| Design-matrix hashes | PASS |
| Coordinate path traced | PASS (shift value UNKNOWN) |
| Shift/mask policy | PARTIAL (policy known; value UNKNOWN) |
| Structural-search recovery | PARTIAL |
| No unsupported default inference | PASS |
| Artifacts hashed | PASS |
| UNKNOWN listed | PASS |
| No manuscript modified | PASS |
| No silent overwrite of scientific outputs | PASS (new versioned dir) |
