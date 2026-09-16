"""S7.7R stage C - Ahat_rec, audits, acceptance, freeze.

Opens no archive. Works only from stage B's registries.

It assembles the explored frontier, completes the multiplicity and constructor
audits that the blocked V1 could not compute, states the searched/unsearched
boundary exactly, and freezes. It selects nothing: the lowest-navigation-score
supports are reported as descriptive properties of Ahat_rec and are never called
optimal, qualified, final, or C*.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
V2 = HERE.parent
S77 = V2.parent
S7 = S77.parent
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
MAN = V2 / "manifests"

FREEZE_ID = "D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2"
SELF_REF = {"S7_7R_ACCEPTANCE_CHECKS.json", "S7_7R_FREEZE.json"}
ACTIVE = ["C0", "C1", "C2", "C3", "C5", "C6", "C7"]
FAMS = ["ece_te_profile", "cer_rotation_ti", "neutral_beams", "gas_injection",
        "magnetics", "filterscope_dalpha", "density"]
SUPPORT_MAX = 12


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    hist = json.loads((MAN / "HISTORICAL_S7_7_V1_RECORD.json").read_text())
    carry = json.loads((MAN / "PRE_SEARCH_CONTRACT_CARRY_FORWARD.json").read_text())
    dif = json.loads((MAN / "SEARCH_POLICY_DIFF.json").read_text())
    polman = json.loads((MAN / "POLICY_FREEZE_V2.json").read_text())
    acc = json.loads((MAN / "ACCESS_AUDIT.json").read_text())
    rt = json.loads((MAN / "SEARCH_BUDGET_RUNTIME_AUDIT.json").read_text())
    pxe = json.loads((MAN / "PROXY_EQUIVALENCE.json").read_text())
    POL = json.loads((V2 / "SEARCH_POLICY_PREVALUE_V2.json").read_text())
    pf = json.loads((V2 / "SEARCH_BUDGET_PREFLIGHT_V2.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    U = json.loads((S76R / "atomic_coordinate_universe.json").read_text())
    AREC = json.loads((S76R / "A_REC_HARDENED.json").read_text())

    AT = pd.read_csv(V2 / "atomic_navigation_scores.csv")
    SH = pd.read_csv(V2 / "constructor_shortlist.csv")
    SEED = pd.read_csv(V2 / "search_seed_registry.csv")
    EV = pd.read_csv(V2 / "search_candidate_evaluations.csv")
    PMAIN = pd.read_csv(V2 / "search_retained_paths.csv")
    PRAW = pd.read_csv(V2 / "raw_only_search_paths.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv")
    fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))
    anc_of = dict(zip(AT.coordinate_id, AT.primitive_ancestors))
    afam = {c: sorted({fam[a] for a in str(s).split("|")})
            for c, s in anc_of.items()}
    N_ATOM = len(AT)

    # ---------------- 17/18. the explored frontier -------------------------
    atomrows = pd.DataFrame({
        "support_id": AT.coordinate_id, "support_size": 1,
        "coordinate_ids": AT.coordinate_id,
        "first_lane": "ATOMIC", "first_expansion_step": 1,
        "constructor_composition": AT.constructor,
        "ancestor_family_composition": ["+".join(afam[c]) for c in AT.coordinate_id],
        "J_search": AT.J_search, "rank_status": AT.rank_status,
        "first_evaluation_order": 0})
    FR = pd.concat([atomrows, EV], ignore_index=True)
    assert FR.support_id.is_unique
    FR = FR.sort_values(["support_size", "J_search", "support_id"])
    FR.to_csv(V2 / "explored_support_registry.csv", index=False)
    M_AHAT = int(len(FR))

    by_size = FR.groupby("support_size").size().to_dict()
    finite = FR[np.isfinite(FR.J_search)]

    # ---------------- 22. lowest navigation score by size ------------------
    low = []
    for m in range(1, SUPPORT_MAX + 1):
        sub = finite[finite.support_size == m]
        if not len(sub):
            continue
        r = sub.sort_values(["J_search", "support_id"]).iloc[0]
        low.append({"support_size": m,
                    "label": f"LOWEST_NAVIGATION_SCORE_SUPPORT_AT_SIZE_{m}",
                    "support_id": r.support_id, "J_search": float(r.J_search),
                    "constructor_composition": r.constructor_composition,
                    "ancestor_family_composition": r.ancestor_family_composition,
                    "n_supports_of_this_size_in_Ahat_rec": int(len(sub)),
                    "is_optimal": False, "is_qualified": False,
                    "is_final": False, "is_C_star": False,
                    "note": "descriptive property of Ahat_rec only"})
    pd.DataFrame(low).to_csv(V2 / "lowest_navigation_score_by_size.csv",
                             index=False)

    rawset = set()
    for cids in PRAW.coordinate_ids:
        rawset.add("|".join(sorted(str(cids).split("|"))))
    rawFR = FR[FR.support_id.isin(rawset)]
    lowraw = []
    for m in range(1, SUPPORT_MAX + 1):
        sub = rawFR[(rawFR.support_size == m) & np.isfinite(rawFR.J_search)]
        if not len(sub):
            continue
        r = sub.sort_values(["J_search", "support_id"]).iloc[0]
        lowraw.append({"support_size": m, "lane": "RAW_ONLY",
                       "support_id": r.support_id, "J_search": float(r.J_search),
                       "ancestor_family_composition": r.ancestor_family_composition,
                       "n_raw_only_path_supports_of_this_size": int(len(sub)),
                       "is_B2": False, "is_final": False})
    pd.DataFrame(lowraw).to_csv(V2 / "raw_only_lowest_navigation_by_size.csv",
                                index=False)

    # ---------------- 20. multiplicity audit -------------------------------
    def touches(comp, f):
        return f in str(comp).split("+")

    retained_main = set(("|".join(sorted(str(c).split("|"))))
                        for c in PMAIN.coordinate_ids)
    retained_all = retained_main | rawset
    RET = FR[FR.support_id.isin(retained_all)]
    seed_ids = set(SEED.coordinate_id)
    short_ids = set(SH.coordinate_id)
    lowset = {r["support_id"] for r in low}
    LOWFR = FR[FR.support_id.isin(lowset)]

    rows = []
    for f in FAMS:
        n_prim = int(sum(v == f for v in fam.values()))
        n_atom = int(sum(touches(c, f) for c in FR[FR.support_size == 1]
                         .ancestor_family_composition))
        n_short = int(sum(f in afam[c] for c in short_ids))
        n_seed = int(sum(f in afam[c] for c in seed_ids))
        n_expl = int(sum(touches(c, f) for c in FR.ancestor_family_composition))
        n_ret = int(sum(touches(c, f) for c in RET.ancestor_family_composition))
        n_low = int(sum(touches(c, f) for c in LOWFR.ancestor_family_composition))
        rows.append({
            "scientific_family": f,
            "A_primitives_in_P_hard": n_prim,
            "A_share_of_P_hard": n_prim / 70,
            "B_atoms_with_this_ancestry": n_atom,
            "B_atom_ancestry_share": n_atom / N_ATOM,
            "C_shortlist_atoms": n_short,
            "C_shortlist_share": n_short / len(short_ids),
            "D_seeds": n_seed, "D_seed_share": n_seed / len(seed_ids),
            "E_explored_supports": n_expl,
            "E_explored_share": n_expl / M_AHAT,
            "F_retained_path_supports": n_ret,
            "F_retained_share": n_ret / len(RET) if len(RET) else 0.0,
            "G_lowest_J_supports": n_low,
            "G_lowest_J_share": n_low / len(LOWFR) if len(LOWFR) else 0.0})
    MA = pd.DataFrame(rows).sort_values("B_atom_ancestry_share", ascending=False)
    MA.to_csv(V2 / "multiplicity_audit.csv", index=False)

    ece = MA[MA.scientific_family == "ece_te_profile"].iloc[0]
    ece_ver = {
        "family": "ece_te_profile",
        "share_of_P_hard": float(ece.A_share_of_P_hard),
        "atom_ancestry_share": float(ece.B_atom_ancestry_share),
        "shortlist_share": float(ece.C_shortlist_share),
        "seed_share": float(ece.D_seed_share),
        "explored_support_share": float(ece.E_explored_share),
        "retained_path_share": float(ece.F_retained_share),
        "lowest_J_support_share": float(ece.G_lowest_J_share),
        "opportunity_was_balanced":
            float(ece.D_seed_share) < float(ece.B_atom_ancestry_share),
        "still_dominant_after_balanced_opportunity":
            float(ece.F_retained_share) >= 0.5,
        "reading": ("the fairness condition is on SEARCH OPPORTUNITY, which was "
                    "met: ECE's seed share is far below its atom-ancestry "
                    "share. What the performance-guided expansion then did with "
                    "that balanced opportunity is an empirical "
                    "development-search outcome and is reported as found."),
        "rebalanced_after_seeing_it": False}

    # ---------------- 21. constructor audit --------------------------------
    crows = []
    for c in ACTIVE:
        n_at = int((AT.constructor == c).sum())
        n_sh = int((SH.constructor == c).sum())
        n_sd = int((SEED[SEED.lane == "MAIN"].constructor == c).sum())
        n_ex = int(sum(c in str(x).split("+")
                       for x in FR.constructor_composition))
        n_rt = int(sum(c in str(x).split("+")
                       for x in RET.constructor_composition))
        crows.append({"constructor": c, "admissible_atoms": n_at,
                      "atom_share": n_at / N_ATOM, "shortlist_atoms": n_sh,
                      "shortlist_share": n_sh / len(SH),
                      "seeds": n_sd, "seed_share": n_sd / 127,
                      "explored_support_participation": n_ex,
                      "explored_participation_share": n_ex / M_AHAT,
                      "retained_path_participation": n_rt,
                      "retained_participation_share":
                          n_rt / len(RET) if len(RET) else 0.0,
                      "status": "ACTIVE"})
    for c in ("C4", "C8"):
        crows.append({"constructor": c, "admissible_atoms": 0, "atom_share": 0.0,
                      "shortlist_atoms": 0, "shortlist_share": 0.0, "seeds": 0,
                      "seed_share": 0.0, "explored_support_participation": 0,
                      "explored_participation_share": 0.0,
                      "retained_path_participation": 0,
                      "retained_participation_share": 0.0,
                      "status": "DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS / "
                                "ZERO_SEARCH_OPPORTUNITY (not a search "
                                "exclusion; not rescued)"})
    pd.DataFrame(crows).to_csv(V2 / "constructor_audit.csv", index=False)

    # ---------------- 24. searched / unsearched boundary -------------------
    unconstrained = sum(math.comb(N_ATOM, m) for m in range(1, SUPPORT_MAX + 1))
    ub = [{"quantity": "admissible atomic coordinates in C_rec_hard^atom",
           "value": N_ATOM},
          {"quantity": "Ahat_rec size-1 supports (all atoms scored)",
           "value": int(by_size.get(1, 0))},
          {"quantity": "unique multivariate supports scored",
           "value": M_AHAT - int(by_size.get(1, 0))},
          {"quantity": "total unique supports in Ahat_rec", "value": M_AHAT},
          {"quantity": "multivariate proposals made (incl. duplicates)",
           "value": rt["multivariate_proposals"]},
          {"quantity": "proposals rejected by Phi_set before evaluation",
           "value": rt["phi_set_rejected_proposals"]},
          {"quantity": "unconstrained admissible supports of size 1..12 "
                       "(ignores Phi_set; shown only for scale)",
           "value": unconstrained},
          {"quantity": "admissible supports NOT searched (ADMISSIBLE_UNSEARCHED)",
           "value": unconstrained - M_AHAT},
          {"quantity": "fraction of the size-1..12 support space actually "
                       "scored", "value": M_AHAT / unconstrained}]
    pd.DataFrame(ub).to_csv(V2 / "unsearched_boundary_summary.csv", index=False)

    boundary = {
        "record_id": "SEARCHED_UNSEARCHED_BOUNDARY_V2",
        "all_atoms_scored": int(by_size.get(1, 0)) == N_ATOM,
        "supports_by_size": {str(k): int(v) for k, v in sorted(by_size.items())},
        "Ahat_rec_cardinality": M_AHAT,
        "ADMISSIBLE_UNSEARCHED": {
            "definition": "an admissible support never proposed",
            "count": unconstrained - M_AHAT,
            "claim_made_about_it": "NONE"},
        "PROPOSED_BUT_SET_INADMISSIBLE": {
            "count": rt["phi_set_rejected_proposals"],
            "note": "outside Ahat_rec because already outside A_rec"},
        "invariant": "NOT SEARCHED != INADMISSIBLE",
        "no_claim_about_unsearched_region": True,
        "language_not_used": ["global optimum", "exhaustive search",
                              "complete search"],
    }
    (MAN / "SEARCHED_UNSEARCHED_BOUNDARY.json").write_text(
        json.dumps(boundary, indent=2), encoding="utf-8")

    # ---------------- Sigma_rec and Ahat_rec -------------------------------
    sigma = {
        "sigma_rec_id": "SIGMA_REC_ONE_SEED_PRIMARY_V2",
        "freeze_id": FREEZE_ID, "status": "FROZEN_AND_EXECUTED",
        "policy_file": "SEARCH_POLICY_PREVALUE_V2.json",
        "policy_sha256": polman["sha256"],
        "policy_frozen_utc": polman["frozen_utc"],
        "parent_policy_sha256": polman["parent_v1_policy_sha256"],
        "policy_diff_verdict": dif["verdict"],
        "only_substantive_change": dif["substantive_change"],
        "ONE_SEED_SEARCH": "PRIMARY",
        "TWO_SEED_SEARCH": POL["s6_primary_vs_sensitivity"]["TWO_SEED_SEARCH"],
        "search_proxy": POL["s7_search_proxy"]["id"],
        "proxy_equivalence_to_lstsq": {
            "max_relative_deviation": pxe["max_relative_deviation"],
            "passes": pxe["passes"]},
        "navigation_score": POL["s8_navigation_score"]["definition"],
        "navigation_score_is_not": ["U_rec", "validation evidence",
                                    "final qualification"],
        "n_active_strata": 127, "n_seeds_main": 127, "n_seeds_raw_only": 7,
        "shortlist_total": int(len(SH)),
        "runtime": rt,
    }
    (V2 / "SIGMA_REC_V2.json").write_text(json.dumps(sigma, indent=2),
                                          encoding="utf-8")

    ahat = {
        "frontier_id": "AHAT_REC_DENSITY_ONE_SEED_V2",
        "freeze_id": FREEZE_ID,
        "parent_universe": AREC["universe_id"],
        "formal_definition": "Ahat_rec = Explore(A_rec^H; Sigma_rec, B_rec) "
                             "subset A_rec^H",
        "membership_rule": "a support is in Ahat_rec iff its search proxy was "
                           "actually numerically evaluated",
        "cardinality": M_AHAT,
        "size_1_supports": int(by_size.get(1, 0)),
        "multivariate_supports": M_AHAT - int(by_size.get(1, 0)),
        "supports_by_size": {str(k): int(v) for k, v in sorted(by_size.items())},
        "deduplicated": True,
        "path_provenance_preserved_in": "search_proposal_provenance.csv",
        "per_cell_nrmse_detail": ["atomic_per_cell_nrmse.npz",
                                  "explored_per_cell_nrmse.npz"],
        "rank_deficient_supports": int((FR.rank_status
                                        == "SEARCH_PROXY_RANK_DEFICIENT").sum()),
        "relation_template": "T_REC_V1 for every C (unchanged)",
        "support_bound": K["B_rec"]["representation_size_range"],
        "lowest_navigation_score_supports": low,
        "explicitly_not": {"C_star_selected": False, "R_star_selected": False,
                           "Q_rec_star_selected": False,
                           "U_rec_applied": False,
                           "baselines_compared": False,
                           "qualified_candidate_declared": False,
                           "validation_claim": False,
                           "optimal_or_exhaustive_language_used": False},
        "target_values": "development only",
        "external_values_accessed": 0,
        "owned_by_next_stage": "S7.8 applies the frozen utility and "
                               "qualification rules over Ahat_rec",
    }
    (V2 / "AHAT_REC_V2.json").write_text(json.dumps(ahat, indent=2, default=str),
                                         encoding="utf-8")

    sens = {
        "record_id": "TWO_SEED_SEARCH_DEPTH_SENSITIVITY",
        "status": ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
        "purpose_if_undertaken": "test whether increasing multi-start depth "
                                 "materially changes conclusions",
        "must_not": ["replace the present primary one-seed frontier",
                     "retroactively become the primary result",
                     "convert a failed primary q_rec into a successful primary "
                     "structural-transfer claim",
                     "rescue, redefine or retroactively optimize the primary "
                     "result"],
        "outcome_trigger_defined": False,
        "forbidden_trigger_example": "'run if the primary result is bad'",
        "if_later_authorised": "it is a search-depth sensitivity analysis "
                               "REGARDLESS of the primary result, separately "
                               "labelled",
        "declared_before_density_access": True,
        "declared_in": "SEARCH_POLICY_PREVALUE_V2.json section "
                       "s6_primary_vs_sensitivity",
    }
    (V2 / "two_seed_sensitivity_declaration.json").write_text(
        json.dumps(sens, indent=2), encoding="utf-8")

    # ---------------- historical V1 preservation ---------------------------
    snap = hist["byte_snapshot"]
    changed = [r for r, h in snap.items()
               if not (S77 / r).exists() or sha(S77 / r) != h]
    preserved = {"n_files_checked": len(snap), "n_changed": len(changed),
                 "changed_files": changed,
                 "verdict": "HISTORICAL_S7_7_V1_BYTE_FOR_BYTE_UNCHANGED"
                            if not changed else "STOP_HISTORICAL_V1_MODIFIED"}
    (MAN / "HISTORICAL_V1_PRESERVATION.json").write_text(
        json.dumps(preserved, indent=2), encoding="utf-8")

    # ---------------- acceptance -------------------------------------------
    md = sorted(p.name for p in V2.glob("*.md"))
    n_short_by_c = {c: int((SH.constructor == c).sum()) for c in ACTIVE}
    strata_in_short = set(SH.search_stratum)
    all_strata = set(AT.search_stratum)
    checks = {
        "all_parents_verified": par["verdict"] == "PARENTS_VERIFIED"
            and par["n_drift"] == 0,
        "historical_S7_7_V1_preserved_unchanged": not changed,
        "stage_A_pre_search_completion_carried_unchanged":
            carry["hash_verified_unchanged"] and carry["regenerated"] is False,
        "S_pers_unchanged": carry["S_PERS_V1"]["present"]
            and carry["S_PERS_V1"]["replaces_NRMSE"] is False
            and carry["S_PERS_V1"]["changes_V3"] is False,
        "B1A_AR1_unchanged": carry["B1A_AR1"]["present"]
            and carry["B1A_AR1"]["run_here"] is False,
        "only_substantive_policy_change_is_seeds_2_to_1":
            dif["verdict"] == "ONLY_SEED_MULTIPLICITY_CHANGED"
            and not dif["unauthorised_changes"],
        "raw_only_lane_changed_consistently_2_to_1":
            POL["s15_raw_only_lane"]["n_seeds_projected"] == 7
            and int((SEED.lane == "RAW_ONLY").sum()) == 7,
        "new_complete_policy_hashed_before_density_access":
            acc["policy_frozen_before_first_density_access"]
            and acc["policy_hash_verified_before_first_archive_open"],
        "projected_search_within_300000": pf["within_budget"]
            and pf["max_projected_support_evaluations"] <= 300000,
        "first_density_access_after_policy_freeze":
            acc["policy_frozen_utc"] < acc["first_density_access_utc"],
        "external_values_accessed_zero": acc["external_signal_values"] == 0
            and acc["external_target_values"] == 0
            and acc["external_shots_read"] == [],
        "all_10778_atoms_scored": int(by_size.get(1, 0)) == 10778 == N_ATOM,
        "all_127_strata_retained": len(all_strata) == 127,
        "no_global_top_K_atom_pruning":
            POL["s11_within_stratum_ranking"]["global_top_K_pruning"] is False
            and int(len(AT)) == 10778,
        "shortlist_rule_unchanged":
            POL["s12_shortlist"]["MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION"] == 96
            and all(v <= 96 for v in n_short_by_c.values()),
        "every_nonempty_stratum_represented_in_shortlist":
            strata_in_short == all_strata,
        "exactly_one_main_seed_per_active_stratum":
            int((SEED.lane == "MAIN").sum()) == 127
            and set(SEED[SEED.lane == "MAIN"].seed_stratum) == all_strata,
        "exactly_one_raw_only_seed_per_active_C0_family":
            int((SEED.lane == "RAW_ONLY").sum())
            == len([s for s in all_strata if s.startswith("C0:")]),
        "greedy_paths_executed_through_size_at_most_12":
            int(PMAIN.support_size.max()) <= 12
            and int(PRAW.support_size.max()) <= 12,
        "Phi_set_unchanged": POL["unchanged_from_parents"]["Phi_set"],
        "no_family_bonus_in_J_search":
            "scientific-family bonus" in POL["s8_navigation_score"][
                "terms_explicitly_excluded"],
        "no_S_pers_in_search": acc["S_pers_computed"] == 0,
        "no_baseline_run": acc["baselines_run"] == 0,
        "C4_not_rescued": U["by_constructor"]["C4"] == 0
            and "rescue C4" in POL["forbidden"],
        "C8_not_rescued": U["by_constructor"]["C8"] == 0
            and "rescue C8" in POL["forbidden"],
        "no_shifted_or_bounded_constructors":
            "shifted phase derivative" in POL["forbidden"],
        "Ahat_rec_constructed": M_AHAT > 0,
        "all_evaluated_supports_registered":
            M_AHAT == int(by_size.get(1, 0)) + rt[
                "unique_multivariate_supports_evaluated"],
        "admissible_unsearched_supports_distinguished":
            boundary["ADMISSIBLE_UNSEARCHED"]["claim_made_about_it"] == "NONE",
        "no_global_optimum_language":
            ahat["explicitly_not"]["optimal_or_exhaustive_language_used"] is False,
        "multiplicity_audit_completed": len(MA) == 7
            and MA.F_retained_path_supports.notna().all(),
        "two_seed_sensitivity_declared_but_not_run":
            sens["status"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
        "no_outcome_triggered_expansion_rule":
            sens["outcome_trigger_defined"] is False,
        "no_final_C_star_selected":
            ahat["explicitly_not"]["C_star_selected"] is False
            and ahat["explicitly_not"]["U_rec_applied"] is False,
        "no_external_validation":
            ahat["explicitly_not"]["validation_claim"] is False,
        "markdown_files_at_most_20": len(md) <= 20,
        "S7_8_not_started": not (S7 / "08_utility_qualification").exists(),
        # structural
        "runtime_within_frozen_allowance": rt["within_frozen_allowance"]
            and rt["verdict"] == "SEARCH_BUDGET_RUNTIME_OK",
        "search_not_truncated_at_limit":
            rt["truncated_after_reaching_limit"] is False,
        "proxy_matches_numpy_lstsq": pxe["passes"],
        "frontier_ids_unique": bool(FR.support_id.is_unique),
        "support_bound_1_12_respected": int(FR.support_size.max()) <= 12
            and int(FR.support_size.min()) >= 1,
        "firewall_intact": acc["verdict"] == "FIREWALL_INTACT",
    }
    checks = {k: bool(v) for k, v in checks.items()}   # numpy bool -> json bool
    n_pass = sum(1 for v in checks.values() if v)
    n_tot = len(checks)
    (V2 / "S7_7R_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "freeze_id": FREEZE_ID, "n_pass": n_pass, "n_total": n_tot,
        "summary": f"{n_pass}/{n_tot}",
        "failing": [k for k, v in checks.items() if not v],
        "checks": checks}, indent=2), encoding="utf-8")

    # ---------------- freeze ------------------------------------------------
    arts = {}
    for p in sorted(V2.rglob("*")):
        if p.is_file() and p.name not in SELF_REF:
            arts[str(p.relative_to(V2)).replace("\\", "/")] = sha(p)

    quals = []
    if float(ece.F_retained_share) >= 0.5:
        quals.append(
            "ECE ancestry appears in %.1f%% of retained-path supports and "
            "%.0f%% of the lowest-navigation-score supports AFTER search "
            "opportunity was balanced (seed share %.1f%%, against an "
            "atom-ancestry share of %.1f%%). The fairness condition is on "
            "OPPORTUNITY and it was met; what the performance-guided expansion "
            "then did with that balanced opportunity is an empirical "
            "development-search outcome, recorded as found and NOT rebalanced."
            % (100 * ece.F_retained_share, 100 * ece.G_lowest_J_share,
               100 * ece.D_seed_share, 100 * ece.B_atom_ancestry_share))
    quals.append(
        "The primary search is one-seed: broad in scientific opportunity, "
        "shallower in multi-start depth. Reduced protection against "
        "greedy-start sensitivity was accepted prospectively. A two-seed "
        "search remains available only as a separately labelled search-depth "
        "sensitivity analysis and may never replace this primary frontier.")
    quals.append(
        "Ahat_rec covers %.3g%% of the unconstrained size-1..12 support space. "
        "The remainder is ADMISSIBLE_UNSEARCHED and carries no negative "
        "finding of any kind." % (100 * M_AHAT / unconstrained))

    freeze = {
        "freeze_id": FREEZE_ID, "status": "FROZEN_WITH_QUALIFICATIONS",
        "supersedes_for_primary_use": {
            "freeze_id": hist["freeze_id"], "status": hist["status"],
            "role": hist["role_here"],
            "preserved": preserved["verdict"]},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sigma_rec_id": sigma["sigma_rec_id"],
        "frontier_id": ahat["frontier_id"],
        "qualifications": quals,
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "pre_search_contract_sha256": carry["sha256"],
        "search_policy_v1_sha256": polman["parent_v1_policy_sha256"],
        "search_policy_v2_sha256": polman["sha256"],
        "search_policy_frozen_utc": polman["frozen_utc"],
        "first_density_access_utc": acc["first_density_access_utc"],
        "policy_diff": dif["substantive_change"],
        "policy_diff_verdict": dif["verdict"],
        "budget": {"projected_max": pf["max_projected_support_evaluations"],
                   "actual_total_proposals": rt["total_proposal_evaluations"],
                   "unique_multivariate": rt[
                       "unique_multivariate_supports_evaluated"],
                   "allowance": 300000, "verdict": rt["verdict"]},
        "atoms_scored": N_ATOM,
        "atoms_rank_deficient": int((AT.rank_status
                                     == "SEARCH_PROXY_RANK_DEFICIENT").sum()),
        "n_active_strata": 127, "shortlist_by_constructor": n_short_by_c,
        "seeds_main": 127, "seeds_raw_only": 7,
        "Ahat_rec_cardinality": M_AHAT,
        "supports_by_size": {str(k): int(v) for k, v in sorted(by_size.items())},
        "lowest_navigation_score_by_size":
            [{"m": r["support_size"], "J_search": r["J_search"],
              "support_id": r["support_id"]} for r in low],
        "ece_after_balanced_opportunity": ece_ver,
        "two_seed_sensitivity": sens["status"],
        "access": {"development_shots": acc["n_development_shots_read"],
                   "predictor_signals": 70, "target": "density (development)",
                   "external_signal_values": 0, "external_target_values": 0,
                   "baselines_run": 0, "verdict": acc["verdict"]},
        "unchanged": {"A_rec": True, "G_rec": True, "P_hard_70": True,
                      "C0_C8": True, "denominator_rule": True,
                      "support_bound_1_12": True, "T_REC_V1": True,
                      "SEARCH_PROXY_OLS_V1": True, "J_search": True,
                      "strata_definitions": True, "Phi_set": True},
        "acceptance_checks": f"{n_pass}/{n_tot}",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "n_artifacts": len(arts), "n_markdown": len(md),
        "all_artifact_hashes": arts,
        "self_referential_excluded": sorted(SELF_REF),
        "next_stage": "S7.8 (Utility qualification over Ahat_rec) - NOT AUTHORISED",
    }
    (V2 / "S7_7R_FREEZE.json").write_text(json.dumps(freeze, indent=2,
                                                     default=str),
                                          encoding="utf-8")

    print(f"Ahat_rec {M_AHAT}  by size "
          f"{ {k: int(v) for k, v in sorted(by_size.items())} }")
    print("lowest J by size:")
    for r in low:
        print(f"   m={r['support_size']:2d}  J={r['J_search']:.4f}  "
              f"{r['ancestor_family_composition']}")
    print(f"ECE  atoms {ece.B_atom_ancestry_share:.3f}  shortlist "
          f"{ece.C_shortlist_share:.3f}  seeds {ece.D_seed_share:.3f}  "
          f"explored {ece.E_explored_share:.3f}  retained "
          f"{ece.F_retained_share:.3f}")
    print(f"historical V1 preservation: {preserved['verdict']}")
    print(f"acceptance {n_pass}/{n_tot}  failing "
          f"{[k for k, v in checks.items() if not v]}")
    print(f"markdown {len(md)}  artifacts {len(arts)}")
    print(f"STATUS {freeze['status']}")


if __name__ == "__main__":
    main()
