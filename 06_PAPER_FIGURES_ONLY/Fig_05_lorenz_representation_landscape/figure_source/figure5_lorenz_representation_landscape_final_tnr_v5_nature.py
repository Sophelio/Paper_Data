"""Nature-ready Lorenz representation landscape (manuscript Figure 4, v5).

The ``figure5_*`` working stem is retained for continuity with the frozen v4
artwork, although this artwork is Figure 4 in the current manuscript.  All
scientific values are read from the frozen ``figure_source_data`` package
(originally ``fig5data``) in the figure folder.  The script
never writes to that package and never modifies the v4 script or artwork.

Evidence encoded
----------------
a  Fixed-cubic containment using archived exact analytic Lorenz-RHS targets.
b  Seventeen canonical candidates evaluated by grouped CV on development data.
c  Protected clean confirmation: all 24 trajectory-level observations on common
   support, with arithmetic means and 95% trajectory-bootstrap intervals.
d  Dense augmentation noise sweep on common support.  Bands are pointwise 95%
   trajectory-cluster bootstrap intervals (20,000 resamples, PCG64 seed 0).
   Every selected trajectory contributes all three noise-replicate rows.

Outputs are PNG, PDF and SVG on an exact 183 x 150 mm canvas.  No tight bounding
box is used, so the delivered physical dimensions are independent of content.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

if os.name == "nt":
    os.environ.setdefault("MIKTEX_UNATTENDED", "1")
    os.environ.setdefault("MIKTEX_AUTOINSTALL", "1")
    _miktex_bin = Path.home() / r"AppData\Local\Programs\MiKTeX\miktex\bin\x64"
    if _miktex_bin.is_dir():
        os.environ["PATH"] = str(_miktex_bin) + os.pathsep + os.environ.get("PATH", "")

import matplotlib as mpl

# Use a non-interactive backend so macOS Retina display scaling cannot round the
# publication canvas to screen-friendly 0.1-inch increments.
mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


HERE: Final = Path(__file__).resolve().parent
# Defaults resolve inside the figure folder: frozen inputs in figure_source_data/,
# outputs next to figure_source/.
DEFAULT_DATA: Final = HERE.parent / "figure_source_data"
DEFAULT_OUT: Final = HERE.parent
STEM: Final = "figure5_lorenz_representation_landscape_final_tnr_v5_nature"

WIDTH_MM: Final = 183.0
HEIGHT_MM: Final = 150.0
MM_PER_INCH: Final = 25.4

# Multiply every type size in this figure. 1 is the manuscript original.
# A new value misses Matplotlib's LaTeX cache, so the first run at that
# scale recompiles every label (several minutes).
Font_scaling = 1.2


def _fs(pt: float) -> float:
    return pt * Font_scaling


# Figure-fraction gap between stacked panel-title lines.
TITLE_LINE_SPACING = 0.028


# Pin the 10 pt Latin Modern design at every size (SIR style spec, section 7A).
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
BOOTSTRAP_RESAMPLES: Final = 20_000
BOOTSTRAP_SEED: Final = 0

REPRESENTATIONS: Final = ("C0_poly2", "C_compact", "C_all")
REP_LABELS: Final = {
    "C0_poly2": "Quadratic",
    "C_compact": "Compact",
    "C_all": r"$C_{\mathrm{all}}$",
}
# Darkened Okabe-Ito-derived colors retain print contrast on white.  Marker
# shapes redundantly encode representation, so color is never the sole cue.
COLORS: Final = {
    "C0_poly2": "#A94700",
    "C_compact": "#007252",
    "C_all": "#005A91",
}
MARKERS: Final = {"C0_poly2": "s", "C_compact": "D", "C_all": "o"}
INK: Final = "#202124"
MID: Final = "#5F6368"
LIGHT: Final = "#A8ADB4"
RULE: Final = "#D9DDE2"
PALE_BLUE: Final = "#EAF2F8"

STYLE: Final = {
    "figure.dpi": 150,
    "savefig.dpi": 600,
    "savefig.bbox": None,
    "savefig.pad_inches": 0.0,
    "savefig.facecolor": "white",
    "savefig.transparent": False,
    # Latin Modern through LaTeX, matching the manuscript typeface.
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
    "font.size": _fs(6.9),
    "axes.labelsize": _fs(7.4),
    "axes.titlesize": _fs(8.0),
    "axes.labelcolor": INK,
    "axes.edgecolor": INK,
    "axes.linewidth": 0.65,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": _fs(6.65),
    "ytick.labelsize": _fs(6.65),
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.fontsize": _fs(6.4),
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
}


@dataclass(frozen=True)
class FigureData:
    """Filtered evidence used by the four panels."""

    attractor: pd.DataFrame
    recovery: dict
    landscape: pd.DataFrame
    clean: pd.DataFrame
    noisy: pd.DataFrame
    stored_noise_summary: pd.DataFrame


@dataclass(frozen=True)
class BootstrapResult:
    """Point estimates, pointwise intervals and paired bootstrap draws."""

    summary: pd.DataFrame
    samples: dict[tuple[float, str], np.ndarray]
    crossover_median: float
    crossover_ci: tuple[float, float]
    difference_04: tuple[float, float, float]
    difference_05: tuple[float, float, float]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pareto_mask(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Return the frontier minimizing both coordinate count and CV RMSE."""
    mask = np.ones(len(x), dtype=bool)
    for i, (xi, yi) in enumerate(zip(x, y, strict=True)):
        dominated = (x <= xi) & (y <= yi) & ((x < xi) | (y < yi))
        mask[i] = not np.any(dominated)
    return mask


def load_and_validate(data_dir: Path) -> FigureData:
    """Load only frozen files and enforce the manuscript evidence contract."""
    required = [
        "canonical_attractor.csv",
        "canonical_recovery.json",
        "representation_landscape.csv",
        "noise_robustness_augmented.csv",
        "noise_robustness_summary.csv",
        "selected_representations.json",
    ]
    missing = [name for name in required if not (data_dir / name).is_file()]
    _require(not missing, f"Missing frozen Figure-4/5 data files: {missing}")

    attractor = pd.read_csv(data_dir / "canonical_attractor.csv")
    recovery = json.loads(
        (data_dir / "canonical_recovery.json").read_text(encoding="utf-8")
    )
    landscape_all = pd.read_csv(data_dir / "representation_landscape.csv")
    augmented = pd.read_csv(data_dir / "noise_robustness_augmented.csv")
    stored_summary_all = pd.read_csv(data_dir / "noise_robustness_summary.csv")
    selections = json.loads(
        (data_dir / "selected_representations.json").read_text(encoding="utf-8")
    )

    _require(
        list(attractor.columns) == ["times", "x", "y", "z"]
        and len(attractor) == 4_001,
        "Panel a requires the archived 4,001-row Lorenz attractor.",
    )
    _require(
        recovery.get("derivative_method")
        == "exact analytic Lorenz right-hand side",
        "Panel-a targets are not the archived exact analytic Lorenz RHS.",
    )
    _require(
        recovery.get("support_recovered_exactly") is True
        and np.isclose(recovery["max_abs_coefficient_deviation"], 2.0e-3),
        "Panel-a recovery checkpoint drifted.",
    )

    landscape = landscape_all.loc[
        (landscape_all["canonical_or_augmentation"] == "canonical")
        & (landscape_all["evidence_level"] == "development_grouped_CV")
        & (landscape_all["regime"] == "clean")
    ].copy()
    _require(
        len(landscape) == 17 and landscape["candidate_id"].nunique() == 17,
        "Panel b must contain exactly 17 unique canonical clean candidates.",
    )

    expected_front = {
        "C0_center",
        "C0_poly2",
        "C0+Q_dy_x",
        "C0+Q_pair",
        "C_all",
    }
    computed_front = set(
        landscape.loc[
            pareto_mask(
                landscape["n_coordinates"].to_numpy(float),
                landscape["cv_rmse_mean"].to_numpy(float),
            ),
            "candidate_id",
        ]
    )
    stored_front = set(landscape.loc[landscape["pareto_front"], "candidate_id"])
    _require(
        computed_front == stored_front == expected_front,
        f"Unexpected Panel-b Pareto frontier: {computed_front}",
    )

    contracts = selections["contracts"]
    _require(
        contracts["q_accuracy"]["selected_candidate"] == "C_all"
        and contracts["q_compact"]["selected_candidate"] == "C0+Q_pair"
        and contracts["q_robust"]["selected_candidate"] == "C_all",
        "Archived representation selections drifted.",
    )
    n_all = int(
        landscape.loc[landscape["candidate_id"] == "C_all", "n_coordinates"].iloc[0]
    )
    n_compact = int(
        landscape.loc[
            landscape["candidate_id"] == "C0+Q_pair", "n_coordinates"
        ].iloc[0]
    )
    _require(
        (n_all, n_compact) == (38, 12)
        and np.isclose(n_all / n_compact, 38 / 12),
        "Archived coordinate counts drifted.",
    )

    aug_base = (
        (augmented["canonical_or_augmentation"] == "augmentation")
        & (augmented["cohort"] == "confirmation_24")
        & (augmented["support_scope"] == "common")
        & (augmented["representation_id"].isin(REPRESENTATIONS))
    )
    clean = augmented.loc[
        aug_base
        & np.isclose(augmented["noise_sigma"], 0.0)
        & (augmented["noise_replicate"] == 0)
    ].copy()
    noisy = augmented.loc[
        aug_base & (augmented["noise_percent"] > 0.0)
    ].copy()

    _require(
        len(clean) == 72
        and clean["trajectory_id"].nunique() == 24
        and clean["representation_id"].nunique() == 3,
        "Panel c must be 24 trajectories x 3 representations (72 rows).",
    )
    clean_counts = clean.groupby("representation_id", observed=True).size()
    _require(
        clean_counts.eq(24).all(),
        "Each clean representation must contain all 24 trajectories once.",
    )
    expected_clean_means = {
        "C0_poly2": 2.1765414924780497,
        "C_compact": 3.3003720588474926e-05,
        "C_all": 1.330530802391035e-05,
    }
    actual_clean_means = clean.groupby("representation_id")["rmse"].mean()
    for rep, expected in expected_clean_means.items():
        _require(
            np.isclose(actual_clean_means[rep], expected, rtol=1e-12, atol=1e-14),
            f"Clean mean drift for {rep}.",
        )

    _require(
        len(noisy) == 2_160,
        "Panel d must contain 2,160 rows after the declared filters.",
    )
    levels = np.sort(noisy["noise_percent"].unique())
    _require(
        len(levels) == 10
        and np.allclose(levels, np.arange(0.1, 1.01, 0.1)),
        f"Unexpected noise grid: {levels}",
    )
    grouped = noisy.groupby(
        ["noise_percent", "representation_id"], observed=True, sort=True
    )
    cell_sizes = grouped.size()
    cell_trajectories = grouped["trajectory_id"].nunique()
    _require(
        cell_sizes.eq(72).all() and cell_trajectories.eq(24).all(),
        "Every noisy cell must contain 72 rows from 24 trajectories.",
    )
    replicate_sets = grouped["noise_replicate"].agg(lambda s: set(map(int, s)))
    _require(
        all(value == {0, 1, 2} for value in replicate_sets),
        "Every noisy cell must contain replicate IDs {0, 1, 2}.",
    )

    stored_summary = stored_summary_all.loc[
        (stored_summary_all["canonical_or_augmentation"] == "augmentation")
        & (stored_summary_all["support_scope"] == "common")
        & (stored_summary_all["representation_id"].isin(REPRESENTATIONS))
    ].copy()
    raw_means = (
        pd.concat([clean, noisy], ignore_index=True)
        .groupby(["noise_percent", "representation_id"], as_index=False)["rmse"]
        .mean()
        .rename(columns={"rmse": "raw_mean"})
    )
    mean_check = raw_means.merge(
        stored_summary[
            ["noise_percent", "representation_id", "mean_rmse"]
        ],
        on=["noise_percent", "representation_id"],
        how="inner",
        validate="one_to_one",
    )
    _require(
        len(mean_check) == 33
        and np.allclose(
            mean_check["raw_mean"], mean_check["mean_rmse"], rtol=1e-12, atol=1e-14
        ),
        "Raw arithmetic means do not match noise_robustness_summary.csv.",
    )

    one_percent = (
        raw_means.loc[np.isclose(raw_means["noise_percent"], 1.0)]
        .set_index("representation_id")["raw_mean"]
    )
    expected_one_percent = {
        "C_all": 2.234681,
        "C0_poly2": 2.866233,
        "C_compact": 4.999489,
    }
    for rep, expected in expected_one_percent.items():
        _require(
            np.isclose(one_percent[rep], expected, atol=5e-7),
            f"1% noise checkpoint drift for {rep}: {one_percent[rep]}",
        )

    noisy_means = noisy.groupby(
        ["noise_percent", "representation_id"], observed=True
    )["rmse"].mean()
    winners = noisy_means.groupby(level=0).idxmin().map(lambda pair: pair[1])
    _require(
        winners.eq("C_all").all(),
        "C_all must have the lowest arithmetic mean at every displayed noise level.",
    )

    return FigureData(
        attractor=attractor,
        recovery=recovery,
        landscape=landscape,
        clean=clean,
        noisy=noisy,
        stored_noise_summary=stored_summary,
    )


def _replicate_matrix(
    group: pd.DataFrame,
    trajectory_ids: list[str],
    expected_replicates: int,
) -> np.ndarray:
    """Return trajectories x replicate rows without collapsing the cluster."""
    matrix = (
        group.pivot(
            index="trajectory_id", columns="noise_replicate", values="rmse"
        )
        .reindex(trajectory_ids)
        .sort_index(axis=1)
        .to_numpy(float)
    )
    _require(
        matrix.shape == (len(trajectory_ids), expected_replicates)
        and np.isfinite(matrix).all(),
        "Incomplete trajectory x replicate matrix for cluster bootstrap.",
    )
    return matrix


def trajectory_cluster_bootstrap(data: FigureData) -> BootstrapResult:
    """Compute pointwise CIs with one shared B x 24 trajectory draw matrix.

    Indexing ``matrix[draws]`` retains trajectory multiplicities and every row
    within the selected cluster.  It intentionally does not use an ``isin``
    filter, which would discard bootstrap multiplicities.
    """
    trajectory_ids = sorted(data.clean["trajectory_id"].unique().tolist())
    _require(len(trajectory_ids) == 24, "Expected 24 protected trajectories.")

    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    draws = rng.integers(
        0,
        len(trajectory_ids),
        size=(BOOTSTRAP_RESAMPLES, len(trajectory_ids)),
    )

    evidence = pd.concat([data.clean, data.noisy], ignore_index=True)
    rows: list[dict[str, float | str]] = []
    samples: dict[tuple[float, str], np.ndarray] = {}
    matrices: dict[tuple[float, str], np.ndarray] = {}

    for level in np.sort(evidence["noise_percent"].unique()):
        expected_replicates = 1 if np.isclose(level, 0.0) else 3
        for rep in REPRESENTATIONS:
            group = evidence.loc[
                np.isclose(evidence["noise_percent"], level)
                & (evidence["representation_id"] == rep)
            ]
            matrix = _replicate_matrix(
                group, trajectory_ids, expected_replicates
            )
            # Shape B x 24 x R: cluster multiplicity is retained, as are all R
            # replicate rows belonging to every resampled trajectory.
            bootstrap_means = matrix[draws].mean(axis=(1, 2))
            lo, hi = np.quantile(
                bootstrap_means, [0.025, 0.975], method="linear"
            )
            key = (float(level), rep)
            matrices[key] = matrix
            samples[key] = bootstrap_means
            rows.append(
                {
                    "noise_percent": float(level),
                    "representation_id": rep,
                    "mean_rmse": float(matrix.mean()),
                    "ci_lo": float(lo),
                    "ci_hi": float(hi),
                }
            )

    summary = pd.DataFrame(rows)

    def paired_difference(level: float) -> tuple[float, float, float, np.ndarray]:
        compact = matrices[(level, "C_compact")]
        quadratic = matrices[(level, "C0_poly2")]
        _require(
            compact.shape == quadratic.shape,
            "Paired representation matrices are misaligned.",
        )
        difference_matrix = compact - quadratic
        point = float(difference_matrix.mean())
        boot = difference_matrix[draws].mean(axis=(1, 2))
        lo, hi = np.quantile(boot, [0.025, 0.975], method="linear")
        return point, float(lo), float(hi), boot

    d04_point, d04_lo, d04_hi, d04_boot = paired_difference(0.4)
    d05_point, d05_lo, d05_hi, d05_boot = paired_difference(0.5)
    _require(
        np.isclose(d04_point, -0.2566488943, atol=1e-10)
        and np.allclose(
            [d04_lo, d04_hi], [-0.36996687, -0.14629409], atol=1e-7
        ),
        "The seeded shared-draw compact-minus-quadratic checkpoint at 0.4% drifted.",
    )
    _require(
        np.isclose(d05_point, 0.2839254827, atol=1e-10)
        and np.allclose(
            [d05_lo, d05_hi], [0.14716986, 0.42459120], atol=1e-7
        ),
        "The seeded shared-draw compact-minus-quadratic checkpoint at 0.5% drifted.",
    )

    denominator = d05_boot - d04_boot
    valid = np.isfinite(denominator) & (denominator > 0)
    _require(valid.mean() > 0.999, "Crossover interpolation is not well defined.")
    crossover = 0.4 + 0.1 * (-d04_boot[valid]) / denominator[valid]
    crossover_median = float(np.median(crossover))
    crossover_lo, crossover_hi = np.quantile(
        crossover, [0.025, 0.975], method="linear"
    )
    _require(
        np.isclose(crossover_median, 0.4475, atol=8e-4)
        and np.allclose(
            [crossover_lo, crossover_hi], [0.4260, 0.4719], atol=1.1e-3
        ),
        "Trajectory-cluster crossover checkpoint drifted.",
    )

    compact_half = summary.loc[
        np.isclose(summary["noise_percent"], 0.5)
        & (summary["representation_id"] == "C_compact")
    ].iloc[0]
    _require(
        np.allclose(
            [compact_half["ci_lo"], compact_half["ci_hi"]],
            [2.85256798, 3.15223437],
            atol=1e-7,
        ),
        "The seeded shared-draw 0.5%-noise compact cluster CI drifted.",
    )

    return BootstrapResult(
        summary=summary,
        samples=samples,
        crossover_median=crossover_median,
        crossover_ci=(float(crossover_lo), float(crossover_hi)),
        difference_04=(d04_point, d04_lo, d04_hi),
        difference_05=(d05_point, d05_lo, d05_hi),
    )


def add_panel_header(
    fig: plt.Figure,
    slot,
    label: str,
    title: str | tuple[str, ...],
    subtitle: str,
    *,
    center_title: bool = False,
) -> None:
    """Place a panel header on the outer GridSpec cell, not the child axes.

    Using the cell bounds gives 3D panel a and 2D panels b-d identical title
    baselines, left edges, and title-to-subtitle spacing.  Extra title lines
    stack above the original baseline so the subtitle does not drop into the
    plot.  ``center_title`` places the title and subtitle on the cell midline.
    """
    bounds = slot.get_position(fig)
    title_lines = (title,) if isinstance(title, str) else tuple(title)
    last_title_y = bounds.y1 + 0.043
    subtitle_y = bounds.y1 + 0.012
    if center_title:
        title_x = 0.5 * (bounds.x0 + bounds.x1)
        title_ha = "center"
    else:
        title_x = bounds.x0
        title_ha = "left"
    first_title_y = last_title_y + (len(title_lines) - 1) * TITLE_LINE_SPACING
    fig.text(
        bounds.x0 - 0.026,
        first_title_y,
        rf"\textbf{{{label}}}",
        ha="left",
        va="baseline",
        fontsize=_fs(8.5),
        color=INK,
    )
    for index, line in enumerate(title_lines):
        fig.text(
            title_x,
            first_title_y - index * TITLE_LINE_SPACING,
            rf"\textbf{{{line}}}",
            ha=title_ha,
            va="baseline",
            fontsize=_fs(8.0),
            color=INK,
        )
    fig.text(
        title_x,
        subtitle_y,
        subtitle,
        ha=title_ha,
        va="baseline",
        fontsize=_fs(6.0),
        color=MID,
    )


def _latex_sci(value: float, digits: int = 1) -> str:
    """Format a number as LaTeX scientific notation, e.g. 2.0\\times10^{-3}."""
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times10^{{{int(exponent)}}}"


def draw_panel_a(fig: plt.Figure, slot, data: FigureData) -> None:
    # Give the attractor most of the cell and use the lower strip only for the
    # recovered equations.  The tighter split avoids the unused vertical band
    # produced by a square 3D axes inside this narrow panel.
    sub = slot.subgridspec(2, 1, height_ratios=[0.80, 0.20], hspace=0.0)
    ax = fig.add_subplot(sub[0], projection="3d")
    text_ax = fig.add_subplot(sub[1])
    text_ax.set_axis_off()

    x = data.attractor["x"].to_numpy()
    y = data.attractor["y"].to_numpy()
    z = data.attractor["z"].to_numpy()
    ax.set_proj_type("ortho")
    ax.plot(
        x,
        y,
        z,
        color="#263A59",
        lw=0.40,
        alpha=0.95,
        clip_on=True,
    )
    ax.set_axis_off()
    ax.view_init(elev=16, azim=-62)
    ax.set_box_aspect((np.ptp(x), np.ptp(y), np.ptp(z) * 0.90), zoom=1.50)

    dy = data.recovery["equations"]["dy"]["recovered_coefficients"]
    dz = data.recovery["equations"]["dz"]["recovered_coefficients"]
    equations = (
        r"$\dot{x}=10(y-x)$" "\n"
        rf"$\dot{{y}}={dy['x']:.3f}x{dy['y']:+.4f}y{dy['x z']:+.4f}xz$" "\n"
        rf"$\dot{{z}}=xy{dz['z']:+.3f}z$"
    )
    text_ax.text(
        0.50,
        0.98,
        equations,
        ha="center",
        va="top",
        fontsize=_fs(8.1),
        color=INK,
        linespacing=1.16,
    )
    text_ax.text(
        0.50,
        -0.68,
        "Exact support recovered; "
        + rf"$\|\Delta\mathbf{{c}}\|_\infty={_latex_sci(data.recovery['max_abs_coefficient_deviation'])}$",
        ha="center",
        va="bottom",
        fontsize=_fs(6.5),
        color=MID,
        clip_on=False,
    )


def draw_panel_b(ax: plt.Axes, landscape: pd.DataFrame) -> None:
    df = landscape.sort_values(["n_coordinates", "cv_rmse_mean"]).copy()
    x = df["n_coordinates"].to_numpy(float)
    y = df["cv_rmse_mean"].to_numpy(float)
    yerr = df["cv_rmse_se"].to_numpy(float)
    frontier = pareto_mask(x, y)
    order = np.argsort(x[frontier])

    frontier_line, = ax.plot(
        x[frontier][order],
        y[frontier][order],
        color="#555B63",
        lw=1.55,
        linestyle=(0, (4.0, 2.0)),
        marker="o",
        markersize=3.4,
        markerfacecolor="white",
        markeredgecolor="#555B63",
        markeredgewidth=0.75,
        zorder=4,
        label="Pareto frontier",
    )
    frontier_legend = Line2D(
        [0],
        [0],
        color="#555B63",
        lw=1.65,
        linestyle=(0, (4.0, 2.0)),
        dash_capstyle="butt",
        label="Pareto frontier",
    )
    ax.errorbar(
        x,
        y,
        yerr=yerr,
        fmt="none",
        ecolor="#949AA2",
        elinewidth=0.65,
        capsize=1.5,
        capthick=0.55,
        zorder=2,
    )

    hero_canonical = {
        "C0_poly2": "C0_poly2",
        "C0+Q_pair": "C_compact",
        "C_all": "C_all",
    }
    other = ~df["candidate_id"].isin(hero_canonical)
    ax.scatter(
        x[other],
        y[other],
        s=20,
        marker="o",
        facecolor="white",
        edgecolor="#747A82",
        linewidth=0.75,
        zorder=3,
        label="Other candidate",
    )
    for candidate, rep in hero_canonical.items():
        row = df.loc[df["candidate_id"] == candidate].iloc[0]
        ax.scatter(
            row["n_coordinates"],
            row["cv_rmse_mean"],
            s=42,
            marker=MARKERS[rep],
            facecolor=COLORS[rep],
            edgecolor="white",
            linewidth=0.7,
            zorder=5,
        )

    quadratic = df.loc[df["candidate_id"] == "C0_poly2"].iloc[0]
    one_q = df.loc[df["candidate_id"] == "C0+Q_dy_x"].iloc[0]
    compact = df.loc[df["candidate_id"] == "C0+Q_pair"].iloc[0]
    all_rep = df.loc[df["candidate_id"] == "C_all"].iloc[0]

    # Keep the three selection callouts in separate white-space regions.  The
    # text boxes do not cover the Pareto path; only their leader lines approach
    # the corresponding selected points.
    ax.annotate(
        "Quadratic baseline\n10 coordinates\n" r"$\rightarrow$ 65 features",
        xy=(quadratic["n_coordinates"], quadratic["cv_rmse_mean"]),
        xytext=(1.6, 0.16),
        ha="left",
        va="center",
        fontsize=_fs(6.05),
        linespacing=1.12,
        color=COLORS["C0_poly2"],
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#D3A27E", lw=0.6),
        arrowprops=dict(
            arrowstyle="-",
            color=COLORS["C0_poly2"],
            lw=0.7,
            shrinkA=1,
            shrinkB=3,
        ),
        zorder=7,
    )
    ax.annotate(
        "Compactness criterion\n(pre-specified practical floor)\n"
        r"$C_0+Q_{\mathrm{pair}}$: 12 coordinates",
        xy=(compact["n_coordinates"], compact["cv_rmse_mean"]),
        xytext=(14.3, 1.8e-3),
        ha="left",
        va="center",
        fontsize=_fs(6.05),
        linespacing=1.15,
        color=COLORS["C_compact"],
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#8CB9AA", lw=0.6),
        arrowprops=dict(
            arrowstyle="-",
            color=COLORS["C_compact"],
            lw=0.7,
            shrinkA=1,
            shrinkB=3,
        ),
        zorder=7,
    )
    ax.annotate(
        "Accuracy and robustness criteria\n"
        r"$C_{\mathrm{all}}$: 38 coordinates",
        xy=(all_rep["n_coordinates"], all_rep["cv_rmse_mean"]),
        xytext=(26.5, 2.2e-4),
        ha="left",
        va="center",
        fontsize=_fs(6.05),
        linespacing=1.15,
        color=COLORS["C_all"],
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#8EB0C8", lw=0.6),
        arrowprops=dict(
            arrowstyle="-",
            color=COLORS["C_all"],
            lw=0.7,
            shrinkA=1,
            shrinkB=3,
        ),
        zorder=7,
    )
    ax.annotate(
        r"$C_0+Q_{\dot y|x}$",
        xy=(one_q["n_coordinates"], one_q["cv_rmse_mean"]),
        xytext=(13.5, 1.4),
        fontsize=_fs(6.0),
        color=MID,
        arrowprops=dict(arrowstyle="-", color=LIGHT, lw=0.55),
    )

    ax.set_yscale("log")
    ax.set_xlim(0.5, 40.5)
    ax.set_ylim(7.0e-6, 18.0)
    ax.set_xticks([2, 10, 12, 18, 30, 38])
    ax.set_xlabel("Scientific coordinates in representation, $C$")
    ax.set_ylabel("Grouped-CV RMSE in $z$")
    ax.grid(axis="y", which="major", color=RULE, lw=0.45, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(
        handles=[frontier_legend],
        loc="upper right",
        bbox_to_anchor=(0.995, 0.995),
        frameon=False,
        handlelength=4.4,
        handletextpad=0.65,
        borderaxespad=0.0,
        fontsize=_fs(6.2),
    )
    ax.text(
        0.985,
        0.905,
        r"Error bars: mean $\pm$ SE",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=_fs(5.75),
        color=MID,
    )


def draw_panel_c(
    ax: plt.Axes, clean: pd.DataFrame, bootstrap: BootstrapResult
) -> None:
    positions = np.arange(3, dtype=float)
    clean_summary = bootstrap.summary.loc[
        np.isclose(bootstrap.summary["noise_percent"], 0.0)
    ].set_index("representation_id")
    class_means = clean_summary.loc[list(REPRESENTATIONS), "mean_rmse"].to_numpy(
        float
    )
    # Connect the three class means (not individual trajectories) to make the
    # clean scale separation visible while avoiding any implication of a fit.
    ax.plot(
        positions,
        class_means,
        color="#737980",
        lw=0.9,
        linestyle=(0, (0.8, 2.2)),
        dash_capstyle="round",
        zorder=1,
    )

    for position, rep in zip(positions, REPRESENTATIONS, strict=True):
        row = clean_summary.loc[rep]
        mean = float(row["mean_rmse"])
        lo = float(row["ci_lo"])
        hi = float(row["ci_hi"])
        ax.errorbar(
            position,
            mean,
            yerr=np.array([[mean - lo], [hi - mean]]),
            fmt=MARKERS[rep],
            ms=7.0,
            mfc=COLORS[rep],
            mec="white",
            mew=0.8,
            ecolor=COLORS[rep],
            elinewidth=1.25,
            capsize=4.8,
            capthick=1.15,
            zorder=5,
        )

    quadratic_mean = clean_summary.loc["C0_poly2", "mean_rmse"]
    compact_mean = clean_summary.loc["C_compact", "mean_rmse"]
    all_mean = clean_summary.loc["C_all", "mean_rmse"]
    compact_gap = np.log10(quadratic_mean / compact_mean)
    all_gap = np.log10(quadratic_mean / all_mean)
    _require(
        np.isclose(compact_gap, 4.819, atol=8e-4)
        and np.isclose(all_gap, 5.214, atol=8e-4),
        "Clean order-of-magnitude gaps drifted.",
    )

    ax.set_yscale("log")
    # Keep only a thin pad past the outer markers so the three two-line
    # tick labels sit farther apart and the second rows do not collide.
    ax.set_xlim(-0.12, 2.12)
    ax.set_ylim(7.5e-6, 5.0)
    ax.set_xticks(positions)
    ax.set_xticklabels(
        [
            "Quadratic\n" r"10 $\rightarrow$ 65 features",
            "Compact\n12 coordinates",
            r"$C_{\mathrm{all}}$" "\n38 coordinates",
        ],
        linespacing=1.55,
    )
    ax.set_ylabel("Confirmation RMSE in $z$")
    ax.grid(axis="y", which="major", color=RULE, lw=0.45, zorder=0)
    ax.set_axisbelow(True)
    ax.text(
        0.97,
        0.93,
        r"$\approx 5$ orders of" "\n" "clean separation",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=_fs(6.25),
        color=INK,
        linespacing=1.15,
    )
    ax.text(
        0.96,
        0.61,
        "Mean and 95\\%\ntrajectory-bootstrap CI",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=_fs(5.75),
        color=MID,
        linespacing=1.15,
    )


def draw_panel_d(ax: plt.Axes, bootstrap: BootstrapResult) -> None:
    summary = bootstrap.summary.loc[bootstrap.summary["noise_percent"] > 0].copy()

    for rep in REPRESENTATIONS:
        group = summary.loc[summary["representation_id"] == rep].sort_values(
            "noise_percent"
        )
        x = group["noise_percent"].to_numpy(float)
        mean = group["mean_rmse"].to_numpy(float)
        lo = group["ci_lo"].to_numpy(float)
        hi = group["ci_hi"].to_numpy(float)
        ax.fill_between(
            x,
            lo,
            hi,
            color=COLORS[rep],
            alpha=0.13,
            linewidth=0,
            zorder=1,
        )
        ax.plot(
            x,
            mean,
            color=COLORS[rep],
            lw=1.65 if rep == "C_all" else 1.25,
            marker=MARKERS[rep],
            markersize=3.4,
            markerfacecolor=COLORS[rep],
            markeredgecolor="white",
            markeredgewidth=0.45,
            zorder=3,
        )
        end_label = {
            "C0_poly2": "Quadratic",
            "C_compact": "Compact",
            "C_all": r"$C_{\mathrm{all}}$",
        }[rep]
        ax.annotate(
            end_label,
            xy=(x[-1], mean[-1]),
            xytext=(4, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=_fs(6.15),
            color=COLORS[rep],
            clip_on=False,
        )

    crossover = bootstrap.crossover_median
    ax.vlines(
        crossover,
        2.72,
        3.48,
        color="#7A7F86",
        lw=0.65,
        linestyles=(0, (2.2, 2.2)),
        zorder=2,
    )
    ax.text(
        0.49,
        3.68,
        "Compact--Quadratic\n" r"crossover $\approx 0.45\%$",
        ha="right",
        va="bottom",
        fontsize=_fs(5.75),
        color=MID,
        linespacing=1.1,
    )

    ax.set_xlim(0.075, 1.13)
    ax.set_ylim(0.35, 5.55)
    ax.set_xticks(np.arange(0.1, 1.01, 0.1))
    ax.set_xlabel(r"Observation noise, $\sigma$ (\% of channel s.d.)")
    ax.set_ylabel("Confirmation RMSE in $z$")
    ax.grid(axis="y", which="major", color=RULE, lw=0.45, zorder=0)
    ax.set_axisbelow(True)
    ax.text(
        0.025,
        0.975,
        r"Robustness criterion selects $C_{\mathrm{all}}$"
        "\nLowest mean at every displayed noise level",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=_fs(6.15),
        color=COLORS["C_all"],
        linespacing=1.18,
        bbox=dict(boxstyle="round,pad=0.22", fc=PALE_BLUE, ec="#A9C1D3", lw=0.55),
        zorder=5,
    )
    ax.text(
        0.955,
        0.055,
        "Mean and pointwise 95\\% trajectory-cluster bootstrap CI",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=_fs(5.75),
        color=MID,
    )


def build_figure(data: FigureData, bootstrap: BootstrapResult) -> plt.Figure:
    """Construct the exact-size four-panel manuscript artwork."""
    fig = plt.figure(figsize=(WIDTH_MM / MM_PER_INCH, HEIGHT_MM / MM_PER_INCH))
    grid = fig.add_gridspec(
        2,
        2,
        width_ratios=[0.88, 1.52],
        height_ratios=[1.06, 0.94],
        left=0.075,
        right=0.945,
        top=0.900,
        bottom=0.095,
        wspace=0.22,
        hspace=0.38,
    )

    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[1, 0])
    ax_d = fig.add_subplot(grid[1, 1])
    draw_panel_a(fig, grid[0, 0], data)
    draw_panel_b(ax_b, data.landscape)
    draw_panel_c(ax_c, data.clean, bootstrap)
    draw_panel_d(ax_d, bootstrap)

    add_panel_header(
        fig,
        grid[0, 0],
        "a",
        ("Fixed-Representation", "Support Recovery"),
        r"Full-state recovery $\cdot$ exact analytic RHS targets",
        center_title=True,
    )
    add_panel_header(
        fig,
        grid[0, 1],
        "b",
        ("Accuracy and Compactness", "Select Different Representations"),
        r"17 admissible representations $\cdot$ 48 development trajectories $\cdot$ 6 grouped folds",
        center_title=True,
    )
    add_panel_header(
        fig,
        grid[1, 0],
        "c",
        "Clean-Data Relational Advantage",
        r"$N=24$ independent trajectories $\cdot$ common support",
        center_title=True,
    )
    add_panel_header(
        fig,
        grid[1, 1],
        "d",
        "Observation Noise Changes Relative Ranking",
        r"Controlled stress test $\cdot$ $N=24$ trajectories $\times$ 3 replicates $\cdot$ common support",
        center_title=True,
    )

    fig.text(
        0.50,
        0.018,
        "Development data select representations; the protected confirmation cohort is used only for evaluation.",
        ha="center",
        va="bottom",
        fontsize=_fs(5.75),
        color=MID,
    )
    return fig


def export_figure(fig: plt.Figure, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / STEM
    paths: list[Path] = []
    for extension in ("png", "pdf", "svg"):
        path = stem.with_suffix(f".{extension}")
        fig.savefig(
            path,
            dpi=600,
            bbox_inches=None,
            pad_inches=0,
            facecolor="white",
            transparent=False,
        )
        paths.append(path)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA,
        help="Frozen input directory (default: ../figure_source_data).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory for the distinct v5 PNG/PDF/SVG outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    data = load_and_validate(data_dir)
    bootstrap = trajectory_cluster_bootstrap(data)
    with mpl.rc_context(STYLE):
        fig = build_figure(data, bootstrap)
        paths = export_figure(fig, output_dir)
        plt.close(fig)

    clean_means = (
        bootstrap.summary.loc[np.isclose(bootstrap.summary["noise_percent"], 0.0)]
        .set_index("representation_id")["mean_rmse"]
    )
    half_compact = bootstrap.summary.loc[
        np.isclose(bootstrap.summary["noise_percent"], 0.5)
        & (bootstrap.summary["representation_id"] == "C_compact")
    ].iloc[0]
    print("Data and bootstrap assertions passed.")
    print(
        "Clean means: "
        + ", ".join(f"{rep}={clean_means[rep]:.8g}" for rep in REPRESENTATIONS)
    )
    print(
        "0.5% compact trajectory-cluster 95% CI: "
        f"[{half_compact['ci_lo']:.5f}, {half_compact['ci_hi']:.5f}]"
    )
    print(
        "Compact-quadratic crossover: "
        f"median={bootstrap.crossover_median:.4f}%, "
        f"95% CI=[{bootstrap.crossover_ci[0]:.4f}%, "
        f"{bootstrap.crossover_ci[1]:.4f}%]"
    )
    print("Wrote:")
    for path in paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()
