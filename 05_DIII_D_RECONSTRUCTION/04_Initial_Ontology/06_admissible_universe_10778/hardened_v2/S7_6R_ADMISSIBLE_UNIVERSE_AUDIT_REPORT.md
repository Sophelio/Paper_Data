# S7.6R — Admissible universe rebuild on the hardened ontology: internal audit

**Freeze:** `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2`
**Universe:** `A_REC_DENSITY_HARDENED_V2`
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance **49/49** · 2026-09-04

---

## 1. Executive verdict

The hardened atomic universe is built and frozen: **23 861 symbolic coordinates
regenerated from scratch**, **10 778 admissible atoms**, nine families, depth 1.
Zero target values, zero external values, no model, no baseline, no
predictor–target statistic, no search, no priority.

**Four qualifications, all recorded rather than repaired:**

1. **`ZERO_SURVIVING_PRIMARY_C4`** — no phase-derivative instance survives the
   unchanged rate-denominator gate.
2. **`ZERO_SURVIVING_PRIMARY_C8`** — no level-over-rate instance survives, by the
   same mechanism.
3. **`ZERO_BINDING_EXACT_DEPENDENCY_GROUPS`** — all 400 re-derived groups are
   vacuous, because four of the eight per-beam component coordinates are
   themselves class-D inadmissible.
4. **`SEARCH_POLICY_MULTIPLICITY_CONTROL_REQUIRED`** is carried to S7.7
   unresolved, and the surviving denominators are *more* ECE-concentrated than
   the primitive basis.

None of these changed a rule, a threshold, or the ontology.

## 2. Parent verification

`PARENTS_VERIFIED` — **0 hash drift** across all ten lineage records (S7.1,
S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1, S7.3R V2, S7.4 V2, S7.5, S7.5H, and the
historical S7.6 V1). All 22 substantive checks pass: target `density`, canonical
unit `m^-3`, `G_REC_DENSITY_HARDENED_V2` v2.0.0 authoritative, `M=70`, `Mt=68`,
`Md=63`, catalogue `C0…C8`, depth 1, symbolic bounds and total 23 861,
`T_REC_V1` unchanged, `FD2_PHYSICAL_TIME_V1` unchanged, support bound 1–12,
external cohort 42 sealed.

## 3. Historical S7.6 V1 reconciliation

> Historical S7.6 V1 was completed on the superseded ontology and is preserved
> as audit history. The primary admissible universe is rebuilt here de novo from
> the hardened ontology.

`D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1` → `HISTORICAL_SUPERSEDED` /
`NOT_A_PRIMARY_PARENT_FOR_ADMISSIBILITY_RESULTS`.

Stage A took a byte snapshot of all 29 files in the V1 directory; stage C
re-verified it after the rebuild:
`HISTORICAL_S7_6_V1_BYTE_FOR_BYTE_UNCHANGED`, 0 files changed.

Contamination: V1 accessed **0** target values, **0** external values, computed
**0** predictor–target statistics, fitted **0** models. No target-derived
information exists anywhere in the lineage.

What was **not** done: no V1 pass/fail list consulted, no V1 registry imported,
no V1 denominator result reused, no V1 dependency group copied, no admissibility
seeded from V1. The only permitted use — an aggregate-count comparison — was
performed in stage C *after* the hardened universe and its predicates were
written and hashed (§15).

## 4. Firewall

```
development shots read            20  (exactly the frozen cohort)
predictor signals read per shot   70  (exactly P_hard)
calibration blocks read           A, B, C  (nested prefixes)
TARGET VALUES ACCESSED             0
EXTERNAL VALUES ACCESSED           0
external shots read               none
models fitted / baselines run      0 / 0
predictor-target correlations      0
```
`FIREWALL_INTACT`.

## 5. Symbolic enumeration

Regenerated mechanically from `P_hard` × the frozen catalogue, with an exact
equality assertion against the ontology's own bounds:

| C0 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | total |
|---|---|---|---|---|---|---|---|---|---|
| 70 | 63 | 2 346 | 4 556 | 3 906 | 68 | 4 284 | 4 284 | 4 284 | **23 861** |

All coordinate IDs unique. Canonical signatures per the frozen S7.5H schema;
`PROD` ordered by frozen inventory index, `C6` explicitly *not* collapsed across
operand roles.

The five sensitivity-only derivative coordinates (`prmtan_neped`,
`prmtan_teped`, `fs04`, `fs03da`, `fs05da`) are registered separately and are
outside primary `A_rec`. The same rule keeps those five signals out of every
rate role in C4, C6, C7 and C8; none was promoted.

## 6. Metadata gates B / A / C / G / F

**0 rejections.** Every ancestor lies in the corrected target-independent
boundary, every provenance lineage is exactly recoverable, every output
dimension and unit expression is certified, depth ≤ 1 everywhere, and the target
is absent everywhere.

This is not a vacuous pass: the gates were evaluated independently of the
operand sets, checking that every *level*-role operand is typed and every
*rate*-role operand is primary derivative-eligible. They agree with the frozen
eligibility rules, which is the expected and desired outcome — the two
uncalibrated quantities appear only under C0, and the five interpolated
quantities never appear in a rate role.

## 7. Numerical-support audit (class D)

Minimum calibration-block length **130 samples** (required ≥ 30). Constancy
detected exactly (`min == max`), with no variance threshold invented.

**1 094 class-D rejections.** All trace to four beamlines — `pinj_15r`,
`pinj_21l`, `pinj_21r`, `pinj_33l` — each identically constant across at least
one required development calibration block, i.e. inactive for that whole
interval. Their levels, their derivatives, and every product or level–rate
coordinate built on them inherit the rejection.

| family | D-rejections |
|---|---|
| C0 | 4 | 
| C1 | 4 |
| C2 | 266 |
| C3 | 156 |
| C6 | 508 |
| C7 | 156 |

## 8. Level-denominator audit (`LEVEL_DENOMINATOR_STATUS`, used by C3/C5/C7)

68 candidates × 60 cells = 4 080 evaluations. **39 pass on every required
block, 29 fail.**

First-failure reasons across cells: sign change 521, zero value 231, RMS zero
96, margin below η 84.

The 39 survivors are **33 ECE channels** plus `bt`, `ip`, `prmtan_neped`,
`cerqtit3`, `cerqtit10`, `cerqtit11`. The failures are all 10 beam signals, all
4 gas valves, 3 filterscopes, 11 CER rotation/temperature chords, and
`prmtan_teped`.

The pattern is physical: electron temperature is strictly positive and smooth
across a calibration block, so it satisfies both the sign and margin conditions;
rotation crosses zero, gas valves and beams switch off, filterscopes fluctuate
to the noise floor.

## 9. Rate-denominator audit (`RATE_DENOMINATOR_STATUS`, used by C4/C8)

63 candidates × 60 cells = 3 780 evaluations. **0 pass. 63 fail.**

First-failure reasons by signal: **sign change 61**, RMS zero 2 (`pinj_21l`,
`pinj_21r` — beamlines that never fired). Every one of the 63 derivatives
changes sign in at least one required calibration block; in fact 3 684 of the
3 780 individual cells show a sign change.

This was **recomputed from scratch** on the hardened basis. The historical V1
result was not consulted, assumed, or used to skip any evaluation. That the two
stages agree is a corroboration, not an inheritance.

## 10. C0–C8 survival census

| family | symbolic | admissible | survival | D-rej | E-rej |
|---|---|---|---|---|---|
| C0 level | 70 | 66 | 94.3% | 4 | — |
| C1 derivative | 63 | 59 | 93.7% | 4 | — |
| C2 product | 2 346 | 2 080 | 88.7% | 266 | — |
| C3 ratio | 4 556 | 2 457 | 53.9% | 156 | 1 943 |
| C4 phase derivative | 3 906 | **0** | 0% | 0 | 3 906 |
| C5 reciprocal | 68 | 39 | 57.4% | 0 | 29 |
| C6 level–rate | 4 284 | 3 776 | 88.1% | 508 | — |
| C7 rate over level | 4 284 | 2 301 | 53.7% | 156 | 1 827 |
| C8 level over rate | 4 284 | **0** | 0% | 0 | 4 284 |
| **total** | **23 861** | **10 778** | **45.2%** | 1 094 | 11 989 |

Rejections by class: **E 11 989, D 1 094**. By reason: sign change 10 157,
constant on a required block 1 094, margin below η 786, zero value 524, RMS zero
522. Every rejection carries an auditable first cause and a first rejecting
class.

**These counts are not evidence of importance.** A family with 3 776 admissible
atoms is not thereby more useful than one with 39.

## 11. Exact dependency groups

`pinj = Σ_b pinj_b`, evidence class `LOCAL_DOCUMENTED`, re-derived over the
hardened catalogue — **not** copied from V1.

Exact restatements hold in eight contexts (**400 groups attempted**):

| context | groups | argument |
|---|---|---|
| `C0` level | 1 | aggregate enters linearly |
| `C1` derivative | 1 | `d/dt` linear; FD2 is a fixed linear stencil |
| `C2` `PROD(pinj,z)` | 59 | `x_z·Σ = Σ x_z·x_b` |
| `C3` `RATIO(pinj,z)` | 59 | aggregate in **numerator** only |
| `C4` `PHASE(pinj\|z)` | 54 | aggregate rate in **numerator** only |
| `C6` `LEVEL_RATE(pinj\|z)` | 54 | linear in the level operand |
| `C6` `LEVEL_RATE(z\|pinj)` | 59 | via derivative linearity |
| `C7` `RATE_OVER_LEVEL(pinj\|z)` | 59 | aggregate rate in **numerator** only |
| `C8` `LEVEL_OVER_RATE(pinj\|z)` | 54 | aggregate level in **numerator** only |

No identity was inferred where the aggregate enters a denominator —
`RATIO(z,pinj)`, `PHASE(z|pinj)`, `RATE_OVER_LEVEL(z|pinj)`,
`LEVEL_OVER_RATE(z|pinj)` — nor under `RECIP(pinj)`, which is not linear, nor
for `PROD(pinj,pinj)`, which is quadratic.

**All 400 groups are VACUOUS. 0 binding.** Each contains at least one
inadmissible member: the four inactive-beamline components fail class D, and
groups in C4 and C8 have no admissible members at all. `Φ_dependency` is
retained and well defined; in this universe it currently excludes nothing. Both
the attempted and the binding tables are written out, so the distinction is
auditable rather than implicit.

## 12. Atomic universe

```
C_REC_HARD_ATOM_V2 : 10 778 atoms from 23 861 symbolic (45.2%)
```

Ancestor-family reach (a two-operand coordinate has two families, so shares sum
above 1):

| family | primitives | atoms with this ancestor | share |
|---|---|---|---|
| ECE | 33 | 9 075 | **0.842** |
| CER | 14 | 3 736 | 0.347 |
| beams | 10 | 1 551 | 0.144 |
| gas | 4 | 1 046 | 0.097 |
| magnetics | 4 | 769 | 0.071 |
| filterscope | 3 | 486 | 0.045 |
| density-aux | 2 | 446 | 0.041 |

## 13. Factorized support universe

```
S_rec^H = { C ⊆ C_rec_hard^atom : 1 ≤ |C| ≤ 12 ∧ Φ_set(C) = PASS }
A_rec^H = { (C, T_REC_V1) : C ∈ S_rec^H }
```

`Φ_set` = size 1–12 · no duplicate IDs · atoms only · no sensitivity-only
coordinate · no complete exact dependency group · target absent.

Support combinations were **not** materialised. The unconstrained subset count
for `M = 10 778` at sizes 1–12 is astronomically large and is reported in
`A_REC_HARDENED.json` only to show why. The factorized definition is exact.

Explicitly **not** imposed: must contain a phase derivative, must span multiple
families, must include raw levels, must include a partial map, or any heuristic,
weight, ranking or preference whatsoever.

## 14. External partial-map rule

Frozen without opening a single external value. Any finally selected support
containing a partial-map coordinate must satisfy the **same** domain rule on
each external local-calibration block. On failure: do not alter the coordinate,
do not replace it, do not add an epsilon, do not refit the support — record that
discharge/block as `NOT_APPLICABLE` and let downstream qualification determine
the surviving `Ω_rec`. That is the already-frozen rule, carried verbatim.

## 15. Historical V1 comparison — audit only

Performed after the hardened universe was determined and written. **No rule was
changed as a result. No V1 pass/fail status was reused.**

| | V1 (78 primitives, C0–C4) | V2 (70 primitives, C0–C8) |
|---|---|---|
| symbolic | 13 604 | 23 861 (1.75×) |
| atoms | 6 034 | **10 778** (1.79×) |
| survival rate | 44.4% | 45.2% |

| family | V1 atoms | V2 atoms |
|---|---|---|
| C0 | 74 | 66 |
| C1 | 66 | 59 |
| C2 | 2 628 | 2 080 |
| C3 | 3 266 | 2 457 |
| C4 | 0 | 0 |
| C5 / C6 / C7 / C8 | — | 39 / 3 776 / 2 301 / 0 |

The four new families contribute **6 116 atoms**, and the narrower basis removes
about 1 372 from the original five. The S7.5H expectation that the broadening
might add only the 68 C5 coordinates was **too pessimistic**: C6, which carries
no denominator, survives at 88% and is now the largest single family. C7
survives wherever its level denominator does. Only C8 shared C4's fate.

## 16. Search-multiplicity handoff

`SEARCH_POLICY_MULTIPLICITY_CONTROL_REQUIRED` → owner **S7.7**.

**Not solved here. 0 coordinates deleted to address it. 0 weights assigned.**

The evidence this stage adds: ECE is 47.1% of `P_hard` but an ancestor of
**84.2%** of admissible atoms, and **33 of the 39** surviving level denominators
are ECE channels. Because C3, C5 and C7 exist only where a level denominator
survives, those three families are *more* ECE-concentrated than the basis is.
This is a property of which signals are strictly positive and smooth, not an
admissibility defect, and it must be handled by search policy.

`ADMISSIBLE ≠ PRIORITIZED`.

## 17. Access audit

20 development discharges, 70 predictor signals each, three nested calibration
blocks. 0 target values, 0 external values, 0 models, 0 baselines, 0
correlations, no ranking, no search. `H0_RAW_HARDENED` frozen and **not run**;
B2 unchanged and **not run**; neither used in admissibility.

## 18–19. Files and reproduction

5 Markdown, 11 CSV, 8 JSON, 3 scripts, 9 manifest records — 34 artifacts hashed
in `S7_6R_FREEZE.json` (the freeze and the acceptance file are self-referentially
excluded).

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\06_admissible_universe\hardened_v2\scripts"
& $P $S\s7_6r_a_preflight.py   # metadata only; opens no archive
& $P $S\s7_6r_b_universe.py    # 20 development discharges, predictors only
& $P $S\s7_6r_c_freeze.py      # A_rec^H, predicates, acceptance, freeze
```

Deterministic; no seeds. Stage B aborts if the denominator rule hash changed.

## 20. Recommendation for S7.7

**`READY_WITH_QUALIFICATIONS`.**

The admissible universe is complete, auditable and frozen. Three points belong
to the next stage rather than to this one:

**First**, two of the nine families contribute nothing. That is settled and
should not be revisited by weakening the gate. If a shifted, bounded or
local-domain variant of a rate-denominator constructor is wanted, it is a
**different constructor** requiring its own prospective declaration — available
to S7.11 sensitivity study, not to the primary path.

**Second**, `Φ_dependency` currently binds nothing. It should stay in the
predicate set: it is correct, it costs nothing, and a different cohort or
calibration geometry would make it bind.

**Third**, the multiplicity problem S7.5H could not solve has become *sharper*,
not milder, in the atomic universe — 84.2% ECE ancestry against 47.1% of the
basis. S7.7 must control exploration by scientific family, and that policy has
to be frozen prospectively, before any coordinate is scored.
