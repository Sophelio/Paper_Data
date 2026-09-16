"""Frozen data loaders for the task-conditioned pendulum panel.

Compression uses stored trajectories and the frozen SIR slope A = -3.645.
Prediction uses saved holdout rollouts under Prediction_model/; SIR is not rerun.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PENDULUM_ROOT = Path(r"D:\SIR_paper\Pendulum")
DATA_DIR = PENDULUM_ROOT / "data"
MANIFEST_PATH = PENDULUM_ROOT / "manifest.csv"
PRED_DIR = PENDULUM_ROOT / "Prediction_model"
TRAJ_DIR = PRED_DIR / "trajectories"
SUMMARY_PATH = PRED_DIR / "prediction_summary.json"

# Frozen compression / prediction coefficients. Do not edit from holdout scores.
SIR_SLOPE = -3.645
SIR_A = -1.82245149
SIR_B = 1.0
# Uncalibrated compression intercept recovery (24 discovery realizations).
R2_B_VS_2E = 0.999999986

# Energy-spaced training realizations (not the protected holdouts).
DEFAULT_COMPRESSION_IDS: tuple[str, ...] = (
    "pendulum_000",
    "pendulum_004",
    "pendulum_008",
    "pendulum_012",
    "pendulum_016",
    "pendulum_020",
    "pendulum_024",
    "pendulum_028",
)
DEFAULT_HOLDOUT_ID = "pendulum_015"
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

# Blue → green, low to high energy (complements the relational-space figure).
ENERGY_COLORS: tuple[str, ...] = (
    "#7BA3C4",
    "#5B8FA8",
    "#4C8A8A",
    "#3E7F6C",
    "#2F7358",
    "#1F6A48",
    "#185C3C",
    "#0D4B25",
)
TRUE_COLOR = "#274C77"
PRED_COLOR = "#0D4B25"
MUTED = "#5a5a5a"


def load_manifest() -> pd.DataFrame:
    man = pd.read_csv(MANIFEST_PATH)
    man["record_id"] = man["realization_id"].map(lambda i: f"pendulum_{int(i):03d}")
    return man


def load_raw(record_id: str) -> pd.DataFrame:
    path = DATA_DIR / f"{record_id}.parquet"
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_parquet(path, columns=["times", "theta", "omega"])


def compression_trace(record_id: str, subsample: int = 6) -> dict:
    df = load_raw(record_id)
    theta = df["theta"].to_numpy(dtype=np.float64)
    omega = df["omega"].to_numpy(dtype=np.float64)
    x = 1.0 - np.cos(theta)
    y = omega**2
    intercept = float(np.mean(y - SIR_SLOPE * x))
    energy = float(0.5 * omega[0] ** 2 + (1.8225) * (1.0 - np.cos(theta[0])))
    sl = slice(None, None, int(subsample))
    x_line = np.linspace(float(np.min(x)), float(np.max(x)), 40)
    return {
        "record_id": record_id,
        "x": x[sl],
        "y": y[sl],
        "x_line": x_line,
        "y_line": SIR_SLOPE * x_line + intercept,
        "intercept": intercept,
        "energy": energy,
        "two_E": 2.0 * energy,
    }


def load_compression(record_ids: tuple[str, ...] | None = None) -> list[dict]:
    ids = tuple(record_ids) if record_ids else DEFAULT_COMPRESSION_IDS
    traces = [compression_trace(rid) for rid in ids]
    traces.sort(key=lambda t: t["energy"])
    for i, tr in enumerate(traces):
        tr["color"] = ENERGY_COLORS[min(i, len(ENERGY_COLORS) - 1)]
    return traces


def load_prediction_bundle(record_id: str = DEFAULT_HOLDOUT_ID) -> pd.DataFrame:
    path = TRAJ_DIR / f"{record_id}_prediction.parquet"
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_parquet(path)
    needed = {"times", "theta_true", "omega_true", "theta_sir", "omega_sir"}
    missing = needed - set(df.columns)
    if missing:
        raise RuntimeError(f"{path.name} missing {missing}")
    return df


def load_pooled_rmse() -> dict[str, dict[str, list[float]]]:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    out = {
        "sir": {"theta": [], "omega": []},
        "exact_audit": {"theta": [], "omega": []},
    }
    horizons = {"theta": [], "omega": []}
    for row in summary["pooled_unwrapped"]:
        model = row["model"]
        if model not in out:
            continue
        var = row["variable"]
        out[model][var].append((float(row["horizon_s"]), float(row["rmse"])))
    for model in out:
        for var in ("theta", "omega"):
            pairs = sorted(out[model][var])
            out[model][var] = {
                "horizon_s": [p[0] for p in pairs],
                "rmse": [p[1] for p in pairs],
            }
    out["a"] = float(summary["primary_model"]["a"])
    out["b"] = float(summary["primary_model"]["b"])
    return out


def subsample_phase(df: pd.DataFrame, step: int = 3) -> dict[str, np.ndarray]:
    sl = slice(None, None, int(step))
    return {
        "times": df["times"].to_numpy(dtype=np.float64)[sl],
        "theta_true": df["theta_true"].to_numpy(dtype=np.float64)[sl],
        "omega_true": df["omega_true"].to_numpy(dtype=np.float64)[sl],
        "theta_sir": df["theta_sir"].to_numpy(dtype=np.float64)[sl],
        "omega_sir": df["omega_sir"].to_numpy(dtype=np.float64)[sl],
        "theta0": float(df["theta_true"].iloc[0]),
        "omega0": float(df["omega_true"].iloc[0]),
    }
