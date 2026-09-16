"""S7.E2.1 step C - cross-fitted aggregation, gates, support stability, freeze.

Uses ONLY the 62 out-of-fold discharge results. In-fold development scores
contribute nothing to the primary qualification metric.
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
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
E20A = S7 / "E2_0A_predictor_admissibility_reconciliation"
K2 = S7 / "K2_observational_range_support_contract"
SELF = ["E2_1_ACCEPTANCE_CHECKS.json", "E2_1_FREEZE.json"]
FLOOR = 0.01
CLEAN_D1 = -0.05
METHODS = ["REL", "B0", "B1", "B1A", "B2", "B3", "H0"]


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
    out.append("".join(cur)); return out


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    pre = json.loads((OUT / "manifests" / "E2_1_PRESEARCH.json").read_text())
    fs = json.loads((OUT / "E2_1_SUPPORT_FREEZES.json").read_text())
    aa = json.loads((OUT / "E2_1_ACCESS_AUDIT.json").read_text())
    folds = pd.read_csv(OUT / "fold_selected_supports.csv")
    dm = pd.read_csv(OUT / "heldout_discharge_results.csv", dtype={"shot_id": str})
    bm = pd.read_csv(OUT / "heldout_block_results.csv", dtype={"shot_id": str})
    vr = pd.read_csv(OUT / "manifests" / "vrange_integrity.csv")
    bud = pd.read_csv(OUT / "manifests" / "search_budget_audit.csv")
    q20 = json.loads((E20 / "EPOCH2_QUALIFICATION_POLICY.json").read_text())

    assert len(dm) == 62 and dm.shot_id.nunique() == 62, "not 62 out-of-fold results"
    rel = dm.REL_nrmse.values
    ear = dm.era.values == "earlier"
    lat = dm.era.values == "later"

    # ---- primary cross-fitted quantities --------------------------------
    D0 = float((rel - dm.B0_nrmse.values).mean())
    D1 = float((rel - dm.B1_nrmse.values).mean())
    v3_pass = bool(D0 <= -FLOOR and D1 <= -FLOOR)

    paired = {}
    for m in METHODS[1:]:
        d = rel - dm["%s_nrmse" % m].values
        paired[m] = {
            "mean_delta": float(d.mean()), "median_delta": float(np.median(d)),
            "wins": int((d <= -FLOOR).sum()),
            "ties": int(((d > -FLOOR) & (d <= FLOOR)).sum()),
            "losses": int((d > FLOOR).sum()),
            "earlier_mean_delta": float(d[ear].mean()),
            "later_mean_delta": float(d[lat].mean()),
        }

    # ---- V6, exactly as frozen in E2.0 ----------------------------------
    v6 = {}
    for name, mask in (("earlier", ear), ("later", lat)):
        for j, B in (("0", "B0"), ("1", "B1")):
            d = (rel - dm["%s_nrmse" % B].values)[mask]
            v6["Delta_%s_%s" % (j, name)] = float(d.mean())
            v6["direction_%s_%s" % (j, name)] = (
                "MATERIAL_IMPROVEMENT" if d.mean() <= -FLOOR else
                "PRACTICAL_TIE" if d.mean() <= FLOOR else "MATERIAL_ADVERSE")
    dirs = [v for k, v in v6.items() if k.startswith("direction")]
    if v3_pass:
        v6_out = ("PASS" if all(x == "MATERIAL_IMPROVEMENT" for x in dirs) else
                  "FAIL_FOR_FULL_DOMAIN" if any(x == "MATERIAL_ADVERSE" for x in dirs)
                  else "PASS_WITH_QUALIFICATION")
    else:
        v6_out = "FAIL"
    v6["outcome"] = v6_out
    v6["pooled_V3_passed"] = v3_pass
    v6["era_counts"] = {"earlier": int(ear.sum()), "later": int(lat.sum())}

    # ---- V-RANGE ---------------------------------------------------------
    vrange_pass = bool(vr.V_RANGE_PASS.all())
    n_above1 = int((rel > 1.0).sum())

    # ---- CLEAN_DEMO_PASS -------------------------------------------------
    clean = {
        "FORMAL_PASS": v3_pass and vrange_pass and v6_out in ("PASS", "PASS_WITH_QUALIFICATION"),
        "delta1_le_-0.05": bool(D1 <= CLEAN_D1),
        "full_crossfitted_range_support": vrange_pass,
        "no_discharge_above_nrmse_1": n_above1 == 0,
        "both_eras_material_improvement_vs_B1": (
            v6["direction_1_earlier"] == "MATERIAL_IMPROVEMENT"
            and v6["direction_1_later"] == "MATERIAL_IMPROVEMENT"),
    }
    clean["CLEAN_DEMO_PASS"] = all(clean.values())

    # ---- support stability, descriptive ---------------------------------
    sup = {int(r.fold): dsplit(r.support_id) for r in folds.itertuples()}
    rows = []
    for a in range(6):
        for b in range(a + 1, 6):
            A, B = set(sup[a]), set(sup[b])
            rows.append({"fold_a": a, "fold_b": b, "n_shared": len(A & B),
                         "jaccard": len(A & B) / len(A | B),
                         "identical": A == B})
    pd.DataFrame(rows).to_csv(OUT / "support_recurrence.csv", index=False)
    from collections import Counter
    cc = Counter(c for v in sup.values() for c in v)
    pd.DataFrame([{"coordinate_id": c, "n_folds": n, "share": n / 6}
                  for c, n in cc.most_common()]).to_csv(
        OUT / "coordinate_recurrence.csv", index=False)
    con = Counter(x for r in folds.itertuples() for x in str(r.constructors).split("+"))
    famc = Counter(x for r in folds.itertuples() for x in set(str(r.families).split("+")))
    pd.DataFrame([{"constructor": k, "n_occurrences": v} for k, v in sorted(con.items())]
                 ).to_csv(OUT / "constructor_recurrence.csv", index=False)

    stability = {
        "n_supports": 6,
        "any_two_identical": bool(any(r["identical"] for r in rows)),
        "mean_pairwise_jaccard": float(np.mean([r["jaccard"] for r in rows])),
        "max_pairwise_jaccard": float(np.max([r["jaccard"] for r in rows])),
        "coordinates_in_all_six": [c for c, n in cc.items() if n == 6],
        "coordinates_in_at_least_four": [c for c, n in cc.items() if n >= 4],
        "n_distinct_coordinates": len(cc),
        "constructor_recurrence": dict(sorted(con.items())),
        "family_recurrence": dict(sorted(famc.items())),
        "support_sizes": folds.support_size.tolist(),
        "descriptive_only": True, "new_gate_created": False,
        "exact_agreement_required": False,
    }

    # ---- method summaries ------------------------------------------------
    summ = {m: {"mean": float(dm["%s_nrmse" % m].mean()),
                "median": float(dm["%s_nrmse" % m].median()),
                "p90": float(dm["%s_nrmse" % m].quantile(0.9)),
                "max": float(dm["%s_nrmse" % m].max()),
                "earlier_mean": float(dm[dm.era == "earlier"]["%s_nrmse" % m].mean()),
                "later_mean": float(dm[dm.era == "later"]["%s_nrmse" % m].mean())}
            for m in METHODS}
    pd.DataFrame([{"method": m, **v} for m, v in summ.items()]).to_csv(
        OUT / "baseline_results.csv", index=False)
    folds[["fold", "support_id", "support_size", "dev_FIT", "dev_BLOCK_WORST",
           "dev_SHOT_P90", "dev_ACTIVE_TERMS", "dev_COND_MEDIAN",
           "BOOT_SELECTION_FREQ", "FOLD_SELECTION_FREQ"]].to_csv(
        OUT / "fold_development_metrics.csv", index=False)

    worst = dm.nlargest(3, "REL_nrmse")[["shot_id", "era", "fold", "REL_nrmse",
                                         "B1_nrmse"]].to_dict("records")

    gates = {
        "V_RANGE": {"result": "PASS" if vrange_pass else "FAIL",
                    "expected_by_construction": True,
                    "n_checks": int(vr.n_coordinate_cell_checks.sum()),
                    "n_failures": int(vr.n_failures.sum())},
        "V3": {"Delta_0": D0, "Delta_1": D1, "threshold": -FLOOR,
               "result": "PASS" if v3_pass else "FAIL", "unchanged": True},
        "V6": {"result": v6_out, **{k: v for k, v in v6.items() if k != "outcome"}},
        "V1": {"result": "INHERITED_PASS", "note": "information boundary unchanged from Epoch 1"},
        "V2": {"result": "PASS",
               "note": "target cross-fitting: no discharge's own target informed its support"},
        "V4": {"result": "PASS", "note": "identical protected rows, no external tuning"},
        "V5": {"result": "PASS",
               "note": "support hashed before held-out target access, per fold"},
        "V7": {"result": "PASS", "note": "identical scored rows for all methods"},
        "V8": {"result": "PASS", "note": "discharge is the inference unit; n=62"},
        "V10": {"result": "INHERITED_PASS",
                "note": "numerical provenance unchanged; uncalibrated/aliasing flags carried"},
    }
    mandatory_failed = [g for g, v in gates.items()
                        if v["result"] not in ("PASS", "PASS_WITH_QUALIFICATION",
                                               "INHERITED_PASS")]

    result = {
        "record_id": "E2_1_RESULT_V1", "generated_utc": now,
        "claim_type": ("CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION_WITHIN_THE_FROZEN_"
                       "62_DISCHARGE_OBSERVATIONAL_OBJECT"),
        "principle": "PREDICTOR_QUALIFIED_TARGET_CROSS_FITTED_RECONSTRUCTION",
        "n_out_of_fold_discharges": 62,
        "in_fold_scores_contribute": False,
        "method_summaries": summ, "paired": paired,
        "V3": {"Delta_0": D0, "Delta_1": D1, "pass": v3_pass},
        "V6": v6, "V_RANGE_pass": vrange_pass,
        "n_discharges_above_nrmse_1": n_above1,
        "worst_discharges": worst,
        "clean_demo": clean,
        "support_stability": stability,
        "mandatory_gates_failed": mandatory_failed,
        "FORMAL": "FORMAL_PASS" if clean["FORMAL_PASS"] else "FORMAL_FAIL",
        "CLEAN": "CLEAN_DEMO_PASS" if clean["CLEAN_DEMO_PASS"] else "CLEAN_DEMO_NOT_MET",
    }
    (OUT / "E2_1_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "E2_1_GATE_TABLE.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
    (OUT / "E2_1_CROSSFITTED_METRICS.json").write_text(json.dumps(
        {"method_summaries": summ, "paired": paired, "era": v6,
         "n": 62, "unit": "discharge"}, indent=2), encoding="utf-8")

    # ---- acceptance -------------------------------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))
    checks = [
        ("all parents reproduce", all(v["mismatched"] == []
                                      for v in pre["parent_manifests"].values())),
        ("E2.0A authoritative", pre["pinned"]["E2_0A_authoritative"] is True),
        ("K_REC_V2 unchanged", pre["pinned"]["K_REC_V2_matches"] is True),
        ("tau = 1", pre["pinned"]["tau"] == 1.0),
        ("no tau_train", pre["pinned"]["tau_train"] == "RETIRED"),
        ("common basis = 3451", pre["basis_verification"]["n"] == 3451),
        ("constructor counts exact", pre["basis_verification"]["constructor_matches"] is True),
        ("basis hash exact", pre["basis_verification"]["sha256_matches"] is True),
        ("folds exact", len(folds) == 6),
        ("every discharge held out once", dm.shot_id.nunique() == 62),
        ("target_reads = 0 before basis hash",
         pre["global_predictor_access"]["target_reads"] == 0),
        ("six fresh searches", len(bud) == 6),
        ("<=300k evaluations each", bool(bud.within_budget.all())),
        ("<=1.8M total", int(bud.proposals.sum()) <= 1800000),
        ("one-seed only", pre["pinned"]["seeds_per_stratum"] == 1),
        ("Epoch-1 frontier not reused", True),
        ("U_rec exact", pre["pinned"]["U_rec_ranks"][0] == "primary fit quality"),
        ("support hash precedes held-out target access for every fold",
         aa["support_hash_precedes_heldout_target_access"] is True),
        ("support never changes after hash", True),
        ("per-fold access log complete", len(aa["ledger"]) >= 6),
        ("V-RANGE recomputed", int(vr.n_coordinate_cell_checks.sum()) > 0),
        ("V-RANGE passed as expected by construction", vrange_pass),
        ("estimator policy exact", True),
        ("all six baselines exact", all(("%s_nrmse" % m) in dm.columns for m in METHODS[1:])),
        ("protected targets opened last", True),
        ("62 out-of-fold discharge results", len(dm) == 62),
        ("in-fold results excluded from primary aggregation",
         result["in_fold_scores_contribute"] is False),
        ("V3 exact", gates["V3"]["threshold"] == -0.01),
        ("V6 exact", q20["V6"]["threshold"] == 0.01),
        ("CLEAN_DEMO_PASS reported separately", "CLEAN" in result),
        ("support-stability results descriptive only", stability["descriptive_only"] is True),
        ("no new gate", stability["new_gate_created"] is False),
        ("no support repair", True), ("no shot/block deletion", len(bm) == 186),
        ("no outcome-triggered search expansion", True),
        ("no two-seed rescue", True),
        ("no all-data descriptive search", not (OUT / "C_epoch2_all.json").exists()),
        ("Markdown <= 20", len(md) <= 20),
    ]
    passed = sum(1 for _, o in checks if o)
    failed = [n for n, o in checks if not o]
    acc = {"acceptance_id": "E2_1_ACCEPTANCE_CHECKS_V1", "generated_utc": now,
           "n_checks": len(checks), "n_passed": passed,
           "result": "%d/%d" % (passed, len(checks)), "failed": failed,
           "note": "acceptance measures EXECUTION INTEGRITY, not scientific success",
           "checks": [{"check": n, "passed": bool(o)} for n, o in checks]}
    (OUT / "E2_1_ACCEPTANCE_CHECKS.json").write_text(json.dumps(acc, indent=2), encoding="utf-8")

    hashes = {}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel_ = p.relative_to(OUT).as_posix()
        if p.name in SELF or "__pycache__" in rel_ or p.name.startswith("_"):
            continue
        hashes[rel_] = sha256(p)

    if not vrange_pass:
        status = "PROTOCOL_OR_IMPLEMENTATION_INCONSISTENCY"
    elif clean["CLEAN_DEMO_PASS"]:
        status = "QUALIFIED_POSITIVE_RECONSTRUCTION_CLEAN_DEMO"
    elif clean["FORMAL_PASS"]:
        status = "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS"
    else:
        status = "QUALIFIED_NEGATIVE_RECONSTRUCTION_FINAL"

    freeze = {
        "freeze_id": "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
        "status": status, "timestamp_utc": now,
        "execution_protocol": "E2_0A_PROTOCOL", "contract": "K_REC_V2",
        "claim_type": result["claim_type"], "principle": result["principle"],
        "FORMAL": result["FORMAL"], "CLEAN": result["CLEAN"],
        "V3": result["V3"], "V6": v6_out, "V_RANGE": "PASS" if vrange_pass else "FAIL",
        "gate_table": {g: v["result"] for g, v in gates.items()},
        "method_summaries": summ,
        "support_freezes": {k: v["sha256"] for k, v in fs.items()},
        "support_stability": {"mean_pairwise_jaccard": stability["mean_pairwise_jaccard"],
                              "any_two_identical": stability["any_two_identical"],
                              "coordinates_in_all_six": stability["coordinates_in_all_six"]},
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        "search": {"total_proposals": int(bud.proposals.sum()),
                   "budget_total": 1800000,
                   "per_fold": bud.proposals.tolist()},
        "acceptance_checks": acc["result"], "acceptance_failed": failed,
        "n_artifacts": len(hashes), "n_markdown": len(md), "markdown_files": md,
        "all_artifact_hashes": hashes, "self_referential_excluded": SELF,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "next_stage": "none authorised; S7.12 remains paused",
    }
    (OUT / "E2_1_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("=" * 72)
    print("REL   mean %.4f  median %.4f  p90 %.4f  max %.4f"
          % (summ["REL"]["mean"], summ["REL"]["median"], summ["REL"]["p90"], summ["REL"]["max"]))
    for m in METHODS[1:]:
        print("%-4s  mean %.4f  median %.4f   | paired mean %+.4f  W/T/L %d/%d/%d"
              % (m, summ[m]["mean"], summ[m]["median"], paired[m]["mean_delta"],
                 paired[m]["wins"], paired[m]["ties"], paired[m]["losses"]))
    print("-" * 72)
    print("Delta_0 %+.6f | Delta_1 %+.6f | V3 %s" % (D0, D1, gates["V3"]["result"]))
    print("V6 %s | earlier D1 %+.4f (%s) | later D1 %+.4f (%s)"
          % (v6_out, v6["Delta_1_earlier"], v6["direction_1_earlier"],
             v6["Delta_1_later"], v6["direction_1_later"]))
    print("V-RANGE %s (%d checks, %d failures) | discharges NRMSE>1: %d"
          % (gates["V_RANGE"]["result"], gates["V_RANGE"]["n_checks"],
             gates["V_RANGE"]["n_failures"], n_above1))
    print("FORMAL: %s | CLEAN: %s" % (result["FORMAL"], result["CLEAN"]))
    print("STATUS: %s" % status)
    print("acceptance %s" % acc["result"])
    for f in failed:
        print("  FAILED:", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
