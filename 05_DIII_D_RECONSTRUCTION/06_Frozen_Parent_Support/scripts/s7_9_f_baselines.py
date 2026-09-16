"""S7.9 step F - baseline specification audit, completion and freeze.

Runs ONLY after DEVELOPMENT_REPRESENTATION_LOCK exists. Aborts otherwise.

Parent definitions win. This stage completes ONLY what the parents left
numerically uninstantiated: the B2/H0 ridge penalty-selection rule. Nothing here
may change the selected representation, and no baseline result is compared to
the relational representation.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S72 = S7 / "02_reconstruction_contract"
S73 = S7 / "03_target_feasibility_and_boundary" / "reconciliation_source_resolution"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S77 = S7 / "07_search_policy_and_frontier"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s7_9_coords import Engine, BLOCKS, CANON, TARGET, DATA  # noqa: E402
import diiid_sir_data_provider as PROV  # noqa: E402

ALPHA_GRID = [0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1,
              1, 10, 100, 1000, 10000, 100000, 1000000]
B3_RANDOM_STATE = 2026090502


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ridge_cell(Zc, Zp, yc, yp, alpha):
    """Ridge with fitted, unpenalized intercept. alpha=0 -> lstsq OLS."""
    ybar = float(yc.mean())
    ycc = yc - ybar
    if alpha == 0:
        X = np.column_stack([np.ones(Zc.shape[0]), Zc])
        beta, *_ = np.linalg.lstsq(X, yc, rcond=None)
        pred = np.column_stack([np.ones(Zp.shape[0]), Zp]) @ beta
    else:
        G = Zc.T @ Zc + alpha * np.eye(Zc.shape[1])
        b = np.linalg.solve(G, Zc.T @ ycc)
        pred = ybar + Zp @ b
    scale = float(np.std(yc, ddof=0))
    return float(np.sqrt(np.mean((yp - pred) ** 2)) / scale)


def main() -> int:
    lock_p = OUT / "DEVELOPMENT_REPRESENTATION_LOCK.json"
    if not lock_p.exists():
        raise SystemExit("STOP: DEVELOPMENT_REPRESENTATION_LOCK missing - "
                         "no baseline tuning may occur")
    lock = json.loads(lock_p.read_text())
    print("lock present: %s (%s)" % (lock["lock_sha256"][:16], lock["locked_utc"]))

    # ---------------- parent specification audit -------------------------
    presearch = json.loads((S77 / "PRE_SEARCH_CONTRACT_COMPLETION.json").read_text())
    h0_parent = json.loads((S75H / "hardened_raw_ablation.json").read_text())
    boundary = pd.read_csv(S73 / "corrected_selected_target_boundary.csv")
    P78 = sorted(boundary[boundary.include_primary == True].signal.tolist())
    P70 = sorted(h0_parent["primitive_levels"])
    assert len(P78) == 78 and len(P70) == 70 and set(P70) <= set(P78)

    audit = {
        "audit_id": "PARENT_BASELINE_SPECIFICATION_AUDIT_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "principle": "PARENT DEFINITIONS WIN; S7.9 completes only what is numerically uninstantiated",
        "families": {
            "B0": {"parent": "S7.2 BASELINE_PROTOCOL.md", "definition_complete": True,
                   "hyperparameters": 0, "completion_needed": False},
            "B1": {"parent": "S7.2 BASELINE_PROTOCOL.md", "definition_complete": True,
                   "hyperparameters": 0, "completion_needed": False},
            "B1A_AR1": {"parent": "S7.7 PRE_SEARCH_CONTRACT_COMPLETION_V1",
                        "definition_complete": True,
                        "hyperparameter_selection": presearch["B1A_AR1"]["hyperparameter_selection"],
                        "completion_needed": False,
                        "carried_verbatim": True},
            "B2": {"parent": "S7.2 BASELINE_PROTOCOL.md + RELATION_AND_TRANSFER_POLICY.md",
                   "definition_complete": False,
                   "missing": "no numeric penalty grid or selection algorithm exists in any parent",
                   "completion_needed": True},
            "B3": {"parent": "S7.2 BASELINE_PROTOCOL.md",
                   "definition_complete": True,
                   "rule": "library defaults except what determinism requires",
                   "completion_needed": False},
            "H0_RAW_HARDENED": {"parent": "S7.5H hardened_raw_ablation.json",
                                "definition_complete": True,
                                "penalty_rule": "same as B2, independently selected on development",
                                "completion_needed": "inherits the B2 completion by reference"},
        },
        "parent_search_performed": [
            "grep for alpha / penalty grid / logspace across S7.2 and S7.3 artifacts",
            "PRE_SEARCH_CONTRACT_COMPLETION.json",
            "hardened_raw_ablation.json",
            "BASELINE_PROTOCOL.md, RELATION_AND_TRANSFER_POLICY.md, STATISTICAL_INFERENCE_PLAN.md",
        ],
        "stronger_parent_rule_found_for_ridge_alpha": False,
        "section_19_default_completion_applies": True,
        "predictor_bases": {
            "B2_and_B3": {"n": 78, "basis": "full target-admissible primitive predictors (I_rec)",
                          "signals": P78,
                          "restricted_to_70_hardened": False,
                          "note": "explicitly NOT shrunk to the hardened basis"},
            "H0": {"n": 70, "basis": "hardened primitive levels P_hard", "signals": P70,
                   "extra_in_B2_not_in_H0": sorted(set(P78) - set(P70))},
        },
    }
    (OUT / "manifests" / "PARENT_BASELINE_SPECIFICATION_AUDIT.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8")

    # ---------------- prospective completion, hashed BEFORE tuning -------
    prevalue = {
        "record_id": "BASELINE_SPECIFICATION_COMPLETION_PREVALUE_V1",
        "status": "PROSPECTIVE_SPECIFICATION_COMPLETION",
        "not_an_outcome_response": True,
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_before_any_alpha_was_evaluated": True,
        "is_baseline_family_selection": False,
        "is_implementation_completion_of_a_frozen_family": True,
        "rule_id": "RIDGE_ALPHA_SELECTION_V1",
        "applies_to": ["B2", "H0_RAW_HARDENED"],
        "independent_selection_per_baseline": True,
        "preprocessing": "predictors standardized from the CALIBRATION interval only; sd<=0 divisor 1.0; no epsilon",
        "intercept": {"fitted": True, "penalized": False},
        "alpha_grid": ALPHA_GRID,
        "alpha_zero_interpretation": "unregularized affine linear regression via the numerically stable lstsq solver",
        "evaluation": [
            "frozen 20 development discharges",
            "same A/B/C rolling validation geometry",
            "fit separately per discharge/block",
            "frozen NRMSE = RMSE(protected)/std(y_calibration, ddof=0)",
            "aggregate within discharge over blocks, then over discharges",
        ],
        "selection": "minimum mean development NRMSE",
        "tie_break": "SMALLER alpha",
        "one_se_enlargement": False,
        "preference_for_stronger_regularization": False,
        "external_information_used": False,
        "development_only": True,
        "lock_sha256_at_time_of_freezing": lock["lock_sha256"],
    }
    (OUT / "BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json").write_text(
        json.dumps(prevalue, indent=2), encoding="utf-8")
    prevalue_sha = sha256(OUT / "BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json")
    print("prevalue frozen: %s (grid of %d alphas)" % (prevalue_sha[:16], len(ALPHA_GRID)))

    # ---------------- load the 78 raw levels on development --------------
    eng = Engine()
    import pandas as _pd
    TR = _pd.read_csv(S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
                      / "trajectory_index.csv", dtype={"discharge": str})
    TRd = TR[TR.cohort == "development"].set_index("discharge")
    RAW = {}
    for s in eng.dev:
        t0 = float(TRd.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TRd.loc[s, "delta_t_ms"])
        n = int(TRd.loc[s, "N_s"])
        grid = t0 + dtm * np.arange(n, dtype=np.float64)
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            M = np.empty((78, n))
            for k, sig in enumerate(P78):
                tt, vv = PROV._load_signal(a, sig)
                M[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                    str(PROV.SIGNAL_UNIT[sig]), 1.0)
        RAW[s] = M
    idx70 = np.array([P78.index(p) for p in P70])

    def tune(rows, label):
        table = []
        for alpha in ALPHA_GRID:
            per_shot = []
            for s in eng.dev:
                vals = []
                for bn, _, _ in BLOCKS:
                    cal, pro = eng.SLC[(s, bn)]
                    X = RAW[s][rows]
                    xc, xp = X[:, cal], X[:, pro]
                    mu = xc.mean(axis=1, keepdims=True)
                    sd = xc.std(axis=1, ddof=0, keepdims=True)
                    div = np.where(sd <= 0, 1.0, sd)
                    Zc, Zp = ((xc - mu) / div).T, ((xp - mu) / div).T
                    vals.append(ridge_cell(Zc, Zp, eng.YT[s][cal], eng.YT[s][pro], alpha))
                per_shot.append(float(np.mean(vals)))
            table.append({"alpha": alpha, "mean_development_NRMSE": float(np.mean(per_shot)),
                          "n_finite_cells": 60})
        df = pd.DataFrame(table)
        m = df.mean_development_NRMSE.min()
        sel = float(df[df.mean_development_NRMSE == m].alpha.min())   # tie -> smaller
        print("  %s selected alpha = %g  (criterion %.6f)" % (label, sel, m))
        return df, sel

    print("tuning B2 (78 predictors) and H0 (70 predictors)...")
    b2_tab, b2_alpha = tune(np.arange(78), "B2")
    h0_tab, h0_alpha = tune(idx70, "H0")
    b2_tab.assign(baseline="B2").to_csv(OUT / "baseline_b2_alpha_tuning.csv", index=False)
    h0_tab.assign(baseline="H0_RAW_HARDENED").to_csv(
        OUT / "baseline_h0_alpha_tuning.csv", index=False)

    # ---------------- configurations -------------------------------------
    common = {
        "target": "density",
        "geometry": "identical calibration intervals and protected samples as every comparator",
        "preprocessing": "calibration-fitted only; sd<=0 divisor 1.0; no epsilon",
        "metric": "NRMSE = RMSE(protected)/std(y_calibration, ddof=0)",
        "development_discharges": 20,
        "external_evaluation": "S7.10",
        "run_in_S7_9": False,
    }

    cfgs = {
        "BASELINE_B0_CONFIG.json": {
            "baseline_id": "B0_CALIBRATION_MEAN_V1", "role": "MANDATORY_V3",
            "definition": "predict mean(y_calibration) throughout the protected block",
            "hyperparameters": {}, "n_hyperparameters": 0,
            "future_target_use": False, "tuned_on_development": False, **common},
        "BASELINE_B1_CONFIG.json": {
            "baseline_id": "B1_PERSISTENCE_V1", "role": "MANDATORY_V3",
            "definition": ("predict the final target value immediately before the "
                           "protected block, held constant over the protected block"),
            "operational": "the last calibration sample of each block",
            "hyperparameters": {}, "n_hyperparameters": 0,
            "tuned_on_development": False, **common},
        "BASELINE_B1A_CONFIG.json": {
            "baseline_id": "B1A_AR1", "role": "DIAGNOSTIC",
            "carried_verbatim_from": "S7.7 PRE_SEARCH_CONTRACT_COMPLETION_V1",
            "definition": presearch["B1A_AR1"]["calibration_fit"],
            "protected_block_procedure": presearch["B1A_AR1"]["protected_block_procedure"],
            "no_teacher_forcing_on_protected_values": True,
            "lag_order": 1, "additional_lags": False,
            "hyperparameters": {}, "n_hyperparameters": 0,
            "added_to_mandatory_V3_thresholds": False,
            "tuned_on_development": False, **common},
        "BASELINE_B2_CONFIG.json": {
            "baseline_id": "B2_RAW_RIDGE", "role": "MANDATORY_V4",
            "estimator": "ridge with fitted unpenalized intercept",
            "predictors": {"n": 78, "basis": "full target-admissible primitive levels (I_rec)",
                           "signals": P78, "constructed_coordinates": False,
                           "restricted_to_hardened_70": False},
            "penalty_rule": "RIDGE_ALPHA_SELECTION_V1",
            "alpha_grid": ALPHA_GRID,
            "selected_alpha": b2_alpha,
            "selection_criterion": "minimum mean development NRMSE; tie -> smaller alpha",
            "tuned_on_development": True,
            "tuned_after_representation_lock": True,
            "compared_to_relational_representation": False, **common},
        "BASELINE_B3_CONFIG.json": {
            "baseline_id": "B3_RAW_HIST_GRADIENT_BOOSTING", "role": "MANDATORY_V4",
            "estimator": "sklearn.ensemble.HistGradientBoostingRegressor",
            "predictors": {"n": 78, "basis": "full target-admissible primitive levels (I_rec)",
                           "signals": P78, "constructed_coordinates": False},
            "tuned_on_development": False,
            "departure_from_defaults": ["random_state fixed for determinism"],
            "compatibility_departure_required": False,
            "random_state": B3_RANDOM_STATE, **common},
        "BASELINE_H0_CONFIG.json": {
            "baseline_id": "H0_RAW_HARDENED", "role": "DIAGNOSTIC_ABLATION",
            "is_mandatory_gate_baseline": False,
            "carried_from": "S7.5H hardened_raw_ablation.json",
            "estimator": "ridge with fitted unpenalized intercept",
            "predictors": {"n": 70, "basis": "hardened primitive levels P_hard",
                           "signals": P70, "constructed_coordinates": False},
            "penalty_rule": "RIDGE_ALPHA_SELECTION_V1 (same procedure as B2, independently selected)",
            "alpha_grid": ALPHA_GRID,
            "selected_alpha": h0_alpha,
            "tuned_on_development": True,
            "tuned_after_representation_lock": True,
            "purpose": h0_parent["purpose"],
            "compared_to_relational_representation": False, **common},
    }

    # B3 full signature audit
    import sklearn
    from sklearn.ensemble import HistGradientBoostingRegressor
    sig = inspect.signature(HistGradientBoostingRegressor.__init__)
    defaults = {k: (v.default if not isinstance(v.default, (list, dict)) else str(v.default))
                for k, v in sig.parameters.items() if k != "self"}
    defaults = {k: (None if v is inspect._empty else v) for k, v in defaults.items()}
    cfgs["BASELINE_B3_CONFIG.json"]["sklearn_version"] = sklearn.__version__
    cfgs["BASELINE_B3_CONFIG.json"]["explicit_parameters"] = {"random_state": B3_RANDOM_STATE}
    cfgs["BASELINE_B3_CONFIG.json"]["inherited_defaults"] = {
        k: v for k, v in defaults.items() if k != "random_state"}
    cfgs["BASELINE_B3_CONFIG.json"]["n_parameters"] = len(defaults)
    cfgs["BASELINE_B3_CONFIG.json"]["instantiation"] = (
        "HistGradientBoostingRegressor(random_state=%d)" % B3_RANDOM_STATE)

    for name, cfg in cfgs.items():
        (OUT / name).write_text(json.dumps(cfg, indent=2, default=str), encoding="utf-8")

    manifest = {
        "manifest_id": "BASELINE_CONFIGURATION_MANIFEST_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "written_after_lock": True,
        "lock_sha256": lock["lock_sha256"],
        "prevalue_sha256": prevalue_sha,
        "baselines": {c["baseline_id"]: {
            "file": n, "role": c["role"], "status": "FROZEN_NOT_RUN",
            "sha256": sha256(OUT / n),
            "tuned_on_development": c["tuned_on_development"],
            "selected_alpha": c.get("selected_alpha"),
        } for n, c in cfgs.items()},
        "all_frozen": True, "all_run": False,
        "external_evaluation_stage": "S7.10",
        "no_baseline_result_compared_to_relational_representation_in_S7_9": True,
        "no_baseline_outcome_influenced_representation_selection": True,
        "ordering_guarantee": (
            "DEVELOPMENT_REPRESENTATION_LOCK was written and hashed before the "
            "first alpha was evaluated; the selected support cannot change"),
        "S_pers": {"metric_id": "S_PERS_V1", "carried_unchanged": True,
                   "used_for_selection": False,
                   "used_to_reopen_any_utility_rank": False,
                   "status": "REQUIRED_REPORTING at S7.10"},
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
    }
    (OUT / "BASELINE_CONFIGURATION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print("baselines frozen: %s" % ", ".join(manifest["baselines"].keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
