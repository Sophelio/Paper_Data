"""Run frozen SIR and exact-coefficient audit rollouts on the 8 holdouts."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from prediction_model import (
    ATOL,
    AUDIT_A,
    AUDIT_B,
    DT,
    HOLDOUT_RECORD_IDS,
    HORIZONS_S,
    INTEGRATION_METHOD,
    RTOL,
    SIR_A,
    SIR_B,
    T_END,
    T_START,
    bundle_to_frame,
    holdout_paths,
    metrics_for_bundle,
    orbit_diagnostic,
    rollout_holdout_file,
)

ROOT = Path(__file__).resolve().parent
DATA_FOLDER = ROOT.parent / "data"
TRAJ_DIR = ROOT / "trajectories"
AUDIT_DIR = ROOT / "audit"
SUMMARY_PATH = ROOT / "prediction_summary.json"
METRICS_PATH = ROOT / "prediction_metrics.csv"


def run(data_folder: Path | None = None) -> dict:
    data_folder = Path(data_folder) if data_folder is not None else DATA_FOLDER
    TRAJ_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    metric_rows: list[dict] = []
    per_record: dict[str, dict] = {}
    pooled_err: dict[tuple[str, str, float], list[np.ndarray]] = {}
    bundles = {}

    for path in holdout_paths(data_folder):
        rid = path.stem
        bundle = rollout_holdout_file(path)
        bundles[rid] = bundle
        if not np.isfinite(bundle["theta_sir"]).all() or not np.isfinite(bundle["omega_sir"]).all():
            raise RuntimeError(f"non-finite SIR rollout for {rid}")
        frame = bundle_to_frame(bundle)
        frame.to_parquet(TRAJ_DIR / f"{rid}_prediction.parquet", index=False)
        frame[
            [
                "times",
                "theta_true",
                "omega_true",
                "theta_exact_audit",
                "omega_exact_audit",
                "theta_error_exact",
                "omega_error_exact",
            ]
        ].to_parquet(AUDIT_DIR / f"{rid}_audit.parquet", index=False)

        rows = metrics_for_bundle(bundle, rid)
        metric_rows.extend(rows)
        diag = orbit_diagnostic(bundle)
        i_final = int(np.argmax(bundle["times"]))
        per_record[rid] = {
            "theta0": float(bundle["theta_true"][0]),
            "omega0": float(bundle["omega_true"][0]),
            "theta_sir_t0": float(bundle["theta_sir"][0]),
            "omega_sir_t0": float(bundle["omega_sir"][0]),
            "final_abs_theta_sir": float(abs(bundle["theta_error_sir"][i_final])),
            "final_abs_omega_sir": float(abs(bundle["omega_error_sir"][i_final])),
            "final_abs_theta_audit": float(abs(bundle["theta_error_exact"][i_final])),
            "final_abs_omega_audit": float(abs(bundle["omega_error_exact"][i_final])),
            "final_abs_theta_sir_minus_audit": float(
                abs(bundle["theta_sir"][i_final] - bundle["theta_exact_audit"][i_final])
            ),
            "final_abs_omega_sir_minus_audit": float(
                abs(bundle["omega_sir"][i_final] - bundle["omega_exact_audit"][i_final])
            ),
            **diag,
        }
        # keep clean full-window unwrapped metrics
        full = [
            row for row in rows
            if row["metric_family"] == "unwrapped" and row["horizon_s"] == T_END
        ]
        per_record[rid]["full_window"] = {
            f"{row['model']}_{row['variable']}": {
                "rmse": row["rmse"],
                "mae": row["mae"],
                "max_abs": row["max_abs"],
            }
            for row in full
        }

        times = bundle["times"]
        for model, th_key, om_key, th_true, om_true in (
            ("sir", "theta_sir", "omega_sir", "theta_true", "omega_true"),
            ("exact_audit", "theta_exact_audit", "omega_exact_audit", "theta_true", "omega_true"),
        ):
            for horizon in HORIZONS_S:
                mask = times <= horizon + 1e-12
                for variable, pred_key, true_key in (
                    ("theta", th_key, th_true),
                    ("omega", om_key, om_true),
                ):
                    pooled_err.setdefault((model, variable, float(horizon)), []).append(
                        bundle[pred_key][mask] - bundle[true_key][mask]
                    )

    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(METRICS_PATH, index=False)

    pooled = []
    for key, chunks in sorted(pooled_err.items()):
        model, variable, horizon = key
        err = np.concatenate(chunks)
        pooled.append({
            "model": model,
            "variable": variable,
            "horizon_s": horizon,
            "rmse": float(np.sqrt(np.mean(err**2))),
            "mae": float(np.mean(np.abs(err))),
            "max_abs": float(np.max(np.abs(err))),
            "n": int(err.size),
        })

    summary = {
        "primary_model": {
            "dtheta_dt": "SIR_B * omega_hat",
            "domega_dt": "SIR_A * sin(theta_hat)",
            "a": SIR_A,
            "b": SIR_B,
            "source": "pre-calibration median A_i from Pendulum run 20260820-175024-08c0",
        },
        "audit_model": {
            "a": AUDIT_A,
            "b": AUDIT_B,
            "note": "exact generating coefficient; not the reported SIR result",
        },
        "solver": {
            "method": INTEGRATION_METHOD,
            "rtol": RTOL,
            "atol": ATOL,
            "t_start": T_START,
            "t_end": T_END,
            "dt": DT,
        },
        "holdout_ids": list(HOLDOUT_RECORD_IDS),
        "initialization": "theta_hat(0)=theta_obs(0), omega_hat(0)=omega_obs(0); autonomous thereafter",
        "horizons_s": list(HORIZONS_S),
        "pooled_unwrapped": pooled,
        "per_record": per_record,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    out = run()
    print("wrote", SUMMARY_PATH)
    print("holdouts", len(out["holdout_ids"]))
    for row in out["pooled_unwrapped"]:
        if row["model"] == "sir" and row["horizon_s"] in {0.5, 5.0, 30.0}:
            print(
                f"SIR {row['variable']:5s} 0-{row['horizon_s']:4g}s "
                f"RMSE={row['rmse']:.6g}  max={row['max_abs']:.6g}"
            )
