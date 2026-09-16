"""Publication panel: same pendulum ensemble, two SIR task contracts.

Writes PNG/PDF/SVG to D:\\SIR_paper\\Figures\\figs\\.
Uses frozen compression slope A = -3.645 and frozen Prediction_model holdouts.
Does not rerun SIR.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, NullFormatter

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from panel_data import (  # noqa: E402
    DEFAULT_HOLDOUT_ID,
    R2_B_VS_2E,
    SIR_A,
    SIR_B,
    SIR_SLOPE,
    TRUE_COLOR,
    PRED_COLOR,
    load_compression,
    load_pooled_rmse,
    load_prediction_bundle,
    subsample_phase,
)

OUT = Path(r"D:\SIR_paper\Figures\figs")
STEM = "pendulum_task_conditioned_panel"
PNG_PATH = OUT / f"{STEM}.png"
PDF_PATH = OUT / f"{STEM}.pdf"
SVG_PATH = OUT / f"{STEM}.svg"

TEXT = "#1f1f1f"
MUTED = "#5a5a5a"
RULE = "#d4d4d4"
CARD = "#f7f8f4"
BLUE = "#274C77"
GREEN = "#0D4B25"
SERIF = "Times New Roman"


def _publication_style() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": SERIF,
            "font.serif": [SERIF, "Times", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 9.5,
            "axes.labelsize": 10.5,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.unicode_minus": True,
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "axes.linewidth": 0.7,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "xtick.major.width": 0.65,
            "ytick.major.width": 0.65,
        }
    )


def _sci(value: float) -> str:
    exp = int(np.floor(np.log10(abs(value))))
    mant = value / (10.0**exp)
    return rf"{mant:.2f}\times 10^{{{exp}}}"


def _serif(**kwargs):
    kwargs.setdefault("fontfamily", SERIF)
    kwargs.setdefault("color", TEXT)
    return kwargs


def _spine(ax) -> None:
    for spine in ax.spines.values():
        spine.set_color(TEXT)
        spine.set_linewidth(0.7)
    ax.tick_params(colors=TEXT, pad=1.8)
    ax.set_facecolor("white")


def _badge(ax, label: str, color: str) -> None:
    ax.text(
        0.0,
        1.028,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.0,
        fontweight="bold",
        fontfamily=SERIF,
        color=color,
    )


def build_figure(
    compression_ids=None,
    holdout_id: str = DEFAULT_HOLDOUT_ID,
):
    traces = load_compression(compression_ids)
    pooled = load_pooled_rmse()
    phase = subsample_phase(load_prediction_bundle(holdout_id), step=3)

    fig = plt.figure(figsize=(7.32, 4.48), facecolor="white")
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.12, 1.0],
        height_ratios=[0.84, 1.08],
        left=0.078,
        right=0.985,
        top=0.82,
        bottom=0.105,
        wspace=0.38,
        hspace=0.38,
    )
    ax_c = fig.add_subplot(gs[:, 0])
    ax_p = fig.add_subplot(gs[0, 1])
    ax_e = fig.add_subplot(gs[1, 1])

    fig.text(
        0.078,
        0.955,
        r"Same observational ensemble  $+$  different task contracts"
        r"  $\rightarrow$  different qualified models",
        ha="left",
        va="center",
        fontsize=10.6,
        **_serif(),
    )
    fig.text(
        0.078,
        0.905,
        "Pendulum  ·  one support, two SIR contracts",
        ha="left",
        va="center",
        fontsize=8.4,
        **_serif(color=MUTED),
    )

    # --- Compression -------------------------------------------------
    _badge(ax_c, "COMPRESSION", GREEN)
    ax_c.set_title(
        r"Conserved representation  ·  shared slope, intercept $2E_i$",
        loc="left",
        fontsize=9.0,
        pad=10,
        **_serif(color=MUTED),
    )
    for tr in traces:
        ax_c.plot(
            tr["x_line"],
            tr["y_line"],
            color=tr["color"],
            lw=1.55,
            solid_capstyle="round",
            zorder=2,
        )
        ax_c.plot(
            tr["x"],
            tr["y"],
            linestyle="none",
            marker="o",
            markersize=1.35,
            markeredgewidth=0.0,
            alpha=0.28,
            color=tr["color"],
            zorder=3,
        )
    ax_c.set_xlabel(r"$1-\cos\theta$", labelpad=3)
    ax_c.set_ylabel(r"$\omega^{2}$", labelpad=4)
    ax_c.set_xlim(left=0.0)
    ax_c.set_ylim(bottom=0.0)
    _spine(ax_c)
    ax_c.text(
        0.035,
        0.965,
        rf"$\omega^{2}=-3.645\,(1-\cos\theta)+2E_i$" "\n"
        rf"$R^{2}(B_i,\,2E_i)={R2_B_VS_2E:.9f}$",
        transform=ax_c.transAxes,
        ha="left",
        va="top",
        fontsize=8.2,
        linespacing=1.45,
        zorder=4,
        bbox=dict(
            boxstyle="round,pad=0.28",
            facecolor=CARD,
            edgecolor=RULE,
            linewidth=0.55,
            alpha=0.96,
        ),
        **_serif(),
    )
    # Energy direction cue (no 8-entry legend).
    cax = ax_c.inset_axes([0.72, 0.075, 0.22, 0.028])
    grad = np.linspace(0, 1, 256)[None, :]
    cax.imshow(grad, aspect="auto", cmap=_energy_cmap())
    cax.set_xticks([])
    cax.set_yticks([])
    for spine in cax.spines.values():
        spine.set_color(RULE)
        spine.set_linewidth(0.5)
    ax_c.text(
        0.72,
        0.125,
        "low $E$",
        transform=ax_c.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.2,
        **_serif(color=MUTED),
    )
    ax_c.text(
        0.94,
        0.125,
        "high $E$",
        transform=ax_c.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.2,
        **_serif(color=MUTED),
    )

    # --- Phase portrait (orbit identity, not milliradian mismatch) ---
    _badge(ax_p, "PREDICTION", BLUE)
    ax_p.set_title(
        rf"Protected holdout  ·  {holdout_id.replace('_', ' ')}",
        loc="left",
        fontsize=9.0,
        pad=10,
        **_serif(color=MUTED),
    )
    ax_p.plot(
        phase["theta_true"],
        phase["omega_true"],
        color=TRUE_COLOR,
        lw=1.35,
        solid_capstyle="round",
        label="true",
        zorder=2,
    )
    ax_p.plot(
        phase["theta_sir"],
        phase["omega_sir"],
        color=PRED_COLOR,
        lw=1.15,
        ls=(0, (1.6, 1.15)),
        solid_capstyle="round",
        label="SIR rollout",
        zorder=3,
    )
    ax_p.plot(
        phase["theta0"],
        phase["omega0"],
        marker="o",
        markersize=4.2,
        color=TEXT,
        markerfacecolor="white",
        markeredgewidth=1.05,
        zorder=4,
        linestyle="none",
    )
    ax_p.annotate(
        r"$t=0$",
        xy=(phase["theta0"], phase["omega0"]),
        xytext=(8, -10),
        textcoords="offset points",
        fontsize=7.2,
        color=MUTED,
        fontfamily=SERIF,
        arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5),
    )
    ax_p.set_xlabel(r"$\theta$", labelpad=2)
    ax_p.set_ylabel(r"$\omega$", labelpad=2)
    _spine(ax_p)
    ax_p.legend(
        loc="upper right",
        frameon=False,
        fontsize=7.4,
        handlelength=1.7,
        borderpad=0.1,
        labelspacing=0.25,
        handletextpad=0.45,
    )
    ax_p.text(
        0.03,
        0.06,
        "orbits coincide at plot scale",
        transform=ax_p.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.0,
        **_serif(color=MUTED),
    )

    # --- RMSE vs horizon (the actual accuracy evidence) --------------
    h_th = np.asarray(pooled["sir"]["theta"]["horizon_s"])
    r_th = np.asarray(pooled["sir"]["theta"]["rmse"])
    h_om = np.asarray(pooled["sir"]["omega"]["horizon_s"])
    r_om = np.asarray(pooled["sir"]["omega"]["rmse"])
    ax_e.plot(
        h_th,
        r_th,
        color=TRUE_COLOR,
        lw=1.7,
        marker="o",
        markersize=4.0,
        markerfacecolor="white",
        markeredgewidth=1.05,
        label=r"RMSE $\theta$",
        zorder=3,
    )
    ax_e.plot(
        h_om,
        r_om,
        color=PRED_COLOR,
        lw=1.7,
        marker="s",
        markersize=3.6,
        markerfacecolor="white",
        markeredgewidth=1.05,
        label=r"RMSE $\omega$",
        zorder=3,
    )
    ax_e.set_yscale("log")
    ax_e.set_xlim(-0.6, 31.2)
    ax_e.set_ylim(8e-7, 2.2e-3)
    ax_e.set_xticks([0, 5, 10, 20, 30])
    ax_e.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
    ax_e.yaxis.set_minor_formatter(NullFormatter())
    ax_e.set_xlabel("prediction horizon (s)", labelpad=3)
    ax_e.set_ylabel("pooled holdout RMSE", labelpad=3)
    _spine(ax_e)
    ax_e.legend(
        loc="upper left",
        frameon=False,
        fontsize=7.6,
        handlelength=1.6,
        borderpad=0.15,
        labelspacing=0.22,
        handletextpad=0.45,
    )
    rmse_th_30 = float(r_th[np.argmin(np.abs(h_th - 30.0))])
    rmse_om_30 = float(r_om[np.argmin(np.abs(h_om - 30.0))])
    ax_e.text(
        0.97,
        0.08,
        "30 s pooled\n"
        + rf"RMSE $\theta={_sci(rmse_th_30)}$ rad" + "\n"
        + rf"RMSE $\omega={_sci(rmse_om_30)}$ rad s$^{{-1}}$",
        transform=ax_e.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.6,
        linespacing=1.4,
        bbox=dict(
            boxstyle="round,pad=0.28",
            facecolor=CARD,
            edgecolor=RULE,
            linewidth=0.55,
            alpha=0.96,
        ),
        **_serif(),
    )
    ax_e.text(
        0.03,
        1.035,
        rf"Frozen law:  $\dot\theta=\omega$,   $\dot\omega={SIR_A}\,\sin\theta$"
        + "  ·  autonomous from $t=0$ only",
        transform=ax_e.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.5,
        **_serif(color=MUTED),
    )

    fig.text(
        0.078,
        0.028,
        "Left: eight energy-spaced discovery realizations on the SIR invariant.  "
        "Right: protected-holdout autonomous rollout; RMSE, not visual overlap, is the accuracy claim.",
        ha="left",
        va="center",
        fontsize=7.3,
        **_serif(color=MUTED),
    )
    # Keep unused locals referenced so a coefficient mismatch is loud.
    assert abs(pooled["a"] - SIR_A) < 1e-12
    assert abs(pooled["b"] - SIR_B) < 1e-12
    assert abs(SIR_SLOPE + 3.645) < 1e-12
    _ = (rmse_th_30, rmse_om_30)
    return fig


def _energy_cmap():
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "pendulum_energy",
        ["#7BA3C4", "#3E7F6C", "#0D4B25"],
        N=256,
    )


def save_figure(fig) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in (PNG_PATH, PDF_PATH, SVG_PATH):
        fig.savefig(
            path,
            dpi=600,
            facecolor="white",
            bbox_inches="tight",
            pad_inches=0.04,
        )


def main() -> None:
    _publication_style()
    fig = build_figure()
    save_figure(fig)
    plt.close(fig)
    print("Saved:")
    print(" ", PNG_PATH)
    print(" ", PDF_PATH)
    print(" ", SVG_PATH)


if __name__ == "__main__":
    main()
