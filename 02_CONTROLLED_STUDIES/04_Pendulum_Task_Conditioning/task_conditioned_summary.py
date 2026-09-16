"""dFL custom grapher: task-conditioned pendulum compression + prediction summary."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

_PANEL_DATA_CANDIDATES = [
    Path(__file__).resolve().parent / "Plotter" / "panel_data.py",
    Path(r"D:\SIR_paper\Pendulum\Plotter\panel_data.py"),
]


def _panel_data():
    for path in _PANEL_DATA_CANDIDATES:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("pendulum_panel_data", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("Pendulum/Plotter/panel_data.py was not found")


def _parse_ids(raw, default, known):
    text = str(raw or "").strip()
    known_set = set(known)
    if not text or text.lower() in {"default", ""}:
        return list(default)
    if text.lower() in {"all", "*"}:
        return list(known)
    chosen, seen = [], set()
    for part in text.replace(";", ",").split(","):
        rid = part.strip()
        if rid and rid not in seen and rid in known_set:
            chosen.append(rid)
            seen.add(rid)
    return chosen or list(default)


def _sci(value: float) -> str:
    if not np.isfinite(value) or value == 0:
        return "n/a"
    exp = int(np.floor(np.log10(abs(value))))
    mant = value / (10.0 ** exp)
    return f"{mant:.2f}×10^{exp}"


def task_conditioned_pendulum_grapher(app_control_parameters, parameters):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    pdmod = _panel_data()
    dc = app_control_parameters["data_coordinator"]
    available = sorted(p.stem for p in Path(dc.data_folder).glob("*.parquet"))
    comp_ids = _parse_ids(
        parameters.get("compression_records"),
        pdmod.DEFAULT_COMPRESSION_IDS,
        available,
    )
    holdout = str(parameters.get("holdout") or pdmod.DEFAULT_HOLDOUT_ID).strip()
    if holdout not in set(pdmod.HOLDOUT_RECORD_IDS):
        holdout = pdmod.DEFAULT_HOLDOUT_ID

    traces = pdmod.load_compression(tuple(comp_ids))
    pooled = pdmod.load_pooled_rmse()
    phase = pdmod.subsample_phase(pdmod.load_prediction_bundle(holdout), step=3)

    fig = make_subplots(
        rows=2,
        cols=2,
        column_widths=[0.54, 0.46],
        row_heights=[0.46, 0.54],
        specs=[[{"rowspan": 2}, {}], [None, {}]],
        horizontal_spacing=0.10,
        vertical_spacing=0.16,
        subplot_titles=(
            "Compression  ·  conserved representation",
            f"Prediction  ·  {holdout}",
            "Pooled holdout RMSE vs horizon",
        ),
    )

    for tr in traces:
        fig.add_trace(
            go.Scatter(
                x=tr["x_line"],
                y=tr["y_line"],
                mode="lines",
                line=dict(color=tr["color"], width=2.2),
                name=tr["record_id"],
                legendgroup="comp",
                showlegend=False,
                hovertemplate=f"{tr['record_id']}<br>B_i={tr['intercept']:.4g}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=tr["x"],
                y=tr["y"],
                mode="markers",
                marker=dict(size=4, color=tr["color"], opacity=0.28),
                name=tr["record_id"] + " data",
                legendgroup="comp",
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=phase["theta_true"],
            y=phase["omega_true"],
            mode="lines",
            line=dict(color=pdmod.TRUE_COLOR, width=2.0),
            name="true",
            legendgroup="pred",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=phase["theta_sir"],
            y=phase["omega_sir"],
            mode="lines",
            line=dict(color=pdmod.PRED_COLOR, width=1.8, dash="dash"),
            name="SIR rollout",
            legendgroup="pred",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[phase["theta0"]],
            y=[phase["omega0"]],
            mode="markers",
            marker=dict(size=9, color="white", line=dict(color="#1f1f1f", width=1.4)),
            name="t = 0",
            legendgroup="pred",
        ),
        row=1,
        col=2,
    )

    h_th = pooled["sir"]["theta"]["horizon_s"]
    r_th = pooled["sir"]["theta"]["rmse"]
    h_om = pooled["sir"]["omega"]["horizon_s"]
    r_om = pooled["sir"]["omega"]["rmse"]
    fig.add_trace(
        go.Scatter(
            x=h_th,
            y=r_th,
            mode="lines+markers",
            line=dict(color=pdmod.TRUE_COLOR, width=2.2),
            marker=dict(size=7, color="white", line=dict(color=pdmod.TRUE_COLOR, width=1.4)),
            name="RMSE θ",
        ),
        row=2,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=h_om,
            y=r_om,
            mode="lines+markers",
            line=dict(color=pdmod.PRED_COLOR, width=2.2),
            marker=dict(
                size=7,
                symbol="square",
                color="white",
                line=dict(color=pdmod.PRED_COLOR, width=1.4),
            ),
            name="RMSE ω",
        ),
        row=2,
        col=2,
    )

    rmse_th_30 = float(r_th[-1])
    rmse_om_30 = float(r_om[-1])
    fig.update_xaxes(title_text="1 − cos(θ)", row=1, col=1)
    fig.update_yaxes(title_text="ω²", row=1, col=1)
    fig.update_xaxes(title_text="θ", row=1, col=2)
    fig.update_yaxes(title_text="ω", row=1, col=2)
    fig.update_xaxes(title_text="prediction horizon (s)", row=2, col=2)
    fig.update_yaxes(title_text="pooled RMSE", type="log", row=2, col=2)
    fig.update_layout(
        title=(
            "Same observational ensemble + different task contracts "
            "→ different qualified models"
        ),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=1.0, xanchor="right"),
        annotations=[
            dict(
                text=(
                    f"ω² = −3.645 (1−cos θ) + 2E_i<br>"
                    f"R²(B_i, 2E_i) = {pdmod.R2_B_VS_2E:.9f}<br><br>"
                    f"θ̇ = ω,  ω̇ = {pdmod.SIR_A} sin θ<br>"
                    "autonomous from t=0 only<br>"
                    f"30 s RMSE θ = {_sci(rmse_th_30)} rad<br>"
                    f"30 s RMSE ω = {_sci(rmse_om_30)} rad s⁻¹"
                ),
                xref="paper",
                yref="paper",
                x=0.01,
                y=0.01,
                xanchor="left",
                yanchor="bottom",
                showarrow=False,
                align="left",
                bgcolor="rgba(247,248,244,0.92)",
                bordercolor="#d4d4d4",
                borderwidth=1,
                font=dict(size=11),
            ),
        ],
    )
    return fig
