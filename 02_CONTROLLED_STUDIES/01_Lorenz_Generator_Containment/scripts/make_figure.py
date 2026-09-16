"""Step 14 — candidate main-text Figure 6: nested representation benchmark.

Three panels:
  A  containment      restricted SIR vs canonical PySINDy Lorenz recovery
  B  representation   C0 -> C_all -> C*, with the selected coordinates named
  C  held-out utility the same two learners across the three representations

The visual message is "conventional learner + broader representation =
nested representation experiment", NOT a leaderboard.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

BENCH = Path(__file__).resolve().parent.parent
FIG = BENCH / "figures"
FIG.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "cm", "pdf.fonttype": 42, "ps.fonttype": 42,
    "svg.fonttype": "none",
    "font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 9,
    "legend.fontsize": 7.2, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.linewidth": 0.7, "xtick.direction": "in", "ytick.direction": "in",
    "legend.frameon": False,
})

INK = "#1b1b1b"
MUTED = "#6f6f6f"
C_RAW = "#8c8c8c"
C_ALL = "#2b6ca3"
C_STAR = "#1f7a3d"
C_TRUE = "#a6171b"

res = pd.read_csv(BENCH / "tables" / "benchmark_results.csv")
abl = pd.read_csv(BENCH / "tables" / "ablation_results.csv")
cont = json.loads((BENCH / "sir" / "containment" / "containment_full.json").read_text())
frozen = json.loads(
    (BENCH / "sir" / "frozen_selection" / "FROZEN_REPRESENTATION.json").read_text())

REPS = ["C0_matched", "C_all", "C_star"]
REP_LABEL = {"C0_matched": r"$\mathcal{C}_0$", "C_all": r"$\mathcal{C}_{\mathrm{all}}$",
             "C_star": r"$\mathcal{C}^{*}$"}
REP_COLOR = {"C0_matched": C_RAW, "C_all": C_ALL, "C_star": C_STAR}


def panel_a(ax):
    """Coefficient agreement on the three Lorenz equations."""
    eqs = ["dx", "dy", "dz"]
    terms, truth, py, sir = [], [], [], []
    for eq in eqs:
        for t, v in cont["ground_truth"][eq].items():
            terms.append(rf"$\dot{{{eq[1]}}}$: {t}")
            truth.append(v)
            py.append(cont["pysindy"]["coefficients"][eq].get(t, 0.0))
            sir.append(cont["restricted_sir"]["coefficients"][eq].get(t, 0.0))
    yy = np.arange(len(terms))[::-1]
    ax.barh(yy, truth, height=0.62, color=C_TRUE, alpha=0.16,
            edgecolor=C_TRUE, linewidth=0.6, label="true coefficient", zorder=1)
    ax.scatter(py, yy + 0.13, s=17, marker="o", facecolor="none",
               edgecolor=C_ALL, linewidth=0.9, label="PySINDy", zorder=3)
    ax.scatter(sir, yy - 0.13, s=15, marker="x", color=C_STAR, linewidth=0.9,
               label="restricted SIR", zorder=3)
    ax.set_yticks(yy)
    ax.set_yticklabels(terms)
    ax.axvline(0, color=MUTED, lw=0.5, zorder=0)
    ax.set_xlabel("coefficient")
    maxerr = max(
        cont["pysindy"]["score"][e]["max_coeff_error"] for e in eqs)
    agree = max(cont["agreement"][e]["max_abs_coefficient_difference"] for e in eqs)
    ax.set_title("A  Containment", loc="left", fontweight="bold")
    ax.text(0.5, -0.30,
            "identical support, both methods\n"
            rf"max $|\Delta c|$ vs truth $= {maxerr:.0e}$"
            "\n"
            rf"max $|\Delta c|$ between methods $= {agree:.0e}$",
            transform=ax.transAxes, ha="center", va="top", fontsize=7, color=MUTED)
    # Below the axes: the data occupy both the left and right of the panel.
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3,
              handletextpad=0.4, columnspacing=0.9, borderaxespad=0.0)
    ax.margins(y=0.08)


def panel_b(ax):
    """C0 -> C_all -> C*, naming what the search kept."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("B  Representation", loc="left", fontweight="bold")

    n0 = len(frozen["representations"]["C0_matched"])
    nall = len(frozen["representations"]["C_all"])
    nstar = len(frozen["selected_coordinates"])

    # Short captions only — anything longer collides at this column width.
    boxes = [
        (0.02, r"$\mathcal{C}_0$", f"{n0} raw", C_RAW, "matched\nstencil"),
        (0.375, r"$\mathcal{C}_{\mathrm{all}}$", f"{nall} coords", C_ALL,
         "all $z$-free\ncandidates"),
        (0.73, r"$\mathcal{C}^{*}$", f"{nstar} coords", C_STAR,
         "selected on\ntrain+val"),
    ]
    for x0, sym, cnt, col, sub in boxes:
        ax.add_patch(Rectangle((x0, 0.66), 0.25, 0.27, facecolor=col, alpha=0.13,
                               edgecolor=col, linewidth=0.9, zorder=2))
        ax.text(x0 + 0.125, 0.845, sym, ha="center", va="center", fontsize=11.5,
                color=INK, zorder=3)
        ax.text(x0 + 0.125, 0.725, cnt, ha="center", va="center", fontsize=7.4,
                color=col, zorder=3)
        ax.text(x0 + 0.125, 0.615, sub, ha="center", va="top", fontsize=6.6,
                color=MUTED, zorder=3, linespacing=1.15)
    for x0 in (0.283, 0.638):
        ax.add_patch(FancyArrowPatch((x0, 0.795), (x0 + 0.078, 0.795),
                                     arrowstyle="-|>", mutation_scale=8.5,
                                     color=MUTED, lw=0.8))
    ax.text(0.322, 0.845, "expand", ha="center", fontsize=6.3, color=MUTED)
    ax.text(0.677, 0.845, "select", ha="center", fontsize=6.3, color=MUTED)

    ax.text(0.5, 0.44, "coordinates the search retained", ha="center",
            va="center", fontsize=7.2, color=INK)
    ax.text(0.5, 0.325, r"$Q[\dot{y}\,|\,x]$        $Q[y\,|\,x]$",
            ha="center", va="center", fontsize=9.0, color=C_STAR)
    ax.text(0.5, 0.195,
            r"$z = 28.000005 - 1.0000\,Q[\dot{y}|x] - 1.0000\,Q[y|x]$",
            ha="center", va="center", fontsize=7.0, color=MUTED)
    ax.text(0.5, 0.055,
            r"analytic identity $z=\rho-(\dot y+y)/x$ — recovered, not imposed",
            ha="center", va="center", fontsize=6.4, color=C_TRUE, style="italic")


def panel_c(ax):
    """Held-out reconstruction error, both learners, three representations."""
    learners = ["STLSQ", "MLP"]
    width = 0.26
    xs = np.arange(len(learners))
    for i, rep in enumerate(REPS):
        vals, errs = [], []
        for ln in learners:
            r = res[(res.representation == rep) & (res.learner == ln)].iloc[0]
            vals.append(max(r["test_rmse"], 1e-6))
            errs.append(r["test_rmse_std"] if ln == "MLP" and
                        np.isfinite(r.get("test_rmse_std", np.nan)) else 0.0)
        off = (i - 1) * width
        ax.bar(xs + off, vals, width * 0.9, yerr=errs, capsize=1.8,
               color=REP_COLOR[rep], alpha=0.85, edgecolor=REP_COLOR[rep],
               linewidth=0.6, label=REP_LABEL[rep],
               error_kw={"elinewidth": 0.7, "capthick": 0.7})
        for x, v, rep_ in zip(xs + off, vals, [rep] * 2):
            nc = len(frozen["representations"][rep_]) if rep_ != "C_star" else \
                len(frozen["selected_coordinates"])
            ax.text(x, v * 1.35, f"{nc}", ha="center", fontsize=5.9, color=MUTED)

    ax.set_yscale("log")
    ax.set_xticks(xs)
    ax.set_xticklabels(["STLSQ", "MLP"])
    ax.set_ylabel(r"held-out RMSE in $z$  (log)", labelpad=2)
    ax.set_title("C  Protected test utility", loc="left", fontweight="bold")
    ax.grid(axis="y", which="both", lw=0.3, alpha=0.28)
    ax.set_axisbelow(True)

    # Headroom above the bars so neither the legend nor sigma_z overlaps them.
    ax.set_ylim(3e-6, 3e3)
    zstd = 9.04
    ax.axhline(zstd, color=C_TRUE, lw=0.7, ls=(0, (3, 2)), zorder=1)
    # Axes-fraction placement keeps this clear of the y-axis tick labels.
    ax.text(0.30, 0.615, r"$\sigma_z$: predict-the-mean", fontsize=6.0,
            color=C_TRUE, ha="left", va="bottom", transform=ax.transAxes)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3,
              columnspacing=0.9, handlelength=1.0, handletextpad=0.4,
              borderaxespad=0.2)
    ax.text(0.5, -0.20,
            "numerals = coordinate count;  noiseless primary benchmark\n"
            "under 1% noise the MLP advantage does not persist (SI)",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.4,
            color=MUTED)


def main() -> None:
    fig = plt.figure(figsize=(7.2, 3.05))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.04, 1.32, 0.92],
                          wspace=0.46, left=0.105, right=0.99,
                          bottom=0.32, top=0.90)
    panel_a(fig.add_subplot(gs[0, 0]))
    panel_b(fig.add_subplot(gs[0, 1]))
    panel_c(fig.add_subplot(gs[0, 2]))

    stem = FIG / "sir_nested_model_benchmark"
    for ext in ("png", "pdf", "svg"):
        fig.savefig(stem.with_suffix(f".{ext}"))
    plt.close(fig)
    print(f"wrote {stem}.png/.pdf/.svg")


if __name__ == "__main__":
    main()
