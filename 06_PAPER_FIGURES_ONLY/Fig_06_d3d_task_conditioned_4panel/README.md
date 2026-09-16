# Figure 6

DIII-D task-conditioned relational discovery: descriptive organization and coefficient heterogeneity (q_desc, panels a-b); support plurality across six folds and target-cross-fitted reconstruction (q_rec, panels c-d).

| | |
|---|---|
| manuscript figure | **Figure 6** |
| final asset | `d3d_task_conditioned_4panel_v5.pdf` |
| generation script | `d3d_task_conditioned_4panel_v5.py` |
| input data | figure_source_data/ — 11 frozen files from DIIID_example/fig6data |
| source run | D3D-SIR-62-ALIGNED-V1 (a-b) + D3D-SIR-S7.E2.1-...-V1 (c-d) |
| regenerate | `python figure_source/d3d_task_conditioned_4panel_v5.py --data-dir figure_source_data --out-dir .` |
| expected output | `d3d_task_conditioned_4panel_v5.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

Verified. The script carries a preflight check for all 10 required inputs and an optional cross-check of its own 6x35 fold-support matrix against the pre-derived `panel2_fold_support_matrix.csv`.

Updated 2026-09-16 to the latest layout revision; frozen inputs unchanged, and the cross-check passes. **Known small mismatch:** the working-folder script was saved about 3 s after the bundled assets were rendered, so a fresh render differs from the bundled PNG in about 1% of pixels (small positional offsets, e.g. divider length; no data or text change). The assets are kept verbatim as produced. Re-render and replace them to make script and asset byte-consistent.

## Are the plotted values exact?

Panel a-b: discharge-specific coefficients and REML heterogeneity, exact. Panel c: binary support membership, exact. Panel d: per-discharge NRMSE, exact. No value is transformed for display beyond axis scaling.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
