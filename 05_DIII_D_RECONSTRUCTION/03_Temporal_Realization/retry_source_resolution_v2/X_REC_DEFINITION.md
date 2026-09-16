# `X_rec` — formal definition

Machine-readable: `X_REC.json` · Blocks: `typed_signal_blocks.csv` ·
Realizations: `trajectory_index.csv` · Constraints:
`interpretation_constraints.json`

`X_rec = Obj_rec(O_rec)` — the mathematical interpretation of the corrected
task-admissible record. It is **not** `G_rec`, not a feature matrix, not an
ontology, not a design matrix, not a model, not an ODE, and not a state-space
assumption. Utility and validation stay in `K_rec`.

---

## Definition

For each discharge `s ∈ S_rec`, let

```
T_s = { t_{s,0}, ... , t_{s,N_s-1} } ⊂ ℝ,   t in seconds
```

be that discharge's corrected physical-time analysis support. Let

```
x_s : T_s -> X_pred        the typed 78-component target-independent trajectory
y_s : T_s -> Y_rec         the line-averaged electron-density trajectory
a_s                        frozen realization metadata
```

Then

```
X_rec = { (T_s, x_s, y_s, a_s) : s ∈ S_rec },   |S_rec| = 62
```

is a **finite discharge-indexed ensemble of typed sampled trajectories**.

`a_s` carries discharge identifier, processing era, operational period and
development/external access class. **`a_s` is realization metadata, never an
explanatory coordinate.**

### Crucially, `T_s ≠ T_r` for `s ≠ r`

The grids are discharge-specific: `Δt_s ∈ [5.853, 14.187] ms`, 53 distinct
values across 62 discharges, `N_s ∈ [325, 833]`. What is shared across the
ensemble is the **typed coordinate support**, not the timestamps.

## Target space

```
Y_rec = electron number density,  canonical unit m^-3
y_s(t) = density_s(t)
```

Archived in cm⁻³; canonicalized by ×10⁶. Origin class
`DIAGNOSTIC_RECONSTRUCTION` — a line integral divided by a chord length, not a
local measurement, and its provenance class is not upgraded beyond that.

Never upstream-upsampled, in any of the 62 discharges. No `dy/dt` is
constructed. No target history enters `X_pred`.

## Predictor space

```
X_pred = X_ECE × X_CER_v × X_CER_Ti × X_NBI × X_mag × X_fs × X_gas × X_density_aux
```

**78 components · 7 broad scientific families · 8 mathematical type blocks.**

| Block | Family | Dim | Canonical unit | Dimensionally homogeneous |
|---|---|---|---|---|
| `X_ECE` | ECE | 40 | eV | **yes** |
| `X_CER_v` | CER | 7 | m/s | **yes** |
| `X_CER_Ti` | CER | 7 | eV | **yes** |
| `X_NBI` | neutral beams | 10 | W, N·m | no |
| `X_mag` | magnetics | 4 | T, A, 2× uncalibrated | no |
| `X_fs` | filterscope | 4 | ph/(sr m² s) | **yes** |
| `X_gas` | gas injection | 4 | V | **yes** |
| `X_density_aux` | density | 2 | m⁻³, eV | no |

**Seven families, eight blocks** — the CER family splits because toroidal
rotation is a velocity and ion temperature is a temperature. They share a
diagnostic system, not a dimension.

Four blocks are **not** dimensionally homogeneous, and this is recorded rather
than papered over: `X_NBI` mixes power with torque, `X_mag` mixes field, current
and two uncalibrated channels, `X_density_aux` mixes density with temperature.
S7.5's dimensional rules must operate on **components**, not blocks — a sum
within a block is not automatically admissible.

Canonicalization applied: 40 ECE keV→eV, 7 CER km/s→m/s, 4 filterscopes
cm⁻²→m⁻², `pinj` kW→W. `pcbcoil` and `pcdiamag3` keep no unit and remain
`UNCALIBRATED_SIGNAL`.

### The 78 are not a physical state vector

They mix diagnostics, diagnostic reconstructions, electromagnetic measurements,
actuator commands and two uncalibrated channels. The correct description is a
**typed heterogeneous observational trajectory**. Channel indices are labels;
no geometry is documented in the frozen object, so a channel index is **not**
asserted to be a spatial coordinate.

## Numerical realization

```
X_s^num ∈ ℝ^{N_s × 78}        y_s^num ∈ ℝ^{N_s}
```

**`X_s^num` is an implementation representation, not the definition of
`X_rec`.** ℝ⁷⁸ does not carry the scientific semantics of `X_pred` — the units,
types, families, provenance classes and resolution qualifications live in the
typed object, not in the array.

`X_rec` is defined in **canonical scientific units**, never in z-scored
coordinates. Any later standardization is a fitted transform subject to the
calibration-only leakage firewall.

## Joint observation (optional)

```
z_s(t) = (x_s(t), y_s(t))          Z_rec = { (T_s, z_s, a_s) }
```

Permitted for describing the joint task observation. **`Z_rec` may not be used
for explanatory coordinate construction** — the notation must not re-admit
density into its own predictors.

## Contemporaneous reconstruction

`x_s(t_k)` corresponds to `y_s(t_k)` at the same index. The eventual relation
has schematic form only:

```
y_s(t) ≈ R_s( C(x_s)(t) )
```

Neither `C` nor `R` is instantiated. There is no prediction horizon. This is
**contemporaneous reconstruction**, not forecasting.

## Ensemble structure

62 realizations — 20 development, 42 external (sealed, values unopened).
Discharges are **not** iid time rows and **may not be concatenated**. The
interpretation supports the frozen structural-transfer contract: shared
scientific coordinate support, discharge-specific fitted coefficients.

## Assumptions explicitly not made

differentiability · `C¹` smoothness · ODE-solution structure · Markov property ·
complete physical state · latent-state recovery · dynamical closure · causal
ordering · channel index as spatial coordinate · cross-discharge concatenation ·
iid pooling of discharges.
