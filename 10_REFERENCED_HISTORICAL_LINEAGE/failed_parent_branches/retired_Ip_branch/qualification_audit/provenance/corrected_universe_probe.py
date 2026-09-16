"""D3D-FIG6-CORRECTED-UNIVERSE-PROBE-V1

Fair feasibility probe for a target-independent q_rec.

The provenance audit leaves only three admissible primitives:
    pcdiamag3 (W_dia), pinj (P_NBI), density (n_e)

A naive linear fit on those three raw levels fails badly on the protected 20%
(median held-out R^2 = -25.6). That probe is however unfair to a corrected SIR
search, which would build derivatives, lags, products and relational
coordinates. This script gives the corrected universe a genuinely fair chance
before any conclusion about feasibility is drawn.

It is a FEASIBILITY PROBE, not a replacement q_rec run: it does not perform
development-cohort support selection, does not freeze a support, and its
numbers must not be quoted as a corrected q_rec result.

Protocol matches the frozen study where it can:
    per discharge, first 80% calibrates, final 20% is protected;
    all scaling fitted on the calibration segment only.
"""

from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = ROOT / "data" / "resampled_data_v6"
FIG6 = ROOT / "fig6data"
ADMISSIBLE = ["pcdiamag3", "pinj", "density"]
SEED = 20260901


def loader(f):
    a = np.load(f, allow_pickle=False)
    return lambda n: (a[n + "_data"].astype(float), a[n + "_times"].astype(float))


def onto(g, name, tref):
    d, t = g(name)
    m = np.isfinite(t) & np.isfinite(d)
    return np.interp(tref, t[m], d[m], left=np.nan, right=np.nan)


def d_dt(v, t):
    out = np.full_like(v, np.nan)
    out[1:-1] = (v[2:] - v[:-2]) / np.where(t[2:] - t[:-2] != 0, t[2:] - t[:-2], np.nan)
    return out


def build(g, tref):
    """Relational-style universe from target-independent primitives only."""
    base = {s: onto(g, s, tref) for s in ADMISSIBLE}
    F = {}
    for s, v in base.items():
        F[f"L_{s}"] = v
        F[f"D_{s}"] = d_dt(v, tref)
        F[f"CU_{s}"] = np.sign(v) * np.abs(v) ** 3 / (np.nanstd(v) ** 3 or 1.0)
        F[f"LAG1_{s}"] = np.concatenate([[np.nan], v[:-1]])
        F[f"LAG2_{s}"] = np.concatenate([[np.nan] * 2, v[:-2]])
    ks = ADMISSIBLE
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            F[f"PROD_{ks[i]}_{ks[j]}"] = base[ks[i]] * base[ks[j]]
            den = base[ks[j]]
            sd = np.nanstd(den) or 1.0
            F[f"RATIO_{ks[i]}_{ks[j]}"] = base[ks[i]] * den / (den ** 2 + (0.1 * sd) ** 2)
            F[f"DRATIO_{ks[i]}_{ks[j]}"] = (
                d_dt(base[ks[i]], tref) * den / (den ** 2 + (0.1 * sd) ** 2))
    return F


def ridge(X, y, lam):
    n, p = X.shape
    A = X.T @ X + lam * np.eye(p)
    return np.linalg.solve(A, X.T @ y)


def main() -> None:
    files = sorted(glob.glob(str(DATA / "shot_*_resampled.npz")))
    rows = []
    for f in files:
        shot = Path(f).name.split("_")[1]
        g = loader(f)
        ip_d, ip_t = g("ip")
        ok = np.isfinite(ip_t) & np.isfinite(ip_d) & (np.abs(ip_d) > 1e5)
        tref, y = ip_t[ok], np.abs(ip_d[ok])
        if len(tref) < 300:
            continue
        F = build(g, tref)
        names = sorted(F)
        X = np.column_stack([F[k] for k in names])
        m = np.isfinite(X).all(axis=1) & np.isfinite(y)
        X, y2, n = X[m], y[m], int(m.sum())
        if n < 300:
            continue
        cut = int(0.8 * n)
        mu, sd = X[:cut].mean(0), X[:cut].std(0)
        sd[sd <= 0] = 1.0
        Z = (X - mu) / sd
        y0 = y2[:cut].mean()
        # ridge strength chosen inside the calibration segment only
        best = None
        icut = int(0.8 * cut)
        for lam in (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0):
            b = ridge(Z[:icut], y2[:icut] - y0, lam)
            v = float(np.sqrt(np.mean((Z[icut:cut] @ b + y0 - y2[icut:cut]) ** 2)))
            if best is None or v < best[1]:
                best = (lam, v)
        b = ridge(Z[:cut], y2[:cut] - y0, best[0])
        pred = Z[cut:] @ b + y0
        yt = y2[cut:]
        scale = np.std(y2[:cut]) or 1.0
        rows.append({
            "shot": shot, "n_calib": cut, "n_eval": len(yt), "lambda": best[0],
            "rmse_norm": float(np.sqrt(np.mean((pred - yt) ** 2)) / scale),
            "r2": float(1 - np.sum((pred - yt) ** 2)
                        / max(np.sum((yt - yt.mean()) ** 2), 1e-12)),
            "n_features": len(names)})
    df = pd.DataFrame(rows)
    df.to_csv(FIG6 / "qrec_corrected_universe_probe.csv", index=False)

    out = {
        "probe_id": "D3D-FIG6-CORRECTED-UNIVERSE-PROBE-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FEASIBILITY_PROBE_NOT_A_QREC_RESULT",
        "admissible_primitives": ADMISSIBLE,
        "n_features_per_shot": int(df.n_features.iloc[0]) if len(df) else 0,
        "n_shots": int(len(df)),
        "median_normalised_rmse": float(df.rmse_norm.median()) if len(df) else None,
        "median_r2": float(df.r2.median()) if len(df) else None,
        "frac_r2_above_0": float((df.r2 > 0).mean()) if len(df) else None,
        "frac_r2_above_0p5": float((df.r2 > 0.5).mean()) if len(df) else None,
        "caveat": "No development-cohort support selection and no frozen "
                  "support. These numbers establish only whether the corrected "
                  "universe can support the task at all; they are not a "
                  "corrected q_rec result and must not be quoted as one.",
    }
    (HERE / "CORRECTED_UNIVERSE_PROBE.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print("corrected-universe feasibility probe (target-independent only)")
    print(f"  primitives : {ADMISSIBLE}")
    print(f"  features   : {out['n_features_per_shot']} per discharge")
    print(f"  shots      : {out['n_shots']}")
    print(f"  median normalised RMSE (protected 20%) : "
          f"{out['median_normalised_rmse']:.4f}")
    print(f"  median R^2                              : {out['median_r2']:.4f}")
    print(f"  frac R^2 > 0                            : {out['frac_r2_above_0']:.3f}")
    print(f"  frac R^2 > 0.5                          : {out['frac_r2_above_0p5']:.3f}")


if __name__ == "__main__":
    main()
