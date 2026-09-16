
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath
from scipy.stats import gaussian_kde

# --------------------------------------------------------------------------
# Local configuration. The frozen figure data live beside this script; both
# locations can be overridden from the command line (see __main__).
# --------------------------------------------------------------------------
DATA_DIR = Path(r"D:\SIR_paper\DIIID_example\fig6data")
SCRIPT_DIR = Path(__file__).resolve().parent

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
MID_SLATE = "#82909C"
GRID = "#DDE4E9"
RULE = "#E2E7EB"
WHITE = "#FFFFFF"
SOFT = "#F7F9FB"
LOSS = "#B0845A"
LOSS_FACE = "#F7EFE8"
UNUSED = "#B0B8BF"
UNUSED_FACE = "#FAFBFC"

# Panel a diagram center-of-mass, in axes units (the panel is 0–1).
# The title stays pinned. Negative x = left (off the vertical rule);
# negative y = down (toward the mid-figure divider).
PANEL_A_SHIFT = (-0.045, -0.079)

# Scale every panel-a fontsize (column headers, nodes, pills, form, title).
PANEL_A_FONT_SCALE = 1.2

# Cohort-Mean box center of mass (x, y), then (width, height).
# Negative x = left; negative y = down. Line gap is the y-step
# between the five text rows inside the box.
PANEL_A_FORM_BOX_CENTER = (0.665, 0.077)
PANEL_A_FORM_BOX_SIZE = (0.73, 0.20)
PANEL_A_FORM_LINE_GAP = 0.040

PRIM_MATH = {
    "pcdiamag3": r"$W_{\mathrm{dia}}$",
    "betan": r"$\beta_N$",
    "kappa": r"$\kappa$",
    "q95": r"$q_{95}$",
    "li": r"$\ell_i$",
}

COORD_MATH = {
    "D_kappa W_dia": r"$D_{\kappa}W_{\mathrm{dia}}$",
    "D_betaN W_dia": r"$D_{\beta_N}W_{\mathrm{dia}}$",
    "D_betaN kappa": r"$D_{\beta_N}\kappa$",
    "D_betaN l_i": r"$D_{\beta_N}\ell_i$",
    "q95 / kappa": r"$q_{95}/\kappa$",
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

def _style():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Tinos", "Nimbus Roman No9 L", "Liberation Serif", "DejaVu Serif"],
        # Math set in Times New Roman as well, so equations match the body text.
        # STIX (Times-metric-compatible) covers any glyph Times lacks.
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
    })

def _round_box(ax, x, y, w, h, fc, ec, lw=0.8, radius=0.012, ls="-", z=3):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls,
        zorder=z, clip_on=False,
    )
    ax.add_patch(patch)
    return patch

def _node(ax, x, y, w, h, text, *, fc=WHITE, ec=RULE, lw=0.8, ls="-",
          fontsize=6.2, color=INK, weight="normal", z=4):
    _round_box(ax, x, y, w, h, fc, ec, lw=lw, ls=ls, z=z)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=color, fontweight=weight, zorder=z + 1, clip_on=False)
    return dict(x=x, y=y, w=w, h=h)

def _curve(ax, a, b, *, color="#CCD4DB", lw=0.5, alpha=0.9, bend=0.04, z=1):
    x1 = a["x"] + a["w"] / 2
    y1 = a["y"]
    x2 = b["x"] - b["w"] / 2
    y2 = b["y"]
    dx = x2 - x1
    verts = [(x1, y1), (x1 + dx * 0.40, y1 + bend),
             (x2 - dx * 0.40, y2 - bend), (x2, y2)]
    path = MplPath(verts, [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4])
    ax.add_patch(PathPatch(path, facecolor="none", edgecolor=color, lw=lw,
                           alpha=alpha, capstyle="round", zorder=z, clip_on=False))

def _panel_title(ax, letter: str, title: str, task: str, color: str,
                 font_scale: float = 1.0) -> None:
    ax.text(0.00, 1.075, letter, transform=ax.transAxes, ha="left", va="top",
            fontsize=10.0 * font_scale, fontweight="bold", color=INK, clip_on=False)
    ax.text(0.055, 1.075, title, transform=ax.transAxes, ha="left", va="top",
            fontsize=8.7 * font_scale, fontweight="bold", color=color, clip_on=False)
    ax.text(0.055, 1.017, task, transform=ax.transAxes, ha="left", va="top",
            fontsize=7.1 * font_scale, color=color, clip_on=False)

def _preflight(data_dir: Path) -> None:
    """Verify every required input exists before any plotting begins."""
    if not data_dir.is_dir():
        raise SystemExit(f"Data directory not found: {data_dir}")
    missing = [name for name in REQUIRED_FILES if not (data_dir / name).is_file()]
    if missing:
        lines = [f"Missing {len(missing)} of {len(REQUIRED_FILES)} required input "
                 f"files in {data_dir}:"]
        lines += [f"  - {name}" for name in missing]
        raise SystemExit("\n".join(lines))
    print(f"Preflight OK: {len(REQUIRED_FILES)} required input files found in {data_dir}")


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
        for c in fold["coordinates"]:
            matrix.loc[k, c] = 1
    return coef, cls, het, held, folds, matrix

def _assert_invariants(coef, cls, held, folds, matrix):
    if len(coef) != 62:
        raise RuntimeError(f"Expected 62 descriptive coefficient rows, found {len(coef)}")
    if len(cls) != 7:
        raise RuntimeError(f"Expected 7 coefficient classifications, found {len(cls)}")
    if len(held) != 62:
        raise RuntimeError(f"Expected 62 held-out discharge rows, found {len(held)}")
    if matrix.shape != (6, 35):
        raise RuntimeError(f"Expected 6 x 35 support matrix, found {matrix.shape}")

def _draw_panel_a(ax, coef: pd.DataFrame) -> None:
    def fs(size: float) -> float:
        return size * PANEL_A_FONT_SCALE

    def bs(size: float) -> float:
        return size * PANEL_A_FONT_SCALE

    _panel_title(ax, "a", "Descriptive Relational Organization", r"$q_{\mathrm{desc}}$",
                 GREEN, font_scale=PANEL_A_FONT_SCALE)
    dx, dy = PANEL_A_SHIFT
    ax.set_xlim(0.0 - dx, 1.0 - dx)
    ax.set_ylim(0.0 - dy, 1.0 - dy)
    ax.axis("off")

    # Raise the diagram toward q_desc so the larger boxes have room below.
    y0 = 0.055

    ax.text(0.12, 0.925 + y0, "Observed", ha="center", va="top", fontsize=fs(6.8),
            color=SLATE, fontweight="bold")
    ax.text(0.53, 0.925 + y0, "Selected Coordinates", ha="center", va="top", fontsize=fs(6.8),
            color=SLATE, fontweight="bold")
    ax.text(0.925, 0.925 + y0, "Response", ha="center", va="top", fontsize=fs(6.8),
            color=SLATE, fontweight="bold")

    selected_engines = ["pcdiamag3", "betan", "kappa", "q95", "li"]
    selected_y = [0.80 + y0, 0.66 + y0, 0.52 + y0, 0.38 + y0, 0.24 + y0]
    prim = {}
    for engine, y in zip(selected_engines, selected_y):
        prim[engine] = _node(ax, 0.12, y, bs(0.185), bs(0.068), PRIM_MATH[engine],
                             fc=WHITE, ec="#9FB0BE", lw=0.7, fontsize=fs(7.5))

    unused_x, unused_y = 0.12, 0.072
    unused_w, unused_h = bs(0.30), bs(0.145)
    _round_box(ax, unused_x, unused_y, unused_w, unused_h, UNUSED_FACE, "#D1D8DE",
               lw=0.6, ls=(0, (2, 1.5)))
    ax.text(unused_x, unused_y + 0.22 * unused_h, "Available,\nUnselected",
            ha="center", va="center", fontsize=fs(5.6), color=UNUSED, fontweight="bold",
            linespacing=1.15)
    ax.text(unused_x, unused_y - 0.28 * unused_h, r"$P_{\mathrm{NBI}}\quad n_e\quad I_p$",
            ha="center", va="center", fontsize=fs(6.3), color=UNUSED)

    def pill(y, text, width=0.25):
        _round_box(ax, 0.53, y, bs(width), bs(0.040), GREEN_WASH, GREEN_MID, lw=0.55, radius=0.008, z=5)
        ax.text(0.53, y, text, ha="center", va="center", fontsize=fs(5.6),
                color=GREEN, fontweight="bold", zorder=6)

    pill(0.835 + y0, "Rates", 0.15)
    c_dotb = _node(ax, 0.45, 0.770 + y0, bs(0.20), bs(0.058), COORD_MATH["dot beta_N"], fc=GREEN_PALE, ec=GREEN_LIGHT, fontsize=fs(6.9))
    c_dotk = _node(ax, 0.61, 0.770 + y0, bs(0.20), bs(0.058), COORD_MATH["dot kappa"], fc=GREEN_PALE, ec=GREEN_LIGHT, fontsize=fs(6.9))

    pill(0.665 + y0, "Trajectory-Relational", 0.30)
    c_dbk = _node(ax, 0.45, 0.600 + y0, bs(0.21), bs(0.058), COORD_MATH["D_betaN kappa"], fc=WHITE, ec=GREEN_LIGHT, fontsize=fs(6.9))
    c_dbl = _node(ax, 0.61, 0.600 + y0, bs(0.21), bs(0.058), COORD_MATH["D_betaN l_i"], fc=WHITE, ec=GREEN_LIGHT, fontsize=fs(6.9))

    pill(0.495 + y0, "Target-Containing", 0.26)
    c_dkw = _node(ax, 0.45, 0.430 + y0, bs(0.22), bs(0.058), COORD_MATH["D_kappa W_dia"], fc="#FFFCF5", ec=GREEN, fontsize=fs(6.9), ls=(0, (2.4, 1.3)))
    c_dbw = _node(ax, 0.61, 0.430 + y0, bs(0.22), bs(0.058), COORD_MATH["D_betaN W_dia"], fc="#FFFCF5", ec=GREEN, fontsize=fs(6.9), ls=(0, (2.4, 1.3)))

    pill(0.325 + y0, "Algebraic", 0.18)
    c_alg = _node(ax, 0.53, 0.260 + y0, bs(0.21), bs(0.058), COORD_MATH["q95 / kappa"], fc=WHITE, ec=GREEN_LIGHT, fontsize=fs(6.9))

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

    target_h = bs(0.095)
    target = _node(ax, 0.925, 0.545 + y0, bs(0.175), target_h, r"$\dot W_{\mathrm{dia}}$",
                   fc=GREEN_PALE, ec=GREEN, lw=1.0, fontsize=fs(8.6), weight="bold", z=5)
    ax.text(0.925, 0.545 + y0 - 0.50 * target_h - 0.028, "Shared Support",
            ha="center", va="center", fontsize=fs(5.8), color=GREEN, fontweight="bold")
    for node, _ in coords.values():
        _curve(ax, node, target, color="#B7C6BE", lw=0.5, bend=0.0, z=2)

    means = {name: float(coef[col].mean()) for name, col in COEF_COLS.items()}
    form_x, form_y = PANEL_A_FORM_BOX_CENTER
    form_w, form_h = PANEL_A_FORM_BOX_SIZE
    gap = PANEL_A_FORM_LINE_GAP
    form_ys = [form_y + (2 - i) * gap for i in range(5)]
    _round_box(ax, form_x, form_y, form_w, form_h, "#FBFDFC", GREEN_LIGHT, lw=0.65, radius=0.009, z=4)
    ax.text(form_x, form_ys[0], "Cohort-Mean Descriptive Form", ha="center", va="center",
            fontsize=fs(6.0), color=GREEN, fontweight="bold", zorder=5)
    ax.text(form_x, form_ys[1],
            rf"$\dot W_{{\rm dia}}={means['D_kappa W_dia']:.3f}D_\kappa W_{{\rm dia}}"
            rf"+{means['D_betaN W_dia']:.3f}D_{{\beta_N}}W_{{\rm dia}}$",
            ha="center", va="center", fontsize=fs(5.25), color=INK, zorder=5)
    ax.text(form_x, form_ys[2],
            rf"${means['D_betaN kappa']:+.3f}D_{{\beta_N}}\kappa"
            rf"{means['D_betaN l_i']:+.4f}D_{{\beta_N}}\ell_i$",
            ha="center", va="center", fontsize=fs(5.25), color=INK, zorder=5)
    ax.text(form_x, form_ys[3],
            rf"${means['q95 / kappa']:+.4f}q_{{95}}/\kappa"
            rf"{means['dot beta_N']:+.4f}\dot\beta_N"
            rf"{means['dot kappa']:+.3f}\dot\kappa+\varepsilon$",
            ha="center", va="center", fontsize=fs(5.25), color=INK, zorder=5)
    ax.text(form_x, form_ys[4], "62 discharges · shared support · discharge-specific coefficients",
            ha="center", va="center", fontsize=fs(5.2), color=SLATE, fontstyle="italic", zorder=5)

def _draw_panel_b(ax, coef: pd.DataFrame, cls: pd.DataFrame, het: pd.DataFrame) -> None:
    _panel_title(ax, "b", "Coefficient Heterogeneity Audit", r"$q_{\mathrm{desc}}$", GREEN)
    ax.set_axis_off()

    # Order chosen to separate robustly resolved coefficients from uncertainty-dominated ones.
    order = ["dot kappa", "dot beta_N", "D_betaN kappa", "D_betaN W_dia",
             "D_betaN l_i", "D_kappa W_dia", "q95 / kappa"]

    cls = cls.set_index("display_name")
    het = het.set_index("display_name")

    ax.text(0.24, 0.99, "62 discharge-specific coefficients", transform=ax.transAxes,
            ha="left", va="top", fontsize=5.2, color=SLATE)
    ax.text(0.805, 1.05, "Decision rule:\n Resolved if between-discharge\nvariation persists beyond\nwithin-discharge uncertainty",
            transform=ax.transAxes, ha="center", va="top", fontsize=4.55, color=GREEN, linespacing=1.03)

    left = 0.24
    width = 0.54
    top = 0.91
    row_h = 0.097
    gap = 0.015

    for i, name in enumerate(order):
        y0 = top - (i + 1) * row_h - i * gap
        iax = ax.inset_axes([left, y0, width, row_h])

        vals = coef[COEF_COLS[name]].to_numpy(float)
        robust = cls.loc[name, "corrected_status"] == "ROBUSTLY_RESOLVED"
        face = GREEN_LIGHT if robust else BLUE_LIGHT
        edge = GREEN if robust else MID_SLATE

        counts, _, _ = iax.hist(vals, bins=9, density=True, color=face,
                                edgecolor="white", linewidth=0.35, alpha=0.95)

        span = np.ptp(vals)
        if span == 0:
            span = 1.0
        xs = np.linspace(vals.min() - 0.10 * span, vals.max() + 0.10 * span, 240)
        try:
            ys = gaussian_kde(vals, bw_method=0.2)(xs)
            iax.plot(xs, ys, color=edge, lw=1.0, zorder=3)
            ymax = max(float(np.max(counts)) if len(counts) else 0.0, float(np.max(ys))) * 1.18
        except Exception:
            ymax = (float(np.max(counts)) if len(counts) else 1.0) * 1.18

        if ymax <= 0:
            ymax = 1.0
        iax.set_ylim(0, ymax)

        mu = float(het.loc[name, "mu_REML"])
        iax.scatter([mu], [0.84 * ymax], s=18, marker="D",
                    facecolor=WHITE,
                    edgecolor=INK if robust else MID_SLATE,
                    linewidth=0.65, zorder=4)

        iax.axvline(0, color=RULE, lw=0.75, zorder=1)
        iax.set_yticks([])
        iax.tick_params(axis="x", labelsize=4.2, length=2.0, pad=1)
        iax.grid(axis="x", color=GRID, lw=0.40, alpha=0.7)
        if i < len(order) - 1:
            iax.set_xticklabels([])

        for side in ["top", "right", "left"]:
            iax.spines[side].set_visible(False)
        iax.spines["bottom"].set_color("#AAB6BE")

        ax.text(0.02, y0 + 0.50 * row_h, COORD_MATH[name], transform=ax.transAxes,
                ha="left", va="center", fontsize=5.4, color=INK)

        ratio = float(het.loc[name, "heterogeneity_ratio"])
        tau2 = float(het.loc[name, "tau2_REML"])
        status = "Resolved" if robust else "Uncertainty\ndominated"
        ax.text(0.80, y0 + 0.62 * row_h, status, transform=ax.transAxes,
                ha="left", va="center", fontsize=4.55,
                color=GREEN if robust else MID_SLATE,
                fontweight="bold", linespacing=0.90)
        ax.text(0.80, y0 + 0.18 * row_h,
                rf"$H_r=\widehat{{s}}_{{B,r}}^{{\,2}}\,/\,\overline{{s}}_{{W,r}}^{{\,2}}={ratio:.2f}$",
                transform=ax.transAxes, ha="left", va="center",
                fontsize=4.5, color=SLATE)

    ax.text(0.02, -0.,
            r"Histogram + KDE on native scales; diamond: random-effects mean $\mu_{\rm REML}$.",
            transform=ax.transAxes, ha="left", va="top", fontsize=4.65, color=SLATE)
    ax.text(0.02, -0.05,
            r"$D_{\beta_N}\ell_i$ is resolved because its between/within ratio is 3.75 and $\tau^2_{\rm REML}>0$;"
            "\n"
            r"$D_{\kappa}W_{\rm dia}$ is not, because its ratio is 0.18 and the REML estimate collapses to $\tau^2_{\rm REML}=0$.",
            transform=ax.transAxes, ha="left", va="top", fontsize=4.5, color=NAVY, linespacing=1.0)

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
        inner = c[3:-1]
        return _short_signal(inner)
    if c.startswith("RATIO(") and c.endswith(")"):
        a, b = c[6:-1].split(",")
        return f"{_short_signal(a)} / {_short_signal(b)}"
    if c.startswith("RECIP(") and c.endswith(")"):
        inner = c[6:-1]
        return f"1 / {_short_signal(inner)}"
    if c.startswith("PROD(") and c.endswith(")"):
        a, b = c[5:-1].split(",")
        return f"{_short_signal(a)} × {_short_signal(b)}"
    return c

def _draw_panel_c(ax, matrix: pd.DataFrame) -> None:
    _panel_title(ax, "c", "Recurrent Support Terms Across Folds", r"$q_{\mathrm{rec}}$", NAVY)
    freq_all = matrix.sum(axis=0).sort_values(ascending=False)
    recurrent = freq_all[freq_all >= 2]
    ordered = list(recurrent.index)
    n_singletons = int((freq_all == 1).sum())

    family_palette = {
        "ID": (BLUE_DARK, BLUE_LIGHT),
        "RATIO": (GREEN, GREEN_LIGHT),
        "RECIP": (LOSS, "#F4E6D9"),
        "PROD": ("#6C5A94", "#E7E0F1"),
    }
    support_x = [1.35, 2.20, 3.05, 3.90, 4.75, 5.60]
    rec_x = 6.55

    ax.set_xlim(-2.45, 7.15)
    ax.set_ylim(len(ordered) - 0.5, -1.85)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[:].set_visible(False)

    # headers lowered to avoid overlap with the panel subtitle.
    ax.text(-2.05, -1.45, "Type", ha="left", va="center", fontsize=4.75,
            color=SLATE, fontweight="bold")
    ax.text(0.55, -1.45, "Relational Term", ha="right", va="center", fontsize=4.75,
            color=SLATE, fontweight="bold")
    ax.text(np.mean(support_x), -1.45, "Fold Support", ha="center", va="center", fontsize=4.75,
            color=SLATE, fontweight="bold")
    ax.text(rec_x, -1.45, "Rec.", ha="center", va="center", fontsize=4.75,
            color=SLATE, fontweight="bold")

    for k, xk in enumerate(support_x):
        ax.text(xk, -0.75, f"F{k+1}", ha="center", va="center", fontsize=4.7, color=SLATE)

    for i, term in enumerate(ordered):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=SOFT, alpha=0.55, zorder=0)
        fam = _coord_family(term)
        edge, face = family_palette.get(fam, (MID_SLATE, BLUE_LIGHT))

        ax.text(-2.05, i, fam.lower(), ha="left", va="center", fontsize=4.40,
                color=edge, fontweight="bold")
        ax.text(0.55, i, _short_coord(term), ha="right", va="center",
                fontsize=4.35, color=INK)

        for k, xk in enumerate(support_x):
            _round_box(ax, xk, i, 0.42, 0.42, WHITE, GRID, lw=0.33, radius=0.04, z=1)
            if int(matrix.loc[k, term]) == 1:
                _round_box(ax, xk, i, 0.34, 0.34, face, edge, lw=0.58, radius=0.04, z=2)

        bar_w = 0.50 * int(recurrent[term]) / 6.0
        ax.add_patch(plt.Rectangle((rec_x - 0.42, i - 0.15), bar_w, 0.30,
                                   facecolor=edge, edgecolor='none', alpha=0.72, zorder=2, clip_on=False))
        ax.text(rec_x, i, str(int(recurrent[term])), ha="center", va="center",
                fontsize=4.55, color=INK if int(recurrent[term]) >= 4 else MID_SLATE,
                fontweight="bold")

    legend_items = [("Ratio", GREEN), ("Product", "#6C5A94"), ("Reciprocal", LOSS), ("Identity", BLUE_DARK)]
    x0 = 0.02
    y0 = -0.14
    for j, (label, color) in enumerate(legend_items):
        xx = x0 + j * 0.20
        ax.scatter([xx], [y0], transform=ax.transAxes, s=28, marker='s', facecolor=color,
                   edgecolor=color, linewidth=0.4, clip_on=False)
        ax.text(xx + 0.02, y0, label, transform=ax.transAxes, ha='left', va='center',
                fontsize=4.45, color=SLATE, clip_on=False)

    ax.text(0.00, -0.23,
            f"Rows show the 15 terms recurring in at least two of the six 12-term supports; {n_singletons} singleton terms are omitted.",
            transform=ax.transAxes, ha="left", va="top", fontsize=4.55, color=SLATE)
    ax.text(0.00, -0.31,
            "Ratio constructions dominate the recurrent set (8 / 15). All ratio and reciprocal terms shown here passed the frozen admissibility and range-support checks in the folds where they were selected.",
            transform=ax.transAxes, ha="left", va="top", fontsize=4.35, color=NAVY, linespacing=1.05)

def _draw_panel_d(ax, held: pd.DataFrame) -> None:
    _panel_title(ax, "d", "Target-Cross-Fitted Density Reconstruction", r"$q_{\mathrm{rec}}$", NAVY)
    x = held["B1_nrmse"].to_numpy(float)
    y = held["REL_nrmse"].to_numpy(float)
    era = held["era"].astype(str).to_numpy()

    hi = 1.0
    xx = np.linspace(0, hi, 300)
    ax.fill_between(xx, 0, xx, color=GREEN_PALE, alpha=0.75, lw=0, zorder=0)
    ax.fill_between(xx, xx, hi, color=LOSS_FACE, alpha=0.55, lw=0, zorder=0)
    ax.plot([0, hi], [0, hi], color="#AEB9C2", lw=0.85, zorder=1)

    earlier = era == "earlier"
    later = era == "later"
    ax.scatter(x[earlier], y[earlier], s=23, facecolor=WHITE, edgecolor=SLATE,
               linewidth=0.65, alpha=0.90, zorder=3)
    ax.scatter(x[later], y[later], s=25, facecolor=BLUE, edgecolor=NAVY,
               linewidth=0.45, alpha=0.90, zorder=4)

    mean_x, mean_y = float(np.mean(x)), float(np.mean(y))
    ax.scatter([mean_x], [mean_y], s=55, marker="*", facecolor=GREEN,
               edgecolor=INK, linewidth=0.5, zorder=6)

    delta = y - x
    wins = int((delta < -0.01).sum())
    ties = int((np.abs(delta) <= 0.01).sum())
    losses = int((delta > 0.01).sum())
    early_delta = float((held.loc[held.era == "earlier", "REL_nrmse"] - held.loc[held.era == "earlier", "B1_nrmse"]).mean())
    late_delta = float((held.loc[held.era == "later", "REL_nrmse"] - held.loc[held.era == "later", "B1_nrmse"]).mean())

    ax.set_xlim(0, 0.70)
    ax.set_ylim(0, 1.00)
    ax.set_xlabel("Persistence NRMSE", fontsize=6.1, labelpad=2)
    ax.set_ylabel("Relational NRMSE", fontsize=6.1, labelpad=2)
    ax.tick_params(labelsize=5.5, length=2.5)
    ax.grid(True, color=GRID, lw=0.42, alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#94A2AD")
    ax.text(0.96, 0.055, "Relational lower error", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=5.1, color=GREEN, fontweight="bold")
    ax.text(0.04, 0.955, "Persistence lower error", transform=ax.transAxes,
            ha="left", va="top", fontsize=5.0, color=LOSS)

    summary = (f"mean NRMSE  {mean_y:.3f} vs {mean_x:.3f}\n"
               f"W / T / L  {wins} / {ties} / {losses}")
    ax.text(0.97, 0.71, summary, transform=ax.transAxes, ha="right", va="top",
            fontsize=5.7, color=NAVY, fontweight="bold", linespacing=1.25,
            bbox=dict(boxstyle="round,pad=0.28", fc=WHITE, ec=BLUE_LIGHT, lw=0.65, alpha=0.96))
    ax.text(0.03, -0.20,
            f"earlier mean Δ = {early_delta:+.4f}  ·  later mean Δ = {late_delta:+.4f}  ·  62 out-of-fold discharges",
            transform=ax.transAxes, ha="left", va="top", fontsize=4.8, color=SLATE)
    ax.text(0.03, -0.26, "finite-object, target-cross-fitted qualification; not external validation",
            transform=ax.transAxes, ha="left", va="top", fontsize=4.7, color=NAVY, fontstyle="italic")

def make_figure(data_dir: Path = DATA_DIR, out_dir: Path | None = None,
                out_stem: str = "d3d_task_conditioned_4panel_v5"):
    data_dir = Path(data_dir)
    out_dir = SCRIPT_DIR if out_dir is None else Path(out_dir)
    _preflight(data_dir)
    _style()
    coef, cls, het, held, folds, matrix = _load(data_dir)
    _assert_invariants(coef, cls, held, folds, matrix)
    _verify_matrix(data_dir, matrix)

    fig = plt.figure(figsize=(7.15, 6.90), dpi=180, facecolor=WHITE)
    gs = fig.add_gridspec(2, 2, left=0.075, right=0.965, bottom=0.095, top=0.905,
                          wspace=0.30, hspace=0.44)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    # Close unused whitespace so panel a sits against the vertical rule.
    pos_a = ax_a.get_position()
    ax_a.set_position([pos_a.x0, pos_a.y0, 0.497 - pos_a.x0, pos_a.height])

    fig.text(0.50, 0.975, "DIII-D: Task-Conditioned Relational Discovery",
             ha="center", va="top", fontsize=11.4, color=INK, fontweight="bold")
    fig.text(0.50, 0.945,
             r"One 62-discharge observational record $\;\rightarrow\;$ Distinct qualified organizations under $q_{\rm desc}$ and $q_{\rm rec}$",
             ha="center", va="top", fontsize=6.5, color=SLATE, fontstyle="italic")

    _draw_panel_a(ax_a, coef)
    _draw_panel_b(ax_b, coef, cls, het)
    _draw_panel_c(ax_c, matrix)
    _draw_panel_d(ax_d, held)

    fig.lines.append(mpl.lines.Line2D([0.50, 0.50], [0.075, 0.91], transform=fig.transFigure, color=RULE, lw=0.7))
    fig.lines.append(mpl.lines.Line2D([0.065, 0.965], [0.505, 0.505], transform=fig.transFigure, color=RULE, lw=0.7))

    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{out_stem}.png"
    pdf = out_dir / f"{out_stem}.pdf"
    svg = out_dir / f"{out_stem}.svg"
    fig.savefig(png, dpi=400, facecolor=WHITE, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(pdf, facecolor=WHITE, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(svg, facecolor=WHITE, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    return png, pdf, svg

def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Render the DIII-D task-conditioned four-panel figure from "
                    "the frozen figure data.")
    p.add_argument("--data-dir", type=Path, default=DATA_DIR,
                   help=f"directory holding the frozen inputs (default: {DATA_DIR})")
    p.add_argument("--out-dir", type=Path, default=SCRIPT_DIR,
                   help=f"directory to write PNG/PDF/SVG (default: {SCRIPT_DIR})")
    p.add_argument("--out-stem", default="d3d_task_conditioned_4panel_v5",
                   help="output filename stem (default: %(default)s)")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    try:
        paths = make_figure(args.data_dir, args.out_dir, args.out_stem)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        raise
    for p in paths:
        print(p)