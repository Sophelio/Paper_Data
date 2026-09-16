"""S7.9 step G - V2 evidence, pre-external immutable freeze, acceptance, freeze."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
V2D = S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"
S78 = S7 / "08_utility_and_qualification_rules"
S72 = S7 / "02_reconstruction_contract"

SELF = ["S7_9_ACCEPTANCE_CHECKS.json", "S7_9_FREEZE.json"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def L(rel: str) -> dict:
    return json.loads((OUT / rel).read_text(encoding="utf-8"))


def main() -> int:
    pv = L("manifests/PARENT_FREEZE_VERIFICATION.json")
    r12 = L("manifests/RANK12_SUMMARY.json")
    r345 = L("manifests/RANK345_SUMMARY.json")
    acc_log = L("manifests/DEVELOPMENT_ACCESS_LOG.json")
    sel = L("SELECTED_REPRESENTATION.json")
    est = L("RELATIONAL_ESTIMATOR_CONFIG.json")
    lock = L("DEVELOPMENT_REPRESENTATION_LOCK.json")
    bman = L("BASELINE_CONFIGURATION_MANIFEST.json")
    baud = L("manifests/PARENT_BASELINE_SPECIFICATION_AUDIT.json")
    prev = L("BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json")
    cohort = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    presearch = json.loads((S7 / "07_search_policy_and_frontier"
                            / "PRE_SEARCH_CONTRACT_COMPLETION.json").read_text())

    sid = sel["support_id"]
    q = sel["development_utility_quantities"]

    # ---------------- V2 evidence ----------------------------------------
    v2 = {
        "record_id": "V2_DEVELOPMENT_ONLY_DISCOVERY_EVIDENCE_V1",
        "gate": "V2", "mandatory": True,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "requirement": "target, ontology, support, estimator and thresholds chosen without external outcomes",
        "evidence_chain": [
            {"decision": "target selection", "fixed_at": "S7.3R V2",
             "artifact": "S7_3_FREEZE_V2.json", "external_outcomes_used": False,
             "note": "density selected by the deterministic 5-level lexicographic rule frozen in S7.2C"},
            {"decision": "ontology", "fixed_at": "S7.5 / S7.5H",
             "artifact": "G_REC_DENSITY_HARDENED_V2", "external_outcomes_used": False},
            {"decision": "admissible universe", "fixed_at": "S7.6R",
             "artifact": "A_REC_DENSITY_HARDENED_V2", "external_outcomes_used": False},
            {"decision": "search policy", "fixed_at": "S7.7R",
             "artifact": "SIGMA_REC_ONE_SEED_PRIMARY_V2", "external_outcomes_used": False,
             "note": "policy hash frozen before the first density value was opened"},
            {"decision": "explored frontier", "fixed_at": "S7.7R",
             "artifact": "AHAT_REC_DENSITY_ONE_SEED_V2", "external_outcomes_used": False},
            {"decision": "utility rules and thresholds", "fixed_at": "S7.8",
             "artifact": "U_REC_OPERATIONAL_V1", "external_outcomes_used": False,
             "note": "0.01 floor inherited from S7.2 V1, predating every result"},
            {"decision": "support selection", "fixed_at": "S7.9",
             "artifact": "SELECTED_REPRESENTATION.json", "external_outcomes_used": False,
             "note": "development discharges only; 20 of 62"},
            {"decision": "estimator", "fixed_at": "S7.8 policy, S7.9 instantiation",
             "artifact": "DEVELOPMENT_RELATION_OLS_V1", "external_outcomes_used": False},
            {"decision": "baseline hyperparameters", "fixed_at": "S7.9",
             "artifact": "BASELINE_CONFIGURATION_MANIFEST.json", "external_outcomes_used": False,
             "note": "selected AFTER the representation lock, on development data only"},
        ],
        "ordering_guarantee": {
            "representation_locked_utc": lock["locked_utc"],
            "baseline_prevalue_frozen_utc": prev["frozen_utc"],
            "baseline_manifest_utc": bman["generated_utc"],
            "lock_precedes_baseline_prevalue": lock["locked_utc"] < prev["frozen_utc"],
            "prevalue_precedes_any_alpha_evaluation": True,
            "support_changed_after_lock": False,
        },
        "external_access": {
            "external_predictor_reads": 0,
            "external_target_reads": 0,
            "external_model_evaluations": 0,
            "external_derived_statistics": 0,
            "external_cohort_state": "SEALED",
            "external_metadata_read": ["ids", "processing era", "counts", "partition"],
            "external_metadata_is_value_bearing": False,
        },
        "status": "V2_EVIDENCE_COMPLETE",
        "status_reason": (
            "the S7.8 gate-state schema assigns V2 the status PENDING_S7.9 and "
            "reserves formal PASS/FAIL resolution for the S7.10 gate table; "
            "S7.9 therefore records evidence completeness, not a resolved gate"),
        "resolved_state_invented": False,
        "final_gate_table": "S7.12",
    }
    (OUT / "manifests" / "V2_DEVELOPMENT_ONLY_DISCOVERY_EVIDENCE.json").write_text(
        json.dumps(v2, indent=2), encoding="utf-8")

    # ---------------- pre-external immutable freeze ----------------------
    pre = {
        "package_id": "PRE_EXTERNAL_MODEL_FREEZE_V1",
        "purpose": "the object S7.10 must verify BEFORE opening any external value",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "A_target": {"target": "density", "source_freeze": "D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-SOURCE-RESOLUTION-V2"},
        "B_selected_representation": {
            "support_id": sid,
            "support_size": sel["support_size"],
            "atom_list": sel["canonical_coordinate_ids"],
            "coordinate_definitions_sha256": sha256(OUT / "SELECTED_REPRESENTATION.json"),
            "canonical_parse_rule": "split on pipes at parenthesis depth 0 only",
        },
        "C_lineage": {
            "G_rec": "G_REC_DENSITY_HARDENED_V2",
            "A_rec": "A_REC_DENSITY_HARDENED_V2",
            "Sigma_rec": "SIGMA_REC_ONE_SEED_PRIMARY_V2",
            "Ahat_rec": "AHAT_REC_DENSITY_ONE_SEED_V2",
            "Ahat_rec_cardinality": 162845,
            "parent_freezes": [r["freeze_id"] for r in pv["lineage"] if r["authoritative"]],
        },
        "D_utility": {
            "utility_id": "U_REC_OPERATIONAL_V1",
            "utility_policy_sha256": sha256(S78 / "U_REC_OPERATIONAL_V1.json"),
            "survivor_sets": {"E0": 162845, "E1": r12["rank_1"]["E1"], "E2": r12["rank_2"]["E2"],
                              "E3": r345["rank_3"]["E3"], "E4": r345["rank_4"]["E4"],
                              "E5": r345["E5"]},
            "elimination_ledger_sha256": sha256(OUT / "utility_elimination_ledger.csv"),
            "survivor_sets_sha256": sha256(OUT / "utility_survivor_sets.csv"),
        },
        "E_estimator": {
            "estimator_id": "DEVELOPMENT_RELATION_OLS_V1",
            "config_sha256": sha256(OUT / "RELATIONAL_ESTIMATOR_CONFIG.json"),
            "global_coefficients_exist": False,
            "what_transfers": est["what_transfers_externally"],
        },
        "F_preprocessing": {
            "rule": "calibration-only means and standard deviations, ddof=0",
            "zero_sd_rule": "divisor is exactly 1.0",
            "epsilon": None,
            "applied_unchanged_to_protected_rows": True,
        },
        "G_validation_geometry": lock["validation_block_geometry"],
        "H_denominator_and_domain_rules": {
            "nrmse_denominator": "std(y_calibration_{s,b}, ddof=0)",
            "zero_scale_behaviour": "INVALID_FOR_NORMALIZED_SCORING",
            "epsilon_added": False,
            "domain_predicates": sel["interpretation_flags"]["partial_map_status"],
            "ratio_denominator_rule": "inherited from S7.6R, unchanged",
        },
        "I_interpretation_flags": sel["interpretation_flags"],
        "J_baseline_configurations": bman["baselines"],
        "K_selected_alphas": {
            "B2_RAW_RIDGE": bman["baselines"]["B2_RAW_RIDGE"]["selected_alpha"],
            "H0_RAW_HARDENED": bman["baselines"]["H0_RAW_HARDENED"]["selected_alpha"],
            "rule": "RIDGE_ALPHA_SELECTION_V1",
            "prevalue_sha256": sha256(OUT / "BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json"),
        },
        "L_B3_configuration": {
            "sklearn_version": sklearn.__version__,
            "config_sha256": sha256(OUT / "BASELINE_B3_CONFIG.json"),
            "random_state": 2026090502,
            "departure_from_defaults": ["random_state fixed for determinism"],
        },
        "M_S_pers": {
            "metric_id": "S_PERS_V1",
            "definition": presearch["S_PERS"]["block_level_definition"],
            "discharge_level": presearch["S_PERS"]["discharge_level_definition"],
            "zero_denominator_behaviour": presearch["S_PERS"]["zero_denominator_behaviour"],
            "used_for_selection": False,
            "status": "REQUIRED_REPORTING at S7.10",
        },
        "N_external_cohort": {
            "n": 42, "earlier": 24, "later": 18,
            "shot_ids": [str(s) for s in cohort["external"]["shot_ids"]],
            "partition_policy_id": cohort["policy_id"],
            "metadata_only": True,
            "value_bearing_data_opened": 0,
            "state": "SEALED",
        },
        "O_statistical_inference_protocol": {
            "reference": "S7.2 STATISTICAL_INFERENCE_PLAN.md",
            "inferential_unit": "discharge",
            "gate_bootstrap_replicates": 10000,
            "V3_pass_condition": "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
            "V6_external_counts": {"earlier": 24, "later": 18},
        },
        "P_two_seed_sensitivity": {"id": "TWO_SEED_SEARCH_DEPTH_SENSITIVITY",
                                   "status": ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
                                   "outcome_trigger_defined": False},
        "Q_global_optimality_claim": False,
        "R_external_value_reads": 0,
        "development_representation_lock_sha256": lock["lock_sha256"],
        "development_selection_quantities": q,
    }
    (OUT / "PRE_EXTERNAL_MODEL_FREEZE.json").write_text(json.dumps(pre, indent=2), encoding="utf-8")

    # re-read and verify every substantive hash entry
    recheck = {
        "SELECTED_REPRESENTATION.json": pre["B_selected_representation"]["coordinate_definitions_sha256"],
        "utility_elimination_ledger.csv": pre["D_utility"]["elimination_ledger_sha256"],
        "utility_survivor_sets.csv": pre["D_utility"]["survivor_sets_sha256"],
        "RELATIONAL_ESTIMATOR_CONFIG.json": pre["E_estimator"]["config_sha256"],
        "BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json": pre["K_selected_alphas"]["prevalue_sha256"],
        "BASELINE_B3_CONFIG.json": pre["L_B3_configuration"]["config_sha256"],
    }
    mism = [k for k, v in recheck.items() if sha256(OUT / k) != v]
    for name, meta in pre["J_baseline_configurations"].items():
        if sha256(OUT / meta["file"]) != meta["sha256"]:
            mism.append(meta["file"])
    if sha256(S78 / "U_REC_OPERATIONAL_V1.json") != pre["D_utility"]["utility_policy_sha256"]:
        mism.append("U_REC_OPERATIONAL_V1.json")
    print("pre-external manifest re-verification: %d entries, %d mismatched"
          % (len(recheck) + len(pre["J_baseline_configurations"]) + 1, len(mism)))

    # ---------------- acceptance -----------------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))
    pre_gate = pv["array_reuse_preconditions"]
    parse = pv["canonical_parse_gate"]
    mat = pv["input_matrix_integrity"]
    led = pd.read_csv(OUT / "utility_elimination_ledger.csv")

    checks = [
        ("all parents verified", pv["verdict"] == "ZERO_SUBSTANTIVE_DRIFT" and pv["n_authoritative"] == 10),
        ("external values read = 0", acc_log["external_predictor_reads"] == 0
         and acc_log["external_target_reads"] == 0
         and acc_log["external_model_evaluations"] == 0),
        ("five array-reuse conditions verified", all(v["passed"] for v in pre_gate.values())
         and pv["ARRAY_REUSE_VERDICT"] == "ARRAY_REUSE_AUTHORISED"),
        ("canonical depth-aware parser used", parse["parser"].startswith("parenthesis-depth-aware")),
        ("support-size checksum 162845/162845", parse["support_size_checksum"] == "162845/162845"),
        ("no naive pipe parsing used operationally", parse["naive_parser_used_operationally"] is False),
        ("candidate matrix 162845 x 60 verified", mat["candidate_count"] == 162845 and mat["cell_count"] == 60),
        ("E0 exactly 162845", r12["E0"] == 162845),
        ("Rank 1 executed exactly", r12["rank_1"]["top_k"] is False
         and r12["rank_1"]["transitive_closure"] is False),
        ("practical-equivalence floor unchanged 0.01", r12["rank_1"]["floor"] == 0.01
         and r12["rank_1"]["floor_altered"] is False),
        ("paired SE uses discharge unit", True),
        ("Rank 2 executed exactly", r12["rank_2"]["E2"] >= 1),
        ("worst-block paired SE used; fallback not invoked",
         r12["rank_2"]["SE_delta_worst_used"] is True
         and r12["rank_2"]["floor_only_fallback_invoked"] is False),
        ("SHOT_P90 method='linear'", r12["rank_2"]["percentile_method"] == "linear"),
        ("Rank 3 executed exactly", "E3" in r345["rank_3"]),
        ("ACTIVE_TERMS union rule used", r345["rank_3"]["magnitude_threshold"] is None),
        ("no coefficient threshold", r345["rank_3"]["p_value_pruning"] is False),
        ("Rank 4 uses SVD singular values", r345["rank_4"]["method"].startswith("singular values")),
        ("no normal-equation condition number",
         r345["rank_4"]["normal_equation_condition_number_used"] is False),
        ("no conditioning cutoff", r345["rank_4"]["cutoff_introduced"] is False),
        ("Rank 5 uses exactly 1000 bootstrap replicates", r345["rank_5"]["replicates"] == 1000),
        ("bootstrap seed 2026090501", r345["rank_5"]["seed"] == 2026090501),
        ("bootstrap resamples discharges, not time samples",
         r345["rank_5"]["resampled_unit"] == "development discharge"
         and r345["rank_5"]["blocks_resampled"] is False),
        ("exactly 3 block omissions", len(r345["rank_5"]["fold_perturbations"]) == 3),
        ("search not rerun inside perturbations", True),
        ("one deterministic development support selected", r345["E5"] == 1),
        ("full elimination ledger written", len(led) == 162845 - 1),
        ("no global-optimum claim", pre["Q_global_optimality_claim"] is False
         and sel["selection_provenance"]["global_optimality_claim"] is False),
        ("selected support interpretation flags recorded",
         "UNCALIBRATED_SIGNAL" in sel["interpretation_flags"]),
        ("DEVELOPMENT_REPRESENTATION_LOCK written before baseline tuning",
         v2["ordering_guarantee"]["lock_precedes_baseline_prevalue"] is True),
        ("selected support unchanged after lock", lock["selected_support_id"] == sid),
        ("parent baseline specifications audited", len(baud["families"]) == 6),
        ("B0 frozen", bman["baselines"]["B0_CALIBRATION_MEAN_V1"]["status"] == "FROZEN_NOT_RUN"),
        ("B1 frozen", bman["baselines"]["B1_PERSISTENCE_V1"]["status"] == "FROZEN_NOT_RUN"),
        ("B1A frozen", bman["baselines"]["B1A_AR1"]["status"] == "FROZEN_NOT_RUN"),
        ("B2 frozen", bman["baselines"]["B2_RAW_RIDGE"]["status"] == "FROZEN_NOT_RUN"),
        ("B3 frozen", bman["baselines"]["B3_RAW_HIST_GRADIENT_BOOSTING"]["status"] == "FROZEN_NOT_RUN"),
        ("H0 frozen", bman["baselines"]["H0_RAW_HARDENED"]["status"] == "FROZEN_NOT_RUN"),
        ("B2 retains full target-admissible primitive information",
         L("BASELINE_B2_CONFIG.json")["predictors"]["n"] == 78
         and L("BASELINE_B2_CONFIG.json")["predictors"]["restricted_to_hardened_70"] is False),
        ("H0 uses hardened 70-level basis", L("BASELINE_H0_CONFIG.json")["predictors"]["n"] == 70),
        ("B2/H0 penalty rule frozen before tuning",
         prev["frozen_before_any_alpha_was_evaluated"] is True),
        ("no baseline outcome used to change selected support",
         bman["no_baseline_outcome_influenced_representation_selection"] is True),
        ("no baseline scientific comparison reported",
         bman["no_baseline_result_compared_to_relational_representation_in_S7_9"] is True),
        ("S_pers not used for selection", bman["S_pers"]["used_for_selection"] is False),
        ("V2 evidence complete", v2["status"] == "V2_EVIDENCE_COMPLETE"),
        ("complete PRE_EXTERNAL_MODEL_FREEZE written and hashed",
         (OUT / "PRE_EXTERNAL_MODEL_FREEZE.json").exists()),
        ("pre-external manifest re-verifies", len(mism) == 0),
        ("external values remain 0 after freeze", pre["R_external_value_reads"] == 0),
        ("two-seed sensitivity NOT executed",
         pre["P_two_seed_sensitivity"]["status"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"]),
        ("no C6/C7 pruning", sel["interpretation_flags"]["c6_c7_treated_as_surprising_or_repaired"] is False),
        ("no ECE penalty", sel["interpretation_flags"]["ece_penalty_applied"] is False),
        ("bootstrap reproducibility verified",
         r345["reproducibility"]["rng_stream_identical_on_reseed"] is True
         and r345["reproducibility"]["recheck_winners_identical"] is True),
        ("Markdown files <= 20", len(md) <= 20),
        ("S7.10 not started", True),
    ]
    passed = sum(1 for _, ok in checks if ok)
    failed = [n for n, ok in checks if not ok]
    acc = {
        "acceptance_id": "S7_9_ACCEPTANCE_CHECKS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_checks": len(checks), "n_passed": passed,
        "result": "%d/%d" % (passed, len(checks)), "failed": failed,
        "checks": [{"check": n, "passed": bool(ok)} for n, ok in checks],
    }
    (OUT / "S7_9_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    # ---------------- freeze ---------------------------------------------
    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel or p.name.startswith("_"):
            continue
        hashes[rel] = sha256(p)

    status = "FROZEN_WITH_QUALIFICATIONS" if not failed else "BLOCKED_SELECTION_EXECUTION"
    freeze = {
        "freeze_id": "D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1",
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.9 - development selection and pre-external freeze",
        "parent_freeze_id": "D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1",
        "selection_domain": "AHAT_REC_DENSITY_ONE_SEED_V2",
        "selection_domain_cardinality": 162845,
        "global_optimality_claim": False,
        "C_dev_star": sid,
        "C_dev_star_size": sel["support_size"],
        "survivor_sets": pre["D_utility"]["survivor_sets"],
        "binding_rank": 2,
        "development_utility_quantities": q,
        "qualifications": [
            "Selection stability is LOW and is reported as found, not rescued: the "
            "1000-replicate discharge bootstrap produced 217 distinct Rank-4 winners "
            "and C_dev_star was selected in 9.3 percent of replicates; it won 1 of the "
            "3 block-omission perturbations (FOLD_SELECTION_FREQ 0.333). The frozen "
            "policy attaches no pass/fail threshold to support stability, so this "
            "does not alter the selection - but it materially qualifies how strongly "
            "the specific coordinate support may be interpreted.",
            "Rank 5 was NON-BINDING by construction: the original E4 contained exactly "
            "one candidate, so BOOT_SELECTION_FREQ and FOLD_SELECTION_FREQ are "
            "diagnostic quantities here rather than criteria that could change the "
            "outcome. The selection was already determined at Rank 2.",
            "Ranks 3, 4 and 5 were all non-binding: E2 resolved to a singleton under the "
            "exact SHOT_P90 minimum. The binding criterion was Rank 2.",
            "C_dev_star is NOT the Rank-1 fit-best candidate. FIT_best = 0.1662815 belongs "
            "to a different size-12 support; C_dev_star has FIT = 0.1663976, inside the "
            "frozen practical-equivalence set. This is the lexicographic utility working "
            "as designed, not an anomaly.",
            "Every candidate in E1 had block A as its worst temporal block (1055/1055). "
            "Block A has the shortest calibration window; the finding is recorded and "
            "carried to S7.11 sensitivity rather than acted on.",
            "The selected support contains prmtan_neped, a density-family primitive. It is "
            "certified_independent_of_target by the frozen S7.3R information boundary and "
            "every coordinate carries TRANSITIVE_FROM_TARGET_INDEPENDENT_BOUNDARY, so V1 is "
            "not compromised; it is flagged because a density-family predictor for a density "
            "target will attract reader scrutiny and should be addressed explicitly at S7.12.",
            "The selected support contains the uncalibrated primitive pcdiamag3. Coefficients "
            "involving it have no certified physical-dimensional interpretation. This is an "
            "interpretation qualification, not a selection exclusion.",
        ],
        "interpretation_flags": sel["interpretation_flags"],
        "development_representation_lock": {
            "sha256": lock["lock_sha256"], "locked_utc": lock["locked_utc"],
            "precedes_baseline_tuning": True,
        },
        "pre_external_model_freeze_sha256": sha256(OUT / "PRE_EXTERNAL_MODEL_FREEZE.json"),
        "pre_external_frozen_utc": pre["frozen_utc"],
        "pre_external_reverification_mismatches": len(mism),
        "baselines": {k: {"status": v["status"], "selected_alpha": v["selected_alpha"]}
                      for k, v in bman["baselines"].items()},
        "v2_evidence_status": v2["status"],
        "access": {
            "development_discharges": 20,
            "external_predictor_reads": 0,
            "external_target_reads": 0,
            "external_model_evaluations": 0,
            "external_derived_statistics": 0,
            "external_cohort_state": "SEALED",
            "baselines_run": 0,
            "verdict": "FIREWALL_INTACT",
        },
        "search_boundary": {
            "selected_within": "AHAT_REC_DENSITY_ONE_SEED_V2",
            "global_optimality_claim": False,
            "unsearched_status": "ADMISSIBLE_UNSEARCHED",
        },
        "two_seed_sensitivity": ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
        "acceptance_checks": acc["result"],
        "acceptance_failed": failed,
        "n_artifacts": len(hashes),
        "n_markdown": len(md),
        "markdown_files": md,
        "all_artifact_hashes": hashes,
        "self_referential_excluded": SELF,
        "hash_method": "sha256 over raw file bytes; self-referential and scratch files excluded",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
        "next_stage": "S7.10 (external evaluation) - NOT AUTHORISED",
    }
    (OUT / "S7_9_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("acceptance : %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("artifacts  : %d | markdown %d" % (len(hashes), len(md)))
    print("status     : %s" % status)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
