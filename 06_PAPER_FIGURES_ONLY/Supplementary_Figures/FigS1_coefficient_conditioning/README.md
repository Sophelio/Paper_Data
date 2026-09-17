# Supplementary Figure S1 — coefficient conditioning

Three panels assembled into one Supplement figure, all from the corrected
coefficient-conditioning audit.

| | |
|---|---|
| panel a | `d3d_coefficient_change_vs_rank_removed.pdf` — relative coefficient change and absolute RMSE change after removing the weakest singular directions |
| panel b | `d3d_heterogeneity_interval_by_coefficient.pdf` — REML between-discharge variance with profile-likelihood intervals |
| panel c | `d3d_multivariate_eigenvalue_uncertainty.pdf` — ordered eigenvalues of Σ_B − Σ_W with bootstrap intervals and matched-null thresholds |
| run | `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1` |
| script | `figure_source/generate_correction_figures.py`, driven by `figure_source/render_figS1.py` |
| regenerate | `python figure_source/render_figS1.py` (run from this folder; reads `figure_source_data/`, writes the three `d3d_` panels here) |
| inputs | `figure_source_data/` — the config and 11 tables the generator reads, copied verbatim from `04_DIII_D_DESCRIPTIVE/D3D-SIR-62-ALIGNED-V1/coefficient_conditioning/` |

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

## Polishing pass (2026-09-16)

See `../../README.md` for the standard. S1-specific points:

- The spec style is applied only to the three S1 plots, via `mpl.rc_context`. The
  other seven audit figures from the same generator are untouched, because their
  raw-underscore labels are not LaTeX-safe.
- Original canvases (10×4 in; 8×4.5 in) and original font sizes are kept.
- Panel b tick labels use the same coefficient notation as Figure 6.
- `render_figS1.py` writes all audit figures to a temporary directory and
  copies out only the three `d3d_` panels as PDF, PNG and SVG. The PNG/SVG
  variants are new to this folder. The input and output directories can also be
  set with the `CORRECTION_AUDIT_DIR` and `CORRECTION_FIGURE_DIR` environment
  variables; the script's defaults are unchanged.

## Self-contained (2026-09-17)

Everything S1 needs is in this folder. `render_figS1.py` needs no arguments:
`--audit-dir` defaults to `figure_source_data/Correction_audit` and `--out-dir`
to this folder. Both still accept other locations.

`figure_source_data/` keeps the audit tree's layout, because the generator reads
`Correction_audit/tables/` and also the parent `tables/`:

```
figure_source_data/
  Correction_audit/correction_audit_config.json
  Correction_audit/tables/   9 CSVs (TSVD, ridge path, heterogeneity, eigenvalue/loading intervals)
  tables/                    d3d_conditioning_per_discharge.csv, d3d_bootstrap_coefficient_summary.csv
```

Each file is byte-identical to its counterpart under
`04_DIII_D_DESCRIPTIVE/D3D-SIR-62-ALIGNED-V1/coefficient_conditioning/`. The generator
reads all 12 up front, including inputs for the seven non-S1 audit figures.

`correction_audit_utils.py` was removed from `figure_source/`. Neither script
imports it, and it could not be imported from here because it imports
`coefficient_conditioning_utils` from the audit tree. The canonical copy stays in
`04_DIII_D_DESCRIPTIVE/.../Correction_audit/`.

Verified by running a copy of this folder on its own, outside the repository:
all three PNGs reproduced pixel-for-pixel.
- The pre-polish PDFs were confirmed to reproduce pixel-for-pixel from this
  generator before editing.
