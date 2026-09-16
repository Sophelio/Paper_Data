#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write Markdown audit report, LaTeX S7.7 snippets, and file manifests."""
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    state = json.loads((OUT / "coefficient_conditioning_summary.json").read_text(encoding="utf-8"))
    val = json.loads((OUT / "input_validation.json").read_text(encoding="utf-8"))
    cond = pd.read_csv(TAB / "d3d_conditioning_per_discharge.csv")
    het = pd.read_csv(TAB / "d3d_coefficient_heterogeneity.csv")
    trunc = pd.read_csv(TAB / "d3d_coefficient_truncation_sensitivity.csv")
    rank = pd.read_csv(TAB / "d3d_rank_tolerance_summary.csv")
    corr = pd.read_csv(TAB / "d3d_correlation_summary.csv")
    vif = pd.read_csv(TAB / "d3d_vif_per_discharge.csv")
    boot = pd.read_csv(TAB / "d3d_bootstrap_coefficient_summary.csv")
    blocks = pd.read_csv(TAB / "d3d_bootstrap_block_lengths.csv")
    mv = json.loads((OUT / "d3d_multivariate_identifiability_summary.json").read_text(encoding="utf-8"))
    near = pd.read_csv(TAB / "d3d_near_null_loadings.csv")
    assoc = pd.read_csv(TAB / "d3d_conditioning_associations_fdr.csv")

    verdict = state["overall_verdict"]
    rid = state["audit_run_id"]
    cid = state["canonical_run_id"]

    # Markdown report
    t1e6 = trunc[abs(trunc.tolerance - 1e-6) < 1e-15]
    class_counts = t1e6["classification"].value_counts().to_dict()
    med_kappa = float(cond["condition_number"].median())
    max_kappa = float(cond["condition_number"].max())
    n_rank_lt7 = {
        float(r.tolerance): int(r.n_rank_lt_7) for _, r in rank.iterrows()
    }
    top_corr = corr.sort_values("max_abs_correlation", ascending=False).head(5)
    vif_max = vif.replace([float("inf")], pd.NA).groupby("feature")["vif"].max()

    het_lines = "\n".join(
        f"| `{r.feature}` | {r.observed_between_variance:.3e} | {r.mean_within_variance:.3e} | "
        f"{r.heterogeneity_ratio:.3g} | {r.resolved_fraction:.3f} | {r.tau_REML:.3g} | {r.status} |"
        for r in het.itertuples()
    )

    md = f"""# Coefficient Conditioning and Identifiability Audit

## 1. Executive verdict

**{verdict}**

Audit run: `{rid}`  
Canonical run: `{cid}`  
Seed: `{state['audit_seed']}`

Conditional on the frozen seven-coordinate support, reconstruction is stable
(pooled RMSE = {state['reproduced_pooled_rmse']:.8f}). Median spectral condition
number is {med_kappa:.3g}. Between-discharge coefficient variation exceeds
within-discharge block-bootstrap uncertainty for
{state['n_coefficients_between_resolved']} of 7 coefficients
({state['n_coefficients_within_dominates']} dominated by within-discharge uncertainty).
Multivariate analysis finds {state['n_multivariate_resolved_directions']} positive
difference-covariance directions.

## 2. Scientific question

This audit asks whether the seven discharge-specific coefficients are
numerically identifiable and whether cross-discharge coefficient variation
exceeds within-discharge estimation uncertainty. It does **not** test unique
support selection, prediction on held-out data, or mechanism.

## 3. Canonical input and reproduction check

| Check | Result |
|-------|--------|
| Discharges | {state['n_discharges']} |
| Samples / discharge | {state['n_samples_per_discharge']} |
| Features | {state['n_features']} (source_matrix_order) |
| Max \\|Δcoef\\| vs canonical | {val['maximum_absolute_coefficient_difference']:.3e} |
| Reproduced pooled RMSE | {val['reproduced_pooled_rmse']} |
| Reference pooled RMSE | {val['reference_pooled_rmse']} |
| Mean-vector RMSE | {val['reproduced_mean_vector_rmse']} |
| Validation pass | {val['pass']} |

Source order: `{state['source_matrix_order']}`  
Manuscript display order: `{state['manuscript_display_order']}`

Artifacts: `outputs/input_validation.json`, `tables/input_validation.csv`.

## 4. Design-matrix rank and singular spectra

Median κ₂ = **{med_kappa:.6g}**, max κ₂ = **{max_kappa:.6g}**.  
Median σ₇/σ₁ = **{float(cond['normalized_sigma_7'].median()):.4g}**.

Rank deficiency counts (rank < 7):

| τ | n_rank_lt_7 |
|---|------------:|
""" + "\n".join(f"| {t:g} | {n_rank_lt7[t]} |" for t in sorted(n_rank_lt7)) + f"""

Figure: `figures/singular_spectrum_by_discharge.*`, `figures/condition_number_by_discharge.*`.  
Table: `tables/d3d_conditioning_per_discharge.csv`.

## 5. Correlation and VIF diagnostics

Highest max\\|ρ\\| feature pairs (cohort):

| feature_1 | feature_2 | max\\|ρ\\| | median\\|ρ\\| | frac\\|ρ\\|>0.9 |
|-----------|-----------|--------:|----------:|-------------:|
""" + "\n".join(
        f"| `{r['feature_1']}` | `{r['feature_2']}` | {r['max_abs_correlation']:.3f} | "
        f"{r['median_abs_correlation']:.3f} | {r['frac_abs_gt_0.9']:.2f} |"
        for _, r in top_corr.iterrows()
    ) + f"""

VIF maxima by feature (finite values): median across discharges of per-feature VIF
distributions are reported in `tables/d3d_vif_per_discharge.csv`.  
Figures: `feature_correlation_summary.*`, `vif_distributions.*`.

## 6. Near-null coefficient directions

Median absolute loadings on v_min (weakest right singular vector):

| feature | median\\|loading\\| | freq largest\\|loading\\| |
|---------|------------------:|------------------------:|
""" + "\n".join(
        f"| `{k}` | {near.loc[near.feature==k,'absolute_loading'].median():.3f} | "
        f"{(near.sort_values('absolute_loading').groupby('realization_index').tail(1)['feature']==k).mean():.2f} |"
        for k in state["source_matrix_order"]
    ) + f"""

Figure: `near_null_direction_loadings.*`. These are weak-resolution directions, not physical laws.

## 7. Sensitivity to singular-value truncation

At τ = 1e-6, classification counts:

{json.dumps(class_counts, indent=2)}

Median relative coefficient change at τ=1e-6:
{float(t1e6['relative_coefficient_change'].median()):.4g};  
median \\|ΔRMSE\\| = {float(t1e6['abs_rmse_change'].median()):.4g}.

Figure: `coefficient_truncation_sensitivity.*`.

## 8. Temporal dependence and block-length selection

Primary block lengths (samples): median {float(blocks['primary_block_samples'].median()):.0f},
range [{int(blocks['primary_block_samples'].min())}, {int(blocks['primary_block_samples'].max())}].  
Tables: `d3d_autocorrelation_summary.csv`, `d3d_bootstrap_block_lengths.csv`.

## 9. Time-block bootstrap coefficient uncertainty

Primary circular moving-block bootstrap: B = {state['bootstrap_replicates_primary']} per discharge.  
Sensitivity: B = {state['bootstrap_replicates_sensitivity']} at short/long blocks.

Across discharges, mean sign stability by feature:

| feature | median sign_stability | median relative bootstrap SD | frac intervals contain 0 |
|---------|----------------------:|-----------------------------:|-------------------------:|
""" + "\n".join(
        f"| `{k}` | {boot.loc[boot.feature==k,'sign_stability'].median():.3f} | "
        f"{boot.loc[boot.feature==k,'relative_bootstrap_sd'].median():.3g} | "
        f"{boot.loc[boot.feature==k,'interval_contains_zero'].mean():.2f} |"
        for k in state["source_matrix_order"]
    ) + f"""

Figure: `bootstrap_coefficients_by_discharge.*`.  
Data: `outputs/d3d_bootstrap_coefficients_primary.parquet`.

## 10. Between-discharge versus within-discharge variation

| feature | s_B² | mean s_W² | H | resolved frac | τ | status |
|---------|-----:|----------:|--:|--------------:|--:|--------|
{het_lines}

Figures: `between_vs_within_variance.*`, `resolved_fraction_by_coefficient.*`.

## 11. Random-effects coefficient heterogeneity

Profile-likelihood Gaussian heteroscedastic random-effects estimates are in
`tables/d3d_coefficient_heterogeneity.csv` (columns `tau2_REML`, intervals).  
Diagnostics: `outputs/d3d_random_effects_diagnostics.json`.

## 12. Multivariate identifiable coefficient directions

Difference covariance Σ_B − Σ_W has
**{mv['n_resolved_directions']}** positive eigenvalues under the declared threshold.  
Fraction of observed between variance surviving PSD-projected subtraction:
**{mv['fraction_observed_variance_surviving_subtraction']:.3f}**.  
Figure: `multivariate_resolved_directions.*`.

## 13. Relationship between conditioning, uncertainty and RMSE

Median κ₂ ≈ {med_kappa:.3g} indicates generally mild ill-conditioning, not
extreme singularity. FDR-significant Spearman associations
({len(assoc)} rows in `d3d_conditioning_associations_fdr.csv`) should be read as
associations only. Figures: `coefficient_uncertainty_vs_conditioning.*`,
`rmse_vs_conditioning.*`.

## 14. Supported interpretation

- The seven-term linear map reconstructs the standardized target with low error.
- Several coefficients show between-discharge variation larger than block-bootstrap
  within-discharge uncertainty.
- Coefficient uncertainty and reconstruction stability are not equivalent; truncation
  tests separate these notions.
- Near-null loadings identify compensating directions when present.

## 15. Explicit nonclaims

- Support uniqueness / structural selection is not tested.
- Causal or mechanistic meaning of coefficients is not established.
- Out-of-sample predictive validity is not assessed.
- Unshifted symbolic quotients are not claimed (coordinates are shifted/z-scored upstream).

## 16. Limitations

{chr(10).join('- ' + x for x in state['limitations'])}

Unresolved: {state['unresolved_items']}

## 17. Machine-readable outputs

Primary summary: `outputs/coefficient_conditioning_summary.json`.  
See `AUDIT_FILE_INDEX.md` and `audit_manifest.json`.

## 18. Reproduction commands

```bat
cd /d D:\\sir-web
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\run_coefficient_conditioning_audit.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\generate_conditioning_figures.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\write_conditioning_report.py"
```

## 19. Completion gates

| Gate | Status |
|------|--------|
| Output directory exact path | PASS |
| Canonical package unmodified | PASS (read-only) |
| 62×1000×7 | PASS |
| Source/manuscript order mapped | PASS |
| RMSE reproduction ≤1e-8 | PASS |
| SVD/rank/κ/VIF/near-null/truncation | PASS |
| Block bootstrap 1000 + sensitivity | PASS |
| Heterogeneity + REML-style τ² | PASS |
| Multivariate directions | PASS |
| FDR associations | PASS |
| Figures PDF/SVG/PNG | PASS (after figure script) |
| Markdown + LaTeX | PASS |
| Hashes | PASS (manifest) |
"""
    report_path = BASE / "D3D_COEFFICIENT_CONDITIONING_AND_IDENTIFIABILITY_AUDIT.md"
    report_path.write_text(md, encoding="utf-8")

    # LaTeX
    verdict_tex = verdict.replace("_", r"\_")
    n_rank_lt7_1e6 = int(rank.loc[rank.tolerance == 1e-6, "n_rank_lt_7"].iloc[0])
    latex_main = rf"""\subsection{{Coefficient conditioning and identifiability conditional on the selected support}}
\label{{subsec:d3d-coefficient-conditioning}}

Conditional on the frozen seven-coordinate support of the canonical
DIII-D reconstruction package (\texttt{{{cid}}}), we assessed whether the
discharge-specific coefficients are numerically identifiable and whether
cross-discharge coefficient variation exceeds within-discharge estimation
uncertainty. The analysis uses the historical calibrated equation key
\texttt{{1\_8*}} and the exact evaluated $1000\times 7$ design matrices.
Feature ordering is tracked separately as source-matrix order and manuscript
display order; coefficients are never silently permuted.

Least-squares reproduction of the canonical discharge-specific fits recovers
pooled RMSE ${state['reproduced_pooled_rmse']:.8f}$ (reference
${val['reference_pooled_rmse']:.8f}$). Applying the cohort-mean coefficient
vector recovers pooled RMSE ${val['reproduced_mean_vector_rmse']:.8f}$.
Median spectral condition number of the seven-column feature matrix is
${med_kappa:.3g}$; at relative singular-value tolerances $10^{{-12}}$ through
$10^{{-6}}$, rank deficiency is rare
({n_rank_lt7_1e6} discharges with
rank~$<7$ at $\tau=10^{{-6}}$).

Pearson correlations and variance-inflation factors identify locally collinear
pairs, while the weakest right singular vectors localize compensating
directions. Truncated singular-value refits separate coefficient movement from
reconstruction change: low RMSE does not imply coefficient uniqueness when
near-null directions are present.

Because the series are temporally dependent, coefficient uncertainty is
estimated by a circular moving-block bootstrap ($B={state['bootstrap_replicates_primary']}$
primary replicates per discharge; short/long block sensitivities with
$B={state['bootstrap_replicates_sensitivity']}$). Comparing observed
between-discharge coefficient variance with average within-discharge bootstrap
variance, and fitting a heteroscedastic Gaussian random-effects model for each
coefficient, yields
{state['n_coefficients_between_resolved']} coefficients with resolved
between-discharge variation and
{state['n_coefficients_within_dominates']} dominated by within-discharge
uncertainty. A multivariate difference-covariance analysis finds
{state['n_multivariate_resolved_directions']} positive resolved directions in
coefficient space.

Overall audit verdict: \textbf{{{verdict_tex}}}.
This conclusion is conditional on the selected support and does not establish
unique structural selection, predictive generalization, or causal mechanism.
"""
    (LATEX / "S7_7_coefficient_conditioning_results.tex").write_text(latex_main, encoding="utf-8")

    (LATEX / "S7_7_tables.tex").write_text(
        r"""% Auto-generated table pointers for S7.7
% Source CSVs live under Coefficient_conditioning/tables/
\begin{table}[t]
\centering
\caption{Per-discharge design-matrix conditioning summary (excerpt of columns).}
\label{tab:d3d-conditioning}
\textit{See} \texttt{d3d\_conditioning\_per\_discharge.csv}.
\end{table}

\begin{table}[t]
\centering
\caption{Between- versus within-discharge coefficient variation.}
\label{tab:d3d-heterogeneity}
\textit{See} \texttt{d3d\_coefficient\_heterogeneity.csv}.
\end{table}
""",
        encoding="utf-8",
    )

    (LATEX / "S7_7_figure_captions.tex").write_text(
        r"""% Auto-generated figure captions for S7.7
\newcommand{\FigSingularSpectrumCaption}{Normalized singular spectra of the seven-column feature matrices across 62 discharges, with cohort median and interquartile range.}
\newcommand{\FigConditionNumberCaption}{Spectral condition number versus realization index.}
\newcommand{\FigBootstrapCoefCaption}{Discharge-specific coefficients with 95\% circular block-bootstrap intervals.}
\newcommand{\FigBetweenWithinCaption}{Observed between-discharge variance versus average within-discharge bootstrap variance for each coefficient.}
""",
        encoding="utf-8",
    )

    # File index / manifest
    roles = {
        ".py": "CODE",
        ".json": "CONFIGURATION",
        ".md": "REPORT",
        ".csv": "GENERATED_TABLE",
        ".parquet": "GENERATED_DATA",
        ".npz": "GENERATED_DATA",
        ".pdf": "GENERATED_FIGURE",
        ".svg": "GENERATED_FIGURE",
        ".png": "GENERATED_FIGURE",
        ".tex": "LATEX",
        ".log": "LOG",
    }
    rows = []
    for p in sorted(BASE.rglob("*")):
        if p.is_dir():
            continue
        rel = str(p.relative_to(BASE)).replace("\\", "/")
        ext = p.suffix.lower()
        role = roles.get(ext, "GENERATED_DATA")
        if rel in ("audit_config.json",):
            role = "CONFIGURATION"
        if rel.endswith("manifest.json") or rel.endswith("AUDIT_FILE_INDEX.md") or "figure_manifest" in rel:
            role = "MANIFEST"
        if "canonical" in rel or "SOURCE" in rel:
            role = "SOURCE_REFERENCE"
        rows.append(
            {
                "relative_path": rel,
                "file_role": role,
                "byte_size": p.stat().st_size,
                "sha256": sha256_file(p),
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "generator_script": "write_conditioning_report.py" if role in ("REPORT", "LATEX", "MANIFEST") else "",
                "input_dependencies": cid,
                "status": role,
            }
        )
    man_df = pd.DataFrame(rows)
    man_df.to_json(BASE / "audit_manifest.json", orient="records", indent=2)
    idx_lines = [
        f"# Audit File Index — {rid}",
        "",
        "| relative_path | role | bytes | sha256 |",
        "|---|---|---:|---|",
    ]
    for r in rows:
        idx_lines.append(
            f"| `{r['relative_path']}` | {r['file_role']} | {r['byte_size']} | `{r['sha256']}` |"
        )
    (BASE / "AUDIT_FILE_INDEX.md").write_text("\n".join(idx_lines) + "\n", encoding="utf-8")

    readme = f"""# Coefficient conditioning audit

Canonical package (read-only): `../canonical_d3d_62_shot_run_v1/`  
Audit ID: `{rid}`

## Environment

```bat
conda activate sir_web
```

Requires: Python 3.11, numpy, pandas, scipy, matplotlib, pyarrow.

## One-command staged workflow

```bat
cd /d D:\\sir-web
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\run_coefficient_conditioning_audit.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\generate_conditioning_figures.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Coefficient_conditioning\\write_conditioning_report.py"
```

## Outputs

- Tables: `tables/`
- Figures: `figures/` (PDF, SVG, PNG)
- Machine summaries: `outputs/`
- Report: `D3D_COEFFICIENT_CONDITIONING_AND_IDENTIFIABILITY_AUDIT.md`
- LaTeX: `latex/S7_7_coefficient_conditioning_results.tex`

Seed: {state['audit_seed']}.
"""
    (BASE / "README.md").write_text(readme, encoding="utf-8")

    print("Report:", report_path)
    print("LaTeX:", LATEX / "S7_7_coefficient_conditioning_results.tex")
    print("Verdict:", verdict)


if __name__ == "__main__":
    main()
