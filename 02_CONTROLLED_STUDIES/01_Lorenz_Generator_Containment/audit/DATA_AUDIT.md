# Data audit

**Date:** 2026-08-27

## Provenance

| Artifact | Status | Detail |
|---|---|---|
| `shared/data/containment.parquet` | **REUSED** | verbatim copy of `Lorenz/data/lorenz_dt001_exact_derivatives.parquet` (40 001 samples, dt=0.001, t∈[0,40], x0=(1,1,1)) |
| `shared/data/ensemble/traj_000..047.parquet` | **GENERATED** | 48 trajectories, dt=0.005, tmax=12.0 (2401 samples each) |
| Generator | **REUSED** | `Lorenz/Lorenz_attractor.py::generate_lorenz`, not re-implemented |

Integrator `scipy.integrate.solve_ivp(method="DOP853", rtol=1e-12, atol=1e-12)`;
σ=10, ρ=28, β=8/3. Per-trajectory derivatives are the **analytic** Lorenz
right-hand side (`add_exact_derivatives`), used only for the containment test and
the audit identity — never as a benchmark feature.

## Initial conditions

Sampled reproducibly (seed 20260827) from a single long canonical trajectory
(dt=0.001, tmax=400, burn-in 20) at evenly spaced blocks with one seeded offset
per block. Every benchmark trajectory therefore starts **on the attractor**, and
no two initial states are near-duplicates.

## Verified

- All 49 artifact SHA-256 hashes match `shared/manifests/source_lineage.json`
  (`test_dataset_hashes_match_manifest`).
- Uniform spacing dt=0.005 to 1e-9 (`test_ensemble_shape_and_spacing`).
- Stored derivatives satisfy the Lorenz field to 1e-12
  (`test_exact_derivatives_satisfy_the_lorenz_field`).
- Generator is bit-deterministic across repeat calls
  (`test_generator_is_deterministic`).
- Nothing outside `Lorenz/benchmark/` was written to; the existing Lorenz example
  and its canonical data are unmodified.
