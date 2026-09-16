# S7.7 — Frozen search policy and explored frontier

**Freeze:** `D3D-SIR-S7.7-FROZEN-SEARCH-POLICY-AND-EXPLORED-FRONTIER-V1`
**Status:** `BLOCKED_SEARCH_BUDGET`

```
Sigma_rec   FROZEN_PREVALUE_COMPLETE_BUT_NOT_EXECUTED   sha a97e690e...
Ahat_rec    NOT_CONSTRUCTED                             cardinality 0
```

**0 archives opened · 0 density values · 0 external values · 0 atoms scored ·
0 baselines run.**

---

## Why it stopped

§16 requires the projected candidate support evaluations to be computed from
metadata **before** any target value is opened, and an unconditional STOP if the
projection exceeds `MAX_SUPPORT_EVALUATIONS = 300,000`.

```
atomic scoring                                    10,778
main lane     252 seeds x 11 steps x 127 strata = 352,044
raw-only lane  14 seeds x 11 steps x   7 strata =   1,078
                                                  -------
maximum projected                                 363,900   overrun  63,900
strict lower bound                                346,484   overrun  46,484
```

**Even the strict lower bound overruns**, so this is not an artifact of a loose
projection — no execution of this policy can come in under 300,000.

The policy was **not** truncated, **not** adjusted, and no coordinate was
pruned. §16 exists to force this decision into the open, prospectively, in front
of a human. → `SEARCH_BUDGET_BLOCK.md`

## The decision you own

| option | max projected | fits 300 000 | what it costs |
|---|---|---|---|
| **`SEEDS_PER_STRATUM = 1`** | **188,736** | **yes** | every stratum still starts a path, but no second independent start |
| raise `MAX_SUPPORT_EVALUATIONS` ≥ 363,900 | 363,900 | redefines the gate | nothing in search semantics; purely a larger allowance |

Either must be re-frozen **prospectively**, with a new policy hash, before any
density value is opened. Amending after target outcomes would make the stage
`SEARCH_POLICY_CONTAMINATED`.

Lowering the 96-atom cap does **not** help: proposals per step scale with the
number of **strata** in the shortlist, not the number of atoms.

## What is finished and does not need redoing

- **11 parent freezes verified, 0 drift.** `A_REC_DENSITY_HARDENED_V2`
  authoritative, 10,778 atoms, C4 = 0, C8 = 0, support 1–12, denominator rule
  and `T_REC_V1` unchanged, external cohort 42 sealed.
- **Pre-search contract completed and hashed** (`1b8df4c0…`) before any target
  access: `S_PERS_V1` persistence skill (required reporting, no epsilon at zero
  denominator, does not change V3) and `B1A_AR1` (diagnostic, calibration-fitted,
  no teacher forcing). **Neither run.**
- **All 10,778 atoms stratified** into **127** search strata, exactly one each.
- **The complete §§5–15 policy** written and hashed.
- **§13 cap-sufficiency gate PASSED** — 96 ≥ 35, the largest per-constructor
  stratum count.
- **Opportunity-side multiplicity audit computed** — and the policy works.

## Multiplicity control works, measurably, before any value is read

| family | primitives | atom ancestry | projected seed share |
|---|---|---|---|
| **ECE** | 33 | **0.842** | **0.310** |
| CER | 14 | 0.347 | 0.310 |
| NBI | 10 | 0.144 | 0.222 |
| gas | 4 | 0.097 | 0.222 |
| magnetics | 4 | 0.071 | 0.310 |
| filterscope | 3 | 0.045 | 0.135 |
| density-aux | 2 | 0.041 | 0.222 |

ECE's share of initial search opportunity falls from **84.2%** of atomic
ancestry to **31.0%** of projected seeds. The §22 criterion — initial
opportunity not proportional to raw atomic multiplicity — is met by
construction. → `MULTIPLICITY_CONTROL_POLICY.md`

Whether ECE still dominates *after* equalized opportunity is **unknown**: that
is answered by retained paths, and no path was run.

## Start here

| File | What it is |
|---|---|
| `SEARCH_BUDGET_BLOCK.md` | the block, the arithmetic, and the remedies (computed, not chosen) |
| `MULTIPLICITY_CONTROL_POLICY.md` | how search opportunity was to be allocated, and what it achieves |
| `S7_7_SEARCH_POLICY_AND_FRONTIER_AUDIT_REPORT.md` | the full internal audit, 20 sections |

`S7_7_SEARCH_POLICY_AND_FRONTIER_FINAL.md` is **deliberately absent**. The §25
manuscript section is built around the explored frontier; there is no explored
frontier, and writing it would describe exploration that did not happen. It is
the first thing to produce on re-run.

## Machine-readable

```
PRE_SEARCH_CONTRACT_COMPLETION.json    S_PERS_V1 + B1A_AR1, hashed pre-target
SEARCH_POLICY_PREVALUE.json            the complete sections 5-15 policy
search_budget_block.json               the block, arithmetic, remedies, non-levers
search_strata.csv                      127 active strata
atom_stratum_assignment.csv            all 10,778 atoms, exactly one stratum each
multiplicity_opportunity_audit.csv/.json
constructor_opportunity_audit.csv
S7_7_ACCEPTANCE_CHECKS.json            34 reached, 6 NOT REACHED
S7_7_FREEZE.json

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/PRE_SEARCH_CONTRACT_FREEZE.json
manifests/POLICY_FREEZE.json
manifests/SEARCH_BUDGET_PREFLIGHT.json
```

The six not-reached acceptance items — atomic scoring, shortlist instantiation,
seed instantiation, raw-only lane, `Ahat_rec` registration, unsearched labelling
— are recorded as **NOT REACHED**, never as passed.

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\07_search_policy_and_frontier\scripts"
& $P $S\s7_7_a_precontract.py            # parents + S_pers + AR(1)
& $P $S\s7_7_b_policy_and_preflight.py   # strata + policy + budget preflight
& $P $S\s7_7_c_block_and_freeze.py       # block record, audits, freeze
```

None of the three opens an archive.

## Stage gate

No density value · no external value · no atom scored · no baseline (B0, B1,
B1A_AR1, B2, B3, `H0_RAW_HARDENED`) · no `C*`, `R*` or `Q_rec*` · no validation
claim · C4 not rescued · C8 not rescued · no shifted or bounded constructors ·
no `q_desc` seeding · no retired `q_rec` seeding · `A_rec`, `G_rec`, target,
`P_hard`, C0–C8, denominator rule, support bound and `T_REC_V1` all unchanged ·
**S7.8 not started.**
