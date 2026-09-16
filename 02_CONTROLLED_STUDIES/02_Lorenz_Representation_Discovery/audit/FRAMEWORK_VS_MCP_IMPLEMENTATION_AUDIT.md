# Framework vs MCP implementation audit

**Date:** 2026-08-27
**`SIR_IMPLEMENTATION_STATUS` = `MCP_NATIVE_PRIMITIVES_PLUS_AUDITED_CONTRACT_HARNESS`**
**Implementation surface: `IMPLEMENTATION_SURFACE_PARTIAL`**

The current SIR MCP does not yet expose the complete task-conditioning and
qualification layer of the SIR framework. This benchmark therefore executes
those contract-level operations in an audited reference harness while using
MCP-native SIR primitives for the operations the MCP currently exposes.

**This is a software implementation limitation, not evidence against the
mathematical framework.** It is carried as a limitation and does not by itself
invalidate the scientific benchmark.

---

## Terminology (never used interchangeably)

| Term | Meaning |
|---|---|
| **SIR framework** | the mathematical formulation in the manuscript |
| **SIR contract harness** | `sir_contract/` — audited benchmark-local reference implementation of the contract layer |
| **SIR MCP** | the Dalia-hosted SIR engine reached over the `dalia` MCP server |
| **PySINDy solver** | STLSQ acting as one admissible relation solver `R_q(C)` |

---

## Operation-by-operation map

| Operation | Layer | Justification |
|---|---|---|
| Lorenz containment (dx, dy, dz recovery) | **MCP_NATIVE** | executed by `run_sir`; three runs, exact support (`sir_mcp/containment/`) |
| Dataset validation for containment | **MCP_NATIVE** | `run_sir(validate_only=True)` |
| Containment relation fitting | **MCP_NATIVE** | `OPTIMAL_SEARCH` inside the MCP |
| Containment provenance / run export | **MCP_NATIVE** | `poll_sir`, run ids recorded |
| Conventional PySINDy containment comparator | **PYSINDY_SOLVER** | independent cubic-library STLSQ |
| Coordinate family: rate (`dx`,`dy`) | **LOCAL_REFERENCE** (MCP-equivalent family exists) | MCP `data_processing` exposes `dx`/`dy` as a *family toggle*, not an addressable coordinate on a 5-point stencil; built locally to match the declared `I_k` |
| Coordinate family: products | **LOCAL_REFERENCE** (MCP-equivalent) | MCP forms products implicitly via `order ≥ 2` search terms |
| Coordinate family: quotients / phase | **LOCAL_REFERENCE** (MCP-equivalent) | MCP exposes `quotients`, `xPhaseder`, `yPhaseder` as family toggles; the benchmark needs individually addressable, individually maskable coordinates |
| Coordinate family: raw stencil lags | **LOCAL_REFERENCE** | the MCP exposes **no lag operator** |
| Coordinate family: curvature | **LOCAL_REFERENCE** | higher-order stencil not exposed |
| Coordinate family: CA / reference-shifted / sensitivity-centered | **LOCAL_REFERENCE** | those blocks live in the DIIID project's `transforms.py`, not the Lorenz project; the implementation is Archaieus-verified at `atol=1e-12` (`AUDIT_dalia_transform_family.md`). Blocks were deliberately **not** ported: the load-bearing gap is contract orchestration, not coordinate expressibility |
| Scientific object `O` | **SIR_CONTRACT_HARNESS** | `sir_contract/scientific_object.py`; no MCP primitive represents `E`, `A`, or `Π` as a first-class object |
| Discovery contract `K_q` | **SIR_CONTRACT_HARNESS** | `sir_contract/discovery_contract.py`; MCP has no contract object |
| Candidate registry `C_q` | **SIR_CONTRACT_HARNESS** | `sir_contract/candidate_registry.py` |
| Grouped held-out validation `V_q` | **SIR_CONTRACT_HARNESS** | `sir_contract/validation.py`; **MCP exposes no held-out contract** |
| Task utility `U_q` | **SIR_CONTRACT_HARNESS** | `sir_contract/qualification.py`; **MCP's objective is a fitted loss, not a declarable task utility** |
| Qualified-model set / task equivalence | **SIR_CONTRACT_HARNESS** | `sir_contract/qualification.py`; **no MCP primitive** |
| Relation solver `R_q(C)` inside contracts | **PYSINDY_SOLVER** | STLSQ, used openly and deliberately — the embedding is the point |
| Contract orchestration | **SIR_CONTRACT_HARNESS** | `sir_contract/contract_runner.py` |
| External task-selection control | **INDEPENDENT_PYSINDY_WRAPPER** | `pysindy/external_contract_wrapper/wrapper.py`; reimplements CV, one-SE/floor equivalence, and the lexicographic ordering without importing `sir_contract` |
| Confirmation evaluation | **SIR_CONTRACT_HARNESS** + **PYSINDY_SOLVER** | freeze-enforced |

---

## Independence of the external control

`tests/test_wrapper_independence.py` (5 tests, passing) enforces that the
wrapper:

1. imports nothing from `sir_contract` (static AST analysis);
2. does not import the shared `engine` module carrying the harness's CV and
   selection helpers;
3. defines its own `score`, `choose_min` and
   `choose_equivalent_then_simplest`;
4. loads **no** `sir_contract` module when imported or exercised (dynamic check);
5. documents that agreement with the harness is the expected, desirable result.

Without these, Step 12 would be tautological.

---

## What must be true for this to remain scientifically valid

The benchmark stays valid as long as **coordinate provenance is trustworthy**.
It is: every `LOCAL_REFERENCE` coordinate family is either (a) numerically
equivalent to an MCP `data_processing` family, or (b) drawn from the audited
reference implementation verified elementwise against canonical Archaieus. If
coordinate provenance could not be established, this would become a
benchmark-invalidating problem — it is not.

---

## Implementation roadmap (recorded for the SIR MCP)

First-class MCP support is needed for:

1. **discovery contracts** as declarable objects;
2. **grouped held-out validation** (fit on a declared training set, apply
   unchanged to a protected set);
3. **task utility** distinct from the fitted loss (e.g. worst-case error over a
   declared observational-uncertainty envelope);
4. **qualified-model sets** and task-equivalence classes;
5. **model/solver primitives**, so an external estimator such as PySINDy can be
   injected as `R_q(C)` inside an MCP-run contract;
6. **individually addressable coordinates** (and a lag operator) rather than
   all-or-nothing `data_processing` family toggles.

Items 1–4 are what forced the contract layer out of the MCP for this benchmark.
