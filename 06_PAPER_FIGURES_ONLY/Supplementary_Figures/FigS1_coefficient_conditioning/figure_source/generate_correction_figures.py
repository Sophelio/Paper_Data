#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate PDF/SVG/PNG figures for the correction audit."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

if os.name == "nt":
    os.environ.setdefault("MIKTEX_UNATTENDED", "1")
    os.environ.setdefault("MIKTEX_AUTOINSTALL", "1")
    _miktex_bin = Path.home() / r"AppData\Local\Programs\MiKTeX\miktex\bin\x64"
    if _miktex_bin.is_dir():
        os.environ["PATH"] = str(_miktex_bin) + os.pathsep + os.environ.get("PATH", "")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Both locations can be overridden so the figures can be rendered outside the
# audit tree (e.g. by render_figS1.py) without writing into the frozen package.
BASE = Path(os.environ.get("CORRECTION_AUDIT_DIR", Path(__file__).resolve().parent))
OUT = BASE / "outputs"
TAB = BASE / "tables"
FIG = Path(os.environ.get("CORRECTION_FIGURE_DIR", BASE / "figures"))
FIG.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Manuscript typography: Latin Modern through LaTeX. Font sizes and canvases
# are the original ones (matplotlib defaults plus the per-site values below).
# The style is applied only to the three Supplementary Figure S1 panels (via
# rc_context); the other audit figures keep matplotlib defaults.
# ---------------------------------------------------------------------------
# Pin the 10 pt Latin Modern design at every size (copied verbatim from
# Figure 6); otherwise lmodern switches to wider optical designs below 10 pt.
LM_DESIGN_SIZE_PIN = (
    r"\DeclareFontFamily{T1}{lmr}{}"
    r"\DeclareFontShape{T1}{lmr}{m}{n}{<-> ec-lmr10}{}"
    r"\DeclareFontShape{T1}{lmr}{m}{it}{<-> ec-lmri10}{}"
    r"\DeclareFontShape{T1}{lmr}{bx}{n}{<-> ec-lmbx10}{}"
    r"\DeclareFontShape{T1}{lmr}{bx}{it}{<-> ec-lmbxi10}{}"
    r"\DeclareFontShape{T1}{lmr}{b}{n}{<->ssub * lmr/bx/n}{}"
    r"\DeclareFontFamily{OT1}{lmr}{}"
    r"\DeclareFontShape{OT1}{lmr}{m}{n}{<-> rm-lmr10}{}"
    r"\DeclareFontShape{OT1}{lmr}{m}{it}{<-> rm-lmri10}{}"
    r"\DeclareFontShape{OT1}{lmr}{bx}{n}{<-> rm-lmbx10}{}"
    r"\DeclareFontShape{OT1}{lmr}{b}{n}{<->ssub * lmr/bx/n}{}"
    r"\DeclareFontFamily{OML}{lmm}{\skewchar\font127 }"
    r"\DeclareFontShape{OML}{lmm}{m}{it}{<-> lmmi10}{}"
    r"\DeclareFontShape{OML}{lmm}{b}{it}{<-> lmmib10}{}"
    r"\DeclareFontShape{OML}{lmm}{bx}{it}{<->ssub * lmm/b/it}{}"
    r"\DeclareFontFamily{OMS}{lmsy}{\skewchar\font48 }"
    r"\DeclareFontShape{OMS}{lmsy}{m}{n}{<-> lmsy10}{}"
    r"\DeclareFontShape{OMS}{lmsy}{b}{n}{<-> lmbsy10}{}"
)

S1_STYLE = {
    "text.usetex": True,
    "font.family": "serif",
    "text.latex.preamble": (
        r"\usepackage[T1]{fontenc}"
        r"\usepackage{lmodern}"
        r"\usepackage{amsmath,amssymb}"
        + LM_DESIGN_SIZE_PIN
    ),
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "path",
}


def bold(text: str) -> str:
    return r"\textbf{" + text + "}"


# LaTeX notation for the coefficient display names; identical to the mapping
# used in Figure 6 (d3d_task_conditioned_4panel_v5.py, COORD_MATH).
COORD_MATH = {
    "D_kappa W_dia": r"$D_{\kappa}^{(s)}W_{\mathrm{dia}}$",
    "D_betaN W_dia": r"$D_{\beta_N}^{(s)}W_{\mathrm{dia}}$",
    "D_betaN kappa": r"$D_{\beta_N}^{(s)}\kappa$",
    "D_betaN l_i": r"$D_{\beta_N}^{(s)}\ell_i$",
    "q95 / kappa": r"$\left(\frac{q_{95}}{\kappa}\right)^{(s)}$",
    "dot beta_N": r"$\dot{\beta}_N$",
    "dot kappa": r"$\dot{\kappa}$",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_fig(fig, stem: str, description: str, inputs: str, manifest_rows: list):
    pdf = FIG / f"{stem}.pdf"
    svg = FIG / f"{stem}.svg"
    png = FIG / f"{stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    manifest_rows.append(
        {
            "figure_id": stem,
            "filename_pdf": pdf.name,
            "filename_svg": svg.name,
            "filename_png": png.name,
            "description": description,
            "source_script": "generate_correction_figures.py",
            "input_tables": inputs,
            "sha256_pdf": sha256_file(pdf),
            "sha256_svg": sha256_file(svg),
            "sha256_png": sha256_file(png),
        }
    )


def main():
    rows = []
    cfg = json.loads((BASE / "correction_audit_config.json").read_text(encoding="utf-8"))
    keys = cfg["source_matrix_order_keys"]
    disp = {m["key"]: m["display"] for m in cfg["manuscript_display_order"]}

    thresh = pd.read_csv(TAB / "corrected_tsvd_fixed_threshold.csv")
    frank = pd.read_csv(TAB / "corrected_tsvd_fixed_rank.csv")
    ridge = pd.read_csv(TAB / "d3d_ridge_path_per_discharge.csv")
    sens = pd.read_csv(TAB / "corrected_coefficient_heterogeneity_block_sensitivity.csv")
    primary = pd.read_csv(TAB / "corrected_coefficient_heterogeneity_primary.csv")
    loo = pd.read_csv(TAB / "corrected_coefficient_heterogeneity_leave_one_out.csv")
    class_df = pd.read_csv(TAB / "corrected_coefficient_classification.csv")
    eigs = pd.read_csv(TAB / "d3d_multivariate_eigenvalue_intervals.csv")
    loads = pd.read_csv(TAB / "d3d_multivariate_loading_intervals.csv")
    cond = pd.read_csv(
        BASE.parent / "tables" / "d3d_conditioning_per_discharge.csv"
    ).sort_values("realization_index")
    boot_sum = pd.read_csv(BASE.parent / "tables" / "d3d_bootstrap_coefficient_summary.csv")

    # 1. actual_singular_direction_removal
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for tau, g in thresh.groupby("tolerance"):
        ax[0].scatter(
            np.full(len(g), np.log10(tau)),
            g["retained_rank"],
            alpha=0.25,
            s=12,
            label=None,
        )
    med = thresh.groupby("tolerance")["retained_rank"].median()
    ax[0].plot(np.log10(med.index.to_numpy()), med.to_numpy(), "k-o", label="median")
    ax[0].set_xlabel("log10 relative threshold")
    ax[0].set_ylabel("retained rank")
    ax[0].set_title("Fixed relative thresholds")
    ax[0].set_ylim(0, 7.5)
    for rk, g in frank.groupby("retained_rank"):
        ax[1].scatter(np.full(len(g), rk), g["n_directions_removed"], alpha=0.25, s=12)
    ax[1].set_xlabel("retained rank (fixed)")
    ax[1].set_ylabel("directions removed")
    ax[1].set_title("Fixed-rank truncation")
    fig.suptitle("Actual singular-direction removal")
    save_fig(
        fig,
        "actual_singular_direction_removal",
        "Retained rank under meaningful truncation",
        "corrected_tsvd_fixed_threshold.csv;corrected_tsvd_fixed_rank.csv",
        rows,
    )

    # 2. coefficient_change_vs_rank_removed  (Supplementary Figure S1a)
    with mpl.rc_context(S1_STYLE):
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        for rk in [7, 6, 5, 4]:
            g = frank[frank.retained_rank == rk]
            ax[0].boxplot(g["relative_coefficient_change"], positions=[7 - rk], widths=0.6)
            ax[1].boxplot(g["absolute_rmse_change"], positions=[7 - rk], widths=0.6)
        ax[0].set_xticks([0, 1, 2, 3])
        ax[0].set_xticklabels(["0", "1", "2", "3"])
        ax[1].set_xticks([0, 1, 2, 3])
        ax[1].set_xticklabels(["0", "1", "2", "3"])
        ax[0].set_xlabel("singular directions removed")
        ax[1].set_xlabel("singular directions removed")
        ax[0].set_ylabel("relative coefficient change")
        ax[1].set_ylabel(r"absolute $\mathrm{RMSE}$ change")
        ax[0].set_title(bold("Coefficient movement"))
        ax[1].set_title(bold("Reconstruction change"))
        fig.suptitle(bold("Coefficient change versus rank removed"))
        save_fig(
            fig,
            "coefficient_change_vs_rank_removed",
            "Coefficient vs RMSE change under fixed-rank truncation",
            "corrected_tsvd_fixed_rank.csv",
            rows,
        )

    # 3. ridge_path_coefficient_stability
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for lr, g in ridge.groupby("lambda_relative"):
        ax[0].scatter(np.full(len(g), np.log10(lr + 1e-16)), g["relative_coefficient_change"], s=8, alpha=0.2)
        ax[1].scatter(np.full(len(g), np.log10(lr + 1e-16)), g["absolute_rmse_change"], s=8, alpha=0.2)
    med_c = ridge.groupby("lambda_relative")["relative_coefficient_change"].median()
    med_r = ridge.groupby("lambda_relative")["absolute_rmse_change"].median()
    x = np.log10(med_c.index.to_numpy() + 1e-16)
    ax[0].plot(x, med_c.to_numpy(), "k-o")
    ax[1].plot(x, med_r.to_numpy(), "k-o")
    ax[0].set_xlabel("log10(lambda_relative + 1e-16)")
    ax[1].set_xlabel("log10(lambda_relative + 1e-16)")
    ax[0].set_ylabel("relative coefficient change")
    ax[1].set_ylabel("absolute RMSE change")
    fig.suptitle("Ridge-path sensitivity")
    save_fig(fig, "ridge_path_coefficient_stability", "Ridge path stability", "d3d_ridge_path_per_discharge.csv", rows)

    # 4. corrected_between_vs_within_variance
    fig, ax = plt.subplots(figsize=(9, 4.5))
    settings = ["primary", "short", "long"]
    x = np.arange(len(keys))
    width = 0.25
    for i, s in enumerate(settings):
        sub = sens[sens.block_setting == s].set_index("feature").reindex(keys)
        ax.bar(x + (i - 1) * width, sub["observed_between_variance"] if i == 0 else sub["mean_within_variance"], width, label=f"{s} within" if i else "between (shared)")
    # clearer: plot H ratio
    ax.cla()
    for i, s in enumerate(settings):
        sub = sens[sens.block_setting == s].set_index("feature").reindex(keys)
        ax.bar(x + (i - 1) * width, sub["heterogeneity_ratio"], width, label=s)
    ax.axhline(1.0, color="k", ls="--", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([disp[k] for k in keys], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("heterogeneity ratio H")
    ax.set_title("Between vs within variance (H) by block setting")
    ax.legend()
    save_fig(
        fig,
        "corrected_between_vs_within_variance",
        "Heterogeneity ratio by block length",
        "corrected_coefficient_heterogeneity_block_sensitivity.csv",
        rows,
    )

    # 5. heterogeneity_interval_by_coefficient  (Supplementary Figure S1b)
    with mpl.rc_context(S1_STYLE):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        y = np.arange(len(keys))
        p = primary.set_index("feature").reindex(keys)
        ax.errorbar(
            p["tau2_REML"],
            y,
            xerr=[
                p["tau2_REML"] - p["tau2_REML_interval_low"],
                p["tau2_REML_interval_high"] - p["tau2_REML"],
            ],
            fmt="o",
            capsize=3,
        )
        ax.set_yticks(y)
        ax.set_yticklabels([COORD_MATH[disp[k]] for k in keys], fontsize=8)
        ax.set_xlabel(r"$\tau^2$ (REML) with profile interval")
        ax.set_title(bold("Corrected heterogeneity intervals"))
        ax.set_xscale("symlog", linthresh=1e-6)
        save_fig(
            fig,
            "heterogeneity_interval_by_coefficient",
            "REML tau2 intervals",
            "corrected_coefficient_heterogeneity_primary.csv",
            rows,
        )

    # 6. leave_one_out_heterogeneity
    fig, ax = plt.subplots(figsize=(9, 4.5))
    data = [loo.loc[loo.feature == k, "tau2_REML"].to_numpy() for k in keys]
    ax.boxplot(data)  # vertical is the default in every matplotlib version
    ax.set_xticks(range(1, len(keys) + 1))
    ax.set_xticklabels([disp[k] for k in keys], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(r"LOO $\tau^2$")
    ax.set_title("Leave-one-discharge-out $\\tau^2$ sensitivity")
    ax.set_yscale("symlog", linthresh=1e-6)
    save_fig(
        fig,
        "leave_one_out_heterogeneity",
        "LOO tau2 sensitivity",
        "corrected_coefficient_heterogeneity_leave_one_out.csv",
        rows,
    )

    # 7. multivariate_eigenvalue_uncertainty  (Supplementary Figure S1c)
    with mpl.rc_context(S1_STYLE):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        idx = eigs["eigenvalue_index"]
        ax.errorbar(
            idx,
            eigs["observed_eigenvalue"],
            yerr=[
                eigs["observed_eigenvalue"] - eigs["boot_q025"],
                eigs["boot_q975"] - eigs["observed_eigenvalue"],
            ],
            fmt="o",
            capsize=3,
            label=r"observed $\pm$ bootstrap 95\%",
        )
        ax.plot(idx, eigs["null_q95"], "s--", label="null 95th percentile")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xlabel("ordered eigenvalue index")
        ax.set_ylabel("eigenvalue of $\\Sigma_B-\\Sigma_W$")
        ax.legend(fontsize=8)
        ax.set_title(bold("Multivariate eigenvalue uncertainty"))
        save_fig(
            fig,
            "multivariate_eigenvalue_uncertainty",
            "Bootstrap intervals and null thresholds for eigenvalues",
            "d3d_multivariate_eigenvalue_intervals.csv",
            rows,
        )

    # 8. robust_multivariate_direction_loadings
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if len(loads):
        for j, g in loads.groupby("eigenvalue_index"):
            g = g.set_index("feature").reindex(keys)
            ax.errorbar(
                np.arange(len(keys)) + 0.05 * (j - 1),
                g["observed_loading"],
                yerr=[g["observed_loading"] - g["boot_q025"], g["boot_q975"] - g["observed_loading"]],
                fmt="o",
                capsize=2,
                label=f"direction {j}",
            )
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels([disp[k] for k in keys], rotation=45, ha="right", fontsize=8)
        ax.axhline(0, color="k", lw=0.8)
        ax.legend(fontsize=8)
    else:
        ax.text(0.5, 0.5, "No robust multivariate directions", ha="center")
        ax.set_axis_off()
    ax.set_ylabel("loading")
    ax.set_title("Robust multivariate direction loadings")
    save_fig(
        fig,
        "robust_multivariate_direction_loadings",
        "Loadings for robustly resolved directions",
        "d3d_multivariate_loading_intervals.csv",
        rows,
    )

    # 9. corrected_coefficient_classification
    fig, ax = plt.subplots(figsize=(8, 3.5))
    order = [
        "ROBUSTLY_RESOLVED",
        "PARTIALLY_RESOLVED",
        "WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES",
        "INDETERMINATE",
    ]
    counts = class_df["corrected_status"].value_counts().reindex(order).fillna(0)
    ax.bar(range(len(order)), counts.to_numpy())
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["Robust", "Partial", "Within-dom.", "Indet."], fontsize=9)
    ax.set_ylabel("number of coefficients")
    for i, k in enumerate(keys):
        st = class_df.loc[class_df.feature == k, "corrected_status"].iloc[0]
        ax.annotate(disp[k], xy=(order.index(st), counts[st]), fontsize=6, rotation=30, alpha=0.0)
    # text list
    labels = []
    for st in order:
        feats = class_df.loc[class_df.corrected_status == st, "display_name"].tolist()
        if feats:
            labels.append(f"{st}: " + ", ".join(feats))
    ax.set_title("Corrected coefficient classifications\n" + "\n".join(labels), fontsize=8)
    save_fig(
        fig,
        "corrected_coefficient_classification",
        "Corrected per-coefficient status counts",
        "corrected_coefficient_classification.csv",
        rows,
    )

    # 10. conditioning_vs_corrected_uncertainty
    fig, ax = plt.subplots(figsize=(7, 4.5))
    # mean bootstrap sd vs condition number
    for k in keys:
        sub = boot_sum[boot_sum.feature == k].sort_values("realization_index")
        ax.scatter(
            np.log10(cond["condition_number"]),
            sub["bootstrap_standard_deviation"],
            s=10,
            alpha=0.5,
            label=disp[k],
        )
    ax.set_xlabel("log10 condition number")
    ax.set_ylabel("primary bootstrap SD")
    ax.legend(fontsize=6, ncol=2)
    ax.set_title("Coefficient uncertainty versus conditioning")
    save_fig(
        fig,
        "conditioning_vs_corrected_uncertainty",
        "Bootstrap SD vs condition number",
        "d3d_conditioning_per_discharge.csv;d3d_bootstrap_coefficient_summary.csv",
        rows,
    )

    pd.DataFrame(rows).to_csv(FIG / "correction_figure_manifest.csv", index=False)
    print(f"Wrote {len(rows)} figures to {FIG}")


if __name__ == "__main__":
    main()
