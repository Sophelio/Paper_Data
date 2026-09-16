# Confirmation integrity audit

**Date:** 2026-08-27 · **Verdict: PASS**

## Independence from development

| Property | Development (exposed) | Confirmation (protected) |
|---|---|---|
| ensemble seed | 20260827 | **20260827904** |
| seed-trajectory x0 | (1, 1, 1) | **(-3.1, 2.7, 19.4)** |
| seed-trajectory tmax | 400 | **900** |
| burn-in | 20 | **40** |
| trajectories | 48 | 24 |
| noise seeds | 11, 12, 13 | **901, 902, 903** |

Development trajectories are referenced by SHA-256 in
`prior_benchmark_reference/imported_hashes.json` and were **never copied** into
this benchmark (`shared/development/` is empty, asserted by
`test_development_referenced_by_hash_not_copied`).

## Non-duplication of initial states

Every confirmation initial state was compared against all 48 development
initial states:

    min separation      0.6763
    median separation   2.4920
    max separation     10.0086
    declared threshold  0.5
    violations          0

## What the confirmation set was never used for

Coordinate selection, transform fitting, hyperparameter selection, task
thresholds, the equivalence floor, noise configuration, MLP early stopping,
sparse threshold selection, and the choice of which contracts to report. All of
those were fixed on development data and hashed into
`PRECONFIRMATION_FREEZE.json` before `run_confirmation.py` opened a single
confirmation file.

## Freeze enforcement

`run_confirmation.py::enforce_freeze` recomputes SHA-256 for all 12 frozen files
and raises `SystemExit` on any mismatch. The confirmation run reported
`freeze verified: 12 files unchanged`.

Covered: `benchmark_config.yaml`, `scripts/engine.py`, `scripts/run_contracts.py`,
`contracts/contract_selections.json`, `shared/manifests/confirmation_lineage.json`,
all six `sir_contract/` modules, and the external wrapper.

## Integrity

All 24 confirmation parquet hashes match `confirmation_lineage.json`
(`test_confirmation_hashes_match_manifest`), and no confirmation file hash
collides with any development file hash.

## Residual risk

The confirmation set has now been **inspected**. If a substantive bug is found
in the analysis from here, this ensemble is spent: per the standing rule, a
fresh ensemble under a new seed would be required, and these results could not
be reused as confirmatory evidence.
