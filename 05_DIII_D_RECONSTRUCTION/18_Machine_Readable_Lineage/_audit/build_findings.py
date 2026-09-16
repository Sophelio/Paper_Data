"""Emit AUDIT_REPORT.json - the machine-readable forensic findings."""
import json
from datetime import datetime, timezone
from pathlib import Path

S7 = Path(__file__).resolve().parent.parent


def F(i, level, title, detail, where, action, resolved):
    return {"finding_id": i, "level": level, "title": title, "detail": detail,
            "location": where, "action": action, "resolved_by_this_audit": resolved}


FINDINGS = [
    F("F-1", "MAJOR",
      "The manuscript's q_rec result is a retired branch",
      "Results 1.5, Fig. 4b and Supplementary S7.8 present the I_p / 141-coordinate "
      "/ 7-development / 55-external / REL10 result, retired 2026-09-02 under "
      "D3D-FIG6-QREC-RETIREMENT-V1 for target-provenance leakage (6/10 REL10 and "
      "4/10 RAW10 features carry upstream I_p dependence; q95 is essentially "
      "shape*a^2*Bt/I_p with 7.3% residual scatter) and for having no skill over a "
      "persistence baseline (persistence 0.0685 beats REL141 0.1137, REL10 0.1257, "
      "RAW10 0.1821).",
      "manuscript draft/SIR_paper.pdf - NOT S7",
      "Replace with the canonical q_rec density result; text and numbers ready in "
      "S7_12_qualified_result/S7_12_MANUSCRIPT_SUMMARY.md and "
      "MANUSCRIPT_ALIGNMENT.md section 5.",
      False),
    F("F-2", "MAJOR",
      "Results 1.1 predates the architecture S7 instantiates",
      "The shipped 1.1 defines K_q as one flat 8-tuple with no claim-defining core, "
      "no operational contract, no operational epoch and no defect/reconciliation "
      "machinery; a text search finds zero occurrences of claim-defining, "
      "operational contract, operational epoch, defect record, reconciliation, "
      "earliest invalidated, j_min, range support, cross-fitted or Epoch. It also "
      "retains the superseded blanket rule that data reserved for final validation "
      "must never influence a revised ontology or search policy.",
      "manuscript draft/SIR_paper.pdf - NOT S7",
      "Adopt K_q^(e) = (K^claim, K^op,(e)) and replace the blanket rule with the "
      "protected-evidence rule.",
      False),
    F("F-3", "MINOR",
      "q_desc canonical artifacts are outside S7",
      "The descriptive branch's canonical run, coefficient-conditioning correction "
      "and implicit-elimination packages live under D:\\sir-web\\Paper Examples\\, "
      "so q_desc cannot be audited from the S7 folder alone. They were verified "
      "read-only and not modified or relocated.",
      "package scope",
      "Recorded in WORKFLOW.md section 7 and AUDIT_REPORT.md section 5. Consider "
      "mirroring the q_desc package so both branches are auditable from one place.",
      True),
    F("F-4", "MINOR",
      "Three PDF figures missing from the external correction-audit manifest",
      "74 of 77 manifest entries reproduce; missing are "
      "figures/coefficient_change_vs_rank_removed.pdf, "
      "figures/heterogeneity_interval_by_coefficient.pdf and "
      "figures/multivariate_eigenvalue_uncertainty.pdf. The PNG and SVG versions "
      "of all three exist.",
      "external: Coefficient_conditioning/Correction_audit",
      "Regenerate the vector PDFs, or amend the manifest. No numerical result is "
      "affected.",
      False),
    F("F-5", "MINOR",
      "Three-cell floating-point tie at tau = 0",
      "An independent re-implementation of the range-support predicate reproduces "
      "the frozen sensitivity table exactly at tau = 0.25, 0.5, 1, 2, 5 and 10, and "
      "differs at tau = 0 by exactly 3 cells of 2,004,708 (1.4965e-6) - an "
      "exact-zero tie at the strict-interpolation boundary. The full-domain atom "
      "count at tau = 0 still matches exactly (9).",
      "S7.K2 range_support_threshold_sensitivity.csv",
      "No action. tau = 0 is not the frozen threshold and no canonical result "
      "depends on it. Recorded in _audit/range_support_independent_recomputation.json.",
      True),
    F("F-6", "MINOR",
      "Rounding in a repeated prose statement",
      "Several documents state that no support in the Epoch-1 development-equivalent "
      "family beat persistence by more than 0.0287. The exact best margin is "
      "-0.028742, which marginally exceeds that bound at the fifth decimal.",
      "S7.11-derived prose in four FROZEN documents: "
      "E2_1_FINAL_RESULT.md, S7_12_CLAIM_BOUNDARY.md, "
      "S7_12_QUALIFIED_RESULT_AUDIT_REPORT.md, S7_12_QUALIFIED_RESULT_FINAL.md",
      "RECORDED AS AN ERRATUM, NOT APPLIED. Editing those files would change their "
      "bytes and break byte-for-byte reproduction across their stage freezes, for a "
      "4e-5 rounding artifact that changes no conclusion. Any future edition should "
      "use -0.028742 or say 'by more than 0.0288'. The substantive point - that "
      "Epoch 2's -0.027308 sits essentially at the Epoch-1 family ceiling - is "
      "unchanged and correct.",
      True),
    F("F-7", "DOCUMENTATION",
      "S7.1 uses a heterogeneous hashing convention",
      "The S7.1 final freeze records nine named per-artifact hashes rather than an "
      "all_artifact_hashes map. Seven are file-byte hashes; two "
      "(signal_inventory_sha256, quality_summary_sha256) are canonical "
      "DataFrame-serialization hashes. All nine reproduce.",
      "S7.1",
      "audit_s7.py verifies all nine under both conventions and reports them "
      "explicitly.",
      True),
    F("F-8", "DOCUMENTATION",
      "The prmtan_neped ablation is not cross-referenced from Epoch 2",
      "prmtan_neped appears in all six Epoch-2 fold supports and in C_E2_ALL_DESC, "
      "but the predeclared ablation bounding its target proximity "
      "(PRMTAN_NEPED_ONLY: mean NRMSE 0.4632, Delta_1 +0.2529, V3-style FAIL) is "
      "recorded only in S7.11.",
      "cross-reference between S7.11 and E2.1/E2.2",
      "Recorded and quantified in INFORMATION_FLOW_AUDIT.md section 2, which is "
      "linked from the dashboard and from the E2 stage pages.",
      True),
    F("F-9", "DOCUMENTATION",
      "An audit-briefing checkpoint is unsupported by the frozen artifacts",
      "A checkpoint expected about 41% of samples with |A| < 1e-4 in the implicit "
      "elimination analysis. The frozen value is frac_abs_lt['0.0001'] = 0.002355, "
      "i.e. 0.24%. The only 0.41 in that package is 0.4125238316, the cohort-mean "
      "vector pooled RMSE. Confirmed instead: min |A| = 2.6428e-07, shift values "
      "14.643-24.243, elimination identity max error 7.896e-15.",
      "audit briefing, not the manuscript",
      "Recorded in MANUSCRIPT_ALIGNMENT.md section 6. No manuscript text is "
      "affected.",
      True),
    F("F-10", "COSMETIC",
      "Empty _logs directory",
      "S7/_logs/ contains no files.",
      "S7",
      "Retained as a declared location and documented in WORKFLOW.md section 6.",
      True),
]

VERIFIED = {
    "freeze_integrity": {
        "canonical_stages": 21,
        "frozen_artifacts_reproducing": 527, "frozen_artifacts_checked": 527,
        "S7_1_named_hashes": "9/9",
        "duplicate_content_groups": 3,
        "note": "_e2_1_basis.npz is byte-identical to _e2_2_basis.npz, so E2.2's "
                "independent recomputation of the range-support matrix reproduced "
                "E2.1's exactly"},
    "range_support_reimplemented": {
        "tau_grid": [0.0, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
        "survivors": [9, 1026, 2099, 3451, 5957, 8722, 9559],
        "all_match_frozen": True,
        "cell_rate_exact_except": [0.0],
        "degenerate_cells": 263, "of_cells": 2004708,
        "constructor_counts_tau1": {"C0": 51, "C1": 18, "C2": 1488, "C3": 382,
                                    "C5": 8, "C6": 965, "C7": 539},
        "monotone": True, "epsilon_used": False},
    "epoch1": {"REL_mean": 0.7423647781201324, "B1_mean": 0.21027421611172853,
               "Delta_0": -0.18009502685176143, "Delta_1": 0.5320905620084037,
               "V3": "FAIL", "shot_187019": 11.952633, "shot_187022": 11.766572,
               "n_above_1": 2,
               "family": {"n": 217, "full_domain": 213, "V3_style_pass": 70,
                          "C_dev_star_rank": "184/213",
                          "gasa2_in_passers": 0, "gasa2_in_failures": 67,
                          "best_Delta_1": -0.028742},
               "all_recomputed": True},
    "epoch2": {"n_out_of_fold": 62, "fold_sizes": [11, 11, 10, 10, 10, 10],
               "Delta_0": -0.764489, "Delta_1": -0.027308, "V3": "PASS",
               "era_earlier": {"n": 35, "Delta_1": 0.0076},
               "era_later": {"n": 27, "Delta_1": -0.0726},
               "V_RANGE_checks": 2232, "V_RANGE_failures": 0,
               "n_above_1": 0, "WTL_vs_persistence": [32, 5, 25],
               "tie_rule": "the contract's own practical-equivalence floor 0.01",
               "supports": {"n": 6, "size": 12, "any_identical": False,
                            "mean_jaccard": 0.285244, "distinct_coordinates": 35},
               "fold_assignment_reproduced": True,
               "all_recomputed": True},
    "epoch2_descriptive": {"support_size": 12, "fit": 0.177509, "max": 0.924190,
                           "n_above_1": 0, "identical_to_any_fold": False,
                           "jaccard_range": [0.143, 0.500]},
    "qdesc_by_reference": {
        "pooled_rmse_frozen": 0.05758467247445343,
        "pooled_rmse_recomputed": 0.05758467247445299,
        "mean_vector_rmse": 0.4125238315775986,
        "n_discharges": 62, "n_samples_each": 1000,
        "coefficient_fit_type": "per_discharge_calibrated_1_8*",
        "conditioning_verdict": "D3D-MIXED-COEFFICIENT-IDENTIFIABILITY",
        "robust_coefficients": 5, "uncertainty_dominated": 2,
        "positive_directions": 5, "robust_directions": 2,
        "rank6_median_rel_coef": 0.7993154563548318,
        "rank6_median_abs_rmse": 0.031029606819801332,
        "estimator": "REML_primary_with_ML_sensitivity",
        "implicit_verdict": "D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED",
        "min_abs_A": 2.6428213717455407e-07,
        "shiftval_range": [14.643161791053483, 24.2426158353731],
        "correction_manifest": "74/77 (3 missing PDF figures)"},
    "leakage": {"verdict": "NO_LEAKAGE_FOUND", "checks_passed": 9,
                "prmtan_neped_residual_scatter": 0.534998,
                "retired_q95_residual_scatter": 0.073,
                "n_predictors_R2_ge_0_75": 2, "n_predictors": 78,
                "efit_quantities_excluded_fail_closed": 15},
    "claim_language": {"markdown_files_scanned": 167,
                       "overstated_claims_in_result_bearing_stages": 0},
    "agent_language": {"files_scanned": 714, "hits_before": 0, "hits_after": 0},
}

CHANGES = {
    "category_A_presentation": ["21 stage index.html pages", "S7 index.html",
                                "README.md", "figures/ (5 figures)"],
    "category_B_documentation": ["21 stage MANIFEST.json", "CANONICAL_INDEX.json",
                                 "WORKFLOW.md", "SIR_ARCHITECTURE_MAP.md",
                                 "REVISION_LEDGER.md", "INFORMATION_FLOW_AUDIT.md/.json",
                                 "CLAIM_EVIDENCE_MATRIX.json",
                                 "MANUSCRIPT_ALIGNMENT.md/.json",
                                 "AUDIT_REPORT.md/.json"],
    "category_C_reproducibility": ["audit_s7.py", "REPRODUCIBILITY.md",
                                   "_audit/ (registry, builders, independent "
                                   "recomputations, Phase-A inventory)",
                                   "figures/FIGURE_PROVENANCE.json"],
    "category_D_noncanonical_correction": [],
    "category_E_scientific_correction": [],
    "frozen_artifacts_modified": 0,
    "files_moved_or_renamed": 0,
    "files_deleted": 0,
    "migration_ledger_required": False,
}

out = {
    "record_id": "S7_FORENSIC_AUDIT_REPORT_V1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "D:/SIR_paper/DIIID_example/S7 (q_rec branch), plus the q_desc branch "
             "audited read-only by reference",
    "verdict": "S7_AUDIT_PASS_WITH_QUALIFICATIONS",
    "verdict_note": "The S7 workflow is sound, internally consistent and "
                    "independently reproducible; no BLOCKER and no MAJOR finding "
                    "inside S7. Both MAJOR findings concern the manuscript.",
    "findings": FINDINGS,
    "findings_by_level": {},
    "independently_verified": VERIFIED,
    "epoch_transition_legitimate": {
        "verdict": True,
        "case": "TWO dispositions in sequence: S7.K2 is Case B (incomplete "
                "operational contract, same claim branch QREC-B1, new operational "
                "epoch); S7.E2.0 is Case C (material narrowing of the evidentiary "
                "commitment V_rec after protected evidence was spent), which "
                "constitutes the provenance-linked descendant claim branch QREC-B2 "
                "under the SAME scientific task q_rec",
        "grounds": [
            "the alternative (Case A) explanation was tested target-blindly and "
            "refuted in S7.R1",
            "the claim-defining core (q, I_rec, U_rec, Omega_rec) is unchanged; "
            "revision_class = MINIMAL_P_ONLY",
            "the new rule is generic, target-blind, and its threshold grid was "
            "hashed before any survivor count existed",
            "spent protected evidence was reconciled by a cross-fitted design AND "
            "an explicitly narrowed claim, never by reuse"],
        "recorded_tension": "RESOLVED by the architecture-semantics hardening pass. "
                            "The original audit preserved both defensible readings "
                            "because the manuscript architecture was not yet "
                            "finalized; with the task / claim-branch / operational-"
                            "epoch hierarchy finalized, the cross-fitted narrower "
                            "qualification is a Case-C descendant claim branch under "
                            "the same task q_rec. See ARCHITECTURE_SEMANTICS_AUDIT."},
    "branch_lineage": {
        "scientific_task": "q_rec",
        "claim_branches": ["QREC-B1", "QREC-B2"],
        "QREC-B1": "sealed-external claim branch; operational epochs 1 and 2; "
                   "carries the preserved qualification failure S7.10",
        "QREC-B2": "cross-fitted finite-object descendant claim branch, parent "
                   "QREC-B1, constituted at S7.E2.0; carries Q_rec*",
        "branch_change_stage": "S7.E2.0",
        "not_at": "S7.K2 - that was an operational-contract revision inside QREC-B1",
        "target_instance_correction": "vsurf -> density changed neither the task "
                                      "nor the claim branch",
        "status": "both branches closed; no further discovery epoch authorized"},
    "changes_made": CHANGES,
    "recommendation": [
        "Replace the q_rec result in Results 1.5, Fig. 4b and Supplementary S7.8.",
        "Update Results 1.1 to the claim-core / operational-epoch architecture and "
        "replace the blanket validation-data rule with the protected-evidence rule.",
        "Add the Epoch-1 to Epoch-2 iterative arc to the Supplement.",
        "Keep the q_desc result as written; it verified cleanly.",
        "Consider mirroring the q_desc canonical package into an auditable location."],
    "companion_records": {
        "automated_checks": "AUDIT_CHECKS.json (regenerate with python audit_s7.py)",
        "manuscript": "MANUSCRIPT_ALIGNMENT.json",
        "leakage": "INFORMATION_FLOW_AUDIT.json",
        "claims": "CLAIM_EVIDENCE_MATRIX.json",
        "stages": "CANONICAL_INDEX.json",
        "phase_a_inventory": "_audit/PHASE_A_INVENTORY.json"},
}
for f in FINDINGS:
    out["findings_by_level"][f["level"]] = out["findings_by_level"].get(f["level"], 0) + 1

(S7 / "AUDIT_REPORT.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("findings:", len(FINDINGS), out["findings_by_level"])
print("verdict:", out["verdict"])
