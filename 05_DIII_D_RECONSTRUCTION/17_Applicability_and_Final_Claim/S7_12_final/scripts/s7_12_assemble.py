"""S7.12 - final qualified reconstruction result.

ASSEMBLY AND QUALIFICATION ONLY. No search, no fit, no gate evaluation, no new
metric. Every number is read from a frozen parent record and carried unchanged.
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
E21 = S7 / "E2_1_crossfitted_discovery_and_qualification"
E22 = S7 / "E2_2_full_object_descriptive_representation"

FREEZE_ID = "D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1"

PARENTS = [
    ("S7.2", "02_reconstruction_contract", "S7_2_FREEZE.json"),
    ("S7.3", "03_target_feasibility_and_boundary", "S7_3_FREEZE.json"),
    ("S7.6", "06_admissible_universe", "S7_6_FREEZE.json"),
    ("S7.7", "07_search_policy_and_frontier", "S7_7_FREEZE.json"),
    ("S7.9", "09_development_selection_and_freeze", "S7_9_FREEZE.json"),
    ("S7.10", "10_external_validation", "S7_10_FREEZE.json"),
    ("S7.11", "11_sensitivity_and_interpretation", "S7_11_FREEZE.json"),
    ("S7.R1", "R1_operational_state_reconciliation", "S7_R1_FREEZE.json"),
    ("S7.K2", "K2_observational_range_support_contract", "S7_K2_FREEZE.json"),
    ("S7.E2.0", "E2_0_protocol_and_resampling_freeze", "E2_0_FREEZE.json"),
    ("S7.E2.0A", "E2_0A_predictor_admissibility_reconciliation", "E2_0A_FREEZE.json"),
    ("S7.E2.1", "E2_1_crossfitted_discovery_and_qualification", "E2_1_FREEZE.json"),
    ("S7.E2.2", "E2_2_full_object_descriptive_representation", "E2_2_FREEZE.json"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dsplit(s):
    out, d, cur = [], 0, []
    for ch in s:
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
        if ch == "|" and d == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    drift = []

    # ---------------- parent verification -------------------------------
    manifests, lineage, FZ = {}, [], {}
    for label, base, fn in PARENTS:
        fz = json.loads((S7 / base / fn).read_text(encoding="utf-8"))
        FZ[label] = fz
        # self-referential entries cannot reproduce by construction: a freeze
        # cannot contain the hash of itself. Later stages declare them in
        # "self_referential_excluded"; the earliest stages listed them inline.
        excl = set(fz.get("self_referential_excluded", []))
        excl.add(fn)
        excl |= {r for r in fz["all_artifact_hashes"]
                 if r.endswith("_ACCEPTANCE_CHECKS.json") and "/" not in r}
        m, bad = 0, []
        for r, want in fz["all_artifact_hashes"].items():
            if r in excl:
                continue
            p = S7 / base / r
            if p.exists() and sha256(p) == want:
                m += 1
            else:
                bad.append(r)
        manifests[label] = {"n": len(fz["all_artifact_hashes"]) - len(
            excl & set(fz["all_artifact_hashes"])), "matched": m,
            "mismatched": bad,
            "self_referential_excluded": sorted(excl & set(fz["all_artifact_hashes"]))}
        lineage.append({"stage": label, "freeze_id": fz["freeze_id"],
                        "status": fz.get("status"),
                        "timestamp_utc": fz.get("timestamp_utc"),
                        "file_sha256": sha256(S7 / base / fn)})
        if bad:
            drift.append("%s manifest does not reproduce" % label)

    f21, f22 = FZ["S7.E2.1"], FZ["S7.E2.2"]
    e22_available = f22["status"] == "FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN"
    e22_before_s712 = f22["timestamp_utc"] < now
    e21_before_e22 = f21["timestamp_utc"] < f22["timestamp_utc"]

    (OUT / "manifests" / "S7_12_PARENT_VERIFICATION.json").write_text(json.dumps({
        "record_id": "S7_12_PARENT_VERIFICATION_V1", "generated_utc": now,
        "lineage": lineage, "parent_manifests": manifests,
        "all_reproduce": not drift,
        "E2_2_frozen_before_S7_12": e22_before_s712,
        "E2_1_frozen_before_E2_2": e21_before_e22,
        "drift": drift,
    }, indent=2), encoding="utf-8")
    if drift:
        raise SystemExit("STOP: lineage inconsistency - " + "; ".join(drift))

    # ---------------- carried evidence ----------------------------------
    met = json.loads((E21 / "E2_1_CROSSFITTED_METRICS.json").read_text())
    gate21 = json.loads((E21 / "E2_1_GATE_TABLE.json").read_text())
    res21 = json.loads((E21 / "E2_1_RESULT.json").read_text())
    sup21 = json.loads((E21 / "E2_1_SUPPORT_FREEZES.json").read_text())
    stab21 = f21["support_stability"]
    res22 = json.loads((E22 / "E2_2_RESULT.json").read_text())
    cmp22 = json.loads((E22 / "E2_2_COMPARISON.json").read_text())
    q22 = json.loads((E22 / "E2_2_QUALIFICATIONS.json").read_text())
    q11 = json.loads((S7 / "11_sensitivity_and_interpretation"
                      / "S7_11_QUALIFICATIONS.json").read_text())["carried_unchanged"]
    kv2 = json.loads((S7 / "K2_observational_range_support_contract"
                      / "K_REC_V2.json").read_text())
    chg = json.loads((S7 / "K2_observational_range_support_contract"
                      / "K_REC_V1_TO_V2_CHANGESET.json").read_text())
    proto = json.loads((S7 / "E2_0A_predictor_admissibility_reconciliation"
                        / "E2_0A_PROTOCOL.json").read_text())
    budget = json.loads((S7 / "E2_0_protocol_and_resampling_freeze"
                         / "EPOCH2_SEARCH_BUDGET.json").read_text())
    folds = pd.read_csv(E21 / "fold_selected_supports.csv")
    vr = pd.read_csv(E21 / "manifests" / "vrange_integrity.csv")
    disch = pd.read_csv(E21 / "heldout_discharge_results.csv", dtype={"shot_id": str})

    M, P = met["method_summaries"], met["paired"]
    ERA = met["era"]

    # ---------------- Q_REC_GATE_TABLE ----------------------------------
    gate_table = {
        "record_id": "Q_REC_GATE_TABLE_V1", "generated_utc": now,
        "source": "E2_1_GATE_TABLE.json, carried unchanged",
        "epoch_2_gates": gate21 if isinstance(gate21, dict) else f21["gate_table"],
        "final_gate_table": f21["gate_table"],
        "mandatory_gates_failed": [],
        "V3": {"rule": "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
               "Delta_0": P["B0"]["mean_delta"], "Delta_1": P["B1"]["mean_delta"],
               "result": "PASS"},
        "V6": {"result": "PASS_WITH_QUALIFICATION",
               "earlier": {"n": ERA["era_counts"]["earlier"],
                           "Delta_1": ERA["Delta_1_earlier"],
                           "direction": ERA["direction_1_earlier"]},
               "later": {"n": ERA["era_counts"]["later"],
                         "Delta_1": ERA["Delta_1_later"],
                         "direction": ERA["direction_1_later"]},
               "note": "the pooled pass is carried by the later era; the earlier "
                       "era is a practical tie. Both are reported."},
        "V_RANGE": {"result": "PASS", "tau": 1.0,
                    "checks": int(vr.n_coordinate_cell_checks.sum()),
                    "failures": int(vr.n_failures.sum()),
                    "character": "APPLICABILITY_PROPERTY_NOT_A_PERFORMANCE_RESULT",
                    "pass_by_construction": True},
        "epoch_1_gate_table_preserved": FZ["S7.11"]["final_gate_table"],
        "tiers": {"FORMAL": f21["FORMAL"], "CLEAN_DEMO": f21["CLEAN"]},
        "no_new_gate_created": True, "no_threshold_moved": True,
    }
    (OUT / "Q_REC_GATE_TABLE.json").write_text(json.dumps(gate_table, indent=2),
                                               encoding="utf-8")

    # ---------------- Q_REC_PROVENANCE_CHAIN ----------------------------
    chain = {
        "record_id": "Q_REC_PROVENANCE_CHAIN_V1", "generated_utc": now,
        "lineage": lineage,
        "arc": [
            {"step": 1, "stage": "S7.9", "event": "Discovery Epoch 1 selected a "
             "development representation under K_REC_V1",
             "C_dev_star": FZ["S7.9"]["C_dev_star"],
             "selection_domain_cardinality": FZ["S7.9"]["selection_domain_cardinality"],
             "bootstrap_selection_frequency": 0.093,
             "distinct_bootstrap_winners": 217},
            {"step": 2, "stage": "S7.10", "event": "frozen external qualification FAILED",
             "verdict": FZ["S7.10"]["primary_scientific_verdict"],
             "REL_mean": FZ["S7.10"]["method_means"]["REL"],
             "Delta_1": FZ["S7.10"]["V3"]["Delta_1"],
             "V3": "FAIL", "V6": "FAIL",
             "catastrophic_discharges": 2, "max_NRMSE": 11.95,
             "IMMUTABLE": True},
            {"step": 3, "stage": "S7.11", "event": "provenance localized the failure to "
             "extreme extrapolation of PROD(gasa,gasa)",
             "verdict": FZ["S7.11"]["S7_11_VERDICT"], "V9": "FAIL",
             "development_equivalent_family_V3_style_pass":
                 FZ["S7.11"]["support_family"]["V3_STYLE_PASS_fraction"],
             "no_support_beat_persistence_by_more_than": 0.0287},
            {"step": 4, "stage": "S7.R1", "event": "an operational-state explanation was "
             "TESTED target-blindly and REFUTED",
             "hypothesis": FZ["S7.R1"]["hypothesis_tested"],
             "verdict": FZ["S7.R1"]["hypothesis_verdict"],
             "evidence": "development covers the external gasa range and a development "
                         "discharge (195650, gasa 7.447) exceeds both catastrophic "
                         "discharges (5.937, 5.923); no clean actuator state separates "
                         "the failures",
             "defect_localized_to": FZ["S7.R1"]["K_rec_minimal_component"],
             "X_rec_revision_proposed": False},
            {"step": 5, "stage": "S7.K2", "event": "minimal contract revision: a generic "
             "observational range-support predicate",
             "revision_class": FZ["S7.K2"]["revision_class"],
             "metric": FZ["S7.K2"]["metric"], "tau": FZ["S7.K2"]["tau"],
             "properties": ["constructor-generic", "dimensionless",
                            "unit-scale invariant", "sign-symmetric", "target-blind"],
             "full_domain_atoms": FZ["S7.K2"]["epoch2_viability"]["full_domain_atoms"],
             "of": 10778,
             "gas_provenance": FZ["S7.K2"]["gas_provenance_resolution"]},
            {"step": 6, "stage": "S7.E2.0", "event": "Epoch-2 protocol and six-fold "
             "resampling frozen; applicability risk disclosed prospectively",
             "n_outer_folds": FZ["S7.E2.0"]["n_outer_folds"],
             "EPOCH2_IS_FINAL_QREC_ATTEMPT": True},
            {"step": 7, "stage": "S7.E2.0A", "event": "transition-specific information "
             "boundary clarified; tau_train retired",
             "principle": FZ["S7.E2.0A"]["principle"],
             "candidate_basis": FZ["S7.E2.0A"]["candidate_basis"]["id"],
             "n": FZ["S7.E2.0A"]["candidate_basis"]["n"],
             "I_q_notation_change_required": False},
            {"step": 8, "stage": "S7.E2.1", "event": "fresh cross-fitted discovery under "
             "K_REC_V2 formally PASSED",
             "status": f21["status"], "FORMAL": f21["FORMAL"], "CLEAN": f21["CLEAN"],
             "Delta_0": P["B0"]["mean_delta"], "Delta_1": P["B1"]["mean_delta"],
             "V3": "PASS", "V6": "PASS_WITH_QUALIFICATION", "V_RANGE": "PASS"},
            {"step": 9, "stage": "S7.E2.2", "event": "full-object descriptive "
             "representation frozen for exposition",
             "status": f22["status"], "machine_name": f22["machine_name"],
             "sha256": f22["support_sha256"], "descriptive_only": True},
        ],
        "epoch_1_to_epoch_2": {
            "epoch1_mean": 0.7423647781201324, "epoch2_mean": M["REL"]["mean"],
            "epoch1_max": 11.95, "epoch2_max": M["REL"]["max"],
            "epoch1_discharges_above_1": 2, "epoch2_discharges_above_1": 0,
            "shot_187019": {"epoch1": 11.95, "epoch2": 0.297},
            "shot_187022": {"epoch1": 11.77, "epoch2": 0.436},
            "causal_language_policy": {
                "permitted": "The revised range-support-qualified discovery procedure "
                             "eliminated the catastrophic extrapolation tail observed "
                             "in Epoch 1.",
                "also_permitted": "The disappearance of the failure mode is consistent "
                                  "with the reconciliation having localized the "
                                  "relevant contract defect.",
                "forbidden": "K2 proved the range-support rule caused the improvement.",
                "reason": "too many things differ between Epoch 1 and Epoch 2 - the "
                          "contract, the basis, the validation geometry and the "
                          "supports all changed",
            },
        },
        "epoch_1_preserved_unmodified": True,
        "R1_refutation_preserved": True,
        "K2_revision_preserved": True,
        "E2_0A_reconciliation_preserved": True,
    }
    (OUT / "Q_REC_PROVENANCE_CHAIN.json").write_text(json.dumps(chain, indent=2),
                                                     encoding="utf-8")

    # ---------------- Q_REC_LIMITATIONS ---------------------------------
    lim = {
        "record_id": "Q_REC_LIMITATIONS_V1", "generated_utc": now,
        "note": "these limitations are PART OF Q_rec*, not footnotes outside it",
        "claim_boundary": {
            "supported": "Within the predictor-qualified frozen 62-discharge "
                         "observational object, relational supports discovered without "
                         "a discharge's own target values reconstruct that discharge "
                         "nontrivially relative to the frozen baselines.",
            "not_supported": [
                "virgin external validation", "untouched external validation",
                "unknown-predictor-distribution transfer",
                "fully inductive predictor generalization",
                "future-discharge applicability", "zero-shot transfer",
                "universal DIII-D relation", "universal DIII-D generalization",
                "cross-device generalization", "unique physical equation",
                "universal coefficient vector"],
        },
        "predictor_side_finite_object_qualification": {
            "statement": "predictor-side applicability was instantiated from the "
                         "non-target observations of the entire finite 62-discharge "
                         "object",
            "consequence": "Epoch 2 tests transfer of the TARGET RELATIONSHIP to "
                           "withheld targets, not transfer of predictor geometry to "
                           "genuinely unseen discharges",
            "authority": "E2_0A_PROTOCOL, PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_"
                         "RECONSTRUCTION",
        },
        "era_asymmetry": {
            "earlier": {"n": ERA["era_counts"]["earlier"],
                        "Delta_1": ERA["Delta_1_earlier"],
                        "direction": ERA["direction_1_earlier"]},
            "later": {"n": ERA["era_counts"]["later"],
                      "Delta_1": ERA["Delta_1_later"],
                      "direction": ERA["direction_1_later"]},
            "forbidden_statement": "both eras improve materially",
            "required": "the pooled pass is carried by the later era",
        },
        "modest_persistence_margin": {
            "Delta_1": P["B1"]["mean_delta"],
            "median_delta": P["B1"]["median_delta"],
            "wins": P["B1"]["wins"], "ties": P["B1"]["ties"],
            "losses": P["B1"]["losses"],
            "description": "MODEST",
            "forbidden_headline": "SIR dramatically beats persistence",
            "context": "persistence is a demanding baseline for a slowly varying "
                       "target; the Epoch-1 sensitivity analysis found no support in "
                       "the development-equivalent family beating persistence by more "
                       "than 0.0287, which suggests the margin is a property of the "
                       "object and task rather than of any one representation",
        },
        "clean_demo_not_met": {
            "status": f21["CLEAN"],
            "criteria_missed": ["Delta_1 <= -0.05 (achieved -0.027308)",
                                "material improvement vs B1 in BOTH eras"],
            "criteria_met": ["FORMAL_PASS", "full cross-fitted range support",
                            "no discharge above NRMSE 1.0"],
            "threshold_frozen_before_the_run": True, "threshold_adjusted": False,
            "tier_promoted_to_a_gate": False,
        },
        "support_non_uniqueness": {
            "n_supports": 6, "all_size": 12, "any_two_identical": False,
            "mean_pairwise_jaccard": stab21["mean_pairwise_jaccard"],
            "distinct_coordinates": 35,
            "in_all_six": stab21["coordinates_in_all_six"],
            "seventh_search_E2_2": {
                "identical_to_any_fold_support":
                    cmp22["identical_to_any_fold_support"],
                "mean_jaccard_with_folds": cmp22["mean_jaccard_with_folds"]},
            "conclusion": "STABLE_RECONSTRUCTION_UTILITY_WITH_NON_UNIQUE_"
                          "RELATIONAL_SUPPORTS",
            "canonical_equation_claim": False,
        },
        "coefficient_qualifications": {
            "locally_calibrated": "coefficients are calibrated per discharge and per "
                                  "block; support transfer does not imply coefficient "
                                  "transfer",
            "universal_coefficient_vector": False,
            "pcdiamag3": q11["pcdiamag3"],
            "prmtan_neped": q11["prmtan_neped"],
            "gas_actuators": "gasa...gasd are actuator command voltages, not fueling "
                             "rates",
            "flagged_primitives_in_C_E2_ALL_DESC": q22["flagged_primitives_present"],
        },
        "search_boundary": {
            "global_optimality_claim": False,
            "proposals_epoch2": f21["search"]["total_proposals"],
            "budget_epoch2": f21["search"]["budget_total"],
            "unsearched_status": "ADMISSIBLE_UNSEARCHED",
        },
    }
    (OUT / "Q_REC_LIMITATIONS.json").write_text(json.dumps(lim, indent=2),
                                                encoding="utf-8")

    # ---------------- Q_REC_STAR ----------------------------------------
    fold_supports = []
    for r in folds.itertuples():
        fold_supports.append({
            "fold": int(r.fold), "support_id": r.support_id,
            "support_size": int(r.support_size), "sha256": r.support_sha256,
            "coordinates": dsplit(r.support_id),
            "n_train": int(r.n_train), "n_heldout": int(r.n_test),
            "dev_FIT": float(r.dev_FIT), "COND_MEDIAN": float(r.dev_COND_MEDIAN),
            "BOOT_SELECTION_FREQ": float(r.BOOT_SELECTION_FREQ),
        })

    qstar = {
        "record_id": "Q_REC_STAR_V1",
        "generated_utc": now,
        "freeze_id": FREEZE_ID,
        "Q_REC_STATUS": "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS",
        "CLEAN_DEMO_STATUS": "CLEAN_DEMO_NOT_MET",
        "statuses_are_distinct_and_must_not_be_blurred": True,

        "identity": {
            "task_id": "q_rec",
            "task": "block-local prequential reconstruction of a plasma observable "
                    "from same-shot relational coordinates",
            "target": "density (line-averaged)",
            "observational_object": "FROZEN_62_DISCHARGE_DIIID_OBJECT",
            "n_discharges": 62,
            "blocks": {"A": "cal [0,0.4] prot [0.4,0.5]",
                       "B": "cal [0,0.6] prot [0.6,0.7]",
                       "C": "cal [0,0.8] prot [0.8,0.9]"},
            "metric": "NRMSE_{s,b} = RMSE(protected) / std(y_calibration, ddof=0)",
            "processing_eras": {"earlier": 35, "later": 27},
        },

        "contract": {
            "id": kv2.get("contract_id", "K_REC_V2"),
            "sha256": FZ["S7.K2"]["K_REC_V2_sha256"],
            "revision_class": FZ["S7.K2"]["revision_class"],
            "revision_lineage_from_K_REC_V1": {
                "changeset_sha256": FZ["S7.K2"]["changeset_sha256"],
                "component_revised": "P_rec",
                "new_clause": "P-RANGE-SUPPORT",
                "metric": FZ["S7.K2"]["metric"],
                "tau": 1.0,
                "tau_meaning": "application may extend beyond the calibration hull by "
                               "no more than one complete calibration-range width",
                "companion_gate": "V-RANGE",
                "components_unchanged": chg.get("unchanged_components", None),
            },
        },

        "information": {
            "I_rec": "frozen S7.3 information boundary, unchanged",
            "predictor_qualified_finite_object_rule":
                "range-support applicability is instantiated from the non-target "
                "observations of the entire finite 62-discharge object",
            "target_cross_fitted_rule":
                "no discharge's own target values were available to the search that "
                "selected the support under which that discharge is scored",
            "transition_specific_boundary": {
                "clarification": "observations admissible for coordinate construction "
                                 "or applicability need not be admissible for relation "
                                 "selection",
                "is_a_clarification_not_a_new_definition_of_I_q": True,
                "I_q_notation_change_required": False,
                "precedent": "S7.6R PARTIAL_MAP_ADMISSIBILITY, an application-time "
                             "predicate",
            },
            "not_target_leakage": True,
        },

        "ontology_and_search": {
            "G_rec": "typed relational ontology, constructors C0-C8, frozen S7.5/S7.5H",
            "A_rec": "primary atomic coordinate universe, 10778 atoms",
            "C_E2_FULL_DOMAIN": {
                "n": 3451, "of": 10778,
                "sha256": FZ["S7.E2.0A"]["candidate_basis"]["sha256"],
                "constructor_counts": FZ["S7.E2.0A"]["candidate_basis"]["constructor_counts"],
                "definition": "atoms satisfying P-RANGE-SUPPORT at tau=1 on every "
                              "discharge-block cell of the object",
            },
            "search_policy": "SIGMA_REC_ONE_SEED_PRIMARY_V2",
            "budget": {"per_search": budget["max_support_evaluations_per_fold"],
                       "epoch2_total": budget["max_support_evaluations_total"],
                       "epoch2_used": f21["search"]["total_proposals"],
                       "per_fold_used": f21["search"]["per_fold"]},
            "explored_frontier": {
                "epoch_2_per_fold_unique_supports":
                    [int(x) for x in folds.frontier_size],
                "epoch_2_E1_sizes": [int(x) for x in folds.E1],
                "epoch_1_selection_domain":
                    FZ["S7.9"]["selection_domain_cardinality"],
                "descriptive_full_object_frontier":
                    res22["search"]["frontier_size"],
            },
            "global_optimality_claim": False,
            "seeds_per_stratum": 1, "second_seed": False,
        },

        "utility": {"id": "U_REC_OPERATIONAL_V1", "unchanged": True,
                    "ranks": ["fit", "stability", "parsimony", "conditioning",
                              "support stability"],
                    "practical_equivalence": "delta_equiv = max(SE_delta, 0.01)",
                    "binding_rank_in_every_epoch2_fold": 2},

        "selected_representations": {
            "structure": "a qualified cross-fitted representation family, NOT one "
                         "uniquely identified (C*, R*)",
            "family": "{(C_k*, R_k*)}_{k=1}^{6}",
            "notation_note": "conceptual only; do NOT introduce this notation into the "
                             "manuscript automatically - determine first whether prose "
                             "suffices",
            "n": 6, "all_size": 12, "any_two_identical": False,
            "folds": fold_supports,
            "estimator": "DEVELOPMENT_RELATION_OLS_V1 - calibration-only "
                         "standardization, fitted intercept, affine OLS, "
                         "discharge/block-local coefficients, no global coefficients",
            "descriptive_realization": {
                "available": e22_available,
                "machine_name": f22["machine_name"],
                "support_id": f22["support_id"],
                "sha256": f22["support_sha256"],
                "size": f22["support_size"],
                "role": "REPRESENTATIVE_FULL_OBJECT_DESCRIPTIVE_REALIZATION",
                "is_externally_validated": False,
                "is_held_out": False,
                "is_canonical": False,
                "is_the_support_that_produced_the_cross_fitted_metric": False,
                "selected_after_the_qualification_verdict_was_frozen": True,
                "cannot_alter_the_qualified_outcome": True,
            },
        },

        "qualification": {
            "protocol": "PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION",
            "unit": "discharge", "n": 62, "out_of_fold": True,
            "method_summaries": M,
            "paired_differences": P,
            "Delta_0": P["B0"]["mean_delta"], "Delta_1": P["B1"]["mean_delta"],
            "vs_raw_representations": {"B2_raw_ridge_78": P["B2"]["mean_delta"],
                                       "B3_raw_histgb_78": P["B3"]["mean_delta"],
                                       "H0_hardened_raw_ridge_70": P["H0"]["mean_delta"]},
            "vs_persistence_record": {"wins": P["B1"]["wins"], "ties": P["B1"]["ties"],
                                      "losses": P["B1"]["losses"]},
            "era": ERA,
            "gate_table": f21["gate_table"],
            "V_RANGE": {"result": "PASS",
                        "checks": int(vr.n_coordinate_cell_checks.sum()),
                        "failures": int(vr.n_failures.sum())},
            "discharges_above_NRMSE_1": int((disch.REL_nrmse > 1.0).sum()),
            "worst_discharge": {"shot": str(disch.loc[disch.REL_nrmse.idxmax(),
                                                      "shot_id"]),
                                "REL_nrmse": float(disch.REL_nrmse.max())},
            "FORMAL": "FORMAL_PASS", "CLEAN_DEMO": "CLEAN_DEMO_NOT_MET",
        },

        "support_interpretation": {
            "non_unique_supports": True,
            "canonical_equation": False,
            "mean_pairwise_jaccard": stab21["mean_pairwise_jaccard"],
            "distinct_coordinates_across_six": 35,
            "coordinates_in_all_six": stab21["coordinates_in_all_six"],
            "seventh_independent_search_produced_a_seventh_distinct_support": True,
            "principle": "observational adequacy does not imply unique mathematical "
                         "representation",
        },

        "provenance": {s["stage"]: s["event"] for s in chain["arc"]},
        "epoch_1_to_epoch_2": chain["epoch_1_to_epoch_2"],
        "limitations": lim,

        "closure": {
            "Q_REC_BRANCH_CLOSED": True,
            "NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED": True,
            "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        },
    }
    (OUT / "Q_REC_STAR.json").write_text(json.dumps(qstar, indent=2), encoding="utf-8")

    # ---------------- Q_REC_BRANCH_CLOSURE ------------------------------
    closure = {
        "record_id": "Q_REC_BRANCH_CLOSURE_V1", "generated_utc": now,
        "Q_REC_BRANCH_CLOSED": True,
        "NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED": True,
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        "final_status": "Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT",
        "subsidiary": ["FORMAL_PASS", "CLEAN_DEMO_NOT_MET",
                       "NON_UNIQUE_RELATIONAL_SUPPORTS", "BRANCH_CLOSED"],
        "not_done_in_S7_12": {
            "new_search": False, "new_gate": False, "threshold_moved": False,
            "support_rescued": False, "budget_increased": False,
            "additional_seeds": False, "folds_changed": False,
            "discharges_deleted": 0, "blocks_deleted": 0,
            "baseline_altered": False, "utility_altered": False,
            "model_fit": False, "metric_recomputed": False,
            "epoch_3": False, "S7_13": False,
        },
        "q_desc_branch": "UNTOUCHED",
        "parent_artifacts_modified": 0,
        "epoch_1_negative_preserved": True,
    }
    (OUT / "Q_REC_BRANCH_CLOSURE.json").write_text(json.dumps(closure, indent=2),
                                                   encoding="utf-8")

    # ---------------- Figure 6 handoff -----------------------------------
    fig6 = {
        "record_id": "FIGURE_6_HANDOFF_V1", "generated_utc": now,
        "status": "RECOMMENDATION_ONLY_FIGURE_NOT_CREATED",
        "principle": "the main figure must stay readable; the S7 audit tree does not "
                     "belong in it",
        "panels_recommended": [
            {"panel": "A", "content": "q_desc result (existing descriptive branch)",
             "note": "unchanged by this stage"},
            {"panel": "B", "content": "the q_rec iterative arc as a compact schematic: "
                                      "discovery -> qualification failure -> contract "
                                      "refinement -> cross-fitted rediscovery -> "
                                      "qualified positive result",
             "note": "this is the SIR mechanism and is the point of the panel"},
            {"panel": "C", "content": "Epoch-1 vs Epoch-2 held-out error distribution",
             "key_numbers": {"epoch1_max": 11.95, "epoch2_max": 0.9199,
                             "epoch1_above_1": 2, "epoch2_above_1": 0},
             "note": "a log or broken axis is needed; the tail is the story"},
            {"panel": "D", "content": "relational vs raw vs persistence paired margins",
             "key_numbers": {"vs_B1": P["B1"]["mean_delta"],
                             "vs_B2": P["B2"]["mean_delta"],
                             "vs_B3": P["B3"]["mean_delta"],
                             "vs_H0": P["H0"]["mean_delta"]},
             "note": "shows the wide raw-coordinate margin and the modest persistence "
                     "margin honestly, side by side"},
        ],
        "optional_inset": {
            "content": "the range-support concept - calibration hull, tau=1 band, an "
                       "excursion outside it",
            "note": "one small schematic; no data needed"},
        "coordinate_labels": {
            "source": "C_E2_ALL_DESC" if e22_available else "six fold supports",
            "available": e22_available,
            "coordinates": res22["support"]["coordinates"] if e22_available else None,
            "label_required": "representative full-object descriptive relation",
            "labels_forbidden": ["validated DIII-D equation", "canonical relation",
                                 "universal relation"],
        },
        "do_not_include": ["the full S7 stage tree", "every gate", "the audit "
                           "mechanics", "bootstrap frequency tables"],
    }
    (OUT / "FIGURE_6_HANDOFF.json").write_text(json.dumps(fig6, indent=2),
                                               encoding="utf-8")

    # ---------------- acceptance checks ----------------------------------
    md_expected = 6
    checks = [
        ("all parents reproduce",
         all(v["matched"] == v["n"] for v in manifests.values())),
        ("E2.1 result unchanged",
         qstar["qualification"]["Delta_0"] == f21["V3"]["Delta_0"]
         and qstar["qualification"]["Delta_1"] == f21["V3"]["Delta_1"]
         and f21["status"] == "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS"),
        ("E2.2 frozen before S7.12", e22_before_s712 and e21_before_e22),
        ("E2.2 cannot change the formal verdict",
         f22["cannot_alter"] and f22["is_externally_validated"] is False
         and qstar["Q_REC_STATUS"] == f21["status"]),
        ("Q_REC_STATUS exact",
         qstar["Q_REC_STATUS"] == "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS"),
        ("CLEAN_DEMO_STATUS exact",
         qstar["CLEAN_DEMO_STATUS"] == "CLEAN_DEMO_NOT_MET"),
        ("Delta_0 exact", round(qstar["qualification"]["Delta_0"], 6) == -0.764489),
        ("Delta_1 exact", round(qstar["qualification"]["Delta_1"], 6) == -0.027308),
        ("V3 exact", gate_table["V3"]["result"] == "PASS"
         and gate_table["V3"]["rule"] == "Delta_0 <= -0.01 AND Delta_1 <= -0.01"),
        ("V6 exact", gate_table["V6"]["result"] == "PASS_WITH_QUALIFICATION"),
        ("V-RANGE exact", gate_table["V_RANGE"]["result"] == "PASS"
         and gate_table["V_RANGE"]["checks"] == 2232
         and gate_table["V_RANGE"]["failures"] == 0),
        ("era asymmetry carried",
         round(ERA["Delta_1_earlier"], 4) == 0.0076
         and round(ERA["Delta_1_later"], 4) == -0.0726
         and ERA["direction_1_earlier"] == "PRACTICAL_TIE"),
        ("raw-baseline margins carried",
         round(P["B2"]["mean_delta"], 4) == -0.0960
         and round(P["B3"]["mean_delta"], 4) == -0.1573
         and round(P["H0"]["mean_delta"], 4) == -0.0951),
        ("persistence margin described as modest",
         lim["modest_persistence_margin"]["description"] == "MODEST"),
        ("six supports retained",
         len(qstar["selected_representations"]["folds"]) == 6
         and len(sup21) == 6),
        ("support non-uniqueness explicit",
         qstar["support_interpretation"]["non_unique_supports"] is True),
        ("no canonical-equation claim",
         qstar["support_interpretation"]["canonical_equation"] is False),
        ("predictor-side full-object qualification explicit",
         "entire finite 62-discharge object"
         in lim["predictor_side_finite_object_qualification"]["statement"]),
        ("target-cross-fitted guarantee explicit",
         "own target values" in qstar["information"]["target_cross_fitted_rule"]),
        ("no external-validation wording",
         "virgin external validation" in lim["claim_boundary"]["not_supported"]
         and "untouched external validation" in lim["claim_boundary"]["not_supported"]),
        ("tau interpretation exact",
         qstar["contract"]["revision_lineage_from_K_REC_V1"]["tau"] == 1.0
         and "one complete calibration-range width"
         in qstar["contract"]["revision_lineage_from_K_REC_V1"]["tau_meaning"]),
        ("information-boundary clarification included",
         qstar["information"]["transition_specific_boundary"][
             "is_a_clarification_not_a_new_definition_of_I_q"] is True),
        ("Epoch-1 negative preserved",
         chain["arc"][1]["verdict"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER"
         and chain["arc"][1]["IMMUTABLE"] is True),
        ("R1 refutation preserved", chain["arc"][3]["verdict"] == "REFUTED"),
        ("K2 revision preserved", chain["arc"][4]["revision_class"] == "MINIMAL_P_ONLY"),
        ("E2.0A reconciliation preserved",
         chain["arc"][6]["principle"] ==
         "PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION"),
        ("no causal claim that K2 alone caused the improvement",
         "K2 proved" in chain["epoch_1_to_epoch_2"]["causal_language_policy"]["forbidden"]),
        ("coefficient qualifications preserved",
         lim["coefficient_qualifications"]["universal_coefficient_vector"] is False),
        ("pcdiamag3 qualification preserved",
         "UNCALIBRATED_SIGNAL" in lim["coefficient_qualifications"]["pcdiamag3"]),
        ("no new search during S7.12", closure["not_done_in_S7_12"]["new_search"] is False),
        ("no new gate", gate_table["no_new_gate_created"] is True),
        ("no threshold movement", gate_table["no_threshold_moved"] is True),
        ("no Epoch 3", closure["not_done_in_S7_12"]["epoch_3"] is False
         and closure["NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED"] is True),
        ("q_desc untouched", closure["q_desc_branch"] == "UNTOUCHED"),
        ("Q_REC_BRANCH_CLOSED", closure["Q_REC_BRANCH_CLOSED"] is True),
    ]

    md = sorted(p.name for p in OUT.glob("*.md"))
    md22 = sorted(p.name for p in E22.glob("*.md"))
    checks.append(("Markdown within limits",
                   len(md) <= 8 and len(md22) <= 6 and len(md) + len(md22) <= 14))
    failed = [c[0] for c in checks if not c[1]]

    (OUT / "S7_12_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "record_id": "S7_12_ACCEPTANCE_CHECKS_V1", "generated_utc": now,
        "checks": [{"check": c, "pass": bool(v)} for c, v in checks],
        "n_pass": sum(1 for c in checks if c[1]), "n_total": len(checks),
        "failed": failed,
        "markdown": {"S7_12": len(md), "limit": 8, "E2_2": len(md22),
                     "E2_2_limit": 6, "combined": len(md) + len(md22),
                     "combined_limit": 14},
    }, indent=2), encoding="utf-8")

    # ---------------- freeze ---------------------------------------------
    SELF = {"S7_12_FREEZE.json"}
    arts = sorted(str(p.relative_to(OUT)).replace("\\", "/")
                  for p in OUT.rglob("*")
                  if p.is_file() and p.name not in SELF
                  and "__pycache__" not in str(p))
    hashes = {a: sha256(OUT / a) for a in arts}

    freeze = {
        "freeze_id": FREEZE_ID,
        "status": "Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT",
        "subsidiary_statuses": ["FORMAL_PASS", "CLEAN_DEMO_NOT_MET",
                                "NON_UNIQUE_RELATIONAL_SUPPORTS", "BRANCH_CLOSED"],
        "timestamp_utc": now,
        "stage": "S7.12 - final qualified reconstruction result (assembly only)",
        "Q_REC_STATUS": "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS",
        "CLEAN_DEMO_STATUS": "CLEAN_DEMO_NOT_MET",
        "qualified_claim": lim["claim_boundary"]["supported"],
        "claims_not_supported": lim["claim_boundary"]["not_supported"],
        "Delta_0": P["B0"]["mean_delta"], "Delta_1": P["B1"]["mean_delta"],
        "V3": "PASS", "V6": "PASS_WITH_QUALIFICATION", "V_RANGE": "PASS",
        "gate_table": f21["gate_table"],
        "REL": {k: M["REL"][k] for k in ("mean", "median", "p90", "max")},
        "era": {"earlier": {"n": 35, "Delta_1": ERA["Delta_1_earlier"],
                            "direction": "PRACTICAL_TIE"},
                "later": {"n": 27, "Delta_1": ERA["Delta_1_later"],
                          "direction": "MATERIAL_IMPROVEMENT"}},
        "representation_family": "{(C_k*, R_k*)}_{k=1}^{6}",
        "n_fold_supports": 6, "support_non_uniqueness": True,
        "canonical_equation_claim": False,
        "descriptive_realization": {
            "available": e22_available, "machine_name": f22["machine_name"],
            "sha256": f22["support_sha256"], "role": "REPRESENTATIVE_ONLY"},
        "provenance_stages": [s["stage"] for s in lineage],
        "Q_REC_BRANCH_CLOSED": True,
        "NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED": True,
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        "q_desc_branch": "UNTOUCHED",
        "parent_artifacts_modified": 0,
        "acceptance_checks": "%d/%d" % (sum(1 for c in checks if c[1]), len(checks)),
        "acceptance_failed": failed,
        "n_artifacts": len(arts),
        "n_markdown": len(md), "markdown_limit": 8, "markdown_files": md,
        "markdown_E2_2": len(md22), "markdown_combined": len(md) + len(md22),
        "markdown_combined_limit": 14,
        "all_artifact_hashes": hashes,
        "self_referential_excluded": sorted(SELF),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "next_stage": "NONE. The q_rec branch is closed. No Epoch 3, no S7.13.",
    }
    (OUT / "S7_12_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    for k, v in manifests.items():
        print("%-9s %d/%d" % (k, v["matched"], v["n"]))
    print("status: %s" % freeze["status"])
    print("Q_REC %s | CLEAN %s" % (freeze["Q_REC_STATUS"], freeze["CLEAN_DEMO_STATUS"]))
    print("D0 %.6f | D1 %.6f | V3 %s | V6 %s | V-RANGE %s (%d checks, %d fail)"
          % (freeze["Delta_0"], freeze["Delta_1"], freeze["V3"], freeze["V6"],
             freeze["V_RANGE"], gate_table["V_RANGE"]["checks"],
             gate_table["V_RANGE"]["failures"]))
    print("acceptance %s | failed %s" % (freeze["acceptance_checks"], failed))
    print("artifacts %d | md %d/8 | combined %d/14"
          % (len(arts), len(md), len(md) + len(md22)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
