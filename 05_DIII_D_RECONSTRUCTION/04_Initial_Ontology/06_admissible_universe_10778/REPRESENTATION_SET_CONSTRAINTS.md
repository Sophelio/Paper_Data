# Representation-set constraints and the factorized `A_rec`

Machine-readable: `A_REC.json`, `representation_set_constraints.json`,
`exact_dependency_groups.csv`, `exact_dependency_groups_attempted.csv`

---

## `A_rec` is finite, and is represented factorially

```
C_rec^atom  =  6 034 admissible atomic coordinates

S_rec  =  { C ⊆ C_rec^atom : 1 ≤ |C| ≤ 12  ∧  Φ_set(C) = 1 }

A_rec  =  { (C, R) : C ∈ S_rec , R ∈ R_rec(C) },   R_rec(C) = T_REC_V1
```

The number of unconstrained subsets of size 1–12 drawn from 6 034 atoms is a
**37-digit** integer. Materializing them is neither possible nor necessary.

> **This is not a failure to instantiate `A_rec`.** The atomic coordinates
> together with the set-level predicates are a *complete and exact* finite
> representation of it. Every member is decidable in constant time: given a
> candidate `C`, check its size, check membership in `C_rec^atom`, and evaluate
> `Φ_set`.

S7.7 will explore only a subset `Ahat_rec`.

## `Φ_set` — the frozen set-level predicates

| # | Constraint | Source |
|---|---|---|
| 1 | `1 ≤ |C| ≤ 12` | frozen `B_rec` bound |
| 2 | no duplicate coordinate IDs in `C` | canonical signatures |
| 3 | every coordinate in `C` belongs to `C_rec^atom` | S7.6 admissibility |
| 4 | no `SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT` coordinate in `C` | S7.5 |
| 5 | `C` contains no **complete** exact linear dependency group | §17 |
| 6 | the target never appears in `C` | `I_rec` |

**Deliberately not imposed:** "must contain a phase derivative", "must contain
multiple families", "must include raw levels", or any other preference. Those
would be **search heuristics, not admissibility**, and belong to S7.7 if
anywhere.

## The exact-dependency constraint `Φ_dependency`

The frozen primitive relation is `pinj = Σ_i pinj_i` over eight beamlines. That
identity propagates through every constructor that is **linear in the aggregate
operand with all other context held fixed**:

| Context | Identity | Groups generated |
|---|---|---|
| level | `ID(pinj) = Σ ID(pinj_i)` | 1 |
| derivative | `DOT(pinj) = Σ DOT(pinj_i)` | 1 |
| product, fixed `z` | `PROD(pinj,z) = Σ PROD(pinj_i,z)` | 67 |
| ratio, aggregate in **numerator** | `RATIO(pinj,z) = Σ RATIO(pinj_i,z)` | 67 |
| phase, aggregate in **numerator** | `PHASE(pinj|z) = Σ PHASE(pinj_i|z)` | 61 |
| | | **197 attempted** |

**No identity is claimed for `RATIO(z,pinj)` or `PHASE(z|pinj)`** — with the
aggregate in the denominator, `z/Σx_i ≠ Σ(z/x_i)`. Recording those would be a
mathematical error, and they are excluded explicitly.

### The rule

```
Φ_dependency(C) = PASS
  iff  C does NOT contain the COMPLETE membership of any frozen exact group
```

A support **may** contain `pinj` together with *some* beam components. It **may
not** contain `pinj` together with **all eight** component restatements in the
same linear context — that would be nine columns spanning eight dimensions.

**No atomic coordinate is deleted** for belonging to a dependency family.
Neither the aggregate nor the component form is privileged a priori; the
constraint acts on *sets*, and a search may legitimately prefer either form.

The principle: **deterministic restatements are not independent scientific
evidence.**

## All 197 groups are VACUOUS on this object

```
attempted 197 · BINDING 0 · VACUOUS 197
```

Every group is incomplete within `C_rec^atom`, because **four of the eight beam
components are numerically inadmissible**:

```
ID(pinj_15r), ID(pinj_21l), ID(pinj_21r), ID(pinj_33l)
    D_CONSTANT_ON_REQUIRED_CALIBRATION_BLOCK
```

`pinj_21l` and `pinj_21r` never fired anywhere in the cohort; the other two are
constant on at least one required calibration interval. Their derivatives,
products and ratios inherit the same fate.

Since no admissible support can ever contain all nine members of any group, the
constraint is **well-defined but has no binding instance on this object**.

That is recorded rather than reported as a bare zero, and both the attempted and
binding sets are frozen. `Φ_dependency` remains an active predicate: if a later
revision restores any of those four components — a different cohort, a relaxed
constant rule — the groups become binding immediately, without a rule change.

## Relation family

For every `C ∈ S_rec`, `R_rec(C) = T_REC_V1`: affine-linear in the constructed
coordinates, intercept permitted and **not counted** toward `|C|`,
discharge-specific coefficients, shared support identity.

**No estimator was run.** OLS versus ridge remains deferred to the frozen search
policy.

## Raw-baseline nesting — corrected wording

**True:** primitive-only coordinate representations are nested within `A_rec`
whenever their support size satisfies 1–12 and the set-level predicates hold.

**Not claimed:** that B2 *itself* is a member of `A_rec`. B2 is the frozen raw
Ridge comparator using the same admissible primitive information — potentially
all 78 primitives — and a 78-primitive model is not an `m ≤ 12` member.

The fairness claim is **SAME INFORMATION BOUNDARY**, not an identical
support-size constraint. **B2 was not modified and was not restricted to 12.**
