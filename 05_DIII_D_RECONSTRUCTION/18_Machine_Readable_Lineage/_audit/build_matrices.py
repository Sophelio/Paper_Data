"""Emit INFORMATION_FLOW_AUDIT.json and CLAIM_EVIDENCE_MATRIX.json."""
import json
from datetime import datetime, timezone
from pathlib import Path

S7 = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc).isoformat()

# ------------------------------------------------------------ information flow
flow = {
    "record_id": "S7_INFORMATION_FLOW_AUDIT_V2", "generated_utc": NOW,
    "scientific_task_id": "q_rec",
    "claim_branches_covered": ["QREC-B1", "QREC-B2"],
    "target_instance": "density",
    "policy_separation": {
        "I_q": "what information is epistemically admissible to the scientific task",
        "V_q": "what evidentiary role admissible information may play, and what "
               "qualification tests the resulting claim must satisfy",
        "evidence_roles_are": "VARIABLE_AND_TRANSITION_SPECIFIC",
        "worked_example": "predictor-side observations are admissible for "
                          "applicability assessment while the corresponding "
                          "held-out target values remain prohibited from support "
                          "discovery",
        "superseded_rule": "a datum or discharge does NOT carry one global "
                           "development/validation status for all transitions"},
    "branch": "q_rec", "target": "density",
    "boundary": {
        "n_quantities": 95, "n_admitted": 78, "n_excluded": 17,
        "exclusions": {
            "R1_target_itself": ["density"],
            "PRIMARY_NUMERICAL_SUPPORT_FAIL": ["vsurf"],
            "R5_unresolved_ancestry_fail_closed": [
                "aminor", "area", "betan", "drsep", "kappa", "li", "q95",
                "rmaxis", "rsurf", "tribot", "tritop", "volume", "zcur",
                "zmaxis", "zsurf"],
        },
        "note": "The 15 fail-closed exclusions are every EFIT-derived equilibrium "
                "quantity. The retired I_p branch admitted q95, betan, li and "
                "kappa and was retired for it.",
    },
    "adversarial_ancestry_test": {
        "instrument": "same test that retired the I_p branch: per-shot correlation, "
                      "single-signal R^2, and relative residual scatter of the "
                      "target after removing the best per-shot affine function of "
                      "the candidate",
        "benchmark_retired_q95_vs_Ip": {
            "median_abs_corr": 0.945, "median_R2": 0.79,
            "residual_scatter": 0.073, "verdict": "ALGEBRAIC_CIRCULARITY"},
        "prmtan_neped_vs_density": {
            "median_abs_corr": 0.892104, "median_R2": 0.795854,
            "residual_scatter": 0.534998, "verdict": "NO_ALGEBRAIC_CIRCULARITY"},
        "pcdiamag3_vs_density": {
            "median_abs_corr": 0.896865, "median_R2": 0.804384,
            "residual_scatter": 0.442202, "verdict": "NO_ALGEBRAIC_CIRCULARITY"},
        "n_predictors_median_R2_ge_0_75": 2, "n_predictors": 78,
        "frozen_predeclared_ablation": {
            "id": "PRMTAN_NEPED_ONLY", "support_size": 1,
            "mean_nrmse": 0.4631741682045934, "Delta_1": 0.2528999520928648,
            "V3_STYLE_PASS": False,
            "reading": "the single most suspect coordinate, alone, is far worse "
                       "than persistence; it is not a proxy for the target"},
        "governing_principle": "ancestry is definitional and computational, not "
                               "statistical; correlation is reported as context only",
    },
    "checks": [
        {"id": 1, "check": "no target descendant in any explanatory support",
         "status": "PASS",
         "evidence": "17 exclusions applied before coordinate construction; all 38 "
                     "selected coordinates lie inside the qualified basis"},
        {"id": 2, "check": "range support uses no held-out target value",
         "status": "PASS",
         "evidence": "predicate is a function of predictor values alone; "
                     "independently re-implemented and reproduced (3451 survivors, "
                     "exact constructor counts, 263 degenerate cells of 2,004,708)"},
        {"id": 3, "check": "normalization does not leak protected statistics",
         "status": "PASS",
         "evidence": "mu and sd from the calibration slice only; sd<=0 -> divisor "
                     "exactly 1.0; NRMSE normalized by std(y_calibration, ddof=0)"},
        {"id": 4, "check": "baselines share the target-availability assumptions",
         "status": "PASS",
         "evidence": "B0, B1, B1A, B2, B3, H0 all read y_cal only through the same "
                     "gated accessor"},
        {"id": 5, "check": "fold construction is target-blind", "status": "PASS",
         "evidence": "deterministic sort by (era, discharge id), position mod 6; no "
                     "seed; one partition generated; all 62 assignments reproduced"},
        {"id": 6, "check": "no support selection saw its own fold's held-out targets",
         "status": "PASS",
         "evidence": "runtime firewall vault; support hash precedes held-out target "
                     "access in all six folds; protected windows opened last"},
        {"id": 7, "check": "no threshold chosen from held-out performance",
         "status": "PASS",
         "evidence": "tau grid hashed before survivor counts; V3 -0.01 and "
                     "CLEAN_DEMO -0.05 frozen before Epoch 2; CLEAN_DEMO missed and "
                     "not moved"},
        {"id": 8, "check": "global predictor statistics permitted by the claim made",
         "status": "PASS_WITH_DISCLOSURE",
         "evidence": "applicability instantiated from the whole finite object; the "
                     "cost is carried in the claim itself (E2.0A)"},
        {"id": 9, "check": "block semantics consistent across estimator and baselines",
         "status": "PASS",
         "evidence": "three block-local prequential windows, identical for all seven "
                     "methods"},
    ],
    "protected_evidence_rule": {
        "triggered": True,
        "where": "S7.10 evaluation evidence was inspected and then used to diagnose "
                 "the defect reconciled at S7.K2",
        "consequence": "that evidence became development evidence for the revised "
                       "procedure and could no longer qualify anything downstream",
        "response": "a valid cross-fitted qualification design AND an explicitly "
                    "narrowed claim, taken together",
        "architectural_result": "descendant claim branch QREC-B2, constituted at "
                                "S7.E2.0"},
    "residual_risks": [
        {"risk": "prmtan_neped is in the target's scientific family",
         "status": "DISCLOSED_AND_BOUNDED"},
        {"risk": "pcdiamag3 is an uncalibrated signal", "status": "DISCLOSED"},
        {"risk": "predictor-side applicability used the whole object",
         "status": "DISCLOSED_AND_LOAD_BEARING"},
        {"risk": "Epoch-1 evaluation evidence informed the Epoch-2 contract",
         "status": "DISCLOSED_HANDLED_BY_CROSS_FITTING_AND_A_NARROWED_CLAIM"},
        {"risk": "the prmtan ablation is Epoch-1, not Epoch-2",
         "status": "NOTED_BOUNDS_TRANSFER"},
    ],
    "verdict": "NO_LEAKAGE_FOUND",
}
(S7 / "INFORMATION_FLOW_AUDIT.json").write_text(json.dumps(flow, indent=2),
                                                encoding="utf-8")

# --------------------------------------------------------- claim evidence matrix
def C(cid, claim, branch, stage, script, data, result, value, status, limits,
      superseded=None, manuscript=None):
    return {"claim_id": cid, "claim": claim, "branch": branch, "stage": stage,
            "manuscript_location": manuscript,
            "supporting_script": script, "supporting_data": data,
            "supporting_result": result, "value": value,
            "validation_status": status, "limitations": limits,
            "superseded_predecessor": superseded}


E21 = "E2_1_crossfitted_discovery_and_qualification"
E22 = "E2_2_full_object_descriptive_representation"

CLAIMS = [
    C("REC-01",
      "Within the predictor-qualified frozen 62-discharge object, relational "
      "supports discovered without a discharge's own target values reconstruct "
      "that discharge nontrivially relative to the frozen baselines.",
      "q_rec", "S7.E2.1 / S7.12",
      "%s/scripts/e2_1_c_aggregate.py" % E21,
      "%s/heldout_discharge_results.csv" % E21,
      "S7_12_qualified_result/Q_REC_STAR.json",
      {"Delta_0": -0.764489, "Delta_1": -0.027308, "V3": "PASS"},
      "QUALIFIED_POSITIVE_FORMAL_PASS",
      ["not external validation", "not future-discharge transfer",
       "not zero-shot", "predictor-side applicability used the whole finite object",
       "margin over persistence is modest and era-asymmetric"],
      "the retired I_p / REL10 structural-transfer claim",
      "Results 1.5, Fig. 4b, Supplementary S7.8 - MUST BE REPLACED"),
    C("REC-02",
      "Relational coordinates add substantial reconstruction utility over the "
      "tested raw-coordinate representations of the same admissible information.",
      "q_rec", "S7.E2.1",
      "%s/scripts/e2_1_c_aggregate.py" % E21,
      "%s/heldout_discharge_results.csv" % E21,
      "%s/E2_1_CROSSFITTED_METRICS.json" % E21,
      {"vs_B2_raw_ridge_78": -0.0960, "vs_B3_raw_histgb_78": -0.1573,
       "vs_H0_hardened_ridge_70": -0.0951},
      "SUPPORTED",
      ["only the tested comparators", "not 'universally better than raw features'"],
      None, "Results 1.5 - candidate replacement for the retired REL10/RAW10 claim"),
    C("REC-03",
      "The object supports a family of adequate relational representations rather "
      "than identifying one.",
      "q_rec", "S7.9 / S7.11 / S7.E2.1 / S7.E2.2",
      "%s/scripts/e2_1_c_aggregate.py" % E21,
      "%s/fold_selected_supports.csv" % E21,
      "%s/support_recurrence.csv" % E21,
      {"n_supports": 6, "all_size": 12, "any_identical": False,
       "mean_pairwise_jaccard": 0.285244, "distinct_coordinates": 35,
       "seventh_search_also_distinct": True,
       "epoch1_bootstrap_winners": 217},
      "SUPPORTED",
      ["no canonical equation", "no fold support is canonical",
       "C_E2_ALL_DESC is representative only"],
      None, "Results 1.5 - present as a positive finding"),
    C("REC-04",
      "The revised range-support-qualified discovery procedure eliminated the "
      "catastrophic extrapolation tail observed in Epoch 1.",
      "q_rec", "S7.10 / S7.E2.1",
      "figures/make_s7_figures.py",
      "10_external_validation/external_discharge_metrics.csv; "
      "%s/heldout_discharge_results.csv" % E21,
      "S7_12_qualified_result/Q_REC_PROVENANCE_CHAIN.json",
      {"epoch1_max": 11.95, "epoch2_max": 0.9199,
       "epoch1_above_1": 2, "epoch2_above_1": 0,
       "shot_187019": [11.95, 0.297], "shot_187022": [11.77, 0.436]},
      "SUPPORTED_NON_CAUSAL",
      ["NOT a controlled ablation: contract, basis, validation geometry and "
       "supports all differ between epochs",
       "forbidden: 'K2 proved the range-support rule caused the improvement'"],
      None, "Results 1.5 / Supplement - new"),
    C("REC-05",
      "A frozen, prospectively declared external qualification of the Epoch-1 "
      "representation failed.",
      "q_rec", "S7.10", "10_external_validation/scripts",
      "10_external_validation/external_discharge_metrics.csv",
      "10_external_validation/S7_10_FREEZE.json",
      {"REL_mean": 0.742365, "B1_mean": 0.210274, "Delta_1": 0.532091,
       "V3": "FAIL", "V6": "FAIL", "Omega_rec": "EMPTY"},
      "NEGATIVE_RESULT_PRESERVED",
      ["this is the result, not a preamble; nothing was repaired after it"],
      None, "Supplement - new; currently absent"),
    C("REC-06",
      "The operational-state explanation of the Epoch-1 failure was tested "
      "target-blindly and refuted.",
      "q_rec", "S7.R1", "R1_operational_state_reconciliation/scripts",
      "R1_operational_state_reconciliation (target-blind predictor evidence)",
      "R1_operational_state_reconciliation/S7_R1_FREEZE.json",
      {"hypothesis_verdict": "REFUTED",
       "earliest_invalidated_stage": "NONE_OF_THE_INSTANTIATED_OBJECTS",
       "K_REC_REVISION_REQUIRED": True, "minimal_component": "P_rec"},
      "SUPPORTED",
      ["refutation, not confirmation of an alternative mechanism"],
      None, "Supplement - new; the load-bearing methodological episode"),
    C("REC-07",
      "Observational range support at tau = 1 admits 3,451 of 10,778 atoms and "
      "eliminates no constructor family.",
      "q_rec", "S7.K2", "K2_observational_range_support_contract/scripts",
      "K2_observational_range_support_contract/range_support_threshold_sensitivity.csv",
      "K2_observational_range_support_contract/S7_K2_FREEZE.json",
      {"tau": 1.0, "survivors": 3451, "of": 10778,
       "family_survival_fraction": {"C0": 0.773, "C1": 0.305, "C2": 0.715,
                                    "C3": 0.155, "C5": 0.205, "C6": 0.256,
                                    "C7": 0.234},
       "degenerate_cells": 263},
      "INDEPENDENTLY_REPRODUCED",
      ["an applicability property, not a performance result",
       "tau is not a hyperparameter, regularizer, physical constant or "
       "confidence level"],
      None, "Supplement - new"),
    C("DESC-01",
      "A shared seven-coordinate relational support organizes standardized "
      "dW_dia/dt across 62 discharges, with discharge-specific coefficients.",
      "q_desc", "external: canonical_d3d_62_shot_run_v1",
      "canonical_d3d_62_shot_run_v1/build_canonical_run_package.py",
      "canonical_d3d_62_shot_run_v1/d3d_discharge_metrics.csv",
      "canonical_d3d_62_shot_run_v1/d3d_pooled_metrics.json",
      {"pooled_rmse": 0.05758467247445343, "mean_vector_rmse": 0.4125238315775986,
       "n_discharges": 62, "n_samples_each": 1000},
      "SUPPORTED_CURRENT",
      ["target-containing implicit closure, not an independent predictor",
       "not causal", "cohort-mean coefficients summarize, they do not define"],
      None, "Results 1.5, Fig. 4a, Supplementary S7.3-S7.4"),
    C("DESC-02",
      "Coefficient identifiability conditional on the selected support is mixed: "
      "five coefficients robustly resolved, two uncertainty-dominated, two robust "
      "coefficient-space directions of five positive.",
      "q_desc", "external: Coefficient_conditioning/Correction_audit",
      "Coefficient_conditioning/Correction_audit/run_correction_audit.py",
      "Coefficient_conditioning/Correction_audit/tables/"
      "corrected_coefficient_classification.csv",
      "Coefficient_conditioning/Correction_audit/outputs/"
      "coefficient_conditioning_correction_summary.json",
      {"verdict": "D3D-MIXED-COEFFICIENT-IDENTIFIABILITY",
       "robust": 5, "uncertainty_dominated": 2,
       "positive_directions": 5, "robust_directions": 2,
       "rank6_median_rel_coef": 0.7993154563548318,
       "rank6_median_abs_rmse": 0.031029606819801332,
       "estimator": "REML_primary_with_ML_sensitivity"},
      "SUPPORTED_CURRENT",
      ["conditional on the selected support",
       "no coefficient is a dimensional physical constant"],
      "D3D-COEFFICIENT-FAMILY-RESOLVED (archived and removed from active outputs)",
      "Supplementary S7.7, Fig. S1"),
    C("DESC-03",
      "The eliminated target-map is explicitly ill conditioned.",
      "q_desc", "external: Implicit_elimination_and_denominator_conditioning",
      "Implicit_elimination_and_denominator_conditioning/"
      "run_implicit_conditioning_audit.py",
      "Implicit_elimination_and_denominator_conditioning/outputs/"
      "eliminated_A_summary.json",
      "Implicit_elimination_and_denominator_conditioning/outputs/"
      "implicit_conditioning_summary.json",
      {"verdict": "D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED",
       "min_abs_A": 2.6428213717455407e-07,
       "frac_abs_A_lt_1e-4": 0.0023548387096774194,
       "shiftval_range": [14.643161791053483, 24.2426158353731],
       "elimination_identity_max_error": 7.896461262646426e-15,
       "explicit_pooled_rmse": 187.2273661101626},
      "SUPPORTED_CURRENT",
      ["a briefing checkpoint expecting ~41% of samples below |A|<1e-4 is not "
       "supported; the frozen value is 0.24%"],
      None, "Supplementary S7.6"),
    C("RETIRED-01",
      "A ten-coordinate target-free relational support selected on seven "
      "discharges retains reconstruction utility on 55 external discharges "
      "(REL10 0.126 vs RAW10 0.182, better on 46/55).",
      "q_rec (retired)", "external: DIII-D Ip relational reconstruction",
      "n/a", "Figure_data/d3d_reconstruction_summary.json",
      "fig6data/RETIREMENT_RECORD.json",
      {"pooled_rmse_REL10": 0.1257122694487528,
       "pooled_rmse_RAW10": 0.182086862730149, "wins": 46, "of": 55},
      "RETIRED_FOR_PROVENANCE_LEAKAGE",
      ["6/10 REL10 and 4/10 RAW10 features carry upstream I_p dependence",
       "a constant persistence predictor (0.0685) beats all three reported models",
       "must not be cited"],
      None, "Results 1.5, Fig. 4b, Supplementary S7.8 - STILL PRESENT IN THE "
            "SHIPPED MANUSCRIPT"),
]

for _c in CLAIMS:
    if _c["branch"] == "q_rec":
        _c["scientific_task_id"] = "q_rec"
        _c["claim_branch"] = ("QREC-B2" if _c["claim_id"] in
                              ("REC-01", "REC-02", "REC-03", "REC-04", "REC-07")
                              else "QREC-B1")
    elif _c["branch"] == "q_desc":
        _c["scientific_task_id"] = "q_desc"
        _c["claim_branch"] = None
    else:
        _c["scientific_task_id"] = "q_rec"
        _c["claim_branch"] = "RETIRED_PRE_S7_LINEAGE"

matrix = {"record_id": "S7_CLAIM_EVIDENCE_MATRIX_V2", "generated_utc": NOW,
          "n_claims": len(CLAIMS), "claims": CLAIMS,
          "branch_lineage": {
              "q_rec": ["QREC-B1", "QREC-B2"],
              "QREC-B2": "descendant of QREC-B1, constituted at S7.E2.0",
              "note": "REC-04 and REC-07 span both branches by construction "
                      "(they compare epochs); they are attributed to QREC-B2, "
                      "which is where the comparison is reported."},
          "rule": "a claim without a reproducible evidence path is not "
                  "publication-ready"}
(S7 / "CLAIM_EVIDENCE_MATRIX.json").write_text(json.dumps(matrix, indent=2),
                                               encoding="utf-8")
print("information-flow checks:", len(flow["checks"]))
print("claims:", len(CLAIMS))
