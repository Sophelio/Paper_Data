"""Compact publication version of the task-conditioned pendulum panel.

Purpose
-------
Keep the scientific content of the frozen pendulum panel while making the
visual hierarchy genuinely two-panel:

(a) compression: shared-slope invariant relations across discovery records;
(b) prediction: pooled holdout RMSE vs horizon, with one protected holdout
    orbit shown only as a small structural inset.

This script does not rerun SIR. It uses the same frozen loaders/results as
panel_data.py.

Place this file beside panel_data.py in Pendulum/Plotter/ and run it from the
existing SIR environment (which already has Parquet support).
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
STEM = "pendulum_task_conditioned_panel_compact"
SERIF = "Times New Roman"


def _publication_style() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": SERIF,
            "font.serif": [SERIF, "Times", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 8.2,
            "axes.labelsize": 8.8,
            "axes.titlesize": 9.2,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.65,
            "xtick.major.size": 2.7,
            "ytick.major.size": 2.7,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.dpi": 600,
        }
    )


def _sci(v: float) -> str:
    exponent = int(np.floor(np.log10(abs(v))))
    mantissa = v / (10.0**exponent)
    return rf"{mantissa:.2f}\times10^{{{exponent}}}"


def _clean_axes(ax) -> None:
    # Keep a conventional scientific frame, but remove visual clutter.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(pad=1.8)


def build_figure(
    compression_ids=None,
    holdout_id: str = DEFAULT_HOLDOUT_ID,
):
    traces = load_compression(compression_ids)
    pooled = load_pooled_rmse()
    phase = subsample_phase(load_prediction_bundle(holdout_id), step=3)

    # Full two-column journal width, but substantially shorter than the
    # previous 7.32 x 4.48 in layout.
    fig, (ax_c, ax_p) = plt.subplots(
        1,
        2,
        figsize=(7.20, 3.02),
        gridspec_kw={"width_ratios": [1.03, 1.0]},
    )
    fig.subplots_adjust(
        left=0.075,
        right=0.985,
        bottom=0.19,
        top=0.90,
        wspace=0.27,
    )

    # ------------------------------------------------------------------
    # (a) Compression
    # ------------------------------------------------------------------
    ax_c.set_title(r"$\bf{a}$  Compression", loc="left", pad=4)

    for tr in traces:
        ax_c.plot(
            tr["x_line"],
            tr["y_line"],
            color=tr["color"],
            lw=1.35,
            solid_capstyle="round",
            zorder=2,
        )
        ax_c.plot(
            tr["x"],
            tr["y"],
            linestyle="none",
            marker="o",
            markersize=1.15,
            markeredgewidth=0.0,
            alpha=0.22,
            color=tr["color"],
            zorder=3,
        )

    ax_c.set_xlabel(r"$1-\cos\theta$", labelpad=2.5)
    ax_c.set_ylabel(r"$\omega^2$", labelpad=3)
    ax_c.set_xlim(left=0.0)
    ax_c.set_ylim(bottom=0.0)
    _clean_axes(ax_c)

    # No card/badge. Only the quantitative relation needed to read the panel.
    ax_c.text(
        0.035,
        0.965,
        rf"$\omega^2=-3.645(1-\cos\theta)+2E_i$"
        "\n"
        rf"$R^2(B_i,2E_i)={R2_B_VS_2E:.9f}$",
        transform=ax_c.transAxes,
        ha="left",
        va="top",
        fontsize=7.7,
        linespacing=1.25,
    )
    ax_c.text(
        0.97,
        0.035,
        "color: increasing $E$",
        transform=ax_c.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.9,
    )

    # ------------------------------------------------------------------
    # (b) Prediction: pooled error is the main evidence
    # ------------------------------------------------------------------
    ax_p.set_title(r"$\bf{b}$  Prediction", loc="left", pad=4)

    h_th = np.asarray(pooled["sir"]["theta"]["horizon_s"], dtype=float)
    r_th = np.asarray(pooled["sir"]["theta"]["rmse"], dtype=float)
    h_om = np.asarray(pooled["sir"]["omega"]["horizon_s"], dtype=float)
    r_om = np.asarray(pooled["sir"]["omega"]["rmse"], dtype=float)

    ax_p.plot(
        h_th,
        r_th,
        color=TRUE_COLOR,
        lw=1.5,
        marker="o",
        markersize=3.5,
        markerfacecolor="white",
        markeredgewidth=0.9,
        label=r"$\theta$",
        zorder=3,
    )
    ax_p.plot(
        h_om,
        r_om,
        color=PRED_COLOR,
        lw=1.5,
        marker="s",
        markersize=3.2,
        markerfacecolor="white",
        markeredgewidth=0.9,
        label=r"$\omega$",
        zorder=3,
    )

    ax_p.set_yscale("log")
    ax_p.set_xlim(-0.5, 31.5)
    ax_p.set_ylim(1.0e-6, 8.0e-4)
    ax_p.set_xticks([0, 5, 10, 20, 30])
    ax_p.yaxis.set_major_locator(LogLocator(base=10, numticks=5))
    ax_p.yaxis.set_minor_formatter(NullFormatter())
    ax_p.set_xlabel("prediction horizon (s)", labelpad=2.5)
    ax_p.set_ylabel("pooled holdout RMSE", labelpad=3)
    _clean_axes(ax_p)

    # A small, low-cost legend in an otherwise empty lower-right region.
    ax_p.legend(
        title="RMSE",
        loc="lower right",
        frameon=False,
        handlelength=1.6,
        handletextpad=0.45,
        labelspacing=0.18,
        borderpad=0.0,
        title_fontsize=7.0,
    )

    rmse_th_30 = float(r_th[np.argmin(np.abs(h_th - 30.0))])
    rmse_om_30 = float(r_om[np.argmin(np.abs(h_om - 30.0))])

    # One compact quantitative sentence replaces the old large callout card.
    ax_p.text(
        0.98,
        0.965,
        "30 s: "
        + rf"$\theta={_sci(rmse_th_30)}$ rad, "
        + rf"$\omega={_sci(rmse_om_30)}$ rad s$^{{-1}}$",
        transform=ax_p.transAxes,
        ha="right",
        va="top",
        fontsize=6.9,
    )

    # Structural inset only: no equal-status third subplot.
    inset = ax_p.inset_axes([0.075, 0.57, 0.37, 0.31])
    inset.plot(
        phase["theta_true"],
        phase["omega_true"],
        color=TRUE_COLOR,
        lw=1.05,
        solid_capstyle="round",
        label="true",
        zorder=2,
    )
    inset.plot(
        phase["theta_sir"],
        phase["omega_sir"],
        color=PRED_COLOR,
        lw=0.95,
        ls=(0, (1.5, 1.1)),
        solid_capstyle="round",
        label="SIR",
        zorder=3,
    )
    inset.plot(
        phase["theta0"],
        phase["omega0"],
        marker="o",
        markersize=2.8,
        markerfacecolor="white",
        markeredgewidth=0.8,
        linestyle="none",
        zorder=4,
    )
    inset.set_xticks([])
    inset.set_yticks([])
    inset.set_xlabel(r"$\theta$", fontsize=6.6, labelpad=0.5)
    inset.set_ylabel(r"$\omega$", fontsize=6.6, labelpad=0.5)
    inset.set_title(
        holdout_id.replace("pendulum_", "holdout "),
        fontsize=6.6,
        pad=1.5,
        loc="left",
    )
    inset.legend(
        loc="upper right",
        frameon=False,
        fontsize=5.8,
        handlelength=1.25,
        handletextpad=0.3,
        labelspacing=0.1,
        borderpad=0.0,
    )
    inset.patch.set_alpha(0.93)

    # Keep frozen-coefficient mismatches loud, as in the original.
    assert abs(pooled["a"] - SIR_A) < 1e-12
    assert abs(pooled["b"] - SIR_B) < 1e-12
    assert abs(SIR_SLOPE + 3.645) < 1e-12

    return fig


def save_figure(fig) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        path = OUT / f"{STEM}.{ext}"
        fig.savefig(
            path,
            dpi=600,
            facecolor="white",
            bbox_inches="tight",
            pad_inches=0.02,
        )
        print(path)


def main() -> None:
    _publication_style()
    fig = build_figure()
    save_figure(fig)
    plt.close(fig)


if __name__ == "__main__":
    main()
