# Figure 1

Admissible relational space: coordinate-generation operators and relation families, with symbolic regression shown as one restricted subfamily.

| | |
|---|---|
| manuscript figure | **Figure 1** |
| final asset | `admissible_relational_space_hierarchical_v15_metaball.pdf` (+ `.png`, `.svg`) |
| generation script | `admissible_relational_space_hierarchical_v15_metaball_final.py` · `admissible_relational_space_hierarchical_v15_metaball.py` |
| input data | none — schematic, no numerical inputs |
| source run | — |
| regenerate | `python figure_source/admissible_relational_space_hierarchical_v15_metaball_final.py` |
| expected output | `admissible_relational_space_hierarchical_v15_metaball.pdf` (plus .svg/.png where the script emits them) |

## Provenance note

**Resolved 2026-09-16.** Both scripts declare the output stem `admissible_relational_space_hierarchical_v15_metaball`. The bundled PDF/PNG/SVG are the render of `_final.py`: the working-folder script that produced them is byte-identical to `_final.py`, carries the same timestamp as the assets (2026-09-09), and re-running `_final.py` reproduces the PNG pixel-for-pixel. The non-final script differs by six lines (a patch edge colour and linewidth) and is kept for lineage only. The script originally wrote to `../Figures/figs` relative to its own folder; see the self-contained note below.

**Polished 2026-09-16** (see `../README.md`). Only `_final.py` was edited; the non-final script is untouched lineage.

**Self-contained, 2026-09-17.** Everything this figure needs is in this folder. Run the regenerate command from anywhere (paths resolve relative to the script); it reads only `figure_source/` and writes the PDF/PNG/SVG into this folder, overwriting the bundled assets. Verified by running a copy of this folder on its own, outside the repository, with no `PYTHONPATH`: the PNG reproduced pixel-for-pixel. `_final.py` now writes to this folder instead of `Figures/figs/`.

## Are the plotted values exact?

Schematic. No plotted value is derived from data.

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
