# Figure 5

Lorenz representation landscape: nested representation discovery under partial observation.

| | |
|---|---|
| manuscript figure | **Figure 5** |
| final asset | `figure5_lorenz_representation_landscape_final_tnr_v5_nature.pdf` (+ `.png`, `.svg`) |
| generation script | `figure5_lorenz_representation_landscape_final_tnr_v5_nature.py` |
| input data | figure_source_data/ — 10 frozen files from Lorenz/fig5data |
| source run | SIR-LORENZ-TASK-CONDITIONING |
| regenerate | `python figure_source/figure5_lorenz_representation_landscape_final_tnr_v5_nature.py --data-dir figure_source_data --output-dir .` |
| expected output | `figure5_lorenz_representation_landscape_final_tnr_v5_nature.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

Verified: the v5_nature script declares this exact stem. The v4 version and both prototypes are excluded from this folder and recorded in `90_AUDIT_REPORTS/excluded_files.csv`.

Updated 2026-09-16 to the latest v5_nature revision (typography and layout only; frozen inputs unchanged). Re-running the bundled script against `figure_source_data/` reproduces the bundled PNG pixel-for-pixel. Without `--data-dir`, the script looks for `fig5data/` beside itself.

**Polished 2026-09-16** (see `../README.md`).

## Are the plotted values exact?

Plotted values are read from the frozen fig5data package; `PROVENANCE_MANIFEST.json` there records their origin.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
