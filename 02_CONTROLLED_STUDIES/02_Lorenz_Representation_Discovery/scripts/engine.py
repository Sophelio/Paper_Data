"""Shared engine: candidate representations, contracts, CV, metrics.

Coordinate construction (C) is imported from the FIRST benchmark's audited
`features.py`, which was verified elementwise (rtol=0, atol=1e-12) against the
canonical Archaieus implementation. It is imported, never re-derived.

Relation families (R) are kept explicitly separate from C: `identity` (linear in
the supplied coordinates), `poly2` and `poly3` (conventional polynomial
libraries over the information-matched raw stencil). The polynomial families
exist so the conventional PySINDy workflow gets a genuinely strong baseline and
is not compared as a merely-linear fit on raw coordinates.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from pysindy.feature_library import PolynomialLibrary
from pysindy.optimizers import STLSQ
from sklearn.model_selection import GroupKFold

TCB = Path(__file__).resolve().parent.parent
PRIOR = TCB.parent / "benchmark"
sys.path.insert(0, str(PRIOR / "scripts"))
import features as F  # noqa: E402  audited coordinate implementation

CFG = yaml.safe_load((TCB / "benchmark_config.yaml").read_text(encoding="utf-8"))
DEV_DIR = Path(CFG["provenance"]["development_source"])
CONF_DIR = TCB / "shared" / "confirmation"


# ===========================================================================
# Candidate representations — fixed, finite, scored identically by every
# contract. A fixed list (rather than greedy search) is what makes
# "same object, different contract, different selection" an auditable claim.
# ===========================================================================
Q4 = ["Q[dy|x]", "Q[y|x]", "Q[dy|dx]", "Q[dx|dy]"]
RS2 = ["RS[dy|x]", "RS[y|x]"]
SC2 = ["SC[dy|x]", "SC[y|x]"]
CA2 = ["CA[dy|x]", "CA[y|x]"]
PRODUCTS = [c.name for c in F.COORDS if c.family == "product"]
RATES = ["dx", "dy"]
CURV = ["d2x", "d2y"]


def candidates() -> dict:
    """name -> (coordinate list, relation family)."""
    M = F.C0_MATCHED
    return {
        "C0_center":            (F.C0_CENTER, "identity"),
        "C0_matched":           (M, "identity"),
        "C0_poly2":             (M, "poly2"),
        "C0_poly3":             (M, "poly3"),
        "C0+rates":             (M + RATES, "identity"),
        "C0+rates+curv":        (M + RATES + CURV, "identity"),
        "C0+products":          (M + PRODUCTS, "identity"),
        "C0+Q_dy_x":            (M + ["Q[dy|x]"], "identity"),
        "C0+Q_pair":            (M + ["Q[dy|x]", "Q[y|x]"], "identity"),
        "C0+Q_phase":           (M + ["Q[dy|dx]"], "identity"),
        "C0+Q_all":             (M + Q4, "identity"),
        "C0+CA_pair":           (M + CA2, "identity"),
        "C0+RS_pair":           (M + RS2, "identity"),
        "C0+SC_pair":           (M + SC2, "identity"),
        "C0+RS+SC":             (M + RS2 + SC2, "identity"),
        "C0+Q_pair+RS_pair":    (M + ["Q[dy|x]", "Q[y|x]"] + RS2, "identity"),
        "C_all":                (F.COORD_NAMES, "identity"),
    }


def expand(X: np.ndarray, family: str) -> np.ndarray:
    """Apply the relation family R to a coordinate matrix C.

    PolynomialLibrary returns pysindy's AxesArray subclass, whose ufunc
    machinery rejects downstream matrix ops; cast back to a plain ndarray.
    """
    X = np.asarray(X, dtype=np.float64)
    if family == "identity":
        return X
    deg = {"poly2": 2, "poly3": 3}[family]
    lib = PolynomialLibrary(degree=deg, include_bias=False)
    return np.asarray(lib.fit_transform(X), dtype=np.float64)


# ===========================================================================
# Data
# ===========================================================================
def dev_ids() -> list[str]:
    return sorted(p.stem for p in DEV_DIR.glob("*.parquet"))


def conf_ids() -> list[str]:
    return sorted(p.stem for p in CONF_DIR.glob("*.parquet"))


def _load(path: Path):
    df = pd.read_parquet(path)
    return (df["x"].to_numpy(np.float64), df["y"].to_numpy(np.float64),
            df["z"].to_numpy(np.float64),
            float(df["times"].iloc[1] - df["times"].iloc[0]))


def load_split(which: str, noise: float = 0.0, seed: int | None = None):
    """Load trajectories; noise is applied to x,y BEFORE any coordinate build."""
    d = DEV_DIR if which == "development" else CONF_DIR
    ids = dev_ids() if which == "development" else conf_ids()
    rng = np.random.default_rng(seed if seed is not None else 0)
    out = []
    for tid in ids:
        x, y, z, dt = _load(d / f"{tid}.parquet")
        if noise > 0:
            # sigma relative to this channel's std; drawn per trajectory.
            x = x + rng.normal(0.0, noise * x.std(), x.shape)
            y = y + rng.normal(0.0, noise * y.std(), y.shape)
        out.append({"id": tid, "x": x, "y": y, "z": z, "dt": dt})
    return out


def build(recs, fit: F.CoordinateFit | None):
    """Attach base quantities and (if fitted) coordinate values."""
    for r in recs:
        r["base"] = F.base_quantities(r["x"], r["y"], r["dt"])
        r["vals"] = F.apply_coordinates(r["base"], fit) if fit else None
    return recs


# Selection-time row stride. Coordinates (and their stencils) are always built
# at FULL resolution; only the rows entering the cross-validated *selection*
# fits are strided, to keep the 18-candidate x 6-fold x 8-regime sweep
# tractable. Confirmation evaluation uses stride 1. Declared pre-freeze.
SELECTION_STRIDE = 8


def support(rec, names, stride: int = 1) -> np.ndarray:
    m = F.interior_mask(len(rec["x"]))
    M = F.build_matrix(rec["vals"], names)
    ok = m & np.isfinite(M).all(axis=1) & np.isfinite(rec["z"])
    if stride > 1:
        keep = np.zeros_like(ok)
        keep[::stride] = True
        ok = ok & keep
    return ok


def stack(recs, cols, sup):
    X = np.concatenate([F.build_matrix(r["vals"], cols)[s]
                        for r, s in zip(recs, sup)], axis=0)
    y = np.concatenate([r["z"][s] for r, s in zip(recs, sup)], axis=0)
    return X, y


# ===========================================================================
# Estimator (PySINDy STLSQ as the common sparse solver)
# ===========================================================================
def fit_stlsq(Xtr, ytr, Xva, yva, thresholds):
    """STLSQ carries no intercept; the target is centred on the TRAIN mean and
    the offset restored at predict time."""
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    y0 = float(ytr.mean())
    Ztr, Zva = (Xtr - mu) / sd, (Xva - mu) / sd
    best = None
    for thr in thresholds:
        opt = STLSQ(threshold=thr, alpha=CFG["estimators"]["stlsq"]["alpha"])
        opt.fit(Ztr, ytr - y0)
        coef = np.asarray(opt.coef_, dtype=np.float64).ravel()
        rmse = float(np.sqrt(np.mean((Zva @ coef + y0 - yva) ** 2)))
        cand = {"threshold": thr, "coef": coef, "y0": y0, "mu": mu, "sd": sd,
                "rmse": rmse, "n_terms": int(np.count_nonzero(coef))}
        if best is None or cand["rmse"] < best["rmse"]:
            best = cand
    return best


def predict(m, X):
    return ((X - m["mu"]) / m["sd"]) @ m["coef"] + m["y0"]


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def nrmse(y_true, y_pred):
    s = float(np.std(y_true))
    return rmse(y_true, y_pred) / (s if s > 0 else 1.0)


# ===========================================================================
# Grouped cross-validation on DEVELOPMENT only
# ===========================================================================
@dataclass
class CVResult:
    name: str
    fold_rmse: list
    mean_rmse: float
    se_rmse: float
    n_coordinates: int
    n_features: int
    n_terms: float
    cond: float
    coverage: float


def grouped_cv(recs, cols, family, thresholds, n_folds):
    """GroupKFold over trajectories. Coordinate fits are refitted inside each
    training fold, so no fold's validation trajectories inform its transforms."""
    groups = np.arange(len(recs))
    gkf = GroupKFold(n_splits=n_folds)
    fold_rmse, terms, conds = [], [], []
    for tr_i, va_i in gkf.split(groups, groups=groups):
        tr = [recs[i] for i in tr_i]
        va = [recs[i] for i in va_i]
        str_ = [support(r, cols, SELECTION_STRIDE) for r in tr]
        sva = [support(r, cols, SELECTION_STRIDE) for r in va]
        Xtr, ytr = stack(tr, cols, str_)
        Xva, yva = stack(va, cols, sva)
        Xtr, Xva = expand(Xtr, family), expand(Xva, family)
        m = fit_stlsq(Xtr, ytr, Xva, yva, thresholds)
        fold_rmse.append(m["rmse"])
        terms.append(m["n_terms"])
        Z = (Xtr - Xtr.mean(0)) / np.where(Xtr.std(0) > 0, Xtr.std(0), 1.0)
        conds.append(float(np.linalg.cond(Z)))
    allsup = [support(r, cols, SELECTION_STRIDE) for r in recs]
    cov = float(sum(s.sum() for s in allsup) / sum(s.size for s in allsup))
    Xa, _ = stack(recs, cols, allsup)
    return CVResult(
        name="", fold_rmse=fold_rmse,
        mean_rmse=float(np.mean(fold_rmse)),
        se_rmse=float(np.std(fold_rmse, ddof=1) / np.sqrt(len(fold_rmse))),
        n_coordinates=len(cols),
        n_features=int(expand(Xa[:2], family).shape[1]),
        n_terms=float(np.mean(terms)),
        cond=float(np.median(conds)), coverage=cov,
    )


# ===========================================================================
# Contract selection rules
# ===========================================================================
def select_accuracy(results: dict) -> tuple[str, dict]:
    """q_accuracy: minimum mean CV error. No compactness preference."""
    best = min(results, key=lambda k: results[k].mean_rmse)
    return best, {"rule": "min mean CV RMSE", "equivalent_set": [best]}


def select_one_se(results: dict, key="mean_rmse") -> tuple[str, dict]:
    """q_compact / q_robust: one-standard-error rule, then lexicographic
    (fewer coordinates -> better conditioning -> fewer terms -> fold stability).
    """
    best = min(results, key=lambda k: getattr(results[k], key))
    thr = getattr(results[best], key) + results[best].se_rmse
    equiv = [k for k in results if getattr(results[k], key) <= thr]
    ranked = sorted(
        equiv,
        key=lambda k: (results[k].n_coordinates, results[k].cond,
                       results[k].n_terms,
                       float(np.std(results[k].fold_rmse))),
    )
    return ranked[0], {
        "rule": "one-SE then lexicographic "
                "[n_coordinates, condition_number, n_terms, fold_stability]",
        "best_by_error": best,
        "threshold": float(thr),
        "equivalent_set": ranked,
    }
