from __future__ import annotations

"""Nature Computational Science-oriented turning-manifold main figure.

This v8 renderer preserves the analytical signals, sensitivity-centered
coordinate, and turning-event calculations from v7 while formatting the figure
at an exact 183 x 170 mm final size.

Outputs
-------
phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf
phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.svg
phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.png
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch, Rectangle
from matplotlib.text import Text
from matplotlib.transforms import ScaledTranslation
from scipy.optimize import brentq

from phase_turning_manifold_sensitivity_centered_with_x2_purple_v7 import (
    ddx1_dt2,
    dsc,
    dx1_dt,
    dx2_dt,
    fit_g_bar,
    fit_phase,
    gain,
    roots_on_interval,
    turning_curve,
    x1,
    x2,
)

OUTDIR = Path(__file__).resolve().parent
STEM = "phase_turning_manifold_sensitivity_centered_with_x2_purple_v8"
PNG = OUTDIR / f"{STEM}.png"
PDF = OUTDIR / f"{STEM}.pdf"
SVG = OUTDIR / f"{STEM}.svg"

WIDTH_MM = 183.0
HEIGHT_MM = 170.0
MM_PER_INCH = 25.4
PNG_DPI = 450

# Restore the v7 blue/green/purple visual identity while retaining the v8
# line-style redundancy: the negative branch is dashed and the positive branch
# is solid, so branch meaning does not depend on color alone.
NEGATIVE = "#2F6FA5"
POSITIVE = "#4F9B68"
REFERENCE = "#A94700"  # x_2(t); matches the Figure 4 omega orange
CONDITION = "#2F7D4F"
INTERSECTION = "#1D4E78"
MANIFOLD = "#111111"
TEXT = "#222222"
MUTED = "#555555"
GUIDE = "#777777"
PANEL_BG = "#F5F5F5"
BRANCH_ALPHA = 0.96
# Standard SIR type scale, in points at the final printed size. The canvas is
# already the 183 mm double-column print width, so PRINT_SCALE is 1.
PRINT_WIDTH_IN = 183.0 / 25.4
PRINT_SCALE = (WIDTH_MM / MM_PER_INCH) / PRINT_WIDTH_IN


def pt(size):
    """Convert a printed point size to canvas points."""
    return size * PRINT_SCALE


FS_TITLE = pt(8.0)
FS_PANEL_LETTER = pt(8.0)
FS_PANEL_TITLE = pt(7.0)
FS_SUBTITLE = pt(6.0)
FS_LABEL = pt(6.5)
FS_TICK = pt(6.0)
FS_BODY = pt(6.0)
FS_FINE = pt(5.5)
# Latin Modern ships optical sizes: at 5-8 pt it switches to the lmr5-lmr8
# designs, which are 15-23% wider than lmr10 and overflow this fixed layout.
# Declaring the families before their .fd files load pins every shape to the
# 10 pt design, scaled; glyphs stay Latin Modern.
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
LATEX_PREAMBLE = (
    r"\usepackage[T1]{fontenc}"
    r"\usepackage{lmodern}"
    r"\usepackage{amsmath,amssymb}"
    + LM_DESIGN_SIZE_PIN
)

# Override the serif/STIX defaults set when the analytical v7 module is
# imported. All text, including math, is typeset by LaTeX in Latin Modern to
# match the manuscript.
mpl.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "text.latex.preamble": LATEX_PREAMBLE,
    "font.size": FS_BODY,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "path",
    "axes.grid": False,
    "axes.linewidth": 0.80,
    "axes.labelcolor": TEXT,
    "axes.labelsize": FS_LABEL,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "xtick.labelsize": FS_TICK,
    "ytick.labelsize": FS_TICK,
    "legend.fontsize": FS_BODY,
    "legend.title_fontsize": FS_BODY,
    "axes.titlesize": FS_PANEL_TITLE,
    "figure.titlesize": FS_TITLE,
    "text.color": TEXT,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def style_axis(ax, *, tick_size=FS_TICK, label_size=FS_LABEL):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_linewidth(0.80)
    ax.tick_params(
        axis="both", which="major", labelsize=tick_size,
        length=2.8, width=0.70, pad=1.8,
    )
    ax.xaxis.label.set_size(label_size)
    ax.yaxis.label.set_size(label_size)
    ax.xaxis.labelpad = 2.2
    ax.yaxis.labelpad = 2.2
    ax.xaxis.get_offset_text().set_fontsize(tick_size)
    ax.yaxis.get_offset_text().set_fontsize(tick_size)
    ax.grid(False)
    ax.set_axisbelow(True)


def add_panel_header(fig, spec, letter, title, subtitle):
    """Create a dedicated header band so panel text never covers data."""
    header = fig.add_subplot(spec)
    header.set_axis_off()
    # Use a fixed physical offset rather than a fraction of axis width so the
    # full-width Panel A title starts at the same margin as Panels B-E.
    title_transform = header.transAxes + ScaledTranslation(
        15.0 / 72.0, 0.0, fig.dpi_scale_trans
    )
    artists = [
        header.text(
            0.00, 0.70, rf"\textbf{{{letter}}}",
            transform=header.transAxes,
            fontsize=FS_PANEL_LETTER,
            ha="left", va="center",
        ),
        header.text(
            0.00, 0.70, rf"\textbf{{{title}}}",
            transform=title_transform,
            fontsize=FS_PANEL_TITLE,
            ha="left", va="center",
        ),
        header.text(
            0.00, 0.20, subtitle,
            transform=title_transform,
            fontsize=FS_SUBTITLE, color=MUTED,
            ha="left", va="center",
        ),
    ]
    return header, artists


def draw_branch_runs(
    ax,
    x,
    y,
    positive_mask,
    *,
    lw=0.72,
    alpha=0.72,
    zorder=2,
):
    """Draw a deterministic trajectory with color and line-style redundancy."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    positive_mask = np.asarray(positive_mask, dtype=bool)
    if not (x.shape == y.shape == positive_mask.shape):
        raise ValueError("Trajectory coordinates and branch mask must align.")

    changes = np.flatnonzero(positive_mask[1:] != positive_mask[:-1]) + 1
    starts = np.r_[0, changes]
    stops = np.r_[changes, x.size]
    for start, stop in zip(starts, stops, strict=True):
        # Include the first point of the next run to avoid a visible gap at the
        # numerically sampled branch transition.
        end = min(int(stop) + 1, x.size)
        flag = bool(positive_mask[int(start)])
        ax.plot(
            x[int(start):end],
            y[int(start):end],
            color=POSITIVE if flag else NEGATIVE,
            linestyle="-" if flag else (0, (3.0, 1.8)),
            lw=lw,
            alpha=alpha,
            solid_capstyle="round",
            dash_capstyle="round",
            zorder=zorder,
        )


def draw_turning_events(ax, x, y, *, size=17, linewidth=0.78, zorder=7):
    return ax.scatter(
        x, y,
        s=size,
        facecolor="white",
        edgecolor=MANIFOLD,
        linewidth=linewidth,
        zorder=zorder,
    )


def add_panel_c_key(ax):
    """Place a compact Panel C semantic key within its inset region."""
    ax.set_axis_off()
    ax.set_facecolor("white")
    ax.add_patch(Rectangle(
        (0.0, 0.0), 1.0, 1.0,
        transform=ax.transAxes,
        facecolor="white",
        edgecolor="none",
        linewidth=0.0,
        alpha=0.96,
        zorder=-1,
        clip_on=False,
    ))
    artists = []

    y_rows = [0.84, 0.50, 0.16]
    ax.plot([0.02, 0.14], [y_rows[0], y_rows[0]], color=MANIFOLD, lw=1.40,
            transform=ax.transAxes, clip_on=False)
    artists.append(ax.text(
        0.20, y_rows[0], r"$\dot{x}_1=0$",
        transform=ax.transAxes, fontsize=FS_BODY, va="center"
    ))

    ax.plot([0.02, 0.14], [y_rows[1], y_rows[1]], color=CONDITION, lw=1.20,
            linestyle=(0, (4.0, 2.5)), transform=ax.transAxes, clip_on=False)
    artists.append(ax.text(
        0.20, y_rows[1], r"$g=\bar{g}$ locus",
        transform=ax.transAxes, fontsize=FS_BODY, va="center"
    ))

    ax.scatter([0.08], [y_rows[2]], marker="x", s=22, color=INTERSECTION,
               linewidth=1.05, transform=ax.transAxes, clip_on=False)
    artists.append(ax.text(
        0.20, y_rows[2], "Intersection",
        transform=ax.transAxes, fontsize=FS_BODY, va="center"
    ))
    return artists


def add_panel_c_condition_note(ax):
    """Restore the v7 conditioning-locus sensitivity statement."""
    ax.set_axis_off()
    ax.set_facecolor("white")
    ax.add_patch(Rectangle(
        (0.0, 0.0), 1.0, 1.0,
        transform=ax.transAxes,
        facecolor="white",
        edgecolor="none",
        alpha=0.96,
        zorder=-1,
        clip_on=False,
    ))
    note = ax.text(
        0.50,
        0.50,
        r"$g=\bar{g}$: Direct Numerator"
        "\n"
        "Sensitivity Vanishes At"
        "\n"
        "The Conditioning Locus",
        transform=ax.transAxes,
        fontsize=FS_BODY,
        linespacing=1.08,
        color=MUTED,
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.22",
            facecolor="white",
            edgecolor="#C7D9CC",
            linewidth=0.55,
            alpha=0.96,
        ),
    )
    return [note]


def add_panel_c_equations(ax):
    """Show the two defining identities with a background fitted to the text."""
    ax.set_axis_off()
    ax.set_facecolor("none")
    equation = ax.text(
        0.0,
        0.72,
        r"$D^{\mathrm{sc}}=u_n(g-\bar{g})+s_{\mathrm{eff}}\,g$"
        "\n"
        r"$\dot{x}_1=0 \;\Leftrightarrow\; D^{\mathrm{sc}}=s_{\mathrm{eff}}\,g(\dot{x}_2)$",
        transform=ax.transAxes,
        fontsize=FS_BODY,
        linespacing=1.18,
        ha="left",
        va="top",
        bbox=dict(
            boxstyle="square,pad=0.12",
            facecolor="white",
            edgecolor="none",
            alpha=0.96,
        ),
    )
    return [equation]


def tick_label_is_in_view(fig, artist):
    """Return False for Matplotlib tick labels outside their axis limits."""
    for axis in fig.axes:
        for tick in [*axis.xaxis.get_major_ticks(), *axis.xaxis.get_minor_ticks()]:
            if artist is tick.label1 or artist is tick.label2:
                lower, upper = sorted(axis.get_xlim())
                return lower - 1e-12 <= tick.get_loc() <= upper + 1e-12
        for tick in [*axis.yaxis.get_major_ticks(), *axis.yaxis.get_minor_ticks()]:
            if artist is tick.label1 or artist is tick.label2:
                lower, upper = sorted(axis.get_ylim())
                return lower - 1e-12 <= tick.get_loc() <= upper + 1e-12
    return True


def visible_nonempty_text(fig):
    return [
        artist for artist in fig.findobj(match=Text)
        if (
            artist.get_visible()
            and artist.get_text().strip()
            and tick_label_is_in_view(fig, artist)
        )
    ]


def audit_dimensions(fig):
    """Assert the final figure canvas is exactly 183 x 170 mm."""
    actual_mm = np.asarray(fig.get_size_inches(), dtype=float) * MM_PER_INCH
    expected_mm = np.array([WIDTH_MM, HEIGHT_MM], dtype=float)
    if not np.allclose(actual_mm, expected_mm, rtol=0.0, atol=1e-10):
        raise RuntimeError(
            "Figure dimensions are not exactly 183 x 170 mm: "
            f"found {actual_mm[0]:.12f} x {actual_mm[1]:.12f} mm."
        )


def audit_typography(fig, panel_labels, figure_title):
    """Assert panel-label, title, text-size, color, and Latin Modern requirements."""
    fig.canvas.draw()
    expected_letters = list("abcde")
    if [artist.get_text() for artist in panel_labels] != [
        rf"\textbf{{{letter}}}" for letter in expected_letters
    ]:
        raise RuntimeError("Panel labels must be exactly lowercase a-e in order.")

    for artist in panel_labels:
        if not np.isclose(artist.get_fontsize(), FS_PANEL_LETTER, rtol=0.0, atol=1e-12):
            raise RuntimeError(f"Panel label {artist.get_text()!r} is not exactly 8 pt.")

    if not np.isclose(figure_title.get_fontsize(), FS_TITLE, rtol=0.0, atol=1e-12):
        raise RuntimeError("The global figure title must be exactly 8 pt.")
    if not figure_title.get_text().startswith(r"\textbf{"):
        raise RuntimeError("The global figure title must be bold.")

    exempt_ids = {id(artist) for artist in panel_labels} | {id(figure_title)}
    invalid_sizes = []
    colored_text = []
    for artist in visible_nonempty_text(fig):
        if id(artist) not in exempt_ids:
            size = float(artist.get_fontsize())
            if not 5.0 <= size <= 7.0:
                invalid_sizes.append((artist.get_text(), size))

        rgba = mpl.colors.to_rgba(artist.get_color())
        if not np.allclose(rgba[:3], [rgba[0]] * 3, rtol=0.0, atol=1e-12):
            colored_text.append((artist.get_text(), artist.get_color()))

    if invalid_sizes:
        raise RuntimeError(f"Visible non-panel text outside 5-7 pt: {invalid_sizes}")
    if not (
        mpl.rcParams["text.usetex"]
        and "lmodern" in mpl.rcParams["text.latex.preamble"]
        and LM_DESIGN_SIZE_PIN in mpl.rcParams["text.latex.preamble"]
    ):
        raise RuntimeError(
            "Figure text must be typeset by LaTeX in Latin Modern (lmodern) "
            "with the 10 pt design-size pin."
        )
    if colored_text:
        raise RuntimeError(f"Figure text must be black or gray: {colored_text}")


def audit_layout(fig, data_axes, contained_groups=(), grid_axes=()):
    """Fail on text clipping, containment escape, grids, or main-axis overlap."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox

    clipped = []
    for artist in visible_nonempty_text(fig):
        bbox = artist.get_window_extent(renderer)
        # Matplotlib keeps off-range tick Text objects marked visible even when
        # they are wholly outside the canvas and are not rendered. Audit only
        # text whose rendered extent intersects the figure canvas.
        if not bbox.overlaps(canvas):
            continue
        if (
            bbox.x0 < canvas.x0 - 1
            or bbox.y0 < canvas.y0 - 1
            or bbox.x1 > canvas.x1 + 1
            or bbox.y1 > canvas.y1 + 1
        ):
            clipped.append(artist.get_text())
    if clipped:
        raise RuntimeError(f"Visible figure text is clipped: {clipped}")

    escaped = []
    for axis, artists in contained_groups:
        axis_bbox = axis.get_window_extent(renderer)
        for artist in artists:
            bbox = artist.get_window_extent(renderer)
            if not (
                bbox.x0 >= axis_bbox.x0 - 1
                and bbox.y0 >= axis_bbox.y0 - 1
                and bbox.x1 <= axis_bbox.x1 + 1
                and bbox.y1 <= axis_bbox.y1 + 1
            ):
                escaped.append(artist.get_text())
    if escaped:
        raise RuntimeError(f"Header/key text escapes its allocated axes: {escaped}")

    for axis in grid_axes:
        gridlines = [*axis.get_xgridlines(), *axis.get_ygridlines()]
        if any(line.get_visible() for line in gridlines):
            raise RuntimeError("Gridlines must not be visible in the submitted figure.")

    # Main data axes should remain disjoint. Sidecar axes are deliberately
    # adjacent and are checked separately by their GridSpec positions.
    for index, left in enumerate(data_axes):
        for right in data_axes[index + 1:]:
            if left.get_position().overlaps(right.get_position()):
                raise RuntimeError("Main data axes overlap after layout.")


def audit_scientific_invariants(tp_r1, x_cond, y_cond, phase):
    if not np.allclose(tp_r1, 0.0, atol=2e-8):
        raise RuntimeError("Turning events no longer lie on dot{x}_1=0.")
    if not np.isclose(turning_curve(np.array([x_cond]), phase)[0], y_cond):
        raise RuntimeError("Conditioning-locus intersection is inconsistent.")


def audit_exports(outputs):
    missing = [str(output) for output in outputs if not output.exists()]
    empty = [str(output) for output in outputs if output.exists() and output.stat().st_size == 0]
    if missing or empty:
        raise RuntimeError(f"Figure export audit failed; missing={missing}, empty={empty}")


def main():
    # Scientific construction retained exactly from v7.
    t = np.linspace(0.0, 36.0, 12000)
    y1 = x1(t)
    y2 = x2(t)
    r1 = dx1_dt(t)
    r2 = dx2_dt(t)
    a1 = ddx1_dt2(t)
    phase = fit_phase(t, rho=0.10, kappa=1.0)
    g_bar = fit_g_bar(t, phase)
    d_sc = dsc(t, phase, g_bar)

    turning_t = roots_on_interval(dx1_dt, t)
    x2_turning_t = roots_on_interval(dx2_dt, t)
    if turning_t.size and x2_turning_t.size:
        separation = np.min(
            np.abs(turning_t[:, None] - x2_turning_t[None, :])
        )
        if float(separation) < 1e-6:
            raise RuntimeError(
                "An x1 turning event coincides with an x2 turning event."
            )

    increasing = r1 >= 0.0
    tp_x1 = x1(turning_t)
    tp_x2 = x2(turning_t)
    tp_r1 = dx1_dt(turning_t)
    tp_r2 = dx2_dt(turning_t)
    tp_a1 = ddx1_dt2(turning_t)
    tp_d_sc = dsc(turning_t, phase, g_bar)

    # Exact double-column final size. No tight bounding box is used on export.
    fig = plt.figure(
        figsize=(WIDTH_MM / MM_PER_INCH, HEIGHT_MM / MM_PER_INCH),
        dpi=254,  # 10 pixels/mm keeps 183 x 170 mm exact on the audit canvas.
        facecolor="white",
    )
    outer = fig.add_gridspec(
        3, 1,
        height_ratios=[0.76, 1.10, 1.10],
        hspace=0.30,
        left=0.080,
        right=0.985,
        bottom=0.070,
        top=0.895,
    )

    header_groups = []
    panel_labels = []

    # Panel a: dedicated header band plus full-width time-series axis.
    a_grid = outer[0].subgridspec(
        2, 1, height_ratios=[0.20, 0.80], hspace=0.02
    )
    header, artists = add_panel_header(
        fig,
        a_grid[0],
        "a",
        "Multiscale analytical target",
        r"Branch style follows the sign of $\dot{x}_1$; circles mark $x_1$ turning events",
    )
    header_groups.append((header, artists))
    panel_labels.append(artists[0])
    ax_a = fig.add_subplot(a_grid[1])

    ax_a.plot(t, y2, color=REFERENCE, lw=1.15, alpha=0.90, zorder=1)
    for tt, yy1, yy2 in zip(turning_t, tp_x1, tp_x2, strict=True):
        ax_a.plot(
            [tt, tt], [yy1, yy2],
            color=GUIDE,
            lw=0.55,
            linestyle=(0, (2.0, 2.2)),
            alpha=0.62,
            zorder=1.5,
        )
    draw_branch_runs(ax_a, t, y1, increasing, lw=1.25, alpha=BRANCH_ALPHA, zorder=3)
    draw_turning_events(ax_a, turning_t, tp_x1, size=13, linewidth=0.72)
    ax_a.set_xlim(float(t.min()), float(t.max()))
    ax_a.set_xlabel(r"$t$ (dimensionless)")
    ax_a.set_ylabel("State amplitude (dimensionless)")
    ax_a.margins(y=0.10)
    style_axis(ax_a)
    header.legend(
        handles=[
            Line2D(
                [0], [0], color=REFERENCE, lw=1.45, linestyle="-",
                label=r"$x_2(t)$",
            )
        ],
        loc="center right",
        bbox_to_anchor=(1.0, 0.48),
        frameon=False,
        fontsize=FS_BODY,
        handlelength=2.2,
        handletextpad=0.50,
        borderaxespad=0.0,
    )

    # Middle and bottom rows share the same two-column geometry so the
    # left spines of Panels C and E align vertically, as in v7.
    middle = outer[1].subgridspec(
        1, 2, width_ratios=[1.0, 1.0], wspace=0.25
    )

    b_grid = middle[0].subgridspec(
        2, 1, height_ratios=[0.19, 0.81], hspace=0.02
    )
    header, artists = add_panel_header(
        fig,
        b_grid[0],
        "b",
        "Level-rate coordinates",
        r"The target branches remain folded in $(x_2,\dot{x}_2)$",
    )
    header_groups.append((header, artists))
    panel_labels.append(artists[0])
    ax_b = fig.add_subplot(b_grid[1])
    draw_branch_runs(ax_b, y2, r2, increasing, lw=1.25, alpha=BRANCH_ALPHA)
    draw_turning_events(ax_b, tp_x2, tp_r2, size=15)
    ax_b.set_xlabel(r"$x_2$ (dimensionless)")
    ax_b.set_ylabel(r"$\dot{x}_2$ (dimensionless)")
    ax_b.margins(x=0.05, y=0.07)
    style_axis(ax_b)

    c_grid = middle[1].subgridspec(
        2, 1, height_ratios=[0.19, 0.81], hspace=0.02
    )
    header, artists = add_panel_header(
        fig,
        c_grid[0],
        "c",
        "Sensitivity-centered phase coordinates",
        "Manifold geometry and conditioning organize the target",
    )
    header_groups.append((header, artists))
    panel_labels.append(artists[0])
    # Panel C uses the full right-column body so its x-axis matches Panel E.
    # The local view and explanatory elements are child insets, following the
    # compact v7 organization without shortening the primary data axis.
    ax_c = fig.add_subplot(c_grid[1])
    ax_c_zoom = ax_c.inset_axes([0.60, 0.66, 0.38, 0.32], zorder=20)
    # Use the open upper-left region for the borderless semantic key.
    ax_c_key = ax_c.inset_axes([0.12, 0.735, 0.24, 0.25], zorder=19)
    # Place the conditioning statement directly below the local zoom, right of
    # the zoom connectors and inside the panel's right spine (three lines keep
    # it clear of both at 6 pt).
    ax_c_condition = ax_c.inset_axes([0.586, 0.337, 0.411, 0.215], zorder=19)
    # Place the defining identities in the lower-left white region near x=-1,
    # clear of the g = g-bar locus and the zoom source box.
    ax_c_equations = ax_c.inset_axes([0.0155, 0.012, 0.47, 0.235], zorder=19)

    draw_branch_runs(ax_c, r2, d_sc, increasing, lw=1.25, alpha=BRANCH_ALPHA)
    draw_turning_events(ax_c, tp_r2, tp_d_sc, size=15)

    dx2_grid = np.linspace(float(r2.min()), float(r2.max()), 1200)
    manifold = turning_curve(dx2_grid, phase)
    ax_c.plot(dx2_grid, manifold, color=MANIFOLD, lw=1.45, zorder=6)

    cond_fun = lambda value: float(
        gain(np.asarray(value) / phase.scale_d, phase) - g_bar
    )
    x_cond = float(brentq(cond_fun, float(r2.min()), float(r2.max())))
    y_cond = float(phase.s_eff * g_bar)
    ax_c.axvline(
        x_cond,
        color=CONDITION,
        lw=1.20,
        linestyle=(0, (4.0, 2.5)),
        zorder=5,
    )
    ax_c.scatter(
        [x_cond], [y_cond],
        marker="x", s=27,
        color=INTERSECTION, linewidth=1.15,
        zorder=9,
    )
    ax_c.set_xlabel(r"$\dot{x}_2$ (dimensionless)")
    ax_c.set_ylabel(r"$D^{\mathrm{sc}}_{x_2}x_1$ (dimensionless)")
    ax_c.set_ylim(bottom=0.0)
    ax_c.margins(x=0.05)
    style_axis(ax_c)

    # Focus the local view on the requested conditioning neighborhood. This
    # single tuple also drives the dotted source box and both connectors.
    zoom_xlim = (-0.45, 0)
    y_half = 0.18
    zoom_ylim = (max(0.0, y_cond - y_half), y_cond + y_half)
    if not zoom_xlim[0] <= x_cond <= zoom_xlim[1]:
        raise RuntimeError(
            "The conditioning-locus intersection falls outside the fixed "
            "Panel C local-view range [-0.3, -0.1]."
        )
    draw_branch_runs(
        ax_c_zoom, r2, d_sc, increasing,
        lw=0.70, alpha=BRANCH_ALPHA, zorder=2,
    )
    ax_c_zoom.plot(dx2_grid, manifold, color=MANIFOLD, lw=1.20, zorder=5)
    ax_c_zoom.axvline(
        x_cond,
        color=CONDITION,
        lw=1.05,
        linestyle=(0, (4.0, 2.5)),
        zorder=4,
    )
    draw_turning_events(ax_c_zoom, tp_r2, tp_d_sc, size=10, linewidth=0.65)
    ax_c_zoom.scatter(
        [x_cond], [y_cond], marker="x", s=21,
        color=INTERSECTION, linewidth=1.10, zorder=8,
    )
    ax_c_zoom.set_xlim(*zoom_xlim)
    ax_c_zoom.set_ylim(*zoom_ylim)
    ax_c_zoom.tick_params(labelsize=FS_FINE, length=2.4, width=0.65, pad=1.2)
    ax_c_zoom.xaxis.get_offset_text().set_fontsize(FS_FINE)
    ax_c_zoom.yaxis.get_offset_text().set_fontsize(FS_FINE)
    ax_c_zoom.grid(False)
    for spine in ax_c_zoom.spines.values():
        spine.set_linewidth(0.75)

    zoom_box = Rectangle(
        (zoom_xlim[0], zoom_ylim[0]),
        zoom_xlim[1] - zoom_xlim[0],
        zoom_ylim[1] - zoom_ylim[0],
        fill=False,
        edgecolor=GUIDE,
        linewidth=0.75,
        linestyle=(0, (2.5, 2.0)),
        zorder=8,
    )
    ax_c.add_patch(zoom_box)

    # Explicit cross-axes connectors preserve the v7 inset relationship while
    # keeping the local view in the non-obscuring external sidecar.
    zoom_connectors = []
    for source, target in [
        ((zoom_xlim[1], zoom_ylim[1]), (0.0, 1.0)),
        ((zoom_xlim[1], zoom_ylim[0]), (0.0, 0.0)),
    ]:
        connector = ConnectionPatch(
            xyA=source,
            xyB=target,
            coordsA=ax_c.transData,
            coordsB=ax_c_zoom.transAxes,
            arrowstyle="-",
            color=GUIDE,
            linewidth=0.68,
            alpha=0.62,
            clip_on=False,
            zorder=7.5,
        )
        fig.add_artist(connector)
        zoom_connectors.append(connector)

    c_key_artists = add_panel_c_key(ax_c_key)
    c_condition_artists = add_panel_c_condition_note(ax_c_condition)
    c_equation_artists = add_panel_c_equations(ax_c_equations)

    # Bottom row: balanced comparison panels with shared y limits.
    bottom = outer[2].subgridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.25)

    d_grid = bottom[0].subgridspec(
        2, 1, height_ratios=[0.19, 0.81], hspace=0.02
    )
    header, artists = add_panel_header(
        fig,
        d_grid[0],
        "d",
        "Rate-rate coordinates",
        r"Turning events lie on $\dot{x}_1=0$ with reference-rate context",
    )
    header_groups.append((header, artists))
    panel_labels.append(artists[0])
    ax_d = fig.add_subplot(d_grid[1])
    draw_branch_runs(ax_d, r2, r1, increasing, lw=1.25, alpha=BRANCH_ALPHA)
    ax_d.axhline(0.0, color=MANIFOLD, lw=1.10, zorder=3)
    draw_turning_events(ax_d, tp_r2, tp_r1, size=13)
    ax_d.set_xlabel(r"$\dot{x}_2$ (dimensionless)")
    ax_d.set_ylabel(r"$\dot{x}_1$ (dimensionless)")
    ax_d.margins(x=0.05)
    style_axis(ax_d)

    e_grid = bottom[1].subgridspec(
        2, 1, height_ratios=[0.19, 0.81], hspace=0.02
    )
    header, artists = add_panel_header(
        fig,
        e_grid[0],
        "e",
        "Rate-acceleration coordinates",
        r"Turning events map to local curvature values on $\dot{x}_1=0$",
    )
    header_groups.append((header, artists))
    panel_labels.append(artists[0])
    ax_e = fig.add_subplot(e_grid[1])
    draw_branch_runs(ax_e, a1, r1, increasing, lw=1.25, alpha=BRANCH_ALPHA)
    ax_e.axhline(0.0, color=MANIFOLD, lw=1.10, zorder=3)
    draw_turning_events(ax_e, tp_a1, tp_r1, size=13)
    ax_e.set_xlabel(r"$\ddot{x}_1$ (dimensionless)")
    ax_e.set_ylabel(r"$\dot{x}_1$ (dimensionless)")
    ax_e.margins(x=0.05)
    style_axis(ax_e)

    shared_y = 1.05 * float(np.max(np.abs(r1)))
    ax_d.set_ylim(-shared_y, shared_y)
    ax_e.set_ylim(-shared_y, shared_y)

    shared_handles = [
        Line2D([0], [0], color=POSITIVE, lw=1.55, linestyle="-",
               label=r"$\dot{x}_1>0$"),
        Line2D([0], [0], color=NEGATIVE, lw=1.55, linestyle=(0, (3.0, 1.8)),
               label=r"$\dot{x}_1<0$"),
        Line2D([0], [0], marker="o", markersize=4.4,
               markerfacecolor="white", markeredgecolor=MANIFOLD,
               markeredgewidth=0.75, linestyle="None",
               label=r"$x_1$ turning event"),
    ]
    figure_title = fig.suptitle(
        r"\textbf{Relational Coordinates Can Simplify The Organization Of A Scientific Target}",
        x=0.5,
        y=0.985,
        fontsize=FS_TITLE,
        color=TEXT,
    )
    fig.legend(
        handles=shared_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.958),
        ncol=3,
        frameon=False,
        fontsize=FS_BODY,
        handlelength=2.2,
        columnspacing=1.25,
        handletextpad=0.50,
    )

    data_axes = [ax_a, ax_b, ax_c, ax_d, ax_e]
    audit_scientific_invariants(tp_r1, x_cond, y_cond, phase)
    audit_dimensions(fig)
    audit_typography(fig, panel_labels, figure_title)

    c_position = ax_c.get_position()
    e_position = ax_e.get_position()
    if not (
        np.isclose(c_position.x0, e_position.x0, rtol=0.0, atol=1e-12)
        and np.isclose(c_position.x1, e_position.x1, rtol=0.0, atol=1e-12)
        and np.isclose(c_position.height, e_position.height, rtol=0.0, atol=1e-12)
    ):
        raise RuntimeError(
            "Panels C and E must have matching x-axis extents and axis heights."
        )

    audit_layout(
        fig,
        data_axes,
        contained_groups=[
            *header_groups,
            (ax_c_key, c_key_artists),
            (ax_c_condition, c_condition_artists),
            (ax_c_equations, c_equation_artists),
        ],
        grid_axes=[*data_axes, ax_c_zoom],
    )

    # Tight bounding boxes include the local view's tick labels. Keep those
    # labels physically disjoint from the sensitivity note placed below it.
    renderer = fig.canvas.get_renderer()
    if ax_c_zoom.get_tightbbox(renderer).overlaps(
        ax_c_condition.get_tightbbox(renderer)
    ):
        raise RuntimeError(
            "Panel C local-view labels overlap the sensitivity note."
        )

    # PDF is the primary editable vector output; SVG remains editable, and PNG
    # is a 450-dpi RGB preview. Exact page size is preserved without tight bbox.
    fig.savefig(PDF, dpi=PNG_DPI, facecolor="white")
    fig.savefig(SVG, facecolor="white")
    fig.savefig(PNG, dpi=PNG_DPI, facecolor="white")
    plt.close(fig)

    audit_exports((PDF, SVG, PNG))

    print("Saved Nature Computational Science-oriented v8:")
    print(f"Primary PDF: {PDF}")
    print(f"Editable SVG: {SVG}")
    print(f"450-dpi PNG preview: {PNG}")
    print(f"physical size: {WIDTH_MM:.0f} x {HEIGHT_MM:.0f} mm")
    print(
        "phase parameters: "
        f"rho={phase.rho:.3f}, kappa={phase.kappa:.3f}, "
        f"g_bar={g_bar:.6f}, t=[{t.min():.1f}, {t.max():.1f}]"
    )


if __name__ == "__main__":
    main()
