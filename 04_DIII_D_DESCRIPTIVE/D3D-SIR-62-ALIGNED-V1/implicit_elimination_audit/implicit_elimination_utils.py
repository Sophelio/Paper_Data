"""Utilities for exact-coordinate and implicit-elimination audit."""
from __future__ import annotations

import hashlib
import json
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    return json.loads((path or (BASE / "audit_config.json")).read_text(encoding="utf-8"))


def setup_logger(log_path: Path, name: str = "implicit_audit") -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    sh = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def canonical_paths(cfg: Dict[str, Any]) -> Dict[str, Path]:
    pkg = REPO / cfg["repo_relative_canonical_package"]
    man = json.loads((pkg / "canonical_run_manifest.json").read_text(encoding="utf-8"))
    design = json.loads((pkg / "d3d_design_matrix_manifest.json").read_text(encoding="utf-8"))
    export = REPO / design["feature_export_directory"]
    return {
        "package": pkg,
        "manifest": pkg / "canonical_run_manifest.json",
        "design_manifest": pkg / "d3d_design_matrix_manifest.json",
        "coordinate_manifest": pkg / "d3d_relational_coordinate_manifest.json",
        "coefficients": pkg / man["coefficient_file"],
        "predictions": pkg / man["prediction_file"],
        "metrics": pkg / man["metrics_file"],
        "pooled": pkg / "d3d_pooled_metrics.json",
        "export": export,
        "model": pkg / man["model_artifact"],
        "correction": REPO / cfg["repo_relative_correction_audit"],
    }


def load_psir(path: Path) -> dict:
    with open(path, "rb") as f:
        return pickle.load(f)


def coef_csv_to_source(row: pd.Series, cfg: Dict[str, Any]) -> np.ndarray:
    key_to_csv = {m["key"]: m["csv_column"] for m in cfg["manuscript_display_order"]}
    out = np.empty(8, dtype=np.float64)
    out[0] = float(row["intercept"])
    for i, key in enumerate(cfg["source_matrix_order_keys"]):
        out[i + 1] = float(row[key_to_csv[key]])
    return out


def display_of(cfg: Dict[str, Any], key: str) -> str:
    for m in cfg["manuscript_display_order"]:
        if m["key"] == key:
            return m["display"]
    return key


def export_col(cfg: Dict[str, Any], key: str) -> str:
    for m in cfg["manuscript_display_order"]:
        if m["key"] == key:
            return m["export_column"]
    return f"[{key}]"


def yphaseder_index(cfg: Dict[str, Any], dx_name: str) -> int:
    return list(cfg["dx_channel_order"]).index(dx_name)


def zscore_1d(x: np.ndarray) -> Tuple[np.ndarray, float, float]:
    x = np.asarray(x, dtype=np.float64)
    mu = float(np.mean(x))
    sig = float(np.std(x, ddof=0))
    if sig == 0:
        return np.zeros_like(x), mu, sig
    return (x - mu) / sig, mu, sig


def reconstruct_yphaseder(
    y: np.ndarray,
    d: np.ndarray,
    shift: float,
    mu: float,
    sigma: float,
) -> np.ndarray:
    """Exact historical construction: z = ((y+s)/(d+s) - mu) / sigma."""
    y = np.asarray(y, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)
    u = (y + shift) / (d + shift)
    return (u - mu) / sigma


def alpha_beta_yphaseder(
    d: np.ndarray,
    shift: float,
    mu: float,
    sigma: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """z = alpha * y + beta with y the standardized target."""
    d = np.asarray(d, dtype=np.float64)
    denom = d + shift
    alpha = 1.0 / (sigma * denom)
    beta = shift / (sigma * denom) - mu / sigma
    return alpha.astype(np.float64), beta.astype(np.float64)


def reconstruct_xphaseder(
    d_num: np.ndarray,
    d_den: np.ndarray,
    shift: float,
    mu: float,
    sigma: float,
) -> np.ndarray:
    u = (d_num + shift) / (d_den + shift)
    return (u - mu) / sigma


def reconstruct_level_quotient(
    a: np.ndarray,
    b: np.ndarray,
    shift: float,
    mu: float,
    sigma: float,
) -> np.ndarray:
    u = (a + shift) / (b + shift)
    return (u - mu) / sigma


def fit_ols(y: np.ndarray, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    X = np.asarray(X, dtype=np.float64)
    A = np.column_stack([np.ones(len(y), dtype=np.float64), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ coef
    rmse = float(np.sqrt(np.mean((y - yhat) ** 2)))
    return coef.astype(np.float64), yhat.astype(np.float64), rmse


def pooled_rmse(residuals: Sequence[np.ndarray]) -> float:
    e = np.concatenate([np.asarray(r, dtype=np.float64).reshape(-1) for r in residuals])
    return float(np.sqrt(np.mean(e ** 2)))


def robust_scale_mad(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    med = float(np.median(x))
    return float(1.4826 * np.median(np.abs(x - med)))


def threshold_fractions(abs_vals: np.ndarray, thresholds: Sequence[float], scale: float) -> Dict[str, float]:
    abs_vals = np.asarray(abs_vals, dtype=np.float64)
    n = len(abs_vals)
    out: Dict[str, float] = {}
    for t in thresholds:
        out[f"frac_abs_lt_{t:g}"] = float(np.mean(abs_vals < t)) if n else np.nan
        if scale > 0:
            out[f"frac_rel_lt_{t:g}"] = float(np.mean(abs_vals / scale < t))
        else:
            out[f"frac_rel_lt_{t:g}"] = np.nan
    return out


def sign_crossings(x: np.ndarray, t: Optional[np.ndarray] = None) -> List[Dict[str, float]]:
    x = np.asarray(x, dtype=np.float64)
    events = []
    for i in range(len(x) - 1):
        a, b = x[i], x[i + 1]
        if not (np.isfinite(a) and np.isfinite(b)):
            continue
        if a == 0.0 or b == 0.0 or (a > 0) != (b > 0):
            if a == 0.0 and b == 0.0:
                continue
            if t is not None and (b - a) != 0:
                frac = float(-a / (b - a))
                frac = float(np.clip(frac, 0.0, 1.0))
                t_cross = float(t[i] + frac * (t[i + 1] - t[i]))
            else:
                t_cross = np.nan
            events.append(
                {
                    "sample_index_left": i,
                    "sample_index_right": i + 1,
                    "value_left": float(a),
                    "value_right": float(b),
                    "crossing_time": t_cross,
                }
            )
    return events


@dataclass
class DischargeBundle:
    realization_index: int
    shot: int
    shiftval: float
    coef: np.ndarray  # (8,)
    y: np.ndarray
    yhat: np.ndarray
    residual: np.ndarray
    time: np.ndarray
    dt_seconds: float
    features: Dict[str, np.ndarray]  # source keys -> columns
    d_kappa: np.ndarray
    d_betan: np.ndarray
    d_li: np.ndarray
    r_q95: np.ndarray
    r_kappa: np.ndarray
    mu_yk: float
    sig_yk: float
    mu_yb: float
    sig_yb: float
    # optional mSD for other coords
    msd: Dict[str, Any]
