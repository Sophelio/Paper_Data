# S7.6 — Admissible universe: internal audit

**Freeze:** `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1`
**Status:** `FROZEN_READY_FOR_S7.7` · acceptance **40/40** · 2026-09-04

---

## 1. Executive verdict

The grammar was instantiated mechanically to exactly **13 604** symbolic primary
coordinates, matching the S7.5 combinatorial prediction before any value was
read. After the frozen admissibility classes, **6 034 atomic coordinates**
survive.

```
C0   78 ->  74      C1   70 ->  66      C2 2926 -> 2628
C3 5700 -> 3266     C4 4830 ->    0     total 13604 -> 6034
```

**`A_rec` is represented factorially** — the subset count for sizes 1–12 is a
37-digit integer and was not materialized.

Two results need stating plainly and without interpretation:

- **The entire C4 family is inadmissible.** No time-derivative denominator
  survives the frozen domain rule. This is an instance-level domain fact, not a
  search result — nothing was fitted and no coordinate was compared to the
  target.
- **All 197 exact dependency groups are vacuous**, because four of the eight
  beam components are numerically inadmissible. The constraint is well-defined
  and remains active; it simply has no binding instance on this object.

**Zero target values, zero external values.**

## 2. Parent verification — `PARENTS_VERIFIED`, 0 drift

All eight lineage freezes verify. Substantive checks pass: target `density`; 78
predictors; ontology `G_REC_DENSITY_V1`; constructor counts 78/70/2926/5700/4830;
symbolic total 13 604; support bound 1–12; external cohort 42 and sealed; S7.6
never previously run.

## 3. Pre-flight contract completion

The denominator margin was frozen and hashed **before stage B opened any
coordinate value** — `PRE_ENUMERATION_CONTRACT_COMPLETION`, explicitly not an
empirical correction.

```
DENOMINATOR_MARGIN_PRIMARY = 0.05
scale(d) = RMS(d)          eta(d) = min(|d|)/RMS(d)
admissible iff finite AND no sign change AND eta >= 0.05, on every required block
sensitivity-only (S7.11): eta = 0.01, 0.10 — may not replace the primary result
```

Stage A opens no archive at all, so the ordering is structural rather than a
matter of discipline.

## 4. Inherited documentation clarifications

Both `DOCUMENTARY_ERRATUM_ONLY`; S7.5 not reopened. Full treatment in
`S7_5_INHERITED_DOCUMENTATION_ERRATA.md`.

**E-1 B2 nesting.** The raw *representation family* is nested in `G_rec`; the
frozen B2 *model* is not an `A_rec` member, because it uses potentially all 78
primitives against an `m ≤ 12` bound. Verified that no executable artifact
references B2. **B2 was not modified and not restricted to 12** — weakening the
comparator to rescue a slogan would defeat its purpose.

**E-2 "eight cannot enter derived coordinates."** Only the 2 uncalibrated
primitives are barred from all derived families; the 6 upstream-upsampled ones
remain eligible for products and ratios. The machine-readable operand counts
were already correct (78/70/76/76/70), and the instantiated registry reproduces
2 926 and 5 700 — which it could not have done under the erroneous reading.

## 5. Symbolic enumeration check

`{C0: 78, C1: 70, C2: 2926, C3: 5700, C4: 4830}`, total **13 604** — asserted
against the S7.5 bounds before any data gate. 6 sensitivity-only derivatives
instantiated separately and never mixed into the primary universe.

## 6. Metadata admissibility (B/A/C/G/F)

**0 rejections** across all 13 604. The instantiation faithfully reproduces the
ontology's own eligibility rules, which is the expected and desired outcome —
any rejection here would have indicated a defect in either the grammar or the
instantiation, and none appeared.

## 7. Numerical-support audit (class D)

Development predictor values only, calibration intervals only, all 60 required
blocks. Minimum calibration length **130 samples** against a floor of 30.

Constancy tested **exactly** (`min == max`), with no tuned variance threshold.

**490 class-D rejections.** Four primitives are constant on at least one
required calibration interval:

```
pinj_15r, pinj_21l, pinj_21r, pinj_33l
```

`pinj_21l` and `pinj_21r` never fired anywhere in the cohort (an S7.1 finding);
the other two are constant on at least one required interval. Their levels (4),
derivatives (4), products (298) and ratios (184) follow.

Products were **not** pruned for magnitude. Large-but-finite values are the
legitimate consequence of multiplying quantities in different units.

## 8. Ratio denominator audit (class E)

**46 of 76** level denominators pass: all 40 ECE channels, `cerqtit3/10/11`,
`bt`, `ip`, `prmtan_neped`.

| Failure | n denominators |
|---|---|
| sign change | 18 |
| `eta < 0.05` | 5 |
| exact zero value (`eta = 0`) | 4 |
| `RMS = 0` | 2 |
| **failing total** | **30** |

Physically legible throughout: rotation reverses, filterscope and gas signals
cross zero between events, beams switch off.

**C3: 3 266 of 5 700 admissible.** Class E removed 2 250; class D removed a
further 184 constructed ratios.

## 9. Phase denominator audit (class E)

**0 of 70** derivative denominators pass. **97.7%** of the 4 200 checks fail by
sign change; the rest by `RMS = 0`.

```
C4: 0 of 4 830 admissible
```

A time derivative changes sign at every local extremum of its source, and over a
calibration interval spanning 40–80% of a discharge essentially every plasma
quantity rises and falls at least once.

**No reaction was taken**, as §13 requires. The constructor remains in `G_rec`;
what `A_rec` records is that no instance satisfies the frozen instance-level
domain requirement on this object. This is the ontology / admissible-universe
distinction working exactly as intended, and it carries no information about
predictive value — nothing was fitted.

Any rescue (shifted, bounded, sensitivity-centered phase derivative) is a
*different construction*, already `PRIMARY_ONTOLOGY_EXCLUDES` at S7.5.

## 10. Rejection census

| Class | n | Reasons |
|---|---|---|
| **E** | 7 080 | sign change 6 042 · margin 450 · zero value 300 · RMS zero 288 |
| **D** | 490 | constant on a required calibration block |
| B/A/C/G/F/H | 0 | — |
| **total** | **7 570** | |

Every rejection carries a frozen reason and the first rejecting class.
`74 + 66 + 2628 + 3266 = 6 034` pass; `6 034 + 7 570 = 13 604` — the census is
complete.

## 11. Atomic coordinate universe

**`C_rec^atom` = 6 034**, in `primary_atomic_coordinate_universe.csv` with full
lineage, dimensions, unit expressions, temporal bounds, flags and domain
predicates per row.

## 12–13. Exact dependency groups and set constraints

**197 attempted · 0 binding · 197 vacuous.**

Contexts: level 1, derivative 1, product 67, ratio 67, phase 61. No identity
claimed for `RATIO(z,pinj)` or `PHASE(z|pinj)` — with the aggregate in the
denominator none exists, and asserting one would be a mathematical error.

All vacuous because `ID(pinj_15r)`, `ID(pinj_21l)`, `ID(pinj_21r)`,
`ID(pinj_33l)` are inadmissible, so no admissible support can contain a complete
nine-member group. Recorded with reasons in
`exact_dependency_groups_attempted.csv` rather than reported as a bare zero.

`Φ_set` freezes six predicates (size, no duplicates, atoms only, no
sensitivity-only, `Φ_dependency`, no target) and **explicitly imposes no search
preference**.

## 14–15. Formal `A_rec` and combinatorial scale

```
A_rec = { (C,R) : C ⊆ C_rec^atom, 1 ≤ |C| ≤ 12, Φ_set(C)=1, R ∈ R_rec(C) }
R_rec(C) = T_REC_V1 for every C
```

Unconstrained subset count for sizes 1–12: a **37-digit** integer.
**Not materialized** — and this is not a failure to instantiate `A_rec`. The
atoms plus predicates are a complete, exact, finite representation; membership
is decidable directly.

## 16. External partial-map rule

Frozen prospectively without opening any external value: same rule (finite, no
sign change, `eta ≥ 0.05`); on failure, no shift, no regularisation, no
replacement, no refit — record `NOT_APPLICABLE` for that discharge/block and let
qualification decide whether `Omega_rec` survives.

## 17. Access audit

```
development shots read      20  (exactly the frozen list)
predictor signals per shot  78
target values accessed       0
external values accessed     0
```

`FIREWALL_INTACT`. The target was never loaded — `density` is absent from the
78-primitive list by construction.

## 18. Files produced

6 Markdown, 9 CSV, 6 JSON, 3 scripts — all hashed in `S7_6_FREEZE.json`.

## 19. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\06_admissible_universe\scripts"
& $P $S\s7_6_a_preflight.py    # metadata only; freezes the denominator rule
& $P $S\s7_6_b_universe.py     # development predictor values only
& $P $S\s7_6_c_freeze.py       # acceptance and freeze
```

Deterministic; no seeds. Stage A exits non-zero on parent drift or a baseline
semantics conflict; stage B exits non-zero on any firewall breach and asserts
the symbolic counts before applying any data gate.

## 20. Recommendation for S7.7

**`READY_FOR_S7.7`.**

S7.7 inherits: 6 034 atoms across four surviving constructor families; the six
`Φ_set` predicates; 197 recorded dependency groups (currently vacuous but
active); the frozen external partial-map rule; and `T_REC_V1` with the estimator
still deferred.

Two facts S7.7 should carry into its search-policy design. First, **C4 is
empty**, so any search policy that assumed trajectory-relational coordinates
would be available must be written against what actually exists. Second, the
surviving universe is heavily weighted toward ratios (3 266) and products
(2 628) over levels (74) and derivatives (66) — relevant to how a frontier is
budgeted, though **no priority is assigned here**.

**S7.7 is not authorised by this document.**
