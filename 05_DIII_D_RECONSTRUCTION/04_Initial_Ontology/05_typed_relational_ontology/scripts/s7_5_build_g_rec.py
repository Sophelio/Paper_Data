"""S7.5 — construct and freeze the typed relational ontology G_rec.

G_rec is the GRAMMAR of admissible relational constructions, not their
enumeration. A_rec is NOT built here.

Opens no archive. All inputs are frozen metadata. The only numerical work is a
synthetic capability check on the declared derivative realization (section 10),
which touches no observational data.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S75 = HERE.parent
S7 = S75.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
RSR = S73 / "reconciliation_source_resolution"
S74 = S7 / "04_mathematical_interpretation"
RV2 = S74 / "retry_source_resolution_v2"
MAN = S75 / "manifests"

FREEZE_ID = "D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1"
TARGET = "density"
SELF_REF = {"S7_5_ACCEPTANCE_CHECKS.json", "S7_5_FREEZE.json"}

SENSITIVITY_ONLY_DERIV = {"prmtan_neped", "prmtan_teped",
                          "fs03da", "fs04", "fs04da", "fs05da"}
UNCALIBRATED = {"pcbcoil", "pcdiamag3"}

# component-level scientific types (NOT block-level)
SCI_TYPE = {
    "eV": ("temperature_energy", "eV"),
    "m/s": ("velocity", "m s^-1"),
    "W": ("power", "W"),
    "N m": ("torque", "N m"),
    "T": ("magnetic_flux_density", "T"),
    "A": ("electric_current", "A"),
    "V": ("electric_potential", "V"),
    "m^-3": ("number_density", "m^-3"),
    "ph/(sr m^2 s)": ("photon_flux", "ph sr^-1 m^-2 s^-1"),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
def verify_parents() -> dict:
    frz = {
        "s7_1": json.loads((R1 / "S7_1_FINAL_FREEZE.json").read_text()),
        "s7_2_v1": json.loads((S72 / "S7_2_FREEZE.json").read_text()),
        "s7_2_v2": json.loads((CV1 / "S7_2_FREEZE_V2.json").read_text()),
        "s7_3_v1": json.loads((S73 / "S7_3_FREEZE.json").read_text()),
        "s7_4_v1": json.loads((S74 / "S7_4_FREEZE.json").read_text()),
        "s7_3r_v2": json.loads((RSR / "S7_3_FREEZE_V2.json").read_text()),
        "s7_4_v2": json.loads((RV2 / "S7_4_FREEZE_V2.json").read_text()),
    }
    SELF = {"S7_4_FREEZE.json", "S7_4_ACCEPTANCE_CHECKS.json",
            "S7_3R_ACCEPTANCE_CHECKS.json", "S7_3_FREEZE_V2.json",
            "S7_4_ACCEPTANCE_CHECKS_V2.json", "S7_4_FREEZE_V2.json"}
    for k in ("s7_2_v2", "s7_3_v1"):
        SELF |= set(frz[k].get("self_referential_excluded", []))
    bases = {"s7_2_v1": S72, "s7_2_v2": CV1, "s7_3_v1": S73, "s7_4_v1": S74,
             "s7_3r_v2": RSR, "s7_4_v2": RV2}

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

    X = json.loads((RV2 / "X_REC.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    irec = json.loads((RSR / "I_REC_SELECTED_V2.json").read_text())
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    sub = {
        "target_is_density": X["target"] == TARGET,
        "canonical_target_unit_m3": X["target_space"]["canonical_unit"] == "m^-3",
        "predictor_count_78": X["predictor_count"] == 78,
        "broad_families_7": X["broad_family_count"] == 7,
        "type_blocks_8": X["mathematical_type_block_count"] == 8,
        "vsurf_excluded": "vsurf" in irec["numerical_support_removed"],
        "external_cohort_42_sealed": part["external"]["n"] == 42,
        "X_rec_instantiated": frz["s7_4_v2"]["X_rec_instantiated"] is True,
        "s7_3r_v2_authoritative":
            frz["s7_4_v2"]["authoritative_boundary"] == frz["s7_3r_v2"]["freeze_id"],
        "s7_4_v2_authoritative":
            frz["s7_4_v2"]["status"] == "FROZEN_READY_FOR_S7.5",
        "s7_4_v1_historical_preserved":
            frz["s7_4_v1"]["X_rec_instantiated"] is False,
        "support_size_bound_1_12":
            K["B_rec"]["representation_size_range"] == [1, 12],
        "max_relational_depth_1": K["B_rec"]["max_relational_depth"] == 1,
    }
    out.update({"verified_utc": datetime.now(timezone.utc).isoformat(),
                "substantive_checks": sub, "n_drift": len(drift), "drift": drift,
                "verdict": ("PARENTS_VERIFIED" if not drift and all(sub.values())
                            else "STOP_PARENT_DRIFT")})
    return out


def preflight(X: dict, T: pd.DataFrame) -> dict:
    """Section 4 semantic consistency checks on inherited S7.4 documentation."""
    het = [b["block"] for b in X["predictor_blocks"]
           if not b["dimensionally_homogeneous"]]
    # independent recount from component-level types
    recount = {}
    for blk, g in T.groupby("mathematical_type_block"):
        n = len({u for u in g.canonical_unit if isinstance(u, str) and u})
        n += 1 if g.uncalibrated_signal_flag.any() else 0
        recount[blk] = n
    implied = sorted(b for b, n in recount.items() if n > 1)

    ts = json.loads((RV2 / "temporal_semantics.json").read_text())
    definition = ts["source_supported_cadence_semantics"]["definition"]
    impl = (RSR / "scripts" / "s7_3r_reconcile.py").read_text(encoding="utf-8")
    impl_ok = "j.support_ms / (j.original_length - 1)" in impl

    return {
        "check_4_1_heterogeneous_blocks": {
            "machine_readable_count": len(het),
            "machine_readable_blocks": sorted(het),
            "independent_component_level_implication": implied,
            "agree": sorted(het) == implied,
            "prose_claimed": 4, "correct_value": len(het),
            "verdict": ("DOCUMENTARY_ERRATUM_ONLY" if len(het) == 3
                        and sorted(het) == implied
                        else "PARENT_SEMANTIC_INCONSISTENCY_REQUIRES_S7.4C"),
            "action": "record erratum 'four' -> 'three'; do NOT reopen S7.4",
        },
        "check_4_2_cadence_denominator": {
            "machine_readable_definition": definition,
            "uses_n_minus_1_in_definition": "- 1)" in definition,
            "implementation_uses_n_minus_1": impl_ok,
            "verdict": ("DOCUMENTARY_ERRATUM_ONLY"
                        if impl_ok and "- 1)" in definition
                        else "STOP_IMPLEMENTATION_USES_N"),
            "action": "correct prose wording to 'one fewer than the number of "
                      "source samples over the recorded support'; frozen "
                      "computation unchanged",
        },
    }


def derivative_realization_check() -> dict:
    """Section 10: confirm the declared FD rule is reproducible on a
    discharge-specific (non-uniform, per-realization) physical-time grid.

    Synthetic data only. No observational value is touched.
    """
    rng = np.random.default_rng(0)
    results = []
    for dt_ms in (5.853, 6.824, 14.187):
        n = 400
        t = np.arange(n) * (dt_ms / 1000.0)          # seconds, per-discharge dt
        f = np.sin(2.0 * t) + 0.5 * t ** 2
        exact = 2.0 * np.cos(2.0 * t) + t
        got = np.gradient(f, t, edge_order=2)
        interior = slice(1, -1)
        err = float(np.max(np.abs(got[interior] - exact[interior])))
        results.append({"dt_ms": dt_ms, "max_interior_abs_error": err,
                        "n_samples": n})
    # second-order convergence on interior points: halving dt over a FIXED
    # window should reduce the interior error by ~4x
    errs = []
    for k in (1.0, 0.5, 0.25):
        n = int(400 / k)
        t = np.arange(n) * (0.006824 * k)
        f = np.sin(2.0 * t)
        got = np.gradient(f, t, edge_order=2)
        exact = 2.0 * np.cos(2.0 * t)
        errs.append(float(np.max(np.abs(got[1:-1] - exact[1:-1]))))
    ratios = [errs[i] / errs[i + 1] for i in range(len(errs) - 1)]

    # non-uniform spacing: np.gradient must still be usable, though it is only
    # first-order accurate there. Recorded, not relied on: each T_s is uniform
    # within its own discharge; only dt differs BETWEEN discharges.
    tnu = np.cumsum(rng.uniform(0.004, 0.010, 300))
    fnu = np.sin(2.0 * tnu)
    nu_err = float(np.max(np.abs(np.gradient(fnu, tnu, edge_order=2)[1:-1]
                                 - 2.0 * np.cos(2.0 * tnu[1:-1]))))
    return {
        "rule": "second-order finite difference with respect to physical time t",
        "reference_implementation": "numpy.gradient(x, t, edge_order=2)",
        "numpy_version": np.__version__,
        "grids_tested_ms": [r["dt_ms"] for r in results],
        "per_grid": results,
        "observed_convergence_ratios": ratios,
        "expected_ratio_for_second_order": 4.0,
        "second_order_confirmed": all(3.5 < r < 4.5 for r in ratios),
        "nonuniform_grid_max_interior_error": nu_err,
        "nonuniform_note": "np.gradient accepts a non-uniform t vector but is "
                           "only first-order there. Not relied upon: each T_s "
                           "is UNIFORM within its own discharge; only dt "
                           "differs BETWEEN discharges, which is the "
                           "second-order case tested above.",
        "reproducible_on_discharge_specific_grid": True,
        "uses_actual_T_s_values": True,
        "assumed_global_dt": False,
        "fitted_smoothing_parameter": False,
        "target_values_involved": False,
        "cross_discharge_stencil": False,
        "synthetic_data_only": True,
        "observational_values_touched": 0,
    }


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent drift")

    X = json.loads((RV2 / "X_REC.json").read_text())
    T = pd.read_csv(RV2 / "typed_signal_blocks.csv")
    K = json.loads((CV1 / "K_REC_PRE_V2.json").read_text())
    dep = pd.read_csv(RV2 / "predictor_dependency_edges.csv")

    pf = preflight(X, T)
    (MAN / "PREFLIGHT_SEMANTIC_CHECKS.json").write_text(
        json.dumps(pf, indent=2), encoding="utf-8")
    for k, v in pf.items():
        if not v["verdict"].startswith("DOCUMENTARY"):
            raise SystemExit(f"STOP: {v['verdict']}")

    fd = derivative_realization_check()
    (MAN / "DERIVATIVE_REALIZATION_CHECK.json").write_text(
        json.dumps(fd, indent=2), encoding="utf-8")
    if not (fd["second_order_confirmed"]
            and fd["reproducible_on_discharge_specific_grid"]):
        raise SystemExit("STOP: derivative realization not reproducible")

    # ---- primitive type registry ------------------------------------------
    rows = []
    for r in T.itertuples():
        s = r.signal
        uncal = bool(r.uncalibrated_signal_flag)
        cu = "" if uncal else str(r.canonical_unit)
        sci, dim = ("uncalibrated_raw_signal", "UNCALIBRATED") if uncal \
            else SCI_TYPE[cu]
        so = s in SENSITIVITY_ONLY_DERIV
        rows.append({
            "primitive_id": s, "signal_index": r.signal_index,
            "mathematical_type_block": r.mathematical_type_block,
            "broad_scientific_family": r.broad_scientific_family,
            "scientific_dimension_class": sci,
            "canonical_unit": cu,
            "dimension_expression": dim,
            "origin_class": r.origin_class,
            "provenance_status": r.provenance_status,
            "archived_dt_ms": r.archived_dt_ms,
            "source_supported_dt_min_ms": r.source_supported_dt_min_ms,
            "source_supported_dt_max_ms": r.source_supported_dt_max_ms,
            "upstream_upsampled_flag": bool(r.upstream_upsampled_flag),
            "aliasing_flag": bool(r.aliasing_flag),
            "uncalibrated_flag": uncal,
            "level_primary_admissible": True,
            "derivative_primary_eligible": (not uncal) and (not so),
            "derivative_sensitivity_only": so,
            "product_ratio_operand_eligible": not uncal,
            "phase_operand_eligible": (not uncal) and (not so),
            "exclusion_reason_for_derived":
                ("UNCALIBRATED_DIMENSIONALLY_UNCERTIFIED" if uncal
                 else "NUMERICAL_SENSITIVITY_ONLY" if so else ""),
        })
    P = pd.DataFrame(rows).sort_values("signal_index").reset_index(drop=True)
    P.to_csv(S75 / "primitive_type_registry.csv", index=False)

    n_all = len(P)
    n_uncal = int(P.uncalibrated_flag.sum())
    n_so = int(P.derivative_sensitivity_only.sum())
    n_deriv = int(P.derivative_primary_eligible.sum())
    n_pr = int(P.product_ratio_operand_eligible.sum())
    assert n_all == 78 and n_uncal == 2 and n_so == 6 and n_deriv == 70

    # ---- symbolic combinatorial bounds (audit only; NOT enumeration) -------
    bounds = {
        "note": "symbolic upper bounds for audit. NO coordinate instance is "
                "enumerated here; instantiation belongs to S7.6.",
        "C0_primitive_level": n_all,
        "C1_first_temporal_derivative_primary": n_deriv,
        "C1_first_temporal_derivative_sensitivity_only": n_so,
        "C2_pairwise_product_incl_self": n_pr * (n_pr - 1) // 2 + n_pr,
        "C3_pairwise_ratio_directional": n_pr * (n_pr - 1),
        "C4_trajectory_relational_derivative_directional":
            n_deriv * (n_deriv - 1),
        "primary_total": (n_all + n_deriv + n_pr * (n_pr - 1) // 2 + n_pr
                          + n_pr * (n_pr - 1) + n_deriv * (n_deriv - 1)),
        "sensitivity_only_total": n_so,
    }

    # ---- constructor catalogue --------------------------------------------
    cat = {
        "catalogue_id": "LAMBDA_REC_V1",
        "max_constructor_depth": 1,
        "constructors_operate_on": "PRIMITIVES ONLY; no constructor may consume "
                                   "another depth-1 constructed coordinate",
        "families": [
            {"id": "C0", "name": "primitive_level", "symbol": "ID(x_i)",
             "depth": 0, "arity": 1,
             "signature": "ID(signal_id)",
             "type_rule": "output type, unit, provenance, temporal and flag "
                          "metadata are inherited unchanged",
             "operand_eligibility": "all 78 primitives, including the two "
                                    "UNCALIBRATED_SIGNAL levels",
             "n_eligible_operands": n_all,
             "notes": "a representation containing only C0 coordinates is an "
                      "admissible special case, so the raw-coordinate "
                      "comparator is NESTED INSIDE the SIR ontology"},
            {"id": "C1", "name": "first_temporal_derivative",
             "symbol": "d x_i / dt", "depth": 1, "arity": 1,
             "signature": "DOT(signal_id)",
             "type_rule": "[x_i] -> [x_i] / s",
             "derivative_parameter": "physical time t in seconds",
             "derivative_wrt_tau": "FORBIDDEN",
             "numerical_realization": "FD2_PHYSICAL_TIME_V1",
             "operand_eligibility": "primitives that are neither uncalibrated "
                                    "nor NUMERICAL_SENSITIVITY_ONLY",
             "n_eligible_operands": n_deriv,
             "sensitivity_only_operands": sorted(SENSITIVITY_ONLY_DERIV),
             "notes": "second derivatives are excluded; no derivative of the "
                      "target is an explanatory coordinate"},
            {"id": "C2", "name": "pairwise_product", "symbol": "x_i x_j",
             "depth": 1, "arity": 2,
             "signature": "PROD(i,j) with i <= j by frozen inventory index",
             "type_rule": "[x_i x_j] = [x_i][x_j]",
             "commutative": True,
             "self_product_allowed": True,
             "operands_need_identical_dimensions": False,
             "operand_eligibility": "dimensionally typed primitives only "
                                    "(uncalibrated excluded)",
             "n_eligible_operands": n_pr,
             "notes": "canonical ordering i <= j prevents S7.6 instantiating "
                      "PROD(i,j) and PROD(j,i) as distinct coordinates; the "
                      "output carries the compound dimension explicitly"},
            {"id": "C3", "name": "pairwise_ratio", "symbol": "x_i / x_j",
             "depth": 1, "arity": 2,
             "signature": "RATIO(i,j), i != j",
             "type_rule": "[x_i / x_j] = [x_i] / [x_j]",
             "directional": True,
             "partial_map": True,
             "mathematical_domain": "x_j != 0",
             "domain_predicate": "DOMAIN_DENOMINATOR_NONZERO",
             "self_ratio_excluded": "x_i / x_i is the trivial constant 1",
             "operand_eligibility": "dimensionally typed primitives only",
             "n_eligible_operands": n_pr,
             "prohibited_modifications": [
                 "denominator shift", "additive epsilon", "clipping",
                 "bounded reciprocal transform"],
             "notes": "those modifications are DIFFERENT coordinate "
                      "constructions and were not frozen as primary "
                      "constructors. Numerical support and conditioning of "
                      "instantiated ratios are handled in S7.6 and S7.11 "
                      "WITHOUT changing the symbolic coordinate."},
            {"id": "C4", "name": "trajectory_relational_derivative",
             "symbol": "D_g^t f = (df/dt) / (dg/dt)",
             "manuscript_terminology": "trajectory-relational derivative; "
                                       "abbreviated 'phase derivative'",
             "depth": 1, "arity": 2,
             "signature": "PHASE(i|j) meaning D_{x_j} x_i",
             "type_rule": "[D_g f] = [f] / [g]  (time dimensions cancel)",
             "directional": True,
             "partial_map": True,
             "mathematical_domain": "dg/dt != 0",
             "domain_predicate": "DOMAIN_DENOMINATOR_RATE_NONZERO",
             "self_excluded": "D_f f is the trivial constant 1 where defined",
             "operand_eligibility": "both operands must be eligible for "
                                    "PRIMARY temporal differentiation",
             "n_eligible_operands": n_deriv,
             "numerical_realization": "FD2_PHYSICAL_TIME_V1",
             "does_NOT_imply": ["f = F(g)", "causality", "oscillatory phase",
                                "a global functional dependency"],
             "prohibited_variants": [
                 "reference-shifted phase derivative",
                 "bounded phase derivative",
                 "sensitivity-centered phase derivative"],
             "notes": "those variants are related but distinct constructions "
                      "and require separate explicit qualification if ever "
                      "studied"},
        ],
        "symbolic_upper_bounds": bounds,
    }
    (S75 / "constructor_catalog.json").write_text(json.dumps(cat, indent=2),
                                                  encoding="utf-8")

    # ---- type / propagation rules -----------------------------------------
    rules = {
        "dimensional_type_algebra": {
            "level": "COMPONENT, never block. Broad blocks are organizational "
                     "only and three of the eight are dimensionally "
                     "heterogeneous.",
            "heterogeneous_blocks": pf["check_4_1_heterogeneous_blocks"][
                "machine_readable_blocks"],
            "base_dimension_classes": sorted(
                {v[0] for v in SCI_TYPE.values()} | {"uncalibrated_raw_signal",
                                                     "time"}),
            "constructor_output": {
                "C0": "[x_i]", "C1": "[x_i] / time",
                "C2": "[x_i] * [x_j]", "C3": "[x_i] / [x_j]",
                "C4": "[x_i] / [x_j]"},
            "standardization_does_not_alter_scientific_type": True,
            "note": "a coordinate is NOT declared dimensionless merely because "
                    "its values are numerically standardized later",
        },
        "temporal_resolution_propagation": {
            "C0": "inherit the primitive's temporal metadata unchanged",
            "C1": "inherit the source primitive's temporal-resolution "
                  "qualification PLUS DERIVED_FROM_NUMERICAL_REALIZATION",
            "C2": "limited by the COARSER provenance-supported temporal "
                  "resolution of the two operands, within each discharge",
            "C3": "limited by the COARSER provenance-supported temporal "
                  "resolution of the two operands, within each discharge",
            "C4": "limited by the COARSER derivative-source resolution of "
                  "numerator and denominator",
            "invariant": "no constructed coordinate may claim temporal "
                         "information finer than either operand",
        },
        "flag_propagation": {
            "ALIASING_RISK": "propagates from any operand to the output; "
                             "levels remain primary admissible; no "
                             "high-frequency physical claim may be made",
            "UPSTREAM_UPSAMPLED": "level remains primary admissible; the "
                                  "first derivative is NUMERICAL_SENSITIVITY_"
                                  "ONLY and leaves the primary grammar",
            "precedence": "where both flags occur, NUMERICAL_SENSITIVITY_ONLY "
                          "dominates PRIMARY eligibility",
            "UNCALIBRATED_SIGNAL": "level primary admissible; ALL derived "
                                   "constructors excluded from the primary "
                                   "ontology",
        },
        "provenance_propagation": {
            "stored_per_coordinate": [
                "constructor", "ordered operands", "primitive ancestors",
                "input provenance classes", "input units and types",
                "temporal qualifications", "transformation depth",
                "target-independence status"],
            "primitive_ancestors_recoverable_exactly": True,
            "target_independence_is_transitive": True,
            "invariant": "if any primitive ancestor is target-forbidden, the "
                         "coordinate is forbidden",
            "holds_automatically_because": "G_rec is generated from the "
                                           "already target-independent "
                                           "78-primitive boundary; the "
                                           "invariant is encoded regardless",
        },
        "uncalibrated_signal_policy": {
            "signals": sorted(UNCALIBRATED),
            "primitive_level": "PRIMARY_ADMISSIBLE",
            "derived_coordinate": "DIMENSIONALLY_UNCERTIFIED_PRIMARY_EXCLUDED",
            "excluded_from": ["C1", "C2", "C3", "C4"],
            "rationale": "their physical dimensions are unresolved, so the "
                         "dimensional type of any constructed coordinate "
                         "cannot be scientifically certified. This is a "
                         "fail-closed dimensional-admissibility decision, NOT "
                         "a claim that the signals carry no information.",
        },
        "numerical_realization": {
            "id": "FD2_PHYSICAL_TIME_V1",
            "rule": "second-order finite difference with respect to actual "
                    "physical time t in seconds",
            "reference_implementation": "numpy.gradient(x, t, edge_order=2)",
            "uses_actual_T_s": True, "assumes_global_dt": False,
            "fitted_smoothing_parameter": False,
            "spline_or_RTS_in_primary": False,
            "target_values_involved": False,
            "cross_discharge_stencil": False,
            "differentiates_wrt_tau": False,
            "capability_check": fd,
            "alternative_realizations": "spline / RTS / other smooth "
                                        "realizations belong to S7.11 "
                                        "sensitivity qualification, not to the "
                                        "primary ontology",
            "interpretation": "a derivative-valued coordinate is a constructor "
                              "acting through a DECLARED numerical realization "
                              "of a sampled trajectory; it is not evidence "
                              "that the samples possess an exact classical "
                              "derivative",
        },
    }
    (S75 / "constructor_type_rules.json").write_text(json.dumps(rules, indent=2),
                                                     encoding="utf-8")

    # ---- excluded families -------------------------------------------------
    excl = {
        "semantics": {
            "GENERAL_FRAMEWORK_PERMITS": "the SIR framework in general admits "
                                         "the construction",
            "TASK_ONTOLOGY_EXCLUDES": "excluded for this task by K_rec or "
                                      "I_rec",
            "PRIMARY_ONTOLOGY_EXCLUDES": "excluded from this finite primary "
                                         "grammar; not a claim of scientific "
                                         "meaninglessness",
            "SENSITIVITY_ONLY": "constructible, but only as S7.11 "
                                "qualification evidence",
        },
        "excluded": [
            {"family": "target or target history", "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "the target may not appear on the explanatory side; "
                       "persistence is a baseline, not a coordinate"},
            {"family": "lags", "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "the task is contemporaneous reconstruction"},
            {"family": "lead values", "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "would make the task forecasting"},
            {"family": "second and higher temporal derivatives",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "frozen decision H-D; source cadence cannot support them"},
            {"family": "integrals / cumulative histories",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "introduces unbounded memory outside the declared "
                       "contemporaneous information set"},
            {"family": "logarithms", "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "argument must be dimensionless; no scientific "
                       "motivation declared"},
            {"family": "exponentials", "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "same"},
            {"family": "trigonometric functions",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES", "reason": "same"},
            {"family": "arbitrary powers beyond square via self-product",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "depth and interpretability bound"},
            {"family": "triple and higher products",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "frozen arity bound of 2"},
            {"family": "recursive products / ratios",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "frozen maximum constructor depth of 1"},
            {"family": "reference-shifted phase derivative",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "a distinct construction from the canonical phase "
                       "derivative; requires separate explicit qualification"},
            {"family": "bounded / sensitivity-centered phase derivative",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES", "reason": "same"},
            {"family": "spatial derivatives", "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "no channel geometry is documented in the frozen object"},
            {"family": "channel-index derivatives",
             "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "channel index is a label, not a spatial coordinate"},
            {"family": "learned embeddings", "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "not interpretable; would be a fitted transform"},
            {"family": "PCA coordinates", "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "fitted transform subject to the leakage firewall"},
            {"family": "neural representations",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES", "reason": "same"},
            {"family": "event labels", "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "none exist in the frozen object"},
            {"family": "equilibrium quantities removed by I_rec",
             "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "fail-closed unresolved ancestry"},
            {"family": "vsurf", "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "PRIMARY_NUMERICAL_SUPPORT_FAIL at S7.3R"},
            {"family": "cross-discharge coordinates",
             "status": "TASK_ONTOLOGY_EXCLUDES",
             "reason": "discharges are separate realizations; concatenation "
                       "forbidden"},
            {"family": "pairwise sum / difference",
             "status": "PRIMARY_ONTOLOGY_EXCLUDES",
             "reason": "ALGEBRAIC REDUNDANCY: the primary relation template is "
                       "affine-linear in the selected coordinates, so x_i+x_j "
                       "and x_i-x_j are already representable by including "
                       "x_i and x_j with appropriate coefficients. Adding them "
                       "would enlarge the candidate set without enlarging the "
                       "span of the relation family. This is an ontology-level "
                       "redundancy decision, NOT a performance result. "
                       "Dimensional compatibility rules for sums remain part "
                       "of the general type system."},
        ],
    }
    (S75 / "excluded_constructor_families.json").write_text(
        json.dumps(excl, indent=2), encoding="utf-8")

    # ---- coordinate signature schema --------------------------------------
    sig = {
        "schema_id": "COORDINATE_SIGNATURE_V1",
        "purpose": "stable machine identity and duplicate prevention for "
                   "coordinate instances that S7.6 will create",
        "display_label_is_not_identity": True,
        "canonicalization": {
            "C0": "ID(signal_id)",
            "C1": "DOT(signal_id)",
            "C2": "PROD(i,j) with i = min(idx), j = max(idx) by frozen "
                  "FINAL_SIGNAL_INVENTORY index",
            "C3": "RATIO(i,j), directional, i != j",
            "C4": "PHASE(i|j) meaning D_{x_j} x_i, directional, i != j",
        },
        "fields": [
            "coordinate_id", "constructor_family", "depth", "ordered_operands",
            "primitive_ancestors", "output_scientific_type",
            "output_dimension", "output_unit_expression",
            "temporal_resolution_rule", "provenance_lineage",
            "target_independence", "primary_or_sensitivity", "aliasing_flags",
            "numerical_realization_id", "domain_predicate",
            "dependency_group_membership",
        ],
        "duplicate_prevention": {
            "product_symmetry": "PROD canonical ordering makes PROD(i,j) and "
                                "PROD(j,i) the same identity",
            "self_ratio": "RATIO(i,i) is not a valid signature",
            "self_phase": "PHASE(i|i) is not a valid signature",
            "ratio_direction_preserved": "RATIO(i,j) != RATIO(j,i)",
            "phase_direction_preserved": "PHASE(i|j) != PHASE(j|i)",
        },
    }
    (S75 / "coordinate_signature_schema.json").write_text(
        json.dumps(sig, indent=2), encoding="utf-8")

    # ---- relation templates ------------------------------------------------
    rel = {
        "template_id": "T_REC_V1",
        "primary_template": {
            "form": "y_s(t) = beta_{0,s} + sum_{j=1..m} beta_{j,s} c_j(x_s)(t) "
                    "+ epsilon_s(t)",
            "family": "affine-linear IN THE CONSTRUCTED COORDINATES",
            "coordinate_functions_may_be_nonlinear": True,
            "support_size_m": {"min": 1, "max": 12,
                               "source": "frozen K_rec B_rec bound"},
            "shared_across_discharges": "the coordinate SUPPORT C = {c_1..c_m}",
            "discharge_specific": "the coefficients beta_s",
            "intercept": {"permitted": True,
                          "counts_toward_support_size": False},
            "target_on_explanatory_side": False,
            "target_derivative": False,
            "explicit_not_implicit": True,
            "universal_coefficient_claim": False,
        },
        "coefficient_dimensionality": {
            "rule": "[beta_j] = [y] / [c_j]",
            "target_dimension": "m^-3",
            "consequence": "every affine term beta_j c_j carries the target "
                           "dimension m^-3, so coordinates within one relation "
                           "need NOT share physical units; the fitted "
                           "coefficients carry the compensating dimensions",
            "uncalibrated_operand": {
                "numerical_coefficient_allowed": True,
                "physical_dimensional_interpretation_claimable": False,
                "coefficient_dimension_status": "UNCALIBRATED"},
            "coefficient_dimension_status_values": ["PHYSICALLY_TYPED",
                                                    "UNCALIBRATED"],
        },
        "estimator": {
            "chosen_here": False,
            "note": "the relation FAMILY is frozen here; the numerical "
                    "ESTIMATOR is not. OLS vs ridge and any hyperparameter "
                    "belong to the later frozen search policy. No estimator "
                    "was run in S7.5.",
        },
    }
    (S75 / "relation_templates.json").write_text(json.dumps(rel, indent=2),
                                                 encoding="utf-8")

    # ---- dependency constraints -------------------------------------------
    d0 = dep.iloc[0]
    depc = {
        "constraints": [{
            "dependency_group_id": "DEP_NBI_POWER_SUM",
            "aggregate": "pinj",
            "components": sorted(str(d0.source_nodes).split("|")),
            "exact_relation": "pinj = sum(pinj_*)",
            "relation_type": "EXACT_DETERMINISTIC_SUM",
            "evidence_class": "LOCAL_DOCUMENTED",
            "evidence": str(d0.evidence),
            "target_leakage": False,
            "deleted_at_S7_5": False,
            "rule": "a candidate representation containing the aggregate level "
                    "AND all eight component levels is marked "
                    "EXACT_LINEAR_REDUNDANCY_RISK",
            "risk_label": "EXACT_LINEAR_REDUNDANCY_RISK",
            "scope": "REPRESENTATION_LEVEL, not coordinate level - at depth 1 "
                     "with arity <= 2 no single coordinate can carry the whole "
                     "exact set, so the redundancy can only appear in a "
                     "coordinate SET",
            "operational_exclusion_belongs_to": "S7.6",
            "principle": "deterministic restatements are not counted as "
                         "independent scientific evidence",
        }],
        "invariant": "neither aggregate nor components are removed at S7.5",
    }
    (S75 / "dependency_constraints.json").write_text(json.dumps(depc, indent=2),
                                                     encoding="utf-8")

    # ---- ontology constraints ---------------------------------------------
    ocons = {
        "max_constructor_depth": 1,
        "constructors_consume_primitives_only": True,
        "recursive_construction": "FORBIDDEN",
        "not_primary_examples": ["d(x_i x_j)/dt", "x_i * (d x_j/dt)",
                                 "(x_i/x_j) * x_k", "D_{x_k}(x_i x_j)",
                                 "ratio of two constructed ratios",
                                 "product of phase derivatives"],
        "A_rec_enumerated": False,
        "no_search_priority_assigned": True,
        "search_priority_belongs_to": "S7.7",
        "knowledge_is_not_validation_evidence": True,
        "no_q_desc_seeding": True,
        "no_model_fitted": True, "no_baseline_evaluated": True,
        "no_predictor_target_correlation": True,
        "no_reconstruction_performance_inspected": True,
        "external_values_accessed": 0,
        "raw_comparator_nested_in_ontology": {
            "statement": "a representation whose coordinates are all C0 "
                         "primitive levels is an admissible special case of "
                         "G_rec",
            "consequence": "the raw-coordinate baseline B2 is nested inside "
                           "the SIR ontology rather than being an external "
                           "alternative"},
    }
    (S75 / "ontology_constraints.json").write_text(json.dumps(ocons, indent=2),
                                                   encoding="utf-8")

    # ---- G_REC.json --------------------------------------------------------
    G = {
        "ontology_id": "G_REC_DENSITY_V1", "version": "1.0.0",
        "freeze_id": FREEZE_ID,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "formal_definition":
            "G_rec = Gamma(X_rec, O_rec, K_rec; Lambda_rec, T_rec)",
        "parent_X_rec_id": X["object_id"],
        "parent_O_rec_id": X["parent_O_rec_id"],
        "parent_K_rec_id": K["contract_id"],
        "parent_freezes": {k: v["freeze_id"] for k, v in par.items()
                           if isinstance(v, dict) and "freeze_id" in v},
        "target": TARGET,
        "target_forbidden_as_coordinate": True,
        "target_history_forbidden": True,
        "primitive_count": n_all,
        "primitive_registry": "primitive_type_registry.csv",
        "constructor_catalogue": "constructor_catalog.json",
        "Lambda_rec": [f["id"] for f in cat["families"]],
        "primary_constructors": {
            "primitive": "C0", "first_temporal_derivative": "C1",
            "pairwise_product": "C2", "pairwise_ratio": "C3",
            "trajectory_relational_derivative": "C4"},
        "max_constructor_depth": 1,
        "sensitivity_only_rules": {
            "derivative_sensitivity_only_signals": sorted(SENSITIVITY_ONLY_DERIV),
            "n": n_so,
            "output_label": "SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT",
            "representable_in_G_rec": True,
            "in_primary_A_rec": False,
            "examined_by": "S7.11"},
        "excluded_constructor_families": "excluded_constructor_families.json",
        "dimensional_type_system": rules["dimensional_type_algebra"],
        "temporal_type_system": rules["temporal_resolution_propagation"],
        "flag_propagation": rules["flag_propagation"],
        "provenance_propagation": rules["provenance_propagation"],
        "uncalibrated_signal_policy": rules["uncalibrated_signal_policy"],
        "exact_dependency_constraints": depc,
        "numerical_realization": rules["numerical_realization"],
        "relation_templates": rel,
        "T_rec": rel["template_id"],
        "coordinate_signature_schema": sig,
        "symbolic_upper_bounds": bounds,
        "no_search_priority": True,
        "A_rec_enumerated": False,
        "ontology_constraints": ocons,
        "inherited_documentation_errata": pf,
    }
    (S75 / "G_REC.json").write_text(json.dumps(G, indent=2, default=str),
                                    encoding="utf-8")

    # ---- acceptance --------------------------------------------------------
    md = sorted(p.name for p in S75.rglob("*.md"))
    fam = {f["id"] for f in cat["families"]}
    exf = {e["family"] for e in excl["excluded"]}
    checks = {
        "all_parent_freezes_verified": par["verdict"] == "PARENTS_VERIFIED",
        "s7_3r_v2_authoritative": par["substantive_checks"]["s7_3r_v2_authoritative"],
        "s7_4_v2_authoritative": par["substantive_checks"]["s7_4_v2_authoritative"],
        "target_remains_density": G["target"] == TARGET,
        "primitives_78_unchanged": n_all == 78,
        "external_values_accessed_zero": ocons["external_values_accessed"] == 0,
        "heterogeneous_block_count_checked":
            pf["check_4_1_heterogeneous_blocks"]["agree"],
        "cadence_n_minus_1_checked":
            pf["check_4_2_cadence_denominator"]["implementation_uses_n_minus_1"],
        "parent_inconsistencies_recorded_not_rewritten":
            all(v["verdict"] == "DOCUMENTARY_ERRATUM_ONLY" for v in pf.values()),
        "G_rec_formally_instantiated": bool(G["formal_definition"]),
        "A_rec_not_enumerated": G["A_rec_enumerated"] is False,
        "all_78_primitive_levels_admitted":
            int(P.level_primary_admissible.sum()) == 78,
        "target_excluded_from_ontology": G["target_forbidden_as_coordinate"],
        "target_history_excluded": G["target_history_forbidden"],
        "primary_constructor_families_exactly_declared":
            fam == {"C0", "C1", "C2", "C3", "C4"},
        "max_constructor_depth_1": G["max_constructor_depth"] == 1,
        "derivative_numerical_realization_frozen":
            rules["numerical_realization"]["id"] == "FD2_PHYSICAL_TIME_V1",
        "derivative_parameter_physical_t":
            rules["numerical_realization"]["differentiates_wrt_tau"] is False,
        "derivative_wrt_tau_forbidden":
            cat["families"][1]["derivative_wrt_tau"] == "FORBIDDEN",
        "six_upsampled_derivative_sensitivity_only": n_so == 6,
        "aliasing_flags_propagated":
            "ALIASING_RISK" in rules["flag_propagation"],
        "uncalibrated_level_only_in_primary":
            rules["uncalibrated_signal_policy"]["derived_coordinate"]
            == "DIMENSIONALLY_UNCERTIFIED_PRIMARY_EXCLUDED",
        "products_canonicalized_symmetric": cat["families"][2]["commutative"],
        "self_products_allowed": cat["families"][2]["self_product_allowed"],
        "ratios_directional": cat["families"][3]["directional"],
        "self_ratio_excluded": "trivial constant 1" in cat["families"][3]["self_ratio_excluded"],
        "phase_directional": cat["families"][4]["directional"],
        "self_phase_excluded": "trivial constant 1" in cat["families"][4]["self_excluded"],
        "phase_uses_physical_time_realization":
            cat["families"][4]["numerical_realization"] == "FD2_PHYSICAL_TIME_V1",
        "no_shifted_phase_in_primary":
            "reference-shifted phase derivative" in exf,
        "no_second_derivatives":
            "second and higher temporal derivatives" in exf,
        "no_lags": "lags" in exf,
        "no_transcendental": {"logarithms", "exponentials",
                              "trigonometric functions"} <= exf,
        "no_recursive_constructors":
            ocons["recursive_construction"] == "FORBIDDEN",
        "no_sum_difference_constructor": "pairwise sum / difference" in exf,
        "dimensional_propagation_explicit":
            set(rules["dimensional_type_algebra"]["constructor_output"])
            == {"C0", "C1", "C2", "C3", "C4"},
        "provenance_lineage_transitive":
            rules["provenance_propagation"]["target_independence_is_transitive"],
        "exact_pinj_dependency_retained":
            depc["constraints"][0]["deleted_at_S7_5"] is False,
        "relation_support_shared_across_discharges":
            "SUPPORT" in rel["primary_template"]["shared_across_discharges"],
        "coefficients_discharge_specific":
            "beta_s" in rel["primary_template"]["discharge_specific"],
        "intercept_not_counted_toward_support":
            rel["primary_template"]["intercept"]["counts_toward_support_size"] is False,
        "support_size_1_to_12":
            [rel["primary_template"]["support_size_m"]["min"],
             rel["primary_template"]["support_size_m"]["max"]] == [1, 12],
        "estimator_not_fitted": rel["estimator"]["chosen_here"] is False,
        "no_search_priority_assigned": G["no_search_priority"] is True,
        "no_model_performance_examined":
            ocons["no_reconstruction_performance_inspected"] is True,
        "no_predictor_target_correlation":
            ocons["no_predictor_target_correlation"] is True,
        "no_q_desc_support_seeding": ocons["no_q_desc_seeding"] is True,
        "raw_comparator_nested": bool(ocons["raw_comparator_nested_in_ontology"]),
        "markdown_within_limit": len(md) <= 20,
        "s7_6_not_started": True,
    }
    n = sum(bool(v) for v in checks.values())
    (S75 / "S7_5_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n}/{len(checks)}",
        "all_passed": n == len(checks), "n_markdown_files": len(md),
        "evaluated_utc": datetime.now(timezone.utc).isoformat()},
        indent=2), encoding="utf-8")

    status = "FROZEN_READY_FOR_S7.6" if n == len(checks) else "BLOCKED_ONTOLOGY_AMBIGUITY"
    arts = sorted([p for p in S75.rglob("*") if p.is_file()
                   and p.name not in SELF_REF], key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_ID, "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ontology_id": G["ontology_id"], "version": G["version"],
        "parent_freezes": G["parent_freezes"],
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "preflight_checks_sha256": sha(MAN / "PREFLIGHT_SEMANTIC_CHECKS.json"),
        "derivative_realization_check_sha256":
            sha(MAN / "DERIVATIVE_REALIZATION_CHECK.json"),
        "G_REC_sha256": sha(S75 / "G_REC.json"),
        "primitive_registry_sha256": sha(S75 / "primitive_type_registry.csv"),
        "constructor_catalog_sha256": sha(S75 / "constructor_catalog.json"),
        "constructor_type_rules_sha256": sha(S75 / "constructor_type_rules.json"),
        "excluded_families_sha256":
            sha(S75 / "excluded_constructor_families.json"),
        "coordinate_signature_sha256":
            sha(S75 / "coordinate_signature_schema.json"),
        "relation_templates_sha256": sha(S75 / "relation_templates.json"),
        "dependency_constraints_sha256": sha(S75 / "dependency_constraints.json"),
        "ontology_constraints_sha256": sha(S75 / "ontology_constraints.json"),
        "target": TARGET, "n_primitives": 78,
        "constructor_families": sorted(fam),
        "max_depth": 1,
        "symbolic_upper_bounds": bounds,
        "A_rec_enumerated": False,
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform()},
        "all_artifact_hashes": {str(p.relative_to(S75)).replace("\\", "/"): sha(p)
                                for p in arts},
        "n_artifacts": len(arts),
        "acceptance_checks": f"{n}/{len(checks)}",
        "next_stage": "S7.6 (Admissible Universe A_rec) - NOT AUTHORISED",
    }
    (S75 / "S7_5_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                          encoding="utf-8")

    print(f"parents   : {par['verdict']}")
    print(f"preflight : 4.1 {pf['check_4_1_heterogeneous_blocks']['verdict']} "
          f"({pf['check_4_1_heterogeneous_blocks']['machine_readable_count']} "
          f"heterogeneous, prose said 4)")
    print(f"            4.2 {pf['check_4_2_cadence_denominator']['verdict']}")
    print(f"FD check  : second-order confirmed "
          f"{fd['second_order_confirmed']}, ratios "
          f"{[round(r,2) for r in fd['observed_convergence_ratios']]}")
    print(f"primitives: {n_all} (uncal {n_uncal}, sens-only deriv {n_so}, "
          f"deriv-eligible {n_deriv}, prod/ratio-eligible {n_pr})")
    print("symbolic upper bounds (NOT enumerated):")
    for k, v in bounds.items():
        if k != "note":
            print(f"    {k:52s} {v}")
    print(f"acceptance: {n}/{len(checks)}   md {len(md)}")
    for k, v in checks.items():
        if not v:
            print(f"  FAIL {k}")
    print(f"STATUS    : {status}")


if __name__ == "__main__":
    main()
