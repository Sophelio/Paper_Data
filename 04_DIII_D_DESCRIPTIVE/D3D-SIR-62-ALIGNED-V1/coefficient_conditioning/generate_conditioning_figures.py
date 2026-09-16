#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate PDF/SVG/PNG figures for the coefficient-conditioning audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
FIG = BASE / "figures"
TAB = BASE / "tables"
OUT = BASE / "outputs"
FIG.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_fig(fig, stem: str, description: str, inputs: str, manifest_rows: list):
    paths = {}
    for ext in ("pdf", "svg", "png"):
        p = FIG / f"{stem}.{ext}"
        fig.savefig(p, dpi=200 if ext == "png" else None, bbox_inches="tight")
        paths[ext] = p
    plt.close(fig)
    manifest_rows.append(
        {
            "figure_id": stem,
            "filename_pdf": paths["pdf"].name,
            "filename_svg": paths["svg"].name,
            "filename_png": paths["png"].name,
            "description": description,
            "source_script": "generate_conditioning_figures.py",
            "input_tables": inputs,
            "sha256_pdf": sha256_file(paths["pdf"]),
            "sha256_svg": sha256_file(paths["svg"]),
            "sha256_png": sha256_file(paths["png"]),
        }
    )


def main():
    cond = pd.read_csv(TAB / "d3d_conditioning_per_discharge.csv")
    sv = pd.read_csv(TAB / "d3d_singular_values_long.csv")
    corr_sum = pd.read_csv(TAB / "d3d_correlation_summary.csv")
    vif = pd.read_csv(TAB / "d3d_vif_per_discharge.csv")
    near = pd.read_csv(TAB / "d3d_near_null_loadings.csv")
    trunc = pd.read_csv(TAB / "d3d_coefficient_truncation_sensitivity.csv")
    boot = pd.read_csv(TAB / "d3d_bootstrap_coefficient_summary.csv")
    het = pd.read_csv(TAB / "d3d_coefficient_heterogeneity.csv")
    state = json.loads((OUT / "coefficient_conditioning_summary.json").read_text(encoding="utf-8"))
    keys = state["source_matrix_order"]
    manifest_rows = []

    # 1 singular spectrum
    fig, ax = plt.subplots(figsize=(7, 4))
    for shot, g in sv.groupby("shot"):
        ax.plot(g["singular_index"], g["normalized_sigma"], color="0.7", lw=0.6, alpha=0.5)
    med = sv.groupby("singular_index")["normalized_sigma"].median()
    q1 = sv.groupby("singular_index")["normalized_sigma"].quantile(0.25)
    q3 = sv.groupby("singular_index")["normalized_sigma"].quantile(0.75)
    ax.fill_between(med.index, q1, q3, color="C0", alpha=0.3, label="IQR")
    ax.plot(med.index, med.values, color="C0", lw=2, label="median")
    ax.set_xlabel("Singular index")
    ax.set_ylabel(r"$\sigma_r / \sigma_1$")
    ax.set_title("Normalized singular spectrum by discharge")
    ax.legend()
    save_fig(fig, "singular_spectrum_by_discharge", "Normalized singular values", "d3d_singular_values_long.csv", manifest_rows)

    # 2 condition number
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.semilogy(cond["realization_index"], cond["condition_number"], "o", ms=3)
    ax.set_xlabel("realization_index")
    ax.set_ylabel(r"$\kappa_2(X)$")
    ax.set_title("Spectral condition number by discharge")
    save_fig(fig, "condition_number_by_discharge", "Condition numbers", "d3d_conditioning_per_discharge.csv", manifest_rows)

    # 3 correlation summary heatmap (median)
    feats = sorted(set(corr_sum["feature_1"]).union(corr_sum["feature_2"]))
    # use source order
    feats = keys
    M = np.eye(len(feats))
    Mabs = np.eye(len(feats))
    idx = {f: i for i, f in enumerate(feats)}
    for _, r in corr_sum.iterrows():
        i, j = idx[r["feature_1"]], idx[r["feature_2"]]
        M[i, j] = M[j, i] = r["median_correlation"]
        Mabs[i, j] = Mabs[j, i] = r["max_abs_correlation"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    im0 = axes[0].imshow(M, vmin=-1, vmax=1, cmap="coolwarm")
    axes[0].set_xticks(range(7))
    axes[0].set_yticks(range(7))
    axes[0].set_xticklabels(feats, rotation=90, fontsize=7)
    axes[0].set_yticklabels(feats, fontsize=7)
    axes[0].set_title("Median correlation")
    fig.colorbar(im0, ax=axes[0], fraction=0.046)
    im1 = axes[1].imshow(Mabs, vmin=0, vmax=1, cmap="viridis")
    axes[1].set_xticks(range(7))
    axes[1].set_yticks(range(7))
    axes[1].set_xticklabels(feats, rotation=90, fontsize=7)
    axes[1].set_yticklabels(feats, fontsize=7)
    axes[1].set_title("Max |correlation|")
    fig.colorbar(im1, ax=axes[1], fraction=0.046)
    fig.tight_layout()
    save_fig(fig, "feature_correlation_summary", "Correlation matrices", "d3d_correlation_summary.csv", manifest_rows)

    # 4 VIF
    fig, ax = plt.subplots(figsize=(8, 4))
    data = [vif.loc[vif.feature == k, "vif"].replace(np.inf, np.nan).dropna().values for k in keys]
    ax.boxplot(data, orientation="vertical")
    ax.set_xticks(range(1, len(keys) + 1))
    ax.set_xticklabels([k.replace("d[", "").replace("]", "")[:18] for k in keys])
    ax.set_yscale("log")
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)
    ax.set_ylabel("VIF")
    ax.set_title("VIF distributions by feature")
    fig.tight_layout()
    save_fig(fig, "vif_distributions", "VIF by feature", "d3d_vif_per_discharge.csv", manifest_rows)

    # 5 near-null loadings
    fig, ax = plt.subplots(figsize=(8, 4))
    data = [near.loc[near.feature == k, "absolute_loading"].values for k in keys]
    ax.boxplot(data)
    ax.set_xticks(range(1, len(keys) + 1))
    ax.set_xticklabels([k[:22] for k in keys])
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)
    ax.set_ylabel("|loading| on v_min")
    ax.set_title("Near-null direction absolute loadings")
    fig.tight_layout()
    save_fig(fig, "near_null_direction_loadings", "Near-null loadings", "d3d_near_null_loadings.csv", manifest_rows)

    # 6 truncation sensitivity
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for tau, g in trunc.groupby("tolerance"):
        axes[0].plot(
            sorted(g["realization_index"]),
            g.sort_values("realization_index")["relative_coefficient_change"],
            "o-",
            ms=2,
            label=f"tau={tau:g}",
        )
        axes[1].plot(
            sorted(g["realization_index"]),
            g.sort_values("realization_index")["abs_rmse_change"],
            "o-",
            ms=2,
            label=f"tau={tau:g}",
        )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("realization_index")
    axes[0].set_ylabel("relative coefficient change")
    axes[0].legend(fontsize=7)
    axes[0].set_title("Coefficient change")
    axes[1].set_xlabel("realization_index")
    axes[1].set_ylabel("|ΔRMSE|")
    axes[1].legend(fontsize=7)
    axes[1].set_title("Reconstruction change")
    fig.tight_layout()
    save_fig(fig, "coefficient_truncation_sensitivity", "Truncation sensitivity", "d3d_coefficient_truncation_sensitivity.csv", manifest_rows)

    # 7 bootstrap coefficients (faceted)
    nfeat = len(keys)
    fig, axes = plt.subplots(nfeat, 1, figsize=(8, 1.6 * nfeat), sharex=True)
    if nfeat == 1:
        axes = [axes]
    for ax, key in zip(axes, keys):
        g = boot[boot.feature == key].sort_values("realization_index")
        x = g["realization_index"].to_numpy()
        y = g["canonical_estimate"].to_numpy()
        lo = g["q025"].to_numpy()
        hi = g["q975"].to_numpy()
        ax.fill_between(x, lo, hi, color="C0", alpha=0.25)
        ax.plot(x, y, "o", ms=2, color="C0")
        ax.axhline(0, color="k", lw=0.5)
        ax.set_ylabel(key[:28], fontsize=7)
    axes[-1].set_xlabel("realization_index")
    fig.suptitle("Canonical coefficients with 95% block-bootstrap intervals", fontsize=10)
    fig.tight_layout()
    save_fig(fig, "bootstrap_coefficients_by_discharge", "Bootstrap intervals", "d3d_bootstrap_coefficient_summary.csv", manifest_rows)

    # 8 between vs within
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(het))
    w = 0.35
    ax.bar(x - w / 2, het["observed_between_variance"], w, label="between")
    ax.bar(x + w / 2, het["mean_within_variance"], w, label="mean within")
    ax.set_xticks(x)
    ax.set_xticklabels([k[:18] for k in het["feature"]], rotation=90, fontsize=7)
    ax.set_yscale("log")
    ax.legend()
    ax.set_title("Between- vs within-discharge variance")
    fig.tight_layout()
    save_fig(fig, "between_vs_within_variance", "Variance comparison", "d3d_coefficient_heterogeneity.csv", manifest_rows)

    # 9 resolved fraction
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - w / 2, het["resolved_fraction"], w, label="resolved fraction")
    ax.bar(x + w / 2, het["heterogeneity_ratio"].replace(np.inf, np.nan), w, label="H ratio")
    ax.set_xticks(x)
    ax.set_xticklabels([k[:18] for k in het["feature"]], rotation=90, fontsize=7)
    ax.legend()
    ax.set_title("Resolved fraction and heterogeneity ratio")
    fig.tight_layout()
    save_fig(fig, "resolved_fraction_by_coefficient", "Heterogeneity metrics", "d3d_coefficient_heterogeneity.csv", manifest_rows)

    # 10 uncertainty vs conditioning
    fig, ax = plt.subplots(figsize=(5.5, 4))
    mean_sd = boot.groupby("realization_index")["bootstrap_standard_deviation"].mean()
    ax.scatter(np.log10(cond["condition_number"]), mean_sd.loc[cond["realization_index"]].values, s=12)
    ax.set_xlabel(r"$\log_{10} \kappa_2$")
    ax.set_ylabel("mean bootstrap SD")
    ax.set_title("Coefficient uncertainty vs conditioning")
    save_fig(fig, "coefficient_uncertainty_vs_conditioning", "Uncertainty vs kappa", "conditioning+bootstrap", manifest_rows)

    # 11 multivariate directions
    mv = pd.read_csv(TAB / "d3d_multivariate_variance_eigenvectors.csv")
    evals = mv.drop_duplicates("eigen_index").sort_values("eigen_index")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    axes[0].plot(evals["eigen_index"], evals["eigenvalue_raw"], "o-")
    axes[0].axhline(0, color="k", lw=0.5)
    axes[0].set_title("Difference-covariance eigenvalues")
    axes[0].set_xlabel("eigen_index")
    # top resolved loadings
    top = mv[mv["resolved_flag"]].copy()
    if len(top):
        eidx = top.groupby("eigen_index")["eigenvalue_raw"].first().sort_values(ascending=False).index[:2]
        for e in eidx:
            g = top[top.eigen_index == e]
            axes[1].plot(range(len(g)), g["loading_source_order"], "o-", label=f"eig {e}")
        axes[1].set_xticks(range(7))
        axes[1].set_xticklabels([k[:12] for k in keys], rotation=90, fontsize=7)
        axes[1].legend(fontsize=7)
    axes[1].set_title("Resolved direction loadings")
    fig.tight_layout()
    save_fig(fig, "multivariate_resolved_directions", "Multivariate directions", "d3d_multivariate_variance_eigenvectors.csv", manifest_rows)

    # 12 rmse vs conditioning
    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.scatter(np.log10(cond["condition_number"]), cond["rmse"], s=12)
    ax.set_xlabel(r"$\log_{10} \kappa_2$")
    ax.set_ylabel("RMSE")
    ax.set_title("Reconstruction RMSE vs conditioning")
    save_fig(fig, "rmse_vs_conditioning", "RMSE vs kappa", "d3d_conditioning_per_discharge.csv", manifest_rows)

    pd.DataFrame(manifest_rows).to_csv(FIG / "figure_manifest.csv", index=False)
    print(f"Wrote {len(manifest_rows)} figures to {FIG}")


if __name__ == "__main__":
    main()
