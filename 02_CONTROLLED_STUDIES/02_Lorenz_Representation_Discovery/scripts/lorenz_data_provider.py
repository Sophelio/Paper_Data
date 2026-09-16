"""SIR data provider for the Lorenz validation example (paper Section 2.6.1).

Loads the parquet files produced by ``Lorenz_attractor.py`` from the sibling
``data/`` directory. Each parquet is one identifier with a ``times`` column plus
one column per signal:

  * ``lorenz_dt001.parquet``                  -> times, x, y, z
  * ``lorenz_dt001_exact_derivatives.parquet`` -> times, x, y, z, dx, dy, dz

All signal columns (including ``dx``, ``dy``, ``dz`` when present) are offered in
the SIR variable checkboxes; only ``times`` is excluded. See ``docs/context.md``
Phase 4 for the full provider contract.
"""

import os
from pathlib import Path
from os import listdir, path

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from scipy.signal import welch

# Lorenz parameters used to synthesize manufactured derivatives when needed.
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

# Original hardcoded path, kept ONLY as a last-resort fallback so an existing
# (Windows) setup keeps working even if portable discovery somehow fails.
_FALLBACK_DATASET_URL = r"D:\sir-web\Paper Examples\Lorenz\data"


def _resolve_dataset_url():
    """Locate ``Paper Examples/Lorenz/data`` portably, with a safe fallback.

    sir-web copies this provider to ``.providers/current_provider.py`` before
    importing, so ``__file__`` sits at a different depth than in the repo. Walk
    up from wherever this file lives until an existing ``Paper Examples/Lorenz/
    data`` directory is found. Cross-platform (pathlib, no drive letters) — works
    on Windows, macOS and Linux, unlike a hardcoded ``D:\\`` path.

    If discovery finds no existing data directory (e.g. an unforeseen layout on a
    platform we can't test), fall back to the original hardcoded path so a known-
    good setup is never broken.
    """
    here = Path(__file__).resolve()
    for root in here.parents:
        candidate = root / "Paper Examples" / "Lorenz" / "data"
        if candidate.is_dir():
            return str(candidate)
    return _FALLBACK_DATASET_URL


DATASET_URL = _resolve_dataset_url()

# Only the time axis is excluded from selectable signals.
EXCLUDED_VARS = {"times"}


def _list_parquet_files(directory):
    try:
        return sorted(f for f in os.listdir(directory) if f.endswith(".parquet"))
    except OSError:
        return []


def _discover_variables(directory):
    parquet_files = _list_parquet_files(directory)
    if not parquet_files:
        return []
    columns = []
    seen = set()
    for fname in parquet_files:
        df = pd.read_parquet(os.path.join(directory, fname))
        for col in df.columns.tolist():
            if col not in EXCLUDED_VARS and col not in seen:
                columns.append(col)
                seen.add(col)
    return columns


def _ensure_requested_columns(df, keys):
    """Ensure requested columns exist, synthesizing Lorenz dx/dy/dz when absent."""
    missing = [k for k in keys if k not in df.columns]
    if not missing:
        return df

    derivative_keys = {"dx", "dy", "dz"}
    if any(k in derivative_keys for k in missing):
        required_xyz = {"x", "y", "z"}
        if not required_xyz.issubset(df.columns):
            # If xyz are absent, fall through to KeyError handling below.
            pass
        else:
            x = df["x"].to_numpy(dtype=np.float64)
            y = df["y"].to_numpy(dtype=np.float64)
            z = df["z"].to_numpy(dtype=np.float64)
            if "dx" in missing:
                df["dx"] = SIGMA * (y - x)
            if "dy" in missing:
                df["dy"] = x * (RHO - z) - y
            if "dz" in missing:
                df["dz"] = x * y - BETA * z

    return df


def get_power_spectrum(app_control_parameters, parameters):
    """Welch power spectrum of one variable across all dataset files."""
    variable = parameters.get("power_spectrum_variable")
    nperseg_raw = parameters.get("power_spectrum_nperseg")
    nperseg = int(nperseg_raw) if nperseg_raw else 256

    identifiers = app_control_parameters.get("identifiers", [])

    fig = go.Figure()
    if not variable:
        fig.update_layout(title="Select a variable to compute the power spectrum")
        return fig

    for identifier in identifiers:
        try:
            df = pd.read_parquet(identifier)
        except Exception:
            continue
        if variable not in df.columns or "times" not in df.columns:
            continue
        signal = df[variable].to_numpy(dtype=np.float64)
        times = df["times"].to_numpy(dtype=np.float64)
        if len(times) < 2:
            continue
        dt = times[1] - times[0]
        if dt <= 0:
            continue
        fs = 1.0 / dt
        seg = max(1, min(nperseg, len(signal)))
        freqs, psd = welch(signal, fs=fs, nperseg=seg)
        fig.add_trace(go.Scatter(
            x=freqs,
            y=psd,
            mode="lines",
            name=Path(identifier).stem,
        ))

    fig.update_layout(
        title=f"Power spectrum ({variable})",
        xaxis_title="Frequency (Hz)",
        yaxis_title="PSD",
        yaxis_type="log",
    )
    return fig


def get_equation_overlay(app_control_parameters, parameters):
    """Plot the SIR-discovered equation alongside the input target signal."""
    formulas = app_control_parameters.get("formulas") or {}
    input_data = app_control_parameters.get("input_data_dict") or []
    target = app_control_parameters.get("target_variable")

    fig = go.Figure()
    if not formulas:
        fig.update_layout(title="Run SIR to populate equations")
        return fig

    plotted_names = []
    for entry in input_data:
        try:
            data_items, name = entry
        except (TypeError, ValueError):
            continue
        plotted_names.append(name)
        for series in data_items:
            try:
                x, y = series
            except (TypeError, ValueError):
                continue
            x_arr = np.asarray(x).reshape(-1)
            y_arr = np.asarray(y).reshape(-1)
            fig.add_trace(go.Scatter(
                x=x_arr, y=y_arr, mode="lines",
                opacity=0.4, name=name, showlegend=False,
            ))

    formula_lines = [f"{name} = {expr}" for name, expr in formulas.items()]
    if formula_lines:
        fig.add_annotation(
            xref="paper", yref="paper", x=0.02, y=0.98, showarrow=False,
            align="left",
            text="<br>".join(formula_lines[:5]),
            bgcolor="rgba(255,255,255,0.6)",
        )

    fig.update_layout(
        title=f"Discovered equation overlay ({target or '—'})",
        xaxis_title="time",
        yaxis_title=", ".join(plotted_names) if plotted_names else "value",
    )
    return fig


def get_provider(_=None):
    def fetch_data(identifier, knames):
        df = pd.read_parquet(identifier)
        df = _ensure_requested_columns(df, knames)
        for key in knames:
            if key not in df.columns:
                raise KeyError(f"column {key!r} missing in {identifier}")

        data = np.array([df[key].to_numpy(dtype=np.float64) for key in knames])
        xflags = np.ones(len(knames), dtype=bool)

        timing_data = np.array([df["times"].to_numpy(dtype=np.float64)])
        # freq MUST be a Python float (scipy.signal.iirfilter calls float(wo)).
        freq = float(timing_data[0, 1] - timing_data[0, 0])
        smooth_rate = 0.2
        return data, xflags, timing_data, freq, smooth_rate

    def fetch_identifier_variables(identifier, key):
        df = pd.read_parquet(identifier)
        df = _ensure_requested_columns(df, [key])
        if key not in df.columns:
            raise KeyError(f"column {key!r} missing in {identifier}")
        return df[key].to_numpy(dtype=np.float64)

    def fetch_identifiers_from_url(directory):
        return sorted(
            path.join(directory, name)
            for name in listdir(directory)
            if name.endswith(".parquet")
        )

    def fetch_dataset_variables(directory):
        return _discover_variables(directory)

    available_vars = _discover_variables(DATASET_URL)
    variable_options = {v: v for v in available_vars} if available_vars else {"(none)": ""}

    custom_grapher_dictionary = {
        "power_spectrum": {
            "display_name": "Power spectrum (Welch)",
            "parameters": {
                "variable": {
                    "default": available_vars[0] if available_vars else "",
                    "options": variable_options,
                    "display_name": "Variable",
                },
                "nperseg": {
                    "default": 256,
                    "min": 8,
                    "max": None,
                    "step": 1,
                    "display_name": "Segment length (nperseg)",
                },
            },
            "function": get_power_spectrum,
        },
        "equation_overlay": {
            "display_name": "Discovered equation overlay",
            "requires": ["formulas", "input_data_dict"],
            "parameters": {},
            "function": get_equation_overlay,
        },
    }

    return {
        "fetch_data": fetch_data,
        "fetch_identifier_variables": fetch_identifier_variables,
        "fetch_identifiers_from_url": fetch_identifiers_from_url,
        "fetch_dataset_variables": fetch_dataset_variables,
        "dataset_url": DATASET_URL,
        "custom_grapher_dictionary": custom_grapher_dictionary,
    }


if __name__ == "__main__":
    prov = get_provider()
    assert get_provider(None)  # Modalia-style call must not raise.

    ids = prov["fetch_identifiers_from_url"](prov["dataset_url"])
    print(f"dataset_url: {prov['dataset_url']}")
    print(f"{len(ids)} identifiers: {[Path(i).name for i in ids]}")

    vars_ = prov["fetch_dataset_variables"](prov["dataset_url"])
    print(f"signals: {vars_}")
    assert len(ids) > 0 and len(vars_) > 0

    knames = vars_[: min(3, len(vars_))]
    data, xflags, timing_data, freq, smooth = prov["fetch_data"](ids[0], knames)
    assert data.dtype == np.float64
    assert data.shape == (len(knames), timing_data.shape[1])
    assert timing_data.shape == (1, data.shape[1])
    assert len(xflags) == len(knames)
    assert isinstance(freq, float)
    print(f"OK — data {data.shape}  freq={freq:.6g}  smooth_rate={smooth}")
