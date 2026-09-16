"""S7.8 step C - acceptance checks and freeze.

Self-referential files (the acceptance file and the freeze file itself) are
excluded from the hash manifest by construction: a file cannot contain its own
hash. This is the S7.2C C-09 discipline, inherited.
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

SELF_REFERENTIAL = ["S7_8_ACCEPTANCE_CHECKS.json", "S7_8_FREEZE.json"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(rel: str) -> dict:
    return json.loads((OUT / rel).read_text(encoding="utf-8"))


def main() -> int:
    pv = load("manifests/PARENT_FREEZE_VERIFICATION.json")
    aa = load("manifests/ACCESS_AUDIT.json")
    dr = load("manifests/ALGORITHM_DRY_RUN.json")
    cf = load("manifests/CARRY_FORWARD_FINDINGS.json")
    ob = load("manifests/OUTCOME_BASED_REVISION_AUDIT.json")
    u = load("U_REC_OPERATIONAL_V1.json")
    v = load("V_REC_OPERATIONAL_V1.json")
    pe = load("practical_equivalence_policy.json")
    est = load("estimator_policy.json")
    st = load("stability_metric_policy.json")
    cond = load("conditioning_policy.json")
    ss = load("support_stability_policy.json")
    alg = load("development_selection_algorithm.json")
    gso = load("gate_stage_ownership.json")

    fi = pv["frontier_integrity"]
    cfacts = pv["contract_facts"]
    md = sorted(p.name for p in OUT.glob("*.md"))

    checks = [
        ("all parent freezes verified", len(pv["lineage"]) == 13 and pv["verdict"] == "ZERO_SUBSTANTIVE_DRIFT"),
        ("S7.7R primary frontier authoritative",
         pv["s7_7r_manifest_recomputation"]["n_matched"] == pv["s7_7r_manifest_recomputation"]["n_recorded"]),
        ("Ahat_rec == 162845 supports", fi["registry_rows"] == 162845),
        ("singleton == 10778 and multivariate == 152067",
         fi["singleton_supports"] == 10778 and fi["multivariate_supports"] == 152067),
        ("support sizes == 1..12", fi["support_size_min"] == 1 and fi["support_size_max"] == 12),
        ("external values accessed = 0",
         aa["external_signal_values_opened"] == 0 and aa["external_target_values_opened"] == 0),
        ("no baseline run", aa["baselines_run"] == 0),
        ("no C* selected", aa["c_star_selected"] is False and u["s7_8_selected_a_candidate"] is False),
        ("S7.2C practical-equivalence correction authoritative",
         pe["authoritative_rule"]["delta_equiv"] == "max(SE_delta, 0.01)"
         and pe["superseded"]["status"] == "SUPERSEDED_BY_S7.2C_C01"),
        ("NRMSE units explicit", pe["authoritative_rule"]["units"] == "CALIBRATION-NORMALIZED RMSE units"
         and pe["authoritative_rule"]["raw_rmse_interpretation"] == "FORBIDDEN"),
        ("delta_equiv = max(SE_delta,0.01)", pe["floor"]["value"] == 0.01 and pe["floor"]["immutable"] is True),
        ("SE_delta uses paired development-discharge differences",
         pe["se_delta"]["n"] == 20 and pe["se_delta"]["ddof"] == 1),
        ("primary estimator frozen as OLS", est["estimator_id"] == "DEVELOPMENT_RELATION_OLS_V1"
         and est["ridge"]["primary_status"] == "NOT_PRIMARY_IN_S7_8"),
        ("intercept fitted", est["intercept"]["fitted"] is True),
        ("per-discharge/block local coefficients", est["coefficients"]["shared_across_discharges"] is False),
        ("utility ordering unchanged", [u["rank_1_fit"]["criterion"], u["rank_2_stability"]["criterion"],
                                        u["rank_3_parsimony"]["criterion"], u["rank_4_conditioning"]["criterion"],
                                        u["rank_5_support_stability"]["criterion"]]
         == ["primary fit quality", "development generalization / stability", "parsimony",
             "conditioning", "support stability"]),
        ("no weighted utility", u["no_weighted_sum"] is True and u["no_family_penalty"] is True),
        ("Rank-1 algorithm frozen", u["rank_1_fit"]["is_top_k"] is False),
        ("Rank-2 algorithm frozen", st["block_worst"]["equivalence"]["requires_discretion"] is False),
        ("Rank-2 fallback resolved without a new threshold",
         st["block_worst"]["equivalence"]["fallback_rule"]["status"] == "NOT_REQUIRED"
         and st["block_worst"]["equivalence"]["new_tunable_threshold_introduced"] is False),
        ("Rank-3 algorithm frozen",
         alg["parsimony_definition"]["active_terms"]["magnitude_threshold"] is None
         and alg["parsimony_definition"]["active_terms"]["intercept_counted"] is False),
        ("Rank-4 condition-number calculation frozen",
         cond["kappa"]["normal_equation_squared_condition_number"] == "FORBIDDEN"
         and cond["no_cutoff"]["arbitrary_condition_number_cutoff_introduced"] is False),
        ("Rank-5 resampling protocol frozen", ss["modifies_ahat_rec"] is False and ss["reruns_search"] is False),
        ("bootstrap seed/count frozen",
         ss["discharge_bootstrap"]["replicates"] == 1000 and ss["discharge_bootstrap"]["seed"] == 2026090501),
        ("fold perturbations frozen", ss["fold_perturbation"]["n_perturbations"] == 3),
        ("no stability pass/fail threshold", ss["pass_fail_threshold"]["introduced"] is False),
        ("S7.9 deterministic selection algorithm frozen",
         [s["set"] for s in alg["stages"]] == ["E0", "E1", "E2", "E3", "E4", "E5"]
         and alg["executed_in_s7_8"] is False),
        ("C6/C7 not pruned", cf["c6_c7"]["declaration"] == "NO_CONSTRUCTOR_FAMILY_PRUNING"
         and cf["c6_c7"]["c6_c7_removed_from_ahat_rec"] is False),
        ("ECE not penalized", cf["ece_dominance"]["penalty_introduced"] is False
         and cf["ece_dominance"]["family_balancing_in_u_rec"] is False),
        ("uncalibrated primitives not silently removed",
         cf["uncalibrated_primitives"]["status_in_ahat_rec"] == "VALID if already present; NOT REMOVED"),
        ("V1-V10 stage ownership explicit", len(v["gates"]) == 10),
        ("V3 not evaluated", next(g for g in v["gates"] if g["gate"] == "V3")["current_status"] == "PENDING_S7.10"),
        ("V4 not evaluated", next(g for g in v["gates"] if g["gate"] == "V4")["current_status"] == "PENDING_S7.10"),
        ("V5 not evaluated", next(g for g in v["gates"] if g["gate"] == "V5")["current_status"] == "PENDING_S7.10"),
        ("V6 uses external 24/18", cfacts["v6_external_counts_authoritative"] == {"earlier": 24, "later": 18, "total": 42}
         and v["external_cohort"]["earlier"] == 24 and v["external_cohort"]["later"] == 18),
        ("V9 remains non-mandatory", v["non_mandatory_gates"] == ["V9"]),
        ("no external gate marked PASS", gso["no_external_gate_marked_pass"] is True
         and all(g["current_status"] in gso["allowed_states_at_s7_8"] for g in gso["gates"])),
        ("baselines defined but not run", all(b["status"] == "NOT_RUN" for b in v["baselines"].values())),
        ("S_pers not used for selection",
         v["baseline_notes"]["S_pers"].endswith("does NOT guide S7.9 selection")),
        ("two-seed sensitivity not executed",
         cf["search_depth_sensitivity"]["status"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"]
         and cf["search_depth_sensitivity"]["executed_in_s7_8"] is False),
        ("no global-optimum claim", u["global_optimality_claim"] is False and v["global_optimality_claim"] is False),
        ("A_rec minus Ahat_rec remains admissible-unsearched",
         cf["search_boundary"]["unsearched_status"] == "ADMISSIBLE_UNSEARCHED"
         and cf["search_boundary"]["negative_conclusion_attached_to_unsearched"] is False),
        ("no outcome-based utility revision", ob["verdict"] == "NO_OUTCOME_BASED_REVISION"
         and ob["conflicts_found"] == 0),
        ("canonical parse checksum verified",
         fi["canonical_id"]["depth_aware_split_reproduces_support_size"] is True),
        ("algorithm proven executable and deterministic",
         dr["verdict"] == "ALGORITHM_EXECUTABLE_AND_DETERMINISTIC"
         and dr["ahat_rec_nrmse_values_read"] is False),
        ("stage semantics preserved: S7.9 not moved into S7.8", gso["s7_9_not_moved_into_s7_8"] is True),
        ("Markdown files <= 20", len(md) <= 20),
        ("S7.9 not started", aa["s7_9_started"] is False and aa["final_support_frozen"] is False),
    ]

    passed = sum(1 for _, ok in checks if ok)
    failed = [name for name, ok in checks if not ok]

    acc = {
        "acceptance_id": "S7_8_ACCEPTANCE_CHECKS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_checks": len(checks),
        "n_passed": passed,
        "result": "%d/%d" % (passed, len(checks)),
        "failed": failed,
        "checks": [{"check": n, "passed": bool(ok)} for n, ok in checks],
    }
    (OUT / "S7_8_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    # ---- hash manifest ---------------------------------------------------
    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF_REFERENTIAL:
            continue
        if "__pycache__" in rel:
            continue
        hashes[rel] = sha256(p)

    status = "FROZEN_READY_FOR_S7.9" if not failed else "BLOCKED_UTILITY_SPECIFICATION"

    freeze = {
        "freeze_id": "D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1",
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.8 - utility and qualification rule operationalization",
        "parent_freeze_id": "D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2",
        "parent_contract_freeze_ids": u["parent_contract"],
        "selection_domain": u["selection_domain"],
        "selection_domain_cardinality": 162845,
        "global_optimality_claim": False,
        "utility_id": u["utility_id"],
        "qualification_id": v["qualification_id"],
        "primary_estimator": est["estimator_id"],
        "what_s7_8_did_not_do": {
            "selected_C_star": False,
            "opened_external_signal_values": False,
            "opened_external_target_values": False,
            "ran_any_baseline": False,
            "computed_utility_over_ahat_rec": False,
            "modified_ahat_rec": False,
            "modified_A_rec": False,
            "modified_G_rec": False,
            "reran_s7_7": False,
            "executed_two_seed_sensitivity": False,
            "froze_the_final_support": False,
            "started_s7_9": False,
        },
        "operational_resolutions": {
            "OR-01": "canonical support id parsed at parenthesis depth 0; registry support_size is the mandatory checksum",
            "OR-02": "E_fit is pairwise against the Rank-1 best, not a transitive class",
            "OR-03": "BLOCK_WORST paired SE uses each candidate's own worst block; identity verified; the 0.01-only fallback is NOT_REQUIRED",
            "OR-04": "percentile estimator frozen as numpy.percentile method='linear'",
            "OR-05": "ACTIVE_TERMS counts columns non-zero in at least one of the 60 calibration fits",
            "OR-06": "conditioning rows are the cell calibration rows; standardization makes centred and standardized readings coincide",
            "OR-07": "kappa from SVD, never the normal-equation square; sigma_min == 0 gives +inf",
            "OR-08": "Rank-4 winner is the canonical-first element of E4",
            "OR-09": "bootstrap multiplicities weight every discharge-level aggregation; blocks are never resampled",
            "OR-10": "fold perturbation aggregates over the two remaining blocks, 40 cells",
            "OR-11": "a non-finite cell gives FIT = +inf and exclusion from E_fit, never inadmissibility",
            "OR-12": "the 1000-replicate Rank-5 bootstrap is distinct from the >=10000-replicate S7.10 gate-inference bootstrap; both stand",
        },
        "qualifications": [
            "The Rank-2 BLOCK_WORST practical-equivalence rule required an operational paired-SE definition. A discretion-free one was found and verified (mean_s d_s = BLOCK_WORST(A) - BLOCK_WORST(B) exactly, max deviation 2.67e-16), so the instruction's permitted fallback to a 0.01-only floor was NOT invoked and no new tunable threshold was introduced.",
            "The canonical support_id cannot be parsed by splitting on the pipe character: C4/C6/C7/C8 signatures embed a pipe inside their own parentheses and a naive split mis-parses 116608 of 162845 rows (71.6 percent). A depth-aware parse plus a mandatory support_size checksum is frozen. S7.9 must run the checksum before computing anything.",
            "ACTIVE_TERMS required a candidate-level aggregation rule because OLS coefficients are discharge/block local. The union rule (non-zero in at least one of the 60 calibration fits) was frozen as the conservative, threshold-free reading; under full-rank OLS it is expected to be non-binding.",
            "Executability was demonstrated on a synthetic fixture rather than on Ahat_rec, so that S7.8 could prove the algorithm runs without performing any part of the S7.9 computation.",
        ],
        "parent_verification_sha256": sha256(OUT / "manifests" / "PARENT_FREEZE_VERIFICATION.json"),
        "u_rec_operational_sha256": sha256(OUT / "U_REC_OPERATIONAL_V1.json"),
        "v_rec_operational_sha256": sha256(OUT / "V_REC_OPERATIONAL_V1.json"),
        "estimator_policy_sha256": sha256(OUT / "estimator_policy.json"),
        "practical_equivalence_policy_sha256": sha256(OUT / "practical_equivalence_policy.json"),
        "stability_metric_policy_sha256": sha256(OUT / "stability_metric_policy.json"),
        "conditioning_policy_sha256": sha256(OUT / "conditioning_policy.json"),
        "support_stability_policy_sha256": sha256(OUT / "support_stability_policy.json"),
        "development_selection_algorithm_sha256": sha256(OUT / "development_selection_algorithm.json"),
        "gate_stage_ownership_sha256": sha256(OUT / "gate_stage_ownership.json"),
        "acceptance_checks_sha256": sha256(OUT / "S7_8_ACCEPTANCE_CHECKS.json"),
        "manuscript_section_sha256": sha256(OUT / "S7_8_UTILITY_AND_QUALIFICATION_RULES_FINAL.md"),
        "audit_report_sha256": sha256(OUT / "S7_8_UTILITY_AND_QUALIFICATION_AUDIT_REPORT.md"),
        "acceptance_checks": acc["result"],
        "acceptance_failed": failed,
        "n_artifacts": len(hashes),
        "n_markdown": len(md),
        "markdown_limit": 20,
        "markdown_files": md,
        "all_artifact_hashes": hashes,
        "self_referential_excluded": SELF_REFERENTIAL,
        "hash_method": "sha256 over raw file bytes; self-referential files excluded by construction",
        "access": {
            "development_frontier_read": "shape, finiteness and identity only",
            "utility_computed_over_ahat_rec": False,
            "external_signal_values": 0,
            "external_target_values": 0,
            "baselines_run": 0,
            "verdict": "FIREWALL_INTACT",
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
        },
        "next_stage": "S7.9 (development selection and representation freeze) - NOT AUTHORISED",
    }
    (OUT / "S7_8_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("acceptance checks : %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("artifacts hashed  : %d" % len(hashes))
    print("markdown files    : %d (limit 20)" % len(md))
    print("status            : %s" % status)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
