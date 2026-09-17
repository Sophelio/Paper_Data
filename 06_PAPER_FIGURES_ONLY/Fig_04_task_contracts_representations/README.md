# Figure 4

Task contracts and the mathematical representations they induce, one row.

| | |
|---|---|
| manuscript figure | **Figure 4** |
| final asset | `figure4_task_contracts_mathematical_representations_nature_one_row.pdf` (+ `.png`, `.svg`) |
| generation script | `figure4_task_contracts_mathematical_representations_nature_one_row.py` + required helper `figure4_task_contracts_mathematical_representations_nature.py` |
| input data | `figure_source/manifest.csv` (read by the helper, which recomputes the pendulum and heat-equation fits); `panel_data.py` is bundled but not imported |
| source run | SIR-PENDULUM |
| regenerate | `python figure_source/figure4_task_contracts_mathematical_representations_nature_one_row.py` (writes to `figure_source/figs/`) |
| expected output | `figure4_task_contracts_mathematical_representations_nature_one_row.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

**Manual step recorded.** The script writes to `Pendulum/Plotter/figs`, which does not exist on disk; the asset lives in `Figures/figs`. The file was relocated by hand after generation.

**Edit 2026-09-16.** Panel b's three representation boxes no longer show per-representation residuals ($\|R\|_\infty$); each shows only its parameter ($\alpha$, $m$, $\kappa$), set at 5.5 pt in the figure's near-black ink (`#202124`) rather than 4.7 pt grey. The residuals are still computed and printed by the script, and the panel footer still reports $\|R\|_\infty<10^{-4}$ for all displayed relations.

## Are the plotted values exact?

Panel values are recomputed at render time by the helper from `manifest.csv`. The script prints the key scientific values, and these were unchanged by the 2026-09-16 polish.

**Polished 2026-09-16** (see `../README.md`). The helper module and its `manifest.csv` were added to `figure_source/` because the one_row script cannot run without them. They were previously missing from this package. The helper is an unedited, verbatim copy of the working-folder file; the one_row script overrides its style. `manifest.csv` is byte-identical to `02_CONTROLLED_STUDIES/04_Pendulum_Task_Conditioning/manifest.csv`.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
