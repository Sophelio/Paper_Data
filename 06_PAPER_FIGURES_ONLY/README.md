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
typographic standard for Nature Computational Science. Wording, data, colours
and figure geometry are unchanged except for small, documented local nudges.

**Font.** Every string is typeset by LaTeX (`text.usetex`) with
`\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage{amsmath,amssymb}`,
matching the manuscript. Each script also carries `LM_DESIGN_SIZE_PIN`, which
pins the 10 pt Latin Modern design at every size. Without it `lmodern`
switches to its 5–8 pt optical designs, which are 15–23% wider. The PDFs embed
only LMRoman10 / LMMath*10 fonts, plus EUFM10/MSBM10 in Fig 1 for ℜ and 𝔼.

**Maths.** Every symbol, variable, subscript, operator and equation is LaTeX
math. No Unicode maths glyphs remain in any script.

**Type scale** (points at the printed size, assuming 183 mm double-column
width; Fig 1's 14.4 in canvas scales every size through `pt()`):

| Role | Size |
|---|---|
| Figure title / figure-level header | 8 pt bold |
| Panel letter | 8 pt bold |
| Panel title (and schematic region titles) | 7 pt bold |
| Panel subtitle | 6 pt, upright |
| Axis and colourbar labels; featured equation displays | 6.5 pt |
| Tick labels, legends, annotations, node labels, boxed equations | 6 pt |
| Fine print (footnotes, dense category labels, inset ticks) | 5.5 pt |

Minimum 5 pt; every ink element at least 2 mm from the canvas edge.

**Regenerating.** Needs a TeX installation with `lmodern` (TeX Live 2026 was
used) and **matplotlib 3.9.x**. matplotlib 3.11.0 silently drops maths minus
signs (and some delimiters) from usetex PDFs; PNGs are unaffected. Every
bundled asset was re-rendered from the bundled script with matplotlib 3.9.2
and verified pixel-identical. Per-figure commands are in each folder's README.
