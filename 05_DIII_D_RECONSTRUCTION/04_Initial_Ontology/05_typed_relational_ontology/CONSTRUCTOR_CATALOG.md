# `Lambda_rec` — the primary constructor catalogue

Machine-readable: `constructor_catalog.json` ·
Exclusions: `excluded_constructor_families.json` ·
Signatures: `coordinate_signature_schema.json`

**Maximum constructor depth = 1.** Every constructor operates directly on
primitives. **No constructor may consume another depth-1 constructed
coordinate.**

Not primary, by that rule alone: `d(x_i x_j)/dt` · `x_i·(dx_j/dt)` ·
`(x_i/x_j)·x_k` · `D_{x_k}(x_i x_j)` · a ratio of two ratios · a product of
phase derivatives.

---

## C0 — primitive level `ID(x_i)`

Depth 0, arity 1. Output inherits signal identity, scientific type, unit or
uncalibrated status, provenance, family, source-resolution metadata, aliasing
and upsample flags — **unchanged**.

**All 78 primitives are admissible**, including the two `UNCALIBRATED_SIGNAL`
levels.

> **The raw-coordinate comparator is nested inside the SIR ontology.** A
> representation whose coordinates are all C0 levels is an admissible special
> case of `G_rec`. Baseline B2 is therefore a *member* of the search space, not
> an external alternative — which is what makes the B2 comparison a statement
> about representation rather than about two different frameworks.

## C1 — first temporal derivative `dx_i/dt`

Depth 1, arity 1. Signature `DOT(signal)`. Type rule `[x_i] → [x_i]/s`.

Derivative parameter is **physical time `t` in seconds**; `d/dtau` is
**forbidden**. Numerical realization `FD2_PHYSICAL_TIME_V1`.

**70 of 78 operands eligible.** Excluded: the 2 uncalibrated primitives
(dimensionally uncertified) and the 6 `NUMERICAL_SENSITIVITY_ONLY` signals
(`prmtan_neped`, `prmtan_teped`, `fs03da`, `fs04`, `fs04da`, `fs05da`), whose
derivatives are representable in `G_rec` as
`SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT` for S7.11 but are not in the primary
grammar.

No second derivatives. No derivative of the target.

## C2 — pairwise product `x_i x_j`

Depth 1, arity 2. Signature `PROD(i,j)` with **`i ≤ j`** by frozen inventory
index. Type rule `[x_i x_j] = [x_i][x_j]`.

- **Commutative** — the canonical ordering is what prevents S7.6 from
  instantiating `PROD(i,j)` and `PROD(j,i)` as two coordinates.
- **Self-products allowed**: `x_i²` is the canonical `i = j` case.
- **Operands need not share dimensions.** The output carries the compound
  dimension explicitly, so a product of a temperature and a power is
  well-typed — it is simply an eV·W coordinate.

**76 eligible operands** (uncalibrated excluded). No triple products, no target
operand.

## C3 — pairwise ratio `x_i / x_j`

Depth 1, arity 2, **`i ≠ j`**. Signature `RATIO(i,j)`. Type rule
`[x_i]/[x_j]`.

- **Directional**: `RATIO(i,j) ≠ RATIO(j,i)`.
- **Partial map** with mathematical domain `x_j ≠ 0`, carried as the domain
  predicate `DOMAIN_DENOMINATOR_NONZERO`.
- `x_i/x_i` excluded — the trivial constant 1.

**Prohibited in the primary coordinate definition:** denominator shifts,
additive epsilons, clipping, bounded reciprocal transforms.

Those are **different coordinate constructions** and were not frozen as primary
constructors. Numerical support and conditioning of instantiated ratios are
handled at S7.6 and S7.11 **without changing the symbolic coordinate** — a
conditioning problem is a reason to reject an instance, never a reason to
silently redefine the constructor.

**76 eligible operands.** No target operand.

## C4 — trajectory-relational derivative `D_g^t f = (df/dt)/(dg/dt)`

Depth 1, arity 2, `f ≠ g`. Signature `PHASE(i|j)` meaning `D_{x_j} x_i`.

Manuscript terminology: *trajectory-relational derivative*; abbreviated **phase
derivative** throughout the work.

**Type rule `[D_g f] = [f]/[g]` — the time dimensions cancel.** A phase
derivative of two temperatures is dimensionless; of a temperature by a current,
eV/A.

- **Directional**: `PHASE(i|j) ≠ PHASE(j|i)`.
- **Partial map** with domain `dg/dt ≠ 0`, predicate
  `DOMAIN_DENOMINATOR_RATE_NONZERO`.
- `D_f f` excluded — trivial constant 1 wherever defined.
- Both operands must be eligible for **primary** temporal differentiation, so
  **70 eligible operands**: neither may be uncalibrated, neither may be one of
  the six sensitivity-only signals. `ALIASING_RISK` propagates if either
  derivative carries it.

### What it does not imply

`D_g f` does **not** assert `f = F(g)`, causality, oscillatory phase, or any
global functional dependency. It is a ratio of two rates evaluated on the same
sampled trajectory.

### Prohibited variants in the primary ontology

Reference-shifted, bounded, and sensitivity-centered phase derivatives are
**related but distinct constructions**. They are excluded here and would require
separate explicit qualification if ever studied.

---

## Sum and difference are deliberately absent

`x_i + x_j` and `x_i − x_j` are **not** primary constructors.

The primary relation template is affine-linear in the selected coordinates, so
both are already representable by including `x_i` and `x_j` with appropriate
coefficients. Adding them as coordinates would enlarge the candidate set
**without enlarging the span of the relation family** — pure algebraic
redundancy.

This is an ontology-level redundancy argument, **not a performance result**.
Dimensional compatibility rules for sums remain part of the general type system;
they simply have no primary constructor to govern.

---

## Symbolic upper bounds — audit only

**No coordinate instance is enumerated here.** These are combinatorial counts
computed from the eligibility rules, for audit and for S7.6 to check against.

| Family | Rule | Count |
|---|---|---|
| C0 primitive level | 78 | **78** |
| C1 derivative (primary) | 70 | **70** |
| C1 derivative (sensitivity-only) | 6 | 6 |
| C2 product, symmetric with self | `C(76,2) + 76` | **2 926** |
| C3 ratio, directional | `76 × 75` | **5 700** |
| C4 phase derivative, directional | `70 × 69` | **4 830** |
| **primary total** | | **13 604** |

Instantiation belongs to **S7.6**.
