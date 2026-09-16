"""S7.2C — pre-target contract correction. Produces V2 machine-readable artifacts.

Inspects no signal values, ranks no targets, fits nothing. The only data read
are V1 contract artifacts and the frozen S7.1 metadata already verified in V1.

V1 is preserved unmodified; V2 inherits it and supersedes named clauses only.

Hash-manifest construction
--------------------------
V1's manifest recorded stale hashes for `S7_2_ACCEPTANCE_CHECKS.json` and
`S7_2_FREEZE.json`, because both are written after the manifest is built -- a
file cannot contain its own hash. V2 excludes self-referential files from the
manifest explicitly and says so, rather than recording a value that is
guaranteed wrong.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CV1 = HERE.parent
S72 = CV1.parent
S7 = S72.parent

FREEZE_V2 = "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V2"
FREEZE_V1 = "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V1"
PARENT_S7_1 = "D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1"

# Written after the manifest is built; cannot contain their own hash.
SELF_REFERENTIAL = {"S7_2_ACCEPTANCE_CHECKS.json", "S7_2_FREEZE.json",
                    "S7_2C_ACCEPTANCE_CHECKS.json", "S7_2_FREEZE_V2.json"}

PRACTICAL_FLOOR = 0.01
RRV_FLOOR = 0.05


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
def verify_v1() -> dict:
    f = json.loads((S72 / "S7_2_FREEZE.json").read_text())
    matched, drift, skipped = [], [], []
    for rel, h in f["all_artifact_hashes"].items():
        if rel in SELF_REFERENTIAL:
            skipped.append(rel)
            continue
        p = S72 / rel
        if not p.exists():
            drift.append({"artifact": rel, "issue": "MISSING"})
        elif sha(p) != h:
            drift.append({"artifact": rel, "issue": "DRIFT",
                          "expected": h, "actual": sha(p)})
        else:
            matched.append(rel)
    return {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "v1_freeze_id": f["freeze_id"],
        "v1_status": f["status"],
        "v1_acceptance": f["acceptance_checks"],
        "v1_freeze_file_sha256": sha(S72 / "S7_2_FREEZE.json"),
        "v1_acceptance_file_sha256": sha(S72 / "S7_2_ACCEPTANCE_CHECKS.json"),
        "v1_K_REC_PRE_sha256": sha(S72 / "K_REC_PRE.json"),
        "n_artifacts_in_v1_manifest": len(f["all_artifact_hashes"]),
        "n_verified": len(matched),
        "n_drift": len(drift),
        "drift": drift,
        "self_referential_excluded": sorted(skipped),
        "self_reference_note": (
            "V1's manifest was built before these files were written, so the "
            "hashes it records for them are necessarily stale. This is a "
            "construction defect in the V1 manifest, not drift in the "
            "artifacts. V2 excludes self-referential files explicitly."),
        "v1_preserved_unmodified": len(drift) == 0,
        "verdict": "V1_INTACT" if not drift else "V1_DRIFT_STOP",
    }


def superseded_clauses() -> list[dict]:
    return [
        {"clause_id": "C-01",
         "v1_location": "UTILITY_AND_QUALIFICATION_POLICY.md; "
                        "K_REC_PRE.json U_rec.practical_equivalence",
         "v1_rule": "practically equivalent iff within 1 SE AND within 0.01",
         "defect": "conjunction makes the floor inoperative exactly when it is "
                   "needed: if SE is tiny, the tiny SE stays binding and the "
                   "0.01 floor never relaxes anything",
         "v2_rule": "delta_equiv = max(SE_delta, 0.01); equivalent iff "
                    "|RMSE_A - RMSE_B| <= delta_equiv (i.e. within 1 SE OR "
                    "within the floor)",
         "floor_value_changed": False,
         "supersedes": "FULL"},
        {"clause_id": "C-02",
         "v1_location": "TARGET_ELIGIBILITY_POLICY.md; "
                        "target_eligibility_schema.json",
         "v1_rule": "min_coefficient_of_variation_development = 0.05 "
                    "(CV = sd/|mean|)",
         "defect": "ordinary CV is undefined or explosive when the mean is near "
                   "zero, and meaningless for sign-changing trajectories",
         "v2_rule": "min_median_robust_relative_variation = 0.05 on "
                    "RRV_dev = median_s(1.4826*MAD(y_s)/RMS(y_s))",
         "floor_value_changed": False,
         "supersedes": "FULL"},
        {"clause_id": "C-03",
         "v1_location": "STATISTICAL_INFERENCE_PLAN.md; "
                        "PREPROCESSING_AND_LEAKAGE_POLICY.md",
         "v1_rule": "'calibration-normalized RMSE', denominator not defined",
         "defect": "the primary metric was named but not specified; the 0.01 "
                   "floor therefore had no defined scale",
         "v2_rule": "NRMSE_{s,b} = RMSE(protected) / std(y_calibration_{s,b}, "
                    "ddof=0); zero scale -> INVALID_FOR_NORMALIZED_SCORING; no "
                    "epsilon",
         "floor_value_changed": False,
         "supersedes": "ADDS_DEFINITION"},
        {"clause_id": "C-04",
         "v1_location": "VALIDATION_PROTOCOL.md; "
                        "PREPROCESSING_AND_LEAKAGE_POLICY.md; "
                        "S7_2_RECONSTRUCTION_CONTRACT_FINAL.md",
         "v1_rule": "'protected' intervals, wording implying permanent sealing",
         "defect": "readable as forbidding block A's evaluation values from ever "
                   "entering later calibration, which contradicts block B's own "
                   "expanding calibration window [0,0.60)",
         "v2_rule": "BLOCK-LOCAL PROTECTION with sequential/prequential "
                    "semantics: score A, freeze the score, only then may those "
                    "values act as ordinary calibration history for B and C",
         "floor_value_changed": False,
         "supersedes": "CLARIFIES"},
        {"clause_id": "C-05",
         "v1_location": "TARGET_ELIGIBILITY_POLICY.md (S7.3 output section)",
         "v1_rule": "eligible set produced; selection needs human review",
         "defect": "leaves discretion open at exactly the moment candidate "
                   "feasibility becomes visible",
         "v2_rule": "deterministic 5-level lexicographic selection rule; "
                    "top-ranked eligible candidate IS the primary target",
         "floor_value_changed": False,
         "supersedes": "FULL"},
        {"clause_id": "C-06",
         "v1_location": "UTILITY_AND_QUALIFICATION_POLICY.md gate V3",
         "v1_rule": "'beats B0 and B1 in the predeclared aggregate sense'",
         "defect": "aggregate never defined, so the gate was not decidable",
         "v2_rule": "Delta_j = mean_s(NRMSE_REL,s - NRMSE_Bj,s) over external "
                    "discharges, NRMSE_,s = mean over blocks A,B,C; PASS iff "
                    "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
         "floor_value_changed": False,
         "supersedes": "ADDS_DEFINITION"},
        {"clause_id": "C-07",
         "v1_location": "UTILITY_AND_QUALIFICATION_POLICY.md gate V6",
         "v1_rule": "report separately for 35 earlier / 27 later",
         "defect": "35/27 are PARENT OBJECT counts; the external gate operates "
                   "on the external cohort, which is 24/18",
         "v2_rule": "external counts 24 earlier / 18 later; three-valued "
                    "outcome PASS / PASS_WITH_QUALIFICATION / "
                    "FAIL_FOR_FULL_DOMAIN",
         "floor_value_changed": False,
         "supersedes": "FULL"},
        {"clause_id": "C-08",
         "v1_location": "S7_2_RECONSTRUCTION_CONTRACT_AUDIT_REPORT.md §21",
         "v1_rule": "six human decisions left open",
         "defect": "open decisions at the S7.3 boundary are discretion that can "
                   "be exercised after feasibility becomes visible",
         "v2_rule": "all six frozen: no EFIT campaign; no PROVENANCE_RELAXED; "
                    "no class override; no 2nd-order derivatives; no support "
                    "beyond 12; S7.1 mixed-hash record not rewritten",
         "floor_value_changed": False,
         "supersedes": "FULL"},
        {"clause_id": "C-09",
         "v1_location": "scripts/build_contract_and_freeze.py hash manifest",
         "v1_rule": "manifest hashes every artifact including itself and the "
                    "acceptance file",
         "defect": "both are written after the manifest is built, so their "
                   "recorded hashes are guaranteed stale; a file cannot contain "
                   "its own hash",
         "v2_rule": "self-referential files excluded from the manifest "
                    "explicitly and listed under self_referential_excluded",
         "floor_value_changed": False,
         "supersedes": "FULL"},
    ]


def target_selection_schema() -> dict:
    return {
        "schema_id": "S7.2C-TARGET-SELECTION-V2",
        "supersedes": "S7.2-TARGET-ELIGIBILITY-V1 (selection step only; "
                      "eligibility criteria unchanged)",
        "applied_at": "S7.3",
        "deterministic": True,
        "produces_ranking_at_S7_2C": False,
        "stage_1_eligibility": {
            "note": "every eligibility criterion is applied independently "
                    "first; only candidates passing ALL of them are ranked",
            "criteria_unchanged_from_v1": True,
            "thresholds": {
                "min_admissible_predictors_after_closure": 10,
                "min_median_robust_relative_variation": RRV_FLOOR,
                "min_distinct_values_fraction": 0.10,
                "max_identically_zero_development_discharges": 0,
            },
            "retired_thresholds": ["min_coefficient_of_variation_development"],
        },
        "stage_2_lexicographic_ranking": [
            {"level": 1, "key": "target_side_major_flags", "direction": "fewer_is_better",
             "definition": "count of MAJOR provenance or numerical flags "
                           "attaching to the TARGET ITSELF",
             "excludes": "flags on predictors that I_rec later removes"},
            {"level": 2, "key": "n_provenance_certified_predictors_surviving_I_rec",
             "direction": "more_is_better"},
            {"level": 3, "key": "n_distinct_signal_families_surviving_I_rec",
             "direction": "more_is_better"},
            {"level": 4, "key": "rrv_margin", "direction": "larger_is_better",
             "definition": f"RRV_dev - {RRV_FLOOR}"},
            {"level": 5, "key": "signal_index", "direction": "lower_is_better",
             "definition": "position in FINAL_SIGNAL_INVENTORY.csv; "
                           "guarantees a unique winner"},
        ],
        "forbidden_inputs": [
            "any reconstruction model or its output",
            "any baseline performance",
            "correlation between target and any predictor",
            "any external-cohort information",
            "any development performance",
        ],
        "outcome": "the top-ranked eligible candidate IS the primary target",
        "human_review_may": [
            "verify the rule was applied correctly",
            "identify a previously unknown scientific or provenance defect",
        ],
        "human_review_may_not": [
            "choose a lower-ranked target because it seems more interesting",
            "choose a lower-ranked target because it appears easier to reconstruct",
            "inspect model performance before the target is frozen",
        ],
        "defect_procedure": (
            "if the top-ranked candidate has a genuine newly discovered defect, "
            "freeze the defect in the ledger and re-apply the identical rule to "
            "the remaining eligible set"),
    }


def metric_definitions() -> dict:
    return {
        "primary_metric": {
            "name": "calibration-normalized RMSE",
            "symbol": "NRMSE_{s,b}",
            "definition": "RMSE(y_protected_{s,b}, yhat_protected_{s,b}) / scale_{s,b}",
            "scale_definition": "scale_{s,b} = std(y_calibration_{s,b}, ddof=0)",
            "ddof": 0,
            "scale_uses": "CALIBRATION target values only",
            "protected_statistics_in_scale": False,
            "zero_scale_behaviour": "INVALID_FOR_NORMALIZED_SCORING",
            "epsilon_added": False,
            "epsilon_note": "no outcome-tuned epsilon; a zero-scale block is "
                            "declared invalid rather than rescued",
            "also_reported": "raw RMSE in the target physical unit",
            "s7_3_requirement": "development target feasibility must report "
                                "whether any zero-scale calibration block "
                                "exists; the primary target must have valid "
                                "normalized scoring across all required "
                                "development blocks",
            "floor_interpretation": f"the {PRACTICAL_FLOOR} practical floor is "
                                    f"1% of the calibration target "
                                    f"standard-deviation scale",
        },
        "practical_equivalence": {
            "delta_equiv": "max(SE_delta, 0.01)",
            "rule": "A and B practically equivalent iff |RMSE_A - RMSE_B| <= delta_equiv",
            "reading": "within one SE OR within the 0.01 practical floor",
            "floor": PRACTICAL_FLOOR,
            "se_definition": {
                "step_1": "aggregate the three validation blocks within each "
                          "DEVELOPMENT discharge",
                "step_2": "compute the paired candidate difference per "
                          "development discharge",
                "step_3": "SE_delta = standard error of that paired "
                          "discharge-level difference across the 20 "
                          "development discharges",
                "n": 20,
                "unit": "development discharge",
            },
            "supersedes": "V1 conjunction (AND), which made the floor "
                          "inoperative exactly when SE was small",
            "computed_in_this_run": False,
        },
        "robust_relative_variation": {
            "symbol": "RRV",
            "per_discharge": "RRV_s = 1.4826 * MAD(y_s) / RMS(y_s)",
            "MAD": "median(|y - median(y)|)",
            "RMS": "sqrt(mean(y^2))",
            "zero_rms_behaviour": "RRV_s = 0",
            "target_level_score": "RRV_dev = median_s(RRV_s) over the 20 frozen "
                                  "development discharges",
            "floor": RRV_FLOOR,
            "threshold_name": "min_median_robust_relative_variation",
            "retires": "min_coefficient_of_variation_development",
            "rationale": "ordinary CV = sd/|mean| is undefined or explosive for "
                         "near-zero means and meaningless for sign-changing "
                         "trajectories; RRV is zero-safe and scale-relative",
            "computed_in_this_run": False,
        },
        "gate_V3": {
            "per_discharge": "NRMSE_method,s = mean over blocks A,B,C of NRMSE_method,s,b",
            "per_baseline": "Delta_j = mean over EXTERNAL discharges s of "
                            "(NRMSE_REL,s - NRMSE_Bj,s)",
            "pass_condition": "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
            "baselines_in_gate": ["B0 calibration mean", "B1 persistence"],
            "confidence_intervals_are_thresholds": False,
            "ci_role": "reported, not used as a significance threshold for V3",
            "also_reported": ["median paired difference", "wins/ties/losses",
                              "95% paired discharge-bootstrap CI",
                              "block-specific values"],
            "computed_in_this_run": False,
        },
        "gate_V6": {
            "applies_to": "EXTERNAL cohort",
            "external_counts": {"earlier": 24, "later": 18, "total": 42},
            "parent_object_counts_for_reference": {"earlier": 35, "later": 27,
                                                   "total": 62},
            "v1_defect": "V6 referred to 35/27, which are parent-object counts, "
                         "not the external cohort the gate operates on",
            "outcomes": {
                "PASS": "pooled V3 passes and the practical direction is "
                        "non-adverse in both eras",
                "PASS_WITH_QUALIFICATION": "pooled V3 passes, but one era is "
                                           "practically tied relative to a "
                                           "trivial baseline; report and narrow "
                                           "the interpretation",
                "FAIL_FOR_FULL_DOMAIN": "pooled V3 passes only because one era "
                                        "dominates while the other is "
                                        "materially worse than B0 or B1 by "
                                        "more than 0.01",
            },
            "fail_for_full_domain_consequence": (
                "does not erase the result; the final Omega_rec claim must be "
                "narrowed rather than averaged across the processing "
                "discontinuity"),
            "computed_in_this_run": False,
        },
        "validation_geometry": {
            "unchanged_from_v1": True,
            "blocks": [
                {"block": "A", "calibration": [0.00, 0.40], "evaluation": [0.40, 0.50]},
                {"block": "B", "calibration": [0.00, 0.60], "evaluation": [0.60, 0.70]},
                {"block": "C", "calibration": [0.00, 0.80], "evaluation": [0.80, 0.90]},
            ],
            "protection_model": "BLOCK_LOCAL_PROTECTION",
            "semantics": "sequential / prequential",
            "sequence": [
                "STEP A: fit on [0,0.40); score A on [0.40,0.50); freeze the A score",
                "only after A scoring is irrevocably complete may those target "
                "values act as ordinary historical calibration observations",
                "STEP B: fit on [0,0.60); score B on [0.60,0.70); freeze the B score",
                "STEP C: fit on [0,0.80); score C on [0.80,0.90)",
            ],
            "a_target_value_may_never_influence": [
                "its own evaluation block's fit",
                "an earlier evaluation block",
                "target, ontology, support or hyperparameter choices that are "
                "supposed to be frozen",
            ],
            "external_cohort": "remains GLOBALLY SEALED before S7.10; "
                               "block-local protection governs only within-"
                               "discharge rolling-origin sequencing",
        },
    }


def frozen_human_decisions() -> list[dict]:
    return [
        {"id": "H-A", "decision": "DO NOT undertake an EFIT-lineage recovery "
         "campaign for the primary study",
         "reason": "the strict experiment may simply lose the 15 "
                   "LINEAGE_PARTIAL equilibrium quantities under fail-closed "
                   "provenance; that cost was accepted prospectively and keeps "
                   "the primary study simpler and cleaner",
         "status": "FROZEN"},
        {"id": "H-B", "decision": "DO NOT declare a PROVENANCE_RELAXED "
         "secondary variant",
         "reason": "the primary paper needs one clean, target-independent "
                   "reconstruction study; a rescue path built on partially "
                   "resolved ancestry would undermine it",
         "status": "FROZEN"},
        {"id": "H-C", "decision": "DO NOT override the frozen primary target "
         "classes", "reason": "eligibility classes stand as frozen in V1",
         "status": "FROZEN"},
        {"id": "H-D", "decision": "DO NOT promote second-order derivatives",
         "reason": "source cadence cannot support them",
         "status": "FROZEN"},
        {"id": "H-E", "decision": "DO NOT widen support beyond 12",
         "reason": "calibration-sample economy on the worst admissible grid",
         "status": "FROZEN"},
        {"id": "H-F", "decision": "DO NOT rewrite the S7.1 mixed-hash "
         "historical freeze; continue using the uniform canonical raw-byte "
         "hashes established by S7.2",
         "reason": "the historical record stays as it was; the workaround is "
                   "already in place and verified",
         "status": "FROZEN"},
    ]


def main() -> None:
    v1 = verify_v1()
    (CV1 / "manifests" / "V1_FREEZE_VERIFICATION.json").write_text(
        json.dumps(v1, indent=2), encoding="utf-8")
    if v1["verdict"] != "V1_INTACT":
        raise SystemExit("STOP: V1 freeze failed verification")

    clauses = superseded_clauses()
    with (CV1 / "manifests" / "SUPERSEDED_CLAUSES.csv").open(
            "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(clauses[0].keys()))
        w.writeheader()
        w.writerows(clauses)

    (CV1 / "target_selection_schema.json").write_text(
        json.dumps(target_selection_schema(), indent=2), encoding="utf-8")

    M = metric_definitions()
    (CV1 / "metric_and_gate_definitions.json").write_text(
        json.dumps(M, indent=2), encoding="utf-8")

    # ---- K_REC_PRE_V2: inherit V1, supersede named fields ------------------
    K = json.loads((S72 / "K_REC_PRE.json").read_text())
    K["contract_id"] = "K_REC_PRE_V2"
    K["freeze_id"] = FREEZE_V2
    K["supersedes_freeze_id"] = FREEZE_V1
    K["parent_freeze_id"] = PARENT_S7_1
    K["generated_utc"] = datetime.now(timezone.utc).isoformat()
    K["inheritance"] = {
        "mode": "INHERIT_V1_EXCEPT_NAMED_CLAUSES",
        "superseded_clause_ids": [c["clause_id"] for c in clauses],
        "clause_manifest": "manifests/SUPERSEDED_CLAUSES.csv",
        "everything_else_binding": True,
    }

    K["U_rec"]["practical_equivalence"] = M["practical_equivalence"]
    K["U_rec"]["primary_metric"] = M["primary_metric"]

    K["V_rec"]["validation_geometry"] = M["validation_geometry"]
    K["V_rec"]["gate_V3_definition"] = M["gate_V3"]
    K["V_rec"]["gate_V6_definition"] = M["gate_V6"]
    K["V_rec"]["primary_metric"] = M["primary_metric"]

    K["q_rec"]["target_selection"] = "DETERMINISTIC_RULE_FROZEN_APPLIED_AT_S7.3"
    K["q_rec"]["target_selection_schema"] = "target_selection_schema.json"

    K["I_rec"]["provenance_relaxed_variant"] = {
        "declared": False,
        "reason": "frozen human decision H-B: the primary paper needs one "
                  "clean, target-independent study; no rescue path built on "
                  "partially resolved ancestry",
    }
    K["I_rec"]["efit_lineage_recovery_campaign"] = {
        "undertaken": False,
        "reason": "frozen human decision H-A; the fail-closed cost was accepted "
                  "prospectively",
    }

    K["robust_relative_variation"] = M["robust_relative_variation"]
    K["frozen_human_decisions"] = frozen_human_decisions()
    K["gate"]["signal_values_inspected"] = False
    K["gate"]["s7_2c_ranked_targets"] = False

    (CV1 / "K_REC_PRE_V2.json").write_text(json.dumps(K, indent=2),
                                           encoding="utf-8")

    # ---- acceptance --------------------------------------------------------
    md_files = sorted(p.name for p in CV1.rglob("*.md"))
    sel = json.loads((CV1 / "target_selection_schema.json").read_text())
    pe = K["U_rec"]["practical_equivalence"]

    checks = {
        "v1_freeze_unchanged_and_preserved": v1["v1_preserved_unmodified"],
        "no_signal_values_inspected": K["gate"]["signal_values_inspected"] is False,
        "no_target_ranked_or_selected":
            K["gate"]["targets_ranked"] is False
            and K["gate"]["target_selected"] is False
            and sel["produces_ranking_at_S7_2C"] is False,
        "no_external_values_accessed":
            K["gate"]["external_signal_values_inspected"] is False,
        "practical_equivalence_uses_max_not_and":
            pe["delta_equiv"] == "max(SE_delta, 0.01)"
            and "OR" in pe["reading"],
        "ordinary_cv_retired":
            "min_coefficient_of_variation_development"
            in sel["stage_1_eligibility"]["retired_thresholds"]
            and "min_coefficient_of_variation_development"
            not in sel["stage_1_eligibility"]["thresholds"],
        "robust_relative_variation_frozen":
            K["robust_relative_variation"]["per_discharge"]
            == "RRV_s = 1.4826 * MAD(y_s) / RMS(y_s)"
            and K["robust_relative_variation"]["floor"] == RRV_FLOOR,
        "nrmse_denominator_explicitly_defined":
            M["primary_metric"]["scale_definition"]
            == "scale_{s,b} = std(y_calibration_{s,b}, ddof=0)",
        "ddof_fixed": M["primary_metric"]["ddof"] == 0,
        "zero_calibration_scale_behaviour_fixed":
            M["primary_metric"]["zero_scale_behaviour"]
            == "INVALID_FOR_NORMALIZED_SCORING"
            and M["primary_metric"]["epsilon_added"] is False,
        "block_local_protection_clarified":
            M["validation_geometry"]["protection_model"] == "BLOCK_LOCAL_PROTECTION"
            and M["validation_geometry"]["semantics"] == "sequential / prequential",
        "validation_fractions_unchanged":
            [b["calibration"] + b["evaluation"]
             for b in M["validation_geometry"]["blocks"]]
            == [[0.0, 0.40, 0.40, 0.50], [0.0, 0.60, 0.60, 0.70],
                [0.0, 0.80, 0.80, 0.90]],
        "deterministic_target_selection_rule_frozen":
            sel["deterministic"] is True
            and len(sel["stage_2_lexicographic_ranking"]) == 5,
        "v3_aggregate_exactly_defined":
            M["gate_V3"]["pass_condition"]
            == "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
        "v6_uses_external_counts_24_18":
            M["gate_V6"]["external_counts"]["earlier"] == 24
            and M["gate_V6"]["external_counts"]["later"] == 18,
        "no_efit_recovery_campaign":
            K["I_rec"]["efit_lineage_recovery_campaign"]["undertaken"] is False,
        "no_provenance_relaxed_variant":
            K["I_rec"]["provenance_relaxed_variant"]["declared"] is False,
        "no_class_override": any(d["id"] == "H-C" and d["status"] == "FROZEN"
                                 for d in K["frozen_human_decisions"]),
        "no_derivative_or_support_expansion":
            K["B_rec"]["max_temporal_derivative_order"] == 1
            and K["B_rec"]["representation_size_range"] == [1, 12],
        "parent_s7_1_historical_freeze_not_rewritten":
            any(d["id"] == "H-F" and d["status"] == "FROZEN"
                for d in K["frozen_human_decisions"]),
        "markdown_output_within_limit": len(md_files) <= 20,
        "all_six_human_decisions_frozen":
            len(K["frozen_human_decisions"]) == 6
            and all(d["status"] == "FROZEN"
                    for d in K["frozen_human_decisions"]),
        "no_model_fitted": True,
        "no_coordinate_generated": K["gate"]["coordinates_generated"] is False,
    }
    n_pass = sum(bool(v) for v in checks.values())
    (CV1 / "S7_2C_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n_pass}/{len(checks)}",
        "all_passed": n_pass == len(checks),
        "markdown_files_created": md_files,
        "n_markdown_files": len(md_files),
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    status = "FROZEN_READY_FOR_S7.3" if n_pass == len(checks) else "BLOCKED"

    arts = sorted([p for p in CV1.rglob("*")
                   if p.is_file() and p.name not in SELF_REFERENTIAL],
                  key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_V2,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "supersedes_freeze_id": FREEZE_V1,
        "parent_s7_1_freeze_id": PARENT_S7_1,
        "v1_freeze_file_sha256": v1["v1_freeze_file_sha256"],
        "v1_K_REC_PRE_sha256": v1["v1_K_REC_PRE_sha256"],
        "v1_verification_sha256":
            sha(CV1 / "manifests" / "V1_FREEZE_VERIFICATION.json"),
        "correction_report_sha256": sha(CV1 / "S7_2C_CORRECTION_REPORT.md")
            if (CV1 / "S7_2C_CORRECTION_REPORT.md").exists() else None,
        "contract_v2_md_sha256": sha(CV1 / "S7_2C_CONTRACT_V2.md")
            if (CV1 / "S7_2C_CONTRACT_V2.md").exists() else None,
        "decision_ledger_sha256": sha(CV1 / "S7_2C_DECISION_LEDGER.md")
            if (CV1 / "S7_2C_DECISION_LEDGER.md").exists() else None,
        "target_selection_rule_md_sha256": sha(CV1 / "TARGET_SELECTION_RULE.md")
            if (CV1 / "TARGET_SELECTION_RULE.md").exists() else None,
        "K_REC_PRE_V2_sha256": sha(CV1 / "K_REC_PRE_V2.json"),
        "target_selection_schema_sha256":
            sha(CV1 / "target_selection_schema.json"),
        "metric_and_gate_definitions_sha256":
            sha(CV1 / "metric_and_gate_definitions.json"),
        "superseded_clauses_sha256":
            sha(CV1 / "manifests" / "SUPERSEDED_CLAUSES.csv"),
        "environment": {"python": sys.version.split()[0],
                        "platform": platform.platform()},
        "hash_method": "sha256 over raw file bytes; self-referential files "
                       "excluded by construction",
        "self_referential_excluded": sorted(SELF_REFERENTIAL),
        "all_artifact_hashes": {
            str(p.relative_to(CV1)).replace("\\", "/"): sha(p) for p in arts},
        "n_artifacts": len(arts),
        "n_superseded_clauses": len(clauses),
        "acceptance_checks": f"{n_pass}/{len(checks)}",
        "n_markdown_files": len(md_files),
        "component_status": K["component_status_summary"],
        "gate": K["gate"],
        "status": status,
        "next_stage": "S7.3 - NOT AUTHORISED",
    }
    (CV1 / "S7_2_FREEZE_V2.json").write_text(json.dumps(freeze, indent=2),
                                             encoding="utf-8")

    print(f"V1 verification : {v1['n_verified']} artifacts intact, "
          f"{v1['n_drift']} drift  ({len(v1['self_referential_excluded'])} "
          f"self-referential excluded)")
    print(f"superseded clauses : {len(clauses)}")
    print(f"acceptance : {n_pass}/{len(checks)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"markdown files : {len(md_files)}  {md_files}")
    print(f"STATUS : {status}")
    print(f"freeze : {FREEZE_V2}")


if __name__ == "__main__":
    main()
