#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main deterministic driver: DIII-D coefficient conditioning audit."""
from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from coefficient_conditioning_utils import (  # noqa: E402
    BASE as UTIL_BASE,
    REPO,
    bh_fdr,
    bootstrap_fit_coefficients,
    choose_block_length,
    effective_rank,
    fit_ols,
    integrated_autocorr_time,
    load_config,
    load_discharges,
    numerical_rank,
    orient_singular_vector,
    pearson_corr,
    pearson_corr_matrix,
    pooled_rmse,
    profile_tau2,
    setup_logger,
    spearman_corr,
    stable_rank,
    svd_features,
    truncated_svd_coefs,
    vif_values,
)

assert UTIL_BASE == BASE

# Cohort-mean vector used by the canonical package / Panel C path.
sys.path.insert(0, str(REPO))
from dash_app.utils.discharge_validation import D3D_RELATION  # noqa: E402


def main() -> int:
    cfg = load_config()
    out = BASE / "outputs"
    tables = BASE / "tables"
    logs = BASE / "logs"
    for d in (out, tables, logs):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(logs / "input_validation.log")
    logger.info("Starting audit %s", cfg["audit_run_id"])
    seed = int(cfg["audit_seed"])
    rng_global = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Phase 0 — validation
    # ------------------------------------------------------------------
    try:
        discharges = load_discharges(cfg, logger)
    except Exception:
        logger.exception("Failed to load discharges")
        (out / "CONTRADICTION_REPORT.txt").write_text(traceback.format_exc(), encoding="utf-8")
        return 2

    n = cfg["n_discharges"]
    p = cfg["n_features"]
    keys = cfg["source_matrix_order_keys"]
    eps = float(cfg["truncation_classification"]["epsilon"])

    # Canonical cohort-mean vector = hard-coded D3D_RELATION (not empirical mean of fits).
    mean_coef = np.array(
        [float(D3D_RELATION["intercept"])]
        + [float(D3D_RELATION["terms"][k]) for k in keys],
        dtype=np.float64,
    )
    C_mat = np.vstack([d.coef_source for d in discharges])

    max_abs_coef = 0.0
    max_rel_coef = 0.0
    max_pred = 0.0
    max_resid = 0.0
    recomputed_resid = []

    val_rows = []
    for d in discharges:
        coef_hat, yhat, rmse = fit_ols(d.y, d.X)
        abs_c = np.max(np.abs(coef_hat - d.coef_source))
        rel_c = abs_c / (np.linalg.norm(d.coef_source) + eps)
        pred_diff = np.max(np.abs(yhat - d.yhat_canonical))
        # residual from recomputed vs canonical residual
        resid_hat = d.y - yhat
        resid_diff = np.max(np.abs(resid_hat - d.residual_canonical))
        max_abs_coef = max(max_abs_coef, float(abs_c))
        max_rel_coef = max(max_rel_coef, float(rel_c))
        max_pred = max(max_pred, float(pred_diff))
        max_resid = max(max_resid, float(resid_diff))
        recomputed_resid.append(resid_hat)
        val_rows.append(
            {
                "realization_index": d.realization_index,
                "shot": d.shot,
                "max_abs_coef_diff": float(abs_c),
                "max_pred_diff": float(pred_diff),
                "rmse_recomputed": rmse,
            }
        )
        # mean-vector prediction residual
        yhat_mean = mean_coef[0] + d.X @ mean_coef[1:]
        d.mean_vector_residual = d.y - yhat_mean  # type: ignore[attr-defined]

    repro_rmse = pooled_rmse(recomputed_resid)
    mean_rmse = pooled_rmse([d.mean_vector_residual for d in discharges])  # type: ignore[attr-defined]
    tol = float(cfg["rmse_acceptance_tolerance"])
    ref_per = float(cfg["reference_pooled_rmse_discharge_specific"])
    ref_mean = float(cfg["reference_pooled_rmse_cohort_mean"])
    ok_per = abs(repro_rmse - ref_per) <= tol
    ok_mean = abs(mean_rmse - ref_mean) <= tol

    validation = {
        "canonical_run_id": cfg["canonical_run_id"],
        "audit_run_id": cfg["audit_run_id"],
        "n_discharges": n,
        "realization_index_ok": list(range(n)) == [d.realization_index for d in discharges],
        "n_samples_per_discharge": cfg["n_samples_per_discharge"],
        "n_features": p,
        "source_matrix_order": keys,
        "manuscript_display_order": [m["display"] for m in cfg["manuscript_display_order"]],
        "maximum_absolute_coefficient_difference": max_abs_coef,
        "maximum_relative_coefficient_difference": max_rel_coef,
        "maximum_prediction_difference": max_pred,
        "maximum_residual_difference": max_resid,
        "reproduced_pooled_rmse": repro_rmse,
        "reference_pooled_rmse": ref_per,
        "delta_pooled_rmse": abs(repro_rmse - ref_per),
        "reproduced_mean_vector_rmse": mean_rmse,
        "reference_mean_vector_rmse": ref_mean,
        "delta_mean_vector_rmse": abs(mean_rmse - ref_mean),
        "rmse_acceptance_tolerance": tol,
        "pass": bool(ok_per and ok_mean),
    }
    (out / "input_validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(val_rows).to_csv(tables / "input_validation.csv", index=False)
    logger.info("Validation: %s", validation)

    if not validation["pass"]:
        (out / "CONTRADICTION_REPORT.txt").write_text(
            "RMSE reproduction failed.\n" + json.dumps(validation, indent=2),
            encoding="utf-8",
        )
        logger.error("STOP: contradiction in RMSE reproduction")
        return 3

    # ------------------------------------------------------------------
    # Phase 1 — SVD geometry
    # ------------------------------------------------------------------
    logger.info("Phase 1 SVD")
    cond_rows = []
    sv_long = []
    rank_summary = {f"rank_{t:g}": 0 for t in cfg["rank_tolerances"]}
    rank_summary = {str(t): {"full7": 0, "lt7": 0} for t in cfg["rank_tolerances"]}

    near_null_rows = []
    null_vecs = []
    corr_long = []
    vif_rows = []

    for d in discharges:
        U, s, Vt = svd_features(d.X)
        s = np.asarray(s, dtype=np.float64)
        # pad if needed
        if s.size < 7:
            s = np.pad(s, (0, 7 - s.size))
        kappa = float(s[0] / s[6]) if s[6] > 0 else float("inf")
        R = pearson_corr_matrix(d.X)
        evals = np.linalg.eigvalsh(np.nan_to_num(R, nan=0.0))
        detR = float(np.linalg.det(np.nan_to_num(R, nan=0.0)))
        ranks = {t: numerical_rank(s, t) for t in cfg["rank_tolerances"]}
        for t, rnk in ranks.items():
            if rnk >= 7:
                rank_summary[str(t)]["full7"] += 1
            else:
                rank_summary[str(t)]["lt7"] += 1
        coef_hat, yhat, rmse = fit_ols(d.y, d.X)
        row = {
            "canonical_run_id": cfg["canonical_run_id"],
            "realization_index": d.realization_index,
            "shot": d.shot,
            "n_samples": cfg["n_samples_per_discharge"],
            "n_features": p,
            "feature_order": "source_matrix_order",
            "sigma_1": float(s[0]),
            "sigma_2": float(s[1]),
            "sigma_3": float(s[2]),
            "sigma_4": float(s[3]),
            "sigma_5": float(s[4]),
            "sigma_6": float(s[5]),
            "sigma_7": float(s[6]),
            "normalized_sigma_7": float(s[6] / s[0]) if s[0] > 0 else np.nan,
            "condition_number": kappa,
            "log10_condition_number": float(np.log10(kappa)) if np.isfinite(kappa) and kappa > 0 else np.inf,
            "rank_1e-12": ranks[1e-12],
            "rank_1e-10": ranks[1e-10],
            "rank_1e-8": ranks[1e-8],
            "rank_1e-6": ranks[1e-6],
            "effective_rank": effective_rank(s),
            "stable_rank": stable_rank(d.X, s),
            "correlation_matrix_min_eigenvalue": float(np.min(evals)),
            "correlation_matrix_determinant": detR,
            "rmse": rmse,
            "max_vif": float(np.nanmax(vif_values(d.X, cfg["vif_perfect_dependence_tolerance"]))),
        }
        cond_rows.append(row)
        for r in range(7):
            sv_long.append(
                {
                    "realization_index": d.realization_index,
                    "shot": d.shot,
                    "singular_index": r + 1,
                    "sigma": float(s[r]),
                    "normalized_sigma": float(s[r] / s[0]) if s[0] > 0 else np.nan,
                }
            )
        # near-null
        vmin = orient_singular_vector(Vt[-1])
        null_vecs.append(vmin)
        for j, key in enumerate(keys):
            near_null_rows.append(
                {
                    "canonical_run_id": cfg["canonical_run_id"],
                    "realization_index": d.realization_index,
                    "shot": d.shot,
                    "feature": key,
                    "feature_order": "source_matrix_order",
                    "loading": float(vmin[j]),
                    "absolute_loading": float(abs(vmin[j])),
                    "normalized_sigma_7": row["normalized_sigma_7"],
                    "condition_number": kappa,
                }
            )
        # correlations + VIF
        for a in range(7):
            for b in range(a + 1, 7):
                corr_long.append(
                    {
                        "realization_index": d.realization_index,
                        "shot": d.shot,
                        "feature_1": keys[a],
                        "feature_2": keys[b],
                        "correlation": float(R[a, b]),
                        "abs_correlation": float(abs(R[a, b])),
                    }
                )
        vifs = vif_values(d.X, cfg["vif_perfect_dependence_tolerance"])
        for j, key in enumerate(keys):
            vif_rows.append(
                {
                    "realization_index": d.realization_index,
                    "shot": d.shot,
                    "feature": key,
                    "vif": float(vifs[j]) if np.isfinite(vifs[j]) else np.inf,
                }
            )
        d.singular_values = s  # type: ignore
        d.Vt = Vt  # type: ignore
        d.condition_number = kappa  # type: ignore
        d.rmse = rmse  # type: ignore
        d.coef_recomputed = coef_hat  # type: ignore

    cond_df = pd.DataFrame(cond_rows)
    cond_df.to_csv(tables / "d3d_conditioning_per_discharge.csv", index=False)
    pd.DataFrame(sv_long).to_csv(tables / "d3d_singular_values_long.csv", index=False)
    rank_rows = [
        {
            "tolerance": float(t),
            "n_full_rank_7": rank_summary[str(t)]["full7"],
            "n_rank_lt_7": rank_summary[str(t)]["lt7"],
        }
        for t in cfg["rank_tolerances"]
    ]
    pd.DataFrame(rank_rows).to_csv(tables / "d3d_rank_tolerance_summary.csv", index=False)
    (out / "d3d_conditioning_summary.json").write_text(
        json.dumps(
            {
                "median_condition_number": float(np.median(cond_df["condition_number"].replace(np.inf, np.nan))),
                "max_condition_number": float(np.nanmax(cond_df["condition_number"].replace(np.inf, np.nan))),
                "median_normalized_sigma_7": float(cond_df["normalized_sigma_7"].median()),
                "rank_summary": rank_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Phase 2 summaries
    corr_df = pd.DataFrame(corr_long)
    corr_df.to_csv(tables / "d3d_feature_correlations_long.csv", index=False)
    vif_df = pd.DataFrame(vif_rows)
    vif_df.to_csv(tables / "d3d_vif_per_discharge.csv", index=False)
    corr_sum = []
    for (f1, f2), g in corr_df.groupby(["feature_1", "feature_2"]):
        a = g["correlation"].to_numpy()
        aa = np.abs(a)
        corr_sum.append(
            {
                "feature_1": f1,
                "feature_2": f2,
                "median_correlation": float(np.median(a)),
                "median_abs_correlation": float(np.median(aa)),
                "q05": float(np.percentile(a, 5)),
                "q25": float(np.percentile(a, 25)),
                "q75": float(np.percentile(a, 75)),
                "q95": float(np.percentile(a, 95)),
                "max_abs_correlation": float(np.max(aa)),
                "frac_abs_gt_0.8": float(np.mean(aa > 0.8)),
                "frac_abs_gt_0.9": float(np.mean(aa > 0.9)),
                "frac_abs_gt_0.95": float(np.mean(aa > 0.95)),
            }
        )
    pd.DataFrame(corr_sum).to_csv(tables / "d3d_correlation_summary.csv", index=False)
    pd.DataFrame(near_null_rows).to_csv(tables / "d3d_near_null_loadings.csv", index=False)

    # ------------------------------------------------------------------
    # Phase 4 — truncation sensitivity
    # ------------------------------------------------------------------
    logger.info("Phase 4 truncation")
    trunc_rows = []
    trunc_long = []
    tcfg = cfg["truncation_classification"]
    for d in discharges:
        c0 = d.coef_recomputed  # type: ignore
        yhat0 = c0[0] + d.X @ c0[1:]
        rmse0 = float(np.sqrt(np.mean((d.y - yhat0) ** 2)))
        for tau in cfg["truncation_tolerances"]:
            c_t, rank_t, yhat_t, rmse_t = truncated_svd_coefs(d.y, d.X, tau, eps)
            rel = float(np.linalg.norm(c_t - c0) / (np.linalg.norm(c0) + eps))
            max_term = float(np.max(np.abs(c_t - c0)))
            abs_rmse = abs(rmse_t - rmse0)
            if np.std(yhat0) > 0 and np.std(yhat_t) > 0:
                corr = float(np.corrcoef(yhat0, yhat_t)[0, 1])
            else:
                corr = np.nan
            rel_pred = float(np.linalg.norm(yhat_t - yhat0) / (np.linalg.norm(yhat0) + eps))
            if rank_t < 7 and s_is_deficient(d, tau):
                klass = "RANK_DEFICIENT"
            else:
                coef_stable = rel <= tcfg["stable_coefficient_relative_change"]
                recon_stable = (
                    abs_rmse <= tcfg["stable_reconstruction_abs_rmse_change"]
                    and (corr >= tcfg["stable_reconstruction_prediction_correlation"] if np.isfinite(corr) else False)
                )
                if coef_stable and recon_stable:
                    klass = "STABLE_COEFFICIENTS_STABLE_RECONSTRUCTION"
                elif (not coef_stable) and recon_stable:
                    klass = "UNSTABLE_COEFFICIENTS_STABLE_RECONSTRUCTION"
                else:
                    klass = "UNSTABLE_COEFFICIENTS_CHANGED_RECONSTRUCTION"
            trunc_rows.append(
                {
                    "realization_index": d.realization_index,
                    "shot": d.shot,
                    "tolerance": tau,
                    "retained_rank": rank_t,
                    "relative_coefficient_change": rel,
                    "max_abs_termwise_change": max_term,
                    "rmse_truncated": rmse_t,
                    "abs_rmse_change": abs_rmse,
                    "relative_prediction_change": rel_pred,
                    "prediction_correlation": corr,
                    "classification": klass,
                }
            )
            for j, key in enumerate(keys):
                trunc_long.append(
                    {
                        "realization_index": d.realization_index,
                        "shot": d.shot,
                        "tolerance": tau,
                        "feature": key,
                        "coefficient": float(c_t[j + 1]),
                        "canonical_coefficient": float(c0[j + 1]),
                        "delta": float(c_t[j + 1] - c0[j + 1]),
                    }
                )
    pd.DataFrame(trunc_rows).to_csv(tables / "d3d_coefficient_truncation_sensitivity.csv", index=False)
    pd.DataFrame(trunc_long).to_csv(tables / "d3d_truncated_coefficients_long.csv", index=False)

    # ------------------------------------------------------------------
    # Phase 5 — autocorrelation / block lengths
    # ------------------------------------------------------------------
    logger.info("Phase 5 autocorrelation")
    acf_rows = []
    block_rows = []
    for d in discharges:
        max_lag = int(cfg["autocorrelation"]["max_lag_fraction"] * len(d.y))
        lengths = []
        for j, key in enumerate(keys):
            iac = integrated_autocorr_time(d.X[:, j], max_lag)
            lengths.append(iac)
            acf_rows.append(
                {
                    "shot": d.shot,
                    "realization_index": d.realization_index,
                    "dt_seconds": d.dt_seconds,
                    "feature_or_residual": key,
                    "integrated_autocorrelation_samples": iac,
                    "correlation_time_seconds": iac * d.dt_seconds,
                }
            )
        iac_r = integrated_autocorr_time(d.y - (d.coef_recomputed[0] + d.X @ d.coef_recomputed[1:]), max_lag)  # type: ignore
        lengths.append(iac_r)
        acf_rows.append(
            {
                "shot": d.shot,
                "realization_index": d.realization_index,
                "dt_seconds": d.dt_seconds,
                "feature_or_residual": "residual",
                "integrated_autocorrelation_samples": iac_r,
                "correlation_time_seconds": iac_r * d.dt_seconds,
            }
        )
        iac_y = integrated_autocorr_time(d.y, max_lag)
        acf_rows.append(
            {
                "shot": d.shot,
                "realization_index": d.realization_index,
                "dt_seconds": d.dt_seconds,
                "feature_or_residual": "target",
                "integrated_autocorrelation_samples": iac_y,
                "correlation_time_seconds": iac_y * d.dt_seconds,
            }
        )
        L = float(np.max(lengths))
        short, primary, long = choose_block_length(
            L, cfg["bootstrap"]["min_block_samples"], cfg["bootstrap"]["max_block_samples"]
        )
        d.block_short = short  # type: ignore
        d.block_primary = primary  # type: ignore
        d.block_long = long  # type: ignore
        block_rows.append(
            {
                "shot": d.shot,
                "realization_index": d.realization_index,
                "dt_seconds": d.dt_seconds,
                "feature_or_residual": "MAX_OVER_FEATURES_AND_RESIDUAL",
                "integrated_autocorrelation_samples": L,
                "correlation_time_seconds": L * d.dt_seconds,
                "primary_block_samples": primary,
                "primary_block_seconds": primary * d.dt_seconds,
                "short_block_samples": short,
                "long_block_samples": long,
                "selection_status": "DATA_DRIVEN_IAC_MAX",
            }
        )
    pd.DataFrame(acf_rows).to_csv(tables / "d3d_autocorrelation_summary.csv", index=False)
    pd.DataFrame(block_rows).to_csv(tables / "d3d_bootstrap_block_lengths.csv", index=False)

    # ------------------------------------------------------------------
    # Phase 6 — bootstrap
    # ------------------------------------------------------------------
    logger.info("Phase 6 bootstrap (this may take several minutes)")
    B = int(cfg["bootstrap"]["primary_replicates"])
    Bs = int(cfg["bootstrap"]["sensitivity_replicates"])
    primary_records = []
    sens_records = []
    boot_summary = []
    cov_long = []
    # store primary coefs for later: list of (62, B, 8)
    primary_cube = np.empty((n, B, 8), dtype=np.float64)

    for d in discharges:
        # deterministic per-discharge seed
        rng = np.random.default_rng(seed + 10007 * (d.realization_index + 1))
        coefs = bootstrap_fit_coefficients(d.y, d.X, d.block_primary, B, rng)  # type: ignore
        primary_cube[d.realization_index] = coefs
        for b in range(B):
            rec = {
                "canonical_run_id": cfg["canonical_run_id"],
                "realization_index": d.realization_index,
                "shot": d.shot,
                "bootstrap_id": b,
                "block_length_samples": d.block_primary,  # type: ignore
                "block_length_seconds": d.block_primary * d.dt_seconds,  # type: ignore
                "intercept": float(coefs[b, 0]),
                "fit_status": "OK",
            }
            for j, key in enumerate(keys):
                rec[f"coef__{key}"] = float(coefs[b, j + 1])
            # rmse on bootstrap sample not stored heavy; skip exact or compute lightly
            primary_records.append(rec)
        # summaries
        c0 = d.coef_recomputed  # type: ignore
        for j, key in enumerate(keys):
            samples = coefs[:, j + 1]
            q = np.percentile(samples, [2.5, 5, 25, 50, 75, 95, 97.5])
            frac_pos = float(np.mean(samples > 0))
            frac_neg = float(np.mean(samples < 0))
            sd = float(np.std(samples, ddof=1))
            boot_summary.append(
                {
                    "realization_index": d.realization_index,
                    "shot": d.shot,
                    "feature": key,
                    "feature_order": "source_matrix_order",
                    "canonical_estimate": float(c0[j + 1]),
                    "bootstrap_mean": float(np.mean(samples)),
                    "bootstrap_median": float(q[3]),
                    "bootstrap_standard_deviation": sd,
                    "bootstrap_variance": float(sd ** 2),
                    "q025": float(q[0]),
                    "q05": float(q[1]),
                    "q25": float(q[2]),
                    "q75": float(q[4]),
                    "q95": float(q[5]),
                    "q975": float(q[6]),
                    "fraction_positive": frac_pos,
                    "fraction_negative": frac_neg,
                    "sign_stability": max(frac_pos, frac_neg),
                    "relative_bootstrap_sd": sd / (abs(float(c0[j + 1])) + eps),
                    "interval_contains_zero": bool(q[0] <= 0 <= q[6]),
                    "primary_block_length": d.block_primary,  # type: ignore
                }
            )
        # covariance of the 7 feature coeffs
        Cboot = np.cov(coefs[:, 1:].T, ddof=1)
        for a in range(7):
            for b in range(7):
                cov_long.append(
                    {
                        "shot": d.shot,
                        "realization_index": d.realization_index,
                        "feature_1": keys[a],
                        "feature_2": keys[b],
                        "covariance": float(Cboot[a, b]),
                        "correlation": float(
                            Cboot[a, b] / (np.sqrt(Cboot[a, a] * Cboot[b, b]) + eps)
                        ),
                    }
                )
        # sensitivity short/long
        for label, blk in (("short", d.block_short), ("long", d.block_long)):  # type: ignore
            rng2 = np.random.default_rng(seed + 90011 * (d.realization_index + 1) + (1 if label == "short" else 2))
            coefs2 = bootstrap_fit_coefficients(d.y, d.X, int(blk), Bs, rng2)
            for b in range(Bs):
                rec = {
                    "canonical_run_id": cfg["canonical_run_id"],
                    "realization_index": d.realization_index,
                    "shot": d.shot,
                    "bootstrap_id": b,
                    "block_setting": label,
                    "block_length_samples": int(blk),
                    "block_length_seconds": float(blk) * d.dt_seconds,
                    "intercept": float(coefs2[b, 0]),
                }
                for j, key in enumerate(keys):
                    rec[f"coef__{key}"] = float(coefs2[b, j + 1])
                sens_records.append(rec)

    logger.info("Writing bootstrap parquet tables")
    pd.DataFrame(primary_records).to_parquet(out / "d3d_bootstrap_coefficients_primary.parquet", index=False)
    pd.DataFrame(sens_records).to_parquet(out / "d3d_bootstrap_coefficients_sensitivity.parquet", index=False)
    boot_sum_df = pd.DataFrame(boot_summary)
    boot_sum_df.to_csv(tables / "d3d_bootstrap_coefficient_summary.csv", index=False)
    pd.DataFrame(cov_long).to_csv(tables / "d3d_bootstrap_covariance_long.csv", index=False)

    # block sensitivity: compare primary vs short/long SD
    sens_cmp = []
    sens_df = pd.DataFrame(sens_records)
    for d in discharges:
        for j, key in enumerate(keys):
            col = f"coef__{key}"
            sd_p = float(np.std(primary_cube[d.realization_index, :, j + 1], ddof=1))
            for label in ("short", "long"):
                sub = sens_df[
                    (sens_df["realization_index"] == d.realization_index)
                    & (sens_df["block_setting"] == label)
                ]
                sd_s = float(sub[col].std(ddof=1))
                sens_cmp.append(
                    {
                        "realization_index": d.realization_index,
                        "shot": d.shot,
                        "feature": key,
                        "block_setting": label,
                        "sd_primary": sd_p,
                        "sd_sensitivity": sd_s,
                        "sd_ratio_sens_over_primary": sd_s / (sd_p + eps),
                    }
                )
    pd.DataFrame(sens_cmp).to_csv(tables / "d3d_bootstrap_block_sensitivity.csv", index=False)

    # ------------------------------------------------------------------
    # Phase 7 — between vs within
    # ------------------------------------------------------------------
    logger.info("Phase 7 heterogeneity")
    het_rows = []
    re_diag = {"coefficients": {}}
    # within variance per discharge from bootstrap
    within_var = np.empty((n, 7), dtype=np.float64)
    canon_coef = np.empty((n, 7), dtype=np.float64)
    for d in discharges:
        canon_coef[d.realization_index] = d.coef_recomputed[1:]  # type: ignore
        within_var[d.realization_index] = np.var(primary_cube[d.realization_index, :, 1:], axis=0, ddof=1)

    for j, key in enumerate(keys):
        c = canon_coef[:, j]
        sB2 = float(np.var(c, ddof=1))
        mean_sW2 = float(np.mean(within_var[:, j]))
        H = sB2 / mean_sW2 if mean_sW2 > 0 else np.inf
        resolved = max(0.0, sB2 - mean_sW2) / sB2 if sB2 > 0 else 0.0
        mu, tau2, lo, hi = profile_tau2(c, within_var[:, j])
        # discharge-level bootstrap of tau2
        rng = np.random.default_rng(seed + 333 + j)
        n_re = int(cfg["random_effects"]["tau2_bootstrap_replicates"])
        tau2_boots = []
        for _ in range(n_re):
            idx = rng.integers(0, n, size=n)
            _, t2, _, _ = profile_tau2(c[idx], within_var[idx, j])
            tau2_boots.append(t2)
        # status
        rules = cfg["random_effects"]
        if resolved >= rules["resolved_fraction_threshold"] and H >= rules["heterogeneity_ratio_resolved"]:
            status = "BETWEEN_DISCHARGE_VARIATION_RESOLVED"
        elif H >= rules["heterogeneity_ratio_partial"] or resolved >= 0.1:
            status = "BETWEEN_DISCHARGE_VARIATION_PARTIALLY_RESOLVED"
        elif H < 1.0 or resolved < 0.05:
            status = "WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES"
        else:
            status = "INDETERMINATE"
        het_rows.append(
            {
                "feature": key,
                "feature_order": "source_matrix_order",
                "mu_r": mu,
                "observed_between_variance": sB2,
                "mean_within_variance": mean_sW2,
                "heterogeneity_ratio": H if np.isfinite(H) else np.inf,
                "resolved_fraction": resolved,
                "tau2_REML": tau2,
                "tau_REML": float(np.sqrt(tau2)),
                "tau2_interval_low": lo,
                "tau2_interval_high": hi,
                "tau2_bootstrap_q025": float(np.percentile(tau2_boots, 2.5)),
                "tau2_bootstrap_q975": float(np.percentile(tau2_boots, 97.5)),
                "fraction_total_variance_between": float(tau2 / (tau2 + mean_sW2)) if (tau2 + mean_sW2) > 0 else np.nan,
                "number_of_discharges": n,
                "status": status,
            }
        )
        re_diag["coefficients"][key] = {"mu": mu, "tau2": tau2, "status": status}
    het_df = pd.DataFrame(het_rows)
    het_df.to_csv(tables / "d3d_coefficient_heterogeneity.csv", index=False)
    (out / "d3d_random_effects_diagnostics.json").write_text(json.dumps(re_diag, indent=2) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------
    # Phase 8 — multivariate
    # ------------------------------------------------------------------
    logger.info("Phase 8 multivariate")
    Sigma_W = np.mean(
        [np.cov(primary_cube[i, :, 1:].T, ddof=1) for i in range(n)], axis=0
    )
    Sigma_B = np.cov(canon_coef.T, ddof=1)
    Sigma_R = Sigma_B - Sigma_W
    Sigma_R_sym = 0.5 * (Sigma_R + Sigma_R.T)
    evals_B, evecs_B = np.linalg.eigh(Sigma_B)
    evals_W, evecs_W = np.linalg.eigh(Sigma_W)
    evals_R, evecs_R = np.linalg.eigh(Sigma_R_sym)
    # PSD projection
    evals_R_clip = np.clip(evals_R, 0, None)
    Sigma_R_psd = (evecs_R * evals_R_clip) @ evecs_R.T
    # resolved directions: positive eigenvalues of difference
    order = np.argsort(evals_R)[::-1]
    mv_rows = []
    n_resolved_dirs = 0
    for k in order:
        lam = float(evals_R[k])
        if lam > 1e-12 * max(1.0, float(np.max(np.abs(evals_B)))):
            n_resolved_dirs += 1
        v = orient_singular_vector(evecs_R[:, k])
        for j, key in enumerate(keys):
            # manuscript display name
            disp = next(m["display"] for m in cfg["manuscript_display_order"] if m["key"] == key)
            mv_rows.append(
                {
                    "eigen_index": int(k),
                    "eigenvalue_raw": lam,
                    "eigenvalue_psd": float(evals_R_clip[k]),
                    "feature": key,
                    "display_name": disp,
                    "loading_source_order": float(v[j]),
                    "resolved_flag": lam > 1e-12 * max(1.0, float(np.max(np.abs(evals_B)))),
                }
            )
    pd.DataFrame(mv_rows).to_csv(tables / "d3d_multivariate_variance_eigenvectors.csv", index=False)
    np.savez(
        out / "d3d_multivariate_variance_components.npz",
        Sigma_B=Sigma_B,
        Sigma_W=Sigma_W,
        Sigma_R=Sigma_R_sym,
        Sigma_R_psd=Sigma_R_psd,
        evals_B=evals_B,
        evals_W=evals_W,
        evals_R=evals_R,
        keys=np.array(keys),
    )
    frac_surviving = float(np.sum(evals_R_clip) / (np.sum(np.clip(evals_B, 0, None)) + eps))
    mv_summary = {
        "n_resolved_directions": n_resolved_dirs,
        "evals_between": evals_B.tolist(),
        "evals_within": evals_W.tolist(),
        "evals_difference": evals_R.tolist(),
        "fraction_observed_variance_surviving_subtraction": frac_surviving,
    }
    (out / "d3d_multivariate_identifiability_summary.json").write_text(
        json.dumps(mv_summary, indent=2) + "\n", encoding="utf-8"
    )

    # ------------------------------------------------------------------
    # Phase 9 — associations + FDR
    # ------------------------------------------------------------------
    logger.info("Phase 9 associations")
    assoc_rows = []
    # discharge-level aggregates
    logkappa = np.log10(np.clip(cond_df["condition_number"].to_numpy(dtype=np.float64), 1e-300, None))
    nsig7 = cond_df["normalized_sigma_7"].to_numpy(dtype=np.float64)
    effr = cond_df["effective_rank"].to_numpy(dtype=np.float64)
    maxvif = cond_df["max_vif"].replace(np.inf, 1e12).to_numpy(dtype=np.float64)
    rmse_v = cond_df["rmse"].to_numpy(dtype=np.float64)
    coef_norm = np.linalg.norm(canon_coef, axis=1)
    # mean bootstrap sd across coeffs
    mean_boot_sd = np.array(
        [
            float(np.mean([boot_sum_df[(boot_sum_df.realization_index == i) & (boot_sum_df.feature == k)]["bootstrap_standard_deviation"].iloc[0] for k in keys]))
            for i in range(n)
        ]
    )
    mean_sign_stab = np.array(
        [
            float(np.mean([boot_sum_df[(boot_sum_df.realization_index == i) & (boot_sum_df.feature == k)]["sign_stability"].iloc[0] for k in keys]))
            for i in range(n)
        ]
    )
    # truncation sensitivity at 1e-6
    trunc_df = pd.DataFrame(trunc_rows)
    trunc_sens = []
    for i in range(n):
        sub = trunc_df[(trunc_df.realization_index == i) & (np.isclose(trunc_df.tolerance, 1e-6))]
        trunc_sens.append(float(sub["relative_coefficient_change"].iloc[0]) if len(sub) else np.nan)
    trunc_sens = np.asarray(trunc_sens, dtype=np.float64)

    pairs = [
        ("log10_condition_number", logkappa, "normalized_sigma_7", nsig7),
        ("log10_condition_number", logkappa, "rmse", rmse_v),
        ("log10_condition_number", logkappa, "coef_vector_norm", coef_norm),
        ("log10_condition_number", logkappa, "mean_bootstrap_sd", mean_boot_sd),
        ("log10_condition_number", logkappa, "mean_sign_stability", mean_sign_stab),
        ("log10_condition_number", logkappa, "truncation_rel_change_1e-6", trunc_sens),
        ("normalized_sigma_7", nsig7, "mean_bootstrap_sd", mean_boot_sd),
        ("effective_rank", effr, "rmse", rmse_v),
        ("max_vif", maxvif, "mean_bootstrap_sd", mean_boot_sd),
    ]
    pvals = []
    for xname, x, yname, y in pairs:
        rs, ps = spearman_corr(x, y)
        rp, pp = pearson_corr(x, y)
        assoc_rows.append(
            {
                "x": xname,
                "y": yname,
                "spearman_r": rs,
                "spearman_p": ps,
                "pearson_r": rp,
                "pearson_p": pp,
                "level": "discharge_aggregate",
                "feature": "",
            }
        )
        pvals.append(ps)

    # per-coefficient vs conditioning
    for j, key in enumerate(keys):
        abs_c = np.abs(canon_coef[:, j])
        sd = np.array(
            [
                float(
                    boot_sum_df[
                        (boot_sum_df.realization_index == i) & (boot_sum_df.feature == key)
                    ]["bootstrap_standard_deviation"].iloc[0]
                )
                for i in range(n)
            ]
        )
        width = np.array(
            [
                float(
                    boot_sum_df[
                        (boot_sum_df.realization_index == i) & (boot_sum_df.feature == key)
                    ]["q975"].iloc[0]
                    - boot_sum_df[
                        (boot_sum_df.realization_index == i) & (boot_sum_df.feature == key)
                    ]["q025"].iloc[0]
                )
                for i in range(n)
            ]
        )
        sign_instab = 1.0 - np.array(
            [
                float(
                    boot_sum_df[
                        (boot_sum_df.realization_index == i) & (boot_sum_df.feature == key)
                    ]["sign_stability"].iloc[0]
                )
                for i in range(n)
            ]
        )
        for yname, y in (
            ("abs_coefficient", abs_c),
            ("bootstrap_sd", sd),
            ("interval_width", width),
            ("sign_instability", sign_instab),
        ):
            for xname, x in (("log10_condition_number", logkappa), ("normalized_sigma_7", nsig7)):
                rs, ps = spearman_corr(x, y)
                rp, pp = pearson_corr(x, y)
                assoc_rows.append(
                    {
                        "x": xname,
                        "y": yname,
                        "spearman_r": rs,
                        "spearman_p": ps,
                        "pearson_r": rp,
                        "pearson_p": pp,
                        "level": "per_coefficient",
                        "feature": key,
                    }
                )
                pvals.append(ps)

    assoc_df = pd.DataFrame(assoc_rows)
    reject, adj = bh_fdr(assoc_df["spearman_p"].to_numpy(), cfg["fdr_alpha"])
    assoc_df["bh_reject"] = reject
    assoc_df["bh_adjusted_p"] = adj
    assoc_df.to_csv(tables / "d3d_conditioning_associations.csv", index=False)
    assoc_df[assoc_df["bh_reject"]].to_csv(tables / "d3d_conditioning_associations_fdr.csv", index=False)

    # ------------------------------------------------------------------
    # Overall verdict
    # ------------------------------------------------------------------
    n_resolved = int(np.sum(het_df["status"] == "BETWEEN_DISCHARGE_VARIATION_RESOLVED"))
    n_partial = int(np.sum(het_df["status"] == "BETWEEN_DISCHARGE_VARIATION_PARTIALLY_RESOLVED"))
    n_within = int(np.sum(het_df["status"] == "WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES"))
    med_kappa = float(np.median(cond_df["condition_number"]))
    # truncation: fraction unstable coeffs stable recon at 1e-6
    t1 = trunc_df[np.isclose(trunc_df.tolerance, 1e-6)]
    frac_unstable_stable = float(
        np.mean(t1["classification"] == "UNSTABLE_COEFFICIENTS_STABLE_RECONSTRUCTION")
    )
    if n_resolved >= 4 and med_kappa < 1e3:
        verdict = "D3D-COEFFICIENT-FAMILY-RESOLVED"
    elif n_within >= 4 and frac_unstable_stable >= 0.3:
        verdict = "D3D-SHARED-SUPPORT-WITH-WEAKLY-IDENTIFIED-COEFFICIENTS"
    elif n_within >= 3 and med_kappa >= 1e3:
        verdict = "D3D-COEFFICIENT-VARIATION-CONDITIONING-DOMINATED"
    elif n_resolved >= 1 and n_within >= 1:
        verdict = "D3D-MIXED-COEFFICIENT-IDENTIFIABILITY"
    else:
        verdict = "D3D-COEFFICIENT-IDENTIFIABILITY-INDETERMINATE"

    summary = {
        "canonical_run_id": cfg["canonical_run_id"],
        "audit_run_id": cfg["audit_run_id"],
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "audit_seed": seed,
        "n_discharges": n,
        "n_samples_per_discharge": cfg["n_samples_per_discharge"],
        "n_features": p,
        "source_matrix_order": keys,
        "manuscript_display_order": [m["display"] for m in cfg["manuscript_display_order"]],
        "reference_pooled_rmse": ref_per,
        "reproduced_pooled_rmse": repro_rmse,
        "maximum_coefficient_reproduction_error": max_abs_coef,
        "rank_counts_by_tolerance": rank_rows,
        "condition_number_summary": {
            "median": med_kappa,
            "max": float(np.max(cond_df["condition_number"])),
            "q25": float(np.percentile(cond_df["condition_number"], 25)),
            "q75": float(np.percentile(cond_df["condition_number"], 75)),
        },
        "normalized_sigma7_summary": {
            "median": float(cond_df["normalized_sigma_7"].median()),
            "min": float(cond_df["normalized_sigma_7"].min()),
        },
        "maximum_vif_summary": {
            "median": float(np.median(maxvif)),
            "max": float(np.max(maxvif)),
        },
        "truncation_sensitivity_summary": {
            "frac_unstable_coefficients_stable_reconstruction_at_1e-6": frac_unstable_stable,
            "classification_counts_at_1e-6": t1["classification"].value_counts().to_dict(),
        },
        "bootstrap_replicates_primary": B,
        "bootstrap_replicates_sensitivity": Bs,
        "block_length_summary": {
            "median_primary": float(np.median([d.block_primary for d in discharges])),  # type: ignore
            "min_primary": int(np.min([d.block_primary for d in discharges])),  # type: ignore
            "max_primary": int(np.max([d.block_primary for d in discharges])),  # type: ignore
        },
        "coefficient_heterogeneity_results": het_rows,
        "multivariate_identifiability_results": mv_summary,
        "n_coefficients_between_resolved": n_resolved,
        "n_coefficients_partial": n_partial,
        "n_coefficients_within_dominates": n_within,
        "n_multivariate_resolved_directions": n_resolved_dirs,
        "overall_verdict": verdict,
        "limitations": [
            "Conditional on selected seven-term support; support uniqueness not tested.",
            "Block-bootstrap approximates temporal dependence; block length is estimated.",
            "Exact historical shift values remain UNKNOWN (inherited from canonical package).",
            "Random-effects model assumes Gaussian sampling distributions of coefficients.",
        ],
        "unresolved_items": [
            "EXACT_SHIFT_VALUE_UNKNOWN inherited from canonical package",
            "Original structural-search hyperparameters UNKNOWN",
        ],
        "dependency_versions": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "python": sys.version.split()[0],
        },
    }
    (out / "coefficient_conditioning_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    # side state for report/figures
    (out / "_audit_state.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("\n=== AUDIT DRIVER COMPLETE ===")
    print("audit_run_id:", cfg["audit_run_id"])
    print("verdict:", verdict)
    print("reproduced_pooled_rmse:", repro_rmse)
    print("median_condition_number:", med_kappa)
    print("n_resolved_coeffs:", n_resolved, "n_within_dominates:", n_within)
    print("n_multivariate_resolved_directions:", n_resolved_dirs)
    return 0


def s_is_deficient(d, tau) -> bool:
    s = d.singular_values  # type: ignore
    return numerical_rank(s, tau) < 7


if __name__ == "__main__":
    raise SystemExit(main())
