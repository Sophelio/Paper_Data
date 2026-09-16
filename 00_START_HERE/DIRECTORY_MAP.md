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
                                         y* = density; 78 of 95 admitted
03_Temporal_Realization                  grids, cadence, no-upsample policy
04_Initial_Ontology/                     23861 symbolic → 10778 atoms
05_Parent_Development_Search             162845 explored supports
06_Frozen_Parent_Support                 C_dev_star frozen before any protected access
07_Protected_Qualification_FAILURE       *** THE PARENT FAILED ***
08_Failure_Diagnosis/                    sensitivities; the state hypothesis REFUTED
09_Range_Support_Case_B_Revision         τ = 1; 10778 → 3451 atoms
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
