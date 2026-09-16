"""Step 12 — INDEPENDENT external PySINDy task-selection wrapper.

CONTROL CONDITION. This module deliberately does NOT import anything from
``sir_contract``. It reimplements the declared selection logic from scratch
using PySINDy and ordinary Python data structures:

    * grouped cross-validated scoring;
    * the one-standard-error / practical-floor equivalence rule;
    * complexity, conditioning and stability ordering;
    * the final lexicographic choice.

It consumes the same frozen coordinate matrices and the same development folds —
those are part of the controlled comparison — but every decision rule is written
here independently. ``tests/test_wrapper_independence.py`` asserts that this file
never imports or calls the SIR contract-selection implementation.

The question it answers: *if the SIR discovery contract is implemented by hand
around PySINDy, can PySINDy serve as the numerical relation solver inside that
larger procedure?* Agreement with the harness is the EXPECTED and desirable
outcome, and supports the nesting interpretation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import yaml
from pysindy.feature_library import PolynomialLibrary
from pysindy.optimizers import STLSQ
from sklearn.model_selection import GroupKFold

TCB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TCB.parent / "benchmark" / "scripts"))
import features as F  # noqa: E402  coordinate values only, no selection logic

CFG = yaml.safe_load((TCB / "benchmark_config.yaml").read_text(encoding="utf-8"))


# --- independent numerics ---------------------------------------------------
def _poly(X, degree):
    lib = PolynomialLibrary(degree=degree, include_bias=False)
    return np.asarray(lib.fit_transform(np.asarray(X, float)), dtype=float)


def _design(X, family):
    X = np.asarray(X, dtype=float)
    if family == "identity":
        return X
    return _poly(X, {"poly2": 2, "poly3": 3}[family])


def _stlsq_rmse(Xtr, ytr, Xva, yva, thresholds):
    """PySINDy STLSQ as the relation solver; threshold chosen on the fold."""
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd[sd <= 0] = 1.0
    off = float(ytr.mean())
    best_rmse, best_terms = np.inf, 0
    for t in thresholds:
        est = STLSQ(threshold=t, alpha=0.0)
        est.fit((Xtr - mu) / sd, ytr - off)
        w = np.asarray(est.coef_, dtype=float).ravel()
        pred = ((Xva - mu) / sd) @ w + off
        r = float(np.sqrt(np.mean((pred - yva) ** 2)))
        if r < best_rmse:
            best_rmse, best_terms = r, int(np.count_nonzero(w))
    return best_rmse, best_terms


def _rows(rec, cols, stride):
    ok = F.interior_mask(len(rec["x"]))
    M = F.build_matrix(rec["vals"], cols)
    ok = ok & np.isfinite(M).all(axis=1) & np.isfinite(rec["z"])
    if stride > 1:
        k = np.zeros_like(ok)
        k[::stride] = True
        ok = ok & k
    return ok


def _gather(recs, cols, stride):
    masks = [_rows(r, cols, stride) for r in recs]
    X = np.concatenate([F.build_matrix(r["vals"], cols)[m]
                        for r, m in zip(recs, masks)], axis=0)
    y = np.concatenate([r["z"][m] for r, m in zip(recs, masks)], axis=0)
    return X, y


# --- independent scoring ----------------------------------------------------
def score(recs, cols, family, stride, n_folds, thresholds) -> dict:
    idx = np.arange(len(recs))
    folds, terms, conds = [], [], []
    for tr, va in GroupKFold(n_splits=n_folds).split(idx, groups=idx):
        Xtr, ytr = _gather([recs[i] for i in tr], cols, stride)
        Xva, yva = _gather([recs[i] for i in va], cols, stride)
        Xtr, Xva = _design(Xtr, family), _design(Xva, family)
        r, t = _stlsq_rmse(Xtr, ytr, Xva, yva, thresholds)
        folds.append(r)
        terms.append(t)
        s = Xtr.std(axis=0)
        s[s <= 0] = 1.0
        conds.append(float(np.linalg.cond((Xtr - Xtr.mean(axis=0)) / s)))
    n = len(folds)
    return {
        "fold_rmse": folds,
        "mean": float(np.mean(folds)),
        "se": float(np.std(folds, ddof=1) / np.sqrt(n)),
        "terms": float(np.mean(terms)),
        "cond": float(np.median(conds)),
        "n_coordinates": len(cols),
        "stability": float(np.std(folds)),
    }


# --- independent selection rules -------------------------------------------
def choose_min(scores: dict) -> str:
    """Minimum mean CV error; no secondary preference."""
    return min(scores.items(), key=lambda kv: kv[1]["mean"])[0]


def choose_equivalent_then_simplest(scores: dict, floor: float,
                                    order: list) -> tuple:
    """One-SE-or-floor equivalence, then the declared lexicographic order."""
    top = min(scores.items(), key=lambda kv: kv[1]["mean"])
    limit = top[1]["mean"] + max(top[1]["se"], floor)
    pool = {k: v for k, v in scores.items() if v["mean"] <= limit}
    field = {"n_coordinates": "n_coordinates", "n_terms": "terms",
             "condition_number": "cond", "fold_stability": "stability"}
    winner = sorted(pool, key=lambda k: tuple(pool[k][field[o]] for o in order))[0]
    return winner, sorted(pool), limit
