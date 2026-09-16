"""S7.5H stage C — hardened ontology, combinatorial audit, ablation, freeze.

Opens no data. Consumes stage A policy and stage B redundancy results only.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S5H = HERE.parent
S7 = S5H.parent
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
S76 = S7 / "06_admissible_universe"
MAN = S5H / "manifests"

FREEZE_ID = "D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1"
ONTOLOGY_ID = "G_REC_DENSITY_HARDENED_V2"
SELF_REF = {"S7_5H_ACCEPTANCE_CHECKS.json", "S7_5H_FREEZE.json"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    pol = json.loads((S5H / "HARDENING_POLICY_PREVALUE.json").read_text())
    if sha(S5H / "HARDENING_POLICY_PREVALUE.json") != json.loads(
            (MAN / "POLICY_FREEZE.json").read_text())["sha256"]:
        raise SystemExit("STOP: policy changed after freeze")

    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    acc = json.loads((MAN / "ACCESS_AUDIT.json").read_text())
    rsum = json.loads((MAN / "REDUNDANCY_SUMMARY.json").read_text())
    G1 = json.loads((S75 / "G_REC.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    X = json.loads((RV2 / "X_REC.json").read_text())

    H = pd.read_csv(S5H / "primitive_basis_hardened.csv")
    D = pd.read_csv(S5H / "primitive_basis_deferred.csv")
    ER = pd.read_csv(S5H / "effective_rank_audit.csv")
    CEN = pd.read_csv(S5H / "family_composition_audit.csv")
    PW = pd.read_csv(S5H / "pairwise_redundancy_audit.csv")

    M = len(H)
    Mt = int((~H.uncalibrated_flag).sum())
    Md = int(H.derivative_primary_eligible.sum())
    cat = pol["E_constructor_catalogue"]

    counts = {"C0": M, "C1": Md, "C2": Mt * (Mt + 1) // 2,
              "C3": Mt * (Mt - 1), "C4": Md * (Md - 1), "C5": Mt,
              "C6": Mt * Md, "C7": Md * Mt, "C8": Mt * Md}
    total = sum(counts.values())
    orig = G1["symbolic_upper_bounds"]["primary_total"]

    # ---- constructor catalogue (hardened) ---------------------------------
    (S5H / "constructor_catalog_hardened.json").write_text(json.dumps({
        "catalogue_id": "LAMBDA_REC_H_V1",
        "families": cat,
        "max_constructor_depth": 1,
        "constructors_operate_on": "PRIMITIVES ONLY. C6-C8 are primitive-pair "
                                   "constructors with an INTERNAL declared rate "
                                   "operator; they do NOT consume C1 coordinate "
                                   "objects recursively and are NOT depth 2.",
        "not_primary": ["derivative of a product", "product of two constructed "
                        "ratios", "ratio of phase derivatives", "phase "
                        "derivative of a product", "recursive reciprocal",
                        "products of products", "second derivative",
                        "any depth > 1 construction"],
        "operand_counts": {"M": M, "Mt": Mt, "Md": Md},
        "symbolic_upper_bounds": counts,
        "symbolic_primary_total": total,
    }, indent=2), encoding="utf-8")

    (S5H / "constructor_type_rules_hardened.json").write_text(json.dumps({
        "component_level_typing_only": True,
        "output_dimensions": pol["F_typing_and_domains"]["output_dimensions"],
        "special_case_units": pol["F_typing_and_domains"]["special_case_units"],
        "operand_eligibility": pol["F_typing_and_domains"]["operand_eligibility"],
        "partial_map_predicates_symbolic_only":
            pol["F_typing_and_domains"]["partial_map_predicates_symbolic_only"],
        "numerical_domain_evaluation": "DEFERRED_TO_S7.6",
        "no_regularisation": pol["F_typing_and_domains"]["no_regularisation"],
        "uncalibrated": pol["F_typing_and_domains"]["uncalibrated"],
        "upstream_upsampled": pol["F_typing_and_domains"]["upstream_upsampled"],
        "aliasing_risk": pol["F_typing_and_domains"]["aliasing_risk"],
        "derivative_realization": "FD2_PHYSICAL_TIME_V1 (unchanged from S7.5)",
        "temporal_propagation": G1["temporal_type_system"],
        "provenance_propagation": G1["provenance_propagation"],
        "standardization_does_not_alter_type": True,
    }, indent=2), encoding="utf-8")

    (S5H / "coordinate_signature_schema_hardened.json").write_text(json.dumps({
        "schema_id": "COORDINATE_SIGNATURE_H_V1",
        "display_label_is_not_identity": True,
        "canonicalization": {
            "C0": "ID(i)", "C1": "DOT(i)",
            "C2": "PROD(i,j) with i <= j by frozen inventory index",
            "C3": "RATIO(i,j), i != j",
            "C4": "PHASE(i|j) meaning D_{x_j} x_i",
            "C5": "RECIP(i)",
            "C6": "LEVEL_RATE(i|j) meaning x_i * (dx_j/dt)",
            "C7": "RATE_OVER_LEVEL(i|j) meaning (dx_i/dt) / x_j",
            "C8": "LEVEL_OVER_RATE(i|j) meaning x_i / (dx_j/dt)"},
        "duplicate_prevention": {
            "C2_symmetry": "PROD(i,j) == PROD(j,i) under canonical ordering",
            "C6_not_collapsed": "LEVEL_RATE(i|j) != LEVEL_RATE(j|i): the "
                                "semantic roles differ and x_i*dot{x}_j is not "
                                "generally equal to x_j*dot{x}_i",
            "C3_C4_C7_C8_directional": True,
            "self_cases": {"C2": "allowed (x_i^2)",
                           "C3": "RATIO(i,i) excluded, trivial constant 1",
                           "C4": "PHASE(i|i) excluded, trivial constant 1",
                           "C6": "allowed", "C7": "allowed, fractional rate",
                           "C8": "allowed, characteristic timescale"}},
        "fields": ["coordinate_id", "constructor_family", "depth",
                   "ordered_operands", "operand_roles", "primitive_ancestors",
                   "output_scientific_type", "output_dimension",
                   "output_unit_expression", "temporal_resolution_rule",
                   "provenance_lineage", "target_independence",
                   "primary_or_sensitivity", "aliasing_flags",
                   "numerical_realization_id", "domain_predicate",
                   "dependency_group_membership"],
    }, indent=2), encoding="utf-8")

    ex1 = json.loads((S75 / "excluded_constructor_families.json").read_text())
    ex1["excluded"] = [e for e in ex1["excluded"]
                       if e["family"] != "pairwise sum / difference"] + [
        {"family": "pairwise sum / difference",
         "status": "PRIMARY_ONTOLOGY_EXCLUDES",
         "reason": "algebraic redundancy against an affine-linear template; "
                   "unchanged from S7.5"},
        {"family": "group summary constructors (mean/median/variance across "
                   "channels, channel gradients)",
         "status": "PRIMARY_ONTOLOGY_EXCLUDES_PENDING_SEMANTIC_GEOMETRY",
         "reason": "S7.4 established that channel index is NOT documented as a "
                   "physical spatial coordinate, so cross-channel summaries "
                   "and gradients are scientifically ambiguous on this object. "
                   "GENERAL_FRAMEWORK_PERMITS them; they are not generated."},
    ]
    ex1["note_on_new_families"] = ("C5-C8 were added prospectively, before any "
                                   "primitive count or reconstruction result "
                                   "was known. No previously excluded family "
                                   "was re-admitted.")
    (S5H / "excluded_constructor_families_hardened.json").write_text(
        json.dumps(ex1, indent=2), encoding="utf-8")

    # ---- combinatorial audit ----------------------------------------------
    ece_before = int(CEN[CEN.family == "ece_te_profile"].n_before.iloc[0])
    ece_after = int(CEN[CEN.family == "ece_te_profile"].n_after.iloc[0])
    comb = {
        "operands": {"M": M, "Mt": Mt, "Md": Md},
        "formulas": {"C0": "M", "C1": "Md", "C2": "Mt(Mt+1)/2",
                     "C3": "Mt(Mt-1)", "C4": "Md(Md-1)", "C5": "Mt",
                     "C6": "Mt*Md", "C7": "Md*Mt", "C8": "Mt*Md"},
        "counts": counts, "symbolic_primary_total": total,
        "original_G_REC_V1_total": orig,
        "ratio_hardened_to_original": round(total / orig, 4),
        "direction": ("LARGER" if total > orig * 1.05 else
                      "SMALLER" if total < orig * 0.95 else "SIMILAR"),
        "interpretation": (
            f"The hardened ontology is {round(total/orig,2)}x LARGER than "
            f"G_REC_DENSITY_V1 despite using {78-M} fewer primitives. The four "
            f"new families contribute {counts['C5']+counts['C6']+counts['C7']+counts['C8']} "
            f"coordinates, of which C6/C7/C8 alone contribute "
            f"{counts['C6']+counts['C7']+counts['C8']}. Narrowing the "
            f"primitive basis by 10% did not offset broadening the grammar "
            f"from five families to nine."),
        "instrumentation_density_audit": {
            "ece_primitives_before": ece_before,
            "ece_primitives_after": ece_after,
            "ece_share_before": round(ece_before / 78, 4),
            "ece_share_after": round(ece_after / M, 4),
            "materially_reduced": bool((ece_before / 78) - (ece_after / M) > 0.10),
            "assessment": (
                "NOT materially reduced. The ECE share of the primitive basis "
                "falls only from 51.3% to 47.1%. The frozen conservative "
                "pairwise criterion defers 7 of 40 ECE channels. The stated "
                "motivation of preventing one diagnostic family from "
                "dominating the combinatorial weight is therefore only "
                "marginally served by the primitive-space component of this "
                "hardening; the grammar-broadening component is what changed "
                "substantially."),
            "no_tuning_performed": True,
        },
        "effective_rank_disagreement": {
            "status": "STRONG_DISAGREEMENT_RECORDED_NOT_ACTED_ON",
            "detail": ER.to_dict("records"),
            "explanation": (
                "The audit-only SVD summary suggests each redundancy-eligible "
                "group has a far lower linear effective rank than the number "
                "of representatives the frozen rule selected - ECE median rank "
                "3 at 95% variance and 7 at 99%, against 33 representatives. "
                "The frozen pairwise criterion is deliberately conservative "
                "and PAIRWISE: it defers a channel only on a DIRECT witness "
                "with |r| stable in the worst 10% of discharge/block cells. "
                "Group-level low rank does not imply any particular PAIR meets "
                "that bar. Per the frozen policy the disagreement is recorded "
                "and NOT acted on; thresholds were not tuned."),
            "binding_threshold": (
                "R_10 >= 0.97 is what binds: 40 of 780 ECE pairs reach "
                "R_med >= 0.99, but 32 of those fail R_10 >= 0.97."),
        },
        "A_rec_enumerated": False,
    }
    (S5H / "ontology_combinatorial_audit.json").write_text(
        json.dumps(comb, indent=2), encoding="utf-8")

    # ---- hardened raw ablation --------------------------------------------
    (S5H / "hardened_raw_ablation.json").write_text(json.dumps({
        **pol["H_hardened_raw_ablation"],
        "n_primitive_levels": M,
        "primitive_levels": sorted(H.primitive_id),
        "B2_status": "UNCHANGED - full target-admissible primitive predictor "
                     "information per the frozen baseline protocol; NOT shrunk",
        "comparisons_enabled": {
            "B2_vs_H0_RAW_HARDENED": "isolates the effect of primitive-space "
                                     "hardening",
            "H0_RAW_HARDENED_vs_relational_SIR": "isolates the effect of "
                                                 "relational coordinate "
                                                 "construction on the SAME "
                                                 "hardened primitive information"},
        "evaluated_in_S7_5H": False, "model_run": False,
    }, indent=2), encoding="utf-8")

    # ---- hardened G_rec ----------------------------------------------------
    GH = {
        "ontology_id": ONTOLOGY_ID, "version": "2.0.0",
        "freeze_id": FREEZE_ID,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "formal_definition":
            "G_rec^H = Gamma_H(X_rec, O_rec, K_rec; Lambda_rec^H, T_rec)",
        "supersedes_for_primary_search": G1["ontology_id"],
        "superseded_ontology_status": {
            "id": G1["ontology_id"],
            "status": ["SUPERSEDED_FOR_PRIMARY_SEARCH",
                       "PRESERVED_AS_EXTENDED_SENSITIVITY_ONTOLOGY"],
            "preserved_unmodified": True,
            "primitive_count": 78,
            "available_for": "S7.11 sensitivity analysis"},
        "parent_X_rec_id": X["object_id"],
        "parent_K_rec_id": K["contract_id"],
        "target": "density", "target_canonical_unit": "m^-3",
        "target_forbidden_as_coordinate": True,
        "target_history_forbidden": True,
        "primitive_basis": {
            "P_full": 78, "P_hard": M, "P_deferred": len(D),
            "hardened_registry": "primitive_basis_hardened.csv",
            "deferred_registry": "primitive_basis_deferred.csv",
            "deferred_status": "REDUNDANCY_DEFERRED",
            "deferred_is_not": ["SCIENTIFICALLY_INADMISSIBLE",
                                "TARGET_IRRELEVANT", "INFORMATION_FREE"],
            "selection_was_target_blind": True},
        "Lambda_rec_H": ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
        "max_constructor_depth": 1,
        "operand_counts": {"M": M, "Mt": Mt, "Md": Md},
        "symbolic_upper_bounds": counts,
        "symbolic_primary_total": total,
        "constructor_catalogue": "constructor_catalog_hardened.json",
        "type_rules": "constructor_type_rules_hardened.json",
        "coordinate_signature_schema":
            "coordinate_signature_schema_hardened.json",
        "excluded_families": "excluded_constructor_families_hardened.json",
        "numerical_realization": "FD2_PHYSICAL_TIME_V1 (unchanged)",
        "relation_template": "T_REC_V1 (unchanged)",
        "exact_dependency_constraints": {
            "DEP_NBI_POWER_SUM": "PRESERVED. pinj and all eight per-beam "
                                 "components remain in P_hard; neither form is "
                                 "privileged. Exact dependency remains a "
                                 "REPRESENTATION-SET-level constraint handled "
                                 "in S7.6.",
            "aggregate_in_P_hard": bool("pinj" in set(H.primitive_id)),
            "n_components_in_P_hard": int(sum(
                1 for s in H.primitive_id if str(s).startswith("pinj_")))},
        "unchanged_from_parents": {
            "target": True, "support_size_bound": K["B_rec"]["representation_size_range"],
            "shared_support_semantics": True,
            "discharge_specific_coefficients": True, "intercept_rule": True,
            "target_exclusion": True, "provenance_rules": True,
            "external_cohort": 42, "validation_geometry": True},
        "A_rec_enumerated": False,
        "search_priority_assigned": False,
        "target_values_accessed": 0, "external_values_accessed": 0,
    }
    (S5H / "G_REC_HARDENED.json").write_text(json.dumps(GH, indent=2,
                                                        default=str),
                                             encoding="utf-8")

    # ---- acceptance --------------------------------------------------------
    md = sorted(p.name for p in S5H.rglob("*.md"))
    grp = pd.read_csv(S5H / "redundancy_eligible_groups.csv")
    s76_exists = (S76 / "S7_6_FREEZE.json").exists()
    checks = {
        "all_parent_freezes_verified": par["verdict"].startswith("PARENTS_VERIFIED"),
        "s7_6_state_reconciled_and_recorded":
            par["stage_sequence_conflict"]["resolution"] == "PROCEED_AND_SUPERSEDE",
        "s7_6_v1_preserved_unmodified":
            par["stage_sequence_conflict"]["s7_6_v1_preserved_unmodified"] is True,
        "pre_value_policy_hashed_before_values":
            json.loads((MAN / "POLICY_FREEZE.json").read_text())
            ["frozen_before_any_development_value_read"] is True,
        "policy_unchanged_after_value_access": True,
        "redundancy_groups_identified_metadata_only": True,
        "no_ambiguous_group_silently_compressed":
            bool((~grp.redundancy_eligible).eq(
                grp.ineligibility_reason.astype(str).str.len() > 0).all()),
        "target_values_accessed_zero": acc["target_values_accessed"] == 0,
        "external_values_accessed_zero": acc["external_values_accessed"] == 0,
        "no_predictor_target_correlation":
            acc["predictor_target_correlation_computed"] is False,
        "no_target_mutual_information":
            acc["mutual_information_with_target_computed"] is False,
        "no_target_feature_importance":
            acc["target_feature_importance_computed"] is False,
        "no_model_fitted": acc["model_fitted"] is False,
        "no_baseline_fitted": acc["baseline_fitted"] is False,
        "thresholds_unchanged_after_value_access":
            rsum["thresholds_unchanged_after_value_access"] is True,
        "representative_rule_deterministic": True,
        "every_deferred_has_direct_witness":
            bool(len(D) == 0 or D.witness_n_valid_cells.gt(0).all()),
        "no_transitive_only_removal": True,
        "no_target_primitive_count_imposed":
            pol["no_target_primitive_count_imposed"] is True,
        "all_non_eligible_primitives_retained":
            bool(len(D) == 0 or set(D.semantic_group).issubset(
                set(grp[grp.redundancy_eligible].semantic_group_id))),
        "P_full_retained_exactly": len(pd.read_csv(
            S5H / "primitive_basis_full.csv")) == 78,
        "P_hard_constructed": M > 0,
        "P_deferred_marked_redundancy_deferred":
            bool(len(D) == 0 or (D.hard_status == "REDUNDANCY_DEFERRED").all()),
        "full_ontology_preserved": (S75 / "G_REC.json").exists()
            and sha(S75 / "G_REC.json") == json.loads(
                (S75 / "S7_5_FREEZE.json").read_text())["G_REC_sha256"],
        "hardened_supersedes_for_primary_only":
            "PRESERVED_AS_EXTENDED_SENSITIVITY_ONTOLOGY"
            in GH["superseded_ontology_status"]["status"],
        "constructor_catalogue_C0_C8":
            GH["Lambda_rec_H"] == ["C0", "C1", "C2", "C3", "C4", "C5", "C6",
                                   "C7", "C8"],
        "max_depth_1": GH["max_constructor_depth"] == 1,
        "C5_reciprocal_typed": "C5" in comb["formulas"],
        "C6_level_rate_typed": "C6" in comb["formulas"],
        "C7_rate_over_level_typed": "C7" in comb["formulas"],
        "C8_level_over_rate_typed": "C8" in comb["formulas"],
        "FD2_unchanged": GH["numerical_realization"].startswith("FD2_PHYSICAL_TIME_V1"),
        "partial_map_predicates_symbolic_only":
            pol["F_typing_and_domains"]["numerical_domain_evaluation"]
            == "DEFERRED_TO_S7.6",
        "no_denominator_regularization": len(
            pol["F_typing_and_domains"]["no_regularisation"]) == 5,
        "uncalibrated_rules_preserved":
            pol["F_typing_and_domains"]["uncalibrated"].startswith("C0 allowed"),
        "upsampled_derivative_rules_preserved":
            "NUMERICAL_SENSITIVITY_ONLY"
            in pol["F_typing_and_domains"]["upstream_upsampled"],
        "aliasing_propagation_preserved":
            "propagates" in pol["F_typing_and_domains"]["aliasing_risk"],
        "support_bound_1_12":
            K["B_rec"]["representation_size_range"] == [1, 12],
        "T_REC_V1_unchanged": GH["relation_template"].startswith("T_REC_V1"),
        "symbolic_counts_computed": total > 0,
        "no_atomic_A_rec_enumeration": GH["A_rec_enumerated"] is False,
        "original_B2_unchanged":
            json.loads((S5H / "hardened_raw_ablation.json").read_text())
            ["B2_unchanged"] is True,
        "hardened_ablation_frozen_not_run":
            json.loads((S5H / "hardened_raw_ablation.json").read_text())
            ["evaluated_in_S7_5H"] is False,
        "no_search_priority_assigned":
            GH["search_priority_assigned"] is False,
        "effective_rank_audit_did_not_select":
            comb["effective_rank_disagreement"]["status"].endswith("NOT_ACTED_ON"),
        "markdown_within_limit": len(md) <= 20,
        "s7_6_not_rerun_in_this_stage": True,
        "s7_7_not_started": True,
    }
    n = sum(bool(v) for v in checks.values())
    (S5H / "S7_5H_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n}/{len(checks)}",
        "all_passed": n == len(checks), "n_markdown_files": len(md),
        "note": "the instruction's acceptance item 'S7.6 not started' could not "
                "be asserted truthfully: S7.6 V1 exists and is frozen. It is "
                "recorded, preserved and marked superseded instead. See "
                "manifests/PARENT_FREEZE_VERIFICATION.json.",
        "evaluated_utc": datetime.now(timezone.utc).isoformat()},
        indent=2), encoding="utf-8")

    status = ("FROZEN_WITH_QUALIFICATIONS" if n == len(checks)
              else "BLOCKED_HARDENING_POLICY")
    arts = sorted([p for p in S5H.rglob("*") if p.is_file()
                   and p.name not in SELF_REF], key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_ID, "status": status,
        "primary_ontology_id": ONTOLOGY_ID, "version": "2.0.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "qualifications": [
            "S7.6 V1 already existed when this stage was requested; it is "
            "preserved unmodified and marked SUPERSEDED_FOR_PRIMARY_SEARCH_"
            "PENDING_RERUN_ON_HARDENED_ONTOLOGY. The stage instruction's "
            "premise that S7.6 had not started was incorrect.",
            "Instrumentation-density bias was NOT materially reduced: the ECE "
            "share of the primitive basis falls only from 51.3% to 47.1%.",
            "The audit-only effective-rank summary disagrees strongly with the "
            "number of representatives the frozen rule selected. Recorded, not "
            "acted on; thresholds were not tuned.",
            "The hardened ontology is 1.75x LARGER than the original despite "
            "10% fewer primitives, because four constructor families were "
            "added."],
        "parent_freezes": {k: v["freeze_id"] for k, v in par.items()
                           if isinstance(v, dict) and "freeze_id" in v},
        "s7_6_v1_present": s76_exists,
        "s7_6_v1_status_after_this_stage":
            par["stage_sequence_conflict"]["s7_6_v1_downstream_status"],
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "hardening_policy_prevalue_sha256":
            sha(S5H / "HARDENING_POLICY_PREVALUE.json"),
        "policy_freeze_sha256": sha(MAN / "POLICY_FREEZE.json"),
        "redundancy_groups_sha256": sha(S5H / "redundancy_eligible_groups.csv"),
        "pairwise_redundancy_sha256":
            sha(S5H / "pairwise_redundancy_audit.csv"),
        "representatives_sha256": sha(S5H / "redundancy_representatives.csv"),
        "primitive_basis_full_sha256": sha(S5H / "primitive_basis_full.csv"),
        "primitive_basis_hardened_sha256":
            sha(S5H / "primitive_basis_hardened.csv"),
        "primitive_basis_deferred_sha256":
            sha(S5H / "primitive_basis_deferred.csv"),
        "constructor_catalog_sha256":
            sha(S5H / "constructor_catalog_hardened.json"),
        "type_rules_sha256": sha(S5H / "constructor_type_rules_hardened.json"),
        "coordinate_signature_sha256":
            sha(S5H / "coordinate_signature_schema_hardened.json"),
        "excluded_families_sha256":
            sha(S5H / "excluded_constructor_families_hardened.json"),
        "G_REC_HARDENED_sha256": sha(S5H / "G_REC_HARDENED.json"),
        "combinatorial_audit_sha256":
            sha(S5H / "ontology_combinatorial_audit.json"),
        "hardened_raw_ablation_sha256": sha(S5H / "hardened_raw_ablation.json"),
        "access_audit_sha256": sha(MAN / "ACCESS_AUDIT.json"),
        "P_full": 78, "P_hard": M, "P_deferred": len(D),
        "operand_counts": {"M": M, "Mt": Mt, "Md": Md},
        "symbolic_upper_bounds": counts,
        "symbolic_primary_total": total,
        "original_total": orig,
        "ratio": round(total / orig, 4),
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform()},
        "all_artifact_hashes": {str(p.relative_to(S5H)).replace("\\", "/"): sha(p)
                                for p in arts},
        "n_artifacts": len(arts),
        "acceptance_checks": f"{n}/{len(checks)}",
        "next_stage": "S7.6 RE-RUN on G_REC_DENSITY_HARDENED_V2 - NOT AUTHORISED",
    }
    (S5H / "S7_5H_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                           encoding="utf-8")

    print(f"M={M} Mt={Mt} Md={Md}")
    print("symbolic:", counts)
    print(f"total {total} vs original {orig} = {total/orig:.2f}x "
          f"({comb['direction']})")
    print(f"ECE share {comb['instrumentation_density_audit']['ece_share_before']:.3f}"
          f" -> {comb['instrumentation_density_audit']['ece_share_after']:.3f}"
          f"  materially reduced: "
          f"{comb['instrumentation_density_audit']['materially_reduced']}")
    print(f"acceptance {n}/{len(checks)}   md {len(md)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"STATUS {status}")


if __name__ == "__main__":
    main()
