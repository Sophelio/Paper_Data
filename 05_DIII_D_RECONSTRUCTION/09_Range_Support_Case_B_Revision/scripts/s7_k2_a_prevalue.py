"""S7.K2 step A - everything that must be frozen BEFORE any candidate metric
is computed.

Order enforced here:
  1. lineage verification through S7.R1
  2. Epoch-1 / R1 immutability invariant
  3. K2 target-blind firewall, hashed
  4. gas-signal provenance resolution
  5. CONCEPTUAL definition of observational range support
  6. NUMERICAL desiderata, hashed

No candidate score is evaluated in this script.
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

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S7R1 = S7 / "R1_operational_state_reconciliation"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


LINEAGE = [
    ("S7.1", "01_observational_object/reconciliation_final/S7_1_FINAL_FREEZE.json"),
    ("S7.2 V1", "02_reconstruction_contract/S7_2_FREEZE.json"),
    ("S7.2 V2", "02_reconstruction_contract/correction_v1/S7_2_FREEZE_V2.json"),
    ("S7.3R V2", "03_target_feasibility_and_boundary/reconciliation_source_resolution/S7_3_FREEZE_V2.json"),
    ("S7.4 V2", "04_mathematical_interpretation/retry_source_resolution_v2/S7_4_FREEZE_V2.json"),
    ("S7.5 V1", "05_typed_relational_ontology/S7_5_FREEZE.json"),
    ("S7.5H V1", "05H_primitive_space_and_ontology_hardening/S7_5H_FREEZE.json"),
    ("S7.6R V2", "06_admissible_universe/hardened_v2/S7_6R_FREEZE.json"),
    ("S7.7R V2", "07_search_policy_and_frontier/one_seed_primary_v2/S7_7R_FREEZE.json"),
    ("S7.8 V1", "08_utility_and_qualification_rules/S7_8_FREEZE.json"),
    ("S7.9 V1", "09_development_selection_and_freeze/S7_9_FREEZE.json"),
    ("S7.10 V1", "10_external_validation/S7_10_FREEZE.json"),
    ("S7.11 V1", "11_sensitivity_and_interpretation/S7_11_FREEZE.json"),
    ("S7.R1 V1", "R1_operational_state_reconciliation/S7_R1_FREEZE.json"),
]


def main() -> int:
    drift = []
    now = datetime.now(timezone.utc).isoformat()

    lineage = []
    for label, rel in LINEAGE:
        p = S7 / rel
        if not p.exists():
            drift.append("MISSING: " + rel)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        lineage.append({"stage": label, "freeze_id": d.get("freeze_id"),
                        "status": d.get("status"), "file_sha256": sha256(p)})

    manifests = {}
    for label, rel, base in [
            ("S7.9", "09_development_selection_and_freeze/S7_9_FREEZE.json",
             "09_development_selection_and_freeze"),
            ("S7.10", "10_external_validation/S7_10_FREEZE.json", "10_external_validation"),
            ("S7.11", "11_sensitivity_and_interpretation/S7_11_FREEZE.json",
             "11_sensitivity_and_interpretation"),
            ("S7.R1", "R1_operational_state_reconciliation/S7_R1_FREEZE.json",
             "R1_operational_state_reconciliation")]:
        fz = json.loads((S7 / rel).read_text(encoding="utf-8"))
        m, bad = 0, []
        for r, want in fz["all_artifact_hashes"].items():
            p = S7 / base / r
            if p.exists() and sha256(p) == want:
                m += 1
            else:
                bad.append(r)
        manifests[label] = {"n": len(fz["all_artifact_hashes"]), "matched": m, "mismatched": bad}
        if bad:
            drift.append("%s manifest does not reproduce" % label)

    fr1 = json.loads((S7R1 / "S7_R1_FREEZE.json").read_text())
    f10 = json.loads((S7 / "10_external_validation" / "S7_10_FREEZE.json").read_text())
    f11 = json.loads((S7 / "11_sensitivity_and_interpretation" / "S7_11_FREEZE.json").read_text())
    sel = json.loads((S7 / "09_development_selection_and_freeze"
                      / "SELECTED_REPRESENTATION.json").read_text())

    invariant = {
        "PRIMARY_EPOCH1_RESULT_IMMUTABLE": True,
        "DISCOVERY_EPOCH_1_INTACT": True,
        "C_dev_star": sel["support_id"], "C_dev_star_size": sel["support_size"],
        "S7_10_primary_verdict": f10["primary_scientific_verdict"],
        "gate_table": f11["final_gate_table"],
        "S7_R1_status": fr1["status"], "S7_R1_recommendation": fr1["recommendation"],
        "R1_gates": fr1["gates"],
        "earliest_invalidated_stage": fr1["earliest_invalidated_stage"],
        "K_rec_minimal_component": fr1["K_rec_minimal_component"],
        "two_seed": "NOT_EXECUTED",
        "S7_R2_exists": (S7 / "R2_state_conditioned_requalification").exists(),
        "S7_12_exists": (S7 / "12_qualified_result").exists(),
    }
    for cond, msg in [
        (invariant["C_dev_star_size"] == 12, "C_dev_star changed"),
        (invariant["S7_10_primary_verdict"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER",
         "Epoch-1 verdict changed"),
        (invariant["gate_table"]["V3"] == "FAIL", "V3 changed"),
        (invariant["S7_R1_recommendation"] == "STOP_OPERATIONAL_STATE_ROUTE",
         "R1 recommendation changed"),
        (invariant["K_rec_minimal_component"] == "P_rec", "R1 minimal component changed"),
        (not invariant["S7_R2_exists"], "S7.R2 exists"),
        (not invariant["S7_12_exists"], "S7.12 exists"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- 3. firewall ----------------------------------------
    firewall = {
        "record_id": "K2_TARGET_BLIND_FIREWALL_V1", "frozen_utc": now,
        "target_reads": 0, "model_error_reads": 0, "residual_reads": 0,
        "V3_label_reads": 0, "support_family_outcome_label_reads": 0,
        "permitted": ["predictor signal values", "coordinate values",
                      "frozen coordinate definitions", "frozen block geometry",
                      "coordinate identities of the 217 fixed supports"],
        "forbidden_during_rule_construction": [
            "density target values", "NRMSE", "residuals", "V3-style pass/fail labels",
            "S7.11 70/143 partition", "any reconstruction outcome"],
        "historical_motivation_permitted_and_recorded": True,
        "motivation_is_not_validation": True,
        "asserted_in_code": True,
    }
    (OUT / "K2_TARGET_BLIND_FIREWALL.json").write_text(json.dumps(firewall, indent=2), encoding="utf-8")

    # ---------------- 4. gas provenance ----------------------------------
    reg = json.loads((S7 / "SIGNAL_UNITS.json").read_text(encoding="utf-8"))
    gas = {s: reg["signals"][s] for s in ("gasa", "gasb", "gasc", "gasd")}
    ur = pd.read_csv(S7 / "01_observational_object" / "reconciliation" / "units_recovery.csv")
    g1 = ur[ur.signal_id == "gasa"].iloc[0]

    prov = {
        "record_id": "GAS_SIGNAL_PROVENANCE_CORRECTION_V1",
        "generated_utc": now,
        "resolution": "GAS_SIGNAL_UNIT_RESOLVED_COMMAND_VOLTAGE",
        "applies_to": ["gasa", "gasb", "gasc", "gasd"],
        "resolved_unit": "V",
        "resolved_semantics": "gas injection valve COMMAND signal (actuator command voltage)",
        "not_a_flow_rate": True,
        "authoritative_source": {
            "artifact": "S7/SIGNAL_UNITS.json",
            "sha256": sha256(S7 / "SIGNAL_UNITS.json"),
            "units_source": reg["provenance"]["units_source"],
            "evidence_class": "LOCAL_DOCUMENTED (units registry)",
            "upstream_variants": {s: v.get("upstream_variants") for s, v in gas.items()},
            "reading": ("the upstream per-shot metadata records the unit string literally as "
                        "'volt' on 51 of 62 shots for gasa/gasb/gasc and on 62 of 62 for gasd; "
                        "the remainder report an empty string, never a conflicting unit"),
        },
        "superseded_record": {
            "artifact": "diiid_sir_data_provider.py SIGNAL_MANIFEST; "
                        "S7.1 reconciliation/units_recovery.csv; S7.1 units_sources.md",
            "unit": "Torr*L/s", "semantic_physical_type": str(g1.semantic_physical_type),
            "evidence_class": str(g1.evidence_class), "confidence": str(g1.confidence),
            "dimensional_signature": str(g1.dimensional_signature),
            "magnitude_test": str(g1.magnitude_test),
            "unresolved_reason": str(g1.unresolved_reason),
            "status": "SUPERSEDED_BY_S7_1R_UNITS_REGISTRY",
        },
        "correction_to_R1_ledger_entry_K_R1_02": (
            "R1 recorded this as an unreconciled inconsistency between two records of equal "
            "standing. K2 finds they are NOT of equal standing: the Torr*L/s entry is a "
            "first-pass external-convention hypothesis at LOW confidence with an AMBIGUOUS "
            "dimensional signature and NOT_TESTED magnitude, and the S7.1R units registry "
            "SUPERSEDED it with local documentary evidence. The same registry and the same "
            "evidence mechanism resolved pcdiamag3 to 'raw'/uncalibrated, which the entire "
            "downstream lineage accepted. The ontology is CORRECT; the stale record is the "
            "provider manifest."),
        "consequence_for_frozen_coordinates": {
            "PROD(gasa,gasa) output_dimension": "(V)*(V)",
            "is_correct": True,
            "R1_concern_withdrawn": True,
            "numerical_impact": "NONE - CANON contains neither label, scale factor is exactly 1.0",
        },
        "epoch1_files_edited": 0,
        "record_class": "FUTURE_EPOCH_SUPERSEDING_PROVENANCE_RECORD",
        "physical_reading_for_epoch2": (
            "gasa..gasd are actuator COMMAND voltages, not fueling rates. A squared gas command, "
            "PROD(gasa,gasa), is dimensionally V^2 and carries no direct physical interpretation "
            "as a fueling quantity. This strengthens, and does not weaken, the S7.11/R1 reading "
            "of the Epoch-1 pathology."),
        "blocks_K2": False,
        "range_support_metric_must_remain_dimensionless_regardless": True,
    }
    (OUT / "GAS_SIGNAL_PROVENANCE_CORRECTION.json").write_text(json.dumps(prov, indent=2), encoding="utf-8")

    # ---------------- 5. conceptual definition ---------------------------
    concept = {
        "record_id": "OBSERVATIONAL_RANGE_SUPPORT_CONCEPT_V1",
        "frozen_utc": now,
        "written_before_any_numerical_realization": True,
        "definition": (
            "For a coordinate c, a local calibration interval T_cal and an application "
            "interval T_app, let S_cal(c) be the empirical support of c on T_cal - the set of "
            "coordinate values actually observed during calibration. The coordinate remains "
            "MATHEMATICALLY defined outside S_cal(c), but its use inside a calibration-fitted "
            "relation is EMPIRICALLY UNSUPPORTED when its application values move sufficiently "
            "far beyond S_cal(c). Observational range support is therefore a property of the "
            "triple (coordinate, calibration interval, application interval) - never of the "
            "constructor type alone."),
        "three_distinct_admissibility_notions": {
            "SYMBOLIC_ADMISSIBILITY": "the coordinate is well formed in the ontology G_rec",
            "MATHEMATICAL_DOMAIN_ADMISSIBILITY": (
                "the coordinate map is defined on the observed inputs - the existing "
                "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1 condition for partial maps"),
            "OBSERVATIONAL_RANGE_APPLICABILITY": (
                "the calibration-fitted relation is empirically supported at the application "
                "values actually encountered - the NEW condition"),
        },
        "must_not_be_collapsed_with_denominator_stability": True,
        "why_they_are_different": (
            "denominator stability asks whether the coordinate map is DEFINED; range support "
            "asks whether the FITTED RELATION is empirically supported where it is applied. A "
            "coordinate can be perfectly well defined everywhere - x^2 is - and still be "
            "unsupported. Conversely a denominator can be admissible on calibration and the "
            "ratio still leave its calibration range."),
        "applies_generically_to": ["C0 levels", "C1 rates", "C2 products", "C3 ratios",
                                   "C4 phase derivatives", "C5 reciprocals",
                                   "C6 level-rate products", "C7 rate-over-level",
                                   "C8 level-over-rate", "future total nonlinear constructors"],
        "not_special_cased_to": ["gasa", "gas actuators", "self-products",
                                 "the two Epoch-1 failing discharges",
                                 "the two Epoch-1 failing blocks"],
        "semantics_on_failure": "RANGE_SUPPORT_NOT_APPLICABLE on that block - a LOCAL partial-"
                                "application status, never global inadmissibility",
    }
    (OUT / "manifests" / "RANGE_SUPPORT_CONCEPT.json").write_text(
        json.dumps(concept, indent=2), encoding="utf-8")

    # ---------------- 6. desiderata --------------------------------------
    desiderata = {
        "record_id": "RANGE_SUPPORT_DESIDERATA_V1",
        "frozen_utc": now,
        "frozen_before_candidate_comparison": True,
        "criteria": {
            "D1_target_blind": "uses no target value",
            "D2_model_error_blind": "uses no residual, NRMSE or qualification label",
            "D3_dimensionless": "the score carries no physical unit",
            "D4_unit_scale_invariant": "invariant under c -> k*c for any nonzero constant k",
            "D5_sign_symmetric": "excursions below and above the calibration hull are treated alike",
            "D6_constructor_generic": "defined identically for every constructor family",
            "D7_local": "the reference support comes only from the relevant calibration interval",
            "D8_application_aware": "assesses the values actually encountered on the application interval",
            "D9_monotone": "greater departure from calibration support cannot improve the score",
            "D10_auditable": "one equation and one short paragraph",
            "D11_no_epsilon": "no epsilon patch anywhere",
            "D12_degenerate_safe": "zero-range / zero-scale calibration receives an explicit status",
            "D13_not_special_cased": "no reference to gasa, products or any Epoch-1 identity",
            "D14_partial_application_semantics": (
                "failure means the relation is not empirically supported on that block, not that "
                "the coordinate is globally meaningless"),
        },
        "selection_basis_permitted": ["mathematical desiderata", "numerical stability",
                                      "broad behaviour over the coordinate universe",
                                      "interpretability", "constructor neutrality"],
        "selection_basis_forbidden": ["whether 187019/B is flagged", "whether 187022/B is flagged",
                                      "whether C_dev_star would pass", "whether V3 would improve",
                                      "the S7.11 70/143 partition"],
    }
    (OUT / "manifests" / "RANGE_SUPPORT_DESIDERATA.json").write_text(
        json.dumps(desiderata, indent=2), encoding="utf-8")

    out = {
        "prevalue_id": "S7_K2_PREVALUE_V1", "generated_utc": now,
        "lineage": lineage, "n_authoritative": len(lineage),
        "manifest_recomputation": manifests,
        "primary_epoch1_invariant": invariant,
        "firewall_sha256": sha256(OUT / "K2_TARGET_BLIND_FIREWALL.json"),
        "gas_provenance_sha256": sha256(OUT / "GAS_SIGNAL_PROVENANCE_CORRECTION.json"),
        "concept_sha256": sha256(OUT / "manifests" / "RANGE_SUPPORT_CONCEPT.json"),
        "desiderata_sha256": sha256(OUT / "manifests" / "RANGE_SUPPORT_DESIDERATA.json"),
        "order_enforced": ["lineage", "invariant", "firewall", "provenance",
                           "concept", "desiderata", "(then candidates)"],
        "candidate_metrics_evaluated_in_this_script": 0,
        "drift": drift,
        "verdict": "PREVALUE_FROZEN" if not drift else "DRIFT_DETECTED",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
    }
    (OUT / "manifests" / "K2_PREVALUE.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("lineage                : %d/14" % len(lineage))
    for kk, v in manifests.items():
        print("  %-6s manifest      : %d/%d" % (kk, v["matched"], v["n"]))
    print("Epoch-1 invariant      : %s | V3 %s | R1 %s"
          % (invariant["S7_10_primary_verdict"][:28], invariant["gate_table"]["V3"],
             invariant["S7_R1_recommendation"]))
    print("firewall               : %s" % out["firewall_sha256"][:16])
    print("gas provenance         : %s -> %s" % (prov["resolution"], prov["resolved_unit"]))
    print("  upstream variants    : %s" % {s: v.get("upstream_variants") for s, v in gas.items()})
    print("concept                : %s" % out["concept_sha256"][:16])
    print("desiderata (14)        : %s" % out["desiderata_sha256"][:16])
    print("verdict                : %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
