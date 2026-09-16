"""Custom graphers for the pendulum ensemble (audit / exploration only)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Qualitative palette so nearby realizations stay distinguishable.
_TRACE_COLORS = [
    "#1D6996", "#CC503E", "#0F8554", "#E17C05", "#5F4690",
    "#38A6A5", "#94346E", "#EDAD08", "#6F4070", "#73AF48",
]
_LEGEND_CAP = 12
_DEFAULT_SLOPE = -3.645
_VIRTUAL_XY = ["one_minus_cos_theta", "omega_squared"]
_HOLDOUT_RECORD_IDS = (
    "pendulum_003",
    "pendulum_007",
    "pendulum_011",
    "pendulum_015",
    "pendulum_019",
    "pendulum_023",
    "pendulum_027",
    "pendulum_031",
)


def _available_record_ids(data_folder) -> list[str]:
    return sorted(p.stem for p in Path(data_folder).glob("*.parquet"))


def _parse_record_ids(raw: object, current: object, available: list[str]) -> list[str]:
    """Resolve the grapher's record list.

    Dalia's graph card supplies a single ``record_id``. Extra realizations
    are selected via the grapher's ``records`` text field: comma-separated
    ids, or ``all``. An empty field uses the currently selected record.
    """
    known = list(available)
    known_set = set(known)
    text = str(raw or "").strip()
    current_id = str(current or "").strip()

    if not text:
        chosen = [current_id] if current_id in known_set else []
        if not chosen and known:
            chosen = [known[0]]
        return chosen

    if text.lower() in {"all", "*"}:
        return known

    chosen: list[str] = []
    seen: set[str] = set()
    for part in text.replace(";", ",").split(","):
        rid = part.strip()
        if not rid or rid in seen:
            continue
        if rid in known_set:
            chosen.append(rid)
            seen.add(rid)
    return chosen


def _fetch_virtual_xy(dc, record_id: str, trim_t1, trim_t2, with_times: bool = False):
    record = dc.fetch_data_async(
        dc.data_folder,
        "pendulum",
        record_id,
        list(_VIRTUAL_XY),
        {},
        trim_1=trim_t1,
        trim_2=trim_t2,
    )
    if not isinstance(record, dict):
        return None
    signals = {s["data_name"]: s for s in (record.get("signals") or [])}
    if any(name not in signals for name in _VIRTUAL_XY):
        return None
    x = np.asarray(signals["one_minus_cos_theta"]["data"], dtype=np.float64)
    y = np.asarray(signals["omega_squared"]["data"], dtype=np.float64)
    if x.size == 0 or y.size == 0 or x.shape != y.shape:
        return None
    if not with_times:
        return x, y
    times = np.asarray(signals["one_minus_cos_theta"].get("times"), dtype=np.float64)
    if times.shape != x.shape:
        times = np.arange(x.size, dtype=np.float64)
    return x, y, times


def _parse_holdout_ids(raw: object, current: object, holdouts: list[str]) -> list[str]:
    """Select among the protected holdout realizations only.

    Blank field: the currently selected record if it is a holdout, otherwise
    the full holdout set. ``all`` is the eight protected ids, not the training
    ensemble.
    """
    text = str(raw or "").strip()
    current_id = str(current or "").strip()
    known = list(holdouts)
    if not text:
        if current_id in set(known):
            return [current_id]
        return known
    return _parse_record_ids(text, current, known)


def _format_sci(value: float) -> str:
    if not np.isfinite(value):
        return "n/a"
    if value == 0:
        return "0"
    abs_value = abs(value)
    if abs_value < 1e-3 or abs_value >= 1e3:
        return f"{value:.3e}"
    return f"{value:.4g}"


def transfer_from_first_observation(x, y, times, slope: float):
    """Frozen-slope transfer using only the earliest sample for B_i.

    Returns intercept B, predicted omega^2, t0 index, later-time RMSE,
    later-time max |error|, and the later-time residual vector. The slope
    is never refit; later samples are used only for validation.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    times = np.asarray(times, dtype=np.float64)
    if x.size == 0 or x.shape != y.shape or times.shape != x.shape:
        raise ValueError("transfer_from_first_observation needs aligned x, y, times")
    i0 = int(np.argmin(times))
    intercept = float(y[i0] - slope * x[i0])
    predicted = slope * x + intercept
    later = np.ones(x.shape, dtype=bool)
    later[i0] = False
    later &= times > times[i0]
    if not np.any(later):
        later = np.ones(x.shape, dtype=bool)
        later[i0] = False
    residuals = y[later] - predicted[later]
    if residuals.size == 0:
        rmse = float("nan")
        max_abs = float("nan")
    else:
        rmse = float(np.sqrt(np.mean(residuals**2)))
        max_abs = float(np.max(np.abs(residuals)))
    return intercept, predicted, i0, rmse, max_abs, residuals


def _overlay_on(parameters: dict) -> bool:
    raw = parameters.get("overlay_reference", "off")
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() in {"on", "true", "1", "yes"}


def _load_prediction_model():
    return _heldout_predictive_phase_module().load_prediction_model()


def _heldout_predictive_phase_module():
    import importlib.util

    candidates = [
        Path(__file__).resolve().parent / "heldout_predictive_phase.py",
        Path(r"D:\SIR_paper\Pendulum\heldout_predictive_phase.py"),
    ]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("heldout_predictive_phase", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("heldout_predictive_phase.py was not found")


def invariant_representation_grapher(app_control_parameters, parameters):
    """Scatter of omega^2 vs 1-cos(theta) for one or more realizations."""
    import plotly.graph_objects as go

    dc = app_control_parameters["data_coordinator"]
    available = _available_record_ids(dc.data_folder)
    record_ids = _parse_record_ids(
        parameters.get("records"),
        app_control_parameters.get("record_id"),
        available,
    )
    fig = go.Figure()
    if not record_ids:
        return fig.update_layout(title="No pendulum realizations selected")

    slope = float(parameters.get("slope", _DEFAULT_SLOPE))
    overlay = _overlay_on(parameters)
    show_legend = len(record_ids) <= _LEGEND_CAP
    trim_t1 = app_control_parameters.get("trim_t1")
    trim_t2 = app_control_parameters.get("trim_t2")

    plotted = 0
    for i, rid in enumerate(record_ids):
        xy = _fetch_virtual_xy(dc, rid, trim_t1, trim_t2)
        if xy is None:
            continue
        x, y = xy
        color = _TRACE_COLORS[i % len(_TRACE_COLORS)]
        order = np.argsort(x, kind="mergesort")
        fig.add_trace(go.Scatter(
            x=x[order],
            y=y[order],
            mode="lines+markers",
            marker=dict(size=4, color=color, opacity=0.55),
            line=dict(color=color, width=1.6),
            name=rid,
            legendgroup=rid,
            showlegend=show_legend,
        ))
        if overlay:
            intercept = float(np.mean(y - slope * x))
            x_line = np.linspace(float(np.min(x)), float(np.max(x)), 40)
            y_line = slope * x_line + intercept
            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                line=dict(color=color, width=1.6, dash="dash"),
                name=f"SIR ref · {rid}",
                legendgroup=f"{rid}-ref",
                showlegend=show_legend,
                hovertemplate=(
                    f"SIR reference<br>slope={slope:g}<br>"
                    f"intercept={intercept:.4g}<extra>{rid}</extra>"
                ),
            ))
        plotted += 1

    if plotted == 0:
        return fig.update_layout(
            title="Pendulum invariant representation — no virtual coordinates"
        )

    title = "Pendulum invariant representation"
    if plotted > 1:
        title = f"{title} · {plotted} realizations"
    if overlay:
        title = f"{title} · SIR slope {slope:g} (reference)"

    return fig.update_layout(
        title=title,
        xaxis_title="1 - cos(theta)",
        yaxis_title="omega^2",
        legend=dict(
            title="Realization" if not overlay else "Realization / SIR reference",
            bgcolor="rgba(255,255,255,0.75)",
        ),
        template="plotly_white",
    )


def phase_portrait_grapher(app_control_parameters, parameters):
    """Phase portrait of the selected record: omega vs theta."""
    import plotly.graph_objects as go

    dc = app_control_parameters["data_coordinator"]
    record = dc.fetch_data_async(
        dc.data_folder,
        "pendulum",
        app_control_parameters.get("record_id"),
        ["theta", "omega"],
        {},
        trim_1=app_control_parameters.get("trim_t1"),
        trim_2=app_control_parameters.get("trim_t2"),
    )
    fig = go.Figure()
    signals = {s["data_name"]: s for s in (record.get("signals") or [])}
    if "theta" not in signals or "omega" not in signals:
        return fig.update_layout(title="Need theta and omega")
    fig.add_trace(go.Scatter(
        x=np.asarray(signals["theta"]["data"], dtype=np.float64),
        y=np.asarray(signals["omega"]["data"], dtype=np.float64),
        mode="lines",
        name=str(record.get("id") or "record"),
    ))
    return fig.update_layout(
        title="Phase portrait · ω vs θ",
        xaxis_title="θ (rad)",
        yaxis_title="ω (rad/s)",
    )


def ensemble_overlay_grapher(app_control_parameters, parameters):
    """Overlay one raw coordinate across every realization parquet."""
    import plotly.graph_objects as go

    dc = app_control_parameters["data_coordinator"]
    signal = str(parameters.get("signal") or "theta")
    fig = go.Figure()
    n = 0
    folder = Path(dc.data_folder)
    for path in sorted(folder.glob("*.parquet")):
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
        xaxis_title="t (s)",
        yaxis_title=signal,
    )


def heldout_transfer_grapher(app_control_parameters, parameters):
    """Held-out transfer: freeze A, infer B_i from the first observation only."""
    import plotly.graph_objects as go

    dc = app_control_parameters["data_coordinator"]
    available = set(_available_record_ids(dc.data_folder))
    holdouts = [rid for rid in _HOLDOUT_RECORD_IDS if rid in available]
    record_ids = _parse_holdout_ids(
        parameters.get("records"),
        app_control_parameters.get("record_id"),
        holdouts,
    )
    fig = go.Figure()
    if not record_ids:
        return fig.update_layout(
            title="Held-out transfer — no protected holdout realizations selected"
        )

    slope = float(parameters.get("slope", _DEFAULT_SLOPE))
    show_legend = len(record_ids) <= _LEGEND_CAP
    t0_x, t0_y, t0_text = [], [], []
    pooled = []
    plotted = 0
    last_rid = ""

    for i, rid in enumerate(record_ids):
        fetched = _fetch_virtual_xy(dc, rid, None, None, with_times=True)
        if fetched is None:
            continue
        x, y, times = fetched
        intercept, _predicted, i0, rmse, _max_abs, residuals = (
            transfer_from_first_observation(x, y, times, slope)
        )
        if residuals.size:
            pooled.append(residuals)
        color = _TRACE_COLORS[i % len(_TRACE_COLORS)]
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(size=4, color=color, opacity=0.42),
            name=f"{rid} observed",
            legendgroup=rid,
            showlegend=show_legend,
            hovertemplate=(
                f"{rid} observed<br>"
                f"RMSE={_format_sci(rmse)}<br>"
                "1-cos(theta)=%{x:.4g}<br>"
                "omega^2=%{y:.4g}<extra></extra>"
            ),
        ))
        x_min = float(np.min(x))
        x_max = float(np.max(x))
        x_line = np.array([x_min, x_max], dtype=np.float64)
        if x_min == x_max:
            x_line = np.array([x_min], dtype=np.float64)
        y_line = slope * x_line + intercept
        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            line=dict(color=color, width=2.4, dash="dash"),
            name=f"{rid} transfer",
            legendgroup=rid,
            showlegend=show_legend,
            hovertemplate=(
                f"{rid} held-out transfer<br>"
                "frozen A, B_i from t0 only<br>"
                f"A={slope:g}<br>"
                f"B_i={intercept:.6g}<br>"
                f"RMSE={_format_sci(rmse)}<extra></extra>"
            ),
        ))
        t0_x.append(float(x[i0]))
        t0_y.append(float(y[i0]))
        t0_text.append(
            f"{rid} t0 calibration<br>B_i={intercept:.6g}<br>RMSE={_format_sci(rmse)}"
        )
        plotted += 1
        last_rid = rid

    if plotted == 0:
        return fig.update_layout(
            title="Held-out transfer — no virtual coordinates on selected holdouts"
        )

    if t0_x:
        fig.add_trace(go.Scatter(
            x=t0_x,
            y=t0_y,
            mode="markers",
            marker=dict(
                size=11,
                symbol="diamond",
                color="#111111",
                line=dict(width=1.2, color="#FFFFFF"),
            ),
            name="t0 calibration (B_i)",
            showlegend=True,
            hovertext=t0_text,
            hovertemplate="%{hovertext}<extra></extra>",
        ))

    if pooled:
        all_err = np.concatenate(pooled)
        pooled_rmse = float(np.sqrt(np.mean(all_err**2)))
        pooled_max = float(np.max(np.abs(all_err)))
    else:
        pooled_rmse = float("nan")
        pooled_max = float("nan")

    title = "Held-out transfer demonstration"
    if plotted == 1:
        title = f"{title} · {last_rid}"
    else:
        title = f"{title} · {plotted} holdouts"
    fig.update_layout(
        title=title,
        xaxis_title="1 - cos(theta)",
        yaxis_title="omega^2",
        legend=dict(
            title="Observed vs t0-transfer",
            bgcolor="rgba(255,255,255,0.8)",
        ),
        template="plotly_white",
        annotations=[
            dict(
                text=(
                    "HELD-OUT TRANSFER<br>"
                    f"frozen A = {slope:g} (not refit)<br>"
                    "B_i from first observation only<br>"
                    f"pooled RMSE = {_format_sci(pooled_rmse)}<br>"
                    f"max |err| = {_format_sci(pooled_max)}<br>"
                    "markers: held-out observations<br>"
                    "dashed: transfer with frozen A and B_i(t0)<br>"
                    "diamonds: t0 calibration points"
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


def heldout_predictive_phase_portrait_grapher(app_control_parameters, parameters):
    """Protected holdout autonomous rollouts in (theta, omega) phase space."""
    _impl = _heldout_predictive_phase_module().heldout_predictive_phase_portrait_grapher
    return _impl(
        app_control_parameters,
        parameters,
        holdout_ids=_HOLDOUT_RECORD_IDS,
        parse_holdout_ids=_parse_holdout_ids,
        available_record_ids=_available_record_ids,
    )


def _task_conditioned_module():
    import importlib.util

    candidates = [
        Path(__file__).resolve().parent / "task_conditioned_summary.py",
        Path(r"D:\SIR_paper\Pendulum\task_conditioned_summary.py"),
    ]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("task_conditioned_summary", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("task_conditioned_summary.py was not found")


def task_conditioned_pendulum_grapher(app_control_parameters, parameters):
    """Paper-like compression + protected-holdout prediction summary."""
    return _task_conditioned_module().task_conditioned_pendulum_grapher(
        app_control_parameters, parameters
    )


def build_custom_graphers(available_vars: list[str] | None = None) -> dict:
    variables = [v for v in (available_vars or ["theta", "omega"]) if v in ("theta", "omega")]
    if not variables:
        variables = ["theta", "omega"]
    options = {v: v for v in variables}
    return {
        "phase_portrait": {
            "function": phase_portrait_grapher,
            "requires_signals": False,
            "display_name": "Phase portrait",
            "parameters": {},
        },
        "ensemble_overlay": {
            "function": ensemble_overlay_grapher,
            "requires_signals": False,
            "display_name": "Ensemble overlay",
            "parameters": {
                "signal": {
                    "default": "theta",
                    "options": options,
                    "display_name": "Signal",
                },
            },
        },
        "invariant_representation": {
            "function": invariant_representation_grapher,
            "requires_signals": False,
            "display_name": "Pendulum invariant",
            "parameters": {
                "records": {
                    "default": "",
                    "display_name": "Records (blank = current; comma-separated or all)",
                },
                "overlay_reference": {
                    "default": "off",
                    "options": {"Off": "off", "On": "on"},
                    "display_name": "Overlay SIR slope (reference)",
                },
                "slope": {
                    "default": _DEFAULT_SLOPE,
                    "display_name": "SIR slope",
                },
            },
        },
        "heldout_transfer": {
            "function": heldout_transfer_grapher,
            "requires_signals": False,
            "display_name": "Held-out transfer",
            "parameters": {
                "records": {
                    "default": "",
                    "display_name": "Holdouts (blank = current holdout or all 8; comma-separated or all)",
                },
                "slope": {
                    "default": _DEFAULT_SLOPE,
                    "display_name": "Frozen SIR slope A",
                },
            },
        },
        "heldout_predictive_phase_portrait": {
            "function": heldout_predictive_phase_portrait_grapher,
            "requires_signals": False,
            "display_name": "Held-out predictive phase portrait",
            "parameters": {
                "records": {
                    "default": "",
                    "display_name": "Holdouts (blank = current holdout or all 8; comma-separated or all)",
                },
                "horizon_s": {
                    "default": 30.0,
                    "options": {
                        "0.5 s": 0.5,
                        "1 s": 1.0,
                        "2 s": 2.0,
                        "5 s": 5.0,
                        "10 s": 10.0,
                        "20 s": 20.0,
                        "30 s": 30.0,
                    },
                    "display_name": "Prediction horizon",
                },
                "overlay_exact_audit": {
                    "default": "off",
                    "options": {"Off": "off", "On": "on"},
                    "display_name": "Overlay exact-coefficient audit",
                },
            },
        },
        "task_conditioned_pendulum": {
            "function": task_conditioned_pendulum_grapher,
            "requires_signals": False,
            "display_name": "Task-conditioned pendulum summary",
            "parameters": {
                "compression_records": {
                    "default": "",
                    "display_name": "Compression records (blank = 8 energy-spaced defaults; comma-separated or all)",
                },
                "holdout": {
                    "default": "pendulum_015",
                    "display_name": "Protected holdout for the phase-portrait inset",
                },
            },
        },
    }
