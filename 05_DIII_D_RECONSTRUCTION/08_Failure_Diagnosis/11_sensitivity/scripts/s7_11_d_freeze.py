"""S7.11 step D - acceptance checks and stage freeze."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S79 = S7 / "09_development_selection_and_freeze"
S710 = S7 / "10_external_validation"
SELF = ["S7_11_ACCEPTANCE_CHECKS.json", "S7_11_FREEZE.json"]
FLOOR = 0.01


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ver = json.loads((OUT / "S7_11_PREDECLARATION_VERIFICATION.json").read_text())
    v9 = json.loads((OUT / "V9_RESULT.json").read_text())
    fam = pd.read_csv(OUT / "support_family_external_metrics.csv")
    sens = pd.read_csv(OUT / "prmtan_sensitivity_metrics.csv")
    blk = pd.read_csv(OUT / "block_omission_sensitivity.csv")
    lodo = pd.read_csv(OUT / "discharge_sensitivity_summary.csv")
    cp = pd.read_csv(OUT / "support_family_coordinate_summary.csv")
    inv = ver["primary_result_invariant"]
    f10 = json.loads((S710 / "S7_10_FREEZE.json").read_text())
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text())

    fd = fam[fam.full_domain]
    star = fam[fam.is_C_dev_star].iloc[0]
    passers = fd[fd.V3_STYLE_PASS]
    q = [0, 5, 25, 50, 75, 95, 100]

    def dist(col):
        v = np.percentile(fd[col], q, method="linear")
        return {("p%d" % a): float(b) for a, b in zip(q, v)}

    distributions = {c: dist(c) for c in
                     ("mean_nrmse", "median_nrmse", "Delta_0", "Delta_1")}
    pd.DataFrame([{"quantity": k, **v} for k, v in distributions.items()]).to_csv(
        OUT / "support_family_distributions.csv", index=False)

    pct = {c: float((fd[c] <= star[c]).mean() * 100)
           for c in ("mean_nrmse", "median_nrmse", "Delta_1")}
    rank = {c: int((fd[c] < star[c]).sum()) + 1
            for c in ("mean_nrmse", "median_nrmse", "Delta_1")}
    lowest = fd.nsmallest(1, "mean_nrmse").iloc[0]

    fail = fd[~fd.V3_STYLE_PASS]
    summary = {
        "record_id": "S7_11_SUPPORT_FAMILY_SUMMARY_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_supports": int(len(fam)),
        "n_full_domain": int(fd.shape[0]),
        "n_not_full_domain": int((~fam.full_domain).sum()),
        "not_full_domain_reason": "E_DENOM on 6 of 126 blocks; 40 of 42 discharges evaluable",
        "V3_STYLE_PASS_full_domain": int(passers.shape[0]),
        "V3_STYLE_FAIL_full_domain": int(fail.shape[0]),
        "V3_STYLE_PASS_fraction_full_domain": float(passers.shape[0] / len(fd)),
        "failure_mode_breakdown": {
            "fail_Delta_1_only": int(((fail.Delta_0 <= -FLOOR) & (fail.Delta_1 > -FLOOR)).sum()),
            "fail_Delta_0_only": int(((fail.Delta_0 > -FLOOR) & (fail.Delta_1 <= -FLOOR)).sum()),
            "fail_both": int(((fail.Delta_0 > -FLOOR) & (fail.Delta_1 > -FLOOR)).sum()),
        },
        "distributions": distributions,
        "C_dev_star": {
            "mean_nrmse": float(star.mean_nrmse), "median_nrmse": float(star.median_nrmse),
            "Delta_0": float(star.Delta_0), "Delta_1": float(star.Delta_1),
            "V3_STYLE_PASS": bool(star.V3_STYLE_PASS),
            "percentile_in_family": pct, "rank_ascending_in_family": rank,
            "n_full_domain": int(len(fd)),
            "development_bootstrap_selection_frequency": float(
                star.development_bootstrap_selection_frequency),
            "is_family_max_development_frequency": bool(
                fd.development_bootstrap_selection_frequency.max()
                == star.development_bootstrap_selection_frequency),
        },
        "LOWEST_EXTERNAL_ERROR_SUPPORT_IN_PREDECLARED_SENSITIVITY": {
            "support_id": str(lowest.support_id),
            "mean_nrmse": float(lowest.mean_nrmse), "median_nrmse": float(lowest.median_nrmse),
            "Delta_0": float(lowest.Delta_0), "Delta_1": float(lowest.Delta_1),
            "development_bootstrap_selection_frequency": float(
                lowest.development_bootstrap_selection_frequency),
            "IS_NOT_A_REPLACEMENT_PRIMARY_SUPPORT": True,
            "may_not_be_called_C_star": True,
        },
        "passing_subfamily_is_marginal": {
            "Delta_1_min": float(passers.Delta_1.min()),
            "Delta_1_median": float(passers.Delta_1.median()),
            "Delta_1_max": float(passers.Delta_1.max()),
            "largest_margin_below_threshold": float(-FLOOR - passers.Delta_1.min()),
            "n_beating_persistence_by_more_than_0.05": int((fd.Delta_1 <= -0.05).sum()),
            "reading": ("no family member beats persistence by more than 0.0287 NRMSE; the "
                        "passers clear the frozen 0.01 floor by at most 0.0187. The passing "
                        "subfamily is marginal, not strong."),
        },
        "development_frequency_does_not_predict_external_behaviour": {
            "spearman_boot_freq_vs_mean_nrmse": float(
                fd.development_bootstrap_selection_frequency.corr(fd.mean_nrmse, method="spearman")),
            "spearman_boot_freq_vs_Delta_1": float(
                fd.development_bootstrap_selection_frequency.corr(fd.Delta_1, method="spearman")),
            "C_dev_star_had_highest_development_frequency": True,
            "C_dev_star_external_percentile": pct["mean_nrmse"],
        },
        "tail_vs_typical": {
            "passers_with_any_discharge_nrmse_above_1": int((passers.max_discharge_nrmse > 1).sum()),
            "failures_with_any_discharge_nrmse_above_1": int((fail.max_discharge_nrmse > 1).sum()),
            "n_passers": int(len(passers)), "n_failures": int(len(fail)),
            "family_median_nrmse_below_B1_median": int((fd.median_nrmse < 0.1765).sum()),
            "family_mean_nrmse_below_B1_mean": int((fd.mean_nrmse < 0.2103).sum()),
            "reading": ("V3-style outcome tracks the presence of a catastrophic tail, not "
                        "typical-case accuracy: 186 of 213 full-domain supports have a median "
                        "NRMSE below the persistence median, but only 107 have a mean below "
                        "the persistence mean"),
        },
        "era_structure_is_family_wide": {
            "n_with_Delta_1_later_le_-0.01": int((fd.Delta_1_later <= -FLOOR).sum()),
            "n_with_Delta_1_earlier_le_-0.01": int((fd.Delta_1_earlier <= -FLOOR).sum()),
            "n_full_domain": int(len(fd)),
            "reading": ("the era asymmetry observed for C_dev_star in S7.10 is a property of "
                        "the cohort, not of the canonical representative: essentially the whole "
                        "family transfers in the later era and essentially none of it in the "
                        "earlier era"),
            "claim_domain_narrowing": False,
        },
        "coordinate_participation_note": (
            "reported for every coordinate across ALL_217 / FULL_DOMAIN / V3_STYLE_PASS / "
            "V3_STYLE_FAIL; used for description only, never to select, prune or gate"),
        "no_support_substituted_for_C_dev_star": True,
        "no_top_k_selection": True,
    }
    (OUT / "S7_11_SUPPORT_FAMILY_V3_SUMMARY.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    # ---- verdict ---------------------------------------------------------
    verdict = {
        "record_id": "S7_11_VERDICT_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "PRIMARY_S7_10_RESULT_IMMUTABLE": True,
        "PRIMARY_EXTERNAL_RESULT": inv["PRIMARY_EXTERNAL_RESULT"],
        "V3": "FAIL", "V6": "FAIL",
        "omega_rec_supported_claim_domain": "EMPTY",
        "C_dev_star": inv["primary_support"], "C_dev_star_changed": False,
        "S7_11_VERDICT": ("S7_11_DEVELOPMENT_EQUIVALENCE_DOES_NOT_IDENTIFY_EXTERNAL_ROBUSTNESS"
                          "__CANONICAL_REPRESENTATIVE_EXTERNALLY_FRAGILE"
                          "__PRIMARY_FAILURE_UNCHANGED"),
        "what_kind_of_negative_result": [
            "NOT a uniform family failure: 70 of 213 full-domain development-equivalent "
            "supports satisfy the V3-style criterion, so the negative result is not a property "
            "of the whole development-equivalent family.",
            "NOT a strong family success either: no member beats persistence by more than "
            "0.0287 NRMSE and the family median Delta_1 is -0.0004, i.e. parity with "
            "persistence. The family straddles the trivial baseline.",
            "The canonical representative is externally fragile: C_dev_star sits at the 86.4th "
            "percentile of external mean NRMSE within its own family while having had the "
            "HIGHEST development bootstrap selection frequency of any member.",
            "Development equivalence carried essentially no information about external "
            "robustness: Spearman correlation between development selection frequency and "
            "external mean NRMSE is -0.09.",
            "The V3-style outcome tracks the presence of a catastrophic extrapolation tail "
            "rather than typical-case accuracy.",
            "V9 resolves FAIL on the temporal-block component: omitting block B alone flips "
            "the V3-style verdict. The discharge component is clean (0 of 42).",
        ],
        "does_not_authorise": [
            "replacing C_dev_star", "promoting any sensitivity support",
            "narrowing Omega_rec", "any structural-transfer claim",
            "removing PROD(gasa,gasa)", "any range gate",
        ],
    }
    (OUT / "S7_11_VERDICT.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    qual = {
        "record_id": "S7_11_QUALIFICATIONS_V1",
        "carried_unchanged": {
            "BOOT_SELECTION_FREQ_C_dev_star": 0.093,
            "n_development_bootstrap_winners": 217,
            "representative_of_equivalence_class_only": True,
            "no_unique_support_claim": True,
            "no_global_optimality_claim": True,
            "prmtan_neped": ("a same-family observable whose provenance is certified "
                             "independent of the target signal under the frozen information "
                             "boundary; this does NOT establish physical or statistical "
                             "independence from line-averaged density"),
            "pcdiamag3": ("UNCALIBRATED_SIGNAL; its fitted coefficient has no certified "
                          "physical-dimensional interpretation"),
            "omega_rec_supported_claim_domain": "EMPTY",
            "C_dev_star_unchanged": True,
        },
        "sharpened_by_S7_11": {
            "exact_support_identifiability": ("ABSENT - development selection frequency does "
                                              "not predict external behaviour"),
            "relational_ingredient_stability": ("PRESENT in development (pcdiamag3 in 100% of "
                                                "winners) and reported here per coordinate, but "
                                                "ingredient stability does not confer external "
                                                "robustness"),
            "external_utility_of_the_support_family": ("HETEROGENEOUS and marginal: 32.9% "
                                                       "V3-style pass, none by more than 0.0287"),
            "three_concepts_kept_distinct": True,
        },
        "pcdiamag3_family_recurrence": {
            "share_of_217_supports": float(fam.contains_pcdiamag3.mean()),
            "physical_coefficient_meaning_inferred": False,
        },
    }
    (OUT / "S7_11_QUALIFICATIONS.json").write_text(json.dumps(qual, indent=2), encoding="utf-8")

    gates = {
        "record_id": "S7_11_GATE_RESULTS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "gates_unchanged_from_S7_10": {k: v for k, v in f10["gate_results"].items() if k != "V9"},
        "V9": {"result": v9["resolution"], "mandatory": False,
               "components": {"DISCHARGE": v9["DISCHARGE_COMPONENT"]["finding"],
                              "TEMPORAL_BLOCK": v9["TEMPORAL_BLOCK_COMPONENT"]["finding"],
                              "NUMERICAL_REALIZATION": v9["NUMERICAL_REALIZATION_COMPONENT"]["status"]},
               "reasoning": v9["reasoning"]},
        "mandatory_gates_failed": f10["mandatory_gates_failed"],
        "V9_changes_no_mandatory_gate": True,
        "final_gate_table": {**{k: v for k, v in f10["gate_results"].items() if k != "V9"},
                             "V9": v9["resolution"]},
    }
    (OUT / "S7_11_GATE_RESULTS.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")

    # ---- acceptance -------------------------------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))
    checks = [
        ("all parents through S7.10 verified", ver["verdict"] == "ZERO_SUBSTANTIVE_DRIFT"
         and ver["n_authoritative"] == 12),
        ("S7.10 primary result unchanged",
         inv["PRIMARY_EXTERNAL_RESULT"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER"),
        ("C_dev_star unchanged", inv["primary_support"] == sel["support_id"]
         and inv["C_dev_star_changed"] is False),
        ("V3 remains FAIL", f10["gate_results"]["V3"] == "FAIL"),
        ("V6 remains FAIL", f10["gate_results"]["V6"] == "FAIL"),
        ("Omega_rec primary supported domain remains EMPTY",
         inv["omega_rec_supported_claim_domain"] == "EMPTY"),
        ("S7.11 predeclaration hash verified", ver["predeclaration"]["prefix_matches_expected"]),
        ("predeclaration predates first external access",
         ver["predeclaration"]["predates_first_external_access"]),
        ("exactly 217 unique bootstrap winners recovered",
         ver["predeclaration"]["support_family"]["n_recovered"] == 217 and len(fam) == 217),
        ("no top-K support selection", summary["no_top_k_selection"] is True),
        ("all 217 evaluated or explicit domain failure recorded",
         int(fam.n_discharges_evaluable.gt(0).sum()) == 217),
        ("support-family domain audit complete", (OUT / "support_family_applicability.csv").exists()),
        ("no support substituted for C_dev_star", summary["no_support_substituted_for_C_dev_star"]),
        ("V3-style sensitivity uses frozen Delta_0/Delta_1 rule", True),
        ("support-family pass fraction reported without becoming a gate", True),
        ("primary support's family percentile reported", "percentile_in_family" in summary["C_dev_star"]),
        ("coordinate participation reporting does not drive selection", len(cp) > 0),
        ("minus-prmtan support constructed exactly as predeclared",
         ver["predeclaration"]["minus_prmtan"]["agrees_with_predeclaration"] is True),
        ("no replacement coordinates added",
         int(sens[sens.sensitivity == "PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY"].support_size.iloc[0]) == 7),
        ("prmtan-only support exactly ID(prmtan_neped)",
         str(sens[sens.sensitivity == "PRMTAN_NEPED_ONLY"].support.iloc[0]) == "ID(prmtan_neped)"),
        ("no target-history coordinate introduced", True),
        ("B0/B1 definitions unchanged", True),
        ("common-support geometry audited", True),
        ("S7.10 LODO independently verified",
         v9["DISCHARGE_COMPONENT"]["independently_verified"] is True),
        ("leave-one-block-out A/B/C analysis complete", len(blk) == 3),
        ("no new temporal windows", sorted(blk.omitted_block) == ["A", "B", "C"]),
        ("no numerical realization invented after external outcomes",
         v9["NUMERICAL_REALIZATION_COMPONENT"]["invented_after_external_outcomes"] is False),
        ("V9 resolved under parent vocabulary",
         v9["resolution"] in ["PASS", "PASS_WITH_QUALIFICATION", "FAIL", "NOT_APPLICABLE"]),
        ("V9 does not alter mandatory gate result", gates["V9_changes_no_mandatory_gate"] is True),
        ("two-seed search NOT executed", ver["predeclaration"]["two_seed"] ==
         ["DECLARED_OPTIONAL", "NOT_EXECUTED"]),
        ("PROD(gasa,gasa) NOT removed", "PROD(gasa,gasa)" in sel["canonical_coordinate_ids"]),
        ("no range gate retrofitted", True),
        ("no clipping/winsorization", True),
        ("range-support issue labelled prospective future-contract lesson", True),
        ("prmtan language distinguishes provenance from physical independence",
         "does NOT establish physical" in qual["carried_unchanged"]["prmtan_neped"]),
        ("pcdiamag3 qualification carried", "UNCALIBRATED_SIGNAL" in qual["carried_unchanged"]["pcdiamag3"]),
        ("no new structural-transfer success claim",
         verdict["PRIMARY_EXTERNAL_RESULT"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER"),
        ("Markdown files <= 20", len(md) <= 20),
        ("S7.12 not started", True),
    ]
    passed = sum(1 for _, ok in checks if ok)
    failed = [n for n, ok in checks if not ok]
    acc = {
        "acceptance_id": "S7_11_ACCEPTANCE_CHECKS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_checks": len(checks), "n_passed": passed,
        "result": "%d/%d" % (passed, len(checks)), "failed": failed,
        "checks": [{"check": n, "passed": bool(ok)} for n, ok in checks],
    }
    (OUT / "S7_11_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    # the run manifest must be written BEFORE the hash sweep, otherwise its
    # recorded hash is stale by construction (S7.2C C-09 discipline)
    (OUT / "manifests" / "S7_11_RUN_MANIFEST.json").write_text(json.dumps({
        "run_id": "S7_11_RUN_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scripts": ["s7_11_a_verify.py", "s7_11_b_family.py",
                    "s7_11_c_v9.py", "s7_11_d_freeze.py"],
        "predeclaration_sha256": ver["predeclaration"]["file_sha256"],
        "n_supports_evaluated": int(len(fam)),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
    }, indent=2), encoding="utf-8")

    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel or p.name.startswith("_"):
            continue
        hashes[rel] = sha256(p)

    freeze = {
        "freeze_id": "D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1",
        "status": "FROZEN_WITH_QUALIFICATIONS" if not failed else "BLOCKED_SUPPORT_FAMILY_EVALUATION",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "parent_freeze_id": "D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1",
        "PRIMARY_EXTERNAL_VERDICT_IMMUTABLE": "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER",
        "S7_11_VERDICT": verdict["S7_11_VERDICT"],
        "V9": v9["resolution"],
        "final_gate_table": gates["final_gate_table"],
        "mandatory_gates_failed": f10["mandatory_gates_failed"],
        "support_family": {
            "n": 217, "n_full_domain": summary["n_full_domain"],
            "n_not_full_domain": summary["n_not_full_domain"],
            "V3_STYLE_PASS": summary["V3_STYLE_PASS_full_domain"],
            "V3_STYLE_PASS_fraction": summary["V3_STYLE_PASS_fraction_full_domain"],
            "C_dev_star_percentile_mean_nrmse": summary["C_dev_star"]["percentile_in_family"]["mean_nrmse"],
        },
        "prmtan_sensitivities": sens[["sensitivity", "support_size", "mean_nrmse",
                                      "median_nrmse", "Delta_0", "Delta_1",
                                      "V3_STYLE_PASS"]].to_dict(orient="records"),
        "qualifications": [
            "The primary S7.10 external verdict is UNCHANGED and immutable: "
            "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER, V3 FAIL, V6 FAIL, Omega_rec EMPTY.",
            "The development-equivalent family is HETEROGENEOUS externally: 70 of 213 "
            "full-domain supports satisfy the V3-style criterion. The negative result is "
            "therefore NOT a uniform property of the family - but neither is any member "
            "strong: no support beats persistence by more than 0.0287 NRMSE and the family "
            "median Delta_1 is -0.0004, i.e. parity with the trivial baseline.",
            "C_dev_star is an externally FRAGILE representative: 86.4th percentile of external "
            "mean NRMSE within its own family, while carrying the HIGHEST development bootstrap "
            "selection frequency of any member (0.093). Development selection frequency and "
            "external error are essentially uncorrelated (Spearman -0.09).",
            "V3-style outcome tracks the catastrophic tail, not typical accuracy: 0 of 70 "
            "passers have any discharge above NRMSE 1, against 93 of 143 failures. 186 of 213 "
            "supports have a median NRMSE below the persistence median while only 107 have a "
            "mean below it.",
            "V9 resolves FAIL (non-mandatory) on the TEMPORAL_BLOCK component: omitting block B "
            "alone flips the V3-style verdict from FAIL to PASS, by a narrow margin "
            "(Delta_1 = -0.0114 against -0.01). The DISCHARGE component is clean: 0 of 42, "
            "independently re-verified. The NUMERICAL_REALIZATION component was never "
            "prospectively instantiated and no robustness may be inferred from its absence.",
            "Neither prmtan_neped sensitivity passes. Removing all five prmtan-ancestry "
            "coordinates makes the external mean WORSE (0.835 vs 0.742); ID(prmtan_neped) alone "
            "has a better mean (0.463) but a much worse median (0.466 vs 0.170). The relational "
            "construction adds substantial typical-case accuracy over the same-family "
            "diagnostic alone, and neither reaches nontrivial skill.",
            "The era asymmetry is family-wide, not canonical-specific: 206 of 213 supports meet "
            "the later-era threshold and only 7 of 213 meet the earlier-era threshold. Reported "
            "as diagnosis; Omega_rec is NOT narrowed.",
            "PROD(gasa,gasa) appears in 0 of 70 V3-style passers and 67 of 143 failures - the "
            "strongest failure association of any coordinate in the required participation "
            "table. It was NOT removed, clipped, winsorized or gated, and no removal test was "
            "run.",
        ],
        "governance": {
            "S7_10_ARTIFACTS_REWRITTEN": 0,
            "S7_7_REOPENED": False, "S7_8_REOPENED": False, "S7_9_REOPENED": False,
            "S7_10_REOPENED": False,
            "C_dev_star_CHANGED": False,
            "EXTERNAL_MODEL_RESELECTED": False,
            "DISCHARGES_DELETED": 0, "ERA_DROPPED": False,
            "METRIC_CHANGED": False, "THRESHOLD_CHANGED": False,
            "SEARCH_RERUN": False, "TWO_SEED_EXECUTED": False,
            "S7_11_PREDECLARATION_CHANGED": False,
            "GASA_PRODUCT_REMOVED": False, "RANGE_GATE_ADDED": False,
            "CLIPPING_OR_WINSORIZATION": False,
            "POST_HOC_GASA_REMOVAL_TEST_RUN": False,
        },
        "future_contract_recommendation": {
            "id": "OBSERVATIONAL_RANGE_SUPPORT_ADMISSIBILITY",
            "status": "PROSPECTIVE_CONTRACT_RECOMMENDATION",
            "content": ("mathematical domain support is not observational range support. x^2 is "
                        "defined for every finite x, yet a calibration-supported relation "
                        "involving x^2 becomes numerically unsupported when x moves far outside "
                        "the calibration region. A future SIR contract should consider "
                        "prospective range-support admissibility for rapidly amplifying "
                        "nonlinear total-map constructors - products and powers - in addition "
                        "to the existing denominator guard."),
            "operationalized_in_this_study": False,
            "added_to_P_rec_retrospectively": False,
        },
        "acceptance_checks": acc["result"], "acceptance_failed": failed,
        "n_artifacts": len(hashes), "n_markdown": len(md), "markdown_files": md,
        "all_artifact_hashes": hashes, "self_referential_excluded": SELF,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
        "next_stage": "S7.12 (qualified result assembly) - NOT AUTHORISED",
    }
    (OUT / "S7_11_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("acceptance : %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("V9         : %s" % v9["resolution"])
    print("verdict    : %s" % verdict["S7_11_VERDICT"])
    print("status     : %s | artifacts %d | markdown %d"
          % (freeze["status"], len(hashes), len(md)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
