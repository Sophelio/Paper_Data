"""Compact one-row variant of manuscript Figure 4.

The top-level panels are arranged side by side on an exact 183 x 92 mm canvas.
Scientific computations and validation checkpoints are imported from
``figure4_task_contracts_mathematical_representations_nature.py`` so this
layout-only variant cannot drift from the validated 32-realization pendulum and
single-mode heat-field analyses.

The original 183 x 150 mm two-row script and exports remain unchanged.  This
script writes distinct ``*_one_row`` PNG, PDF and SVG files with an opaque white
background and no tight bounding box.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

import figure4_task_contracts_mathematical_representations_nature as source


HERE: Final = Path(__file__).resolve().parent
OUTPUT_DIR: Final = HERE / "figs"
STEM: Final = "figure4_task_contracts_mathematical_representations_nature_one_row"
WIDTH_MM: Final = 183.0
HEIGHT_MM: Final = 92.0
MM_PER_INCH: Final = 25.4

INK: Final = source.INK
GREEN: Final = source.GREEN
BLUE: Final = source.BLUE
ORANGE: Final = source.ORANGE
MID: Final = source.MID
LIGHT: Final = source.LIGHT
RULE: Final = source.RULE
WHITE: Final = source.WHITE
PALE_GREEN: Final = source.PALE_GREEN
PALE_BLUE: Final = source.PALE_BLUE

# Pin the 10 pt Latin Modern design at every size (STYLE_SPEC 7A); copied
# verbatim from the Figure 6 script.
LM_DESIGN_SIZE_PIN = (
    r"\DeclareFontFamily{T1}{lmr}{}"
    r"\DeclareFontShape{T1}{lmr}{m}{n}{<-> ec-lmr10}{}"
    r"\DeclareFontShape{T1}{lmr}{m}{it}{<-> ec-lmri10}{}"
    r"\DeclareFontShape{T1}{lmr}{bx}{n}{<-> ec-lmbx10}{}"
    r"\DeclareFontShape{T1}{lmr}{bx}{it}{<-> ec-lmbxi10}{}"
    r"\DeclareFontShape{T1}{lmr}{b}{n}{<->ssub * lmr/bx/n}{}"
    r"\DeclareFontFamily{OT1}{lmr}{}"
    r"\DeclareFontShape{OT1}{lmr}{m}{n}{<-> rm-lmr10}{}"
    r"\DeclareFontShape{OT1}{lmr}{m}{it}{<-> rm-lmri10}{}"
    r"\DeclareFontShape{OT1}{lmr}{bx}{n}{<-> rm-lmbx10}{}"
    r"\DeclareFontShape{OT1}{lmr}{b}{n}{<->ssub * lmr/bx/n}{}"
    r"\DeclareFontFamily{OML}{lmm}{\skewchar\font127 }"
    r"\DeclareFontShape{OML}{lmm}{m}{it}{<-> lmmi10}{}"
    r"\DeclareFontShape{OML}{lmm}{b}{it}{<-> lmmib10}{}"
    r"\DeclareFontShape{OML}{lmm}{bx}{it}{<->ssub * lmm/b/it}{}"
    r"\DeclareFontFamily{OMS}{lmsy}{\skewchar\font48 }"
    r"\DeclareFontShape{OMS}{lmsy}{m}{n}{<-> lmsy10}{}"
    r"\DeclareFontShape{OMS}{lmsy}{b}{n}{<-> lmbsy10}{}"
)

STYLE: Final = dict(source.STYLE)
for _dead_key in ("font.sans-serif", "mathtext.fontset", "axes.titleweight"):
    STYLE.pop(_dead_key, None)
STYLE.update(
    {
        # Latin Modern through LaTeX, matching the manuscript typography.
        "text.usetex": True,
        "font.family": "serif",
        "text.latex.preamble": (
            r"\usepackage[T1]{fontenc}"
            r"\usepackage{lmodern}"
            r"\usepackage{amsmath,amssymb}"
            + LM_DESIGN_SIZE_PIN
        ),
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
        "font.size": 5.9,
        "axes.labelsize": 6.25,
        "axes.titlesize": 6.5,
        "xtick.labelsize": 5.55,
        "ytick.labelsize": 5.55,
        "legend.fontsize": 4.8,
    }
)


def sci_tex(value: float, digits: int) -> str:
    """Format a number as LaTeX scientific notation (no 'e' notation)."""
    if value == 0.0:
        return "0"
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times 10^{{{int(exponent)}}}"


# Header baselines (figure fraction above the panel slot). In Latin Modern bold,
# panel b's title overruns the canvas on one line, so it wraps to two lines; every
# panel letter and first title line sits one title line higher so the letters stay
# aligned across the row.
HEADER_FIRST_BASELINE: Final = 0.138
HEADER_LINE_STEP: Final = 0.030


def add_panel_header(
    fig: plt.Figure,
    slot,
    label: str,
    title: str | tuple[str, ...],
    subtitle: str,
    title_fontsize: float = 7.35,
) -> None:
    """Align panel labels and headers above both side-by-side cells."""
    bounds = slot.get_position(fig)
    title_lines = (title,) if isinstance(title, str) else title
    fig.text(
        bounds.x0 - 0.030,
        bounds.y1 + HEADER_FIRST_BASELINE,
        rf"\textbf{{{label}}}",
        ha="left",
        va="baseline",
        fontsize=8.2,
        color=INK,
    )
    for index, line in enumerate(title_lines):
        fig.text(
            bounds.x0,
            bounds.y1 + HEADER_FIRST_BASELINE - index * HEADER_LINE_STEP,
            rf"\textbf{{{line}}}",
            ha="left",
            va="baseline",
            fontsize=title_fontsize,
            color=INK,
        )
    fig.text(
        bounds.x0,
        bounds.y1 + 0.056,
        subtitle,
        ha="left",
        va="baseline",
        fontsize=5.4,
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
    ax.text(
        0.0,
        1.10,
        rf"\textbf{{{title}}}",
        ha="left",
        va="top",
        fontsize=7.0,
        color=color,
    )
    ax.text(
        0.0,
        0.78,
        subtitle,
        ha="left",
        va="top",
        fontsize=5.35,
        color=MID,
    )
    ax.text(
        0.0,
        0.13,
        equation,
        ha="left",
        va="bottom",
        fontsize=6.05,
        color=INK,
        bbox={
            "boxstyle": "round,pad=0.23",
            "facecolor": background,
            "edgecolor": color,
            "linewidth": 0.52,
        },
    )


def draw_panel_a(
    fig: plt.Figure,
    slot,
    result: source.PendulumResults,
) -> None:
    panel = slot.subgridspec(1, 2, width_ratios=[1.04, 1.0], wspace=0.30)
    compression = panel[0].subgridspec(2, 1, height_ratios=[0.22, 0.78], hspace=0.04)
    prediction = panel[1].subgridspec(2, 1, height_ratios=[0.22, 0.78], hspace=0.04)

    compression_header = fig.add_subplot(compression[0])
    prediction_header = fig.add_subplot(prediction[0])
    add_contract_header(
        compression_header,
        "Compression",
        r"Shared invariant $+$ one scalar per realization",
        r"$\omega^2=-3.645(1-\cos\theta)+2E_i$",
        GREEN,
        PALE_GREEN,
    )
    add_contract_header(
        prediction_header,
        "Prediction",
        r"Frozen law $+$ eight protected holdouts",
        r"$\dot{\theta}=\omega,\quad \dot{\omega}=-1.82245149\sin\theta$",
        BLUE,
        PALE_BLUE,
    )

    compression_plot = compression[1].subgridspec(
        1,
        2,
        width_ratios=[1.0, 0.047],
        wspace=0.26,
    )
    ax_comp = fig.add_subplot(compression_plot[0])
    cax = fig.add_subplot(compression_plot[1])
    ax_pred = fig.add_subplot(prediction[1])

    energy = result.manifest.set_index("realization_id")["energy_initial"]
    representative_energy = energy.loc[list(source.COMP_REP)].to_numpy(float)
    norm = Normalize(
        vmin=float(representative_energy.min()),
        vmax=float(representative_energy.max()),
    )
    green_map = LinearSegmentedColormap.from_list(
        "energy_green_one_row",
        ["#DDEFE8", "#80B9A5", GREEN],
        N=256,
    )
    for realization_id in source.COMP_REP:
        theta, omega = result.truth[realization_id]
        ax_comp.plot(
            1.0 - np.cos(theta),
            omega**2,
            color=green_map(norm(float(energy.loc[realization_id]))),
            lw=0.9,
            alpha=0.96,
        )
    ax_comp.set(
        xlabel=r"$1-\cos\theta$",
        ylabel=r"$\omega^2$",
        xlim=(0.0, 1.88),
        ylim=(0.0, 6.85),
    )
    ax_comp.text(
        0.02,
        0.98,
        r"8 trajectories shown $\cdot$ 32 fits",
        transform=ax_comp.transAxes,
        ha="left",
        va="top",
        fontsize=4.8,
        color=MID,
    )
    ax_comp.text(
        0.98,
        0.045,
        rf"median $A_i={result.median_slope:.4f}$"
        + "\n"
        + rf"max $|B_i-2E_i|={sci_tex(result.max_intercept_error, 1)}$",
        transform=ax_comp.transAxes,
        ha="right",
        va="bottom",
        fontsize=4.35,
        color=INK,
        linespacing=1.18,
        bbox={
            "boxstyle": "round,pad=0.20",
            "facecolor": WHITE,
            "edgecolor": GREEN,
            "linewidth": 0.45,
            "alpha": 0.94,
        },
    )
    source.style_axis(ax_comp)

    scalar_map = mpl.cm.ScalarMappable(norm=norm, cmap=green_map)
    scalar_map.set_array([])
    colorbar = fig.colorbar(scalar_map, cax=cax)
    colorbar.set_label("")
    colorbar.ax.set_title(r"$E_i$", fontsize=4.8, color=INK, pad=1.5)
    colorbar.ax.yaxis.set_ticks_position("left")
    colorbar.ax.tick_params(
        labelsize=4.7,
        colors=MID,
        length=1.5,
        width=0.45,
        pad=0.8,
    )
    colorbar.outline.set_edgecolor(LIGHT)
    colorbar.outline.set_linewidth(0.45)

    ax_pred.plot(
        source.HORIZONS,
        result.theta_rmse,
        color=BLUE,
        marker="o",
        markersize=2.5,
        markeredgewidth=0.0,
        lw=1.05,
        label=r"$\theta$ (rad)",
    )
    ax_pred.plot(
        source.HORIZONS,
        result.omega_rmse,
        color=ORANGE,
        marker="s",
        markersize=2.35,
        markeredgewidth=0.0,
        lw=1.0,
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
    ax_pred.yaxis.labelpad = 1.0
    ax_pred.text(
        0.02,
        0.98,
        "Initial state supplied only at $t=0$",
        transform=ax_pred.transAxes,
        ha="left",
        va="top",
        fontsize=4.7,
        color=MID,
    )
    ax_pred.legend(
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.0, 0.87),
        handlelength=1.45,
        labelspacing=0.28,
    )
    ax_pred.text(
        0.97,
        0.055,
        rf"30 s: $\mathrm{{RMSE}}_\theta={sci_tex(result.theta_rmse[-1], 2)}$"
        + "\n"
        + rf"$\mathrm{{RMSE}}_\omega={sci_tex(result.omega_rmse[-1], 2)}$",
        transform=ax_pred.transAxes,
        ha="right",
        va="bottom",
        fontsize=4.25,
        color=INK,
        linespacing=1.15,
        bbox={
            "boxstyle": "round,pad=0.20",
            "facecolor": WHITE,
            "edgecolor": BLUE,
            "linewidth": 0.45,
            "alpha": 0.94,
        },
    )
    source.style_axis(ax_pred)


def add_relation_strip(
    ax: plt.Axes,
    y0: float,
    title: str,
    equation: str,
    parameter: str,
) -> None:
    height = 0.245
    strip = FancyBboxPatch(
        (0.015, y0),
        0.97,
        height,
        boxstyle="round,pad=0.006,rounding_size=0.018",
        transform=ax.transAxes,
        facecolor=WHITE,
        edgecolor=RULE,
        linewidth=0.58,
        clip_on=False,
    )
    ax.add_patch(strip)
    ax.add_patch(
        Rectangle(
            (0.015, y0),
            0.018,
            height,
            transform=ax.transAxes,
            facecolor=ORANGE,
            edgecolor="none",
            clip_on=False,
        )
    )
    ax.text(
        0.055,
        y0 + 0.177,
        rf"\textbf{{{title}}}",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=4.65,
        color=INK,
    )
    ax.text(
        0.055,
        y0 + 0.068,
        equation,
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=6.15,
        color=ORANGE,
    )
    ax.text(
        0.97,
        y0 + 0.068,
        parameter,
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=5.5,
        color=INK,
    )


def draw_panel_b(
    fig: plt.Figure,
    slot,
    result: source.HeatResults,
) -> None:
    panel = slot.subgridspec(2, 1, height_ratios=[0.49, 0.51], hspace=0.22)
    field_slot = panel[0].subgridspec(
        1,
        3,
        width_ratios=[1.0, 0.028, 0.025],
        wspace=0.10,
    )
    ax_field = fig.add_subplot(field_slot[0])
    cax = fig.add_subplot(field_slot[1])
    ax_relations = fig.add_subplot(panel[1])
    ax_relations.set_axis_off()

    signed_map = LinearSegmentedColormap.from_list(
        "signed_blue_white_orange_one_row",
        [
            (0.0, BLUE),
            (0.38, "#9FC6DB"),
            (0.5, WHITE),
            (0.62, "#E8B99D"),
            (1.0, ORANGE),
        ],
        N=1025,
    )
    image = ax_field.imshow(
        result.field,
        extent=(result.x[0], result.x[-1], result.t[0], result.t[-1]),
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        cmap=signed_map,
        norm=TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0),
        rasterized=True,
    )
    ax_field.set(xlabel="$x$", ylabel="$t$", title=r"\textbf{Observed field} $u(x,t)$")
    ax_field.title.set_fontsize(5.9)
    ax_field.title.set_color(INK)
    ax_field.tick_params(length=2.0)
    ax_field.spines[["top", "right"]].set_visible(True)
    ax_field.spines[:].set_color(LIGHT)

    colorbar = fig.colorbar(image, cax=cax, orientation="vertical")
    colorbar.set_ticks([-1.0, 0.0, 1.0])
    colorbar.set_label(
        r"Field amplitude $u(x,t)$",
        fontsize=4.55,
        color=INK,
        labelpad=1.0,
        rotation=270,
        va="bottom",
    )
    colorbar.ax.tick_params(
        labelsize=4.65,
        colors=MID,
        length=1.4,
        width=0.45,
        pad=0.8,
    )
    colorbar.outline.set_edgecolor(LIGHT)
    colorbar.outline.set_linewidth(0.45)

    add_relation_strip(
        ax_relations,
        0.690,
        "Temporal representation",
        r"$u_t+\alpha u=0$",
        rf"$\alpha={result.alpha:.5f}$",
    )
    add_relation_strip(
        ax_relations,
        0.405,
        "Spatial representation",
        r"$u_{xx}+(m\pi)^2u=0$",
        rf"$m={source.HEAT_MODE}$",
    )
    add_relation_strip(
        ax_relations,
        0.120,
        "Coupled diffusion representation",
        r"$u_t-\kappa u_{xx}=0$",
        rf"$\kappa={source.KAPPA:.2f}$",
    )
    ax_relations.text(
        0.50,
        0.015,
        r"\textbf{All displayed relations:} $\|R\|_\infty<10^{-4}$",
        transform=ax_relations.transAxes,
        ha="center",
        va="bottom",
        fontsize=4.5,
        color=ORANGE,
    )


def build_figure(
    pendulum: source.PendulumResults,
    heat: source.HeatResults,
) -> plt.Figure:
    fig = plt.figure(
        figsize=(WIDTH_MM / MM_PER_INCH, HEIGHT_MM / MM_PER_INCH),
        facecolor=WHITE,
    )
    outer = fig.add_gridspec(
        1,
        2,
        width_ratios=[1.58, 1.0],
        left=0.055,
        right=0.975,
        top=0.805,
        bottom=0.105,
        wspace=0.17,
    )
    draw_panel_a(fig, outer[0], pendulum)
    draw_panel_b(fig, outer[1], heat)
    add_panel_header(
        fig,
        outer[0],
        "a",
        "Task contracts select trajectory representations",
        r"32 realizations $\cdot$ compression invariant and protected autonomous prediction",
    )
    add_panel_header(
        fig,
        outer[1],
        "b",
        ("Structural uncertainty supports", "multiple representations"),
        "Temporal, spatial and coupled relations on one mode",
        title_fontsize=6.65,
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
    manifest = source.load_manifest(source.MANIFEST)
    pendulum = source.compute_pendulum(manifest)
    heat = source.compute_heat()
    with mpl.rc_context(STYLE):
        figure = build_figure(pendulum, heat)
        paths = export_figure(figure)
        plt.close(figure)

    print(f"canvas_mm={WIDTH_MM:.1f}x{HEIGHT_MM:.1f}")
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
