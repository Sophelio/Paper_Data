# S7.6R — Admissible universe rebuild on the hardened ontology

**Freeze:** `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2`
**Universe:** `A_REC_DENSITY_HARDENED_V2`
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance **49/49**

```
G_REC_DENSITY_HARDENED_V2  ->  23,861 symbolic  ->  10,778 admissible atoms
70 primitives · 9 families C0-C8 · depth 1 · support 1-12 · T_REC_V1
```

**Zero density values. Zero external values. No model, no baseline, no
correlation, no ranking, no search.**

---

## What this is, and what it is not

> Historical S7.6 V1 was completed on the superseded ontology and is preserved
> as audit history. The primary admissible universe is rebuilt here de novo from
> the hardened ontology.

`D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1` (78 primitives, C0–C4, 6 034 atoms) is
marked `HISTORICAL_SUPERSEDED` / `NOT_A_PRIMARY_PARENT_FOR_ADMISSIBILITY_RESULTS`
and was re-verified **byte-for-byte unchanged** after this rebuild. None of its
pass/fail lists, registries, denominator results, or dependency groups was
consulted. Every signature here was regenerated from scratch.

## Survival

| family | symbolic | admissible | | family | symbolic | admissible |
|---|---|---|---|---|---|---|
| C0 level | 70 | 66 | | C5 reciprocal | 68 | 39 |
| C1 derivative | 63 | 59 | | C6 level·rate | 4 284 | **3 776** |
| C2 product | 2 346 | 2 080 | | C7 rate/level | 4 284 | 2 301 |
| C3 ratio | 4 556 | 2 457 | | C8 level/rate | 4 284 | **0** |
| C4 phase | 3 906 | **0** | | **total** | **23 861** | **10 778** |

Rejections: **E 11 989** (denominator domain) · **D 1 094** (numerical support).
Every one carries an auditable first cause.

## Four qualifications

**1. `ZERO_SURVIVING_PRIMARY_C4`** and **2. `ZERO_SURVIVING_PRIMARY_C8`.** The
rate-denominator table passes **0 of 63** candidates: 61 fail on a sign change
(a derivative crosses zero inside every calibration block), 2 on zero scale
(beamlines that never fired). Recomputed from scratch, not inherited.
→ `PARTIAL_MAP_ADMISSIBILITY.md`

> `G_rec^H` admitted the constructor family conceptually; the observational
> object failed to support stable primary instances under `K_rec`'s
> numerical-domain condition.

The gate was not weakened, the ontology was not revised, and neither family was
removed from the catalogue.

**3. `ZERO_BINDING_EXACT_DEPENDENCY_GROUPS`.** All 400 re-derived `pinj` groups
are vacuous: four of the eight per-beam components are themselves class-D
inadmissible, so no admissible support can hold a complete exact set. The
predicate is retained. → `REPRESENTATION_SET_CONSTRAINTS.md`

**4. `SEARCH_POLICY_MULTIPLICITY_CONTROL_REQUIRED`.** Carried to S7.7
**unresolved**. 0 coordinates were deleted for it and 0 weights assigned. ECE is
47.1% of `P_hard` but an ancestor of **84.2%** of admissible atoms, and 33 of
the 39 surviving level denominators are ECE — so C3, C5 and C7 are *more*
ECE-concentrated than the basis. `ADMISSIBLE ≠ PRIORITIZED`.

## The denominator rule

Verified by hash (`6d4004eb…`), **not reopened**, threshold unchanged, scope
declared: `LEVEL_DENOMINATOR_STATUS` (C3, C5, C7) and `RATE_DENOMINATOR_STATUS`
(C4, C8). C6 has no denominator and no gate — which is why it is now the largest
admissible family.

## Start here

| File | What it is |
|---|---|
| `S7_6R_ADMISSIBLE_UNIVERSE_FINAL.md` | manuscript-ready prose |
| `S7_6R_ADMISSIBLE_UNIVERSE_AUDIT_REPORT.md` | the full internal audit, 20 sections |
| `PARTIAL_MAP_ADMISSIBILITY.md` | the denominator tables and the two zero-survivor families |
| `REPRESENTATION_SET_CONSTRAINTS.md` | `Φ_set`, and why all 400 dependency groups are vacuous |

## Machine-readable

```
A_REC_HARDENED.json                    the factorized universe
atomic_coordinate_universe.json        C_REC_HARD_ATOM_V2
representation_set_constraints.json    PHI_SET_H_V2
partial_map_admissibility.json         both denominator tables
search_multiplicity_handoff.json       the S7.7 requirement
historical_v1_comparison.json          AUDIT ONLY, written after the freeze data
S7_6R_ACCEPTANCE_CHECKS.json           49 checks
S7_6R_FREEZE.json

coordinate_registry_symbolic.csv       23,861 regenerated signatures
coordinate_admissibility.csv           per-coordinate B/A/C/G/F/D/E/H
primary_atomic_coordinate_universe.csv 10,778 atoms
coordinate_rejection_log.csv           13,083 rejections, first cause each
denominator_conditioning_audit.csv     7,860 denominator evaluations
numerical_support_audit.csv            per-primitive class D
constructor_survival_census.csv
atomic_family_composition.csv
exact_dependency_groups_attempted.csv  400 rows, BINDING / VACUOUS
exact_dependency_groups.csv            the binding subset (empty)
sensitivity_only_coordinate_registry.csv

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/HISTORICAL_S7_6_V1_RECORD.json      byte snapshot taken before the rebuild
manifests/HISTORICAL_V1_PRESERVATION.json     re-verified after it
manifests/DENOMINATOR_RULE_VERIFICATION.json
manifests/STAGE_SEQUENCE_QUALIFICATION.json
manifests/DEPENDENCY_DERIVATION.json
manifests/UNIVERSE_SUMMARY.json
manifests/ACCESS_AUDIT.json
manifests/DATA_ACCESS_LOG.csv
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\06_admissible_universe\hardened_v2\scripts"
& $P $S\s7_6r_a_preflight.py   # metadata only; opens no archive
& $P $S\s7_6r_b_universe.py    # 20 development discharges, predictors only
& $P $S\s7_6r_c_freeze.py      # A_rec^H, predicates, acceptance, freeze
```

Deterministic; no seeds. Stage B aborts if the denominator rule hash changed.

## Stage gate

No search · no search policy · no search priority · no ranking · no model · no
baseline · no target correlation · no density value · no external value ·
`H0_RAW_HARDENED` frozen and not run · B2 unchanged and not run · support bound
1–12 unchanged · `T_REC_V1` unchanged · `FD2_PHYSICAL_TIME_V1` unchanged ·
historical S7.6 V1 byte-for-byte unchanged · **S7.7 not started.**
