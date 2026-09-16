# Stale artifact resolution

## Finding

`Coefficient_conditioning/outputs/CONTRADICTION_REPORT.txt` was a **stale**
artifact from an earlier Phase-0 attempt. Its content reports
`pass: false` because the cohort-mean-vector RMSE was computed from the
empirical mean of discharge-specific coefficients
(`reproduced_mean_vector_rmse ≈ 0.412575`), which differs from the canonical
reference based on the hard-coded `D3D_RELATION` vector
(`0.4125238315775986`).

The successful current audit (`outputs/input_validation.json`) reports
`pass: true` with both RMSE values matched to machine/tolerance precision.

## Actions

1. Copied the file to `Correction_audit/archived_artifacts/superseded_CONTRADICTION_REPORT.txt`
2. Recorded SHA-256 and metadata in `superseded_CONTRADICTION_REPORT_metadata.json`
3. Removed the active copy from `Coefficient_conditioning/outputs/`
4. Wrote `Coefficient_conditioning/MANIFEST_CORRECTION_RECORD.json`
5. Marked the original manifest entry `SUPERSEDED_ARCHIVED`

## Status

`ARCHIVED_AND_REMOVED_FROM_ACTIVE_OUTPUTS`

Original SHA-256: `54a5706ad5fd889f88b8b68065c0921edeb1adbd47f84d4bae4751bb22b87f43`
