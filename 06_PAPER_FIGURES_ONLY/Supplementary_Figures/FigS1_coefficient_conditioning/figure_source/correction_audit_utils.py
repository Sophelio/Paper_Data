"""Utilities for the DIII-D coefficient-conditioning correction audit."""
from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
PARENT = BASE.parent
REPO = PARENT.parents[2]

# Import original audit loaders (read-only reuse).
sys.path.insert(0, str(PARENT))
from coefficient_conditioning_utils import (  # noqa: E402
    DischargeData,
    fit_ols,
    load_config as load_parent_config,
    load_discharges,
    pooled_rmse,
    sha256_file,
    truncated_svd_coefs,
)


def load_correction_config(path: Optional[Path] = None) -> Dict[str, Any]:
    path = path or (BASE / "correction_audit_config.json")
    return json.loads(path.read_text(encoding="utf-8"))


def setup_logger(log_path: Path, name: str = "correction_audit") -> logging.Logger:
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


def display_name(cfg: Dict[str, Any], key: str) -> str:
    for m in cfg["manuscript_display_order"]:
        if m["key"] == key:
            return m["display"]
    return key


def coef_col(key: str) -> str:
    return f"coef__{key}"


def derived_seed(base: int, *parts: int) -> int:
    x = int(base) & 0x7FFFFFFF
    for p in parts:
        x = (x * 1103515245 + int(p) + 12345) & 0x7FFFFFFF
    return int(x if x != 0 else 1)


def reconstruction_label(
    abs_rmse_change: float,
    pred_corr: float,
    cfg: Dict[str, Any],
) -> str:
    th = cfg["reconstruction_labels"]
    if abs_rmse_change <= th["stable_abs_rmse_change"] and pred_corr >= th["stable_prediction_correlation"]:
        return "STABLE_RECONSTRUCTION"
    if abs_rmse_change > th["moderate_abs_rmse_change"] or pred_corr < th["material_prediction_correlation"]:
        return "MATERIAL_RECONSTRUCTION_CHANGE"
    return "MODERATE_RECONSTRUCTION_CHANGE"


def coefficient_movement_label(rel_coef_change: float, cfg: Dict[str, Any]) -> str:
    if rel_coef_change <= cfg["reconstruction_labels"]["stable_coefficient_relative_change"]:
        return "STABLE_COEFFICIENTS"
    return "LARGE_COEFFICIENT_MOVEMENT"


def combined_sensitivity_class(rel_coef: float, abs_rmse: float, pred_corr: float, cfg: Dict[str, Any]) -> str:
    c = coefficient_movement_label(rel_coef, cfg)
    r = reconstruction_label(abs_rmse, pred_corr, cfg)
    if c == "STABLE_COEFFICIENTS" and r == "STABLE_RECONSTRUCTION":
        return "STABLE_COEFFICIENTS_STABLE_RECONSTRUCTION"
    if c == "LARGE_COEFFICIENT_MOVEMENT" and r == "STABLE_RECONSTRUCTION":
        return "LARGE_COEFFICIENT_MOVEMENT_STABLE_RECONSTRUCTION"
    if c == "LARGE_COEFFICIENT_MOVEMENT":
        return "LARGE_COEFFICIENT_MOVEMENT_CHANGED_RECONSTRUCTION"
    return "STABLE_COEFFICIENTS_CHANGED_RECONSTRUCTION"


def truncated_svd_fixed_rank(
    y: np.ndarray,
    X: np.ndarray,
    rank_keep: int,
) -> Tuple[np.ndarray, int, np.ndarray, float, np.ndarray]:
    """Intercept via demeaning; retain top `rank_keep` singular directions of centered X."""
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    X = np.asarray(X, dtype=np.float64)
    y_mean = y.mean()
    X_mean = X.mean(axis=0)
    yc = y - y_mean
    Xc = X - X_mean
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    k = int(max(0, min(rank_keep, s.size)))
    s_inv = np.zeros_like(s)
    if k > 0:
        s_inv[:k] = 1.0 / s[:k]
    beta = (Vt.T * s_inv) @ (U.T @ yc)
    intercept = float(y_mean - X_mean @ beta)
    coef = np.concatenate([[intercept], beta])
    yhat = intercept + X @ beta
    rmse = float(np.sqrt(np.mean((y - yhat) ** 2)))
    return coef.astype(np.float64), k, yhat.astype(np.float64), rmse, s.astype(np.float64)


def ridge_path_standardized(
    y: np.ndarray,
    X: np.ndarray,
    lambda_relative: float,
) -> Tuple[np.ndarray, float, float, float, np.ndarray]:
    """Ridge on column-standardized features; intercept unpenalized.

    lambda = lambda_relative * sigma_1^2 of the standardized design.
    Returns coef[8], rmse, pred_corr_placeholder_unused, edf, beta_std.
    """
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    X = np.asarray(X, dtype=np.float64)
    y_mean = float(y.mean())
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0, ddof=0)
    X_std = np.where(X_std > 0, X_std, 1.0)
    Xs = (X - X_mean) / X_std
    yc = y - y_mean
    U, s, Vt = np.linalg.svd(Xs, full_matrices=False)
    sigma1 = float(s[0]) if s.size else 0.0
    lam = float(lambda_relative) * (sigma1 ** 2)
    if s.size == 0:
        beta_std = np.zeros(X.shape[1], dtype=np.float64)
        edf = 0.0
    else:
        filt = (s ** 2) / (s ** 2 + lam) if lam > 0 else np.ones_like(s)
        if lam == 0.0:
            s_inv = 1.0 / s
            beta_std = (Vt.T * s_inv) @ (U.T @ yc)
            edf = float(np.sum(s > 0))
        else:
            beta_std = (Vt.T * (s / (s ** 2 + lam))) @ (U.T @ yc)
            edf = float(np.sum(filt))
    beta = beta_std / X_std
    intercept = y_mean - float(X_mean @ beta)
    coef = np.concatenate([[intercept], beta])
    yhat = intercept + X @ beta
    rmse = float(np.sqrt(np.mean((y - yhat) ** 2)))
    return coef.astype(np.float64), rmse, edf, lam, beta_std.astype(np.float64)


def profile_ml_tau2(
    estimates: np.ndarray,
    within_var: np.ndarray,
    grid: Optional[np.ndarray] = None,
    chi2_crit: float = 3.841458448338683,
) -> Tuple[float, float, float, float]:
    """Profile Gaussian ML for random-intercept meta-analysis (known within variances).

    Objective: maximize -0.5 * sum(log(v_i) + (y_i-mu)^2/v_i), mu profiled.
    This is NOT REML.
    """
    y = np.asarray(estimates, dtype=np.float64)
    wvar = np.maximum(np.asarray(within_var, dtype=np.float64), 0.0)
    if grid is None:
        grid = np.unique(
            np.concatenate(
                [np.array([0.0]), np.logspace(-16, np.log10(max(np.var(y), 1e-16)) + 2, 500)]
            )
        )

    def nll(tau2: float) -> Tuple[float, float]:
        v = wvar + tau2
        w = 1.0 / v
        mu = float(np.sum(w * y) / np.sum(w))
        ll = -0.5 * (np.sum(np.log(v)) + np.sum((y - mu) ** 2 / v))
        return -ll, mu

    best = None
    records = []
    for t2 in grid:
        val, mu = nll(float(t2))
        records.append((float(t2), val, mu))
        if best is None or val < best[1]:
            best = (float(t2), val, mu)
    assert best is not None
    tau2_hat, nll_min, mu_hat = best
    thresh = nll_min + 0.5 * chi2_crit
    ok = [t2 for t2, v, _ in records if v <= thresh]
    lo = float(min(ok)) if ok else 0.0
    hi = float(max(ok)) if ok else tau2_hat
    return mu_hat, tau2_hat, lo, hi


def reml_tau2(
    estimates: np.ndarray,
    within_var: np.ndarray,
    grid: Optional[np.ndarray] = None,
    chi2_crit: float = 3.841458448338683,
) -> Tuple[float, float, float, float]:
    """Restricted ML for one-parameter random-intercept model with known sampling variances.

    REML profile log-likelihood (Viechtbauer / standard meta-analysis form):
      l_R(tau2) = -1/2 { sum log(v_i) + log(sum w_i) + sum w_i (y_i - mu)^2 }
    with v_i = sigma_i^2 + tau2, w_i = 1/v_i, mu = weighted mean.
    """
    y = np.asarray(estimates, dtype=np.float64)
    wvar = np.maximum(np.asarray(within_var, dtype=np.float64), 0.0)
    if grid is None:
        grid = np.unique(
            np.concatenate(
                [np.array([0.0]), np.logspace(-16, np.log10(max(np.var(y), 1e-16)) + 2, 500)]
            )
        )

    def nll(tau2: float) -> Tuple[float, float]:
        v = wvar + tau2
        w = 1.0 / v
        sw = float(np.sum(w))
        mu = float(np.sum(w * y) / sw)
        ll = -0.5 * (np.sum(np.log(v)) + np.log(sw) + np.sum(w * (y - mu) ** 2))
        return -ll, mu

    best = None
    records = []
    for t2 in grid:
        val, mu = nll(float(t2))
        records.append((float(t2), val, mu))
        if best is None or val < best[1]:
            best = (float(t2), val, mu)
    assert best is not None
    tau2_hat, nll_min, mu_hat = best
    thresh = nll_min + 0.5 * chi2_crit
    ok = [t2 for t2, v, _ in records if v <= thresh]
    lo = float(min(ok)) if ok else 0.0
    hi = float(max(ok)) if ok else tau2_hat
    return mu_hat, tau2_hat, lo, hi


def bootstrap_tau2(
    estimates: np.ndarray,
    within_var: np.ndarray,
    n_boot: int,
    rng: np.random.Generator,
    estimator: str = "REML",
) -> np.ndarray:
    """Discharge-level nonparametric bootstrap of tau2."""
    n = len(estimates)
    out = np.empty(n_boot, dtype=np.float64)
    fn = reml_tau2 if estimator.upper() == "REML" else profile_ml_tau2
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        _, t2, _, _ = fn(estimates[idx], within_var[idx])
        out[b] = t2
    return out


def heterogeneity_metrics(
    estimates: np.ndarray,
    within_var: np.ndarray,
    estimator: str = "REML",
    chi2_crit: float = 3.841458448338683,
) -> Dict[str, float]:
    y = np.asarray(estimates, dtype=np.float64)
    w = np.asarray(within_var, dtype=np.float64)
    s_B = float(np.var(y, ddof=1))
    mean_W = float(np.mean(w))
    H = s_B / mean_W if mean_W > 0 else np.inf
    resolved = max(0.0, s_B - mean_W) / s_B if s_B > 0 else 0.0
    fn = reml_tau2 if estimator.upper() == "REML" else profile_ml_tau2
    mu, tau2, lo, hi = fn(y, w, chi2_crit=chi2_crit)
    frac_between = float(tau2 / (tau2 + mean_W)) if (tau2 + mean_W) > 0 else 0.0
    return {
        "observed_between_variance": s_B,
        "mean_within_variance": mean_W,
        "heterogeneity_ratio": float(H),
        "resolved_fraction": float(resolved),
        "mu": float(mu),
        "tau2": float(tau2),
        "tau": float(np.sqrt(tau2)),
        "tau2_interval_low": float(lo),
        "tau2_interval_high": float(hi),
        "fraction_total_variance_between": frac_between,
    }


def orient_vector(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64).copy()
    k = int(np.argmax(np.abs(v)))
    if v[k] < 0:
        v = -v
    return v


def align_sign(v: np.ndarray, ref: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    ref = np.asarray(ref, dtype=np.float64)
    return v if float(np.dot(v, ref)) >= 0 else -v


def principal_angles_degrees(Q1: np.ndarray, Q2: np.ndarray) -> np.ndarray:
    """Principal angles (degrees) between column subspaces of Q1 and Q2."""
    Q1, _ = np.linalg.qr(Q1)
    Q2, _ = np.linalg.qr(Q2)
    s = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    s = np.clip(s, -1.0, 1.0)
    return np.degrees(np.arccos(s))


def bh_fdr(pvals: Sequence[float], alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    p = np.asarray(pvals, dtype=np.float64)
    m = len(p)
    order = np.argsort(p)
    ranked = p[order]
    thresh = alpha * (np.arange(1, m + 1) / m)
    passed = ranked <= thresh
    if not np.any(passed):
        reject = np.zeros(m, dtype=bool)
    else:
        kmax = int(np.max(np.where(passed)[0]))
        reject_sorted = np.zeros(m, dtype=bool)
        reject_sorted[: kmax + 1] = True
        reject = np.empty(m, dtype=bool)
        reject[order] = reject_sorted
    adj = np.empty(m, dtype=np.float64)
    cummin = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        val = ranked[i] * m / rank
        cummin = min(cummin, val)
        adj[order[i]] = min(cummin, 1.0)
    return reject, adj


def spearman_corr(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    from scipy.stats import spearmanr

    r, p = spearmanr(x, y, nan_policy="omit")
    return float(r), float(p)


def hash_inputs(paths: Dict[str, Path]) -> Dict[str, str]:
    return {k: sha256_file(p) for k, p in paths.items() if p.exists()}
