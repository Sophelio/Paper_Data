"""Emit MANUSCRIPT_ALIGNMENT.json from the audited statement classification."""
import json
from datetime import datetime, timezone
from pathlib import Path

S7 = Path(__file__).resolve().parent.parent

S = lambda i, sec, txt, cls, fix: {          # noqa: E731
    "id": i, "section": sec, "statement": txt, "classification": cls,
    "proposed_correction": fix}

STATEMENTS = [
    S("1.1-a", "Results 1.1",
      "K_q = (q, I_q, P_q, B_q, H_q, U_q, V_q, Omega_q) as one flat tuple",
      "SEMANTICALLY_INCONSISTENT",
      "Split into K_q^(e) = (K_q^claim, K_q^op,(e)) with K^claim = (q, I_q, U_q, "
      "V_q, Omega_q) and K^op,(e) = (P_q, B_q, H_q)."),
    S("1.1-b", "Results 1.1",
      "data reserved for final validation must not influence the revised ontology "
      "or search policy",
      "SEMANTICALLY_INCONSISTENT",
      "Replace with the protected-evidence rule: inspected evaluation evidence "
      "becomes development evidence for the revised epoch; a later qualification "
      "must use new protected evidence, a valid cross-fitted design, or an "
      "explicitly narrowed claim."),
    S("1.1-c", "Results 1.1",
      "Sigma_q = SearchPolicy(G_q, K_q); ontology != universe != frontier != policy",
      "SUPPORTED_CURRENT",
      "None. S7 instantiates the distinction: G_q (S7.5H) != A_q 10778 (S7.6R) != "
      "Ahat_q 162845 (S7.7R) != Sigma_q."),
    S("1.1-d", "Results 1.1",
      "a construction absent from the explored frontier is not thereby shown "
      "inadmissible, inferior or nonexistent",
      "SUPPORTED_CURRENT",
      "None. S7.9 records global_optimality_claim=false, "
      "unsearched_status=ADMISSIBLE_UNSEARCHED."),
    S("1.1-e", "Results 1.1",
      "no audit/reconciliation machinery (delta, rho, j_min)",
      "MISSING_FROM_MANUSCRIPT",
      "Add. S7.R1 is the concrete instance: earliest_invalidated_stage = "
      "NONE_OF_THE_INSTANTIATED_OBJECTS; K_REC_REVISION_REQUIRED = true; minimal "
      "component P_rec."),
    S("1.1-f", "Results 1.1",
      "no scientific-task / claim-branch / operational-epoch hierarchy",
      "MISSING_FROM_MANUSCRIPT",
      "Add. Without it the q_rec lineage cannot be stated: S7 has one task, two "
      "claim branches (QREC-B1, QREC-B2) and three operational epochs."),
    S("1.1-g", "Results 1.1",
      "no descendant-claim-branch disposition",
      "MISSING_FROM_MANUSCRIPT",
      "Add. It is what the Epoch-1 to Epoch-2 transition actually is: a material "
      "narrowing of V_q after protected evidence was spent, producing a "
      "provenance-linked descendant branch under an unchanged q."),
    S("1.1-h", "Results 1.1",
      "I_q and V_q are not clearly separated, and evidence roles are treated as "
      "global per datum",
      "SEMANTICALLY_INCONSISTENT",
      "Separate them: I_q = what information is epistemically admissible; V_q = "
      "what evidentiary role it may play. Roles are variable- and "
      "transition-specific; S7's predictor-side applicability versus target-side "
      "discovery is the worked example."),

    S("desc-1", "Results 1.5 / S7.1", "62 discharges, eight admitted quantities",
      "SUPPORTED_CURRENT", "None."),
    S("desc-2", "Results 1.5 / S7.3", "seven-coordinate descriptive support",
      "SUPPORTED_CURRENT", "None; verified against d3d_discharge_coefficients.csv."),
    S("desc-3", "Results 1.5 / S7.4", "pooled RMSE 5.76e-2 with discharge-specific "
      "coefficients", "SUPPORTED_CURRENT",
      "None; recomputed 0.05758467247445299 vs frozen 0.05758467247445343."),
    S("desc-4", "S7.3", "cohort-mean coefficients summarize, do not define",
      "SUPPORTED_CURRENT", "None; mean-vector RMSE 0.4125238316."),
    S("desc-5", "S7.6", "target-containing implicit closure, not a predictor",
      "SUPPORTED_CURRENT",
      "None; verdict D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED."),
    S("desc-6", "S7.7", "mixed coefficient identifiability: 5 resolved, 2 "
      "uncertainty-dominated, 2 of 5 robust directions", "SUPPORTED_CURRENT",
      "None; verdict D3D-MIXED-COEFFICIENT-IDENTIFIABILITY; rank-6 0.7993 / 0.03103; "
      "REML primary with ML sensitivity."),
    S("desc-7", "S7.5", "spline and RTS variants provisional until tied to a frozen "
      "manifest", "UNVERIFIED",
      "Still correct as written; the variants remain untied to a frozen run "
      "manifest. Keep the provisional wording or drop the variants."),
    S("desc-8", "S7.2", "the canonical analysis does not use a fixed 20 ms grid",
      "SUPPORTED_CURRENT", "None; 1000 aligned samples per discharge."),

    S("rec-1", "Results 1.5 / S7.8", "the designated target was I_p",
      "STALE_SUPERSEDED", "Canonical q_rec target is `density`."),
    S("rec-2", "Results 1.5 / S7.8", "explored frontier of 141 relational coordinates",
      "STALE_SUPERSEDED",
      "Admissible universe 10778 atoms; Epoch-1 frontier 162845 supports; Epoch-2 "
      "qualified basis 3451 atoms."),
    S("rec-3", "Results 1.5 / S7.8",
      "seven development discharges, frozen, then 55 external discharges",
      "STALE_SUPERSEDED",
      "Epoch 1: 20 development / 42 external. Epoch 2: six discharge-grouped folds "
      "over all 62."),
    S("rec-4", "Results 1.5 / Fig 4b / S7.8",
      "pooled RMSE 0.126 REL10 / 0.114 REL141 / 0.182 RAW10", "STALE_SUPERSEDED",
      "Retired for leakage and for being beaten by persistence (0.0685). Replace "
      "with the Epoch-2 table."),
    S("rec-5", "Results 1.5 / Fig 4b", "lower error on 46 of 55 external discharges",
      "STALE_SUPERSEDED",
      "Replace with 32 wins / 5 ties / 25 losses against persistence over 62 "
      "out-of-fold discharges."),
    S("rec-6", "Results 1.5 / S7.8", "effective degrees of freedom 99 -> 10.6",
      "UNVERIFIED", "Never reproduced from primary artifacts; belongs to the "
      "retired branch. Remove."),
    S("rec-7", "Fig 4b title",
      "Compact Representation With External Structural Transfer",
      "STALE_SUPERSEDED",
      "The frozen verdict for the corrected branch is "
      "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER (S7.10). The Epoch-2 claim is "
      "target-cross-fitted reconstruction over a predictor-qualified finite object."),
    S("rec-8", "Results 1.5",
      "utility survives structural transfer to discharges excluded from selection",
      "STALE_SUPERSEDED",
      "Replace with the Epoch-2 statement and attach both qualifications."),
    S("rec-9", "Fig 4b",
      "93% Nominal Reduction; Support Selected on 7 Development Discharges",
      "STALE_SUPERSEDED", "Remove."),
    S("rec-10", "S7.8", "I_p and its descendants excluded before structural search",
      "SEMANTICALLY_INCONSISTENT",
      "The principle is retained and is correct; in the archive it was NOT achieved "
      "for I_p, which is why the branch was retired. For `density` it is achieved: "
      "17 of 95 quantities excluded, including all 15 EFIT quantities fail-closed."),
    S("rec-11", "Results 1.5 / S7", "the Epoch-1 to Epoch-2 iterative arc",
      "MISSING_FROM_MANUSCRIPT",
      "Add; it is the strongest methodological content the DIII-D example yields."),

    S("m-1", "Methods", "DIII-D reconstruction paragraphs referring to I_p",
      "STALE_SUPERSEDED", "Retarget to `density` and the cross-fitted design."),
    S("m-2", "Methods / S1 / S3",
      "any statement that all post-evaluation operational change creates a new "
      "scientific branch", "SEMANTICALLY_INCONSISTENT",
      "Replace with the operational-epoch rule. The blanket form occurs in 1.1-b."),
    S("m-3", "S8", "provenance-preserving ontology refinement",
      "SUPPORTED_BUT_WORDING_NEEDS_UPDATE",
      "Frame refinement as advancing an operational epoch; cite S7.K2 as the "
      "worked example."),
]

RETIREMENT = {
    "retired_branch": "q_rec target I_p, 141 coordinates, 7 development / 55 external, "
                      "REL10 / REL141 / RAW10",
    "retirement_id": "D3D-FIG6-QREC-RETIREMENT-V1",
    "retired_utc": "2026-09-02T04:48:03Z",
    "records": [
        "DIIID_example/fig6data/RETIREMENT_RECORD.json",
        "DIIID_example/Figure6_qualification_audit/FIGURE6_QUALIFICATION_AUDIT_REPORT.md",
        "S7/_legacy_reference/LEGACY_QREC_STATUS.md",
    ],
    "grounds": [
        {"id": "PROVENANCE_LEAKAGE",
         "detail": "6/10 REL10 and 4/10 RAW10 features carry upstream I_p "
                   "dependence; q95 is essentially shape*a^2*Bt/I_p (median |corr| "
                   "0.945 with 1/I_p, 7.3% residual scatter, I_p recovered at "
                   "median R^2 0.79)."},
        {"id": "NO_SKILL_OVER_TRIVIAL_BASELINE",
         "detail": "persistence median normalised RMSE 0.0685 beats REL141 0.1137, "
                   "REL10 0.1257 and RAW10 0.1821; var(eval)/var(calib) median "
                   "0.0032."},
    ],
    "canonical_replacement": "S7 q_rec density branch, freeze "
                             "D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1",
}

REPLACEMENT_NUMBERS = {
    "target": "density", "n_discharges": 62, "n_predictors": 78,
    "admissible_atoms": 10778, "qualified_basis": 3451, "tau": 1.0,
    "n_folds": 6, "design": "target cross-fitted, discharge grouped",
    "Delta_0": -0.764489, "Delta_1": -0.027308,
    "REL": {"mean": 0.1891, "median": 0.1515, "p90": 0.2959, "max": 0.9199},
    "vs_raw_ridge_78": -0.0960, "vs_raw_histgb_78": -0.1573,
    "vs_hardened_ridge_70": -0.0951,
    "vs_persistence_WTL": [32, 5, 25],
    "era_earlier": {"n": 35, "Delta_1": 0.0076, "direction": "PRACTICAL_TIE"},
    "era_later": {"n": 27, "Delta_1": -0.0726, "direction": "MATERIAL_IMPROVEMENT"},
    "V3": "PASS", "V6": "PASS_WITH_QUALIFICATION",
    "V_RANGE": {"result": "PASS", "checks": 2232, "failures": 0},
    "tiers": ["FORMAL_PASS", "CLEAN_DEMO_NOT_MET"],
    "supports": {"n": 6, "size": 12, "any_identical": False, "mean_jaccard": 0.285},
}

out = {
    "record_id": "S7_MANUSCRIPT_ALIGNMENT_V1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "manuscript_artifact_audited": {
        "path": "draft/SIR_paper.pdf", "pages": 64,
        "modified": "2026-09-02T10:45",
        "sha256": "94ccf533b841fe39a0468735eb2dbc31a80cceba70b094bcaa480a4029ea7b70",
        "rechecked_at_semantics_pass": "UNCHANGED",
        "latex_source_found": False},
    "current_manuscript_architecture": {
        "source": "finalized Results 1.1 semantics",
        "expressed_by_S7_documentation": True,
        "expressed_by_shipped_pdf": False,
        "note": "The S7 documentation layer uses the current architecture. The "
                "shipped PDF has not been regenerated to match, so the findings "
                "below stand against the artifact, not the architecture."},
    "manuscript": {"path": "draft/SIR_paper.pdf", "pages": 64,
                   "modified": "2026-09-02T10:45",
                   "latex_source_found": False},
    "manuscript_edited_by_this_audit": False,
    "headline_finding": "The manuscript's q_rec result (Results 1.5, Fig. 4b, "
                        "Supplementary S7.8) is the branch this repository retired "
                        "on 2026-09-02 for target-provenance leakage and for having "
                        "no skill over a persistence baseline.",
    "architecture_finding": "The shipped Results 1.1 carries the flat 8-tuple "
                            "contract with no claim-core / operational-epoch "
                            "distinction and no defect/reconciliation machinery; a "
                            "text search finds zero occurrences of the current "
                            "vocabulary.",
    "retirement": RETIREMENT,
    "statements": STATEMENTS,
    "summary": {},
    "replacement_numbers": REPLACEMENT_NUMBERS,
    "briefing_discrepancy": {
        "expected": "about 41% of samples with |A| < 1e-4",
        "frozen_value": 0.002355,
        "artifact": "Implicit_elimination_and_denominator_conditioning/outputs/"
                    "eliminated_A_summary.json",
        "likely_origin": "0.4125238316 is the cohort-mean-vector pooled RMSE",
        "confirmed_instead": {"min_abs_A": 2.6428213717455407e-07,
                              "shiftval_range": [14.643161791053483, 24.2426158353731],
                              "elimination_identity_max_error": 7.896461262646426e-15},
        "manuscript_affected": False,
    },
}
for s in STATEMENTS:
    out["summary"][s["classification"]] = out["summary"].get(s["classification"], 0) + 1

(S7 / "MANUSCRIPT_ALIGNMENT.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("statements:", len(STATEMENTS))
for k, v in sorted(out["summary"].items()):
    print("  %-38s %d" % (k, v))
