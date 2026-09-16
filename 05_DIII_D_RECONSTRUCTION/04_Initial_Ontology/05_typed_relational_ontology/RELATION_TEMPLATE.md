# `T_rec` — the relation template

Machine-readable: `relation_templates.json`

---

## Primary template

```
y_s(t)  =  beta_{0,s}  +  sum_{j=1..m} beta_{j,s} · c_j(x_s)(t)  +  epsilon_s(t)

1 <= m <= 12
C = { c_1, ..., c_m }   the shared scientific coordinate support
beta_s                  discharge-specific coefficients
```

**Affine-linear in the constructed coordinates.** The coordinate functions
themselves may be nonlinear relational constructions — products, ratios,
derivatives, phase derivatives. Nonlinearity lives in the coordinates, not in
the relation, which is what keeps the discovered structure readable.

| Property | |
|---|---|
| support `C` | **shared across all discharges** |
| coefficients `beta_s` | **discharge-specific** (structural transfer with local calibration) |
| intercept `beta_{0,s}` | permitted; **does not count toward `m`** |
| support size `m` | 1 – 12, from the frozen `B_rec` bound |
| target on explanatory side | never |
| target derivative | never |
| relation form | **explicit**, not implicit |
| universal-coefficient claim | none |

The shared object is the **support**; the coefficients are local. That is the
whole content of the structural-transfer contract, and this template is its
algebraic form.

## Coefficient dimensionality

```
[beta_j]  =  [y] / [c_j]  =  m^-3 / [c_j]
```

Every affine term `beta_j · c_j` therefore carries the **target dimension
m⁻³**, whatever the coordinate's own dimension is.

**Consequence:** coordinates within one relation need **not** share physical
units. A relation may combine an eV coordinate, a dimensionless phase
derivative and a W·s⁻¹ derivative — the fitted coefficients carry the
compensating dimensions. This is why the ontology admits products of unlike
quantities without a dimensional conflict.

### Uncalibrated operands

For an `UNCALIBRATED_SIGNAL` primitive the numerical coefficient is allowed, but
**no physical dimensional interpretation of that coefficient may be claimed**.

```
coefficient_dimension_status  ∈  { PHYSICALLY_TYPED , UNCALIBRATED }
```

Recorded per coefficient, so a later reader can tell which coefficients admit a
physical reading and which do not.

## The estimator is not the relation template

S7.5 freezes the **relation family**: affine-linear in constructed coordinates.

It does **not** choose the **numerical estimator**. OLS versus ridge, any
penalty, and any hyperparameter belong to the later frozen search policy, and
the frozen contract already requires those to be selected on development data
and frozen before external evaluation.

**No estimator was run in S7.5.** No coefficient was fitted, no residual
computed, no performance inspected.

## What the template rules out

- implicit relations `F(y, x) = 0`
- any relation with `y` or a function of `y` on the right-hand side
- a single global coefficient vector shared across discharges
- support sizes outside 1–12
- counting the intercept as a coordinate, which would let a 12-coordinate
  representation quietly become 13 parameters
