# S7 figure export

Minimal machine-readable inputs for the four-panel manuscript figure. Every file
here is a **verbatim copy** of a frozen artifact, except one clearly marked
derived matrix.

**Nothing was rerun, refitted or regenerated.** No source artifact was modified.
Every source sha256 is recorded in `EXPORT_MANIFEST.json`, and each copy was
hash-verified against its source at export time.

Rebuild with `python ../_audit/build_figure_export.py`.

---

## Panel 1 — `q_desc` discharge-specific coefficients

> **These sources are outside S7.** The descriptive branch's canonical artifacts
> live at `D:\sir-web\Paper Examples\Relational Coordinates for Multimodal Plasma
> Observations\`. S7 contains the `q_rec` lineage only — a known limitation of
> the package, recorded as finding F-3 in `../AUDIT_REPORT.md`.

| exported file | source | freeze / stage |
|---|---|---|
| `panel1_qdesc_discharge_coefficients.csv` | `canonical_d3d_62_shot_run_v1/d3d_discharge_coefficients.csv` | `D3D-SIR-62-ALIGNED-V1` |
| `panel1_qdesc_coefficient_classification.csv` | `Coefficient_conditioning/Correction_audit/tables/corrected_coefficient_classification.csv` | `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1` |
| `panel1_qdesc_coefficient_uncertainty.csv` | `Coefficient_conditioning/Correction_audit/tables/corrected_coefficient_heterogeneity_primary.csv` | `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1` |

**Coefficients** — 62 rows, one per discharge, in manuscript display order:
`coef_Dkappa_Wdia`, `coef_Dbetan_Wdia`, `coef_Dbetan_kappa`, `coef_Dbetan_li`,
`coef_q95_over_kappa`, `coef_dot_betan`, `coef_dot_kappa`, plus `intercept`,
`shot`, `fit_rank` and `fit_residual_sum_squares`.

**Classification** — the corrected audit verdict
`D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`:

| | coefficient | `corrected_status` |
|---|---|---|
| 1 | `dot kappa` | ROBUSTLY_RESOLVED |
| 2 | `D_betaN W_dia` | ROBUSTLY_RESOLVED |
| 3 | `D_betaN kappa` | ROBUSTLY_RESOLVED |
| 4 | `dot beta_N` | ROBUSTLY_RESOLVED |
| 5 | `D_betaN l_i` | ROBUSTLY_RESOLVED |
| 6 | `D_kappa W_dia` | WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES |
| 7 | `q95 / kappa` | WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES |

**Uncertainty** — for error bars use `tau2_REML` with
`tau2_REML_interval_low/high` (profile-likelihood), or
`tau2_bootstrap_q025/q975`. `observed_between_variance` and
`mean_within_variance` give the ratio the classification rests on.

Two things the panel must not imply: these are **not** dimensional physical
constants, and the analysis is **conditional on the selected support**.

Also available at the source but not exported, since it is a different analysis:
`tables/d3d_multivariate_eigenvalue_intervals.csv` (5 positive eigenvalues, 2
robust directions).

## Panel 2 — `q_rec` six-fold support membership

All from `../E2_1_crossfitted_discovery_and_qualification/`, freeze
`D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1`.

| exported file | source | role |
|---|---|---|
| `panel2_fold_0..5_result.json` | `folds/fold_k_result.json` | **primary frozen** |
| `panel2_fold_support_matrix.csv` | derived from the six JSON files | **derived by this export** |
| `panel2_coordinate_recurrence.csv` | `coordinate_recurrence.csv` | frozen reporting |
| `panel2_support_pairwise_jaccard.csv` | `support_recurrence.csv` | frozen reporting |
| `panel2_constructor_recurrence.csv` | `constructor_recurrence.csv` | frozen reporting |

`panel2_fold_support_matrix.csv` is the **6 × 35 binary matrix**: first column
`fold` (0–5), then 35 columns named by coordinate id, 1 where that fold's support
contains it. It is the only transformed file here — a one-hot expansion of the
six `coordinates` lists over their sorted union. No numerical value is altered.

> ### Parsing hazard — read this before using `support_id`
>
> Coordinate ids in the C4/C6/C7/C8 constructor families embed a pipe **inside
> parentheses**, for example `LEVEL_RATE(cerqrott12|ece35)` and
> `RATE_OVER_LEVEL(ip|ece39)`. Splitting a pipe-joined `support_id` on `|`
> therefore corrupts three of the six supports (sizes become 12, 12, 12, **14**,
> **13**, **13**).
>
> This export avoids the issue entirely: the per-fold JSON `coordinates` field is
> already a list, and the matrix is already expanded. If you must parse a
> `support_id`, split only at parenthesis depth zero.

Verified on export: six supports, all size 12, **none identical**, 35 distinct
coordinates, mean pairwise Jaccard **0.285244**, and `ID(pcdiamag3)` and
`RATIO(ece21,cerqtit10)` in all six.

## Panel 3 — `q_rec` out-of-fold reconstruction

All from the same E2.1 freeze.

| exported file | source | role |
|---|---|---|
| `panel3_heldout_discharge_results.csv` | `heldout_discharge_results.csv` | **primary frozen** |
| `panel3_method_summaries.csv` | `baseline_results.csv` | frozen reporting |
| `panel3_crossfitted_metrics.json` | `E2_1_CROSSFITTED_METRICS.json` | frozen reporting |

62 rows, one per out-of-fold discharge: `fold`, `shot_id`, `era`, `support_id`,
and NRMSE for all seven methods — `REL_nrmse`, `B0_nrmse` (calibration mean),
`B1_nrmse` (persistence), `B1A_nrmse` (AR(1)), `B2_nrmse` (raw ridge, 78),
`B3_nrmse` (raw HistGB, 78), `H0_nrmse` (hardened raw ridge, 70).

Verified on export: 62 unique discharges, REL mean **0.189115**, persistence mean
**0.216422**, **32 wins / 5 ties / 25 losses**.

**Ties.** The 32/5/25 record uses the contract's own practical-equivalence floor:
a discharge is a tie when `|REL − B1| ≤ 0.01`. Recomputing with strict inequality
gives a different split; use the floor to reproduce the published record.

Block-level results (186 rows, three blocks per discharge, with `scale` and
`log10_kappa`) exist at `heldout_block_results.csv` but are not exported, since
the panel is per-discharge.

## Provenance and cautions

`EXPORT_MANIFEST.json` carries, for every file: exported name, panel, role,
absolute source path, freeze or stage id, source sha256, byte size, whether it
was transformed, and a field-level description — plus the cross-checks above.

Two cautions that must travel with any figure built from these files:

- The panel-3 result is **target-cross-fitted reconstruction over a
  predictor-qualified finite 62-discharge object**. It is *not* external
  validation, not zero-shot, and not a claim about unseen discharges. See
  `../S7_12_qualified_result/S7_12_CLAIM_BOUNDARY.md`.
- Panel 2 shows **support non-uniqueness**. No fold support is canonical, and the
  descriptive `C_E2_ALL_DESC` support (S7.E2.2, not exported here) is
  representative rather than validated.
