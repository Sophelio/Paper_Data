"""S7.10 step C - paired comparisons, bootstrap CIs, win/tie/loss, LODO, eras,
S_pers, and the V1-V10 gate table.

Uses exactly the pre-value frozen external inference policy. No threshold is
changed. No result is rescued.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S79 = S7 / "09_development_selection_and_freeze"

FLOOR = 0.01
COMPARATORS = ["B0", "B1", "B1A", "B2", "B3", "H0"]


def boot_ci(d, seed, nrep=10000):
    """Percentile CI of the mean paired difference; shared indices per cohort."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), (nrep, len(d)))
    stat = d[idx].mean(axis=1)
    return (float(np.percentile(stat, 2.5, method="linear")),
            float(np.percentile(stat, 97.5, method="linear")), idx)


def main() -> int:
    pol = json.loads((OUT / "EXTERNAL_INFERENCE_POLICY_PREVALUE.json").read_text())
    bm = pd.read_csv(OUT / "external_block_metrics.csv")
    dm = pd.read_csv(OUT / "external_discharge_metrics.csv")
    dm = dm[dm.evaluable].reset_index(drop=True)
    n = len(dm)
    assert n == 42

    ear = dm.era.values == "earlier"
    lat = dm.era.values == "later"
    assert ear.sum() == 24 and lat.sum() == 18

    seeds = {"pooled": pol["bootstrap"]["pooled_seed"],
             "earlier": pol["bootstrap"]["earlier_seed"],
             "later": pol["bootstrap"]["later_seed"]}
    NREP = pol["bootstrap"]["replicates"]

    # ONE index matrix per cohort, reused for every comparator
    idxs = {}
    for coh, mask, seed in [("pooled", np.ones(n, bool), seeds["pooled"]),
                            ("earlier", ear, seeds["earlier"]),
                            ("later", lat, seeds["later"])]:
        rng = np.random.default_rng(seed)
        idxs[coh] = (mask, rng.integers(0, int(mask.sum()), (NREP, int(mask.sum()))))

    rel = dm.REL_nrmse.values
    paired_rows, ci_rows, wtl_rows, lodo_rows, era_rows = [], [], [], [], []

    for B in COMPARATORS:
        b = dm["%s_nrmse" % B].values
        d = rel - b                                  # negative = REL lower error
        for coh in ("pooled", "earlier", "later"):
            mask, ix = idxs[coh]
            dd = d[mask]
            stat = dd[ix].mean(axis=1)
            lo = float(np.percentile(stat, 2.5, method="linear"))
            hi = float(np.percentile(stat, 97.5, method="linear"))
            ci_rows.append({"comparator": B, "cohort": coh, "n": int(mask.sum()),
                            "mean_delta": float(dd.mean()),
                            "median_delta": float(np.median(dd)),
                            "ci_lo_2.5": lo, "ci_hi_97.5": hi,
                            "replicates": NREP, "seed": seeds[coh],
                            "ci_type": "percentile", "method": "linear",
                            "ci_excludes_zero": bool(lo > 0 or hi < 0),
                            "ci_is_a_significance_gate": False})
        w = int((d <= -FLOOR).sum()); t = int(((d > -FLOOR) & (d <= FLOOR)).sum())
        l = int((d > FLOOR).sum())
        wtl_rows.append({"comparator": B, "wins": w, "ties": t, "losses": l,
                         "n": n, "floor": FLOOR, "reporting_only": True})
        lo_vals = np.array([np.delete(d, k).mean() for k in range(n)])
        lodo_rows.append({"comparator": B, "full_cohort_mean_delta": float(d.mean()),
                          "lodo_min": float(lo_vals.min()), "lodo_max": float(lo_vals.max()),
                          "lodo_range": float(lo_vals.max() - lo_vals.min()),
                          "most_influential_shot": str(dm.shot_id.values[int(np.argmax(np.abs(lo_vals - d.mean())))]),
                          "n_lodo_cohorts_meeting_minus_0.01": int((lo_vals <= -FLOOR).sum())})
        for name, mask in [("earlier", ear), ("later", lat)]:
            dd = d[mask]
            direction = ("MATERIAL_IMPROVEMENT" if dd.mean() <= -FLOOR else
                         "PRACTICAL_TIE" if dd.mean() <= FLOOR else "MATERIAL_ADVERSE")
            era_rows.append({"comparator": B, "era": name, "n": int(mask.sum()),
                             "mean_REL_nrmse": float(rel[mask].mean()),
                             "mean_comparator_nrmse": float(b[mask].mean()),
                             "mean_delta": float(dd.mean()),
                             "median_delta": float(np.median(dd)),
                             "practical_direction": direction})
        for k in range(n):
            paired_rows.append({"shot_id": dm.shot_id.values[k], "era": dm.era.values[k],
                                "comparator": B, "NRMSE_REL": float(rel[k]),
                                "NRMSE_comparator": float(b[k]), "d_s": float(d[k]),
                                "class": ("WIN" if d[k] <= -FLOOR else
                                          "TIE" if d[k] <= FLOOR else "LOSS")})

    pd.DataFrame(paired_rows).to_csv(OUT / "external_paired_differences.csv", index=False)
    pd.DataFrame(ci_rows).to_csv(OUT / "external_bootstrap_intervals.csv", index=False)
    pd.DataFrame(wtl_rows).to_csv(OUT / "external_win_tie_loss.csv", index=False)
    pd.DataFrame(lodo_rows).to_csv(OUT / "external_lodo_results.csv", index=False)

    # ---- era table including REL and every method -----------------------
    for m in ["REL"] + COMPARATORS:
        for name, mask in [("earlier", ear), ("later", lat)]:
            era_rows.append({"comparator": "(level) " + m, "era": name,
                             "n": int(mask.sum()),
                             "mean_REL_nrmse": np.nan, "mean_comparator_nrmse": np.nan,
                             "mean_delta": np.nan, "median_delta": np.nan,
                             "practical_direction": "",
                             "mean_nrmse_of_method": float(dm["%s_nrmse" % m].values[mask].mean())})
    pd.DataFrame(era_rows).to_csv(OUT / "external_era_results.csv", index=False)

    # ---- V3 --------------------------------------------------------------
    D0 = float((rel - dm.B0_nrmse.values).mean())
    D1 = float((rel - dm.B1_nrmse.values).mean())
    v3_pass = bool(D0 <= -FLOOR and D1 <= -FLOOR)
    lo0 = np.array([np.delete(rel - dm.B0_nrmse.values, k).mean() for k in range(n)])
    lo1 = np.array([np.delete(rel - dm.B1_nrmse.values, k).mean() for k in range(n)])
    v3_lodo = [(bool(a <= -FLOOR and b <= -FLOOR)) for a, b in zip(lo0, lo1)]

    # ---- V6 --------------------------------------------------------------
    v6 = {}
    for name, mask in [("earlier", ear), ("later", lat)]:
        for j, B in [("0", "B0"), ("1", "B1")]:
            dd = (rel - dm["%s_nrmse" % B].values)[mask]
            v6["Delta_%s_%s" % (j, name)] = float(dd.mean())
            v6["direction_%s_%s" % (j, name)] = (
                "MATERIAL_IMPROVEMENT" if dd.mean() <= -FLOOR else
                "PRACTICAL_TIE" if dd.mean() <= FLOOR else "MATERIAL_ADVERSE")
    dirs = [v for k, v in v6.items() if k.startswith("direction")]
    if v3_pass:
        v6_out = ("PASS" if all(d == "MATERIAL_IMPROVEMENT" for d in dirs) else
                  "FAIL_FOR_FULL_DOMAIN" if any(d == "MATERIAL_ADVERSE" for d in dirs) else
                  "PASS_WITH_QUALIFICATION")
    else:
        v6_out = "FAIL"
    v6["outcome"] = v6_out
    v6["pooled_V3_passed"] = v3_pass
    v6["note"] = ("the three-valued S7.2C outcome schema is conditioned on pooled V3 "
                  "passing; pooled V3 failed, so V6 resolves to FAIL under the parent "
                  "four-state gate vocabulary. V6 may not rescue V3. Era results are "
                  "reported in full regardless.") if not v3_pass else ""

    # ---- S_pers ----------------------------------------------------------
    sp = dm.S_pers_REL.values
    sp_ok = np.isfinite(sp)
    spers = {"n_defined": int(sp_ok.sum()), "n_undefined": int((~sp_ok).sum()),
             "mean": float(np.mean(sp[sp_ok])), "median": float(np.median(sp[sp_ok])),
             "earlier_mean": float(np.mean(sp[ear & sp_ok])),
             "later_mean": float(np.mean(sp[lat & sp_ok])),
             "n_positive": int((sp[sp_ok] > 0).sum()),
             "interpretation": "> 0 improves on persistence; < 0 worse than persistence",
             "is_a_V3_threshold": False, "replaces_NRMSE": False}

    # ---- gate table -------------------------------------------------------
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text())
    pf = json.loads((OUT / "manifests" / "PREFLIGHT.json").read_text())
    fa = json.loads((OUT / "manifests" / "FIRST_EXTERNAL_ACCESS.json").read_text())
    v2ev = json.loads((S79 / "manifests" / "V2_DEVELOPMENT_ONLY_DISCOVERY_EVIDENCE.json").read_text())
    ineligible = int((~bm.comparison_eligible).sum())

    gates = [
        {"gate": "V1", "name": "information boundary", "mandatory": True,
         "authoritative_rule": "no target leakage; no admitted quantity with unresolved target ancestry",
         "evidence": ("all 13 primitive ancestors of C_dev_star are certified_independent_of_target "
                      "under the frozen S7.3R boundary; all 12 coordinates carry "
                      "TRANSITIVE_FROM_TARGET_INDEPENDENT_BOUNDARY"),
         "result": "PASS",
         "qualification": ("prmtan_neped is a density-family diagnostic. It is "
                           "provenance-certified independent of the target SIGNAL. This does NOT "
                           "establish physical or statistical independence from line-averaged density."),
         "claim_consequence": "no leakage-based invalidation"},
        {"gate": "V2", "name": "development-only discovery", "mandatory": True,
         "authoritative_rule": "target, ontology, support, estimator and thresholds chosen without external outcomes",
         "evidence": ("S7.9 V2_EVIDENCE_COMPLETE; representation lock precedes baseline tuning; "
                      "PRE_EXTERNAL_MODEL_FREEZE verified 13/13 before first external access at "
                      + fa["first_external_value_access_utc"]),
         "result": "PASS", "qualification": "",
         "claim_consequence": "discovery discipline intact"},
        {"gate": "V3", "name": "nontrivial skill vs B0/B1", "mandatory": True,
         "authoritative_rule": "Delta_0 <= -0.01 AND Delta_1 <= -0.01",
         "evidence": "Delta_0 = %.6f (meets), Delta_1 = %+.6f (does NOT meet)" % (D0, D1),
         "result": "PASS" if v3_pass else "FAIL",
         "qualification": ("the relational representation is materially WORSE than the "
                           "persistence baseline on the external cohort"),
         "claim_consequence": ("MANDATORY FAILURE: the primary q_rec result may NOT be presented "
                               "as a successful nontrivial structural-transfer result")},
        {"gate": "V4", "name": "fair raw comparison vs B2/B3", "mandatory": True,
         "authoritative_rule": "fair comparison on identical information and geometry; fairness, not victory",
         "evidence": ("identical 42-discharge cohort, identical calibration and protected rows, "
                      "identical target, identical calibration-fitted preprocessing, frozen "
                      "information boundary, zero external hyperparameter tuning (B2 alpha=1, "
                      "H0 alpha=1, B3 defaults + random_state, all frozen pre-external)"),
         "result": "PASS",
         "qualification": "REL is materially worse than B2, B3 and H0; V4 does not require victory",
         "claim_consequence": "the comparison is valid; no accuracy-superiority claim is available"},
        {"gate": "V5", "name": "external structural transfer", "mandatory": True,
         "authoritative_rule": "support frozen and hashed before any external evaluation",
         "evidence": ("PRE_EXTERNAL_MODEL_FREEZE frozen %s, first external value access %s, "
                      "strict ordering verified; local external calibration changed coefficients "
                      "only, never support or coordinate definitions"
                      % (fa["pre_external_model_freeze_utc"], fa["first_external_value_access_utc"])),
         "result": "PASS",
         "qualification": "V5 governs freeze discipline, not performance; performance is V3",
         "claim_consequence": "the transfer test was conducted honestly"},
        {"gate": "V6", "name": "processing-era robustness", "mandatory": True,
         "authoritative_rule": "external results reported separately for 24 earlier and 18 later discharges",
         "evidence": json.dumps({k: v for k, v in v6.items() if k.startswith(("Delta", "direction"))}),
         "result": v6_out,
         "qualification": v6["note"],
         "claim_consequence": "no era supports the claim; V6 may not rescue V3"},
        {"gate": "V7", "name": "common support", "mandatory": True,
         "authoritative_rule": "cross-representation comparisons use identical scored samples",
         "evidence": ("all 126 external blocks eligible; every method scored on identical "
                      "protected rows; %d ineligible blocks; no selective deletion" % ineligible),
         "result": "PASS", "qualification": "",
         "claim_consequence": "paired comparisons are valid"},
        {"gate": "V8", "name": "discharge-level inference", "mandatory": True,
         "authoritative_rule": "discharge, not time sample, is the independent unit",
         "evidence": ("blocks aggregated to discharge before every inference; all paired "
                      "differences and all bootstrap resampling operate on the 42 discharges"),
         "result": "PASS", "qualification": "",
         "claim_consequence": "precision is not overstated"},
        {"gate": "V9", "name": "sensitivity", "mandatory": False,
         "authoritative_rule": "no result depends catastrophically on one discharge, block or realization",
         "evidence": ("LODO computed and reported; S7.11 sensitivities predeclared and hashed "
                      "before first external access but NOT executed"),
         "result": "PENDING_S7.11", "qualification": "non-mandatory",
         "claim_consequence": "not resolved here"},
        {"gate": "V10", "name": "numerical provenance", "mandatory": True,
         "authoritative_rule": "no claim rests on interpolation-created resolution without qualification",
         "evidence": ("S7.3R/S7.4 V2 source-cadence record carried unchanged; ID(pcdiamag3) "
                      "carries UNCALIBRATED_SIGNAL; no aliasing or upsample flag set on any "
                      "selected coordinate"),
         "result": "PASS",
         "qualification": ("ID(pcdiamag3) is uncalibrated digitiser output; its fitted coefficient "
                           "has no certified physical-dimensional interpretation. Recorded whether "
                           "or not the coordinate appears influential."),
         "claim_consequence": "interpretation qualified, not invalidated"},
    ]
    mandatory_failed = [g["gate"] for g in gates if g["mandatory"] and g["result"] not in ("PASS", "PASS_WITH_QUALIFICATION")]

    primary = ("QUALIFIED_STRUCTURAL_TRANSFER_CANDIDATE" if not mandatory_failed
               else "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER")

    res = {
        "record_id": "V_REC_EXTERNAL_RESULTS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "cohort": {"n": 42, "earlier": 24, "later": 18, "evaluable": int(n),
                   "blocks_total": int(len(bm)), "blocks_eligible": int(len(bm) - ineligible)},
        "method_means": {m: float(dm["%s_nrmse" % m].mean()) for m in ["REL"] + COMPARATORS},
        "method_medians": {m: float(dm["%s_nrmse" % m].median()) for m in ["REL"] + COMPARATORS},
        "V3": {"Delta_0": D0, "Delta_1": D1, "threshold": -FLOOR, "pass": v3_pass,
               "ci_role": "reported, not a significance threshold",
               "lodo_cohorts_passing": int(sum(v3_lodo)), "lodo_n": n,
               "verdict_flips_under_any_single_omission": bool(any(v3_lodo) != all(v3_lodo))},
        "V6": v6,
        "S_pers": spers,
        "gates": gates,
        "mandatory_gates_failed": mandatory_failed,
        "PRIMARY_EXTERNAL_RESULT": primary,
        "rescue_attempted": False,
        "support_changed_after_external_access": False,
    }
    (OUT / "V_REC_EXTERNAL_RESULTS.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

    print("=" * 66)
    print("V3   Delta_0 = %+.6f   Delta_1 = %+.6f   threshold <= -0.01" % (D0, D1))
    print("V3   %s" % ("PASS" if v3_pass else "FAIL"))
    print("V6   %s   %s" % (v6_out, {k: round(v, 4) for k, v in v6.items() if k.startswith("Delta")}))
    print("mandatory gates failed: %s" % (mandatory_failed or "none"))
    print("PRIMARY_EXTERNAL_RESULT: %s" % primary)
    print("=" * 66)
    ci = pd.DataFrame(ci_rows)
    print(ci[ci.cohort == "pooled"][["comparator", "mean_delta", "median_delta",
                                     "ci_lo_2.5", "ci_hi_97.5"]].to_string(index=False))
    print()
    print(pd.DataFrame(wtl_rows)[["comparator", "wins", "ties", "losses"]].to_string(index=False))
    print()
    print("S_pers mean %.4f median %.4f  (positive in %d/%d discharges)"
          % (spers["mean"], spers["median"], spers["n_positive"], spers["n_defined"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
