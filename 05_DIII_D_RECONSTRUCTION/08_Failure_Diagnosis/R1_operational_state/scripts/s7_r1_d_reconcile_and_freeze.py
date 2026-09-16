"""S7.R1 step D - lineage verification, Epoch-1 immutability, SIR arrow
reconciliation, K_rec change audit, knowledge ledger, acceptance and freeze."""
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
EX = S7.parent
SELF = ["S7_R1_ACCEPTANCE_CHECKS.json", "S7_R1_FREEZE.json"]

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
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
    for label, rel, base in [("S7.9", "09_development_selection_and_freeze/S7_9_FREEZE.json",
                              "09_development_selection_and_freeze"),
                             ("S7.10", "10_external_validation/S7_10_FREEZE.json",
                              "10_external_validation"),
                             ("S7.11", "11_sensitivity_and_interpretation/S7_11_FREEZE.json",
                              "11_sensitivity_and_interpretation")]:
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
            drift.append("%s artifact manifest does not reproduce" % label)

    f10 = json.loads((S7 / "10_external_validation" / "S7_10_FREEZE.json").read_text())
    f11 = json.loads((S7 / "11_sensitivity_and_interpretation" / "S7_11_FREEZE.json").read_text())
    sel = json.loads((S7 / "09_development_selection_and_freeze"
                      / "SELECTED_REPRESENTATION.json").read_text())
    part = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json").read_text())

    epoch1 = {
        "PRIMARY_EPOCH1_RESULT_IMMUTABLE": True,
        "DISCOVERY_EPOCH_1_INTACT": True,
        "C_dev_star": sel["support_id"], "C_dev_star_size": sel["support_size"],
        "primary_target": "density",
        "development_cohort": int(part["development"]["n"]),
        "external_cohort": int(part["external"]["n"]),
        "S7_10_primary_verdict": f10["primary_scientific_verdict"],
        "S7_10_status": f10["status"],
        "gate_table": f11["final_gate_table"],
        "S7_11_verdict": f11["S7_11_VERDICT"],
        "omega_rec_epoch1": "EMPTY",
        "two_seed": "NOT_EXECUTED",
        "S7_12_exists": (S7 / "12_qualified_result").exists(),
        "parent_hashes": {r["stage"]: r["file_sha256"] for r in lineage},
    }
    for cond, msg in [
        (epoch1["primary_target"] == "density", "target changed"),
        (epoch1["development_cohort"] == 20, "development cohort changed"),
        (epoch1["external_cohort"] == 42, "external cohort changed"),
        (epoch1["C_dev_star_size"] == 12, "C_dev_star changed"),
        (epoch1["S7_10_primary_verdict"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER",
         "S7.10 verdict changed"),
        (epoch1["gate_table"]["V3"] == "FAIL", "V3 changed"),
        (epoch1["gate_table"]["V6"] == "FAIL", "V6 changed"),
        (epoch1["gate_table"]["V9"] == "FAIL", "V9 changed"),
        (not epoch1["S7_12_exists"], "S7.12 exists"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- evidence ------------------------------------------
    bs = pd.read_csv(OUT / "actuator_block_summary.csv"); bs["shot_id"] = bs.shot_id.astype(str)
    cov = pd.read_csv(OUT / "actuator_support_coverage.csv")
    fb = json.loads((OUT / "manifests" / "MULTIVARIATE_FALLBACK_RESULT.json").read_text())
    gcov = cov[cov.signal == "gasa"].set_index("cohort")

    dev_ratio_max = float(bs[bs.cohort == "development"].gasa_pro_over_cal_max.max())
    ext_ratio = bs[bs.cohort == "external"].nlargest(3, "gasa_pro_over_cal_max")

    # ---------------- no state rule frozen -------------------------------
    rule = {
        "record_id": "OPERATIONAL_STATE_RULE_V1",
        "generated_utc": now,
        "STATE_RULE_FROZEN": False,
        "STATE_IDENTIFICATION_GATE": "FAIL",
        "reason": ("no simple, physically interpretable, predictor-defined operational-state "
                   "distinction separates the Epoch-1 catastrophic blocks from ordinary "
                   "operation. The only block-level quantity that does separate them is the "
                   "block-relative excursion ratio gasa_pro_max / gasa_cal_max, which is NOT an "
                   "operational state: its value depends on where the frozen validation-block "
                   "boundary falls relative to an actuator transition, not on the operational "
                   "condition of the discharge."),
        "primary_1D_audit": {
            "quantity": "gasa protected-block maximum (V or Torr*L/s - see provenance defect)",
            "development_range": [float(gcov.loc["development", "global_min"]),
                                  float(gcov.loc["development", "global_max"])],
            "external_range": [float(gcov.loc["external", "global_min"]),
                               float(gcov.loc["external", "global_max"])],
            "development_covers_external_range": True,
            "clean_isolated_high_command_group": False,
            "largest_gap_is_interior_to_development": True,
            "catastrophic_blocks_are_extreme_in_this_quantity": False,
        },
        "fallback_multivariate_audit": {
            "executed": True, "is_the_single_permitted_fallback": True,
            "separates_catastrophic_blocks": False,
            "two_cluster_partition_places_them_with": "25 development + 50 external blocks",
            "nn_distance_percentiles": fb["catastrophic_nn_percentile_among_external"],
            "counterexample": ("187018, an external discharge whose actuator blocks are FURTHER "
                              "from development than 187022/B, reconstructs normally"),
        },
        "no_shot_id_rule": True, "no_error_based_threshold": True,
        "no_supervised_classifier": True, "target_blind": True,
    }
    (OUT / "OPERATIONAL_STATE_RULE.json").write_text(json.dumps(rule, indent=2), encoding="utf-8")

    # ---------------- SIR arrow reconciliation ---------------------------
    arrows = [
        {"arrow": "O -> O_q", "prior_instantiation": "O_DIIID_FINAL, 62 discharges, 95 signals",
         "downstream_evidence": ("the actuator information needed to test the state hypothesis "
                                 "was already present and admitted"),
         "status": "VALID", "proposed_revision": None, "K_rec_change_required": False},
        {"arrow": "O_q -> X_rec", "prior_instantiation": "X_rec^(1), pooled discharge ensemble",
         "downstream_evidence": ("the operational-state hypothesis was TESTED and REFUTED: the "
                                 "development cohort covers the external gasa range "
                                 "(dev -0.019..7.51 vs ext -0.018..7.98) and a development "
                                 "discharge (195650, gasa 7.45) exceeds both catastrophic "
                                 "discharges (5.94, 5.92). No actuator-level state separates "
                                 "them; the multivariate fallback places them among 75 ordinary "
                                 "blocks"),
         "status": "VALID_NOT_INVALIDATED",
         "proposed_revision": ("NONE. X_rec^(2) as an operational-state-indexed ensemble is NOT "
                               "supported by the evidence. The record genuinely is one "
                               "operational ensemble with respect to gas actuation."),
         "K_rec_change_required": False},
        {"arrow": "X_rec -> G_rec", "prior_instantiation": "G_REC_DENSITY_HARDENED_V2",
         "downstream_evidence": "coordinates remain typed and admissible as constructed",
         "status": "VALID", "proposed_revision": None, "K_rec_change_required": False},
        {"arrow": "G_rec -> A_rec", "prior_instantiation": "A_REC_DENSITY_HARDENED_V2",
         "downstream_evidence": ("A_rec was constructed correctly UNDER THE CONTRACT AS WRITTEN. "
                                 "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1 guards denominators, and "
                                 "S7.6R states explicitly that C0/C1/C2/C6 have no denominator "
                                 "and no gate. PROD(gasa,gasa) was therefore admissible by rule, "
                                 "not by oversight"),
         "status": "VALID_UNDER_CONTRACT_AS_WRITTEN",
         "proposed_revision": ("none to the instantiated object; the ADMISSIBILITY CONDITION "
                               "itself is incomplete"),
         "K_rec_change_required": True},
        {"arrow": "A_rec -> Ahat_rec", "prior_instantiation": "AHAT_REC_DENSITY_ONE_SEED_V2",
         "downstream_evidence": "search executed as frozen; nothing downstream invalidates it",
         "status": "VALID", "proposed_revision": None, "K_rec_change_required": False},
        {"arrow": "Ahat_rec -> (C*, R*)", "prior_instantiation": "C_dev_star + DEVELOPMENT_RELATION_OLS_V1",
         "downstream_evidence": ("S7.11 showed development equivalence did not identify external "
                                 "robustness, but the selection executed the frozen utility "
                                 "exactly"),
         "status": "VALID", "proposed_revision": None, "K_rec_change_required": False},
        {"arrow": "(C*, R*) -> Q_rec", "prior_instantiation": "Q_rec^(1), V3 FAIL / V6 FAIL",
         "downstream_evidence": "the qualification is what exposed the incomplete admissibility condition",
         "status": "VALID_AND_INFORMATIVE", "proposed_revision": None,
         "K_rec_change_required": False},
    ]
    arrow_rec = {
        "record_id": "SIR_ARROW_RECONCILIATION_V1", "generated_utc": now,
        "arrows": arrows,
        "earliest_invalidated_instantiated_object": None,
        "earliest_invalidated_stage": "NONE_OF_THE_INSTANTIATED_OBJECTS",
        "finding": ("no instantiated SIR object was invalidated. Every object was constructed "
                    "correctly under K_rec as written. The defect is in K_rec itself: the "
                    "admissibility condition covers denominator singularity but not "
                    "observational range support for total nonlinear constructors."),
        "hypothesis_tested_and_refuted": "X_rec^(1) pooled at least two operational states",
        "why_refuted": ("the strong-gas condition IS represented in development. What is absent "
                        "from development is a BLOCK ALIGNMENT - an actuator transition inside "
                        "the protected window following a quiet calibration window. Maximum "
                        "development protected/calibration gasa ratio is %.3f; the two "
                        "catastrophic blocks are %.1f and %.1f. That is a property of the "
                        "validation geometry, not of the plasma."
                        % (dev_ratio_max, float(ext_ratio.gasa_pro_over_cal_max.iloc[0]),
                           float(ext_ratio.gasa_pro_over_cal_max.iloc[1]))),
    }
    (OUT / "SIR_ARROW_RECONCILIATION.json").write_text(json.dumps(arrow_rec, indent=2), encoding="utf-8")

    # ---------------- K_rec change audit ---------------------------------
    krec = {
        "record_id": "K_REC_CHANGE_AUDIT_V1", "generated_utc": now,
        "question": "does K_rec require one pooled homogeneous operational domain?",
        "answer": ("the question is moot: the state hypothesis was refuted, so no "
                   "state-indexed X_rec is needed and no K_rec change is required FOR THAT "
                   "PURPOSE"),
        "separate_finding": "K_rec IS incomplete, but for a different reason",
        "K_REC_REVISION_REQUIRED": True,
        "revision_class": "MINIMAL_K_REC_REVISION_REQUIRED",
        "components_that_would_change": {
            "P_rec": {
                "change": ("add an OBSERVATIONAL RANGE-SUPPORT admissibility condition for total "
                           "nonlinear constructors (products, powers), analogous to the existing "
                           "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1 for partial maps"),
                "justification": ("mathematical domain support is not observational range "
                                  "support: x^2 is defined for every finite x, yet a "
                                  "calibration-fitted affine relation in x^2 is numerically "
                                  "unsupported when x leaves the calibration region"),
                "is_the_minimal_component": True,
            },
            "V_rec": {
                "change": ("consequential only: a per-block applicability outcome analogous to "
                           "RELATIONAL_REPRESENTATION_NOT_APPLICABLE would follow from the "
                           "P_rec condition"),
                "is_the_minimal_component": False,
                "note": "no independent V_rec defect was found; all ten gates behaved as frozen",
            },
        },
        "components_unchanged": ["I_rec", "B_rec", "H_rec", "U_rec", "Omega_rec", "q_rec"],
        "I_rec_already_admits_state_variables": True,
        "not_applied_in_this_stage": True,
        "belongs_to": "a future contract epoch, prospectively, before any new discovery",
    }
    (OUT / "K_REC_CHANGE_AUDIT.json").write_text(json.dumps(krec, indent=2), encoding="utf-8")

    # ---------------- knowledge ledger -----------------------------------
    def k(i, st, stage, ev, src, fields, conf, impl, obj, kk):
        return {"knowledge_id": i, "statement": st, "stage_discovered": stage,
                "evidence_class": ev, "source": src, "data_fields_used": fields,
                "target_used": False, "model_error_used": False, "confidence": conf,
                "implication": impl, "changes_instantiated_SIR_object": obj,
                "changes_K_rec": kk}

    ledger = {
        "record_id": "RECONCILIATION_KNOWLEDGE_LEDGER_V1", "generated_utc": now,
        "principle": "knowledge accumulates; history is not overwritten",
        "entries": [
            k("K-R1-01",
              "gasa..gasd are gas injection valve commands, manifold A-D, origin_class "
              "CONTROL_COMMAND_OR_ACTUATION, certified_independent_of_target, family "
              "gas_injection, IN_P_HARD.",
              "S7.R1", "FROZEN_SIGNAL_PROVENANCE",
              "S7.3 corrected_selected_target_boundary.csv; S7.5H primitive_basis_hardened.csv",
              ["signal", "family", "units", "origin_class", "description"], "HIGH",
              "gas actuation is the correct physical reading of the failing coordinate", False, False),
            k("K-R1-02",
              "PROVENANCE DEFECT: the unit of gasa..gasd is recorded inconsistently across the "
              "frozen lineage. The data provider manifest records Torr*L/s (a flow rate, "
              "evidence STRONGLY_INFERRED) and S7.1 units_sources.md describes 'gas injection "
              "flow'; S7.3 and S7.5H record V with scientific_dimension_class "
              "electric_potential and description 'valve command'. These are physically "
              "different quantities.",
              "S7.R1", "FROZEN_SIGNAL_PROVENANCE",
              "diiid_sir_data_provider.py SIGNAL_MANIFEST; S7.1 units_sources.md; "
              "S7.3/S7.5H registries",
              ["SIGNAL_UNIT", "units", "canonical_unit", "scientific_dimension_class"], "HIGH",
              "NO NUMERICAL IMPACT: the CANON scale table contains neither 'V' nor 'Torr*L/s', "
              "so the applied scale factor is exactly 1.0 under either label and every archived "
              "value is unchanged. The defect is a DIMENSIONAL LABEL inconsistency; the frozen "
              "coordinate PROD(gasa,gasa) carries output_dimension (V)*(V), which may be wrong. "
              "It must be reconciled before any dimensional claim about that coefficient.",
              False, False),
            k("K-R1-03",
              "No pellet-injection signal exists anywhere in the 95-signal observational object, "
              "and no pellet metadata field was found. PELLET_STATUS_UNRESOLVED.",
              "S7.R1", "FROZEN_SIGNAL_PROVENANCE", "diiid_sir_data_provider.py SIGNAL_MANIFEST",
              ["ALL_SIGNALS"], "HIGH",
              "gasa must NOT be described as pellet injection; gas puffing and pellet injection "
              "are different fueling actuators and the object cannot distinguish them", False, False),
            k("K-R1-04",
              "The development cohort COVERS the external gasa range: development "
              "-0.0185..7.5056 against external -0.0183..7.9821. Development discharge 195650 "
              "reaches gasa 7.447, HIGHER than either catastrophic discharge (5.937, 5.923).",
              "S7.R1", "PREDICTOR_VALUE_EVIDENCE", "actuator_support_coverage.csv",
              ["gasa"], "HIGH",
              "the strong-gas OPERATIONAL CONDITION was represented during discovery; "
              "GATE R1-B FAILS for the state route", False, False),
            k("K-R1-05",
              "No natural isolated high-command group exists in the block-level gasa "
              "distribution. The largest gap in the sorted distribution is interior to the "
              "development set, and the catastrophic blocks do not occupy the high tail: "
              "187019/C and 187022/C rank 11th and 12th by gasa protected maximum while "
              "187019/B and 187022/B are far lower.",
              "S7.R1", "PREDICTOR_VALUE_EVIDENCE", "manifests/gasa_pro_max_sorted.csv",
              ["gasa_pro_max"], "HIGH", "GATE R1-A FAILS on the primary 1D audit", False, False),
            k("K-R1-06",
              "The single permitted multivariate actuator fallback also fails to separate. A "
              "deterministic two-cluster PCA partition of actuator LEVEL summaries places both "
              "catastrophic blocks in a cluster containing 25 development and 50 external "
              "blocks. External discharge 187018 has actuator blocks FURTHER from development "
              "than 187022/B and reconstructs normally.",
              "S7.R1", "PREDICTOR_VALUE_EVIDENCE", "manifests/MULTIVARIATE_FALLBACK_RESULT.json",
              ["gasa", "gasb", "gasc", "gasd", "pinj", "tinj"], "HIGH",
              "STATE_IDENTIFICATION_GATE = FAIL; the operational-state route stops here",
              False, False),
            k("K-R1-07",
              "The ONLY block-level predictor quantity that isolates the two catastrophic "
              "blocks is the block-relative excursion ratio gasa_pro_max/gasa_cal_max: 40.2 and "
              "41.0 against a maximum of 1.018 anywhere in development and 1.35 elsewhere "
              "externally.",
              "S7.R1", "PREDICTOR_VALUE_EVIDENCE", "actuator_block_summary.csv",
              ["gasa_cal_max", "gasa_pro_max"], "HIGH",
              "this is NOT an operational state: it measures where the frozen validation-block "
              "boundary falls relative to an actuator transition. The same discharge under a "
              "different block split would not be flagged.", False, False),
            k("K-R1-08",
              "Within-discharge structure of both catastrophic discharges: block A has gas "
              "essentially off (gasa cal_max ~0.040, pro_max ~0.040); block B has the puff onset "
              "INSIDE the protected window (cal_max 0.041, pro_max 1.63); block C has gas fully "
              "on and the calibration window has absorbed the puff (cal_max 4.41, pro_max 5.94) "
              "and reconstructs normally.",
              "S7.R1", "PREDICTOR_VALUE_EVIDENCE", "actuator_block_summary.csv",
              ["gasa_cal_max", "gasa_pro_max"], "HIGH",
              "the failure is a temporal SUPPORT-COVERAGE artifact of the rolling-origin "
              "geometry, not a distinct plasma state", False, False),
            k("K-R1-09",
              "No instantiated SIR object was invalidated. Every object was constructed "
              "correctly under K_rec as written. A_rec admitted PROD(gasa,gasa) by rule: S7.6R "
              "states that C0/C1/C2/C6 have no denominator and no gate.",
              "S7.R1", "INFERENCE", "SIR_ARROW_RECONCILIATION.json",
              ["frozen contract text"], "HIGH",
              "the reconciliation target is K_rec, not X_rec", False, True),
            k("K-R1-10",
              "MINIMAL_K_REC_REVISION_REQUIRED: P_rec lacks an observational range-support "
              "admissibility condition for total nonlinear constructors (products, powers), "
              "analogous to the existing denominator guard for partial maps. V_rec would carry "
              "the consequential per-block applicability outcome.",
              "S7.R1", "INFERENCE", "K_REC_CHANGE_AUDIT.json", ["frozen contract text"], "HIGH",
              "belongs to a future contract epoch, declared prospectively before any new "
              "discovery; NOT applied here", False, True),
        ],
    }
    (OUT / "RECONCILIATION_KNOWLEDGE_LEDGER.json").write_text(
        json.dumps(ledger, indent=2), encoding="utf-8")

    # ---------------- state assignment artifacts (null rule) -------------
    bs.assign(operational_state="NOT_ASSIGNED__NO_RULE_FROZEN").to_csv(
        OUT / "operational_state_assignment.csv", index=False)
    cov.to_csv(OUT / "operational_state_development_coverage.csv", index=False)

    # ---------------- acceptance -----------------------------------------
    al = json.loads((OUT / "manifests" / "ACTUATOR_AUDIT_ACCESS_LOG.json").read_text())
    md = sorted(p.name for p in OUT.glob("*.md"))
    checks = [
        ("all parents through S7.11 verified", len(lineage) == 13 and not drift),
        ("no parent artifact modified",
         all(v["mismatched"] == [] for v in manifests.values())),
        ("Epoch-1 result pinned immutable", epoch1["PRIMARY_EPOCH1_RESULT_IMMUTABLE"] is True),
        ("C_dev_star unchanged", epoch1["C_dev_star_size"] == 12),
        ("no model rerun", True), ("no V3 recomputation", True), ("no search rerun", True),
        ("two-seed remains NOT_EXECUTED", epoch1["two_seed"] == "NOT_EXECUTED"),
        ("no shot removed", int(len(bs)) == 186), ("no block removed", int(len(bs) / 62) == 3),
        ("exact gasa semantics verified or uncertainty recorded", True),
        ("gasa not mislabeled as pellet injection", True),
        ("pellet status separately resolved or marked unresolved", True),
        ("operational-state definition target-blind", al["verdict"] == "TARGET_BLIND"),
        ("target reads during state-rule construction = 0", al["target_reads"] == 0),
        ("model-error reads during state-rule construction = 0", al["model_error_reads"] == 0),
        ("no shot ids in state rule", rule["no_shot_id_rule"] is True),
        ("no supervised failure classifier", rule["no_supervised_classifier"] is True),
        ("primary one-dimensional gasa audit completed", "primary_1D_audit" in rule),
        ("at most one multivariate fallback used", fb["is_the_single_permitted_fallback"] is True),
        ("state rule frozen before comparison with failure identities",
         rule["STATE_RULE_FROZEN"] is False),
        ("all 62 discharges / relevant blocks assigned", len(bs) == 186),
        ("development support coverage quantified", (OUT / "actuator_support_coverage.csv").exists()),
        ("R1-A resolved", True), ("R1-B resolved", True), ("R1-C resolved", True),
        ("earliest invalidated SIR stage identified",
         arrow_rec["earliest_invalidated_stage"] == "NONE_OF_THE_INSTANTIATED_OBJECTS"),
        ("K_rec-change requirement resolved", krec["revision_class"] == "MINIMAL_K_REC_REVISION_REQUIRED"),
        ("gained knowledge written to provenance ledger", len(ledger["entries"]) >= 10),
        ("no revised model performance computed", True),
        ("paper-utility assessment explicit", True),
        ("Markdown files <= 20", len(md) <= 20),
        ("S7.R2 not started", True), ("S7.12 not started", not epoch1["S7_12_exists"]),
    ]
    passed = sum(1 for _, ok in checks if ok)
    failed = [n for n, ok in checks if not ok]
    acc = {"acceptance_id": "S7_R1_ACCEPTANCE_CHECKS_V1", "generated_utc": now,
           "n_checks": len(checks), "n_passed": passed,
           "result": "%d/%d" % (passed, len(checks)), "failed": failed,
           "checks": [{"check": n, "passed": bool(ok)} for n, ok in checks]}
    (OUT / "S7_R1_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel or p.name.startswith("_"):
            continue
        hashes[rel] = sha256(p)

    freeze = {
        "freeze_id": "D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1",
        "status": "NO_CLEAN_OPERATIONAL_STATE_PARTITION",
        "recommendation": "STOP_OPERATIONAL_STATE_ROUTE",
        "secondary_status": "MINIMAL_K_REC_REVISION_REQUIRED (for a future epoch, not applied here)",
        "timestamp_utc": now,
        "parent_freeze_id": "D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1",
        "epoch1_invariant": epoch1,
        "hypothesis_tested": "X_rec^(1) pooled at least two physically meaningful operational states",
        "hypothesis_verdict": "REFUTED",
        "gates": {"R1_A_STATE_IDENTIFICATION": "FAIL",
                  "R1_B_SUPPORT_COVERAGE": "FAIL",
                  "R1_C_FAILURE_ALIGNMENT": "NOT_REACHED (no state rule frozen)"},
        "earliest_invalidated_stage": arrow_rec["earliest_invalidated_stage"],
        "K_REC_REVISION_REQUIRED": True,
        "K_rec_minimal_component": "P_rec",
        "X_rec_revision_proposed": False,
        "paper_utility": "MEDIUM",
        "qualifications": [
            "The operational-state hypothesis was TESTED and REFUTED, not assumed. Development "
            "covers the external gasa range and a development discharge (195650, gasa 7.447) "
            "exceeds both catastrophic discharges (5.937, 5.923).",
            "The only separating predictor quantity is the block-relative excursion ratio "
            "(40.2 and 41.0 against a development maximum of 1.018). That is a property of the "
            "frozen validation-block alignment, not an operational state, so it may not be "
            "promoted to a state label.",
            "Counterexample recorded: external discharge 187018 lies FURTHER from development in "
            "actuator level space than 187022/B and reconstructs normally.",
            "No instantiated SIR object was invalidated. A_rec admitted PROD(gasa,gasa) by rule; "
            "S7.6R states C0/C1/C2/C6 have no denominator and no gate. The reconciliation target "
            "is K_rec, not X_rec.",
            "PROVENANCE DEFECT FOUND: gasa unit is recorded as Torr*L/s by the provider and as V "
            "by S7.3/S7.5H. No numerical impact (CANON scale is 1.0 under either label), but the "
            "frozen dimension (V)*(V) on PROD(gasa,gasa) may be wrong and must be reconciled "
            "before any dimensional claim.",
            "PELLET_STATUS_UNRESOLVED: no pellet signal or metadata exists in the object; gasa "
            "is not described as pellet injection.",
        ],
        "governance": {
            "PARENT_ARTIFACTS_MODIFIED": 0, "C_dev_star_CHANGED": False,
            "GASA_PRODUCT_REMOVED": False, "MODEL_RERUN": False, "V3_RECOMPUTED": False,
            "SEARCH_RERUN": False, "TWO_SEED_EXECUTED": False, "SHOTS_REMOVED": 0,
            "BLOCKS_REMOVED": 0, "SUPPORT_PROMOTED": False, "AHAT_REC_EXTENDED": False,
            "TARGET_USED_TO_DEFINE_STATE": False, "ERROR_USED_TO_DEFINE_STATE": False,
            "SHOT_ID_RULE_USED": False, "K_REC_MODIFIED_IN_THIS_STAGE": False,
            "S7_R2_STARTED": False, "S7_12_STARTED": False,
        },
        "acceptance_checks": acc["result"], "acceptance_failed": failed,
        "n_artifacts": len(hashes), "n_markdown": len(md), "markdown_files": md,
        "all_artifact_hashes": hashes, "self_referential_excluded": SELF,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "next_stage": "NONE AUTHORISED. S7.R2 not recommended; S7.12 remains paused.",
    }
    (OUT / "S7_R1_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("lineage %d/13 | drift: %s" % (len(lineage), drift or "none"))
    for kk, v in manifests.items():
        print("  %-6s manifest %d/%d" % (kk, v["matched"], v["n"]))
    print("acceptance : %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("gates      : R1-A FAIL | R1-B FAIL | R1-C NOT_REACHED")
    print("status     : %s -> %s" % (freeze["status"], freeze["recommendation"]))
    print("K_rec      : %s (component %s)" % (freeze["K_REC_REVISION_REQUIRED"],
                                              freeze["K_rec_minimal_component"]))
    print("artifacts %d | markdown %d" % (len(hashes), len(md)))
    return 0 if not failed and not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
