# The support universe, defined by predicates

Machine-readable: `A_REC_HARDENED.json`, `representation_set_constraints.json`,
`exact_dependency_groups.csv`, `exact_dependency_groups_attempted.csv`,
`manifests/DEPENDENCY_DERIVATION.json`

---

## Definition

```
C_rec_hard^atom            10 778 admissible atomic coordinates

S_rec^H  =  { C ⊆ C_rec_hard^atom  :  1 ≤ |C| ≤ 12  ∧  Φ_set(C) = PASS }

A_rec^H  =  { (C, T_REC_V1)  :  C ∈ S_rec^H }
```

`T_REC_V1` is unchanged: affine-linear in the constructed coordinates, intercept
allowed and not counted toward `|C|`, shared support identity across discharges,
discharge-specific coefficients.

## `Φ_set` — the six predicates

| id | rule |
|---|---|
| `size` | `1 ≤ |C| ≤ 12` — the frozen `B_rec` bound, unchanged |
| `no_duplicates` | no duplicate coordinate IDs in `C` |
| `atoms_only` | every coordinate in `C` belongs to `C_rec_hard^atom` |
| `no_sensitivity_only` | no `SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT` coordinate in `C` |
| `phi_dependency` | `C` must not contain the **complete** membership of any frozen exact linear dependency group |
| `no_target` | the target never appears in `C` |

Explicitly **not** imposed: must contain a phase derivative · must span multiple
families · must include raw levels · must include a partial map · any heuristic,
weight, ranking, or preference. Those belong to S7.7, if anywhere.

## Not materialised

The number of unconstrained subsets of 10 778 atoms at sizes 1–12 is
astronomically large; it is recorded in `A_REC_HARDENED.json` only to show why
enumeration was never attempted. **The atomic set plus the predicates is an
exact finite representation of `A_rec^H`.** Nothing is approximated by
factorising.

---

## `Φ_dependency` in detail

`pinj = Σ_b pinj_b` over eight beamlines, evidence class `LOCAL_DOCUMENTED`.
Re-derived over C0–C8 — **not** copied from the superseded universe.

### Where the identity restates exactly (400 groups)

| context | groups | why it is linear |
|---|---|---|
| `ID(pinj)` | 1 | the aggregate enters linearly |
| `DOT(pinj)` | 1 | `d/dt` is linear and FD2 is a fixed linear stencil on the shared grid |
| `PROD(pinj,z)` | 59 | `x_z·Σ_b x_b = Σ_b x_z·x_b` |
| `RATIO(pinj,z)` | 59 | aggregate in the **numerator** only |
| `PHASE(pinj\|z)` | 54 | aggregate **rate** in the numerator only |
| `LEVEL_RATE(pinj\|z)` | 54 | linear in the level operand |
| `LEVEL_RATE(z\|pinj)` | 59 | through derivative linearity |
| `RATE_OVER_LEVEL(pinj\|z)` | 59 | aggregate rate in the numerator only |
| `LEVEL_OVER_RATE(pinj\|z)` | 54 | aggregate level in the numerator only |

Each group has 9 members: the aggregate coordinate plus its 8 per-beam
restatements in one fixed context.

### Where no identity was inferred

| form | why not |
|---|---|
| `RECIP(pinj)` | `1/Σ_b x_b ≠ Σ_b 1/x_b` — the reciprocal is not linear |
| `RATIO(z,pinj)` | aggregate is the **denominator** level |
| `PHASE(z\|pinj)` | aggregate rate is the **denominator** |
| `RATE_OVER_LEVEL(z\|pinj)` | aggregate level is the **denominator** |
| `LEVEL_OVER_RATE(z\|pinj)` | aggregate rate is the **denominator** |
| `PROD(pinj,pinj)` | quadratic: `(Σ_b x_b)² ≠ Σ_b x_b²` |

## All 400 groups are vacuous — and the predicate stays

```
attempted 400    BINDING 0    VACUOUS 400
```

Four of the eight per-beam component coordinates — `pinj_15r`, `pinj_21l`,
`pinj_21r`, `pinj_33l` — are themselves **class-D inadmissible**, because those
beamlines were inactive throughout at least one required development calibration
block and their level is therefore identically constant there. Every group in
every context inherits at least one inadmissible member, so **no admissible
support can contain a complete exact set**. Groups in C4 and C8 are vacuous a
fortiori: those families have no admissible members at all.

`Φ_dependency` is therefore correct, well defined, and currently excludes
nothing. It is retained rather than dropped:

- it costs nothing to evaluate;
- a different cohort, calibration geometry, or block boundary would make it bind;
- silently dropping a constraint because it happens not to bite is exactly the
  kind of quiet narrowing this audit chain exists to prevent.

Both tables are written out — `exact_dependency_groups_attempted.csv` (400 rows,
with `status` and `vacuous_reason`) and `exact_dependency_groups.csv` (the
binding subset, empty) — so the distinction is auditable rather than implicit.

## Neither representation is privileged

`pinj` and all eight components remain in `P_hard` and in the atomic universe
wherever they are individually admissible. The constraint is **set-level**: a
support may contain the aggregate and *some* components; it may not contain the
aggregate and *all eight* restatements in the same linear context. Nothing here
prefers the aggregate form over the component form, or the reverse.
