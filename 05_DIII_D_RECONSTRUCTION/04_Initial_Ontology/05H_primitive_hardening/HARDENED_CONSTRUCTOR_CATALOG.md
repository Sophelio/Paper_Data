# `Lambda_rec^H` — the hardened constructor catalogue

Machine-readable: `constructor_catalog_hardened.json`,
`constructor_type_rules_hardened.json`,
`coordinate_signature_schema_hardened.json`,
`excluded_constructor_families_hardened.json`

**Nine families, maximum depth 1.** The catalogue was frozen in
`HARDENING_POLICY_PREVALUE.json` **before any development value was read**, so
no family was added or removed in knowledge of the resulting primitive count.

```
M = |P_hard| = 70     Mt = typed (non-uncalibrated) = 68     Md = derivative-eligible = 63
```

---

## The five inherited families

| | Family | Signature | Output dimension | Count |
|---|---|---|---|---|
| **C0** | primitive level | `ID(i)` | `[x_i]` | 70 |
| **C1** | first temporal derivative | `DOT(i)` | `[x_i]/s` | 63 |
| **C2** | level–level product | `PROD(i,j)`, `i ≤ j` | `[x_i][x_j]` | 2 346 |
| **C3** | level–level ratio | `RATIO(i,j)` | `[x_i]/[x_j]` | 4 556 |
| **C4** | trajectory-relational (phase) derivative | `PHASE(i\|j)` | `[x_i]/[x_j]` | 3 906 |

## The four new families

| | Family | Signature | Output dimension | Count |
|---|---|---|---|---|
| **C5** | unary reciprocal `1/x_i` | `RECIP(i)` | `[x_i]⁻¹` | 68 |
| **C6** | level–rate interaction `x_i·ẋ_j` | `LEVEL_RATE(i\|j)` | `[x_i][x_j]/s` | 4 284 |
| **C7** | rate over level `ẋ_i/x_j` | `RATE_OVER_LEVEL(i\|j)` | `[x_i]/([x_j]·s)` | 4 284 |
| **C8** | level over rate `x_i/ẋ_j` | `LEVEL_OVER_RATE(i\|j)` | `s·[x_i]/[x_j]` | 4 284 |

### Scientific semantics

**C5** — inverse observational scale.

**C6** — the level of one observed quantity weighted by the instantaneous rate
of another.

**C7** — the rate of one quantity relative to the level scale of another. The
self case `ẋ_i/x_i` is a **fractional temporal rate**, equivalently a
logarithmic rate where defined; unit `s⁻¹`.

**C8** — an observed level relative to another quantity's rate. The self case
`x_i/ẋ_i` is a **local characteristic-timescale** coordinate; unit `s`.

Together C6–C8 fill the **level–rate** portion of the grammar, which the
original five families left empty: C0–C3 relate levels to levels, C4 relates
rates to rates, and nothing related a level to a rate.

### C6–C8 are depth 1, not depth 2

They are **primitive-pair constructors with an internal declared rate
operator**. They do **not** consume `C1` coordinate objects recursively. A
coordinate `LEVEL_RATE(i|j)` has primitive ancestors `{x_i, x_j}` and depth 1,
not `{x_i, DOT(x_j)}` at depth 2.

This distinction is recorded explicitly because the notation invites the wrong
reading, and because depth 1 is a frozen bound.

### C6 is role-directional but has no denominator

Multiplication is numerically commutative, but `LEVEL_RATE(i|j)` is **not
collapsed** with `LEVEL_RATE(j|i)`: the semantic roles differ, and
`x_i·ẋ_j ≠ x_j·ẋ_i` in general. Both are distinct coordinates.

C6 alone among the new families has **no partial-map singularity predicate** —
no denominator, no domain gate. It remains subject at S7.6 to numerical support,
finite dynamic range, conditioning and the derivative qualifications, but not to
a denominator test.

## Operand eligibility

| Family | Operands |
|---|---|
| C0 | any primitive in `P_hard` (70) |
| C1 | `P_dot` (63) |
| C2 | `P_typed × P_typed`, symmetric, self allowed (68) |
| C3 | `P_typed × P_typed`, `i ≠ j` (68) |
| C4 | `P_dot × P_dot`, `i ≠ j` (63) |
| C5 | `P_typed` (68) |
| C6 | level `P_typed` × rate `P_dot`, `i` may equal `j` |
| C7 | rate `P_dot` × level `P_typed`, `i` may equal `j` |
| C8 | level `P_typed` × rate `P_dot`, `i` may equal `j` |

The target is never an operand.

**Preserved unchanged from S7.5:** the 2 uncalibrated primitives are C0-only;
an upstream-upsampled signal may serve as a **level** operand anywhere —
including as the level operand of C6, the level denominator of C7 and the level
numerator of C8 — but any constructor requiring *its* derivative is
`NUMERICAL_SENSITIVITY_ONLY`; `ALIASING_RISK` propagates from any operand.

Of the 5 upstream-upsampled primitives retained in `P_hard`
(`prmtan_neped`, `prmtan_teped`, `fs03da`, `fs04`, `fs05da`), all remain
available as level operands and none is derivative-eligible — which is why
`Md = 63 = 70 − 2 − 5`.

## Partial-map predicates — symbolic only

```
C3: x_j != 0        C4: dx_j/dt != 0      C5: x_i != 0
C7: x_j != 0        C8: dx_j/dt != 0      C6: none
```

**No numerical domain evaluation happens here** — that is S7.6. No epsilon,
shift, clipping, bounded reciprocal or denominator repair; those are distinct
coordinate definitions.

## Derivative realization — unchanged

`FD2_PHYSICAL_TIME_V1`: second-order finite difference,
`numpy.gradient(x, t, edge_order=2)`, physical time `t` in seconds, per-discharge
`T_s`, no smoothing parameter, never `d/dτ`, no cross-discharge stencil.

## What remains excluded

All S7.5 exclusions stand: transcendental functions, arbitrary powers, cubic and
triple products, second derivatives, lags, leads, integrals, cumulative
histories, PCA and learned embeddings, spatial and channel-index derivatives,
and shifted / bounded / sensitivity-centered phase derivatives.

**No previously excluded family was re-admitted.** This is ontology broadening
along one declared axis, not an opening to unrestricted symbolic regression.

**Group summary constructors** (channel mean, median, variance, gradients) are
recorded as `PRIMARY_ONTOLOGY_EXCLUDES_PENDING_SEMANTIC_GEOMETRY`: S7.4
established that channel index is not documented as a physical spatial
coordinate, so cross-channel summaries are scientifically ambiguous on this
object. `GENERAL_FRAMEWORK_PERMITS` them; they are not generated.

## Combinatorial consequence

```
hardened total  23 861      original (G_REC_DENSITY_V1)  13 604      = 1.75x LARGER
```

The four new families contribute **12 920** coordinates, of which C6/C7/C8 alone
contribute **12 852**. Narrowing the primitive basis by 10% did not come close
to offsetting broadening the grammar from five families to nine.

The hardened ontology is therefore **substantially larger**, not smaller. That
is a direct consequence of the two changes pulling in opposite directions, and
it is reported rather than adjusted.
