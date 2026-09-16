"""Canonical S7 stage registry.

Single source of truth for the S7 normalization layer: which directories are
canonical stages, where each sits in the SIR discovery architecture, which
freeze governs it, and which stage consumes it.

Data only. Consumed by build_s7_package.py and audit_s7.py.
"""

# ---------------------------------------------------------------------------
# Scientific tasks, claim branches and operational epochs.
#
# Current SIR architecture (Results 1.1):
#
#   scientific task q
#       |__ provenance-linked claim branch   (fixes q, I_q, U_q, V_q, Omega_q)
#               |__ operational epoch(s)     (revises P_q, B_q, H_q)
#
# A material revision of a claim-defining commitment produces a provenance-linked
# DESCENDANT claim branch under the SAME task. Only a material change to the
# scientific task itself requires a new q.
# ---------------------------------------------------------------------------

TASK_REC = "q_rec"
TASK_DESC = "q_desc"
BRANCH_REC = TASK_REC          # retained: legacy alias used below
BRANCH_DESC = TASK_DESC

TASKS = {
    "q_rec": {
        "task_id": "q_rec",
        "statement": "contemporaneous reconstruction of an admissible diagnostic "
                     "quantity from the remaining task-admissible observational "
                     "system, under the declared target-selection, information, "
                     "utility and qualification policies",
        "note": "q_rec is the scientific TASK. It is deliberately more stable than "
                "any single target instance, protocol realization or validation "
                "implementation. The canonical target instance y* = density was "
                "selected under the frozen task rules after the source-resolution "
                "correction; the earlier vsurf instantiation was corrected under "
                "the SAME task and the SAME claim branch.",
        "target_instance": "density (line-averaged electron density)",
        "superseded_target_instance": "vsurf",
    },
    "q_desc": {
        "task_id": "q_desc",
        "statement": "retrospective descriptive organization of the realized plasma "
                     "trajectories, admitting contemporaneous target-containing "
                     "coordinates",
        "note": "A DIFFERENT scientific task, not an operational epoch of q_rec: "
                "the information policy, utility and validation structure all "
                "differ materially. Its canonical artifacts are outside S7.",
    },
}

CLAIM_BRANCHES = {
    "QREC-B1": {
        "branch_id": "QREC-B1",
        "task_id": "q_rec",
        "label": "sealed-external claim branch",
        "parent_claim_branch": None,
        "claim_commitment": "structural transfer of a development-selected "
                            "representation, qualified on a sealed external cohort "
                            "of 42 discharges",
        "operational_epochs": [1, 2],
        "branch_local_operational_epochs": 2,
        "epoch_advance_stages": ["S7.K2"],
        "contract_corrections_not_advancing_epoch": ["S7.2C", "S7.7R"],
        "status": "CLOSED_BY_QUALIFICATION_FAILURE_THEN_SUPERSEDED",
        "outcome": "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER (S7.10): a NEGATIVE "
                   "QUALIFICATION OUTCOME. The branch was subjected to "
                   "qualification and FAILED it; the failure is preserved "
                   "unmodified and the branch was then superseded.",
    },
    "QREC-B2": {
        "branch_id": "QREC-B2",
        "task_id": "q_rec",
        "label": "cross-fitted finite-object descendant claim branch",
        "parent_claim_branch": "QREC-B1",
        "claim_commitment": "target-cross-fitted reconstruction over the "
                            "predictor-qualified frozen 62-discharge observational "
                            "object",
        "why_descendant": "Epoch-1 evaluation evidence had been inspected and used "
                          "to diagnose the defect, so it could no longer serve as "
                          "untouched validation evidence. The evidentiary "
                          "commitment V_q was therefore MATERIALLY NARROWED, which "
                          "constitutes a descendant claim branch under the same "
                          "q_rec task. The narrowing was constituted at S7.E2.0, "
                          "NOT at S7.K2: K2 was an operational-contract revision "
                          "within QREC-B1.",
        "Omega_q_status": "Omega_rec, the INTENDED claim domain and a member of "
                          "K_q^claim, is UNCHANGED: the frozen 62-discharge "
                          "observational object throughout. Only V_rec was "
                          "materially revised. Omega*_rec, the domain actually "
                          "SUPPORTED by qualification, is part of Q*_q and not a "
                          "member of K_q^claim; it changes downstream as a "
                          "consequence of the narrowed V_rec, not as a separate "
                          "claim-defining revision.",
        "operational_epochs": [2],
        "branch_local_operational_epochs": 1,
        "epoch_label_note": "Retained as S7's historical label 'Epoch 2'. Counted "
                            "branch-locally this is QREC-B2's FIRST operational "
                            "epoch; the descendant branch begins its own "
                            "operational lineage.",
        "contract_corrections_not_advancing_epoch": ["S7.E2.0A"],
        "status": "CLOSED",
        "outcome": "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS, assembled as "
                   "Q_rec* in S7.12.",
    },
}

# revision_level vocabulary
#   NONE                  nothing was revised at this stage
#   INSTANTIATION         Case A - an object was instantiated incorrectly
#   OPERATIONAL_CONTRACT  Case B - P_q / B_q / H_q revised
#   CLAIM_DEFINING        material revision of I_q / U_q / V_q / Omega_q;
#                         constitutes a descendant claim branch under the same q
#   NEW_TASK              the scientific task itself changes; requires a new q
#
# An operational-contract VERSION change is not automatically an operational-
# EPOCH advance. A Case-B revision advances the epoch only when the superseded
# contract had already governed an EXECUTED operational realization. A
# pre-execution correction, or completion of an as-yet-unexecuted contract, is a
# versioned correction WITHIN the pending epoch. The `epoch` field therefore
# identifies materially executed operational regimes; `revision_level` marks
# every contract version. Only S7.K2 advances an epoch in this lineage.

# SIR architecture elements, current manuscript vocabulary
#   O            scientific object
#   K_claim      claim-defining core (q, I_q, U_q, V_q, Omega_q)
#   K_op         operational contract (P_q, B_q, H_q) at epoch e
#   O_q          task-admissible record
#   X_q          task-conditioned mathematical interpretation
#   G_q          relational ontology
#   A_q          admissible coordinate-relation universe
#   Sigma_q      search policy
#   Ahat_q       explored frontier
#   CR           selected representation (C*, R*)
#   Q_q          qualified output
#   delta        defect record
#   rho          reconciliation
#   j_min        earliest invalidated stage

STAGES = [
    {
        "stage_id": "S7.1",
        "scientific_task_id": 'shared',
        "claim_branch": None,
        "claim_branch_role": 'PRE_CONTRACT',
        "revision_level": 'NONE',
        "dir": "01_observational_object",
        "title": "Observational object and provenance",
        "branch": "shared",
        "epoch": None,
        "sir": ["O"],
        "freeze": "reconciliation_final/S7_1_FINAL_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1",
        "status": "CANONICAL",
        "question": "What finite scientific object was supplied to discovery?",
        "operation": "Census of 62 DIII-D discharges and 95 quantities; provenance, "
                     "units, temporal support and availability instantiated.",
        "verdict": "FROZEN_WITH_QUALIFICATIONS - 62 discharges, 95 signals, 32/32 "
                   "acceptance tests, 0 unresolved critical items.",
        "parents": [],
        "children": ["S7.2"],
        "key_numbers": {"n_discharges": 62, "n_signals": 95},
        "notes": "No target selected, no admissibility applied. A is ancillary "
                 "observational information, not admissibility.",
    },
    {
        "stage_id": "S7.2",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'ORIGIN',
        "revision_level": 'NONE',
        "dir": "02_reconstruction_contract",
        "title": "Reconstruction contract (target-blind skeleton)",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["K_claim", "K_op"],
        "freeze": "S7_2_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-V1",
        "status": "CANONICAL_SUPERSEDED_BY_S7.2C",
        "question": "What contract governs the reconstruction claim, before any "
                    "target is chosen?",
        "operation": "Froze q, the information-boundary rules, admissibility "
                     "classes, construction bounds, knowledge policy, utility, "
                     "validation geometry and intended domain.",
        "verdict": "FROZEN_READY_FOR_S7.3 - contract skeleton frozen with no "
                   "target selected.",
        "parents": ["S7.1"],
        "children": ["S7.2C", "S7.3"],
        "key_numbers": {"development": 20, "external": 42, "blocks": 3},
        "notes": "Cohort partition deterministic and target-blind. External "
                 "cohort sealed until S7.10.",
    },
    {
        "stage_id": "S7.2C",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'OPERATIONAL_CONTRACT',
        "dir": "02_reconstruction_contract/correction_v1",
        "title": "Contract correction V2",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["K_claim", "K_op", "delta", "rho"],
        "freeze": "S7_2_FREEZE_V2.json",
        "freeze_id": "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V2",
        "status": "CANONICAL",
        "question": "Do any contract clauses need correcting before instantiation?",
        "operation": "Nine superseded clauses corrected; V1 preserved unmodified.",
        "verdict": "V2 authoritative; V1 preserved byte-for-byte as audit history.",
        "parents": ["S7.2"],
        "children": ["S7.3"],
        "key_numbers": {"clauses_superseded": 9},
        "notes": "Includes C-01 (practical-equivalence floor) and C-07 (external "
                 "era counts 24/18).",
    },
    {
        "stage_id": "S7.3",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "03_target_feasibility_and_boundary",
        "title": "Target feasibility and information boundary",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["K_claim", "O_q"],
        "freeze": "S7_3_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.3-TARGET-FEASIBILITY-V1",
        "status": "CANONICAL_SUPERSEDED_BY_S7.3V2",
        "question": "Which target is feasible, and which observations may be used?",
        "operation": "Target census and ranking; information boundary instantiated "
                     "with fail-closed ancestry rules.",
        "verdict": "Target selected; boundary instantiated.",
        "parents": ["S7.2C"],
        "children": ["S7.3V2"],
        "key_numbers": {},
        "notes": "Superseded by the source-resolution V2 after a temporal-"
                 "resolution reconciliation.",
    },
    {
        "stage_id": "S7.3V2",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'INSTANTIATION',
        "dir": "03_target_feasibility_and_boundary/reconciliation_source_resolution",
        "title": "Target and boundary, source-resolved",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["K_claim", "O_q", "delta", "rho"],
        "freeze": "S7_3_FREEZE_V2.json",
        "freeze_id": "D3D-SIR-S7.3-TARGET-FEASIBILITY-SOURCE-RESOLUTION-V2",
        "status": "CANONICAL",
        "question": "Which target survives source-supported cadence, and which "
                    "78 predictors are admissible?",
        "operation": "Corrected target boundary; 95 quantities reduced to the "
                     "target plus 78 admissible explanatory predictors.",
        "verdict": "Target INSTANCE y* = density (line-averaged), selected by "
                   "applying the frozen task rules correctly. 78 predictors "
                   "admitted, 17 excluded (1 target itself, 1 cadence failure, "
                   "15 fail-closed unresolved EFIT ancestry).",
        "parents": ["S7.3"],
        "children": ["S7.4V2"],
        "key_numbers": {"n_predictors": 78, "n_excluded": 17, "target": "density"},
        "notes": "Case A. The contract already required source-supported temporal "
                 "resolution; the first instantiation (vsurf) violated it, and "
                 "applying the SAME rule correctly selected density. The "
                 "scientific task q_rec and the claim branch are unchanged - only "
                 "the target INSTANCE was corrected. The 15 EFIT quantities "
                 "excluded fail-closed are exactly the class that contaminated "
                 "the retired I_p branch.",
    },
    {
        "stage_id": "S7.4V2",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'INSTANTIATION',
        "dir": "04_mathematical_interpretation/retry_source_resolution_v2",
        "title": "Task-conditioned mathematical interpretation",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["X_q"],
        "freeze": "S7_4_FREEZE_V2.json",
        "freeze_id": "D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2",
        "status": "CANONICAL",
        "question": "As what mathematical object is the admissible record to be read?",
        "operation": "Discharge-wise trajectory ensemble on discharge-specific "
                     "source-supported grids; trajectory index frozen.",
        "verdict": "X_rec instantiated; cadence 5.853-14.187 ms, discharge-specific; "
                   "target never upsampled.",
        "parents": ["S7.3V2"],
        "children": ["S7.5"],
        "key_numbers": {},
        "notes": "Supersedes S7.4 V1, which was blocked on temporal resolution.",
    },
    {
        "stage_id": "S7.5",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "05_typed_relational_ontology",
        "title": "Typed relational ontology",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["G_q"],
        "freeze": "S7_5_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1",
        "status": "CANONICAL_SUPERSEDED_BY_S7.5H",
        "question": "What grammar of representations may be constructed?",
        "operation": "Typed constructors, signatures and admissibility predicates.",
        "verdict": "Ontology frozen.",
        "parents": ["S7.4V2"],
        "children": ["S7.5H"],
        "key_numbers": {},
        "notes": "G_rec is a grammar, not a feature library and not the universe.",
    },
    {
        "stage_id": "S7.5H",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'INSTANTIATION',
        "dir": "05H_primitive_space_and_ontology_hardening",
        "title": "Primitive space and ontology hardening",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["G_q"],
        "freeze": "S7_5H_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1",
        "status": "CANONICAL",
        "question": "Which primitives and constructors survive hardening?",
        "operation": "70-primitive hardened basis; 9 constructor families C0-C8; "
                     "23,861 symbolic coordinates.",
        "verdict": "G_REC_DENSITY_HARDENED_V2 v2.0.0 frozen, 48/48 acceptance.",
        "parents": ["S7.5"],
        "children": ["S7.6R"],
        "key_numbers": {"n_primitives": 70, "n_symbolic": 23861, "families": 9},
        "notes": "Derivative eligibility declared per primitive (63 of 70).",
    },
    {
        "stage_id": "S7.6R",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'INSTANTIATION',
        "dir": "06_admissible_universe/hardened_v2",
        "title": "Admissible coordinate universe",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["A_q"],
        "freeze": "S7_6R_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2",
        "status": "CANONICAL",
        "question": "Which constructions are concretely admissible on this object?",
        "operation": "Denominator admissibility, numerical support, duplicate and "
                     "exact-dependency handling applied to the symbolic space.",
        "verdict": "A_REC_DENSITY_HARDENED_V2: 10,778 atoms from 23,861 symbolic, "
                   "49/49 acceptance.",
        "parents": ["S7.5H"],
        "children": ["S7.7R"],
        "key_numbers": {"n_atoms": 10778, "C0": 66, "C1": 59, "C2": 2080,
                        "C3": 2457, "C5": 39, "C6": 3776, "C7": 2301},
        "notes": "PARTIAL_MAP_ADMISSIBILITY established here as an APPLICATION-TIME "
                 "predicate - the precedent E2.0A later invokes.",
    },
    {
        "stage_id": "S7.7R",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'OPERATIONAL_CONTRACT',
        "dir": "07_search_policy_and_frontier/one_seed_primary_v2",
        "title": "Search policy and explored frontier",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["Sigma_q", "Ahat_q"],
        "freeze": "S7_7R_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2",
        "status": "CANONICAL",
        "question": "Which part of the admissible universe was actually explored?",
        "operation": "SIGMA_REC_ONE_SEED_PRIMARY_V2 executed over the development "
                     "cohort; frontier recorded.",
        "verdict": "AHAT_REC_DENSITY_ONE_SEED_V2: 162,845 supports of size 1-12, "
                   "43/43 acceptance.",
        "parents": ["S7.6R"],
        "children": ["S7.8"],
        "key_numbers": {"frontier": 162845, "strata": 127},
        "notes": "A versioned Case-B correction WITHIN operational epoch 1: the "
                 "superseded budget had not yet governed a completed "
                 "qualification, so no epoch advance. S7.7 V1 "
                 "(BLOCKED_SEARCH_BUDGET) preserved as audit history.",
    },
    {
        "stage_id": "S7.8",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "08_utility_and_qualification_rules",
        "title": "Utility and qualification rule operationalization",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["K_claim"],
        "freeze": "S7_8_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1",
        "status": "CANONICAL",
        "question": "How exactly are candidates compared and qualified?",
        "operation": "U_rec made executable: five lexicographic ranks with a frozen "
                     "practical-equivalence rule. V_rec gates operationalized.",
        "verdict": "FROZEN_READY_FOR_S7.9, 48/48 acceptance.",
        "parents": ["S7.7R"],
        "children": ["S7.9"],
        "key_numbers": {"ranks": 5, "equivalence_floor": 0.01},
        "notes": "delta_equiv = max(SE_delta, 0.01). Floor immutable. No gate "
                 "evaluated at this stage.",
    },
    {
        "stage_id": "S7.9",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "09_development_selection_and_freeze",
        "title": "Development selection and pre-external freeze",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["CR"],
        "freeze": "S7_9_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1",
        "status": "CANONICAL",
        "question": "Which representation does the frozen utility select on "
                    "development evidence alone?",
        "operation": "U_rec applied to the 162,845-support frontier; 12-coordinate "
                     "support selected; model frozen before any external access.",
        "verdict": "FROZEN_WITH_QUALIFICATIONS. C_dev_star selected at Rank 2; "
                   "selection stability LOW and reported as found.",
        "parents": ["S7.8"],
        "children": ["S7.10"],
        "key_numbers": {"support_size": 12, "E1": 1055, "binding_rank": 2,
                        "bootstrap_selection_frequency": 0.093,
                        "distinct_bootstrap_winners": 217},
        "notes": "Firewall intact: 0 external predictor reads, 0 external target "
                 "reads at freeze time.",
    },
    {
        "stage_id": "S7.10",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "10_external_validation",
        "title": "External qualification - EPOCH 1 FAILURE",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["Q_q", "delta"],
        "freeze": "S7_10_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1",
        "status": "CANONICAL_NEGATIVE_RESULT",
        "question": "Does the frozen representation qualify on the sealed external "
                    "cohort?",
        "operation": "42 sealed external discharges opened for the first time; the "
                     "frozen model and six baselines evaluated; gates applied.",
        "verdict": "PRIMARY_EXTERNAL_GATE_FAILURE. "
                   "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER. V3 FAIL, V6 FAIL, "
                   "Omega_rec EMPTY.",
        "parents": ["S7.9"],
        "children": ["S7.11"],
        "key_numbers": {"REL_mean": 0.7423647781201324, "B1_mean": 0.21027421611172853,
                        "Delta_0": -0.18009502685176143, "Delta_1": 0.5320905620084037,
                        "shot_187019": 11.952633, "shot_187022": 11.766572,
                        "n_above_1": 2},
        "notes": "This negative result is scientific evidence and is preserved "
                 "prominently. Nothing was repaired after the outcome was seen.",
    },
    {
        "stage_id": "S7.11",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "11_sensitivity_and_interpretation",
        "title": "Sensitivity and failure interpretation",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["delta"],
        "freeze": "S7_11_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1",
        "status": "CANONICAL",
        "question": "Was the failure specific to the selected support, or general?",
        "operation": "Predeclared sensitivities executed: 217-member "
                     "development-equivalent family, prmtan ablations, block and "
                     "discharge omissions.",
        "verdict": "Development equivalence does not identify external robustness; "
                   "the canonical representative is externally fragile; the primary "
                   "failure is unchanged. V9 FAIL.",
        "parents": ["S7.10"],
        "children": ["S7.R1"],
        "key_numbers": {"family": 217, "full_domain": 213, "V3_style_pass": 70,
                        "C_dev_star_rank": 184, "best_Delta_1": -0.028742,
                        "gasa2_in_passers": 0, "gasa2_in_failures": 67},
        "notes": "Sensitivity plan hashed 100.6 s before the first external access "
                 "in S7.10. PRMTAN_NEPED_ONLY scores 0.4632 - direct evidence "
                 "against target circularity.",
    },
    {
        "stage_id": "S7.R1",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "R1_operational_state_reconciliation",
        "title": "Operational-state reconciliation - HYPOTHESIS REFUTED",
        "branch": BRANCH_REC,
        "epoch": 1,
        "sir": ["delta", "rho", "j_min"],
        "freeze": "S7_R1_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1",
        "status": "CANONICAL",
        "question": "Did the development cohort pool distinct operational states?",
        "operation": "The hypothesis was TESTED with target-blind predictor evidence "
                     "and rejected.",
        "verdict": "NO_CLEAN_OPERATIONAL_STATE_PARTITION. Hypothesis REFUTED. "
                   "STOP_OPERATIONAL_STATE_ROUTE. earliest_invalidated_stage = "
                   "NONE_OF_THE_INSTANTIATED_OBJECTS.",
        "parents": ["S7.11"],
        "children": ["S7.K2"],
        "key_numbers": {"K_REC_REVISION_REQUIRED": True,
                        "minimal_component": "P_rec"},
        "notes": "The pivot of the whole branch: every instantiated object satisfied "
                 "the contract AS WRITTEN, so the defect lies in the operational "
                 "admissibility contract, not in any constructed object.",
    },
    {
        "stage_id": "S7.K2",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B1',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'OPERATIONAL_CONTRACT',
        "dir": "K2_observational_range_support_contract",
        "title": "Observational range-support contract revision",
        "branch": BRANCH_REC,
        "epoch": "1 -> 2",
        "sir": ["K_op", "rho"],
        "freeze": "S7_K2_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1",
        "status": "CANONICAL",
        "question": "What minimal operational-contract revision addresses the "
                    "localized defect?",
        "operation": "A generic, dimensionless, constructor-generic observational "
                     "range-support predicate added to P_rec, with threshold and "
                     "companion gate frozen before any new search.",
        "verdict": "FROZEN_READY_FOR_DISCOVERY_EPOCH_2. Revision class "
                   "MINIMAL_P_ONLY. K_REC_V2 issued.",
        "parents": ["S7.R1"],
        "children": ["S7.E2.0"],
        "key_numbers": {"tau": 1.0, "full_domain_atoms": 3451, "of": 10778,
                        "degenerate_cells": 263, "of_cells": 2004708},
        "notes": "Case B. q, I_rec, U_rec, V_rec and Omega_rec are unchanged as "
                 "SEMANTIC COMMITMENTS; only the operational admissibility rule "
                 "P_rec is revised, and the operational qualification procedure "
                 "is correspondingly extended with the V-RANGE check that tests "
                 "satisfaction of the new admissibility condition. V-RANGE is an "
                 "operational check of revised P_rec, NOT evidence that the "
                 "claim-defining V_rec changed. K2 did not create the descendant "
                 "claim branch; it advanced the operational epoch within QREC-B1.",
    },
    {
        "stage_id": "S7.E2.0",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B2',
        "claim_branch_role": 'DESCENDANT_ORIGIN',
        "revision_level": 'CLAIM_DEFINING',
        "dir": "E2_0_protocol_and_resampling_freeze",
        "title": "Epoch-2 protocol and resampling freeze",
        "branch": BRANCH_REC,
        "epoch": 2,
        "sir": ["K_claim", "K_op"],
        "freeze": "E2_0_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.E2.0-DISCOVERY-EPOCH2-PROTOCOL-V1",
        "status": "CANONICAL_SUPERSEDED_BY_E2.0A",
        "question": "Under what evidential design may discovery legitimately resume?",
        "operation": "Six deterministic discharge-grouped outer folds; budget, "
                     "qualification policy and stop rule frozen.",
        "verdict": "FROZEN_WITH_QUALIFICATIONS. Applicability risk disclosed "
                   "prospectively. EPOCH2_IS_FINAL_QREC_ATTEMPT = true. This "
                   "stage CONSTITUTES the descendant claim branch QREC-B2.",
        "parents": ["S7.K2"],
        "children": ["S7.E2.0A"],
        "key_numbers": {"n_folds": 6, "budget_per_fold": 300000,
                        "budget_total": 1800000},
        "notes": "Because Epoch-1 evaluation evidence had become development evidence "
                 "for the revised procedure, the sealed-external claim of QREC-B1 "
                 "could no longer be supported. Declaring target cross-fitting "
                 "over the finite object MATERIALLY NARROWS V_rec, which "
                 "constitutes descendant claim branch QREC-B2 under the same task "
                 "q_rec. Omega_rec, the intended claim domain, is unchanged - the "
                 "same frozen 62-discharge object; the qualified scope Omega*_rec "
                 "supported downstream narrows as a consequence, but Omega*_rec is "
                 "part of Q*_q, not a member of K_q^claim. Introduced a "
                 "training-side headroom threshold (tau_train = 0.5) that E2.0A "
                 "later retired. Preserved as historical parent.",
    },
    {
        "stage_id": "S7.E2.0A",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B2',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'OPERATIONAL_CONTRACT',
        "dir": "E2_0A_predictor_admissibility_reconciliation",
        "title": "Predictor-side admissibility reconciliation",
        "branch": BRANCH_REC,
        "epoch": 2,
        "sir": ["K_op", "delta", "rho"],
        "freeze": "E2_0A_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.E2.0A-PREDICTOR-SIDE-ADMISSIBILITY-RECONCILIATION-V1",
        "status": "CANONICAL_AUTHORITATIVE_FOR_EPOCH2",
        "question": "Is predictor-side blinding consistent with the finite-object "
                    "claim actually being made?",
        "operation": "Confirmed the mismatch on contract-internal grounds; retired "
                     "tau_train with no replacement; single threshold tau = 1 retained.",
        "verdict": "FROZEN_READY_FOR_EPOCH2_SEARCH. Principle: "
                   "PREDICTOR_QUALIFIED, TARGET_CROSS_FITTED, RECONSTRUCTION.",
        "parents": ["S7.E2.0", "S7.K2"],
        "children": ["S7.E2.1"],
        "key_numbers": {"tau": 1.0, "tau_train": "RETIRED",
                        "C_E2_FULL_DOMAIN": 3451},
        "notes": "A versioned Case-B correction WITHIN the pending epoch, made "
                 "before any Epoch-2 search executed; it does not advance the "
                 "operational epoch. The information boundary is "
                 "transition-specific: observations admissible for applicability "
                 "need not be admissible for relation selection. A clarification "
                 "of I_rec, not a redefinition.",
    },
    {
        "stage_id": "S7.E2.1",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B2',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "E2_1_crossfitted_discovery_and_qualification",
        "title": "Cross-fitted discovery and qualification - EPOCH 2 PASS",
        "branch": BRANCH_REC,
        "epoch": 2,
        "sir": ["Sigma_q", "Ahat_q", "CR", "Q_q"],
        "freeze": "E2_1_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
        "status": "CANONICAL_PRIMARY_RESULT",
        "question": "Under the revised operational contract, does relational "
                    "discovery qualify?",
        "operation": "Six fresh searches over the 3,451-coordinate qualified basis, "
                     "one frozen policy, one non-interactive run; each support hashed "
                     "before any held-out target was opened.",
        "verdict": "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS. FORMAL_PASS and, "
                   "separately, CLEAN_DEMO_NOT_MET.",
        "parents": ["S7.E2.0A"],
        "children": ["S7.E2.2", "S7.12"],
        "key_numbers": {"Delta_0": -0.764489, "Delta_1": -0.027308,
                        "REL_mean": 0.1891, "REL_max": 0.9199,
                        "V3": "PASS", "V6": "PASS_WITH_QUALIFICATION",
                        "V_RANGE_checks": 2232, "V_RANGE_failures": 0,
                        "proposals": 765758, "n_supports": 6,
                        "mean_jaccard": 0.285},
        "notes": "Six folds produced six different size-12 supports, none identical. "
                 "Stable utility, non-unique relational supports.",
    },
    {
        "stage_id": "S7.E2.2",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B2',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "E2_2_full_object_descriptive_representation",
        "title": "Full-object descriptive representation",
        "branch": BRANCH_REC,
        "epoch": 2,
        "sir": ["CR"],
        "freeze": "E2_2_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1",
        "status": "CANONICAL_DESCRIPTIVE_ONLY",
        "question": "What single representation best exhibits the object, for "
                    "exposition?",
        "operation": "One fresh all-62-discharge search under the same frozen policy "
                     "and utility, run AFTER the qualification verdict was frozen.",
        "verdict": "FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN. C_E2_ALL_DESC, "
                   "size 12.",
        "parents": ["S7.E2.1"],
        "children": ["S7.12"],
        "key_numbers": {"support_size": 12, "proposals": 127642,
                        "descriptive_fit": 0.177509,
                        "mean_jaccard_with_folds": 0.313},
        "notes": "NOT validation evidence. Descriptive, representative, in-sample. "
                 "Its 0.1775 must never be compared with the cross-fitted 0.1891 as "
                 "a competing accuracy score.",
    },
    {
        "stage_id": "S7.12",
        "scientific_task_id": 'q_rec',
        "claim_branch": 'QREC-B2',
        "claim_branch_role": 'MEMBER',
        "revision_level": 'NONE',
        "dir": "S7_12_qualified_result",
        "title": "Final qualified reconstruction result",
        "branch": BRANCH_REC,
        "epoch": 2,
        "sir": ["Q_q"],
        "freeze": "S7_12_FREEZE.json",
        "freeze_id": "D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1",
        "status": "CANONICAL_FINAL",
        "question": "What does the completed branch establish, and what does it not?",
        "operation": "Assembly and qualification only. No search, no fit, no gate "
                     "evaluation, no new metric.",
        "verdict": "Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT. Q_REC_BRANCH_CLOSED.",
        "parents": ["S7.E2.1", "S7.E2.2"],
        "children": [],
        "key_numbers": {"acceptance": "36/36", "branch_closed": True},
        "notes": "Q_rec* carries a qualified representation FAMILY, not one "
                 "uniquely identified (C*, R*).",
    },
]

# Directories that are preserved history rather than canonical stages.
HISTORICAL = [
    ("02_reconstruction_contract/S7_2_FREEZE.json", "S7.2 V1",
     "PRESERVED_AS_AUDIT_HISTORY", "superseded by S7.2C correction_v1"),
    ("03_target_feasibility_and_boundary/S7_3_FREEZE.json", "S7.3 V1",
     "PRESERVED_AS_AUDIT_HISTORY", "target vsurf; superseded by source-resolution V2"),
    ("04_mathematical_interpretation/S7_4_FREEZE.json", "S7.4 V1",
     "PRESERVED_AS_AUDIT_HISTORY", "blocked on target temporal resolution"),
    ("06_admissible_universe/S7_6_FREEZE.json", "S7.6 V1",
     "HISTORICAL_SUPERSEDED", "6,034 atoms, C0-C4 on the 78-primitive ontology"),
    ("07_search_policy_and_frontier/S7_7_FREEZE.json", "S7.7 V1",
     "PRESERVED_AS_AUDIT_HISTORY", "BLOCKED_SEARCH_BUDGET"),
    ("_legacy_reference/LEGACY_QREC_STATUS.md", "legacy q_rec (I_p) branch",
     "RETIRED_NOT_USED", "retired for target-provenance leakage and no skill over "
     "a persistence baseline; see DIIID_example/fig6data/RETIREMENT_RECORD.json"),
]

# q_desc canonical artifacts are NOT inside S7.
EXTERNAL_BRANCH = {
    "task_id": TASK_DESC,
    "branch": BRANCH_DESC,
    "location": r"D:\sir-web\Paper Examples\Relational Coordinates for "
                r"Multimodal Plasma Observations",
    "run_id": "D3D-SIR-62-ALIGNED-V1",
    "packages": [
        "canonical_d3d_62_shot_run_v1",
        "Coefficient_conditioning",
        "Coefficient_conditioning/Correction_audit",
        "Implicit_elimination_and_denominator_conditioning",
        "Conditioning_repair",
    ],
    "note": "S7 as a directory contains the q_rec branch only. The descriptive "
            "branch is audited here by reference; its artifacts were verified "
            "read-only and are not copied or modified.",
}
