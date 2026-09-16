# Manuscript snapshot

## What is here

`main_manuscript/SIR_paper_2026-09-02.pdf` — 64 pages, the **only** manuscript
artifact in the repository. It contains the main text **and** Supplementary Notes
S1–S8 in one file; there is no separate Supplement document.

## What is not here, and why

There is **no TeX source** for either the main manuscript or the Supplement
anywhere under `D:\SIR_paper\`, and **no `\releasepending` placeholder** of any
kind. This was established by searching every file type in the tree, by content
search for the paper title, and by inspecting every archive.

Consequently the requested manuscript parse (sections, figure environments,
`\includegraphics`, tables, release placeholders) **could not be performed**.
`manuscript_inventory.json` records what could be established from the PDF text
layer instead.

## This PDF is stale

| evidence | |
|---|---|
| `REL10` occurrences | 16 |
| `141 relational` | 4 |
| `cross-fitted` | 0 |
| `3451` / `3,451` | 0 |
| `\releasepending` | 0 |

It reports the `I_p` reconstruction branch that this project **retired** on
2026-09-02 — see `10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/`. It
also predates all five current main-text figure assets, the earliest of which is
dated 2026-09-07.

**Do not treat this PDF as the current scientific state.** The frozen artifacts
are canonical. `90_AUDIT_REPORTS/unresolved_release_fields.csv` lists every
passage that must change.
