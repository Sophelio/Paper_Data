# S7.3 — Target feasibility and information-boundary selection

**Freeze:** `D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-V1`
**Status:** `FROZEN_READY_FOR_S7.4` · acceptance **35/35**
**Parents:** S7.1 final · S7.2 V1 · **S7.2 V2 (authoritative)** — all verified, 0 drift

```
y* = vsurf   (surface loop voltage, V, DIRECT_MEASUREMENT, 20.0 ms native)

95 quantities  ->  79 admissible primitive explanatory quantities  ->  7 families
primary analysis cadence: 20.0 ms
```

**First stage to open signal values — 20 development discharges only, 0 external.**
No model, no baseline, no correlation, no coordinate.

## Start here

| File | What it is |
|---|---|
| `S7_3_TARGET_FEASIBILITY_FINAL.md` | manuscript-ready prose |
| `S7_3_TARGET_FEASIBILITY_AUDIT_REPORT.md` | the full internal audit |
| `SELECTED_TARGET.md` | the target and why it won |
| `INFORMATION_BOUNDARY_FINAL.md` | what survived `I_rec` and what left |
| `TARGET_SELECTION_AUDIT.md` | 95 → 64 → 62 → 1, with the ranking table |

## Selection in one line

`vsurf` and `density` tied on flags (0), predictors (79) and families (7);
**Level 4** (variation margin, 0.1297 vs 0.0483) resolved it.

Notably `fs05da` has the largest margin of all (0.4140) and ranks **third** — as
a filterscope target it loses 3 siblings, giving 76 predictors across 6 families.
Level 2 outranks Level 4, so breadth of surviving information beats target
variability. A weighted score would have chosen differently, which is why the
contract forbids one.

## Machine-readable

```
TARGET_SELECTION_RESULT.json    the selection, its keys and resolution level
I_REC_SELECTED.json             rules applied and the exclusion census
O_REC_SELECTED.json             the 79 primitives, families, cadence
S7_3_ACCEPTANCE_CHECKS.json     35 checks
S7_3_FREEZE.json                freeze record and all artifact hashes

candidate_target_census.csv          95 rows: class pass/fail + flags
target_flag_mapping.csv              95 rows: U001/U003/U004/U009/U010
target_boundary_summary.csv          64 rows: per-candidate I_rec
target_feasibility_metrics.csv       64 rows: development-only statistics
target_eligibility_matrix.csv        64 rows: all 12 criteria
target_ranking.csv                   62 rows: lexicographic keys + resolution level
selected_target_boundary.csv         95 rows: full boundary for vsurf
selected_target_exclusions.csv       16 rows: every removal with evidence
selected_target_sibling_sensitivity.csv   NOT_APPLICABLE for vsurf
development_rrv_per_shot.csv         all 20 per-discharge RRV values
development_nrmse_scale_audit.csv    every block scale, 64 x 20 x 3
algebraic_duplicate_audit.csv        criterion 9 evidence
target_unit_canonicalization.csv     archived -> canonical unit per candidate

manifests/PARENT_FREEZE_VERIFICATION.json
manifests/CONTRACT_NOTATION_AUDIT.json        section 4 sanity check
manifests/TARGET_FLAG_MAPPING_FREEZE.json     frozen BEFORE values opened
manifests/SIBLING_SUBFAMILY_RULE.json         scientific, not provider group
manifests/SIBLING_AMBIGUITY_SENSITIVITY.json  tested; immaterial
manifests/SELECTED_TARGET_SANITY_AUDIT.json
manifests/DATA_ACCESS_LOG.csv                 every archive read
manifests/EXTERNAL_FIREWALL_AUDIT.json        20 dev / 0 external
```

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\03_target_feasibility_and_boundary\scripts"
& $P $S\s7_3_a_metadata.py      # metadata only; opens no archive
& $P $S\s7_3_b_feasibility.py   # development values only
& $P $S\s7_3_c_select.py        # ranking, selection, boundary, freeze
```

Deterministic; no seeds. Stage A exits non-zero on parent drift; stage B exits
non-zero on any external read.

## Stage gate

`O_rec = I_rec(O)` contains **primitives only**. No product, ratio, derivative,
phase derivative, symbolic term, `G_rec`, `A_rec` or search exists. No external
value has been opened. **S7.4 not started.**
