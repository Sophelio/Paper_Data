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
| `Fig_02` | PNG/SVG added; PDF and script already current |
| `Fig_04` | PNG added; PDF/SVG and script already current |
| `Fig_05` | script and PDF updated (typography/layout revision); PNG/SVG added |
| `Fig_06` | script and PDF/PNG/SVG updated (layout revision) |
| `FigS1` | no counterpart in the working folder; unchanged |

Updated rows carry the new source path, size, hash and timestamp in
`00_START_HERE/PACKAGE_MANIFEST.csv`.
