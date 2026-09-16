# S7.6 — Admissible universe `A_rec`

**Freeze:** `D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1`
**Status:** `FROZEN_READY_FOR_S7.7` · acceptance **40/40**
**Universe:** `A_REC_DENSITY_V1`

```
13,604 symbolic primary coordinates  ->  6,034 admissible atoms

C0   78 ->   74      C1   70 ->   66      C2 2926 -> 2628
C3 5700 -> 3266      C4 4830 ->    0
```

`A_rec = { (C,R) : C ⊆ C_rec^atom, 1 ≤ |C| ≤ 12, Φ_set(C)=1, R ∈ T_REC_V1 }`

**Represented factorially.** The subset count for sizes 1–12 is a **37-digit**
integer and was not materialized — the atoms plus set predicates are a complete,
exact, finite representation.

## Two results to read carefully

**The entire C4 family is inadmissible — 0 of 4 830.** No time-derivative
denominator survives the frozen domain rule; 97.7% fail by sign change, because
`dx/dt` crosses zero at every local extremum and every plasma quantity rises and
falls within a calibration interval.

> This is an **instance-level domain fact**, not a search result. Nothing was
> fitted; no coordinate was compared with the target. The constructor remains in
> `G_rec` — what `A_rec` records is that no *instance* satisfies the task's
> frozen domain requirement on this object. That is precisely the
> ontology / admissible-universe distinction.

**All 197 exact dependency groups are vacuous**, because four of the eight beam
components are numerically inadmissible (`pinj_21l` and `pinj_21r` never fired
anywhere in the cohort). `Φ_dependency` is well-defined and stays active; it has
no binding instance here.

## Start here

| File | What it is |
|---|---|
| `S7_6_ADMISSIBLE_UNIVERSE_FINAL.md` | manuscript-ready prose |
| `S7_6_ADMISSIBLE_UNIVERSE_AUDIT_REPORT.md` | the full internal audit |
| `PARTIAL_MAP_ADMISSIBILITY.md` | the denominator rule and what it removed |
| `REPRESENTATION_SET_CONSTRAINTS.md` | `Φ_set`, dependency groups, factorized `A_rec` |
| `S7_5_INHERITED_DOCUMENTATION_ERRATA.md` | two S7.5 prose corrections |

## The denominator rule — frozen before any value was read

```
eta(d) = min(|d|) / RMS(d)   on each calibration block
admissible iff  finite  AND  no sign change  AND  eta >= 0.05
```

Hashed in stage A, which opens no archive at all. No shifts, epsilons, clipping
or bounded reciprocals — those are *different constructions*. Sensitivity values
`0.01` / `0.10` predeclared for S7.11 only.

**46 of 76** ratio denominators pass · **0 of 70** derivative denominators pass.

## Rejection census

| Class | n | Reasons |
|---|---|---|
| **E** denominator | 7 080 | sign change 6 042 · margin 450 · zero value 300 · RMS zero 288 |
| **D** numerical support | 490 | constant on a required calibration block |
| B/A/C/G/F/H | 0 | — |

`6 034 pass + 7 570 reject = 13 604`. Every rejection carries a frozen reason.

## Access

```
development shots read     20      target values accessed   0
predictor signals          78      external values accessed 0
```

`FIREWALL_INTACT`. The target is absent from the 78-primitive list by
construction, so `density` was never loaded.

## Machine-readable

```
A_REC.json                              the universe, factorized
atomic_coordinate_universe.json         C_rec^atom summary
representation_set_constraints.json     the six Phi_set predicates
denominator_admissibility_rule.json     frozen BEFORE stage B
coordinate_registry_all.csv             13,604 symbolic instances
coordinate_admissibility.csv            per-coordinate class results
primary_atomic_coordinate_universe.csv  the 6,034 survivors
coordinate_rejection_log.csv            7,570 rejections with reasons
denominator_conditioning_audit.csv      every (denominator, shot, block) check
numerical_support_audit.csv             per-primitive class-D stats
exact_dependency_groups.csv             binding groups (0)
exact_dependency_groups_attempted.csv   all 197, with vacuity reasons
sensitivity_only_coordinate_registry.csv  the 6, kept out of primary A_rec
S7_6_ACCEPTANCE_CHECKS.json             40 checks
S7_6_FREEZE.json                        freeze record and all artifact hashes

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/PREFLIGHT_CHECKS.json
manifests/ACCESS_AUDIT.json
manifests/DATA_ACCESS_LOG.csv
manifests/UNIVERSE_SUMMARY.json
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\06_admissible_universe\scripts"
& $P $S\s7_6_a_preflight.py
& $P $S\s7_6_b_universe.py
& $P $S\s7_6_c_freeze.py
```

Deterministic; no seeds. Stage B asserts the symbolic counts before applying any
data gate and exits non-zero on any firewall breach.

## Stage gate

No search · no search priority · no `Ahat_rec` · no estimator · no
predictor-target correlation · no reconstruction performance · no target values ·
no external values · support bound unchanged at 1–12 · relation unchanged at
`T_REC_V1` · **S7.7 not started.**
