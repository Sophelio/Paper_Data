"""S7.6 stage A — parent verification and the three pre-flight items.

METADATA ONLY. This script opens no archive. In particular the denominator
admissibility rule (section 4.3) is frozen and hashed here, BEFORE any
coordinate value is inspected in stage B.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S76 = HERE.parent
S7 = S76.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
S74 = S7 / "04_mathematical_interpretation"
RV2 = S74 / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
MAN = S76 / "manifests"


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
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json",
            "S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json",
            "S7_5_ACCEPTANCE_CHECKS.json", "S7_5_FREEZE.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73, "s7_4_v1": S74,
             "s7_3r_v2": RSR, "s7_4_v2": RV2, "s7_5": S75}

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

    G = json.loads((S75 / "G_REC.json").read_text())
    X = json.loads((RV2 / "X_REC.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    b = G["symbolic_upper_bounds"]
    sub = {
        "target_is_density": G["target"] == "density",
        "predictor_count_78": G["primitive_count"] == 78,
        "ontology_is_G_REC_DENSITY_V1": G["ontology_id"] == "G_REC_DENSITY_V1",
        "constructor_counts_match": [
            b["C0_primitive_level"],
            b["C1_first_temporal_derivative_primary"],
            b["C2_pairwise_product_incl_self"],
            b["C3_pairwise_ratio_directional"],
            b["C4_trajectory_relational_derivative_directional"],
        ] == [78, 70, 2926, 5700, 4830],
        "symbolic_primary_total_13604": b["primary_total"] == 13604,
        "support_bound_1_12": K["B_rec"]["representation_size_range"] == [1, 12],
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "X_rec_instantiated": X["coordinates_constructed"] is False,
        "A_rec_not_yet_built": G["A_rec_enumerated"] is False,
        "s7_6_never_previously_run": not (S76 / "S7_6_FREEZE.json").exists(),
    }
    out.update({"verified_utc": datetime.now(timezone.utc).isoformat(),
                "substantive_checks": sub, "n_drift": len(drift), "drift": drift,
                "verdict": ("PARENTS_VERIFIED" if not drift and all(sub.values())
                            else "STOP_PARENT_DRIFT")})
    return out


def preflight_4_1() -> dict:
    """B2 nesting language."""
    bp = (S72 / "BASELINE_PROTOCOL.md").read_text(encoding="utf-8")
    oc = json.loads((S75 / "ontology_constraints.json").read_text())
    rel = json.loads((S75 / "relation_templates.json").read_text())
    claim = oc.get("raw_comparator_nested_in_ontology", {})
    b2_uses_all_primitives = "same target-admissible primitive predictors" in bp \
        and "no constructed coordinates" in bp
    m_max = rel["primary_template"]["support_size_m"]["max"]
    # is the claim executable anywhere, or only a documentary annotation?
    executable = False
    for f in ("constructor_catalog.json", "constructor_type_rules.json",
              "relation_templates.json", "G_REC.json"):
        t = (S75 / f).read_text(encoding="utf-8")
        if '"B2"' in t or "baseline_B2" in t:
            executable = True
    return {
        "item": "B2 nesting language",
        "true_statement": "the RAW COORDINATE REPRESENTATION FAMILY is nested "
                          "in G_rec, because C0 primitive coordinates are "
                          "admissible",
        "not_generally_true": "the specific frozen B2 model is itself a member "
                              "of A_rec",
        "why": f"B2 is Ridge on the SAME target-admissible primitive predictors "
               f"with no constructed coordinates, i.e. potentially all 78 "
               f"primitives. A_rec members obey m <= {m_max}. A 78-primitive "
               f"model is therefore not an m<={m_max} member of A_rec.",
        "b2_uses_full_primitive_information_set": bool(b2_uses_all_primitives),
        "A_rec_support_bound_max": m_max,
        "claim_found_in_s7_5": claim.get("consequence", ""),
        "claim_is_executable": executable,
        "b2_modified": False,
        "b2_restricted_to_12": False,
        "corrected_wording": (
            "Primitive-only representations are nested within the SIR ontology. "
            "B2 is the frozen full-information raw linear comparator using the "
            "same target-admissible primitive information."),
        "fairness_claim": "SAME INFORMATION BOUNDARY, not necessarily identical "
                          "support-size constraint",
        "verdict": ("DOCUMENTARY_ERRATUM_ONLY" if not executable
                    else "PARENT_BASELINE_SEMANTICS_CONFLICT"),
    }


def preflight_4_2() -> dict:
    """'Eight cannot enter derived coordinates' wording."""
    cat = json.loads((S75 / "constructor_catalog.json").read_text())
    n = {f["id"]: f["n_eligible_operands"] for f in cat["families"]}
    ok = n["C1"] == 70 and n["C2"] == 76 and n["C3"] == 76 and n["C4"] == 70
    return {
        "item": "'eight primitives cannot enter derived coordinates'",
        "inaccurate_statement": "eight primitives cannot enter derived coordinates",
        "authoritative_rules": {
            "pcbcoil, pcdiamag3": "C0 primary admissible; C1-C4 excluded",
            "six UPSTREAM_UPSAMPLED": "C0 admissible; C1 derivative "
                                      "sensitivity-only; C2 product ADMISSIBLE; "
                                      "C3 ratio ADMISSIBLE; C4 phase derivative "
                                      "sensitivity-only",
        },
        "machine_readable_operand_counts": n,
        "encodes_76_for_C2_C3_and_70_for_C1_C4": ok,
        "corrected_wording": (
            "Two uncalibrated primitives cannot enter any primary derived "
            "coordinate. Six upstream-upsampled primitives remain eligible for "
            "products and ratios but not for primary derivative-based "
            "coordinates."),
        "s7_5_reopened": False,
        "verdict": "DOCUMENTARY_ERRATUM_ONLY" if ok else "STOP_OPERAND_COUNTS",
    }


def preflight_4_3() -> dict:
    """Denominator margin: PRE_ENUMERATION_CONTRACT_COMPLETION."""
    return {
        "rule_id": "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1",
        "status": "PRE_ENUMERATION_CONTRACT_COMPLETION",
        "not_an_empirical_correction": True,
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_before_any_coordinate_value_inspected": True,
        "parent_principle": (
            "S7.2 P_rec class E froze the principle: a denominator whose "
            "calibration-interval sign changes, or whose minimum absolute "
            "magnitude falls below a fixed fraction of its calibration scale, "
            "is inadmissible unless a declared regularisation is used. The "
            "PRIMARY ontology declares NO denominator regularisation. The "
            "fixed fraction and the scale were never numerically instantiated; "
            "this completes that specification."),
        "DENOMINATOR_MARGIN_PRIMARY": 0.05,
        "scale_definition": "scale(d) = RMS(d) = sqrt(mean(d^2)) on one "
                            "calibration block",
        "margin_definition": "eta(d) = min(|d|) / RMS(d) on one calibration block",
        "zero_scale_behaviour": "RMS(d) == 0  ->  FAIL",
        "primary_conditions_all_required": [
            "d is finite throughout the calibration block",
            "d does NOT change sign within the calibration block",
            "eta(d) >= 0.05",
        ],
        "interpretation": "the denominator must remain at least 5% of its RMS "
                          "calibration scale away from zero",
        "evaluated_on": "every required development calibration block "
                        "(20 discharges x blocks A, B, C)",
        "fail_if_any_required_block_fails": True,
        "no_regularisation_permitted": [
            "denominator shift", "additive epsilon", "clipping",
            "bounded reciprocal", "piecewise branch repair"],
        "sensitivity_values_for_S7_11_only": [0.01, 0.10],
        "sensitivity_may_replace_primary": False,
        "applies_to": {
            "C3_ratio": "denominator d = x_j (level, canonical units)",
            "C4_phase": "denominator d = dx_j/dt from FD2_PHYSICAL_TIME_V1",
        },
        "external_application_rule": {
            "same_rule_applies": True,
            "on_failure": ["do NOT shift or regularize",
                           "do NOT replace the coordinate",
                           "do NOT refit the support",
                           "record the representation as NOT_APPLICABLE on that "
                           "discharge/block"],
            "outcome_decided_by": "the downstream qualification stage, not S7.6",
        },
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent drift")

    p41, p42 = preflight_4_1(), preflight_4_2()
    if p41["verdict"] != "DOCUMENTARY_ERRATUM_ONLY":
        raise SystemExit("STOP: PARENT_BASELINE_SEMANTICS_CONFLICT")
    if p42["verdict"] != "DOCUMENTARY_ERRATUM_ONLY":
        raise SystemExit("STOP: " + p42["verdict"])

    rule = preflight_4_3()
    (S76 / "denominator_admissibility_rule.json").write_text(
        json.dumps(rule, indent=2), encoding="utf-8")
    rule_sha = sha(S76 / "denominator_admissibility_rule.json")

    (MAN / "PREFLIGHT_CHECKS.json").write_text(json.dumps({
        "check_4_1_b2_nesting": p41,
        "check_4_2_derived_coordinate_wording": p42,
        "check_4_3_denominator_margin": {
            "rule_file": "denominator_admissibility_rule.json",
            "sha256": rule_sha,
            "frozen_before_stage_B": True,
            "verdict": "PRE_ENUMERATION_CONTRACT_COMPLETION"},
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    print(f"parents   : {par['verdict']}")
    print(f"  symbolic counts match: {par['substantive_checks']['constructor_counts_match']}"
          f"  total 13604: {par['substantive_checks']['symbolic_primary_total_13604']}")
    print(f"4.1 B2 nesting        : {p41['verdict']} "
          f"(executable claim: {p41['claim_is_executable']}, B2 unmodified)")
    print(f"4.2 derived wording   : {p42['verdict']} "
          f"(operand counts {p42['machine_readable_operand_counts']})")
    print(f"4.3 denominator rule  : FROZEN eta>=0.05, RMS scale, no "
          f"regularisation  sha {rule_sha[:16]}")
    print("NO ARCHIVE OPENED IN STAGE A")


if __name__ == "__main__":
    main()
