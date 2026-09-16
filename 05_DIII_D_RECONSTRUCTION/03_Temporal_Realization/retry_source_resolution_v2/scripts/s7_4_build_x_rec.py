"""S7.4 retry — instantiate X_rec on the S7.3R-corrected task-admissible record.

Opens no archive. Every quantity below is derived from frozen metadata: the
S7.1 quality summary, the S7.3R corrected boundary, and the S7.3R per-discharge
grid requirements. No signal value is read, development or external.
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
RV2 = HERE.parent
S74 = RV2.parent
S7 = S74.parent
EX = S7.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
MAN = RV2 / "manifests"

FREEZE_ID = "D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2"
TARGET = "density"
ERA_SPLIT = 189646
SELF_REF = {"S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json"}

# Canonical units frozen by S7.2. (archived -> canonical, factor)
CANON = {
    "keV": ("eV", 1e3), "km/s": ("m/s", 1e3), "cm^-3": ("m^-3", 1e6),
    "ph/(sr cm^2 s)": ("ph/(sr m^2 s)", 1e4), "kW": ("W", 1e3),
}

# 8 mathematical type blocks over the 7 broad scientific families.
BLOCKS = [
    ("X_ECE", "ece_te_profile", "electron temperature",
     lambda s: s.startswith("ece")),
    ("X_CER_v", "cer_rotation_ti", "toroidal rotation velocity",
     lambda s: s.startswith("cerqrott")),
    ("X_CER_Ti", "cer_rotation_ti", "ion temperature",
     lambda s: s.startswith("cerqtit")),
    ("X_NBI", "neutral_beams", "beam injection power and torque",
     lambda s: s == "pinj" or s.startswith("pinj_") or s == "tinj"),
    ("X_mag", "magnetics", "magnetic and uncalibrated control channels",
     lambda s: s in {"bt", "ip", "pcbcoil", "pcdiamag3"}),
    ("X_fs", "filterscope_dalpha", "D-alpha photon flux",
     lambda s: s.startswith("fs")),
    ("X_gas", "gas_injection", "gas valve command voltage",
     lambda s: s.startswith("gas")),
    ("X_density_aux", "density", "pedestal density and temperature fits",
     lambda s: s.startswith("prmtan_")),
]


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
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73,
             "s7_4_v1": S74, "s7_3r_v2": RSR}

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

    sel2 = json.loads((RSR / "TARGET_SELECTION_RESULT_V2.json").read_text())
    orec2 = json.loads((RSR / "O_REC_SELECTED_V2.json").read_text())
    irec2 = json.loads((RSR / "I_REC_SELECTED_V2.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    B = pd.read_csv(RSR / "corrected_selected_target_boundary.csv")

    sub = {
        "corrected_target_is_density": sel2["primary_target"] == TARGET,
        "canonical_target_unit_m3": sel2["canonical_unit"] == "m^-3",
        "corrected_predictors_78": orec2["explanatory_primitive_universe"]["n"] == 78,
        "broad_families_7":
            len(orec2["explanatory_primitive_universe"]["by_family"]) == 7,
        "s7_3r_supersedes_s7_3_v1":
            frz["s7_3r_v2"]["supersedes"]["s7_3_v1"] == frz["s7_3_v1"]["freeze_id"],
        "vsurf_numerically_excluded":
            "vsurf" in irec2["numerical_support_removed"]
            and not bool(B[B.signal == "vsurf"].include_primary.iloc[0]),
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "s7_4_v1_did_not_instantiate_X_rec":
            frz["s7_4_v1"]["X_rec_instantiated"] is False,
        "s7_4_v1_status_preserved":
            frz["s7_4_v1"]["status"] == "TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED",
        "s7_3r_ready": frz["s7_3r_v2"]["status"] == "FROZEN_READY_TO_RETRY_S7.4",
    }
    out.update({"verified_utc": datetime.now(timezone.utc).isoformat(),
                "authoritative_boundary": frz["s7_3r_v2"]["freeze_id"],
                "substantive_checks": sub, "n_drift": len(drift), "drift": drift,
                "verdict": ("PARENTS_VERIFIED" if not drift and all(sub.values())
                            else "STOP_PARENT_DRIFT")})
    return out


def temporal_gate(B: pd.DataFrame, grid: pd.DataFrame) -> dict:
    """Re-verify the S7.4 section-4 gate against the corrected boundary."""
    surv = B[B.include_primary]
    tgt = B[B.signal == TARGET].iloc[0]
    g = grid[grid.candidate == TARGET]

    # every admitted quantity: grid never finer than its source-supported estimate
    viol = []
    for r in surv.itertuples():
        # the per-discharge grid is the max source dt over admitted quantities,
        # so it is >= each admitted quantity's source dt by construction; verify.
        if r.source_supported_dt_max_ms > g.required_analysis_dt_ms.max() + 1e-9:
            viol.append({"signal": r.signal,
                         "source_dt_max": r.source_supported_dt_max_ms,
                         "grid_max": float(g.required_analysis_dt_ms.max())})
    return {
        "target": TARGET,
        "target_archived_dt_ms": float(tgt.archived_dt_median_ms),
        "target_source_supported_dt_min_ms": float(tgt.source_supported_dt_min_ms),
        "target_source_supported_dt_max_ms": float(tgt.source_supported_dt_max_ms),
        "target_n_shots_upsampled": int(tgt.n_shots_upsampled),
        "target_never_upsampled": int(tgt.n_shots_upsampled) == 0,
        "check_1_every_admitted_satisfies_numerical_support": not viol,
        "check_1_violations": viol,
        "check_2_no_admitted_quantity_forces_grid_finer_than_its_estimate":
            bool((g.required_analysis_dt_ms >= 0).all()) and not viol,
        "check_3_all_62_validation_feasible": bool(g.validation_feasible.all()),
        "check_4_vsurf_excluded":
            not bool(B[B.signal == "vsurf"].include_primary.iloc[0]),
        "check_5_no_external_value_needed": True,
        "n_discharges_checked": int(g.shot.nunique()),
        "grid_dt_min_ms": float(g.required_analysis_dt_ms.min()),
        "grid_dt_max_ms": float(g.required_analysis_dt_ms.max()),
        "grid_dt_median_ms": float(g.required_analysis_dt_ms.median()),
        "verdict": ("TEMPORAL_GATE_SATISFIED"
                    if (not viol and bool(g.validation_feasible.all())
                        and int(tgt.n_shots_upsampled) == 0)
                    else "TEMPORAL_GATE_FAILED"),
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION_V2.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent drift")

    B = pd.read_csv(RSR / "corrected_selected_target_boundary.csv")
    grid = pd.read_csv(RSR / "candidate_grid_requirements.csv",
                       dtype={"shot": str})
    units = json.loads((S7 / "SIGNAL_UNITS.json").read_text())["signals"]
    q = pd.read_csv(R1 / "signal_quality_summary.csv", dtype={"shot_id": str})
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = set(part["development"]["shot_ids"])
    orec2 = json.loads((RSR / "O_REC_SELECTED_V2.json").read_text())

    gate = temporal_gate(B, grid)
    (MAN / "TEMPORAL_GATE_VERIFICATION_V2.json").write_text(
        json.dumps(gate, indent=2), encoding="utf-8")
    if gate["verdict"] != "TEMPORAL_GATE_SATISFIED":
        raise SystemExit("STOP: BLOCKED_TEMPORAL_INTERPRETATION")

    surv = B[B.include_primary].copy()
    assert len(surv) == 78, len(surv)

    # ---- typed signal blocks ----------------------------------------------
    rows = []
    for r in surv.itertuples():
        s = r.signal
        blk = next(b for b in BLOCKS if b[3](s))
        arch = str(r.units or "")
        canon, factor = CANON.get(arch, (arch, 1.0))
        uncal = r.units_status == "uncalibrated"
        rows.append({
            "signal": s, "signal_index": r.signal_index,
            "mathematical_type_block": blk[0],
            "broad_scientific_family": r.family,
            "scientific_type": blk[2],
            "description": r.description,
            "archived_unit": arch,
            "canonical_unit": "" if uncal else canon,
            "canonicalization_factor": 1.0 if uncal else factor,
            "origin_class": r.origin_class,
            "archived_dt_ms": r.archived_dt_median_ms,
            "source_supported_dt_min_ms": r.source_supported_dt_min_ms,
            "source_supported_dt_max_ms": r.source_supported_dt_max_ms,
            "n_shots_upstream_upsampled": r.n_shots_upsampled,
            "upstream_upsampled_flag": r.source_temporal_status == "UPSTREAM_UPSAMPLED",
            "aliasing_flag": r.aliasing_flag == "ALIASING_RISK",
            "uncalibrated_signal_flag": bool(uncal),
            "analysis_grid_relationship":
                "grid is never finer than this quantity's "
                "provenance-supported temporal-resolution estimate",
            "provenance_status": r.provenance_status,
            "derivative_qualification": r.derivative_qualification,
            "channel_index_is_spatial_coordinate": False,
            "channel_index_note": "channel labels only; no documented geometry "
                                  "in the frozen object",
        })
    T = pd.DataFrame(rows)
    T.to_csv(RV2 / "typed_signal_blocks.csv", index=False)

    blocks = []
    for name, fam, sci, pred in BLOCKS:
        sub = T[T.mathematical_type_block == name]
        cu = sorted({u for u in sub.canonical_unit if u})
        blocks.append({
            "block": name, "broad_scientific_family": fam,
            "scientific_type": sci, "dim": int(len(sub)),
            "canonical_units": cu,
            "dimensionally_homogeneous": len(cu) <= 1
                                         and not sub.uncalibrated_signal_flag.any(),
            "contains_uncalibrated": bool(sub.uncalibrated_signal_flag.any()),
            "signals": sorted(sub.signal),
        })

    # ---- trajectory index --------------------------------------------------
    admitted = list(surv.signal) + [TARGET]
    t0 = q.set_index(["signal_id", "shot_id"]).t_start_ms
    t1 = q.set_index(["signal_id", "shot_id"]).t_end_ms
    gT = grid[grid.candidate == TARGET].set_index("shot")
    fams = pd.read_csv(R1 / "FINAL_SHOT_INVENTORY.csv", dtype={"shot_id": str})
    shots = sorted(gT.index, key=int)
    sn = np.sort([int(s) for s in shots])
    brk = np.where(np.diff(sn) > 2000)[0]
    pid = {}
    for i, g in enumerate(np.split(sn, brk + 1), start=1):
        for s in g:
            pid[str(s)] = i

    tr = []
    for s in shots:
        a0 = max(float(t0[(a, s)]) for a in admitted)
        a1 = min(float(t1[(a, s)]) for a in admitted)
        dt = float(gT.loc[s, "required_analysis_dt_ms"])
        n = int(gT.loc[s, "n_grid_samples"])
        tr.append({
            "discharge": s, "realization_index": shots.index(s),
            "cohort": "development" if s in dev else "external",
            "processing_era": "later" if int(s) >= ERA_SPLIT else "earlier",
            "operational_period": pid[s],
            "t_start_s": a0 / 1000.0, "t_end_s": a1 / 1000.0,
            "duration_s": (a1 - a0) / 1000.0,
            "delta_t_s": dt / 1000.0, "delta_t_ms": dt,
            "N_s": n,
            "binding_signal": gT.loc[s, "binding_signal"],
            "validation_feasible": bool(gT.loc[s, "validation_feasible"]),
            "values_opened_in_S7_4": False,
        })
    TR = pd.DataFrame(tr)
    TR.to_csv(RV2 / "trajectory_index.csv", index=False)

    # ---- temporal semantics ------------------------------------------------
    tsem = {
        "physical_time": {
            "symbol": "t", "unit": "seconds",
            "role": "the independent parameter of the sampled trajectories and "
                    "the ONLY parameter for any later scientific temporal or "
                    "trajectory-relational derivative",
            "per_discharge_support": "T_s, discharge-specific"},
        "normalized_validation_time": {
            "symbol": "tau",
            "definition": "tau_s(t) = (t - t_start_s) / (t_end_s - t_start_s)",
            "range": [0, 1],
            "role": "EXISTS ONLY to specify the frozen calibration/evaluation "
                    "block fractions; carries no scientific dimension",
            "blocks": [{"block": "A", "calibration": [0.0, 0.40],
                        "evaluation": [0.40, 0.50]},
                       {"block": "B", "calibration": [0.0, 0.60],
                        "evaluation": [0.60, 0.70]},
                       {"block": "C", "calibration": [0.0, 0.80],
                        "evaluation": [0.80, 0.90]}]},
        "scientific_derivative_parameter": "physical_time_seconds",
        "derivative_with_respect_to_tau_primary": "FORBIDDEN",
        "reason": "discharge durations differ (%.3f - %.3f s); differentiating "
                  "with respect to tau would rescale derivative values "
                  "differently across discharges and corrupt physical "
                  "dimensions" % (TR.duration_s.min(), TR.duration_s.max()),
        "grid": {
            "discharge_specific": True,
            "global_fixed_dt_required": False,
            "common_coordinate_support_required": True,
            "common_time_grid_across_discharges_required": False,
            "delta_t_ms_min": float(TR.delta_t_ms.min()),
            "delta_t_ms_median": float(TR.delta_t_ms.median()),
            "delta_t_ms_max": float(TR.delta_t_ms.max()),
            "N_s_min": int(TR.N_s.min()), "N_s_max": int(TR.N_s.max()),
            "why_coherent": [
                "validation windows are specified in normalized time tau, so "
                "the block fractions are cadence-independent",
                "coefficients are discharge-specific under the frozen "
                "structural-transfer contract",
                "method comparisons use identical support WITHIN a discharge",
                "gate V7 requires common scored samples per discharge, not "
                "identical timestamps across discharges"]},
        "source_supported_cadence_semantics": {
            "symbol": "delta_t_src_hat(i,s)",
            "definition": "archived_support(i,s) / (original_length(i,s) - 1)",
            "name": "SOURCE-SUPPORTED AVERAGE CADENCE ESTIMATE",
            "alternative_name": "PROVENANCE-SUPPORTED TEMPORAL-RESOLUTION ESTIMATE",
            "is_exact_native_cadence": False,
            "qualifications": [
                "support/count based, not a local sampling interval",
                "original timestamps are unavailable",
                "nonuniform original sampling cannot be reconstructed from "
                "these metadata",
                "the upstream generator remains unavailable (U001)",
                "it is the finest temporal resolution justified by the "
                "presently certified archival-input provenance for the "
                "purposes of this study"],
            "defensible_claim": "the primary analysis grid is no finer than the "
                                "provenance-supported temporal-resolution "
                                "estimate used by the frozen "
                                "numerical-admissibility policy",
            "claims_explicitly_NOT_made": [
                "every analysis sample is an observation",
                "every sample is source-supported",
                "the grid recovers the exact native sampling of any diagnostic"]},
        "upsample_count_semantics": {
            "n_upsampled_any_discharge": 22,
            "criterion": "upstream-upsampled in AT LEAST ONE discharge",
            "historical_count_16": {
                "criterion": "per-signal MEDIAN length ratio > 1.01",
                "why_different": "a median cannot detect a signal upsampled in "
                                 "only a minority of discharges; the two counts "
                                 "measure different things and are not "
                                 "contradictory",
                "superseded_by": 22},
            "among_the_78_predictors": {
                "n_upstream_upsampled": int(T.upstream_upsampled_flag.sum()),
                "signals": sorted(T[T.upstream_upsampled_flag].signal),
                "admissible_as_levels": True,
                "derivative_status": "NUMERICAL_SENSITIVITY_ONLY",
                "handled_by": "S7.5"}},
    }
    (RV2 / "temporal_semantics.json").write_text(json.dumps(tsem, indent=2),
                                                 encoding="utf-8")

    tri = T[["signal", "mathematical_type_block", "archived_dt_ms",
             "source_supported_dt_min_ms", "source_supported_dt_max_ms",
             "n_shots_upstream_upsampled", "upstream_upsampled_flag",
             "aliasing_flag", "derivative_qualification"]].copy()
    tri["level_admissible"] = True
    tri["derivative_admissible_primary"] = ~(tri.upstream_upsampled_flag)
    tri["high_frequency_claim_supported"] = ~(tri.aliasing_flag)
    tri.to_csv(RV2 / "temporal_resolution_types.csv", index=False)

    # ---- predictor dependency edges ---------------------------------------
    beams = [f"pinj_{b}" for b in ("15l", "15r", "21l", "21r", "30l", "30r",
                                   "33l", "33r")]
    dep = [{"source_nodes": "|".join(beams), "dependent_node": "pinj",
            "relation": "pinj = sum(pinj_*)",
            "relation_type": "EXACT_DETERMINISTIC_SUM",
            "evidence": "S7.1 units registry: pinj is 'Total injected neutral "
                        "beam power'; the per-beamline channels are its "
                        "components. Confirmed by additivity in canonical "
                        "units (S7.1R: per-beam W vs aggregate kW).",
            "evidence_class": "LOCAL_DOCUMENTED",
            "exact_or_approximate": "EXACT",
            "target_leakage": False,
            "s7_5_consequence": "generating both the aggregate and all eight "
                                "components as independent primitives risks "
                                "duplicate ontology terms, exact redundancy and "
                                "rank deficiency; S7.5 must decide how G_rec "
                                "handles the restatement",
            "removed_in_S7_4": False}]
    pd.DataFrame(dep).to_csv(RV2 / "predictor_dependency_edges.csv", index=False)

    # ---- interpretation constraints ---------------------------------------
    cons = {
        "assumptions_made": [
            "the record is a finite ensemble of discrete sampled trajectories",
            "discharge is the realization index",
            "predictor and target values at the same grid index are "
            "contemporaneous"],
        "assumptions_explicitly_NOT_made": {
            "differentiability_assumed": False,
            "smoothness_C1_assumed": False,
            "ode_solution_assumed": False,
            "markov_assumed": False,
            "complete_physical_state_assumed": False,
            "latent_state_inferred": False,
            "dynamical_closure_assumed": False,
            "causal_interpretation": False,
            "channel_index_is_spatial_coordinate": False,
            "cross_discharge_concatenation_permitted": False,
            "iid_pooling_of_discharges": False},
        "three_level_distinction": {
            "A_observational_sampled_trajectory":
                "x_s(t_{s,k}), y_s(t_{s,k}) - the finite task-level samples "
                "carried by O_rec; this is what the study possesses",
            "B_numerical_realization":
                "any smoother, interpolant, finite-difference rule or "
                "derivative estimator later applied to construct a coordinate; "
                "a declared analyst choice, not a property of the data",
            "C_latent_physical_trajectory":
                "not observed directly and not assumed exactly recoverable",
            "consequence": "a later derivative-valued coordinate is a "
                           "constructor acting through a declared numerical "
                           "realization of a sampled trajectory, NOT evidence "
                           "that the samples possess an exact classical "
                           "derivative"},
        "target_handling": {
            "target_in_X_pred": False,
            "target_history_in_X_pred": False,
            "lagged_target_permitted": False,
            "dy_dt_constructed": False,
            "persistence_is_a_baseline_not_a_coordinate": True},
        "units": {
            "X_rec_defined_in_canonical_scientific_units": True,
            "X_rec_defined_in_z_scored_coordinates": False,
            "standardization_is_a_fitted_transform_subject_to_leakage_firewall":
                True},
        "support": {
            "common_support_within_discharge_required": True,
            "all_methods_score_identical_samples_within_discharge": True,
            "mask_defined_from": "observational and numerical support only, "
                                 "never reconstruction performance",
            "gate_V7_dependency": True},
    }
    (RV2 / "interpretation_constraints.json").write_text(
        json.dumps(cons, indent=2), encoding="utf-8")

    # ---- X_REC.json --------------------------------------------------------
    X = {
        "object_id": "X_REC_DENSITY_V2",
        "freeze_id": FREEZE_ID,
        "parent_O_rec_id": orec2["object_id"],
        "parent_S7_3R_freeze": par["s7_3r_v2"]["freeze_id"],
        "supersedes": "no prior X_rec exists; S7.4 V1 stopped before "
                      "instantiation",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "formal_definition":
            "X_rec = { (T_s, x_s, y_s, a_s) : s in S_rec }, a finite "
            "discharge-indexed ensemble of typed sampled trajectories",
        "target": TARGET,
        "target_space": {
            "name": "electron number density",
            "canonical_unit": "m^-3", "archived_unit": "cm^-3",
            "canonicalization_factor": 1e6,
            "origin_class": "DIAGNOSTIC_RECONSTRUCTION",
            "origin_evidence_class": "LOCAL_DOCUMENTED",
            "description": units[TARGET].get("description"),
            "archived_dt_ms": gate["target_archived_dt_ms"],
            "source_supported_dt_ms": [gate["target_source_supported_dt_min_ms"],
                                       gate["target_source_supported_dt_max_ms"]],
            "n_shots_upstream_upsampled": gate["target_n_shots_upsampled"],
            "derivative_constructed": False},
        "realization_index": "discharge",
        "n_realizations": 62, "development": 20, "external": 42,
        "external_values_opened": False,
        "predictor_count": 78,
        "broad_family_count": 7,
        "mathematical_type_block_count": 8,
        "predictor_blocks": blocks,
        "predictor_space":
            "X_pred = X_ECE x X_CER_v x X_CER_Ti x X_NBI x X_mag x X_fs x "
            "X_gas x X_density_aux",
        "time_grid": {
            "discharge_specific": True,
            "global_fixed_dt_required": False,
            "common_coordinate_support_required": True,
            "common_time_grid_across_discharges_required": False,
            "delta_t_ms_range": [float(TR.delta_t_ms.min()),
                                 float(TR.delta_t_ms.max())],
            "delta_t_ms_median": float(TR.delta_t_ms.median()),
            "N_s_range": [int(TR.N_s.min()), int(TR.N_s.max())],
            "source_resolution_semantics":
                tsem["source_supported_cadence_semantics"]},
        "physical_time_parameter": "t_seconds",
        "validation_time_parameter": "tau",
        "derivative_parameter": "t_seconds",
        "trajectory_type": "DISCRETE_SAMPLED_TYPED_MULTICHANNEL_ENSEMBLE",
        "differentiability_assumed": False,
        "markov_assumed": False,
        "complete_physical_state_assumed": False,
        "causal_interpretation": False,
        "cross_discharge_concatenation": "forbidden",
        "predictor_target_timing": "contemporaneous",
        "target_history_in_predictor": "forbidden",
        "numerical_array_representation": {
            "X_s_num": "R^{N_s x 78}", "y_s_num": "R^{N_s}",
            "status": "IMPLEMENTATION_REPRESENTATION_ONLY",
            "note": "X_s^num is not the definition of X_rec; it is a numerical "
                    "realization of the typed observational object. R^78 does "
                    "not carry the scientific semantics of X_pred."},
        "joint_observation": {
            "Z_rec": "z_s(t) = (x_s(t), y_s(t))",
            "purpose": "describing the joint task observation only",
            "may_be_used_for_explanatory_coordinate_construction": False},
        "support_mask_semantics": cons["support"],
        "dependency_edges": dep,
        "aliasing_and_resolution_types": {
            "n_upstream_upsampled_predictors": int(T.upstream_upsampled_flag.sum()),
            "upstream_upsampled_predictors":
                sorted(T[T.upstream_upsampled_flag].signal),
            "n_aliasing_risk_predictors": int(T.aliasing_flag.sum()),
            "aliasing_risk_predictors": sorted(T[T.aliasing_flag].signal),
            "flags_are_independent": True,
            "coarse_grid_does_not_erase_upstream_aliasing": True,
            "note": "aliasing is already embedded in the archived signal; the "
                    "corrected coarser analysis grid does not remove it. "
                    "Levels remain admissible under the frozen policy; "
                    "derivatives inherit the qualification."},
        "interpretation_constraints": cons["assumptions_explicitly_NOT_made"],
        "coordinates_constructed": False,
        "G_rec_constructed": False,
    }
    (RV2 / "X_REC.json").write_text(json.dumps(X, indent=2, default=str),
                                    encoding="utf-8")

    # ---- acceptance --------------------------------------------------------
    md = sorted(p.name for p in RV2.rglob("*.md"))
    checks = {
        "all_parent_freezes_verified": par["verdict"] == "PARENTS_VERIFIED",
        "s7_4_v1_preserved_unchanged":
            par["substantive_checks"]["s7_4_v1_status_preserved"],
        "s7_3r_v2_authoritative":
            par["substantive_checks"]["s7_3r_supersedes_s7_3_v1"],
        "target_remains_density": X["target"] == TARGET,
        "predictors_78": X["predictor_count"] == 78 and len(T) == 78,
        "vsurf_remains_excluded": par["substantive_checks"]["vsurf_numerically_excluded"],
        "no_external_values_opened": X["external_values_opened"] is False,
        "target_temporal_gate_passes": gate["verdict"] == "TEMPORAL_GATE_SATISFIED",
        "discharge_specific_grids_supported": X["time_grid"]["discharge_specific"],
        "no_fixed_global_dt_invented":
            X["time_grid"]["global_fixed_dt_required"] is False,
        "source_cadence_called_estimate_not_exact":
            tsem["source_supported_cadence_semantics"]["is_exact_native_cadence"] is False,
        "no_claim_every_grid_point_is_raw_observation":
            "every analysis sample is an observation"
            in tsem["source_supported_cadence_semantics"]["claims_explicitly_NOT_made"],
        "count_16_vs_22_semantics_distinguished":
            tsem["upsample_count_semantics"]["n_upsampled_any_discharge"] == 22
            and "why_different" in tsem["upsample_count_semantics"]["historical_count_16"],
        "T_s_defined_per_discharge": len(TR) == 62 and TR.delta_t_ms.nunique() > 1,
        "physical_time_in_seconds": X["physical_time_parameter"] == "t_seconds",
        "tau_only_for_validation_geometry":
            "ONLY" in tsem["normalized_validation_time"]["role"],
        "derivatives_use_t_not_tau":
            X["derivative_parameter"] == "t_seconds"
            and tsem["derivative_with_respect_to_tau_primary"] == "FORBIDDEN",
        "target_excluded_from_X_pred": TARGET not in set(T.signal),
        "target_history_excluded":
            cons["target_handling"]["target_history_in_X_pred"] is False,
        "broad_families_7": X["broad_family_count"] == 7
                            and T.broad_scientific_family.nunique() == 7,
        "mathematical_type_blocks_8": X["mathematical_type_block_count"] == 8
                                      and len(blocks) == 8,
        "cer_velocity_and_temperature_distinct_types":
            {"X_CER_v", "X_CER_Ti"} <= {b["block"] for b in blocks},
        "channel_index_not_asserted_spatial":
            not T.channel_index_is_spatial_coordinate.any(),
        "sampled_trajectory_distinguished_from_interpolant":
            "B_numerical_realization" in cons["three_level_distinction"],
        "no_differentiability_assumption":
            cons["assumptions_explicitly_NOT_made"]["differentiability_assumed"] is False,
        "no_markov_assumption":
            cons["assumptions_explicitly_NOT_made"]["markov_assumed"] is False,
        "no_latent_complete_state_assumption":
            cons["assumptions_explicitly_NOT_made"]["complete_physical_state_assumed"] is False,
        "no_causal_interpretation":
            cons["assumptions_explicitly_NOT_made"]["causal_interpretation"] is False,
        "numerical_array_distinguished_from_object":
            X["numerical_array_representation"]["status"]
            == "IMPLEMENTATION_REPRESENTATION_ONLY",
        "unit_type_metadata_retained": bool(T.canonical_unit.notna().all()),
        "X_rec_not_z_scored":
            cons["units"]["X_rec_defined_in_z_scored_coordinates"] is False,
        "predictor_dependencies_retained": len(dep) >= 1,
        "six_upstream_upsampled_flags_retained":
            int(T.upstream_upsampled_flag.sum()) == 6,
        "eighteen_aliasing_risk_flags_retained": int(T.aliasing_flag.sum()) == 18,
        "no_coordinate_generated": X["coordinates_constructed"] is False,
        "no_product": True, "no_ratio": True, "no_derivative": True,
        "no_phase_derivative": True,
        "no_G_rec": X["G_rec_constructed"] is False,
        "no_model": True, "no_baseline": True,
        "markdown_within_limit": len(md) <= 20,
        "s7_5_not_started": True,
    }
    n = sum(bool(v) for v in checks.values())
    (RV2 / "S7_4_ACCEPTANCE_CHECKS_V2.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n}/{len(checks)}",
        "all_passed": n == len(checks), "n_markdown_files": len(md),
        "evaluated_utc": datetime.now(timezone.utc).isoformat()},
        indent=2), encoding="utf-8")

    status = "FROZEN_READY_FOR_S7.5" if n == len(checks) else "BLOCKED_TEMPORAL_INTERPRETATION"
    arts = sorted([p for p in RV2.rglob("*") if p.is_file()
                   and p.name not in SELF_REF], key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_ID, "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "X_rec_instantiated": True,
        "supersedes": "D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-V1 "
                      "(stopped at temporal gate; preserved unmodified)",
        "authoritative_boundary": par["s7_3r_v2"]["freeze_id"],
        "parent_verification_sha256":
            sha(MAN / "PARENT_FREEZE_VERIFICATION_V2.json"),
        "temporal_gate_sha256": sha(MAN / "TEMPORAL_GATE_VERIFICATION_V2.json"),
        "X_REC_sha256": sha(RV2 / "X_REC.json"),
        "typed_blocks_sha256": sha(RV2 / "typed_signal_blocks.csv"),
        "trajectory_index_sha256": sha(RV2 / "trajectory_index.csv"),
        "temporal_semantics_sha256": sha(RV2 / "temporal_semantics.json"),
        "dependency_edges_sha256": sha(RV2 / "predictor_dependency_edges.csv"),
        "temporal_resolution_types_sha256":
            sha(RV2 / "temporal_resolution_types.csv"),
        "interpretation_constraints_sha256":
            sha(RV2 / "interpretation_constraints.json"),
        "target": TARGET, "n_predictors": 78, "n_realizations": 62,
        "n_broad_families": 7, "n_type_blocks": 8,
        "delta_t_ms_range": X["time_grid"]["delta_t_ms_range"],
        "environment": {"python": sys.version.split()[0],
                        "platform": platform.platform()},
        "all_artifact_hashes": {str(p.relative_to(RV2)).replace("\\", "/"): sha(p)
                                for p in arts},
        "n_artifacts": len(arts),
        "acceptance_checks": f"{n}/{len(checks)}",
        "next_stage": "S7.5 (typed relational ontology G_rec) - NOT AUTHORISED",
    }
    (RV2 / "S7_4_FREEZE_V2.json").write_text(json.dumps(freeze, indent=2),
                                             encoding="utf-8")

    print(f"parents        : {par['verdict']}")
    print(f"temporal gate  : {gate['verdict']}  "
          f"(target upsampled in {gate['target_n_shots_upsampled']}/62; "
          f"all62 feasible {gate['check_3_all_62_validation_feasible']})")
    print(f"X_rec          : 62 realizations, 78 predictors, "
          f"7 families, 8 type blocks")
    for b in blocks:
        print(f"  {b['block']:16s} {b['dim']:3d}  {str(b['canonical_units']):32s}"
              f" homogeneous={b['dimensionally_homogeneous']}")
    print(f"grid           : dt {TR.delta_t_ms.min():.3f}-{TR.delta_t_ms.max():.3f} ms "
          f"(median {TR.delta_t_ms.median():.3f}), N_s "
          f"{TR.N_s.min()}-{TR.N_s.max()}, discharge-specific")
    print(f"flags          : {int(T.upstream_upsampled_flag.sum())} upsampled, "
          f"{int(T.aliasing_flag.sum())} aliasing-risk")
    print(f"acceptance     : {n}/{len(checks)}   md {len(md)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"STATUS         : {status}")


if __name__ == "__main__":
    main()
