# S7.3R — Source-supported temporal admissibility and target reconciliation

**Freeze:** `D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-SOURCE-RESOLUTION-V2`
**Status:** `FROZEN_READY_TO_RETRY_S7.4` · acceptance **31/31**
**Supersedes:** S7.3 V1 target selection · **Unblocks:** S7.4 V1

```
y* = density   (line-averaged electron density, m^-3 canonical)
95 quantities -> 78 admissible primitives -> 7 families
corrected cadence: 5.853 - 14.187 ms, discharge-specific, source-supported
```

## What changed, and what did not

**Changed:** one instantiation. S7.3 used **archived** cadence where the frozen
no-super-resolution policy requires **source-supported** cadence. Corrected
uniformly across all 95 signals and all 64 candidates.

**Not changed:** the ranking rule, every threshold, the class policy, the
validation minima, the block fractions, the 20/42 cohort, fail-closed
provenance, the sibling rule. No `PROVENANCE_RELAXED` branch, no EFIT recovery,
no accept-and-qualify exception.

## Outcome

| | S7.3 V1 | S7.3R V2 |
|---|---|---|
| target | `vsurf` | **`density`** |
| predictors | 79 | **78** |
| families | 7 | 7 |
| cadence | 20.0 ms flat | **5.85 – 14.19 ms**, per discharge |
| resolved at | Level 4 | **Level 2** |

**`vsurf` is the only quantity in the object that fails.** Across all 64
candidate boundaries there were 63 numerical-support removals and every one is
`vsurf`. It fails as a target too — at external discharge `165027` its
source-supported cadence is 82.909 ms, leaving every evaluation block below the
frozen minimum of 10 samples.

V1 status: `RETIRED_BY_SOURCE_RESOLUTION_RECONCILIATION`. Not a failed result —
no reconstruction was ever attempted. S7.3 V1 and S7.4 V1 preserved unmodified.

## Correction to a historical count: 16 → 22

The upstream-upsampled signal count was recomputed from primary metadata rather
than assumed. The old figure of 16 used a per-signal **median** ratio and could
not see signals upsampled in a minority of discharges. Under "upsampled in
**any** discharge" the count is **22** — adding `prmtan_neped`, `prmtan_teped`
and the four filterscopes.

## Start here

| File | What it is |
|---|---|
| `S7_3R_TEMPORAL_ADMISSIBILITY_FINAL.md` | manuscript-ready prose |
| `S7_3R_TEMPORAL_ADMISSIBILITY_AUDIT_REPORT.md` | the full internal audit |
| `CORRECTED_TARGET_SELECTION.md` | the corrected target and why it wins |
| `CORRECTED_INFORMATION_BOUNDARY.md` | the 78 survivors and the one removal |

## Machine-readable

```
TARGET_SELECTION_RESULT_V2.json    corrected selection, keys, vsurf status
I_REC_SELECTED_V2.json             rules applied, exclusion census
O_REC_SELECTED_V2.json             78 primitives, cadence, feasibility
S7_3R_ACCEPTANCE_CHECKS.json       31 checks
S7_3_FREEZE_V2.json                freeze record and all artifact hashes

source_supported_signal_cadence.csv     5890 rows: every signal x discharge
source_supported_signal_summary.csv     95 rows: per-signal cadence summary
numerical_admissibility_by_signal.csv   63 removals, each with its rule
candidate_grid_requirements.csv         per candidate x discharge grid + feasibility
corrected_target_boundary_summary.csv   64 candidates, old vs corrected counts
corrected_target_feasibility.csv        recomputed development statistics
corrected_target_eligibility_matrix.csv 13 criteria per candidate
corrected_target_ranking.csv            61 eligible, lexicographic keys
corrected_selected_target_boundary.csv  95 rows, full boundary for density
corrected_selected_target_exclusions.csv
corrected_development_nrmse_scale_audit.csv

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/UPSAMPLE_COUNT_CORRECTION.json
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\03_target_feasibility_and_boundary\reconciliation_source_resolution\scripts\s7_3r_reconcile.py
```

Deterministic; no seeds. Exits non-zero on parent drift or any external read.

## Access

**Zero external signal values.** Metadata for all 62 discharges (permitted by
the frozen firewall); signal values for the 20 development discharges only.

## Stage gate

No `X_rec` · no coordinates, products, ratios or derivatives · no `G_rec` · no
regression · no baseline · no predictor-target correlation · no external
outcome · cohort unchanged · **S7.4 not re-entered, S7.5 not started.**
