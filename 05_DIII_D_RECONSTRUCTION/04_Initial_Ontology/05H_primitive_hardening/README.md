# S7.5H — Primitive-space and ontology hardening

**Freeze:** `D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1`
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance **48/48**
**New primary ontology:** `G_REC_DENSITY_HARDENED_V2` v2.0.0

```
P_full 78  ->  P_hard 70  (P_deferred 8)
5 constructor families  ->  9  (C0-C8), max depth 1
13,604 symbolic coordinates  ->  23,861   (1.75x LARGER)
```

**Zero density values. Zero external values. No model, no baseline, no target
statistic.**

---

## Read this first — four qualifications

**1. S7.6 had already been run.** The stage premise says it has not started; it
has. `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1` exists (6 034 atoms, built on the
full 78-primitive ontology). It accessed **0 target values and 0 external
values**, so no contamination is possible. It is **preserved unmodified** and
marked `SUPERSEDED_FOR_PRIMARY_SEARCH_PENDING_RERUN_ON_HARDENED_ONTOLOGY`.
→ `EXTENDED_ONTOLOGY_STATUS.md`

**2. Instrumentation-density bias was not materially reduced.** The ECE share of
the primitive basis falls only **51.3% → 47.1%**. Only 9 of 828 within-group
pairs met the frozen redundancy criterion. The primitive-space component of this
hardening is close to a null result.

**3. The effective-rank audit disagrees strongly.** ECE needs ~3 components for
95% of variance, against **33** retained channels. Recorded, **not acted on** —
thresholds were not tuned. The binding threshold is `R_10 ≥ 0.97`: 40 ECE pairs
reach `R_med ≥ 0.99` but 32 of those fail `R_10`.

**4. The ontology got bigger, not smaller.** Removing 8 primitives cut the
original five families to 10 941; adding four pairwise families brought the
total to 23 861. C6/C7/C8 alone contribute 12 852.

## What was deferred

8 channels, each on a **direct** witness (no transitive removal):

`fs04da`→`fs04` · `ece17`→`ece16` · `ece23`→`ece22` · `ece24`→`ece25` ·
`ece26`→`ece25` · `ece32`→`ece31` · `ece34`→`ece33` · `ece40`→`ece39`

All ECE pairs are channel-adjacent. **Neither CER group yielded a single
redundant pair** — all 14 chords retained.

> `fs04` and `fs04da` correlate at **|r| = 1.000000 in all 60 cells** — not the
> behaviour of two distinct viewing chords. Flagged as a **provenance item for
> follow-up**; not asserted as identity, and it changed nothing.

`REDUNDANCY_DEFERRED` ≠ `SCIENTIFICALLY_INADMISSIBLE` ≠ `TARGET_IRRELEVANT`.
All 8 remain in the preserved extended ontology.

## The nine families

| | Family | Count | | | Family | Count |
|---|---|---|---|---|---|---|
| C0 | level | 70 | | C5 | reciprocal `1/x_i` | 68 |
| C1 | derivative | 63 | | C6 | level·rate `x_i ẋ_j` | 4 284 |
| C2 | product | 2 346 | | C7 | rate/level `ẋ_i/x_j` | 4 284 |
| C3 | ratio | 4 556 | | C8 | level/rate `x_i/ẋ_j` | 4 284 |
| C4 | phase derivative | 3 906 | | | **total** | **23 861** |

C6–C8 fill the **level–rate** gap the original grammar left empty. They are
**depth 1** — primitive-pair constructors with an internal rate operator, not
consumers of C1 objects.

## Start here

| File | What it is |
|---|---|
| `S7_5H_PRIMITIVE_SPACE_AND_ONTOLOGY_HARDENING_FINAL.md` | manuscript-ready prose |
| `S7_5H_HARDENING_AUDIT_REPORT.md` | the full internal audit |
| `PRIMARY_PRIMITIVE_BASIS.md` | what was deferred and why, with the rank disagreement |
| `HARDENED_CONSTRUCTOR_CATALOG.md` | the nine families, typing and domains |
| `EXTENDED_ONTOLOGY_STATUS.md` | preserved full ontology + the S7.6 conflict |

## Machine-readable

```
HARDENING_POLICY_PREVALUE.json        frozen BEFORE any value was read
G_REC_HARDENED.json                   the new primary ontology
constructor_catalog_hardened.json     Lambda_rec^H, C0-C8
constructor_type_rules_hardened.json  typing, domains, propagation
coordinate_signature_schema_hardened.json
excluded_constructor_families_hardened.json
ontology_combinatorial_audit.json     counts, bias audit, rank disagreement
hardened_raw_ablation.json            H0_RAW_HARDENED, frozen not run
redundancy_eligible_groups.csv        4 eligible, 4 ineligible with reasons
pairwise_redundancy_audit.csv         828 pairs
redundancy_representatives.csv
primitive_basis_full.csv / _hardened.csv / _deferred.csv
effective_rank_audit.csv              AUDIT ONLY, never selection
family_composition_audit.csv
S7_5H_ACCEPTANCE_CHECKS.json          48 checks
S7_5H_FREEZE.json

manifests/PARENT_FREEZE_VERIFICATION.json   incl. the S7.6 conflict record
manifests/POLICY_FREEZE.json                policy hash + ordering proof
manifests/ACCESS_AUDIT.json
manifests/DATA_ACCESS_LOG.csv
manifests/REDUNDANCY_SUMMARY.json
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\05H_primitive_space_and_ontology_hardening\scripts"
& $P $S\s7_5h_a_policy.py      # metadata only; opens no archive
& $P $S\s7_5h_b_redundancy.py  # 20 development discharges, predictors only
& $P $S\s7_5h_c_ontology.py    # hardened ontology, audit, freeze
```

Deterministic; no seeds. Stage B aborts if the policy hash changed after freeze.

## Stage gate

No `A_rec` enumeration · no search · no search priority · no model · no
baseline · no target correlation · no density value · no external value · B2
unchanged · support bound 1–12 unchanged · `T_REC_V1` unchanged ·
`FD2_PHYSICAL_TIME_V1` unchanged · **S7.6 not re-run in this stage; S7.7 not
started.**
