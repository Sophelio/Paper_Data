# S7.2 — Unit and type policy (part of `P_rec`)

S7.1 found three unit-scale inconsistencies **inside** the object, all invisible
under within-discharge z-scoring. They become live the moment a construction
crosses a pair — which is exactly what a relational ontology does.

| Quantity | Signals | Stored as | Ratio |
|---|---|---|---|
| Power | `pinj` / `pinj_*` | kW / W | 10³ |
| Number density | `density` / `prmtan_neped` | cm⁻³ / m⁻³ | 10⁶ |
| Temperature | `ece*` / `cerqtit*`, `prmtan_teped` | keV / eV | 10³ |

## Order of operations — FROZEN

Before **any** coordinate constructor operates:

1. **Canonicalise units.** Convert compatible physical quantities to one
   canonical unit per dimension.
2. **Preserve the conversion mapping.** Record factor, source unit and canonical
   unit per signal, as a hashed artifact.
3. **Dimensionally check every algebraic construction.** A construction that
   fails the check is rejected at generation time, not filtered later.
4. **Never rely on z-scoring to hide a unit mismatch.**

Standardisation, where used, happens **after** canonicalisation and is a
numerical-conditioning step, never a substitute for dimensional correctness.

### Canonical units

| Dimension | Canonical | Converted from |
|---|---|---|
| power | W | `pinj` kW → W (×10³) |
| number density | m⁻³ | `density` cm⁻³ → m⁻³ (×10⁶) |
| temperature | eV | `ece*` keV → eV (×10³) |
| length, area, volume | m, m², m³ | already canonical |
| current | A | already canonical |
| magnetic flux density | T | already canonical |
| electric potential | V | already canonical |
| velocity | m s⁻¹ | `cerqrott*` km/s → m s⁻¹ (×10³) |
| torque | N m | already canonical |
| photon flux | ph sr⁻¹ m⁻² s⁻¹ | filterscopes cm⁻² → m⁻² (×10⁴) |
| dimensionless | 1 | already canonical |

SI base is chosen throughout, except **eV for temperature**, which is retained
because it is the field's convention and because the majority of temperature
channels (CER, pedestal) are already in eV — converting to joules would obscure
the physics without removing any ambiguity.

Choosing **eV over keV** and **m⁻³ over cm⁻³** resolves each trap toward the SI-
consistent member of the pair.

---

## Constructor type rules — FROZEN

| Constructor | Dimensional rule | Output type |
|---|---|---|
| **sum / difference** | operands must be dimensionally **identical** | same dimension |
| **ratio** | dimensions tracked explicitly; flagged **dimensionless** when they cancel | dim(num) − dim(den) |
| **product** | always defined | dim(a) + dim(b) |
| **temporal derivative** | always defined | dim(x) · time⁻¹ |
| **trajectory-relational derivative** | ratio of rates | dim(num) − dim(den) |
| **normalization** | must record the reference scale **and** whether it is physical or empirical | dimensionless |
| **log / exp / transcendental** | argument must be **dimensionless** | dimensionless |

The sum rule is strict: `pinj + density` is rejected at construction, not
discovered later as a poorly-conditioned coordinate.

The normalization rule matters for provenance. A **physical** reference (e.g.
a Greenwald-style scale) is a knowledge claim; an **empirical** reference (a
calibration-set standard deviation) is a fitted quantity subject to the leakage
firewall. The two must be distinguishable in the coordinate's type.

---

## Uncalibrated signals

`pcbcoil` and `pcdiamag3` are documented upstream as `raw`: uncalibrated
digitiser output with no physical unit.

> **Do not invent physical dimensions for them.**

If used later, their type remains permanently:

```
UNCALIBRATED_SIGNAL
```

Consequences:

- they may **not** enter sums or differences with any dimensioned quantity;
- they may **not** enter dimensional-consistency arguments;
- a ratio of two `UNCALIBRATED_SIGNAL` quantities is `UNCALIBRATED_RATIO`, not
  dimensionless;
- any coordinate containing one inherits the flag transitively;
- they are **excluded as primary targets** (`TARGET_ELIGIBILITY_POLICY.md`),
  because reconstruction error in an undefined unit is uninterpretable.

They are not excluded as *predictors*. An uncalibrated channel can still carry
information; it simply cannot carry a dimensional argument.

## Deferred

- **S7.5:** the instantiated conversion table for the admitted set (hashed), and
  per-coordinate dimensional signatures.
- **S7.6:** dimensional rejection counts during ontology generation.
