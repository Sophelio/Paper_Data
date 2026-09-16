"""Generate the autonomous nonlinear-pendulum ensemble for the SIR paper.

The same trajectory files are intended for two later task contracts
(compression / description vs prediction / evolution). This script only
writes the canonical raw observations:

    times, theta, omega

and a manifest plus QC artifacts. Derived coordinates and energy are not
stored as measurements.

Usage
-----
python generate_pendulum_data.py
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.integrate import solve_ivp
from scipy.stats.qmc import LatinHypercube, scale

from pendulum_coordinates import (
    ATOL,
    DT,
    GENERATOR_VERSION,
    INTEGRATION_METHOD,
    N_REALIZATIONS,
    OMEGA0,
    OMEGA0_SQUARED,
    RTOL,
    SEED,
    T_END,
    T_START,
    energy_separatrix,
    mechanical_energy,
    time_grid,
)

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / "data"
QC_DIR = OUTPUT_DIR / "qc"
MANIFEST_PATH = OUTPUT_DIR / "manifest.csv"
QC_REPORT_PATH = QC_DIR / "pendulum_qc_report.json"
QC_PLOT_PATH = QC_DIR / "pendulum_dataset_qc.png"

THETA0_MIN, THETA0_MAX = -2.4, 2.4
OMEGA_INIT_MIN, OMEGA_INIT_MAX = -1.2, 1.2
E_FRAC_LO, E_FRAC_HI = 0.08, 0.90
N_LHS_DRAW = 2048
REL_ENERGY_DRIFT_LIMIT = 1e-7
ABS_ENERGY_DRIFT_LIMIT = 1e-8


def pendulum_rhs(t, u, omega0=OMEGA0):
    theta, omega = u
    return [omega, -(omega0**2) * np.sin(theta)]


def integrate_trajectory(theta0: float, omega_init: float) -> pd.DataFrame:
    t_eval = time_grid()
    sol = solve_ivp(
        pendulum_rhs,
        (float(t_eval[0]), float(t_eval[-1])),
        (float(theta0), float(omega_init)),
        method=INTEGRATION_METHOD,
        t_eval=t_eval,
        rtol=RTOL,
        atol=ATOL,
        dense_output=False,
        vectorized=False,
    )
    if not sol.success:
        raise RuntimeError(
            f"Pendulum integration failed for ({theta0}, {omega_init}): {sol.message}"
        )
    if sol.y.shape[1] != t_eval.size:
        raise RuntimeError("Solver returned a time grid that does not match t_eval")
    return pd.DataFrame(
        {
            "times": np.asarray(sol.t, dtype=np.float64),
            "theta": np.asarray(sol.y[0], dtype=np.float64),
            "omega": np.asarray(sol.y[1], dtype=np.float64),
        }
    )


def propose_initial_conditions(n_draw: int = N_LHS_DRAW, seed: int = SEED) -> np.ndarray:
    sampler = LatinHypercube(d=2, seed=int(seed))
    unit = sampler.random(n=n_draw)
    lo = np.array([THETA0_MIN, OMEGA_INIT_MIN], dtype=np.float64)
    hi = np.array([THETA0_MAX, OMEGA_INIT_MAX], dtype=np.float64)
    return np.asarray(scale(unit, lo, hi), dtype=np.float64)


def select_initial_conditions(
    candidates: np.ndarray,
    n: int = N_REALIZATIONS,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Keep n ICs in the libration window, 8 per sign-quadrant, energy-spaced."""
    theta0 = candidates[:, 0]
    omega_init = candidates[:, 1]
    energy = mechanical_energy(theta0, omega_init)
    frac = energy / energy_separatrix()
    ok = (frac > E_FRAC_LO) & (frac < E_FRAC_HI)
    cand = candidates[ok]
    energy = energy[ok]
    frac = frac[ok]
    if cand.shape[0] < n:
        raise RuntimeError(
            f"Only {cand.shape[0]} accepted ICs after energy filter; need {n}"
        )

    q_theta = (cand[:, 0] >= 0.0).astype(np.int64)
    q_omega = (cand[:, 1] >= 0.0).astype(np.int64)
    quadrant = 2 * q_theta + q_omega
    per_q = n // 4
    picked: list[int] = []
    for qi in range(4):
        idx = np.where(quadrant == qi)[0]
        if idx.size < per_q:
            raise RuntimeError(
                f"Quadrant {qi} has only {idx.size} accepted ICs; need {per_q}"
            )
        order = idx[np.argsort(energy[idx], kind="mergesort")]
        loc = np.unique(np.round(np.linspace(0, order.size - 1, per_q)).astype(int))
        if loc.size < per_q:
            extra = [i for i in range(order.size) if i not in set(loc.tolist())]
            loc = np.concatenate([loc, np.asarray(extra[: per_q - loc.size])])
        picked.extend(int(i) for i in order[loc[:per_q]])

    picked_arr = np.asarray(picked, dtype=np.int64)
    # Stable, auditable order: increasing energy, then theta0.
    sort_keys = np.lexsort((cand[picked_arr, 0], energy[picked_arr]))
    chosen = picked_arr[sort_keys]
    return cand[chosen], energy[chosen], frac[chosen]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_parquet(path: Path, df: pd.DataFrame, meta: dict[str, object]) -> None:
    table = pa.Table.from_pandas(df, preserve_index=False)
    encoded = {str(k): str(v).encode("utf-8") for k, v in meta.items()}
    existing = table.schema.metadata or {}
    table = table.replace_schema_metadata({**existing, **encoded})
    pq.write_table(table, path)


def ode_residuals(df: pd.DataFrame, omega0: float = OMEGA0) -> dict[str, float]:
    times = df["times"].to_numpy(dtype=np.float64)
    theta = df["theta"].to_numpy(dtype=np.float64)
    omega = df["omega"].to_numpy(dtype=np.float64)
    dtheta_dt = np.gradient(theta, times)
    domega_dt = np.gradient(omega, times)
    rhs_theta = omega
    rhs_omega = -(omega0**2) * np.sin(theta)
    err_theta = dtheta_dt - rhs_theta
    err_omega = domega_dt - rhs_omega
    return {
        "max_abs_dtheta_residual": float(np.max(np.abs(err_theta))),
        "rms_dtheta_residual": float(np.sqrt(np.mean(err_theta**2))),
        "max_abs_domega_residual": float(np.max(np.abs(err_omega))),
        "rms_domega_residual": float(np.sqrt(np.mean(err_omega**2))),
    }


def energy_drift(df: pd.DataFrame, omega0: float = OMEGA0) -> dict[str, float]:
    e = mechanical_energy(
        df["theta"].to_numpy(dtype=np.float64),
        df["omega"].to_numpy(dtype=np.float64),
        omega0=omega0,
    )
    e0 = float(e[0])
    drift = e - e0
    rel = drift / e0 if e0 != 0.0 else drift
    return {
        "energy_initial": e0,
        "max_abs_energy_drift": float(np.max(np.abs(drift))),
        "max_rel_energy_drift": float(np.max(np.abs(rel))),
        "rms_energy_drift": float(np.sqrt(np.mean(drift**2))),
        "energy_series": e,
    }


def assert_time_grid(df: pd.DataFrame, reference: np.ndarray) -> None:
    times = df["times"].to_numpy(dtype=np.float64)
    if times.shape != reference.shape or not np.allclose(times, reference, rtol=0.0, atol=1e-15):
        raise RuntimeError("Time grid mismatch")
    if not np.all(np.diff(times) > 0):
        raise RuntimeError("Times are not strictly monotone")
    dt = np.diff(times)
    if not np.allclose(dt, DT, rtol=0.0, atol=1e-12):
        raise RuntimeError("dt is not constant")


def write_qc_plot(
    frames: list[pd.DataFrame],
    ics: np.ndarray,
    drifts: list[dict[str, float]],
    path: Path,
) -> None:
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 200,
            "font.size": 9,
            "axes.grid": True,
            "grid.alpha": 0.35,
        }
    )
    n_show = min(8, len(frames))
    idx = np.linspace(0, len(frames) - 1, n_show).astype(int)
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.2))

    ax = axes[0, 0]
    for i in idx:
        ax.plot(frames[i]["times"], frames[i]["theta"], lw=0.9, alpha=0.85)
    ax.set_xlabel("t (s)")
    ax.set_ylabel(r"$\theta$ (rad)")
    ax.set_title("Representative $\\theta(t)$")

    ax = axes[0, 1]
    for i in idx:
        ax.plot(frames[i]["theta"], frames[i]["omega"], lw=0.9, alpha=0.85)
    ax.set_xlabel(r"$\theta$ (rad)")
    ax.set_ylabel(r"$\omega$ (rad/s)")
    ax.set_title("Phase portraits")

    ax = axes[1, 0]
    for i, d in enumerate(drifts):
        series = d["energy_series"]
        ax.plot(
            frames[i]["times"],
            series - series[0],
            lw=0.7,
            alpha=0.55,
            color="0.35",
        )
    ax.set_xlabel("t (s)")
    ax.set_ylabel(r"$E(t)-E(0)$")
    ax.set_title("Energy drift (all realizations)")

    ax = axes[1, 1]
    ax.scatter(ics[:, 0], ics[:, 1], c=[d["energy_initial"] for d in drifts], s=28)
    ax.set_xlabel(r"$\theta_0$ (rad)")
    ax.set_ylabel(r"$\omega(0)$ (rad/s)")
    ax.set_title("Accepted initial conditions")
    ax.axhline(0.0, color="0.6", lw=0.6)
    ax.axvline(0.0, color="0.6", lw=0.6)

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def generate_and_write() -> dict[str, object]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    QC_DIR.mkdir(parents=True, exist_ok=True)
    for stale in DATA_DIR.glob("pendulum_*.parquet"):
        stale.unlink()

    reference_times = time_grid()
    candidates = propose_initial_conditions()
    ics, energies, fracs = select_initial_conditions(candidates)
    if ics.shape[0] != N_REALIZATIONS:
        raise RuntimeError(f"Expected {N_REALIZATIONS} ICs, got {ics.shape[0]}")

    rows = []
    frames = []
    drifts = []
    ode_stats = []
    for i, ((theta0, omega_init), e0, frac) in enumerate(zip(ics, energies, fracs)):
        df = integrate_trajectory(float(theta0), float(omega_init))
        assert_time_grid(df, reference_times)
        if not np.isfinite(df.to_numpy(dtype=np.float64)).all():
            raise RuntimeError(f"Non-finite values in realization {i:03d}")
        drift = energy_drift(df)
        ode = ode_residuals(df)
        if drift["max_rel_energy_drift"] > REL_ENERGY_DRIFT_LIMIT:
            raise RuntimeError(
                f"Realization {i:03d} relative energy drift "
                f"{drift['max_rel_energy_drift']:.3e} exceeds {REL_ENERGY_DRIFT_LIMIT:.1e}"
            )
        if drift["max_abs_energy_drift"] > ABS_ENERGY_DRIFT_LIMIT:
            raise RuntimeError(
                f"Realization {i:03d} absolute energy drift "
                f"{drift['max_abs_energy_drift']:.3e} exceeds {ABS_ENERGY_DRIFT_LIMIT:.1e}"
            )
        filename = f"pendulum_{i:03d}.parquet"
        path = DATA_DIR / filename
        meta = {
            "realization_id": f"{i:03d}",
            "theta0": float(theta0),
            "omega_init": float(omega_init),
            "omega0": OMEGA0,
            "energy_initial": float(e0),
            "dt": DT,
            "integration_method": INTEGRATION_METHOD,
            "rtol": RTOL,
            "atol": ATOL,
            "generator_version": GENERATOR_VERSION,
        }
        write_parquet(path, df, meta)
        sha = sha256_file(path)
        rows.append(
            {
                "realization_id": f"{i:03d}",
                "filename": filename,
                "sha256": sha,
                "theta0": float(theta0),
                "omega_init": float(omega_init),
                "omega0": OMEGA0,
                "omega0_squared": OMEGA0_SQUARED,
                "energy_initial": float(e0),
                "normalized_energy_fraction": float(frac),
                "sample_count": int(len(df)),
                "t_start": T_START,
                "t_end": T_END,
                "dt": DT,
                "max_abs_energy_drift": drift["max_abs_energy_drift"],
                "max_rel_energy_drift": drift["max_rel_energy_drift"],
                "rms_energy_drift": drift["rms_energy_drift"],
            }
        )
        frames.append(df)
        drifts.append(drift)
        ode_stats.append(ode)

    fieldnames = list(rows[0].keys())
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    write_qc_plot(frames, ics, drifts, QC_PLOT_PATH)

    abs_drifts = np.array([d["max_abs_energy_drift"] for d in drifts])
    rel_drifts = np.array([d["max_rel_energy_drift"] for d in drifts])
    report = {
        "n_realizations": int(len(rows)),
        "seed": SEED,
        "lhs_draw": N_LHS_DRAW,
        "omega0": OMEGA0,
        "omega0_squared": OMEGA0_SQUARED,
        "dt": DT,
        "t_start": T_START,
        "t_end": T_END,
        "sample_count": int(reference_times.size),
        "solver": INTEGRATION_METHOD,
        "rtol": RTOL,
        "atol": ATOL,
        "theta0_min": float(np.min(ics[:, 0])),
        "theta0_median": float(np.median(ics[:, 0])),
        "theta0_max": float(np.max(ics[:, 0])),
        "omega_init_min": float(np.min(ics[:, 1])),
        "omega_init_median": float(np.median(ics[:, 1])),
        "omega_init_max": float(np.max(ics[:, 1])),
        "energy_min": float(np.min(energies)),
        "energy_median": float(np.median(energies)),
        "energy_max": float(np.max(energies)),
        "energy_frac_min": float(np.min(fracs)),
        "energy_frac_median": float(np.median(fracs)),
        "energy_frac_max": float(np.max(fracs)),
        "n_theta0_negative": int(np.sum(ics[:, 0] < 0)),
        "n_theta0_positive": int(np.sum(ics[:, 0] > 0)),
        "n_omega_init_negative": int(np.sum(ics[:, 1] < 0)),
        "n_omega_init_positive": int(np.sum(ics[:, 1] > 0)),
        "max_abs_energy_drift": float(np.max(abs_drifts)),
        "median_abs_energy_drift": float(np.median(abs_drifts)),
        "max_rel_energy_drift": float(np.max(rel_drifts)),
        "median_rel_energy_drift": float(np.median(rel_drifts)),
        "max_abs_dtheta_residual": float(
            max(s["max_abs_dtheta_residual"] for s in ode_stats)
        ),
        "max_abs_domega_residual": float(
            max(s["max_abs_domega_residual"] for s in ode_stats)
        ),
        "qc_plot": str(QC_PLOT_PATH),
        "manifest": str(MANIFEST_PATH),
    }
    QC_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    report = generate_and_write()
    print(json.dumps({k: v for k, v in report.items() if k != "energy_series"}, indent=2))
