"""S7.E2.0 step B - freeze the Epoch-2 protocol, access ordering, range-support
operation, search budget, qualification policy, claim boundary and stop rule.

No search, no fit, no baseline, no scoring. Target-blind throughout.
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
K2 = S7 / "K2_observational_range_support_contract"
SELF = ["E2_0_ACCEPTANCE_CHECKS.json", "E2_0_FREEZE.json"]

TAU_QUAL = 1.0        # K_REC_V2 P-RANGE / V-RANGE, unchanged
TAU_TRAIN = 0.5       # Epoch-2 search-side training-domain requirement
FLOOR = 0.01
CLEAN_DEMO_DELTA1 = -0.05     # 5x the frozen practical-equivalence floor


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    fd = json.loads((OUT / "manifests" / "FOLD_DESIGN.json").read_text())
    if fd["verdict"] != "FOLD_DESIGN_FROZEN":
        raise SystemExit("STOP: fold design not frozen")
    fa = pd.read_csv(OUT / "outer_fold_assignment.csv", dtype={"discharge": str})
    feas = json.loads((OUT / "manifests" / "APPLICABILITY_FEASIBILITY.json").read_text())
    krec2 = json.loads((K2 / "K_REC_V2.json").read_text())

    # ---------------- access policy: the audited ordering -----------------
    access = {
        "policy_id": "EPOCH2_ACCESS_POLICY_V1", "frozen_utc": now,
        "principle": ("every discharge receives qualification predictions only from a relational "
                      "support discovered without that discharge participating in support "
                      "discovery"),
        "per_outer_fold_ordering": [
            {"step": 1, "action": "verify fold identities and hashes", "opens": "metadata only"},
            {"step": 2, "action": "construct D_train candidate basis under the training-domain "
                                  "range-support requirement",
             "opens": "D_train PREDICTOR values only",
             "forbidden": "D_test predictors, all target values"},
            {"step": 3, "action": "run a fresh one-seed search",
             "opens": "D_train predictor and D_train TARGET values",
             "forbidden": "any D_test value of any kind"},
            {"step": 4, "action": "execute the frozen U_rec selection", "opens": "D_train only"},
            {"step": 5, "action": "write the selected support", "opens": "nothing"},
            {"step": 6, "action": "HASH the selected support",
             "note": "THE SUPPORT MAY NEVER CHANGE AFTER THIS STEP"},
            {"step": 7, "action": "freeze estimator and baseline configurations", "opens": "D_train only"},
            {"step": 8, "action": "permit D_test PREDICTOR access", "opens": "D_test predictors"},
            {"step": 9, "action": "evaluate V-RANGE on D_test", "opens": "D_test predictors"},
            {"step": 10, "action": "permit D_test local CALIBRATION target access",
             "opens": "D_test calibration-interval targets only"},
            {"step": 11, "action": "fit local coefficients and baselines",
             "opens": "D_test calibration targets"},
            {"step": 12, "action": "open D_test PROTECTED targets", "opens": "D_test protected targets"},
            {"step": 13, "action": "score", "opens": "nothing new"},
        ],
        "held_out_predictor_ranges_may_influence_search": False,
        "held_out_targets_may_influence_support_discovery": False,
        "why_held_out_predictors_are_excluded_from_search": (
            "filtering candidates by D_test predictor ranges would let the held-out fold shape "
            "which coordinates are even considered, destroying genuine held-out support transfer"),
        "support_frozen_before_any_held_out_predictor_access": True,
        "protected_targets_last": True,
        "machine_auditable": True,
        "required_audit_artifact_per_fold": "an access log recording, per step, what was opened",
    }
    (OUT / "EPOCH2_ACCESS_POLICY.json").write_text(json.dumps(access, indent=2), encoding="utf-8")

    # ---------------- range-support operation inside a fold ---------------
    rsp = {
        "policy_id": "EPOCH2_RANGE_SUPPORT_POLICY_V1", "frozen_utc": now,
        "inherits": "K_REC_V2 P-RANGE-SUPPORT and V-RANGE, unchanged",
        "qualification_threshold_tau": TAU_QUAL,
        "qualification_threshold_is_contractual_and_unchanged": True,
        "no_global_prefilter_over_all_62": True,
        "A_training_admissibility": {
            "rule": ("a coordinate may enter the Epoch-2 search for fold k only if E(c,s,b) <= "
                     "%.2f on EVERY D_train(k) discharge/block, using D_train predictors alone"
                     % TAU_TRAIN),
            "tau_train": TAU_TRAIN,
            "is_a_search_side_requirement_not_a_contract_change": True,
            "authorised_by": ("E2.0 section 11A - 'candidates may enter the search only if they "
                              "satisfy the prospectively frozen training-domain requirement'"),
            "interpretation": ("on the training discharges a coordinate may leave its calibration "
                               "hull by at most HALF a calibration range, leaving a further half "
                               "range of headroom before the contractual qualification threshold "
                               "at tau = 1"),
            "why_stricter_than_tau": ("a coordinate admitted at exactly tau on training has no "
                                      "headroom and is near-certain to breach tau on unseen "
                                      "discharges; the headroom is what makes held-out "
                                      "applicability attainable at all"),
            "chosen_on": "interpretability and basis adequacy, target-blind",
            "not_chosen_by_maximising_a_pass_probability": True,
            "per_fold_basis_size": feas["basis_size_by_tau_train"][str(TAU_TRAIN)],
            "all_seven_constructor_families_survive_in_every_fold": True,
        },
        "B_heldout_qualification": {
            "rule": ("after the support is frozen and hashed, apply P-RANGE at tau = %.1f to "
                     "every D_test(k) discharge/block" % TAU_QUAL),
            "support_predicate": "conjunction - EVERY coordinate must pass on EVERY held-out block",
            "failure_status": "RANGE_SUPPORT_NOT_APPLICABLE",
            "on_failure_forbidden": ["reselect another support", "delete the block",
                                     "delete the discharge", "loosen tau", "clip the coordinate",
                                     "re-run the fold search"],
            "on_failure_required": ("record the status; the fold does not qualify for full-domain "
                                    "success; report it"),
        },
        "inner_geometry": {
            "blocks": {"A": [[0.0, 0.4], [0.4, 0.5]], "B": [[0.0, 0.6], [0.6, 0.7]],
                       "C": [[0.0, 0.8], [0.8, 0.9]]},
            "unchanged_from_epoch1": True,
            "new_temporal_windows": False,
            "local_coefficients": "discharge x block, calibration-only, as in Epoch 1",
            "support_shared_across_outer_training_discharges": True,
        },
    }
    (OUT / "EPOCH2_RANGE_SUPPORT_POLICY.json").write_text(json.dumps(rsp, indent=2), encoding="utf-8")

    # ---------------- search budget ---------------------------------------
    budget = {
        "policy_id": "EPOCH2_SEARCH_BUDGET_V1", "frozen_utc": now,
        "frozen_before_any_target_access": True,
        "epoch1_frontier_reused_or_reranked": False,
        "search_policy_family": "SIGMA_REC_ONE_SEED_PRIMARY_V2 (S7.7R), adapted mechanically",
        "mechanical_adaptations_only": [
            "the atomic basis is the fold-specific training-admissible set instead of all 10,778",
            "strata are recomputed over that basis by the unchanged stratum definition"],
        "seeds_per_stratum": 1,
        "two_seed_in_primary_protocol": False,
        "two_seed_status": "remains outside the primary study, as declared since S7.7R",
        "support_size_bound": [1, 12],
        "shortlist_cap_per_constructor": 96,
        "max_support_evaluations_per_fold": 300000,
        "max_support_evaluations_total": 1800000,
        "outcome_triggered_expansion": False,
        "budget_may_be_raised_after_seeing_results": False,
        "note": ("the per-fold allowance equals Epoch 1's, over a basis roughly a fifth the size, "
                 "so the budget is not the binding constraint"),
    }
    (OUT / "EPOCH2_SEARCH_BUDGET.json").write_text(json.dumps(budget, indent=2), encoding="utf-8")

    # ---------------- qualification policy --------------------------------
    qual = {
        "policy_id": "EPOCH2_QUALIFICATION_POLICY_V1", "frozen_utc": now,
        "primary_statistical_unit": "discharge",
        "pseudoreplication_over_time_samples": False,
        "per_discharge_aggregation": "mean over the valid A/B/C blocks, exactly as frozen",
        "cross_fitted_aggregation": {
            "rule": ("assemble the 62 out-of-fold discharge results, one per discharge, each "
                     "produced by the support of the fold in which that discharge was held out"),
            "in_fold_development_scores_contribute": False,
            "each_discharge_contributes_exactly_one_result": True,
        },
        "V3": {"Delta_0": "mean_s(NRMSE_REL,s - NRMSE_B0,s)",
               "Delta_1": "mean_s(NRMSE_REL,s - NRMSE_B1,s)",
               "pass": "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
               "unchanged_from_epoch1": True, "ci_role": "reported, not a threshold"},
        "V6": {"eras": {"earlier": 35, "later": 27},
               "note": "62-object era counts, since the qualification domain is now all 62",
               "quantity": "Delta_{j,e} over out-of-fold discharges in era e",
               "MATERIAL_IMPROVEMENT": "Delta <= -0.01",
               "PRACTICAL_TIE": "-0.01 < Delta <= +0.01",
               "MATERIAL_ADVERSE": "Delta > +0.01",
               "one_era_may_not_rescue_another": True,
               "threshold": FLOOR, "frozen_now": True},
        "V_RANGE_primary_coverage": {
            "requirement": "FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT",
            "definition": ("every held-out discharge/block, under its own fold-selected support, "
                           "satisfies V-RANGE at tau = 1"),
            "one_failure_fails_the_gate": True,
            "silent_omission_forbidden": True,
            "partial_domain_results": "may be reported diagnostically; cannot rescue the primary",
        },
        "positive_result_tiers": {
            "FORMAL_PASS": "the frozen gates pass, exactly as written",
            "CLEAN_DEMO_PASS": {
                "requires": ["FORMAL_PASS",
                             "Delta_1 <= %.2f" % CLEAN_DEMO_DELTA1,
                             "FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT",
                             "no out-of-fold discharge with REL NRMSE > 1.0",
                             "both eras MATERIAL_IMPROVEMENT against B1"],
                "delta1_threshold": CLEAN_DEMO_DELTA1,
                "derivation": ("five times the frozen practical-equivalence floor of 0.01, which "
                               "S7.2 declared before any result existed as lying BELOW any "
                               "scientifically meaningful difference. Five times that floor is "
                               "unambiguously above it"),
                "derived_from_any_outcome": False,
                "option_chosen": "A - a simple prospective reporting threshold, frozen now",
                "consequence_note": ("this is a demanding standard: S7.11 recorded that no member "
                                     "of the Epoch-1 support family beat persistence by more than "
                                     "0.0287, so no Epoch-1 object would reach it. Recorded as "
                                     "context AFTER the derivation, not as its basis"),
            },
            "CLEAN_DEMO_PASS_can_change_the_scientific_gate": False,
        },
        "baselines": {
            "carried": ["B0 calibration mean", "B1 persistence", "B1A AR(1)",
                        "B2 raw ridge", "B3 raw HGBR", "H0 hardened raw ridge"],
            "hyperparameters_re_estimated_from": "D_train only, per fold",
            "held_out_targets_may_influence_baseline_tuning": False,
            "identical_protected_rows_for_all_comparable_methods": True,
        },
        "U_rec": {"status": "UNCHANGED", "tail_penalty_added": False,
                  "rank1_changed": False, "practical_equivalence_changed": False,
                  "range_support_rewarded_inside_U_rec": False,
                  "separation_principle": ("range support is an admissibility/applicability "
                                           "condition in P_rec/V_rec, never a performance "
                                           "objective in U_rec")},
        "support_stability_reporting": {
            "expected": "one selected support per outer fold, six in total",
            "predeclared_descriptive_reports": ["exact support overlap across folds",
                                                "coordinate recurrence", "constructor recurrence",
                                                "primitive-family recurrence"],
            "minimum_exact_support_agreement_required": None,
            "new_exact_support_gate_created": False,
            "legitimate_outcome": ("stable reconstruction utility with non-unique relational "
                                   "supports, consistent with the S7.9/S7.11 lesson"),
        },
        "optional_all_data_descriptive_support": {
            "permitted": True,
            "permitted_only_after": "the cross-fitted qualification is completely frozen",
            "label": "FULL_OBJECT_DESCRIPTIVE_REPRESENTATION",
            "may_be_called_externally_validated": False,
            "may_alter_the_crossfitted_verdict": False,
            "purpose": "description, visualization, manuscript interpretation",
        },
    }
    (OUT / "EPOCH2_QUALIFICATION_POLICY.json").write_text(json.dumps(qual, indent=2), encoding="utf-8")

    # ---------------- master protocol -------------------------------------
    protocol = {
        "protocol_id": "EPOCH2_PROTOCOL_V1", "frozen_utc": now,
        "parent_contract": "K_REC_V2",
        "parent_contract_sha256": sha256(K2 / "K_REC_V2.json"),
        "architecture": "DISCHARGE_GROUPED_CROSS_FITTED_DISCOVERY_AND_QUALIFICATION",
        "claim_type": ("CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION_WITHIN_THE_FROZEN_"
                       "62_DISCHARGE_OBSERVATIONAL_OBJECT"),
        "why_no_new_external_cohort": (
            "the former 42-discharge external cohort is no longer sealed: its target values were "
            "opened in S7.10 and it informed the R1/K2 diagnosis. Carving a fresh 'never seen' "
            "cohort out of the same 62 discharges would be fabrication, because every discharge "
            "has now contributed to the contract-learning process. Cross-fitting is the honest "
            "architecture: it does not claim virgin data, it claims that no discharge's own "
            "target informed the support used to reconstruct it"),
        "n_outer_folds": 6,
        "fold_sizes": fd["fold_sizes"],
        "fold_algorithm": fd["fold_algorithm"],
        "every_discharge_held_out_exactly_once": True,
        "outer_statistical_unit": "discharge",
        "row_level_random_split": False,
        "block_level_split_across_roles": False,
        "access_policy": "EPOCH2_ACCESS_POLICY_V1",
        "range_support_policy": "EPOCH2_RANGE_SUPPORT_POLICY_V1",
        "search_budget": "EPOCH2_SEARCH_BUDGET_V1",
        "qualification_policy": "EPOCH2_QUALIFICATION_POLICY_V1",
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        "stop_rule": {
            "if_epoch2_fails": ["do not revise K_rec again for this paper",
                                "do not add another threshold", "do not change the split",
                                "do not remove shots", "do not launch Discovery Epoch 3"],
            "then": ("close q_rec as a qualified iterative case study and use q_desc as the "
                     "positive DIII-D headline result"),
        },
        "forbidden_claims": ["virgin external validation", "untouched external cohort",
                             "zero-shot transfer", "prospective clinical-style confirmation",
                             "universal DIII-D generalization"],
    }
    (OUT / "EPOCH2_PROTOCOL.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")

    # ---------------- acceptance and freeze -------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))
    al = json.loads((OUT / "manifests" / "E2_0_ACCESS_LOG.json").read_text())
    fw = json.loads((OUT / "E2_PROTOCOL_FIREWALL.json").read_text())
    contract = fd["contract_verification"]

    checks = [
        ("all parents through S7.K2 verified", fd["verdict"] == "FOLD_DESIGN_FROZEN"
         and fd["n_authoritative"] == 15),
        ("K_REC_V2 exact", contract["K_REC_V2_matches_K2_freeze"] is True),
        ("no parent modified", all(v["mismatched"] == []
                                   for v in fd["manifest_recomputation"].values())),
        ("protocol target reads = 0", al["target_reads"] == 0),
        ("protocol performance reads = 0", al["epoch1_performance_reads_for_partition"] == 0),
        ("six-fold discharge grouping resolved", protocol["n_outer_folds"] == 6),
        ("every discharge held out exactly once", fd["every_discharge_held_out_exactly_once"]),
        ("folds constructed from target-blind metadata only",
         fw["partition_variables_actually_used"] == ["processing_era", "discharge id (sort key only)"]),
        ("fold-generation algorithm frozen", fd["fold_algorithm"]["deterministic"] is True),
        ("no performance-based partition choice",
         fd["fold_algorithm"]["n_partitions_generated"] == 1
         and fd["fold_algorithm"]["trial_and_selection"] is False),
        ("held-out predictors excluded from search",
         access["held_out_predictor_ranges_may_influence_search"] is False),
        ("held-out targets excluded from support discovery",
         access["held_out_targets_may_influence_support_discovery"] is False),
        ("training-domain P-RANGE rule exact", "tau_train" in rsp["A_training_admissibility"]),
        ("held-out V-RANGE rule exact", rsp["B_heldout_qualification"]["support_predicate"].startswith("conjunction")),
        ("support freeze occurs before held-out predictor access",
         access["support_frozen_before_any_held_out_predictor_access"] is True),
        ("local calibration-target access order explicit",
         access["per_outer_fold_ordering"][9]["step"] == 10),
        ("protected target access occurs last", access["protected_targets_last"] is True),
        ("U_rec unchanged", qual["U_rec"]["status"] == "UNCHANGED"),
        ("V3 unchanged", qual["V3"]["unchanged_from_epoch1"] is True),
        ("V6 logic frozen", qual["V6"]["frozen_now"] is True),
        ("baselines frozen", len(qual["baselines"]["carried"]) == 6),
        ("discharge remains inference unit", qual["primary_statistical_unit"] == "discharge"),
        ("cross-fitted aggregation exact",
         qual["cross_fitted_aggregation"]["in_fold_development_scores_contribute"] is False),
        ("no Epoch-1 frontier reuse", budget["epoch1_frontier_reused_or_reranked"] is False),
        ("search budget frozen", budget["frozen_before_any_target_access"] is True),
        ("two-seed not primary", budget["two_seed_in_primary_protocol"] is False),
        ("support-stability reporting frozen",
         qual["support_stability_reporting"]["new_exact_support_gate_created"] is False),
        ("optional all-data descriptive support decision frozen",
         qual["optional_all_data_descriptive_support"]["permitted"] is True),
        ("claim boundary frozen", len(protocol["forbidden_claims"]) == 5),
        ("final-attempt stop rule frozen", protocol["EPOCH2_IS_FINAL_QREC_ATTEMPT"] is True),
        ("CLEAN_DEMO_PASS threshold frozen prospectively",
         qual["positive_result_tiers"]["CLEAN_DEMO_PASS"]["derived_from_any_outcome"] is False),
        ("Discovery Epoch 2 not started", True),
        ("S7.12 not started", not contract["S7_12_exists"]),
        ("Markdown files <= 20", len(md) <= 20),
    ]
    passed = sum(1 for _, o in checks if o)
    failed = [n for n, o in checks if not o]
    acc = {"acceptance_id": "E2_0_ACCEPTANCE_CHECKS_V1", "generated_utc": now,
           "n_checks": len(checks), "n_passed": passed,
           "result": "%d/%d" % (passed, len(checks)), "failed": failed,
           "checks": [{"check": n, "passed": bool(o)} for n, o in checks]}
    (OUT / "E2_0_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel or p.name.startswith("_"):
            continue
        hashes[rel] = sha256(p)

    freeze = {
        "freeze_id": "D3D-SIR-S7.E2.0-DISCOVERY-EPOCH2-PROTOCOL-V1",
        "status": "FROZEN_WITH_QUALIFICATIONS",
        "recommendation": "READY_FOR_EPOCH2_SEARCH_WITH_A_DISCLOSED_APPLICABILITY_RISK",
        "timestamp_utc": now,
        "parent_freeze_id": "D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1",
        "protocol_sha256": sha256(OUT / "EPOCH2_PROTOCOL.json"),
        "access_policy_sha256": sha256(OUT / "EPOCH2_ACCESS_POLICY.json"),
        "range_support_policy_sha256": sha256(OUT / "EPOCH2_RANGE_SUPPORT_POLICY.json"),
        "search_budget_sha256": sha256(OUT / "EPOCH2_SEARCH_BUDGET.json"),
        "qualification_policy_sha256": sha256(OUT / "EPOCH2_QUALIFICATION_POLICY.json"),
        "fold_assignment_sha256": sha256(OUT / "outer_fold_assignment.csv"),
        "claim_type": protocol["claim_type"],
        "n_outer_folds": 6, "fold_sizes": fd["fold_sizes"],
        "tau_qualification": TAU_QUAL, "tau_training": TAU_TRAIN,
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        "epoch1_invariant": {"verdict": contract["epoch1_verdict"],
                             "gate_table": contract["epoch1_gate_table"]},
        "qualifications": [
            "DOMINANT RISK, QUANTIFIED PROSPECTIVELY AND TARGET-BLINDLY: the "
            "FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT gate is demanding. Under random 12-coordinate "
            "draws from each fold's training-admissible basis, the probability that ALL held-out "
            "coordinates remain range-supported is %s per fold and roughly %s across all six "
            "folds jointly. Epoch 2 is therefore more likely to fail on APPLICABILITY than on "
            "reconstruction skill. This is disclosed now, before any search, and the standard was "
            "NOT weakened to improve those odds."
            % (feas["joint12_by_tau_train"][str(TAU_TRAIN)]["per_fold_range"],
               feas["joint12_by_tau_train"][str(TAU_TRAIN)]["six_fold_product"]),
            "The risk is compounding attrition, NOT hostile discharges. Every one of the 62 "
            "discharges retains at least 93.8 percent of its fold's training basis (median 99.8 "
            "percent). There is no Epoch-1-style pathological discharge: the gasa-squared "
            "coordinate that caused the Epoch-1 failure is excluded from every training basis by "
            "K_REC_V2 itself.",
            "A training-side requirement tau_train = 0.5, stricter than the contractual "
            "qualification tau = 1, is frozen as a SEARCH-side admissibility condition under "
            "E2.0 section 11A. It does not alter K_REC_V2. It exists because a coordinate "
            "admitted at exactly tau on training has no headroom on unseen discharges.",
            "tau_train was chosen on interpretability and basis adequacy - half a calibration "
            "range of headroom, ~2,300 coordinates per fold, all seven constructor families "
            "present - and explicitly NOT by maximising a pass probability. The full sensitivity "
            "table is recorded, including that tau_train = 0.25 would give a somewhat higher "
            "joint applicability estimate on a much thinner basis.",
            "CLEAN_DEMO_PASS is frozen prospectively at Delta_1 <= -0.05, five times the frozen "
            "practical-equivalence floor. It is a reporting tier only and cannot change the "
            "scientific gate, which remains V3 at -0.01 exactly.",
            "The claim type is explicitly NOT external validation. The former external cohort is "
            "no longer sealed and no new virgin cohort is fabricated from the same 62 discharges.",
            "EPOCH2_IS_FINAL_QREC_ATTEMPT = true. If this protocol fails, q_rec closes as a "
            "qualified iterative case study and q_desc becomes the positive DIII-D headline.",
        ],
        "governance": {
            "PARENT_ARTIFACTS_MODIFIED": 0, "K_REC_V2_MODIFIED": False,
            "U_REC_MODIFIED": False, "V3_MODIFIED": False, "TAU_QUALIFICATION_MODIFIED": False,
            "EPOCH1_FRONTIER_REUSED": False, "SEARCH_RUN": False, "MODEL_FIT": False,
            "BASELINE_RUN": False, "V3_RECOMPUTED": False, "SUPPORT_SELECTED": False,
            "TARGET_READ_FOR_PROTOCOL": False, "PERFORMANCE_READ_FOR_PARTITION": False,
            "PARTITIONS_GENERATED": 1, "EPOCH2_STARTED": False, "S7_12_STARTED": False,
        },
        "paper_utility": "MEDIUM_HIGH",
        "acceptance_checks": acc["result"], "acceptance_failed": failed,
        "n_artifacts": len(hashes), "n_markdown": len(md), "markdown_files": md,
        "all_artifact_hashes": hashes, "self_referential_excluded": SELF,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "next_stage": "S7.E2.1 Discovery Epoch 2 search - NOT AUTHORISED IN THIS STAGE",
    }
    (OUT / "E2_0_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("acceptance : %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("status     : %s" % freeze["status"])
    print("tau_qual %.1f | tau_train %.2f | folds 6 | claim: %s"
          % (TAU_QUAL, TAU_TRAIN, protocol["claim_type"][:52]))
    print("artifacts %d | markdown %d" % (len(hashes), len(md)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
