# S7.5 — Typed relational ontology: internal audit

**Freeze:** `D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1`
**Status:** `FROZEN_READY_FOR_S7.6` · acceptance **50/50** · 2026-09-04

---

## 1. Executive verdict

`G_rec = Gamma(X_rec, O_rec, K_rec; Lambda_rec, T_rec)` is instantiated as a
**grammar**, not an enumeration. Five primary constructor families over 78
primitives at maximum depth 1, with component-level dimensional typing,
conservative temporal and flag propagation, transitive provenance, one exact
dependency constraint, a frozen derivative realization, and an affine-linear
relation template.

**`A_rec` is not enumerated.** Symbolic upper bounds are recorded for audit
(13 604 primary coordinates) but no instance was created.

Both inherited S7.4 pre-flight checks resolve as **documentary errata only** —
the machine-readable artifacts and the frozen computation are correct in both
cases, so S7.4 was not reopened.

**Zero external values. No model, no baseline, no correlation, no search
priority.**

Two design points are worth stating up front. First, **the raw-coordinate
comparator is nested inside the ontology** — an all-C0 representation is an
admissible special case, so the B2 comparison is a statement about
representation rather than about two frameworks. Second, **sum and difference
are deliberately absent** on a redundancy argument, not a performance one.

## 2. Parent verification — `PARENTS_VERIFIED`, 0 drift

All seven parents verify: S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1, S7.3R V2,
S7.4 V2. Thirteen substantive checks pass, including: `y* = density`; canonical
unit `m^-3`; 78 predictors; 7 families; 8 blocks; `vsurf` excluded; external
cohort 42 and sealed; `X_rec` instantiated; S7.3R V2 and S7.4 V2 authoritative;
S7.4 V1 historical stop preserved; support bound 1–12 and depth 1 unchanged.

## 3. Inherited documentation errata

Full treatment in `S7_4_INHERITED_DOCUMENTATION_ERRATA.md`.

**E-1 — "four" heterogeneous blocks → three.** `X_REC.json` flags exactly three
(`X_NBI`, `X_mag`, `X_density_aux`); an independent component-level recount from
`typed_signal_blocks.csv` agrees. S7.4 prose said four while naming three.
`DOCUMENTARY_ERRATUM_ONLY`; S7.4 not reopened.

**E-2 — cadence denominator wording.** Both the machine-readable definition and
`s7_3r_reconcile.py` use `(original_length − 1)`, verified by source inspection.
The loose prose said "divided by the number of samples received". The correct
denominator matters in the conservative direction: dividing by `n` would
understate the spacing and thereby **overstate** resolution.
`DOCUMENTARY_ERRATUM_ONLY`; frozen computation unchanged.

No frozen S7.4 file was edited. `S7/STATUS.md`, a living document, was corrected
in place.

## 4. Formal `G_rec`

```
G_rec = Gamma(X_rec, O_rec, K_rec; Lambda_rec, T_rec)
ontology_id  G_REC_DENSITY_V1   version 1.0.0
Lambda_rec   {C0, C1, C2, C3, C4}      T_rec  T_REC_V1
```

Retains explicit access to primitive scientific types, units, origin/provenance,
temporal qualifications, exact dependency edges, target exclusion and
numerical-realization semantics.

## 5. Primitive type registry — 78

| Dimension class | Unit | n |
|---|---|---|
| temperature / energy | eV | **48** |
| velocity | m s⁻¹ | 7 |
| power | W | 9 |
| electric potential | V | 4 |
| photon flux | ph sr⁻¹ m⁻² s⁻¹ | 4 |
| uncalibrated | — | 2 |
| torque, magnetic flux density, electric current, number density | N m, T, A, m⁻³ | 1 each |

Eligibility: **78** level-admissible · **76** product/ratio operands · **70**
derivative and phase operands · **6** derivative sensitivity-only · **2**
uncalibrated.

The 48 eV components span three blocks, which is why typing follows the
component.

## 6. Constructor catalogue

| | Family | Depth | Arity | Eligible operands |
|---|---|---|---|---|
| C0 | primitive level | 0 | 1 | 78 |
| C1 | first temporal derivative | 1 | 1 | 70 |
| C2 | pairwise product, symmetric, self allowed | 1 | 2 | 76 |
| C3 | pairwise ratio, directional | 1 | 2 | 76 |
| C4 | trajectory-relational (phase) derivative, directional | 1 | 2 | 70 |

Maximum depth 1; constructors consume **primitives only**. Explicitly not
primary: `d(x_i x_j)/dt`, `x_i·(dx_j/dt)`, `(x_i/x_j)·x_k`, `D_{x_k}(x_i x_j)`,
ratio of ratios, product of phase derivatives.

Symbolic upper bounds (audit only): 78 + 70 + 2 926 + 5 700 + 4 830 =
**13 604** primary, plus 6 sensitivity-only.

## 7. Derivative numerical realization — `FD2_PHYSICAL_TIME_V1`

`numpy.gradient(x, t, edge_order=2)` with respect to actual physical time in
seconds, using each discharge's own `T_s`.

No fitted smoothing parameter · no target values · no whole-ensemble fit · no
cross-discharge stencil · no spline or RTS in primary · never with respect to
`tau`.

**Capability check passed** (§10 requirement): tested at 5.853, 6.824 and
14.187 ms; halving `dt` over a fixed window reduced maximum interior error by
**4.00×** at both refinements — second-order confirmed. Synthetic data only;
zero observational values touched. Each `T_s` is uniform within its discharge,
so the second-order case is the operative one; non-uniform behaviour is recorded
but not relied upon.

## 8. Dimensional type algebra

Component-level. `C0 → [x]` · `C1 → [x]/time` · `C2 → [x_i][x_j]` ·
`C3, C4 → [x_i]/[x_j]`. Phase derivative time dimensions cancel.

Standardization does not alter scientific type. Operands of products and ratios
need not share dimensions — the output carries the compound dimension
explicitly.

## 9. Temporal and provenance propagation

C0 inherits unchanged; C1 inherits plus `DERIVED_FROM_NUMERICAL_REALIZATION`;
C2/C3 limited by the coarser operand resolution; C4 by the coarser
derivative-source resolution. **Invariant: no coordinate may claim resolution
finer than either operand.**

`ALIASING_RISK` propagates from any operand. `UPSTREAM_UPSAMPLED` keeps the
level but removes the derivative from primary. Where both occur —
`prmtan_neped`, `prmtan_teped` — sensitivity-only dominates.

Every coordinate keeps an exactly recoverable ancestor set; target independence
is **transitive** and encoded as an invariant even though it holds
automatically from the 78-primitive boundary.

## 10. Uncalibrated-signal policy

`pcbcoil`, `pcdiamag3`: level `PRIMARY_ADMISSIBLE`; every derived coordinate
`DIMENSIONALLY_UNCERTIFIED_PRIMARY_EXCLUDED`. Fail-closed dimensional
admissibility — not a claim that the signals lack information. This is why C2
and C3 have 76 eligible operands rather than 78.

## 11. Exact dependency constraint

`DEP_NBI_POWER_SUM`: `pinj = sum(pinj_*)`, `EXACT_DETERMINISTIC_SUM`,
`LOCAL_DOCUMENTED`. Neither aggregate nor components removed.

**Scope is representation-level.** At depth 1 with arity ≤ 2 no single
coordinate can carry the whole exact set, so the redundancy can only appear in a
coordinate *set*. A representation containing the aggregate and all eight
components is flagged `EXACT_LINEAR_REDUNDANCY_RISK`. The operational exclusion
rule belongs to S7.6; the principle it must implement is that deterministic
restatements are not independent scientific evidence.

## 12. Coordinate canonicalization

`ID(sig)` · `DOT(sig)` · `PROD(i,j)` with `i ≤ j` · `RATIO(i,j)` ·
`PHASE(i|j)` meaning `D_{x_j} x_i`. Display labels are explicitly **not**
identity.

Duplicate prevention: product symmetry collapses transposes to one identity;
`RATIO(i,i)` and `PHASE(i|i)` are invalid signatures; ratio and phase direction
are preserved as distinct.

## 13. Relation template `T_REC_V1`

Affine-linear in constructed coordinates; support shared across discharges;
coefficients discharge-specific; intercept permitted and **not counted** toward
`m ∈ [1,12]`; target never on the explanatory side.

`[beta_j] = m^-3 / [c_j]`, so coordinates within one relation need not share
units. Uncalibrated operands get `coefficient_dimension_status = UNCALIBRATED`
and no physical reading.

**Estimator not chosen and not run** — that belongs to the frozen search policy.

## 14. Excluded families

23 recorded with a four-valued status vocabulary: `GENERAL_FRAMEWORK_PERMITS` /
`TASK_ONTOLOGY_EXCLUDES` / `PRIMARY_ONTOLOGY_EXCLUDES` / `SENSITIVITY_ONLY`.

The vocabulary matters: exclusion from this finite primary ontology is **not** a
claim of scientific meaninglessness. Reference-shifted, bounded and
sensitivity-centered phase derivatives are excluded as *distinct constructions*
requiring separate qualification, not as invalid mathematics.

Sum/difference carries the fullest reasoning, because it is the one exclusion
that could be mistaken for an empirical judgement: it is algebraic redundancy
against an affine-linear template, and the dimensional compatibility rules for
sums remain in the general type system regardless.

## 15. Primary versus sensitivity-only

Primary grammar: 13 604 symbolic coordinates. Sensitivity-only: the 6
derivatives of the upstream-upsampled signals, representable in `G_rec` as
`SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT` so S7.11 can examine them, and **not** in
primary `A_rec` unless the contract is explicitly revised.

## 16. External access audit

**Zero external values. Zero archives opened.** The only numerical work was the
synthetic derivative capability check. No predictor-target correlation, no
regression, no baseline, no reconstruction performance, no search priority, no
`q_desc` seeding.

## 17. Files produced

7 Markdown, 1 CSV, 9 JSON, 1 script — all hashed in `S7_5_FREEZE.json`.

## 18. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\05_typed_relational_ontology\scripts\s7_5_build_g_rec.py
```

Deterministic; the one seeded draw is the synthetic non-uniform grid check
(`default_rng(0)`). Exits non-zero on parent drift, on a pre-flight
inconsistency that would require S7.4C, or if the derivative realization fails
its capability check.

## 19. Recommendation for S7.6

**`READY_FOR_S7.6`.**

S7.6 inherits: five constructor families at depth 1; per-family operand
eligibility (78 / 70 / 76 / 76 / 70); the canonical signature schema and its
duplicate-prevention rules; component-level dimensional algebra; temporal, flag
and provenance propagation rules; domain predicates for the two partial maps;
the `EXACT_LINEAR_REDUNDANCY_RISK` constraint to operationalise; and symbolic
upper bounds of 13 604 primary coordinates to check its enumeration against.

Two things S7.6 must decide that S7.5 deliberately did not: the operational
exclusion rule for coordinate sets carrying the exact dependency, and how
domain predicates on the two partial maps become instance-level admissibility
under numerical support.

**S7.6 is not authorised by this document.**
