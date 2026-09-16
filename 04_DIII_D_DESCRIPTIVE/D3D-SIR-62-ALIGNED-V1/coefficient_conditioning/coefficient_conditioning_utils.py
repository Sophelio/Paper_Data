"""Utilities for the DIII-D coefficient-conditioning audit."""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

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
    path = path or (BASE / "audit_config.json")
    return json.loads(path.read_text(encoding="utf-8"))


def setup_logger(log_path: Path, name: str = "coeff_audit") -> logging.Logger:
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


@dataclass
class DischargeData:
    realization_index: int
    shot: int
    X: np.ndarray  # (1000, 7) source order, float64
    y: np.ndarray  # (1000,)
    time_ms: np.ndarray
    dt_seconds: float
    coef_source: np.ndarray  # (8,) intercept + 7 source-order coeffs
    yhat_canonical: np.ndarray
    residual_canonical: np.ndarray


def feature_short_names(cfg: Dict[str, Any]) -> List[str]:
    return list(cfg["source_matrix_order_keys"])


def manuscript_map(cfg: Dict[str, Any]) -> List[Dict[str, str]]:
    return list(cfg["manuscript_display_order"])


def source_index_of_key(cfg: Dict[str, Any], key: str) -> int:
    return cfg["source_matrix_order_keys"].index(key)


def canonical_paths(cfg: Dict[str, Any]) -> Dict[str, Path]:
    pkg = REPO / cfg["repo_relative_canonical_package"]
    man = json.loads((pkg / "canonical_run_manifest.json").read_text(encoding="utf-8"))
    design = json.loads((pkg / "d3d_design_matrix_manifest.json").read_text(encoding="utf-8"))
    export = REPO / design["feature_export_directory"]
    return {
        "package": pkg,
        "manifest": pkg / "canonical_run_manifest.json",
        "design_manifest": pkg / "d3d_design_matrix_manifest.json",
        "coefficients": pkg / man["coefficient_file"],
        "predictions": pkg / man["prediction_file"],
        "metrics": pkg / man["metrics_file"],
        "pooled": pkg / "d3d_pooled_metrics.json",
        "export": export,
        "model": pkg / man["model_artifact"],
    }


def fit_ols(y: np.ndarray, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    """Return (coef[8], yhat, rmse) with intercept + columns of X."""
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    X = np.asarray(X, dtype=np.float64)
    A = np.column_stack([np.ones(len(y), dtype=np.float64), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ coef
    rmse = float(np.sqrt(np.mean((y - yhat) ** 2)))
    return coef.astype(np.float64), yhat.astype(np.float64), rmse


def coef_csv_to_source_order(row: pd.Series, cfg: Dict[str, Any]) -> np.ndarray:
    """Map coefficient CSV (manuscript/semantic columns) → source-order vector length 8."""
    key_to_csv = {m["key"]: m["csv_column"] for m in cfg["manuscript_display_order"]}
    out = np.empty(8, dtype=np.float64)
    out[0] = float(row["intercept"])
    for i, key in enumerate(cfg["source_matrix_order_keys"]):
        out[i + 1] = float(row[key_to_csv[key]])
    return out


def load_discharges(cfg: Dict[str, Any], logger: logging.Logger) -> List[DischargeData]:
    paths = canonical_paths(cfg)
    design = json.loads(paths["design_manifest"].read_text(encoding="utf-8"))
    feature_cols = design["feature_columns_psir_order"]
    target_col = design["target_column"]
    assert feature_cols == [f"[{k}]" for k in cfg["source_matrix_order_keys"]]

    coef_df = pd.read_csv(paths["coefficients"]).sort_values("realization_index")
    pred_df = pd.read_parquet(paths["predictions"])
    assert len(coef_df) == cfg["n_discharges"]
    assert len(pred_df) == cfg["n_discharges"] * cfg["n_samples_per_discharge"]
    assert set(coef_df["realization_index"]) == set(range(cfg["n_discharges"]))

    discharges: List[DischargeData] = []
    for _, row in coef_df.iterrows():
        i = int(row["realization_index"])
        shot = int(row["shot"])
        f = paths["export"] / f"shot_{shot}_resampled__model.parquet"
        if not f.exists():
            raise FileNotFoundError(f)
        df = pd.read_parquet(f)
        if len(df) != cfg["n_samples_per_discharge"]:
            raise AssertionError(f"shot {shot}: expected 1000 rows, got {len(df)}")
        X = np.column_stack(
            [df[c].to_numpy(dtype=np.float64) for c in feature_cols]
        )
        y = df[target_col].to_numpy(dtype=np.float64)
        t = df["times"].to_numpy(dtype=np.float64)
        if not (np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(t).all()):
            raise AssertionError(f"nonfinite values in shot {shot}")
        dt_s = float(np.median(np.diff(t)) / 1000.0)
        coef = coef_csv_to_source_order(row, cfg)
        sub = pred_df[pred_df["realization_index"] == i].sort_values("sample_index")
        if len(sub) != cfg["n_samples_per_discharge"]:
            raise AssertionError(f"prediction rows for realization {i}")
        yhat = sub["prediction_standardized"].to_numpy(dtype=np.float64)
        resid = sub["residual_standardized"].to_numpy(dtype=np.float64)
        discharges.append(
            DischargeData(
                realization_index=i,
                shot=shot,
                X=X,
                y=y,
                time_ms=t,
                dt_seconds=dt_s,
                coef_source=coef,
                yhat_canonical=yhat,
                residual_canonical=resid,
            )
        )
    logger.info("Loaded %d discharges", len(discharges))
    return discharges


def svd_features(X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Economy SVD of feature matrix only (no intercept). Returns U, s, Vt."""
    return np.linalg.svd(np.asarray(X, dtype=np.float64), full_matrices=False)


def numerical_rank(s: np.ndarray, tau: float) -> int:
    s = np.asarray(s, dtype=np.float64)
    if s.size == 0 or s[0] <= 0:
        return 0
    return int(np.sum(s / s[0] > tau))


def effective_rank(s: np.ndarray) -> float:
    s = np.asarray(s, dtype=np.float64)
    s2 = s ** 2
    tot = float(np.sum(s2))
    if tot <= 0:
        return 0.0
    p = s2 / tot
    p = p[p > 0]
    return float(np.exp(-np.sum(p * np.log(p))))


def stable_rank(X: np.ndarray, s: np.ndarray) -> float:
    fro2 = float(np.sum(np.asarray(X, dtype=np.float64) ** 2))
    op2 = float(s[0] ** 2) if s.size and s[0] > 0 else np.nan
    return fro2 / op2 if op2 and np.isfinite(op2) and op2 > 0 else np.nan


def pearson_corr_matrix(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    Xc = X - X.mean(axis=0, keepdims=True)
    std = Xc.std(axis=0, ddof=0)
    std[std == 0] = np.nan
    C = (Xc.T @ Xc) / X.shape[0]
    D = np.outer(std, std)
    with np.errstate(invalid="ignore", divide="ignore"):
        R = C / D
    np.fill_diagonal(R, 1.0)
    return R


def vif_values(X: np.ndarray, tol: float = 1e-14) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    p = X.shape[1]
    vifs = np.empty(p, dtype=np.float64)
    for r in range(p):
        y = X[:, r]
        Z = np.delete(X, r, axis=1)
        A = np.column_stack([np.ones(len(y)), Z])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        yhat = A @ coef
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        if ss_tot <= 0:
            vifs[r] = np.inf
            continue
        r2 = 1.0 - float(np.sum((y - yhat) ** 2)) / ss_tot
        denom = 1.0 - r2
        vifs[r] = np.inf if denom <= tol else 1.0 / denom
    return vifs


def orient_singular_vector(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64).copy()
    k = int(np.argmax(np.abs(v)))
    if v[k] < 0:
        v = -v
    return v


def truncated_svd_coefs(
    y: np.ndarray,
    X: np.ndarray,
    tau: float,
    epsilon: float = 1e-15,
) -> Tuple[np.ndarray, int, np.ndarray, float]:
    """Fit intercept by demeaning, then truncated SVD on centered features.

    Equivalent OLS when full rank: intercept = mean(y) - mean(X) @ beta.
    Truncation applies only to the feature part.
    """
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    X = np.asarray(X, dtype=np.float64)
    y_mean = y.mean()
    X_mean = X.mean(axis=0)
    yc = y - y_mean
    Xc = X - X_mean
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    if s.size == 0 or s[0] <= 0:
        beta = np.zeros(X.shape[1], dtype=np.float64)
        rank = 0
    else:
        keep = s / s[0] > tau
        rank = int(np.sum(keep))
        s_inv = np.zeros_like(s)
        s_inv[keep] = 1.0 / s[keep]
        beta = (Vt.T * s_inv) @ (U.T @ yc)
    intercept = float(y_mean - X_mean @ beta)
    coef = np.concatenate([[intercept], beta])
    yhat = intercept + X @ beta
    rmse = float(np.sqrt(np.mean((y - yhat) ** 2)))
    return coef, rank, yhat, rmse


def integrated_autocorr_time(x: np.ndarray, max_lag: int) -> float:
    """Positive-run truncated IAC estimate in samples (ACF sum)."""
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    x = x - x.mean()
    n = x.size
    var = float(np.dot(x, x) / n)
    if var <= 0:
        return 1.0
    iac = 1.0
    for lag in range(1, max_lag + 1):
        c = float(np.dot(x[:-lag], x[lag:]) / n) / var
        if c <= 0:
            break
        iac += 2.0 * c
    return float(max(iac, 1.0))


def choose_block_length(
    iac_samples: float, min_b: int, max_b: int
) -> Tuple[int, int, int]:
    primary = int(np.clip(round(iac_samples), min_b, max_b))
    short = int(max(min_b, round(primary / 2)))
    long = int(min(max_b, round(2 * primary)))
    return short, primary, long


def circular_block_bootstrap_indices(
    n: int, block: int, rng: np.random.Generator
) -> np.ndarray:
    if block < 1:
        block = 1
    if block > n:
        block = n
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=n_blocks)
    idx = np.empty(n_blocks * block, dtype=np.int64)
    for b, s in enumerate(starts):
        idx[b * block : (b + 1) * block] = (s + np.arange(block)) % n
    return idx[:n]


def bootstrap_fit_coefficients(
    y: np.ndarray,
    X: np.ndarray,
    block: int,
    n_boot: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Return array (n_boot, 8) of intercept+coefs."""
    n = len(y)
    out = np.empty((n_boot, 8), dtype=np.float64)
    for b in range(n_boot):
        idx = circular_block_bootstrap_indices(n, block, rng)
        coef, _, _ = fit_ols(y[idx], X[idx])
        out[b] = coef
    return out


def pooled_rmse(residuals: Iterable[np.ndarray]) -> float:
    e = np.concatenate([np.asarray(r, dtype=np.float64).reshape(-1) for r in residuals])
    return float(np.sqrt(np.mean(e ** 2)))


def profile_tau2(
    estimates: np.ndarray,
    within_var: np.ndarray,
    grid: Optional[np.ndarray] = None,
) -> Tuple[float, float, float, float]:
    """Gaussian heteroscedastic random-effects: return mu, tau2, lo, hi (profile ~95%).

    Maximizes profile log-likelihood over tau2 >= 0.
    Interval: values with 2*(Lmax - L) <= 3.841458 (chi2_1 0.95).
    """
    y = np.asarray(estimates, dtype=np.float64)
    wvar = np.asarray(within_var, dtype=np.float64)
    wvar = np.maximum(wvar, 0.0)
    if grid is None:
        grid = np.unique(
            np.concatenate(
                [
                    np.array([0.0]),
                    np.logspace(-16, np.log10(max(np.var(y), 1e-16)) + 2, 400),
                ]
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
    thresh = nll_min + 0.5 * 3.841458448338683  # 0.5 * chi2 crit for -2Δll
    ok = [t2 for t2, v, _ in records if v <= thresh]
    lo = float(min(ok)) if ok else 0.0
    hi = float(max(ok)) if ok else tau2_hat
    return mu_hat, tau2_hat, lo, hi


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
        kmax = np.max(np.where(passed)[0])
        reject_sorted = np.zeros(m, dtype=bool)
        reject_sorted[: kmax + 1] = True
        reject = np.empty(m, dtype=bool)
        reject[order] = reject_sorted
    # BH adjusted p
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


def pearson_corr(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    from scipy.stats import pearsonr

    r, p = pearsonr(x, y)
    return float(r), float(p)
