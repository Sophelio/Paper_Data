"""S7.7 stage B - search strata, pre-value search policy, budget preflight.

METADATA ONLY. THIS SCRIPT OPENS NO ARCHIVE AND READS NO SIGNAL OR TARGET VALUE.

Order matters and is structural, not a matter of discipline:

  1. every one of the 10,778 admissible atoms is assigned to exactly one search
     stratum from frozen metadata;
  2. the complete search policy of sections 5-15 is written and hashed;
  3. the deterministic search-budget projection of section 16 is evaluated.

Only if step 3 passes may a later stage open a density value. If the projection
exceeds MAX_SUPPORT_EVALUATIONS this script stops here and reports
SEARCH_BUDGET_REQUIRES_HUMAN_REVIEW. It never truncates, and it never adjusts
the policy to fit the budget.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
S77 = HERE.parent
S7 = S77.parent
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
MAN = S77 / "manifests"

# ---- frozen policy constants (sections 12, 13, 14, 16) --------------------
MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION = 96
SEEDS_PER_STRATUM = 2
SUPPORT_MIN, SUPPORT_MAX = 1, 12
MAX_SUPPORT_EVALUATIONS = 300000

FAMILY_CODE = {
    "ece_te_profile": "ECE", "cer_rotation_ti": "CER", "neutral_beams": "NBI",
    "gas_injection": "GAS", "magnetics": "MAG", "filterscope_dalpha": "FS",
    "density": "DEN"}
UNARY = ("C0", "C1", "C5")
ACTIVE_CONSTRUCTORS = ["C0", "C1", "C2", "C3", "C5", "C6", "C7"]
ZERO_ATOM_CONSTRUCTORS = ["C4", "C8"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def signature(constructor: str, ops: list[str], fam: dict) -> tuple[str, str]:
    """Return (signature, role_semantics). Exactly one stratum per atom."""
    f = [FAMILY_CODE[fam[o]] for o in ops]
    if constructor in UNARY:
        return f[0], "(family_i)"
    if constructor == "C2":
        return "{%s}" % ",".join(sorted(f)), "unordered {family_i, family_j}"
    if constructor == "C3":
        return f"{f[0]}|{f[1]}", "(numerator_family | denominator_family)"
    if constructor == "C6":
        return f"{f[0]}|{f[1]}", "(level_family | rate_family)"
    if constructor == "C7":
        return f"{f[0]}|{f[1]}", "(rate_family | denominator_level_family)"
    raise SystemExit(f"STOP: no stratum rule for {constructor}")


def main() -> None:
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: run stage A first")
    pre = json.loads((MAN / "PRE_SEARCH_CONTRACT_FREEZE.json").read_text())

    ATOM = pd.read_csv(S76R / "primary_atomic_coordinate_universe.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv")
    fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))
    assert len(ATOM) == 10778

    # ---- 6. search strata, metadata only ---------------------------------
    sig, sem = [], []
    for c, ops in zip(ATOM.constructor, ATOM.ordered_operands):
        s, r = signature(c, str(ops).split("|"), fam)
        sig.append(s)
        sem.append(r)
    ATOM = ATOM.assign(family_signature=sig, role_semantics=sem)
    ATOM["search_stratum"] = ATOM.constructor + ":" + ATOM.family_signature
    assert ATOM.search_stratum.notna().all()
    assert ATOM.coordinate_id.is_unique

    ATOM[["coordinate_id", "constructor", "ordered_operands", "operand_roles",
          "family_signature", "role_semantics", "search_stratum"]].to_csv(
        S77 / "atom_stratum_assignment.csv", index=False)

    grp = ATOM.groupby("search_stratum")
    strata = grp.agg(constructor=("constructor", "first"),
                     family_signature=("family_signature", "first"),
                     role_semantics=("role_semantics", "first"),
                     n_atoms=("coordinate_id", "size")).reset_index()
    strata["seeds_projected"] = strata.n_atoms.clip(upper=SEEDS_PER_STRATUM)
    strata = strata.sort_values(["constructor", "family_signature"]).reset_index(
        drop=True)

    n_strata = int(len(strata))
    per_constructor = {c: int((strata.constructor == c).sum())
                       for c in ACTIVE_CONSTRUCTORS}
    atoms_per_constructor = {c: int((ATOM.constructor == c).sum())
                             for c in ACTIVE_CONSTRUCTORS}
    shortlist_size = {c: min(atoms_per_constructor[c],
                             MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION)
                      for c in ACTIVE_CONSTRUCTORS}
    n_seeds_main = int(strata.seeds_projected.sum())

    # section 13 gate: 96 must give at least one slot to every stratum
    insufficient = {c: per_constructor[c] for c in ACTIVE_CONSTRUCTORS
                    if per_constructor[c] > shortlist_size[c]}

    # round 1 of the round-robin gives every stratum one slot, so every stratum
    # of every constructor is represented in the shortlist
    strata_in_shortlist = n_strata if not insufficient else None

    # ---- 15. raw-only control lane, metadata projection -------------------
    c0 = strata[strata.constructor == "C0"]
    n_seeds_raw = int(c0.n_atoms.clip(upper=SEEDS_PER_STRATUM).sum())
    n_strata_raw = int(len(c0))

    # ---- 16. deterministic budget projection ------------------------------
    steps = SUPPORT_MAX - 1                     # m = 2..12
    main_max = n_seeds_main * steps * strata_in_shortlist
    # strict lower bound: at proposal time for size m the support holds m-1
    # atoms, so at most m-1 strata can already be exhausted
    main_min = n_seeds_main * sum(strata_in_shortlist - (m - 1)
                                  for m in range(2, SUPPORT_MAX + 1))
    raw_max = n_seeds_raw * steps * n_strata_raw
    raw_min = n_seeds_raw * sum(max(0, n_strata_raw - (m - 1))
                                for m in range(2, SUPPORT_MAX + 1))
    atomic = int(len(ATOM))

    proj_max = atomic + main_max + raw_max
    proj_min = atomic + main_min + raw_min
    within = proj_max <= MAX_SUPPORT_EVALUATIONS
    within_even_at_minimum = proj_min <= MAX_SUPPORT_EVALUATIONS

    strata.to_csv(S77 / "search_strata.csv", index=False)

    # ---- 9. pre-value search policy ---------------------------------------
    policy = {
        "policy_id": "SIGMA_REC_PREVALUE_V1",
        "status": "FROZEN_BEFORE_ANY_DENSITY_VALUE",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "stage_b_opens_no_archive": True,
        "parent_universe": "A_REC_DENSITY_HARDENED_V2",
        "parent_ontology": "G_REC_DENSITY_HARDENED_V2",
        "pre_search_contract_sha256": pre["sha256"],

        "s5_multiplicity_problem": {
            "ece_share_of_P_hard": 0.471,
            "ece_ancestry_share_of_admissible_atoms": 0.842,
            "is_an_admissibility_defect": False,
            "coordinates_deleted": 0, "P_hard_altered": False,
            "must_prevent": "atom count -> automatic search priority",
            "principle": "ADMISSIBLE != PRIORITIZED",
            "balance_by": ["constructor_family",
                           "scientific_ancestor_family_signature"]},

        "s6_search_strata": {
            "definition": "search_stratum(c) = (constructor_family, "
                          "scientific_family_signature)",
            "signatures": {
                "C0": "(family_i)", "C1": "(family_i)", "C5": "(family_i)",
                "C2": "unordered sorted pair {family_i, family_j}",
                "C3": "(numerator_family | denominator_family)",
                "C6": "(level_family | rate_family)",
                "C7": "(rate_family | denominator_level_family)"},
            "C4_C8": "no admissible atoms, therefore no active strata",
            "exactly_one_stratum_per_atom": True,
            "multiple_counting_memberships": False,
            "assigned_from_metadata_only": True,
            "n_active_strata": n_strata,
            "strata_per_constructor": per_constructor},

        "s7_search_proxy": {
            "id": "SEARCH_PROXY_OLS_V1",
            "is_final_estimator": False, "is_validation": False,
            "procedure": [
                "calibration values only for predictor mean/std",
                "standardize each coordinate with those calibration statistics",
                "apply unchanged to protected predictor values",
                "fit affine OLS y_cal = beta_0 + X_C,cal beta",
                "score protected target with frozen NRMSE = "
                "RMSE_protected / std(y_cal, ddof=0)"],
            "solver": "numpy.linalg.lstsq(..., rcond=None)",
            "joint_fit_across_discharges": False,
            "coefficients": "discharge/block local",
            "rank_deficient_handling": {
                "flag": "SEARCH_PROXY_RANK_DEFICIENT",
                "navigation_score": "+infinity",
                "declares_support_scientifically_inadmissible": False,
                "note": "that distinction belongs to later qualification"}},

        "s8_navigation_score": {
            "definition": "J_search(C) = mean over 20 development discharges of "
                          "NRMSE_s(C), where NRMSE_s(C) = mean_b NRMSE_{s,b}(C) "
                          "over blocks A, B, C",
            "lower_is_better": True,
            "is_U_rec": False, "is_validation_evidence": False,
            "is_final_qualification": False,
            "terms_explicitly_excluded": ["parsimony", "conditioning",
                                          "scientific-family bonus",
                                          "baseline skill", "persistence skill"],
            "support_size_control": "already handled by search depth",
            "tie_break": "canonical support ID, lexicographic"},

        "s10_atomic_scoring": {
            "scope": "ALL admissible atoms as one-coordinate supports",
            "n_expected": atomic,
            "cohort": "20 development discharges only",
            "external_sealed": True,
            "poor_performance_causes_inadmissibility": False},

        "s11_within_stratum_ranking": {
            "sort_key": ["lower J_search", "canonical coordinate ID"],
            "global_top_K_pruning": False,
            "rationale": "prevents large diagnostic families from receiving "
                         "more initial search opportunities merely because "
                         "they contain more atoms"},

        "s12_shortlist": {
            "MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION":
                MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION,
            "method": "per constructor, round-robin over its nonempty "
                      "scientific-family strata; round r takes the r-th best "
                      "atom of every stratum",
            "constructors": ACTIVE_CONSTRUCTORS,
            "retain_all_if_at_or_below_cap": True,
            "projected_shortlist_size": shortlist_size,
            "not_shortlisted_label": "ADMISSIBLE_NOT_IN_EXPANSION_SHORTLIST",
            "not_shortlisted_is_not": "INADMISSIBLE"},

        "s13_budget_interpretation": {
            "96_is": "a computational search allowance",
            "96_is_not": "a scientific threshold",
            "claim_about_rank_97": "none; no claim that rank 97 is "
                                   "scientifically inferior",
            "changing_after_outcomes_seen": "FORBIDDEN",
            "stop_condition": "if 96 cannot give at least one slot to every "
                              "nonempty stratum of a constructor, STOP before "
                              "target access",
            "stop_condition_triggered": bool(insufficient),
            "insufficient_constructors": insufficient},

        "s14_greedy_search": {
            "seeds": "top 2 atoms by within-stratum rank per active stratum "
                     "(or the single atom if only one exists)",
            "n_seeds_projected": n_seeds_main,
            "growth_sizes": "m = 2..12",
            "proposal_rule": "at each step, EVERY active stratum represented in "
                             "the expansion shortlist proposes exactly one atom: "
                             "its highest within-stratum-ranked shortlisted atom "
                             "not already in the support",
            "no_proposal_if_stratum_exhausted": True,
            "extension_filter": "discard only extensions violating frozen Phi_set",
            "selection": "lowest J_search; tie-break canonical support ID",
            "terminate": "|C| = 12 or no valid extension",
            "opportunity_set": "stratum-balanced",
            "expansion_choice": "performance-guided"},

        "s15_raw_only_lane": {
            "lane_id": "C0_ONLY_GREEDY",
            "atoms": "the 66 admissible C0 atoms only",
            "strata": "the broad scientific families represented among C0",
            "n_strata": n_strata_raw,
            "seeds": "top two C0 atoms per nonempty scientific family",
            "n_seeds_projected": n_seeds_raw,
            "growth": "same greedy rule, one highest-ranked unused C0 atom "
                      "offered per scientific-family stratum per step",
            "support_max": SUPPORT_MAX,
            "purpose": "guarantee the explored frontier contains compact "
                       "raw-only representations",
            "is_B2": False,
            "B2_remains": "the frozen full-information raw Ridge comparator"},

        "s17_explored_definition": {
            "in_Ahat_rec_iff": "its search proxy was actually evaluated",
            "includes": ["all one-coordinate supports",
                         "every candidate multivariate extension actually scored",
                         "every retained greedy path support"],
            "PROPOSED_BUT_SET_INADMISSIBLE": "outside Ahat_rec because already "
                                             "outside A_rec",
            "ADMISSIBLE_UNSEARCHED": "admissible support never proposed",
            "invariant": "NOT SEARCHED != INADMISSIBLE"},

        "s19_no_selection": {
            "returns_C_star": False, "returns_R_star": False,
            "returns_Q_rec_star": False,
            "lowest_J_search_may_be_called":
                "lowest-navigation-score support in the explored frontier",
            "may_not_be_called": "best scientific representation"},

        "s20_no_baselines": {
            "B0": False, "B1": False, "B1A_AR1": False, "B2": False,
            "B3": False, "H0_RAW_HARDENED": False,
            "persistence_skill_used_for_search": False,
            "relational_vs_baseline_comparison": False},

        "s21_external": {"external_signal_values": 0, "external_target_values": 0,
                         "on_any_read": "FIREWALL_BREACH, STOP"},

        "unchanged_from_parents": {
            "A_rec": True, "G_rec": True, "target": True, "P_hard": True,
            "constructor_catalogue_C0_C8": True, "denominator_rule": True,
            "support_bound_1_12": True, "T_REC_V1": True, "Phi_set": True},
        "forbidden": ["rescue C4", "rescue C8", "shifted phase derivative",
                      "bounded phase derivative", "q_desc coordinate seeding",
                      "retired q_rec support seeding", "external information",
                      "final representation selection", "validation claim"],
    }
    pol = S77 / "SEARCH_POLICY_PREVALUE.json"
    pol.write_text(json.dumps(policy, indent=2), encoding="utf-8")
    pol_sha = sha(pol)

    # ---- 16. preflight verdict --------------------------------------------
    preflight = {
        "record_id": "SEARCH_BUDGET_PREFLIGHT_V1",
        "computed_from": "METADATA_ONLY",
        "no_density_value_opened": True,
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
        "search_policy_sha256": pol_sha,
        "MAX_SUPPORT_EVALUATIONS": MAX_SUPPORT_EVALUATIONS,

        "active_stratum_count": n_strata,
        "strata_per_constructor": per_constructor,
        "atoms_per_constructor": atoms_per_constructor,
        "expansion_shortlist_count": shortlist_size,
        "expansion_shortlist_total": int(sum(shortlist_size.values())),
        "strata_represented_in_shortlist": strata_in_shortlist,
        "every_nonempty_stratum_gets_a_slot": not insufficient,

        "main_lane": {"n_seeds": n_seeds_main, "growth_steps": steps,
                      "proposals_per_step_max": strata_in_shortlist,
                      "evaluations_max": main_max,
                      "evaluations_strict_lower_bound": main_min},
        "raw_only_lane": {"n_seeds": n_seeds_raw, "growth_steps": steps,
                          "proposals_per_step_max": n_strata_raw,
                          "evaluations_max": raw_max,
                          "evaluations_strict_lower_bound": raw_min},
        "atomic_scoring_evaluations": atomic,

        "max_projected_support_evaluations": proj_max,
        "strict_lower_bound_support_evaluations": proj_min,
        "within_budget_at_maximum": within,
        "within_budget_even_at_strict_minimum": within_even_at_minimum,
        "overrun_at_maximum": max(0, proj_max - MAX_SUPPORT_EVALUATIONS),
        "overrun_at_strict_minimum": max(0, proj_min - MAX_SUPPORT_EVALUATIONS),

        "verdict": ("SEARCH_BUDGET_OK" if within
                    else "SEARCH_BUDGET_REQUIRES_HUMAN_REVIEW"),
        "policy_truncated_to_fit": False,
        "policy_changed_to_fit": False,
        "target_values_opened": 0,
    }
    (MAN / "SEARCH_BUDGET_PREFLIGHT.json").write_text(
        json.dumps(preflight, indent=2), encoding="utf-8")
    (MAN / "POLICY_FREEZE.json").write_text(json.dumps({
        "file": "SEARCH_POLICY_PREVALUE.json", "sha256": pol_sha,
        "frozen_utc": policy["frozen_utc"],
        "frozen_before_any_density_value_opened": True,
        "stage_a_and_b_open_no_archive": True,
        "ordering_is_structural": "stages A and B contain no data-loading code "
                                  "path at all; the later scoring stage verifies "
                                  "this hash before opening anything",
        "contamination_check": "SEARCH_POLICY_CONTAMINATED if the hash changes "
                               "after any density value is opened"}, indent=2),
        encoding="utf-8")

    print(f"active strata            : {n_strata}   {per_constructor}")
    print(f"shortlist per constructor: {shortlist_size} "
          f"(total {sum(shortlist_size.values())})")
    print(f"every stratum gets a slot: {not insufficient}")
    print(f"seeds  main {n_seeds_main}   raw-only {n_seeds_raw} "
          f"({n_strata_raw} C0 strata)")
    print(f"projected evaluations    : atomic {atomic} + main {main_max} + "
          f"raw {raw_max} = {proj_max}")
    print(f"strict lower bound       : {proj_min}")
    print(f"budget                   : {MAX_SUPPORT_EVALUATIONS}")
    print(f"policy sha {pol_sha[:16]}")
    print(f"VERDICT: {preflight['verdict']}")
    if not within:
        print(f"  overrun at maximum        {preflight['overrun_at_maximum']}")
        print(f"  overrun at strict minimum {preflight['overrun_at_strict_minimum']}")
        print("  STOPPING BEFORE ANY TARGET VALUE IS OPENED.")
        print("  Policy NOT truncated. Policy NOT changed.")


if __name__ == "__main__":
    main()
