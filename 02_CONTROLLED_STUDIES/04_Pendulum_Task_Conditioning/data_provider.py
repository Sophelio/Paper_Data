"""Dalia provider for the autonomous nonlinear-pendulum ensemble.

Each parquet under ``data/`` is one realization with raw columns

    times, theta, omega

Virtual (derived) coordinates are computed at fetch time from theta/omega:

    sin_theta, cos_theta, one_minus_cos_theta, omega_squared

Energy and analytic ODE right-hand sides are not selectable.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from custom_graphs import build_custom_graphers
from pendulum_coordinates import (
    SELECTABLE_COLUMNS,
    ensure_requested_columns,
)

DEFAULT_DATA_FOLDER = Path(r"D:\SIR_paper\Pendulum\data")


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
    # Raw files only contain times/theta/omega; virtual names are always offered.
    columns: list[str] = []
    seen: set[str] = set()
    for path in sorted(Path(folder).glob("*.parquet")):
        df = pd.read_parquet(path)
        for col in df.columns:
            if col == "times" or col in seen:
                continue
            columns.append(col)
            seen.add(col)
        break
    for extra in SELECTABLE_COLUMNS:
        if extra not in seen:
            columns.append(extra)
            seen.add(extra)
    return columns


def _trim(times: np.ndarray, values: np.ndarray, t1, t2):
    if t1 is None and t2 is None:
        return times, values
    lo = -np.inf if t1 is None or t1 == "" else float(t1)
    hi = np.inf if t2 is None or t2 == "" else float(t2)
    mask = (times >= lo) & (times <= hi)
    return times[mask], values[mask]


def get_provider(_: Any) -> dict:
    data_folder = _data_folder()
    all_possible_signals = _discover_signals(data_folder) or list(SELECTABLE_COLUMNS)

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

        df = ensure_requested_columns(pd.read_parquet(path), list(signals))
        times = df["times"].to_numpy(dtype=np.float64)
        out, errored = [], []
        for name in signals:
            if name not in df.columns:
                errored.append(name)
                continue
            values = df[name].to_numpy(dtype=np.float64)
            t, v = _trim(times, values, data_trim_1, data_trim_2)
            out.append({"data": v, "data_name": name, "times": t, "errored": False})
        return {"id": record_id, "signals": out, "errored_signals": errored}

    def fetch_sir_record_ids(folder: Path, _unused: Optional[Any] = None) -> list[str]:
        return _record_ids(folder)

    def fetch_data_sir(folder: Path, record_id: str, variables: Optional[list[str]] = None) -> dict[str, Any]:
        names = list(all_possible_signals) if variables is None else list(variables)
        df = ensure_requested_columns(pd.read_parquet(_parquet_path(folder, str(record_id))), names)
        payload: dict[str, Any] = {
            "times": df["times"].to_numpy(dtype=np.float64),
        }
        for name in names:
            if name not in df.columns:
                raise RuntimeError(f"SIR variable {name!r} not in {record_id}")
            payload[name] = df[name].to_numpy(dtype=np.float64)
        return payload

    return {
        "fetch_data": fetch_data,
        "dataset_id": "pendulum",
        "fetch_record_ids_for_dataset_id": fetch_record_ids_for_dataset_id,
        "all_possible_signals": list(all_possible_signals),
        "is_date": False,
        "data_folder": data_folder,
        "fetch_sir_record_ids": fetch_sir_record_ids,
        "fetch_data_sir": fetch_data_sir,
        "custom_grapher_dictionary": build_custom_graphers(all_possible_signals),
    }
