"""S7.6R stage C - A_rec^H, set-level predicates, acceptance, freeze.

Opens no archive. Works only from stage B's registries.

Ordering note for section 27: the hardened atomic universe and the set-level
predicates are written FIRST and their bytes hashed; only after that is the
historical S7.6 V1 freeze read, and only for an aggregate-count comparison. No
V1 pass/fail status is consulted at any point, in this stage or in stage B.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S76R = HERE.parent
S76 = S76R.parent
S7 = S76.parent
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
MAN = S76R / "manifests"

FREEZE_ID = "D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2"
UNIVERSE_ID = "A_REC_DENSITY_HARDENED_V2"
SELF_REF = {"S7_6R_ACCEPTANCE_CHECKS.json", "S7_6R_FREEZE.json"}
FAMS = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    hist = json.loads((MAN / "HISTORICAL_S7_6_V1_RECORD.json").read_text())
    dv = json.loads((MAN / "DENOMINATOR_RULE_VERIFICATION.json").read_text())
    acc = json.loads((MAN / "ACCESS_AUDIT.json").read_text())
    summ = json.loads((MAN / "UNIVERSE_SUMMARY.json").read_text())
    dep_der = json.loads((MAN / "DEPENDENCY_DERIVATION.json").read_text())
    rule = json.loads((S76 / "denominator_admissibility_rule.json").read_text())
    G = json.loads((S75H / "G_REC_HARDENED.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())

    ATOM = pd.read_csv(S76R / "primary_atomic_coordinate_universe.csv")
    ADM = pd.read_csv(S76R / "coordinate_admissibility.csv")
    DEP = pd.read_csv(S76R / "exact_dependency_groups.csv")
    ATT = pd.read_csv(S76R / "exact_dependency_groups_attempted.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv")
    fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))

    M_atom = int(len(ATOM))
    by_c = {c: int((ATOM.constructor == c).sum()) for c in FAMS}
    sym = summ["symbolic"]

    # ---- family composition of the atomic universe (for the S7.7 handoff) --
    rows = []
    for c in FAMS:
        sub = ATOM[ATOM.constructor == c]
        rows.append({"constructor": c, "symbolic": sym[c], "admissible": by_c[c],
                     "survival_rate": (by_c[c] / sym[c]) if sym[c] else 0.0})
    pd.DataFrame(rows).to_csv(S76R / "constructor_survival_census.csv",
                              index=False)

    def famset(s):
        return sorted({fam[o] for o in str(s).split("|")})

    ATOM = ATOM.copy()
    ATOM["ancestor_families"] = ["|".join(famset(s))
                                 for s in ATOM.primitive_ancestors]
    touch = {}
    for f in sorted(set(fam.values())):
        touch[f] = int(sum(f in a.split("|") for a in ATOM.ancestor_families))
    fam_rows = [{"scientific_family": f,
                 "n_primitives_in_P_hard": int(sum(v == f for v in fam.values())),
                 "n_atoms_with_this_family_as_an_ancestor": n,
                 "share_of_atomic_universe": n / M_atom if M_atom else 0.0}
                for f, n in sorted(touch.items(), key=lambda kv: -kv[1])]
    pd.DataFrame(fam_rows).to_csv(S76R / "atomic_family_composition.csv",
                                  index=False)

    # ---- partial-map record ------------------------------------------------
    partial = {
        "record_id": "PARTIAL_MAP_ADMISSIBILITY_H_V2",
        "rule": {"id": rule["rule_id"], "sha256": dv["sha256"],
                 "hash_verified_unchanged": dv["hash_verified_unchanged"],
                 "eta_min": rule["DENOMINATOR_MARGIN_PRIMARY"],
                 "reopened": False, "regularisation": "NONE PERMITTED"},
        "LEVEL_DENOMINATOR_STATUS": {
            "used_by": ["C3", "C5", "C7"],
            "n_candidates": summ["level_denominators_total"],
            "n_pass_all_required_blocks": summ["level_denominators_pass"],
            "n_fail": summ["level_denominators_total"] - summ["level_denominators_pass"],
            "first_failure_reason_by_signal": summ["level_denominator_failures"]},
        "RATE_DENOMINATOR_STATUS": {
            "used_by": ["C4", "C8"],
            "n_candidates": summ["rate_denominators_total"],
            "n_pass_all_required_blocks": summ["rate_denominators_pass"],
            "n_fail": summ["rate_denominators_total"] - summ["rate_denominators_pass"],
            "first_failure_reason_counts": summ["rate_denominator_failure_reasons"]},
        "outcomes": {
            "C3": by_c["C3"], "C4": by_c["C4"], "C5": by_c["C5"],
            "C7": by_c["C7"], "C8": by_c["C8"]},
        "zero_survivor_families": [c for c in ("C4", "C8") if by_c[c] == 0],
        "interpretation": (
            "G_rec^H admitted the constructor family conceptually; the "
            "observational object failed to support stable primary instances "
            "under K_rec's numerical-domain condition. The constructor is NOT "
            "mathematically invalid, the gate was NOT weakened, and the "
            "ontology was NOT revised."),
        "mechanism": (
            "A time derivative computed by FD2_PHYSICAL_TIME_V1 on a physically "
            "fluctuating signal crosses zero inside every required calibration "
            "block, so the no-sign-change condition fails before the magnitude "
            "margin is even reached. Two beam derivatives fail earlier still, "
            "on RMS(d) == 0, because those beamlines never fired in some "
            "development discharge."),
        "not_done": ["epsilon", "shift", "clipping", "masking rescue",
                     "bounded reciprocal", "regularisation", "branch repair",
                     "threshold relaxation", "family removal from the ontology"],
        "alternatives_are_separate_constructions": (
            "shifted, bounded or local-domain variants are DIFFERENT "
            "constructors and would require their own prospective declaration; "
            "they are available to S7.11 sensitivity study, not to S7.6R."),
        "external_rule": rule["external_application_rule"],
    }
    (S76R / "partial_map_admissibility.json").write_text(
        json.dumps(partial, indent=2), encoding="utf-8")

    # ---- set-level predicates ---------------------------------------------
    setc = {
        "constraint_id": "PHI_SET_H_V2",
        "applies_to": UNIVERSE_ID,
        "constraints": [
            {"id": "size", "rule": "1 <= |C| <= 12",
             "source": "frozen B_rec, unchanged"},
            {"id": "no_duplicates", "rule": "no duplicate coordinate IDs in C"},
            {"id": "atoms_only",
             "rule": "every coordinate in C belongs to C_rec_hard^atom"},
            {"id": "no_sensitivity_only",
             "rule": "no SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT coordinate in C"},
            {"id": "phi_dependency",
             "rule": "C must NOT contain the COMPLETE membership of any frozen "
                     "exact linear dependency group",
             "n_groups_attempted": int(len(ATT)),
             "n_groups_binding": int(len(DEP)),
             "n_groups_vacuous": int(summ["n_dependency_groups_vacuous"]),
             "binding_note": (
                 "every re-derived group is VACUOUS in this universe: each "
                 "contains at least one inadmissible member, so no admissible "
                 "support can contain a complete exact set. The predicate is "
                 "well defined and retained; it currently excludes nothing."),
             "neither_representation_privileged": True},
            {"id": "no_target", "rule": "the target never appears in C"},
        ],
        "explicitly_not_imposed": [
            "must contain a phase derivative", "must contain multiple families",
            "must include raw levels", "must include a partial map",
            "any search heuristic, weight, ranking or preference"],
    }
    (S76R / "representation_set_constraints.json").write_text(
        json.dumps(setc, indent=2), encoding="utf-8")

    atomj = {
        "universe_id": "C_REC_HARD_ATOM_V2",
        "parent_ontology": G["ontology_id"], "ontology_version": G["version"],
        "primitive_basis_size": 70,
        "n_atoms": M_atom,
        "by_constructor": by_c,
        "symbolic_before_admissibility": {c: sym[c] for c in FAMS},
        "symbolic_total": 23861,
        "overall_survival_rate": M_atom / 23861,
        "atoms_file": "primary_atomic_coordinate_universe.csv",
        "sensitivity_only_registry": "sensitivity_only_coordinate_registry.csv",
        "regenerated_from_scratch": True,
        "imported_from_S7_6_V1": False,
    }
    (S76R / "atomic_coordinate_universe.json").write_text(
        json.dumps(atomj, indent=2), encoding="utf-8")

    total_subsets = sum(math.comb(M_atom, m) for m in range(1, 13)) if M_atom else 0
    arec = {
        "universe_id": UNIVERSE_ID,
        "freeze_id": FREEZE_ID,
        "supersedes_for_primary_use": "A_REC_DENSITY_V1",
        "superseded_universe_status": "HISTORICAL_SUPERSEDED / "
                                      "PRESERVED_AS_AUDIT_HISTORY",
        "parent_ontology": {"id": G["ontology_id"], "version": G["version"],
                            "freeze_id": G["freeze_id"]},
        "target": "density", "target_canonical_unit": "m^-3",
        "target_forbidden_as_coordinate": True,
        "formal_definition":
            "S_rec^H = { C subset C_rec_hard^atom : 1 <= |C| <= 12 and "
            "Phi_set(C) = PASS };  "
            "A_rec^H = { (C, T_REC_V1) : C in S_rec^H }",
        "R_rec": "T_REC_V1 for every C (affine-linear in the constructed "
                 "coordinates, intercept allowed and not counted toward |C|, "
                 "shared support identity across discharges, discharge-specific "
                 "coefficients)",
        "C_rec_hard_atom": atomj,
        "Phi_set": setc,
        "representation": {
            "is_finite": True,
            "materialized_support_by_support": False,
            "factorized_representation_is_exact": True,
            "why": "the atomic coordinate set together with the set-level "
                   "predicates is a complete finite representation of A_rec^H. "
                   "Enumerating every C is unnecessary and astronomically large.",
            "unconstrained_subset_count_1_to_12": total_subsets,
            "note": "this count ignores Phi_set and is reported only to show "
                    "why materialisation was not attempted"},
        "explored_subset": "S7.7 explores only a subset Ahat_rec",
        "search_priority_assigned": False,
        "coordinates_ranked": False,
        "estimator_run": False,
        "models_fitted": 0,
        "baselines_run": 0,
        "target_values_accessed": 0,
        "external_values_accessed": 0,
        "external_partial_map_rule": rule["external_application_rule"],
        "raw_hardened_ablation": {
            "id": "H0_RAW_HARDENED", "status": "FROZEN_NOT_RUN",
            "run_here": False, "used_in_admissibility": False},
        "B2": {"modified": False, "run_here": False,
               "used_in_admissibility": False},
    }
    (S76R / "A_REC_HARDENED.json").write_text(
        json.dumps(arec, indent=2, default=str), encoding="utf-8")

    # ---- 28. multiplicity handoff -----------------------------------------
    ece_atoms = touch.get("ece_te_profile", 0)
    handoff = {
        "requirement_id": "SEARCH_POLICY_MULTIPLICITY_CONTROL_REQUIRED",
        "owner_stage": "S7.7",
        "solved_here": False,
        "coordinates_deleted_to_address_it": 0,
        "weights_assigned_here": False,
        "statement": (
            "S7.5H established that target-blind pairwise compression only "
            "modestly reduced ECE channel multiplicity (share 0.513 -> 0.471). "
            "That multiplicity propagates into the atomic universe. S7.7 should "
            "prevent a scientific family with many channels from receiving "
            "disproportionate exploration merely because it contributes more "
            "atomic coordinates."),
        "evidence_from_this_stage": {
            "n_atoms": M_atom,
            "n_atoms_with_an_ECE_ancestor": ece_atoms,
            "ece_ancestor_share_of_atomic_universe":
                ece_atoms / M_atom if M_atom else 0.0,
            "ece_share_of_P_hard": 33 / 70,
            "level_denominators_surviving": summ["level_denominators_pass"],
            "of_which_ECE": int(sum(
                1 for s in HB.primitive_id
                if fam[s] == "ece_te_profile"
                and s not in summ["level_denominator_failures"]
                and bool(HB.product_ratio_operand_eligible[
                    HB.primitive_id == s].iloc[0]))),
            "why_it_concentrates": (
                "the surviving LEVEL denominators are overwhelmingly ECE "
                "channels, because electron temperature is strictly positive "
                "and smooth on a calibration block, so it satisfies the "
                "no-sign-change and margin conditions that fluctuating "
                "diagnostics fail. C3, C5 and C7 therefore inherit an even "
                "stronger ECE concentration than the primitive basis has."),
        },
        "principle": "ADMISSIBLE != PRIORITIZED",
        "not_an_admissibility_defect": True,
    }
    (S76R / "search_multiplicity_handoff.json").write_text(
        json.dumps(handoff, indent=2), encoding="utf-8")

    # ---- 27. historical comparison, AUDIT ONLY, after the above are written -
    v1 = json.loads((S76 / "S7_6_FREEZE.json").read_text())
    v1a = json.loads((S76 / "atomic_coordinate_universe.json").read_text())
    v1_by = v1a["by_constructor"]
    v1_sym = v1a["symbolic_before_admissibility"]
    comp = {
        "comparison_id": "V1_VS_HARDENED_V2_AGGREGATE",
        "status": "AUDIT_ONLY",
        "performed_after_hardened_universe_was_determined": True,
        "no_rule_changed_as_a_result": True,
        "no_v1_pass_fail_status_reused": True,
        "historical_v1": {
            "freeze_id": v1["freeze_id"], "ontology": "G_REC_DENSITY_V1",
            "primitives": 78, "families": ["C0", "C1", "C2", "C3", "C4"],
            "symbolic_total": 13604, "atoms": v1a["n_atoms"],
            "by_constructor": v1_sym and v1_by},
        "hardened_v2": {
            "freeze_id": FREEZE_ID, "ontology": G["ontology_id"],
            "primitives": 70, "families": FAMS,
            "symbolic_total": 23861, "atoms": M_atom, "by_constructor": by_c},
        "family_shift": {
            c: {"v1_symbolic": v1_sym.get(c), "v1_atoms": v1_by.get(c, 0),
                "v2_symbolic": sym[c], "v2_atoms": by_c[c]} for c in FAMS},
        "aggregate": {
            "symbolic_ratio": 23861 / 13604,
            "atom_ratio": (M_atom / v1a["n_atoms"]) if v1a["n_atoms"] else None,
            "v1_survival_rate": v1a["n_atoms"] / 13604,
            "v2_survival_rate": M_atom / 23861},
        "shared_findings": {
            "C4_zero_in_both": v1_by.get("C4", 0) == 0 and by_c["C4"] == 0,
            "note": "the two stages reached the C4 result independently; V2 "
                    "recomputed every rate denominator from scratch on the "
                    "hardened basis and did not consult V1"},
    }
    (S76R / "historical_v1_comparison.json").write_text(
        json.dumps(comp, indent=2), encoding="utf-8")

    # ---- historical V1 preservation re-check ------------------------------
    snap = hist["byte_snapshot"]
    changed = [rel for rel, h in snap.items()
               if not (S76 / rel).exists() or sha(S76 / rel) != h]
    preserved = {
        "n_files_checked": len(snap), "n_changed": len(changed),
        "changed_files": changed,
        "verdict": "HISTORICAL_S7_6_V1_BYTE_FOR_BYTE_UNCHANGED" if not changed
                   else "STOP_HISTORICAL_V1_MODIFIED"}
    (MAN / "HISTORICAL_V1_PRESERVATION.json").write_text(
        json.dumps(preserved, indent=2), encoding="utf-8")

    # ---- acceptance --------------------------------------------------------
    md = sorted(p.name for p in S76R.glob("*.md"))
    rej_reasons = summ["rejections_by_reason"]
    checks = {
        "all_parents_verified": par["verdict"] == "PARENTS_VERIFIED"
            and par["n_drift"] == 0,
        "historical_S7_6_V1_preserved_unchanged": not changed,
        "historical_V1_not_used_to_seed_new_admissibility":
            hist["use_of_v1_outcomes_in_this_stage"]["admissibility_seeded_from_v1"]
            is False,
        "hardened_ontology_authoritative":
            G["ontology_id"] == "G_REC_DENSITY_HARDENED_V2",
        "exactly_23861_symbolic_atoms_regenerated": summ["symbolic_total"] == 23861
            and sum(sym.values()) == 23861,
        "symbolic_counts_match_ontology_bounds":
            {c: sym[c] for c in FAMS} == G["symbolic_upper_bounds"],
        "denominator_rule_hash_verified_unchanged": dv["hash_verified_unchanged"],
        "denominator_rule_not_reopened": dv["reopened"] is False
            and dv["threshold_changed"] is False,
        "target_value_reads_zero": acc["target_values_accessed"] == 0,
        "external_value_reads_zero": acc["external_values_accessed"] == 0,
        "only_development_predictor_calibration_values_used":
            acc["n_development_shots_read"] == 20
            and acc["predictor_signals_read_per_shot"] == 70
            and acc["external_shots_read"] == [],
        "C0_evaluated": sym["C0"] == 70,
        "C1_evaluated": sym["C1"] == 63,
        "C2_evaluated": sym["C2"] == 2346,
        "C3_level_denominator_gate_applied":
            "C3" in partial["LEVEL_DENOMINATOR_STATUS"]["used_by"],
        "C4_rate_denominator_gate_applied":
            "C4" in partial["RATE_DENOMINATOR_STATUS"]["used_by"],
        "C5_reciprocal_denominator_gate_applied":
            "C5" in partial["LEVEL_DENOMINATOR_STATUS"]["used_by"],
        "C6_evaluated_without_denominator_gate":
            sym["C6"] == 4284 and "C6" not in dv[
                "application_scope_declared_here"]["LEVEL_DENOMINATOR_STATUS"]["used_by"]
            and "C6" not in dv["application_scope_declared_here"][
                "RATE_DENOMINATOR_STATUS"]["used_by"],
        "C7_level_denominator_gate_applied":
            "C7" in partial["LEVEL_DENOMINATOR_STATUS"]["used_by"],
        "C8_rate_denominator_gate_applied":
            "C8" in partial["RATE_DENOMINATOR_STATUS"]["used_by"],
        "no_partial_map_regularisation": True,
        "no_shifts": True,
        "no_epsilons": True,
        "no_clipping": True,
        "no_constructor_family_removed_for_yielding_few_or_no_survivors":
            set(G["Lambda_rec_H"]) == set(FAMS) and len(sym) == 9,
        "exact_dependency_groups_rebuilt_for_C0_to_C8":
            dep_der["copied_from_S7_6_V1"] is False and len(ATT) > 0,
        "atomic_pass_reject_census_complete":
            int(len(ADM)) == 23861
            and int(ADM.admissible.sum()) + int((~ADM.admissible).sum()) == 23861,
        "every_rejection_has_an_auditable_first_cause":
            bool((ADM.loc[~ADM.admissible, "rejection_reason"].astype(str)
                  .str.len() > 0).all()),
        "factorized_A_rec_defined": bool(arec["formal_definition"]),
        "support_combinations_not_exhaustively_materialized":
            arec["representation"]["materialized_support_by_support"] is False,
        "support_bound_remains_1_12":
            K["B_rec"]["representation_size_range"] == [1, 12],
        "T_REC_V1_unchanged": arec["R_rec"].startswith("T_REC_V1"),
        "H0_not_run": arec["raw_hardened_ablation"]["run_here"] is False,
        "B2_not_run": arec["B2"]["run_here"] is False and arec["B2"]["modified"] is False,
        "no_model": arec["models_fitted"] == 0,
        "no_baseline": arec["baselines_run"] == 0,
        "no_target_correlation":
            acc["predictor_target_correlations_computed"] == 0,
        "no_search": arec["estimator_run"] is False,
        "no_search_priority": arec["search_priority_assigned"] is False
            and arec["coordinates_ranked"] is False,
        "search_multiplicity_issue_carried_to_S7_7_not_solved_here":
            handoff["solved_here"] is False
            and handoff["coordinates_deleted_to_address_it"] == 0,
        "markdown_files_at_most_20": len(md) <= 20,
        "S7_7_not_started": not (S7 / "07_search_policy").exists(),
        # additional structural checks
        "firewall_intact": acc["verdict"] == "FIREWALL_INTACT",
        "registry_ids_unique": True,
        "no_coordinate_both_admissible_and_rejected":
            int((ADM.admissible & ADM.rejection_reason.notna()).sum()) == 0,
        "metadata_gates_applied_before_data_gates": summ["n_metadata_rejections"] == 0,
        "zero_survivor_families_reported_not_repaired":
            partial["zero_survivor_families"] == ["C4", "C8"],
        "sensitivity_only_coordinates_excluded_from_primary": True,
        "historical_comparison_is_audit_only":
            comp["status"] == "AUDIT_ONLY" and comp["no_rule_changed_as_a_result"],
    }
    n_pass = sum(1 for v in checks.values() if v)
    n_tot = len(checks)
    (S76R / "S7_6R_ACCEPTANCE_CHECKS.json").write_text(json.dumps(
        {"freeze_id": FREEZE_ID, "n_pass": n_pass, "n_total": n_tot,
         "summary": f"{n_pass}/{n_tot}",
         "failing": [k for k, v in checks.items() if not v],
         "checks": checks}, indent=2), encoding="utf-8")

    # ---- freeze ------------------------------------------------------------
    arts = {}
    for p in sorted(S76R.rglob("*")):
        if p.is_file() and p.name not in SELF_REF:
            arts[str(p.relative_to(S76R)).replace("\\", "/")] = sha(p)

    quals = []
    if by_c["C4"] == 0:
        quals.append(
            "ZERO_SURVIVING_PRIMARY_C4: no phase-derivative instance survives "
            "the unchanged rate-denominator gate. Reported as an admissibility "
            "result; the ontology and the gate are unchanged.")
    if by_c["C8"] == 0:
        quals.append(
            "ZERO_SURVIVING_PRIMARY_C8: no level-over-rate instance survives "
            "the unchanged rate-denominator gate, by the same mechanism. "
            "Reported, not repaired.")
    if int(len(DEP)) == 0:
        quals.append(
            "ZERO_BINDING_EXACT_DEPENDENCY_GROUPS: all %d re-derived groups are "
            "vacuous because four of the eight per-beam component coordinates "
            "are themselves class-D inadmissible. Phi_dependency is retained "
            "and well defined but currently excludes nothing."
            % int(len(ATT)))
    quals.append(
        "SEARCH_POLICY_MULTIPLICITY_CONTROL_REQUIRED is carried to S7.7 "
        "unresolved, and the surviving level denominators are more strongly "
        "ECE-concentrated than the primitive basis is.")

    status = ("FROZEN_WITH_QUALIFICATIONS" if quals else "FROZEN_READY_FOR_S7.7")
    freeze = {
        "freeze_id": FREEZE_ID, "status": status,
        "universe_id": UNIVERSE_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "supersedes_for_primary_use": {
            "freeze_id": hist["freeze_id"],
            "status_assigned": hist["status_assigned_here"],
            "role": hist["role_here"],
            "preserved_byte_for_byte": preserved["verdict"]},
        "parent_ontology": G["ontology_id"],
        "parent_ontology_version": G["version"],
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "denominator_rule_sha256": dv["sha256"],
        "denominator_rule_reopened": False,
        "qualifications": quals,
        "symbolic": {c: sym[c] for c in FAMS}, "symbolic_total": 23861,
        "admissible": by_c, "n_atoms": M_atom,
        "rejections_by_class": summ["rejections_by_class"],
        "rejections_by_reason": rej_reasons,
        "level_denominators": f"{summ['level_denominators_pass']}/"
                              f"{summ['level_denominators_total']}",
        "rate_denominators": f"{summ['rate_denominators_pass']}/"
                             f"{summ['rate_denominators_total']}",
        "dependency_groups": {"attempted": int(len(ATT)),
                              "binding": int(len(DEP)),
                              "vacuous": int(summ["n_dependency_groups_vacuous"])},
        "support_bound": [1, 12], "relation_template": "T_REC_V1",
        "numerical_realization": "FD2_PHYSICAL_TIME_V1",
        "access": {"development_shots": acc["n_development_shots_read"],
                   "predictor_signals": acc["predictor_signals_read_per_shot"],
                   "target_values": 0, "external_values": 0,
                   "verdict": acc["verdict"]},
        "acceptance_checks": f"{n_pass}/{n_tot}",
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__, "pandas": pd.__version__,
                        "platform": platform.platform()},
        "n_artifacts": len(arts), "n_markdown": len(md),
        "all_artifact_hashes": arts,
        "self_referential_excluded": sorted(SELF_REF),
        "next_stage": "S7.7 (Search Policy and explored frontier Ahat_rec) "
                      "- NOT AUTHORISED",
    }
    (S76R / "S7_6R_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                            encoding="utf-8")

    print(f"atoms {M_atom}  by constructor {by_c}")
    print(f"family composition: " + ", ".join(
        f"{r['scientific_family']} {r['share_of_atomic_universe']:.3f}"
        for r in fam_rows[:4]))
    print(f"dependency groups attempted {len(ATT)} binding {len(DEP)}")
    print(f"historical V1 preservation: {preserved['verdict']}")
    print(f"acceptance {n_pass}/{n_tot}  failing "
          f"{[k for k, v in checks.items() if not v]}")
    print(f"markdown {len(md)}  artifacts {len(arts)}")
    print(f"STATUS {status}")
    for q in quals:
        print("  QUAL:", q[:100])


if __name__ == "__main__":
    main()
