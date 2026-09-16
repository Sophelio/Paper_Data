# Final primary information boundary for `y* = vsurf`

Machine-readable: `I_REC_SELECTED.json`, `O_REC_SELECTED.json`,
`selected_target_boundary.csv` (all 95 rows), `selected_target_exclusions.csv`

```
O_rec = I_rec(vsurf)(O)
```

## Exclusion census

| Category | n |
|---|---|
| initial quantities in O | **95** |
| target itself | 1 |
| duplicate / alias | 0 |
| definitional descendant | 0 |
| verified target ancestry | 0 |
| **unresolved target ancestry (fail-closed)** | **15** |
| sibling exclusion | 0 |
| other frozen `P_rec` reason | 0 |
| **surviving primary predictors** | **79** |

```
95 observed quantities  ->  16 removed  ->  79 admissible primitive explanatory quantities
```

Every removal is auditable in `selected_target_exclusions.csv` with its rule,
reason, provenance evidence and evidence class.

## What was removed, and why

**`vsurf` itself** (rule R1). The target may not predict itself, at any lag —
the frozen target-history exclusion.

**The 15 equilibrium quantities** (rule R5, fail-closed): `aminor`, `area`,
`betan`, `drsep`, `kappa`, `li`, `q95`, `rmaxis`, `rsurf`, `tribot`, `tritop`,
`volume`, `zcur`, `zmaxis`, `zsurf`.

All are `LINEAGE_PARTIAL`: the EFIT family is identified but its settings,
inputs and constraints are not present in any local artifact, so independence
from `vsurf` cannot be **certified** in either direction. Under the frozen
fail-closed rule, unresolved ancestry is not independence.

This is the full accepted cost of decisions D-03, H-A and H-B. There is **no
EFIT recovery campaign and no `PROVENANCE_RELAXED` variant**. The 15 are out and
stay out.

**No aliases, no definitional descendants.** S7.1 established one-to-one signal
identity throughout the object, and the only documented deterministic algebraic
relation — `pinj = Σ pinj_*` — does not involve `vsurf`.

**No siblings.** `vsurf` is not a member of any same-quantity channel series.
The magnetics group holds five *distinct* quantities, not a channel series, so
the sibling rule does not apply and the sibling-sensitivity boundary is
**`NOT_APPLICABLE`**.

## The 79 surviving primitives, by scientific family

| Family | n | Signals |
|---|---|---|
| **ECE electron temperature** | 40 | `ece1` … `ece40` |
| **CER rotation / ion temperature** | 14 | `cerqrott{3,6,8,10,11,12,13}`, `cerqtit{3,6,8,10,11,12,13}` |
| **Neutral beams** | 10 | `pinj`, `pinj_{15l,15r,21l,21r,30l,30r,33l,33r}`, `tinj` |
| **Magnetics** | 4 | `bt`, `ip`, `pcbcoil`, `pcdiamag3` |
| **Filterscope D-alpha** | 4 | `fs03da`, `fs04`, `fs04da`, `fs05da` |
| **Gas injection** | 4 | `gasa`, `gasb`, `gasc`, `gasd` |
| **Density** | 3 | `density`, `prmtan_neped`, `prmtan_teped` |
| | **79** | across **7** families |

### Target eligibility ≠ predictor admissibility

Two groups excluded as *targets* survive as *predictors*, correctly:

- **`pcbcoil` and `pcdiamag3`** were target-ineligible because they are
  uncalibrated raw digitiser output with no physical unit. They remain
  admissible predictors carrying a permanent `UNCALIBRATED_SIGNAL` type. An
  uncalibrated channel can still carry information; it simply cannot carry a
  dimensional argument.
- **The 14 actuation quantities** (gas valve commands, beam power and torque)
  were target-ineligible because reconstructing an actuator command describes
  the control system rather than the plasma. As predictors they are admissible
  and, physically, they are exactly the kind of quantity a loop-voltage relation
  might involve.

Only the 15 equilibrium quantities were removed on *provenance* grounds.

## Carried flags on surviving predictors

**18 of the 79 carry `ALIASING_RISK`** (U010): all 14 CER channels plus `bt`,
`ip`, `prmtan_neped`, `prmtan_teped`. They remain admissible **as levels**; their
derivatives inherit the flag, and no high-frequency claim may rest on them.

Four also carry U009 (era-varying upstream resampling method): `bt`, `ip`,
`prmtan_neped`, `prmtan_teped`.

These are recorded per row in `selected_target_boundary.csv` for S7.5 and are
not exclusions.

## Primary analysis cadence

```
primary_grid_dt = 20.0 ms
```

Set by the frozen no-super-resolution rule: **no finer than the coarsest native
cadence among admitted quantities, target included.** `vsurf` is itself 20 ms
native, and the CER and pedestal channels are 10 ms, so 20 ms binds.

The cost is explicit: the 0.02 ms filterscopes and 0.2 ms ECE channels are
block-averaged down to 20 ms. That discards fine temporal detail — and it is
preferable to manufacturing evidence by interpolating the 20 ms target onto a
finer grid.

Validation geometry was audited feasible at 20 ms in S7.2 (186/186), and the
selected target confirms it: 60/60 development blocks valid, calibration
75–140+ samples, evaluation 19–23 samples.

## What this is not

`O_rec` contains **primitives only**. No product, ratio, derivative, phase
derivative, symbolic term or coordinate of any kind has been constructed. S7.4
determines what mathematical object these primitives are interpreted as; S7.5
generates the typed ontology `G_rec`.
