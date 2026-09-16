"""Shared pendulum coordinates: raw columns, virtual columns, energy (audit only).

Virtual coordinates are deterministic functions of the primitive observations
``theta`` and ``omega``. They are never written to the raw Parquet files.
``energy_true`` and analytic ODE right-hand sides are audit-only helpers and
must not be offered as selectable SIR / Dalia variables.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

GENERATOR_VERSION = "1.0.0"
OMEGA0 = 1.35
OMEGA0_SQUARED = OMEGA0 * OMEGA0  # 1.8225
SEED = 20260820
N_REALIZATIONS = 32
T_START = 0.0
T_END = 30.0
DT = 0.01
RTOL = 1e-12
ATOL = 1e-14
INTEGRATION_METHOD = "DOP853"

RAW_COLUMNS: tuple[str, ...] = ("times", "theta", "omega")
VIRTUAL_COLUMNS: tuple[str, ...] = (
    "sin_theta",
    "cos_theta",
    "one_minus_cos_theta",
    "omega_squared",
)
# Selectable model / graph variables. ``times`` is the axis, never a feature.
SELECTABLE_COLUMNS: tuple[str, ...] = ("theta", "omega") + VIRTUAL_COLUMNS
EXCLUDED_VARS = {"times"}
FORBIDDEN_SELECTABLE = {
    "energy",
    "energy_true",
    "energy_initial",
    "dtheta_dt",
    "domega_dt",
    "omega0",
    "theta0",
    "omega_init",
}


def time_grid(
    t_start: float = T_START, t_end: float = T_END, dt: float = DT
) -> np.ndarray:
    n_steps = int(round((t_end - t_start) / dt))
    return np.linspace(t_start, t_end, n_steps + 1, dtype=np.float64)


def mechanical_energy(
    theta: np.ndarray,
    omega: np.ndarray,
    omega0: float = OMEGA0,
) -> np.ndarray:
    """Audit-only conserved energy: 0.5 omega^2 + omega0^2 (1 - cos(theta))."""
    theta = np.asarray(theta, dtype=np.float64)
    omega = np.asarray(omega, dtype=np.float64)
    return 0.5 * omega**2 + (omega0**2) * (1.0 - np.cos(theta))


def energy_separatrix(omega0: float = OMEGA0) -> float:
    return 2.0 * (omega0**2)


def virtual_coordinates(theta: np.ndarray, omega: np.ndarray) -> dict[str, np.ndarray]:
    theta = np.asarray(theta, dtype=np.float64)
    omega = np.asarray(omega, dtype=np.float64)
    cos_theta = np.cos(theta)
    return {
        "sin_theta": np.sin(theta),
        "cos_theta": cos_theta,
        "one_minus_cos_theta": 1.0 - cos_theta,
        "omega_squared": omega**2,
    }


def ensure_requested_columns(df: pd.DataFrame, keys: Sequence[str]) -> pd.DataFrame:
    """Add virtual columns on demand. Never synthesizes energy or ODE truth."""
    missing = [k for k in keys if k not in df.columns]
    if not missing:
        return df
    forbidden = [k for k in missing if k in FORBIDDEN_SELECTABLE]
    if forbidden:
        raise KeyError(
            f"refusing to expose audit-only channel(s) {forbidden!r}"
        )
    virtual_needed = [k for k in missing if k in VIRTUAL_COLUMNS]
    if virtual_needed:
        if "theta" not in df.columns or "omega" not in df.columns:
            raise KeyError("theta and omega are required to compute virtual coordinates")
        derived = virtual_coordinates(
            df["theta"].to_numpy(dtype=np.float64),
            df["omega"].to_numpy(dtype=np.float64),
        )
        for name in virtual_needed:
            df[name] = derived[name]
    still_missing = [k for k in keys if k not in df.columns]
    if still_missing:
        raise KeyError(f"column(s) {still_missing!r} are not available")
    return df


def discover_selectable_variables(columns: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for col in columns:
        if col in EXCLUDED_VARS or col in FORBIDDEN_SELECTABLE or col in seen:
            continue
        out.append(col)
        seen.add(col)
    for extra in SELECTABLE_COLUMNS:
        if extra not in seen:
            out.append(extra)
            seen.add(extra)
    return out


def metadata_from_mapping(meta: Mapping[str, object]) -> dict[str, str]:
    return {str(k): str(v) for k, v in meta.items()}
