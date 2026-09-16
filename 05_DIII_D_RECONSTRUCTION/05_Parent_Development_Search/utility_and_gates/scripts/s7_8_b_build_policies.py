"""S7.8 step B - emit the machine-readable utility and qualification policies.

This script FREEZES EXECUTION RULES ONLY. It computes no utility quantity over
Ahat_rec, selects no candidate, runs no baseline, and opens no external value.
"""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).isoformat()

SELECTION_DOMAIN = "AHAT_REC_DENSITY_ONE_SEED_V2"
PARENT_CONTRACT = [
    "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V1",
    "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V2",
]
PRIMARY_SEARCH = "D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2"

DOMAIN_BLOCK = {
    "selection_domain": SELECTION_DOMAIN,
    "selection_domain_cardinality": 162845,
    "global_optimality_claim": False,
    "domain_reading": (
        "every quantity defined here is evaluated over the frozen explored "
        "frontier Ahat_rec only; A_rec minus Ahat_rec remains "
        "ADMISSIBLE_UNSEARCHED and carries no negative finding"),
}


def write(name: str, obj: dict) -> None:
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print("wrote", name)


# ======================================================================
# canonical identity and shared numerical conventions
# ======================================================================
CANONICAL_ID = {
    "rule_id": "CANONICAL_SUPPORT_ID_V1",
    "authoritative_registry": (
        "07_search_policy_and_frontier/one_seed_primary_v2/"
        "explored_support_registry.csv"),
    "id_form": "atom signatures joined by a top-level pipe, atoms ascending-sorted",
    "atom_membership_rule": (
        "split the support_id on pipe characters occurring at parenthesis "
        "depth 0 ONLY"),
    "hazard": (
        "C4/C6/C7/C8 atom signatures PHASE(i|j), LEVEL_RATE(i|j), "
        "RATE_OVER_LEVEL(i|j), LEVEL_OVER_RATE(i|j) embed a pipe inside their "
        "own parentheses; a naive split on the pipe returns the wrong atom "
        "count for 116608 of the 162845 registry rows (71.6 percent)"),
    "mandatory_checksum": (
        "the depth-aware parse must reproduce registry support_size for all "
        "162845 rows before any utility computation begins"),
    "verified_in_s7_8": True,
    "tie_break": {
        "rule": "lexicographic ascending byte order of the canonical support_id",
        "role": "FINAL deterministic tie-break at every rank",
        "sufficient": (
            "support_ids are unique across Ahat_rec, so the tie-break always "
            "resolves to exactly one candidate"),
    },
}

STANDARDIZATION = {
    "rule_id": "CALIBRATION_STANDARDIZATION_V1",
    "inherited_from": "S7.7R scripts/s7_7r_b_search.py (unchanged)",
    "location": "fit on CALIBRATION rows only, applied unchanged to protected rows",
    "mean": "mu = mean of the coordinate over the cell calibration interval",
    "sd": "sd = std of the coordinate over the cell calibration interval, ddof=0",
    "zero_sd_rule": (
        "if sd <= 0 or sd is non-finite the divisor is the exact value 1.0; "
        "the column is centred but not rescaled"),
    "epsilon_added": False,
    "consequence_of_zero_sd": (
        "the standardized column is exactly zero on the calibration rows, so "
        "the design loses rank there and sigma_min = 0, giving kappa = +inf "
        "under the Rank-4 rule; this is a conditioning outcome, never an "
        "admissibility decision"),
}

CELL_GEOMETRY = {
    "n_development_discharges": 20,
    "blocks": ["A", "B", "C"],
    "n_cells": 60,
    "block_windows": {
        "A": {"calibration": [0.0, 0.4], "evaluation": [0.4, 0.5]},
        "B": {"calibration": [0.0, 0.6], "evaluation": [0.6, 0.7]},
        "C": {"calibration": [0.0, 0.8], "evaluation": [0.8, 0.9]},
    },
    "protection_model": "BLOCK_LOCAL_PROTECTION",
    "semantics": "sequential / prequential",
    "external_cohort": "GLOBALLY SEALED until S7.10",
    "unchanged_from": "S7.2 / S7.2C validation geometry",
}

PRIMARY_METRIC = {
    "metric_id": "NRMSE_CALIBRATION_NORMALIZED_V1",
    "inherited_from": "S7.2C metric_and_gate_definitions.json (unchanged)",
    "scale": "scale_{s,b} = std(y_calibration_{s,b}, ddof=0)",
    "cell": "NRMSE_{s,b} = RMSE(y_protected, yhat_protected) / scale_{s,b}",
    "zero_scale_behaviour": "INVALID_FOR_NORMALIZED_SCORING",
    "epsilon_added": False,
    "per_discharge": "NRMSE_s(C) = mean over blocks A,B,C of NRMSE_{s,b}(C)",
    "candidate_level": "FIT(C) = mean over the 20 development discharges of NRMSE_s(C)",
    "units": "calibration-normalized RMSE units (dimensionless)",
    "raw_rmse": {
        "retained": True,
        "role": "REPORTING_ONLY",
        "is_primary_utility_measure": False,
        "unit": "target physical unit (density)",
    },
    "non_finite_cell_rule": {
        "rule": "a candidate with any non-finite cell has FIT = +inf and cannot enter E_fit",
        "observed_in_frozen_frontier": 0,
        "note": "all 162845 x 60 cells of the frozen frontier are finite; the rule is defensive",
    },
}

# ======================================================================
# 1. practical equivalence
# ======================================================================
practical_equivalence = {
    "policy_id": "PRACTICAL_EQUIVALENCE_OPERATIONAL_V1",
    "generated_utc": NOW,
    "authoritative_source": "S7.2C correction clause C-01",
    "authoritative_rule": {
        "delta_equiv": "max(SE_delta, 0.01)",
        "test": "A and B practically equivalent iff |NRMSE_A - NRMSE_B| <= delta_equiv",
        "reading": "within one SE OR within the 0.01 practical floor",
        "units": "CALIBRATION-NORMALIZED RMSE units",
        "raw_rmse_interpretation": "FORBIDDEN",
    },
    "floor": {
        "value": 0.01,
        "immutable": True,
        "interpretation": "1 percent of the calibration target standard-deviation scale",
        "declared_before": "any search result existed (S7.2 V1, retained by S7.2C)",
        "may_be_adjusted_after_seeing_results": False,
    },
    "epsilon_added": False,
    "se_delta": {
        "step_1": "aggregate the three validation blocks within each development discharge",
        "step_2": "compute the paired candidate difference per development discharge",
        "step_3": "SE_delta = sd(delta_s, ddof=1) / sqrt(20)",
        "delta_s": "delta_s = mean_b NRMSE_{A,s,b} - mean_b NRMSE_{B,s,b}",
        "n": 20,
        "ddof": 1,
        "unit": "development discharge",
        "pairing": "paired within discharge; both candidates scored on identical cells",
    },
    "superseded": {
        "clause": "S7.2 V1 UTILITY_AND_QUALIFICATION_POLICY.md practical-equivalence conjunction",
        "v1_wording": "practically equivalent iff within 1 SE AND within 0.01",
        "status": "SUPERSEDED_BY_S7.2C_C01",
        "defect": (
            "the conjunction made the floor inoperative exactly when it was "
            "needed: a tiny SE stayed binding and the 0.01 floor never relaxed "
            "anything"),
        "must_not_be_used": True,
    },
    "operational_resolutions": {
        "OR-02": {
            "question": "is the Rank-1 equivalence set a transitive class or a comparison against the best?",
            "resolution": (
                "E_fit is defined by pairwise comparison against the Rank-1 best "
                "candidate: C in E_fit iff |FIT(C) - FIT_best| <= "
                "max(SE_delta(C, best), 0.01)"),
            "authority": "S7.2 V1 lexicographic wording plus the section-10 instantiation; it is not a transitive equivalence class and must not be closed transitively",
            "outcome_independent": True,
            "best_is_always_member": "SE_delta(best,best) = 0 and |0| <= 0.01",
        },
        "OR-11": {
            "question": "how is a non-finite candidate treated?",
            "resolution": "FIT = +inf, excluded from E_fit; never re-labelled inadmissible",
            "observed_count_in_frontier": 0,
        },
    },
    "not_taken": [
        "top-K truncation",
        "a tuned epsilon",
        "a percentage-of-best tolerance",
        "any post-hoc adjustment of the 0.01 floor",
    ],
    "execution_stage": "S7.9",
    **DOMAIN_BLOCK,
}

# ======================================================================
# 2. estimator
# ======================================================================
estimator_policy = {
    "policy_id": "ESTIMATOR_POLICY_V1",
    "generated_utc": NOW,
    "estimator_id": "DEVELOPMENT_RELATION_OLS_V1",
    "role": "PRIMARY development relation estimator for U_rec",
    "parent_permission": {
        "source": "S7.2 RELATION_AND_TRANSFER_POLICY.md",
        "wording": "a transparent linear estimator: ordinary least squares, or ridge with a development-selected penalty",
        "s7_8_choice": "OLS",
        "is_a_narrowing_not_a_change": True,
    },
    "reasons": [
        "relation support is at most 12 coordinates",
        "the scientific claim must remain attributable to the coordinate representation rather than to estimator complexity",
        "OLS is transparent and hyperparameter-free",
        "it is the estimator already used by the frozen search proxy SEARCH_PROXY_OLS_V1",
        "S7.7R found no rank-deficient explored design (atoms_rank_deficient = 0)",
        "no hyperparameter selection is required, so no selection discretion is created",
    ],
    "freeze_character": {
        "is_estimator_policy_freeze": True,
        "is_performance_comparison": False,
        "no_ridge_fit_was_run_to_decide_this": True,
    },
    "procedure": [
        "1. fit predictor means and standard deviations on the cell CALIBRATION interval only",
        "2. standardize coordinates using those calibration values",
        "3. apply the calibration mean and sd unchanged to the protected predictor values",
        "4. fit an intercept",
        "5. solve affine OLS on the standardized design",
        "6. coefficients are discharge/block local",
    ],
    "intercept": {
        "fitted": True,
        "counts_toward_parsimony": False,
        "counts_toward_conditioning": False,
        "rationale": "the Lorenz benchmarks in this project established that a no-intercept estimator silently destroys performance when the target is not centred",
    },
    "coefficients": {
        "shared_across_discharges": False,
        "scope": "one coefficient vector per discharge/block cell",
        "transfer_statement": "the scientific coordinate support is shared; numerical coefficients may be discharge-specific",
    },
    "standardization": STANDARDIZATION,
    "ridge": {
        "primary_status": "NOT_PRIMARY_IN_S7_8",
        "permitted_later_as": "CONDITIONING sensitivity realization, separately labelled",
        "may_be_chosen_on_performance": False,
        "must_be_justified_by": "numerical conditioning evidence on development data only",
        "must_be_granted_equally_to": "baseline B2",
        "must_be_recorded_in": "the decision ledger with conditioning evidence",
    },
    "search_proxy_equivalence": {
        "search_proxy_id": "SEARCH_PROXY_OLS_V1",
        "method": "partitioned (Frisch-Waugh) normal equations on the centred calibration design",
        "algebraic_relation": "identical to numpy.linalg.lstsq on the explicit [1, Z] design for a full-rank design",
        "s7_7r_numerical_check": {
            "reference": "numpy.linalg.lstsq(..., rcond=None)",
            "support_sizes_tested": [2, 5, 9, 12],
            "max_relative_deviation": 1.7176192738513556e-13,
            "tolerance": 1e-09,
            "passes": True,
        },
        "semantic_separation": {
            "statement": (
                "the fact that FIT(C) may numerically equal J_search(C) does NOT "
                "make J_search the scientific utility"),
            "J_search_role": "determined WHERE the search looked (navigation)",
            "FIT_role": "one criterion inside U_rec applied to the frozen frontier",
            "preserved_even_if_numbers_coincide": True,
            "search_frequency_is_not_scientific_importance": True,
            "search_priority_is_not_validation": True,
        },
    },
    "execution_stage": "S7.9",
    **DOMAIN_BLOCK,
}

# ======================================================================
# 3. Rank-2 stability metrics
# ======================================================================
stability_metric_policy = {
    "policy_id": "STABILITY_METRIC_POLICY_V1",
    "generated_utc": NOW,
    "parent_wording": "generalization / stability: aggregated across development discharges and all three predeclared temporal blocks",
    "parent_machine_readable_definition": {
        "source": "K_REC_PRE_V2.json U_rec.criteria_in_order",
        "content": "criterion NAME only; no stronger machine-readable operational definition exists",
        "conflict_found": False,
        "conflict_check_note": (
            "the section-11 operationalization was compared against the only "
            "machine-readable parent (K_REC_PRE_V2 U_rec) and against "
            "UTILITY_AND_QUALIFICATION_POLICY.md; the parent constrains the "
            "criterion name, its rank and its data scope, all of which are "
            "honoured; no override occurred"),
    },
    "applies_within": "E_fit (the Rank-1 practical-equivalence set)",
    "no_weighted_score": True,
    "block_worst": {
        "symbol": "BLOCK_WORST(C)",
        "definition": "max over b in {A,B,C} of (mean_s NRMSE_{s,b}(C))",
        "aggregation_order": "discharges first, then the maximum over blocks",
        "worst_block": {
            "symbol": "b_star(C)",
            "definition": "argmax_b (mean_s NRMSE_{s,b}(C))",
            "tie_break": "earliest block in the canonical order A < B < C",
            "identity": "BLOCK_WORST(C) = mean_s NRMSE_{s, b_star(C)}(C)",
        },
        "equivalence": {
            "rule": "delta = max(SE_delta_worst, 0.01)",
            "paired_difference": (
                "d_s(A,B) = NRMSE_{s, b_star(A)}(A) - NRMSE_{s, b_star(B)}(B); "
                "each candidate contributes its OWN worst block"),
            "se": "SE_delta_worst = sd(d_s, ddof=1) / sqrt(20)",
            "coherence_proof": (
                "mean_s d_s(A,B) = BLOCK_WORST(A) - BLOCK_WORST(B) exactly, so "
                "the paired discharge-level differences average to precisely the "
                "candidate-level quantity being compared; the SE is therefore the "
                "standard error OF THAT difference and introduces no discretion"),
            "requires_discretion": False,
            "fallback_rule": {
                "described_in": "S7.8 instruction section 11",
                "content": "use the fixed absolute 0.01 NRMSE floor only, and record the qualification",
                "status": "NOT_REQUIRED",
                "reason": (
                    "a mathematically coherent paired-SE definition WAS "
                    "implementable without discretion, because b_star(C) is "
                    "determined by the frozen formula and its A<B<C tie-break; "
                    "the fallback is therefore not invoked"),
            },
            "new_tunable_threshold_introduced": False,
        },
    },
    "shot_p90": {
        "symbol": "SHOT_P90(C)",
        "definition": "90th percentile over the 20 values NRMSE_s(C)",
        "estimator": "numpy.percentile(v, 90, method='linear')",
        "estimator_frozen_because": (
            "percentile estimators differ between conventions; the library "
            "default is fixed here so the quantity is reproducible, not chosen "
            "to favour any outcome"),
        "n": 20,
        "interpolation_note": "for n=20 the linear method interpolates between the 18th and 19th order statistics at index 0.9*19 = 17.1",
        "epsilon_or_tolerance": None,
        "minimized": "deterministically, after the BLOCK_WORST equivalence restriction",
    },
    "rank_2_order": [
        "minimize BLOCK_WORST",
        "among candidates practically equivalent on BLOCK_WORST, minimize SHOT_P90 exactly",
    ],
    "exact_minimum_semantics": (
        "the SHOT_P90 step takes the exact argmin; ties are retained in full and "
        "resolved by later ranks, never by a new tolerance"),
    "execution_stage": "S7.9",
    **DOMAIN_BLOCK,
}

# ======================================================================
# 4. conditioning
# ======================================================================
conditioning_policy = {
    "policy_id": "CONDITIONING_POLICY_V1",
    "generated_utc": NOW,
    "parent_wording": "conditioning: better-conditioned design matrix (lower condition number)",
    "design": {
        "matrix": "Z_{s,b}(C)",
        "rows": "the CALIBRATION rows of discharge s, block b",
        "columns": "the |C| scientific coordinates of the support",
        "standardization": "calibration mean and sd of that same cell (see CALIBRATION_STANDARDIZATION_V1)",
        "intercept_column": "EXCLUDED",
        "centring_note": (
            "because standardization subtracts the calibration mean, Z restricted "
            "to the calibration rows is already exactly column-centred; the "
            "centred-design and standardized-design readings coincide, so no "
            "ambiguity remains"),
    },
    "kappa": {
        "definition": "kappa_{s,b}(C) = sigma_max(Z_{s,b}) / sigma_min(Z_{s,b})",
        "computed_from": "singular values of Z (SVD)",
        "normal_equation_squared_condition_number": "FORBIDDEN",
        "zero_sigma_min_rule": "sigma_min == 0 implies kappa = +inf",
        "singleton_note": (
            "for |C| = 1 the design has a single singular value and kappa = 1 "
            "exactly, so log10(kappa) = 0; this is an arithmetic consequence of "
            "the frozen definition, recorded here in advance rather than "
            "discovered later"),
    },
    "candidate_level": {
        "COND_MEDIAN": "median over the 60 discharge/block cells of log10(kappa_{s,b}(C))",
        "COND_P90": "numpy.percentile(log10(kappa) over the 60 cells, 90, method='linear')",
        "COND_MAX": "max over the 60 cells of log10(kappa_{s,b}(C))",
        "log_base": 10,
        "infinite_cells": (
            "log10(+inf) = +inf propagates; the median remains defined unless at "
            "least half the cells are infinite, in which case COND_MEDIAN = +inf"),
    },
    "rank_4_order": ["minimize COND_MEDIAN", "tie-break by COND_P90", "then COND_MAX"],
    "no_cutoff": {
        "arbitrary_condition_number_cutoff_introduced": False,
        "conditioning_is_a_utility_criterion_not_an_admissibility_rule": True,
        "statement": (
            "a candidate is not declared inadmissible solely because another "
            "candidate is better conditioned"),
    },
    "relation_to_search_rank_deficiency": {
        "search_rule": (
            "S7.7R used eigenvalues of the centred Gram with "
            "sqrt(min/max) <= max(n_prot, m+1)*eps to set J_search = +inf and "
            "label SEARCH_PROXY_RANK_DEFICIENT"),
        "s7_8_rule": "Rank-4 conditioning uses the SVD of Z directly",
        "conflict": False,
        "reading": (
            "these are different quantities serving different purposes: the "
            "search rule governs whether a navigation score is defined; the "
            "Rank-4 rule ranks admissible candidates by conditioning; neither "
            "was changed"),
    },
    "also_reported": ["COND_P90", "COND_MAX"],
    "execution_stage": "S7.9",
    **DOMAIN_BLOCK,
}

# ======================================================================
# 5. support stability
# ======================================================================
support_stability_policy = {
    "policy_id": "SUPPORT_STABILITY_POLICY_V1",
    "generated_utc": NOW,
    "parent_wording": "support stability: survives development-shot resampling and fold perturbation",
    "character": {
        "type": "ANALYST_DEFINED_QUALIFICATION_PROCEDURE",
        "required_label": "analyst-defined qualification procedure",
        "is_observational_uncertainty": False,
        "fabricated_error_weights": False,
        "note": (
            "E is not instantiated; this resampling describes selection "
            "stability, never measurement error"),
    },
    "modifies_ahat_rec": False,
    "reruns_search": False,
    "discharge_bootstrap": {
        "replicates": 1000,
        "unit": "development discharge",
        "n_per_replicate": 20,
        "with_replacement": True,
        "seed": 2026090501,
        "generator": "numpy.random.default_rng(2026090501)",
        "draw_order": "replicates drawn in sequence from a single generator stream; replicate r is the r-th draw",
        "resampled_object": "discharge indices only; the three blocks are never resampled",
        "weighting": (
            "a resampled discharge multiset is applied as integer multiplicities "
            "in every discharge-level aggregation (FIT, BLOCK_WORST, SHOT_P90 and "
            "the 60-cell conditioning summaries)"),
        "per_replicate_procedure": [
            "retain the same candidate frontier Ahat_rec",
            "recompute utility Ranks 1 to 4 using the resampled discharge indices",
            "identify the Rank-4 winner according to the frozen algorithm",
        ],
        "replicate_count_may_be_reduced_after_inspecting_outcomes": False,
    },
    "fold_perturbation": {
        "n_perturbations": 3,
        "perturbations": ["omit block A", "omit block B", "omit block C"],
        "per_perturbation_procedure": [
            "recompute utility Ranks 1 to 4 over the remaining two blocks",
            "do not alter the search",
            "do not alter support identities",
        ],
        "aggregation": {
            "NRMSE_s": "mean over the two remaining blocks",
            "BLOCK_WORST": "max over the two remaining blocks",
            "cells_per_perturbation": 40,
        },
    },
    "scores": {
        "evaluated_over": "the candidates surviving the original (unresampled) Ranks 1 to 4, i.e. E4",
        "BOOT_SELECTION_FREQ": "fraction of the 1000 bootstrap replicates in which C is the Rank-4 winner",
        "FOLD_SELECTION_FREQ": "fraction of the 3 block-omission perturbations in which C is the Rank-4 winner",
        "rank_4_winner_definition": (
            "the canonical-first element of E4 under that replicate or "
            "perturbation, i.e. the unique candidate the frozen Ranks 1 to 4 plus "
            "the canonical support-id tie-break resolve to"),
    },
    "rank_5_order": [
        "maximize BOOT_SELECTION_FREQ",
        "maximize FOLD_SELECTION_FREQ",
        "canonical support ID tie-break",
    ],
    "pass_fail_threshold": {
        "introduced": False,
        "statement": "support stability is a ranking/qualification quantity, not a gate",
    },
    "computation": {
        "guidance": (
            "vectorize over the frozen per-cell NRMSE arrays; Ranks 1 to 3 are "
            "pure functions of the 162845 x 60 NRMSE matrix and the registry "
            "support_size, so all 1000 replicates can be evaluated by weighted "
            "matrix reductions"),
        "conditioning_cost_control": (
            "per-cell kappa is independent of the discharge resample, so kappa "
            "may be computed lazily and memoized for the candidates that reach "
            "Rank 4 in any replicate; this is an efficiency measure and changes "
            "no defined quantity"),
        "determinism_requirement": "identical inputs must yield identical E5 across runs and machines",
    },
    "distinct_from_gate_inference_bootstrap": {
        "this_procedure": "1000 replicates, development-side Rank-5 support stability, S7.9",
        "gate_inference_procedure": "at least 10000 replicates, paired discharge bootstrap for confidence intervals on gate comparisons, S7.10",
        "source": "S7.2 STATISTICAL_INFERENCE_PLAN.md item 6; K_REC_PRE_V2 V_rec.bootstrap_replicates = 10000",
        "conflict": False,
        "reading": (
            "different procedures with different purposes and different stages; "
            "neither replaces the other and the parent count is not modified"),
    },
    "execution_stage": "S7.9",
    **DOMAIN_BLOCK,
}

# ======================================================================
# 6. deterministic S7.9 selection algorithm
# ======================================================================
development_selection_algorithm = {
    "algorithm_id": "DEVELOPMENT_SELECTION_ALGORITHM_V1",
    "generated_utc": NOW,
    "owner_stage": "S7.9",
    "executed_in_s7_8": False,
    "input": {
        "frontier": SELECTION_DOMAIN,
        "cardinality": 162845,
        "per_cell_nrmse": [
            "07_search_policy_and_frontier/one_seed_primary_v2/explored_per_cell_nrmse.npz",
            "07_search_policy_and_frontier/one_seed_primary_v2/atomic_per_cell_nrmse.npz",
        ],
        "registry": "07_search_policy_and_frontier/one_seed_primary_v2/explored_support_registry.csv",
    },
    "output": {
        "one_deterministic_development_selected_candidate": True,
        "full_survivor_sets_at_every_rank": True,
        "elimination_ledger": True,
    },
    "stages": [
        {"set": "E0", "content": "Ahat_rec", "size": 162845},
        {"set": "E1", "rank": 1, "criterion": "primary fit quality",
         "rule": "C in E1 iff |FIT(C) - FIT_best| <= max(SE_delta(C, best), 0.01)",
         "note": "practical-equivalence set, NOT a top-K truncation"},
        {"set": "E2", "rank": 2, "criterion": "development generalization / stability",
         "rule": "within E1: BLOCK_WORST practical-equivalence restriction, then exact argmin of SHOT_P90"},
        {"set": "E3", "rank": 3, "criterion": "parsimony",
         "rule": "within E2: exact argmin of |C|, then exact argmin of ACTIVE_TERMS(C)"},
        {"set": "E4", "rank": 4, "criterion": "conditioning",
         "rule": "within E3: exact argmin of COND_MEDIAN, then COND_P90, then COND_MAX"},
        {"set": "E5", "rank": 5, "criterion": "support stability",
         "rule": "within E4: max BOOT_SELECTION_FREQ, then max FOLD_SELECTION_FREQ, then canonical support ID"},
    ],
    "parsimony_definition": {
        "first": "|C|, the number of scientific coordinates, from registry support_size",
        "second": "ACTIVE_TERMS(C)",
        "active_terms": {
            "definition": "the number of explanatory columns whose OLS coefficient is not exactly zero under ordinary floating arithmetic",
            "magnitude_threshold": None,
            "significance_or_p_value_pruning": False,
            "intercept_counted": False,
            "aggregation_rule": {
                "OR-05": (
                    "a column is ACTIVE for C iff its coefficient is not exactly "
                    "0.0 in at least one of the 60 calibration fits; "
                    "ACTIVE_TERMS(C) is the count of active columns"),
                "rationale": (
                    "coefficients are discharge/block local, so the criterion "
                    "needs a candidate-level integer; the union rule is the "
                    "conservative reading (a term counts as used if it is used "
                    "anywhere) and requires no threshold"),
                "outcome_independent": True,
            },
            "expected_behaviour": (
                "under full-rank OLS an exactly-zero coefficient essentially "
                "never occurs, so ACTIVE_TERMS(C) = |C| and the second parsimony "
                "subcriterion is non-binding, exactly as the parent anticipates"),
        },
    },
    "canonical_tie_break": CANONICAL_ID["tie_break"],
    "elimination_ledger_schema": {
        "one_row_per_eliminated_candidate": True,
        "columns": [
            "support_id",
            "support_size",
            "rank_eliminated",
            "criterion",
            "reason",
            "comparison_quantity",
            "candidate_value",
            "reference_value",
            "threshold_applied",
        ],
        "surviving_candidates_recorded_separately_per_rank": True,
    },
    "determinism": {
        "sources_of_randomness": ["the Rank-5 discharge bootstrap only"],
        "seed": 2026090501,
        "all_other_steps": "deterministic given the frozen inputs",
        "reproducibility_requirement": "identical inputs must yield an identical selected candidate",
    },
    "preconditions_before_reusing_s7_7r_arrays": {
        "source": "S7.8 instruction section 8",
        "required_verifications": [
            "artifact hashes match the S7.7R recorded manifest",
            "estimator equivalence: DEVELOPMENT_RELATION_OLS_V1 == SEARCH_PROXY_OLS_V1 for the fit criterion",
            "metric equivalence: NRMSE definition, scale and ddof unchanged",
            "support identity: canonical support_id set matches Ahat_rec exactly",
            "block identity: the 60 cells match the frozen development cohort and block windows",
        ],
        "otherwise": "recompute from source",
        "s7_8_status": "all five verified in S7.8; S7.9 must re-verify at execution time",
    },
    "forbidden_in_execution": [
        "selecting a candidate before the ranks are computed in order",
        "introducing a tolerance not defined in this algorithm",
        "reordering the ranks",
        "pruning a constructor family",
        "penalizing ECE ancestry",
        "removing uncalibrated primitives",
    ],
    **DOMAIN_BLOCK,
}

# ======================================================================
# 7. U_rec operational
# ======================================================================
u_rec = {
    "utility_id": "U_REC_OPERATIONAL_V1",
    "generated_utc": NOW,
    "parent_contract": PARENT_CONTRACT,
    "parent_status": "U_rec FROZEN at S7.2; S7.8 instantiates execution rules only",
    "primary_search": PRIMARY_SEARCH,
    "structure": "lexicographic",
    "no_weighted_sum": True,
    "no_pareto_weight_tuning": True,
    "no_family_penalty": True,
    "no_scientific_family_bonus": True,
    "no_constructor_preference": True,
    "no_ece_penalty": True,
    "no_c6_c7_penalty": True,
    "no_diversity_bonus": True,
    "primary_estimator": "DEVELOPMENT_RELATION_OLS_V1",
    "primary_metric": PRIMARY_METRIC,
    "cell_geometry": CELL_GEOMETRY,
    "canonical_identity": CANONICAL_ID,
    "practical_equivalence": practical_equivalence["authoritative_rule"],
    "rank_1_fit": {
        "criterion": "primary fit quality",
        "quantity": "FIT(C) = mean_s NRMSE_s(C)",
        "best": "FIT_best = min_C FIT(C)",
        "survivor_set": "E_fit = { C : |FIT(C) - FIT_best| <= max(SE_delta(C,best), 0.01) }",
        "is_top_k": False,
        "no_candidate_outside_E_fit_advances": True,
        "policy_ref": "practical_equivalence_policy.json",
    },
    "rank_2_stability": {
        "criterion": "development generalization / stability",
        "quantities": ["BLOCK_WORST(C)", "SHOT_P90(C)"],
        "order": stability_metric_policy["rank_2_order"],
        "policy_ref": "stability_metric_policy.json",
    },
    "rank_3_parsimony": {
        "criterion": "parsimony",
        "quantities": ["|C|", "ACTIVE_TERMS(C)"],
        "order": ["minimize |C|", "then minimize ACTIVE_TERMS(C)"],
        "intercept_counted": False,
        "policy_ref": "development_selection_algorithm.json",
    },
    "rank_4_conditioning": {
        "criterion": "conditioning",
        "quantities": ["COND_MEDIAN(C)", "COND_P90(C)", "COND_MAX(C)"],
        "order": conditioning_policy["rank_4_order"],
        "policy_ref": "conditioning_policy.json",
    },
    "rank_5_support_stability": {
        "criterion": "support stability",
        "quantities": ["BOOT_SELECTION_FREQ(C)", "FOLD_SELECTION_FREQ(C)"],
        "order": support_stability_policy["rank_5_order"],
        "policy_ref": "support_stability_policy.json",
    },
    "canonical_tie_break": CANONICAL_ID["tie_break"],
    "fabricated_error_weights": False,
    "measurement_error_weights": False,
    "execution_stage": "S7.9",
    "s7_8_selected_a_candidate": False,
    **DOMAIN_BLOCK,
}

# ======================================================================
# 8. gate stage ownership + V_rec operational
# ======================================================================
GATES = [
    {
        "gate": "V1",
        "name": "information boundary",
        "authoritative_definition": "no target leakage; no admitted quantity with unresolved target ancestry in the primary boundary",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "S7.3 established the boundary; final gate table at S7.12",
        "current_status": "PROTOCOL_VERIFIED",
        "status_detail": "auditable now from lineage; the final gate table is produced downstream",
        "evidence_required": "S7.3 information-boundary artifacts and the leakage matrix, carried unchanged",
        "failure_meaning": "MANDATORY: a failure prevents presenting Q_rec as a successful structural-transfer result",
    },
    {
        "gate": "V2",
        "name": "development-only discovery",
        "authoritative_definition": "target, ontology, support, estimator and thresholds chosen without external outcomes",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "S7.9 freeze",
        "current_status": "PENDING_S7.9",
        "status_detail": "auditable now and provisionally satisfied; it remains provisional until the S7.9 freeze fixes the support and estimator",
        "evidence_required": "access audits showing zero external signal and target values through S7.9, plus the S7.9 hash record",
        "failure_meaning": "MANDATORY: a failure prevents the structural-transfer claim",
    },
    {
        "gate": "V3",
        "name": "nontrivial skill vs B0/B1",
        "authoritative_definition": "Delta_j = mean over EXTERNAL discharges of (NRMSE_REL,s - NRMSE_Bj,s), with NRMSE_,s = mean over blocks A,B,C; PASS iff Delta_0 <= -0.01 AND Delta_1 <= -0.01",
        "mandatory": True,
        "authoritative_corrections": ["S7.2C C-06 supplied the missing aggregate definition; the V1 wording 'predeclared aggregate sense' was not decidable"],
        "stage_owner": "S7.10",
        "current_status": "PENDING_S7.10",
        "status_detail": "NOT evaluated in S7.8; requires the external cohort",
        "evidence_required": "external protected scoring of the frozen representation and of B0 and B1 on identical samples",
        "failure_meaning": "MANDATORY: this is the gate the retired q_rec failed",
    },
    {
        "gate": "V4",
        "name": "fair raw comparison vs B2/B3",
        "authoritative_definition": "fair comparison against B2 and B3 on identical information and geometry",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "S7.10",
        "current_status": "PENDING_S7.10",
        "status_detail": "NOT evaluated in S7.8",
        "evidence_required": "identical calibration intervals, identical protected samples, identical estimator discipline for B2 and B3",
        "failure_meaning": "MANDATORY, but requires FAIRNESS not victory: the gate passes if the comparison was conducted properly, whatever the outcome",
    },
    {
        "gate": "V5",
        "name": "external structural transfer",
        "authoritative_definition": "support frozen and hashed before any external evaluation",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "S7.10, conditioned on the S7.9 freeze",
        "current_status": "PENDING_S7.10",
        "status_detail": "NOT evaluated until S7.10; the precondition is created by the S7.9 hash",
        "evidence_required": "the S7.9 freeze hash predating the first external access timestamp",
        "failure_meaning": "MANDATORY: without it the local-calibration design makes the claim vacuous",
    },
    {
        "gate": "V6",
        "name": "processing-era robustness",
        "authoritative_definition": "external results reported separately for the 24 earlier and 18 later external discharges; outcomes PASS / PASS_WITH_QUALIFICATION / FAIL_FOR_FULL_DOMAIN",
        "mandatory": True,
        "authoritative_corrections": [
            "S7.2C C-07: external counts are 24 earlier / 18 later",
            "the V1 wording 35 earlier / 27 later is SUPERSEDED_FOR_V6_BY_S7.2C_C07; those are PARENT OBJECT counts, not the external cohort the gate operates on",
        ],
        "stage_owner": "S7.10",
        "current_status": "PENDING_S7.10",
        "status_detail": "NOT evaluated in S7.8",
        "evidence_required": "era-split external results using 24/18",
        "failure_meaning": "MANDATORY; FAIL_FOR_FULL_DOMAIN does not erase the result but narrows Omega_rec rather than averaging across the processing discontinuity",
    },
    {
        "gate": "V7",
        "name": "common support",
        "authoritative_definition": "cross-representation comparisons use identical scored samples",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "protocol check S7.8; empirical comparison S7.10",
        "current_status": "PROTOCOL_VERIFIED",
        "status_detail": "the protocol requirement is verified now; the empirical common-support check belongs with the comparison",
        "evidence_required": "identical protected sample sets across the representation and all four baselines",
        "failure_meaning": "MANDATORY: unequal scored samples invalidate every paired comparison",
    },
    {
        "gate": "V8",
        "name": "discharge-level inference",
        "authoritative_definition": "discharge, not time sample, is the independent unit",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "protocol frozen S7.8; evaluated downstream",
        "current_status": "PROTOCOL_VERIFIED",
        "status_detail": "every S7.8 quantity aggregates to the discharge before any standard error is taken; SE_delta uses n = 20 discharges",
        "evidence_required": "paired discharge-level differences and discharge bootstrap in all inference",
        "failure_meaning": "MANDATORY: sample-level inference would overstate precision by orders of magnitude",
    },
    {
        "gate": "V9",
        "name": "sensitivity",
        "authoritative_definition": "no result depends catastrophically on one discharge, one temporal block, or one numerical realization",
        "mandatory": False,
        "authoritative_corrections": [],
        "stage_owner": "S7.11",
        "current_status": "PENDING_S7.11",
        "status_detail": "NON-MANDATORY; a single influential discharge is a finding to report rather than a disqualification, provided it is reported",
        "evidence_required": "leave-one-discharge-out, block, and numerical-realization sensitivity",
        "failure_meaning": "NON-MANDATORY: reported, does not block the claim",
    },
    {
        "gate": "V10",
        "name": "numerical provenance",
        "authoritative_definition": "no claim rests on interpolation-created resolution without qualification",
        "mandatory": True,
        "authoritative_corrections": [],
        "stage_owner": "lineage auditable S7.8; final qualification downstream",
        "current_status": "PROTOCOL_VERIFIED",
        "status_detail": "S7.3R source-resolution reconciliation is carried unchanged; the final qualification statement belongs with the result",
        "evidence_required": "the S7.3R/S7.4 V2 source-cadence and numerical-admissibility record",
        "failure_meaning": "MANDATORY: a claim resting on interpolated resolution must be qualified or withdrawn",
    },
]

gate_stage_ownership = {
    "policy_id": "GATE_STAGE_OWNERSHIP_V1",
    "generated_utc": NOW,
    "allowed_states_at_s7_8": [
        "PROTOCOL_VERIFIED",
        "PENDING_S7.9",
        "PENDING_S7.10",
        "PENDING_S7.11",
    ],
    "forbidden_states_at_s7_8": ["PASS", "PASS_WITH_QUALIFICATION", "FAIL", "NOT_APPLICABLE"],
    "no_external_gate_marked_pass": True,
    "final_gate_resolution_states": ["PASS", "PASS_WITH_QUALIFICATION", "FAIL", "NOT_APPLICABLE"],
    "stage_division_preserved_from_s7_2": {
        "S7.9": "instantiated utility computation on development",
        "S7.10": "qualification-gate evaluation",
        "S7.11": "sensitivity",
        "S7.12": "Q_rec*",
    },
    "s7_9_not_moved_into_s7_8": True,
    "gates": [
        {k: g[k] for k in ("gate", "name", "mandatory", "stage_owner", "current_status")}
        for g in GATES
    ],
    "evaluable_before_s7_10": ["V1", "V2", "V7", "V8", "V10"],
    "not_evaluable_before_s7_10": ["V3", "V4", "V5", "V6"],
    "not_evaluable_before_s7_11": ["V9"],
    "reason_not_evaluable": "these gates require the sealed external cohort or executed baselines, neither of which S7.8 may open or run",
}

v_rec = {
    "qualification_id": "V_REC_OPERATIONAL_V1",
    "generated_utc": NOW,
    "parent_contract": PARENT_CONTRACT,
    "parent_status": "V_rec protocol FROZEN at S7.2; gate evaluation DEFERRED_TO_S7.10",
    "mandatory_gates": ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V10"],
    "non_mandatory_gates": ["V9"],
    "mandatory_failure_meaning": (
        "if a mandatory gate fails, Q_rec may NOT be presented as a successful "
        "structural-transfer result"),
    "gates": GATES,
    "baselines": {
        "B0": {"definition": "calibration mean predicted throughout the protected block", "status": "NOT_RUN", "owner": "S7.9 configuration, S7.10 execution"},
        "B1": {"definition": "persistence: last calibration sample of the block held constant", "status": "NOT_RUN", "owner": "S7.9 configuration, S7.10 execution"},
        "B1A_AR1": {"definition": "AR(1) diagnostic baseline", "status": "NOT_RUN", "role": "DIAGNOSTIC", "owner": "S7.9 configuration, S7.10 execution"},
        "B2": {"definition": "raw ridge linear regression on target-admissible primitive predictors", "status": "NOT_RUN", "owner": "S7.9 configuration, S7.10 execution"},
        "B3": {"definition": "sklearn.ensemble.HistGradientBoostingRegressor on the same raw predictors", "status": "NOT_RUN", "owner": "S7.9 configuration, S7.10 execution"},
        "H0_RAW_HARDENED": {"definition": "hardened raw diagnostic", "status": "NOT_RUN", "role": "DIAGNOSTIC", "owner": "S7.9 configuration, S7.10 execution"},
    },
    "baseline_notes": {
        "V3_requires": "actual skill versus B0 and B1",
        "V4_requires": "FAIR comparison with B2 and B3; V4 does NOT require beating B2/B3",
        "S_pers": "remains required reporting but does NOT guide S7.9 selection",
        "identical_geometry_granted_to_every_comparator": True,
    },
    "inferential_unit": "discharge",
    "gate_inference_bootstrap_replicates": 10000,
    "validation_geometry": CELL_GEOMETRY,
    "external_cohort": {
        "n": 42,
        "earlier": 24,
        "later": 18,
        "state": "SEALED",
        "values_opened_in_s7_8": 0,
    },
    "execution_stage": "S7.10 (V9: S7.11)",
    **DOMAIN_BLOCK,
}


def main() -> int:
    write("practical_equivalence_policy.json", practical_equivalence)
    write("estimator_policy.json", estimator_policy)
    write("stability_metric_policy.json", stability_metric_policy)
    write("conditioning_policy.json", conditioning_policy)
    write("support_stability_policy.json", support_stability_policy)
    write("development_selection_algorithm.json", development_selection_algorithm)
    write("U_REC_OPERATIONAL_V1.json", u_rec)
    write("V_REC_OPERATIONAL_V1.json", v_rec)
    write("gate_stage_ownership.json", gate_stage_ownership)

    # ---- manifests ------------------------------------------------------
    write("manifests/ACCESS_AUDIT.json", {
        "audit_id": "S7_8_ACCESS_AUDIT_V1",
        "generated_utc": NOW,
        "external_signal_values_opened": 0,
        "external_target_values_opened": 0,
        "external_cohort_state": "SEALED",
        "baselines_run": 0,
        "search_rerun": False,
        "ahat_rec_modified": False,
        "a_rec_modified": False,
        "g_rec_modified": False,
        "two_seed_sensitivity_executed": False,
        "c_star_selected": False,
        "final_support_frozen": False,
        "s7_9_started": False,
        "development_values_read": {
            "utility_computed_over_ahat_rec": False,
            "note": (
                "S7.8 read the frozen per-cell NRMSE arrays only for SHAPE, "
                "FINITENESS and IDENTITY verification; no FIT, BLOCK_WORST, "
                "SHOT_P90, conditioning or stability quantity was computed over "
                "Ahat_rec, and no ranking was performed"),
        },
        "verdict": "FIREWALL_INTACT",
    })

    write("manifests/S7_9_REUSE_PRECONDITIONS.json", {
        "manifest_id": "S7_9_ARRAY_REUSE_PRECONDITIONS_V1",
        "generated_utc": NOW,
        "source": "S7.8 instruction section 8",
        "rule": (
            "S7.9 may reuse the S7.7R per-cell NRMSE arrays ONLY after verifying "
            "all five preconditions; otherwise it must recompute"),
        "preconditions": development_selection_algorithm[
            "preconditions_before_reusing_s7_7r_arrays"]["required_verifications"],
        "s7_8_verification": {
            "hashes": "41/41 S7.7R artifacts reproduce byte-for-byte",
            "estimator_equivalence": "SEARCH_PROXY_OLS_V1 is algebraically identical to DEVELOPMENT_RELATION_OLS_V1 for the fit criterion; S7.7R measured max relative deviation 1.72e-13 against numpy.linalg.lstsq",
            "metric_equivalence": "NRMSE definition, calibration scale and ddof=0 unchanged from S7.2C",
            "support_identity": "162845 unique canonical support_ids, sizes 1..12, matching the S7.7R histogram exactly",
            "block_identity": "60 cells over the 20 frozen development discharges and blocks A/B/C",
        },
        "s7_9_must_re_verify_at_execution_time": True,
        "semantic_caveat": (
            "reuse is a NUMERICAL convenience only; J_search remains a "
            "navigation score and FIT remains a utility criterion, even where "
            "the numbers coincide"),
    })

    write("manifests/SEMANTIC_SEPARATION.json", {
        "manifest_id": "NAVIGATION_VERSUS_UTILITY_V1",
        "generated_utc": NOW,
        "s7_7_answered": "Where did the frozen search look?",
        "s7_8_answers": "By what exact scientific rule will we judge what it found?",
        "s7_8_does_not_answer": "Which representation wins? (that is S7.9)",
        "invariants": [
            "SEARCH FREQUENCY != SCIENTIFIC IMPORTANCE",
            "SEARCH PRIORITY != VALIDATION",
            "PRACTICAL EQUIVALENCE != NUMERICAL IDENTITY",
            "SELECTED WITHIN Ahat_rec != GLOBALLY OPTIMAL",
        ],
        "numerical_coincidence_note": (
            "FIT(C) may equal J_search(C) numerically because both are the mean "
            "over the 60 cells of the same OLS NRMSE; this is an identity of "
            "arithmetic, not of scientific role"),
        **DOMAIN_BLOCK,
    })

    write("manifests/CARRY_FORWARD_FINDINGS.json", {
        "manifest_id": "S7_8_CARRY_FORWARD_V1",
        "generated_utc": NOW,
        "acted_on_in_s7_8": False,
        "c6_c7": {
            "finding": "C6 + C7 supplied 56.38 percent of admissible atoms (C6 35.03, C7 21.35) and had substantial seed opportunity (C6 27.6 percent, C7 15.7 percent of seeds)",
            "admissible_atoms": {"C6": 3776, "C7": 2301},
            "explored_participation_share": {"C6": 0.5108723018821579, "C7": 0.3684116798182321},
            "retained_participation": {"C6": 0.046296296296296294, "C7": 0.026455026455026454},
            "lowest_J_support_participation": "neither appears in the lowest-J support at any size 1..12",
            "declaration": "NO_CONSTRUCTOR_FAMILY_PRUNING",
            "c6_c7_removed_from_ahat_rec": False,
            "if_utility_eliminates_them": "report that later; it is an outcome, not a rule",
            "if_a_c6_c7_candidate_survives": "accept it",
            "reason": "this is exactly why navigation and utility are separate",
        },
        "ece_dominance": {
            "seed_opportunity_share": 0.30708661417322836,
            "atom_ancestry_share": 0.841992948598998,
            "retained_path_share": 0.8544973544973545,
            "lowest_navigation_support_share": 1.0,
            "opportunity_was_balanced": True,
            "penalty_introduced": False,
            "family_quota_introduced": False,
            "diversity_bonus_introduced": False,
            "family_balancing_in_u_rec": False,
            "reading": "the search opportunity correction has already done its job; utility now evaluates the found representations as they are",
        },
        "uncalibrated_primitives": {
            "signals": ["pcbcoil", "pcdiamag3"],
            "provenance": "S7.1 records both as uncalibrated digitiser output for which no unit exists",
            "status_in_ahat_rec": "VALID if already present; NOT REMOVED",
            "carried_label": "UNCALIBRATED_SIGNAL",
            "consequence": "if a selected representation contains one, its fitted coefficient has no certified physical-dimensional interpretation",
            "is_selection_exclusion": False,
            "is_interpretation_qualification": True,
        },
        "search_depth_sensitivity": {
            "id": "TWO_SEED_SEARCH_DEPTH_SENSITIVITY",
            "status": ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
            "executed_in_s7_8": False,
            "outcome_trigger_defined": False,
            "may_be_executed_later_as": "a separately labelled S7.11 sensitivity, regardless of whether the primary result is good or bad",
            "may_replace_the_one_seed_primary_frontier": False,
        },
        "search_boundary": {
            "selection_domain": SELECTION_DOMAIN,
            "global_optimality_claim": False,
            "explored_fraction_of_size_1_12_space": "3.19e-33 percent",
            "unsearched_admissible_combinations": "approximately 5.1e39",
            "unsearched_status": "ADMISSIBLE_UNSEARCHED",
            "negative_conclusion_attached_to_unsearched": False,
            "final_candidate_means": "selected from the frozen explored frontier",
            "final_candidate_does_not_mean": "best representation in A_rec",
        },
    })

    write("manifests/OUTCOME_BASED_REVISION_AUDIT.json", {
        "manifest_id": "NO_OUTCOME_BASED_UTILITY_REVISION_V1",
        "generated_utc": NOW,
        "forbidden_and_not_done": {
            "changed_the_0.01_floor": False,
            "changed_stability_quantiles_after_seeing_candidate_behaviour": False,
            "changed_the_bootstrap_count_after_seeing_stability": False,
            "added_a_c6_c7_penalty": False,
            "added_an_ece_penalty": False,
            "added_a_family_diversity_term": False,
            "changed_support_size_preferences": False,
            "changed_condition_number_rules_to_favour_a_candidate": False,
            "chose_ridge_because_a_support_performs_better_with_ridge": False,
            "deleted_pcdiamag3_because_its_coefficient_is_hard_to_interpret": False,
            "changed_the_utility_ordering": False,
        },
        "precondition_for_all_of_the_above": (
            "no candidate-level utility quantity was computed over Ahat_rec in "
            "S7.8, so no outcome was available to revise against"),
        "conflict_procedure": (
            "if an inherited rule had been mathematically impossible to execute, "
            "S7.8 would STOP with UTILITY_SPECIFICATION_CONFLICT rather than "
            "repair it using observed outcomes"),
        "conflicts_found": 0,
        "verdict": "NO_OUTCOME_BASED_REVISION",
    })

    print("environment:", sys.version.split()[0], platform.platform())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
