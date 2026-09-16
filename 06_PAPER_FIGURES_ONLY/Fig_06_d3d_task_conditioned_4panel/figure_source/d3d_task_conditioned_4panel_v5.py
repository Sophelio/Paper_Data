"""Render the DIII-D task-conditioned four-panel manuscript figure.

The frozen data bundle is expected in ``fig6data`` beside this script unless a
location is supplied with ``--data-dir``.  All panel-level movement, scaling,
and typography controls live together near the top of this file so layout
adjustments do not require retuning individual artists.
"""

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "fig6data"

REQUIRED_FILES = [
    "d3d_discharge_coefficients.csv",
    "corrected_coefficient_classification.csv",
    "corrected_coefficient_heterogeneity_primary.csv",
    "heldout_discharge_results.csv",
] + [f"fold_{k}_result.json" for k in range(6)]

# Optional: if present, the pre-derived matrix is used only to cross-check the
# 6 x 35 matrix this script builds from the six fold JSON files.
OPTIONAL_CHECK_FILE = "panel2_fold_support_matrix.csv"

INK = "#17324D"
NAVY = "#274C77"
BLUE = "#4F7FA8"
BLUE_DARK = "#315E86"
BLUE_LIGHT = "#B8CCDD"
GREEN = "#2E7D62"
GREEN_MID = "#5E9A82"
GREEN_LIGHT = "#BFD8CC"
GREEN_PALE = "#EDF6F1"
GREEN_WASH = "#F6FAF8"
SLATE = "#66788B"
MID_SLATE = "#66788B"
GRID = "#DDE4E9"
RULE = "#E2E7EB"
WHITE = "#FFFFFF"
SOFT = "#F7F9FB"
LOSS = "#8D633E"
LOSS_FACE = "#F7EFE8"
UNUSED = "#637480"
UNUSED_FACE = "#FAFBFC"

# Semantic enlargement for explanatory slate/gray text only. Scientific marks,
# colored annotations, equations, and axis typography retain their own scales.
GRAY_TEXT_SCALE = 1.15
LOWER_PANEL_GRAY_BOOST = 1.15
GLOBAL_SUBTITLE_FONTSIZE = 7.8


@dataclass(frozen=True)
class PanelLayout:
    """Top-level transform and typography controls for one panel.

    ``rect`` is ``(left, bottom, width, height)`` in the panel GridSpec cell.
    Editing this one tuple moves or scales every content artist in the panel;
    the panel heading remains aligned to the shared figure grid.
    """

    rect: tuple[float, float, float, float]
    font_scale: float = 1.0
    box_scale: float = 1.0


# --------------------------------------------------------------------------
# Panel containers: tune the whole figure from these four lines.
# ``font_scale`` changes type only; ``box_scale`` changes Panel-A nodes only.
# --------------------------------------------------------------------------
PANEL_A_LAYOUT = PanelLayout(rect=(-0.025, -0.005, 1.055, 0.995), font_scale=1.12, box_scale=1.04)
PANEL_B_LAYOUT = PanelLayout(rect=(-0.015, -0.005, 1.030, 0.995), font_scale=1.10)
PANEL_C_LAYOUT = PanelLayout(rect=(-0.015, -0.005, 1.030, 0.995), font_scale=1.10)
PANEL_D_LAYOUT = PanelLayout(rect=(-0.010, -0.005, 1.020, 0.995), font_scale=1.12)

# Panel-A bottom summaries share a height but allocate width according to content:
# the semantic inventory is compact, while the complete cohort equation is wide.
PANEL_A_UNUSED_BOX_CENTER = (0.130, 0.100)
PANEL_A_UNUSED_BOX_SIZE = (0.230, 0.185)
PANEL_A_FORM_BOX_CENTER = (0.635, 0.100)
PANEL_A_FORM_BOX_SIZE = (0.700, 0.185)

# Exact physical canvas.  This is a general two-column manuscript layout;
# publisher-specific requirements should be checked at submission time.
FIGURE_SIZE_IN = (7.15, 6.90)
EXPORT_DPI = 600

PRIM_MATH = {
    "pcdiamag3": r"$W_{\mathrm{dia}}$",
    "betan": r"$\beta_N$",
    "kappa": r"$\kappa$",
    "q95": r"$q_{95}$",
    "li": r"$\ell_i$",
}

COORD_MATH = {
    "D_kappa W_dia": r"$D_{\kappa}^{(s)}W_{\mathrm{dia}}$",
    "D_betaN W_dia": r"$D_{\beta_N}^{(s)}W_{\mathrm{dia}}$",
    "D_betaN kappa": r"$D_{\beta_N}^{(s)}\kappa$",
    "D_betaN l_i": r"$D_{\beta_N}^{(s)}\ell_i$",
    "q95 / kappa": r"$\left(\frac{q_{95}}{\kappa}\right)^{(s)}$",
    "dot beta_N": r"$\dot{\beta}_N$",
    "dot kappa": r"$\dot{\kappa}$",
}

COEF_COLS = {
    "D_kappa W_dia": "coef_Dkappa_Wdia",
    "D_betaN W_dia": "coef_Dbetan_Wdia",
    "D_betaN kappa": "coef_Dbetan_kappa",
    "D_betaN l_i": "coef_Dbetan_li",
    "q95 / kappa": "coef_q95_over_kappa",
    "dot beta_N": "coef_dot_betan",
    "dot kappa": "coef_dot_kappa",
}


def _style() -> dict[str, object]:
    """Return a scoped print style without mutating caller-wide rcParams."""
    return {
        "figure.dpi": 180,
        "savefig.dpi": EXPORT_DPI,
        "savefig.bbox": None,
        "savefig.pad_inches": 0.0,
        "savefig.facecolor": WHITE,
        "savefig.transparent": False,
        "font.family": "serif",
        "font.serif": [
            "Times New Roman",
            "Tinos",
            "Nimbus Roman No9 L",
            "Liberation Serif",
            "DejaVu Serif",
        ],
        # STIX supplies Times-compatible glyphs if the primary family lacks one.
        "mathtext.fontset": "custom",
        "mathtext.rm": "Times New Roman",
        "mathtext.it": "Times New Roman:italic",
        "mathtext.bf": "Times New Roman:bold",
        "mathtext.sf": "Times New Roman",
        "mathtext.fallback": "stix",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "font.size": 7.3,
        "axes.linewidth": 0.6,
    }


def _panel_container(panel_ax: plt.Axes, layout: PanelLayout) -> plt.Axes:
    """Create one movable/scalable content container inside a panel cell."""
    panel_ax.set_axis_off()
    content = panel_ax.inset_axes(layout.rect, transform=panel_ax.transAxes, zorder=1)
    content.set_facecolor("none")
    return content


def _round_box(ax, x, y, w, h, fc, ec, lw=0.8, radius=0.012, ls="-", z=3):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        linestyle=ls,
        zorder=z,
        clip_on=False,
    )
    ax.add_patch(patch)
    return patch


def _node(
    ax,
    x,
    y,
    w,
    h,
    text,
    *,
    fc=WHITE,
    ec=RULE,
    lw=0.8,
    ls="-",
    fontsize=6.2,
    color=INK,
    weight="normal",
    z=4,
):
    _round_box(ax, x, y, w, h, fc, ec, lw=lw, ls=ls, z=z)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=color,
        fontweight=weight,
        zorder=z + 1,
        clip_on=False,
    )
    return dict(x=x, y=y, w=w, h=h)


def _curve(ax, a, b, *, color="#CCD4DB", lw=0.5, alpha=0.9, bend=0.04, z=1):
    x1 = a["x"] + a["w"] / 2
    y1 = a["y"]
    x2 = b["x"] - b["w"] / 2
    y2 = b["y"]
    dx = x2 - x1
    verts = [
        (x1, y1),
        (x1 + dx * 0.40, y1 + bend),
        (x2 - dx * 0.40, y2 - bend),
        (x2, y2),
    ]
    path = MplPath(
        verts,
        [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4],
    )
    ax.add_patch(
        PathPatch(
            path,
            facecolor="none",
            edgecolor=color,
            lw=lw,
            alpha=alpha,
            capstyle="round",
            zorder=z,
            clip_on=False,
        )
    )


def _panel_title(ax, letter: str, title: str, task: str, color: str) -> None:
    """Draw one baseline-aligned heading with its task contract in parentheses."""
    baseline_y = 1.050
    ax.text(
        0.00,
        baseline_y,
        letter,
        transform=ax.transAxes,
        ha="left",
        va="baseline",
        fontsize=9.8,
        fontweight="bold",
        color=INK,
        clip_on=False,
        zorder=20,
    )
    ax.text(
        0.060,
        baseline_y,
        f"{title} ({task})",
        transform=ax.transAxes,
        ha="left",
        va="baseline",
        fontsize=8.35,
        fontweight="bold",
        color=color,
        clip_on=False,
        zorder=20,
    )


def _preflight(data_dir: Path) -> None:
    """Verify every required input exists before any plotting begins."""
    if not data_dir.is_dir():
        raise SystemExit(f"Data directory not found: {data_dir}")
    missing = [name for name in REQUIRED_FILES if not (data_dir / name).is_file()]
    if missing:
        lines = [
            f"Missing {len(missing)} of {len(REQUIRED_FILES)} required input "
            f"files in {data_dir}:"
        ]
        lines += [f"  - {name}" for name in missing]
        raise SystemExit("\n".join(lines))
    print(
        f"Preflight OK: {len(REQUIRED_FILES)} required input files found in {data_dir}"
    )


def _verify_matrix(data_dir: Path, matrix: pd.DataFrame) -> None:
    """Optional cross-check against the pre-derived fold-support matrix."""
    path = data_dir / OPTIONAL_CHECK_FILE
    if not path.is_file():
        return
    ref = pd.read_csv(path).drop(columns=["fold"])
    same_cols = list(ref.columns) == list(matrix.columns)
    same_vals = same_cols and np.array_equal(ref.to_numpy(), matrix.to_numpy())
    if not same_vals:
        raise SystemExit(f"Fold-support matrix disagrees with {OPTIONAL_CHECK_FILE}")
    print(f"Cross-check OK: matrix matches {OPTIONAL_CHECK_FILE}")


def _load(data_dir: Path):
    coef = pd.read_csv(data_dir / "d3d_discharge_coefficients.csv")
    cls = pd.read_csv(data_dir / "corrected_coefficient_classification.csv")
    het = pd.read_csv(data_dir / "corrected_coefficient_heterogeneity_primary.csv")
    held = pd.read_csv(data_dir / "heldout_discharge_results.csv")

    folds = []
    for k in range(6):
        with (data_dir / f"fold_{k}_result.json").open("r", encoding="utf-8") as f:
            folds.append(json.load(f))

    all_coords = sorted({c for fold in folds for c in fold["coordinates"]})
    matrix = pd.DataFrame(0, index=range(6), columns=all_coords, dtype=int)
    for fold in folds:
        k = int(fold["fold"])
        for coordinate in fold["coordinates"]:
            matrix.loc[k, coordinate] = 1
    return coef, cls, het, held, folds, matrix


def _assert_invariants(coef, cls, held, folds, matrix):
    if len(coef) != 62:
        raise RuntimeError(
            f"Expected 62 descriptive coefficient rows, found {len(coef)}"
        )
    if len(cls) != 7:
        raise RuntimeError(f"Expected 7 coefficient classifications, found {len(cls)}")
    if len(held) != 62:
        raise RuntimeError(f"Expected 62 held-out discharge rows, found {len(held)}")
    if len(folds) != 6:
        raise RuntimeError(f"Expected 6 fold results, found {len(folds)}")
    if matrix.shape != (6, 35):
        raise RuntimeError(f"Expected 6 x 35 support matrix, found {matrix.shape}")
    if not np.isin(matrix.to_numpy(), [0, 1]).all():
        raise RuntimeError("Fold-support matrix must be binary")

    coefficient_values = coef[list(COEF_COLS.values())].to_numpy(float)
    if not np.isfinite(coefficient_values).all():
        raise RuntimeError("Coefficient table contains non-finite values")

    eras = set(held["era"].astype(str))
    if eras != {"earlier", "later"}:
        raise RuntimeError(f"Expected earlier/later eras, found {sorted(eras)}")
    held_values = held[["B1_nrmse", "REL_nrmse"]].to_numpy(float)
    if not np.isfinite(held_values).all():
        raise RuntimeError("Held-out NRMSE table contains non-finite values")
    if (
        np.any(held_values < 0)
        or np.any(held_values[:, 0] > 0.70)
        or np.any(held_values[:, 1] > 1.00)
    ):
        raise RuntimeError("Held-out NRMSE values fall outside the displayed axes")


def _draw_panel_a(panel_ax: plt.Axes, coef: pd.DataFrame) -> None:
    layout = PANEL_A_LAYOUT
    fs = lambda size: size * layout.font_scale
    gfs = lambda size: fs(size) * GRAY_TEXT_SCALE
    bs = lambda size: size * layout.box_scale

    _panel_title(
        panel_ax,
        "a",
        "Descriptive Relational Organization",
        r"$q_{\mathrm{desc}}$",
        GREEN,
    )
    ax = _panel_container(panel_ax, layout)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.set_axis_off()

    header_y = 0.975
    ax.text(
        0.11,
        header_y,
        "Observed",
        ha="center",
        va="top",
        fontsize=gfs(6.5),
        color=SLATE,
        fontweight="bold",
    )
    ax.text(
        0.53,
        header_y,
        "Selected Coordinates",
        ha="center",
        va="top",
        fontsize=gfs(6.5),
        color=SLATE,
        fontweight="bold",
    )
    ax.text(
        0.91,
        header_y,
        "Response",
        ha="center",
        va="top",
        fontsize=gfs(6.5),
        color=SLATE,
        fontweight="bold",
    )

    selected_engines = ["pcdiamag3", "betan", "kappa", "q95", "li"]
    selected_y = [0.835, 0.695, 0.555, 0.415, 0.275]
    prim = {}
    for engine, y in zip(selected_engines, selected_y, strict=True):
        prim[engine] = _node(
            ax,
            0.11,
            y,
            bs(0.17),
            bs(0.064),
            PRIM_MATH[engine],
            fc=WHITE,
            ec="#9FB0BE",
            lw=0.7,
            fontsize=fs(7.15),
        )

    unused_x, unused_y = PANEL_A_UNUSED_BOX_CENTER
    unused_w, unused_h = (bs(size) for size in PANEL_A_UNUSED_BOX_SIZE)
    _round_box(
        ax,
        unused_x,
        unused_y,
        unused_w,
        unused_h,
        UNUSED_FACE,
        "#D1D8DE",
        lw=0.6,
        ls=(0, (2, 1.5)),
    )
    ax.text(
        unused_x,
        unused_y + 0.19 * unused_h,
        "Available,\nUnselected",
        ha="center",
        va="center",
        fontsize=gfs(5.65),
        color=UNUSED,
        fontweight="bold",
        linespacing=1.06,
    )
    ax.text(
        unused_x,
        unused_y - 0.25 * unused_h,
        r"$P_{\mathrm{NBI}}\quad n_e\quad I_p$",
        ha="center",
        va="center",
        fontsize=gfs(6.20),
        color=UNUSED,
    )

    def pill(y, text, width):
        _round_box(
            ax,
            0.53,
            y,
            bs(width),
            bs(0.038),
            GREEN_WASH,
            GREEN_MID,
            lw=0.55,
            radius=0.008,
            z=5,
        )
        ax.text(
            0.53,
            y,
            text,
            ha="center",
            va="center",
            fontsize=fs(5.35),
            color=GREEN,
            fontweight="bold",
            zorder=6,
        )

    pair_x = (0.42, 0.64)
    pill(0.890, "Rates", 0.15)
    c_dotb = _node(
        ax,
        pair_x[0],
        0.825,
        bs(0.17),
        bs(0.056),
        COORD_MATH["dot beta_N"],
        fc=GREEN_PALE,
        ec=GREEN_LIGHT,
        fontsize=fs(6.65),
    )
    c_dotk = _node(
        ax,
        pair_x[1],
        0.825,
        bs(0.17),
        bs(0.056),
        COORD_MATH["dot kappa"],
        fc=GREEN_PALE,
        ec=GREEN_LIGHT,
        fontsize=fs(6.65),
    )

    pill(0.720, "Trajectory-Relational", 0.29)
    c_dbk = _node(
        ax,
        pair_x[0],
        0.655,
        bs(0.18),
        bs(0.06),
        COORD_MATH["D_betaN kappa"],
        fc=WHITE,
        ec=GREEN_LIGHT,
        fontsize=fs(6.55),
    )
    c_dbl = _node(
        ax,
        pair_x[1],
        0.655,
        bs(0.18),
        bs(0.06),
        COORD_MATH["D_betaN l_i"],
        fc=WHITE,
        ec=GREEN_LIGHT,
        fontsize=fs(6.55),
    )

    pill(0.550, "Target-Containing", 0.25)
    c_dkw = _node(
        ax,
        pair_x[0],
        0.485,
        bs(0.19),
        bs(0.06),
        COORD_MATH["D_kappa W_dia"],
        fc="#FFFCF5",
        ec=GREEN,
        fontsize=fs(6.45),
        ls=(0, (2.4, 1.3)),
    )
    c_dbw = _node(
        ax,
        pair_x[1],
        0.485,
        bs(0.19),
        bs(0.06),
        COORD_MATH["D_betaN W_dia"],
        fc="#FFFCF5",
        ec=GREEN,
        fontsize=fs(6.45),
        ls=(0, (2.4, 1.3)),
    )

    pill(0.380, "Algebraic", 0.18)
    c_alg = _node(
        ax,
        0.53,
        0.315,
        bs(0.18),
        bs(0.06),
        COORD_MATH["q95 / kappa"],
        fc=WHITE,
        ec=GREEN_LIGHT,
        fontsize=fs(6.55),
    )

    coords = {
        "dot beta_N": (c_dotb, ["betan"]),
        "dot kappa": (c_dotk, ["kappa"]),
        "D_betaN kappa": (c_dbk, ["betan", "kappa"]),
        "D_betaN l_i": (c_dbl, ["betan", "li"]),
        "D_kappa W_dia": (c_dkw, ["kappa", "pcdiamag3"]),
        "D_betaN W_dia": (c_dbw, ["betan", "pcdiamag3"]),
        "q95 / kappa": (c_alg, ["q95", "kappa"]),
    }
    for node, deps in coords.values():
        for j, engine in enumerate(deps):
            bend = 0.010 * (j - (len(deps) - 1) / 2)
            _curve(ax, prim[engine], node, color="#D2D8DE", lw=0.43, bend=bend)

    target_h = bs(0.090)
    target_y = 0.600
    target = _node(
        ax,
        0.91,
        target_y,
        bs(0.16),
        target_h,
        r"$\dot W_{\mathrm{dia}}$",
        fc=GREEN_PALE,
        ec=GREEN,
        lw=1.0,
        fontsize=fs(8.1),
        weight="bold",
        z=5,
    )
    ax.text(
        0.91,
        target_y - 0.5 * target_h - 0.025,
        "Shared Support",
        ha="center",
        va="center",
        fontsize=fs(5.45),
        color=GREEN,
        fontweight="bold",
    )
    for node, _ in coords.values():
        _curve(ax, node, target, color="#B7C6BE", lw=0.5, bend=0.0, z=2)

    means = {name: float(coef[column].mean()) for name, column in COEF_COLS.items()}
    form_x, form_y = PANEL_A_FORM_BOX_CENTER
    form_w, form_h = (bs(size) for size in PANEL_A_FORM_BOX_SIZE)
    _round_box(
        ax,
        form_x,
        form_y,
        form_w,
        form_h,
        "#FBFDFC",
        GREEN_LIGHT,
        lw=0.65,
        radius=0.009,
        z=4,
    )
    ax.text(
        form_x,
        form_y + 0.39 * form_h,
        "Cohort-Mean Descriptive Form",
        ha="center",
        va="center",
        fontsize=fs(6.15),
        color=GREEN,
        fontweight="bold",
        zorder=5,
    )
    equation_lines = [
        rf"$\dot W_{{\rm dia}}={means['D_kappa W_dia']:.3f}D_\kappa^{{(s)}} W_{{\rm dia}}"
        rf"{means['D_betaN W_dia']:+.3f}D_{{\beta_N}}^{{(s)}}W_{{\rm dia}}"
        rf"{means['D_betaN kappa']:+.3f}D_{{\beta_N}}^{{(s)}}\kappa$",
        rf"${means['D_betaN l_i']:+.4f}D_{{\beta_N}}^{{(s)}}\ell_i"
        rf"{means['q95 / kappa']:+.4f}\left(\frac{{q_{{95}}}}{{\kappa}}\right)^{{(s)}}"
        rf"{means['dot beta_N']:+.4f}\dot\beta_N"
        rf"{means['dot kappa']:+.3f}\dot\kappa+\varepsilon$",
    ]
    equation_offsets = (0.12, -0.07)
    for line, offset in zip(equation_lines, equation_offsets, strict=True):
        ax.text(
            form_x,
            form_y + offset * form_h,
            line,
            ha="center",
            va="center",
            fontsize=fs(5.35),
            color=INK,
            zorder=5,
        )
    ax.text(
        form_x,
        form_y - 0.36 * form_h,
        "62 discharges · shared support · discharge-specific coefficients",
        ha="center",
        va="center",
        fontsize=gfs(4.35),
        color=SLATE,
        fontstyle="italic",
        zorder=5,
    )


def _draw_panel_b(
    panel_ax: plt.Axes,
    coef: pd.DataFrame,
    cls: pd.DataFrame,
    het: pd.DataFrame,
) -> None:
    layout = PANEL_B_LAYOUT
    fs = lambda size: size * layout.font_scale
    gfs = lambda size: fs(size) * GRAY_TEXT_SCALE
    _panel_title(
        panel_ax,
        "b",
        "Coefficient Heterogeneity Audit",
        r"$q_{\mathrm{desc}}$",
        GREEN,
    )
    panel_ax.text(
        0.060,
        1.005,
        "62 discharge-specific coefficients",
        transform=panel_ax.transAxes,
        ha="left",
        va="top",
        fontsize=gfs(5.05),
        color=SLATE,
        fontstyle="italic",
        clip_on=False,
        zorder=20,
    )
    ax = _panel_container(panel_ax, layout)
    ax.set_axis_off()

    # Order separates robustly resolved coefficients from uncertainty-dominated ones.
    order = [
        "dot kappa",
        "dot beta_N",
        "D_betaN kappa",
        "D_betaN W_dia",
        "D_betaN l_i",
        "D_kappa W_dia",
        "q95 / kappa",
    ]
    cls = cls.set_index("display_name")
    het = het.set_index("display_name")

    ax.text(
        0.85,
        1.005,
        "Decision rule",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=fs(4.75),
        color=GREEN,
        fontweight="bold",
    )
    ax.text(
        0.85,
        0.966,
        "Resolved when between-discharge variation\n"
        "persists beyond within-discharge uncertainty",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=fs(4.15),
        color=GREEN,
        linespacing=1.05,
    )

    left = 0.180
    width = 0.585
    top = 0.905
    row_h = 0.082
    gap = 0.034

    for i, name in enumerate(order):
        y0 = top - (i + 1) * row_h - i * gap
        iax = ax.inset_axes([left, y0, width, row_h])

        vals = coef[COEF_COLS[name]].to_numpy(float)
        robust = cls.loc[name, "corrected_status"] == "ROBUSTLY_RESOLVED"
        face = GREEN_LIGHT if robust else BLUE_LIGHT
        edge = GREEN if robust else MID_SLATE

        counts, _, _ = iax.hist(
            vals,
            bins=9,
            density=True,
            color=face,
            edgecolor="white",
            linewidth=0.35,
            alpha=0.95,
        )

        vmin = float(np.min(vals))
        vmax = float(np.max(vals))
        span = vmax - vmin
        if span == 0:
            span = 1.0
        xs = np.linspace(vmin - 0.10 * span, vmax + 0.10 * span, 240)
        try:
            ys = gaussian_kde(vals, bw_method=0.2)(xs)
            iax.plot(xs, ys, color=edge, lw=1.0, zorder=3)
            ymax = max(
                float(np.max(counts)) if len(counts) else 0.0,
                float(np.max(ys)),
            ) * 1.18
        except Exception:
            ymax = (float(np.max(counts)) if len(counts) else 1.0) * 1.18

        if ymax <= 0:
            ymax = 1.0
        iax.set_ylim(0, ymax)

        mu = float(het.loc[name, "mu_REML"])
        iax.scatter(
            [mu],
            [0.72 * ymax],
            s=18,
            marker="D",
            facecolor=WHITE,
            edgecolor=INK if robust else MID_SLATE,
            linewidth=0.65,
            zorder=4,
        )

        iax.axvline(0, color=RULE, lw=0.75, zorder=1)
        iax.set_xlim(vmin, vmax)
        iax.set_yticks([])
        iax.set_xticks([vmin, vmax])
        iax.set_xticklabels([f"{vmin:.2g}", f"{vmax:.2g}"])
        iax.set_xticks(np.linspace(vmin, vmax, 5)[1:-1], minor=True)
        iax.tick_params(
            axis="x",
            which="major",
            labelbottom=True,
            labelsize=gfs(3.55),
            labelcolor=SLATE,
            color="#AAB6BE",
            length=1.5,
            width=0.45,
            pad=0.3,
        )
        iax.tick_params(
            axis="x",
            which="minor",
            labelbottom=False,
            length=0,
        )
        endpoint_labels = iax.get_xticklabels()
        endpoint_labels[0].set_ha("left")
        endpoint_labels[-1].set_ha("right")
        iax.grid(axis="x", which="minor", color=GRID, lw=0.40, alpha=0.7)
        iax.set_axisbelow(True)

        for side in ["top", "right", "left"]:
            iax.spines[side].set_visible(False)
        iax.spines["bottom"].set_color("#AAB6BE")
        iax.spines["bottom"].set_linewidth(0.5)

        ax.text(
            0.01,
            y0 + 0.50 * row_h,
            COORD_MATH[name],
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=fs(5.15),
            color=INK,
        )

        ratio = float(het.loc[name, "heterogeneity_ratio"])
        status = "Resolved" if robust else "Uncertainty\ndominated"
        ax.text(
            0.79,
            y0 + 0.70 * row_h,
            status,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=fs(4.25) if robust else gfs(4.25),
            color=GREEN if robust else MID_SLATE,
            fontweight="bold",
            linespacing=0.90,
        )
        ax.text(
            0.79,
            y0 + 0.10 * row_h,
            rf"$H_r=\widehat{{s}}_{{B,r}}^{{\,2}}\,/\,\overline{{s}}_{{W,r}}^{{\,2}}={ratio:.2f}$",
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=gfs(4.05),
            color=SLATE,
        )

    resolved_ratio = float(het.loc["D_betaN l_i", "heterogeneity_ratio"])
    unresolved_ratio = float(het.loc["D_kappa W_dia", "heterogeneity_ratio"])
    unresolved_tau2 = float(het.loc["D_kappa W_dia", "tau2_REML"])
    tau_text = (
        r"$\tau^2_{\rm REML}=0$"
        if np.isclose(unresolved_tau2, 0.0)
        else rf"$\tau^2_{{\rm REML}}={unresolved_tau2:.2g}$"
    )
    ax.text(
        0.01,
        0.082,
        r"Native-scale histogram + KDE; range: observed min–max; diamond: random-effects mean $\mu_{\rm REML}$.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=gfs(4.45),
        color=SLATE,
    )
    ax.text(
        0.01,
        0.027,
        rf"$D_{{\beta_N}}\ell_i$ is resolved ($H_r={resolved_ratio:.2f}$, $\tau^2_{{\rm REML}}>0$); "
        rf"$D_\kappa W_{{\rm dia}}$ is uncertainty-dominated ($H_r={unresolved_ratio:.2f}$, {tau_text}).",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=gfs(4.45),
        color=NAVY,
        linespacing=1.05,
    )


def _coord_family(c: str) -> str:
    return c.split("(", 1)[0]


def _short_signal(s: str) -> str:
    mapping = {
        "pcdiamag3": r"$W_{\rm dia}$",
        "ece21": "ece21",
        "cerqtit10": "cerTi10",
        "prmtan_neped": r"$n_{e,{\rm ped}}$",
        "cerqtit3": "cerTi3",
        "tinj": r"$t_{\rm inj}$",
        "ece20": "ece20",
        "bt": r"$B_t$",
        "ip": r"$I_p$",
        "fs03da": r"D$\alpha$03",
        "ece37": "ece37",
        "ece39": "ece39",
        "cerqtit6": "cerTi6",
        "pinj": r"$P_{\rm inj}$",
        "pinj_33r": r"$P_{33R}$",
        "fs04": r"D$\alpha$04",
        "cerqrott8": "cerV8",
    }
    return mapping.get(s, s)


def _short_coord(c: str) -> str:
    if c.startswith("ID(") and c.endswith(")"):
        return _short_signal(c[3:-1])
    if c.startswith("RATIO(") and c.endswith(")"):
        a, b = c[6:-1].split(",")
        return f"{_short_signal(a)} / {_short_signal(b)}"
    if c.startswith("RECIP(") and c.endswith(")"):
        return f"1 / {_short_signal(c[6:-1])}"
    if c.startswith("PROD(") and c.endswith(")"):
        a, b = c[5:-1].split(",")
        return f"{_short_signal(a)} × {_short_signal(b)}"
    return c


def _draw_panel_c(panel_ax: plt.Axes, matrix: pd.DataFrame) -> None:
    layout = PANEL_C_LAYOUT
    fs = lambda size: size * layout.font_scale
    gfs = lambda size: fs(size) * GRAY_TEXT_SCALE * LOWER_PANEL_GRAY_BOOST
    _panel_title(
        panel_ax,
        "c",
        "Recurrent Support Terms Across Folds",
        r"$q_{\mathrm{rec}}$",
        NAVY,
    )
    container = _panel_container(panel_ax, layout)
    container.set_axis_off()
    ax = container.inset_axes([0.00, 0.245, 1.00, 0.755])
    footer = container.inset_axes([0.00, 0.000, 1.00, 0.225])
    footer.set_axis_off()

    freq_all = matrix.sum(axis=0).sort_values(ascending=False)
    recurrent = freq_all[freq_all >= 2]
    ordered = list(recurrent.index)
    n_singletons = int((freq_all == 1).sum())
    n_ratios = sum(_coord_family(term) == "RATIO" for term in ordered)

    family_palette = {
        "ID": (BLUE_DARK, BLUE_LIGHT),
        "RATIO": (GREEN, GREEN_LIGHT),
        "RECIP": (LOSS, "#F4E6D9"),
        "PROD": ("#6C5A94", "#E7E0F1"),
    }
    support_x = [1.30, 2.05, 2.80, 3.55, 4.30, 5.05]
    rec_header_x = 6.00
    rec_bar_left = 5.58
    rec_bar_max = 0.34
    rec_count_x = 6.24

    ax.set_xlim(-2.25, 6.65)
    ax.set_ylim(len(ordered) - 0.5, -1.70)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[:].set_visible(False)

    ax.text(
        -2.05,
        -1.35,
        "Type",
        ha="left",
        va="center",
        fontsize=gfs(4.65),
        color=SLATE,
        fontweight="bold",
    )
    ax.text(
        0.55,
        -1.35,
        "Relational Term",
        ha="right",
        va="center",
        fontsize=gfs(4.65),
        color=SLATE,
        fontweight="bold",
    )
    ax.text(
        np.mean(support_x),
        -1.35,
        "Fold Support",
        ha="center",
        va="center",
        fontsize=gfs(4.65),
        color=SLATE,
        fontweight="bold",
    )
    ax.text(
        rec_header_x,
        -1.35,
        "Rec.",
        ha="center",
        va="center",
        fontsize=gfs(4.65),
        color=SLATE,
        fontweight="bold",
    )

    for k, xk in enumerate(support_x):
        ax.text(
            xk,
            -0.65,
            f"F{k + 1}",
            ha="center",
            va="center",
            fontsize=gfs(4.55),
            color=SLATE,
        )

    for i, term in enumerate(ordered):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=SOFT, alpha=0.55, zorder=0)
        family = _coord_family(term)
        edge, face = family_palette.get(family, (MID_SLATE, BLUE_LIGHT))

        ax.text(
            -2.05,
            i,
            family.lower(),
            ha="left",
            va="center",
            fontsize=fs(4.30) if family in family_palette else gfs(4.30),
            color=edge,
            fontweight="bold",
        )
        ax.text(
            0.55,
            i,
            _short_coord(term),
            ha="right",
            va="center",
            fontsize=fs(4.25),
            color=INK,
        )

        for k, xk in enumerate(support_x):
            _round_box(
                ax,
                xk,
                i,
                0.38,
                0.36,
                WHITE,
                GRID,
                lw=0.33,
                radius=0.04,
                z=1,
            )
            if int(matrix.loc[k, term]) == 1:
                _round_box(
                    ax,
                    xk,
                    i,
                    0.30,
                    0.28,
                    face,
                    edge,
                    lw=0.58,
                    radius=0.04,
                    z=2,
                )

        bar_w = rec_bar_max * int(recurrent[term]) / 6.0
        ax.add_patch(
            plt.Rectangle(
                (rec_bar_left, i - 0.14),
                bar_w,
                0.28,
                facecolor=edge,
                edgecolor="none",
                alpha=0.72,
                zorder=2,
                clip_on=False,
            )
        )
        ax.text(
            rec_count_x,
            i,
            str(int(recurrent[term])),
            ha="center",
            va="center",
            fontsize=fs(4.45) if int(recurrent[term]) >= 4 else gfs(4.45),
            color=INK if int(recurrent[term]) >= 4 else MID_SLATE,
            fontweight="bold",
        )

    legend_items = [
        ("Ratio", GREEN),
        ("Product", "#6C5A94"),
        ("Reciprocal", LOSS),
        ("Identity", BLUE_DARK),
    ]
    for x0, (label, color) in zip(
        (0.02, 0.26, 0.52, 0.78), legend_items, strict=True
    ):
        footer.scatter(
            [x0],
            [0.86],
            transform=footer.transAxes,
            s=22,
            marker="s",
            facecolor=color,
            edgecolor=color,
            linewidth=0.4,
            clip_on=False,
        )
        footer.text(
            x0 + 0.025,
            0.86,
            label,
            transform=footer.transAxes,
            ha="left",
            va="center",
            fontsize=gfs(4.35),
            color=SLATE,
        )

    footer.text(
        0.50,
        0.67,
        f"Rows show {len(ordered)} terms recurring in at least two of six 12-term supports\n"
        f"{n_singletons} singleton terms are omitted.",
        transform=footer.transAxes,
        ha="center",
        va="top",
        fontsize=gfs(4.40),
        color=SLATE,
        linespacing=1.05,
    )
    footer.text(
        0.5,
        0.30,
        f"Ratio constructions comprise {n_ratios} / {len(ordered)} recurrent terms. Ratio and reciprocal terms shown passed\n"
        "the frozen admissibility and range-support checks in every fold where selected.",
        transform=footer.transAxes,
        ha="center",
        va="top",
        fontsize=fs(5.5),
        color=NAVY,
        linespacing=1.08,
    )


def _draw_panel_d(panel_ax: plt.Axes, held: pd.DataFrame) -> None:
    layout = PANEL_D_LAYOUT
    fs = lambda size: size * layout.font_scale
    gfs = lambda size: fs(size) * GRAY_TEXT_SCALE * LOWER_PANEL_GRAY_BOOST
    _panel_title(
        panel_ax,
        "d",
        "Target-Cross-Fitted Density Reconstruction",
        r"$q_{\mathrm{rec}}$",
        NAVY,
    )
    container = _panel_container(panel_ax, layout)
    container.set_axis_off()

    x = held["B1_nrmse"].to_numpy(float)
    y = held["REL_nrmse"].to_numpy(float)
    era = held["era"].astype(str).to_numpy()
    earlier = era == "earlier"
    later = era == "later"

    mean_x, mean_y = float(np.mean(x)), float(np.mean(y))
    delta = y - x
    wins = int((delta < -0.01).sum())
    ties = int((np.abs(delta) <= 0.01).sum())
    losses = int((delta > 0.01).sum())
    early_delta = float(np.mean(y[earlier] - x[earlier]))
    late_delta = float(np.mean(y[later] - x[later]))

    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=WHITE,
            markeredgecolor=SLATE,
            markeredgewidth=0.65,
            markersize=4.0,
            label="Earlier",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=BLUE,
            markeredgecolor=NAVY,
            markeredgewidth=0.45,
            markersize=4.0,
            label="Later",
        ),
        Line2D(
            [0],
            [0],
            marker="*",
            linestyle="none",
            markerfacecolor=GREEN,
            markeredgecolor=INK,
            markeredgewidth=0.45,
            markersize=5.8,
            label="Mean",
        ),
    ]
    container.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.095, 0.995),
        ncol=3,
        frameon=False,
        fontsize=fs(4.55),
        handletextpad=0.35,
        columnspacing=0.85,
        borderaxespad=0.0,
    )
    container.text(
        0.985,
        0.995,
        f"mean NRMSE  {mean_y:.3f} vs {mean_x:.3f}\nW / T / L  {wins} / {ties} / {losses}",
        transform=container.transAxes,
        ha="right",
        va="top",
        fontsize=fs(4.85),
        color=NAVY,
        fontweight="bold",
        linespacing=1.12,
        bbox=dict(
            boxstyle="round,pad=0.24",
            fc=WHITE,
            ec=BLUE_LIGHT,
            lw=0.65,
            alpha=0.98,
        ),
    )

    ax = container.inset_axes([0.115, 0.265, 0.865, 0.605])
    hi = 1.0
    xx = np.linspace(0, hi, 300)
    ax.fill_between(xx, 0, xx, color=GREEN_PALE, alpha=0.75, lw=0, zorder=0)
    ax.fill_between(xx, xx, hi, color=LOSS_FACE, alpha=0.55, lw=0, zorder=0)
    ax.plot([0, hi], [0, hi], color="#AEB9C2", lw=0.85, zorder=1)
    ax.scatter(
        x[earlier],
        y[earlier],
        s=23,
        facecolor=WHITE,
        edgecolor=SLATE,
        linewidth=0.65,
        alpha=0.90,
        zorder=3,
    )
    ax.scatter(
        x[later],
        y[later],
        s=25,
        facecolor=BLUE,
        edgecolor=NAVY,
        linewidth=0.45,
        alpha=0.90,
        zorder=4,
    )
    ax.scatter(
        [mean_x],
        [mean_y],
        s=55,
        marker="*",
        facecolor=GREEN,
        edgecolor=INK,
        linewidth=0.5,
        zorder=6,
    )

    ax.set_xlim(0, 0.70)
    ax.set_ylim(0, 1.00)
    ax.set_xlabel("Persistence NRMSE", fontsize=fs(6.0), labelpad=2)
    ax.set_ylabel("Relational NRMSE", fontsize=fs(6.0), labelpad=2)
    ax.tick_params(labelsize=fs(5.25), length=2.5, width=0.55)
    ax.grid(True, color=GRID, lw=0.42, alpha=0.75)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#94A2AD")
    ax.text(
        0.96,
        0.055,
        "Relational lower error",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=fs(4.85),
        color=GREEN,
        fontweight="bold",
    )
    ax.text(
        0.04,
        0.955,
        "Persistence lower error",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=fs(4.75),
        color=LOSS,
    )

    container.text(
        0.125,
        0.905,
        f"Earlier mean Δ = {early_delta:+.4f}  ·  later mean Δ = {late_delta:+.4f}",
        transform=container.transAxes,
        ha="left",
        va="top",
        fontsize=gfs(4.35),
        color=SLATE,
    )
    container.text(
        0.05,
        0.130,
        "62 out-of-fold discharges · finite-object, target-cross-fitted qualification",
        transform=container.transAxes,
        ha="left",
        va="top",
        fontsize=gfs(5),
        color=NAVY,
        fontstyle="italic",
    )
    container.text(
        0.4,
        0.095,
        "not external validation",
        transform=container.transAxes,
        ha="left",
        va="top",
        fontsize=gfs(5),
        color=NAVY,
        fontstyle="italic",
    )


def _build_figure(
    coef: pd.DataFrame,
    cls: pd.DataFrame,
    het: pd.DataFrame,
    held: pd.DataFrame,
    matrix: pd.DataFrame,
) -> plt.Figure:
    """Construct the fixed-size figure from already validated frozen data."""
    fig = plt.figure(figsize=FIGURE_SIZE_IN, facecolor=WHITE)
    gs = fig.add_gridspec(
        2,
        2,
        left=0.050,
        right=0.950,
        bottom=0.025,
        top=0.883,
        wspace=0.14,
        hspace=0.24,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    fig.text(
        0.50,
        0.975,
        "DIII-D: Task-Conditioned Relational Discovery",
        ha="center",
        va="top",
        fontsize=11.4,
        color=INK,
        fontweight="bold",
    )
    fig.text(
        0.50,
        0.945,
        r"One 62-discharge observational record $\;\rightarrow\;$ Distinct qualified organizations under $q_{\rm desc}$ and $q_{\rm rec}$",
        ha="center",
        va="top",
        fontsize=GLOBAL_SUBTITLE_FONTSIZE,
        color=SLATE,
        fontstyle="italic",
    )

    _draw_panel_a(ax_a, coef)
    _draw_panel_b(ax_b, coef, cls, het)
    _draw_panel_c(ax_c, matrix)
    _draw_panel_d(ax_d, held)

    pos_a = ax_a.get_position()
    pos_b = ax_b.get_position()
    pos_c = ax_c.get_position()
    divider_x = 0.5 * (pos_a.x1 + pos_b.x0)
    divider_y = 0.5 * (pos_c.y1 + pos_a.y0)
    fig.lines.append(
        mpl.lines.Line2D(
            [divider_x, divider_x],
            [0.020, 0.893],
            transform=fig.transFigure,
            color=RULE,
            lw=0.7,
        )
    )
    fig.lines.append(
        mpl.lines.Line2D(
            [0.055, 0.945],
            [divider_y, divider_y],
            transform=fig.transFigure,
            color=RULE,
            lw=0.7,
        )
    )
    return fig


def _export_figure(
    fig: plt.Figure,
    out_dir: Path,
    out_stem: str,
) -> tuple[Path, Path, Path]:
    """Export exact-size raster and vector versions without tight-bbox drift."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = tuple(out_dir / f"{out_stem}.{extension}" for extension in ("png", "pdf", "svg"))
    for path in paths:
        fig.savefig(
            path,
            dpi=EXPORT_DPI,
            facecolor=WHITE,
            transparent=False,
            bbox_inches=None,
            pad_inches=0,
        )
    return paths


def make_figure(
    data_dir: Path = DATA_DIR,
    out_dir: Path | None = None,
    out_stem: str = "d3d_task_conditioned_4panel_v5",
):
    data_dir = Path(data_dir).expanduser().resolve()
    out_dir = SCRIPT_DIR if out_dir is None else Path(out_dir).expanduser().resolve()
    _preflight(data_dir)
    coef, cls, het, held, folds, matrix = _load(data_dir)
    _assert_invariants(coef, cls, held, folds, matrix)
    _verify_matrix(data_dir, matrix)

    with mpl.rc_context(_style()):
        fig = _build_figure(coef, cls, het, held, matrix)
        paths = _export_figure(fig, out_dir, out_stem)
        plt.close(fig)
    return paths


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Render the DIII-D task-conditioned four-panel figure from "
        "the frozen figure data."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"directory holding the frozen inputs (default: {DATA_DIR})",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=SCRIPT_DIR,
        help=f"directory to write PNG/PDF/SVG (default: {SCRIPT_DIR})",
    )
    parser.add_argument(
        "--out-stem",
        default="d3d_task_conditioned_4panel_v5",
        help="output filename stem (default: %(default)s)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    try:
        output_paths = make_figure(args.data_dir, args.out_dir, args.out_stem)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        raise
    for output_path in output_paths:
        print(output_path)
