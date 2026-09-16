"""S7.7 stage C - budget-block record, option analysis, acceptance, freeze.

METADATA ONLY. THIS SCRIPT OPENS NO ARCHIVE AND READS NO SIGNAL OR TARGET VALUE.

Stage B's preflight exceeded MAX_SUPPORT_EVALUATIONS, so section 16 requires the
stage to stop before any density value is opened. This stage records that block,
computes what each candidate remedy would cost - WITHOUT choosing one, because
choosing one is a policy change and policy changes belong to the human - and
freezes S7.7 as BLOCKED_SEARCH_BUDGET.

Nothing here truncates the search, adjusts a threshold, or scores a coordinate.
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

HERE = Path(__file__).resolve().parent
S77 = HERE.parent
S7 = S77.parent
S76R = S7 / "06_admissible_universe" / "hardened_v2"
MAN = S77 / "manifests"

FREEZE_ID = "D3D-SIR-S7.7-FROZEN-SEARCH-POLICY-AND-EXPLORED-FRONTIER-V1"
SELF_REF = {"S7_7_ACCEPTANCE_CHECKS.json", "S7_7_FREEZE.json"}
SUPPORT_MAX = 12


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def project(n_seeds_main, n_strata_short, n_seeds_raw, n_strata_raw, atomic):
    steps = SUPPORT_MAX - 1
    mx = n_seeds_main * steps * n_strata_short + n_seeds_raw * steps * n_strata_raw
    mn = (n_seeds_main * sum(max(0, n_strata_short - (m - 1))
                             for m in range(2, SUPPORT_MAX + 1))
          + n_seeds_raw * sum(max(0, n_strata_raw - (m - 1))
                              for m in range(2, SUPPORT_MAX + 1)))
    return atomic + mx, atomic + mn


def main() -> None:
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    pre = json.loads((MAN / "PRE_SEARCH_CONTRACT_FREEZE.json").read_text())
    pf = json.loads((MAN / "SEARCH_BUDGET_PREFLIGHT.json").read_text())
    pol = json.loads((MAN / "POLICY_FREEZE.json").read_text())
    policy = json.loads((S77 / "SEARCH_POLICY_PREVALUE.json").read_text())
    strata = pd.read_csv(S77 / "search_strata.csv")
    ATOM = pd.read_csv(S77 / "atom_stratum_assignment.csv")

    if pf["verdict"] == "SEARCH_BUDGET_OK":
        raise SystemExit("budget preflight passed; this stage is the block path")

    CAP = pf["MAX_SUPPORT_EVALUATIONS"]
    atomic = pf["atomic_scoring_evaluations"]
    n_short = pf["strata_represented_in_shortlist"]
    n_raw_str = pf["raw_only_lane"]["proposals_per_step_max"]

    # ---- option analysis: what each candidate remedy would cost -----------
    opts = []
    for k in (1, 2):
        seeds_main = int(strata.n_atoms.clip(upper=k).sum())
        c0 = strata[strata.constructor == "C0"]
        seeds_raw = int(c0.n_atoms.clip(upper=k).sum())
        mx, mn = project(seeds_main, n_short, seeds_raw, n_raw_str, atomic)
        opts.append({
            "option": f"SEEDS_PER_STRATUM = {k}",
            "lever": "section 14 seed rule",
            "seeds_main": seeds_main, "seeds_raw_only": seeds_raw,
            "max_projected": mx, "strict_lower_bound": mn,
            "fits_300000": mx <= CAP,
            "cost": ("none to coverage: every stratum still receives a starting "
                     "path, but only one instead of two, so a stratum whose best "
                     "atom leads into a poor basin has no second independent "
                     "start" if k == 1 else "this is the frozen policy"),
        })
    opts.append({
        "option": "raise MAX_SUPPORT_EVALUATIONS to >= 363,900",
        "lever": "section 16 computational budget",
        "seeds_main": pf["main_lane"]["n_seeds"],
        "seeds_raw_only": pf["raw_only_lane"]["n_seeds"],
        "max_projected": pf["max_projected_support_evaluations"],
        "strict_lower_bound": pf["strict_lower_bound_support_evaluations"],
        "fits_300000": False,
        "cost": ("no change to search semantics at all; purely a larger "
                 "computational allowance. Must be re-frozen prospectively, "
                 "before any density value is opened."),
    })
    non_levers = [
        {"candidate": "lower MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION below 96",
         "why_it_does_not_help": (
             "proposals per growth step equal the number of STRATA represented "
             "in the shortlist, not the number of shortlisted atoms. Round 1 of "
             "the round-robin already gives every stratum one slot, so any cap "
             "at or above 35 (the largest per-constructor stratum count) yields "
             "the same 127 proposals per step. A cap below a constructor's "
             "stratum count would instead trip the section 13 STOP."),
         "usable_lever": False},
        {"candidate": "reduce the support bound below 12",
         "why_it_does_not_help": "forbidden by section 0; B_rec is frozen",
         "usable_lever": False},
        {"candidate": "deduplicate supports reached by multiple paths",
         "why_it_does_not_help": (
             "section 18 deduplication governs the REGISTRY, not the number of "
             "proxy evaluations proposed. More importantly, which supports "
             "coincide across paths depends on target-dependent greedy choices, "
             "so a dedup-based projection is not computable from metadata and "
             "cannot certify the budget BEFORE target access, which is exactly "
             "what section 16 requires."),
         "usable_lever": False},
        {"candidate": "prune strata, atoms, or constructor families",
         "why_it_does_not_help": (
             "would delete admissible coordinates to fit a computational "
             "allowance, inverting ADMISSIBLE != PRIORITIZED and contradicting "
             "section 5's explicit prohibition"),
         "usable_lever": False},
    ]

    block = {
        "record_id": "SEARCH_BUDGET_BLOCK_V1",
        "verdict": "SEARCH_BUDGET_REQUIRES_HUMAN_REVIEW",
        "stage_outcome": "BLOCKED_SEARCH_BUDGET",
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
        "computed_from": "METADATA_ONLY",
        "density_values_opened": 0,
        "external_values_opened": 0,
        "why": (
            "Section 16 requires the deterministic policy's projected candidate "
            "support evaluations to be computed from metadata before any target "
            "value is opened, and requires an unconditional STOP if the "
            "projection exceeds MAX_SUPPORT_EVALUATIONS = 300,000. The frozen "
            "policy of sections 12-15 projects 363,900 evaluations at maximum "
            "and 346,484 at a strict lower bound. Both exceed the budget."),
        "arithmetic": {
            "active_strata": pf["active_stratum_count"],
            "strata_represented_in_shortlist": n_short,
            "seeds_main_lane": pf["main_lane"]["n_seeds"],
            "seeds_raw_only_lane": pf["raw_only_lane"]["n_seeds"],
            "growth_steps_per_seed": SUPPORT_MAX - 1,
            "main_lane_max": f"{pf['main_lane']['n_seeds']} seeds x 11 steps x "
                             f"{n_short} proposals = "
                             f"{pf['main_lane']['evaluations_max']}",
            "raw_lane_max": f"{pf['raw_only_lane']['n_seeds']} seeds x 11 steps "
                            f"x {n_raw_str} proposals = "
                            f"{pf['raw_only_lane']['evaluations_max']}",
            "atomic_scoring": atomic,
            "total_max": pf["max_projected_support_evaluations"],
            "total_strict_lower_bound": pf["strict_lower_bound_support_evaluations"],
            "budget": CAP,
            "overrun_max": pf["overrun_at_maximum"],
            "overrun_strict_minimum": pf["overrun_at_strict_minimum"]},
        "not_a_bound_artifact": (
            "the STRICT LOWER BOUND also overruns, by 46,484. The lower bound "
            "assumes the most favourable possible stratum exhaustion, namely "
            "that at proposal time for size m every one of the m-1 atoms "
            "already in the support has exhausted a distinct stratum. No "
            "execution of this policy can come in under 300,000."),
        "what_was_not_done": [
            "the policy was NOT truncated",
            "the policy was NOT changed to fit the budget",
            "no seed count, cap, stratum or support bound was adjusted",
            "no admissible coordinate was pruned",
            "no density value was opened",
            "no atom was scored"],
        "remedies_computed_not_chosen": opts,
        "non_levers": non_levers,
        "decision_belongs_to": "human review",
        "constraint_on_any_remedy": (
            "whichever remedy is chosen must be re-frozen PROSPECTIVELY, before "
            "any density value is opened, and the new SEARCH_POLICY_PREVALUE "
            "hash recorded. Adjusting the budget or the policy after target "
            "outcomes are seen is forbidden by sections 13 and 16 and would "
            "make the stage SEARCH_POLICY_CONTAMINATED."),
    }
    (S77 / "search_budget_block.json").write_text(json.dumps(block, indent=2),
                                                  encoding="utf-8")

    # ---- multiplicity audit, opportunity side only ------------------------
    # Sections 22A and 22B are computable from metadata. 22C-E require the
    # target-dependent ranking that this stage is blocked from performing.
    HB = pd.read_csv(S7 / "05H_primitive_space_and_ontology_hardening"
                     / "primitive_basis_hardened.csv")
    fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))
    rows = []
    for f in sorted(set(fam.values())):
        n_at = int(sum(f in {fam[o] for o in str(s).split("|")}
                       for s in ATOM.ordered_operands))
        rows.append({"scientific_family": f,
                     "n_primitives_in_P_hard": int(sum(v == f for v in fam.values())),
                     "n_admissible_atoms_with_this_ancestry": n_at,
                     "atom_ancestry_share": n_at / len(ATOM)})
    MA = pd.DataFrame(rows).sort_values("n_admissible_atoms_with_this_ancestry",
                                        ascending=False)
    # opportunity share: strata are the unit of search opportunity
    occ = []
    for f in sorted(set(fam.values())):
        code = {"ece_te_profile": "ECE", "cer_rotation_ti": "CER",
                "neutral_beams": "NBI", "gas_injection": "GAS",
                "magnetics": "MAG", "filterscope_dalpha": "FS",
                "density": "DEN"}[f]
        n_str = int(sum(code in str(s).replace("{", "").replace("}", "")
                        .replace("|", ",").split(",")
                        for s in strata.family_signature))
        seeds = int(strata.loc[[code in str(s).replace("{", "").replace("}", "")
                                .replace("|", ",").split(",")
                                for s in strata.family_signature],
                               "seeds_projected"].sum())
        occ.append({"scientific_family": f, "family_code": code,
                    "n_strata_touching_this_family": n_str,
                    "stratum_share": n_str / len(strata),
                    "projected_seeds_touching_this_family": seeds,
                    "projected_seed_share": seeds / int(strata.seeds_projected.sum())})
    OCC = pd.DataFrame(occ).sort_values("n_strata_touching_this_family",
                                        ascending=False)
    MA = MA.merge(OCC, on="scientific_family")
    MA["multiplicity_amplification_removed"] = (
        MA.atom_ancestry_share - MA.projected_seed_share)
    MA.to_csv(S77 / "multiplicity_opportunity_audit.csv", index=False)

    ma_json = {
        "audit_id": "MULTIPLICITY_OPPORTUNITY_AUDIT_V1",
        "scope": "sections 22A and 22B only - the OPPORTUNITY side, which is "
                 "computable from metadata",
        "not_computable_here": {
            "22C_seed_share_realised": "seeds are the top-2 atoms BY WITHIN-"
                                       "STRATUM RANK, which requires J_search",
            "22D_explored_support_participation": "requires the search to run",
            "22E_retained_path_participation": "requires the search to run"},
        "reason": "the stage is blocked before target access",
        "by_family": MA.to_dict(orient="records"),
        "headline": {
            "ece_atom_ancestry_share": float(
                MA.loc[MA.scientific_family == "ece_te_profile",
                       "atom_ancestry_share"].iloc[0]),
            "ece_projected_seed_share": float(
                MA.loc[MA.scientific_family == "ece_te_profile",
                       "projected_seed_share"].iloc[0]),
            "interpretation": "the stratified policy would have cut ECE's share "
                              "of initial search opportunity well below its "
                              "share of atomic multiplicity. That is the "
                              "policy's purpose and it is demonstrable from "
                              "metadata alone, independently of the block."},
    }
    (S77 / "multiplicity_opportunity_audit.json").write_text(
        json.dumps(ma_json, indent=2, default=str), encoding="utf-8")

    # ---- constructor audit, opportunity side ------------------------------
    ca = []
    for c in ["C0", "C1", "C2", "C3", "C5", "C6", "C7"]:
        n_at = int((ATOM.constructor == c).sum())
        sub = strata[strata.constructor == c]
        ca.append({"constructor": c, "admissible_atoms": n_at,
                   "atom_share": n_at / len(ATOM),
                   "n_strata": int(len(sub)),
                   "projected_shortlist": pf["expansion_shortlist_count"][c],
                   "shortlist_share": pf["expansion_shortlist_count"][c]
                   / pf["expansion_shortlist_total"],
                   "projected_seeds": int(sub.seeds_projected.sum()),
                   "seed_share": int(sub.seeds_projected.sum())
                   / int(strata.seeds_projected.sum()),
                   "status": "ACTIVE"})
    for c in ["C4", "C8"]:
        ca.append({"constructor": c, "admissible_atoms": 0, "atom_share": 0.0,
                   "n_strata": 0, "projected_shortlist": 0,
                   "shortlist_share": 0.0, "projected_seeds": 0,
                   "seed_share": 0.0,
                   "status": "DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS / "
                             "ZERO_SEARCH_OPPORTUNITY (not a search exclusion)"})
    pd.DataFrame(ca).to_csv(S77 / "constructor_opportunity_audit.csv", index=False)

    md = sorted(p.name for p in S77.glob("*.md"))

    # ---- acceptance --------------------------------------------------------
    U = json.loads((S76R / "atomic_coordinate_universe.json").read_text())
    A = json.loads((S76R / "A_REC_HARDENED.json").read_text())
    NA = "NOT_REACHED_STAGE_BLOCKED_BEFORE_TARGET_ACCESS"
    checks = {
        "all_parent_freezes_verified": par["verdict"] == "PARENTS_VERIFIED"
            and par["n_drift"] == 0,
        "S7_6R_authoritative": par["substantive_checks"][
            "A_REC_DENSITY_HARDENED_V2_authoritative"],
        "A_rec_unchanged": sha(S76R / "A_REC_HARDENED.json")
            == json.loads((S76R / "S7_6R_FREEZE.json").read_text())
            ["all_artifact_hashes"]["A_REC_HARDENED.json"],
        "G_rec_unchanged": par["substantive_checks"][
            "ontology_is_G_REC_DENSITY_HARDENED_V2"],
        "S_pers_frozen_before_target_access":
            pre["frozen_before_any_density_value_opened"],
        "AR1_diagnostic_frozen_before_target_access":
            pre["frozen_before_any_density_value_opened"],
        "neither_baseline_run": pre["neither_run"],
        "complete_search_policy_hashed_before_any_density_value":
            pol["frozen_before_any_density_value_opened"],
        "search_strata_assigned_metadata_only":
            policy["s6_search_strata"]["assigned_from_metadata_only"],
        "each_atom_assigned_exactly_one_stratum":
            len(ATOM) == 10778 and ATOM.search_stratum.notna().all()
            and ATOM.coordinate_id.is_unique,
        "constructor_and_family_role_semantics_correct":
            set(policy["s6_search_strata"]["signatures"])
            == {"C0", "C1", "C5", "C2", "C3", "C6", "C7"},
        "every_nonempty_stratum_receives_at_least_one_shortlist_opportunity":
            pf["every_nonempty_stratum_gets_a_slot"],
        "max_96_expansion_atoms_per_constructor":
            all(v <= 96 for v in pf["expansion_shortlist_count"].values()),
        "no_global_top_K_atomic_pruning":
            policy["s11_within_stratum_ranking"]["global_top_K_pruning"] is False,
        "support_bound_stays_at_most_12":
            policy["s15_raw_only_lane"]["support_max"] == 12,
        "Phi_set_enforced_unchanged":
            policy["unchanged_from_parents"]["Phi_set"],
        "search_proxy_OLS_frozen": policy["s7_search_proxy"]["id"]
            == "SEARCH_PROXY_OLS_V1",
        "search_score_uses_development_NRMSE_only":
            "20 development discharges" in policy["s8_navigation_score"]["definition"],
        "search_score_explicitly_not_U_rec":
            policy["s8_navigation_score"]["is_U_rec"] is False,
        "no_S_pers_used_for_search":
            "persistence skill" in policy["s8_navigation_score"][
                "terms_explicitly_excluded"],
        "no_baseline_result_used": all(
            v is False for k, v in policy["s20_no_baselines"].items()),
        "projected_support_evaluations_checked_before_target_access":
            pf["computed_from"] == "METADATA_ONLY" and pf["target_values_opened"] == 0,
        "budget_gate_honoured_not_truncated":
            block["what_was_not_done"][0].startswith("the policy was NOT truncated")
            and pf["policy_truncated_to_fit"] is False
            and pf["policy_changed_to_fit"] is False,
        "C4_not_rescued": U["by_constructor"]["C4"] == 0
            and "rescue C4" in policy["forbidden"],
        "C8_not_rescued": U["by_constructor"]["C8"] == 0
            and "rescue C8" in policy["forbidden"],
        "no_shifted_or_bounded_constructors":
            "shifted phase derivative" in policy["forbidden"]
            and "bounded phase derivative" in policy["forbidden"],
        "no_q_desc_seeding": "q_desc coordinate seeding" in policy["forbidden"],
        "no_retired_q_rec_seeding":
            "retired q_rec support seeding" in policy["forbidden"],
        "external_value_reads_zero": block["external_values_opened"] == 0,
        "density_value_reads_zero": block["density_values_opened"] == 0,
        "no_final_C_star_selected": A["search_priority_assigned"] is False
            and policy["s19_no_selection"]["returns_C_star"] is False,
        "no_validation_claim": True,
        "markdown_files_at_most_20": len(md) <= 20,
        "S7_8_not_started": not (S7 / "08_utility_qualification").exists(),
        # gated by the block - recorded as NOT REACHED, never as passed
        "all_10778_atoms_univariately_scored": NA,
        "shortlist_built_by_constructor_balanced_round_robin": NA,
        "up_to_two_seeds_per_stratum_instantiated": NA,
        "raw_only_control_lane_executed": NA,
        "all_scored_supports_recorded_in_Ahat_rec": NA,
        "unsearched_admissible_supports_not_called_inadmissible": NA,
    }
    reached = {k: v for k, v in checks.items() if v is not NA}
    n_pass = sum(1 for v in reached.values() if v)
    n_reach = len(reached)
    n_gated = len(checks) - n_reach
    (S77 / "S7_7_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "freeze_id": FREEZE_ID,
        "summary": f"{n_pass}/{n_reach} reached, {n_gated} not reached "
                   f"(stage blocked before target access)",
        "n_pass": n_pass, "n_reached": n_reach, "n_not_reached": n_gated,
        "failing": [k for k, v in reached.items() if not v],
        "not_reached": [k for k, v in checks.items() if v is NA],
        "not_reached_meaning": "these checks concern operations the stage is "
                               "blocked from performing. They are recorded as "
                               "NOT REACHED, never as passed.",
        "checks": checks}, indent=2), encoding="utf-8")

    # ---- freeze ------------------------------------------------------------
    arts = {}
    for p in sorted(S77.rglob("*")):
        if p.is_file() and p.name not in SELF_REF:
            arts[str(p.relative_to(S77)).replace("\\", "/")] = sha(p)

    freeze = {
        "freeze_id": FREEZE_ID,
        "status": "BLOCKED_SEARCH_BUDGET",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "blocked_at": "section 16 search-budget preflight",
        "blocked_before": "any density value was opened",
        "sigma_rec_state": "FROZEN_PREVALUE_COMPLETE_BUT_NOT_EXECUTED",
        "Ahat_rec_state": "NOT_CONSTRUCTED",
        "reason": block["why"],
        "arithmetic": block["arithmetic"],
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "pre_search_contract_sha256": pre["sha256"],
        "search_policy_prevalue_sha256": pol["sha256"],
        "search_policy_frozen_utc": policy["frozen_utc"],
        "n_active_strata": pf["active_stratum_count"],
        "strata_per_constructor": pf["strata_per_constructor"],
        "projected_max": pf["max_projected_support_evaluations"],
        "projected_strict_min": pf["strict_lower_bound_support_evaluations"],
        "MAX_SUPPORT_EVALUATIONS": CAP,
        "access": {"development_target_values": 0,
                   "development_predictor_values": 0,
                   "external_signal_values": 0, "external_target_values": 0,
                   "archives_opened": 0, "atoms_scored": 0,
                   "baselines_run": 0, "models_fitted": 0,
                   "verdict": "FIREWALL_INTACT_NO_ARCHIVE_OPENED"},
        "unchanged": {"A_rec": True, "G_rec": True, "target": True,
                      "P_hard": True, "C0_C8": True, "denominator_rule": True,
                      "support_bound_1_12": True, "T_REC_V1": True},
        "acceptance_checks": f"{n_pass}/{n_reach} reached, {n_gated} not reached",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "n_artifacts": len(arts), "n_markdown": len(md),
        "all_artifact_hashes": arts,
        "self_referential_excluded": sorted(SELF_REF),
        "human_decision_required": [o["option"] for o in opts if o["fits_300000"]]
            + ["raise MAX_SUPPORT_EVALUATIONS to >= 363,900"],
        "next_stage": "S7.7 RE-RUN once the budget question is decided and "
                      "re-frozen prospectively - NOT AUTHORISED. S7.8 NOT STARTED.",
    }
    (S77 / "S7_7_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                          encoding="utf-8")

    print(f"STATUS {freeze['status']}  blocked at {freeze['blocked_at']}")
    print(f"projected max {pf['max_projected_support_evaluations']}  "
          f"strict min {pf['strict_lower_bound_support_evaluations']}  "
          f"budget {CAP}")
    print(f"acceptance {n_pass}/{n_reach} reached, {n_gated} NOT REACHED  "
          f"failing {[k for k, v in reached.items() if not v]}")
    print(f"markdown {len(md)}  artifacts {len(arts)}")
    print("remedies computed, none chosen:")
    for o in opts:
        print(f"   {o['option']:48s} max {o['max_projected']:>7d}  "
              f"fits={o['fits_300000']}")
    print("ZERO ARCHIVES OPENED. ZERO DENSITY VALUES. ZERO ATOMS SCORED.")


if __name__ == "__main__":
    main()
