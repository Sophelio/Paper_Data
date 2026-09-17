# Reproduction guide

Everything below runs offline against the bundled artifacts.

## 0. Verify the package before trusting it

```
python 09_REPRODUCIBILITY/validation_scripts/verify_paper_data.py
```

Recomputes every SHA-256 against `00_START_HERE/PACKAGE_MANIFEST.csv`, checks
figure allow-list compliance, confirms no manifest source path points inside
`Paper_Data`, and re-derives the headline numbers from the artifacts. Exit code 0
means the package is internally consistent.

## 1. Environment

| | |
|---|---|
| Python | 3.13.5 |
| numpy / pandas / scipy | 2.5.2 / 3.0.5 / 1.18.1 |
| matplotlib / scikit-learn | 3.11.1 / 1.9.0 |
| platform | Windows-11-10.0.26200-SP0 |

`environment/requirements_frozen.txt` is a full `pip freeze`;
`environment/environment.yml` is a convenience conda export. Neither existed in
the repository — both were generated here.

**Version sensitivity.** The DIII-D utility uses exact-equality comparisons on
fit scores, so a different BLAS or numpy build could in principle change a
selected support. Reproduce in the environment above for bit-identical results.

## 2. What you can reproduce, in increasing cost

### Free — read the frozen results
Every number in the paper is already in a machine-readable artifact. Start from
`00_START_HERE/CLAIM_TO_ARTIFACT_INDEX.csv`.

### Seconds — re-verify the DIII-D reconstruction lineage
```
python 05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/audit_s7.py
```
Checks 527 frozen artifacts across 21 stages and recomputes the headline metrics.

### Minutes — regenerate the paper figures
```
python 06_PAPER_FIGURES_ONLY/Fig_06_d3d_task_conditioned_4panel/figure_source/d3d_task_conditioned_4panel_v5.py
python 06_PAPER_FIGURES_ONLY/Fig_05_lorenz_representation_landscape/figure_source/figure5_lorenz_representation_landscape_final_tnr_v5_nature.py
```
Every figure folder is self-contained: its script needs no arguments, reads only
its own `figure_source/` and `figure_source_data/`, and writes the PDF/PNG/SVG into
that figure folder. The figures need LaTeX with `lmodern` and matplotlib 3.9.x (see
`06_PAPER_FIGURES_ONLY/README.md`). Each figure folder's README gives its exact command.

### Minutes — independent recomputations of the DIII-D contract
```
python 05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/_audit/verify_range_support.py out.json
python 05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/_audit/verify_target_ancestry.py table.csv summary.json
```
These re-implement the range-support predicate from the frozen policy equation
and re-run the target-ancestry test. **They need the restricted source archive**
(see §4).

### Longer — controlled studies
Each study folder carries its own scripts, config and README. The Lorenz
benchmarks reproduce from `benchmark_config.yaml` plus `scripts/`.

## 3. Dependency order

```
03_DIII_D_SOURCE_OBJECT      (object, units, provenance)
        |
        +--> 04_DIII_D_DESCRIPTIVE      (q_desc: aligned run -> coefficients -> audits)
        |
        +--> 05_DIII_D_RECONSTRUCTION   (q_rec: contract -> ontology -> search ->
                                         FAILURE -> diagnosis -> revision ->
                                         cross-fitting -> Q_rec*)
                    |
                    +--> 06_PAPER_FIGURES_ONLY / 07_TABLES_AND_REPORTED_NUMBERS

02_CONTROLLED_STUDIES is independent of the DIII-D branches.
```

## 4. What you cannot rerun from this package alone

The 62 DIII-D `.npz` archives are **not bundled** (see
`00_START_HERE/ACCESS_AND_LICENSE.md`). Anything that reads raw signals —
re-running the search from scratch, or the two independent recomputations above —
needs authorised access to the archive. Their SHA-256 values are in
`03_DIII_D_SOURCE_OBJECT/source_access_notes/RESTRICTED_SOURCE_INDEX.csv` so you
can confirm you hold identical bytes.

Everything downstream of the aligned exports reproduces from what is here.

## 5. Rebuilding this package

```
python build_paper_data.py          # copy artifacts, write manifest + checksums
python build_paper_data_docs.py     # indexes and claim ledger
python build_paper_data_audit.py    # audit reports
python build_paper_data_readmes.py  # READMEs
python build_paper_data_repro.py    # figure READMEs, environment, this file
```

Copies from the canonical sources in `D:\SIR_paper\` and the external DIII-D
tree. Non-destructive: nothing outside `Paper_Data` is written.
