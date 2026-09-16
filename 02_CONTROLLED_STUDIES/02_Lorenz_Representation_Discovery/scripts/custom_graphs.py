"""Custom graphers for the Lorenz paper example."""
from __future__ import annotations

import numpy as np


def power_spectrum_grapher(app_control_parameters, parameters):
    """Welch power spectrum of one variable on the selected record."""
    import plotly.graph_objects as go
    from scipy.signal import welch

    variable = str(parameters.get("variable") or "x")
    nperseg = int(parameters.get("nperseg") or 256)
    dc = app_control_parameters["data_coordinator"]
    record = dc.fetch_data_async(
        dc.data_folder,
        "lorenz",
        app_control_parameters.get("record_id"),
        [variable],
        {},
        trim_1=app_control_parameters.get("trim_t1"),
        trim_2=app_control_parameters.get("trim_t2"),
    )
    fig = go.Figure()
    signals = record.get("signals") or []
    if not signals:
        return fig.update_layout(title=f"No data for {variable}")
    values = np.asarray(signals[0]["data"], dtype=np.float64)
    times = np.asarray(signals[0]["times"], dtype=np.float64)
    if times.size < 2:
        return fig.update_layout(title=f"Not enough samples for {variable}")
    dt = float(times[1] - times[0])
    if dt <= 0:
        return fig.update_layout(title="Non-positive time step")
    seg = max(1, min(nperseg, values.size))
    freqs, psd = welch(values, fs=1.0 / dt, nperseg=seg)
    fig.add_trace(go.Scatter(x=freqs, y=psd, mode="lines", name=variable))
    return fig.update_layout(
        title=f"Power spectrum ({variable})",
        xaxis_title="Frequency (Hz)",
        yaxis_title="PSD",
        yaxis_type="log",
    )


def equation_overlay_grapher(app_control_parameters, parameters):
    """Overlay SIR reconstructed output on the target signal."""
    import plotly.graph_objects as go
    from worker.provider_api import sir_results

    sir = sir_results(app_control_parameters)
    fig = go.Figure()
    if not sir.available:
        return fig.update_layout(title="Run SIR first to populate equations")
    names = sir.equation_names
    if not names:
        return fig.update_layout(title="SIR run has no equations")
    equation = names[0]
    for i, (predicted, actual, x) in enumerate(sir.fit(equation)):
        fig.add_trace(go.Scatter(
            x=x, y=actual, mode="lines", name="data",
            line={"color": "#888888", "width": 1.0, "dash": "dot"},
            showlegend=i == 0, legendgroup="data",
        ))
        fig.add_trace(go.Scatter(
            x=x, y=predicted, mode="lines", name=equation,
            showlegend=i == 0, legendgroup="fit",
        ))
    return fig.update_layout(
        title=f"Discovered equation overlay · {equation} · target {sir.target_variable}",
        xaxis_title="time",
        yaxis_title="value",
    )


def build_custom_graphers(available_vars: list[str] | None = None) -> dict:
    variables = list(available_vars or ["x", "y", "z"])
    options = {v: v for v in variables} if variables else {"x": "x"}
    return {
        "power_spectrum": {
            "function": power_spectrum_grapher,
            "requires_signals": False,
            "display_name": "Power spectrum (Welch)",
            "parameters": {
                "variable": {
                    "default": variables[0] if variables else "x",
                    "options": options,
                    "display_name": "Variable",
                },
                "nperseg": {
                    "default": 256,
                    "min": 8,
                    "step": 1,
                    "display_name": "Segment length (nperseg)",
                },
            },
        },
        "equation_overlay": {
            "function": equation_overlay_grapher,
            "requires_signals": False,
            "requires": ["formulas", "model"],
            "display_name": "Discovered equation overlay",
            "parameters": {},
        },
    }
