"""S7.6R stage A - parent verification, historical V1 preservation, rule check.

METADATA ONLY. THIS SCRIPT OPENS NO ARCHIVE AND READS NO SIGNAL VALUE.

It verifies the ten lineage freezes, records the byte state of the historical
S7.6 V1 directory so that stage C can prove it was never touched, verifies the
already-frozen denominator rule hash, and declares (without changing the rule)
the constructor families to which that unchanged rule is applied.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S76R = HERE.parent                      # 06_admissible_universe/hardened_v2
S76 = S76R.parent                       # 06_admissible_universe  (historical V1)
S7 = S76.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
S74 = S7 / "04_mathematical_interpretation"
RV2 = S74 / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
MAN = S76R / "manifests"

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
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json",
            "S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json",
            "S7_5_ACCEPTANCE_CHECKS.json", "S7_5_FREEZE.json",
            "S7_5H_ACCEPTANCE_CHECKS.json", "S7_5H_FREEZE.json",
            "S7_6_ACCEPTANCE_CHECKS.json", "S7_6_FREEZE.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73, "s7_4_v1": S74,
             "s7_3r_v2": RSR, "s7_4_v2": RV2, "s7_5": S75, "s7_5h": S75H,
             "s7_6_v1_historical": S76}

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

    G = json.loads((S75H / "G_REC_HARDENED.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    X = json.loads((RV2 / "X_REC.json").read_text())
    b = G["symbolic_upper_bounds"]
    oc = G["operand_counts"]
    cat = json.loads((S75H / "constructor_catalog_hardened.json").read_text())
    sub = {
        "target_is_density": G["target"] == "density",
        "target_canonical_unit_m3": G["target_canonical_unit"] == "m^-3",
        "ontology_is_G_REC_DENSITY_HARDENED_V2":
            G["ontology_id"] == "G_REC_DENSITY_HARDENED_V2",
        "ontology_version_2_0_0": G["version"] == "2.0.0",
        "P_hard_70": oc["M"] == 70,
        "Mt_68": oc["Mt"] == 68,
        "Md_63": oc["Md"] == 63,
        "catalogue_is_C0_to_C8":
            G["Lambda_rec_H"] == ["C0", "C1", "C2", "C3", "C4", "C5", "C6",
                                  "C7", "C8"],
        "max_depth_1": G["max_constructor_depth"] == 1,
        "symbolic_bounds_match": [b[c] for c in ("C0", "C1", "C2", "C3", "C4",
                                                 "C5", "C6", "C7", "C8")]
            == [70, 63, 2346, 4556, 3906, 68, 4284, 4284, 4284],
        "symbolic_primary_total_23861": G["symbolic_primary_total"] == 23861,
        "catalogue_total_matches": cat["symbolic_primary_total"] == 23861,
        "T_REC_V1_unchanged": G["relation_template"] == "T_REC_V1 (unchanged)",
        "FD2_unchanged": G["numerical_realization"]
            == "FD2_PHYSICAL_TIME_V1 (unchanged)",
        "support_bound_1_12": K["B_rec"]["representation_size_range"] == [1, 12],
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "X_rec_instantiated": X["coordinates_constructed"] is False,
        "hardened_A_rec_not_yet_built": G["A_rec_enumerated"] is False,
        "s7_5h_frozen": frz["s7_5h"]["status"] == "FROZEN_WITH_QUALIFICATIONS",
        "historical_s7_6_v1_present": (S76 / "S7_6_FREEZE.json").exists(),
        "s7_6r_never_previously_run": not (S76R / "S7_6R_FREEZE.json").exists(),
    }
    out.update({"verified_utc": datetime.now(timezone.utc).isoformat(),
                "substantive_checks": sub, "n_drift": len(drift), "drift": drift,
                "verdict": ("PARENTS_VERIFIED" if not drift and all(sub.values())
                            else "STOP_PARENT_DRIFT")})
    return out


def historical_v1_record() -> dict:
    """Byte snapshot of the historical S7.6 V1 directory (top level only; the
    hardened_v2 subtree is this stage's own output and is excluded)."""
    files = sorted(p for p in S76.iterdir() if p.is_file())
    sub = sorted(p for p in (S76 / "manifests").glob("*") if p.is_file())
    sub += sorted(p for p in (S76 / "scripts").glob("*") if p.is_file())
    snap = {str(p.relative_to(S76)).replace("\\", "/"): sha(p)
            for p in files + sub}
    f = json.loads((S76 / "S7_6_FREEZE.json").read_text())
    return {
        "freeze_id": f["freeze_id"],
        "status_in_its_own_record": f.get("status", ""),
        "status_assigned_here": "HISTORICAL_SUPERSEDED",
        "role_here": "NOT_A_PRIMARY_PARENT_FOR_ADMISSIBILITY_RESULTS",
        "meaning": ("Historical S7.6 V1 was completed on the superseded "
                    "ontology G_REC_DENSITY_V1 and is preserved as audit "
                    "history. The primary admissible universe is rebuilt here "
                    "de novo from the hardened ontology."),
        "its_ontology": "G_REC_DENSITY_V1",
        "its_primitive_count": 78,
        "its_constructor_families": ["C0", "C1", "C2", "C3", "C4"],
        "contamination_assessment": {
            "target_values_accessed_by_v1": 0,
            "external_values_accessed_by_v1": 0,
            "predictor_target_statistics_computed_by_v1": 0,
            "models_fitted_by_v1": 0,
            "verdict": "NO_TARGET_DERIVED_INFORMATION_EXISTS_IN_THE_LINEAGE",
        },
        "use_of_v1_outcomes_in_this_stage": {
            "pass_fail_lists_reused": False,
            "coordinate_registry_imported": False,
            "denominator_results_reused": False,
            "dependency_groups_copied": False,
            "admissibility_seeded_from_v1": False,
            "only_permitted_use": "aggregate-count comparison AFTER the "
                                  "hardened universe is frozen (section 27)",
        },
        "byte_snapshot_taken_utc": datetime.now(timezone.utc).isoformat(),
        "n_files_snapshotted": len(snap),
        "byte_snapshot": snap,
    }


def denominator_rule_check() -> dict:
    p = S76 / "denominator_admissibility_rule.json"
    got = sha(p)
    rule = json.loads(p.read_text())
    return {
        "rule_file": "../denominator_admissibility_rule.json",
        "rule_id": rule["rule_id"],
        "expected_sha256_prefix": "6d4004eb",
        "sha256": got,
        "hash_verified_unchanged": got == DENOM_RULE_SHA,
        "reopened": False,
        "threshold_changed": False,
        "DENOMINATOR_MARGIN_PRIMARY": rule["DENOMINATOR_MARGIN_PRIMARY"],
        "scale_definition": rule["scale_definition"],
        "margin_definition": rule["margin_definition"],
        "primary_conditions_all_required": rule["primary_conditions_all_required"],
        "no_regularisation_permitted": rule["no_regularisation_permitted"],
        "application_scope_declared_here": {
            "note": ("The frozen rule text names C3 and C4 because those were "
                     "the only partial maps in the superseded five-family "
                     "grammar. The hardened grammar adds three more partial "
                     "maps. The RULE IS UNCHANGED; only the set of families it "
                     "is applied to grows with the catalogue. No threshold, "
                     "scale, condition or regularisation policy is altered."),
            "LEVEL_DENOMINATOR_STATUS": {
                "denominator": "d = x_j (primitive level, canonical units)",
                "used_by": ["C3", "C5", "C7"],
                "C5_note": "unary partial map, denominator is the operand itself",
            },
            "RATE_DENOMINATOR_STATUS": {
                "denominator": "d = dx_j/dt from FD2_PHYSICAL_TIME_V1",
                "used_by": ["C4", "C8"],
            },
            "no_denominator_gate": ["C0", "C1", "C2", "C6"],
        },
        "external_application_rule": rule["external_application_rule"],
        "sensitivity_values_remain_sensitivity_only":
            rule["sensitivity_values_for_S7_11_only"],
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")

    hist = historical_v1_record()
    (MAN / "HISTORICAL_S7_6_V1_RECORD.json").write_text(
        json.dumps(hist, indent=2), encoding="utf-8")

    den = denominator_rule_check()
    (MAN / "DENOMINATOR_RULE_VERIFICATION.json").write_text(
        json.dumps(den, indent=2), encoding="utf-8")

    seq = {
        "carried_from": "D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1",
        "statement": ("Historical S7.6 V1 was completed on the superseded "
                      "ontology and is preserved as audit history. The primary "
                      "admissible universe is rebuilt here de novo from the "
                      "hardened ontology."),
        "explicitly_not_claimed": "S7.6 had never started.",
        "why_no_contamination": {
            "target_values": 0, "external_values": 0,
            "predictor_target_statistics": 0, "models": 0},
        "residual_risk": "LOW_AND_RECORDED",
        "v1_outcomes_used_for_v2_decisions": False,
    }
    (MAN / "STAGE_SEQUENCE_QUALIFICATION.json").write_text(
        json.dumps(seq, indent=2), encoding="utf-8")

    print(f"parents : {par['verdict']}  drift {par['n_drift']}")
    bad = [k for k, v in par["substantive_checks"].items() if not v]
    print(f"substantive checks failing: {bad if bad else 'none'}")
    print(f"historical S7.6 V1 : {hist['freeze_id']} -> "
          f"{hist['status_assigned_here']} / {hist['role_here']}  "
          f"({hist['n_files_snapshotted']} files snapshotted)")
    print(f"denominator rule   : hash_verified_unchanged="
          f"{den['hash_verified_unchanged']}  sha {den['sha256'][:16]}  "
          f"eta>={den['DENOMINATOR_MARGIN_PRIMARY']}")
    print("NO ARCHIVE OPENED IN STAGE A")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent drift")
    if not den["hash_verified_unchanged"]:
        raise SystemExit("STOP: denominator rule hash mismatch")


if __name__ == "__main__":
    main()
