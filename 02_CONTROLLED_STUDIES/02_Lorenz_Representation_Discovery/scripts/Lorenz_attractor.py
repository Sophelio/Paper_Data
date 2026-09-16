"""Generate the Lorenz-system dataset used in Section 2.6.1 of the SIR paper.

The Lorenz system (Eq. lorenz in the paper):

    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z

with initial condition (1.0, 1.0, 1.0) and parameters
rho = 28.0, sigma = 10.0, beta = 8/3, sampled on t in [0, 40]
with Delta t = 0.01.

Running this script:
  * integrates the system to high accuracy,
  * writes ``lorenz_dt001.parquet`` (columns: ``times, x, y, z``) so it can be
    ingested directly by an SIR data provider (see ``providers/``),
  * renders two publication-grade figures (the 3-D attractor and the x/y/z
    time series) as 600-dpi PNG and vector PDF.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.mplot3d.art3d import Line3DCollection


# --------------------------------------------------------------------------
# Paper parameters (Section 2.6.1)
# --------------------------------------------------------------------------
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

X0 = (1.0, 1.0, 1.0)
DT = 0.001
TMAX = 40.0

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / "data"
PARQUET_PATH = DATA_DIR / "lorenz_dt001.parquet"
EXACT_DERIV_PARQUET_PATH = DATA_DIR / "lorenz_dt001_exact_derivatives.parquet"


# --------------------------------------------------------------------------
# Lorenz system
# --------------------------------------------------------------------------
def lorenz(t, u, sigma=SIGMA, rho=RHO, beta=BETA):
    """Right-hand side of the Lorenz system."""
    x, y, z = u
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return [dx, dy, dz]


def generate_lorenz(dt=DT, tmax=TMAX, x0=X0):
    """Integrate the Lorenz system on a uniform grid t in [0, tmax].

    Returns a DataFrame with columns ``times, x, y, z``. The ``times`` column
    name matches the convention expected by the SIR parquet data providers.
    """
    # Inclusive endpoint at exactly tmax with a clean dt step.
    n_steps = int(round(tmax / dt))
    t_eval = np.linspace(0.0, tmax, n_steps + 1)

    sol = solve_ivp(
        lorenz,
        (0.0, tmax),
        x0,
        method="DOP853",
        t_eval=t_eval,
        rtol=1e-12,
        atol=1e-12,
        dense_output=False,
    )
    if not sol.success:
        raise RuntimeError(f"Lorenz integration failed: {sol.message}")

    return pd.DataFrame(
        {
            "times": sol.t.astype(np.float64),
            "x": sol.y[0].astype(np.float64),
            "y": sol.y[1].astype(np.float64),
            "z": sol.y[2].astype(np.float64),
        }
    )


def add_exact_derivatives(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with analytic (manufactured) derivatives appended.

    Instead of approximating ``dx, dy, dz`` with finite differences, evaluate the
    Lorenz right-hand side directly at every sampled state. This reproduces the
    "exact derivative" recovery in Eq. (lorenz_diff_exact) of the paper, where the
    system is recovered perfectly. Columns: ``times, x, y, z, dx, dy, dz``.
    """
    x = df["x"].to_numpy(dtype=np.float64)
    y = df["y"].to_numpy(dtype=np.float64)
    z = df["z"].to_numpy(dtype=np.float64)

    out = df.copy()
    out["dx"] = SIGMA * (y - x)
    out["dy"] = x * (RHO - z) - y
    out["dz"] = x * y - BETA * z
    return out


# --------------------------------------------------------------------------
# Publication-grade plotting
# --------------------------------------------------------------------------
def _set_publication_style():
    """A compact serif style suitable for PRL / Nature single-column figures."""
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 800,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "mathtext.fontset": "cm",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 9,
            "axes.labelsize": 10,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.minor.size": 2.0,
            "ytick.minor.size": 2.0,
            "lines.linewidth": 1.0,
            "legend.frameon": False,
            "axes.grid": False,
        }
    )


def plot_attractor(df: pd.DataFrame, out_stem: Path):
    """3-D Lorenz attractor, trajectory colored by time."""
    x = df["x"].to_numpy()
    y = df["y"].to_numpy()
    z = df["z"].to_numpy()
    t = df["times"].to_numpy()

    points = np.column_stack([x, y, z]).reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    fig = plt.figure(figsize=(3.6, 3.1))
    ax = fig.add_subplot(111, projection="3d", proj_type="ortho")

    # Subtle underlay to make the two lobes read cleanly in print.
    ax.plot(
        x,
        y,
        z,
        color="0.70",
        linewidth=0.30,
        alpha=0.22,
        antialiased=True,
    )

    lc = Line3DCollection(
        segments,
        cmap="plasma",
        array=t[:-1],
        linewidth=0.70,
        alpha=0.95,
    )
    ax.add_collection3d(lc)

    pad = 1.2
    ax.set_xlim(x.min() - pad, x.max() + pad)
    ax.set_ylim(y.min() - pad, y.max() + pad)
    ax.set_zlim(z.min() - pad, z.max() + pad)
    ax.set_box_aspect((np.ptp(x), np.ptp(y), np.ptp(z) * 0.85))

    ax.set_xlabel(r"$x$", labelpad=-8)
    ax.set_ylabel(r"$y$", labelpad=-8)
    ax.set_zlabel(r"$z$", labelpad=-7)
    ax.tick_params(pad=-2, width=0.7, colors="0.20")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
    ax.zaxis.set_major_locator(ticker.MaxNLocator(4))
    ax.view_init(elev=20, azim=-52)

    # Clean pane styling for publication output.
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_edgecolor("0.87")
        axis.pane.set_facecolor((1.0, 1.0, 1.0, 0.00))
    ax.grid(True, linewidth=0.35, alpha=0.28, color="0.65")

    # Mark start/end points to orient the trajectory in static print.
    ax.scatter([x[0]], [y[0]], [z[0]], s=14, color="#36454F", depthshade=False, zorder=5)
    ax.scatter([x[-1]], [y[-1]], [z[-1]], s=14, color="#B22222", depthshade=False, zorder=5)

    cbar = fig.colorbar(lc, ax=ax, pad=0.06, shrink=0.62, aspect=22)
    cbar.set_label(r"$t$", rotation=0, labelpad=7)
    cbar.outline.set_linewidth(0.6)
    cbar.ax.tick_params(width=0.6, length=2.5)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_stem.with_suffix(f".{ext}"))
    plt.close(fig)


def plot_timeseries(df: pd.DataFrame, out_stem: Path, tmax_plot: float | None = None):
    """Stacked x(t), y(t), z(t) time series."""
    t = df["times"].to_numpy()
    mask = np.ones_like(t, dtype=bool) if tmax_plot is None else (t <= tmax_plot)

    colors = ("#1b3a6b", "#a6171b", "#1f7a3d")
    labels = (r"$x(t)$", r"$y(t)$", r"$z(t)$")
    cols = ("x", "y", "z")

    fig, axes = plt.subplots(3, 1, figsize=(3.5, 3.6), sharex=True)
    for ax, col, color, label in zip(axes, cols, colors, labels):
        ax.plot(t[mask], df[col].to_numpy()[mask], color=color, linewidth=0.9)
        ax.set_ylabel(label)
        ax.margins(x=0.0)
        ax.minorticks_on()

    axes[-1].set_xlabel(r"$t$")
    fig.align_ylabels(axes)
    fig.tight_layout(h_pad=0.4)
    for ext in ("png", "pdf"):
        fig.savefig(out_stem.with_suffix(f".{ext}"))
    plt.close(fig)


# --------------------------------------------------------------------------
# Central-difference derivative-error study
# --------------------------------------------------------------------------
def central_difference_error(dt, tmax=TMAX, x0=X0):
    """RMS error of the 3-point central difference vs. the exact derivative.

    Samples the (high-accuracy) Lorenz solution on a uniform grid of spacing
    ``dt``, approximates dx/dt, dy/dt, dz/dt with the second-order central
    scheme ``(s[i+1] - s[i-1]) / (2*dt)`` on interior points, and compares to
    the analytic right-hand side. Returns one RMS value per component (x, y, z).
    """
    df = generate_lorenz(dt=dt, tmax=tmax, x0=x0)
    state = df[["x", "y", "z"]].to_numpy(dtype=np.float64)

    # Exact derivatives at the interior grid points.
    x, y, z = state[:, 0], state[:, 1], state[:, 2]
    exact = np.column_stack(
        [SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z]
    )[1:-1]

    # Second-order central difference on interior points.
    cd = (state[2:] - state[:-2]) / (2.0 * dt)

    err = cd - exact
    return np.sqrt(np.mean(err**2, axis=0))  # (rms_x, rms_y, rms_z)


def plot_derivative_error(out_stem: Path, dts=None):
    """Log-log plot of central-difference RMS error vs. dt for x, y, z."""
    if dts is None:
        dts = np.logspace(-3, -1, 9)  # 0.001 ... 0.1

    rms = np.array([central_difference_error(dt) for dt in dts])  # (n_dt, 3)

    colors = ("#1b3a6b", "#a6171b", "#1f7a3d")
    labels = (r"$dx/dt$", r"$dy/dt$", r"$dz/dt$")

    fig, ax = plt.subplots(figsize=(3.5, 2.9))
    for j, (color, label) in enumerate(zip(colors, labels)):
        ax.loglog(dts, rms[:, j], "o-", color=color, ms=3.5, lw=1.0, label=label)

    # Second-order reference guide line, anchored at the largest dt (total RMS).
    total_rms = np.sqrt(np.sum(rms**2, axis=1))
    ref = total_rms[-1] * (dts / dts[-1]) ** 2
    ax.loglog(dts, ref, "--", color="0.4", lw=0.9, label=r"$\mathcal{O}(\Delta t^{2})$")

    ax.set_xlabel(r"$\Delta t$")
    ax.set_ylabel(r"central-difference RMS error")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.4)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_stem.with_suffix(f".{ext}"))
    plt.close(fig)

    # Report the empirical convergence slope on the log-log axes.
    slope = np.polyfit(np.log(dts), np.log(total_rms), 1)[0]
    return slope


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def main():
    _set_publication_style()

    df = generate_lorenz()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_PATH, index=False)
    print(f"Wrote {len(df)} samples -> {PARQUET_PATH}")
    print(f"Columns: {list(df.columns)}")

    df_exact = add_exact_derivatives(df)
    df_exact.to_parquet(EXACT_DERIV_PARQUET_PATH, index=False)
    print(f"Wrote {len(df_exact)} samples -> {EXACT_DERIV_PARQUET_PATH}")
    print(f"Columns: {list(df_exact.columns)}")

    plot_attractor(df, OUTPUT_DIR / "lorenz_attractor")
    plot_timeseries(df, OUTPUT_DIR / "lorenz_timeseries")
    slope = plot_derivative_error(OUTPUT_DIR / "lorenz_cd_error_vs_dt")
    print(f"Central-difference error convergence slope ~ {slope:.2f} (expect ~2)")
    print(f"Saved figures (png + pdf) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
