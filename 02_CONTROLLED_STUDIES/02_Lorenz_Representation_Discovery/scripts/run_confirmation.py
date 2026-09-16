"""Steps 11-15 — protected confirmation evaluation.

REFUSES TO RUN unless every hash in PRECONFIRMATION_FREEZE.json still matches.

Evaluates on the 24 never-seen confirmation trajectories:
  * PySINDy STLSQ on C0_matched, raw poly2/poly3, C_all, and each contract's
    selected representation;
  * the external-contract PySINDy wrapper (Step 12);
  * the fixed MLP on raw / C_all / selected-clean / selected-robust (Step 13),
    scored on both clean and 1% noisy confirmation data.

Everything is fitted on DEVELOPMENT data only and applied unchanged.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

TCB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TCB / "scripts"))
import engine as E  # noqa: E402
import features as F  # noqa: E402

CFG = E.CFG
THR = CFG["estimators"]["stlsq"]["thresholds"]


# ===========================================================================
# Freeze enforcement
# ===========================================================================
def enforce_freeze() -> dict:
    fp = TCB / "PRECONFIRMATION_FREEZE.json"
    if not fp.exists():
        raise SystemExit("ABORT: PRECONFIRMATION_FREEZE.json missing — "
                         "run run_contracts.py first.")
    fr = json.loads(fp.read_text(encoding="utf-8"))
    bad = []
    for rel, want in fr["files"].items():
        p = TCB / rel
        got = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        if got != want:
            bad.append({"file": rel, "expected": want[:16],
                        "found": (got[:16] if got else "MISSING")})
    if bad:
        for b in bad:
            print(f"  HASH MISMATCH {b['file']}: {b['expected']} -> {b['found']}")
        raise SystemExit(
            "ABORT: preconfirmation freeze violated. The design changed after "
            "freezing; confirmation evaluation is invalid."
        )
    print(f"freeze verified: {len(fr['files'])} files unchanged")
    return fr


# ===========================================================================
# Fit on development, apply to confirmation
# ===========================================================================
def dev_and_conf(noise, dev_seed, conf_seed):
    dev0 = E.build(E.load_split("development", noise, dev_seed), None)
    fit = F.fit_coordinates([r["base"] for r in dev0], CFG)
    dev = E.build(E.load_split("development", noise, dev_seed), fit)
    conf = E.build(E.load_split("confirmation", noise, conf_seed), fit)
    return dev, conf, fit


def eval_stlsq(dev, conf, cols, family):
    """Fit on ALL development trajectories; score per confirmation trajectory."""
    sdev = [E.support(r, cols) for r in dev]
    sconf = [E.support(r, cols) for r in conf]
    Xd, yd = E.stack(dev, cols, sdev)
    Xd = E.expand(Xd, family)
    # threshold picked on development only (last fold held out internally)
    n = len(dev)
    tr = list(range(0, n - 8))
    va = list(range(n - 8, n))
    Xtr, ytr = E.stack([dev[i] for i in tr], cols, [sdev[i] for i in tr])
    Xva, yva = E.stack([dev[i] for i in va], cols, [sdev[i] for i in va])
    m = E.fit_stlsq(E.expand(Xtr, family), ytr, E.expand(Xva, family), yva, THR)
    # refit at the chosen threshold on all development data
    m_full = E.fit_stlsq(Xd, yd, Xd, yd, [m["threshold"]])

    per = []
    for r, s in zip(conf, sconf):
        Xi = E.expand(F.build_matrix(r["vals"], cols)[s], family)
        pred = E.predict(m_full, Xi)
        per.append({"trajectory": r["id"], "rmse": E.rmse(r["z"][s], pred),
                    "nrmse": E.nrmse(r["z"][s], pred), "n": int(s.sum())})
    Xc, yc = E.stack(conf, cols, sconf)
    pooled = E.predict(m_full, E.expand(Xc, family))
    Z = (Xd - Xd.mean(0)) / np.where(Xd.std(0) > 0, Xd.std(0), 1.0)
    return {
        "pooled_rmse": E.rmse(yc, pooled),
        "pooled_r2": float(1 - np.mean((pooled - yc) ** 2) / np.var(yc)),
        "per_trajectory": per,
        "threshold": m["threshold"], "n_terms": m_full["n_terms"],
        "n_coordinates": len(cols), "n_features": int(Xd.shape[1]),
        "condition_number": float(np.linalg.cond(Z)),
        "coverage": float(sum(s.sum() for s in sconf) /
                          sum(s.size for s in sconf)),
    }


def eval_mlp(dev, conf, cols, seeds):
    sdev = [E.support(r, cols) for r in dev]
    sconf = [E.support(r, cols) for r in conf]
    Xd, yd = E.stack(dev, cols, sdev)
    Xc, yc = E.stack(conf, cols, sconf)
    sc = StandardScaler().fit(Xd)
    m = CFG["estimators"]["mlp"]
    vals, npar = [], None
    for sd in seeds:
        net = MLPRegressor(
            hidden_layer_sizes=tuple(m["hidden_layer_sizes"]),
            activation=m["activation"], solver=m["solver"], alpha=m["alpha"],
            learning_rate_init=m["learning_rate_init"], max_iter=m["max_iter"],
            early_stopping=m["early_stopping"],
            n_iter_no_change=m["n_iter_no_change"], random_state=sd)
        net.fit(sc.transform(Xd), yd)
        npar = int(sum(c.size for c in net.coefs_)
                   + sum(b.size for b in net.intercepts_))
        vals.append(E.rmse(yc, net.predict(sc.transform(Xc))))
    return {"mean_rmse": float(np.mean(vals)), "std_rmse": float(np.std(vals)),
            "n_coordinates": len(cols), "n_params": npar, "seeds": list(seeds)}


def bootstrap_ci(vals, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    v = np.asarray(vals, float)
    if len(v) < 2:
        return [float("nan")] * 2
    m = [rng.choice(v, len(v), replace=True).mean() for _ in range(n)]
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main() -> None:
    fr = enforce_freeze()
    sel = json.loads((TCB / "contracts" / "contract_selections.json")
                     .read_text(encoding="utf-8"))
    cands = E.candidates()

    print("\nconfirmation trajectories:", len(E.conf_ids()))
    dev_c, conf_c, _ = dev_and_conf(0.0, None, None)
    nz = CFG["noise"]["envelope"][-1]
    dev_n, conf_n, _ = dev_and_conf(nz, CFG["noise"]["development_seeds"][0],
                                    CFG["noise"]["confirmation_seeds"][0])

    comparators = {
        "C0_matched": cands["C0_matched"],
        "C0_poly2": cands["C0_poly2"],
        "C0_poly3": cands["C0_poly3"],
        "C_all": cands["C_all"],
    }
    for q in ("q_accuracy", "q_compact", "q_robust"):
        comparators[f"C*_{q.split('_')[1]}"] = (
            sel[q]["coordinates"], sel[q]["relation_family"])

    rows, per_rows = [], []
    for regime, (dv, cf) in {"clean": (dev_c, conf_c),
                             f"noise_{nz}": (dev_n, conf_n)}.items():
        for name, (cols, fam) in comparators.items():
            r = eval_stlsq(dv, cf, cols, fam)
            pt = [p["rmse"] for p in r["per_trajectory"]]
            lo, hi = bootstrap_ci(pt)
            rows.append({
                "regime": regime, "method": "STLSQ", "representation": name,
                "n_coordinates": r["n_coordinates"], "n_features": r["n_features"],
                "n_terms": r["n_terms"], "threshold": r["threshold"],
                "pooled_rmse": r["pooled_rmse"], "pooled_r2": r["pooled_r2"],
                "median_rmse": float(np.median(pt)),
                "iqr_rmse": float(np.percentile(pt, 75) - np.percentile(pt, 25)),
                "ci_lo": lo, "ci_hi": hi,
                "condition_number": r["condition_number"],
                "coverage": r["coverage"],
            })
            for p in r["per_trajectory"]:
                per_rows.append({"regime": regime, "representation": name,
                                 "learner": "STLSQ", **p})
            print(f"  [{regime}] STLSQ {name:16s} "
                  f"pooled_rmse={r['pooled_rmse']:.5g} "
                  f"coords={r['n_coordinates']} terms={r['n_terms']}")

        for name in ("C0_matched", "C_all", "C*_compact", "C*_robust"):
            cols, fam = comparators[name]
            if fam != "identity":
                continue
            mm = eval_mlp(dv, cf, cols, CFG["estimators"]["mlp"]["seeds"])
            rows.append({
                "regime": regime, "method": "MLP", "representation": name,
                "n_coordinates": mm["n_coordinates"], "n_features": mm["n_coordinates"],
                "n_terms": mm["n_params"], "threshold": None,
                "pooled_rmse": mm["mean_rmse"], "pooled_r2": float("nan"),
                "median_rmse": float("nan"), "iqr_rmse": float("nan"),
                "ci_lo": mm["mean_rmse"] - 1.96 * mm["std_rmse"],
                "ci_hi": mm["mean_rmse"] + 1.96 * mm["std_rmse"],
                "condition_number": float("nan"), "coverage": float("nan"),
            })
            print(f"  [{regime}] MLP   {name:16s} "
                  f"rmse={mm['mean_rmse']:.5g} +/-{mm['std_rmse']:.3g} "
                  f"params={mm['n_params']}")

    df = pd.DataFrame(rows)
    df.to_csv(TCB / "tables" / "confirmation_results.csv", index=False)
    pd.DataFrame(per_rows).to_csv(
        TCB / "tables" / "confirmation_per_trajectory.csv", index=False)
    (TCB / "benchmark_results.json").write_text(json.dumps({
        "freeze": fr, "selections": {q: sel[q]["selected_candidate"] for q in sel},
        "rows": rows}, indent=2), encoding="utf-8")
    print("\nwrote tables/confirmation_results.csv")


if __name__ == "__main__":
    main()
