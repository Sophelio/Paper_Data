"""Steps 6-9 — hidden-z reconstruction: representation selection and evaluation.

Pipeline
--------
1. Evaluate every declared coordinate on all 48 trajectories, with all
   fit-dependent parameters fitted on TRAIN ONLY.
2. Define one shared evaluation support (interior stencil mask AND finite across
   every column of C_all) so every method is scored on identical rows.
3. Select C* on TRAIN + VALIDATION only, by the rule declared in
   benchmark_config.yaml. Freeze it to FROZEN_REPRESENTATION.json.
4. Evaluate PySINDy STLSQ and a fixed MLP on C0_center, C0_matched, C_all, C*.
   Sparse thresholds and MLP early stopping use validation only.
5. Score once on the PROTECTED test trajectories.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from pysindy.optimizers import STLSQ
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

BENCH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BENCH / "scripts"))
import features as F  # noqa: E402

CFG = yaml.safe_load((BENCH / "benchmark_config.yaml").read_text(encoding="utf-8"))
DATA = BENCH / "shared" / "data" / "ensemble"
SPLITS = BENCH / "shared" / "splits"
RNG_SEEDS = CFG["estimators"]["mlp"]["seeds"]


# ===========================================================================
# Data assembly
# ===========================================================================
def split_ids(name: str) -> list[str]:
    return (SPLITS / f"{name}.txt").read_text(encoding="utf-8").split()


def load_traj(tid: str):
    df = pd.read_parquet(DATA / f"{tid}.parquet")
    dt = float(df["times"].iloc[1] - df["times"].iloc[0])
    return df, dt


def assemble(ids: list[str], fit: F.CoordinateFit | None, dt_expected=None):
    """Return per-trajectory (coord_values, z, mask)."""
    out = []
    for tid in ids:
        df, dt = load_traj(tid)
        x = df["x"].to_numpy(np.float64)
        y = df["y"].to_numpy(np.float64)
        z = df["z"].to_numpy(np.float64)          # TARGET ONLY — never a feature
        base = F.base_quantities(x, y, dt)
        vals = F.apply_coordinates(base, fit) if fit is not None else None
        out.append({"id": tid, "base": base, "z": z, "n": len(x), "dt": dt,
                    "vals": vals})
    return out


def shared_support(rec, names) -> np.ndarray:
    """Interior stencil mask AND finite across every C_all column."""
    m = F.interior_mask(rec["n"])
    M = F.build_matrix(rec["vals"], names)
    return m & np.isfinite(M).all(axis=1) & np.isfinite(rec["z"])


def stack(recs, names, support):
    X = np.concatenate([F.build_matrix(r["vals"], names)[s] for r, s in
                        zip(recs, support)], axis=0)
    y = np.concatenate([r["z"][s] for r, s in zip(recs, support)], axis=0)
    return X, y


# ===========================================================================
# Metrics
# ===========================================================================
def metrics(y_true, y_pred) -> dict:
    err = y_pred - y_true
    rmse = float(np.sqrt(np.mean(err**2)))
    var = float(np.var(y_true))
    return {
        "rmse": rmse,
        "nrmse": float(rmse / np.std(y_true)),
        "r2": float(1.0 - np.mean(err**2) / var) if var > 0 else float("nan"),
        "mae": float(np.mean(np.abs(err))),
        "n": int(len(y_true)),
    }


def bootstrap_ci(per_traj, n_boot=2000, seed=0):
    """Percentile CI of the mean per-trajectory RMSE across test trajectories."""
    rng = np.random.default_rng(seed)
    v = np.asarray(per_traj, dtype=float)
    if len(v) < 2:
        return [float("nan"), float("nan")]
    means = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(n_boot)]
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


# ===========================================================================
# Estimators
# ===========================================================================
def fit_stlsq(Xtr, ytr, Xva, yva, thresholds):
    """Threshold chosen on VALIDATION only.

    pysindy's STLSQ carries no intercept (a SINDy library supplies its own bias
    column), so the target is centred on the TRAIN mean here and the offset is
    added back at predict time. Without this the estimator would be forced
    through the origin against a target whose mean is ~24.
    """
    best = None
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    y0 = float(ytr.mean())
    Ztr = (Xtr - mu) / sd
    Zva = (Xva - mu) / sd
    for thr in thresholds:
        opt = STLSQ(threshold=thr, alpha=CFG["estimators"]["stlsq"]["alpha"])
        opt.fit(Ztr, ytr - y0)
        coef = np.asarray(opt.coef_).ravel()
        m = metrics(yva, Zva @ coef + y0)
        cand = {"threshold": thr, "coef": coef, "intercept": y0,
                "mu": mu, "sd": sd, "val_rmse": m["rmse"],
                "n_terms": int(np.count_nonzero(coef))}
        if best is None or cand["val_rmse"] < best["val_rmse"]:
            best = cand
    return best


def predict_stlsq(model, X):
    return ((X - model["mu"]) / model["sd"]) @ model["coef"] + model["intercept"]


def fit_mlp(Xtr, ytr, Xva, yva, seed):
    """Scaler fitted on TRAIN only; early stopping uses a validation fraction
    carved from TRAIN, never the protected test set."""
    sc = StandardScaler().fit(Xtr)
    m = CFG["estimators"]["mlp"]
    net = MLPRegressor(
        hidden_layer_sizes=tuple(m["hidden_layer_sizes"]),
        activation=m["activation"], solver=m["solver"], alpha=m["alpha"],
        learning_rate_init=m["learning_rate_init"], max_iter=m["max_iter"],
        early_stopping=m["early_stopping"], n_iter_no_change=m["n_iter_no_change"],
        random_state=seed,
    )
    net.fit(sc.transform(Xtr), ytr)
    return {"net": net, "scaler": sc,
            "val_rmse": metrics(yva, net.predict(sc.transform(Xva)))["rmse"],
            "n_params": int(sum(c.size for c in net.coefs_)
                            + sum(b.size for b in net.intercepts_))}


def predict_mlp(model, X):
    return model["net"].predict(model["scaler"].transform(X))


# ===========================================================================
# Representation selection (TRAIN + VALIDATION only)
# ===========================================================================
def select_representation(recs_tr, recs_va, sup_tr, sup_va, all_names):
    """Greedy forward selection from C0_matched over the derived candidates.

    Declared rule (benchmark_config.yaml):
      primary criterion  = validation RMSE
      candidates within `equivalence_rel_tol` of the best are equivalent;
      among equivalents prefer FEWER coordinates.
    Selection stops when no candidate improves validation RMSE by more than
    the equivalence tolerance. The protected test set is never touched.
    """
    tol = float(CFG["selection"]["equivalence_rel_tol"])
    cap = int(CFG["selection"]["max_coordinates"])
    pool = [n for n in all_names if n not in F.C0_MATCHED]

    chosen = list(F.C0_MATCHED)
    Xtr, ytr = stack(recs_tr, chosen, sup_tr)
    Xva, yva = stack(recs_va, chosen, sup_va)
    base = fit_stlsq(Xtr, ytr, Xva, yva, CFG["estimators"]["stlsq"]["thresholds"])
    history = [{"step": 0, "added": None, "val_rmse": base["val_rmse"],
                "n_coords": len(chosen)}]
    cur = base["val_rmse"]

    while len(chosen) < cap and pool:
        scored = []
        for cand in pool:
            trial = chosen + [cand]
            Xt, yt = stack(recs_tr, trial, sup_tr)
            Xv, yv = stack(recs_va, trial, sup_va)
            mdl = fit_stlsq(Xt, yt, Xv, yv,
                            CFG["estimators"]["stlsq"]["thresholds"])
            scored.append((mdl["val_rmse"], cand))
        scored.sort()
        best_rmse, best_cand = scored[0]
        if best_rmse >= cur * (1.0 - tol):
            break                      # no candidate clears the declared margin
        chosen.append(best_cand)
        pool.remove(best_cand)
        cur = best_rmse
        history.append({"step": len(history), "added": best_cand,
                        "val_rmse": cur, "n_coords": len(chosen)})
    return chosen, history


# ===========================================================================
# Main
# ===========================================================================
def main() -> None:
    tr_ids, va_ids, te_ids = (split_ids(s) for s in
                              ("train", "validation", "test"))
    print(f"train={len(tr_ids)} validation={len(va_ids)} test={len(te_ids)}")

    # -- fit coordinates on TRAIN only -------------------------------------
    tr_raw = assemble(tr_ids, None)
    fit = F.fit_coordinates([r["base"] for r in tr_raw], CFG)
    print("coordinate fit (train only):")
    for k, v in fit.shift_fits.items():
        print(f"  {k}: s_0={v['s_0']:.4f} s_eff={v['s_eff']:.4f} "
              f"g_bar={v['g_bar']:.6f}")

    recs = {s: assemble(i, fit) for s, i in
            (("train", tr_ids), ("validation", va_ids), ("test", te_ids))}
    names = F.COORD_NAMES
    sup = {s: [shared_support(r, names) for r in recs[s]] for s in recs}
    for s in sup:
        tot = sum(m.size for m in sup[s])
        kept = sum(m.sum() for m in sup[s])
        print(f"  support {s}: {kept}/{tot} = {kept/tot:.4f} retained")

    # -- select C* on train+validation only --------------------------------
    Cstar, history = select_representation(
        recs["train"], recs["validation"], sup["train"], sup["validation"], names
    )
    added = [h["added"] for h in history if h["added"]]
    print(f"\nC* = C0_matched + {added}  ({len(Cstar)} coordinates)")

    reps = {
        "C0_center": F.C0_CENTER,
        "C0_matched": F.C0_MATCHED,
        "C_all": names,
        "C_star": Cstar,
    }

    frozen = {
        "selected_coordinates": Cstar,
        "added_over_C0_matched": added,
        "selection_history": history,
        "selection_rule": CFG["selection"],
        "coordinate_fit": fit.as_dict(),
        "representations": {k: v for k, v in reps.items()},
        "splits": {"train": tr_ids, "validation": va_ids, "test": te_ids},
        "support_retained_fraction": {
            s: float(sum(m.sum() for m in sup[s]) / sum(m.size for m in sup[s]))
            for s in sup
        },
    }
    payload = json.dumps(frozen, indent=2, sort_keys=True)
    frozen["sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    out = BENCH / "sir" / "frozen_selection" / "FROZEN_REPRESENTATION.json"
    out.write_text(json.dumps(frozen, indent=2), encoding="utf-8")
    print(f"froze {out.name} sha256={frozen['sha256'][:16]}")

    # -- evaluate ----------------------------------------------------------
    rows, per_traj_rows = [], []
    for rep_name, cols in reps.items():
        Xtr, ytr = stack(recs["train"], cols, sup["train"])
        Xva, yva = stack(recs["validation"], cols, sup["validation"])

        sp = fit_stlsq(Xtr, ytr, Xva, yva, CFG["estimators"]["stlsq"]["thresholds"])
        Xte, yte = stack(recs["test"], cols, sup["test"])
        te = metrics(yte, predict_stlsq(sp, Xte))
        ptr = []
        for r, s in zip(recs["test"], sup["test"]):
            Xi = F.build_matrix(r["vals"], cols)[s]
            mi = metrics(r["z"][s], predict_stlsq(sp, Xi))
            ptr.append(mi["rmse"])
            per_traj_rows.append({"representation": rep_name, "learner": "STLSQ",
                                  "trajectory": r["id"], "rmse": mi["rmse"],
                                  "r2": mi["r2"], "n": mi["n"]})
        rows.append({
            "representation": rep_name, "learner": "STLSQ",
            "n_coordinates": len(cols), "n_terms": sp["n_terms"],
            "threshold": sp["threshold"], "val_rmse": sp["val_rmse"],
            "test_rmse": te["rmse"], "test_nrmse": te["nrmse"], "test_r2": te["r2"],
            "test_mae": te["mae"], "n_test_samples": te["n"],
            "per_traj_median": float(np.median(ptr)),
            "per_traj_iqr": float(np.percentile(ptr, 75) - np.percentile(ptr, 25)),
            "ci_lo": bootstrap_ci(ptr)[0], "ci_hi": bootstrap_ci(ptr)[1],
            "cond_number": float(np.linalg.cond(
                (Xtr - Xtr.mean(0)) / np.where(Xtr.std(0) > 0, Xtr.std(0), 1.0))),
        })

        seed_rmse, seed_r2, npar = [], [], None
        for sd in RNG_SEEDS:
            mp = fit_mlp(Xtr, ytr, Xva, yva, sd)
            npar = mp["n_params"]
            mm = metrics(yte, predict_mlp(mp, Xte))
            seed_rmse.append(mm["rmse"])
            seed_r2.append(mm["r2"])
            for r, s in zip(recs["test"], sup["test"]):
                Xi = F.build_matrix(r["vals"], cols)[s]
                mi = metrics(r["z"][s], predict_mlp(mp, Xi))
                per_traj_rows.append({"representation": rep_name,
                                      "learner": f"MLP(seed={sd})",
                                      "trajectory": r["id"], "rmse": mi["rmse"],
                                      "r2": mi["r2"], "n": mi["n"]})
        rows.append({
            "representation": rep_name, "learner": "MLP",
            "n_coordinates": len(cols), "n_terms": npar,
            "threshold": None, "val_rmse": float("nan"),
            "test_rmse": float(np.mean(seed_rmse)),
            "test_rmse_std": float(np.std(seed_rmse)),
            "test_nrmse": float(np.mean(seed_rmse) / np.std(yte)),
            "test_r2": float(np.mean(seed_r2)),
            "test_mae": float("nan"), "n_test_samples": int(len(yte)),
            "per_traj_median": float("nan"), "per_traj_iqr": float("nan"),
            "ci_lo": float(np.mean(seed_rmse) - 1.96 * np.std(seed_rmse)),
            "ci_hi": float(np.mean(seed_rmse) + 1.96 * np.std(seed_rmse)),
            "cond_number": float("nan"),
        })
        print(f"  {rep_name:12s} STLSQ test_rmse={rows[-2]['test_rmse']:.4f} "
              f"| MLP test_rmse={rows[-1]['test_rmse']:.4f} "
              f"+/-{rows[-1]['test_rmse_std']:.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(BENCH / "tables" / "benchmark_results.csv", index=False)
    pd.DataFrame(per_traj_rows).to_csv(
        BENCH / "tables" / "per_trajectory_results.csv", index=False)
    pd.DataFrame(
        [{"coordinate": c, "in_C_star": c in Cstar,
          "family": next(k.family for k in F.COORDS if k.name == c)}
         for c in names]
    ).to_csv(BENCH / "tables" / "selected_coordinates.csv", index=False)

    (BENCH / "benchmark_results.json").write_text(
        json.dumps({"rows": rows, "C_star": Cstar,
                    "frozen_sha256": frozen["sha256"]}, indent=2), encoding="utf-8")
    print("\nwrote tables/benchmark_results.csv and per_trajectory_results.csv")


if __name__ == "__main__":
    main()
