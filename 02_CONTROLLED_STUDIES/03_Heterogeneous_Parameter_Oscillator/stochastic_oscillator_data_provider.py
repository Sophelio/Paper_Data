"""SIR data provider for the random-coefficient harmonic-oscillator ensemble.

Loads the parquet files produced by ``stochastic_oscillator.py`` from the
sibling ``data/`` directory. Each parquet is one realization (one identifier)
of ``h_alpha(x) = sin(alpha*pi*x)`` with columns:

    times, h, dh, d2h, alpha

where ``times`` is the spatial coordinate x, ``dh``/``d2h`` are the analytic
("exact") first/second derivatives, and ``alpha`` is the (constant) latent
parameter — treated as metadata and excluded from the selectable signals.

Recommended SIR setup (recovers ``a*d2h/dx2 + b*h = 0`` per realization):
  * Variables: ``h`` (and optionally ``dh``, ``d2h`` to use exact derivatives).
  * Target variable: ``h`` with target type ``Double Derivative`` so SIR's
    output is d2h/dx2 and the feature library includes ``h``.
  * Operator library: +, -, * up to order ~2, as in the Lorenz example.
  * The recovered ratio ``-b/a`` approximates ``(alpha*pi)^2``.

See ``docs/context.md`` Phase 4 for the full provider contract.
"""

import logging
import os
import pickle
import re
from pathlib import Path
from os import listdir, path

import numpy as np
import pandas as pd

import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Absolute path fallback for known-good Windows setups; prefer portable discovery.
_FALLBACK_DATASET_URL = r"D:\sir-web\Paper Examples\Stochastic oscillator\data"


def _resolve_dataset_url():
    """Locate ``Paper Examples/Stochastic oscillator/data`` portably."""
    here = Path(__file__).resolve()
    for root in here.parents:
        candidate = root / "Paper Examples" / "Stochastic oscillator" / "data"
        if candidate.is_dir():
            return str(candidate)
    return _FALLBACK_DATASET_URL


DATASET_URL = _resolve_dataset_url()

# ``times`` is the coordinate axis; ``alpha`` is constant metadata. Neither is a
# selectable input signal.
EXCLUDED_VARS = {"times", "alpha"}


def _list_parquet_files(directory):
    try:
        return sorted(f for f in os.listdir(directory) if f.endswith(".parquet"))
    except OSError:
        return []


def _discover_variables(directory):
    parquet_files = _list_parquet_files(directory)
    if not parquet_files:
        return []
    columns = []
    seen = set()
    for fname in parquet_files:
        df = pd.read_parquet(os.path.join(directory, fname))
        for col in df.columns.tolist():
            if col not in EXCLUDED_VARS and col not in seen:
                columns.append(col)
                seen.add(col)
    return columns


def _ensure_requested_columns(df, keys):
    """Synthesize exact dh/d2h from h (and alpha/times) when a file lacks them.

    Keeps the provider robust to mixed schemas (e.g. an ``h``-only parquet):
      dh  = alpha*pi * cos(alpha*pi*x)
      d2h = -(alpha*pi)**2 * sin(alpha*pi*x) = -(alpha*pi)**2 * h
    """
    missing = [k for k in keys if k not in df.columns]
    if not missing:
        return df

    derivative_keys = {"dh", "d2h"}
    if any(k in derivative_keys for k in missing):
        if "alpha" in df.columns and "times" in df.columns and "h" in df.columns:
            alpha = float(df["alpha"].iloc[0])
            w = alpha * np.pi
            x = df["times"].to_numpy(dtype=np.float64)
            h = df["h"].to_numpy(dtype=np.float64)
            if "dh" in missing:
                df["dh"] = w * np.cos(w * x)
            if "d2h" in missing:
                df["d2h"] = -(w**2) * h

    return df


def get_true_coefficients(directory):
    """Return (alpha, (alpha*pi)^2) arrays read from every realization file."""
    alphas = []
    for fname in _list_parquet_files(directory):
        df = pd.read_parquet(os.path.join(directory, fname))
        if "alpha" in df.columns and len(df) > 0:
            alphas.append(float(df["alpha"].iloc[0]))
    alphas = np.asarray(alphas, dtype=np.float64)
    return alphas, (alphas * np.pi) ** 2


# --- Colorblind-safe palette (Okabe-Ito) for the true/recovered comparison ---
_COLOR_TRUE = "#0072B2"        # blue
_COLOR_RECOVERED = "#D55E00"   # vermilion/orange


def _alpha_from_file(file_path):
    """Read the (constant) latent alpha from one realization parquet."""
    try:
        df = pd.read_parquet(file_path, columns=["alpha"])
    except Exception:
        df = pd.read_parquet(file_path)
    if "alpha" in df.columns and len(df) > 0:
        return float(df["alpha"].iloc[0])
    return np.nan


def _ecdf(values):
    """Return (x_sorted, y) for an empirical CDF: y = (1..n)/n."""
    v = np.sort(np.asarray(values, dtype=np.float64))
    n = v.size
    if n == 0:
        return v, np.array([])
    y = np.arange(1, n + 1, dtype=np.float64) / n
    return v, y


def _ks_distance(a, b):
    """Two-sample Kolmogorov-Smirnov distance (max |F_a - F_b|)."""
    return _ks_detail(a, b)[0]


def _ks_detail(a, b):
    """Return (D_KS, x_star, F_a(x_star), F_b(x_star)) for the max-gap location."""
    a = np.sort(np.asarray(a, dtype=np.float64))
    b = np.sort(np.asarray(b, dtype=np.float64))
    if a.size == 0 or b.size == 0:
        return np.nan, np.nan, np.nan, np.nan
    grid = np.concatenate([a, b])
    fa = np.searchsorted(a, grid, side="right") / a.size
    fb = np.searchsorted(b, grid, side="right") / b.size
    diff = np.abs(fa - fb)
    j = int(np.argmax(diff))
    return float(diff[j]), float(grid[j]), float(fa[j]), float(fb[j])


def _load_sir_result(model):
    """Load the calibrated per-realization results dict from ``model.output_path``.

    ``output_path`` is typically relative to the app cwd (e.g.
    ``RESULTS/output.h.psir``); fall back to resolving it from there.
    """
    output_path = getattr(model, "output_path", None)
    if not output_path:
        raise FileNotFoundError("model has no output_path (run SIR first)")
    candidates = [output_path, os.path.abspath(output_path)]
    for cand in candidates:
        if os.path.exists(cand):
            with open(cand, "rb") as f:
                return pickle.load(f)
    raise FileNotFoundError(f"SIR result file not found: {output_path}")


def _select_equation_key(result, value_term, requested=""):
    """Pick the equation whose term names include the function value ``[h]`` term.

    Prefers the user-requested key when valid; otherwise the calibrated
    (starred) variant with the FEWEST terms containing the value term, so we
    isolate the clean ``a*h_xx + b*h = 0`` relation rather than a wider fit.
    """
    eq_key_re = re.compile(r"^\d+_\d+\*?$")

    def _has_target(key):
        eq = result.get(key)
        return (
            isinstance(eq, dict)
            and "name" in eq
            and value_term in [str(n) for n in eq["name"]]
        )

    if requested and requested in result and _has_target(requested):
        return requested

    candidates = [k for k in result.keys() if eq_key_re.match(k) and _has_target(k)]
    if not candidates:
        return None

    def _sort_key(key):
        eq = result[key]
        n_terms = len(eq["name"])
        starred = 0 if key.endswith("*") else 1  # prefer calibrated (*) refit
        return (n_terms, starred)

    return sorted(candidates, key=_sort_key)[0]


def _recovered_alpha_from_model(model, value_variable="h", requested_equation=""):
    """Reconstruct per-realization alpha_hat from SIR's recovered coefficients.

    Whichever way the run is configured, SIR's output is the second derivative
    (``h_xx``) and the relation reduces to ``a*h_xx + b*h = 0`` per realization:

      * Target = ``h`` with type 'Double Derivative'  -> output is d2h, and
      * Target = ``d2h`` with type 'Variable'          -> output is d2h,

    and in both cases the *feature* term we need is the function value ``[h]``
    (the target/output itself never appears in ``eq['name']`` — only the RHS
    features and ``CONST`` do). We take a = 1 (the output's implicit unit
    coefficient) and b = the recovered coefficient of the ``[h]`` term, so
    ``-b/a = (alpha*pi)^2`` and ``alpha_hat = sqrt(max(0, -b/a)) / pi``.

    ``value_variable`` names the function-value column (default ``h``).

    Returns (alpha_hat, filenames, n_invalid, equation_key).
    """
    result = _load_sir_result(model)
    value_term = f"[{value_variable}]"
    eq_key = _select_equation_key(result, value_term, requested_equation)
    if eq_key is None:
        available = sorted(
            str(n)
            for k, eq in result.items()
            if isinstance(eq, dict) and "name" in eq
            for n in eq["name"]
        )
        raise ValueError(
            f"No recovered equation contains the value term '{value_term}'. "
            f"The coefficient on '{value_variable}' encodes (alpha*pi)^2, so "
            f"'{value_variable}' must be one of the regression features (e.g. "
            f"set target = 'd2h' as a Variable and include '{value_variable}', "
            f"or set target = '{value_variable}' with type 'Double Derivative'). "
            f"Recovered feature terms so far: {sorted(set(available))}."
        )

    eq = result[eq_key]
    names = [str(n) for n in eq["name"]]
    h_index = names.index(value_term)
    coeff = np.asarray(eq["x"], dtype=np.float64)  # (n_realizations, n_terms)
    b = coeff[:, h_index]
    a = np.ones_like(b)  # SIR's output (h_xx) carries an implicit unit coefficient

    ratio = np.where(a != 0.0, -b / a, np.nan)  # (alpha*pi)^2
    valid = np.isfinite(ratio) & (ratio > 0.0)
    alpha_hat = np.full_like(ratio, np.nan)
    alpha_hat[valid] = np.sqrt(ratio[valid]) / np.pi
    n_invalid = int((~valid).sum())

    filenames = result.get("filenames") or []
    return alpha_hat, list(filenames), n_invalid, eq_key


def _export_cdf_figure(true_alpha, recovered_alpha, ks, out_dir):
    """Write publication-quality PNG (600 dpi) + PDF + SVG via matplotlib.

    Best-effort: any failure is logged and swallowed so the interactive
    plotly panel still renders.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # pragma: no cover - matplotlib always present here
        logger.warning("matplotlib unavailable, skipping vector export: %s", e)
        return None

    from matplotlib.ticker import MultipleLocator

    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.linewidth": 0.9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "axes.labelsize": 11.5,
        "legend.fontsize": 9,
    })

    fig, ax = plt.subplots(figsize=(3.7, 3.05))
    ax.set_facecolor("white")

    xt, yt = _ecdf(true_alpha)
    xr, yr = _ecdf(recovered_alpha)

    # Faint theoretical reference: alpha ~ U[1,2] has CDF = (alpha - 1) on [1,2].
    ax.plot([1.0, 2.0], [0.0, 1.0], color="0.55", linewidth=1.0,
            linestyle=(0, (1, 1.5)), zorder=1, label=r"Ideal $U[1,2]$")

    # ECDFs as post-steps, with subtle white-edged markers at each jump.
    ax.step(xt, yt, where="post", color=_COLOR_TRUE, linewidth=2.0,
            linestyle="-", zorder=3, label=r"True $\alpha$", solid_capstyle="round")
    ax.plot(xt, yt, linestyle="none", marker="o", markersize=3.0,
            markerfacecolor=_COLOR_TRUE, markeredgecolor="white",
            markeredgewidth=0.4, zorder=4)
    ax.step(xr, yr, where="post", color=_COLOR_RECOVERED, linewidth=2.0,
            linestyle=(0, (5, 2)), zorder=3, label=r"Recovered $\hat{\alpha}$",
            solid_capstyle="round")
    ax.plot(xr, yr, linestyle="none", marker="s", markersize=2.8,
            markerfacecolor=_COLOR_RECOVERED, markeredgecolor="white",
            markeredgewidth=0.4, zorder=4)

    # Visualize what D_KS measures: the largest vertical gap between the ECDFs.
    dks, x_star, fa_star, fb_star = _ks_detail(true_alpha, recovered_alpha)
    if np.isfinite(dks) and dks > 0:
        ylo, yhi = sorted((fa_star, fb_star))
        ax.vlines(x_star, ylo, yhi, color="0.25", linewidth=1.1, zorder=5)
        ax.plot([x_star, x_star], [ylo, yhi], linestyle="none", marker="_",
                markersize=6, markeredgewidth=1.1, color="0.25", zorder=5)

    lo = min(0.95, float(np.nanmin([xt.min() if xt.size else 0.95,
                                    xr.min() if xr.size else 0.95])))
    hi = max(2.05, float(np.nanmax([xt.max() if xt.size else 2.05,
                                    xr.max() if xr.size else 2.05])))
    ax.set_xlim(lo, hi)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel(r"Coefficient parameter, $\alpha$")
    ax.set_ylabel(r"Empirical CDF")

    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.yaxis.set_major_locator(MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(MultipleLocator(0.125))
    ax.tick_params(which="major", length=4, width=0.9)
    ax.tick_params(which="minor", length=2, width=0.7)

    ax.grid(True, which="major", color="0.88", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    leg = ax.legend(frameon=False, loc="lower right", handlelength=1.9,
                    labelspacing=0.35, borderaxespad=0.4)
    leg.set_zorder(6)
    if np.isfinite(ks):
        ax.text(0.045, 0.955, rf"$D_{{\mathrm{{KS}}}} = {ks:.3f}$",
                transform=ax.transAxes, fontsize=9.5, va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="0.8", linewidth=0.6, alpha=0.9))
    fig.tight_layout(pad=0.5)

    out_dir = Path(out_dir)
    stem = out_dir / "coefficient_cdf_true_vs_recovered"
    written = []
    for ext in ("png", "pdf", "svg"):
        try:
            fig.savefig(f"{stem}.{ext}")
            written.append(f"{stem}.{ext}")
        except Exception as e:
            logger.warning("Failed to write %s.%s: %s", stem, ext, e)
    plt.close(fig)
    return written


def get_recovered_vs_true_cdf(app_control_parameters, parameters):
    """Compare true alpha distribution vs SIR-recovered alpha_hat via ECDFs.

    Requires a completed SIR run (uses the dilled ``model`` and its ``.psir``).
    """
    fig = go.Figure()

    model = app_control_parameters.get("model")
    if model is None:
        fig.update_layout(title="Run SIR first to recover coefficients")
        return fig

    directory = app_control_parameters.get("dataset_url") or DATASET_URL
    parameters = parameters or {}
    requested_equation = parameters.get("recovered_vs_true_cdf_equation") or ""
    true_source = parameters.get("recovered_vs_true_cdf_true_source") or "used"
    # The coefficient on the function value h encodes (alpha*pi)^2, regardless of
    # whether the target is 'h' (Double Derivative) or 'd2h' (Variable).
    value_variable = parameters.get("recovered_vs_true_cdf_value_variable") or "h"

    try:
        alpha_hat, filenames, n_invalid, eq_key = _recovered_alpha_from_model(
            model, value_variable, requested_equation
        )
    except Exception as e:
        logger.warning("Could not reconstruct recovered alpha: %s", e)
        fig.update_layout(title=f"Could not reconstruct recovered \u03b1: {e}")
        return fig

    recovered = alpha_hat[np.isfinite(alpha_hat)]

    # True alpha: either the realizations actually used in the run (paired,
    # most rigorous), or the entire dataset's latent draws.
    if true_source == "all" or not filenames:
        true_alpha, _ = get_true_coefficients(directory)
    else:
        true_alpha = np.asarray(
            [_alpha_from_file(f) for f in filenames], dtype=np.float64
        )
        true_alpha = true_alpha[np.isfinite(true_alpha)]

    if recovered.size == 0 or true_alpha.size == 0:
        fig.update_layout(title="No valid coefficients to compare")
        return fig

    ks = _ks_distance(true_alpha, recovered)
    logger.info(
        "SHO coefficient CDF [eq %s]: KS=%.4f, recovered n=%d (invalid=%d), "
        "true n=%d", eq_key, ks, recovered.size, n_invalid, true_alpha.size
    )

    # Vector-friendly static export for the manuscript.
    written = _export_cdf_figure(true_alpha, recovered, ks, Path(directory).parent)
    if written:
        logger.info("Wrote publication figures: %s", ", ".join(written))

    xt, yt = _ecdf(true_alpha)
    xr, yr = _ecdf(recovered)

    # Faint theoretical reference: alpha ~ U[1,2] has CDF = (alpha - 1) on [1,2].
    fig.add_trace(go.Scatter(
        x=[1.0, 2.0], y=[0.0, 1.0], mode="lines",
        line=dict(color="rgba(120,120,120,0.7)", width=1.2, dash="dot"),
        name="Ideal U[1,2]", hoverinfo="skip",
    ))

    # Mark the KS gap (largest vertical distance between the two ECDFs).
    dks, x_star, fa_star, fb_star = _ks_detail(true_alpha, recovered)
    if np.isfinite(dks) and dks > 0:
        fig.add_trace(go.Scatter(
            x=[x_star, x_star], y=sorted((fa_star, fb_star)), mode="lines+markers",
            line=dict(color="rgba(60,60,60,0.9)", width=1.6),
            marker=dict(symbol="line-ew", size=8,
                        line=dict(color="rgba(60,60,60,0.9)", width=1.6)),
            name=f"KS gap = {dks:.3f}", hoverinfo="name",
        ))

    fig.add_trace(go.Scatter(
        x=xt, y=yt, mode="lines+markers", line_shape="hv",
        line=dict(color=_COLOR_TRUE, width=2.4),
        marker=dict(color=_COLOR_TRUE, size=6,
                    line=dict(color="white", width=1)),
        name="True \u03b1",
    ))
    fig.add_trace(go.Scatter(
        x=xr, y=yr, mode="lines+markers", line_shape="hv",
        line=dict(color=_COLOR_RECOVERED, width=2.4, dash="dash"),
        marker=dict(color=_COLOR_RECOVERED, size=6, symbol="square",
                    line=dict(color="white", width=1)),
        name="Recovered \u03b1\u0302",
    ))

    lo = min(0.95, float(min(xt.min(), xr.min())))
    hi = max(2.05, float(max(xt.max(), xr.max())))
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Coefficient parameter, \u03b1",
        yaxis_title="Empirical CDF",
        font=dict(size=14),
        legend=dict(x=0.975, y=0.045, xanchor="right", yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.6)", borderwidth=0),
        margin=dict(l=70, r=25, t=30, b=55),
    )
    fig.update_xaxes(range=[lo, hi], dtick=0.2, showgrid=True,
                     gridcolor="rgba(0,0,0,0.07)", zeroline=False,
                     ticks="outside", mirror=False)
    fig.update_yaxes(range=[-0.02, 1.02], dtick=0.25, showgrid=True,
                     gridcolor="rgba(0,0,0,0.07)", zeroline=False,
                     ticks="outside", mirror=False)
    if np.isfinite(ks):
        fig.add_annotation(
            x=0.035, y=0.965, xref="paper", yref="paper",
            text=f"D<sub>KS</sub> = {ks:.3f}", showarrow=False,
            xanchor="left", yanchor="top",
            bordercolor="rgba(0,0,0,0.2)", borderwidth=1, borderpad=4,
            bgcolor="rgba(255,255,255,0.85)",
        )
    return fig


def get_true_parameter_distribution(app_control_parameters, parameters):
    """Histogram of the true oscillator coefficient (alpha*pi)^2 across the ensemble."""
    directory = app_control_parameters.get("dataset_url") or DATASET_URL
    quantity = parameters.get("true_parameter_distribution_quantity") or "coefficient"

    alphas, coeff = get_true_coefficients(directory)
    fig = go.Figure()
    if len(alphas) == 0:
        fig.update_layout(title="No realizations found")
        return fig

    if quantity == "alpha":
        values, title, xaxis = alphas, "True distribution of \u03b1", "\u03b1"
    else:
        values, title, xaxis = coeff, "True distribution of (\u03b1\u03c0)\u00b2", "(\u03b1\u03c0)\u00b2"

    fig.add_trace(go.Histogram(x=values, nbinsx=12, marker_color="#1f7a3d"))
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        yaxis_title="count",
        bargap=0.05,
    )
    return fig


def get_ensemble_overlay(app_control_parameters, parameters):
    """Overlay every realization's h(x) using the input plot data from a run."""
    input_data = app_control_parameters.get("input_data_dict") or []

    fig = go.Figure()
    if not input_data:
        fig.update_layout(title="Run SIR (or load data) to populate the ensemble")
        return fig

    for entry in input_data:
        try:
            data_items, name = entry
        except (TypeError, ValueError):
            continue
        for series in data_items:
            try:
                x, y = series
            except (TypeError, ValueError):
                continue
            fig.add_trace(go.Scatter(
                x=np.asarray(x).reshape(-1), y=np.asarray(y).reshape(-1),
                mode="lines", opacity=0.5, name=name, showlegend=False,
            ))

    fig.update_layout(title="Ensemble overlay", xaxis_title="x", yaxis_title="value")
    return fig


def get_provider(_=None):
    def fetch_data(identifier, knames):
        df = pd.read_parquet(identifier)
        df = _ensure_requested_columns(df, knames)
        for key in knames:
            if key not in df.columns:
                raise KeyError(f"column {key!r} missing in {identifier}")

        data = np.array([df[key].to_numpy(dtype=np.float64) for key in knames])
        xflags = np.ones(len(knames), dtype=bool)

        timing_data = np.array([df["times"].to_numpy(dtype=np.float64)])
        # freq MUST be a Python float (scipy.signal.iirfilter calls float(wo)).
        freq = float(timing_data[0, 1] - timing_data[0, 0])
        smooth_rate = 0.2
        return data, xflags, timing_data, freq, smooth_rate

    def fetch_identifier_variables(identifier, key):
        df = pd.read_parquet(identifier)
        df = _ensure_requested_columns(df, [key])
        if key not in df.columns:
            raise KeyError(f"column {key!r} missing in {identifier}")
        return df[key].to_numpy(dtype=np.float64)

    def fetch_identifiers_from_url(directory):
        return sorted(
            path.join(directory, name)
            for name in listdir(directory)
            if name.endswith(".parquet")
        )

    def fetch_dataset_variables(directory):
        return _discover_variables(directory)

    available_vars = _discover_variables(DATASET_URL)

    custom_grapher_dictionary = {
        "recovered_vs_true_cdf": {
            "display_name": "Recovered vs true \u03b1 (ECDF)",
            "requires": ["model"],
            "parameters": {
                "true_source": {
                    "default": "used",
                    "options": {
                        "Realizations used in run": "used",
                        "All dataset realizations": "all",
                    },
                    "display_name": "True \u03b1 source",
                },
                "value_variable": {
                    "default": "h",
                    "display_name": "Function value variable (coeff source)",
                },
                "equation": {
                    "default": "",
                    "display_name": "Equation key (blank = auto)",
                },
            },
            "function": get_recovered_vs_true_cdf,
        },
        "true_parameter_distribution": {
            "display_name": "True parameter distribution",
            "parameters": {
                "quantity": {
                    "default": "coefficient",
                    "options": {
                        "(\u03b1\u03c0)\u00b2 coefficient": "coefficient",
                        "\u03b1": "alpha",
                    },
                    "display_name": "Quantity",
                },
            },
            "function": get_true_parameter_distribution,
        },
        "ensemble_overlay": {
            "display_name": "Ensemble overlay",
            "requires": ["input_data_dict"],
            "parameters": {},
            "function": get_ensemble_overlay,
        },
    }

    return {
        "fetch_data": fetch_data,
        "fetch_identifier_variables": fetch_identifier_variables,
        "fetch_identifiers_from_url": fetch_identifiers_from_url,
        "fetch_dataset_variables": fetch_dataset_variables,
        "dataset_url": DATASET_URL,
        "custom_grapher_dictionary": custom_grapher_dictionary,
    }


if __name__ == "__main__":
    prov = get_provider()
    assert get_provider(None)  # Modalia-style call must not raise.

    ids = prov["fetch_identifiers_from_url"](prov["dataset_url"])
    print(f"dataset_url: {prov['dataset_url']}")
    print(f"{len(ids)} identifiers (showing first 3): {[Path(i).name for i in ids[:3]]}")

    vars_ = prov["fetch_dataset_variables"](prov["dataset_url"])
    print(f"signals: {vars_}")
    assert len(ids) > 0 and len(vars_) > 0

    knames = vars_[: min(3, len(vars_))]
    data, xflags, timing_data, freq, smooth = prov["fetch_data"](ids[0], knames)
    assert data.dtype == np.float64
    assert data.shape == (len(knames), timing_data.shape[1])
    assert timing_data.shape == (1, data.shape[1])
    assert len(xflags) == len(knames)
    assert isinstance(freq, float)

    alphas, coeff = get_true_coefficients(prov["dataset_url"])
    print(f"true alpha range: [{alphas.min():.4f}, {alphas.max():.4f}]  "
          f"(alpha*pi)^2 range: [{coeff.min():.3f}, {coeff.max():.3f}]")
    print(f"OK - data {data.shape}  freq={freq:.6g}  smooth_rate={smooth}")
