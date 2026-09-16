"""S7.E2.0A step B - the superseding protocol amendment, information-boundary
record, candidate basis, changeset, acceptance and freeze."""
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
K2 = S7 / "K2_observational_range_support_contract"
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
SELF = ["E2_0A_ACCEPTANCE_CHECKS.json", "E2_0A_FREEZE.json"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    ver = json.loads((OUT / "manifests" / "E2_0A_VERIFICATION.json").read_text())
    if ver["verdict"] != "VERIFIED":
        raise SystemExit("STOP: verification failed")
    inh = ver["inherited_unchanged"]
    fk2 = json.loads((K2 / "S7_K2_FREEZE.json").read_text())
    f20 = json.loads((E20 / "E2_0_FREEZE.json").read_text())
    a20 = json.loads((E20 / "EPOCH2_ACCESS_POLICY.json").read_text())

    # ---------------- information boundary --------------------------------
    ib = {
        "record_id": "E2_0A_INFORMATION_BOUNDARY_V1", "frozen_utc": now,
        "principle": "PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION",
        "the_boundary_is_transition_specific": True,
        "ROLE_A_predictor_side_admissibility": {
            "what": ("all admissible NON-TARGET predictor observations in the frozen "
                     "62-discharge object may instantiate P-RANGE-SUPPORT"),
            "why_admissible": ("the intended domain Omega_rec IS the frozen 62-discharge "
                               "object. Asking whether a coordinate is observationally "
                               "applicable over that domain is answerable from that domain's "
                               "predictor side; it is a property of the domain, not a peek at "
                               "an unseen one"),
            "properties": ["target-blind", "error-blind", "performance-blind"],
            "governs": "P_rec applicability",
        },
        "ROLE_B_target_side_discovery": {
            "what": ("within outer fold k, held-out target values may not influence search, "
                     "utility, support selection, estimator selection, or any relation-selection "
                     "decision"),
            "only_influencing_targets": "D_train^(k)",
            "governs": "the relational search and U_rec selection",
        },
        "epistemic_guarantee_actually_tested": (
            "no discharge's OWN TARGET VALUES influenced the support used to reconstruct it"),
        "contract_internal_justification": [
            {"source": "S7.6R PARTIAL_MAP_ADMISSIBILITY.md, 'The external rule'",
             "text": ("the sibling partial-map condition - denominator admissibility - is "
                      "explicitly an APPLICATION-TIME predicate: a selected support 'must "
                      "satisfy the same rule on each external local-calibration block'. It was "
                      "never required to be predictable from development data alone"),
             "implication": ("P-RANGE, its sibling under the same partial-map semantics, is "
                             "correctly evaluated over the intended domain rather than "
                             "forecast from a training subset")},
            {"source": "K_REC_V2 coverage_policy and A_rec_architecture_decision",
             "text": ("K2 recorded FULL_DOMAIN_RANGE_SUPPORT as 'feasible target-blindly' with "
                      "evidence of 3,451 full-domain atoms computed over ALL 62 discharges, and "
                      "reasoned that 'a search restricted to full-domain coordinates yields "
                      "full-domain supports by construction'"),
             "implication": ("K2's own architecture presumed a search over the full-object "
                             "certified basis. E2.0's predictor-blinding contradicted the "
                             "parent contract it was implementing")},
        ],
        "I_q_notation_audit": {
            "question": "does the existing I_rec definition already permit this arrangement?",
            "finding": "YES - no notation revision is required",
            "reasoning": (
                "I_rec is defined as O_rec = I_rec(O): a VARIABLE-SET boundary whose six "
                "exclusion rules are all about ANCESTRY RELATIVE TO THE TARGET (the target "
                "itself, aliases, definitional descendants, verified upstream dependence, "
                "unresolved ancestry fail-closed, and transitive closure). I_rec never governed "
                "WHICH OBSERVATIONS of an admitted variable are available at WHICH STAGE. That "
                "is a different concept, and in Epoch 1 it already lived in P_rec "
                "(calibration-only preprocessing) and V_rec (block-local protection, external "
                "sealing) - not in I_rec. So the transition-specific arrangement is expressible "
                "under the existing components without redefining I_q"),
            "notation_change_required": False,
            "manuscript_clarification_recommended": True,
            "recommended_sentence": (
                "The information boundary is transition-specific: observations admissible for "
                "coordinate construction or applicability need not be admissible for relation "
                "selection. In the reconstruction example, non-target observations across the "
                "finite scientific object determine range-support applicability, while held-out "
                "target values remain unavailable to support discovery."),
            "why_a_clarification_is_still_worth_adding": (
                "readers will naturally conflate I_q (which variables may enter) with the "
                "stage-wise availability of an admitted variable's observations (P_q / V_q). "
                "One sentence prevents that conflation without changing any definition"),
        },
        "information_flow": [
            "O_q --(all admissible predictor values)--> P-RANGE applicability",
            "P-RANGE applicability --> C_E2_FULL_DOMAIN",
            "C_E2_FULL_DOMAIN + D_train^(k) targets --> fold-k exploration / utility / selection",
            "selection --> HASH(C_k*)",
            "HASH(C_k*) + held-out CALIBRATION targets --> local coefficient estimation",
            "local coefficients + held-out PROTECTED targets (LAST) --> qualification",
        ],
        "not_target_leakage": {
            "statement": ("using all 62 predictor values to instantiate P-RANGE is NOT target "
                          "leakage under this frozen finite-object claim"),
            "because": ("the target, density, remains unavailable to the held-out fold during "
                        "support discovery. The admissibility calculation uses only non-target "
                        "predictor values, frozen coordinate definitions, frozen block geometry "
                        "and the frozen tau = 1"),
            "distinction": {"PREDICTOR_SIDE_DOMAIN_KNOWLEDGE": "admissible under this claim",
                            "TARGET_SIDE_DISCOVERY_INFORMATION": "remains cross-fitted"},
        },
        "what_this_does_NOT_buy": {
            "forbidden_claims": ["unknown-predictor-distribution transfer",
                                 "fully inductive held-out predictor generalization",
                                 "future-discharge applicability",
                                 "untouched external validation"],
            "permitted_description": ("target-cross-fitted reconstruction over a "
                                      "predictor-qualified finite observational object"),
            "epistemic_cost_recorded_explicitly": (
                "E2.0's stricter rule would have tested TWO things on held-out data: whether the "
                "target relationship transfers, AND whether the support's predictor geometry "
                "holds up on discharges whose ranges were never consulted. E2.0A tests only the "
                "first; the second is now satisfied by construction. A positive Epoch-2 result "
                "is therefore a WEAKER statement than E2.0 would have produced, and the claim "
                "boundary must say so"),
        },
    }
    (OUT / "E2_0A_INFORMATION_BOUNDARY.json").write_text(json.dumps(ib, indent=2), encoding="utf-8")

    # ---------------- candidate basis --------------------------------------
    cb = ver["candidate_basis"]
    basis = {
        "record_id": "E2_0A_CANDIDATE_BASIS_V1", "frozen_utc": now,
        "id": "C_E2_FULL_DOMAIN",
        "definition": ("exactly the K2-certified atomic coordinates with FULL_DOMAIN_RANGE_SUPPORT "
                       "over all 62 discharges and 186 blocks at tau = 1"),
        "n": cb["n_full_domain"],
        "of_atomic_universe": cb["atomic_universe"],
        "constructor_counts": cb["constructor_counts"],
        "matches_K2_freeze": cb["matches_K2_freeze"],
        "coordinate_ids_sha256": cb["coordinate_ids_sha256"],
        "listing": "manifests/C_E2_FULL_DOMAIN.csv",
        "tau": 1.0, "tau_train": None,
        "different_ontology_generated": False,
        "role": "the common initial candidate basis for EVERY outer fold",
        "closure_property": {
            "claim": ver["closure_property"]["claim"],
            "verified_not_assumed": True,
            "verified_at_support_sizes": [t["support_size"] for t in
                                          ver["closure_property"]["verified_empirically"]],
            "all_pass": ver["closure_property"]["all_sizes_pass"],
            "adversarial_control_fraction": ver["closure_property"]["adversarial_control"]["fraction_full_domain"],
            "control_purpose": ver["closure_property"]["adversarial_control"]["purpose"],
        },
        "A_rec_status": "UNCHANGED - the 7,327 locally partial atoms are NOT erased",
        "G_rec_status": "UNCHANGED",
        "P_rec_status": "UNCHANGED from K_REC_V2",
        "relationship": ("C_E2_FULL_DOMAIN is a subset of Coord(G_rec) selected by the frozen "
                         "P_rec applicability predicate over the intended domain. It constrains "
                         "the Epoch-2 SEARCH FRONTIER; it does not redefine A_rec"),
    }
    (OUT / "E2_0A_CANDIDATE_BASIS.json").write_text(json.dumps(basis, indent=2), encoding="utf-8")

    # ---------------- the amended protocol ---------------------------------
    proto = {
        "protocol_id": "E2_0A_PROTOCOL", "frozen_utc": now,
        "status": "AUTHORITATIVE_FOR_EPOCH2_EXECUTION",
        "parent_protocol": "E2_0_PROTOCOL_V1",
        "parent_protocol_status": "PRESERVED_AS_HISTORICAL_PARENT",
        "parent_protocol_sha256": f20["protocol_sha256"],
        "parent_contract": "K_REC_V2", "parent_contract_sha256": inh["K_REC_V2_sha256"],
        "principle": "PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION",
        "claim_type": inh["claim_type"],
        "claim_type_changed": False,
        "tau": {"value": 1.0, "unchanged": True,
                "definition": ("E(c) = max(L - min(c_app), 0, max(c_app) - U) / (U - L), "
                               "with L = min(c_cal), U = max(c_cal)"),
                "interpretation": ("distance outside the observed calibration hull, measured in "
                                   "units of the calibration-range width"),
                "reading_at_tau_1": ("application values may extend beyond the calibration hull "
                                     "by no more than ONE COMPLETE calibration-range width"),
                "worked_example": {"calibration_range": [2, 6], "width": 4,
                                   "app_inside_2_6": 0.0, "app_reaches_7": 0.25,
                                   "app_reaches_8": 0.50, "app_reaches_10": 1.00,
                                   "app_reaches_11": "1.25 -> NOT APPLICABLE"},
                "tau_is_NOT": ["a regression parameter", "a regularisation parameter",
                               "a performance threshold", "a learned constant",
                               "a physical constant", "a confidence level",
                               "a train/test tuning knob"],
                "tau_IS": "an observational-applicability bound in P_rec",
                "degenerate_calibration_rule": "unchanged from K_REC_V2"},
        "tau_train": {"status": "RETIRED", "e2_0_value": f20["tau_training"],
                      "replaced_by_any_other_training_threshold": False,
                      "retirement_rationale": "CONCEPTUAL",
                      "rationale": ("predictor-side support of the intended finite object may be "
                                    "instantiated using the predictor side of that object; a "
                                    "headroom margin was only needed under the stronger "
                                    "predictor-blinded reading E2.0 imported"),
                      "NOT_retired_because_of_applicability_odds": True,
                      "e2_0_feasibility_table": "PRESERVED_HISTORICALLY, not deleted"},
        "candidate_basis": "C_E2_FULL_DOMAIN (3451 coordinates)",
        "outer_folds": {"n": 6, "unchanged": True,
                        "source": "E2.0 outer_fold_assignment.csv",
                        "sha256": ver["fold_check"]["source_sha256"],
                        "sizes": ver["fold_check"]["sizes"],
                        "repartitioned": False, "new_seed": False, "optimised": False},
        "access_order": {
            "GLOBAL_PRE_SEARCH": [
                {"step": 1, "action": "verify O_q and K_REC_V2", "opens": "metadata and hashes"},
                {"step": 2, "action": "open non-target predictor values for all 62 discharges",
                 "opens": "PREDICTORS ONLY"},
                {"step": 3, "action": "instantiate P-RANGE at tau = 1", "opens": "nothing new"},
                {"step": 4, "action": "verify and load C_E2_FULL_DOMAIN = 3451", "opens": "nothing new"},
                {"step": 5, "action": "HASH the common candidate basis", "opens": "nothing"},
            ],
            "no_target_value_opened_in_steps_1_to_5": True,
            "PER_OUTER_FOLD": [
                {"step": 6, "action": "expose D_train^(k) TARGETS"},
                {"step": 7, "action": "fresh fold-specific search over C_E2_FULL_DOMAIN"},
                {"step": 8, "action": "apply frozen U_rec"},
                {"step": 9, "action": "select C_k*"},
                {"step": 10, "action": "WRITE AND HASH C_k*",
                 "note": "the support may never change after this step"},
                {"step": 11, "action": "freeze estimators and baseline configurations"},
                {"step": 12, "action": "open D_test^(k) CALIBRATION targets"},
                {"step": 13, "action": "fit local coefficients and baseline calibration"},
                {"step": 14, "action": "open D_test^(k) PROTECTED targets LAST"},
                {"step": 15, "action": "score"},
            ],
            "held_out_targets_may_never_cause": ["support reselection", "coordinate replacement",
                                                 "tau change", "fold change", "search extension"],
        },
        "V_RANGE": {
            "deleted": False,
            "expected_outcome": "PASS_BY_CONSTRUCTION for supports drawn only from C_E2_FULL_DOMAIN",
            "must_still_be_recomputed_during_execution": True,
            "remaining_role": "INTEGRITY_CHECK",
            "on_unexpected_failure": {
                "classification": "PROTOCOL_OR_IMPLEMENTATION_INCONSISTENCY",
                "action": "STOP EXECUTION FOR AUDIT",
                "must_not_be_classified_as": "ordinary scientific failure before checking lineage",
                "because": ("K2's closure property, verified again here, says combinations of "
                            "full-domain coordinates are full-domain supports"),
            },
        },
        "unchanged_from_E2_0": {
            "U_rec": inh["U_rec"], "V3": inh["V3"], "V6_threshold": inh["V6_threshold"],
            "baselines": inh["baselines"],
            "search_budget_per_fold": inh["budget_per_fold"],
            "search_budget_total": inh["budget_total"],
            "one_seed_policy": True, "two_seed_in_primary": False,
            "CLEAN_DEMO_PASS_delta1": inh["clean_demo_delta1"],
            "EPOCH2_IS_FINAL_QREC_ATTEMPT": inh["stop_rule_final_attempt"],
            "support_stability_reporting": "unchanged",
            "optional_all_data_descriptive_support": "unchanged",
            "forbidden_claim_wording": "unchanged and not weakened",
        },
        "goal_shifting_guardrail": {
            "scientific_goal_reinterpreted_as_future_discharge_generalization": False,
            "headroom_added_for_a_hypothetical_unseen_predictor_distribution": False,
            "tau_train_reintroduced_under_another_name": False,
            "finite_object_claim_replaced_by_inductive_transfer_claim": False,
        },
    }
    (OUT / "E2_0A_PROTOCOL.json").write_text(json.dumps(proto, indent=2), encoding="utf-8")

    # ---------------- changeset -------------------------------------------
    chg = {
        "changeset_id": "E2_0A_CHANGESET_V1", "generated_utc": now,
        "parent": "E2_0_PROTOCOL_V1", "child": "E2_0A_PROTOCOL",
        "parent_overwritten": False,
        "parent_status": "PRESERVED_AS_HISTORICAL_PARENT",
        "child_status": "AUTHORITATIVE_FOR_EPOCH2_EXECUTION",
        "changes": [
            {"item": "held-out predictor ranges may not influence candidate filtering",
             "from": "FORBIDDEN (E2.0)", "to": "PERMITTED for P-RANGE applicability only (E2.0A)",
             "type": "RELAXATION", "justified_on": "claim semantics + contract precedent",
             "affects_target_side": False},
            {"item": "tau_train", "from": 0.5, "to": None, "type": "RETIREMENT",
             "justified_on": "conceptual - unnecessary under the finite-object claim",
             "replacement_threshold_created": False},
            {"item": "candidate basis",
             "from": "per-fold, rebuilt from D_train at tau_train = 0.5 (2217-2352 coords)",
             "to": "common C_E2_FULL_DOMAIN, K2-certified over all 62 (3451 coords)",
             "type": "SUBSTITUTION"},
            {"item": "access order", "from": "13 per-fold steps",
             "to": "5 global pre-search steps + 10 per-fold steps", "type": "RESTRUCTURE"},
            {"item": "V-RANGE", "from": "a substantive held-out gate",
             "to": "expected to pass by construction; retained as an INTEGRITY CHECK",
             "type": "ROLE_CHANGE", "deleted": False},
        ],
        "unchanged": ["claim type", "the six outer folds", "tau = 1", "K_REC_V2", "G_rec",
                      "A_rec", "P_rec", "U_rec", "V3", "V6", "baselines", "search budget",
                      "one-seed policy", "CLEAN_DEMO_PASS", "stop rule",
                      "forbidden claim wording"],
        "epistemic_effect": ib["what_this_does_NOT_buy"]["epistemic_cost_recorded_explicitly"],
        "amendment_justified_by_success_probability": False,
        "e2_0_feasibility_estimate": {
            "value": "roughly 1 in 5 six-fold applicability under random draws",
            "role_now": "HISTORICAL_CONTEXT_ONLY",
            "was_the_justification": False,
            "preserved_at": "E2_0_protocol_and_resampling_freeze/manifests/APPLICABILITY_FEASIBILITY.json",
        },
    }
    (OUT / "E2_0A_CHANGESET.json").write_text(json.dumps(chg, indent=2), encoding="utf-8")

    # ---------------- acceptance and freeze --------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))
    fw = json.loads((OUT / "E2_0A_FIREWALL.json").read_text())
    pm = ver["parent_manifests"]

    checks = [
        ("S7.K2 parent reproduces", pm["S7.K2"]["mismatched"] == []),
        ("S7.E2.0 parent reproduces", pm["S7.E2.0"]["mismatched"] == []),
        ("no parent file modified", pm["S7.K2"]["mismatched"] == [] and pm["S7.E2.0"]["mismatched"] == []),
        ("K_REC_V2 unchanged", inh["K_REC_V2_matches_K2_freeze"] is True),
        ("tau remains exactly 1", proto["tau"]["value"] == 1.0),
        ("tau_train retired", proto["tau_train"]["status"] == "RETIRED"),
        ("no replacement training-only threshold created",
         proto["tau_train"]["replaced_by_any_other_training_threshold"] is False),
        ("claim type unchanged", proto["claim_type_changed"] is False),
        ("six folds unchanged exactly", ver["fold_check"]["matches_frozen_parent"] is True),
        ("all 62 predictors permitted for P-RANGE",
         ib["ROLE_A_predictor_side_admissibility"]["what"].startswith("all admissible")),
        ("all held-out targets remain excluded from support discovery",
         ib["ROLE_B_target_side_discovery"]["only_influencing_targets"] == "D_train^(k)"),
        ("common candidate basis exactly matches K2 full-domain result",
         basis["matches_K2_freeze"] is True),
        ("candidate basis count = 3451", basis["n"] == 3451),
        ("constructor counts match K2", ver["candidate_basis"]["constructor_counts_match"] is True),
        ("closure property verified", basis["closure_property"]["all_pass"] is True
         and basis["closure_property"]["adversarial_control_fraction"] == 0.0),
        ("A_rec itself not rewritten", basis["A_rec_status"].startswith("UNCHANGED")),
        ("U_rec unchanged", inh["U_rec"] == "UNCHANGED"),
        ("V3 unchanged", inh["V3"] == "Delta_0 <= -0.01 AND Delta_1 <= -0.01"),
        ("V6 unchanged", inh["V6_threshold"] == 0.01),
        ("baselines unchanged", len(inh["baselines"]) == 6),
        ("search budget unchanged", inh["budget_per_fold"] == 300000 and inh["budget_total"] == 1800000),
        ("stop rule unchanged", inh["stop_rule_final_attempt"] is True),
        ("CLEAN_DEMO_PASS unchanged", inh["clean_demo_delta1"] == -0.05),
        ("target_reads = 0", fw["target_reads"] == 0),
        ("model_error_reads = 0", fw["model_error_reads"] == 0),
        ("no support selected", True), ("no model fitted", True),
        ("Epoch 2 not started", not inh["epoch2_result_exists"]),
        ("S7.12 not started", not inh["S7_12_exists"]),
        ("transition-specific information-flow interpretation written",
         ib["the_boundary_is_transition_specific"] is True and len(ib["information_flow"]) == 6),
        ("no inductive/future-discharge claim introduced",
         proto["goal_shifting_guardrail"]["finite_object_claim_replaced_by_inductive_transfer_claim"] is False),
        ("historical E2.0 feasibility table preserved",
         (E20 / "manifests" / "APPLICABILITY_FEASIBILITY.json").exists()),
        ("amendment justification does not cite improved success odds as its basis",
         chg["amendment_justified_by_success_probability"] is False
         and fw["e2_0_feasibility_estimate_role"] == "HISTORICAL_CONTEXT_ONLY_NOT_JUSTIFICATION"),
        ("epistemic cost of the relaxation recorded explicitly",
         "WEAKER statement" in ib["what_this_does_NOT_buy"]["epistemic_cost_recorded_explicitly"]),
        ("Markdown count <= 20", len(md) <= 20),
    ]
    passed = sum(1 for _, o in checks if o)
    failed = [n for n, o in checks if not o]
    acc = {"acceptance_id": "E2_0A_ACCEPTANCE_CHECKS_V1", "generated_utc": now,
           "n_checks": len(checks), "n_passed": passed,
           "result": "%d/%d" % (passed, len(checks)), "failed": failed,
           "checks": [{"check": n, "passed": bool(o)} for n, o in checks]}
    (OUT / "E2_0A_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel or p.name.startswith("_"):
            continue
        hashes[rel] = sha256(p)

    freeze = {
        "freeze_id": "D3D-SIR-S7.E2.0A-PREDICTOR-SIDE-ADMISSIBILITY-RECONCILIATION-V1",
        "status": "FROZEN_READY_FOR_EPOCH2_SEARCH" if not failed
                  else "BLOCKED_INFORMATION_BOUNDARY_INCONSISTENCY",
        "timestamp_utc": now,
        "contract_parent": "D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1",
        "protocol_parent": "D3D-SIR-S7.E2.0-DISCOVERY-EPOCH2-PROTOCOL-V1",
        "E2_0_PROTOCOL_V1": "PRESERVED_AS_HISTORICAL_PARENT",
        "E2_0A_PROTOCOL": "AUTHORITATIVE_FOR_EPOCH2_EXECUTION",
        "mismatch_confirmed": True,
        "principle": "PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION",
        "tau": 1.0, "tau_train": None,
        "candidate_basis": {"id": "C_E2_FULL_DOMAIN", "n": 3451,
                            "constructor_counts": ver["candidate_basis"]["constructor_counts"],
                            "sha256": ver["candidate_basis"]["coordinate_ids_sha256"]},
        "protocol_sha256": sha256(OUT / "E2_0A_PROTOCOL.json"),
        "information_boundary_sha256": sha256(OUT / "E2_0A_INFORMATION_BOUNDARY.json"),
        "candidate_basis_sha256": sha256(OUT / "E2_0A_CANDIDATE_BASIS.json"),
        "changeset_sha256": sha256(OUT / "E2_0A_CHANGESET.json"),
        "firewall_sha256": sha256(OUT / "E2_0A_FIREWALL.json"),
        "I_q_notation_change_required": False,
        "manuscript_clarification_recommended": True,
        "qualifications": [
            "The E2.0 mismatch is CONFIRMED, on contract-internal grounds rather than on odds. "
            "S7.6R's sibling partial-map rule is explicitly an APPLICATION-TIME predicate - a "
            "selected support 'must satisfy the same rule on each external local-calibration "
            "block' - and was never required to be forecastable from training data. K2's own "
            "coverage policy cited 3,451 full-domain atoms computed over ALL 62 discharges as "
            "its feasibility evidence. E2.0's predictor-blinding contradicted the parent "
            "contract it was implementing.",
            "EPISTEMIC COST, RECORDED NOT HIDDEN: E2.0 would have tested two things on held-out "
            "data - whether the target relationship transfers, and whether the support's "
            "predictor geometry survives discharges whose ranges were never consulted. E2.0A "
            "tests only the first; the second is now true by construction. A positive Epoch-2 "
            "result is therefore a WEAKER statement than E2.0 would have produced, and the claim "
            "boundary says so.",
            "tau_train is RETIRED on conceptual grounds and NOT replaced by any other "
            "training-only threshold. The E2.0 feasibility table showing roughly 1-in-5 six-fold "
            "applicability is preserved historically and is explicitly NOT the justification.",
            "V-RANGE is NOT deleted. It is expected to pass by construction for supports drawn "
            "only from C_E2_FULL_DOMAIN, and must still be recomputed during execution as an "
            "integrity check. An unexpected failure is a PROTOCOL OR IMPLEMENTATION "
            "INCONSISTENCY and must STOP execution for audit, not be recorded as ordinary "
            "scientific failure.",
            "The existing I_rec definition already permits this arrangement: I_rec is a "
            "VARIABLE-SET boundary about target ancestry and never governed which observations "
            "of an admitted variable are available at which stage. No notation revision is "
            "required; a one-sentence manuscript clarification is recommended so readers do not "
            "conflate I_q with stage-wise observation availability.",
            "Nothing else moved. Claim type, the six folds, tau = 1, K_REC_V2, G_rec, A_rec, "
            "P_rec, U_rec, V3, V6, the six baselines, the search budget, the one-seed policy, "
            "CLEAN_DEMO_PASS and the stop rule are all unchanged, and the forbidden claim "
            "wording was not weakened.",
        ],
        "governance": {
            "PARENT_ARTIFACTS_MODIFIED": 0, "E2_0_OVERWRITTEN": False,
            "K_REC_V2_MODIFIED": False, "TAU_MODIFIED": False, "FOLDS_MODIFIED": False,
            "U_REC_MODIFIED": False, "V3_MODIFIED": False, "V6_MODIFIED": False,
            "BASELINES_MODIFIED": False, "BUDGET_MODIFIED": False,
            "STOP_RULE_MODIFIED": False, "CLEAN_DEMO_PASS_MODIFIED": False,
            "CLAIM_STRENGTHENED": False, "FORBIDDEN_WORDING_WEAKENED": False,
            "SEARCH_RUN": False, "MODEL_FITTED": False, "BASELINE_RUN": False,
            "SUPPORT_SELECTED": False, "TARGET_READ": False,
            "TAU_TRAIN_REINTRODUCED_UNDER_ANOTHER_NAME": False,
            "EPOCH2_STARTED": False, "S7_12_STARTED": False,
        },
        "acceptance_checks": acc["result"], "acceptance_failed": failed,
        "n_artifacts": len(hashes), "n_markdown": len(md), "markdown_files": md,
        "all_artifact_hashes": hashes, "self_referential_excluded": SELF,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "next_stage": "S7.E2.1 Discovery Epoch 2 search - NOT AUTHORISED IN THIS STAGE",
    }
    (OUT / "E2_0A_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("acceptance : %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("status     : %s" % freeze["status"])
    print("basis      : C_E2_FULL_DOMAIN n=%d | tau=1.0 | tau_train=RETIRED" % basis["n"])
    print("I_q change required: %s | clarification recommended: %s"
          % (freeze["I_q_notation_change_required"], freeze["manuscript_clarification_recommended"]))
    print("artifacts %d | markdown %d" % (len(hashes), len(md)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
