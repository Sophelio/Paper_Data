"""Nature-ready Figure 4: task contracts and mathematical representations.

Panel a regenerates the 32 pendulum trajectories from the initial states in
``manifest.csv``.  It recomputes one compression fit per realization and
protected autonomous-prediction errors for the eight prespecified holdouts.
Panel b evaluates temporal, spatial and coupled relations on one analytic heat-
equation mode.  The temporal derivative is estimated with a second-order
finite difference; the spatial derivative is analytic.

Outputs are PNG, PDF and SVG on an exact 183 x 150 mm opaque-white canvas.  No
tight bounding box is used, so the physical dimensions do not depend on the
artists.  The dense signed field is rasterized inside the otherwise editable
vector PDF/SVG exports.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Final

if os.name == "nt":
    os.environ.setdefault("MIKTEX_UNATTENDED", "1")
    os.environ.setdefault("MIKTEX_AUTOINSTALL", "1")
    _miktex_bin = Path.home() / r"AppData\Local\Programs\MiKTeX\miktex\bin\x64"
    if _miktex_bin.is_dir():
        os.environ["PATH"] = str(_miktex_bin) + os.pathsep + os.environ.get("PATH", "")

import matplotlib as mpl

# Avoid display-dependent canvas rounding on macOS.
mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.patches import ConnectionPatch, FancyBboxPatch, Rectangle
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp


HERE: Final = Path(__file__).resolve().parent
MANIFEST: Final = HERE / "manifest.csv"
OUTPUT_DIR: Final = HERE / "figs"
STEM: Final = "figure4_task_contracts_mathematical_representations_nature"

WIDTH_MM: Final = 183.0
HEIGHT_MM: Final = 150.0
MM_PER_INCH: Final = 25.4

OMEGA0: Final = 1.35
A_COMP_REPORTED: Final = -3.64499998
A_PRED: Final = -1.82245149
B_PRED: Final = 1.0
COMP_REP: Final = (0, 4, 8, 12, 16, 20, 24, 28)
HOLDOUTS: Final = (3, 7, 11, 15, 19, 23, 27, 31)
HORIZONS: Final = np.array([0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0])
T_EVAL: Final = np.linspace(0.0, 30.0, 3001)

HEAT_MODE: Final = 2
KAPPA: Final = 0.03
HEAT_X: Final = np.linspace(0.0, 1.0, 500)
HEAT_T: Final = np.linspace(0.0, 1.7, 360)

INK: Final = "#202124"
GREEN: Final = "#007252"
BLUE: Final = "#005A91"
ORANGE: Final = "#A94700"
MID: Final = "#5F6368"
LIGHT: Final = "#A8ADB4"
RULE: Final = "#D9DDE2"
WHITE: Final = "#FFFFFF"
PALE_GREEN: Final = "#E7F3EE"
PALE_BLUE: Final = "#EAF2F8"
PALE_ORANGE: Final = "#F7ECE5"

STYLE: Final = {
    "figure.dpi": 150,
    "savefig.dpi": 600,
    "savefig.bbox": None,
    "savefig.pad_inches": 0.0,
    "savefig.facecolor": WHITE,
    "savefig.transparent": False,
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Arial",
        "Helvetica",
        "Nimbus Sans L",
        "Liberation Sans",
        "DejaVu Sans",
    ],
    "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "font.size": 6.6,
    "axes.labelsize": 7.0,
    "axes.titlesize": 7.6,
    "axes.titleweight": "semibold",
    "axes.labelcolor": INK,
    "axes.edgecolor": INK,
    "axes.linewidth": 0.65,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 6.3,
    "ytick.labelsize": 6.3,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.fontsize": 5.9,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
}


@dataclass(frozen=True)
class PendulumResults:
    manifest: pd.DataFrame
    truth: dict[int, np.ndarray]
    prediction: dict[int, np.ndarray]
    slopes: np.ndarray
    intercepts: np.ndarray
    median_slope: float
    max_intercept_error: float
    theta_rmse: np.ndarray
    omega_rmse: np.ndarray


@dataclass(frozen=True)
class HeatResults:
    x: np.ndarray
    t: np.ndarray
    field: np.ndarray
    alpha: float
    temporal_residual: float
    spatial_residual: float
    coupled_residual: float


def require(condition: bool, message: str) -> None:
    """Raise a clear error when a scientific or export contract is violated."""
    if not condition:
        raise RuntimeError(message)


def load_manifest(path: Path) -> pd.DataFrame:
    """Load and validate the 32-realization initial-state contract."""
    require(path.is_file(), f"Manifest not found: {path}")
    frame = pd.read_csv(path)
    required = {
        "realization_id",
        "theta0",
        "omega_init",
        "omega0",
        "omega0_squared",
        "energy_initial",
        "sample_count",
        "t_start",
        "t_end",
        "dt",
    }
    require(required.issubset(frame.columns), "Manifest is missing required columns.")
    require(len(frame) == 32, "Manifest must contain exactly 32 realizations.")
    ids = frame["realization_id"].astype(int).to_numpy()
    require(np.array_equal(np.sort(ids), np.arange(32)), "Realization IDs must be 0--31.")
    require(frame["realization_id"].is_unique, "Realization IDs must be unique.")
    require(np.allclose(frame["omega0"], OMEGA0, rtol=0.0, atol=1e-14), "Unexpected omega0.")
    require(
        np.allclose(frame["omega0_squared"], OMEGA0**2, rtol=0.0, atol=1e-14),
        "Unexpected omega0_squared.",
    )
    require(np.all(frame["sample_count"].to_numpy(int) == T_EVAL.size), "Unexpected sample count.")
    require(np.allclose(frame["t_start"], 0.0), "Unexpected trajectory start time.")
    require(np.allclose(frame["t_end"], 30.0), "Unexpected trajectory end time.")
    require(np.allclose(frame["dt"], 0.01), "Unexpected trajectory time step.")
    require(np.isfinite(frame[list(required - {"realization_id"})].to_numpy(float)).all(), "Non-finite manifest values.")
    return frame.assign(realization_id=ids).sort_values("realization_id").reset_index(drop=True)


def truth_rhs(_time: float, state: np.ndarray) -> tuple[float, float]:
    return float(state[1]), float(-(OMEGA0**2) * np.sin(state[0]))


def prediction_rhs(_time: float, state: np.ndarray) -> tuple[float, float]:
    return float(B_PRED * state[1]), float(A_PRED * np.sin(state[0]))


def integrate(initial_state: tuple[float, float], rhs) -> np.ndarray:
    solution = solve_ivp(
        rhs,
        (0.0, 30.0),
        initial_state,
        t_eval=T_EVAL,
        method="DOP853",
        rtol=1e-12,
        atol=1e-14,
    )
    require(solution.success, f"Pendulum integration failed: {solution.message}")
    require(solution.y.shape == (2, T_EVAL.size), "Unexpected integration output shape.")
    return solution.y


def compute_pendulum(frame: pd.DataFrame) -> PendulumResults:
    """Regenerate trajectories, refit compression, and score holdouts."""
    require(abs(A_COMP_REPORTED + 2.0 * OMEGA0**2) < 2.1e-8, "Compression coefficient checkpoint failed.")
    require(abs(A_PRED + OMEGA0**2) < 4.9e-5, "Prediction coefficient checkpoint failed.")

    truth: dict[int, np.ndarray] = {}
    for row in frame.itertuples(index=False):
        rid = int(row.realization_id)
        truth[rid] = integrate((float(row.theta0), float(row.omega_init)), truth_rhs)

    slopes = np.empty(len(frame), dtype=float)
    intercepts = np.empty(len(frame), dtype=float)
    energies = frame.set_index("realization_id")["energy_initial"]
    for rid in range(32):
        theta, omega = truth[rid]
        coordinate = 1.0 - np.cos(theta)
        design = np.column_stack((coordinate, np.ones_like(coordinate)))
        slopes[rid], intercepts[rid] = np.linalg.lstsq(design, omega**2, rcond=None)[0]

    expected_intercepts = 2.0 * energies.loc[np.arange(32)].to_numpy(float)
    median_slope = float(np.median(slopes))
    max_intercept_error = float(np.max(np.abs(intercepts - expected_intercepts)))
    require(abs(median_slope + 2.0 * OMEGA0**2) < 5e-10, "Refitted compression slope checkpoint failed.")
    require(max_intercept_error < 1e-9, "Compression intercept checkpoint failed.")

    prediction: dict[int, np.ndarray] = {}
    for rid in HOLDOUTS:
        row = frame.loc[frame["realization_id"] == rid].iloc[0]
        prediction[rid] = integrate((float(row.theta0), float(row.omega_init)), prediction_rhs)

    theta_rmse: list[float] = []
    omega_rmse: list[float] = []
    for horizon in HORIZONS:
        mask = T_EVAL <= horizon + 1e-12
        theta_error = np.concatenate(
            [prediction[rid][0, mask] - truth[rid][0, mask] for rid in HOLDOUTS]
        )
        omega_error = np.concatenate(
            [prediction[rid][1, mask] - truth[rid][1, mask] for rid in HOLDOUTS]
        )
        theta_rmse.append(float(np.sqrt(np.mean(theta_error**2))))
        omega_rmse.append(float(np.sqrt(np.mean(omega_error**2))))

    theta_values = np.asarray(theta_rmse)
    omega_values = np.asarray(omega_rmse)
    require(np.isclose(theta_values[-1], 3.28e-4, rtol=0.006), "30-s theta RMSE checkpoint failed.")
    require(np.isclose(omega_values[-1], 3.38e-4, rtol=0.006), "30-s omega RMSE checkpoint failed.")

    return PendulumResults(
        manifest=frame,
        truth=truth,
        prediction=prediction,
        slopes=slopes,
        intercepts=intercepts,
        median_slope=median_slope,
        max_intercept_error=max_intercept_error,
        theta_rmse=theta_values,
        omega_rmse=omega_values,
    )


def compute_heat() -> HeatResults:
    """Evaluate three relations on one analytic heat-equation realization."""
    x_grid, t_grid = np.meshgrid(HEAT_X, HEAT_T)
    angular_wavenumber = HEAT_MODE * np.pi
    alpha = angular_wavenumber**2 * KAPPA
    field = np.exp(-alpha * t_grid) * np.sin(angular_wavenumber * x_grid)

    # This finite-difference choice is part of the figure's residual provenance.
    u_t = np.gradient(field, HEAT_T, axis=0, edge_order=2)
    u_xx = -(angular_wavenumber**2) * field
    temporal_residual = float(np.max(np.abs(u_t + alpha * field)))
    spatial_residual = float(np.max(np.abs(u_xx + angular_wavenumber**2 * field)))
    coupled_residual = float(np.max(np.abs(u_t - KAPPA * u_xx)))

    require(temporal_residual < 1e-4, "Temporal residual exceeds the displayed threshold.")
    require(spatial_residual < 1e-12, "Spatial residual exceeds the displayed threshold.")
    require(coupled_residual < 1e-4, "Coupled residual exceeds the displayed threshold.")
    return HeatResults(
        x=HEAT_X,
        t=HEAT_T,
        field=field,
        alpha=float(alpha),
        temporal_residual=temporal_residual,
        spatial_residual=spatial_residual,
        coupled_residual=coupled_residual,
    )


def style_axis(ax: plt.Axes, *, grid: bool = True) -> None:
    ax.spines[["left", "bottom"]].set_color(LIGHT)
    if grid:
        ax.grid(True, which="major", color=RULE, lw=0.45, alpha=0.72)
        ax.set_axisbelow(True)


def add_panel_header(fig: plt.Figure, slot, label: str, title: str, subtitle: str) -> None:
    bounds = slot.get_position(fig)
    title_y = bounds.y1 + 0.064
    subtitle_y = bounds.y1 + 0.029
    fig.text(
        bounds.x0 - 0.035,
        title_y,
        label,
        ha="left",
        va="baseline",
        fontsize=8.4,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        bounds.x0,
        title_y,
        title,
        ha="left",
        va="baseline",
        fontsize=8.0,
        fontweight="semibold",
        color=INK,
    )
    fig.text(
        bounds.x0,
        subtitle_y,
        subtitle,
        ha="left",
        va="baseline",
        fontsize=5.65,
        color=MID,
    )


def add_contract_header(
    ax: plt.Axes,
    title: str,
    subtitle: str,
    equation: str,
    color: str,
    background: str,
) -> None:
    ax.set_axis_off()
    ax.text(0.0, 0.88, title, ha="left", va="top", fontsize=7.5, fontweight="semibold", color=color)
    ax.text(0.0, 0.57, subtitle, ha="left", va="top", fontsize=5.55, color=MID)
    ax.text(
        0.0,
        0.04,
        equation,
        ha="left",
        va="bottom",
        fontsize=7.25,
        color=INK,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": background, "edgecolor": color, "linewidth": 0.55},
    )


def draw_panel_a(fig: plt.Figure, slot, result: PendulumResults) -> None:
    panel = slot.subgridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.25)
    compression = panel[0].subgridspec(2, 1, height_ratios=[0.27, 0.73], hspace=0.08)
    prediction = panel[1].subgridspec(2, 1, height_ratios=[0.27, 0.73], hspace=0.08)

    compression_header = fig.add_subplot(compression[0])
    prediction_header = fig.add_subplot(prediction[0])
    add_contract_header(
        compression_header,
        "Compression",
        "Shared invariant + one scalar per realization",
        r"$\omega^2=-3.645(1-\cos\theta)+2E_i$",
        GREEN,
        PALE_GREEN,
    )
    add_contract_header(
        prediction_header,
        "Prediction",
        "Frozen law + eight protected holdouts",
        r"$\dot{\theta}=\omega,\quad \dot{\omega}=-1.82245149\sin\theta$",
        BLUE,
        PALE_BLUE,
    )

    compression_plot = compression[1].subgridspec(1, 2, width_ratios=[1.0, 0.045], wspace=0.10)
    ax_comp = fig.add_subplot(compression_plot[0])
    cax = fig.add_subplot(compression_plot[1])
    ax_pred = fig.add_subplot(prediction[1])

    energy = result.manifest.set_index("realization_id")["energy_initial"]
    representative_energy = energy.loc[list(COMP_REP)].to_numpy(float)
    norm = Normalize(vmin=float(representative_energy.min()), vmax=float(representative_energy.max()))
    green_map = LinearSegmentedColormap.from_list(
        "energy_green", ["#DDEFE8", "#80B9A5", GREEN], N=256
    )
    for rid in COMP_REP:
        theta, omega = result.truth[rid]
        ax_comp.plot(
            1.0 - np.cos(theta),
            omega**2,
            color=green_map(norm(float(energy.loc[rid]))),
            lw=1.05,
            alpha=0.96,
        )
    ax_comp.set(xlabel=r"$1-\cos\theta$", ylabel=r"$\omega^2$", xlim=(0.0, None), ylim=(0.0, None))
    ax_comp.text(
        0.02,
        0.98,
        "8 representative trajectories · 32 fits",
        transform=ax_comp.transAxes,
        ha="left",
        va="top",
        fontsize=5.25,
        color=MID,
    )
    ax_comp.text(
        0.98,
        0.04,
        rf"median $A_i={result.median_slope:.4f}$" + "\n" + rf"max $|B_i-2E_i|={result.max_intercept_error:.1e}$",
        transform=ax_comp.transAxes,
        ha="right",
        va="bottom",
        fontsize=5.3,
        color=INK,
        linespacing=1.22,
        bbox={"boxstyle": "round,pad=0.24", "facecolor": WHITE, "edgecolor": GREEN, "linewidth": 0.5, "alpha": 0.94},
    )
    style_axis(ax_comp)

    scalar_map = mpl.cm.ScalarMappable(norm=norm, cmap=green_map)
    scalar_map.set_array([])
    colorbar = fig.colorbar(scalar_map, cax=cax)
    colorbar.set_label(r"Initial energy $E_i$", fontsize=5.45, color=INK, labelpad=2)
    colorbar.ax.tick_params(labelsize=5.2, colors=MID, length=1.8, width=0.5)
    colorbar.outline.set_edgecolor(LIGHT)
    colorbar.outline.set_linewidth(0.5)

    ax_pred.plot(
        HORIZONS,
        result.theta_rmse,
        color=BLUE,
        marker="o",
        markersize=3.0,
        markeredgewidth=0.0,
        lw=1.25,
        label=r"$\theta$ (rad)",
    )
    ax_pred.plot(
        HORIZONS,
        result.omega_rmse,
        color=ORANGE,
        marker="s",
        markersize=2.8,
        markeredgewidth=0.0,
        lw=1.2,
        ls="--",
        dashes=(3.0, 1.6),
        label=r"$\omega$ (rad s$^{-1}$)",
    )
    ax_pred.set_yscale("log")
    ax_pred.set(
        xlabel="Forecast horizon (s)",
        ylabel="Pooled RMSE",
        xlim=(0.0, 31.0),
        ylim=(1e-6, 1.2e-3),
        xticks=[0, 5, 10, 20, 30],
    )
    ax_pred.text(
        0.02,
        0.98,
        "Initial state supplied only at $t=0$",
        transform=ax_pred.transAxes,
        ha="left",
        va="top",
        fontsize=5.25,
        color=MID,
    )
    ax_pred.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.86), ncol=1, handlelength=1.7)
    ax_pred.annotate(
        rf"30 s: $\mathrm{{RMSE}}_\theta={result.theta_rmse[-1]:.2e}$" + "\n" + rf"$\mathrm{{RMSE}}_\omega={result.omega_rmse[-1]:.2e}$",
        xy=(30.0, result.theta_rmse[-1]),
        xycoords="data",
        xytext=(0.97, 0.06),
        textcoords="axes fraction",
        ha="right",
        va="bottom",
        fontsize=5.25,
        color=INK,
        linespacing=1.18,
        bbox={"boxstyle": "round,pad=0.23", "facecolor": WHITE, "edgecolor": BLUE, "linewidth": 0.5, "alpha": 0.94},
        arrowprops={"arrowstyle": "-", "color": BLUE, "linewidth": 0.55, "shrinkA": 3.0, "shrinkB": 3.0},
    )
    style_axis(ax_pred)


def add_representation_card(
    ax: plt.Axes,
    y0: float,
    title: str,
    equation: str,
    parameter_text: str,
    residual: float,
) -> float:
    height = 0.285
    card = FancyBboxPatch(
        (0.035, y0),
        0.95,
        height,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        transform=ax.transAxes,
        facecolor=WHITE,
        edgecolor=RULE,
        linewidth=0.65,
        clip_on=False,
    )
    ax.add_patch(card)
    ax.add_patch(
        Rectangle(
            (0.035, y0),
            0.018,
            height,
            transform=ax.transAxes,
            facecolor=ORANGE,
            edgecolor="none",
            clip_on=False,
        )
    )
    ax.text(0.078, y0 + 0.224, title, transform=ax.transAxes, ha="left", va="center", fontsize=6.35, fontweight="semibold", color=INK)
    ax.text(0.078, y0 + 0.132, equation, transform=ax.transAxes, ha="left", va="center", fontsize=8.1, color=ORANGE)
    ax.text(0.58, y0 + 0.135, parameter_text, transform=ax.transAxes, ha="left", va="center", fontsize=5.35, color=MID)
    ax.text(0.078, y0 + 0.047, rf"max $|R|={residual:.1e}$", transform=ax.transAxes, ha="left", va="center", fontsize=5.2, color=MID)
    return y0 + height / 2.0


def draw_panel_b(fig: plt.Figure, slot, result: HeatResults) -> None:
    panel = slot.subgridspec(1, 2, width_ratios=[1.18, 1.0], wspace=0.26)
    field_slot = panel[0].subgridspec(2, 1, height_ratios=[0.88, 0.12], hspace=0.20)
    ax_field = fig.add_subplot(field_slot[0])
    cax = fig.add_subplot(field_slot[1])
    ax_cards = fig.add_subplot(panel[1])
    ax_cards.set_axis_off()

    # An odd LUT size places pure white exactly at the signed midpoint.
    signed_map = LinearSegmentedColormap.from_list(
        "signed_blue_white_orange",
        [(0.0, BLUE), (0.38, "#9FC6DB"), (0.5, WHITE), (0.62, "#E8B99D"), (1.0, ORANGE)],
        N=1025,
    )
    # The analytic mode has unit amplitude; using exact symmetric limits keeps
    # the ±1 colorbar endpoints inside the normalization despite grid sampling.
    amplitude = 1.0
    image = ax_field.imshow(
        result.field,
        extent=(result.x[0], result.x[-1], result.t[0], result.t[-1]),
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        cmap=signed_map,
        norm=TwoSlopeNorm(vmin=-amplitude, vcenter=0.0, vmax=amplitude),
        rasterized=True,
    )
    ax_field.set(xlabel="$x$", ylabel="$t$", title=r"Observed field $u(x,t)$")
    ax_field.title.set_fontsize(6.7)
    ax_field.title.set_fontweight("semibold")
    ax_field.title.set_color(INK)
    ax_field.tick_params(length=2.2)
    ax_field.spines[["top", "right"]].set_visible(True)
    ax_field.spines[:].set_color(LIGHT)

    colorbar = fig.colorbar(image, cax=cax, orientation="horizontal")
    colorbar.set_ticks([-1.0, 0.0, 1.0])
    colorbar.set_label(r"Field amplitude $u(x,t)$", fontsize=5.45, color=INK, labelpad=1.5)
    colorbar.ax.tick_params(labelsize=5.1, colors=MID, length=1.8, width=0.5, pad=1.0)
    colorbar.outline.set_edgecolor(LIGHT)
    colorbar.outline.set_linewidth(0.5)

    centers = [
        add_representation_card(
            ax_cards,
            0.690,
            "Temporal representation",
            r"$u_t+\alpha u=0$",
            rf"$\alpha={result.alpha:.5f}$",
            result.temporal_residual,
        ),
        add_representation_card(
            ax_cards,
            0.375,
            "Spatial representation",
            r"$u_{{xx}}+(m\pi)^2u=0$",
            rf"$m={HEAT_MODE}$",
            result.spatial_residual,
        ),
        add_representation_card(
            ax_cards,
            0.060,
            "Coupled diffusion representation",
            r"$u_t-\kappa u_{{xx}}=0$",
            rf"$\kappa={KAPPA:.2f}$",
            result.coupled_residual,
        ),
    ]
    for field_y, card_y in zip((0.82, 0.52, 0.22), centers):
        connector = ConnectionPatch(
            xyA=(1.02, field_y),
            coordsA=ax_field.transAxes,
            xyB=(0.035, card_y),
            coordsB=ax_cards.transAxes,
            arrowstyle="-",
            color=RULE,
            linewidth=0.7,
            zorder=0,
            clip_on=False,
        )
        fig.add_artist(connector)
    ax_cards.text(
        0.51,
        0.004,
        r"All displayed relations: $\|R\|_\infty<10^{-4}$",
        transform=ax_cards.transAxes,
        ha="center",
        va="bottom",
        fontsize=5.45,
        fontweight="semibold",
        color=ORANGE,
    )


def build_figure(pendulum: PendulumResults, heat: HeatResults) -> plt.Figure:
    fig = plt.figure(
        figsize=(WIDTH_MM / MM_PER_INCH, HEIGHT_MM / MM_PER_INCH),
        facecolor=WHITE,
    )
    outer = fig.add_gridspec(
        2,
        1,
        left=0.075,
        right=0.955,
        top=0.854,
        bottom=0.078,
        hspace=0.54,
    )
    draw_panel_a(fig, outer[0], pendulum)
    draw_panel_b(fig, outer[1], heat)
    add_panel_header(
        fig,
        outer[0],
        "a",
        "Task contracts select different representations of the same trajectories",
        "32-realization pendulum ensemble · compression invariant and protected autonomous prediction",
    )
    add_panel_header(
        fig,
        outer[1],
        "b",
        "One field realization supports multiple mathematical representations",
        "Temporal, spatial and coupled relations are observationally equivalent on a single mode",
    )
    return fig


def export_figure(fig: plt.Figure) -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for extension in ("png", "pdf", "svg"):
        path = (OUTPUT_DIR / STEM).with_suffix(f".{extension}")
        fig.savefig(
            path,
            dpi=600,
            bbox_inches=None,
            pad_inches=0,
            facecolor=WHITE,
            transparent=False,
        )
        paths.append(path)
    return paths


def main() -> None:
    manifest = load_manifest(MANIFEST)
    pendulum = compute_pendulum(manifest)
    heat = compute_heat()
    with mpl.rc_context(STYLE):
        figure = build_figure(pendulum, heat)
        paths = export_figure(figure)
        plt.close(figure)

    print(f"median_compression_slope={pendulum.median_slope:.10f}")
    print(f"max_compression_intercept_error={pendulum.max_intercept_error:.6e}")
    print(f"theta_rmse_30s={pendulum.theta_rmse[-1]:.8e}")
    print(f"omega_rmse_30s={pendulum.omega_rmse[-1]:.8e}")
    print(f"heat_alpha={heat.alpha:.10f}")
    print(f"heat_temporal_residual={heat.temporal_residual:.6e}")
    print(f"heat_spatial_residual={heat.spatial_residual:.6e}")
    print(f"heat_coupled_residual={heat.coupled_residual:.6e}")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
