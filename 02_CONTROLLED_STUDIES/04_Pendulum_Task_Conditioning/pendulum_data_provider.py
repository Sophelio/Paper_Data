"""SIR-web data provider for the autonomous nonlinear-pendulum ensemble.

Loads the parquet files produced by ``generate_pendulum_data.py`` from the
sibling ``data/`` directory. Each parquet is one identifier with columns

    times, theta, omega

Virtual coordinates (not stored on disk) are synthesized on request:

    sin_theta = sin(theta)
    cos_theta = cos(theta)
    one_minus_cos_theta = 1 - cos(theta)
    omega_squared = omega^2

``times`` is excluded from selectable signals. Energy and analytic ODE
right-hand sides are never offered.
"""
from __future__ import annotations

from os import listdir, path
from pathlib import Path

import numpy as np
import pandas as pd

from pendulum_coordinates import (
    SELECTABLE_COLUMNS,
    discover_selectable_variables,
    ensure_requested_columns,
)

_FALLBACK_DATASET_URL = r"D:\SIR_paper\Pendulum\data"


def _resolve_dataset_url() -> str:
    here = Path(__file__).resolve()
    sibling = here.parent / "data"
    if sibling.is_dir():
        return str(sibling)
    for root in here.parents:
        for candidate in (
            root / "Pendulum" / "data",
            root / "SIR_paper" / "Pendulum" / "data",
            root / "Paper Examples" / "Pendulum" / "data",
        ):
            if candidate.is_dir():
                return str(candidate)
    return _FALLBACK_DATASET_URL


DATASET_URL = _resolve_dataset_url()


def _list_parquet_files(directory: str) -> list[str]:
    try:
        return sorted(f for f in listdir(directory) if f.endswith(".parquet"))
    except OSError:
        return []


def _discover_variables(directory: str) -> list[str]:
    parquet_files = _list_parquet_files(directory)
    columns: list[str] = []
    if parquet_files:
        df = pd.read_parquet(path.join(directory, parquet_files[0]))
        columns = df.columns.tolist()
    return discover_selectable_variables(columns)


def get_provider(_=None):
    def fetch_data(identifier, knames):
        df = pd.read_parquet(identifier)
        df = ensure_requested_columns(df, knames)
        for key in knames:
            if key not in df.columns:
                raise KeyError(f"column {key!r} missing in {identifier}")

        data = np.array([df[key].to_numpy(dtype=np.float64) for key in knames])
        xflags = np.ones(len(knames), dtype=bool)
        timing_data = np.array([df["times"].to_numpy(dtype=np.float64)])
        freq = float(timing_data[0, 1] - timing_data[0, 0])
        smooth_rate = 0.2
        return data, xflags, timing_data, freq, smooth_rate

    def fetch_identifier_variables(identifier, key):
        df = pd.read_parquet(identifier)
        df = ensure_requested_columns(df, [key])
        if key not in df.columns:
            raise KeyError(f"column {key!r} missing in {identifier}")
        return df[key].to_numpy(dtype=np.float64)

    def fetch_identifiers_from_url(directory):
        return sorted(
            path.join(directory, name)
            for name in _list_parquet_files(directory)
        )

    def fetch_dataset_variables(directory):
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
    assert get_provider(None)
    ids = prov["fetch_identifiers_from_url"](prov["dataset_url"])
    print(f"dataset_url: {prov['dataset_url']}")
    print(f"{len(ids)} identifiers")
    vars_ = prov["fetch_dataset_variables"](prov["dataset_url"])
    print(f"signals: {vars_}")
    assert vars_ == list(SELECTABLE_COLUMNS) or set(SELECTABLE_COLUMNS).issubset(vars_)
    data, xflags, timing_data, freq, smooth = prov["fetch_data"](ids[0], vars_)
    print(f"OK — data {data.shape}  freq={freq:.6g}  smooth_rate={smooth}")
