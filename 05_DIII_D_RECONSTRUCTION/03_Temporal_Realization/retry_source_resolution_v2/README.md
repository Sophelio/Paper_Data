# S7.4 retry — Mathematical interpretation `X_rec`

**Freeze:** `D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2`
**Status:** `FROZEN_READY_FOR_S7.5` · acceptance **44/44** · **`X_rec`
instantiated: YES**
**Supersedes:** S7.4 V1 (stopped at the temporal gate; preserved unmodified)
**Authoritative boundary:** `D3D-SIR-S7.3-…-SOURCE-RESOLUTION-V2`

```
X_rec = { (T_s, x_s, y_s, a_s) : s in S_rec },   |S_rec| = 62

y* = density        line-averaged electron density, m^-3
x  = 78 primitives  7 broad families, 8 mathematical type blocks
T_s                 discharge-specific, 5.853 - 14.187 ms, 53 distinct values
```

## The gate that stopped V1 now passes

`density` is upstream-upsampled in **0 of 62** discharges — its archived and
source-supported cadences coincide, which is exactly what failed for `vsurf`. No
admitted quantity forces a grid finer than its resolution estimate; all 62
discharges are validation-feasible; `vsurf` remains excluded.

## Start here

| File | What it is |
|---|---|
| `S7_4_MATHEMATICAL_INTERPRETATION_FINAL.md` | manuscript-ready prose |
| `S7_4_MATHEMATICAL_INTERPRETATION_AUDIT_REPORT.md` | the full internal audit |
| `X_REC_DEFINITION.md` | the formal object, blocks, spaces |
| `TEMPORAL_SEMANTICS.md` | `t` vs `tau`, cadence semantics, flags |

## Two things a reader should not miss

**Grids are discharge-specific by design.** 53 distinct spacings across 62
discharges. The ensemble shares its *typed coordinate support*, not its
timestamps. The contract holds because validation windows live in normalized
time, coefficients are per-discharge, and gate V7 constrains comparisons
*within* a discharge.

**Four of the eight type blocks are dimensionally heterogeneous** — `X_NBI`
(W + N·m), `X_mag` (T + A + 2 uncalibrated), `X_density_aux` (m⁻³ + eV). S7.5
must apply dimensional rules at **component** level; a sum within a block is not
automatically admissible.

## Typed blocks

| Block | Dim | Canonical unit | Homogeneous |
|---|---|---|---|
| `X_ECE` | 40 | eV | yes |
| `X_CER_v` | 7 | m/s | yes |
| `X_CER_Ti` | 7 | eV | yes |
| `X_NBI` | 10 | W, N·m | **no** |
| `X_mag` | 4 | T, A, uncal ×2 | **no** |
| `X_fs` | 4 | ph/(sr m² s) | yes |
| `X_gas` | 4 | V | yes |
| `X_density_aux` | 2 | m⁻³, eV | **no** |

## Machine-readable

```
X_REC.json                       the object, machine-readable
typed_signal_blocks.csv          78 rows: type, unit, cadence, flags
trajectory_index.csv             62 rows: T_s, dt_s, N_s, cohort, era, period
temporal_semantics.json          t vs tau, cadence semantics, 16-vs-22
temporal_resolution_types.csv    78 rows: level/derivative admissibility
predictor_dependency_edges.csv   pinj = sum(pinj_*), exact
interpretation_constraints.json  assumptions made and NOT made
S7_4_ACCEPTANCE_CHECKS_V2.json   44 checks
S7_4_FREEZE_V2.json              freeze record and all artifact hashes

manifests/PARENT_FREEZE_VERIFICATION_V2.json
manifests/TEMPORAL_GATE_VERIFICATION_V2.json
```

## Access

**Zero archives opened.** Everything is metadata-derived from the S7.1 quality
summary and the S7.3R corrected boundary and grid requirements. No signal value
read — development or external. External cohort (42) remains sealed.

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\04_mathematical_interpretation\retry_source_resolution_v2\scripts\s7_4_build_x_rec.py
```

Deterministic; no seeds. Exits non-zero on parent drift or a failed temporal
gate.

## Stage gate

No coordinate · no product · no ratio · no derivative · no phase derivative ·
no `G_rec` · no `A_rec` · no model · no baseline · no correlation · no external
value · target unchanged · 78 predictors unchanged · `vsurf` still excluded ·
**S7.5 not started.**
