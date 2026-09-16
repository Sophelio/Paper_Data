# Type system and propagation

Machine-readable: `constructor_type_rules.json`, `primitive_type_registry.csv`
(78 rows), `dependency_constraints.json`

---

## Dimensional typing is at COMPONENT level, never block level

Broad type blocks are **organizational**. Three of the eight are dimensionally
heterogeneous — `X_NBI` (W, N·m), `X_mag` (T, A, 2× uncalibrated),
`X_density_aux` (m⁻³, eV) — so block membership carries no dimensional
guarantee, and no dimensional rule may be applied at block level.

### The 78 primitives by scientific dimension class

| Dimension class | Canonical unit | n |
|---|---|---|
| temperature / energy | eV | **48** |
| velocity | m s⁻¹ | 7 |
| power | W | 9 |
| electric potential | V | 4 |
| photon flux | ph sr⁻¹ m⁻² s⁻¹ | 4 |
| uncalibrated raw signal | — | 2 |
| torque | N m | 1 |
| magnetic flux density | T | 1 |
| electric current | A | 1 |
| number density | m⁻³ | 1 |
| | | **78** |

The 48 eV components span three different blocks (`X_ECE` 40, `X_CER_Ti` 7,
`X_density_aux` 1) — another reason typing must follow the component, not the
block.

## Constructor output dimensions

| Constructor | Output |
|---|---|
| C0 primitive | `[x_i]` |
| C1 derivative | `[x_i] / time` |
| C2 product | `[x_i] · [x_j]` |
| C3 ratio | `[x_i] / [x_j]` |
| C4 phase derivative | `[x_i] / [x_j]` |

> **Numerical standardization does not alter the scientific type.** A coordinate
> is never declared dimensionless merely because its values are z-scored later.
> Standardization is a fitted transform under the leakage firewall; the type is
> a property of the coordinate.

## Uncalibrated-signal policy

`pcbcoil` and `pcdiamag3` are documented upstream as `raw`.

| | |
|---|---|
| primitive level | `PRIMARY_ADMISSIBLE` |
| any derived coordinate (C1–C4) | `DIMENSIONALLY_UNCERTIFIED_PRIMARY_EXCLUDED` |

Their physical dimensions are unresolved, so the dimensional type of any
construction containing them cannot be scientifically certified.

**This is a fail-closed dimensional-admissibility decision, not a claim that the
signals carry no information.** They remain fully available as levels, where no
dimensional argument is required of them.

## Temporal-resolution propagation

| Constructor | Rule |
|---|---|
| C0 | inherit the primitive's temporal metadata unchanged |
| C1 | inherit the source's qualification **plus** `DERIVED_FROM_NUMERICAL_REALIZATION` |
| C2, C3 | limited by the **coarser** provenance-supported resolution of the two operands, within each discharge |
| C4 | limited by the **coarser** derivative-source resolution of numerator and denominator |

**Invariant:** no constructed coordinate may claim temporal information finer
than either operand. Construction cannot manufacture resolution any more than
interpolation can.

## Flag propagation

| Flag | Rule |
|---|---|
| `ALIASING_RISK` (18 primitives) | propagates from any operand to the output. Levels remain primary admissible; **no high-frequency physical claim may be made** on any coordinate carrying it. |
| `UPSTREAM_UPSAMPLED` (6 primitives) | level remains primary admissible; the **first derivative is `NUMERICAL_SENSITIVITY_ONLY`** and leaves the primary grammar. |
| `UNCALIBRATED_SIGNAL` (2 primitives) | level primary admissible; **all** derived constructors excluded. |

**Precedence:** where both `ALIASING_RISK` and `UPSTREAM_UPSAMPLED` occur —
`prmtan_neped` and `prmtan_teped` carry both — `NUMERICAL_SENSITIVITY_ONLY`
dominates primary eligibility.

A coarser analysis grid does **not** erase upstream aliasing; it is already
embedded in the archived values.

## Numerical realization of derivatives — `FD2_PHYSICAL_TIME_V1`

```
second-order finite difference with respect to actual physical time t [s]
reference implementation: numpy.gradient(x, t, edge_order=2)
```

| Property | |
|---|---|
| derivative parameter | physical `t` in seconds |
| `d/dtau` | **forbidden** |
| uses actual `T_s` values | **yes** — never an assumed global `dt` |
| fitted smoothing parameter | none |
| target values involved | none |
| whole-ensemble fit | none |
| cross-discharge stencil | none |
| spline / RTS in primary | none — those belong to S7.11 sensitivity |

**Capability check (synthetic data only, no observational value touched):**
verified at the three representative discharge cadences 5.853, 6.824 and
14.187 ms; halving `dt` over a fixed window reduced the maximum interior error
by a factor of **4.00** at both refinements, confirming second-order accuracy.
Each `T_s` is uniform within its own discharge — only `dt` differs *between*
discharges — which is exactly the case tested.

> A derivative-valued coordinate is a **constructor acting through a declared
> numerical realization** of a sampled trajectory. It is not evidence that the
> samples possess an exact classical derivative.

## Provenance propagation

Every constructed coordinate carries a lineage graph recording: constructor,
ordered operands, primitive ancestors, input provenance classes, input units and
types, temporal qualifications, transformation depth, target-independence
status.

`primitive_ancestors(c)` is exactly recoverable for every coordinate.

**Target independence is transitive.** If any primitive ancestor is
target-forbidden, the coordinate is forbidden. Because `G_rec` is generated from
the already target-independent 78-primitive boundary this holds automatically —
the invariant is encoded regardless, so a future boundary change cannot silently
violate it.

## Exact predictor dependency

```
DEP_NBI_POWER_SUM :  pinj = sum(pinj_*)     EXACT_DETERMINISTIC_SUM
```

Evidence `LOCAL_DOCUMENTED` — the units-registry description plus the S7.1R
additivity check in canonical units. **Not** target leakage for `density`.

**Neither the aggregate nor the components are removed at S7.5.** The constraint
is encoded as a dependency group instead.

**Scope is representation-level, not coordinate-level.** At depth 1 with arity
≤ 2, no single coordinate can carry the whole exact set, so the redundancy can
only appear in a coordinate *set*. A candidate representation containing the
aggregate level **and** all eight component levels is marked
`EXACT_LINEAR_REDUNDANCY_RISK`.

The operational exclusion rule for coordinate sets belongs to **S7.6**. The
principle it must implement: **deterministic restatements are not independent
scientific evidence**.
