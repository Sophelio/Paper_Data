from __future__ import annotations

"""Five-panel turning-manifold figure with sensitivity-centered phase coordinates in Panel C.

Panel D uses $\dot{x}_1$ versus $\dot{x}_2$.

Outputs
-------
phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.png
phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.pdf
phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.svg
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from scipy.optimize import brentq

OUTDIR = Path(__file__).resolve().parent
PNG = OUTDIR / "phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.png"
PDF = OUTDIR / "phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.pdf"
SVG = OUTDIR / "phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.svg"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": [
            "Times New Roman",
            "Tinos",
            "Times",
            "Nimbus Roman",
            "Liberation Serif",
            "DejaVu Serif",
        ],
        "mathtext.fontset": "stix",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.linewidth": 0.8,
    }
)

BLUE = "#2F6FA5"
GREEN = "#4F9B68"
PURPLE = "#4B2E83"
TEXT = "#222222"
MUTED = "#555555"


def x1(t):
    t = np.asarray(t)
    phase = 0.72 * t + 0.28 * np.sin(0.13 * t)
    return (
        0.95 * np.sin(phase)
        + 0.34 * np.sin(2.05 * t + 0.7)
        + 0.18 * np.sin(4.70 * t - 0.3)
        + 0.16 * np.sin(0.17 * t) * np.sin(1.33 * t + 0.4)
        + 0.08 * np.sin(7.40 * t + 1.1)
    )


def dx1_dt(t):
    t = np.asarray(t)
    phase = 0.72 * t + 0.28 * np.sin(0.13 * t)
    phase_dot = 0.72 + 0.28 * 0.13 * np.cos(0.13 * t)
    return (
        0.95 * np.cos(phase) * phase_dot
        + 0.34 * 2.05 * np.cos(2.05 * t + 0.7)
        + 0.18 * 4.70 * np.cos(4.70 * t - 0.3)
        + 0.16
        * (
            0.17 * np.cos(0.17 * t) * np.sin(1.33 * t + 0.4)
            + 1.33 * np.sin(0.17 * t) * np.cos(1.33 * t + 0.4)
        )
        + 0.08 * 7.40 * np.cos(7.40 * t + 1.1)
    )


def ddx1_dt2(t):
    t = np.asarray(t)
    phase = 0.72 * t + 0.28 * np.sin(0.13 * t)
    phase_dot = 0.72 + 0.28 * 0.13 * np.cos(0.13 * t)
    phase_ddot = -0.28 * (0.13**2) * np.sin(0.13 * t)

    term1 = 0.95 * (-np.sin(phase) * phase_dot**2 + np.cos(phase) * phase_ddot)
    term2 = -0.34 * (2.05**2) * np.sin(2.05 * t + 0.7)
    term3 = -0.18 * (4.70**2) * np.sin(4.70 * t - 0.3)

    a = 0.17
    b = 1.33
    term4 = 0.16 * (
        -a**2 * np.sin(a * t) * np.sin(b * t + 0.4)
        + 2 * a * b * np.cos(a * t) * np.cos(b * t + 0.4)
        - b**2 * np.sin(a * t) * np.sin(b * t + 0.4)
    )
    term5 = -0.08 * (7.40**2) * np.sin(7.40 * t + 1.1)
    return term1 + term2 + term3 + term4 + term5


def x2(t):
    t = np.asarray(t)
    return (
        0.82 * np.sin(0.49 * t + 0.45)
        + 0.31 * np.sin(1.18 * t - 0.35)
        + 0.14 * np.sin(2.66 * t + 0.25)
        + 0.08 * np.sin(5.10 * t - 0.6)
    )


def dx2_dt(t):
    t = np.asarray(t)
    return (
        0.82 * 0.49 * np.cos(0.49 * t + 0.45)
        + 0.31 * 1.18 * np.cos(1.18 * t - 0.35)
        + 0.14 * 2.66 * np.cos(2.66 * t + 0.25)
        + 0.08 * 5.10 * np.cos(5.10 * t - 0.6)
    )


@dataclass(frozen=True)
class PhaseParams:
    scale_n: float
    scale_d: float
    rho: float
    kappa: float
    s0: float
    s_eff: float


def pooled_rms(a):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return 1e-15
    return max(float(np.sqrt(np.mean(a * a))), 1e-15)


def gain(u_d, p: PhaseParams):
    w = np.asarray(u_d, dtype=float) + p.s_eff
    return w / (w * w + p.rho * p.rho)


def fit_phase(t, rho=0.10, kappa=1.0):
    n = dx1_dt(t)
    d = dx2_dt(t)
    scale_n = pooled_rms(n)
    scale_d = pooled_rms(d)
    u_d = d / scale_d
    s0 = max(0.0, -float(np.nanmin(u_d)))
    s_eff = s0 + float(kappa)
    return PhaseParams(scale_n, scale_d, float(rho), float(kappa), s0, s_eff)


def drs(t, p: PhaseParams):
    u_n = dx1_dt(t) / p.scale_n
    u_d = dx2_dt(t) / p.scale_d
    return (u_n + p.s_eff) * gain(u_d, p)


def fit_g_bar(t, p: PhaseParams):
    """Fit mean denominator gain used by sensitivity centering."""
    u_d = dx2_dt(t) / p.scale_d
    return float(np.mean(gain(u_d, p)))


def dsc(t, p: PhaseParams, g_bar: float):
    """Sensitivity-centered reference-shifted coordinate.

    D^sc = D^rs - g_bar*u_n
         = u_n*(g-g_bar) + s_eff*g.
    """
    u_n = dx1_dt(t) / p.scale_n
    u_d = dx2_dt(t) / p.scale_d
    g = gain(u_d, p)
    return u_n * (g - g_bar) + p.s_eff * g


def turning_curve(dx2_values, p: PhaseParams):
    u_d = np.asarray(dx2_values, dtype=float) / p.scale_d
    return p.s_eff * gain(u_d, p)


def roots_on_interval(func, t_grid, *, zero_tol=1e-12):
    t_grid = np.asarray(t_grid, dtype=float)
    f = np.asarray(func(t_grid), dtype=float)
    roots = []
    hit = np.flatnonzero(np.isfinite(f) & (np.abs(f) <= zero_tol))
    roots.extend(float(t_grid[i]) for i in hit)
    good = np.isfinite(f[:-1]) & np.isfinite(f[1:])
    idx = np.flatnonzero(good & (f[:-1] * f[1:] < 0.0))
    for i in idx:
        roots.append(float(brentq(lambda z: float(func(z)), float(t_grid[i]), float(t_grid[i + 1]))))
    if not roots:
        return np.empty(0, dtype=float)
    roots = np.array(sorted(roots), dtype=float)
    keep = np.r_[True, np.diff(roots) > 1e-8]
    return roots[keep]


def colored_line(ax, x, y, positive_mask, *, lw=1.45):
    points = np.column_stack([x, y]).reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    colors = [GREEN if flag else BLUE for flag in positive_mask[:-1]]
    lc = LineCollection(segments, colors=colors, linewidths=lw, capstyle="round", joinstyle="round", zorder=3)
    ax.add_collection(lc)
    ax.autoscale_view()
    return lc


def add_scatter_panel(ax, xneg, yneg, xpos, ypos, xtp, ytp, panel_letter, title, subtitle, xlabel, ylabel, textbox=None):
    ax.scatter(xneg, yneg, s=6.3, alpha=0.60, linewidths=0, color=BLUE, zorder=2)
    ax.scatter(xpos, ypos, s=6.3, alpha=0.60, linewidths=0, color=GREEN, zorder=2)
    ax.scatter(xtp, ytp, s=28, facecolor="white", edgecolor="#202020", linewidth=0.75, zorder=5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8.6)
    ax.set_xlabel(xlabel, fontsize=11.6)
    ax.set_ylabel(ylabel, fontsize=11.6)
    ax.text(0.02, 1.12, panel_letter, transform=ax.transAxes, fontsize=11.8, fontweight="bold", va="top")
    ax.text(0.09, 1.12, title, transform=ax.transAxes, fontsize=10.9, fontweight="bold", va="top")
    ax.text(0.09, 1.04, subtitle, transform=ax.transAxes, fontsize=8.9, va="top", color=MUTED)
    if textbox is not None:
        ax.text(
            textbox.get("x", 0.05),
            textbox.get("y", 0.06),
            textbox["text"],
            transform=ax.transAxes,
            fontsize=textbox.get("fontsize", 8.8),
            va=textbox.get("va", "bottom"),
            ha=textbox.get("ha", "left"),
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbbbbb", alpha=0.94),
            zorder=10,
        )


def main():
    t = np.linspace(0.0, 36.0, 12000)
    y1 = x1(t)
    y2 = x2(t)
    r1 = dx1_dt(t)
    r2 = dx2_dt(t)
    a1 = ddx1_dt2(t)
    p = fit_phase(t)
    g_bar = fit_g_bar(t, p)
    D = dsc(t, p, g_bar)

    turning_t = roots_on_interval(dx1_dt, t)
    increasing = r1 > 0.0
    decreasing = r1 < 0.0

    # Verify x1 and x2 turning points remain distinct in time.
    x2_turning_t = roots_on_interval(dx2_dt, t)
    if turning_t.size and x2_turning_t.size:
        min_tp_separation = float(np.min(np.abs(turning_t[:, None] - x2_turning_t[None, :])))
        if min_tp_separation < 1e-6:
            raise RuntimeError("An x1 turning point coincides with an x2 turning point; perturb x2(t).")

    tp_x1 = x1(turning_t)
    tp_x2 = x2(turning_t)
    tp_r1 = dx1_dt(turning_t)
    tp_r2 = dx2_dt(turning_t)
    tp_a1 = ddx1_dt2(turning_t)
    tp_D = dsc(turning_t, p, g_bar)

    fig = plt.figure(figsize=(10.9, 9.1), facecolor="white")
    gs = fig.add_gridspec(
        3,
        2,
        height_ratios=[0.88, 1.25, 1.25],
        hspace=0.60,
        wspace=0.28,
        left=0.075,
        right=0.965,
        bottom=0.08,
        top=0.92,
    )

    # Panel A
    ax0 = fig.add_subplot(gs[0, :])
    ax0.plot(t, y2, color=PURPLE, lw=1.45, alpha=0.82, zorder=2)
    for tt, yy1, yy2 in zip(turning_t, tp_x1, tp_x2, strict=True):
        ax0.plot([tt, tt], [yy1, yy2], color="#111111", lw=0.55, linestyle=(0, (2.0, 2.4)), alpha=0.48, zorder=2.5)
    colored_line(ax0, t, y1, increasing, lw=1.45)
    ax0.scatter(turning_t, tp_x1, s=18, facecolor="white", edgecolor="#111111", linewidth=0.7, zorder=5)
    ax0.set_xlim(float(t.min()), float(t.max()))
    ax0.set_ylabel(r"$x_1(t)$", fontsize=12)
    ax0.set_xlabel(r"$t$", fontsize=11.1, labelpad=1)
    ax0.spines[["top", "right"]].set_visible(False)
    ax0.tick_params(labelsize=9)
    ax0.text(0.01, 1.16, "A", transform=ax0.transAxes, fontsize=12, fontweight="bold", va="top")
    ax0.text(0.04, 1.16, "Analytical Target With Multiscale, Noise-Like Structure", transform=ax0.transAxes, fontsize=11.4, fontweight="bold", va="top")
    ax0.text(0.04, 1.04, r"Line Color Encodes Branch Sign Of $\dot{x}_1$; Dashed Guides Show $x_2$ At The Same Turning Times", transform=ax0.transAxes, fontsize=9.2, va="top", color=MUTED)
    ax0.plot([], [], color=GREEN, lw=2.0, label=r"$\dot{x}_1>0$")
    ax0.plot([], [], color=BLUE, lw=2.0, label=r"$\dot{x}_1<0$")
    ax0.plot([], [], color=PURPLE, lw=1.45, label=r"$x_2(t)$")
    ax0.legend(loc="upper right", frameon=False, fontsize=8.8, ncol=3, handlelength=2.2, columnspacing=1.2)

    # Panel B
    ax1 = fig.add_subplot(gs[1, 0])
    add_scatter_panel(
        ax1,
        y2[decreasing], r2[decreasing], y2[increasing], r2[increasing],
        tp_x2, tp_r2,
        "B",
        "Level-Rate Relational Coordinates",
        r"Target Branch Label = Sign Of $\dot{x}_1$",
        r"$x_2$",
        r"$\dot{x}_2$",
        textbox={"text": "Branches Of The Target\nRemain Folded Together", "x": 0.05, "y": 0.06, "fontsize": 9.5},
    )
    ax1.scatter([], [], s=18, color=BLUE, label=r"$\dot{x}_1<0$")
    ax1.scatter([], [], s=18, color=GREEN, label=r"$\dot{x}_1>0$")
    ax1.legend(loc="upper right", frameon=False, fontsize=8.8, markerscale=1.6, handletextpad=0.4)

    # Panel C
    ax2 = fig.add_subplot(gs[1, 1])
    add_scatter_panel(
        ax2,
        r2[decreasing], D[decreasing], r2[increasing], D[increasing],
        tp_r2, tp_D,
        "C",
        "Sensitivity-Centered Phase Coordinates",
        r"Turning Manifold And Conditioning Locus Organize The Same Target",
        r"$\dot{x}_2$",
        r"$D^{\mathrm{sc}}_{x_2}x_1$",
    )
    dx2_grid = np.linspace(float(r2.min()), float(r2.max()), 1200)
    turnD = turning_curve(dx2_grid, p)
    ax2.plot(dx2_grid, turnD, color="#111111", lw=1.85, label=r"$\dot{x}_1=0$ Turning Manifold", zorder=6)

    # Sensitivity centering makes the direct numerator sensitivity proportional
    # to g-g_bar.  Its zero defines the conditioning locus.
    cond_fun = lambda z: float(gain(np.asarray(z) / p.scale_d, p) - g_bar)
    x_cond = float(brentq(cond_fun, float(r2.min()), float(r2.max())))
    y_cond = float(p.s_eff * g_bar)
    ax2.axvline(
        x_cond,
        color="#2F7D4F",
        lw=1.25,
        linestyle=(0, (4.0, 3.0)),
        alpha=0.95,
        label=r"$g=\bar g$ Conditioning Locus",
        zorder=5,
    )
    ax2.scatter([x_cond], [y_cond], marker="x", s=47, color="#1D4E78", linewidth=1.25, zorder=9)
    ax2.legend(loc="upper left", bbox_to_anchor=(0.12, 0.86), frameon=True, framealpha=0.95, fontsize=8.25, edgecolor="#bbbbbb")
    ax2.text(
        0.018,
        0.035,
        r"$D^{\rm sc}=u_n(g-\bar g)+s_{\rm eff}g$" + "\n" + r"$\dot{x}_1=0\;\Longleftrightarrow\;D^{\rm sc}=s_{\rm eff}g(\dot{x}_2)$",
        transform=ax2.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.55,
        bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#aaaaaa", alpha=0.95),
        zorder=12,
    )
    target_x = -0.23
    idx_center = int(np.argmin(np.abs(tp_r2 - target_x)))
    x0 = float(tp_r2[idx_center])
    y0 = float(tp_D[idx_center])
    xhalf, yhalf = 0.16, 0.19
    xlim = (x0 - xhalf, x0 + xhalf)
    ylim = (max(0.0, y0 - yhalf), y0 + yhalf)
    axins = ax2.inset_axes([0.63, 0.50, 0.35, 0.35], zorder=20)
    local = (r2 >= xlim[0]) & (r2 <= xlim[1]) & (D >= ylim[0]) & (D <= ylim[1])
    axins.scatter(r2[local & decreasing], D[local & decreasing], s=5.0, alpha=0.74, linewidths=0, color=BLUE)
    axins.scatter(r2[local & increasing], D[local & increasing], s=5.0, alpha=0.74, linewidths=0, color=GREEN)
    gd = np.linspace(xlim[0], xlim[1], 500)
    axins.plot(gd, turning_curve(gd, p), color="#111111", lw=1.45, zorder=5)
    axins.axvline(x_cond, color="#2F7D4F", lw=1.05, linestyle=(0, (4.0, 3.0)), alpha=0.95, zorder=5)
    axins.scatter([x_cond], [y_cond], marker="x", s=38, color="#1D4E78", linewidth=1.1, zorder=8)
    tlocal = (tp_r2 >= xlim[0]) & (tp_r2 <= xlim[1]) & (tp_D >= ylim[0]) & (tp_D <= ylim[1])
    axins.scatter(tp_r2[tlocal], tp_D[tlocal], s=27, facecolor="white", edgecolor="#202020", linewidth=0.75, zorder=7)
    axins.set_xlim(*xlim)
    axins.set_ylim(*ylim)
    axins.tick_params(labelsize=7, pad=1)
    axins.set_title("Zoom: Conditioning Locus", fontsize=8.3, pad=3)
    for spine in axins.spines.values():
        spine.set_linewidth(0.75)
    ax2.indicate_inset_zoom(axins, edgecolor="#777777", alpha=0.65, linewidth=0.8)
    ax2.text(0.57, 0.41, "$g=\\bar g$: Direct Numerator Sensitivity\\nVanishes At The Conditioning Locus", transform=ax2.transAxes, ha="left", va="center", fontsize=8.0, color="#2F7D4F", bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#c7d9cc", alpha=0.92), zorder=13)

    # Panel D
    ax3 = fig.add_subplot(gs[2, 0])
    add_scatter_panel(
        ax3,
        r2[decreasing], r1[decreasing], r2[increasing], r1[increasing],
        tp_r2, tp_r1,
        "D",
        "Rate-Rate Relational Coordinates",
        r"Turning Events Remain On $\dot{x}_1=0$ But Gain Reference-Rate Context",
        r"$\dot{x}_2$",
        r"$\dot{x}_1$",
        textbox={"text": "Same Turning Manifold As Before,\nNow Viewed Against The Reference\nRate Instead Of The State Level", "x": 0.05, "y": 0.05, "fontsize": 8.8},
    )
    ax3.axhline(0.0, color="#111111", lw=1.2, zorder=1, alpha=0.9)

    # Panel E
    ax4 = fig.add_subplot(gs[2, 1])
    add_scatter_panel(
        ax4,
        a1[decreasing], r1[decreasing], a1[increasing], r1[increasing],
        tp_a1, tp_r1,
        "E",
        "Rate-Acceleration Relational Coordinates",
        r"Turning Points Map To $\dot{x}_1=0$ At Their Local Curvature Values",
        r"$\ddot{x}_1$",
        r"$\dot{x}_1$",
        textbox={"text": "Adds Local Curvature Context\nAt Each Turning Event", "x": 0.05, "y": 0.05, "fontsize": 8.8},
    )
    ax4.axhline(0.0, color="#111111", lw=1.2, zorder=1, alpha=0.9)

    fig.suptitle(
        "Relational Coordinates Can Simplify The Organization Of A Scientific Target",
        fontsize=16.2,
        fontweight="bold",
        y=0.975,
    )
    fig.text(
        0.5,
        0.025,
        "A Useful Coordinate Need Not Merely Separate Points: It Can Simplify Turning Structure, Branching, And Event Organization.",
        ha="center",
        va="center",
        fontsize=10.0,
        color="#333333",
    )

    fig.savefig(PNG, dpi=500, bbox_inches="tight", facecolor="white")
    fig.savefig(PDF, bbox_inches="tight", facecolor="white")
    fig.savefig(SVG, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print("Saved:")
    print(PNG)
    print(PDF)
    print(SVG)


if __name__ == "__main__":
    main()
