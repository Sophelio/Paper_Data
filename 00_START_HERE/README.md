# SIR accompanying data and reproducibility package

Generated 2026-09-16 · **1587 files · 560 MB**

This package is assembled by copying from `D:\SIR_paper\` and from the external
canonical DIII-D tree. **No original scientific artifact was moved, renamed,
modified or deleted.** Every file carries its original absolute path, size,
SHA-256 and modification time in `PACKAGE_MANIFEST.csv`.

---

## Read this first

> **The manuscript in this package is stale on the reconstruction branch, and
> no manuscript source exists in the repository.**
>
> `D:\SIR_paper\` contains **no TeX** for either the main manuscript or the
> Supplement, and **no `\releasepending` placeholder** of any kind. The only
> manuscript artifact is a PDF dated 2026-09-02, staged here under
> `01_MANUSCRIPT_SNAPSHOT/`. It reports the reconstruction branch that this
> project **retired** on 2026-09-02 for target-provenance leakage and for having
> no skill over a persistence baseline.
>
> The **frozen artifacts are canonical**; the manuscript text is not. Every
> canonical value in this package was re-extracted from the artifacts and agrees
> with the current scientific state. See `90_AUDIT_REPORTS/` and
> `KNOWN_LIMITATIONS.md`.

## What the package establishes

| | |
|---|---|
| Observational object | **62 discharges**, **95 quantities**, 5890 signal-discharge pairs |
| `q_desc` pooled RMSE | **0.05758467247445343** (discharge-specific coefficients, shared 7-coordinate support) |
| `q_desc` cohort-mean-vector RMSE | 0.4125238315775986 — a single universal vector is far worse |
| `q_desc` coefficient verdict | `D3D-MIXED-COEFFICIENT-IDENTIFIABILITY` — 5 robustly resolved, 2 uncertainty-dominated, 2 of 5 multivariate directions |
| `q_desc` implicit closure | `D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED` |
| `q_rec` ontology | 78 predictors → 70 hardened primitives → 23861 symbolic → 10778 atoms → **3451** range-supported at τ = 1.0 |
| `q_rec` parent branch | **NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER** — a preserved qualification FAILURE on 42 protected discharges |
| `q_rec` descendant branch | 0.1891 vs persistence 0.2164; Δ = -0.027308; 32/5/25 W/T/L |
| era split | earlier n=35 +0.0076 · later n=27 -0.0726 |
| supports | six folds, sizes [12, 12, 12, 12, 12, 12], union 35, mean Jaccard 0.285244 |
| final status | `QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS` / `CLEAN_DEMO_NOT_MET` |

## Where to start

| Question | Go to |
|---|---|
| Where did a number in the paper come from? | `CLAIM_TO_ARTIFACT_INDEX.csv` |
| Which run produced this? | `RUN_INDEX.csv` |
| Which script made this figure? | `FIGURE_TO_SOURCE_INDEX.csv` |
| What is in each folder? | `DIRECTORY_MAP.md` |
| Can I redistribute this? | `ACCESS_AND_LICENSE.md` |
| What is missing or ambiguous? | `../90_AUDIT_REPORTS/` |
| How do I rerun it? | `../09_REPRODUCIBILITY/RUN_ME_FIRST.md` |
| What should I not conclude? | `KNOWN_LIMITATIONS.md` |

## Verify the package

```
python Paper_Data/09_REPRODUCIBILITY/validation_scripts/verify_paper_data.py
```

Recomputes every SHA-256, checks the figure allow-list, confirms no source path
points inside `Paper_Data`, and re-derives the headline numbers.
