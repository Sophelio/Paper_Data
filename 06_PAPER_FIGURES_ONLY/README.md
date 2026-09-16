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
| `Fig_01_admissible_relational_space` | admissible relational space | **AMBIGUOUS** |
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
