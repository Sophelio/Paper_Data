"""S7.7R stage A - lineage, carry-forward, one-constant policy diff, preflight.

METADATA ONLY. THIS SCRIPT OPENS NO ARCHIVE AND READS NO SIGNAL OR TARGET VALUE.

It verifies the twelve lineage records, carries the stage-A pre-search contract
forward unchanged by hash, snapshots historical S7.7 V1 so stage C can prove it
was never touched, writes the COMPLETE V2 search policy (not a patch), proves by
machine-readable diff that the only substantive change is the seed multiplicity
2 -> 1, and recomputes the metadata-only budget projection.

Only after the V2 policy hash exists may any density value be opened.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
V2 = HERE.parent                                  # one_seed_primary_v2
S77 = V2.parent                                   # 07_search_policy_and_frontier
S7 = S77.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
S74 = S7 / "04_mathematical_interpretation"
RV2 = S74 / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76 = S7 / "06_admissible_universe"
S76R = S76 / "hardened_v2"
MAN = V2 / "manifests"

DENOM_RULE_SHA = ("6d4004eb3ae95067b2a01dddeb90226748cfee7097217d68ab5377ac"
                  "50ed716d")
PRE_CONTRACT_SHA = ("1b8df4c0672686be21665c00aaf4fc8f36ab9e53")   # prefix check
SEEDS_PER_STRATUM_V1 = 2
SEEDS_PER_STRATUM_V2 = 1
MAX_SUPPORT_EVALUATIONS = 300000
MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION = 96
SUPPORT_MAX = 12
ACTIVE_CONSTRUCTORS = ["C0", "C1", "C2", "C3", "C5", "C6", "C7"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_parents() -> dict:
    frz = {
        "s7_1": json.loads((R1 / "S7_1_FINAL_FREEZE.json").read_text()),
        "s7_2_v1": json.loads((S72 / "S7_2_FREEZE.json").read_text()),
        "s7_2_v2": json.loads((CV1 / "S7_2_FREEZE_V2.json").read_text()),
        "s7_3_v1": json.loads((S73 / "S7_3_FREEZE.json").read_text()),
        "s7_4_v1": json.loads((S74 / "S7_4_FREEZE.json").read_text()),
        "s7_3r_v2": json.loads((RSR / "S7_3_FREEZE_V2.json").read_text()),
        "s7_4_v2": json.loads((RV2 / "S7_4_FREEZE_V2.json").read_text()),
        "s7_5": json.loads((S75 / "S7_5_FREEZE.json").read_text()),
        "s7_5h": json.loads((S75H / "S7_5H_FREEZE.json").read_text()),
        "s7_6_v1_historical": json.loads((S76 / "S7_6_FREEZE.json").read_text()),
        "s7_6r_v2": json.loads((S76R / "S7_6R_FREEZE.json").read_text()),
        "s7_7_v1_blocked": json.loads((S77 / "S7_7_FREEZE.json").read_text()),
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json",
            "S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json",
            "S7_5_ACCEPTANCE_CHECKS.json", "S7_5_FREEZE.json",
            "S7_5H_ACCEPTANCE_CHECKS.json", "S7_5H_FREEZE.json",
            "S7_6_ACCEPTANCE_CHECKS.json", "S7_6_FREEZE.json",
            "S7_6R_ACCEPTANCE_CHECKS.json", "S7_6R_FREEZE.json",
            "S7_7_ACCEPTANCE_CHECKS.json", "S7_7_FREEZE.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73, "s7_4_v1": S74,
             "s7_3r_v2": RSR, "s7_4_v2": RV2, "s7_5": S75, "s7_5h": S75H,
             "s7_6_v1_historical": S76, "s7_6r_v2": S76R, "s7_7_v1_blocked": S77}

    s71v = json.loads((S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json").read_text())
    s71map = {"signal_inventory_sha256": R1 / "FINAL_SIGNAL_INVENTORY.csv",
              "shot_inventory_sha256": R1 / "FINAL_SHOT_INVENTORY.csv",
              "units_registry_sha256": S7 / "SIGNAL_UNITS.json",
              "provenance_graph_sha256": R1 / "provenance_graph.json",
              "dalia_parity_sha256": R1 / "DALIA_SIGNAL_PARITY.csv",
              "temporal_lineage_sha256": R1 / "FINAL_TEMPORAL_LINEAGE.csv",
              "equilibrium_lineage_sha256": R1 / "equilibrium_lineage_status.csv",
              "source_inventory_sha256": R1 / "SOURCE_ARTIFACT_INVENTORY.csv",
              "quality_summary_sha256": R1 / "signal_quality_summary.csv"}
    drift = [{"parent": "s7_1", "artifact": k} for k, p in s71map.items()
             if sha(p) != s71v["canonical_raw_byte_hashes"][k]]
    out = {"s7_1": {"freeze_id": frz["s7_1"]["freeze_id"],
                    "n_verified": sum(1 for k, p in s71map.items()
                                      if sha(p) == s71v["canonical_raw_byte_hashes"][k])}}
    for k, base in bases.items():
        n = 0
        for rel, h in frz[k]["all_artifact_hashes"].items():
            if Path(rel).name in SELF:
                continue
            p = base / rel
            if not p.exists() or sha(p) != h:
                drift.append({"parent": k, "artifact": rel})
            else:
                n += 1
        out[k] = {"freeze_id": frz[k]["freeze_id"],
                  "status": frz[k].get("status", ""), "n_verified": n}

    A = json.loads((S76R / "A_REC_HARDENED.json").read_text())
    U = json.loads((S76R / "atomic_coordinate_universe.json").read_text())
    G = json.loads((S75H / "G_REC_HARDENED.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    strata = pd.read_csv(S77 / "search_strata.csv")
    sub = {
        "target_is_density": A["target"] == "density",
        "A_REC_DENSITY_HARDENED_V2_authoritative":
            A["universe_id"] == "A_REC_DENSITY_HARDENED_V2",
        "atomic_universe_10778": U["n_atoms"] == 10778,
        "active_strata_127": int(len(strata)) == 127,
        "support_bound_1_12": K["B_rec"]["representation_size_range"] == [1, 12],
        "C4_admissible_zero": U["by_constructor"]["C4"] == 0,
        "C8_admissible_zero": U["by_constructor"]["C8"] == 0,
        "denominator_rule_unchanged":
            sha(S76 / "denominator_admissibility_rule.json") == DENOM_RULE_SHA,
        "T_REC_V1_unchanged": A["R_rec"].startswith("T_REC_V1"),
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "ontology_is_G_REC_DENSITY_HARDENED_V2":
            G["ontology_id"] == "G_REC_DENSITY_HARDENED_V2",
        "P_hard_70": G["operand_counts"]["M"] == 70,
        "historical_s7_7_v1_blocked":
            frz["s7_7_v1_blocked"]["status"] == "BLOCKED_SEARCH_BUDGET",
        "historical_s7_7_v1_Ahat_not_constructed":
            frz["s7_7_v1_blocked"]["Ahat_rec_state"] == "NOT_CONSTRUCTED",
        "historical_s7_7_v1_opened_nothing":
            frz["s7_7_v1_blocked"]["access"]["archives_opened"] == 0
            and frz["s7_7_v1_blocked"]["access"]["atoms_scored"] == 0,
        "search_priority_not_yet_assigned": A["search_priority_assigned"] is False,
        "estimator_not_yet_run": A["estimator_run"] is False,
        "s7_7r_never_previously_run": not (V2 / "S7_7R_FREEZE.json").exists(),
    }
    out.update({"verified_utc": datetime.now(timezone.utc).isoformat(),
                "substantive_checks": sub, "n_drift": len(drift), "drift": drift,
                "verdict": ("PARENTS_VERIFIED" if not drift and all(sub.values())
                            else "STOP_PARENT_DRIFT")})
    return out


def historical_v1_snapshot() -> dict:
    files = sorted(p for p in S77.iterdir() if p.is_file())
    for d in ("manifests", "scripts"):
        files += sorted(p for p in (S77 / d).glob("*") if p.is_file())
    snap = {str(p.relative_to(S77)).replace("\\", "/"): sha(p) for p in files}
    f = json.loads((S77 / "S7_7_FREEZE.json").read_text())
    return {
        "freeze_id": f["freeze_id"], "status": f["status"],
        "status_assigned_here": "BLOCKED_SEARCH_BUDGET",
        "role_here": "PRESERVED_AS_AUDIT_HISTORY",
        "sigma_rec_state_v1": f["sigma_rec_state"],
        "Ahat_rec_state_v1": f["Ahat_rec_state"],
        "v1_opened": f["access"],
        "why_no_contamination": (
            "historical S7.7 V1 opened no archive, scored no atom, ran no "
            "baseline and constructed no frontier. It contains no "
            "target-dependent information of any kind, so nothing it recorded "
            "can bias the one-seed policy frozen here."),
        "byte_snapshot_taken_utc": datetime.now(timezone.utc).isoformat(),
        "n_files_snapshotted": len(snap), "byte_snapshot": snap,
    }


def build_v2_policy(strata: pd.DataFrame, v1: dict, pre_sha: str) -> dict:
    """The COMPLETE policy, not a patch. Identical to V1 except seeds."""
    pol = json.loads(json.dumps(v1))          # deep copy of the V1 policy
    pol["policy_id"] = "SIGMA_REC_PREVALUE_V2_ONE_SEED"
    pol["supersedes"] = v1["policy_id"]
    pol["supersedes_for_primary_use"] = True
    pol["frozen_utc"] = datetime.now(timezone.utc).isoformat()
    pol["pre_search_contract_sha256"] = pre_sha

    seeds_main = int(strata.n_atoms.clip(upper=SEEDS_PER_STRATUM_V2).sum())
    c0 = strata[strata.constructor == "C0"]
    seeds_raw = int(c0.n_atoms.clip(upper=SEEDS_PER_STRATUM_V2).sum())

    pol["SEEDS_PER_STRATUM"] = SEEDS_PER_STRATUM_V2
    pol["s14_greedy_search"]["seeds"] = (
        "top 1 atom by within-stratum rank per active stratum")
    pol["s14_greedy_search"]["n_seeds_projected"] = seeds_main
    pol["s14_greedy_search"]["seed_rank_deficient_handling"] = (
        "if the only atom in a stratum has +infinity navigation score it is "
        "retained as the formal seed and flagged SEED_PROXY_RANK_DEFICIENT; "
        "normal path rules then determine whether useful extension is possible")
    pol["s15_raw_only_lane"]["seeds"] = (
        "top one C0 atom per nonempty scientific family")
    pol["s15_raw_only_lane"]["n_seeds_projected"] = seeds_raw

    pol["s6_primary_vs_sensitivity"] = {
        "ONE_SEED_SEARCH": "PRIMARY",
        "TWO_SEED_SEARCH": ["NOT_EXECUTED",
                            "OPTIONAL_FUTURE_SEARCH_DEPTH_SENSITIVITY"],
        "decided_by": "prospective human decision, before any density value",
        "reason": "computational economy while retaining one independent "
                  "starting path for every active stratum",
        "a_future_two_seed_analysis": {
            "may": ["test search robustness",
                    "show whether a larger exploration frontier changes "
                    "conclusions"],
            "must": ["preserve the present primary one-seed result"],
            "may_not": [
                "retroactively become the primary result merely because it "
                "finds a better representation",
                "convert a failed primary q_rec into a successful primary "
                "structural-transfer claim",
                "replace, rescue, redefine or retroactively optimize the "
                "primary one-seed result"]},
        "outcome_trigger_defined": False,
        "outcome_trigger_forbidden_example":
            "'run if the primary result is bad' - forbidden; if later "
            "authorised it is a sensitivity REGARDLESS of the primary result",
        "recorded_before_density_access": True,
        "price_accepted_prospectively":
            "broad in scientific opportunity, shallower in multi-start depth; "
            "reduced protection against greedy-start sensitivity. No stratum "
            "was removed to meet the budget.",
    }
    return pol


def diff_policies(v1: dict, v2: dict) -> dict:
    """Flatten both policies and require the only substantive diffs to be seeds."""
    def flat(d, pre=""):
        out = {}
        if isinstance(d, dict):
            for k, v in d.items():
                out.update(flat(v, f"{pre}.{k}" if pre else k))
        elif isinstance(d, list):
            out[pre] = json.dumps(d)
        else:
            out[pre] = d
        return out

    # non-substantive provenance/bookkeeping fields, plus the one authorised
    # substantive constant
    IGNORE = {"policy_id", "frozen_utc", "supersedes",
              "supersedes_for_primary_use", "parent_policy_sha256",
              "SEEDS_PER_STRATUM"}
    ALLOWED_PREFIX = ("s14_greedy_search.seeds",
                      "s14_greedy_search.n_seeds_projected",
                      "s14_greedy_search.seed_rank_deficient_handling",
                      "s15_raw_only_lane.seeds",
                      "s15_raw_only_lane.n_seeds_projected",
                      "s6_primary_vs_sensitivity")
    a, b = flat(v1), flat(v2)
    keys = sorted(set(a) | set(b))
    changed, added, removed, unauthorised = [], [], [], []
    for k in keys:
        top = k.split(".")[0]
        allowed = top in IGNORE or k.startswith(ALLOWED_PREFIX)
        if k not in a:
            added.append(k)
            if not allowed:
                unauthorised.append({"field": k, "change": "added",
                                     "v2": b[k]})
        elif k not in b:
            removed.append(k)
            if not allowed:
                unauthorised.append({"field": k, "change": "removed",
                                     "v1": a[k]})
        elif a[k] != b[k]:
            changed.append({"field": k, "v1": a[k], "v2": b[k],
                            "authorised": allowed})
            if not allowed:
                unauthorised.append({"field": k, "change": "modified",
                                     "v1": a[k], "v2": b[k]})
    return {
        "diff_id": "SEARCH_POLICY_DIFF_V1_TO_V2",
        "n_fields_compared": len(keys),
        "n_changed": len(changed), "n_added": len(added),
        "n_removed": len(removed),
        "substantive_change": {"SEEDS_PER_STRATUM": f"{SEEDS_PER_STRATUM_V1} -> "
                                                    f"{SEEDS_PER_STRATUM_V2}",
                               "raw_only_lane_seeds": "2 -> 1 per C0 family"},
        "unchanged_and_verified": {
            "MAX_SUPPORT_EVALUATIONS": v2["s13_budget_interpretation"] and
                MAX_SUPPORT_EVALUATIONS,
            "MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION":
                v2["s12_shortlist"]["MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION"],
            "support_size_range": [1, SUPPORT_MAX],
            "atoms_scored_univariately": v2["s10_atomic_scoring"]["n_expected"],
            "n_active_strata": v2["s6_search_strata"]["n_active_strata"],
            "signatures": v2["s6_search_strata"]["signatures"],
            "SEARCH_PROXY_OLS_V1": v2["s7_search_proxy"]["id"],
            "J_search": v2["s8_navigation_score"]["definition"],
            "greedy_proposal_rule": v2["s14_greedy_search"]["proposal_rule"],
            "Phi_set": v2["unchanged_from_parents"]["Phi_set"]},
        "changed_fields": changed,
        "added_fields": added, "removed_fields": removed,
        "unauthorised_changes": unauthorised,
        "verdict": ("ONLY_SEED_MULTIPLICITY_CHANGED" if not unauthorised
                    else "UNAUTHORISED_SEARCH_POLICY_DRIFT"),
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"] != "PARENTS_VERIFIED":
        print(json.dumps(par["drift"][:10], indent=1))
        print([k for k, v in par["substantive_checks"].items() if not v])
        raise SystemExit("STOP: parent drift")

    hist = historical_v1_snapshot()
    (MAN / "HISTORICAL_S7_7_V1_RECORD.json").write_text(
        json.dumps(hist, indent=2), encoding="utf-8")

    # ---- 4. pre-search contract carried forward unchanged -----------------
    pc = S77 / "PRE_SEARCH_CONTRACT_COMPLETION.json"
    pc_sha = sha(pc)
    pc_ok = pc_sha.startswith(PRE_CONTRACT_SHA[:8])
    pcj = json.loads(pc.read_text())
    carry = {
        "file": "../PRE_SEARCH_CONTRACT_COMPLETION.json",
        "sha256": pc_sha, "expected_prefix": PRE_CONTRACT_SHA[:8],
        "hash_verified_unchanged": pc_ok,
        "regenerated": False, "modified": False,
        "S_PERS_V1": {"present": "S_PERS" in pcj,
                      "status": pcj["S_PERS"]["status"],
                      "used_for_search": pcj["S_PERS"]["may_guide_S7_7_search"],
                      "replaces_NRMSE": pcj["S_PERS"]["does_not_replace_frozen_NRMSE"]
                      is False,
                      "changes_V3": pcj["S_PERS"]["does_not_change_V3"] is False},
        "B1A_AR1": {"present": "B1A_AR1" in pcj,
                    "status": pcj["B1A_AR1"]["status"],
                    "run_here": pcj["B1A_AR1"]["run_in_S7_7"]},
        "neither_run": True,
    }
    (MAN / "PRE_SEARCH_CONTRACT_CARRY_FORWARD.json").write_text(
        json.dumps(carry, indent=2), encoding="utf-8")
    if not pc_ok:
        raise SystemExit("STOP: pre-search contract hash changed")

    # ---- 5/7. complete V2 policy + diff ------------------------------------
    strata = pd.read_csv(S77 / "search_strata.csv")
    strata.to_csv(V2 / "search_strata.csv", index=False)
    v1pol = json.loads((S77 / "SEARCH_POLICY_PREVALUE.json").read_text())
    v1_sha = sha(S77 / "SEARCH_POLICY_PREVALUE.json")
    v2pol = build_v2_policy(strata, v1pol, pc_sha)
    v2pol["parent_policy_sha256"] = v1_sha
    p2 = V2 / "SEARCH_POLICY_PREVALUE_V2.json"
    p2.write_text(json.dumps(v2pol, indent=2), encoding="utf-8")
    v2_sha = sha(p2)

    dif = diff_policies(v1pol, v2pol)
    dif["v1_policy_sha256"] = v1_sha
    dif["v2_policy_sha256"] = v2_sha
    (MAN / "SEARCH_POLICY_DIFF.json").write_text(json.dumps(dif, indent=2),
                                                 encoding="utf-8")
    if dif["verdict"] != "ONLY_SEED_MULTIPLICITY_CHANGED":
        print(json.dumps(dif["unauthorised_changes"], indent=1))
        raise SystemExit("STOP: UNAUTHORISED_SEARCH_POLICY_DRIFT")

    # ---- 8. budget preflight ----------------------------------------------
    n_strata = int(len(strata))
    per_constructor = {c: int((strata.constructor == c).sum())
                       for c in ACTIVE_CONSTRUCTORS}
    atoms_per_constructor = {c: int(strata.loc[strata.constructor == c,
                                               "n_atoms"].sum())
                             for c in ACTIVE_CONSTRUCTORS}
    shortlist = {c: min(atoms_per_constructor[c],
                        MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION)
                 for c in ACTIVE_CONSTRUCTORS}
    insufficient = {c: per_constructor[c] for c in ACTIVE_CONSTRUCTORS
                    if per_constructor[c] > shortlist[c]}
    seeds_main = int(strata.n_atoms.clip(upper=SEEDS_PER_STRATUM_V2).sum())
    c0 = strata[strata.constructor == "C0"]
    seeds_raw = int(c0.n_atoms.clip(upper=SEEDS_PER_STRATUM_V2).sum())
    n_raw_str = int(len(c0))
    steps = SUPPORT_MAX - 1
    atomic = int(strata.n_atoms.sum())
    main_max = seeds_main * steps * n_strata
    raw_max = seeds_raw * steps * n_raw_str
    proj = atomic + main_max + raw_max
    within = proj <= MAX_SUPPORT_EVALUATIONS

    pf = {
        "record_id": "SEARCH_BUDGET_PREFLIGHT_V2",
        "computed_from": "METADATA_ONLY", "no_density_value_opened": True,
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
        "search_policy_v2_sha256": v2_sha,
        "MAX_SUPPORT_EVALUATIONS": MAX_SUPPORT_EVALUATIONS,
        "SEEDS_PER_STRATUM": SEEDS_PER_STRATUM_V2,
        "active_stratum_count": n_strata,
        "strata_per_constructor": per_constructor,
        "atoms_per_constructor": atoms_per_constructor,
        "expansion_shortlist_count": shortlist,
        "expansion_shortlist_total": int(sum(shortlist.values())),
        "strata_represented_in_shortlist": n_strata,
        "every_nonempty_stratum_gets_a_slot": not insufficient,
        "atomic_scoring_evaluations": atomic,
        "main_lane": {"n_seeds": seeds_main, "growth_steps": steps,
                      "proposals_per_step_max": n_strata,
                      "evaluations_max": main_max,
                      "arithmetic": f"{seeds_main} x {steps} x {n_strata} = "
                                    f"{main_max}"},
        "raw_only_lane": {"n_seeds": seeds_raw, "growth_steps": steps,
                          "proposals_per_step_max": n_raw_str,
                          "evaluations_max": raw_max,
                          "arithmetic": f"{seeds_raw} x {steps} x {n_raw_str} = "
                                        f"{raw_max}"},
        "max_projected_support_evaluations": proj,
        "expected_from_instruction": 188736,
        "matches_expected": proj == 188736,
        "within_budget": within,
        "headroom": MAX_SUPPORT_EVALUATIONS - proj,
        "policy_truncated_to_fit": False, "policy_changed_to_fit": False,
        "verdict": "SEARCH_BUDGET_OK" if within
                   else "SEARCH_BUDGET_REQUIRES_HUMAN_REVIEW",
    }
    (V2 / "SEARCH_BUDGET_PREFLIGHT_V2.json").write_text(json.dumps(pf, indent=2),
                                                        encoding="utf-8")
    (MAN / "POLICY_FREEZE_V2.json").write_text(json.dumps({
        "file": "SEARCH_POLICY_PREVALUE_V2.json", "sha256": v2_sha,
        "frozen_utc": v2pol["frozen_utc"],
        "parent_v1_policy_sha256": v1_sha,
        "pre_search_contract_sha256": pc_sha,
        "diff_verdict": dif["verdict"],
        "frozen_before_any_density_value_opened": True,
        "stage_a_opens_no_archive": True,
        "ordering_is_structural": "stage A contains no data-loading code path; "
                                  "the search stage verifies this hash before "
                                  "opening anything",
        "on_mismatch": "SEARCH_POLICY_CONTAMINATED"}, indent=2),
        encoding="utf-8")

    print(f"parents        : {par['verdict']}  drift {par['n_drift']}")
    print(f"historical V1  : {hist['status']} / {hist['role_here']} "
          f"({hist['n_files_snapshotted']} files snapshotted)")
    print(f"pre-contract   : carried forward unchanged  sha {pc_sha[:16]}")
    print(f"policy diff    : {dif['verdict']}  "
          f"({dif['n_changed']} changed, {dif['n_added']} added, "
          f"{dif['n_removed']} removed, {len(dif['unauthorised_changes'])} "
          f"unauthorised)")
    print(f"policy V2      : sha {v2_sha[:16]}  frozen {v2pol['frozen_utc']}")
    print(f"budget         : atomic {atomic} + main {main_max} + raw {raw_max} "
          f"= {proj}  (expected 188736: {pf['matches_expected']})")
    print(f"                 budget {MAX_SUPPORT_EVALUATIONS}  headroom "
          f"{pf['headroom']}  VERDICT {pf['verdict']}")
    print("NO ARCHIVE OPENED IN STAGE A.  NO DENSITY VALUE OPENED.")
    if not within:
        raise SystemExit("STOP: budget")


if __name__ == "__main__":
    main()
