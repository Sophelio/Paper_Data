"""Custom graphers for the stochastic oscillator ensemble."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _true_alphas(folder) -> np.ndarray:
    alphas = []
    for path in sorted(Path(folder).glob("*.parquet")):
        try:
            df = pd.read_parquet(path, columns=["alpha"])
        except Exception:
            df = pd.read_parquet(path)
        if "alpha" in df.columns and len(df):
            alphas.append(float(df["alpha"].iloc[0]))
    return np.asarray(alphas, dtype=np.float64)


def true_parameter_distribution_grapher(app_control_parameters, parameters):
    import plotly.graph_objects as go

    dc = app_control_parameters["data_coordinator"]
    quantity = str(parameters.get("quantity") or "coefficient")
    alphas = _true_alphas(dc.data_folder)
    fig = go.Figure()
    if alphas.size == 0:
        return fig.update_layout(title="No realizations found")
    if quantity == "alpha":
        values, title, xaxis = alphas, "True distribution of α", "α"
    else:
        values = (alphas * np.pi) ** 2
        title, xaxis = "True distribution of (απ)²", "(απ)²"
    fig.add_trace(go.Histogram(x=values, nbinsx=12, marker_color="#1f7a3d"))
    return fig.update_layout(title=title, xaxis_title=xaxis, yaxis_title="count", bargap=0.05)


def ensemble_overlay_grapher(app_control_parameters, parameters):
    """Overlay h(x) for every realization in the data folder."""
    import plotly.graph_objects as go

    dc = app_control_parameters["data_coordinator"]
    signal = str(parameters.get("signal") or "h")
    fig = go.Figure()
    n = 0
    for path in sorted(Path(dc.data_folder).glob("*.parquet")):
        df = pd.read_parquet(path)
        if signal not in df.columns or "times" not in df.columns:
            continue
        fig.add_trace(go.Scatter(
            x=df["times"].to_numpy(dtype=np.float64),
            y=df[signal].to_numpy(dtype=np.float64),
            mode="lines",
            opacity=0.45,
            name=path.stem,
            showlegend=False,
        ))
        n += 1
    if n == 0:
        return fig.update_layout(title=f"No {signal} series found")
    return fig.update_layout(
        title=f"Ensemble overlay · {n} realizations · {signal}",
        xaxis_title="x",
        yaxis_title=signal,
    )


def recovered_vs_true_cdf_grapher(app_control_parameters, parameters):
    """Compare true α vs SIR-recovered α̂ from the [h] coefficient."""
    import plotly.graph_objects as go
    from worker.provider_api import sir_results

    fig = go.Figure()
    sir = sir_results(app_control_parameters)
    if not sir.available:
        return fig.update_layout(title="Run SIR first to recover coefficients")

    value_variable = str(parameters.get("value_variable") or "h")
    value_term = f"[{value_variable}]"
    wanted = str(parameters.get("equation") or "").strip()
    names = list(sir.equation_names or [])
    equation = wanted if wanted in names else (names[0] if names else "")
    if not equation:
        return fig.update_layout(title="SIR run has no equations")

    coeff, term_names = sir.coefficients(equation)
    term_names = [str(n) for n in term_names]
    if value_term not in term_names:
        return fig.update_layout(
            title=f"No recovered equation contains {value_term}. Terms: {term_names}"
        )
    b = np.asarray(coeff, dtype=np.float64)[:, term_names.index(value_term)]
    ratio = -b
    valid = np.isfinite(ratio) & (ratio > 0.0)
    recovered = np.full_like(ratio, np.nan)
    recovered[valid] = np.sqrt(ratio[valid]) / np.pi
    recovered = recovered[np.isfinite(recovered)]

    dc = app_control_parameters["data_coordinator"]
    true_alpha = _true_alphas(dc.data_folder)
    if recovered.size == 0 or true_alpha.size == 0:
        return fig.update_layout(title="No valid coefficients to compare")

    def ecdf(values):
        v = np.sort(np.asarray(values, dtype=np.float64))
        y = np.arange(1, v.size + 1, dtype=np.float64) / v.size
        return v, y

    xt, yt = ecdf(true_alpha)
    xr, yr = ecdf(recovered)
    fig.add_trace(go.Scatter(x=xt, y=yt, mode="lines", line_shape="hv", name="True α"))
    fig.add_trace(go.Scatter(x=xr, y=yr, mode="lines", line_shape="hv", name="Recovered α̂"))
    return fig.update_layout(
        title=f"Recovered vs true α · {equation}",
        xaxis_title="α",
        yaxis_title="Empirical CDF",
    )


def build_custom_graphers() -> dict:
    return {
        "true_parameter_distribution": {
            "function": true_parameter_distribution_grapher,
            "requires_signals": False,
            "display_name": "True parameter distribution",
            "parameters": {
                "quantity": {
                    "default": "coefficient",
                    "options": {
                        "(απ)² coefficient": "coefficient",
                        "α": "alpha",
                    },
                    "display_name": "Quantity",
                },
            },
        },
        "ensemble_overlay": {
            "function": ensemble_overlay_grapher,
            "requires_signals": False,
            "display_name": "Ensemble overlay",
            "parameters": {
                "signal": {
                    "default": "h",
                    "options": {"h": "h", "dh": "dh", "d2h": "d2h"},
                    "display_name": "Signal",
                },
            },
        },
        "recovered_vs_true_cdf": {
            "function": recovered_vs_true_cdf_grapher,
            "requires_signals": False,
            "requires": ["formulas", "model"],
            "display_name": "Recovered vs true α (ECDF)",
            "parameters": {
                "value_variable": {
                    "default": "h",
                    "display_name": "Function value variable",
                },
                "equation": {
                    "default": "",
                    "display_name": "Equation key (blank = first)",
                },
            },
        },
    }
