# Lorenz nested-representation benchmark

Controlled benchmark for Section 1.4 / Figure 6. Tests three narrow claims:
**containment** (conventional sparse recovery as a restricted SIR contract),
**representation expansion** (the same estimator given an expanded, admissible
coordinate library), and **learner independence** (does the selected
representation also help an unchanged MLP).

It is **not** a superiority test against PySINDy or neural networks. PySINDy is
explicitly given the same expanded features.

**Result: classification C — LEARNER_SPECIFIC_AUGMENTATION.**
See `BENCHMARK_REPORT.md` and `audit/FINAL_REVIEWER_AUDIT.md`.

## Layout

    benchmark_config.yaml       frozen configuration (declared before evaluation)
    benchmark_results.json      headline results
    benchmark_run_manifest.json artifact hashes + environment
    BENCHMARK_REPORT.md         full report
    SECTION_1_4_RESULTS.tex     manuscript-ready section (not auto-inserted)
    shared/data                 containment trajectory + 48-trajectory ensemble
    shared/splits               frozen whole-trajectory splits (32/8/8)
    shared/manifests            source lineage, environment freeze
    scripts/                    make_dataset, features, run_containment,
                                run_benchmark, run_ablations, make_tables, make_figure
    sir/containment             restricted-SIR containment result
    sir/frozen_selection        FROZEN_REPRESENTATION.json (hashed)
    pysindy/containment         canonical PySINDy recovery
    tables/                     results, per-trajectory, ablations, summary (csv/tex)
    figures/                    sir_nested_model_benchmark.{png,pdf,svg}
    audit/                      5 audits + SIR MCP capability audit + reviewer audit
    tests/                      pytest suite (27 tests)
    logs/pytest_final.txt       test output

## Reproduce

    cd D:\SIR_paper
    $P = ".venv_lorenz_benchmark\Scripts\python.exe"
    & $P Lorenz\benchmark\scripts\make_dataset.py
    & $P Lorenz\benchmark\scripts\run_containment.py
    & $P Lorenz\benchmark\scripts\run_benchmark.py
    & $P Lorenz\benchmark\scripts\run_ablations.py
    & $P Lorenz\benchmark\scripts\make_tables.py
    & $P Lorenz\benchmark\scripts\make_figure.py
    & $P -m pytest Lorenz\benchmark\tests -v

Order matters: `run_benchmark.py` writes the freeze that the later steps consume.

## Notes

- The canonical generator `Lorenz/Lorenz_attractor.py` is **reused**, not copied.
  Nothing outside `benchmark/` is modified.
- Isolated environment `D:/SIR_paper/.venv_lorenz_benchmark/` (PySINDy 2.1.0);
  the manuscript Anaconda environment is untouched.
- The SIR MCP could not be reached for this project (Dalia binds one project
  environment at a time). See `audit/SIR_MCP_CAPABILITY_AUDIT.md` for what that
  affected and what was done instead.
