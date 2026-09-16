# Paper_Data — SIR accompanying data and reproducibility package

Frozen data, analysis artifacts, provenance records and figure-reproduction
assets for the SIR (System Identification and Regression) manuscript.

**Start at [`00_START_HERE/README.md`](00_START_HERE/README.md).** That file, plus
[`00_START_HERE/DIRECTORY_MAP.md`](00_START_HERE/DIRECTORY_MAP.md), is the intended
entry point; this page is only a pointer.

---

## Read this before using any number from this repository

The manuscript PDF bundled here (`01_MANUSCRIPT_SNAPSHOT/`, dated 2026-09-02) is
**stale with respect to the artifacts in this repository.** It reports an earlier
`I_p` reconstruction branch that was retired on 2026-09-02 for target-provenance
leakage and for showing no skill over a persistence baseline.

The current result is the **density (`prmtan_neped`) six-fold cross-fitted
reconstruction** in `05_DIII_D_RECONSTRUCTION/12_Six_Fold_Target_Cross_Fitting/`.

Where the PDF and the artifacts disagree, **the artifacts are canonical.** Every
disagreement is enumerated in
[`90_AUDIT_REPORTS/unresolved_release_fields.csv`](90_AUDIT_REPORTS/unresolved_release_fields.csv).

## Verify the package

```bash
python 09_REPRODUCIBILITY/validation_scripts/verify_paper_data.py
```

17 checks: manifest integrity, all 1,587 SHA-256 hashes, figure allow-list
compliance, claim→artifact resolution, restricted-data containment, historical
marking, and five headline numbers re-derived from raw per-record data rather
than read back from the ledger. Offline; no network, no credentials.

Expected result: `17 passed, 0 warnings, 0 failures -> PASS`.

## Layout

| Directory | Contents |
|---|---|
| `00_START_HERE/` | Entry point, manifest, claim/figure/table/run indexes, limitations, license |
| `01_MANUSCRIPT_SNAPSHOT/` | The manuscript PDF as staged (see warning above) |
| `02_CONTROLLED_STUDIES/` | Lorenz, heterogeneous oscillator, pendulum, heat equation |
| `03_DIII_D_SOURCE_OBJECT/` | Observational object S7.1, retrieval metadata, access notes |
| `04_DIII_D_DESCRIPTIVE/` | `q_desc` canonical run, coefficient conditioning, implicit closure |
| `05_DIII_D_RECONSTRUCTION/` | `q_rec` lineage end to end, including the negative parent result |
| `06_PAPER_FIGURES_ONLY/` | Assets, scripts and frozen data for manuscript figures only |
| `07_TABLES_AND_REPORTED_NUMBERS/` | Numerical claim ledger |
| `08_CONTRACTS_PROVENANCE_AND_QUALIFICATION/` | Artifact lineage |
| `09_REPRODUCIBILITY/` | Environment capture, build scripts, verification script |
| `10_REFERENCED_HISTORICAL_LINEAGE/` | Retired and superseded material, explicitly marked |
| `90_AUDIT_REPORTS/` | Missing, ambiguous, excluded, duplicate and unresolved-field audits |

## Two things that will bite you

**The negative result is not a mistake.** `05_DIII_D_RECONSTRUCTION/07_Protected_Qualification_FAILURE/`
records a genuine qualification failure (REL 0.7424, Δ₁ +0.5321, Ω\*_rec empty). It is
canonical and is preserved byte-for-byte. It is the parent of the positive
descendant result, not a superseded draft of it.

**Coordinate identifiers contain `|` inside parentheses** — for example
`LEVEL_RATE(cerqrott12|ece35)`. Splitting a support string naively on `|` silently
corrupts three of the six fold supports (sizes become 12, 12, 12, 14, 13, 13 instead
of 12 × 6). Split at parenthesis depth 0, or use the `coordinates` field in
`folds/fold_*_result.json`, which is already a JSON list.

## Data access

The 62 DIII-D `*_resampled.npz` source archives (1.1 GB) are **not redistributed
here** because redistribution rights are not established. They are *restricted, not
missing*: each is indexed with its SHA-256 and original path in
`03_DIII_D_SOURCE_OBJECT/source_access_notes/RESTRICTED_SOURCE_INDEX.csv`.

See [`00_START_HERE/ACCESS_AND_LICENSE.md`](00_START_HERE/ACCESS_AND_LICENSE.md) for
terms and [`00_START_HERE/KNOWN_LIMITATIONS.md`](00_START_HERE/KNOWN_LIMITATIONS.md)
for what this package does not contain.
