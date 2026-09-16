"""Step 23 — candidate main-text figure: task-conditioned relational discovery.

Panels
  A  nesting / problem formulation — PySINDy as an admissible solver INSIDE SIR
  B  containment — MCP-native SIR vs the canonical generator
  C  same clean object, different contracts -> different qualified representations
  D  observational uncertainty — what the robust contract does and does not change

Visual message: there is no task-independent best representation.
Not a leaderboard.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

TCB = Path(__file__).resolve().parent.parent
FIG = TCB / "figures"
FIG.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03, "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "cm", "pdf.fonttype": 42, "ps.fonttype": 42,
    "svg.fonttype": "none", "font.size": 7.6, "axes.labelsize": 8,
    "axes.titlesize": 8.6, "legend.fontsize": 6.8, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "axes.linewidth": 0.7,
    "xtick.direction": "in", "ytick.direction": "in", "legend.frameon": False,
})

INK, MUTED = "#1b1b1b", "#6f6f6f"
C_SIR, C_PY, C_RAW = "#1f7a3d", "#2b6ca3", "#8c8c8c"
C_TRUE, C_ACC, C_CMP = "#a6171b", "#2b6ca3", "#1f7a3d"

res = pd.read_csv(TCB / "tables" / "confirmation_results.csv")
sel = json.loads((TCB / "contracts" / "contract_selections.json").read_text())
mcp = json.loads((TCB / "sir_mcp" / "containment" / "mcp_containment.json").read_text())
sweep = pd.read_csv(TCB / "tables" / "equivalence_sensitivity.csv")


def _v(regime, method, rep, col="pooled_rmse"):
    r = res[(res.regime == regime) & (res.method == method) &
            (res.representation == rep)]
    return float(r[col].iloc[0]) if len(r) else float("nan")


# ---------------------------------------------------------------- panel A
def panel_a(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("A  Formulation", loc="left", fontweight="bold")

    ax.text(0.5, 0.965, "conventional workflow", ha="center", fontsize=6.8,
            color=MUTED, style="italic")
    # Stacked, not side by side: three labels do not fit across this column.
    for i, (lab, col) in enumerate([
            ("scientific choices supplied upstream", C_RAW),
            ("coordinates + library", C_RAW),
            ("PySINDy relation fit", C_PY)]):
        yb = 0.855 - i * 0.070
        ax.add_patch(FancyBboxPatch((0.06, yb), 0.88, 0.048,
                     boxstyle="round,pad=0.007,rounding_size=0.013",
                     facecolor=col, alpha=0.13, edgecolor=col, lw=0.7))
        ax.text(0.5, yb + 0.024, lab, ha="center", va="center", fontsize=6.1,
                color=INK)
        if i < 2:
            ax.add_patch(FancyArrowPatch((0.5, yb - 0.001), (0.5, yb - 0.017),
                         arrowstyle="-|>", mutation_scale=5, color=MUTED, lw=0.6))

    ax.plot([0.02, 0.98], [0.685, 0.685], color="#d8d8d8", lw=0.8)
    ax.text(0.5, 0.655, "SIR", ha="center", fontsize=7.6, color=C_SIR,
            fontweight="bold")

    # Stacked: the two formulae are too wide to sit side by side here.
    ax.add_patch(FancyBboxPatch((0.06, 0.545), 0.88, 0.072,
                 boxstyle="round,pad=0.008,rounding_size=0.015",
                 facecolor=C_SIR, alpha=0.10, edgecolor=C_SIR, lw=0.75))
    ax.text(0.5, 0.581, r"scientific object $O=(D,\Omega_{obs},S,E,\Pi,A)$",
            ha="center", va="center", fontsize=6.2, color=INK)
    ax.add_patch(FancyBboxPatch((0.06, 0.455), 0.88, 0.072,
                 boxstyle="round,pad=0.008,rounding_size=0.015",
                 facecolor=C_SIR, alpha=0.10, edgecolor=C_SIR, lw=0.75))
    ax.text(0.5, 0.491, r"discovery contract $K_q=(q,I_q,C_q,R_q,U_q,V_q)$",
            ha="center", va="center", fontsize=6.2, color=INK)

    ax.add_patch(FancyArrowPatch((0.5, 0.450), (0.5, 0.375), arrowstyle="-|>",
                 mutation_scale=7, color=C_SIR, lw=0.9))
    ax.add_patch(FancyBboxPatch((0.05, 0.175), 0.90, 0.185,
                 boxstyle="round,pad=0.012,rounding_size=0.02",
                 facecolor="none", edgecolor=C_SIR, lw=0.9, linestyle=(0, (3, 2))))
    ax.text(0.5, 0.322, "search over qualified $(C,R)$", ha="center",
            fontsize=6.5, color=C_SIR)
    ax.add_patch(FancyBboxPatch((0.16, 0.198), 0.68, 0.070,
                 boxstyle="round,pad=0.007,rounding_size=0.013",
                 facecolor=C_PY, alpha=0.16, edgecolor=C_PY, lw=0.75))
    ax.text(0.50, 0.233, "PySINDy as one solver $R_q(C)$", ha="center",
            va="center", fontsize=6.2, color=INK)
    ax.text(0.5, 0.115, "qualified representation $C^{*}_q$", ha="center",
            fontsize=6.8, color=INK)
    ax.text(0.5, 0.025, "the estimator is nested inside the contract,\n"
            "not opposed to it", ha="center", va="bottom", fontsize=6.0,
            color=MUTED, style="italic", linespacing=1.2)


# ---------------------------------------------------------------- panel B
def panel_b(ax):
    ax.set_title("B  Containment", loc="left", fontweight="bold")
    terms, true, got = [], [], []
    for eq in ("dx", "dy", "dz"):
        r = mcp["runs"][eq]
        for k, v in r["true_coefficients"].items():
            terms.append(rf"$\dot{{{eq[1]}}}$: {k}")
            true.append(v)
            got.append(r["coefficients"][k])
    yy = np.arange(len(terms))[::-1]
    ax.barh(yy, true, height=0.6, color=C_TRUE, alpha=0.16, edgecolor=C_TRUE,
            lw=0.6, label="true", zorder=1)
    ax.scatter(got, yy, s=15, marker="o", facecolor="none", edgecolor=C_SIR,
               lw=0.9, label="SIR (MCP)", zorder=3)
    ax.set_yticks(yy); ax.set_yticklabels(terms, fontsize=6.2)
    ax.axvline(0, color=MUTED, lw=0.5, zorder=0)
    ax.set_xlabel("coefficient")
    ax.legend(loc="lower right", handletextpad=0.4, borderaxespad=0.2)
    ax.margins(y=0.07)
    ax.text(0.5, -0.22, "exact support, all three equations\n"
            r"max $|\Delta c|$ vs truth $\approx 2\times10^{-3}$",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.2,
            color=MUTED)


# ---------------------------------------------------------------- panel C
def panel_c(ax):
    ax.set_title("C  Two contracts", loc="left", fontweight="bold")
    labs = ["$C_0$", "poly2", r"$q_{\rm acc}$", r"$q_{\rm cmp}$"]
    reps = ["C0_matched", "C0_poly2", "C*_accuracy", "C*_compact"]
    cols = [C_RAW, C_PY, C_ACC, C_CMP]
    vals = [max(_v("clean", "STLSQ", r), 1e-6) for r in reps]
    ncoord = [int(res[(res.regime == "clean") & (res.method == "STLSQ") &
                      (res.representation == r)].n_coordinates.iloc[0])
              for r in reps]
    nfeat = [int(res[(res.regime == "clean") & (res.method == "STLSQ") &
                     (res.representation == r)].n_terms.iloc[0]) for r in reps]
    xs = np.arange(len(reps))
    ax.bar(xs, vals, 0.62, color=cols, alpha=0.85, edgecolor=cols, lw=0.6)
    # Counts live in the tick labels: in-axes annotation collides either with
    # the sigma_z line or with the neighbouring bar at this column width.
    ax.set_yscale("log"); ax.set_ylim(3e-6, 3e3)
    ax.set_xticks(xs)
    # Coordinate count only — "Nc/Mt" is too wide for this bar spacing.
    ax.set_xticklabels([f"{a}\n{c}c" for a, c in zip(labs, ncoord)],
                       fontsize=6.5, linespacing=1.35)
    ax.set_ylabel("confirmation RMSE in $z$ (log)", labelpad=2)
    ax.axhline(9.04, color=C_TRUE, lw=0.7, ls=(0, (3, 2)))
    ax.text(0.72, 0.80, r"$\sigma_z$", transform=ax.transAxes, fontsize=6.2,
            color=C_TRUE)
    ax.grid(axis="y", which="both", lw=0.3, alpha=0.25); ax.set_axisbelow(True)
    ax.text(0.5, -0.185, "c = coordinate count\n"
            "accuracy and compactness\ndisagree here",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.1,
            color=MUTED)


# ---------------------------------------------------------------- panel D
def panel_d(ax):
    ax.set_title("D  Uncertainty", loc="left", fontweight="bold")
    reps = ["C0_matched", "C0_poly2", "C*_accuracy", "C*_compact"]
    labs = ["$C_0$", "poly2", "$C_{\\rm all}$", "$C^{*}$"]
    cols = [C_RAW, C_PY, C_ACC, C_CMP]
    noisy_regime = [r for r in res.regime.unique() if r.startswith("noise")][0]
    xs = np.arange(len(reps)); w = 0.38
    clean = [max(_v("clean", "STLSQ", r), 1e-6) for r in reps]
    noisy = [max(_v(noisy_regime, "STLSQ", r), 1e-6) for r in reps]
    ax.bar(xs - w / 2, clean, w * 0.92, color=cols, alpha=0.85, lw=0.5,
           edgecolor=cols, label="clean")
    ax.bar(xs + w / 2, noisy, w * 0.92, color=cols, alpha=0.42, lw=0.5,
           edgecolor=cols, hatch="///", label="1% noise")
    ax.set_yscale("log"); ax.set_ylim(3e-6, 3e3)
    ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=6.6)
    ax.set_ylabel("confirmation RMSE in $z$ (log)", labelpad=2)
    ax.grid(axis="y", which="both", lw=0.3, alpha=0.25); ax.set_axisbelow(True)
    ax.axhline(9.04, color=C_TRUE, lw=0.7, ls=(0, (3, 2)))
    h = [plt.Rectangle((0, 0), 1, 1, facecolor="0.55", alpha=0.85),
         plt.Rectangle((0, 0), 1, 1, facecolor="0.55", alpha=0.42, hatch="///")]
    ax.legend(h, ["clean", "1% noise"], loc="upper left", handlelength=1.2,
              borderaxespad=0.25)
    ax.text(0.5, -0.155,
            r"$q_{\rm rob}$ = same coordinates as $q_{\rm acc}$;"
            "\nuncertainty changed the\nqualification, not the coordinates",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.1,
            color=MUTED)


def main() -> None:
    fig = plt.figure(figsize=(7.4, 3.55))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.22, 1.02, 1.0, 1.0],
                          wspace=0.62, left=0.055, right=0.99,
                          bottom=0.20, top=0.91)
    panel_a(fig.add_subplot(gs[0, 0]))
    panel_b(fig.add_subplot(gs[0, 1]))
    panel_c(fig.add_subplot(gs[0, 2]))
    panel_d(fig.add_subplot(gs[0, 3]))
    stem = FIG / "sir_task_conditioning_benchmark"
    for ext in ("png", "pdf", "svg"):
        fig.savefig(stem.with_suffix(f".{ext}"))
    plt.close(fig)
    print(f"wrote {stem}.png/.pdf/.svg")


if __name__ == "__main__":
    main()
