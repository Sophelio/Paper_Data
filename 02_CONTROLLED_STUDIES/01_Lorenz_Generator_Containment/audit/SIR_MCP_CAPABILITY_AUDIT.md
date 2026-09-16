# SIR MCP capability audit

**Date:** 2026-08-27
**MCP server:** `dalia` → `http://127.0.0.1:8765/mcp` (HTTP, user scope, connected)

---

## 1. Operations the MCP exposes

| Capability required by the benchmark | MCP operation | Available |
|---|---|---|
| Observational-object / project creation | `create_project(name, template)` | yes (templates: starter, weather, fusion, csv) |
| Provider authoring (source variables) | `save_provider_file`, `create_file`, `reload_provider`, `check_syntax` | yes |
| Discovery contract (target, variables, order, terms) | `run_sir(target_variable, target_type, variables, num_terms, order, model_type, loss, constant, constraints, regularizer, iterations)` | yes |
| Derivatives / feature families | `run_sir(data_processing=[x, dx, y, dy, quotients, xPhaseder, yPhaseder, …])` | yes, as **family toggles** — not individually addressable coordinates |
| Lags | — | **no** dedicated lag operator exposed |
| Algebraic products / ratios | `data_processing` families (`quotients`) | partial — family-level only |
| Classical phase derivatives | `data_processing` `xPhaseder`/`yPhaseder` | yes (family-level) |
| Reference-shifted regularized phase | `prep_steps` block `reference_shifted_phase` | yes, via project transform blocks |
| Sensitivity-centered reference-shifted phase | `prep_steps` block `sensitivity_centered_phase` | yes, via project transform blocks |
| Coordinate fit/apply semantics | implicit in the blocks (cohort-fitted, frozen) | yes, but not separately addressable |
| Scaling / conditioning | `prep_steps` (`sir_feature_zscore`, `normalize_*`, `sir_nmin`) | yes |
| Sparse / explicit relation fitting | `run_sir(model_type=SUBOPTIMAL_SEARCH \| OPTIMAL_SEARCH \| KITCHEN_SINK)`, `fixed_equation` | yes |
| Coordinate **selection** as a first-class op | — | **no** — selection is implicit in the search, not exposed as a separate contract |
| Held-out / train-test validation | — | **no** — `record_ids` chooses which records a run uses; there is no fit-on-train / apply-to-test contract |
| Provenance / export | `poll_sir` (formulas, error, run id), `run_module_command(sir, run_results / list_runs / compare)`, `export_features` | partial |
| Dry-run / validation | `run_sir(validate_only=True)`, `sir/validate_dataset` | yes |

---

## 2. Blocking limitation encountered

**The SIR engine could not be reached for the Lorenz project in this session.**

Every SIR call against the Lorenz project (`b595325c-…`) returns:

> this project runs in its own Python environment, which is not the one
> currently loaded. Go Home and open the project again to start it

Confirmed for `sir/status`, `get_sir_state`, and `reload_provider`.

Diagnosis: Dalia binds **one project worker environment at a time**. The
`DIIID_SIR_Paper` project (which declares an `onnxruntime` extra, env key
`64c96aea3723`) is the loaded one; the Lorenz project declares no extra
environment and therefore needs the *default* worker. Switching requires
opening the project from the Dalia Home screen.

There is **no MCP operation that switches the active project environment.**
`navigate` moves the user's view between modules *within* the open project and
takes no project id. So this cannot be resolved from the MCP side.

### Consequence for the benchmark

Two components could not be executed through the MCP:

1. **Restricted-SIR containment** (Step 5B).
2. **SIR end-to-end evaluation of the frozen representation** (Step 8).

### What was done instead, and why it is defensible

For **containment**, the restricted SIR contract was implemented directly in
`scripts/run_containment.py::run_restricted_sir` as sequentially thresholded
least squares over the identical cubic library, consuming the identical exact
derivatives. This is not a re-invention of SIR: it is precisely the restricted
contract the containment test *defines* — same source variables, same
polynomial degree, same allowed terms, same coefficient model, same sparsity
rule. Its agreement with PySINDy (max |Δcoefficient| = 3.9×10⁻¹⁴) is reported
as such and **is not presented as an MCP-executed SIR result**.

For the **relational coordinates**, no ad hoc formula was substituted. The
reference-shifted and sensitivity-centered coordinates come from
`D:\SIR_paper\DIIID_example\transforms.py`, which is the audited reference
implementation verified elementwise (`rtol=0, atol=1e-12`) against canonical
Archaieus in `AUDIT_dalia_transform_family.md`, and which is byte-identical in
math to the Dalia project blocks reachable over this same MCP. This satisfies
the "do not substitute an ad hoc formula" requirement through equivalence to
the canonical implementation rather than through the MCP transport.

### To complete the MCP-native path

Open the Lorenz project once from Dalia's Home screen, then re-run:

```
scripts/run_sir_mcp.py     # not yet executed — blocked on the above
```

Note a second limitation that persists even after the environment is loaded:
the MCP has **no held-out contract**. A SIR run fits over the `record_ids` it
is given. Reproducing the protected-test protocol would require running SIR on
the 32 train records, exporting the relation, and applying it to the 8 test
records outside the MCP — which is what the local evaluation already does.

---

## 3. Capabilities absent from the MCP (documented, not worked around silently)

| Missing | Impact | Handling |
|---|---|---|
| Active-project environment switch | blocks all SIR calls for a non-loaded project | reported above; requires one UI action |
| Explicit lag operator | lags built locally on the declared stencil | `features.py::shift`, inside the declared information boundary |
| Individually addressable coordinates in `data_processing` | families are all-or-nothing | local coordinate library used, with each coordinate declared and provenance-tracked |
| Train/apply (held-out) contract | cannot express the protected-test protocol | fit/apply implemented locally with frozen parameters (`features.CoordinateFit`) |
| Coordinate selection as a first-class operation | selection is implicit in the search | declared greedy rule in `benchmark_config.yaml`, frozen to `FROZEN_REPRESENTATION.json` |

None of these were silently reinterpreted: every local adapter is minimal, is
declared here, and is tested against the canonical implementation where one
exists (`tests/test_benchmark.py`).
