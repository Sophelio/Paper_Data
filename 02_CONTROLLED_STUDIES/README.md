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
