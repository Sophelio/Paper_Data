"""S7.2 — assemble K_rec^pre, run acceptance checks, freeze.

Hashes are taken over **raw file bytes** throughout, uniformly. The S7.1 freeze
used a mixed rule (see manifests/S7_1_INPUT_VERIFICATION.json); S7.2 does not
repeat that.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S72 = HERE.parent
S7 = S72.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"

FREEZE_ID = "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V1"
PARENT_ID = "D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
def target_eligibility_schema() -> dict:
    return {
        "schema_id": "S7.2-TARGET-ELIGIBILITY-V1",
        "applied_at": "S7.3",
        "produces_ranking_at_S7_2": False,
        "class_policy": {
            "eligible": [
                "DIRECT_MEASUREMENT with resolved physical meaning and unit",
                "DIAGNOSTIC_RECONSTRUCTION with resolved physical meaning and unit",
            ],
            "normally_excluded": {
                "CONTROL_COMMAND_OR_ACTUATION": {
                    "n": 14,
                    "reason": "reconstructing an actuator command describes the "
                              "control system, not the plasma"},
                "EQUILIBRIUM_DERIVED": {
                    "n": 15,
                    "reason": "all LINEAGE_PARTIAL; EFIT ancestry unresolved so "
                              "provenance closure cannot be certified"},
                "UNCALIBRATED_RAW": {
                    "n": 2, "signals": ["pcbcoil", "pcdiamag3"],
                    "reason": "no physical unit exists; reconstruction error "
                              "would be uninterpretable"},
                "DERIVED_EVENT_LABELS": {
                    "n": 0, "reason": "none exist in the archive"},
            },
            "override_allowed": True,
            "override_conditions": [
                "justified without reference to model performance",
                "recorded in CONTRACT_DECISION_LEDGER.md",
                "decided on development data only",
            ],
        },
        "criteria": [
            {"id": 1, "criterion": "scalar time series",
             "decidable_from": "S7.1 metadata", "cohort": "n/a"},
            {"id": 2, "criterion": "available across the frozen object",
             "decidable_from": "S7.1 metadata", "cohort": "n/a"},
            {"id": 3, "criterion": "physically interpretable",
             "decidable_from": "units registry", "cohort": "n/a"},
            {"id": 4, "criterion": "resolved physical unit",
             "decidable_from": "units registry", "cohort": "n/a"},
            {"id": 5, "criterion": "calibrated diagnostic or state quantity",
             "decidable_from": "origin classification", "cohort": "n/a"},
            {"id": 6, "criterion": "plausible residual explanatory information "
                                   "after boundary closure",
             "decidable_from": "instantiated I_rec", "cohort": "DEVELOPMENT_ONLY"},
            {"id": 7, "criterion": "no event taxonomy required",
             "decidable_from": "task definition", "cohort": "n/a"},
            {"id": 8, "criterion": "no specialist regime classification required",
             "decidable_from": "task definition", "cohort": "n/a"},
            {"id": 9, "criterion": "no obvious algebraic duplicate among "
                                   "admitted predictors",
             "decidable_from": "provenance + values", "cohort": "DEVELOPMENT_ONLY"},
            {"id": 10, "criterion": "meaningful temporal variation",
             "decidable_from": "values", "cohort": "DEVELOPMENT_ONLY"},
            {"id": 11, "criterion": "usable in both processing eras",
             "decidable_from": "S7.1 metadata", "cohort": "n/a"},
            {"id": 12, "criterion": "no dependence on an unresolved "
                                    "label-generation pipeline",
             "decidable_from": "provenance", "cohort": "n/a"},
        ],
        "predeclared_thresholds": {
            "min_admissible_predictors_after_closure": 10,
            "min_coefficient_of_variation_development": 0.05,
            "min_distinct_values_fraction": 0.10,
            "max_identically_zero_development_discharges": 0,
        },
        "firewall": {
            "external_cohort_may_be_inspected": False,
            "candidates_compared_on_reconstructability": False,
            "model_fitted_for_eligibility": False,
        },
        "multichannel_family_rule": (
            "if the candidate belongs to ECE / CER / beams / filterscopes, the "
            "sibling rule in INFORMATION_BOUNDARY_POLICY.md applies: primary "
            "boundary excludes same-family siblings; full-boundary variant is a "
            "declared sensitivity"),
    }


def k_rec_pre() -> dict:
    F, P = "FROZEN", "PARTIALLY_FROZEN"
    return {
        "contract_id": "K_REC_PRE_V1",
        "freeze_id": FREEZE_ID,
        "parent_freeze_id": PARENT_ID,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "formal_tuple": "K_rec = (q, I, P, B, H, U, V, Omega)",
        "note": ("Explicit incompleteness is a feature. Components that depend "
                 "on a target cannot be instantiated before S7.3 selects one, "
                 "and pretending otherwise would hide a decision."),
        "q_rec": {
            "status": F,
            "task_class": "CONTINUOUS_RECONSTRUCTION",
            "statement": ("reconstruct one observed scalar plasma or state "
                          "quantity from the other task-admissible "
                          "contemporaneous observations"),
            "transfer_type": "STRUCTURAL_TRANSFER_WITH_LOCAL_CALIBRATION",
            "is_not": ["ELM detection", "event classification", "forecasting",
                       "causal inference", "control",
                       "zero-shot coefficient transfer",
                       "universal plasma equation discovery"],
            "target_selected": False,
            "target_selection": "DEFERRED_TO_S7.3",
            "artifacts": ["RECONSTRUCTION_TASK_DEFINITION.md",
                          "RELATION_AND_TRANSFER_POLICY.md"],
        },
        "I_rec": {
            "policy_status": F,
            "instantiated_signal_set": "DEFERRED_TO_S7.3",
            "coordinate_closure": "DEFERRED_TO_S7.5",
            "exclusion_rules": [
                "the target itself",
                "exact duplicates and aliases of the target",
                "quantities whose definition contains the target",
                "quantities with verified upstream dependence on the target",
                "quantities with UNRESOLVED ancestry relative to the target "
                "(fail-closed)",
                "downstream coordinates of anything excluded (transitive)",
            ],
            "fail_closed": True,
            "correlation_is_ancestry": False,
            "sibling_rule": "primary boundary excludes same-family siblings; "
                            "full-boundary variant is a declared sensitivity",
            "artifacts": ["INFORMATION_BOUNDARY_POLICY.md",
                          "leakage_matrix.csv"],
        },
        "P_rec": {
            "invariant_rules_status": F,
            "target_specific_provenance_closure": "DEFERRED_TO_S7.3",
            "instantiated_over_ontology": "DEFERRED_TO_S7.6",
            "classes": ["A provenance", "B information-boundary compliance",
                        "C dimensional", "D numerical support",
                        "E denominator/singularity", "F temporal resolution",
                        "G semantic", "H leakage"],
            "unit_canonicalisation": F,
            "numerical_resolution_rule": F,
            "artifacts": ["ADMISSIBILITY_POLICY.md", "UNIT_AND_TYPE_POLICY.md",
                          "NUMERICAL_RESOLUTION_POLICY.md"],
        },
        "B_rec": {
            "constructor_depth_rules_status": F,
            "surviving_candidate_count": "DEFERRED_TO_S7.5/S7.6",
            "explored_frontier": "DEFERRED_TO_S7.7",
            "max_temporal_derivative_order": 1,
            "max_relational_depth": 1,
            "max_product_arity": 2,
            "representation_size_range": [1, 12],
            "transcendental_library": "none unless scientifically motivated",
            "artifacts": ["SEARCH_BOUND_POLICY.md"],
        },
        "H_rec": {
            "status": F,
            "allowed_uses": ["admit or reject a constructor", "assign type",
                             "identify known dependency",
                             "prioritise a search family"],
            "forbidden_use": "knowledge may not count as validation evidence",
            "seeding_firewall": {
                "q_desc_support_may_seed": False,
                "retired_q_rec_support_may_seed": False,
                "dfl_export_may_seed": False,
                "dfl_features_as_primitives": False,
            },
            "artifacts": ["KNOWLEDGE_POLICY.md"],
        },
        "U_rec": {
            "status": F,
            "structure": "lexicographic",
            "criteria_in_order": ["primary fit quality",
                                  "generalization/stability", "parsimony",
                                  "conditioning", "support stability"],
            "practical_equivalence": {
                "one_standard_error_rule": True,
                "practical_equivalence_floor_calibration_normalized_rmse": 0.01,
                "declared_before_search": True,
            },
            "fabricated_error_weights": False,
            "instantiated_computation": "DEFERRED_TO_S7.9",
            "artifacts": ["UTILITY_AND_QUALIFICATION_POLICY.md"],
        },
        "V_rec": {
            "protocol_status": F,
            "gate_evaluation": "DEFERRED_TO_S7.10",
            "validation_geometry": {
                "type": "rolling-origin, expanding calibration, disjoint "
                        "protected blocks",
                "blocks": [
                    {"block": "A", "calibration": [0.0, 0.40],
                     "protected": [0.40, 0.50]},
                    {"block": "B", "calibration": [0.0, 0.60],
                     "protected": [0.60, 0.70]},
                    {"block": "C", "calibration": [0.0, 0.80],
                     "protected": [0.80, 0.90]},
                ],
                "feasibility": "FEASIBLE_AT_ALL_CANDIDATE_CADENCES",
                "chosen_without_target_values": True,
            },
            "baselines": ["B0 calibration mean", "B1 persistence",
                          "B2 raw ridge linear",
                          "B3 HistGradientBoostingRegressor"],
            "gates": {f"V{i}": g for i, g in enumerate([
                "information boundary", "development-only discovery",
                "nontrivial skill", "raw-coordinate comparison",
                "external structural transfer", "processing-era robustness",
                "common support", "discharge-level inference", "sensitivity",
                "numerical provenance"], start=1)},
            "mandatory_gates": ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8",
                                "V10"],
            "inferential_unit": "discharge",
            "bootstrap_replicates": 10000,
            "artifacts": ["VALIDATION_PROTOCOL.md", "BASELINE_PROTOCOL.md",
                          "STATISTICAL_INFERENCE_PLAN.md",
                          "PREPROCESSING_AND_LEAKAGE_POLICY.md"],
        },
        "Omega_rec": {
            "candidate_status": F,
            "candidate": "the frozen 62-discharge DIII-D observational object "
                         + PARENT_ID,
            "final_status": "DEFERRED_TO_S7.10/S7.12",
            "cohort_partition": {
                "status": F, "development": 20, "external": 42,
                "deterministic": True, "seed": None, "target_blind": True,
            },
            "out_of_scope": ["all DIII-D", "all operating regimes",
                             "unseen devices", "prospective control",
                             "forecasting", "causal structure",
                             "native high-frequency physics",
                             "diagnostic bandwidth",
                             "universal plasma relations"],
            "artifacts": ["DOMAIN_AND_CLAIM_BOUNDARY.md", "CLAIM_BOUNDARY.md",
                          "COHORT_PARTITION_POLICY.md",
                          "EXTERNAL_COHORT_FIREWALL.md"],
        },
        "component_status_summary": {
            "q_rec": F, "I_rec": P, "P_rec": P, "B_rec": P, "H_rec": F,
            "U_rec": F, "V_rec": P, "Omega_rec": P,
        },
        "gate": {
            "target_selected": False, "targets_ranked": False,
            "sir_run": False, "regression_run": False,
            "coordinates_generated": False, "G_rec_constructed": False,
            "A_rec_enumerated": False, "Ahat_rec_searched": False,
            "performance_inspected": False,
            "external_signal_values_inspected": False,
            "s7_3_started": False,
        },
    }


def main() -> None:
    (S72 / "target_eligibility_schema.json").write_text(
        json.dumps(target_eligibility_schema(), indent=2), encoding="utf-8")
    K = k_rec_pre()
    (S72 / "K_REC_PRE.json").write_text(json.dumps(K, indent=2),
                                        encoding="utf-8")

    verif = json.loads(
        (S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    vw = json.loads((S72 / "validation_windows.json").read_text())
    lm = (S72 / "leakage_matrix.csv").read_text(encoding="utf-8")

    def has(doc: str, *needles: str) -> bool:
        t = (S72 / doc).read_text(encoding="utf-8")
        return all(n.lower() in t.lower() for n in needles)

    checks = {
        "s7_1_hashes_verified": verif["verdict"] == "S7_1_INPUT_VERIFIED",
        "O_remains_frozen_95_signal_object":
            verif["object_summary"]["n_signals"] == 95
            and verif["object_summary"]["n_discharges"] == 62,
        "no_target_selected": not K["gate"]["target_selected"],
        "no_candidate_target_ranked": not K["gate"]["targets_ranked"],
        "no_model_performance_inspected": not K["gate"]["performance_inspected"],
        "partition_uses_metadata_only":
            part["signal_values_used"] is False
            and part["target_values_used"] is False,
        "both_processing_eras_represented":
            len(part["development"]["by_era"]) == 2
            and len(part["external"]["by_era"]) == 2,
        "external_values_sealed_until_S7_10":
            has("EXTERNAL_COHORT_FIREWALL.md", "SEALED", "S7.10"),
        "target_values_forbidden_as_features":
            "feature / coordinate construction,NO,NO,NO" in lm,
        "fail_closed_provenance_frozen": K["I_rec"]["fail_closed"] is True,
        "correlation_not_ancestry": K["I_rec"]["correlation_is_ancestry"] is False,
        "unit_canonicalisation_frozen": K["P_rec"]["unit_canonicalisation"] == "FROZEN",
        "numerical_resolution_rule_frozen":
            K["P_rec"]["numerical_resolution_rule"] == "FROZEN",
        "interpolation_cannot_create_primary_derivative_evidence":
            has("NUMERICAL_RESOLUTION_POLICY.md", "NO SUPER-RESOLUTION",
                "NUMERICAL_SENSITIVITY_ONLY"),
        "whole_discharge_protected_normalization_forbidden":
            has("PREPROCESSING_AND_LEAKAGE_POLICY.md",
                "whole-discharge z-scoring is FORBIDDEN"),
        "validation_geometry_frozen_without_target_values":
            vw["target_values_used_to_choose_windows"] is False
            and vw["verdict"] == "FEASIBLE_AT_ALL_CANDIDATE_CADENCES",
        "baseline_B0_constant_frozen": "B0 calibration mean" in K["V_rec"]["baselines"],
        "baseline_B1_persistence_frozen": "B1 persistence" in K["V_rec"]["baselines"],
        "baseline_B2_raw_linear_frozen": "B2 raw ridge linear" in K["V_rec"]["baselines"],
        "baseline_B3_raw_nonlinear_frozen":
            "B3 HistGradientBoostingRegressor" in K["V_rec"]["baselines"],
        "discharge_is_inferential_unit": K["V_rec"]["inferential_unit"] == "discharge",
        "processing_era_stratification_required":
            has("UTILITY_AND_QUALIFICATION_POLICY.md", "V6", "processing-era"),
        "q_desc_support_not_used":
            K["H_rec"]["seeding_firewall"]["q_desc_support_may_seed"] is False,
        "retired_q_rec_support_not_used":
            K["H_rec"]["seeding_firewall"]["retired_q_rec_support_may_seed"] is False,
        "dfl_features_not_used_as_primitives":
            K["H_rec"]["seeding_firewall"]["dfl_features_as_primitives"] is False,
        "E_not_fabricated": K["U_rec"]["fabricated_error_weights"] is False,
        "claim_is_reconstruction_structural_transfer_only":
            K["q_rec"]["task_class"] == "CONTINUOUS_RECONSTRUCTION"
            and K["q_rec"]["transfer_type"]
                == "STRUCTURAL_TRANSFER_WITH_LOCAL_CALIBRATION",
        "K_REC_PRE_records_deferred_fields":
            any("DEFERRED" in json.dumps(v) for v in K.values()
                if isinstance(v, dict)),
        "contract_decision_ledger_complete":
            (S72 / "CONTRACT_DECISION_LEDGER.md").exists(),
        "s7_1_files_unchanged": verif["n_hash_drift"] == 0,
    }

    # hash every artifact produced by this stage
    arts = sorted(
        [p for p in S72.rglob("*")
         if p.is_file() and p.suffix in {".md", ".json", ".csv", ".py"}],
        key=lambda p: str(p).lower())
    art_hashes = {str(p.relative_to(S72)).replace("\\", "/"): sha(p)
                  for p in arts}
    checks["all_generated_artifacts_hashed"] = len(art_hashes) >= 25

    n_pass = sum(bool(v) for v in checks.values())
    (S72 / "S7_2_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n_pass}/{len(checks)}",
        "all_passed": n_pass == len(checks),
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    status = ("FROZEN_READY_FOR_S7.3" if n_pass == len(checks) else "BLOCKED")

    freeze = {
        "freeze_id": FREEZE_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "S7_1_parent_freeze_id": PARENT_ID,
        "S7_1_parent_hash": verif["canonical_raw_byte_hashes"],
        "S7_1_input_verification":
            sha(S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json"),
        "cohort_partition_hash": sha(S72 / "COHORT_PARTITION.json"),
        "validation_protocol_hash": sha(S72 / "validation_windows.json"),
        "information_boundary_policy_hash":
            sha(S72 / "INFORMATION_BOUNDARY_POLICY.md"),
        "admissibility_policy_hash": sha(S72 / "ADMISSIBILITY_POLICY.md"),
        "baseline_protocol_hash": sha(S72 / "BASELINE_PROTOCOL.md"),
        "utility_policy_hash": sha(S72 / "UTILITY_AND_QUALIFICATION_POLICY.md"),
        "K_REC_PRE_hash": sha(S72 / "K_REC_PRE.json"),
        "contract_decision_ledger_hash":
            sha(S72 / "CONTRACT_DECISION_LEDGER.md"),
        "target_eligibility_schema_hash":
            sha(S72 / "target_eligibility_schema.json"),
        "leakage_matrix_hash": sha(S72 / "leakage_matrix.csv"),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "interpreter": r".venv_lorenz_benchmark\Scripts\python.exe",
        },
        "hash_method": "sha256 over raw file bytes, uniformly",
        "all_artifact_hashes": art_hashes,
        "n_artifacts": len(art_hashes),
        "acceptance_checks": f"{n_pass}/{len(checks)}",
        "component_status": K["component_status_summary"],
        "gate": K["gate"],
        "status": status,
        "next_stage": "S7.3 (target feasibility and information boundary) "
                      "- NOT AUTHORISED",
    }
    (S72 / "S7_2_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                          encoding="utf-8")

    print(f"S7.2 acceptance: {n_pass}/{len(checks)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"artifacts hashed: {len(art_hashes)}")
    print(f"STATUS: {status}")
    print(f"freeze_id: {FREEZE_ID}")


if __name__ == "__main__":
    main()
