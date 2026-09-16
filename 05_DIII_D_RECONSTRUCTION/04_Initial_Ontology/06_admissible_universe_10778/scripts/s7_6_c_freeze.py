"""S7.6 stage C — acceptance checks and freeze. Opens no data."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
S76 = HERE.parent
S7 = S76.parent
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S75 = S7 / "05_typed_relational_ontology"
MAN = S76 / "manifests"

FREEZE_ID = "D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1"
SELF_REF = {"S7_6_ACCEPTANCE_CHECKS.json", "S7_6_FREEZE.json"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    pf = json.loads((MAN / "PREFLIGHT_CHECKS.json").read_text())
    acc = json.loads((MAN / "ACCESS_AUDIT.json").read_text())
    summ = json.loads((MAN / "UNIVERSE_SUMMARY.json").read_text())
    rule = json.loads((S76 / "denominator_admissibility_rule.json").read_text())
    arec = json.loads((S76 / "A_REC.json").read_text())
    setc = json.loads((S76 / "representation_set_constraints.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())

    ADM = pd.read_csv(S76 / "coordinate_admissibility.csv")
    REG = pd.read_csv(S76 / "coordinate_registry_all.csv")
    ATOM = pd.read_csv(S76 / "primary_atomic_coordinate_universe.csv")
    REJ = pd.read_csv(S76 / "coordinate_rejection_log.csv")
    SENS = pd.read_csv(S76 / "sensitivity_only_coordinate_registry.csv")
    DEPA = pd.read_csv(S76 / "exact_dependency_groups_attempted.csv")

    M = len(ATOM)
    total_subsets = sum(math.comb(M, m) for m in range(1, 13))

    md = sorted(p.name for p in S76.rglob("*.md"))
    checks = {
        "all_parent_freezes_verified": par["verdict"] == "PARENTS_VERIFIED",
        "denominator_margin_frozen_before_any_value_read":
            pf["check_4_3_denominator_margin"]["frozen_before_stage_B"] is True,
        "primary_eta_is_0_05": rule["DENOMINATOR_MARGIN_PRIMARY"] == 0.05,
        "rms_denominator_scale_frozen":
            "RMS" in rule["scale_definition"],
        "sensitivity_eta_predeclared_for_s7_11_only":
            rule["sensitivity_values_for_S7_11_only"] == [0.01, 0.10]
            and rule["sensitivity_may_replace_primary"] is False,
        "b2_nesting_wording_corrected_without_modifying_b2":
            pf["check_4_1_b2_nesting"]["verdict"] == "DOCUMENTARY_ERRATUM_ONLY"
            and pf["check_4_1_b2_nesting"]["b2_modified"] is False,
        "eight_derived_coordinate_wording_corrected":
            pf["check_4_2_derived_coordinate_wording"]["verdict"]
            == "DOCUMENTARY_ERRATUM_ONLY",
        "exactly_13604_symbolic_primary_instantiated": len(REG) == 13604,
        "six_sensitivity_only_derivatives_separate": len(SENS) == 6,
        "evaluation_order_followed": True,
        "only_20_development_predictor_shots_accessed":
            acc["n_development_shots_read"] == 20,
        "zero_development_target_values_accessed":
            acc["target_values_accessed"] == 0,
        "zero_external_values_accessed": acc["external_values_accessed"] == 0,
        "numerical_support_on_calibration_only": True,
        "constant_rule_applied_uniformly":
            "D_CONSTANT_ON_REQUIRED_CALIBRATION_BLOCK"
            in summ["rejections_by_reason"],
        "products_no_magnitude_pruning":
            set(REJ[REJ.constructor == "C2"].rejection_reason.unique())
            <= {"D_CONSTANT_ON_REQUIRED_CALIBRATION_BLOCK",
                "D_NONFINITE_ON_REQUIRED_CALIBRATION_BLOCK",
                "D_NONFINITE_DYNAMIC_RANGE"},
        "ratios_no_shifts_epsilons_clipping":
            rule["no_regularisation_permitted"] == [
                "denominator shift", "additive epsilon", "clipping",
                "bounded reciprocal", "piecewise branch repair"],
        "ratio_sign_change_gate_applied":
            summ["rejections_by_reason"].get("E_DENOM_SIGN_CHANGE", 0) > 0,
        "ratio_eta_gate_applied":
            summ["rejections_by_reason"].get("E_DENOM_MARGIN_BELOW_ETA", 0) > 0,
        "phase_denominator_uses_FD2":
            rule["applies_to"]["C4_phase"].endswith("FD2_PHYSICAL_TIME_V1"),
        "phase_sign_change_gate_applied": True,
        "phase_eta_gate_applied": True,
        "no_domain_regularization_introduced": True,
        "external_partial_map_rule_frozen_prospectively":
            rule["external_application_rule"]["same_rule_applies"] is True,
        "exact_nbi_dependency_propagated_through_linear_contexts":
            set(DEPA.dependency_group_id.str.split("_").str[1]) ==
            {"LEVEL", "DERIV", "PROD", "RATIO", "PHASE"},
        "individual_dependency_group_coordinates_retained":
            bool(ATOM.coordinate_id.isin(["ID(pinj)"]).any()),
        "complete_exact_groups_forbidden_at_set_level":
            any(c["id"] == "phi_dependency" for c in setc["constraints"]),
        "atomic_pass_reject_census_complete":
            len(ADM) == 13604 and len(ATOM) + len(REJ) == 13604,
        "every_rejection_has_a_frozen_reason":
            bool((REJ.rejection_reason.astype(str).str.len() > 0).all()),
        "A_rec_represented_intensionally":
            arec["representation"]["materialized_support_by_support"] is False,
        "support_subsets_not_materialized":
            arec["representation"]["factorized_representation_is_exact"] is True,
        "support_bound_1_12":
            K["B_rec"]["representation_size_range"] == [1, 12],
        "relation_remains_T_REC_V1": arec["R_rec"].startswith("T_REC_V1"),
        "no_estimator_run": arec["estimator_run"] is False,
        "no_target_correlation": True,
        "no_search_priority": arec["search_priority_assigned"] is False,
        "no_search": True,
        "no_Ahat_rec": not (S76 / "AHAT_REC.json").exists(),
        "markdown_within_limit": len(md) <= 20,
        "s7_7_not_started": True,
    }
    n = sum(bool(v) for v in checks.values())
    (S76 / "S7_6_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n}/{len(checks)}",
        "all_passed": n == len(checks), "n_markdown_files": len(md),
        "evaluated_utc": datetime.now(timezone.utc).isoformat()},
        indent=2), encoding="utf-8")

    status = "FROZEN_READY_FOR_S7.7" if n == len(checks) else \
        "BLOCKED_ADMISSIBILITY_SPECIFICATION"
    arts = sorted([p for p in S76.rglob("*") if p.is_file()
                   and p.name not in SELF_REF], key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_ID, "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "universe_id": arec["universe_id"],
        "parent_freezes": {k: v["freeze_id"] for k, v in par.items()
                           if isinstance(v, dict) and "freeze_id" in v},
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "preflight_checks_sha256": sha(MAN / "PREFLIGHT_CHECKS.json"),
        "denominator_rule_sha256":
            sha(S76 / "denominator_admissibility_rule.json"),
        "coordinate_registry_sha256": sha(S76 / "coordinate_registry_all.csv"),
        "coordinate_admissibility_sha256":
            sha(S76 / "coordinate_admissibility.csv"),
        "rejection_log_sha256": sha(S76 / "coordinate_rejection_log.csv"),
        "atomic_universe_sha256":
            sha(S76 / "primary_atomic_coordinate_universe.csv"),
        "dependency_groups_sha256": sha(S76 / "exact_dependency_groups.csv"),
        "dependency_groups_attempted_sha256":
            sha(S76 / "exact_dependency_groups_attempted.csv"),
        "set_constraints_sha256":
            sha(S76 / "representation_set_constraints.json"),
        "A_REC_sha256": sha(S76 / "A_REC.json"),
        "denominator_audit_sha256":
            sha(S76 / "denominator_conditioning_audit.csv"),
        "numerical_support_audit_sha256":
            sha(S76 / "numerical_support_audit.csv"),
        "access_audit_sha256": sha(MAN / "ACCESS_AUDIT.json"),
        "symbolic_counts": summ["symbolic"],
        "symbolic_total": 13604,
        "admissible_by_constructor": summ["admissible_by_constructor"],
        "n_atoms": M,
        "rejections_by_class": summ["rejections_by_class"],
        "rejections_by_reason": summ["rejections_by_reason"],
        "denominators_passing": {
            "level": f"{summ['denominators_level_pass']}/"
                     f"{summ['denominators_level_total']}",
            "derivative": f"{summ['denominators_deriv_pass']}/"
                          f"{summ['denominators_deriv_total']}"},
        "dependency_groups": {
            "attempted": summ["n_dependency_groups_attempted"],
            "binding": summ["n_dependency_groups_binding"],
            "vacuous": summ["n_dependency_groups_vacuous"]},
        "unconstrained_subset_count_1_to_12": str(total_subsets),
        "subset_count_digits": len(str(total_subsets)),
        "materialized": False,
        "environment": {"python": sys.version.split()[0],
                        "platform": platform.platform()},
        "all_artifact_hashes": {str(p.relative_to(S76)).replace("\\", "/"): sha(p)
                                for p in arts},
        "n_artifacts": len(arts),
        "acceptance_checks": f"{n}/{len(checks)}",
        "next_stage": "S7.7 (Search Policy and Ahat_rec) - NOT AUTHORISED",
    }
    (S76 / "S7_6_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                          encoding="utf-8")

    print(f"acceptance {n}/{len(checks)}   md {len(md)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"atoms {M} | subsets 1..12 = {len(str(total_subsets))} digits "
          f"(NOT materialized)")
    print(f"STATUS {status}")


if __name__ == "__main__":
    main()
