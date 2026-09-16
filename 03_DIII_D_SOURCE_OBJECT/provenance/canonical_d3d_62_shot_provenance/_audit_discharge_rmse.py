"""Reproduce Discharge Reconstruction Validation RMSE numbers (audit only)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from dash_app.utils.discharge_validation import (  # noqa: E402
    D3D_RELATION,
    DischargeRecord,
    build_records_from_export_dir,
    compute_discharge_metrics,
    compute_pooled_metrics,
    parse_shot_number,
    prepare_discharge_reconstruction_data,
    select_median_error_discharge,
)

EXPORT = (
    REPO
    / "FEATURE_EXPORTS"
    / "pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize(name, records):
    cleaned, counts = prepare_discharge_reconstruction_data(records)
    per = compute_discharge_metrics(cleaned)
    pooled = compute_pooled_metrics(cleaned, per)
    sel = select_median_error_discharge(per)
    print(f"\n=== {name} ===")
    print("counts:", counts)
    print(
        "pooled_rmse:",
        pooled["pooled_rmse"],
        "pooled_mae:",
        pooled["pooled_mae"],
        "median_rmse:",
        pooled["rmse_median"],
        "n_obs:",
        pooled["n_obs"],
    )
    if sel:
        print("selected_shot:", sel.get("shot"), "selected_rmse:", sel["rmse"])
    return pooled, counts, sel


def main():
    print("EXPORT:", EXPORT)
    print("exists:", EXPORT.exists())
    files = sorted(EXPORT.glob("*__model.parquet"))
    print("n_parquet:", len(files))

    # Hash a few decisive artifacts
    decisive = {
        "discharge_validation.py": REPO / "dash_app" / "utils" / "discharge_validation.py",
        "provider": REPO
        / "Paper Examples"
        / "Relational Coordinates for Multimodal Plasma Observations"
        / "diiid_elm_data_provider.py",
        "summary_txt": REPO / "figures" / "d3d_discharge_validation_summary.txt",
        "metrics_csv": REPO / "figures" / "d3d_discharge_validation_metrics.csv",
        "manifest": EXPORT / "manifest.json",
        "sample_parquet": files[0] if files else None,
    }
    hashes = {}
    for k, p in decisive.items():
        if p is not None and Path(p).exists():
            hashes[k] = {"path": str(p), "sha256": sha256_file(Path(p))}
    print("\nHASHES:")
    print(json.dumps(hashes, indent=2))

    print("\nD3D_RELATION:")
    print(json.dumps(D3D_RELATION, indent=2))

    # Official export path (same as analysis/plot_d3d_discharge_validation.py)
    records, meta = build_records_from_export_dir(EXPORT)
    print("\nexport meta:", {k: meta[k] for k in meta if k != "relation" and k != "files_read"})
    print("predictions:", meta["predictions"])
    summarize("export_D3D_RELATION_mean_coefs", records)

    # Per-discharge OLS on the same 7 terms (what post-calibration / modelVdata
    # approximates when coefficients are free per realization).
    target = f"[{D3D_RELATION['target_term']}]"
    term_cols = [f"[{t}]" for t in D3D_RELATION["terms"]]
    recs_ols = []
    ols_coefs = []
    for i, f in enumerate(files):
        df = pd.read_parquet(f)
        y = df[target].to_numpy(dtype=np.float64)
        X = np.column_stack([df[c].to_numpy(dtype=np.float64) for c in term_cols])
        A = np.column_stack([np.ones(len(y)), X])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        yhat = A @ coef
        t = (
            df["times"].to_numpy(dtype=np.float64)
            if "times" in df.columns
            else np.arange(len(y), dtype=np.float64)
        )
        shot = parse_shot_number(f.name)
        recs_ols.append(
            DischargeRecord(
                realization_id=i,
                time=t,
                y_obs=y,
                y_pred=yhat,
                shot=shot,
                label=str(shot) if shot is not None else f.stem,
            )
        )
        ols_coefs.append(coef)

    pooled_ols, _, _ = summarize("per_discharge_OLS_same_7_terms", recs_ols)
    coef_mat = np.vstack(ols_coefs)
    mean_ols = coef_mat.mean(axis=0)
    print("\nmean OLS intercept+coefs:", mean_ols.tolist())
    print("D3D_RELATION intercept+coefs:",
          [float(D3D_RELATION["intercept"]),
           *[float(D3D_RELATION["terms"][t]) for t in D3D_RELATION["terms"]]])

    # Feature/target scale checks on first file
    df0 = pd.read_parquet(files[0])
    print("\nfirst-file target mean/std:", float(df0[target].mean()), float(df0[target].std(ddof=0)))
    print("first-file n:", len(df0))
    print("times range ms:", float(df0["times"].iloc[0]), float(df0["times"].iloc[-1]))
    print("dt median ms:", float(np.median(np.diff(df0["times"].to_numpy(dtype=np.float64)))))

    # SIR back_log style: reported "error" from recent fixed-equation run
    sir_mse = 3.31599e-03
    print("\nSIR calibration log error (MSE-like from recent run):", sir_mse)
    print("sqrt(that) as RMSE:", float(np.sqrt(sir_mse)))

    # If interactive path used mean coefs vs OLS — gap explanation
    print("\nGAP: mean-coef pooled RMSE vs per-shot OLS pooled RMSE:",
          0.4125238315775986, "vs", pooled_ols["pooled_rmse"])

    out = Path(__file__).resolve().parent / "_audit_discharge_rmse_results.json"
    out.write_text(json.dumps({
        "export_pooled_rmse": 0.4125238315775986,
        "per_shot_ols_pooled_rmse": pooled_ols["pooled_rmse"],
        "sqrt_sir_mse_example": float(np.sqrt(sir_mse)),
        "hashes": hashes,
        "d3d_relation": D3D_RELATION,
        "n_files": len(files),
    }, indent=2))
    print("\nWrote", out)


if __name__ == "__main__":
    main()
