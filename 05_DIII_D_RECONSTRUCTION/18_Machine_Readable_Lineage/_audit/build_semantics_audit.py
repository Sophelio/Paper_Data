"""Emit ARCHITECTURE_SEMANTICS_AUDIT.json.

Machine-readable record of the architecture-semantics hardening pass, including
the compact q_rec branch lineage. Documentation layer only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S7 = HERE.parent
sys.path.insert(0, str(HERE))
from stage_registry import TASKS, CLAIM_BRANCHES, STAGES  # noqa: E402


def F(i, where, statement, cls, disposition):
    return {"id": i, "location": where, "statement": statement,
            "classification": cls, "disposition": disposition}


FINDINGS = [
    F(1, "REVISION_LEDGER.md",
      "Case C defined as 'the scientific claim itself changed; this is a new "
      "branch'", "STALE_SEMANTICS",
      "Redefined: Case C is a MATERIAL CLAIM REVISION producing a descendant "
      "branch under the same q. A fourth disposition, new q, covers a changed "
      "scientific task."),
    F(2, "REVISION_LEDGER.md",
      "section 'One tension recorded rather than resolved away' left two "
      "competing readings of V_q active", "AMBIGUOUS",
      "RESOLVED. Replaced by the canonical two-disposition account (K2 Case B, "
      "E2.0 Case C descendant branch). A short historical note explains why the "
      "ambiguity existed."),
    F(3, "REVISION_LEDGER.md, SIR_ARCHITECTURE_MAP.md, _audit/stage_registry.py",
      "'V_rec gains / is extended by V-RANGE'", "AMBIGUOUS",
      "Reworded so it cannot imply the claim-defining V_rec changed at K2: P_rec "
      "was revised, and the operational qualification procedure was "
      "correspondingly extended with the V-RANGE check."),
    F(4, "SIR_ARCHITECTURE_MAP.md",
      "'It is not Case C. q (reconstruct density) ...'", "STALE_SEMANTICS",
      "Removed. q_rec is stated as a TASK with y* = density as the target "
      "INSTANCE; K2 is Case B and the descendant branch is constituted at "
      "S7.E2.0."),
    F(5, "WORKFLOW.md", "'Three orderings, not one' - no branch-lineage view",
      "AMBIGUOUS",
      "Fourth ordering added as section 2b, branch lineage, kept distinct from "
      "the scientific dependency graph."),
    F(6, "WORKFLOW.md, README.md", "'q_desc ... is a different branch'",
      "AMBIGUOUS",
      "q_desc is a different scientific TASK, hence a different lineage entirely "
      "- not a branch or operational epoch of q_rec."),
    F(7, "AUDIT_REPORT.md", "referred to the unresolved V_q tension",
      "HISTORICAL_BUT_VALID",
      "Preserved as a record of what the original audit correctly found, with a "
      "note on how the finalized architecture resolves it. Not rewritten to "
      "pretend it was resolved earlier."),
    F(8, "MANUSCRIPT_ALIGNMENT.md", "one undifferentiated 'the manuscript'",
      "AMBIGUOUS",
      "Split into manuscript artifact audited (unchanged PDF, sha256 94ccf533...) "
      "versus current manuscript architecture. Four new 1.1 entries added."),
    F(9, "21 stage MANIFEST.json, CANONICAL_INDEX.json",
      "no task / claim-branch / operational-epoch metadata", "AMBIGUOUS",
      "Added scientific_task_id, claim_branch, claim_branch_role, "
      "parent_claim_branch, revision_level; plus scientific_tasks, "
      "claim_branches and branch_lineage at index level."),
    F(10, "INFORMATION_FLOW_AUDIT.md/.json",
      "I_q and V_q not explicitly separated", "AMBIGUOUS",
      "Separation stated at the head of the document and in policy_separation; "
      "the protected-evidence trigger recorded explicitly."),
    F(11, "frozen stage prose (128 markdown files, all freeze JSON)",
      "epoch/branch vocabulary predating the finalized architecture",
      "FROZEN_DO_NOT_EDIT",
      "PRESERVED UNMODIFIED. Mapped to current semantics in the documentation "
      "layer, never rewritten in place."),
]

PRESERVED = [
    {"artifact": "S7_12_FREEZE.json",
     "fields": ["Q_REC_BRANCH_CLOSED = true",
                "NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED = true"],
     "current_reading": "the final canonical q_rec descendant branch is closed, "
                        "and the q_rec scientific lineage has no authorized "
                        "further discovery epoch on any branch",
     "modified": False},
    {"artifact": "S7_K2_FREEZE.json", "fields": ["revision_class = MINIMAL_P_ONLY"],
     "current_reading": "exactly right and unchanged: only P_rec was revised",
     "modified": False},
    {"artifact": "S7_10_FREEZE.json",
     "fields": ["NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER"],
     "current_reading": "the NEGATIVE QUALIFICATION OUTCOME of claim branch "
                        "QREC-B1: subjected to qualification, and failed",
     "modified": False},
    {"artifact": "128 frozen markdown files",
     "fields": ["pre-finalization epoch/branch vocabulary"],
     "current_reading": "mapped in SIR_ARCHITECTURE_MAP.md and this document",
     "modified": False},
    {"artifact": "AUDIT_REPORT.md original V_q finding",
     "fields": ["recorded ambiguity"],
     "current_reading": "correct at the time; the architecture was not yet "
                        "finalized. Retained, annotated, not retconned.",
     "modified": False},
]

LINEAGE = {
    "scientific_task": TASKS["q_rec"],
    "claim_branches": CLAIM_BRANCHES,
    "sequence": [
        {"stage": "S7.2", "branch": "QREC-B1", "epoch": 1, "event": "claim branch "
         "originates; sealed-external commitment"},
        {"stage": "S7.3V2", "branch": "QREC-B1", "epoch": 1,
         "event": "Case A - target INSTANCE corrected vsurf -> density; task and "
                  "branch unchanged"},
        {"stage": "S7.10", "branch": "QREC-B1", "epoch": 1,
         "event": "QUALIFICATION FAILED; protected evidence spent"},
        {"stage": "S7.R1", "branch": "QREC-B1", "epoch": 1,
         "event": "Case A refuted; defect localized to the operational contract"},
        {"stage": "S7.K2", "branch": "QREC-B1", "epoch": 2,
         "event": "Case B - P_rec revised; operational epoch advances; branch "
                  "UNCHANGED"},
        {"stage": "S7.E2.0", "branch": "QREC-B2", "epoch": 2,
         "event": "Case C - V_rec materially narrowed; CONSTITUTES the descendant "
                  "claim branch"},
        {"stage": "S7.E2.0A", "branch": "QREC-B2", "epoch": 2,
         "event": "Case B - tau_train retired; I_rec clarified, not redefined"},
        {"stage": "S7.E2.1", "branch": "QREC-B2", "epoch": 2,
         "event": "FORMAL_PASS"},
        {"stage": "S7.12", "branch": "QREC-B2", "epoch": 2,
         "event": "Q_rec* assembled; branch CLOSED"},
    ],
    "branch_change_stage": "S7.E2.0",
    "branch_change_not_at": "S7.K2",
    "new_q_required": False,
    "lineage_status": "CLOSED",
    "operational_epoch_convention": {
        "rule": "An operational-contract VERSION change is not automatically an "
                "operational-EPOCH advance. A Case-B revision advances the epoch "
                "only when the superseded contract had already governed an "
                "EXECUTED operational realization; a pre-execution correction, or "
                "completion of an as-yet-unexecuted contract, is a versioned "
                "correction within the pending epoch.",
        "epoch_advances": ["S7.K2"],
        "versioned_corrections_not_advancing_epoch": ["S7.2C", "S7.7R", "S7.E2.0A"],
        "epoch_counts": {"QREC-B1": 2, "QREC-B2": 1},
        "note": "S7's historical labels 'Epoch 1' and 'Epoch 2' are retained in "
                "the frozen artifacts and in the `epoch` field. Counted "
                "branch-locally, QREC-B2's single operational epoch is its FIRST.",
    },
    "Omega_q_status": {
        "Omega_rec_intended_claim_domain": "UNCHANGED - the frozen 62-discharge "
                                           "observational object throughout; a "
                                           "member of K_q^claim",
        "Omega_star_rec_supported_domain": "part of Q*_q, NOT a member of "
                                           "K_q^claim; it narrows downstream as a "
                                           "consequence of the narrowed V_rec",
        "claim_defining_revision_at_S7_E2_0": ["V_rec"],
        "forbidden_statement": "V_rec and Omega*_rec are both claim-defining "
                               "commitments",
    },
}

out = {
    "record_id": "S7_ARCHITECTURE_SEMANTICS_AUDIT_V1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "verdict": "S7_ARCHITECTURE_SEMANTICS_RECONCILED",
    "scope": "documentation and indexing layer only",
    "authoritative_architecture": {
        "hierarchy": "scientific task q -> provenance-linked claim branch -> "
                     "operational epoch(s)",
        "K_claim": ["q", "I_q", "U_q", "V_q", "Omega_q"],
        "K_op": ["P_q", "B_q", "H_q"],
        "reconciliation": "rho_q(K_q^(e), Z_q^(e), delta^(e)) -> (K_q^(e+1), j_min) "
                          "describes SAME-BRANCH reconciliation",
        "descendant_branch": "a material revision of a claim-defining commitment "
                             "produces a provenance-linked descendant claim branch "
                             "under the same task",
        "new_q": "only a material change to the scientific task itself",
        "I_q": "what information is epistemically admissible",
        "V_q": "what evidentiary role admissible information may play",
        "evidence_roles": "VARIABLE_AND_TRANSITION_SPECIFIC",
    },
    "manuscript_status": {
        "artifact": "draft/SIR_paper.pdf",
        "sha256": "94ccf533b841fe39a0468735eb2dbc31a80cceba70b094bcaa480a4029ea7b70",
        "rechecked_at_this_pass": "UNCHANGED",
        "contains_finalized_1_1_vocabulary": False,
        "S7_documentation_expresses_it": True,
    },
    "files_inspected": {
        "active_top_level_markdown": 9,
        "generated_stage_manifests": 21,
        "generated_stage_pages": 21,
        "machine_readable_audits": 4,
        "generators": 6,
        "frozen_markdown_inspected_not_edited": 128,
    },
    "findings": FINDINGS,
    "n_findings": len(FINDINGS),
    "findings_by_class": {},
    "preserved_because_frozen_or_historical": PRESERVED,
    "qrec_branch_lineage": LINEAGE,
    "QREC_B1_outcome_wording": {
        "canonical_phrase": "negative qualification outcome",
        "acceptable_variants": ["preserved qualification failure",
                                "failed qualification result"],
        "avoid": "its qualified outcome",
        "reason": "'qualified' must not be read as 'passed'; QREC-B1 was subjected "
                  "to qualification and FAILED",
    },
    "V_q_treatment": {
        "definition": "a claim-defining commitment: the evidentiary role "
                      "admissible information may play and the qualification the "
                      "claim must survive",
        "at_S7_K2": "UNCHANGED as a semantic commitment; the operational "
                    "qualification procedure was extended with V-RANGE",
        "at_S7_E2_0": "MATERIALLY NARROWED - cross-fitted qualification over the "
                      "finite object; this constitutes descendant branch QREC-B2. "
                      "V_rec is the ONLY claim-defining commitment revised; "
                      "Omega_rec is unchanged.",
        "direction": "STRICTLY_WEAKER",
        "forced_by": "the protected-evidence rule, not chosen for advantage",
        "external_validation_language": "absent from all active documentation",
    },
    "K2_classification": {
        "case": "B", "revision_class": "MINIMAL_P_ONLY",
        "claim_branch": "QREC-B1", "branch_changed": False,
        "operational_epoch_advanced": True,
        "P_RANGE_SUPPORT": "the K2 revision; an operational admissibility rule in "
                           "P_rec",
        "V_RANGE": "the operational qualification check that tests satisfaction of "
                   "the revised admissibility condition; NOT evidence that the "
                   "claim-defining V_rec changed",
        "created_descendant_branch": False,
    },
    "vsurf_to_density": {
        "case": "A", "task_changed": False, "claim_branch_changed": False,
        "what_changed": "the target INSTANCE",
        "why": "the contract already required source-supported temporal "
               "resolution; the first instantiation violated it, and applying the "
               "same rule correctly selected density",
        "j_min": "O_q",
    },
    "branch_closure": {
        "QREC-B1": "closed by qualification failure, then superseded; its negative "
                   "failure is preserved as that branch's negative "
                   "qualification outcome",
        "QREC-B2": "closed by S7.12 with the qualified positive result Q_rec*",
        "lineage": "no authorized further discovery epoch on any q_rec branch",
        "frozen_fields_modified": False,
    },
    "integrity": {
        "frozen_scientific_artifacts_modified": 0,
        "frozen_artifacts_reproducing": "527/527",
        "freeze_json_edited_for_terminology": 0,
        "searches_rerun": 0,
        "models_refit": 0,
        "supports_recomputed": 0,
        "thresholds_or_gates_changed": 0,
        "metrics_changed": 0,
        "numerical_results_changed": 0,
        "scientific_verdicts_changed": 0,
        "new_epochs_or_branches_created_by_analysis": 0,
        "files_moved_renamed_or_deleted": 0,
        "markdown_files_edited": 9,
        "markdown_edit_preference": "<= 15",
        "scientific_audit_verdict_unchanged": "S7_AUDIT_PASS_WITH_QUALIFICATIONS",
    },
    "remaining_ambiguities": [
        "The shipped manuscript artifact still does not contain this architecture; "
        "it is byte-identical to the one originally audited.",
        "Where exactly a claim branch begins is a judgement. This package places "
        "the boundary at S7.E2.0; a reader could argue for S7.E2.0A. Both precede "
        "any Epoch-2 search and neither changes the task, the numbers or the claim "
        "boundary.",
        "QREC-B1's second operational epoch produced no qualification of its own: "
        "the branch was superseded before that epoch could be qualified under the "
        "sealed-external commitment.",
        "Frozen prose predates this vocabulary by design; the mapping lives in the "
        "documentation layer, and the frozen text is not edited.",
    ],
    "companion_records": {
        "narrative": "ARCHITECTURE_SEMANTICS_AUDIT.md",
        "lineage_map": "SIR_ARCHITECTURE_MAP.md",
        "revision_classification": "REVISION_LEDGER.md",
        "scientific_audit": "AUDIT_REPORT.md / AUDIT_REPORT.json",
        "automated_checks": "AUDIT_CHECKS.json (python audit_s7.py)",
    },
}
for f in FINDINGS:
    out["findings_by_class"][f["classification"]] = \
        out["findings_by_class"].get(f["classification"], 0) + 1

(S7 / "ARCHITECTURE_SEMANTICS_AUDIT.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")
print("verdict:", out["verdict"])
print("findings:", len(FINDINGS), out["findings_by_class"])
print("lineage stages:", len(LINEAGE["sequence"]))
