"""Held-out autonomous prediction phase portrait (dFL grapher)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_TRACE_COLORS = [
    "#1D6996", "#CC503E", "#0F8554", "#E17C05", "#5F4690",
    "#38A6A5", "#94346E", "#EDAD08", "#6F4070", "#73AF48",
]


def load_prediction_model():
    candidates = [
        Path(__file__).resolve().parent / "Prediction_model",
        Path(r"D:\SIR_paper\Pendulum\Prediction_model"),
    ]
    for folder in candidates:
        if (folder / "prediction_model.py").is_file():
            text = str(folder)
            if text not in sys.path:
                sys.path.insert(0, text)
            import prediction_model as pm

            return pm
    raise ImportError("Pendulum Prediction_model/prediction_model.py was not found")


def fetch_theta_omega(dc, record_id: str):
    record = dc.fetch_data_async(
        dc.data_folder,
        "pendulum",
        record_id,
        ["theta", "omega"],
        {},
        trim_1=None,
        trim_2=None,
    )
    if not isinstance(record, dict):
        return None
    signals = {s["data_name"]: s for s in (record.get("signals") or [])}
    if "theta" not in signals or "omega" not in signals:
        return None
    theta = np.asarray(signals["theta"]["data"], dtype=np.float64)
    omega = np.asarray(signals["omega"]["data"], dtype=np.float64)
    times = np.asarray(signals["theta"].get("times"), dtype=np.float64)
    if theta.size == 0 or theta.shape != omega.shape:
        return None
    if times.shape != theta.shape:
        times = np.arange(theta.size, dtype=np.float64)
    return times, theta, omega


def format_sci(value: float) -> str:
    if not np.isfinite(value):
        return "n/a"
    if value == 0:
        return "0"
    abs_value = abs(value)
    if abs_value < 1e-3 or abs_value >= 1e3:
        return f"{value:.3e}"
    return f"{value:.4g}"


def heldout_predictive_phase_portrait_grapher(
    app_control_parameters,
    parameters,
    *,
    holdout_ids,
    parse_holdout_ids,
    available_record_ids,
):
    """Protected holdout autonomous rollouts in (theta, omega) phase space."""
    import plotly.graph_objects as go

    pm = load_prediction_model()
    dc = app_control_parameters["data_coordinator"]
    available = set(available_record_ids(dc.data_folder))
    holdouts = [rid for rid in holdout_ids if rid in available]
    record_ids = parse_holdout_ids(
        parameters.get("records"),
        app_control_parameters.get("record_id"),
        holdouts,
    )
    fig = go.Figure()
    if not record_ids:
        return fig.update_layout(
            title="Protected held-out autonomous rollouts — no holdouts selected"
        )

    horizon = float(parameters.get("horizon_s", 30.0))
    overlay_audit = str(parameters.get("overlay_exact_audit", "off")).strip().lower() in {
        "on", "true", "1", "yes",
    }
    show_legend = len(record_ids) <= 4 or (len(record_ids) <= 8 and not overlay_audit)
    theta_err = []
    omega_err = []
    plotted = 0
    last_rid = ""

    for i, rid in enumerate(record_ids):
        fetched = fetch_theta_omega(dc, rid)
        if fetched is None:
            continue
        times, theta_obs, omega_obs = fetched
        bundle = pm.rollout_from_observed(times, theta_obs, omega_obs)
        mask = bundle["times"] <= horizon + 1e-12
        color = _TRACE_COLORS[i % len(_TRACE_COLORS)]
        fig.add_trace(go.Scatter(
            x=bundle["theta_true"][mask],
            y=bundle["omega_true"][mask],
            mode="lines",
            line=dict(color=color, width=2.0),
            name=f"{rid} true",
            legendgroup=rid,
            showlegend=show_legend,
        ))
        fig.add_trace(go.Scatter(
            x=bundle["theta_sir"][mask],
            y=bundle["omega_sir"][mask],
            mode="lines",
            line=dict(color=color, width=2.0, dash="dash"),
            name=f"{rid} SIR",
            legendgroup=rid,
            showlegend=show_legend,
        ))
        if overlay_audit:
            fig.add_trace(go.Scatter(
                x=bundle["theta_exact_audit"][mask],
                y=bundle["omega_exact_audit"][mask],
                mode="lines",
                line=dict(color=color, width=1.4, dash="dot"),
                name=f"{rid} exact audit",
                legendgroup=rid,
                showlegend=show_legend,
            ))
        theta_err.append(bundle["theta_error_sir"][mask])
        omega_err.append(bundle["omega_error_sir"][mask])
        plotted += 1
        last_rid = rid

    if plotted == 0:
        return fig.update_layout(
            title="Protected held-out autonomous rollouts — no trajectories"
        )

    th = np.concatenate(theta_err)
    om = np.concatenate(omega_err)
    title = "PROTECTED HELD-OUT AUTONOMOUS ROLLOUTS"
    if plotted == 1:
        title = f"{title} · {last_rid}"
    else:
        title = f"{title} · {plotted} holdouts"
    title = f"{title} · horizon {horizon:g} s"
    fig.update_layout(
        title=title,
        xaxis_title="theta",
        yaxis_title="omega",
        legend=dict(
            title="True vs SIR prediction",
            bgcolor="rgba(255,255,255,0.8)",
        ),
        template="plotly_white",
        annotations=[
            dict(
                text=(
                    "HELD-OUT AUTONOMOUS PREDICTION<br>"
                    "solid: true holdout · dashed: SIR rollout<br>"
                    "initialized at t=0 only; sin(theta_hat)<br>"
                    f"a = {pm.SIR_A:g}, b = {pm.SIR_B:g}<br>"
                    f"pooled RMSE theta = {format_sci(float(np.sqrt(np.mean(th**2))))}<br>"
                    f"pooled RMSE omega = {format_sci(float(np.sqrt(np.mean(om**2))))}"
                    + ("<br>dotted: exact-coefficient audit" if overlay_audit else "")
                ),
                xref="paper",
                yref="paper",
                x=0.01,
                y=0.99,
                xanchor="left",
                yanchor="top",
                showarrow=False,
                align="left",
                bgcolor="rgba(255,255,255,0.88)",
                bordercolor="#888888",
                borderwidth=1,
                font=dict(size=11),
            ),
        ],
    )
    return fig
