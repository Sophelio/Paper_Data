# Lorenz task-conditioning benchmark

Second Lorenz study, testing **task-conditioned relational discovery** rather
than feature augmentation: does the *same* scientific object, interrogated under
*different* discovery contracts, yield *different* qualified representations?

It does **not** claim PySINDy cannot do task conditioning. PySINDy is
extensible, is given every SIR-generated coordinate here, and serves as the
common sparse solver throughout. See `audit/PYSINDY_CAPABILITY_AUDIT.md`.

## Relationship to the first benchmark

`D:/SIR_paper/Lorenz/benchmark/` is **EXPOSED DEVELOPMENT EVIDENCE**. Its
protected test results were inspected and informed this design, so its 48
trajectories are used here only for search, cross-validation and calibration —
never as confirmatory evidence. Confirmatory evidence comes from **24 new
trajectories** under a new seed, new seed trajectory and different initial
condition, audited for non-duplication. See
`audit/PRIOR_KNOWLEDGE_AND_POSTHOC_DESIGN_AUDIT.md`.

## Contracts

| Contract | Object | Objective |
|---|---|---|
| `K_containment` | full state + exact derivatives | recover the canonical Lorenz generator |
| `K_accuracy_clean` | clean partial (x,y) | minimum mean grouped-CV RMSE |
| `K_compact_clean` | clean partial (x,y) | one-SE-equivalent, then fewest coordinates → best conditioning → fewest terms → most stable |
| `K_robust_noise` | partial (x,y) **with** an observational-uncertainty model | minimum worst-case CV error over σ ∈ {0, 0.005, 0.01}, then the same lexicographic rule |

Full definitions: `contracts/CONTRACT_DEFINITIONS.md`.

## Layout

    benchmark_config.yaml            frozen configuration
    PRECONFIRMATION_FREEZE.json      hashes; the evaluator refuses to run if they change
    contracts/                       contract definitions + selections
    shared/confirmation/             24 protected trajectories
    shared/manifests/                confirmation lineage
    prior_benchmark_reference/       development data referenced by hash (not copied)
    scripts/                         make_confirmation, engine, run_contracts, run_confirmation
    sir_mcp/containment/             MCP-native containment runs
    tables/, figures/, audit/, tests/, logs/

## Reproduce

    cd D:\SIR_paper
    $P = ".venv_lorenz_benchmark\Scripts\python.exe"
    & $P Lorenz\task_conditioning_benchmark\scripts\make_confirmation.py
    & $P Lorenz\task_conditioning_benchmark\scripts\run_contracts.py     # writes the freeze
    & $P Lorenz\task_conditioning_benchmark\scripts\run_confirmation.py  # enforces the freeze
    & $P -m pytest Lorenz\task_conditioning_benchmark\tests -v

## Important scope note

The SIR MCP executed the **containment** contract natively (three runs, exact
support recovery). It could **not** execute the task-conditioned contracts
natively: it exposes no held-out validation, no declarable task utility and no
qualified-model-set primitive. Those contracts were therefore implemented
outside the MCP over numerically equivalent coordinates — which means the
task-conditioning result is, by construction, an *external wrapper around
PySINDy*, exactly the control Step 12 asks for. This is reported as a limitation
on the strength of the MCP-native claim, not worked around.
