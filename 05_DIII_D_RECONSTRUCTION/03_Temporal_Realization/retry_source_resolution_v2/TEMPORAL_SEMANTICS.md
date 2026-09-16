# Temporal semantics of `X_rec`

Machine-readable: `temporal_semantics.json`, `trajectory_index.csv` (62 rows),
`temporal_resolution_types.csv` (78 rows)

---

## Two time parameters, kept strictly apart

### Physical time `t` — seconds

The independent parameter of the sampled trajectories, and **the only parameter
for any later scientific temporal or trajectory-relational derivative**.

Per-discharge support `T_s`. Durations 3.780 – 5.360 s (median 4.598).

### Normalized validation time `tau` — dimensionless

```
tau_s(t) = (t − t_start,s) / (t_end,s − t_start,s)  ∈ [0, 1]
```

**`tau` exists only to specify the frozen calibration/evaluation block
fractions.** It carries no scientific dimension.

| Block | Calibration | Evaluation |
|---|---|---|
| A | `[0.00, 0.40)` | `[0.40, 0.50)` |
| B | `[0.00, 0.60)` | `[0.60, 0.70)` |
| C | `[0.00, 0.80)` | `[0.80, 0.90)` |

### The rule

```
scientific_derivative_parameter          = t (seconds)
derivative_with_respect_to_tau_primary   = FORBIDDEN
```

Discharge durations differ by a factor of 1.42 (3.780 s to 5.360 s).
Differentiating with respect to `tau` would rescale derivative values
differently in every discharge and destroy their physical dimensions. `tau` is a
bookkeeping coordinate for validation geometry and nothing else.

---

## Discharge-specific grids — a feature, not a defect

```
global_fixed_dt_required                        = false
common_coordinate_support_required              = true
common_time_grid_across_discharges_required     = false
```

| | Value |
|---|---|
| `Δt_s` range | **5.853 – 14.187 ms** |
| `Δt_s` median | 6.824 ms |
| distinct `Δt` values | **53** across 62 discharges |
| `N_s` range | 325 – 833 |
| total analysis samples | 40 572 |
| binding signal | `prmtan_teped` (26), `cerqrott3` (25), `cerqrott8` (10), `cerqrott13` (1) |

Development `Δt` 5.853 – 14.144 ms (`N_s` 326 – 782); external 5.859 – 14.187 ms
(`N_s` 325 – 833). Neither cohort is systematically coarser.

**The 62 trajectories are not forced onto one shared global grid.** What is
shared is the typed coordinate support, not the timestamps. The contract stays
coherent because:

- validation windows live in `tau`, so block fractions are cadence-independent;
- coefficients are discharge-specific under structural transfer;
- method comparisons use identical support **within** a discharge;
- gate V7 requires common scored samples **per discharge**, not identical
  timestamps across discharges.

---

## What the cadence estimate is — and is not

For signal `i` and discharge `s`:

```
Δt_src_hat(i,s) = archived_support(i,s) / (original_length(i,s) − 1)
```

Call this the **source-supported average cadence estimate**, or equivalently the
**provenance-supported temporal-resolution estimate**. It is **not** an exact
native cadence.

**Qualifications, all binding:**

- it is **support/count based**, not a local sampling interval;
- **original timestamps are unavailable**;
- **nonuniform original sampling cannot be reconstructed** from these metadata;
- the **upstream generator remains unavailable** (U001);
- it is the finest temporal resolution justified by the presently certified
  archival-input provenance, for the purposes of this study.

### The defensible claim

> The primary analysis grid is **no finer than the provenance-supported
> temporal-resolution estimate** used by the frozen numerical-admissibility
> policy.

### Claims explicitly not made

- ~~every analysis sample is an observation~~
- ~~every sample is source-supported~~
- ~~the grid recovers the exact native sampling of any diagnostic~~

This is a **semantic qualification on the language**, not a reason to reopen
S7.3R. The admissibility computation is unchanged; only its description is
tightened.

---

## The 16 vs 22 count — two different measurements

```
n_upsampled_any_discharge = 22
```

| Count | Criterion | Meaning |
|---|---|---|
| **22** | upstream-upsampled in **at least one** discharge | the operative count downstream |
| 16 | per-signal **median** length ratio > 1.01 | superseded |

A median cannot detect a signal upsampled in only a minority of discharges. The
two figures measure different things and are **not contradictory**; 22
supersedes 16 for all downstream use.

### Among the 78 predictors

**6 are `UPSTREAM_UPSAMPLED`** in at least one discharge:

`prmtan_neped` · `prmtan_teped` · `fs03da` · `fs04` · `fs04da` · `fs05da`

- **Admissible as levels** — the corrected grid respects their resolution
  estimate.
- **Derivative status `NUMERICAL_SENSITIVITY_ONLY`.** S7.5 handles it.

---

## Aliasing is independent, and a coarser grid does not fix it

**18 predictors carry `ALIASING_RISK`:** all 14 CER channels plus `bt`, `ip`,
`prmtan_neped`, `prmtan_teped`.

> **Aliasing is already embedded in the archived signal.** Coarsening the
> analysis grid does not remove it.

Levels remain admissible under the frozen policy. Derivatives inherit the
qualification, and no high-frequency claim may rest on these 18.

The two flags are **independent** and are carried separately.
`prmtan_neped` and `prmtan_teped` carry both.

---

## Sampled trajectory ≠ interpolant ≠ latent physics

| | |
|---|---|
| **A — observational sampled trajectory** | `x_s(t_{s,k})`, `y_s(t_{s,k})`: the finite task-level samples carried by `O_rec`. This is what the study possesses. |
| **B — numerical realization** | any smoother, interpolant, finite-difference rule or derivative estimator later applied to build a coordinate. A declared analyst choice, not a property of the data. |
| **C — latent physical trajectory** | not observed directly, not assumed exactly recoverable. |

The sampled trajectories are **not** assumed `C¹`, smooth, differentiable, or
solutions of an ODE.

**Consequence for S7.5:** a derivative-valued coordinate is a constructor acting
through a *declared numerical realization* of a sampled trajectory. It is not
evidence that the samples possess an exact classical derivative. For the SIR
phase and trajectory-relational derivatives this distinction is load-bearing.

## Support and masks

Each discharge has one primary analysis support `T_s`, shared by the target, all
78 predictors, and every method later compared on that discharge. Masks, where
needed, are defined from **observational and numerical support only — never from
reconstruction performance**. Gate V7 depends on this.
