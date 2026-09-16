"""Frozen autonomous pendulum prediction model (holdout evaluation only).

PRIMARY SIR-discovered law (pre-calibration, 24 training realizations):

    d(theta_hat)/dt = 1.0 * omega_hat
    d(omega_hat)/dt = -1.82245149 * sin(theta_hat)

AUDIT-ONLY generating coefficient:

    d(omega_hat)/dt = -1.8225 * sin(theta_hat)

After t = 0 the model is closed: sin is always evaluated on the predicted
angle. Observed holdout series are used only for the initial state and for
post-hoc scoring. Coefficients are never refit here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

# Dataset integration standard (same as generate_pendulum_data.py).
import sys

_PENDULUM_ROOT = Path(__file__).resolve().parents[1]
if str(_PENDULUM_ROOT) not in sys.path:
    sys.path.insert(0, str(_PENDULUM_ROOT))

from pendulum_coordinates import (  # noqa: E402
    ATOL,
    DT,
    FORBIDDEN_SELECTABLE,
    INTEGRATION_METHOD,
    RAW_COLUMNS,
    RTOL,
    T_END,
    T_START,
    mechanical_energy,
    time_grid,
)

# Frozen PRIMARY coefficients. Do not edit from holdout scores.
SIR_A = -1.82245149
SIR_B = 1.0
# Audit-only generating coefficient (not the reported SIR result).
AUDIT_A = -1.8225
AUDIT_B = 1.0

HOLDOUT_RECORD_IDS: tuple[str, ...] = (
    "pendulum_003",
    "pendulum_007",
    "pendulum_011",
    "pendulum_015",
    "pendulum_019",
    "pendulum_023",
    "pendulum_027",
    "pendulum_031",
)
HORIZONS_S: tuple[float, ...] = (0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0)
OBSERVED_COLUMNS: tuple[str, ...] = RAW_COLUMNS  # times, theta, omega only

DEFAULT_DATA_FOLDER = _PENDULUM_ROOT / "data"
TRAJECTORY_COLUMNS: tuple[str, ...] = (
    "times",
    "theta_true",
    "omega_true",
    "theta_sir",
    "omega_sir",
    "theta_exact_audit",
    "omega_exact_audit",
    "theta_error_sir",
    "omega_error_sir",
    "theta_error_exact",
    "omega_error_exact",
)


def frozen_rhs(t, u, a: float, b: float):
    """Autonomous RHS. ``sin`` is of predicted theta, never an observed channel."""
    theta_hat, omega_hat = u
    return [b * omega_hat, a * np.sin(theta_hat)]


def sir_rhs(t, u):
    return frozen_rhs(t, u, SIR_A, SIR_B)


def audit_rhs(t, u):
    return frozen_rhs(t, u, AUDIT_A, AUDIT_B)


def initial_state_from_observed(
    times: np.ndarray,
    theta: np.ndarray,
    omega: np.ndarray,
) -> tuple[float, float, float]:
    """Return (t0, theta(t0), omega(t0)) from the earliest sample only."""
    times = np.asarray(times, dtype=np.float64)
    theta = np.asarray(theta, dtype=np.float64)
    omega = np.asarray(omega, dtype=np.float64)
    if times.size == 0 or times.shape != theta.shape or times.shape != omega.shape:
        raise ValueError("observed times/theta/omega must be nonempty and aligned")
    i0 = int(np.argmin(times))
    return float(times[i0]), float(theta[i0]), float(omega[i0])


def integrate_frozen_model(
    *,
    theta0: float,
    omega0: float,
    a: float,
    b: float,
    t_eval: np.ndarray | None = None,
    rtol: float = RTOL,
    atol: float = ATOL,
    method: str = INTEGRATION_METHOD,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate the frozen autonomous ODE from a scalar initial state.

    Keyword-only: callers cannot pass an observed sin_theta series.
    """
    t_eval = time_grid() if t_eval is None else np.asarray(t_eval, dtype=np.float64)
    sol = solve_ivp(
        frozen_rhs,
        (float(t_eval[0]), float(t_eval[-1])),
        (float(theta0), float(omega0)),
        args=(float(a), float(b)),
        method=method,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        dense_output=False,
        vectorized=False,
    )
    if not sol.success:
        raise RuntimeError(f"Frozen-model integration failed: {sol.message}")
    if sol.y.shape[1] != t_eval.size:
        raise RuntimeError("Solver returned a time grid that does not match t_eval")
    return (
        np.asarray(sol.t, dtype=np.float64),
        np.asarray(sol.y[0], dtype=np.float64),
        np.asarray(sol.y[1], dtype=np.float64),
    )


def rollout_from_observed(
    times: np.ndarray,
    theta_obs: np.ndarray,
    omega_obs: np.ndarray,
) -> dict[str, np.ndarray]:
    """Autonomous SIR + audit rollouts from the observed t0 state only."""
    times = np.asarray(times, dtype=np.float64)
    theta_obs = np.asarray(theta_obs, dtype=np.float64)
    omega_obs = np.asarray(omega_obs, dtype=np.float64)
    _t0, theta0, omega0 = initial_state_from_observed(times, theta_obs, omega_obs)
    t_sir, theta_sir, omega_sir = integrate_frozen_model(
        theta0=theta0, omega0=omega0, a=SIR_A, b=SIR_B, t_eval=times,
    )
    t_audit, theta_audit, omega_audit = integrate_frozen_model(
        theta0=theta0, omega0=omega0, a=AUDIT_A, b=AUDIT_B, t_eval=times,
    )
    if not np.array_equal(t_sir, times) or not np.array_equal(t_audit, times):
        raise RuntimeError("Rollout time grid does not match the observational grid")
    return {
        "times": times,
        "theta_true": theta_obs,
        "omega_true": omega_obs,
        "theta_sir": theta_sir,
        "omega_sir": omega_sir,
        "theta_exact_audit": theta_audit,
        "omega_exact_audit": omega_audit,
        "theta_error_sir": theta_sir - theta_obs,
        "omega_error_sir": omega_sir - omega_obs,
        "theta_error_exact": theta_audit - theta_obs,
        "omega_error_exact": omega_audit - omega_obs,
    }


def read_observed_raw(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load only raw observational columns. Virtual/energy channels are refused."""
    path = Path(path)
    df = pd.read_parquet(path, columns=list(OBSERVED_COLUMNS))
    extra = [c for c in df.columns if c not in OBSERVED_COLUMNS]
    if extra:
        raise RuntimeError(f"unexpected columns in {path.name}: {extra}")
    banned = [c for c in FORBIDDEN_SELECTABLE if c in df.columns]
    if banned:
        raise RuntimeError(f"refusing audit-only columns {banned} from {path.name}")
    return (
        df["times"].to_numpy(dtype=np.float64),
        df["theta"].to_numpy(dtype=np.float64),
        df["omega"].to_numpy(dtype=np.float64),
    )


def rollout_holdout_file(path: Path) -> dict[str, np.ndarray]:
    times, theta, omega = read_observed_raw(path)
    return rollout_from_observed(times, theta, omega)


def _window_mask(times: np.ndarray, horizon_s: float) -> np.ndarray:
    return np.asarray(times, dtype=np.float64) <= (float(horizon_s) + 1e-12)


def error_metrics(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    err = np.asarray(pred, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    if err.size == 0:
        return {"rmse": float("nan"), "mae": float("nan"), "max_abs": float("nan"), "n": 0}
    return {
        "rmse": float(np.sqrt(np.mean(err**2))),
        "mae": float(np.mean(np.abs(err))),
        "max_abs": float(np.max(np.abs(err))),
        "n": int(err.size),
    }


def wrapped_theta_error(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    """Secondary modulo-2pi metric. Primary metric remains unwrapped."""
    err = np.asarray(pred, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    wrapped = np.abs(np.angle(np.exp(1j * err)))
    if wrapped.size == 0:
        return {"rmse": float("nan"), "mae": float("nan"), "max_abs": float("nan"), "n": 0}
    return {
        "rmse": float(np.sqrt(np.mean(wrapped**2))),
        "mae": float(np.mean(wrapped)),
        "max_abs": float(np.max(wrapped)),
        "n": int(wrapped.size),
    }


def metrics_for_bundle(
    bundle: Mapping[str, np.ndarray],
    record_id: str,
) -> list[dict[str, Any]]:
    times = np.asarray(bundle["times"], dtype=np.float64)
    rows: list[dict[str, Any]] = []
    pairs = (
        ("sir", "theta", "theta_sir", "theta_true"),
        ("sir", "omega", "omega_sir", "omega_true"),
        ("exact_audit", "theta", "theta_exact_audit", "theta_true"),
        ("exact_audit", "omega", "omega_exact_audit", "omega_true"),
        ("sir_minus_audit", "theta", "theta_sir", "theta_exact_audit"),
        ("sir_minus_audit", "omega", "omega_sir", "omega_exact_audit"),
    )
    for model, variable, pred_key, true_key in pairs:
        pred = np.asarray(bundle[pred_key], dtype=np.float64)
        truth = np.asarray(bundle[true_key], dtype=np.float64)
        for horizon in HORIZONS_S:
            mask = _window_mask(times, horizon)
            stats = error_metrics(pred[mask], truth[mask])
            row: dict[str, Any] = {
                "record_id": record_id,
                "model": model,
                "variable": variable,
                "horizon_s": float(horizon),
                "metric_family": "unwrapped",
                **stats,
            }
            if variable == "theta" and model in {"sir", "exact_audit"}:
                wrapped = wrapped_theta_error(pred[mask], truth[mask])
                row["wrapped_rmse"] = wrapped["rmse"]
                row["wrapped_mae"] = wrapped["mae"]
                row["wrapped_max_abs"] = wrapped["max_abs"]
            rows.append(row)
    i_final = int(np.argmax(times))
    for model, th_key, om_key in (
        ("sir", "theta_sir", "omega_sir"),
        ("exact_audit", "theta_exact_audit", "omega_exact_audit"),
    ):
        rows.append({
            "record_id": record_id,
            "model": model,
            "variable": "theta",
            "horizon_s": float(times[i_final]),
            "metric_family": "final_time",
            "rmse": float("nan"),
            "mae": float("nan"),
            "max_abs": float(np.abs(bundle[th_key][i_final] - bundle["theta_true"][i_final])),
            "n": 1,
        })
        rows.append({
            "record_id": record_id,
            "model": model,
            "variable": "omega",
            "horizon_s": float(times[i_final]),
            "metric_family": "final_time",
            "rmse": float("nan"),
            "mae": float("nan"),
            "max_abs": float(np.abs(bundle[om_key][i_final] - bundle["omega_true"][i_final])),
            "n": 1,
        })
    return rows


def orbit_diagnostic(bundle: Mapping[str, np.ndarray]) -> dict[str, float]:
    """Post-hoc energy mismatch. Not used by the predictive model."""
    e_true = mechanical_energy(bundle["theta_true"], bundle["omega_true"])
    e_sir = mechanical_energy(bundle["theta_sir"], bundle["omega_sir"])
    e_audit = mechanical_energy(bundle["theta_exact_audit"], bundle["omega_exact_audit"])
    return {
        "energy_true_mean": float(np.mean(e_true)),
        "rel_energy_mismatch_sir": float(np.max(np.abs(e_sir - e_true)) / max(abs(e_true[0]), 1e-15)),
        "rel_energy_mismatch_audit": float(np.max(np.abs(e_audit - e_true)) / max(abs(e_true[0]), 1e-15)),
        "abs_energy_mismatch_sir": float(np.max(np.abs(e_sir - e_true))),
        "abs_energy_mismatch_audit": float(np.max(np.abs(e_audit - e_true))),
    }


def bundle_to_frame(bundle: Mapping[str, np.ndarray]) -> pd.DataFrame:
    return pd.DataFrame({name: np.asarray(bundle[name], dtype=np.float64) for name in TRAJECTORY_COLUMNS})


def holdout_paths(data_folder: Path | None = None) -> list[Path]:
    folder = Path(data_folder) if data_folder is not None else DEFAULT_DATA_FOLDER
    paths = [folder / f"{rid}.parquet" for rid in HOLDOUT_RECORD_IDS]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"missing holdout parquet(s): {missing}")
    return paths
