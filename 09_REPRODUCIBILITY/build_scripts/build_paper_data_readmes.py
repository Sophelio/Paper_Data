#!/usr/bin/env python
"""Generate every human-facing README, the reproducibility layer and the
environment capture for Paper_Data (Phases 11, 14)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\SIR_paper")
PKG = ROOT / "Paper_Data"
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d")
S = json.loads((PKG / "_staging_records.json").read_text(encoding="utf-8"))
RECS = S["records"]
NF = len(RECS)
MB = sum(r["size_bytes"] for r in RECS) / 1048576
V = json.loads((PKG / "07_TABLES_AND_REPORTED_NUMBERS" / "numerical_claims" /
                "claim_ledger.json").read_text(encoding="utf-8"))["canonical_values"]


def w(rel, text):
    p = PKG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.lstrip("\n").rstrip() + "\n", encoding="utf-8")
    print("  ", rel)


# ======================================================== 00_START_HERE
w("00_START_HERE/README.md", f"""
# SIR accompanying data and reproducibility package

Generated {STAMP} · **{NF} files · {MB:.0f} MB**

This package is assembled by copying from `D:\\SIR_paper\\` and from the external
canonical DIII-D tree. **No original scientific artifact was moved, renamed,
modified or deleted.** Every file carries its original absolute path, size,
SHA-256 and modification time in `PACKAGE_MANIFEST.csv`.

---

## Read this first

> **The manuscript in this package is stale on the reconstruction branch, and
> no manuscript source exists in the repository.**
>
> `D:\\SIR_paper\\` contains **no TeX** for either the main manuscript or the
> Supplement, and **no `\\releasepending` placeholder** of any kind. The only
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
| Observational object | **{V['n_discharges']} discharges**, **{V['n_signals']} quantities**, {V['n_pairs']} signal-discharge pairs |
| `q_desc` pooled RMSE | **{V['qdesc_pooled_rmse']}** (discharge-specific coefficients, shared 7-coordinate support) |
| `q_desc` cohort-mean-vector RMSE | {V['qdesc_mean_vector_rmse']} — a single universal vector is far worse |
| `q_desc` coefficient verdict | `{V['cond_verdict']}` — {V['n_robust']} robustly resolved, {V['n_unc']} uncertainty-dominated, {V['robust_dirs']} of {V['pos_dirs']} multivariate directions |
| `q_desc` implicit closure | `{V['implicit_verdict']}` |
| `q_rec` ontology | {V['n_pred']} predictors → {V['n_primitives']} hardened primitives → {V['n_symbolic']} symbolic → {V['n_atoms']} atoms → **{V['n_range']}** range-supported at τ = {V['tau']} |
| `q_rec` parent branch | **{V['parent_verdict']}** — a preserved qualification FAILURE on {V['n_external']} protected discharges |
| `q_rec` descendant branch | {V['REL']:.4f} vs persistence {V['B1']:.4f}; Δ = {V['D1']:.6f}; {V['W']}/{V['T']}/{V['L']} W/T/L |
| era split | earlier n={V['n_e']} {V['era_e']:+.4f} · later n={V['n_l']} {V['era_l']:+.4f} |
| supports | six folds, sizes {V['sizes']}, union {V['union']}, mean Jaccard {V['jaccard']:.6f} |
| final status | `{V['final_status']}` / `{V['clean']}` |

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
""")

w("00_START_HERE/DIRECTORY_MAP.md", f"""
# Directory map

Numbered so a reviewer can read the science in order rather than reverse-engineer
filenames.

```
00_START_HERE/                    indexes, manifest, limitations, licence
01_MANUSCRIPT_SNAPSHOT/           the staged (stale) manuscript PDF
02_CONTROLLED_STUDIES/            the six controlled studies the paper discusses
03_DIII_D_SOURCE_OBJECT/          the shared 62-discharge / 95-quantity object
04_DIII_D_DESCRIPTIVE/            q_desc: D3D-SIR-62-ALIGNED-V1 and its audits
05_DIII_D_RECONSTRUCTION/         q_rec: the full lineage, failure included
06_PAPER_FIGURES_ONLY/            ONLY figures in the current manuscript
07_TABLES_AND_REPORTED_NUMBERS/   the claim ledger
09_REPRODUCIBILITY/               environment, run order, build and verify
10_REFERENCED_HISTORICAL_LINEAGE/ retired and superseded work, clearly marked
90_AUDIT_REPORTS/                 what is missing, ambiguous or excluded
```

## 02_CONTROLLED_STUDIES

| Folder | Study |
|---|---|
| `01_Lorenz_Generator_Containment` | fixed-representation containment; SIR / pySINDy / MLP arms |
| `02_Lorenz_Representation_Discovery` | partially observed Lorenz, task conditioning, Figure 5 data |
| `03_Heterogeneous_Parameter_Oscillator` | shared structure under heterogeneous α, 40 realizations |
| `04_Pendulum_Task_Conditioning` | compression vs autonomous evolution; Figure 4 panels |
| `05_Heat_Equation_Degeneracy_and_Multimode` | single-mode ambiguity and multimode resolution |
| `06_Trajectory_Relational_Geometry` | turning-manifold geometry; Figure 2 |

## 05_DIII_D_RECONSTRUCTION — read in order

The lineage is the scientific content. It is numbered chronologically.

```
00_Pretarget_Contract                    contract before any target is chosen
01_Target_Selection_and_02_Information_Boundary
                                         y* = density; {V['n_pred']} of {V['n_signals']} admitted
03_Temporal_Realization                  grids, cadence, no-upsample policy
04_Initial_Ontology/                     {V['n_symbolic']} symbolic → {V['n_atoms']} atoms
05_Parent_Development_Search             {V['frontier']} explored supports
06_Frozen_Parent_Support                 C_dev_star frozen before any protected access
07_Protected_Qualification_FAILURE       *** THE PARENT FAILED ***
08_Failure_Diagnosis/                    sensitivities; the state hypothesis REFUTED
09_Range_Support_Case_B_Revision         τ = 1; {V['n_atoms']} → {V['n_range']} atoms
11_Descendant_Case_C_Contract/           six folds; information boundary reconciled
12_Six_Fold_Target_Cross_Fitting         *** THE DESCENDANT PASSED ***
17_Applicability_and_Final_Claim/        Q_rec*, claim boundary, branch closure
18_Machine_Readable_Lineage/             stage index, revision ledger, audits
```

Folders 10, 13-16 of the requested template are not separate directories here:
the hardened 3,451-atom ontology lives inside `09_Range_Support_Case_B_Revision`
(where it was produced), and baselines, per-discharge results, bootstrap and era
stratification are all inside `12_Six_Fold_Target_Cross_Fitting`, which is where
the frozen artifacts actually place them. Splitting them would have meant
copying files twice or inventing directories with no frozen counterpart.
""")

w("00_START_HERE/KNOWN_LIMITATIONS.md", f"""
# Known limitations

Stated plainly, because a reviewer needs them more than the headline numbers.

## 1. The staged manuscript is stale and has no source

No TeX exists for the main manuscript or the Supplement anywhere in
`D:\\SIR_paper\\`, and no `\\releasepending` placeholder exists. The staged PDF
(2026-09-02) reports the **retired** `I_p` reconstruction branch: 16 occurrences
of `REL10`, zero of `cross-fitted` or `3451`. It also predates all five current
main-text figure assets.

Consequence: the figure allow-list could not be parsed from TeX. It was derived
from on-disk assets and **verified by tracing each script's declared output
stem**, which is stronger than filename matching but weaker than reading the
actual `\\includegraphics` calls.

## 2. What the `q_rec` result does and does not establish

**Does:** within the predictor-qualified frozen {V['n_discharges']}-discharge object,
relational supports discovered without a discharge's own target values
reconstruct that discharge nontrivially relative to the frozen baselines.

**Does not:** external validation · future-discharge transfer · zero-shot
inference · a universal DIII-D relation · a unique equation · universal
coefficients.

Two limits travel with it. The margin over persistence is **modest and
era-asymmetric** ({V['D1']:+.4f} pooled; {V['era_e']:+.4f} earlier vs {V['era_l']:+.4f} later;
{V['W']}-{V['T']}-{V['L']} at discharge level). And predictor-side applicability was
instantiated from the **whole finite object**, so what was tested is transfer of
the target relationship, not of predictor geometry.

## 3. Support non-uniqueness

Six folds produced six **different** size-12 supports, union {V['union']}, mean
pairwise Jaccard {V['jaccard']:.6f}. A seventh full-object search produced a seventh
distinct support. No fold support is canonical, and the descriptive
`C_E2_ALL_DESC` is representative, not validated.

## 4. Coefficients are not physical constants

`q_desc` coefficients are locally calibrated per discharge. The verdict is
`{V['cond_verdict']}`: {V['n_robust']} of 7 robustly resolved, {V['n_unc']}
uncertainty-dominated, {V['robust_dirs']} of {V['pos_dirs']} multivariate directions
resolved. `pcdiamag3` remains an uncalibrated signal wherever it appears.

## 5. Restricted source data is not bundled

The 62 resampled `.npz` archives (1.1 GB) are **not** in this package. They are
indexed with SHA-256 in
`03_DIII_D_SOURCE_OBJECT/source_access_notes/RESTRICTED_SOURCE_INDEX.csv`, and all
derived metadata is included. This is *not bundled because access is restricted*,
not *missing*. See `ACCESS_AND_LICENSE.md`.

## 6. Gaps recorded rather than papered over

- No `q_desc` explored-frontier record exists (the `q_rec` one is complete).
- No frozen paired-bootstrap interval for Δ₁; per-discharge Δⱼ is present, so it
  is computable.
- Spline and RTS numerical realizations are untied to a frozen run manifest.
- The Figure 1 script → asset mapping is **ambiguous**; both candidate scripts
  are bundled.

All are itemised in `90_AUDIT_REPORTS/missing_artifacts.csv` and
`ambiguous_artifacts.csv`.
""")

w("00_START_HERE/ACCESS_AND_LICENSE.md", """
# Access, licensing and redistribution

Presence of a file on the authoring machine does not establish the right to
redistribute it. Categories are separated below.

## Freely redistributable

| Category | Where |
|---|---|
| Generated synthetic data | Lorenz, pendulum, heat-equation, oscillator trajectories in `02_CONTROLLED_STUDIES/` |
| Analysis and figure source code | throughout; authored for this work |
| Derived numerical results | all frozen JSON/CSV/parquet outputs |
| Manuscript-generated tables and indexes | `07_TABLES_AND_REPORTED_NUMBERS/`, `00_START_HERE/` |
| Audit, manifest and provenance records | `08_...`, `18_Machine_Readable_Lineage`, `90_AUDIT_REPORTS/` |

## Restricted: DIII-D source archive — NOT BUNDLED

The 62 resampled discharge archives
(`DIIID_example/data/resampled_data_v6/*_resampled.npz`, 1.1 GB) are **deliberately
excluded**. Redistribution rights for the underlying DIII-D measurements have not
been established here.

This is a deliberate exclusion, **not a missing artifact**.

The strongest legally safe reproducibility path is provided instead:

1. **Discharge identifiers** — the complete 62-shot list, in
   `03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/`.
2. **SHA-256 of every excluded file** —
   `source_access_notes/RESTRICTED_SOURCE_INDEX.csv`, so a reader who obtains the
   archive independently can confirm they hold the identical bytes.
3. **Per-shot resampling metadata** — method, category, units and provenance for
   every admitted signal, in `retrieval_metadata/shot_metadata/` (bundled;
   derived and redistributable).
4. **The units registry** — `SIGNAL_UNITS.json`. Units are read from here, never
   inferred from signal names.
5. **Every derived artifact** — aligned exports, coordinates, coefficients,
   metrics and audits are all bundled.
6. **The data provider** — `retrieval_metadata/diiid_sir_data_provider.py`, the
   exact code that reads the archive.

Anyone with authorised access to the DIII-D archive can reconstruct the
observational object from these materials and verify byte identity.

## Third-party assets

Fonts under `General/fonts` are **not** bundled. Figure scripts request Times New
Roman and fall back to available serif faces; no third-party font is
redistributed here.

## Before public release

- Assign a DOI or archive identifier and record it here.
- Confirm the DIII-D data-use agreement covers the derived artifacts that *are*
  bundled.
- Choose and add a licence file (code and data may warrant different terms).
""")

# ======================================================== 01
w("01_MANUSCRIPT_SNAPSHOT/README.md", """
# Manuscript snapshot

## What is here

`main_manuscript/SIR_paper_2026-09-02.pdf` — 64 pages, the **only** manuscript
artifact in the repository. It contains the main text **and** Supplementary Notes
S1–S8 in one file; there is no separate Supplement document.

## What is not here, and why

There is **no TeX source** for either the main manuscript or the Supplement
anywhere under `D:\\SIR_paper\\`, and **no `\\releasepending` placeholder** of any
kind. This was established by searching every file type in the tree, by content
search for the paper title, and by inspecting every archive.

Consequently the requested manuscript parse (sections, figure environments,
`\\includegraphics`, tables, release placeholders) **could not be performed**.
`manuscript_inventory.json` records what could be established from the PDF text
layer instead.

## This PDF is stale

| evidence | |
|---|---|
| `REL10` occurrences | 16 |
| `141 relational` | 4 |
| `cross-fitted` | 0 |
| `3451` / `3,451` | 0 |
| `\\releasepending` | 0 |

It reports the `I_p` reconstruction branch that this project **retired** on
2026-09-02 — see `10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/`. It
also predates all five current main-text figure assets, the earliest of which is
dated 2026-09-07.

**Do not treat this PDF as the current scientific state.** The frozen artifacts
are canonical. `90_AUDIT_REPORTS/unresolved_release_fields.csv` lists every
passage that must change.
""")

# ======================================================== per-area READMEs
w("02_CONTROLLED_STUDIES/README.md", """
# Controlled studies

Each folder contains enough to reconstruct the reported result independently:
generator, parameters, seeds, splits, trajectories, coordinate and candidate
inventories, search settings, selected representation, coefficients, scores,
baselines and a report.

| Folder | What it demonstrates | Canonical entry point |
|---|---|---|
| `01_Lorenz_Generator_Containment` | a fixed representation contains the generator; SIR vs pySINDy vs MLP | `BENCHMARK_REPORT.md`, `benchmark_results.json` |
| `02_Lorenz_Representation_Discovery` | discovery under partial observation; task conditioning; clean/noisy comparison | `TASK_CONDITIONING_BENCHMARK_REPORT.md`, `PRECONFIRMATION_FREEZE.json` |
| `03_Heterogeneous_Parameter_Oscillator` | shared structure with heterogeneous α across 40 realizations | `README.md`, `data/realization_*.parquet` |
| `04_Pendulum_Task_Conditioning` | compression versus autonomous evolution | `README.md`, `Plotter/PENDULUM_TASK_CONDITIONED_PANEL_REPORT.md` |
| `05_Heat_Equation_Degeneracy_and_Multimode` | single-mode ambiguity; multimode shared-coefficient resolution | `README.md` |
| `06_Trajectory_Relational_Geometry` | turning-manifold geometry behind Figure 2 | `AUDIT_sensitivity_centered_phase.md` |

**Audit note.** Both Lorenz benchmark packages carry their own `audit/`
directories with leakage, fairness, reproducibility and prior-knowledge audits.
Read those before quoting a comparative number. Where an MLP arm is present in
the benchmark but the corresponding result is not reported in the manuscript,
that is recorded in `90_AUDIT_REPORTS/missing_artifacts.csv` rather than treated
as a paper result.
""")

w("03_DIII_D_SOURCE_OBJECT/README.md", f"""
# DIII-D source object

The observational object shared by **both** DIII-D branches: **{V['n_discharges']}
discharges** and **{V['n_signals']} quantities**, {V['n_pairs']} signal-discharge pairs.

Supports Supplement S7.1–S7.2 and every downstream claim.

| Subfolder | Contents |
|---|---|
| `observational_object_S7_1/` | cohort and signal inventories, provenance graph, units, temporal support, availability matrix, equilibrium lineage, quality summary, and the full S7.1 reconciliation history |
| `provenance/` | discharge ledger, preprocessing provenance, reconstruction validation audit |
| `units_and_availability/` | `SIGNAL_UNITS.json`, the frozen units registry |
| `retrieval_metadata/` | the data provider, transform realization, and per-shot resampling metadata |
| `source_access_notes/` | what is restricted, its hashes, and how to obtain it |

## Units

Units are read from `SIGNAL_UNITS.json` and are **never inferred from signal
names**. That registry is hashed into the S7.1 freeze as
`units_registry_sha256`.

## Restricted data

The 62 `.npz` archives are **not bundled**. Every one is listed with its SHA-256
in `source_access_notes/RESTRICTED_SOURCE_INDEX.csv`. See
`00_START_HERE/ACCESS_AND_LICENSE.md`.

## Ancestry

The information boundary that reduces {V['n_signals']} quantities to {V['n_pred']}
admitted predictors is in `05_DIII_D_RECONSTRUCTION/01_Target_Selection...`.
{V['n_excl_efit']} EFIT-derived quantities are excluded **fail-closed** on unresolved
ancestry — the class that contaminated the retired branch.
""")

w("04_DIII_D_DESCRIPTIVE/README.md", f"""
# DIII-D descriptive branch — `q_desc`

**Run `D3D-SIR-62-ALIGNED-V1`.** Supports Results 1.5 and Supplement S7.1–S7.7,
and panels a–b of the DIII-D figure.

## The result

A shared **seven-coordinate** relational support organizes standardized
`dW_dia/dt` across {V['qdesc_n']} discharges, with **discharge-specific** coefficients.

| | |
|---|---|
| pooled RMSE | **{V['qdesc_pooled_rmse']}** |
| pooled MSE | {V['qdesc_pooled_mse']} |
| cohort-mean-vector RMSE | {V['qdesc_mean_vector_rmse']} |
| samples | {V['qdesc_samples']} ({V['qdesc_n']} × 1000) |

The gap between those two RMSE values is the point: the reported figure is a
discharge-specific fit on a shared support, **not** one universal equation.

## Qualification

| audit | verdict |
|---|---|
| coefficient identifiability | `{V['cond_verdict']}` — {V['n_robust']} robust, {V['n_unc']} uncertainty-dominated |
| multivariate directions | {V['robust_dirs']} robust of {V['pos_dirs']} positive |
| rank-6 truncation | {V['rank6_coef']:.4f} median relative coefficient change, {V['rank6_rmse']:.4f} median RMSE change |
| random-effects estimator | `{V['re_estimator']}` |
| implicit closure | `{V['implicit_verdict']}` |

## Canonical vs superseded — read this

`coefficient_conditioning/` contains **both** audits:

- `Correction_audit/` — **CANONICAL**. Verdict `{V['cond_verdict']}`.
- everything above it — **SUPERSEDED**. The original carried the retired verdict
  `D3D-COEFFICIENT-FAMILY-RESOLVED` and mislabelled profile-ML as REML.

The original is retained because the manuscript documents its correction. Do not
quote it as a current result. `Correction_audit/STALE_ARTIFACT_RESOLUTION.md`
records the archival.

## Interpretation limits

Target-containing implicit closure, not an independent predictor. Not causal. The
coefficients are not dimensional physical constants.
""")

w("05_DIII_D_RECONSTRUCTION/README.md", f"""
# DIII-D reconstruction branch — `q_rec`

**This is a lineage, not one model.** The failure is preserved as prominently as
the pass, because the sequence is the scientific content.

## The arc

```
{V['n_signals']} quantities → {V['n_pred']} admitted predictors → {V['n_primitives']} hardened primitives
   → {V['n_symbolic']} symbolic → {V['n_atoms']} admissible atoms
   → {V['frontier']} explored supports → C_dev_star (size {V['support_cap']}), frozen
   → *** PROTECTED QUALIFICATION FAILED on {V['n_external']} discharges ***
   → state hypothesis TESTED and REFUTED
   → operational contract revised: range support at τ = {V['tau']} → {V['n_range']} atoms
   → information boundary reconciled
   → six-fold target cross-fitting → *** FORMAL PASS ***
   → Q_rec*, branch closed
```

## The two outcomes, which must not be confused

| | parent branch | descendant branch |
|---|---|---|
| folder | `07_Protected_Qualification_FAILURE` | `12_Six_Fold_Target_Cross_Fitting` |
| design | frozen support, {V['n_external']} sealed protected discharges | six discharge-grouped folds over all {V['n_discharges']} |
| REL mean | {V['parent_REL']:.6f} | **{V['REL']:.6f}** |
| persistence | {V['parent_B1']:.6f} | {V['B1']:.6f} |
| Δ vs persistence | **{V['parent_D1']:+.6f}** | **{V['D1']:+.6f}** |
| verdict | **{V['parent_verdict']}** | **{V['final_status']}** |

The parent result is a genuine negative and is **immutable**. Nothing was
repaired after it was seen.

## Reading order

Folders are numbered chronologically — read them in order. `18_Machine_Readable_Lineage`
carries the stage index, the revision ledger (which classifies every revision),
the information-flow audit, and a re-runnable checker:

```
python 18_Machine_Readable_Lineage/audit_s7.py
```

## What the qualified claim supports

Within the predictor-qualified frozen {V['n_discharges']}-discharge object, relational
supports discovered without a discharge's own target values reconstruct that
discharge nontrivially relative to the frozen baselines.

**Not** external validation. **Not** zero-shot. **Not** a universal relation. Six
folds gave six different supports (union {V['union']}, mean Jaccard {V['jaccard']:.6f}):
stable utility, non-unique representations. Full boundary in
`17_Applicability_and_Final_Claim/S7_12_final/S7_12_CLAIM_BOUNDARY.md`.
""")

w("06_PAPER_FIGURES_ONLY/README.md", """
# Paper figures only

**Allow-list enforced.** Figure-generation scripts and figure-specific data are
included here **only** for figures in the current manuscript or Supplement. Every
other figure script in the project — obsolete versions, rejected concepts,
exploratory plots — is recorded with a reason in
`90_AUDIT_REPORTS/excluded_files.csv` (22 figure scripts excluded).

## How the allow-list was derived

No manuscript TeX exists (see `01_MANUSCRIPT_SNAPSHOT/README.md`), so
`\\includegraphics` could not be parsed. Instead each candidate script was opened
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
""")

w("07_TABLES_AND_REPORTED_NUMBERS/README.md", f"""
# Tables and reported numbers

## The claim ledger

`numerical_claims/claim_ledger.json` and
`00_START_HERE/CLAIM_TO_ARTIFACT_INDEX.csv` map every major numerical claim to a
canonical machine-readable artifact, with the exact field or column.

Every value was **re-extracted from the artifacts**, not transcribed from the
manuscript, so displayed rounding never becomes the source of truth. The ledger
carries both the rounded value as displayed and the full-precision value.

Three statuses appear:

| status | meaning |
|---|---|
| `VERIFIED` | the artifact reproduces the claim |
| `VERIFIED_BUT_MANUSCRIPT_DISAGREES` | the artifact is canonical and the staged manuscript says something else |
| `VERIFIED_MISSING_FROM_MANUSCRIPT` | the artifact exists and the manuscript does not report it at all |

The last two categories exist because the staged manuscript is stale on the
reconstruction branch.

## Tables

`00_START_HERE/TABLE_TO_SOURCE_INDEX.csv` maps each manuscript/Supplement table
to the artifact behind it.
""")

w("10_REFERENCED_HISTORICAL_LINEAGE/README.md", """
# Referenced historical lineage

**Nothing in this folder is a current result.** It is retained because the
manuscript's corrections cannot be understood without it.

| Folder | Status | Superseded by |
|---|---|---|
| `failed_parent_branches/retired_Ip_branch/` | **RETIRED** | the `density` lineage in `05_DIII_D_RECONSTRUCTION/` |
| `superseded_manuscript/` | **SUPERSEDED** | `01_MANUSCRIPT_SNAPSHOT/` |

## The retired `I_p` branch

Retired 2026-09-02 under `D3D-FIG6-QREC-RETIREMENT-V1` on two independent
grounds, either sufficient:

1. **Target-provenance leakage.** 6 of 10 `REL10` and 4 of 10 `RAW10` features
   carried upstream `I_p` dependence. `q95` proved to be essentially
   `shape·a²B_t/I_p` in this archive — median |corr| 0.945 with `1/I_p`, only
   **7.3 %** residual scatter after algebraic removal. Both the relational
   representation *and its comparator* were contaminated.
2. **No skill over a trivial baseline.** A constant persistence predictor reached
   median normalized RMSE **0.0685**, beating REL141 (0.1137), REL10 (0.1257) and
   RAW10 (0.1821).

**The staged manuscript still reports this branch.** That is the single most
important finding of this package.

The corrective rebuild — the `density` branch in `05_DIII_D_RECONSTRUCTION/` —
satisfies all five prerequisites the retirement record demanded, including a
target-independent candidate universe and a mandatory persistence gate.
""")

w("08_CONTRACTS_PROVENANCE_AND_QUALIFICATION/README.md", """
# Contracts, provenance and qualification

Most contract and qualification material lives with the stage that produced it,
under `05_DIII_D_RECONSTRUCTION/`, so that chronology is preserved. This folder
holds the cross-cutting records.

| Where to look | What it holds |
|---|---|
| `05_.../00_Pretarget_Contract/` | `K_REC_PRE`, cohort partition, validation protocol, baseline protocol, claim boundary |
| `05_.../09_Range_Support_Case_B_Revision/` | `K_REC_V2`, the V1→V2 changeset, range-support policy |
| `05_.../11_Descendant_Case_C_Contract/` | Epoch-2 protocol, access policy, search budget, qualification policy, stop rule |
| `05_.../18_Machine_Readable_Lineage/` | stage index, **revision ledger**, information-flow audit, claim-evidence matrix, architecture map |
| `04_DIII_D_DESCRIPTIVE/.../Correction_audit/` | the correction that superseded the original conditioning verdict |
| `artifact_lineage/` | the transform-family audit |

## The revision ledger

`05_.../18_Machine_Readable_Lineage/REVISION_LEDGER.md` classifies every
revision in the reconstruction lineage as one of:

- **Case A** — an object was instantiated incorrectly; contract adequate.
- **Case B** — every object satisfied the contract as written, but the
  operational contract was incomplete.
- **Case C** — a claim-defining commitment materially changed, producing a
  descendant claim branch under the same task.

That table is the fastest way to see what changed after the qualification
failure, and why each change was legitimate rather than post hoc tuning.
""")
print("READMEs written")
