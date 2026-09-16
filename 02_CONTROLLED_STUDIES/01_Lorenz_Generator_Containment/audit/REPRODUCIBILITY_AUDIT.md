# Reproducibility audit

**Date:** 2026-08-27 · **Verdict: PASS**

## Environment

Isolated venv `D:/SIR_paper/.venv_lorenz_benchmark/` — the manuscript's Anaconda
environment was **not** modified and has no PySINDy installed.

| Package | Version |
|---|---|
| Python | 3.13.5 |
| **pysindy** | **2.1.0** (PyPI wheel) |
| numpy | 2.5.2 |
| scipy | 1.18.1 |
| scikit-learn | 1.9.0 |
| pandas | 3.0.5 |
| matplotlib | 3.11.1 |
| pytest | 9.1.1 |

Full freeze: `shared/manifests/environment_freeze.txt` (30 packages).
PySINDy was installed from PyPI rather than a git checkout; no commit hash
applies. `derivative 0.6.3` is pulled in as a PySINDy dependency but is not used
— all derivatives here are the explicit 5-point stencils in `features.py`.

## Determinism

| Source of randomness | Control |
|---|---|
| Initial-state sampling | seed 20260827, recorded in config |
| Split assignment | seed 20260827, frozen to `shared/splits/*.txt` |
| MLP initialisation | 5 predeclared seeds (0–4); mean ± sd reported |
| Ablation noise draws | fixed seeds per split (1000 / 2000 / 3000) |
| Bootstrap CIs | seed 0 |
| ODE integration | deterministic (DOP853, fixed tolerances) |

No unseeded RNG is used anywhere in the pipeline.

## Integrity

- `FROZEN_REPRESENTATION.json` self-hash verifies
  (`test_frozen_representation_is_self_consistent`); recomputing SHA-256 over the
  body reproduces the stored digest `96ee24b2c5f22e51…`.
- All 49 dataset artifacts hash-match `source_lineage.json`.
- `benchmark_run_manifest.json` records a SHA-256 prefix for every CSV, JSON,
  TXT, YAML, TEX, PY and MD artifact in the tree.
- **27/27 tests pass** — `logs/pytest_final.txt`.

## Re-running from scratch

```powershell
cd D:\SIR_paper
$P = ".venv_lorenz_benchmark\Scripts\python.exe"
& $P Lorenz\benchmark\scripts\make_dataset.py      # data + frozen splits
& $P Lorenz\benchmark\scripts\run_containment.py   # Step 5
& $P Lorenz\benchmark\scripts\run_benchmark.py     # Steps 6-9 (writes the freeze)
& $P Lorenz\benchmark\scripts\run_ablations.py     # Step 10  (~10 min)
& $P Lorenz\benchmark\scripts\make_tables.py       # Step 13
& $P Lorenz\benchmark\scripts\make_figure.py       # Step 14
& $P -m pytest Lorenz\benchmark\tests -v
```

Order matters: `run_benchmark.py` writes `FROZEN_REPRESENTATION.json`, which
`run_ablations.py`, `make_tables.py` and `make_figure.py` all consume read-only.

## Caveat

`run_benchmark.py` **re-derives** the frozen representation each time it runs
rather than loading an existing freeze. Re-running it on the same data and config
reproduces the same C* (the selection is deterministic), but a genuine
"evaluate-only against the existing freeze" entry point does not yet exist. Any
future change to the config or data would silently produce a *new* freeze rather
than failing loudly against the old one. Recommended hardening before the
representation is treated as immutable: add a `--use-frozen` path that loads
`FROZEN_REPRESENTATION.json`, verifies its hash, and refuses to re-select.
