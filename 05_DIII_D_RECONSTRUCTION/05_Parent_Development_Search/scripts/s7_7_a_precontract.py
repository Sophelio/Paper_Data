"""S7.7 stage A - parent verification and pre-search contract completion.

METADATA ONLY. THIS SCRIPT OPENS NO ARCHIVE AND READS NO SIGNAL OR TARGET VALUE.

It verifies the eleven lineage freezes and completes the two project-wide
definitions that were left prospectively unspecified by the earlier q_rec
planning: the persistence skill metric S_pers and the AR(1) diagnostic
comparator B1A_AR1. Both are frozen and hashed here, before any density value
can be opened by any later stage.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S77 = HERE.parent
S7 = S77.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
S74 = S7 / "04_mathematical_interpretation"
RV2 = S74 / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76 = S7 / "06_admissible_universe"
S76R = S76 / "hardened_v2"
MAN = S77 / "manifests"

DENOM_RULE_SHA = ("6d4004eb3ae95067b2a01dddeb90226748cfee7097217d68ab5377ac"
                  "50ed716d")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_parents() -> dict:
    frz = {
        "s7_1": json.loads((R1 / "S7_1_FINAL_FREEZE.json").read_text()),
        "s7_2_v1": json.loads((S72 / "S7_2_FREEZE.json").read_text()),
        "s7_2_v2": json.loads((CV1 / "S7_2_FREEZE_V2.json").read_text()),
        "s7_3_v1": json.loads((S73 / "S7_3_FREEZE.json").read_text()),
        "s7_4_v1": json.loads((S74 / "S7_4_FREEZE.json").read_text()),
        "s7_3r_v2": json.loads((RSR / "S7_3_FREEZE_V2.json").read_text()),
        "s7_4_v2": json.loads((RV2 / "S7_4_FREEZE_V2.json").read_text()),
        "s7_5": json.loads((S75 / "S7_5_FREEZE.json").read_text()),
        "s7_5h": json.loads((S75H / "S7_5H_FREEZE.json").read_text()),
        "s7_6_v1_historical": json.loads((S76 / "S7_6_FREEZE.json").read_text()),
        "s7_6r_v2": json.loads((S76R / "S7_6R_FREEZE.json").read_text()),
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json",
            "S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json",
            "S7_5_ACCEPTANCE_CHECKS.json", "S7_5_FREEZE.json",
            "S7_5H_ACCEPTANCE_CHECKS.json", "S7_5H_FREEZE.json",
            "S7_6_ACCEPTANCE_CHECKS.json", "S7_6_FREEZE.json",
            "S7_6R_ACCEPTANCE_CHECKS.json", "S7_6R_FREEZE.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73, "s7_4_v1": S74,
             "s7_3r_v2": RSR, "s7_4_v2": RV2, "s7_5": S75, "s7_5h": S75H,
             "s7_6_v1_historical": S76, "s7_6r_v2": S76R}

    s71v = json.loads((S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json").read_text())
    s71map = {"signal_inventory_sha256": R1 / "FINAL_SIGNAL_INVENTORY.csv",
              "shot_inventory_sha256": R1 / "FINAL_SHOT_INVENTORY.csv",
              "units_registry_sha256": S7 / "SIGNAL_UNITS.json",
              "provenance_graph_sha256": R1 / "provenance_graph.json",
              "dalia_parity_sha256": R1 / "DALIA_SIGNAL_PARITY.csv",
              "temporal_lineage_sha256": R1 / "FINAL_TEMPORAL_LINEAGE.csv",
              "equilibrium_lineage_sha256": R1 / "equilibrium_lineage_status.csv",
              "source_inventory_sha256": R1 / "SOURCE_ARTIFACT_INVENTORY.csv",
              "quality_summary_sha256": R1 / "signal_quality_summary.csv"}
    drift = [{"parent": "s7_1", "artifact": k} for k, p in s71map.items()
             if sha(p) != s71v["canonical_raw_byte_hashes"][k]]
    out = {"s7_1": {"freeze_id": frz["s7_1"]["freeze_id"],
                    "n_verified": sum(1 for k, p in s71map.items()
                                      if sha(p) == s71v["canonical_raw_byte_hashes"][k])}}
    for k, base in bases.items():
        n = 0
        for rel, h in frz[k]["all_artifact_hashes"].items():
            if Path(rel).name in SELF:
                continue
            p = base / rel
            if not p.exists() or sha(p) != h:
                drift.append({"parent": k, "artifact": rel})
            else:
                n += 1
        out[k] = {"freeze_id": frz[k]["freeze_id"],
                  "status": frz[k].get("status", ""), "n_verified": n}

    A = json.loads((S76R / "A_REC_HARDENED.json").read_text())
    U = json.loads((S76R / "atomic_coordinate_universe.json").read_text())
    G = json.loads((S75H / "G_REC_HARDENED.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    sub = {
        "A_REC_DENSITY_HARDENED_V2_authoritative":
            A["universe_id"] == "A_REC_DENSITY_HARDENED_V2",
        "atomic_universe_10778": U["n_atoms"] == 10778,
        "symbolic_total_23861": U["symbolic_total"] == 23861,
        "target_is_density": A["target"] == "density",
        "target_unit_m3": A["target_canonical_unit"] == "m^-3",
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "C4_admissible_zero": U["by_constructor"]["C4"] == 0,
        "C8_admissible_zero": U["by_constructor"]["C8"] == 0,
        "surviving_family_counts_match": U["by_constructor"] == {
            "C0": 66, "C1": 59, "C2": 2080, "C3": 2457, "C4": 0, "C5": 39,
            "C6": 3776, "C7": 2301, "C8": 0},
        "support_bound_1_12": K["B_rec"]["representation_size_range"] == [1, 12],
        "denominator_rule_unchanged":
            sha(S76 / "denominator_admissibility_rule.json") == DENOM_RULE_SHA,
        "T_REC_V1_unchanged": A["R_rec"].startswith("T_REC_V1"),
        "ontology_is_G_REC_DENSITY_HARDENED_V2":
            G["ontology_id"] == "G_REC_DENSITY_HARDENED_V2",
        "P_hard_70": G["operand_counts"]["M"] == 70,
        "s7_6r_frozen": frz["s7_6r_v2"]["status"] == "FROZEN_WITH_QUALIFICATIONS",
        "historical_s7_6_v1_preserved": json.loads(
            (S76R / "manifests" / "HISTORICAL_V1_PRESERVATION.json").read_text()
        )["n_changed"] == 0,
        "search_priority_not_yet_assigned":
            A["search_priority_assigned"] is False,
        "estimator_not_yet_run": A["estimator_run"] is False,
        "s7_7_never_previously_run": not (S77 / "S7_7_FREEZE.json").exists(),
    }
    out.update({"verified_utc": datetime.now(timezone.utc).isoformat(),
                "substantive_checks": sub, "n_drift": len(drift), "drift": drift,
                "verdict": ("PARENTS_VERIFIED" if not drift and all(sub.values())
                            else "STOP_PARENT_DRIFT")})
    return out


def pre_search_contract() -> dict:
    return {
        "record_id": "PRE_SEARCH_CONTRACT_COMPLETION_V1",
        "status": "PROSPECTIVE_SPECIFICATION_COMPLETION",
        "not_an_outcome_response": True,
        "frozen_before_any_density_value_opened": True,
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "parent_principle": (
            "Both items were required by earlier q_rec planning but were never "
            "numerically instantiated. They are completed here, prospectively, "
            "before the first target-dependent operation of the pipeline."),

        "S_PERS": {
            "metric_id": "S_PERS_V1",
            "name": "persistence skill",
            "status": "REQUIRED_REPORTING",
            "block_level_definition":
                "S_pers(M,s,b) = 1 - MSE(M,s,b) / MSE(B1_persistence,s,b)",
            "identical_protected_samples_required": True,
            "zero_denominator_behaviour": {
                "condition": "MSE(B1_persistence,s,b) == 0",
                "value": "UNDEFINED_ZERO_PERSISTENCE_ERROR",
                "epsilon_permitted": False,
                "note": "no epsilon, no floor, no substitution"},
            "discharge_level_definition":
                "S_pers(M,s) = 1 - mean_b MSE(M,s,b) / mean_b MSE(B1,s,b), "
                "provided the denominator is nonzero",
            "cohort_summaries_operate_on": "discharge-level values",
            "interpretation": {"> 0": "improves on persistence",
                               "= 0": "matches persistence",
                               "< 0": "worse than persistence"},
            "does_not_replace_frozen_NRMSE": True,
            "does_not_change_V3": True,
            "V3_mandatory_gate": "remains exactly the already-frozen paired "
                                 "NRMSE condition, unchanged",
            "may_guide_S7_7_search": False,
            "run_in_S7_7": False},

        "B1A_AR1": {
            "baseline_id": "B1A_AR1",
            "name": "simple first-order autoregressive comparator",
            "status": "DIAGNOSTIC_BASELINE",
            "required_to_report": True,
            "replaces_B1_persistence": False,
            "added_to_mandatory_V3_thresholds": False,
            "added_to_V3_note": "not added unless a frozen parent already "
                                "requires it; no frozen parent does",
            "calibration_fit": "y_k = a + phi * y_{k-1} + eps_k, ordinary "
                               "least squares on the calibration interval",
            "protected_block_procedure": [
                "initialise with the FINAL CALIBRATION target value",
                "predict recursively",
                "NEVER update the recursion using protected target values",
                "a and phi remain calibration-fitted and frozen over that block"],
            "no_teacher_forcing_on_protected_values": True,
            "lag_order": 1, "additional_lags": False,
            "hyperparameter_selection": "NONE",
            "run_in_S7_7": False,
            "belongs_to": "S7.9 / S7.10, alongside B0-B3 and H0_RAW_HARDENED"},

        "neither_baseline_run_here": True,
        "no_density_value_opened_by_this_stage": True,
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")

    pre = pre_search_contract()
    p = S77 / "PRE_SEARCH_CONTRACT_COMPLETION.json"
    p.write_text(json.dumps(pre, indent=2), encoding="utf-8")
    h = sha(p)
    (MAN / "PRE_SEARCH_CONTRACT_FREEZE.json").write_text(json.dumps({
        "file": "PRE_SEARCH_CONTRACT_COMPLETION.json", "sha256": h,
        "frozen_utc": pre["frozen_utc"],
        "frozen_before_any_density_value_opened": True,
        "stage_a_opens_no_archive": True,
        "items": ["S_PERS_V1", "B1A_AR1"],
        "neither_run": True}, indent=2), encoding="utf-8")

    print(f"parents : {par['verdict']}  drift {par['n_drift']}")
    bad = [k for k, v in par["substantive_checks"].items() if not v]
    print(f"substantive checks failing: {bad if bad else 'none'}")
    print(f"pre-search contract frozen: sha {h[:16]}  (S_PERS_V1, B1A_AR1)")
    print("NEITHER BASELINE RUN.  NO ARCHIVE OPENED IN STAGE A.")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent drift")


if __name__ == "__main__":
    main()
