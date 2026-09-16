# S7.9 — Development selection and pre-external freeze

Freeze **`D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1`**
Status **`FROZEN_WITH_QUALIFICATIONS`** · 54/54 acceptance · `FIREWALL_INTACT`
Parent `D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1`

---

## What this stage did

Executed the frozen `U_rec` over the frozen frontier, selected **one**
development representation deterministically, locked and hashed it, froze all
six comparator configurations without running them, and wrote the immutable
pre-external package.

## What it did not do

Opened **zero** external predictor values, **zero** external target values, made
**zero** external model evaluations. Ran no baseline. Altered nothing frozen
upstream. Did not begin S7.10.

## The reduction

| Set | Count | Criterion | Bound |
|---|---|---|---|
| `E0` | 162 845 | explored frontier | — |
| `E1` | 1 055 | primary fit quality | yes |
| `E2` | **1** | development generalization / stability | **decisive** |
| `E3` | 1 | parsimony | no |
| `E4` | 1 | conditioning | no |
| `E5` | 1 | support stability | no |

## `C_dev_star`

```
ID(cerqtit6)|ID(pcdiamag3)|ID(prmtan_neped)|PROD(ece37,ece39)|PROD(gasa,gasa)|
PROD(pinj,cerqrott6)|PROD(prmtan_neped,prmtan_neped)|RATIO(ece21,prmtan_neped)|
RATIO(fs03da,prmtan_neped)|RATIO(ip,ece22)|RECIP(cerqtit10)|RECIP(prmtan_neped)
```

Size 12 · C0×3, C2×4, C3×3, C5×2 · seven scientific families · no C6/C7 ·
ECE ancestry present · contains the uncalibrated `pcdiamag3`.

`FIT` 0.166398 · `BLOCK_WORST` 0.194252 (`b_star` = A) · `SHOT_P90` 0.211412 ·
`ACTIVE_TERMS` 12/12 · `COND_MEDIAN` 1.9918 · `BOOT_SELECTION_FREQ` **0.093** ·
`FOLD_SELECTION_FREQ` 0.333.

**Development-selected. Not externally validated, not a structural-transfer
success, not a global optimum.**

## Three things a reader should know

**1. Rank 2 decided it, not Rank 1.** `C_dev_star` is *not* the best-fitting
support. It sits 0.000116 above `FIT_best` — inside the frozen
practical-equivalence set — and won on worst-block and per-discharge robustness.
That is the lexicographic utility working as designed.

**2. Support-level stability is low, and is reported as found.** 1 000
bootstrap replicates produced **217 distinct winners**; `C_dev_star` won 9.3 %
of them and 1 of 3 block omissions. The frozen policy attaches no threshold to
support stability, and `E4` was already a singleton, so Rank 5 was diagnostic
rather than selective. Nothing was rescued.

**3. Coordinate-level stability is much higher.** `ID(pcdiamag3)` appears in
**100 %** of the 217 winners; `RATIO(ip,ece22)` in 84 %,
`RATIO(fs03da,prmtan_neped)` in 75 %, `PROD(prmtan_neped,ece39)` in 74 %. Eight
coordinates recur in at least half. Twenty discharges identify the relational
*ingredients* far more reliably than any particular twelve-element combination.
Reporting only — no criterion, no threshold, nothing changed.

## Ordering that makes V2 and V5 meaningful

```
E0 -> E5  ->  LOCK (hashed)  ->  penalty rule (hashed)  ->  alphas  ->
baseline configs  ->  PRE_EXTERNAL_MODEL_FREEZE (hashed)  ->  [S7.10]
```

The lock precedes every baseline hyperparameter, so comparator behaviour cannot
have influenced which support was chosen. Verified programmatically.

## Start here

| Document | Purpose |
|---|---|
| `S7_9_DEVELOPMENT_SELECTION_AND_FREEZE_FINAL.md` | manuscript-ready section |
| `S7_9_DEVELOPMENT_SELECTION_AUDIT_REPORT.md` | full internal audit, 26 sections |
| `SELECTED_REPRESENTATION.md` | the twelve coordinates, units, flags |
| `BASELINE_CONFIGURATION_FREEZE.md` | six comparators, frozen not run |
| `PRE_EXTERNAL_FREEZE.md` | what S7.10 must verify first |

## Files

**Results (CSV)** — `utility_rank_1_fit`, `utility_rank_2_stability`,
`utility_rank_3_parsimony`, `utility_rank_4_conditioning`,
`utility_rank_5_support_stability`, `utility_survivor_sets`,
`utility_elimination_ledger` (162 844 rows), `bootstrap_selection_frequency`,
`bootstrap_coordinate_participation`, `fold_selection_frequency`,
`baseline_b2_alpha_tuning`, `baseline_h0_alpha_tuning`

**Frozen objects** — `SELECTED_REPRESENTATION.json`,
`RELATIONAL_ESTIMATOR_CONFIG.json`, `DEVELOPMENT_REPRESENTATION_LOCK.json`,
`BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json`, six `BASELINE_*_CONFIG.json`,
`BASELINE_CONFIGURATION_MANIFEST.json`, `PRE_EXTERNAL_MODEL_FREEZE.json`,
`S7_9_ACCEPTANCE_CHECKS.json`, `S7_9_FREEZE.json`

**Manifests** — parent verification, development access log, rank summaries,
parent baseline specification audit, V2 evidence, coordinate participation

## Reproduce

```bash
python scripts/s7_9_a_verify.py           # hard gates
python scripts/s7_9_b_ranks12.py          # Rank 1, Rank 2
python scripts/s7_9_d_rank345.py          # Rank 3, 4, 5 + bootstrap + folds
python scripts/s7_9_e_select_and_lock.py  # ledger, representation, LOCK
python scripts/s7_9_f_baselines.py        # baseline audit, completion, freeze
python scripts/s7_9_h_coord_stability.py  # coordinate participation (reporting)
python scripts/s7_9_g_freeze.py           # V2, pre-external, acceptance, freeze
```

Python 3.13.5 · numpy 2.5.2 · pandas 3.0.5 · scikit-learn 1.9.0 ·
Windows-11-10.0.26200-SP0. Bootstrap runtime 21 s; winner vector hashes to
`918166f2…`.

## Boundary

Selection occurred **within the frozen explored frontier only**.
`global_optimality_claim = false`. ~5.1 × 10³⁹ admissible combinations remain
`ADMISSIBLE_UNSEARCHED` with no negative finding.

**Next stage: S7.10 — external evaluation. NOT AUTHORISED.**
