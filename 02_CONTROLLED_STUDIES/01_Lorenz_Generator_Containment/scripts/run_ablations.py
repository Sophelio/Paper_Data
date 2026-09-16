"""Step 10 — predeclared secondary analyses: noise, sample efficiency, resolution.

These were declared in benchmark_config.yaml BEFORE any test evaluation and do
not redefine the primary benchmark.

Noise is applied to the OBSERVED x and y only, BEFORE any derivative or
relational coordinate is built, so every derived coordinate inherits the noise
rather than being computed from clean data. Coordinate fits are re-fitted on the
noisy TRAIN split for each noise level; the protected test split is only scored.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

BENCH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BENCH / "scripts"))
import features as F  # noqa: E402
from run_benchmark import (  # noqa: E402
    CFG, DATA, fit_mlp, fit_stlsq, load_traj, metrics, predict_mlp,
    predict_stlsq, shared_support, split_ids, stack,
)


def assemble_noisy(ids, fit, noise, seed, stride=1):
    """Build coordinates from noisy, optionally downsampled observations."""
    rng = np.random.default_rng(seed)
    out = []
    for k, tid in enumerate(ids):
        df, dt = load_traj(tid)
        x = df["x"].to_numpy(np.float64)[::stride]
        y = df["y"].to_numpy(np.float64)[::stride]
        z = df["z"].to_numpy(np.float64)[::stride]
        dt = dt * stride
        if noise > 0:
            # sigma relative to each channel's own train-set std
            x = x + rng.normal(0.0, noise * x.std(), size=x.shape)
            y = y + rng.normal(0.0, noise * y.std(), size=y.shape)
        base = F.base_quantities(x, y, dt)
        vals = F.apply_coordinates(base, fit) if fit is not None else None
        out.append({"id": tid, "base": base, "z": z, "n": len(x), "dt": dt,
                    "vals": vals})
    return out


def evaluate(reps, recs, sup, label_extra):
    rows = []
    Xtr_all = {}
    for rep_name, cols in reps.items():
        Xtr, ytr = stack(recs["train"], cols, sup["train"])
        Xva, yva = stack(recs["validation"], cols, sup["validation"])
        Xte, yte = stack(recs["test"], cols, sup["test"])
        sp = fit_stlsq(Xtr, ytr, Xva, yva, CFG["estimators"]["stlsq"]["thresholds"])
        te = metrics(yte, predict_stlsq(sp, Xte))
        rows.append({**label_extra, "representation": rep_name, "learner": "STLSQ",
                     "n_coordinates": len(cols), "test_rmse": te["rmse"],
                     "test_r2": te["r2"], "n_test": te["n"]})
        seeds = CFG["estimators"]["mlp"]["seeds"][:3]
        vals = []
        for sd in seeds:
            mp = fit_mlp(Xtr, ytr, Xva, yva, sd)
            vals.append(metrics(yte, predict_mlp(mp, Xte))["rmse"])
        rows.append({**label_extra, "representation": rep_name, "learner": "MLP",
                     "n_coordinates": len(cols),
                     "test_rmse": float(np.mean(vals)),
                     "test_rmse_std": float(np.std(vals)),
                     "test_r2": float("nan"), "n_test": int(len(yte))})
    return rows


def main() -> None:
    tr, va, te = (split_ids(s) for s in ("train", "validation", "test"))
    frozen = json.loads(
        (BENCH / "sir" / "frozen_selection" / "FROZEN_REPRESENTATION.json")
        .read_text(encoding="utf-8")
    )
    Cstar = frozen["selected_coordinates"]
    names = F.COORD_NAMES
    rows = []

    # ---------------- A. noise sweep -------------------------------------
    for noise in CFG["ablations"]["noise_levels"]:
        tr_raw = assemble_noisy(tr, None, noise, seed=1000)
        fit = F.fit_coordinates([r["base"] for r in tr_raw], CFG)
        recs = {
            "train": assemble_noisy(tr, fit, noise, seed=1000),
            "validation": assemble_noisy(va, fit, noise, seed=2000),
            "test": assemble_noisy(te, fit, noise, seed=3000),
        }
        sup = {s: [shared_support(r, names) for r in recs[s]] for s in recs}
        reps = {"C0_matched": F.C0_MATCHED, "C_all": names, "C_star": Cstar}
        rows += evaluate(reps, recs, sup, {"ablation": "noise", "level": noise})
        print(f"noise={noise}: done "
              f"(support={sum(m.sum() for m in sup['test'])/sum(m.size for m in sup['test']):.3f})")

    # ---------------- B. training-set fraction ---------------------------
    fit0 = F.fit_coordinates(
        [r["base"] for r in assemble_noisy(tr, None, 0.0, seed=1000)], CFG)
    recs_full = {
        "train": assemble_noisy(tr, fit0, 0.0, seed=1000),
        "validation": assemble_noisy(va, fit0, 0.0, seed=2000),
        "test": assemble_noisy(te, fit0, 0.0, seed=3000),
    }
    sup_full = {s: [shared_support(r, names) for r in recs_full[s]]
                for s in recs_full}
    # Small but non-zero noise so the comparison is not degenerate at RMSE~0.
    fitn = F.fit_coordinates(
        [r["base"] for r in assemble_noisy(tr, None, 0.01, seed=1000)], CFG)
    recs_n = {
        "train": assemble_noisy(tr, fitn, 0.01, seed=1000),
        "validation": assemble_noisy(va, fitn, 0.01, seed=2000),
        "test": assemble_noisy(te, fitn, 0.01, seed=3000),
    }
    sup_n = {s: [shared_support(r, names) for r in recs_n[s]] for s in recs_n}

    for frac in CFG["ablations"]["train_fractions"]:
        k = max(1, int(round(frac * len(tr))))
        sub = {"train": recs_n["train"][:k], "validation": recs_n["validation"],
               "test": recs_n["test"]}
        subsup = {"train": sup_n["train"][:k], "validation": sup_n["validation"],
                  "test": sup_n["test"]}
        reps = {"C0_matched": F.C0_MATCHED, "C_all": names, "C_star": Cstar}
        rows += evaluate(reps, sub, subsup,
                         {"ablation": "train_fraction", "level": frac,
                          "n_train_trajectories": k})
        print(f"train_fraction={frac} (n={k}): done")

    # ---------------- C. temporal resolution ------------------------------
    for stride in CFG["ablations"]["downsample_factors"]:
        tr_raw = assemble_noisy(tr, None, 0.0, seed=1000, stride=stride)
        fit = F.fit_coordinates([r["base"] for r in tr_raw], CFG)
        recs = {
            "train": assemble_noisy(tr, fit, 0.0, seed=1000, stride=stride),
            "validation": assemble_noisy(va, fit, 0.0, seed=2000, stride=stride),
            "test": assemble_noisy(te, fit, 0.0, seed=3000, stride=stride),
        }
        sup = {s: [shared_support(r, names) for r in recs[s]] for s in recs}
        reps = {"C0_matched": F.C0_MATCHED, "C_all": names, "C_star": Cstar}
        rows += evaluate(reps, recs, sup,
                         {"ablation": "resolution", "level": stride,
                          "dt": CFG["ensemble"]["dt"] * stride})
        print(f"stride={stride}: done")

    df = pd.DataFrame(rows)
    df.to_csv(BENCH / "tables" / "ablation_results.csv", index=False)
    print(f"\nwrote tables/ablation_results.csv ({len(df)} rows)")
    for ab in df["ablation"].unique():
        print(f"\n{ab}")
        sub = df[df["ablation"] == ab]
        print(sub.pivot_table(index=["level", "learner"],
                              columns="representation",
                              values="test_rmse").to_string(float_format=lambda v: f"{v:.4g}"))


if __name__ == "__main__":
    main()
