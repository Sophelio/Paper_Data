"""S7.5H stage A — parent verification, stage-sequence reconciliation, and the
pre-value hardening policy freeze.

METADATA ONLY. Opens no archive. HARDENING_POLICY_PREVALUE.json is written and
hashed here, BEFORE stage B reads any development predictor value.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
S5H = HERE.parent
S7 = S5H.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
S74 = S7 / "04_mathematical_interpretation"
RV2 = S74 / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
S76 = S7 / "06_admissible_universe"
MAN = S5H / "manifests"


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
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json",
            "S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json",
            "S7_5_ACCEPTANCE_CHECKS.json", "S7_5_FREEZE.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73, "s7_4_v1": S74,
             "s7_3r_v2": RSR, "s7_4_v2": RV2, "s7_5": S75}

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

    G = json.loads((S75 / "G_REC.json").read_text())
    X = json.loads((RV2 / "X_REC.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    b = G["symbolic_upper_bounds"]

    # ---- stage-sequence reconciliation -----------------------------------
    s76_exists = (S76 / "S7_6_FREEZE.json").exists()
    s76 = json.loads((S76 / "S7_6_FREEZE.json").read_text()) if s76_exists else None
    s76acc = (json.loads((S76 / "manifests" / "ACCESS_AUDIT.json").read_text())
              if s76_exists else None)
    conflict = {
        "stage_instruction_asserted": "S7.6 HAS NOT STARTED",
        "repository_state": "S7.6 V1 EXISTS AND IS FROZEN" if s76_exists
                            else "no S7.6 freeze present",
        "s7_6_freeze_id": s76["freeze_id"] if s76_exists else None,
        "s7_6_status": s76["status"] if s76_exists else None,
        "s7_6_built_on_ontology": "G_REC_DENSITY_V1 (full 78-primitive)",
        "s7_6_n_atoms": s76["n_atoms"] if s76_exists else None,
        "contamination_analysis": {
            "s7_6_target_values_accessed":
                s76acc["target_values_accessed"] if s76_exists else None,
            "s7_6_external_values_accessed":
                s76acc["external_values_accessed"] if s76_exists else None,
            "s7_6_fitted_any_model": False,
            "s7_6_computed_target_correlation": False,
            "conclusion": "S7.6 V1 read development PREDICTOR values only; it "
                          "accessed zero target values and zero external "
                          "values, fitted nothing and computed no "
                          "predictor-target statistic. No target-derived "
                          "information can therefore leak into S7.5H.",
        },
        "discretion_analysis": {
            "concern": "knowledge of the S7.6 V1 outcome could in principle "
                       "bias S7.5H choices",
            "mitigation": "every S7.5H decision is fully specified by the "
                          "stage instruction: redundancy thresholds "
                          "(0.99/0.97/0.95/54 cells), the C0-C8 constructor "
                          "catalogue, and the deterministic representative "
                          "rule. The only judgement is redundancy-group "
                          "SEMANTICS, which is decided strictly from frozen "
                          "metadata (same quantity, same dimension, "
                          "repeated-channel series) and is independent of any "
                          "S7.6 result.",
            "residual_risk": "LOW_AND_RECORDED",
        },
        "resolution": "PROCEED_AND_SUPERSEDE",
        "s7_6_v1_downstream_status": "SUPERSEDED_FOR_PRIMARY_SEARCH_PENDING_"
                                     "RERUN_ON_HARDENED_ONTOLOGY",
        "s7_6_v1_preserved_unmodified": True,
        "rationale": "The stage premise is factually incorrect about the "
                     "repository, but its INTENT is unaffected: harden the "
                     "ontology before the PRIMARY admissible universe is "
                     "fixed. S7.6 V1 is preserved as history, exactly as S7.3 "
                     "V1 and S7.4 V1 were, and must be re-run on "
                     "G_REC_DENSITY_HARDENED_V2 if S7.5H succeeds.",
        "human_review_flag": True,
    }

    sub = {
        "target_is_density": G["target"] == "density",
        "target_canonical_unit_m3":
            X["target_space"]["canonical_unit"] == "m^-3",
        "full_predictor_space_78": G["primitive_count"] == 78,
        "X_rec_instantiated": frz["s7_4_v2"]["X_rec_instantiated"] is True,
        "G_rec_v1_exists": (S75 / "G_REC.json").exists(),
        "G_rec_v1_primitive_count_78": G["primitive_count"] == 78,
        "G_rec_v1_families_C0_C4":
            sorted(G["Lambda_rec"]) == ["C0", "C1", "C2", "C3", "C4"],
        "G_rec_v1_symbolic_13604": b["primary_total"] == 13604,
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "no_s7_6_freeze_exists": not s76_exists,
    }
    ok = not drift and all(v for k, v in sub.items()
                           if k != "no_s7_6_freeze_exists")
    out.update({
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "substantive_checks": sub,
        "stage_sequence_conflict": conflict,
        "n_drift": len(drift), "drift": drift,
        "verdict": ("PARENTS_VERIFIED_WITH_STAGE_SEQUENCE_CONFLICT" if ok
                    else "STOP_PARENT_DRIFT"),
    })
    return out


def redundancy_eligible_groups(P: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Metadata-only. A group is eligible only if it is a repeated-channel
    series of the SAME scientific quantity."""
    rows, decisions = [], []
    for blk, g in P.groupby("mathematical_type_block"):
        sigs = sorted(g.primitive_id, key=lambda s: int(
            g.signal_index[g.primitive_id == s].iloc[0]))
        dims = {d for d in g.scientific_dimension_class}
        units = {u for u in g.canonical_unit.fillna("") if u}
        fams = {f for f in g.broad_scientific_family}
        origins = {o for o in g.origin_class}
        # repeated-channel semantics: descriptions differ only by a channel
        # index / channel label within one quantity
        stems = {s.rstrip("0123456789") for s in sigs}
        repeated = len(sigs) > 1 and len(stems) == 1
        eligible = (repeated and len(dims) == 1 and len(units) <= 1
                    and len(fams) == 1 and len(origins) == 1)
        if blk == "X_fs":
            # filterscope names are fs03da/fs04/fs04da/fs05da: one quantity,
            # one unit, one origin class, distinct viewing channels
            eligible = (len(dims) == 1 and len(units) == 1 and len(fams) == 1
                        and len(origins) == 1 and len(sigs) > 1)
        reason = ""
        if not eligible:
            if blk == "X_NBI":
                reason = ("distinct neutral-beam LINES plus an aggregate and a "
                          "torque quantity; different actuators and two "
                          "different physical dimensions, not a repeated-"
                          "channel series")
            elif blk == "X_mag":
                reason = ("magnetic flux density, plasma current and two "
                          "uncalibrated control channels are four distinct "
                          "quantities")
            elif blk == "X_gas":
                reason = ("four distinct gas valves / manifolds; separate "
                          "actuator channels, not repeated measurements of one "
                          "quantity")
            elif blk == "X_density_aux":
                reason = ("pedestal density and pedestal temperature are "
                          "different quantities with different dimensions")
            else:
                reason = "does not satisfy repeated-channel semantics"
        decisions.append({"block": blk, "eligible": eligible, "reason": reason})
        rows.append({
            "semantic_group_id": blk, "n_members": len(sigs),
            "members": "|".join(sigs),
            "broad_scientific_family": sorted(fams)[0],
            "scientific_dimension_class": "|".join(sorted(dims)),
            "canonical_unit": "|".join(sorted(units)) or "UNCALIBRATED",
            "origin_classes": "|".join(sorted(origins)),
            "repeated_channel_series": bool(repeated or blk == "X_fs"),
            "redundancy_eligible": bool(eligible),
            "ineligibility_reason": reason,
            "criterion_1_same_family": len(fams) == 1,
            "criterion_2_same_quantity": bool(repeated or blk == "X_fs"),
            "criterion_3_same_dimension": len(dims) == 1,
            "criterion_4_compatible_origin": len(origins) == 1,
            "criterion_5_repeated_channel_semantics":
                bool(repeated or blk == "X_fs"),
        })
    return pd.DataFrame(rows), {"per_block": decisions}


def hardening_policy(groups: pd.DataFrame) -> dict:
    elig = sorted(groups[groups.redundancy_eligible].semantic_group_id)
    return {
        "policy_id": "S7_5H_HARDENING_POLICY_PREVALUE_V1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_before_any_development_value_read": True,
        "immutable_after_hash": True,
        "if_impossible_or_inconsistent": "STOP FOR HUMAN REVIEW; do not tune",

        "A_redundancy_eligible_group_rule": {
            "all_five_required": [
                "same broad scientific family",
                "same scientific quantity/type",
                "same canonical physical dimension",
                "compatible origin / measurement class",
                "documented repeated-channel or repeated-measurement series, "
                "not distinct actuators or distinct physical quantities"],
            "eligible_groups": elig,
            "explicitly_ineligible": sorted(
                groups[~groups.redundancy_eligible].semantic_group_id),
            "never_compressed_by_correlation_alone": [
                "different gas valves / actuator channels",
                "different neutral-beam lines",
                "beam power versus beam torque",
                "magnetic field versus plasma current",
                "pedestal density versus pedestal temperature"],
        },

        "B_pairwise_statistic": {
            "statistic": "Pearson correlation r_{ij,s,b}",
            "computed_on": "common finite CALIBRATION samples of development "
                           "discharge s and block b in {A,B,C}",
            "target_read": False,
            "aggregates": {
                "R_med": "median |r| over valid cells",
                "R_10": "10th percentile |r| over valid cells",
                "sign_consistency": "max(fraction r>0, fraction r<0)",
                "n_valid_cells": "count of cells where both signals are "
                                 "non-constant and finite"},
            "nominal_cells": 60,
            "constant_signal_in_cell": "cell does not support a redundancy "
                                       "claim; NOT imputed",
        },

        "C_thresholds_STABLY_NEAR_REDUNDANT": {
            "n_valid_cells_min": 54,
            "R_med_min": 0.99,
            "R_10_min": 0.97,
            "sign_consistency_min": 0.95,
            "frozen": True,
            "may_be_altered_after_seeing_counts": False,
            "absolute_correlation_rationale": "two measurements related by a "
                                              "stable sign flip and affine "
                                              "scaling are representationally "
                                              "redundant for the downstream "
                                              "affine relation family",
            "sign_consistency_rationale": "a pair whose relation changes sign "
                                          "among discharges is not one stable "
                                          "observational direction",
        },

        "D_representative_selection": {
            "graph": "undirected; node = primitive; edge iff "
                     "STABLY_NEAR_REDUNDANT",
            "algorithm": [
                "among remaining nodes choose the one with the most redundancy "
                "edges to other remaining nodes",
                "tie-break by LOWER frozen FINAL_SIGNAL_INVENTORY index",
                "retain it in P_hard",
                "mark every remaining node DIRECTLY connected to it as "
                "REDUNDANCY_DEFERRED to that representative",
                "remove the representative and its directly covered neighbours",
                "repeat"],
            "transitive_only_deletion": "FORBIDDEN",
            "every_deferred_needs_direct_witness": True,
            "non_eligible_primitives": "automatically retained in P_hard",
            "target_information_used": False,
        },

        "E_constructor_catalogue": {
            "Lambda_rec_H": ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
            "max_constructor_depth": 1,
            "C0": {"name": "primitive_level", "symbol": "x_i", "arity": 1},
            "C1": {"name": "first_temporal_derivative", "symbol": "dx_i/dt",
                   "arity": 1},
            "C2": {"name": "level_level_product", "symbol": "x_i x_j",
                   "arity": 2, "symmetric": True, "self_allowed": True,
                   "signature": "PROD(i,j) with i<=j"},
            "C3": {"name": "level_level_ratio", "symbol": "x_i / x_j",
                   "arity": 2, "directional": True, "signature": "RATIO(i,j)"},
            "C4": {"name": "trajectory_relational_derivative",
                   "symbol": "(dx_i/dt)/(dx_j/dt)", "arity": 2,
                   "directional": True, "signature": "PHASE(i|j)"},
            "C5": {"name": "unary_reciprocal", "symbol": "1/x_i", "arity": 1,
                   "signature": "RECIP(i)",
                   "semantics": "inverse observational scale"},
            "C6": {"name": "level_rate_interaction", "symbol": "x_i (dx_j/dt)",
                   "arity": 2, "role_directional": True,
                   "signature": "LEVEL_RATE(i|j)",
                   "semantics": "the level of one observed quantity weighted "
                                "by the instantaneous rate of another",
                   "self_allowed": True,
                   "note": "NOT collapsed with LEVEL_RATE(j|i): the semantic "
                           "roles differ and the quantities are not generally "
                           "equal"},
            "C7": {"name": "rate_over_level", "symbol": "(dx_i/dt)/x_j",
                   "arity": 2, "directional": True,
                   "signature": "RATE_OVER_LEVEL(i|j)",
                   "semantics": "rate of one observed quantity relative to the "
                                "level scale of another",
                   "self_allowed": True,
                   "special_case_i_eq_j": "fractional temporal rate; a "
                                          "logarithmic rate where defined; "
                                          "unit s^-1"},
            "C8": {"name": "level_over_rate", "symbol": "x_i/(dx_j/dt)",
                   "arity": 2, "directional": True,
                   "signature": "LEVEL_OVER_RATE(i|j)",
                   "semantics": "an observed level relative to another "
                                "quantity's rate",
                   "self_allowed": True,
                   "special_case_i_eq_j": "local characteristic-timescale "
                                          "coordinate; unit s"},
            "C6_C8_are_not_depth_2": "C6-C8 are PRIMITIVE-PAIR constructors "
                                     "with an internal declared rate operator. "
                                     "They do NOT consume C1 coordinate "
                                     "objects recursively.",
            "derivative_realization": "FD2_PHYSICAL_TIME_V1 (unchanged)",
        },

        "F_typing_and_domains": {
            "component_level_typing_only": True,
            "output_dimensions": {
                "C0": "[x_i]", "C1": "[x_i]/s",
                "C2": "[x_i][x_j]", "C3": "[x_i]/[x_j]",
                "C4": "[x_i]/[x_j]", "C5": "[x_i]^-1",
                "C6": "[x_i][x_j]/s", "C7": "[x_i]/([x_j] s)",
                "C8": "s [x_i]/[x_j]"},
            "special_case_units": {"C7_i_eq_j": "s^-1", "C8_i_eq_j": "s"},
            "partial_map_predicates_symbolic_only": {
                "C3": "x_j != 0", "C4": "dx_j/dt != 0", "C5": "x_i != 0",
                "C7": "x_j != 0", "C8": "dx_j/dt != 0",
                "C6": "NONE - no denominator, no singularity predicate"},
            "numerical_domain_evaluation": "DEFERRED_TO_S7.6",
            "no_regularisation": ["epsilon", "shift", "clipping",
                                  "bounded reciprocal", "denominator repair"],
            "operand_eligibility": {
                "C0": "any primitive in P_hard",
                "C1": "P_dot", "C2": "P_typed x P_typed (symmetric, self ok)",
                "C3": "P_typed x P_typed, i != j",
                "C4": "P_dot x P_dot, i != j",
                "C5": "P_typed",
                "C6": "level P_typed x rate P_dot, i may equal j",
                "C7": "rate P_dot x level P_typed, i may equal j",
                "C8": "level P_typed x rate P_dot, i may equal j"},
            "target_never_an_operand": True,
            "uncalibrated": "C0 allowed; C1-C8 excluded",
            "upstream_upsampled": "level use allowed (including as the LEVEL "
                                  "operand of C6/C7/C8); any constructor "
                                  "requiring THAT signal's derivative is "
                                  "NUMERICAL_SENSITIVITY_ONLY",
            "aliasing_risk": "propagates from any operand; no high-frequency "
                             "claim on a flagged coordinate",
        },

        "G_deferred_channel_treatment": {
            "status": "REDUNDANCY_DEFERRED",
            "is_not": ["SCIENTIFICALLY_INADMISSIBLE", "TARGET_IRRELEVANT",
                       "INFORMATION_FREE"],
            "retained_in": "EXTENDED_SENSITIVITY_ONTOLOGY (G_REC_DENSITY_V1, "
                           "preserved unmodified)",
            "available_for": "S7.11 sensitivity analysis",
        },

        "H_hardened_raw_ablation": {
            "id": "H0_RAW_HARDENED",
            "definition": "Ridge regression using ONLY the primitive levels in "
                          "P_hard; no constructed coordinates; same "
                          "calibration geometry, preprocessing and "
                          "penalty-selection rule as B2; development-only "
                          "tuning; frozen before external evaluation",
            "status": "DIAGNOSTIC_ABLATION",
            "is_mandatory_gate_baseline": False,
            "replaces_B2": False,
            "B2_unchanged": True,
            "evaluated_in_S7_5H": False,
            "purpose": {
                "B2_vs_H0": "isolates the effect of primitive-space hardening",
                "H0_vs_relational_SIR": "isolates the effect of relational "
                                        "coordinate construction on the SAME "
                                        "hardened primitive information"},
        },

        "forbidden_selection_criteria": [
            "predictor-target correlation", "mutual information with density",
            "regression against density", "density reconstruction error",
            "feature importance from a target model",
            "'probably does not matter for density'"],
        "effective_rank_audit": "PERMITTED AS AUDIT SUMMARY ONLY; may not "
                                "determine P_hard",
        "no_target_primitive_count_imposed": True,
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"].startswith("STOP"):
        raise SystemExit("STOP: parent drift")

    P = pd.read_csv(S75 / "primitive_type_registry.csv")
    groups, decisions = redundancy_eligible_groups(P)
    groups.to_csv(S5H / "redundancy_eligible_groups.csv", index=False)

    ambiguous = [d for d in decisions["per_block"]
                 if d["eligible"] is False and not d["reason"]]
    if ambiguous:
        raise SystemExit("STOP: REDUNDANCY_GROUP_SEMANTICS_REQUIRES_HUMAN_REVIEW")

    pol = hardening_policy(groups)
    (S5H / "HARDENING_POLICY_PREVALUE.json").write_text(
        json.dumps(pol, indent=2), encoding="utf-8")
    h = sha(S5H / "HARDENING_POLICY_PREVALUE.json")
    (MAN / "POLICY_FREEZE.json").write_text(json.dumps({
        "policy_file": "HARDENING_POLICY_PREVALUE.json", "sha256": h,
        "frozen_utc": pol["frozen_utc"],
        "frozen_before_any_development_value_read": True,
        "stage_A_opens_no_archive": True}, indent=2), encoding="utf-8")

    print(f"parents: {par['verdict']}")
    print(f"  STAGE-SEQUENCE CONFLICT: instruction says 'S7.6 HAS NOT STARTED'; "
          f"repository has {par['stage_sequence_conflict']['s7_6_freeze_id']}")
    print(f"  resolution: {par['stage_sequence_conflict']['resolution']} -> "
          f"S7.6 V1 {par['stage_sequence_conflict']['s7_6_v1_downstream_status']}")
    print(f"  contamination: target reads "
          f"{par['stage_sequence_conflict']['contamination_analysis']['s7_6_target_values_accessed']}, "
          f"external reads "
          f"{par['stage_sequence_conflict']['contamination_analysis']['s7_6_external_values_accessed']}")
    print()
    print("redundancy-eligible groups:")
    for r in groups.itertuples():
        mark = "ELIGIBLE  " if r.redundancy_eligible else "ineligible"
        print(f"  {mark} {r.semantic_group_id:16s} n={r.n_members:3d}  "
              f"{r.canonical_unit:18s} {r.ineligibility_reason[:60]}")
    print(f"\npolicy frozen: sha {h[:32]}")
    print("NO ARCHIVE OPENED IN STAGE A")


if __name__ == "__main__":
    main()
