# Figure 2

Sensitivity-centred phase turning manifold; trajectory-relational geometry.

| | |
|---|---|
| manuscript figure | **Figure 2** |
| final asset | `phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf` |
| generation script | `phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py` + required helper `phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.py` (imported for the analytic signals and turning-event calculations) |
| input data | none — analytic construction |
| source run | — |
| regenerate | `python figure_source/phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py` (run from this folder; writes here) |
| expected output | `phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

Verified: the v8 script declares this exact stem. Superseded v4 and v7 scripts are retained as lineage under `02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry/`. The v7 script is **also** bundled in `figure_source/`, byte-identical to that copy, because v8 imports its functions; its own `main()` is not run.

**Colour edit, 2026-09-16.** The $x_2(t)$ trace in panel a (and its legend entry) was recoloured from purple `#4B2E83` to `#A94700`, the orange used for $\omega$ in Figure 4, by changing the `REFERENCE` constant in the bundled script. The PDF/PNG/SVG here were re-rendered from that edited script, so this folder now **diverges from the working-folder copy** of v8. The `_purple` filename stem is kept so references stay stable.

**Polished 2026-09-16** (see `../README.md`). The script's built-in font audit now requires usetex with `lmodern`; its overlap and containment audits still pass.

**Self-contained, 2026-09-17.** Everything this figure needs is in this folder. Run the regenerate command from anywhere (paths resolve relative to the script); it reads only `figure_source/` and writes the PDF/PNG/SVG into this folder, overwriting the bundled assets. Verified by running a copy of this folder on its own, outside the repository, with no `PYTHONPATH`: the PNG reproduced pixel-for-pixel. Before this, the script needed `PYTHONPATH` pointing at `02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry` and wrote its outputs into `figure_source/`.

## Are the plotted values exact?

Analytic; values are computed by the script, not loaded.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
