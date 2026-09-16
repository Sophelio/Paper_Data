"""Dalia provider for the Heat Equation Degeneracy paper example.

Each parquet under ``data/`` is one realization. Columns:

    times, x, t, u, du_dx, d2u_dx2, du_dt, d2u_dt2, kappa, mode

``times`` is the sample axis; ``kappa`` and ``mode`` are constant metadata
and are not offered as signals. Missing spatial/time derivatives are
synthesized from the analytic heat-equation mode when ``x``, ``t``,
``kappa``, and ``mode`` are present.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

DEFAULT_DATA_FOLDER = Path(r"D:\SIR_paper\Heat Equation Degeneracy\data")
EXCLUDED_VARS = {"times", "kappa", "mode"}
DERIVATIVE_KEYS = {"u", "du_dx", "d2u_dx2", "du_dt", "d2u_dt2"}


def _data_folder(folder: Optional[Path] = None) -> Path:
    if folder is not None:
        return Path(folder)
    linked = Path(__file__).resolve().parent / "data"
    if linked.is_dir():
        return linked
    return DEFAULT_DATA_FOLDER


def _record_ids(folder: Path) -> list[str]:
    return sorted(p.stem for p in Path(folder).glob("*.parquet"))


def _parquet_path(folder: Path, record_id: str) -> Path:
    return Path(folder) / f"{record_id}.parquet"


def _discover_signals(folder: Path) -> list[str]:
    columns: list[str] = []
    seen: set[str] = set()
    for path in sorted(Path(folder).glob("*.parquet")):
        df = pd.read_parquet(path)
        for col in df.columns:
            if col not in EXCLUDED_VARS and col not in seen:
                columns.append(col)
                seen.add(col)
    return columns


def _ensure_requested_columns(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    missing = [k for k in keys if k not in df.columns]
    if not missing or not any(k in DERIVATIVE_KEYS for k in missing):
        return df
    required = {"x", "t", "kappa", "mode"}
    if not required.issubset(df.columns):
        return df

    x = df["x"].to_numpy(dtype=np.float64)
    t = df["t"].to_numpy(dtype=np.float64)
    kappa = float(df["kappa"].iloc[0])
    mode = int(df["mode"].iloc[0])
    w = mode * np.pi
    decay = np.exp(-(w**2) * kappa * t)
    trig = np.sin(w * x)
    u = decay * trig

    if "u" in missing:
        df["u"] = u
    if "du_dx" in missing:
        df["du_dx"] = w * decay * np.cos(w * x)
    if "d2u_dx2" in missing:
        df["d2u_dx2"] = -(w**2) * u
    if "du_dt" in missing:
        df["du_dt"] = -(w**2) * kappa * u
    if "d2u_dt2" in missing:
        df["d2u_dt2"] = (w**4) * (kappa**2) * u
    return df


def _trim(times: np.ndarray, values: np.ndarray, t1, t2):
    if t1 is None and t2 is None:
        return times, values
    lo = -np.inf if t1 is None or t1 == "" else float(t1)
    hi = np.inf if t2 is None or t2 == "" else float(t2)
    mask = (times >= lo) & (times <= hi)
    return times[mask], values[mask]


def get_provider(_: Any) -> dict:
    data_folder = _data_folder()
    all_possible_signals = _discover_signals(data_folder) or [
        "x", "t", "u", "du_dx", "d2u_dx2", "du_dt", "d2u_dt2"
    ]

    def fetch_record_ids_for_dataset_id(folder: Path, _unused: Optional[Any] = None) -> list[str]:
        return _record_ids(folder)

    def fetch_data(
        folder: Path,
        _dataset_id: Optional[str],
        record_id: Optional[str],
        signals: Optional[list[str]],
        _global_data_params: Optional[dict],
        data_trim_1=None,
        data_trim_2=None,
    ):
        if record_id is None:
            return []
        if not signals:
            signals = [all_possible_signals[0]]

        path = _parquet_path(folder, str(record_id))
        if not path.exists():
            return {"id": record_id, "signals": [], "errored_signals": list(signals)}

        df = _ensure_requested_columns(pd.read_parquet(path), list(signals))
        times = df["times"].to_numpy(dtype=np.float64) if "times" in df.columns else np.arange(len(df), dtype=np.float64)
        out, errored = [], []
        for name in signals:
            if name not in df.columns:
                errored.append(name)
                continue
            t, v = _trim(times, df[name].to_numpy(dtype=np.float64), data_trim_1, data_trim_2)
            out.append({"data": v, "data_name": name, "times": t, "errored": False})
        return {"id": record_id, "signals": out, "errored_signals": errored}

    def fetch_sir_record_ids(folder: Path, _unused: Optional[Any] = None) -> list[str]:
        return _record_ids(folder)

    def fetch_data_sir(folder: Path, record_id: str, variables: Optional[list[str]] = None) -> dict[str, Any]:
        names = list(all_possible_signals) if variables is None else list(variables)
        df = _ensure_requested_columns(pd.read_parquet(_parquet_path(folder, str(record_id))), names)
        payload: dict[str, Any] = {
            "times": df["times"].to_numpy(dtype=np.float64) if "times" in df.columns else np.arange(len(df), dtype=np.float64)
        }
        for name in names:
            if name not in df.columns:
                raise RuntimeError(f"SIR variable {name!r} not in {record_id}")
            payload[name] = df[name].to_numpy(dtype=np.float64)
        return payload

    return {
        "fetch_data": fetch_data,
        "dataset_id": "heat_equation_degeneracy",
        "fetch_record_ids_for_dataset_id": fetch_record_ids_for_dataset_id,
        "all_possible_signals": list(all_possible_signals),
        "is_date": False,
        "data_folder": data_folder,
        "fetch_sir_record_ids": fetch_sir_record_ids,
        "fetch_data_sir": fetch_data_sir,
    }
