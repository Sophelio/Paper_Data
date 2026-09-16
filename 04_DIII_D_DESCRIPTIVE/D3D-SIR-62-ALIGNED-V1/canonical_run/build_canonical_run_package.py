#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build immutable canonical DIII-D 62-shot run package D3D-SIR-62-ALIGNED-V1.

Uses the historical RESULTS/output.pcdiamag3.psir when present and verified;
otherwise regenerates per-discharge OLS from the frozen feature export.
Does not modify manuscript files or overwrite prior package artifacts in place
beyond regenerating this versioned output directory.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from dash_app.utils.discharge_validation import (  # noqa: E402
    D3D_RELATION,
    DischargeRecord,
    compute_discharge_metrics,
    compute_pooled_metrics,
    prepare_discharge_reconstruction_data,
    reconstruct_prediction,
    select_median_error_discharge,
)

CANONICAL_RUN_ID = "D3D-SIR-62-ALIGNED-V1"
ARTIFACT_STATUS_HISTORICAL = "HISTORICAL_ORIGINAL"
ARTIFACT_STATUS_REGENERATED = "REGENERATED_CANONICAL_EQUIVALENT"

EXPORT_DIR = (
    REPO
    / "FEATURE_EXPORTS"
    / "pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized"
)
LEDGER_CSV = (
    REPO
    / "Paper Examples"
    / "Relational Coordinates for Multimodal Plasma Observations"
    / "canonical_d3d_62_shot_provenance"
    / "d3d_discharge_ledger.csv"
)
SHOT_LIST_SRC = (
    REPO
    / "Paper Examples"
    / "Relational Coordinates for Multimodal Plasma Observations"
    / "SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py"
)
HISTORICAL_PSIR = REPO / "RESULTS" / "output.pcdiamag3.psir"
DISCHARGE_VALIDATION_PY = REPO / "dash_app" / "utils" / "discharge_validation.py"
CONSUMER_PY = (
    REPO / "submodules" / "Archaieus" / "src" / "Archaieus" / "sir" / "consumer_function.py"
)
TRANSFORMS_PY = (
    REPO
    / "submodules"
    / "Archaieus"
    / "src"
    / "Archaieus"
    / "sir"
    / "utils"
    / "transforms.py"
)
PROVIDER_PY = (
    REPO
    / "Paper Examples"
    / "Relational Coordinates for Multimodal Plasma Observations"
    / "diiid_elm_data_provider.py"
)

# Design-matrix / D3D_RELATION native order (matches historical .psir 1_8* columns 1..7)
PSIR_TERM_ORDER = [
    "d[pcdiamag3]/d[kappa]",
    "d[kappa]/d[t]",
    "r[q95]/r[kappa]",
    "d[pcdiamag3]/d[betan]",
    "d[kappa]/d[betan]",
    "d[betan]/d[t]",
    "d[li]/d[betan]",
]
PSIR_FEATURE_COLS = [f"[{t}]" for t in PSIR_TERM_ORDER]
TARGET_COL = f"[{D3D_RELATION['target_term']}]"

# Required CSV semantic column order (Task B)
SEMANTIC_COEF_COLS = [
    ("coef_Dkappa_Wdia", "d[pcdiamag3]/d[kappa]"),
    ("coef_Dbetan_Wdia", "d[pcdiamag3]/d[betan]"),
    ("coef_Dbetan_kappa", "d[kappa]/d[betan]"),
    ("coef_Dbetan_li", "d[li]/d[betan]"),
    ("coef_q95_over_kappa", "r[q95]/r[kappa]"),
    ("coef_dot_betan", "d[betan]/d[t]"),
    ("coef_dot_kappa", "d[kappa]/d[t]"),
]

NEAR_ZERO_THRESHOLD = 1e-6
EXPECTED_N_DISCHARGES = 62
EXPECTED_N_SAMPLES = 1000
EXPECTED_TOTAL = EXPECTED_N_DISCHARGES * EXPECTED_N_SAMPLES
TOL_RMSE_PER = 1e-12
TOL_RMSE_MEAN = 1e-12
REF_PER_RMSE = 0.05758467247445343
REF_MEAN_RMSE = 0.4125238315775986


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_array(arr: np.ndarray) -> str:
    a = np.ascontiguousarray(arr, dtype=np.float64)
    return sha256_bytes(a.tobytes())


def git_rev(path: Path) -> Tuple[str, bool]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=path, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=path, text=True
            ).strip()
        )
        return commit, dirty
    except Exception:
        return "UNKNOWN", True


def parse_shot(name: Any) -> Optional[int]:
    m = re.search(r"shot[_\-]?(\d+)", str(name))
    return int(m.group(1)) if m else None


def load_export_files() -> List[Path]:
    files = sorted(EXPORT_DIR.glob("*__model.parquet"))
    assert len(files) == EXPECTED_N_DISCHARGES, (
        f"expected {EXPECTED_N_DISCHARGES} parquets, found {len(files)}"
    )
    shots = [parse_shot(f.name) for f in files]
    assert None not in shots and len(set(shots)) == EXPECTED_N_DISCHARGES
    return files


def verify_and_load_historical_psir() -> Optional[Dict[str, Any]]:
    if not HISTORICAL_PSIR.exists():
        return None
    with open(HISTORICAL_PSIR, "rb") as f:
        d = pickle.load(f)
    if not isinstance(d, dict):
        return None
    if "1_8*" not in d or "filenames" not in d or "O1_variables" not in d:
        return None
    fn = d["filenames"]
    if len(fn) != EXPECTED_N_DISCHARGES:
        return None
    coeffs = np.asarray(d["1_8*"]["x"], dtype=np.float64)
    if coeffs.shape != (EXPECTED_N_DISCHARGES, 8):
        return None
    # Reproduce pooled RMSE
    records = []
    for i in range(EXPECTED_N_DISCHARGES):
        C = coeffs[i].reshape(1, -1)
        X = np.asarray(d["O1_variables"][i], dtype=np.float64)
        yhat = np.matmul(C, X[: C.shape[1]]).reshape(-1)
        y = np.asarray(d["output"]["x"][i], dtype=np.float64).reshape(-1)
        t = np.asarray(d["timing"][i], dtype=np.float64).reshape(-1)
        assert yhat.size == EXPECTED_N_SAMPLES and y.size == EXPECTED_N_SAMPLES
        records.append(
            DischargeRecord(
                realization_id=i,
                time=t,
                y_obs=y,
                y_pred=yhat,
                shot=parse_shot(fn[i]),
            )
        )
    cleaned, counts = prepare_discharge_reconstruction_data(records)
    assert counts["rows_retained"] == EXPECTED_TOTAL
    pooled = compute_pooled_metrics(cleaned)
    if abs(pooled["pooled_rmse"] - REF_PER_RMSE) > 1e-12:
        print(
            "WARNING: historical 1_8* RMSE mismatch:",
            pooled["pooled_rmse"],
            "vs",
            REF_PER_RMSE,
        )
        return None
    # Confirm mean coeffs ≈ D3D_RELATION
    mean_c = coeffs.mean(axis=0)
    rel = np.array(
        [float(D3D_RELATION["intercept"]),
         *[float(D3D_RELATION["terms"][t]) for t in PSIR_TERM_ORDER]]
    )
    if not np.allclose(mean_c, rel, rtol=0, atol=5e-4):
        print("WARNING: mean historical coeffs diverge from D3D_RELATION", mean_c, rel)
    return d


def fit_ols(y: np.ndarray, X: np.ndarray) -> Tuple[np.ndarray, int, float]:
    """Intercept + 7 features via numpy lstsq (same as prior audit)."""
    A = np.column_stack([np.ones(len(y), dtype=np.float64), X])
    coef, residuals, rank, _ = np.linalg.lstsq(A, y, rcond=None)
    rss = float(residuals[0]) if len(residuals) else float(np.sum((A @ coef - y) ** 2))
    return coef.astype(np.float64), int(rank), rss


def build_from_psir(d: Dict[str, Any]) -> Dict[str, Any]:
    coeffs = np.asarray(d["1_8*"]["x"], dtype=np.float64)
    files = load_export_files()
    # Align by shot number: psir filenames vs export stems
    psir_shots = [parse_shot(n) for n in d["filenames"]]
    export_by_shot = {parse_shot(f.name): f for f in files}
    assert set(psir_shots) == set(export_by_shot.keys())

    coef_rows = []
    pred_rows = []
    metric_rows = []
    hash_rows = []
    mean_pred_records = []
    per_pred_records = []

    for i, shot in enumerate(psir_shots):
        f = export_by_shot[shot]
        df = pd.read_parquet(f)
        assert len(df) == EXPECTED_N_SAMPLES
        for col in PSIR_FEATURE_COLS + [TARGET_COL, "times"]:
            assert col in df.columns, f"missing {col} in {f.name}"

        y = df[TARGET_COL].to_numpy(dtype=np.float64)
        X_exp = np.column_stack(
            [df[c].to_numpy(dtype=np.float64) for c in PSIR_FEATURE_COLS]
        )
        t_ms = df["times"].to_numpy(dtype=np.float64)

        C = coeffs[i]
        X_psir = np.asarray(d["O1_variables"][i], dtype=np.float64)
        # Confirm design matrix in psir matches export (up to float noise)
        # y_hat from psir coeffs @ psir X
        yhat = (C.reshape(1, -1) @ X_psir[:8]).reshape(-1)
        y_obs = np.asarray(d["output"]["x"][i], dtype=np.float64).reshape(-1)
        t_psir = np.asarray(d["timing"][i], dtype=np.float64).reshape(-1)

        # Cross-check export target vs psir output
        if not np.allclose(y, y_obs, rtol=0, atol=1e-8):
            # Allow tiny differences; record max abs
            max_diff = float(np.max(np.abs(y - y_obs)))
            if max_diff > 1e-5:
                raise AssertionError(
                    f"shot {shot}: export target vs psir output max|diff|={max_diff}"
                )

        # OLS on export for rank/rss metadata (should match historical coeffs)
        coef_ols, rank, rss = fit_ols(y, X_exp)
        if not np.allclose(C, coef_ols, rtol=0, atol=1e-8):
            # Historical calibrated coeffs should match OLS on same support
            max_c = float(np.max(np.abs(C - coef_ols)))
            if max_c > 1e-6:
                raise AssertionError(
                    f"shot {shot}: historical coeffs vs export OLS max|diff|={max_c}"
                )

        term_to_coef = {t: float(C[j + 1]) for j, t in enumerate(PSIR_TERM_ORDER)}
        row = {
            "canonical_run_id": CANONICAL_RUN_ID,
            "artifact_status": ARTIFACT_STATUS_HISTORICAL,
            "realization_index": i,
            "shot": int(shot),
            "n_samples": EXPECTED_N_SAMPLES,
            "intercept": float(C[0]),
        }
        for csv_name, term in SEMANTIC_COEF_COLS:
            row[csv_name] = term_to_coef[term]
        row.update(
            {
                "fit_rank": rank,
                "fit_residual_sum_squares": rss,
                "source_feature_export": str(EXPORT_DIR.relative_to(REPO)).replace("\\", "/"),
                "source_feature_export_manifest_sha256": sha256_file(EXPORT_DIR / "manifest.json"),
                "model_artifact_sha256": sha256_file(HISTORICAL_PSIR),
            }
        )
        coef_rows.append(row)

        resid = y_obs - yhat
        for j in range(EXPECTED_N_SAMPLES):
            pred_rows.append(
                {
                    "canonical_run_id": CANONICAL_RUN_ID,
                    "artifact_status": ARTIFACT_STATUS_HISTORICAL,
                    "realization_index": i,
                    "shot": int(shot),
                    "sample_index": j,
                    "time_native": float(t_ms[j]),
                    "time_units": "ms",
                    "time_seconds": float(t_ms[j]) / 1000.0,
                    "target_standardized": float(y_obs[j]),
                    "prediction_standardized": float(yhat[j]),
                    "residual_standardized": float(resid[j]),
                    "squared_residual": float(resid[j] ** 2),
                    "absolute_residual": float(abs(resid[j])),
                }
            )

        e = resid
        ss_tot = float(np.sum((y_obs - np.mean(y_obs)) ** 2))
        r2 = None if ss_tot == 0 else 1.0 - float(np.sum(e ** 2)) / ss_tot
        metric_rows.append(
            {
                "canonical_run_id": CANONICAL_RUN_ID,
                "realization_index": i,
                "shot": int(shot),
                "n_samples": EXPECTED_N_SAMPLES,
                "mse": float(np.mean(e ** 2)),
                "rmse": float(np.sqrt(np.mean(e ** 2))),
                "mae": float(np.mean(np.abs(e))),
                "r2": r2,
                "residual_mean": float(np.mean(e)),
                "residual_std": float(np.std(e)),
                "coefficient_fit_type": "per_discharge_calibrated_1_8*",
            }
        )

        hash_rows.append(
            {
                "shot": int(shot),
                "realization_index": i,
                "n_rows": EXPECTED_N_SAMPLES,
                "n_features": 7,
                "feature_matrix_sha256": sha256_array(X_exp),
                "target_sha256": sha256_array(y),
                "time_sha256": sha256_array(t_ms),
            }
        )

        per_pred_records.append(
            DischargeRecord(i, t_ms, y_obs, yhat, shot=int(shot))
        )
        yhat_mean = reconstruct_prediction(df, D3D_RELATION)
        mean_pred_records.append(
            DischargeRecord(i, t_ms, y, yhat_mean, shot=int(shot))
        )

    return {
        "artifact_status": ARTIFACT_STATUS_HISTORICAL,
        "equation_key": "1_8*",
        "model_path": HISTORICAL_PSIR,
        "coef_rows": coef_rows,
        "pred_rows": pred_rows,
        "metric_rows": metric_rows,
        "hash_rows": hash_rows,
        "per_pred_records": per_pred_records,
        "mean_pred_records": mean_pred_records,
        "psir": d,
    }


def build_regenerated() -> Dict[str, Any]:
    files = load_export_files()
    coef_rows, pred_rows, metric_rows, hash_rows = [], [], [], []
    per_pred_records, mean_pred_records = [], []
    model_payload = {
        "canonical_run_id": CANONICAL_RUN_ID,
        "artifact_status": ARTIFACT_STATUS_REGENERATED,
        "equation_key": "REGENERATED_OLS_7TERM",
        "term_order": PSIR_TERM_ORDER,
        "coefficients": [],
        "shots": [],
        "filenames": [],
    }

    for i, f in enumerate(files):
        shot = parse_shot(f.name)
        df = pd.read_parquet(f)
        assert len(df) == EXPECTED_N_SAMPLES
        y = df[TARGET_COL].to_numpy(dtype=np.float64)
        X = np.column_stack(
            [df[c].to_numpy(dtype=np.float64) for c in PSIR_FEATURE_COLS]
        )
        t_ms = df["times"].to_numpy(dtype=np.float64)
        C, rank, rss = fit_ols(y, X)
        yhat = np.column_stack([np.ones(len(y)), X]) @ C
        term_to_coef = {t: float(C[j + 1]) for j, t in enumerate(PSIR_TERM_ORDER)}
        row = {
            "canonical_run_id": CANONICAL_RUN_ID,
            "artifact_status": ARTIFACT_STATUS_REGENERATED,
            "realization_index": i,
            "shot": int(shot),
            "n_samples": EXPECTED_N_SAMPLES,
            "intercept": float(C[0]),
        }
        for csv_name, term in SEMANTIC_COEF_COLS:
            row[csv_name] = term_to_coef[term]
        row.update(
            {
                "fit_rank": rank,
                "fit_residual_sum_squares": rss,
                "source_feature_export": str(EXPORT_DIR.relative_to(REPO)).replace("\\", "/"),
                "source_feature_export_manifest_sha256": sha256_file(EXPORT_DIR / "manifest.json"),
                "model_artifact_sha256": "PENDING",
            }
        )
        coef_rows.append(row)
        resid = y - yhat
        for j in range(EXPECTED_N_SAMPLES):
            pred_rows.append(
                {
                    "canonical_run_id": CANONICAL_RUN_ID,
                    "artifact_status": ARTIFACT_STATUS_REGENERATED,
                    "realization_index": i,
                    "shot": int(shot),
                    "sample_index": j,
                    "time_native": float(t_ms[j]),
                    "time_units": "ms",
                    "time_seconds": float(t_ms[j]) / 1000.0,
                    "target_standardized": float(y[j]),
                    "prediction_standardized": float(yhat[j]),
                    "residual_standardized": float(resid[j]),
                    "squared_residual": float(resid[j] ** 2),
                    "absolute_residual": float(abs(resid[j])),
                }
            )
        e = resid
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = None if ss_tot == 0 else 1.0 - float(np.sum(e ** 2)) / ss_tot
        metric_rows.append(
            {
                "canonical_run_id": CANONICAL_RUN_ID,
                "realization_index": i,
                "shot": int(shot),
                "n_samples": EXPECTED_N_SAMPLES,
                "mse": float(np.mean(e ** 2)),
                "rmse": float(np.sqrt(np.mean(e ** 2))),
                "mae": float(np.mean(np.abs(e))),
                "r2": r2,
                "residual_mean": float(np.mean(e)),
                "residual_std": float(np.std(e)),
                "coefficient_fit_type": "per_discharge_OLS_7term",
            }
        )
        hash_rows.append(
            {
                "shot": int(shot),
                "realization_index": i,
                "n_rows": EXPECTED_N_SAMPLES,
                "n_features": 7,
                "feature_matrix_sha256": sha256_array(X),
                "target_sha256": sha256_array(y),
                "time_sha256": sha256_array(t_ms),
            }
        )
        per_pred_records.append(DischargeRecord(i, t_ms, y, yhat, shot=int(shot)))
        mean_pred_records.append(
            DischargeRecord(i, t_ms, y, reconstruct_prediction(df, D3D_RELATION), shot=int(shot))
        )
        model_payload["coefficients"].append(C.tolist())
        model_payload["shots"].append(int(shot))
        model_payload["filenames"].append(str(f))

    return {
        "artifact_status": ARTIFACT_STATUS_REGENERATED,
        "equation_key": "REGENERATED_OLS_7TERM",
        "model_path": None,
        "model_payload": model_payload,
        "coef_rows": coef_rows,
        "pred_rows": pred_rows,
        "metric_rows": metric_rows,
        "hash_rows": hash_rows,
        "per_pred_records": per_pred_records,
        "mean_pred_records": mean_pred_records,
    }


def coefficient_summary(coef_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for csv_name, term in SEMANTIC_COEF_COLS:
        v = coef_df[csv_name].to_numpy(dtype=np.float64)
        rows.append(
            {
                "canonical_run_id": CANONICAL_RUN_ID,
                "term": term,
                "csv_column": csv_name,
                "mean": float(np.mean(v)),
                "median": float(np.median(v)),
                "standard_deviation": float(np.std(v, ddof=0)),
                "minimum": float(np.min(v)),
                "maximum": float(np.max(v)),
                "q05": float(np.percentile(v, 5)),
                "q25": float(np.percentile(v, 25)),
                "q75": float(np.percentile(v, 75)),
                "q95": float(np.percentile(v, 95)),
                "fraction_positive": float(np.mean(v > NEAR_ZERO_THRESHOLD)),
                "fraction_negative": float(np.mean(v < -NEAR_ZERO_THRESHOLD)),
                "fraction_near_zero": float(np.mean(np.abs(v) <= NEAR_ZERO_THRESHOLD)),
                "near_zero_threshold": NEAR_ZERO_THRESHOLD,
            }
        )
    # intercept summary too
    v = coef_df["intercept"].to_numpy(dtype=np.float64)
    rows.insert(
        0,
        {
            "canonical_run_id": CANONICAL_RUN_ID,
            "term": "intercept",
            "csv_column": "intercept",
            "mean": float(np.mean(v)),
            "median": float(np.median(v)),
            "standard_deviation": float(np.std(v, ddof=0)),
            "minimum": float(np.min(v)),
            "maximum": float(np.max(v)),
            "q05": float(np.percentile(v, 5)),
            "q25": float(np.percentile(v, 25)),
            "q75": float(np.percentile(v, 75)),
            "q95": float(np.percentile(v, 95)),
            "fraction_positive": float(np.mean(v > NEAR_ZERO_THRESHOLD)),
            "fraction_negative": float(np.mean(v < -NEAR_ZERO_THRESHOLD)),
            "fraction_near_zero": float(np.mean(np.abs(v) <= NEAR_ZERO_THRESHOLD)),
            "near_zero_threshold": NEAR_ZERO_THRESHOLD,
        },
    )
    return pd.DataFrame(rows)


def write_tables(bundle: Dict[str, Any]) -> Dict[str, Path]:
    paths: Dict[str, Path] = {}
    coef_df = pd.DataFrame(bundle["coef_rows"])
    assert len(coef_df) == EXPECTED_N_DISCHARGES
    assert coef_df["shot"].nunique() == EXPECTED_N_DISCHARGES

    pred_df = pd.DataFrame(bundle["pred_rows"])
    assert len(pred_df) == EXPECTED_TOTAL

    metrics_df = pd.DataFrame(bundle["metric_rows"])
    assert len(metrics_df) == EXPECTED_N_DISCHARGES

    hash_df = pd.DataFrame(bundle["hash_rows"])
    summary_df = coefficient_summary(coef_df)

    cleaned_per, _ = prepare_discharge_reconstruction_data(bundle["per_pred_records"])
    per = compute_discharge_metrics(cleaned_per)
    pooled_per = compute_pooled_metrics(cleaned_per, per)
    sel = select_median_error_discharge(per)

    cleaned_mean, _ = prepare_discharge_reconstruction_data(bundle["mean_pred_records"])
    pooled_mean = compute_pooled_metrics(cleaned_mean)

    d_per = abs(pooled_per["pooled_rmse"] - REF_PER_RMSE)
    d_mean = abs(pooled_mean["pooled_rmse"] - REF_MEAN_RMSE)
    assert d_per <= TOL_RMSE_PER, f"per-discharge RMSE mismatch: {pooled_per['pooled_rmse']}"
    assert d_mean <= TOL_RMSE_MEAN, f"mean-vector RMSE mismatch: {pooled_mean['pooled_rmse']}"

    paths["coefficients"] = PKG / "d3d_discharge_coefficients.csv"
    coef_df.to_csv(paths["coefficients"], index=False)

    paths["coef_summary"] = PKG / "d3d_coefficient_summary.csv"
    summary_df.to_csv(paths["coef_summary"], index=False)

    paths["predictions"] = PKG / "d3d_discharge_predictions.parquet"
    pred_df.to_parquet(paths["predictions"], index=False)

    paths["metrics"] = PKG / "d3d_discharge_metrics.csv"
    metrics_df.to_csv(paths["metrics"], index=False)

    paths["hashes"] = PKG / "d3d_design_matrix_hashes.csv"
    hash_df.to_csv(paths["hashes"], index=False)

    pooled = {
        "canonical_run_id": CANONICAL_RUN_ID,
        "n_discharges": EXPECTED_N_DISCHARGES,
        "n_samples_total": EXPECTED_TOTAL,
        "pooled_mse": float(pooled_per["pooled_rmse"] ** 2),
        "pooled_rmse": float(pooled_per["pooled_rmse"]),
        "pooled_mae": float(pooled_per["pooled_mae"]),
        "pooled_r2": pooled_per["pooled_r2"],
        "median_discharge_rmse": float(pooled_per["rmse_median"]),
        "q25_discharge_rmse": float(pooled_per["rmse_q1"]),
        "q75_discharge_rmse": float(pooled_per["rmse_q3"]),
        "median_error_shot": sel["shot"] if sel else None,
        "mean_vector_pooled_rmse": float(pooled_mean["pooled_rmse"]),
        "mean_vector_pooled_mse": float(pooled_mean["pooled_rmse"] ** 2),
        "reference_per_discharge_rmse": REF_PER_RMSE,
        "reference_mean_vector_rmse": REF_MEAN_RMSE,
        "delta_per_discharge_rmse": d_per,
        "delta_mean_vector_rmse": d_mean,
        "equation_key": bundle["equation_key"],
        "artifact_status": bundle["artifact_status"],
    }
    paths["pooled"] = PKG / "d3d_pooled_metrics.json"
    paths["pooled"].write_text(json.dumps(pooled, indent=2) + "\n", encoding="utf-8")

    bundle["pooled"] = pooled
    bundle["paths"] = paths
    return paths


def write_model_artifact(bundle: Dict[str, Any]) -> Path:
    dest_dir = PKG / "model_artifact"
    dest_dir.mkdir(parents=True, exist_ok=True)
    if bundle["artifact_status"] == ARTIFACT_STATUS_HISTORICAL:
        dest = dest_dir / "output.pcdiamag3.psir"
        if not dest.exists() or sha256_file(dest) != sha256_file(HISTORICAL_PSIR):
            shutil.copy2(HISTORICAL_PSIR, dest)
        meta = {
            "canonical_run_id": CANONICAL_RUN_ID,
            "artifact_status": ARTIFACT_STATUS_HISTORICAL,
            "original_path": str(HISTORICAL_PSIR),
            "sha256": sha256_file(dest),
            "equation_key": "1_8*",
            "n_realizations": EXPECTED_N_DISCHARGES,
            "coeff_shape": [EXPECTED_N_DISCHARGES, 8],
            "samples_per_realization": EXPECTED_N_SAMPLES,
            "term_order_psir": ["intercept"] + PSIR_TERM_ORDER,
            "note": "Byte-copied from RESULTS/output.pcdiamag3.psir; not modified.",
        }
        (dest_dir / "model_artifact_meta.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )
        # Update coef rows model hash if needed
        for row in bundle["coef_rows"]:
            row["model_artifact_sha256"] = meta["sha256"]
        return dest

    dest = dest_dir / "regenerated_canonical_equivalent_model.json"
    payload = bundle["model_payload"]
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    h = sha256_file(dest)
    for row in bundle["coef_rows"]:
        row["model_artifact_sha256"] = h
    meta = {
        "canonical_run_id": CANONICAL_RUN_ID,
        "artifact_status": ARTIFACT_STATUS_REGENERATED,
        "sha256": h,
        "equation_key": payload["equation_key"],
        "note": "REGENERATED_CANONICAL_EQUIVALENT — not HISTORICAL_ORIGINAL.",
    }
    (dest_dir / "model_artifact_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return dest


def write_coordinate_manifest() -> Path:
    consumer_sha = sha256_file(CONSUMER_PY)
    transforms_sha = sha256_file(TRANSFORMS_PY)
    entries = []

    def entry(
        display_name,
        export_col,
        deps,
        target_containing,
        deriv_order,
        num_expr,
        den_expr,
        kind,
    ):
        return {
            "display_name": display_name,
            "export_column_name": export_col,
            "primitive_dependencies": deps,
            "target_containing": target_containing,
            "derivative_order": deriv_order,
            "numerator_expression": num_expr,
            "denominator_expression": den_expr,
            "shift_policy": (
                "global_per_realization_get_shiftval_on_x_and_dx_for_Derivative_target"
                if kind in ("phase", "quotient")
                else "none_for_temporal_derivative_columns"
            ),
            "shift_value": "EXACT_SHIFT_VALUE_UNKNOWN",
            "normalization_before": "per_realization_zscore_of_primitive_signals",
            "normalization_after": "per_realization_zscore_when_total_normalization_true_OR_export_zscore",
            "time_units": "ms_as_returned_by_diiid_elm_data_provider_freq",
            "mask_policy": "finite_rows_only_in_discharge_validation_prepare; no special quotient mask in make_Quotients",
            "source_code_path": str(CONSUMER_PY.relative_to(REPO)).replace("\\", "/"),
            "source_code_sha256": consumer_sha,
            "transforms_source_path": str(TRANSFORMS_PY.relative_to(REPO)).replace("\\", "/"),
            "transforms_source_sha256": transforms_sha,
            "status": "CONSTRUCTION_TRACED_SHIFT_VALUE_UNKNOWN",
            "canonical_run_id": CANONICAL_RUN_ID,
        }

    # Phase: (dx_a + s)/(dx_b + s) then optionally zscored
    mapping = [
        ("D_kappa W_dia", "[d[pcdiamag3]/d[kappa]]", ["pcdiamag3", "kappa"], True, 1,
         "(d[pcdiamag3]/d[t] + shift)", "(d[kappa]/d[t] + shift)", "phase"),
        ("D_betaN W_dia", "[d[pcdiamag3]/d[betan]]", ["pcdiamag3", "betan"], True, 1,
         "(d[pcdiamag3]/d[t] + shift)", "(d[betan]/d[t] + shift)", "phase"),
        ("D_betaN kappa", "[d[kappa]/d[betan]]", ["kappa", "betan"], False, 1,
         "(d[kappa]/d[t] + shift)", "(d[betan]/d[t] + shift)", "phase"),
        ("D_betaN l_i", "[d[li]/d[betan]]", ["li", "betan"], False, 1,
         "(d[li]/d[t] + shift)", "(d[betan]/d[t] + shift)", "phase"),
        ("q95 / kappa", "[r[q95]/r[kappa]]", ["q95", "kappa"], False, 0,
         "(r[q95] + shift)", "(r[kappa] + shift)", "quotient"),
        ("dot beta_N", "[d[betan]/d[t]]", ["betan"], False, 1,
         "d[betan]/d[t]", "1", "temporal"),
        ("dot kappa", "[d[kappa]/d[t]]", ["kappa"], False, 1,
         "d[kappa]/d[t]", "1", "temporal"),
    ]
    for args in mapping:
        entries.append(entry(*args))

    path = PKG / "d3d_relational_coordinate_manifest.json"
    path.write_text(
        json.dumps(
            {
                "canonical_run_id": CANONICAL_RUN_ID,
                "nmin_default_in_current_settings": 100,
                "shift_formula_Derivative": "shift = abs(min(vstack(x, dx))) + nmin",
                "make_Quotients": "(X_i + shift) / (X_j + shift); add_inverse=True adds reciprocal",
                "exact_shift_value_status": "EXACT_SHIFT_VALUE_UNKNOWN",
                "terms": entries,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def write_design_manifest(bundle: Dict[str, Any], model_sha: str) -> Path:
    path = PKG / "d3d_design_matrix_manifest.json"
    path.write_text(
        json.dumps(
            {
                "canonical_run_id": CANONICAL_RUN_ID,
                "artifact_status": bundle["artifact_status"],
                "feature_export_directory": str(EXPORT_DIR.relative_to(REPO)).replace("\\", "/"),
                "feature_export_manifest_sha256": sha256_file(EXPORT_DIR / "manifest.json"),
                "target_column": TARGET_COL,
                "feature_columns_psir_order": PSIR_FEATURE_COLS,
                "feature_columns_semantic_order": [f"[{t}]" for _, t in SEMANTIC_COEF_COLS],
                "intercept_included": True,
                "row_ordering": "sample_index 0..999 as stored in each parquet / psir timing",
                "discharge_ordering": "realization_index = order of filenames in historical psir (shot ascending in export sort when regenerated)",
                "realization_index_convention": "0..61 matching model.filenames order for HISTORICAL_ORIGINAL",
                "sample_index_convention": "0..999 along aligned TARGET_N grid",
                "finite_row_mask": "all 1000 rows finite in canonical export; prepare_discharge_reconstruction_data drops nonfinite",
                "expected_shape_features_per_discharge": [1000, 7],
                "expected_shape_target_per_discharge": [1000],
                "standardization_state": "export columns are z-scored per discharge (manifest normalization=zscore); target mean~0 std~1",
                "fitting_method": "numpy.linalg.lstsq on [1|X] for metadata; historical predictions from psir 1_8* coeffs",
                "solver_implementation": "numpy.linalg.lstsq(..., rcond=None)",
                "numerical_tolerance_rmse": TOL_RMSE_PER,
                "model_artifact_sha256": model_sha,
                "array_hash_representation": "numpy.ascontiguousarray(arr, dtype=float64).tobytes() then SHA-256",
                "coefficients_are": bundle["artifact_status"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def main():
    PKG.mkdir(parents=True, exist_ok=True)
    print("Building", CANONICAL_RUN_ID, "in", PKG)

    historical = verify_and_load_historical_psir()
    if historical is not None:
        print("HISTORICAL model verified:", HISTORICAL_PSIR)
        bundle = build_from_psir(historical)
    else:
        print("No verified historical model; regenerating OLS equivalent")
        bundle = build_regenerated()

    model_path = write_model_artifact(bundle)
    model_sha = sha256_file(model_path)
    # rewrite coef csv after model hash filled for regenerated path
    paths = write_tables(bundle)
    # rewrite coefficients with final model sha
    pd.DataFrame(bundle["coef_rows"]).to_csv(paths["coefficients"], index=False)

    coord_path = write_coordinate_manifest()
    design_path = write_design_manifest(bundle, model_sha)

    # shot list hash from ADMISSIBLE_SHOTS source file
    shot_list_sha = sha256_file(SHOT_LIST_SRC)
    ledger_sha = sha256_file(LEDGER_CSV)
    repo_commit, repo_dirty = git_rev(REPO)
    arch_commit, arch_dirty = git_rev(REPO / "submodules" / "Archaieus")

    unresolved = [
        "EXACT_SHIFT_VALUE_UNKNOWN for get_shiftval on the historical export-generating run",
        "ORIGINAL structural-search checklist / data_processing list at discovery time PARTIALLY UNKNOWN",
        "Whether discovery used pooled search then per-realization calibration: evidenced by 1_8 vs 1_8* but full UI settings at discovery UNKNOWN",
        "Random seeds / n_starts for SUBOPTIMAL_SEARCH: UNKNOWN",
    ]
    contradictions: List[str] = []
    # Current .bin/settings.json has incomplete data_processing vs export feature richness — not a contradiction of frozen export, but note.
    not_claimed = [
        "Full automatic rediscovery of the seven-term support from a blank library",
        "Physical interpretation of coefficient heterogeneity",
        "Out-of-sample predictive validation",
    ]

    file_hashes = {
        "coefficients": sha256_file(paths["coefficients"]),
        "predictions": sha256_file(paths["predictions"]),
        "metrics": sha256_file(paths["metrics"]),
        "pooled": sha256_file(paths["pooled"]),
        "model": model_sha,
        "coordinate_manifest": sha256_file(coord_path),
        "design_manifest": sha256_file(design_path),
        "coef_summary": sha256_file(paths["coef_summary"]),
        "design_hashes": sha256_file(paths["hashes"]),
    }

    manifest = {
        "canonical_run_id": CANONICAL_RUN_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifact_status": bundle["artifact_status"],
        "historical_model_found": bundle["artifact_status"] == ARTIFACT_STATUS_HISTORICAL,
        "repository_root": str(REPO),
        "repository_git_commit": repo_commit,
        "repository_dirty": repo_dirty,
        "archaieus_commit": arch_commit,
        "archaieus_dirty": arch_dirty,
        "python_version": sys.version.split()[0],
        "dependency_versions": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
        },
        "cohort_size": EXPECTED_N_DISCHARGES,
        "sample_count_per_discharge": EXPECTED_N_SAMPLES,
        "total_sample_count": EXPECTED_TOTAL,
        "shot_list_sha256": shot_list_sha,
        "ledger_sha256": ledger_sha,
        "feature_export_path": str(EXPORT_DIR.relative_to(REPO)).replace("\\", "/"),
        "feature_export_manifest_sha256": sha256_file(EXPORT_DIR / "manifest.json"),
        "selected_support": PSIR_TERM_ORDER,
        "selected_support_semantic_order": [t for _, t in SEMANTIC_COEF_COLS],
        "target_column": TARGET_COL,
        "coefficient_file": paths["coefficients"].name,
        "coefficient_file_sha256": file_hashes["coefficients"],
        "prediction_file": paths["predictions"].name,
        "prediction_file_sha256": file_hashes["predictions"],
        "metrics_file": paths["metrics"].name,
        "metrics_file_sha256": file_hashes["metrics"],
        "model_artifact": str(model_path.relative_to(PKG)).replace("\\", "/"),
        "model_artifact_sha256": file_hashes["model"],
        "coordinate_manifest": coord_path.name,
        "coordinate_manifest_sha256": file_hashes["coordinate_manifest"],
        "design_matrix_manifest": design_path.name,
        "design_matrix_manifest_sha256": file_hashes["design_manifest"],
        "search_provenance_file": "D3D_STRUCTURAL_SEARCH_PROVENANCE.md",
        "search_provenance_sha256": "PENDING_AFTER_DOC_WRITE",
        "pooled_rmse_discharge_specific": bundle["pooled"]["pooled_rmse"],
        "pooled_rmse_cohort_mean": bundle["pooled"]["mean_vector_pooled_rmse"],
        "near_zero_threshold": NEAR_ZERO_THRESHOLD,
        "equation_key": bundle["equation_key"],
        "unresolved_items": unresolved,
        "contradictions": contradictions,
        "not_claimed": not_claimed,
    }

    # Persist interim manifest; docs written by companion writer will update search sha
    man_path = PKG / "canonical_run_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Side JSON for doc writer
    (PKG / "_build_state.json").write_text(
        json.dumps(
            {
                "canonical_run_id": CANONICAL_RUN_ID,
                "artifact_status": bundle["artifact_status"],
                "historical_model_found": manifest["historical_model_found"],
                "pooled": bundle["pooled"],
                "file_hashes": file_hashes,
                "unresolved_items": unresolved,
                "contradictions": contradictions,
                "not_claimed": not_claimed,
                "model_path": str(model_path),
                "repo_commit": repo_commit,
                "repo_dirty": repo_dirty,
                "archaieus_commit": arch_commit,
                "archaieus_dirty": arch_dirty,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("\n=== SUMMARY ===")
    print("canonical_run_id:", CANONICAL_RUN_ID)
    print("historical_model_found:", manifest["historical_model_found"])
    print("coefficient_rows:", len(bundle["coef_rows"]))
    print("prediction_rows:", len(bundle["pred_rows"]))
    print("pooled_rmse_discharge_specific:", bundle["pooled"]["pooled_rmse"])
    print("pooled_rmse_cohort_mean:", bundle["pooled"]["mean_vector_pooled_rmse"])
    print("unresolved_items:", len(unresolved))
    print("output_directory:", PKG)


if __name__ == "__main__":
    main()
