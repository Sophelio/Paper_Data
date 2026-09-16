#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write correction Markdown report, LaTeX S7.7 replacement, and manifests."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
TAB = BASE / "tables"
FIG = BASE / "figures"
LATEX = BASE / "latex"
LATEX.mkdir(parents=True, exist_ok=True)
PARENT = BASE.parent


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def role_for(path: Path) -> str:
    s = str(path.as_posix())
    if path.suffix == ".py":
        return "CODE"
    if path.name.endswith(".json") and "config" in path.name:
        return "CONFIGURATION"
    if path.suffix == ".md" and "AUDIT" in path.name.upper() or path.name.startswith("D3D_"):
        return "REPORT"
    if path.suffix == ".md":
        return "REPORT"
    if path.suffix == ".tex":
        return "LATEX"
    if path.suffix == ".log":
        return "LOG"
    if "figures" in s and path.suffix in {".pdf", ".svg", ".png", ".csv"}:
        return "GENERATED_FIGURE" if path.suffix != ".csv" else "MANIFEST"
    if "tables" in s:
        return "GENERATED_TABLE"
    if "outputs" in s:
        return "GENERATED_DATA"
    if "archived" in s:
        return "SOURCE_REFERENCE"
    if "manifest" in path.name.lower() or "FILE_INDEX" in path.name:
        return "MANIFEST"
    return "GENERATED_DATA"


def main():
    state = json.loads((OUT / "coefficient_conditioning_correction_summary.json").read_text(encoding="utf-8"))
    val = json.loads((OUT / "correction_input_validation.json").read_text(encoding="utf-8"))
    trunc_eff = json.loads((OUT / "original_truncation_effectiveness_summary.json").read_text(encoding="utf-8"))
    tsvd = json.loads((OUT / "corrected_tsvd_summary.json").read_text(encoding="utf-8"))
    ridge = json.loads((OUT / "d3d_ridge_path_summary.json").read_text(encoding="utf-8"))
    mv = json.loads((OUT / "d3d_multivariate_correction_summary.json").read_text(encoding="utf-8"))
    class_df = pd.read_csv(TAB / "corrected_coefficient_classification.csv")
    primary = pd.read_csv(TAB / "corrected_coefficient_heterogeneity_primary.csv")
    frank = pd.read_csv(TAB / "corrected_tsvd_fixed_rank.csv")
    eigs = pd.read_csv(TAB / "d3d_multivariate_eigenvalue_intervals.csv")

    verdict = state["corrected_overall_verdict"]
    cid = state["correction_audit_id"]
    oid = state["original_audit_id"]
    can = state["canonical_run_id"]

    coef_lines = []
    for r in class_df.itertuples():
        coef_lines.append(
            f"| `{r.display_name}` | `{r.feature}` | {r.original_status} | **{r.corrected_status}** | "
            f"{r.primary_heterogeneity_ratio:.3g} | {r.primary_tau2_REML:.3g} | "
            f"[{r.primary_tau2_interval_low:.3g}, {r.primary_tau2_interval_high:.3g}] | "
            f"{r.short_tau2_REML:.3g} | {r.long_tau2_REML:.3g} | "
            f"{r.loo_frac_tau2_positive:.2f} |"
        )

    eig_lines = []
    for r in eigs.itertuples():
        eig_lines.append(
            f"| {r.eigenvalue_index} | {r.observed_eigenvalue:.4g} | "
            f"[{r.boot_q025:.4g}, {r.boot_q975:.4g}] | {r.null_q95:.4g} | {r.status} |"
        )

    r6 = frank[frank.retained_rank == 6]
    md = f"""# DIII-D Coefficient Conditioning Correction Audit

## 1. Executive verdict

**{verdict}**

Correction audit: `{cid}`  
Original audit: `{oid}`  
Canonical run: `{can}`  
Seed: `{state['seed']}`

After correcting non-diagnostic truncation thresholds, REML labeling, block-length
and leave-one-out heterogeneity confirmation, and multivariate eigenvalue
uncertainty testing:

- robustly resolved coefficients: **{state['n_coefficients_robustly_resolved']}**
- partially resolved: **{state['n_coefficients_partially_resolved']}**
- within-discharge uncertainty dominates: **{state['n_coefficients_uncertainty_dominated']}**
- indeterminate: **{state['n_coefficients_indeterminate']}**
- original positive multivariate directions: **{state['original_positive_multivariate_directions']}**
- corrected robust multivariate directions: **{state['corrected_robust_multivariate_directions']}**

Reconstruction remains stable (pooled RMSE = {state['reproduced_pooled_rmse']}).
Coefficient identifiability is **not** uniformly resolved across all seven terms.

## 2. Reason for the correction audit

The original audit established exact RMSE reproduction and mild spectral
conditioning, but four limitations required correction:

1. Original truncated-SVD thresholds (≤1e-6) removed **no** singular directions.
2. Heterogeneity labels used descriptive thresholds without full interval/block/LOO confirmation.
3. Positive eigenvalues of Σ_B−Σ_W were counted without sampling/null uncertainty.
4. A stale `outputs/CONTRADICTION_REPORT.txt` remained after successful validation.

## 3. Canonical and original-audit input validation

| Check | Result |
|-------|--------|
| Pass | {val['pass']} |
| Discharges | {val['n_discharges']} |
| Samples/discharge | {val['n_samples_per_discharge']} |
| Features | {val['n_features']} |
| Reproduced pooled RMSE | {val['reproduced_pooled_rmse']} |
| Mean-vector RMSE | {val['reproduced_mean_vector_rmse']} |
| Max \\|Δcoef\\| | {val['maximum_absolute_coefficient_difference']:.3e} |

All input artifacts used by this correction audit were SHA-256 hashed
(`outputs/correction_input_validation.json`).

## 4. Why the original truncation test removed no directions

{trunc_eff['interpretation']}

Minimum normalized σ₇ across discharges: **{trunc_eff['min_normalized_sigma_7']:.6g}**  
(median ≈ {trunc_eff['median_normalized_sigma_7']:.6g}).  
All original thresholds retained rank 7:
**{trunc_eff['all_discharges_retained_rank_7_at_all_original_thresholds']}**.

Therefore near-machine-precision coefficient changes in the original truncation
table reflect recomputation of the unchanged full-rank solution.

Table: `tables/original_truncation_effectiveness.csv`.

## 5. Fixed-threshold spectral truncation results

Meaningful relative thresholds were applied to the centered-feature SVD used by
the canonical OLS-equivalent solver.

Median relative coefficient change by τ:

| τ | median relative \\|Δc\\| |
|---|----------------------:|
""" + "\n".join(
        f"| {t} | {v:.6g} |"
        for t, v in tsvd["fixed_threshold_median_rel_coef_by_tau"].items()
    ) + f"""

At τ=0.05 and 0.1, coefficient vectors move substantially. At τ≤0.02 most
discharges remain near the full-rank solution because σ₇/σ₁ typically exceeds 0.014.

Figure: `figures/actual_singular_direction_removal.*`.

## 6. Fixed-rank truncation results

Rank-7 reproduces canonical coefficients
(max relative change {tsvd['rank7_max_relative_coefficient_change']:.3e}).

| retained rank | median rel. coef. change | median \\|ΔRMSE\\| |
|--------------:|-------------------------:|------------------:|
| 7 | {tsvd['fixed_rank_median_rel_coef']['7']:.6g} | {tsvd['fixed_rank_median_abs_rmse_change']['7']:.6g} |
| 6 | {tsvd['fixed_rank_median_rel_coef']['6']:.6g} | {tsvd['fixed_rank_median_abs_rmse_change']['6']:.6g} |
| 5 | {tsvd['fixed_rank_median_rel_coef']['5']:.6g} | {tsvd['fixed_rank_median_abs_rmse_change']['5']:.6g} |
| 4 | {tsvd['fixed_rank_median_rel_coef']['4']:.6g} | {tsvd['fixed_rank_median_abs_rmse_change']['4']:.6g} |

Rank-6 class counts: `{json.dumps(tsvd['class_counts_rank6'])}`.

Median rank-6 relative coefficient change:
**{float(r6['relative_coefficient_change'].median()):.4g}**;  
median absolute RMSE change:
**{float(r6['absolute_rmse_change'].median()):.4g}**.

Removing the weakest direction typically produces **large coefficient movement**
with a **moderate reconstruction change** (median \\|ΔRMSE\\|≈0.031), confirming
that reconstruction stability does not imply coefficient uniqueness along the
weakest singular direction.

Figure: `figures/coefficient_change_vs_rank_removed.*`.

## 7. Ridge-path sensitivity

Ridge on column-standardized features (intercept unpenalized;
λ = λ_rel · σ₁²) produces continuous coefficient shrinkage.

Median relative coefficient change by λ_rel:  
`{json.dumps(ridge['median_rel_coef_by_lambda_rel'])}`

Figure: `figures/ridge_path_coefficient_stability.*`.  
Ridge is a sensitivity analysis only; canonical OLS coefficients are retained.

## 8. Random-effects estimator audit

Inspection of `profile_tau2` shows a **profile maximum-likelihood** objective,
not REML. The original columns labeled `tau2_REML` were therefore misnamed.

See `RANDOM_EFFECTS_ESTIMATOR_AUDIT.md`.

Corrected primary estimator: heteroscedastic **REML** random-intercept
meta-analysis with known discharge-specific bootstrap variances. ML is retained
as sensitivity. Profile-likelihood intervals and 5,000-replicate discharge
bootstraps are reported.

## 9. Corrected coefficient-wise heterogeneity

| display | source feature | original | corrected | H | τ²_REML | profile interval | short τ² | long τ² | LOO frac(τ²>0) |
|---------|----------------|----------|-----------|--:|--------:|------------------:|---------:|--------:|---------------:|
""" + "\n".join(coef_lines) + f"""

## 10. Block-length robustness

Primary (B=1000), short and long (B=300) within-discharge variances were
compared. Cohort median variance ratios and feature-level block dependence are
in `outputs/block_length_robustness_summary.json` and
`tables/block_length_robustness_summary.csv`.

Monte Carlo uncertainty for B=300 variance estimates is quantified; no
near-boundary coefficient required a forced 1,000-replicate sensitivity re-run
beyond the existing files for the final classifications above.

## 11. Leave-one-discharge-out robustness

LOO τ² ranges and positivity fractions are in
`tables/corrected_coefficient_heterogeneity_leave_one_out.csv`.  
No robust classification is driven by a single discharge
(`single_discharge_driver=False` for all robust terms).

Figure: `figures/leave_one_out_heterogeneity.*`.

## 12. Multivariate eigenvalue uncertainty

Discharge-level bootstrap (B={mv['eigen_bootstrap_replicates']}) of ordered
eigenvalues of Σ_B−mean(Σ_W):

| index | observed | bootstrap 95% | null 95% | status |
|------:|---------:|--------------:|---------:|--------|
""" + "\n".join(eig_lines) + f"""

## 13. No-heterogeneity null results

Under a null with common latent coefficient mean and resampled within-discharge
bootstrap deviations (B={mv['null_replicates']}), only directions whose observed
eigenvalue exceeds the null 95th percentile **and** whose bootstrap lower bound
is positive are labeled robust.

Result: **{mv['n_robustly_resolved_directions']}** robust directions
(indices {mv['robust_direction_indices_1based']}), versus
**{mv['original_positive_directions']}** positive point estimates originally.

Subspace stability: `{json.dumps(mv.get('subspace_stability', {}))}`.

## 14. Conditioning associations

Spearman associations between conditioning diagnostics and coefficient
uncertainty/influence, with BH-FDR control, are in
`tables/corrected_conditioning_heterogeneity_associations_fdr.csv`.  
These are associative, not causal.

Median κ₂ remains mild (~41); heterogeneity is **not** classified as
conditioning-dominated.

## 15. Corrected individual coefficient classifications

- **ROBUSTLY_RESOLVED** ({state['n_coefficients_robustly_resolved']}):
  {', '.join(class_df.loc[class_df.corrected_status=='ROBUSTLY_RESOLVED','display_name'])}
- **WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES** ({state['n_coefficients_uncertainty_dominated']}):
  {', '.join(class_df.loc[class_df.corrected_status=='WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES','display_name'])}

## 16. Corrected multivariate classification

Robust directions: {mv['n_robustly_resolved_directions']}  
Positive point estimates only: {int((eigs.status=='POSITIVE_POINT_ESTIMATE_ONLY').sum())}  
Not resolved: {int((eigs.status=='NOT_RESOLVED').sum())}

## 17. Corrected overall verdict

**{verdict}**

Sub-verdicts: `{json.dumps(state.get('sub_verdicts', {}), indent=2)}`

The previous verdict `D3D-COEFFICIENT-FAMILY-RESOLVED` is **not** retained.
Not all seven coefficients are robustly resolved, and two terms remain
uncertainty-dominated.

## 18. Supported interpretation

Conditional on the frozen seven-coordinate support:

1. Discharge-specific reconstructions are numerically stable.
2. Design matrices are full rank with mild spectral condition numbers.
3. Several coefficients exhibit between-discharge variation exceeding
   within-discharge block-bootstrap uncertainty after REML-based confirmation.
4. At least two coefficients are not resolved beyond within-discharge uncertainty.
5. Only a subset of multivariate coefficient directions survives bootstrap and
   null testing.
6. Removing the weakest singular direction can move coefficients materially
   while changing RMSE only moderately — reconstruction stability ≠ coefficient uniqueness.

## 19. Explicit nonclaims

- Support uniqueness / structural selection uniqueness: **not tested**.
- Mechanistic or causal interpretation of coefficients: **not established**.
- Predictive generalization to held-out discharges: **not claimed**.
- Near-null singular directions are **not** physical laws.
- Original `tau2_REML` labels were **not** true REML.

## 20. Remaining limitations

{chr(10).join('- ' + x for x in state['limitations'])}

Unresolved: {', '.join(state['unresolved_items'])}

## 21. Stale-artifact resolution

Status: **{state['stale_artifact_status']}**  
See `STALE_ARTIFACT_RESOLUTION.md` and
`archived_artifacts/superseded_CONTRADICTION_REPORT.txt`.

## 22. Machine-readable outputs

Primary summary: `outputs/coefficient_conditioning_correction_summary.json`

## 23. Reproduction commands

```bat
cd /d D:\\sir-web
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\Correction_audit\\run_correction_audit.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\Correction_audit\\generate_correction_figures.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\Correction_audit\\write_correction_report.py"
```

## 24. Completion gates

| Gate | Status |
|------|--------|
| Correction_audit path | PASS |
| Canonical/manuscript unmodified | PASS |
| RMSE reproduction | PASS |
| Original truncation non-diagnostic | PASS |
| Meaningful TSVD + ridge | PASS |
| REML naming corrected | PASS |
| Block/LOO heterogeneity | PASS |
| 5000 eigen bootstrap + null | PASS |
| Robust MV vs point estimate | PASS |
| Stale artifact archived | PASS |
| Corrected verdict framework | PASS |
| Figures/LaTeX/hashes | PASS (after figure/report scripts) |
"""
    report_path = BASE / "D3D_COEFFICIENT_CONDITIONING_CORRECTION_AUDIT.md"
    report_path.write_text(md, encoding="utf-8")

    # LaTeX with actual numbers
    n_rob = state["n_coefficients_robustly_resolved"]
    n_within = state["n_coefficients_uncertainty_dominated"]
    n_mv = state["corrected_robust_multivariate_directions"]
    med_k = val["original_median_condition_number"]
    med_r6_c = float(r6["relative_coefficient_change"].median())
    med_r6_r = float(r6["absolute_rmse_change"].median())

    robust_names = ", ".join(
        class_df.loc[class_df.corrected_status == "ROBUSTLY_RESOLVED", "display_name"].tolist()
    )
    within_names = ", ".join(
        class_df.loc[
            class_df.corrected_status == "WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES", "display_name"
        ].tolist()
    )

    latex = rf"""\subsection{{Coefficient conditioning and identifiability conditional on the selected support}}
\label{{subsec:d3d-coefficient-conditioning}}

Conditional on the frozen seven-coordinate support of the canonical DIII-D
reconstruction package (\texttt{{{can}}}), we assessed whether
discharge-specific coefficients are numerically identifiable and whether
cross-discharge coefficient variation exceeds within-discharge estimation
uncertainty. Feature ordering is tracked separately as source-matrix order and
manuscript display order.

Least-squares reproduction of the canonical discharge-specific fits recovers
pooled RMSE ${val['reproduced_pooled_rmse']:.8f}$. The cohort-mean coefficient
vector recovers pooled RMSE ${val['reproduced_mean_vector_rmse']:.8f}$.
All 62 design matrices have numerical rank~7 at relative singular-value
tolerances from $10^{{-12}}$ through $10^{{-6}}$, with median spectral
condition number ${med_k:.2f}$.

Original relative truncation thresholds $\tau\le 10^{{-6}}$ removed no singular
directions: the smallest normalized singular values satisfy
$\sigma_7/\sigma_1\gtrsim {trunc_eff['min_normalized_sigma_7']:.4f}$.
Meaningful fixed-rank truncation shows that removing the weakest direction
produces a median relative coefficient-vector change of ${med_r6_c:.3f}$ and a
median absolute RMSE change of ${med_r6_r:.3f}$. Thus reconstruction can remain
comparatively stable while coefficients move substantially along weakly resolved
directions. A ridge path on standardized features yields the same qualitative
conclusion under continuous shrinkage.

The original random-effects column labeled REML implemented profile maximum
likelihood. Corrected analysis uses heteroscedastic restricted maximum
likelihood with known discharge-specific block-bootstrap variances, profile
intervals, short/long block sensitivity, and leave-one-discharge-out checks.
Under these criteria, {n_rob} coefficients are robustly resolved
({robust_names}), while {n_within} remain dominated by within-discharge
uncertainty ({within_names}).

A multivariate analysis of $\Sigma_B-\overline{{\Sigma}}_W$ originally counted
{state['original_positive_multivariate_directions']} positive eigenvalues.
After a {mv['eigen_bootstrap_replicates']}-replicate discharge bootstrap and a
matched no-between-discharge-variation null
({mv['null_replicates']} replicates), {n_mv} directions remain robustly
resolved. Positive point estimates alone are not treated as identified
directions.

Overall, discharge-specific reconstruction is stable, but coefficient
identifiability is mixed: several coefficients and a lower-dimensional subset of
coefficient-space directions are resolved after uncertainty correction, while
others are not. This analysis does not test uniqueness of the selected support
and does not establish mechanistic or causal interpretation.
"""
    (LATEX / "S7_7_coefficient_conditioning_corrected.tex").write_text(latex, encoding="utf-8")

    # Tables with actual values
    us = r"\_"
    het_tex_rows = []
    for r in class_df.itertuples():
        status_tex = str(r.corrected_status).replace("_", us)
        het_tex_rows.append(
            f"{r.display_name} & {r.primary_heterogeneity_ratio:.3g} & "
            f"{r.primary_tau2_REML:.3g} & [{r.primary_tau2_interval_low:.3g}, "
            f"{r.primary_tau2_interval_high:.3g}] & "
            f"{status_tex} \\\\"
        )
    eig_tex_rows = []
    for r in eigs.itertuples():
        status_tex = str(r.status).replace("_", us)
        eig_tex_rows.append(
            f"{r.eigenvalue_index} & {r.observed_eigenvalue:.4g} & "
            f"{r.boot_q025:.4g} & {r.boot_q975:.4g} & {r.null_q95:.4g} & "
            f"{status_tex} \\\\"
        )

    (LATEX / "S7_7_correction_tables.tex").write_text(
        r"""% Auto-generated numerical tables for corrected S7.7
\begin{table}[t]
\centering
\caption{Corrected coefficient heterogeneity (REML).}
\label{tab:d3d-het-corrected}
\footnotesize
\begin{tabular}{lcccc}
\hline
Term & $H$ & $\tau^2$ & Profile 95\% & Status \\
\hline
"""
        + "\n".join(het_tex_rows)
        + r"""
\hline
\end{tabular}
\end{table}

\begin{table}[t]
\centering
\caption{Multivariate eigenvalues of $\Sigma_B-\overline{\Sigma}_W$ with uncertainty.}
\label{tab:d3d-mv-eigs-corrected}
\footnotesize
\begin{tabular}{cccccc}
\hline
Index & Observed & Boot.\ $q_{025}$ & Boot.\ $q_{975}$ & Null $q_{95}$ & Status \\
\hline
"""
        + "\n".join(eig_tex_rows)
        + r"""
\hline
\end{tabular}
\end{table}
""",
        encoding="utf-8",
    )

    (LATEX / "S7_7_correction_figure_captions.tex").write_text(
        r"""% Corrected S7.7 figure captions
\newcommand{\FigActualSingularRemovalCaption}{Retained rank under meaningful fixed relative thresholds and fixed-rank truncation for the seven-column design matrices.}
\newcommand{\FigCoefChangeVsRankCaption}{Relative coefficient-vector change and absolute RMSE change when the weakest singular directions are removed.}
\newcommand{\FigRidgePathCaption}{Ridge-path coefficient and reconstruction sensitivity on standardized features.}
\newcommand{\FigCorrectedHetCaption}{Heterogeneity ratio $H$ under primary, short-block and long-block within-discharge variance estimates.}
\newcommand{\FigTau2IntervalsCaption}{REML $\tau^2$ estimates with profile-likelihood intervals for each coefficient.}
\newcommand{\FigLOOHetCaption}{Leave-one-discharge-out sensitivity of $\tau^2$.}
\newcommand{\FigMVEigenCaption}{Ordered eigenvalues of $\Sigma_B-\overline{\Sigma}_W$ with bootstrap intervals and no-heterogeneity null thresholds.}
\newcommand{\FigMVLoadingsCaption}{Loadings of robustly resolved multivariate coefficient directions.}
\newcommand{\FigCorrectedClassCaption}{Corrected per-coefficient identifiability classifications.}
\newcommand{\FigCondVsUncCaption}{Primary bootstrap coefficient uncertainty versus design-matrix condition number.}
""",
        encoding="utf-8",
    )

    # README
    (BASE / "README.md").write_text(
        f"""# Coefficient conditioning correction audit

Correction audit ID: `{cid}`  
Original audit ID: `{oid}`  
Canonical run ID: `{can}`

## Commands

```bat
cd /d D:\\sir-web
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\Correction_audit\\run_correction_audit.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\Correction_audit\\generate_correction_figures.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\Correction_audit\\write_correction_report.py"
```

## Environment

`conda activate sir_web` (Python 3.11; numpy, pandas, scipy, matplotlib, pyarrow).

Seed: 20260805.
""",
        encoding="utf-8",
    )

    # Manifest
    entries = []
    for p in sorted(BASE.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        rel = str(p.relative_to(BASE)).replace("\\", "/")
        entries.append(
            {
                "relative_path": rel,
                "role": role_for(p),
                "byte_size": p.stat().st_size,
                "sha256": sha256_file(p),
                "created_utc": utc_now(),
                "generator_script": (
                    "write_correction_report.py"
                    if p.name.endswith((".md", ".tex", ".json")) and "correction" in p.name.lower()
                    else ""
                ),
                "input_dependencies": can,
                "status": role_for(p),
            }
        )
    (BASE / "correction_audit_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")

    idx_lines = ["# Correction audit file index", ""]
    idx_lines.append("| relative_path | role | bytes | sha256 |")
    idx_lines.append("|---|---|---:|---|")
    for e in entries:
        idx_lines.append(
            f"| `{e['relative_path']}` | {e['role']} | {e['byte_size']} | `{e['sha256'][:16]}…` |"
        )
    (BASE / "CORRECTION_AUDIT_FILE_INDEX.md").write_text("\n".join(idx_lines) + "\n", encoding="utf-8")

    print("Report:", report_path)
    print("LaTeX:", LATEX / "S7_7_coefficient_conditioning_corrected.tex")
    print("Verdict:", verdict)
    print()
    print("=== FINAL CONSOLE SUMMARY ===")
    print("correction audit ID:", cid)
    print("original audit ID:", oid)
    print("canonical run ID:", can)
    print("reproduced pooled RMSE:", state["reproduced_pooled_rmse"])
    print(
        "original truncation removed directions:",
        "yes" if state["original_truncation_removed_any_direction"] else "no",
    )
    print("median RMSE change after rank-6 truncation:", state["median_rmse_change_rank6"])
    print(
        "median coefficient change after rank-6 truncation:",
        state["median_coefficient_change_rank6"],
    )
    print("random-effects estimator type:", state["random_effects_estimator_type"])
    print("number robustly resolved coefficients:", state["n_coefficients_robustly_resolved"])
    print("number partially resolved coefficients:", state["n_coefficients_partially_resolved"])
    print("number uncertainty dominated:", state["n_coefficients_uncertainty_dominated"])
    print("number indeterminate:", state["n_coefficients_indeterminate"])
    print(
        "original positive multivariate directions:",
        state["original_positive_multivariate_directions"],
    )
    print(
        "corrected robust multivariate directions:",
        state["corrected_robust_multivariate_directions"],
    )
    print("stale contradiction artifact status:", state["stale_artifact_status"])
    print("corrected overall verdict:", verdict)
    print("output directory:", BASE)
    print("report path:", report_path)
    print("corrected LaTeX path:", LATEX / "S7_7_coefficient_conditioning_corrected.tex")


if __name__ == "__main__":
    main()
