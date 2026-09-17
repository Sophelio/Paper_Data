# Paper figures only

**Allow-list enforced.** Figure-generation scripts and figure-specific data are
included here **only** for figures in the current manuscript or Supplement. Every
other figure script in the project — obsolete versions, rejected concepts,
exploratory plots — is recorded with a reason in
`90_AUDIT_REPORTS/excluded_files.csv` (22 figure scripts excluded).

## How the allow-list was derived

No manuscript TeX exists (see `01_MANUSCRIPT_SNAPSHOT/README.md`), so
`\includegraphics` could not be parsed. Instead each candidate script was opened
and its **declared output stem** traced to the asset on disk. That is stronger
than filename matching, but it is not the same as reading the manuscript's own
figure calls, and it is the one place where this package rests on inference.

| Folder | Figure | Mapping status |
|---|---|---|
| `Fig_01_admissible_relational_space` | admissible relational space | verified (resolved 2026-09-16) |
| `Fig_02_phase_turning_manifold` | turning manifold | verified |
| `Fig_04_task_contracts_representations` | task contracts | verified, manual relocation |
| `Fig_05_lorenz_representation_landscape` | Lorenz landscape | verified |
| `Fig_06_d3d_task_conditioned_4panel` | DIII-D four-panel | verified |
| `Supplementary_Figures/FigS1_coefficient_conditioning` | coefficient conditioning, 3 panels | verified |

Figure 3 has no external asset in the current set — it is either produced inline
in TeX or absent. Because no TeX exists, no source could be recovered; this is
recorded in `90_AUDIT_REPORTS/missing_artifacts.csv`.

Per-figure detail is in each folder's `README.md` and in
`00_START_HERE/FIGURE_TO_SOURCE_INDEX.csv`.

## Update of 2026-09-16

Figure assets and scripts were refreshed from the working figures folder
(`Documents/Papers/figures`). Frozen `figure_source_data/` inputs were compared
by SHA-256 and are unchanged. Each figure folder now carries every same-stem
PDF/PNG/SVG variant its script emits.

| Folder | Change |
|---|---|
| `Fig_01` | PDF replaced by the render of `_final.py`; PNG/SVG added; mapping resolved |
| `Fig_02` | PNG/SVG added; then $x_2(t)$ recoloured purple → Figure 4 orange `#A94700` and re-rendered (diverges from working folder) |
| `Fig_04` | PNG added; PDF/SVG and script already current |
| `Fig_05` | script and PDF updated (typography/layout revision); PNG/SVG added |
| `Fig_06` | script and PDF/PNG/SVG updated (layout revision) |
| `FigS1` | no counterpart in the working folder; unchanged |

Updated rows carry the new source path, size, hash and timestamp in
`00_START_HERE/PACKAGE_MANIFEST.csv`.

## Polishing pass (2026-09-16)

All figures in this folder (1, 2, 4, 5, 6, S1) were brought to one
typographic style for Nature Computational Science. Font sizes, wording, data,
colours and figure geometry are the originals, except for small documented
local nudges where the new font needed them.

**Font.** Every string is typeset by LaTeX (`text.usetex`) with
`\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage{amsmath,amssymb}`,
matching the manuscript. Each script also carries `LM_DESIGN_SIZE_PIN`, which
pins the 10 pt Latin Modern design at every size. Without it `lmodern`
switches to its 5–8 pt optical designs, which are 15–23% wider. The PDFs embed
only LMRoman10 / LMMath*10 fonts, plus EUFM10/MSBM10 in Fig 1 for ℜ and 𝔼.

**Maths.** Every symbol, variable, subscript, operator and equation is LaTeX
math. No Unicode maths glyphs remain in any script.

**Sizes.** A standardized type scale was trialled and then withdrawn at the
author's request: every figure keeps its **original** per-site font sizes and
canvas size. Titles, headers, panel letters and row headings use `\textbf`,
except Fig 1's two top headers, which stay regular weight as originally.
Subtitles and captions are upright instead of italic. Some original sizes
print below 5 pt at 183 mm width, notably small annotations in Figs 4 and 6.

**Regenerating.** Needs a TeX installation with `lmodern` (TeX Live 2026 was
used) and **matplotlib 3.9.x**. matplotlib 3.11.0 silently drops maths minus
signs (and some delimiters) from usetex PDFs; PNGs are unaffected. Every
bundled asset was re-rendered from the bundled script with matplotlib 3.9.2
and verified pixel-identical. Per-figure commands are in each folder's README.

## Self-contained figure folders (2026-09-17)

Each figure folder now regenerates on its own. From inside the folder:

```
python figure_source/<script>.py
```

No arguments and no `PYTHONPATH` are needed. Scripts resolve paths from their own
location, read only `figure_source/` and `figure_source_data/`, and write the
PDF/PNG/SVG into the figure folder, overwriting the bundled assets.

| Folder | What was missing | Fix |
|---|---|---|
| `Fig_01` | output went to a `Figures/figs/` subfolder | output to the figure folder |
| `Fig_02` | imported the v7 script from `02_CONTROLLED_STUDIES` via `PYTHONPATH`; output into `figure_source/` | v7 bundled in `figure_source/` (byte-identical); output to the figure folder |
| `Fig_04` | output went to `figure_source/figs/` | output to the figure folder |
| `Fig_05` | default data dir `fig5data/` did not exist; output into `figure_source/` | defaults: `figure_source_data/`, figure folder |
| `Fig_06` | default data dir `fig6data/` did not exist; output into `figure_source/` | defaults: `figure_source_data/`, figure folder |
| `FigS1` | `--audit-dir` into `04_DIII_D_DESCRIPTIVE` was required; bundled `correction_audit_utils.py` imported a module from that tree | config + 11 tables bundled in `figure_source_data/`; driver defaults to them; unused `correction_audit_utils.py` removed |

Only path defaults changed; no plotting code changed. Every folder was copied on
its own outside the repository and run with no arguments from an unrelated working
directory. All eight PNGs reproduced the bundled ones pixel-for-pixel.
