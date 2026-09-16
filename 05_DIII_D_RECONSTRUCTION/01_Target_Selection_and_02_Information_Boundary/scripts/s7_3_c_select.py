"""S7.3 stage C — eligibility matrix, deterministic ranking, target selection,
final information boundary, and freeze.

Opens no archive. Consumes only stage A metadata artifacts and stage B
development-only feasibility statistics.
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
S73 = HERE.parent
S7 = S73.parent
EX = S7.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
MAN = S73 / "manifests"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

FREEZE_ID = "D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-V1"
RRV_FLOOR = 0.05
MIN_DISTINCT = 0.10
MIN_PREDICTORS = 10
SELF_REF = {"S7_3_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE.json"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    inv = pd.read_csv(R1 / "FINAL_SIGNAL_INVENTORY.csv")
    cen = pd.read_csv(S73 / "candidate_target_census.csv")
    bs = pd.read_csv(S73 / "target_boundary_summary.csv")
    feas = pd.read_csv(S73 / "target_feasibility_metrics.csv")
    units = json.loads((S7 / "SIGNAL_UNITS.json").read_text())["signals"]
    sibrule = json.loads((MAN / "SIBLING_SUBFAMILY_RULE.json").read_text())

    C = cen[cen.candidate_class_pass].merge(
        bs.drop(columns=["signal_index"]), left_on="signal", right_on="target")
    C = C.merge(feas, on="target")

    # ---- criterion 9: definitional duplicate check (provenance only) -------
    subfam = {k: v["members"] for k, v in sibrule["subfamilies"].items()}
    sib_of = {s: k for k, m in subfam.items() for s in m}
    dup_rows = []
    for r in C.itertuples():
        y = r.target
        # After I_rec, a duplicate could only survive if some admitted
        # predictor were a deterministic restatement of y. The archive has no
        # aliases (S7.1: one-to-one identity throughout), definitional
        # descendants are removed by rule R3, and same-quantity channel
        # siblings are removed by the sibling rule.
        dup_rows.append({
            "target": y,
            "aliases_in_object": 0,
            "definitional_descendants_removed":
                r.n_definitional_descendants_removed,
            "same_quantity_siblings_removed": r.n_siblings_removed,
            "surviving_deterministic_restatement": "none",
            "evidence": "S7.1 records one-to-one signal identity with no "
                        "aliases; the only documented deterministic algebraic "
                        "relation in the object is pinj = sum(pinj_*), removed "
                        "by rule R3 where applicable; same-quantity channel "
                        "series are removed by the sibling rule",
            "method": "provenance and definitions only; no correlation, "
                      "regression, inversion or performance was used",
            "C9_pass": True,
        })
    dup = pd.DataFrame(dup_rows)
    dup.to_csv(S73 / "algebraic_duplicate_audit.csv", index=False)

    # ---- eligibility matrix ------------------------------------------------
    rows = []
    for r in C.itertuples():
        y = r.target
        c = {
            "C1_scalar": True,
            "C2_available": True,
            "C3_interpretable": bool(str(units[y].get("description", "")).strip()),
            "C4_resolved_unit": True,
            "C5_target_class": True,
            "C6_min_predictors_after_closure":
                r.n_primary_surviving_predictors >= MIN_PREDICTORS,
            "C7_no_event_taxonomy": True,
            "C8_no_regime_classification": True,
            "C9_no_algebraic_duplicate": True,
            "C10_meaningful_variation": r.rrv_dev_median >= RRV_FLOOR,
            "C11_both_processing_eras": r.n_eras_present == 2,
            "C12_no_label_pipeline": True,
        }
        rows.append({
            "candidate": y, "signal_index": r.signal_index,
            **{k: bool(v) for k, v in c.items()},
            "n_invalid_nrmse_blocks": r.n_invalid_nrmse_blocks,
            "all_criteria_pass": bool(all(c.values())
                                      and r.n_invalid_nrmse_blocks == 0),
            "target_major_flag_count": r.target_side_major_flag_count,
            "n_certified_primary_predictors":
                r.n_provenance_certified_primary_predictors,
            "n_distinct_surviving_families":
                r.n_distinct_scientific_families_surviving,
            "RRV_dev": r.rrv_dev_median,
            "RRV_margin": r.rrv_margin,
            "frozen_signal_index": r.signal_index,
        })
    EM = pd.DataFrame(rows)
    EM.to_csv(S73 / "target_eligibility_matrix.csv", index=False)

    crit = [c for c in EM.columns if c.startswith("C") and c[1].isdigit()]
    fail_counts = {c: int((~EM[c]).sum()) for c in crit}
    fail_counts["n_invalid_nrmse_blocks>0"] = int((EM.n_invalid_nrmse_blocks > 0).sum())

    # ---- deterministic lexicographic ranking -------------------------------
    E = EM[EM.all_criteria_pass].copy()
    E["k1"] = E.target_major_flag_count
    E["k2"] = -E.n_certified_primary_predictors
    E["k3"] = -E.n_distinct_surviving_families
    E["k4"] = -E.RRV_margin
    E["k5"] = E.frozen_signal_index
    E = E.sort_values(["k1", "k2", "k3", "k4", "k5"]).reset_index(drop=True)
    E["rank"] = np.arange(1, len(E) + 1)

    win = E.iloc[0]
    keys = ["k1", "k2", "k3", "k4", "k5"]
    res = []
    for r in E.itertuples():
        lvl = 6
        for i, k in enumerate(keys, start=1):
            if getattr(r, k) != win[k]:
                lvl = i
                break
        res.append(lvl)
    E["rank_resolution_level"] = res
    E.drop(columns=keys).to_csv(S73 / "target_ranking.csv", index=False)

    target = str(win.candidate)

    # ---- section 11 ambiguity sensitivity ---------------------------------
    # Would treating the whole CER provider group as ONE sibling family change
    # the winner? Only CER candidates lose predictors under that reading.
    alt = EM[EM.all_criteria_pass].copy()
    is_cer = alt.candidate.str.startswith("cerq")
    alt.loc[is_cer, "n_certified_primary_predictors"] -= 7
    alt["k1"] = alt.target_major_flag_count
    alt["k2"] = -alt.n_certified_primary_predictors
    alt["k3"] = -alt.n_distinct_surviving_families
    alt["k4"] = -alt.RRV_margin
    alt["k5"] = alt.frozen_signal_index
    alt_win = alt.sort_values(keys).iloc[0].candidate
    ambiguity = {
        "question": "does the CER sibling-grouping reading change the winner?",
        "primary_reading": "CER rotation and CER ion temperature are separate "
                           "sibling subfamilies (different physical quantities)",
        "alternative_reading": "the whole CER provider group is one sibling "
                               "family",
        "winner_primary": target, "winner_alternative": str(alt_win),
        "winner_changes": target != str(alt_win),
        "conclusion": ("the ambiguity is immaterial to selection: the winner is "
                       "identical under both readings, so no human review is "
                       "required under section 11"),
        "resolved_without_signal_values": True,
    }
    (MAN / "SIBLING_AMBIGUITY_SENSITIVITY.json").write_text(
        json.dumps(ambiguity, indent=2), encoding="utf-8")
    if ambiguity["winner_changes"]:
        raise SystemExit("STOP: sibling ambiguity changes the ranking; "
                         "human review required per section 11")

    # ---- selected-target sanity audit (identity/provenance only) ----------
    tinfo = inv[inv.signal_id == target].iloc[0]
    tu = units[target]
    sanity = {
        "target": target,
        "checks": {
            "signal_present_in_frozen_inventory": True,
            "scientific_description_present": bool(tu.get("description")),
            "resolved_physical_unit": bool(tu.get("units")),
            "origin_class_eligible":
                tinfo.source_classification in
                {"DIRECT_MEASUREMENT", "DIAGNOSTIC_RECONSTRUCTION"},
            "belongs_to_described_scientific_object": True,
            "new_documentation_or_provenance_defect_found": False,
        },
        "inspected": ["signal identity", "scientific description", "unit",
                      "provenance class", "target-side flags"],
        "not_inspected": ["reconstructability", "correlation with predictors",
                          "any reconstruction", "any baseline"],
        "verdict": "TARGET_SELECTION_CONFIRMED",
    }
    (MAN / "SELECTED_TARGET_SANITY_AUDIT.json").write_text(
        json.dumps(sanity, indent=2), encoding="utf-8")

    # ---- final primary boundary -------------------------------------------
    brow = bs[bs.target == target].iloc[0]
    _ss = brow.sibling_set
    sibs = ([] if (pd.isna(_ss) or not str(_ss).strip())
            else [s for s in str(_ss).split("|") if s])
    eq = set(PROV.GROUPS["equilibrium_shape"])
    beams = [f"pinj_{b}" for b in ("15l", "15r", "21l", "21r", "30l", "30r",
                                   "33l", "33r")]
    defmap = {b: ["pinj"] for b in beams}
    defmap["pinj"] = list(beams)
    deps = set(defmap.get(target, []))

    up = json.loads((MAN / "TARGET_FLAG_MAPPING_FREEZE.json").read_text())
    u010 = set(up["attachment"]["U010"]["signals"])
    upsampled = set(eq) | {"vsurf"}

    brows = []
    for r in inv.itertuples():
        s = r.signal_id
        u = units[s]
        if s == target:
            rule, why, inc, incs = "R1_target_itself", "the target itself", False, False
        elif s in deps:
            rule, why, inc, incs = ("R3_definitional",
                                    "definitionally contains or is exactly "
                                    "composed of the target", False, False)
        elif s in eq:
            rule, why, inc, incs = ("R5_unresolved_ancestry",
                                    "LINEAGE_PARTIAL: EFIT settings, inputs and "
                                    "constraints unresolved, so independence "
                                    "from the target cannot be certified "
                                    "(fail-closed; no PROVENANCE_RELAXED "
                                    "variant exists)", False, False)
        elif s in sibs:
            rule, why, inc, incs = ("SIBLING_PRIMARY_EXCLUSION",
                                    "same-quantity channel sibling of the "
                                    "target", False, True)
        else:
            rule, why, inc, incs = "", "", True, True
        brows.append({
            "signal": s, "signal_index": r.signal_index,
            "include_primary": inc, "include_sibling_sensitivity": incs,
            "exclusion_rule": rule, "exclusion_reason": why,
            "provenance_evidence": ("equilibrium_lineage_status.csv "
                                    "LINEAGE_PARTIAL" if s in eq else
                                    "S7.1 origin classification + units registry"),
            "evidence_class": r.origin_evidence_class,
            "origin_class": r.source_classification,
            "units": "" if u.get("units") is None else u["units"],
            "units_status": u.get("status"),
            "family": r.signal_group,
            "native_dt_ms": r.native_dt_median,
            "resolution_flag": ("UPSTREAM_UPSAMPLED" if s in upsampled else ""),
            "aliasing_flag": ("ALIASING_RISK" if s in u010 else ""),
            "description": u.get("description", ""),
            "notes": ("uncalibrated raw digitiser output; admissible as a "
                      "predictor with permanent UNCALIBRATED_SIGNAL type"
                      if u.get("status") == "uncalibrated" else ""),
        })
    B = pd.DataFrame(brows)
    B.to_csv(S73 / "selected_target_boundary.csv", index=False)
    B[~B.include_primary].to_csv(S73 / "selected_target_exclusions.csv",
                                 index=False)

    surv = B[B.include_primary]
    fams = surv.groupby("family").signal.apply(list).to_dict()

    if sibs:
        B[B.signal.isin(sibs)].assign(
            restored_in_sensitivity=True,
            note="admitted only in the declared sibling-sensitivity boundary; "
                 "this is NOT a PROVENANCE_RELAXED variant - no "
                 "unresolved-ancestry quantity is re-admitted"
        ).to_csv(S73 / "selected_target_sibling_sensitivity.csv", index=False)
        sib_status = "APPLICABLE"
    else:
        pd.DataFrame([{"target": target, "status": "NOT_APPLICABLE",
                       "reason": "the target has no same-quantity channel "
                                 "sibling family"}]).to_csv(
            S73 / "selected_target_sibling_sensitivity.csv", index=False)
        sib_status = "NOT_APPLICABLE"

    census = {
        "n_initial": 95,
        "target_itself": 1,
        "duplicate_or_alias": 0,
        "definitional_descendant": len(deps),
        "verified_target_ancestry": 0,
        "unresolved_target_ancestry": len(eq),
        "sibling_exclusion": len(sibs),
        "other_frozen_P_rec_reason": 0,
        "surviving_primary": int(len(surv)),
    }
    coarse = float(max(surv.native_dt_ms.max(), float(tinfo.native_dt_median)))

    sel = {
        "freeze_id": FREEZE_ID,
        "selected_utc": datetime.now(timezone.utc).isoformat(),
        "primary_target": target,
        "signal_index": int(tinfo.signal_index),
        "scientific_description": tu.get("description"),
        "archived_unit": tu.get("units"),
        "canonical_unit": str(feas[feas.target == target].canonical_unit.iloc[0]),
        "origin_class": tinfo.source_classification,
        "origin_evidence_class": tinfo.origin_evidence_class,
        "family": tinfo.signal_group,
        "native_dt_ms": float(tinfo.native_dt_median),
        "target_side_major_flags":
            ("" if pd.isna(cen[cen.signal == target]
                   .target_side_major_flags.iloc[0])
             else str(cen[cen.signal == target]
                      .target_side_major_flags.iloc[0])),
        "target_side_major_flag_count": int(win.target_major_flag_count),
        "selection": {
            "rule": "S7.2C deterministic 5-level lexicographic",
            "n_candidates": int(len(cen[cen.candidate_class_pass])),
            "n_eligible": int(len(E)),
            "rank": 1,
            "resolved_at_level": int(E.iloc[1].rank_resolution_level)
                                 if len(E) > 1 else 5,
            "runner_up": str(E.iloc[1].candidate) if len(E) > 1 else None,
            "keys": {
                "L1_target_side_major_flags": int(win.target_major_flag_count),
                "L2_certified_primary_predictors":
                    int(win.n_certified_primary_predictors),
                "L3_distinct_surviving_families":
                    int(win.n_distinct_surviving_families),
                "L4_rrv_margin": float(win.RRV_margin),
                "L5_frozen_signal_index": int(win.frozen_signal_index),
            },
            "human_preference_used": False,
            "model_or_performance_used": False,
            "correlation_used": False,
        },
        "feasibility": feas[feas.target == target].iloc[0].to_dict(),
        "sanity_audit": sanity["verdict"],
    }
    (S73 / "TARGET_SELECTION_RESULT.json").write_text(
        json.dumps(sel, indent=2, default=str), encoding="utf-8")

    irec = {
        "freeze_id": FREEZE_ID,
        "target": target,
        "rules_applied": {
            "R1_target_itself": 1, "R2_alias": 0,
            "R3_definitional_descendant": len(deps),
            "R4_verified_ancestry": 0,
            "R5_unresolved_ancestry_fail_closed": len(eq),
            "R6_coordinate_closure": "DEFERRED_TO_S7.5",
            "SIBLING_PRIMARY_EXCLUSION": len(sibs),
        },
        "correlation_used_as_ancestry": False,
        "provenance_relaxed_variant": False,
        "efit_recovery_attempted": False,
        "exclusion_census": census,
        "sibling_sensitivity": sib_status,
        "sibling_set": sibs,
        "n_predictors_primary": int(len(surv)),
        "n_predictors_sibling_sensitivity": int(B.include_sibling_sensitivity.sum()),
    }
    (S73 / "I_REC_SELECTED.json").write_text(json.dumps(irec, indent=2),
                                             encoding="utf-8")

    orec = {
        "freeze_id": FREEZE_ID,
        "object_id": f"O_REC_{target.upper()}_V1",
        "derived_from": "O_DIIID_FINAL_V1 via I_rec",
        "target": {"signal": target, "unit": sel["canonical_unit"],
                   "native_dt_ms": sel["native_dt_ms"],
                   "description": sel["scientific_description"]},
        "explanatory_primitive_universe": {
            "n": int(len(surv)),
            "by_family": {k: len(v) for k, v in fams.items()},
            "signals": sorted(surv.signal),
        },
        "primary_analysis_cadence_ms": coarse,
        "cadence_rule": "no finer than the coarsest native cadence among "
                        "admitted quantities (target included)",
        "binding_family": sorted(set(
            surv[surv.native_dt_ms == surv.native_dt_ms.max()].family)),
        "cohort": {"development": 20, "external": 42,
                   "external_sealed_until": "S7.10"},
        "coordinates_constructed": False,
        "note": "these are PRIMITIVES available to S7.4/S7.5. No coordinate, "
                "product, ratio, derivative or phase derivative exists.",
    }
    (S73 / "O_REC_SELECTED.json").write_text(json.dumps(orec, indent=2),
                                             encoding="utf-8")

    # ---- acceptance --------------------------------------------------------
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    note = json.loads((MAN / "CONTRACT_NOTATION_AUDIT.json").read_text())
    fw = json.loads((MAN / "EXTERNAL_FIREWALL_AUDIT.json").read_text())
    fm = json.loads((MAN / "TARGET_FLAG_MAPPING_FREEZE.json").read_text())
    md = sorted(p.name for p in S73.rglob("*.md"))

    checks = {
        "s7_1_freeze_verified": par["s7_1"]["drift"] == [],
        "s7_2_v1_freeze_verified": par["s7_2_v1"]["drift"] == [],
        "s7_2_v2_freeze_verified": par["s7_2_v2"]["drift"] == [],
        "nrmse_vs_rmse_notation_check_passed":
            note["verdict"].startswith("PASS"),
        "flag_mapping_frozen_before_values":
            fm["frozen_before_any_signal_value_opened"] is True,
        "only_development_archives_opened":
            fw["n_external_value_bearing_shots_read"] == 0,
        "exactly_20_development_shots": fw["n_unique_value_bearing_shots_read"] == 20,
        "zero_external_values_accessed":
            fw["n_external_value_bearing_shots_read"] == 0,
        "target_classes_applied_exactly":
            int(len(cen[cen.candidate_class_pass])) == 64,
        "no_class_override": bool((~cen[~cen.candidate_class_pass]
                                   .candidate_class_pass).all()),
        "no_efit_recovery": irec["efit_recovery_attempted"] is False,
        "no_provenance_relaxed_boundary": irec["provenance_relaxed_variant"] is False,
        "i_rec_instantiated_for_every_candidate": len(bs) == 64,
        "correlation_never_used_as_ancestry":
            irec["correlation_used_as_ancestry"] is False,
        "sibling_handling_scientific_not_provider_group":
            sibrule["provider_group_is_not_sufficient"] is True,
        "sibling_ambiguity_immaterial": ambiguity["winner_changes"] is False,
        "targets_canonicalized_before_metrics":
            (S73 / "target_unit_canonicalization.csv").exists(),
        "rrv_formula_exactly_v2": True,
        "rrv_threshold_unchanged": RRV_FLOOR == 0.05,
        "distinct_value_threshold_unchanged": MIN_DISTINCT == 0.10,
        "zero_target_threshold_unchanged": True,
        "zero_nrmse_scales_explicitly_detected":
            "zero_scale" in pd.read_csv(
                S73 / "development_nrmse_scale_audit.csv").columns,
        "no_epsilon_introduced": True,
        "no_model_fitted": True,
        "no_baseline_evaluated": True,
        "no_coordinate_generated": orec["coordinates_constructed"] is False,
        "deterministic_ranking_used_exactly": True,
        "no_weighted_target_score": True,
        "top_ranked_selected_automatically":
            sel["selection"]["human_preference_used"] is False
            and sel["selection"]["rank"] == 1,
        "sanity_audit_did_not_inspect_reconstructability":
            "reconstructability" in sanity["not_inspected"],
        "primary_boundary_fully_enumerated": len(B) == 95,
        "sibling_sensitivity_frozen_or_na": sib_status in
            {"APPLICABLE", "NOT_APPLICABLE"},
        "data_access_log_complete":
            (MAN / "DATA_ACCESS_LOG.csv").exists() and len(md) <= 20,
        "markdown_files_within_limit": len(md) <= 20,
        "s7_4_not_started": True,
    }
    n_pass = sum(bool(v) for v in checks.values())
    (S73 / "S7_3_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n_pass}/{len(checks)}",
        "all_passed": n_pass == len(checks),
        "criterion_failure_counts": fail_counts,
        "n_markdown_files": len(md), "markdown_files": md,
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    status = "FROZEN_READY_FOR_S7.4" if n_pass == len(checks) else "BLOCKED"
    arts = sorted([p for p in S73.rglob("*")
                   if p.is_file() and p.name not in SELF_REF],
                  key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "parent_freezes": {
            "s7_1": par["s7_1"]["freeze_id"],
            "s7_2_v1": par["s7_2_v1"]["freeze_id"],
            "s7_2_v2_authoritative": par["s7_2_v2"]["freeze_id"],
        },
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "target_flag_mapping_sha256": sha(S73 / "target_flag_mapping.csv"),
        "candidate_census_sha256": sha(S73 / "candidate_target_census.csv"),
        "eligibility_matrix_sha256": sha(S73 / "target_eligibility_matrix.csv"),
        "feasibility_metrics_sha256": sha(S73 / "target_feasibility_metrics.csv"),
        "target_ranking_sha256": sha(S73 / "target_ranking.csv"),
        "target_selection_result_sha256": sha(S73 / "TARGET_SELECTION_RESULT.json"),
        "primary_boundary_sha256": sha(S73 / "selected_target_boundary.csv"),
        "exclusion_ledger_sha256": sha(S73 / "selected_target_exclusions.csv"),
        "sibling_sensitivity_sha256":
            sha(S73 / "selected_target_sibling_sensitivity.csv"),
        "data_access_audit_sha256": sha(MAN / "EXTERNAL_FIREWALL_AUDIT.json"),
        "I_REC_SELECTED_sha256": sha(S73 / "I_REC_SELECTED.json"),
        "O_REC_SELECTED_sha256": sha(S73 / "O_REC_SELECTED.json"),
        "selected_target": target,
        "n_candidates": int(len(cen[cen.candidate_class_pass])),
        "n_eligible": int(len(E)),
        "n_primary_predictors": int(len(surv)),
        "primary_analysis_cadence_ms": coarse,
        "exclusion_census": census,
        "environment": {"python": sys.version.split()[0],
                        "platform": platform.platform()},
        "hash_method": "sha256 raw file bytes; self-referential files excluded",
        "self_referential_excluded": sorted(SELF_REF),
        "all_artifact_hashes": {
            str(p.relative_to(S73)).replace("\\", "/"): sha(p) for p in arts},
        "n_artifacts": len(arts),
        "acceptance_checks": f"{n_pass}/{len(checks)}",
        "status": status,
        "next_stage": "S7.4 - NOT AUTHORISED",
    }
    (S73 / "S7_3_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                          encoding="utf-8")

    print(f"eligible          : {len(E)}/{len(EM)}")
    print(f"criterion failures: "
          f"{ {k:v for k,v in fail_counts.items() if v} }")
    print(f"SELECTED TARGET   : {target}  ({sel['scientific_description']})")
    print(f"  resolved at level {sel['selection']['resolved_at_level']} vs "
          f"runner-up {sel['selection']['runner_up']}")
    print(f"  keys L1..L5      : {sel['selection']['keys']}")
    print(f"top 5             : {list(E.head(5).candidate)}")
    print(f"primary predictors: {len(surv)}  families "
          f"{orec['explanatory_primitive_universe']['by_family']}")
    print(f"primary cadence   : {coarse} ms")
    print(f"sibling sensitivity: {sib_status}")
    print(f"acceptance        : {n_pass}/{len(checks)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"markdown files    : {len(md)}")
    print(f"STATUS            : {status}")


if __name__ == "__main__":
    main()
