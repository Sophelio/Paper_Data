# Figure 6

DIII-D task-conditioned relational discovery: descriptive organization and coefficient heterogeneity (q_desc, panels a-b); support plurality across six folds and target-cross-fitted reconstruction (q_rec, panels c-d).

| | |
|---|---|
| manuscript figure | **Figure 6** |
| final asset | `d3d_task_conditioned_4panel_v5.pdf` |
| generation script | `d3d_task_conditioned_4panel_v5.py` |
| input data | figure_source_data/ — 11 frozen files from DIIID_example/fig6data |
| source run | D3D-SIR-62-ALIGNED-V1 (a-b) + D3D-SIR-S7.E2.1-...-V1 (c-d) |
| regenerate | `python figure_source/d3d_task_conditioned_4panel_v5.py` (run from this folder; reads `figure_source_data/`, writes here) |
| expected output | `d3d_task_conditioned_4panel_v5.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

Verified. The script carries a preflight check for all 10 required inputs and an optional cross-check of its own 6x35 fold-support matrix against the pre-derived `panel2_fold_support_matrix.csv`.

Updated 2026-09-16 to the latest layout revision; frozen inputs unchanged. **Polished 2026-09-16** (see `../README.md`). The assets were re-rendered from the bundled script, so they now match it exactly. This resolves the small script/asset mismatch noted in the earlier update. The fold-support cross-check still passes.

**Self-contained, 2026-09-17.** Everything this figure needs is in this folder. Run the regenerate command from anywhere (paths resolve relative to the script); it reads only `figure_source/` and `figure_source_data/` and writes the PDF/PNG/SVG into this folder, overwriting the bundled assets. Verified by running a copy of this folder on its own, outside the repository, with no `PYTHONPATH`: the PNG reproduced pixel-for-pixel. The script's defaults previously pointed at a non-existent `fig6data/` beside itself and wrote into `figure_source/`; `--data-dir` and `--out-dir` still override them.

## Are the plotted values exact?

Panel a-b: discharge-specific coefficients and REML heterogeneity, exact. Panel c: binary support membership, exact. Panel d: per-discharge NRMSE, exact. No value is transformed for display beyond axis scaling.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
