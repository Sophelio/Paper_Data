#!/usr/bin/env python
"""Generate the human-facing layer of Paper_Data: START_HERE indexes, per-
directory READMEs, the claim-to-artifact ledger and the audit reports.

Run after build_paper_data.py. Reads only the staged package and the canonical
artifacts; writes only inside Paper_Data.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\SIR_paper")
PKG = ROOT / "Paper_Data"
NOW = datetime.now(timezone.utc).isoformat()
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d")

STAGE = json.loads((PKG / "_staging_records.json").read_text(encoding="utf-8"))
RECS = STAGE["records"]


def w(rel: str, text: str):
    p = PKG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n", encoding="utf-8")


def wcsv(rel: str, rows: list[dict], cols: list[str]):
    p = PKG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: r.get(k, "") for k in cols})


def wjson(rel: str, obj):
    p = PKG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


# ==========================================================================
# Canonical values, re-extracted from the staged package so the ledger is
# evidence-backed rather than transcribed from the manuscript.
# ==========================================================================
def extract() -> dict:
    import pandas as pd
    QD = PKG / "04_DIII_D_DESCRIPTIVE" / "D3D-SIR-62-ALIGNED-V1"
    REC = PKG / "05_DIII_D_RECONSTRUCTION"
    v = {}
    pm = json.loads((QD / "canonical_run" / "d3d_pooled_metrics.json").read_text())
    v |= {"qdesc_pooled_rmse": pm["pooled_rmse"], "qdesc_pooled_mse": pm["pooled_mse"],
          "qdesc_mean_vector_rmse": pm["mean_vector_pooled_rmse"],
          "qdesc_n": pm["n_discharges"], "qdesc_samples": pm["n_samples_total"]}
    cs = json.loads((QD / "coefficient_conditioning" / "Correction_audit" / "outputs" /
                     "coefficient_conditioning_correction_summary.json").read_text())
    v |= {"cond_verdict": cs["corrected_overall_verdict"],
          "n_robust": cs["n_coefficients_robustly_resolved"],
          "n_unc": cs["n_coefficients_uncertainty_dominated"],
          "pos_dirs": cs["original_positive_multivariate_directions"],
          "robust_dirs": cs["corrected_robust_multivariate_directions"],
          "rank6_coef": cs["median_coefficient_change_rank6"],
          "rank6_rmse": cs["median_rmse_change_rank6"],
          "re_estimator": cs["random_effects_estimator_type"]}
    ie = QD / "implicit_elimination_audit" / "outputs"
    v |= {"implicit_verdict": json.loads((ie / "implicit_conditioning_summary.json"
                                          ).read_text())["overall_verdict"]}
    ea = json.loads((ie / "eliminated_A_summary.json").read_text())
    v |= {"min_abs_A": ea["min_abs_pooled"], "frac_A_1e4": ea["frac_abs_lt"]["0.0001"]}
    v |= {"ident_err": json.loads((ie / "elimination_identity_validation.json"
                                   ).read_text())["max_identity_error"]}
    sr = json.loads((ie / "shift_recovery_diagnostics.json").read_text())
    v |= {"shift_min": sr["shiftval_min"], "shift_max": sr["shiftval_max"]}
    v |= {"explicit_rmse": json.loads((ie / "explicit_closure_summary.json"
                                       ).read_text())["pooled_rmse"]}
    o1 = json.loads((PKG / "03_DIII_D_SOURCE_OBJECT" / "observational_object_S7_1" /
                     "reconciliation_final" / "S7_1_FINAL_FREEZE.json").read_text())
    v |= {"n_discharges": o1["n_shots"], "n_signals": o1["n_signals"],
          "n_pairs": o1["n_shots"] * o1["n_signals"]}
    b = pd.read_csv(REC / "01_Target_Selection_and_02_Information_Boundary" /
                    "reconciliation_source_resolution" /
                    "corrected_selected_target_boundary.csv")
    v |= {"n_pred": int((b.include_primary == True).sum()),
          "n_excl": int((b.include_primary == False).sum()),
          "n_excl_efit": int((b.exclusion_rule == "R5_unresolved_ancestry").sum()),
          "target": b[b.target_status == "TARGET"].signal.iloc[0]}
    v |= {"n_primitives": len(pd.read_csv(
        REC / "04_Initial_Ontology" / "05H_primitive_hardening" /
        "primitive_basis_hardened.csv"))}
    v |= {"n_symbolic": json.loads((REC / "04_Initial_Ontology" /
                                    "05H_primitive_hardening" / "S7_5H_FREEZE.json"
                                    ).read_text())["symbolic_primary_total"]}
    v |= {"n_atoms": len(pd.read_csv(
        REC / "04_Initial_Ontology" / "06_admissible_universe_10778" / "hardened_v2" /
        "primary_atomic_coordinate_universe.csv"))}
    f9 = json.loads((REC / "06_Frozen_Parent_Support" / "S7_9_FREEZE.json").read_text())
    v |= {"frontier": f9["selection_domain_cardinality"],
          "support_cap": f9["C_dev_star_size"], "C_dev_star": f9["C_dev_star"]}
    f10 = json.loads((REC / "07_Protected_Qualification_FAILURE" /
                      "S7_10_FREEZE.json").read_text())
    v |= {"parent_verdict": f10["primary_scientific_verdict"],
          "parent_REL": f10["method_means"]["REL"],
          "parent_B1": f10["method_means"]["B1"],
          "parent_D1": f10["V3"]["Delta_1"], "n_external": f10["external_cohort"]["n"]}
    k2 = json.loads((REC / "09_Range_Support_Case_B_Revision" /
                     "S7_K2_FREEZE.json").read_text())
    v |= {"tau": k2["tau"], "n_range": k2["epoch2_viability"]["full_domain_atoms"],
          "revision_class": k2["revision_class"]}
    E1 = REC / "12_Six_Fold_Target_Cross_Fitting"
    m = json.loads((E1 / "E2_1_CROSSFITTED_METRICS.json").read_text())
    v |= {"REL": m["method_summaries"]["REL"]["mean"],
          "B1": m["method_summaries"]["B1"]["mean"],
          "D0": m["paired"]["B0"]["mean_delta"], "D1": m["paired"]["B1"]["mean_delta"],
          "W": m["paired"]["B1"]["wins"], "T": m["paired"]["B1"]["ties"],
          "L": m["paired"]["B1"]["losses"],
          "era_e": m["era"]["Delta_1_earlier"], "era_l": m["era"]["Delta_1_later"],
          "n_e": m["era"]["era_counts"]["earlier"], "n_l": m["era"]["era_counts"]["later"]}
    f21 = json.loads((E1 / "E2_1_FREEZE.json").read_text())
    v |= {"jaccard": f21["support_stability"]["mean_pairwise_jaccard"]}
    sets = [set(json.loads((E1 / "folds" / f"fold_{k}_result.json").read_text()
                           )["coordinates"]) for k in range(6)]
    v |= {"union": len(set().union(*sets)), "sizes": [len(s) for s in sets],
          "in_all6": sorted(set.intersection(*sets))}
    d = pd.read_csv(E1 / "heldout_discharge_results.csv", dtype={"shot_id": str})
    v |= {"n_oof": len(d), "n_above1": int((d.REL_nrmse > 1.0).sum())}
    f12 = json.loads((REC / "17_Applicability_and_Final_Claim" / "S7_12_final" /
                      "S7_12_FREEZE.json").read_text())
    v |= {"final_status": f12["Q_REC_STATUS"], "clean": f12["CLEAN_DEMO_STATUS"]}
    return v


V = extract()

# ==========================================================================
# Claim ledger
# ==========================================================================
def C(cid, section, claim, shown, full, metric, pop, task, run, artifact, field,
      script, status="VERIFIED", notes=""):
    return dict(claim_id=cid, manuscript="SIR_paper_2026-09-02.pdf (STALE)",
                section=section, claim=claim, displayed_value=shown,
                full_precision_value=full, metric_definition=metric,
                population=pop, scientific_task=task, source_run=run,
                canonical_artifact=artifact, field_or_column=field,
                reproduction_script=script, audit_status=status, notes=notes)


QDR = "04_DIII_D_DESCRIPTIVE/D3D-SIR-62-ALIGNED-V1"
RCR = "05_DIII_D_RECONSTRUCTION"
E1R = f"{RCR}/12_Six_Fold_Target_Cross_Fitting"

CLAIMS = [
    C("OBJ-01", "Supplement S7.1", "62 DIII-D discharge realizations", "62",
      V["n_discharges"], "count", "observational object", "shared", "S7.1",
      "03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/reconciliation_final/S7_1_FINAL_FREEZE.json",
      "n_shots", "audit_s7.py"),
    C("OBJ-02", "Supplement S7.1", "95 source quantities", "95", V["n_signals"],
      "count", "observational object", "shared", "S7.1",
      "03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/reconciliation_final/FINAL_SIGNAL_INVENTORY.csv",
      "row count / n_signals", "audit_s7.py"),
    C("OBJ-03", "Supplement S7.1", "5,890 signal-discharge pairs", "5890",
      V["n_pairs"], "62 x 95", "observational object", "shared", "S7.1",
      "03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/availability_matrix.csv",
      "derived product", "audit_s7.py",
      notes="Derived as n_shots x n_signals; availability matrix carries the "
            "per-pair finite fraction."),

    C("DESC-01", "Results 1.5; Supplement S7.4", "pooled descriptive-fit RMSE",
      "5.76e-2", V["qdesc_pooled_rmse"],
      "sqrt(sum_j sum_k e^2 / sum_j N_j), standardized target", "62 discharges x 1000 samples",
      "q_desc", "D3D-SIR-62-ALIGNED-V1",
      f"{QDR}/canonical_run/d3d_pooled_metrics.json", "pooled_rmse",
      "verify_paper_data.py"),
    C("DESC-02", "Supplement S7.4", "cohort-mean coefficient-vector RMSE", "0.413",
      V["qdesc_mean_vector_rmse"], "pooled RMSE applying the cohort-mean vector",
      "62 discharges", "q_desc", "D3D-SIR-62-ALIGNED-V1",
      f"{QDR}/canonical_run/d3d_pooled_metrics.json", "mean_vector_pooled_rmse",
      "verify_paper_data.py",
      notes="Demonstrates that the reported 0.0576 is a discharge-specific "
            "coefficient fit on a shared support, not one universal equation."),
    C("DESC-03", "Results 1.5; Supplement S7.3",
      "shared seven-coordinate descriptive support", "7 coordinates", 7,
      "support size", "62 discharges", "q_desc", "D3D-SIR-62-ALIGNED-V1",
      f"{QDR}/canonical_run/d3d_discharge_coefficients.csv",
      "coef_* columns", "verify_paper_data.py"),
    C("DESC-04", "Supplement S7.7", "coefficient identifiability verdict",
      "mixed", V["cond_verdict"], "categorical verdict", "62 discharges",
      "q_desc", "D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
      f"{QDR}/coefficient_conditioning/Correction_audit/outputs/coefficient_conditioning_correction_summary.json",
      "corrected_overall_verdict", "run_correction_audit.py"),
    C("DESC-05", "Supplement S7.7",
      "five coefficients robustly resolved, two uncertainty-dominated", "5 / 2",
      f'{V["n_robust"]} / {V["n_unc"]}', "classification count", "7 coefficients",
      "q_desc", "D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
      f"{QDR}/coefficient_conditioning/Correction_audit/tables/corrected_coefficient_classification.csv",
      "corrected_status", "run_correction_audit.py"),
    C("DESC-06", "Supplement S7.7.4",
      "two robust multivariate coefficient-space directions of five positive",
      "2 of 5", f'{V["robust_dirs"]} of {V["pos_dirs"]}', "eigenvalue count",
      "7x7 covariance", "q_desc", "D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
      f"{QDR}/coefficient_conditioning/Correction_audit/tables/d3d_multivariate_eigenvalue_intervals.csv",
      "status", "run_correction_audit.py",
      notes="5,000 discharge-bootstrap and 5,000 matched-null replicates."),
    C("DESC-07", "Supplement S7.7.2", "rank-6 truncation perturbation",
      "0.799 / 0.031", f'{V["rank6_coef"]} / {V["rank6_rmse"]}',
      "median relative coefficient change / median absolute RMSE change",
      "62 discharges", "q_desc", "D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
      f"{QDR}/coefficient_conditioning/Correction_audit/outputs/coefficient_conditioning_correction_summary.json",
      "median_coefficient_change_rank6 / median_rmse_change_rank6",
      "run_correction_audit.py"),
    C("DESC-08", "Supplement S7.6", "implicit-closure conditioning verdict",
      "ill-conditioned", V["implicit_verdict"], "categorical verdict",
      "62 discharges", "q_desc", "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
      f"{QDR}/implicit_elimination_audit/outputs/implicit_conditioning_summary.json",
      "overall_verdict", "run_implicit_conditioning_audit.py"),
    C("DESC-09", "Supplement S7.6", "minimum |A| after elimination", "2.6e-7",
      V["min_abs_A"], "min over pooled samples", "62,000 samples", "q_desc",
      "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
      f"{QDR}/implicit_elimination_audit/outputs/eliminated_A_summary.json",
      "min_abs_pooled", "run_implicit_conditioning_audit.py"),
    C("DESC-10", "Supplement S7.6", "fraction of samples with |A| < 1e-4",
      "not stated in manuscript", V["frac_A_1e4"], "fraction", "62,000 samples",
      "q_desc", "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
      f"{QDR}/implicit_elimination_audit/outputs/eliminated_A_summary.json",
      'frac_abs_lt["0.0001"]', "run_implicit_conditioning_audit.py",
      notes="An audit briefing expected ~41%. The canonical value is 0.24%. "
            "0.4125 is the cohort-mean-vector RMSE, not this fraction."),
    C("DESC-11", "Supplement S7.6", "shift-value range", "14.64-24.24",
      f'{V["shift_min"]} - {V["shift_max"]}', "per-discharge shiftval",
      "62 discharges", "q_desc", "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
      f"{QDR}/implicit_elimination_audit/outputs/shift_recovery_diagnostics.json",
      "shiftval_min / shiftval_max", "run_implicit_conditioning_audit.py"),
    C("DESC-12", "Supplement S7.6", "elimination identity error", "machine precision",
      V["ident_err"], "max |A*y - B - eps|", "62,000 samples", "q_desc",
      "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
      f"{QDR}/implicit_elimination_audit/outputs/elimination_identity_validation.json",
      "max_identity_error", "run_implicit_conditioning_audit.py"),
    C("DESC-13", "Supplement S7.6", "explicit-closure pooled RMSE", "not stated",
      V["explicit_rmse"], "pooled RMSE of the explicit form", "62 discharges",
      "q_desc", "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
      f"{QDR}/implicit_elimination_audit/outputs/explicit_closure_summary.json",
      "pooled_rmse", "run_implicit_conditioning_audit.py"),

    C("REC-01", "Supplement S7 (current lineage)", "q_rec target instance",
      "density", V["target"], "categorical", "62 discharges", "q_rec",
      "D3D-SIR-S7.3-...-SOURCE-RESOLUTION-V2",
      f"{RCR}/01_Target_Selection_and_02_Information_Boundary/reconciliation_source_resolution/corrected_selected_target_boundary.csv",
      "target_status == TARGET", "audit_s7.py",
      status="VERIFIED_BUT_MANUSCRIPT_DISAGREES",
      notes="The staged manuscript PDF still names I_p. That branch was retired; "
            "see 10_REFERENCED_HISTORICAL_LINEAGE."),
    C("REC-02", "Supplement S7", "78 admitted predictor primitives", "78",
      V["n_pred"], "count", "95 quantities", "q_rec",
      "D3D-SIR-S7.3-...-SOURCE-RESOLUTION-V2",
      f"{RCR}/01_Target_Selection_and_02_Information_Boundary/reconciliation_source_resolution/corrected_selected_target_boundary.csv",
      "include_primary == True", "audit_s7.py",
      notes=f'{V["n_excl"]} excluded: 1 target, 1 numerical-support failure, '
            f'{V["n_excl_efit"]} EFIT quantities fail-closed on unresolved ancestry.'),
    C("REC-03", "Supplement S7", "hardened level basis of 70 primitives", "70",
      V["n_primitives"], "count", "78 admitted", "q_rec",
      "D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1",
      f"{RCR}/04_Initial_Ontology/05H_primitive_hardening/primitive_basis_hardened.csv",
      "row count", "audit_s7.py"),
    C("REC-04", "Supplement S7", "23,861 symbolic candidates", "23,861",
      V["n_symbolic"], "count", "symbolic space", "q_rec",
      "D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1",
      f"{RCR}/04_Initial_Ontology/05H_primitive_hardening/S7_5H_FREEZE.json",
      "symbolic_primary_total", "audit_s7.py"),
    C("REC-05", "Supplement S7", "10,778 admissible evaluated atoms", "10,778",
      V["n_atoms"], "count", "admissible universe", "q_rec",
      "D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2",
      f"{RCR}/04_Initial_Ontology/06_admissible_universe_10778/hardened_v2/primary_atomic_coordinate_universe.csv",
      "row count", "audit_s7.py"),
    C("REC-06", "Supplement S7", "explored frontier 162,845 supports", "162,845",
      V["frontier"], "count of explored supports", "development cohort", "q_rec",
      "D3D-SIR-S7.7-...-V2", f"{RCR}/06_Frozen_Parent_Support/S7_9_FREEZE.json",
      "selection_domain_cardinality", "audit_s7.py"),
    C("REC-07", "Supplement S7", "support cap 12", "12", V["support_cap"],
      "max support size", "search bound", "q_rec", "D3D-SIR-S7.2/S7.7",
      f"{RCR}/00_Pretarget_Contract/SEARCH_BOUND_POLICY.md",
      "support_size_bound [1,12]", "audit_s7.py"),
    C("REC-08", "Supplement S7", "20 development / 42 protected discharges",
      "20 / 42", f'20 / {V["n_external"]}', "cohort partition", "62 discharges",
      "q_rec", "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-V1",
      f"{RCR}/00_Pretarget_Contract/COHORT_PARTITION.json",
      "development / external shot_ids", "audit_s7.py"),
    C("REC-09", "Supplement S7 (MISSING from manuscript)",
      "parent external qualification FAILED", "not in manuscript",
      V["parent_verdict"], "categorical verdict", "42 protected discharges",
      "q_rec", "D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1",
      f"{RCR}/07_Protected_Qualification_FAILURE/S7_10_FREEZE.json",
      "primary_scientific_verdict", "audit_s7.py",
      status="VERIFIED_MISSING_FROM_MANUSCRIPT",
      notes=f'REL mean {V["parent_REL"]:.6f} vs persistence {V["parent_B1"]:.6f}; '
            f'Delta_1 = +{V["parent_D1"]:.6f}. The negative result is preserved.'),
    C("REC-10", "Supplement S7", "range-support hardening to 3,451 atoms", "3,451",
      V["n_range"], "count at tau = 1", "10,778 atoms", "q_rec",
      "D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1",
      f"{RCR}/09_Range_Support_Case_B_Revision/range_support_threshold_sensitivity.csv",
      "atoms_full_domain_62 at tau=1.0", "_audit/verify_range_support.py",
      notes=f'tau = {V["tau"]}; revision_class = {V["revision_class"]}.'),
    C("REC-11", "Supplement S7", "six deterministic target-cross-fitted folds", "6",
      6, "fold count", "62 discharges", "q_rec", "D3D-SIR-S7.E2.0-...-V1",
      f"{RCR}/11_Descendant_Case_C_Contract/E2_0_protocol/outer_fold_assignment.csv",
      "outer_fold", "audit_s7.py"),
    C("REC-12", "Supplement S7", "six distinct size-12 supports", "6 x 12",
      str(V["sizes"]), "support sizes", "six folds", "q_rec",
      "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/folds/fold_k_result.json",
      "coordinates", "audit_s7.py"),
    C("REC-13", "Supplement S7", "union of 35 coordinates", "35", V["union"],
      "cardinality of the union", "six supports", "q_rec",
      "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/coordinate_recurrence.csv",
      "row count", "audit_s7.py"),
    C("REC-14", "Supplement S7", "mean pairwise Jaccard", "0.285", V["jaccard"],
      "mean over 15 fold pairs", "six supports", "q_rec",
      "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/support_recurrence.csv",
      "jaccard", "audit_s7.py",
      notes=f'Coordinates in all six: {", ".join(V["in_all6"])}.'),
    C("REC-15", "Supplement S7", "cross-fitted mean NRMSE vs persistence",
      "0.189 vs 0.216", f'{V["REL"]:.6f} vs {V["B1"]:.6f}',
      "mean over out-of-fold discharge NRMSE", f'{V["n_oof"]} discharges',
      "q_rec", "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/heldout_discharge_results.csv",
      "REL_nrmse / B1_nrmse", "audit_s7.py"),
    C("REC-16", "Supplement S7", "Delta NRMSE against persistence", "-0.0273",
      V["D1"], "paired mean difference", f'{V["n_oof"]} discharges', "q_rec",
      "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/E2_1_CROSSFITTED_METRICS.json",
      "paired.B1.mean_delta", "audit_s7.py",
      notes=f'W/T/L {V["W"]}/{V["T"]}/{V["L"]} using the contract practical-'
            f'equivalence floor 0.01. Delta_0 vs calibration mean {V["D0"]:.6f}.'),
    C("REC-17", "Supplement S7", "era-stratified point estimates",
      "+0.0076 / -0.0726", f'{V["era_e"]:+.6f} / {V["era_l"]:+.6f}',
      "paired mean difference vs persistence, per era",
      f'earlier n={V["n_e"]}, later n={V["n_l"]}', "q_rec",
      "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/E2_1_CROSSFITTED_METRICS.json",
      "era.Delta_1_earlier / era.Delta_1_later", "audit_s7.py",
      notes="The pooled pass is carried by the later era; the earlier era is a "
            "practical tie."),
    C("REC-18", "Supplement S7", "no held-out discharge exceeds NRMSE 1",
      "0", V["n_above1"], "count", f'{V["n_oof"]} discharges', "q_rec",
      "D3D-SIR-S7.E2.1-...-V1", f"{E1R}/heldout_discharge_results.csv",
      "REL_nrmse > 1.0", "audit_s7.py"),
    C("REC-19", "Supplement S7", "final qualified status", "not in manuscript",
      f'{V["final_status"]} / {V["clean"]}', "categorical", "62 discharges",
      "q_rec", "D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1",
      f"{RCR}/17_Applicability_and_Final_Claim/S7_12_final/S7_12_FREEZE.json",
      "Q_REC_STATUS / CLEAN_DEMO_STATUS", "audit_s7.py",
      status="VERIFIED_MISSING_FROM_MANUSCRIPT"),
]

wcsv("00_START_HERE/CLAIM_TO_ARTIFACT_INDEX.csv", CLAIMS,
     ["claim_id", "manuscript", "section", "claim", "displayed_value",
      "full_precision_value", "metric_definition", "population",
      "scientific_task", "source_run", "canonical_artifact", "field_or_column",
      "reproduction_script", "audit_status", "notes"])
wjson("07_TABLES_AND_REPORTED_NUMBERS/numerical_claims/claim_ledger.json",
      {"record_id": "SIR_CLAIM_LEDGER_V1", "generated_utc": NOW,
       "n_claims": len(CLAIMS), "claims": CLAIMS,
       "canonical_values": V})

# ==========================================================================
# Run index
# ==========================================================================
RUNS = [
    dict(run_id="D3D-SIR-62-ALIGNED-V1", task="q_desc", status="CANONICAL",
         description="Canonical 62-discharge aligned descriptive run",
         package_path=f"{QDR}/canonical_run",
         supports="Results 1.5; Supplement S7.1-S7.4; Figure 6 panels a-b"),
    dict(run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1", task="q_desc",
         status="CANONICAL", description="Corrected coefficient conditioning and "
         "identifiability audit; supersedes D3D-SIR-62-COEFFICIENT-CONDITIONING-V1",
         package_path=f"{QDR}/coefficient_conditioning/Correction_audit",
         supports="Supplement S7.7; Supplementary Figure S1"),
    dict(run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-V1", task="q_desc",
         status="SUPERSEDED", description="Original conditioning audit; carried the "
         "retired verdict D3D-COEFFICIENT-FAMILY-RESOLVED and mislabelled profile-ML "
         "as REML", package_path=f"{QDR}/coefficient_conditioning",
         supports="Supplement S7.7 (documents its correction)"),
    dict(run_id="D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1", task="q_desc",
         status="CANONICAL", description="Implicit elimination and denominator "
         "conditioning", package_path=f"{QDR}/implicit_elimination_audit",
         supports="Supplement S7.6"),
    dict(run_id="D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1", task="shared",
         status="CANONICAL", description="Frozen 62-discharge / 95-quantity object",
         package_path="03_DIII_D_SOURCE_OBJECT/observational_object_S7_1",
         supports="Supplement S7.1"),
    dict(run_id="D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1",
         task="q_rec", status="CANONICAL", description="Parent development "
         "selection and pre-external freeze",
         package_path=f"{RCR}/06_Frozen_Parent_Support", supports="Supplement S7"),
    dict(run_id="D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1",
         task="q_rec", status="CANONICAL_NEGATIVE_RESULT",
         description="Parent protected qualification FAILURE",
         package_path=f"{RCR}/07_Protected_Qualification_FAILURE",
         supports="Supplement S7 (absent from the staged manuscript)"),
    dict(run_id="D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1", task="q_rec",
         status="CANONICAL", description="Operational-state explanation tested and "
         "REFUTED", package_path=f"{RCR}/08_Failure_Diagnosis/R1_operational_state",
         supports="Supplement S7"),
    dict(run_id="D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1",
         task="q_rec", status="CANONICAL", description="Case-B operational-contract "
         "revision; 10,778 -> 3,451 atoms at tau = 1",
         package_path=f"{RCR}/09_Range_Support_Case_B_Revision",
         supports="Supplement S7"),
    dict(run_id="D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
         task="q_rec", status="CANONICAL_PRIMARY_RESULT",
         description="Six-fold target-cross-fitted discovery and qualification",
         package_path=E1R, supports="Supplement S7; Figure 6 panels c-d"),
    dict(run_id="D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1", task="q_rec",
         status="CANONICAL_FINAL", description="Q_rec*, branch closure",
         package_path=f"{RCR}/17_Applicability_and_Final_Claim/S7_12_final",
         supports="Supplement S7"),
    dict(run_id="D3D-FIG6-QREC-RETIREMENT-V1", task="q_rec (retired)",
         status="RETIRED", description="Retirement of the I_p reconstruction branch "
         "for target-provenance leakage and no skill over persistence",
         package_path="10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch",
         supports="The staged manuscript still reports this retired branch"),
    dict(run_id="SIR-LORENZ-BENCHMARK", task="controlled", status="CANONICAL",
         description="Lorenz fixed-representation containment",
         package_path="02_CONTROLLED_STUDIES/01_Lorenz_Generator_Containment",
         supports="Results 1.3, 1.4; Supplement S6"),
    dict(run_id="SIR-LORENZ-TASK-CONDITIONING", task="controlled",
         status="CANONICAL", description="Partially observed Lorenz representation "
         "discovery and task conditioning",
         package_path="02_CONTROLLED_STUDIES/02_Lorenz_Representation_Discovery",
         supports="Results 1.3, 1.4; Figure 5; Supplement S6"),
]
wcsv("00_START_HERE/RUN_INDEX.csv", RUNS,
     ["run_id", "task", "status", "description", "package_path", "supports"])

# ==========================================================================
# Figure index
# ==========================================================================
FIGROWS = [
    dict(figure="Figure 1", folder="Fig_01_admissible_relational_space",
         asset="admissible_relational_space_hierarchical_v15_metaball.pdf",
         script="General/admissible_relational_space_hierarchical_v15_metaball_final.py "
                "(and ..._metaball.py)",
         data="none (schematic)", run_id="", status="AMBIGUOUS",
         notes="Both scripts declare the SAME output stem "
               "'admissible_relational_space_hierarchical_v15_metaball'. The asset on "
               "disk has the mtime of the NON-final script; the _final script is newer "
               "and has apparently never been rendered. Neither script can emit the "
               "'..._metaball_final.pdf' filename referenced in the figure cross-check."),
    dict(figure="Figure 2", folder="Fig_02_phase_turning_manifold",
         asset="phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf",
         script="DIIID_example/phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py",
         data="none (analytic)", run_id="", status="VERIFIED",
         notes="Script declares this exact stem. v4/v7 retained under "
               "02_CONTROLLED_STUDIES/06 as superseded lineage."),
    dict(figure="Figure 4", folder="Fig_04_task_contracts_representations",
         asset="figure4_task_contracts_mathematical_representations_nature_one_row.pdf",
         script="Pendulum/Plotter/figure4_task_contracts_mathematical_representations_nature_one_row.py",
         data="Pendulum/Plotter/panel_data.py", run_id="SIR-PENDULUM",
         status="VERIFIED_WITH_MANUAL_STEP",
         notes="Script writes to Pendulum/Plotter/figs; the asset was relocated by "
               "hand to Figures/figs. Manual relocation recorded."),
    dict(figure="Figure 5", folder="Fig_05_lorenz_representation_landscape",
         asset="figure5_lorenz_representation_landscape_final_tnr_v5_nature.pdf",
         script="Lorenz/figure5_lorenz_representation_landscape_final_tnr_v5_nature.py",
         data="Lorenz/fig5data (10 frozen files)",
         run_id="SIR-LORENZ-TASK-CONDITIONING", status="VERIFIED",
         notes="v4 and the two prototypes retained as superseded lineage, not copied "
               "into 06_PAPER_FIGURES_ONLY."),
    dict(figure="Figure 6", folder="Fig_06_d3d_task_conditioned_4panel",
         asset="d3d_task_conditioned_4panel_v5.pdf",
         script="DIIID_example/d3d_task_conditioned_4panel_v5.py",
         data="DIIID_example/fig6data (11 frozen files)",
         run_id="D3D-SIR-62-ALIGNED-V1 + D3D-SIR-S7.E2.1-...-V1",
         status="VERIFIED",
         notes="Script has a preflight check and an optional cross-check against the "
               "pre-derived 6x35 fold-support matrix. Panels: a-b q_desc, c-d q_rec."),
    dict(figure="Supplementary Figure S1 (panel a)",
         folder="Supplementary_Figures/FigS1_coefficient_conditioning",
         asset="d3d_coefficient_change_vs_rank_removed.pdf",
         script="Coefficient_conditioning/Correction_audit/generate_correction_figures.py",
         data="Correction_audit/outputs + tables",
         run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
         status="VERIFIED", notes="PDF only; PNG/SVG exist under the un-prefixed name."),
    dict(figure="Supplementary Figure S1 (panel b)",
         folder="Supplementary_Figures/FigS1_coefficient_conditioning",
         asset="d3d_heterogeneity_interval_by_coefficient.pdf",
         script="Coefficient_conditioning/Correction_audit/generate_correction_figures.py",
         data="Correction_audit/tables/corrected_coefficient_heterogeneity_primary.csv",
         run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
         status="VERIFIED", notes="PDF only."),
    dict(figure="Supplementary Figure S1 (panel c)",
         folder="Supplementary_Figures/FigS1_coefficient_conditioning",
         asset="d3d_multivariate_eigenvalue_uncertainty.pdf",
         script="Coefficient_conditioning/Correction_audit/generate_correction_figures.py",
         data="Correction_audit/tables/d3d_multivariate_eigenvalue_intervals.csv",
         run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
         status="VERIFIED", notes="PDF only."),
]
wcsv("00_START_HERE/FIGURE_TO_SOURCE_INDEX.csv", FIGROWS,
     ["figure", "folder", "asset", "script", "data", "run_id", "status", "notes"])

wcsv("00_START_HERE/TABLE_TO_SOURCE_INDEX.csv", [
    dict(table="Supplement S7 Table S4 (observational roles)",
         source="03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/reconciliation_final/FINAL_SIGNAL_INVENTORY.csv",
         run_id="D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1", status="VERIFIED",
         notes="Signal inventory with group, semantic type, provenance status."),
    dict(table="Lorenz benchmark summary table",
         source="02_CONTROLLED_STUDIES/01_Lorenz_Generator_Containment/tables/benchmark_summary.tex",
         run_id="SIR-LORENZ-BENCHMARK", status="VERIFIED",
         notes="TeX table fragment plus the JSON results it is built from."),
    dict(table="Lorenz task-conditioning summary table",
         source="02_CONTROLLED_STUDIES/02_Lorenz_Representation_Discovery/tables/benchmark_summary.tex",
         run_id="SIR-LORENZ-TASK-CONDITIONING", status="VERIFIED", notes=""),
    dict(table="q_desc coefficient summary",
         source=f"{QDR}/canonical_run/d3d_coefficient_summary.csv",
         run_id="D3D-SIR-62-ALIGNED-V1", status="VERIFIED",
         notes="Per-term mean/median/quantiles across the 62 discharge fits."),
    dict(table="Coefficient classification (5 robust / 2 uncertainty-dominated)",
         source=f"{QDR}/coefficient_conditioning/Correction_audit/tables/corrected_coefficient_classification.csv",
         run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
         status="VERIFIED", notes=""),
], ["table", "source", "run_id", "status", "notes"])
print("indexes written")
