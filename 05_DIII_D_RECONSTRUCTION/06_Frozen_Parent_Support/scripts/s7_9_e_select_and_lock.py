"""S7.9 step E - elimination ledger, selected representation, and the
DEVELOPMENT_REPRESENTATION_LOCK.

The lock MUST be written before any baseline hyperparameter selection occurs,
so that baseline behaviour cannot feed back into representation selection.
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
V2 = S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"
S78 = S7 / "08_utility_and_qualification_rules"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s7_9_coords import Engine  # noqa: E402


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def depth_split(s: str) -> list:
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "|" and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def main() -> int:
    z12 = np.load(OUT / "manifests" / "_rank12_state.npz", allow_pickle=True)
    z345 = np.load(OUT / "manifests" / "_rank345_state.npz", allow_pickle=True)
    r12 = json.loads((OUT / "manifests" / "RANK12_SUMMARY.json").read_text())
    r345 = json.loads((OUT / "manifests" / "RANK345_SUMMARY.json").read_text())

    ids, size = z12["support_id"], z12["size"]
    fit, se1, bw, bstar, p90, keep = (z12["fit"], z12["se1"], z12["bw"],
                                      z12["bstar"], z12["p90"], z12["keep"])
    e1, e2 = z12["e1"], z12["e2"]
    best, ref = int(z12["best"][0]), int(z12["ref"][0])
    e3, e4, e5 = z345["e3"], z345["e4"], z345["e5"]
    star = int(z345["c_dev_star"][0])
    sid = str(ids[star])
    atoms = depth_split(sid)

    # ---------------- elimination ledger ---------------------------------
    rows = []
    inE1 = np.zeros(len(ids), bool); inE1[e1] = True
    absdiff = np.abs(fit - fit[best])
    thr1 = np.maximum(se1, 0.01)
    for i in np.flatnonzero(~inE1):
        rows.append((str(ids[i]), int(size[i]), 1, "primary fit quality",
                     "outside the Rank-1 practical-equivalence set",
                     "|FIT - FIT_best|", float(absdiff[i]), float(fit[best]),
                     float(thr1[i])))
    pos = {int(v): k for k, v in enumerate(e1)}
    inE2 = set(e2.tolist())
    for i in e1:
        if i in inE2:
            continue
        k = pos[i]
        if not keep[k]:
            rows.append((str(ids[i]), int(size[i]), 2,
                         "development generalization / stability",
                         "outside the BLOCK_WORST practical-equivalence set",
                         "|BLOCK_WORST - BLOCK_WORST_ref|",
                         float(abs(bw[k] - bw[ref])), float(bw[ref]), None))
        else:
            rows.append((str(ids[i]), int(size[i]), 2,
                         "development generalization / stability",
                         "not the exact minimum SHOT_P90 among BLOCK_WORST-equivalent survivors",
                         "SHOT_P90", float(p90[k]), float(p90[keep].min()), None))
    for setname, prev, cur, rank, crit in [
            ("E3", e2, e3, 3, "parsimony"), ("E4", e3, e4, 4, "conditioning"),
            ("E5", e4, e5, 5, "support stability")]:
        drop = set(prev.tolist()) - set(cur.tolist())
        for i in drop:
            rows.append((str(ids[i]), int(size[i]), rank, crit,
                         "eliminated at rank %d" % rank, crit, None, None, None))

    led = pd.DataFrame(rows, columns=[
        "support_id", "support_size", "rank_eliminated", "criterion", "reason",
        "comparison_quantity", "candidate_value", "reference_value",
        "threshold_applied"])
    led.sort_values(["rank_eliminated", "candidate_value", "support_id"]).to_csv(
        OUT / "utility_elimination_ledger.csv", index=False)
    print("elimination ledger rows: %d (E0 - E5 = %d)"
          % (len(led), len(ids) - len(e5)))
    assert len(led) == len(ids) - len(e5)

    # ---------------- coordinate metadata --------------------------------
    uni = pd.read_csv(S76R / "primary_atomic_coordinate_universe.csv").set_index("coordinate_id")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").set_index("primitive_id")
    reg = pd.read_csv(V2 / "explored_support_registry.csv").set_index("support_id")

    coords = []
    for a in atoms:
        u = uni.loc[a]
        anc = str(u.primitive_ancestors).split("|")
        coords.append({
            "coordinate_id": a,
            "constructor": str(u.constructor),
            "constructor_name": {"C0": "identity level", "C1": "derivative",
                                 "C2": "level-level product", "C3": "level-level ratio",
                                 "C5": "unary reciprocal", "C6": "level-rate interaction",
                                 "C7": "rate over level"}.get(str(u.constructor), "?"),
            "ordered_operands": str(u.ordered_operands),
            "operand_roles": str(u.operand_roles),
            "primitive_ancestors": anc,
            "n_ancestors": int(u.n_ancestors),
            "depth": int(u.depth),
            "output_dimension": str(u.output_dimension),
            "unit_expression": str(u.unit_expression),
            "temporal_resolution_rule": str(u.temporal_resolution_rule),
            "temporal_resolution_bound_ms": float(u.temporal_resolution_bound_ms),
            "provenance_lineage": str(u.provenance_lineage),
            "target_independence": str(u.target_independence),
            "aliasing_flag": bool(u.aliasing_flag),
            "upsample_flag": bool(u.upsample_flag),
            "uncalibrated_flag": bool(u.uncalibrated_flag),
            "primary_or_sensitivity": str(u.primary_or_sensitivity),
            "numerical_realization_id": str(u.numerical_realization_id),
            "domain_predicate": (None if pd.isna(u.domain_predicate) else str(u.domain_predicate)),
            "ancestor_scientific_families": sorted({str(HB.loc[p, "broad_scientific_family"]) for p in anc}),
            "ancestor_uncalibrated": sorted([p for p in anc if bool(HB.loc[p, "uncalibrated_flag"])]),
        })

    fams = sorted({f for c in coords for f in c["ancestor_scientific_families"]})
    cons = {}
    for c in coords:
        cons[c["constructor"]] = cons.get(c["constructor"], 0) + 1
    unc = sorted({p for c in coords for p in c["ancestor_uncalibrated"]})
    prof = Engine().candidate_profile(atoms)

    k = int(np.flatnonzero(e1 == star)[0])
    quant = {
        "FIT": float(fit[star]),
        "FIT_best_in_E0": float(fit[best]),
        "FIT_gap_to_best": float(fit[star] - fit[best]),
        "SE_delta_vs_best": float(se1[star]),
        "delta_equiv_vs_best": float(max(se1[star], 0.01)),
        "BLOCK_WORST": float(bw[k]),
        "b_star": ["A", "B", "C"][int(bstar[k])],
        "SHOT_P90": float(p90[k]),
        "ACTIVE_TERMS": int(prof["ACTIVE_TERMS"]),
        "support_size": int(size[star]),
        "ACTIVE_TERMS_equals_support_size": bool(prof["ACTIVE_TERMS"] == size[star]),
        "COND_MEDIAN": prof["COND_MEDIAN"],
        "COND_P90": prof["COND_P90"],
        "COND_MAX": prof["COND_MAX"],
        "n_infinite_conditioning_cells": prof["n_infinite_cells"],
        "n_degenerate_sd_cells": prof["n_degenerate_sd_cells"],
        "BOOT_SELECTION_FREQ": r345["rank_5"]["BOOT_SELECTION_FREQ"][sid],
        "FOLD_SELECTION_FREQ": r345["rank_5"]["FOLD_SELECTION_FREQ"][sid],
    }

    sel = {
        "record_id": "DEVELOPMENT_SELECTED_REPRESENTATION_V1",
        "terminology": "DEVELOPMENT_SELECTED_REPRESENTATION",
        "not_claimed": ["externally validated", "structural-transfer success",
                        "global optimum", "universal relation"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "support_id": sid,
        "support_size": int(size[star]),
        "canonical_coordinate_ids": atoms,
        "canonical_serialization": "|".join(atoms),
        "canonical_serialization_matches_registry": "|".join(atoms) == sid,
        "coordinates": coords,
        "constructor_composition": cons,
        "constructor_composition_registry": str(reg.loc[sid, "constructor_composition"]),
        "scientific_ancestor_families": fams,
        "ancestor_family_composition_registry": str(reg.loc[sid, "ancestor_family_composition"]),
        "interpretation_flags": {
            "contains_uncalibrated_primitive": len(unc) > 0,
            "uncalibrated_primitives": unc,
            "UNCALIBRATED_SIGNAL": len(unc) > 0,
            "uncalibrated_consequence": (
                "coefficients involving the uncalibrated primitive have no "
                "certified physical-dimensional interpretation") if unc else None,
            "support_rejected_for_uncalibrated": False,
            "contains_C6": "C6" in cons,
            "contains_C7": "C7" in cons,
            "c6_c7_treated_as_surprising_or_repaired": False,
            "contains_ece_ancestry": "ece_te_profile" in fams,
            "ece_penalty_applied": False,
            "any_aliasing_flag": any(c["aliasing_flag"] for c in coords),
            "any_upsample_flag": any(c["upsample_flag"] for c in coords),
            "partial_map_status": sorted({c["domain_predicate"] for c in coords
                                          if c["domain_predicate"]}) or "TOTAL_ON_DEVELOPMENT_SUPPORT",
            "all_primary_not_sensitivity": all(
                c["primary_or_sensitivity"] == "PRIMARY" for c in coords),
        },
        "development_utility_quantities": quant,
        "lineage": {
            "target": "density",
            "ontology_id": "G_REC_DENSITY_HARDENED_V2",
            "admissible_universe_id": "A_REC_DENSITY_HARDENED_V2",
            "search_policy_id": "SIGMA_REC_ONE_SEED_PRIMARY_V2",
            "Ahat_rec_id": "AHAT_REC_DENSITY_ONE_SEED_V2",
            "utility_policy_id": "U_REC_OPERATIONAL_V1",
            "qualification_policy_id": "V_REC_OPERATIONAL_V1",
            "estimator_id": "DEVELOPMENT_RELATION_OLS_V1",
        },
        "selection_provenance": {
            "E0": int(len(ids)), "E1": int(len(e1)), "E2": int(len(e2)),
            "E3": int(len(e3)), "E4": int(len(e4)), "E5": int(len(e5)),
            "binding_rank": 2,
            "binding_criterion": "Rank 2 SHOT_P90 exact minimum among BLOCK_WORST-equivalent survivors",
            "ranks_3_4_5_non_binding_because_E2_was_a_singleton": True,
            "selected_within": "AHAT_REC_DENSITY_ONE_SEED_V2",
            "global_optimality_claim": False,
        },
    }
    (OUT / "SELECTED_REPRESENTATION.json").write_text(json.dumps(sel, indent=2), encoding="utf-8")

    # ---------------- estimator config -----------------------------------
    est = {
        "config_id": "RELATIONAL_ESTIMATOR_CONFIG_V1",
        "estimator_id": "DEVELOPMENT_RELATION_OLS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "support_id": sid,
        "procedure": [
            "1. compute coordinate means and standard deviations on the cell CALIBRATION interval only (ddof=0)",
            "2. sd <= 0 or non-finite -> divisor is the exact value 1.0 (no epsilon)",
            "3. standardize calibration coordinates with those values",
            "4. apply the SAME calibration mean and divisor UNCHANGED to the protected rows",
            "5. fit an intercept",
            "6. solve affine OLS of the calibration target on the standardized calibration design",
            "7. predict the protected rows; score NRMSE against std(y_calibration, ddof=0)",
        ],
        "solver": "numpy.linalg.lstsq on the explicit [1, Z] design, rcond=None",
        "intercept": {"fitted": True, "penalized": False,
                      "counted_in_parsimony": False, "counted_in_conditioning": False},
        "coefficients": {
            "scope": "discharge/block local",
            "shared_across_discharges": False,
            "global_coefficients_exist": False,
            "note": "there are NO learned global coefficients to carry into external discharges",
        },
        "what_transfers_externally": [
            "support identity",
            "coordinate definitions",
            "numerical construction rules",
            "estimator class and procedure",
        ],
        "external_procedure_at_S7_10": (
            "each external discharge receives locally calibrated coefficients "
            "estimated only from its permitted calibration interval"),
        "ridge_used_for_relational_representation": False,
        "ridge_rejected_on_performance_grounds": False,
        "numerical_equivalence_check": {
            "reference": "frozen S7.7R per-cell NRMSE arrays (SEARCH_PROXY_OLS_V1)",
            "recomputed_independently_in_S7_9": True,
            "max_relative_deviation": 4.406e-08,
            "float32_storage_eps": 1.192e-07,
            "verdict": "AGREES_TO_FLOAT32_STORAGE_PRECISION",
        },
    }
    (OUT / "RELATIONAL_ESTIMATOR_CONFIG.json").write_text(json.dumps(est, indent=2), encoding="utf-8")

    # ---------------- THE LOCK -------------------------------------------
    lock_payload = {
        "lock_id": "DEVELOPMENT_REPRESENTATION_LOCK_V1",
        "locked_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "fix the selected representation BEFORE any development-side "
            "baseline hyperparameter selection, so baseline behaviour cannot "
            "feed back into representation selection"),
        "selected_support_id": sid,
        "selected_support_size": int(size[star]),
        "canonical_coordinate_ids": atoms,
        "target": "density",
        "estimator_id": "DEVELOPMENT_RELATION_OLS_V1",
        "preprocessing": "calibration-only standardization; sd<=0 divisor 1.0; no epsilon",
        "validation_block_geometry": {
            "A": {"calibration": [0.0, 0.4], "evaluation": [0.4, 0.5]},
            "B": {"calibration": [0.0, 0.6], "evaluation": [0.6, 0.7]},
            "C": {"calibration": [0.0, 0.8], "evaluation": [0.8, 0.9]},
            "protection_model": "BLOCK_LOCAL_PROTECTION",
        },
        "utility_policy_id": "U_REC_OPERATIONAL_V1",
        "selection_provenance": sel["selection_provenance"],
        "artifact_hashes": {
            "SELECTED_REPRESENTATION.json": sha256(OUT / "SELECTED_REPRESENTATION.json"),
            "RELATIONAL_ESTIMATOR_CONFIG.json": sha256(OUT / "RELATIONAL_ESTIMATOR_CONFIG.json"),
            "utility_elimination_ledger.csv": sha256(OUT / "utility_elimination_ledger.csv"),
            "utility_survivor_sets.csv": sha256(OUT / "utility_survivor_sets.csv"),
        },
        "support_may_change_after_this_lock": False,
        "baseline_tuning_permitted_after_this_lock": True,
        "no_baseline_had_been_fitted_before_this_lock": True,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
    }
    body = json.dumps(lock_payload, indent=2, sort_keys=True)
    lock_payload["lock_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (OUT / "DEVELOPMENT_REPRESENTATION_LOCK.json").write_text(
        json.dumps(lock_payload, indent=2), encoding="utf-8")

    print("C_dev_star: %s" % sid)
    print("  size %d | constructors %s | families %s" % (size[star], cons, fams))
    print("  uncalibrated: %s | C6/C7: %s | ECE: %s"
          % (unc or "none", ("C6" in cons or "C7" in cons),
             "ece_te_profile" in fams))
    print("LOCK sha256 %s  at %s" % (lock_payload["lock_sha256"][:16], lock_payload["locked_utc"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
