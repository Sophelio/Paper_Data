# Figure 2

Sensitivity-centred phase turning manifold; trajectory-relational geometry.

| | |
|---|---|
| manuscript figure | **Figure 2** |
| final asset | `phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf` |
| generation script | `phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py` |
| input data | none — analytic construction |
| source run | — |
| regenerate | `PYTHONPATH=02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry python figure_source/phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py` (run from the package root; the v8 script imports helpers from the v7 script kept there) |
| expected output | `phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

Verified: the v8 script declares this exact stem. Superseded v4 and v7 scripts are retained under `02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry/`, not here.

**Colour edit, 2026-09-16.** The $x_2(t)$ trace in panel a (and its legend entry) was recoloured from purple `#4B2E83` to `#A94700`, the orange used for $\omega$ in Figure 4, by changing the `REFERENCE` constant in the bundled script. The PDF/PNG/SVG here were re-rendered from that edited script, so this folder now **diverges from the working-folder copy** of v8. The `_purple` filename stem is kept so references stay stable.

## Are the plotted values exact?

Analytic; values are computed by the script, not loaded.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
