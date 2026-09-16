"""SIR data provider for the Heat Equation Degeneracy example."""

from __future__ import annotations

import os
from pathlib import Path
from os import listdir, path

import numpy as np
import pandas as pd


# Absolute path fallback for known-good Windows setups; prefer portable discovery.
_FALLBACK_DATASET_URL = r"D:\sir-web\Paper Examples\Heat Equation Degeneracy\data"


def _resolve_dataset_url():
    """Locate ``Paper Examples/Heat Equation Degeneracy/data`` portably."""
    here = Path(__file__).resolve()
    for root in here.parents:
        candidate = root / "Paper Examples" / "Heat Equation Degeneracy" / "data"
        if candidate.is_dir():
            return str(candidate)
    return _FALLBACK_DATASET_URL


DATASET_URL = _resolve_dataset_url()
EXCLUDED_VARS = {"times", "kappa", "mode"}


def _list_parquet_files(directory: str) -> list[str]:
    try:
        return sorted(f for f in os.listdir(directory) if f.endswith(".parquet"))
    except OSError:
        return []


def _discover_variables(directory: str) -> list[str]:
    parquet_files = _list_parquet_files(directory)
    if not parquet_files:
        return []
    columns: list[str] = []
    seen: set[str] = set()
    for fname in parquet_files:
        df = pd.read_parquet(os.path.join(directory, fname))
        for col in df.columns.tolist():
            if col not in EXCLUDED_VARS and col not in seen:
                columns.append(col)
                seen.add(col)
    return columns


def _ensure_requested_columns(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Synthesize missing derivatives when base columns are present."""
    missing = [k for k in keys if k not in df.columns]
    if not missing:
        return df

    derivative_keys = {"u", "du_dx", "d2u_dx2", "du_dt", "d2u_dt2"}
    if not any(k in derivative_keys for k in missing):
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


def get_provider(_=None):
    def fetch_data(identifier: str, knames: list[str]):
        df = pd.read_parquet(identifier)
        df = _ensure_requested_columns(df, knames)
        for key in knames:
            if key not in df.columns:
                raise KeyError(f"column {key!r} missing in {identifier}")

        data = np.array([df[key].to_numpy(dtype=np.float64) for key in knames])
        xflags = np.ones(len(knames), dtype=bool)
        timing_data = np.array([df["times"].to_numpy(dtype=np.float64)])
        freq = float(timing_data[0, 1] - timing_data[0, 0])
        # Must be > 0 when SIR smoothing is enabled (low-pass filter requirement).
        smooth_rate = 0.2
        return data, xflags, timing_data, freq, smooth_rate

    def fetch_identifier_variables(identifier: str, key: str):
        df = pd.read_parquet(identifier)
        df = _ensure_requested_columns(df, [key])
        if key not in df.columns:
            raise KeyError(f"column {key!r} missing in {identifier}")
        return df[key].to_numpy(dtype=np.float64)

    def fetch_identifiers_from_url(directory: str):
        return sorted(
            path.join(directory, name)
            for name in listdir(directory)
            if name.endswith(".parquet")
        )

    def fetch_dataset_variables(directory: str):
        return _discover_variables(directory)

    return {
        "fetch_data": fetch_data,
        "fetch_identifier_variables": fetch_identifier_variables,
        "fetch_identifiers_from_url": fetch_identifiers_from_url,
        "fetch_dataset_variables": fetch_dataset_variables,
        "dataset_url": DATASET_URL,
    }


if __name__ == "__main__":
    prov = get_provider()
    ids = prov["fetch_identifiers_from_url"](prov["dataset_url"])
    print(f"dataset_url: {prov['dataset_url']}")
    print(f"{len(ids)} identifiers")
    if ids:
        vars_ = prov["fetch_dataset_variables"](prov["dataset_url"])
        print(f"signals: {vars_}")
        data, _, timing_data, freq, _ = prov["fetch_data"](ids[0], vars_[:5])
        print(f"shape={data.shape}, timing={timing_data.shape}, freq={freq}")
