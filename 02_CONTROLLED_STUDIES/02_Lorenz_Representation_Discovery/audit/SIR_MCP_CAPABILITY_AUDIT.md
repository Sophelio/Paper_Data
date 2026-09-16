# SIR MCP capability audit

**Date:** 2026-08-27
**Server:** `dalia` → `http://127.0.0.1:8765/mcp`
**Lorenz project:** `b595325c-ed38-4a7e-b3f0-d2826df64b28`
**Engine status:** `sir/status` → `{"available": true, "vendored": true}`

**The blocker reported in the first benchmark is resolved.** The Lorenz project
is loaded and the SIR engine executes.

---

## 1. Verified capability surface

| Requested capability | MCP operation | Status |
|---|---|---|
| Scientific/observational object creation | `create_project`, provider files, `set_data_source` | **partial** — a project + provider is the object; O's uncertainty model and admissibility set are not first-class fields |
| Discovery contract | `run_sir(target_variable, target_type, variables, order, num_terms, model_type, loss, constant, constraints, regularizer, iterations)` | **yes** |
| Source variables | `run_sir(variables=…)`, `sir/variables` | **yes** |
| Coordinate operators | `run_sir(data_processing=[x, dx, y, dy, quotients, xPhaseder, yPhaseder, …])` | **partial** — family toggles, not individually addressable coordinates |
| Conditioning operators | `prep_steps` (`sir_feature_zscore`, `sir_nmin`, `shift_up`, `normalize_*`, `smooth_*`) | **yes** |
| Temporal derivatives | `data_processing` `dx`/`dy`; prep block `differentiate` | **yes** |
| Lags | — | **no** dedicated lag operator |
| Algebraic coordinates | products appear via `order` ≥ 2 in the search | **yes** (implicit) |
| Quotient coordinates | `data_processing` `quotients` | **yes** (family-level) |
| Phase derivatives | `data_processing` `xPhaseder`, `yPhaseder` | **yes** (family-level) |
| Reference-shifted regularised | project transform block | **not in this project** — the Lorenz project's blocks are the built-ins + `test`; the RS/SC family lives in the DIIID project's `transforms.py` |
| Sensitivity-centered | same | **not in this project** |
| Coordinate fit/apply semantics | implicit in blocks | **partial** — not separately addressable |
| Sparse relation fitting | `model_type` ∈ {SUBOPTIMAL_SEARCH, OPTIMAL_SEARCH, KITCHEN_SINK}, `num_terms`, `regularizer` | **yes** |
| Explicit relation fitting | `fixed_equation` | **yes** |
| Model/solver primitives | — | **no** — the search engine is fixed; PySINDy cannot be injected as the solver |
| Task utilities | — | **no** — the objective is the fitted loss (`loss` ∈ l1/l2/soft_l1/cauchy/arctan…), not a declarable task utility |
| Validation | `validate_only`, `sir/validate_dataset` | **partial** — dataset validation only, no held-out contract |
| Provenance | `poll_sir` (formulas, error, run id), `sir/list_runs`, `sir/run_results`, `sir/compare`, `export_features` | **yes** |
| Qualified result export | `sir/run_results`, `export_features` | **partial** — a run's result, not a qualified model set |

---

## 2. What the MCP actually executed for this benchmark

**Containment (Contract A) — executed natively through the MCP.** Three runs on
`lorenz_dt001_exact_derivatives`, `target_type=Derivative`, `constant=false`,
`loss=l2`, `OPTIMAL_SEARCH`:

| target | run id | `data_processing` | order / terms | recovered | final error |
|---|---|---|---|---|---|
| x | `20260827-172225-76c6` | x, y | 1 / 2 | `10.000[y] − 10.000[x]` | 1.35e−6 |
| y | `20260827-172239-bc92` | x, y | 2 / 3 | `27.998[x] − 0.999[y] − 1.000[x][z]` | 5.27e−6 |
| z | `20260827-172200-2231` | x, y | 2 / 2 | `−2.667[z] + 1.000[x][y]` | 6.66e−6 |

Exact support recovery on all three equations.

**A semantic difference worth recording.** SIR partitions `data_processing`
into a *feature* family (`x`) and a *target* family (`y`); the target
variable's own level is only available when `y` is included. A first run with
`data_processing=["x"]` therefore could not express `dz/dt = xy − (8/3)z` and
returned `−0.920[x][x] + 1.319[x][y]` (error 1431). This is not a defect: it is
SIR's target/feature separation, and it differs from SINDy's convention of
regressing each state derivative on the full state. Recorded because it changes
how a contract must be written, not because either convention is wrong.

---

## 3. Capabilities absent from the MCP, and how they were handled

| Missing | Impact on this benchmark | Handling |
|---|---|---|
| Held-out / grouped-CV contract | the whole confirmation protocol | implemented outside the MCP over the same coordinates |
| Declarable task utility (compactness, worst-case-over-noise) | contracts C and D cannot be expressed to the engine | implemented outside the MCP as declared, frozen rules |
| Qualified model set | the one-SE equivalent set | implemented outside the MCP |
| Solver injection (PySINDy inside SIR) | Step 7's preferred variant | not possible; MCP-native search used instead and compared |
| Individually addressable coordinates | the 18-candidate grammar | coordinates built with the audited reference implementation |
| RS/SC blocks in the Lorenz project | those two candidate families | supplied from the audited implementation, verified against Archaieus at 1e-12 |
| Lag operator | stencil lags | built locally inside the declared boundary |

**Consequence for the classification.** The MCP executed the containment
contract natively and end to end. It could **not** execute contracts B, C and D
natively, because it exposes no held-out validation, no task utility and no
qualified-model-set primitive. Those contracts were run outside the MCP over
coordinates that are numerically equivalent to it.

This is reported honestly rather than papered over: the task-conditioning result
is **not** an MCP-native result, and the benchmark is classified accordingly.
See `FINAL_REVIEWER_AUDIT.md`.
