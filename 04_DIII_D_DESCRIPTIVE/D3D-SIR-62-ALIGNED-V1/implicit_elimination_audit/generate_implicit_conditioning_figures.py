#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate PDF/SVG/PNG figures for the implicit-conditioning audit."""
from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
OUT, TAB, FIG = BASE / "outputs", BASE / "tables", BASE / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def save(fig, stem, desc, inputs, rows):
    for ext in ("pdf", "svg", "png"):
        kw = {"dpi": 200} if ext == "png" else {}
        fig.savefig(FIG / f"{stem}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)
    rows.append(
        {
            "figure_id": stem,
            "filename_pdf": f"{stem}.pdf",
            "filename_svg": f"{stem}.svg",
            "filename_png": f"{stem}.png",
            "description": desc,
            "source_script": "generate_implicit_conditioning_figures.py",
            "input_tables": inputs,
            "sha256_pdf": sha(FIG / f"{stem}.pdf"),
            "sha256_svg": sha(FIG / f"{stem}.svg"),
            "sha256_png": sha(FIG / f"{stem}.png"),
        }
    )


def main():
    rows = []
    repro = pd.read_csv(TAB / "feature_reproduction_per_discharge.csv")
    den = pd.read_csv(TAB / "primitive_denominator_per_discharge.csv")
    Aper = pd.read_csv(TAB / "eliminated_A_per_discharge.csv")
    elim = pd.read_parquet(OUT / "eliminated_relation_rows.parquet")
    curve = pd.read_csv(TAB / "explicit_closure_threshold_curve.csv")
    fb = pd.read_csv(TAB / "target_feedback_decomposition.csv")
    cross = pd.read_csv(TAB / "eliminated_A_crossings.csv")
    frozen = pd.read_csv(TAB / "shift_sensitivity_frozen_model.csv")
    refit = pd.read_csv(TAB / "shift_sensitivity_refit.csv")
    deg = pd.read_csv(TAB / "local_degeneracy_classification.csv")
    tunit = pd.read_csv(TAB / "time_unit_consistency.csv")

    # 1
    fig, ax = plt.subplots(figsize=(8, 4))
    for feat, g in repro.groupby("display_name"):
        ax.scatter(g.realization_index, g.max_abs_diff + 1e-20, s=10, label=feat)
    ax.set_yscale("log")
    ax.set_xlabel("realization index")
    ax.set_ylabel("max |repro error|")
    ax.legend(fontsize=6, ncol=2)
    ax.set_title("Exact coordinate reproduction")
    save(fig, "exact_coordinate_reproduction", "Feature reproduction errors", "feature_reproduction_per_discharge.csv", rows)

    # 2
    fig, ax = plt.subplots(figsize=(8, 4))
    dens = den["denominator"].unique()
    data = [den.loc[den.denominator == d, "min_abs"].to_numpy() for d in dens]
    ax.boxplot(data, orientation="vertical")
    ax.set_xticks(range(1, len(dens) + 1))
    ax.set_xticklabels(dens, rotation=30, ha="right", fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("min |denominator|")
    ax.set_title("Primitive denominator distributions (min abs per discharge)")
    save(fig, "primitive_denominator_distributions", "Denominator min-abs", "primitive_denominator_per_discharge.csv", rows)

    # 3
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].hist(np.abs(elim["A"]), bins=80, log=True)
    ax[0].set_xlabel("|A|")
    ax[0].set_title("Pooled |A|")
    ax[1].boxplot([np.abs(elim.loc[elim.realization_index == i, "A"]) for i in range(0, 62, 5)], orientation="vertical")
    ax[1].set_yscale("log")
    ax[1].set_title("|A| sample of discharges")
    save(fig, "eliminated_A_distribution", "|A| distributions", "eliminated_relation_rows.parquet", rows)

    # 4
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(Aper.realization_index, Aper.min_abs_A, "o-", ms=3, label="min |A|")
    ax.plot(Aper.realization_index, Aper.q01_abs_A, "s-", ms=3, label="q01 |A|")
    ax.plot(Aper.realization_index, Aper.median_abs_A, "^-", ms=3, label="median |A|")
    ax.set_yscale("log")
    ax.legend(fontsize=8)
    ax.set_xlabel("realization index")
    ax.set_ylabel("|A|")
    ax.set_title("Eliminated A by discharge")
    save(fig, "eliminated_A_by_discharge", "A quantiles by discharge", "eliminated_A_per_discharge.csv", rows)

    # 5
    fig, ax = plt.subplots(figsize=(7, 4.5))
    m = np.isfinite(elim.explicit_error) & (np.abs(elim.A) > 0)
    ax.scatter(np.abs(elim.A[m]), np.abs(elim.explicit_error[m]), s=1, alpha=0.05)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("|A|")
    ax.set_ylabel("|explicit error|")
    ax.set_title("Explicit error amplification")
    save(fig, "explicit_error_amplification", "Explicit error vs |A|", "eliminated_relation_rows.parquet", rows)

    # 6
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(curve.retained_fraction, curve.pooled_explicit_rmse, "o-")
    ax.set_xlabel("retained coverage (|A| >= tau)")
    ax.set_ylabel("pooled explicit RMSE")
    ax.set_yscale("log")
    ax.set_title("Explicit coverage–error curve")
    save(fig, "explicit_coverage_error_curve", "Coverage vs explicit RMSE", "explicit_closure_threshold_curve.csv", rows)

    # 7
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(fb.F_kappa_median, fb.F_betan_median, c=np.arange(len(fb)), s=20)
    ax.set_xlabel("median F_kappa")
    ax.set_ylabel("median F_betan")
    ax.set_title("Target-feedback decomposition")
    save(fig, "target_feedback_decomposition", "Feedback contributions", "target_feedback_decomposition.csv", rows)

    # 8
    fig, ax = plt.subplots(figsize=(9, 4))
    if len(cross):
        ax.scatter(cross.realization_index, cross.sample_index_left, s=2, alpha=0.3)
    ax.set_xlabel("realization index")
    ax.set_ylabel("sample index of A sign crossing")
    ax.set_title("A sign-crossing map")
    save(fig, "denominator_crossing_map", "A crossings by discharge", "eliminated_A_crossings.csv", rows)

    # 9
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(frozen.shift_multiplier, frozen.pooled_implicit_rmse, "o-", label="implicit RMSE")
    ax.plot(frozen.shift_multiplier, frozen.pooled_explicit_rmse, "s-", label="explicit RMSE")
    ax.set_xlabel("shift multiplier")
    ax.set_ylabel("RMSE")
    ax.set_yscale("log")
    ax.legend()
    ax.set_title("Shift sensitivity (frozen coefficients)")
    save(fig, "shift_sensitivity_frozen_model", "Frozen-model shift sensitivity", "shift_sensitivity_frozen_model.csv", rows)

    # 10
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(refit.shift_multiplier, refit.median_rel_coef_change, "o-")
    ax.set_xlabel("shift multiplier")
    ax.set_ylabel("median relative coefficient change")
    ax.set_title("Shift sensitivity after refit")
    save(fig, "shift_sensitivity_refit", "Refit shift sensitivity", "shift_sensitivity_refit.csv", rows)

    # 11
    fig, ax = plt.subplots(figsize=(8, 4))
    sub = deg[np.isclose(deg.a_rel, 0.1)]
    for cls, g in sub.groupby("class"):
        ax.plot(g.realization_index, g.fraction, "o-", ms=3, label=cls)
    ax.legend(fontsize=7)
    ax.set_xlabel("realization index")
    ax.set_ylabel("fraction")
    ax.set_title("Local degeneracy classification (a_rel=b_rel=0.1)")
    save(fig, "local_degeneracy_classification", "Degeneracy classes", "local_degeneracy_classification.csv", rows)

    # 12
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["inconsistent s", "consistent s"], [tunit.max_abs_diff_inconsistent_s.median(), tunit.max_abs_diff_consistent_s.median()])
    ax.set_yscale("log")
    ax.set_ylabel("median max |Δu|")
    ax.set_title("Time-unit consistency of shifted ratios")
    save(fig, "time_unit_consistency", "Time-unit effects", "time_unit_consistency.csv", rows)

    pd.DataFrame(rows).to_csv(FIG / "figure_manifest.csv", index=False)
    print(f"Wrote {len(rows)} figures")


if __name__ == "__main__":
    main()
