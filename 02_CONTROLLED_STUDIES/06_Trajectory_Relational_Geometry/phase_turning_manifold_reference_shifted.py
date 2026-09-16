from __future__ import annotations

"""Reference-shifted regularized phase coordinate: turning-manifold figure.

Scientific purpose
------------------
This figure illustrates the statement

    A useful coordinate need not merely separate points; it can simplify the
    organization of a scientific target.

A deterministic analytical x1(t) is intentionally multiscale and visually
noise-like.  The branch label is the sign of dx1/dt.  Panel B shows that these
branches remain folded together in an ordinary (x2, dx2/dt) representation.
Panel C instead uses the reference-shifted regularized phase coordinate

    D^rs_{x2} x1 = (u_n + s_eff) g(u_d),

where

    u_n = (dx1/dt)/S_n,
    u_d = (dx2/dt)/S_d,
    s0 = max(0, -min_fit(u_d)),
    s_eff = s0 + kappa,
    w = u_d + s_eff,
    g(w) = w/(w^2 + rho^2).

The paper convention is D_g f = (df/dt)/(dg/dt), so x2 is the
reference/denominator and x1 the numerator/operand.

Because clearance gives w >= kappa > 0, g(w) > 0 throughout the observed
range.  Therefore

    dx1/dt = S_n [D^rs/g - s_eff],

and the exact turning condition dx1/dt = 0 is the one-dimensional manifold

    D^rs = s_eff g(dx2/dt).

Consequently, increasing and decreasing target branches lie on opposite sides
of the turning manifold with no sensitivity-centering collapse locus.

Outputs
-------
Written to the shared figure directory ``<repo>/Figures/figs/``:

phase_turning_manifold_reference_shifted.png
phase_turning_manifold_reference_shifted.pdf   (vector)
phase_turning_manifold_reference_shifted.svg   (vector)
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from scipy.optimize import brentq

# All figures land in the shared figure directory alongside the other panels,
# not next to this script.
OUTDIR = Path(__file__).resolve().parent.parent / "Figures" / "figs"
OUTDIR.mkdir(parents=True, exist_ok=True)
PNG = OUTDIR / "phase_turning_manifold_reference_shifted.png"
PDF = OUTDIR / "phase_turning_manifold_reference_shifted.pdf"
SVG = OUTDIR / "phase_turning_manifold_reference_shifted.svg"

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

# Restrained blue/green palette.
BLUE = "#2F6FA5"       # dx1/dt < 0
GREEN = "#4F9B68"      # dx1/dt > 0
BLUE_DARK = "#1D4E78"
GREEN_DARK = "#2F7D4F"
TEXT = "#222222"
MUTED = "#555555"


# -----------------------------------------------------------------------------
# Fully analytical signals
# -----------------------------------------------------------------------------
def x1(t):
    """Complex-looking but fully deterministic analytical target signal."""
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
    """Exact analytic time derivative of x1(t)."""
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


def x2(t):
    """Analytical reference signal with related but non-identical time scales."""
    t = np.asarray(t)
    return (
        0.82 * np.sin(0.49 * t + 0.45)
        + 0.31 * np.sin(1.18 * t - 0.35)
        + 0.14 * np.sin(2.66 * t + 0.25)
        + 0.08 * np.sin(5.10 * t - 0.6)
    )


def dx2_dt(t):
    """Exact analytic time derivative of x2(t)."""
    t = np.asarray(t)
    return (
        0.82 * 0.49 * np.cos(0.49 * t + 0.45)
        + 0.31 * 1.18 * np.cos(1.18 * t - 0.35)
        + 0.14 * 2.66 * np.cos(2.66 * t + 0.25)
        + 0.08 * 5.10 * np.cos(5.10 * t - 0.6)
    )


# -----------------------------------------------------------------------------
# Reference-shifted regularized phase coordinate
# -----------------------------------------------------------------------------
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
    """Regularized denominator gain g(w)=w/(w^2+rho^2), w=u_d+s_eff."""
    w = np.asarray(u_d, dtype=float) + p.s_eff
    return w / (w * w + p.rho * p.rho)


def fit_phase(t, rho=0.10, kappa=1.0):
    """Fit operand scales and reference clearance on the normalized denominator."""
    n = dx1_dt(t)
    d = dx2_dt(t)
    scale_n = pooled_rms(n)
    scale_d = pooled_rms(d)
    u_d = d / scale_d
    s0 = max(0.0, -float(np.nanmin(u_d)))
    s_eff = s0 + float(kappa)
    return PhaseParams(scale_n, scale_d, float(rho), float(kappa), s0, s_eff)


def drs(t, p: PhaseParams):
    """D^rs_{x2}x1 = (u_n+s_eff)g(u_d)."""
    u_n = dx1_dt(t) / p.scale_n
    u_d = dx2_dt(t) / p.scale_d
    return (u_n + p.s_eff) * gain(u_d, p)


def turning_curve(dx2_values, p: PhaseParams):
    """Exact D^rs curve satisfying dx1/dt=0."""
    u_d = np.asarray(dx2_values, dtype=float) / p.scale_d
    return p.s_eff * gain(u_d, p)


def reconstructed_dx1(dx2_values, drs_values, p: PhaseParams):
    """Exact inversion: dx1/dt = S_n [D^rs/g - s_eff]."""
    u_d = np.asarray(dx2_values, dtype=float) / p.scale_d
    g = gain(u_d, p)
    with np.errstate(divide="ignore", invalid="ignore"):
        u_n = np.asarray(drs_values, dtype=float) / g - p.s_eff
    return p.scale_n * u_n


# -----------------------------------------------------------------------------
# Exact turning events
# -----------------------------------------------------------------------------
def roots_on_interval(func, t_grid, *, zero_tol=1e-12):
    t_grid = np.asarray(t_grid, dtype=float)
    f = np.asarray(func(t_grid), dtype=float)
    roots = []

    hit = np.flatnonzero(np.isfinite(f) & (np.abs(f) <= zero_tol))
    roots.extend(float(t_grid[i]) for i in hit)

    good = np.isfinite(f[:-1]) & np.isfinite(f[1:])
    idx = np.flatnonzero(good & (f[:-1] * f[1:] < 0.0))
    for i in idx:
        roots.append(
            float(brentq(lambda z: float(func(z)), float(t_grid[i]), float(t_grid[i + 1])))
        )

    if not roots:
        return np.empty(0, dtype=float)

    roots = np.array(sorted(roots), dtype=float)
    keep = np.r_[True, np.diff(roots) > 1e-8]
    return roots[keep]


def exact_turning_times(t_grid):
    return roots_on_interval(dx1_dt, t_grid)


def colored_line(ax, x, y, positive_mask, *, lw=1.45):
    """Draw a continuous curve whose color follows the sign of dx1/dt."""
    points = np.column_stack([x, y]).reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    colors = [GREEN if flag else BLUE for flag in positive_mask[:-1]]
    lc = LineCollection(
        segments,
        colors=colors,
        linewidths=lw,
        capstyle="round",
        joinstyle="round",
        zorder=3,
    )
    ax.add_collection(lc)
    ax.autoscale_view()
    return lc


# -----------------------------------------------------------------------------
# Figure
# -----------------------------------------------------------------------------
def make_figure():
    # Dense grid supports smooth rendering and root bracketing; turning points are
    # refined continuously with Brent's method and are not restricted to this grid.
    t = np.linspace(0.0, 36.0, 12000)
    y1 = x1(t)
    y2 = x2(t)
    r1 = dx1_dt(t)
    r2 = dx2_dt(t)
    p = fit_phase(t)
    D = drs(t, p)

    turning_t = exact_turning_times(t)
    turning_r2 = dx2_dt(turning_t)
    turning_D = drs(turning_t, p)

    increasing = r1 > 0.0
    decreasing = r1 < 0.0

    fig = plt.figure(figsize=(10.9, 6.35), facecolor="white")
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[0.88, 1.55],
        hspace=0.37,
        wspace=0.26,
        left=0.075,
        right=0.965,
        bottom=0.12,
        top=0.90,
    )

    # ------------------------------------------------------------------ Panel A
    ax0 = fig.add_subplot(gs[0, :])
    colored_line(ax0, t, y1, increasing)
    ax0.scatter(
        turning_t,
        x1(turning_t),
        s=18,
        facecolor="white",
        edgecolor="#111111",
        linewidth=0.7,
        zorder=5,
    )
    ax0.set_xlim(float(t.min()), float(t.max()))
    ax0.set_ylabel(r"$x_1(t)$", fontsize=12)
    ax0.set_xlabel(r"$t$", fontsize=11, labelpad=1)
    ax0.spines[["top", "right"]].set_visible(False)
    ax0.tick_params(labelsize=9)
    ax0.text(0.01, 1.02, "A", transform=ax0.transAxes, fontsize=12, fontweight="bold", va="top")
    ax0.text(
        0.04,
        1.02,
        "Analytical Target With Multiscale, Noise-Like Structure",
        transform=ax0.transAxes,
        fontsize=11.5,
        fontweight="bold",
        va="top",
    )
    ax0.text(
        0.04,
        0.90,
        r"Line Color Encodes Branch Sign Of $\dot{x}_1$; Open Circles Mark Exact Turning Points",
        transform=ax0.transAxes,
        fontsize=9.3,
        va="top",
        color=MUTED,
    )
    ax0.plot([], [], color=GREEN, lw=2.0, label=r"$\dot{x}_1>0$")
    ax0.plot([], [], color=BLUE, lw=2.0, label=r"$\dot{x}_1<0$")
    ax0.legend(
        loc="upper right",
        frameon=False,
        fontsize=8.9,
        ncol=2,
        handlelength=2.2,
        columnspacing=1.2,
    )

    # ------------------------------------------------------------------ Panel B
    ax1 = fig.add_subplot(gs[1, 0])
    ax1.scatter(
        y2[decreasing],
        r2[decreasing],
        s=6.5,
        alpha=0.58,
        linewidths=0,
        color=BLUE,
        label=r"$\dot{x}_1<0$",
    )
    ax1.scatter(
        y2[increasing],
        r2[increasing],
        s=6.5,
        alpha=0.58,
        linewidths=0,
        color=GREEN,
        label=r"$\dot{x}_1>0$",
    )
    ax1.scatter(
        x2(turning_t),
        dx2_dt(turning_t),
        s=27,
        facecolor="white",
        edgecolor="#202020",
        linewidth=0.75,
        zorder=5,
    )
    ax1.set_xlabel(r"$x_2$", fontsize=12)
    ax1.set_ylabel(r"$\dot{x}_2$", fontsize=12)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.tick_params(labelsize=9)
    ax1.text(0.02, 0.98, "B", transform=ax1.transAxes, fontsize=12, fontweight="bold", va="top")
    ax1.text(
        0.09,
        0.98,
        "Ordinary Coordinates",
        transform=ax1.transAxes,
        fontsize=11.5,
        fontweight="bold",
        va="top",
    )
    ax1.text(
        0.09,
        0.90,
        r"Branch Label = Sign Of Target $\dot{x}_1$",
        transform=ax1.transAxes,
        fontsize=9.4,
        va="top",
        color=MUTED,
    )
    ax1.text(
        0.05,
        0.06,
        "Increasing And Decreasing Branches\nRemain Folded Together",
        transform=ax1.transAxes,
        fontsize=9.8,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbbbbb", alpha=0.94),
    )
    ax1.legend(
        loc="upper right",
        frameon=False,
        fontsize=9.0,
        markerscale=2.2,
        handletextpad=0.4,
    )

    # ------------------------------------------------------------------ Panel C
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.scatter(
        r2[decreasing], D[decreasing], s=6.5, alpha=0.60, linewidths=0, color=BLUE, zorder=2
    )
    ax2.scatter(
        r2[increasing], D[increasing], s=6.5, alpha=0.60, linewidths=0, color=GREEN, zorder=2
    )

    dx2_grid = np.linspace(float(r2.min()), float(r2.max()), 1200)
    turnD = turning_curve(dx2_grid, p)
    ax2.plot(
        dx2_grid,
        turnD,
        color="#111111",
        lw=1.85,
        label=r"$\dot{x}_1=0$ Turning Manifold",
        zorder=6,
    )
    ax2.scatter(
        turning_r2,
        turning_D,
        s=31,
        facecolor="white",
        edgecolor="#202020",
        linewidth=0.8,
        zorder=8,
    )

    ax2.set_xlabel(r"$\dot{x}_2$", fontsize=12)
    ax2.set_ylabel(r"$D^{\mathrm{rs}}_{x_2}x_1$", fontsize=12)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.tick_params(labelsize=9)
    ax2.text(0.02, 0.98, "C", transform=ax2.transAxes, fontsize=12, fontweight="bold", va="top")
    ax2.text(
        0.09,
        0.98,
        "Relational Coordinates",
        transform=ax2.transAxes,
        fontsize=11.5,
        fontweight="bold",
        va="top",
    )
    ax2.text(
        0.09,
        0.90,
        r"Reference-Shifted Phase Organizes The Target Around A Turning Manifold",
        transform=ax2.transAxes,
        fontsize=9.2,
        va="top",
        color=MUTED,
    )
    ax2.legend(
        loc="upper left",
        bbox_to_anchor=(0.12, 0.86),
        frameon=True,
        framealpha=0.95,
        fontsize=8.8,
        edgecolor="#bbbbbb",
    )

    # Explanatory box: low-left and close to the D-axis, away from data.
    eq = (
        r"$D^{\rm rs}=(u_n+s_{\rm eff})g$"
        + "\n"
        + r"$\dot{x}_1=0\;\Longleftrightarrow\;D^{\rm rs}=s_{\rm eff}g(\dot{x}_2)$"
    )
    ax2.text(
        0.018,
        0.035,
        eq,
        transform=ax2.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.9,
        bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#aaaaaa", alpha=0.95),
        zorder=12,
    )

    # Pick a crowded turning-point neighborhood for the inset.  A point near
    # xdot2 ~ -0.23 gives a clear local view and preserves continuity with the
    # earlier sensitivity-centered diagnostic figure, but there is no collapse.
    target_x = -0.23
    idx_center = int(np.argmin(np.abs(turning_r2 - target_x)))
    x0 = float(turning_r2[idx_center])
    y0 = float(turning_D[idx_center])
    xhalf = 0.16
    yhalf = 0.19
    xlim = (x0 - xhalf, x0 + xhalf)
    ylim = (max(0.0, y0 - yhalf), y0 + yhalf)

    axins = ax2.inset_axes([0.63, 0.50, 0.35, 0.35], zorder=20)
    local = (r2 >= xlim[0]) & (r2 <= xlim[1]) & (D >= ylim[0]) & (D <= ylim[1])
    axins.scatter(
        r2[local & decreasing],
        D[local & decreasing],
        s=5.0,
        alpha=0.74,
        linewidths=0,
        color=BLUE,
    )
    axins.scatter(
        r2[local & increasing],
        D[local & increasing],
        s=5.0,
        alpha=0.74,
        linewidths=0,
        color=GREEN,
    )
    gd = np.linspace(xlim[0], xlim[1], 500)
    axins.plot(gd, turning_curve(gd, p), color="#111111", lw=1.45, zorder=5)

    tlocal = (
        (turning_r2 >= xlim[0])
        & (turning_r2 <= xlim[1])
        & (turning_D >= ylim[0])
        & (turning_D <= ylim[1])
    )
    axins.scatter(
        turning_r2[tlocal],
        turning_D[tlocal],
        s=27,
        facecolor="white",
        edgecolor="#202020",
        linewidth=0.75,
        zorder=7,
    )
    axins.set_xlim(*xlim)
    axins.set_ylim(*ylim)
    axins.tick_params(labelsize=7, pad=1)
    axins.set_title("Zoom: Local Branch Separation", fontsize=8.4, pad=3)
    for spine in axins.spines.values():
        spine.set_linewidth(0.75)
    ax2.indicate_inset_zoom(axins, edgecolor="#777777", alpha=0.65, linewidth=0.8)

    # Small note emphasizing the key consequence of using D^rs.
    ax2.text(
        0.56,
        0.41,
        "$g>0$: Branch Sign Is Preserved\nAcross The Relational Chart",
        transform=ax2.transAxes,
        ha="left",
        va="center",
        fontsize=8.3,
        color=GREEN_DARK,
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#c7d9cc", alpha=0.92),
        zorder=13,
    )

    fig.suptitle(
        "Relational Coordinates Can Simplify The Organization Of A Scientific Target",
        fontsize=16.5,
        fontweight="bold",
        y=0.975,
    )
    fig.text(
        0.5,
        0.035,
        "A Useful Coordinate Need Not Merely Separate Points: It Can Turn A Folded Dynamical Target Into A Simple Branch Boundary.",
        ha="center",
        va="center",
        fontsize=10.2,
        color="#333333",
    )

    return fig, p, t, r1, r2, D, turning_t


def main():
    fig, p, t, r1, r2, D, turning_t = make_figure()
    fig.savefig(PNG, dpi=500, bbox_inches="tight", facecolor="white")
    fig.savefig(PDF, bbox_inches="tight", facecolor="white")
    fig.savefig(SVG, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    rec = reconstructed_dx1(r2, D, p)
    stable = np.isfinite(rec)
    maxerr = float(np.max(np.abs(rec[stable] - r1[stable]))) if np.any(stable) else np.nan

    # Verify the analytical branch-separation statement numerically.
    curve_at_samples = turning_curve(r2, p)
    signed_gap = D - curve_at_samples
    branch_mismatch = int(
        np.sum(((r1 > 1e-10) & (signed_gap <= 0.0)) | ((r1 < -1e-10) & (signed_gap >= 0.0)))
    )

    gvals = gain(r2 / p.scale_d, p)

    print("Reference-shifted regularized phase parameters:")
    print(f"  S_n     = {p.scale_n:.10f}")
    print(f"  S_d     = {p.scale_d:.10f}")
    print(f"  rho     = {p.rho:.8f}")
    print(f"  kappa   = {p.kappa:.8f}")
    print(f"  s0      = {p.s0:.10f}")
    print(f"  s_eff   = {p.s_eff:.10f}")
    print(f"  min(g)  = {np.min(gvals):.10f}")
    print(f"  exact turning events dx1/dt=0: {len(turning_t)}")
    print(f"  inversion max |error|: {maxerr:.3e}")
    print(f"  branch-sign mismatches vs turning manifold: {branch_mismatch}")
    print()
    print("Saved:")
    print(" ", PNG)
    print(" ", PDF)
    print(" ", SVG)


if __name__ == "__main__":
    main()
