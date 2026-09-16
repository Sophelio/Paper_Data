# S7.5 — Typed relational ontology `G_rec`

**Freeze:** `D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1`
**Status:** `FROZEN_READY_FOR_S7.6` · acceptance **50/50**
**Ontology:** `G_REC_DENSITY_V1` v1.0.0

```
G_rec = Gamma( X_rec, O_rec, K_rec ; Lambda_rec, T_rec )

78 primitives · 5 constructor families · max depth 1
Lambda_rec = {C0 level, C1 derivative, C2 product, C3 ratio, C4 phase derivative}
T_rec      = affine-linear in constructed coordinates, m in [1,12]
```

> `G_rec` is the **grammar**, not the enumeration. **`A_rec` is not built here** —
> that is S7.6.

## Start here

| File | What it is |
|---|---|
| `S7_5_TYPED_RELATIONAL_ONTOLOGY_FINAL.md` | manuscript-ready prose |
| `S7_5_TYPED_RELATIONAL_ONTOLOGY_AUDIT_REPORT.md` | the full internal audit |
| `CONSTRUCTOR_CATALOG.md` | the five families and their rules |
| `TYPE_SYSTEM_AND_PROPAGATION.md` | dimensional, temporal, flag, provenance typing |
| `RELATION_TEMPLATE.md` | the reconstruction relation and coefficient dimensions |
| `S7_4_INHERITED_DOCUMENTATION_ERRATA.md` | two S7.4 prose corrections |

## Constructor families

| | Family | Depth | Eligible operands | Notes |
|---|---|---|---|---|
| **C0** | primitive level | 0 | **78** | includes both uncalibrated levels |
| **C1** | first temporal derivative | 1 | **70** | `FD2_PHYSICAL_TIME_V1`, `d/dtau` forbidden |
| **C2** | pairwise product | 1 | **76** | symmetric, self allowed, unlike dimensions allowed |
| **C3** | pairwise ratio | 1 | **76** | directional, partial map `x_j ≠ 0` |
| **C4** | phase derivative `D_{x_j} x_i` | 1 | **70** | directional, partial map `dx_j/dt ≠ 0` |

Symbolic upper bounds, **audit only**: 78 + 70 + 2 926 + 5 700 + 4 830 =
**13 604** primary coordinates, plus 6 sensitivity-only. No instance enumerated.

## Three things worth knowing

**The raw comparator is nested inside the ontology.** A representation whose
coordinates are all C0 levels is an admissible special case, so baseline B2 is a
*member* of the search space — the comparison is about representation, not about
two frameworks.

**Sum and difference are deliberately absent.** Against an affine-linear
template, `x_i ± x_j` is already representable by including both primitives with
coefficients. Adding them would enlarge the candidate set without enlarging the
span. An algebraic-redundancy argument, **not** a performance result.

**Eight of 78 primitives cannot enter derived coordinates.** The 2 uncalibrated
(dimensionally uncertified, fail-closed) plus the 6 upstream-upsampled
(derivatives are `NUMERICAL_SENSITIVITY_ONLY`). All 8 remain fully admissible as
levels.

## Inherited errata (both documentary only)

- **"four" heterogeneous type blocks → three.** Machine-readable artifacts
  encode three; an independent component-level recount agrees. S7.4 not
  reopened.
- **cadence denominator wording.** Definition and implementation both use
  `(n − 1)`, verified in source. Prose said "the number of samples received".

## Machine-readable

```
G_REC.json                          the ontology
primitive_type_registry.csv         78 rows: type, unit, flags, eligibility
constructor_catalog.json            Lambda_rec, 5 families + symbolic bounds
constructor_type_rules.json         dimensional/temporal/flag/provenance rules
excluded_constructor_families.json  23 exclusions, 4-valued status vocabulary
coordinate_signature_schema.json    canonicalization + duplicate prevention
relation_templates.json             T_rec
dependency_constraints.json         pinj = sum(pinj_*) group
ontology_constraints.json           depth, no-search-priority, A_rec not built
S7_5_ACCEPTANCE_CHECKS.json         50 checks
S7_5_FREEZE.json                    freeze record and all artifact hashes

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/PREFLIGHT_SEMANTIC_CHECKS.json
manifests/DERIVATIVE_REALIZATION_CHECK.json
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\05_typed_relational_ontology\scripts\s7_5_build_g_rec.py
```

Opens no archive. Exits non-zero on parent drift, on a pre-flight inconsistency
requiring S7.4C, or if the derivative realization fails its capability check.

## Stage gate

`A_rec` not enumerated · no search · no search priority · no regression · no
baseline · no predictor-target correlation · no reconstruction performance · no
external value · target unchanged · 78 primitives unchanged · **S7.6 not
started.**
