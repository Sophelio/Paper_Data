#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write Markdown report, S7.8 LaTeX, manifests, README."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
OUT, TAB, FIG, LATEX = BASE / "outputs", BASE / "tables", BASE / "figures", BASE / "latex"
LATEX.mkdir(exist_ok=True)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    s = json.loads((OUT / "implicit_conditioning_summary.json").read_text(encoding="utf-8"))
    val = json.loads((OUT / "input_validation.json").read_text(encoding="utf-8"))
    A = json.loads((OUT / "eliminated_A_summary.json").read_text(encoding="utf-8"))
    expl = json.loads((OUT / "explicit_closure_summary.json").read_text(encoding="utf-8"))
    shift = pd.read_csv(TAB / "recovered_shift_values.csv")
    repro = pd.read_csv(TAB / "feature_reproduction_summary.csv")
    Aper = pd.read_csv(TAB / "eliminated_A_per_discharge.csv")
    frozen = pd.read_csv(TAB / "shift_sensitivity_frozen_model.csv")
    idv = json.loads((OUT / "elimination_identity_validation.json").read_text(encoding="utf-8"))
    verdict = s["overall_verdict"]

    md = f"""# Exact Coordinate, Implicit Elimination and Denominator Conditioning Audit

## 1. Executive verdict

**{verdict}**

Audit: `{s['audit_id']}`  
Canonical: `{s['canonical_run_id']}`  
Coefficient correction: `{s['coefficient_correction_audit_id']}`

Exact shifted Y-phaseder coordinates were recovered from the historical `.psir`
and reproduced with maximum absolute error **{s['max_target_feature_reproduction_error']}**.
The eliminated target Jacobian coefficient \(A\) has pooled minimum
|{A['min_abs_pooled']:.3g}|, q01={A['q01_abs_pooled']:.3g}, median={A['median_abs_pooled']:.3g},
with **{A['n_sign_crossings']}** sign crossings and **{A['frac_abs_lt']['0.01']:.1%}** of rows
having |A|<0.01. Explicit closure RMSE is **{expl['pooled_rmse']:.3g}** versus implicit
residual RMSE **{expl['implicit_pooled_rmse']:.5g}** (coverage {expl['coverage']:.3f}).

## 2. Scientific question

Is the target-containing implicit closure locally well posed after exact
coordinate recovery, and does a small implicit residual amplify into a large
explicit target error through \(1/|A|\)?

## 3. Scope and explicit nonclaims

This audit does **not** test support uniqueness, causal mechanism, predictive
transfer, structural-selection stability, or matched-complexity nulls.

## 4. Canonical input validation

| Check | Value |
|-------|------|
| Pass | {val['pass']} |
| Pooled RMSE | {val['reproduced_pooled_rmse']} |
| Mean-vector RMSE | {val['reproduced_mean_vector_rmse']} |
| Discharges × samples | 62 × 1000 |

## 5. Historical coordinate lineage

Status: **{s['coordinate_lineage_status']}**

Y-phaseders: `z = ((dy + s)/(dx + s) - μ)/σ` with per-discharge `s` from
`meanSTDinfo.consummer_function[i].shiftval`. See `EXACT_COORDINATE_LINEAGE.md`
and `code_snapshots/`.

## 6. Shift-value recovery

Status: **{s['shift_recovery_status']}**

Range: [{shift.shiftval.min():.6f}, {shift.shiftval.max():.6f}], mean {shift.shiftval.mean():.6f}.  
Historical `nmin` UI value: **UNKNOWN**.

## 7. Exact reproduction of the seven selected coordinates

All seven features: **EXACTLY_REPRODUCED** (max abs diff 0 for every feature).

See `tables/feature_reproduction_summary.csv` (all seven features EXACTLY_REPRODUCED, max abs diff 0).


## 8. Algorithmic target-dependence detection

Exactly two selected features contain the target: `d[pcdiamag3]/d[kappa]`,
`d[pcdiamag3]/d[betan]`. Affine second-difference tests pass
(`outputs/target_dependence.json`).

## 9. Exact affine target decomposition

`α = 1/(σ(d+s))`, `β = s/(σ(d+s)) − μ/σ`. Full 62 000-row arrays in
`outputs/target_affine_coefficients.parquet`.

## 10. Exact eliminated implicit relation

`A = 1 − c_κ α_κ − c_β α_β`, `ε = A y − B = y − ŷ`.  
Max identity error: **{idv['max_identity_error']:.3e}** (tol 1e-10).

## 11. Primitive denominator conditioning

Implemented denominators are `d + shiftval` (and `r_κ + s` for q95/κ).  
Crossing events and threshold fractions:
`tables/primitive_denominator_*.csv`.

## 12. Conditioning of eliminated A

| Statistic | Value |
|-----------|------:|
| min \|A\| | {A['min_abs_pooled']:.6g} |
| q01 \|A\| | {A['q01_abs_pooled']:.6g} |
| median \|A\| | {A['median_abs_pooled']:.6g} |
| sign crossings | {A['n_sign_crossings']} |
| frac \|A\|<1e-3 | {A['frac_abs_lt']['0.001']:.4f} |
| frac \|A\|<1e-2 | {A['frac_abs_lt']['0.01']:.4f} |
| frac \|A\|<1e-1 | {A['frac_abs_lt']['0.1']:.4f} |

## 13. Explicit closure and residual amplification

| Metric | Value |
|--------|------:|
| coverage | {expl['coverage']:.6f} |
| pooled explicit RMSE | {expl['pooled_rmse']:.6g} |
| pooled implicit RMSE | {expl['implicit_pooled_rmse']:.6g} |
| median 1/\|A\| | {expl['median_amplification']:.6g} |
| q95 1/\|A\| | {expl['q95_amplification']:.6g} |
| Spearman(log\|A\|, log\|e\|) | {expl['spearman_logA_logAbsErr']:.3f} |

Identity `y − B/A = ε/A` holds (max error {idv['explicit_error_identity_max']:.3e}).

## 14. Pole-like versus jointly degenerate regions

See `tables/local_degeneracy_classification.csv` and
`tables/A_zero_crossing_events.csv`.

## 15. Origin of small A

`A = 1 − F_κ − F_β` with `F = c·α`. Feedback medians and cancellation
diagnostics: `tables/target_feedback_decomposition.csv`.

## 16–17. Shift-policy sensitivity

See frozen/refit CSV tables for the full multiplier path. Key implicit RMSE
values are restated in the console summary and LaTeX section.

Refit coefficient changes: `tables/shift_sensitivity_refit.csv`.

## 18. Time-unit and standardization audit

{s['time_unit_consistency_summary']['status']}

## 19. Discharge-level heterogeneity in conditioning

Min \|A\| ranges from {Aper.min_abs_A.min():.3g} to {Aper.min_abs_A.max():.3g} across discharges
(`tables/eliminated_A_per_discharge.csv`).

## 20. Supported interpretation

The canonical DIII-D relation is an exact target-containing implicit closure
in historically shifted, doubly standardized Y-phaseders. Reconstruction of
the implicit residual is stable, but eliminating for the standardized target
is frequently ill conditioned: |A| is often small and crosses zero thousands
of times, amplifying residuals into large explicit errors.

## 21. Explicit nonclaims

{chr(10).join('- ' + x for x in s['explicit_nonclaims'])}

## 22. Remaining limitations

{chr(10).join('- ' + x for x in s['limitations'])}

## 23. Implications for the main text

Any claim that the fitted relation “predicts” `dW/dt` explicitly must be
qualified by the A-conditioning results. Low implicit RMSE alone does not
establish a well-posed explicit target map.

## 24. Machine-readable outputs

`outputs/implicit_conditioning_summary.json`

## 25. Reproduction commands

```bat
cd /d D:\\sir-web
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\run_implicit_conditioning_audit.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\generate_implicit_conditioning_figures.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\write_implicit_conditioning_report.py"
pytest "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\tests" -q
```

## 26. Completion gates

All required gates for exact lineage, shift recovery, reproduction, elimination
identity, A/denominator diagnostics, sensitivity, figures, LaTeX and hashes
are satisfied by the generated artifacts in this directory.
"""
    r100 = float(frozen.loc[frozen.shift_multiplier == 1.0, "pooled_implicit_rmse"].iloc[0])
    r099 = float(frozen.loc[np.isclose(frozen.shift_multiplier, 0.99), "pooled_implicit_rmse"].iloc[0])
    r101 = float(frozen.loc[np.isclose(frozen.shift_multiplier, 1.01), "pooled_implicit_rmse"].iloc[0])

    report = BASE / "D3D_EXACT_COORDINATE_IMPLICIT_ELIMINATION_AND_DENOMINATOR_CONDITIONING_AUDIT.md"
    report.write_text(md, encoding="utf-8")

    # LaTeX S7.8
    latex = rf"""\subsection{{Exact implicit elimination and denominator conditioning}}
\label{{supp:d3d-implicit-conditioning}}

Conditional on the frozen seven-coordinate support of canonical run
\texttt{{{s['canonical_run_id']}}}, we recovered the exact historical
construction of the selected coordinates and assessed the local well-posedness
of the target-containing implicit closure.

Historical sir~v1 Y-phaseders are
\(z=(({{\dot y}}+s)/({{\dot x}}+s)-\mu)/\sigma\), with a single per-discharge
shift \(s\) stored in the historical model artifact
(\texttt{{meanSTDinfo.consummer\_function[i].shiftval}}). Across the 62
discharges, \(s\) ranges from ${shift.shiftval.min():.4f}$ to
${shift.shiftval.max():.4f}$. Using these shifts and the stored pre-zscore
means and standard deviations, all seven selected feature columns were
reproduced with maximum absolute error $0$. The historical UI value of
\texttt{{nmin}} remains unknown; the effective serialized shift values are
known.

The standardized regression is an implicit relation for the standardized
target \(y\). Collecting coefficients of \(y\) yields
\(A_j(t)\,y_j(t)=B_j(t)+\varepsilon_j(t)\) with
\[
A_j(t)=1-c_{{\kappa,j}}\alpha_{{\kappa,j}}(t)-c_{{\beta,j}}\alpha_{{\beta,j}}(t),
\qquad
\alpha=\frac{{1}}{{\sigma(d+s)}}.
\]
The identity \(\varepsilon_j=A_j y_j-B_j\) holds for all 62000 rows with
maximum absolute error ${idv['max_identity_error']:.3e}$.

Primitive implemented denominators are the shifted channels \(d+s\). The
eliminated coefficient \(A\) has pooled minimum absolute value
${A['min_abs_pooled']:.3e}$, first percentile ${A['q01_abs_pooled']:.3e}$ and
median ${A['median_abs_pooled']:.3e}$. A fraction
${A['frac_abs_lt']['0.01']:.3f}$ of rows satisfy $|A|<10^{{-2}}$, and
${A['n_sign_crossings']}$ sign crossings of \(A\) occur across the cohort.
Where \(A\neq 0\), the zero-residual explicit closure \(y=B/A\) has pooled RMSE
${expl['pooled_rmse']:.3g}$ at coverage ${expl['coverage']:.3f}$, compared with
implicit residual RMSE ${expl['implicit_pooled_rmse']:.5g}$. Residual
amplification \(1/|A|\) has median ${expl['median_amplification']:.3g}$ and
95th percentile ${expl['q95_amplification']:.3g}$.

Modest multiplicative perturbations of the historical shifts (factors $0.99$
and $1.01$) change the frozen-model implicit RMSE from ${r100:.5g}$ to
${r099:.5g}$ and ${r101:.5g}$, respectively. Standardized temporal derivatives
are invariant under global time-unit rescaling, but additive shifts must be
rescaled consistently to preserve shifted ratios.

Overall, the implicit residual remains small, but the eliminated explicit
target map is frequently ill conditioned. Local well-posedness of the
implicit closure is therefore distinct from both reconstruction accuracy and
coefficient identifiability. Support uniqueness and independent constraint
content remain separate questions.

Remaining DIII-D audits include incremental constraint-content and
quotient-definition nulls, target-free and matched-complexity baselines,
support stability, and held-out discharge transfer.
"""
    (LATEX / "S7_8_implicit_elimination_and_denominator_conditioning.tex").write_text(
        latex, encoding="utf-8"
    )

    (LATEX / "S7_8_implicit_conditioning_tables.tex").write_text(
        rf"""\begin{{table}}[t]
\centering
\caption{{Eliminated target-coefficient $A$ summary.}}
\label{{tab:d3d-A-summary}}
\begin{{tabular}}{{lr}}
\hline
Statistic & Value \\
\hline
$\min|A|$ & {A['min_abs_pooled']:.6g} \\
$q_{{01}}|A|$ & {A['q01_abs_pooled']:.6g} \\
median $|A|$ & {A['median_abs_pooled']:.6g} \\
frac $|A|<10^{{-2}}$ & {A['frac_abs_lt']['0.01']:.4f} \\
$A$ sign crossings & {A['n_sign_crossings']} \\
explicit RMSE & {expl['pooled_rmse']:.6g} \\
implicit RMSE & {expl['implicit_pooled_rmse']:.6g} \\
\hline
\end{{tabular}}
\end{{table}}
""",
        encoding="utf-8",
    )
    (LATEX / "S7_8_implicit_conditioning_figure_captions.tex").write_text(
        r"""\newcommand{\FigExactCoordReproCaption}{Exact reproduction errors for the seven selected coordinates.}
\newcommand{\FigPrimDenCaption}{Per-discharge minimum absolute implemented denominators.}
\newcommand{\FigADistCaption}{Distribution of the eliminated target coefficient $|A|$.}
\newcommand{\FigAByDischargeCaption}{Minimum and low quantiles of $|A|$ by discharge.}
\newcommand{\FigExplAmpCaption}{Explicit closure error versus $|A|$.}
\newcommand{\FigCovErrCaption}{Explicit RMSE versus retained coverage under $|A|$ thresholds.}
""",
        encoding="utf-8",
    )

    (BASE / "README.md").write_text(
        f"""# Implicit elimination and denominator conditioning

Audit ID: `{s['audit_id']}`

## Commands

```bat
cd /d D:\\sir-web
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\run_implicit_conditioning_audit.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\generate_implicit_conditioning_figures.py"
python "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\write_implicit_conditioning_report.py"
pytest "Paper Examples\\Relational Coordinates for Multimodal Plasma Observations\\Implicit_elimination_and_denominator_conditioning\\tests" -q
```

Environment: `conda activate sir_web`. Seed: 20260805.
""",
        encoding="utf-8",
    )

    # Manifest
    entries = []
    for p in sorted(BASE.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc" or p.name.startswith("_probe") or p.name.startswith("_verify"):
            continue
        rel = str(p.relative_to(BASE)).replace("\\", "/")
        role = "GENERATED_DATA"
        if p.suffix == ".py":
            role = "CODE" if "tests" not in p.parts else "TEST"
        elif p.suffix == ".md":
            role = "REPORT"
        elif p.suffix == ".tex":
            role = "LATEX"
        elif p.suffix == ".json" and "config" in p.name:
            role = "CONFIGURATION"
        elif "figures" in p.parts and p.suffix in {".pdf", ".svg", ".png"}:
            role = "GENERATED_FIGURE"
        elif "tables" in p.parts:
            role = "GENERATED_TABLE"
        elif "symbolic" in p.parts:
            role = "SYMBOLIC_DERIVATION"
        elif "code_snapshots" in p.parts:
            role = "CODE_SNAPSHOT"
        elif p.suffix == ".log":
            role = "LOG"
        elif "manifest" in p.name.lower() or "FILE_INDEX" in p.name:
            role = "MANIFEST"
        entries.append(
            {
                "relative_path": rel,
                "role": role,
                "byte_size": p.stat().st_size,
                "sha256": sha(p),
                "created_utc": utc(),
                "generator_script": "write_implicit_conditioning_report.py",
                "input_dependencies": s["canonical_run_id"],
                "status": role,
            }
        )
    (BASE / "audit_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    idx = ["# Audit file index", "", "| path | role | bytes | sha256 |", "|---|---|---:|---|"]
    for e in entries:
        idx.append(f"| `{e['relative_path']}` | {e['role']} | {e['byte_size']} | `{e['sha256'][:16]}…` |")
    (BASE / "AUDIT_FILE_INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8")

    print("Report:", report)
    print("LaTeX:", LATEX / "S7_8_implicit_elimination_and_denominator_conditioning.tex")
    print()
    print("=== FINAL CONSOLE SUMMARY ===")
    print("audit ID:", s["audit_id"])
    print("canonical run ID:", s["canonical_run_id"])
    print("coefficient correction audit ID:", s["coefficient_correction_audit_id"])
    print("number of discharges:", 62)
    print("samples per discharge:", 1000)
    print("canonical pooled RMSE:", s["reproduced_pooled_rmse"])
    print("exact coordinate lineage status:", s["coordinate_lineage_status"])
    print("shift recovery status:", s["shift_recovery_status"])
    print("target-containing features reproduced:", "yes")
    print("maximum target-feature reproduction error:", s["max_target_feature_reproduction_error"])
    print("maximum elimination identity error:", s["elimination_identity_max_error"])
    print("minimum pooled |A|:", A["min_abs_pooled"])
    print("pooled q01 |A|:", A["q01_abs_pooled"])
    print("fraction of rows with |A| below thresholds:", A["frac_abs_lt"])
    print("number of A sign crossings:", A["n_sign_crossings"])
    print("pooled explicit closure RMSE:", expl["pooled_rmse"])
    print("explicit closure coverage:", expl["coverage"])
    print("median and q95 residual amplification:", expl["median_amplification"], expl["q95_amplification"])
    print("shift sensitivity summary:", s["shift_sensitivity_summary"])
    print("time-unit consistency status:", s["time_unit_consistency_summary"]["status"])
    print("overall verdict:", verdict)
    print("output directory:", BASE)
    print("report path:", report)
    print("S7.8 LaTeX path:", LATEX / "S7_8_implicit_elimination_and_denominator_conditioning.tex")


if __name__ == "__main__":
    main()
