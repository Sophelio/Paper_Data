#!/usr/bin/env python
"""Assemble D:\\SIR_paper\\Paper_Data - the reviewer-auditable data and
reproducibility package for the SIR manuscript.

NON-DESTRUCTIVE. Every scientific artifact is COPIED with shutil.copy2 (metadata
preserved). No source file is moved, renamed, modified or deleted. Paper_Data is
excluded from every scan so re-running cannot nest the package inside itself.

    python build_paper_data.py              # build
    python build_paper_data.py --dry-run    # plan only, copy nothing

Outputs the package plus PACKAGE_MANIFEST.{csv,json}, the START_HERE indexes and
the audit reports. Verification is a separate script:
    python Paper_Data/09_REPRODUCIBILITY/validation_scripts/verify_paper_data.py
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\SIR_paper")
PKG = ROOT / "Paper_Data"
WEB = Path(r"D:\sir-web\Paper Examples\Relational Coordinates for "
           r"Multimodal Plasma Observations")
S7 = ROOT / "DIIID_example" / "S7"
DEX = ROOT / "DIIID_example"

NOW = datetime.now(timezone.utc).isoformat()

# --------------------------------------------------------------------------
# Exclusions. Build noise and anything that would recurse into the package.
# --------------------------------------------------------------------------
EXCLUDE_DIR_PARTS = {
    "Paper_Data", "__pycache__", ".git", ".venv_lorenz_benchmark", ".venv",
    ".pytest_cache", ".dalia", ".cursor", ".claude", "node_modules",
    ".ipynb_checkpoints", ".mypy_cache", ".ruff_cache",
}
EXCLUDE_GLOBS = [
    "*.pyc", "*.pyo", "*.aux", "*.log", "*.synctex.gz", "*.out", "*.toc",
    "*.fls", "*.fdb_latexmk", "*.bcf", "*.run.xml", "*.blg", "*.nav", "*.snm",
    "*.swp", "*~", ".DS_Store", "Thumbs.db", "*.tmp",
]

# Restricted source data: identified and hashed, never bundled.
RESTRICTED_GLOBS = ["*_resampled.npz"]


def excluded(p: Path) -> bool:
    if any(part in EXCLUDE_DIR_PARTS for part in p.parts):
        return True
    return any(fnmatch.fnmatch(p.name, g) for g in EXCLUDE_GLOBS)


def restricted(p: Path) -> bool:
    return any(fnmatch.fnmatch(p.name, g) for g in RESTRICTED_GLOBS)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Copy specification.
#   T(src, dest, category, sections, run_id, status, redist, notes, only=None)
#     copies a whole subtree; `only` optionally filters by suffix/name glob.
#   F(src, dest, ...) copies a single file.
# --------------------------------------------------------------------------
TREES: list[dict] = []
FILES: list[dict] = []


def T(src, dest, category, sections, run_id, status, redist, notes, only=None):
    TREES.append(dict(src=Path(src), dest=dest, category=category,
                      sections=sections, run_id=run_id, status=status,
                      redist=redist, notes=notes, only=only))


def F(src, dest, category, sections, run_id, status, redist, notes):
    FILES.append(dict(src=Path(src), dest=dest, category=category,
                      sections=sections, run_id=run_id, status=status,
                      redist=redist, notes=notes))


# ---- 01 manuscript snapshot ----------------------------------------------
F(ROOT / "draft" / "SIR_paper.pdf",
  "01_MANUSCRIPT_SNAPSHOT/main_manuscript/SIR_paper_2026-09-02.pdf",
  "manuscript", "all", None, "STALE_ONLY_MANUSCRIPT_ARTIFACT_IN_REPO", "yes",
  "The ONLY manuscript artifact in the repository. Contains main text and "
  "Supplementary Notes S1-S8 in one PDF. Demonstrably stale on the q_rec "
  "branch: 16 occurrences of REL10, zero of 'cross-fitted' or '3451'. No TeX "
  "source, and no \\releasepending placeholder, exists anywhere under D:\\SIR_paper.")
F(ROOT / "Lorenz" / "SIR_paper_orig.pdf",
  "10_REFERENCED_HISTORICAL_LINEAGE/superseded_manuscript/SIR_paper_orig.pdf",
  "manuscript", "all", None, "SUPERSEDED", "yes",
  "Older manuscript PDF retained for lineage. Superseded by "
  "01_MANUSCRIPT_SNAPSHOT/main_manuscript/SIR_paper_2026-09-02.pdf.")

# ---- 02 controlled studies ------------------------------------------------
T(ROOT / "Lorenz" / "benchmark",
  "02_CONTROLLED_STUDIES/01_Lorenz_Generator_Containment",
  "controlled_study", "Results 1.3, 1.4; Supplement S6", "SIR-LORENZ-BENCHMARK",
  "CANONICAL", "yes",
  "Lorenz fixed-representation containment benchmark: config, run manifest, "
  "results, SIR/pySINDy/MLP arms, audits, tables, tests, report.")
T(ROOT / "Lorenz" / "task_conditioning_benchmark",
  "02_CONTROLLED_STUDIES/02_Lorenz_Representation_Discovery",
  "controlled_study", "Results 1.3, 1.4; Supplement S6",
  "SIR-LORENZ-TASK-CONDITIONING", "CANONICAL", "yes",
  "Partially observed Lorenz representation discovery and task conditioning: "
  "contracts, preconfirmation freeze, benchmark results, audits, report.")
T(ROOT / "Lorenz" / "fig5data",
  "02_CONTROLLED_STUDIES/02_Lorenz_Representation_Discovery/figure5_frozen_data",
  "controlled_study", "Figure 5", "SIR-LORENZ-TASK-CONDITIONING", "CANONICAL",
  "yes", "Frozen numerical inputs for main-text Figure 5.")
T(ROOT / "Lorenz" / "data", "02_CONTROLLED_STUDIES/02_Lorenz_Representation_Discovery/trajectories",
  "controlled_study", "Results 1.3", "SIR-LORENZ-TASK-CONDITIONING", "CANONICAL",
  "yes", "Generated Lorenz trajectory realizations.")
for nm in ("Lorenz_attractor.py", "lorenz_data_provider.py", "data_provider.py",
           "custom_graphs.py", "build_fig5data.py",
           "figure5_lorenz_nested_representation_discovery.py", "README.md"):
    F(ROOT / "Lorenz" / nm,
      f"02_CONTROLLED_STUDIES/02_Lorenz_Representation_Discovery/scripts/{nm}",
      "controlled_study", "Results 1.3, 1.4", "SIR-LORENZ-TASK-CONDITIONING",
      "CANONICAL", "yes", "Lorenz generator / provider / figure-data builder.")

T(ROOT / "Stochastic oscillator",
  "02_CONTROLLED_STUDIES/03_Heterogeneous_Parameter_Oscillator",
  "controlled_study", "Results 1.3; Supplement S6", "SIR-SHO-ENSEMBLE",
  "CANONICAL", "yes",
  "Shared structure with heterogeneous parameter alpha: 40 realizations, "
  "provider, coefficient-recovery outputs.")
T(ROOT / "Pendulum", "02_CONTROLLED_STUDIES/04_Pendulum_Task_Conditioning",
  "controlled_study", "Results 1.3, 1.4; Figure 4; Supplement S6",
  "SIR-PENDULUM", "CANONICAL", "yes",
  "Pendulum compression versus autonomous evolution, task-conditioning panels, "
  "held-out predictive phase, QC and tests.")
T(ROOT / "Heat Equation Degeneracy",
  "02_CONTROLLED_STUDIES/05_Heat_Equation_Degeneracy_and_Multimode",
  "controlled_study", "Results 1.3; Supplement S6", "SIR-HEAT-DEGENERACY",
  "CANONICAL", "yes",
  "Heat-equation single-mode ambiguity and multimode shared-coefficient "
  "resolution.")
for nm in ("phase_turning_manifold_reference_shifted.py",
           "phase_turning_manifold_sensitivity_centered_with_x2_purple_v7.py",
           "phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py"):
    p = DEX / nm
    F(p, f"02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry/{nm}",
      "controlled_study", "Results 1.2; Figure 2", None,
      "CANONICAL" if nm.endswith("v8.py") else "SUPERSEDED", "yes",
      "Trajectory-relational geometry / turning-manifold construction. v8 is the "
      "version whose output the current manuscript references.")
F(ROOT / "AUDIT_sensitivity_centered_phase.md",
  "02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry/AUDIT_sensitivity_centered_phase.md",
  "audit", "Results 1.2", None, "CANONICAL", "yes",
  "Audit of the sensitivity-centred phase construction used by Figure 2.")
F(ROOT / "AUDIT_dalia_transform_family.md",
  "08_CONTRACTS_PROVENANCE_AND_QUALIFICATION/artifact_lineage/AUDIT_dalia_transform_family.md",
  "audit", "Methods", None, "CANONICAL", "yes",
  "Audit of the transform family used to realize relational coordinates.")

# ---- 03 DIII-D source object ---------------------------------------------
T(S7 / "01_observational_object", "03_DIII_D_SOURCE_OBJECT/observational_object_S7_1",
  "source_object", "Supplement S7.1", "D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1",
  "CANONICAL", "yes",
  "The frozen 62-discharge / 95-quantity observational object: cohort and signal "
  "inventories, provenance graph, units registry, temporal support, availability, "
  "equilibrium lineage, quality summary and the S7.1 reconciliation history.")
F(S7 / "SIGNAL_UNITS.json", "03_DIII_D_SOURCE_OBJECT/units_and_availability/SIGNAL_UNITS.json",
  "source_object", "Supplement S7.1", "D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1",
  "CANONICAL", "yes",
  "Frozen units registry. Units are read from here, never inferred from signal "
  "names. Hashed into the S7.1 freeze as units_registry_sha256.")
T(WEB / "canonical_d3d_62_shot_provenance",
  "03_DIII_D_SOURCE_OBJECT/provenance/canonical_d3d_62_shot_provenance",
  "source_object", "Supplement S7.1, S7.2", "D3D-SIR-62-ALIGNED-V1", "CANONICAL",
  "yes", "Discharge ledger, preprocessing provenance and reconstruction "
  "validation audit for the canonical 62-shot object.")
for nm in ("diiid_sir_data_provider.py", "transforms.py", "verify_transforms_62shot.py",
           "_dalia_runtime_transforms.py", "_dalia_prefix_transforms.py",
           "ELM_AUTOLABELER_PARAMETERS.md", "README.md"):
    F(DEX / nm, f"03_DIII_D_SOURCE_OBJECT/retrieval_metadata/{nm}",
      "source_object", "Methods; Supplement S7.2", None, "CANONICAL", "yes",
      "Data provider and transform realization used to read the archive and "
      "construct coordinates.")

# ---- 04 DIII-D descriptive branch ----------------------------------------
QD = "04_DIII_D_DESCRIPTIVE/D3D-SIR-62-ALIGNED-V1"
T(WEB / "canonical_d3d_62_shot_run_v1", f"{QD}/canonical_run",
  "qdesc", "Results 1.5; Supplement S7.1-S7.4", "D3D-SIR-62-ALIGNED-V1",
  "CANONICAL", "yes",
  "The canonical descriptive run: run manifest, aligned 62x1000 export, "
  "coordinate construction and manifest, design-matrix contract and hashes, "
  "discharge-specific coefficients, per-discharge metrics, pooled metrics, "
  "predictions, structural-search provenance, model artifact.")
T(WEB / "Coefficient_conditioning", f"{QD}/coefficient_conditioning",
  "qdesc", "Supplement S7.7; Figure S1", "D3D-SIR-62-COEFFICIENT-CONDITIONING-V1",
  "CANONICAL_WITH_SUPERSEDED_ORIGINAL", "yes",
  "Coefficient conditioning and identifiability. The ORIGINAL audit is retained "
  "here because the manuscript documents its correction; Correction_audit/ is "
  "the canonical verdict. See the directory README.")
T(WEB / "Implicit_elimination_and_denominator_conditioning",
  f"{QD}/implicit_elimination_audit",
  "qdesc", "Supplement S7.6", "D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1",
  "CANONICAL", "yes",
  "Implicit elimination and denominator conditioning: eliminated A summary, "
  "elimination identity validation, shift recovery, explicit-closure "
  "conditioning, target Jacobian validation, time-unit audit.")

# ---- 05 DIII-D reconstruction lineage ------------------------------------
REC = [
    ("02_reconstruction_contract", "00_Pretarget_Contract",
     "D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-V1",
     "Target-blind pretarget contract skeleton and its V2 correction; cohort "
     "partition; validation protocol; baseline protocol; claim boundary."),
    ("03_target_feasibility_and_boundary", "01_Target_Selection_and_02_Information_Boundary",
     "D3D-SIR-S7.3-TARGET-FEASIBILITY-SOURCE-RESOLUTION-V2",
     "Target census, ranking and selection (y* = density); the information "
     "boundary that admits 78 of 95 quantities and excludes 17 with reasons."),
    ("04_mathematical_interpretation", "03_Temporal_Realization",
     "D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2",
     "Task-conditioned mathematical interpretation: discharge-wise trajectory "
     "ensemble, source-supported cadence, trajectory index, no-upsample policy."),
    ("05_typed_relational_ontology", "04_Initial_Ontology/05_typed_relational_ontology",
     "D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1",
     "Typed relational ontology: constructor catalogue, type rules, signature "
     "schema."),
    ("05H_primitive_space_and_ontology_hardening", "04_Initial_Ontology/05H_primitive_hardening",
     "D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1",
     "Hardened primitive basis (70 levels, 63 derivative-eligible) and the "
     "23,861 symbolic coordinate space."),
    ("06_admissible_universe", "04_Initial_Ontology/06_admissible_universe_10778",
     "D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2",
     "The 10,778-atom admissible universe, denominator admissibility, numerical "
     "support, exact dependency groups, partial-map admissibility."),
    ("07_search_policy_and_frontier", "05_Parent_Development_Search",
     "D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2",
     "Search policy, strata, budget and the explored frontier of 162,845 "
     "supports, including the full candidate-evaluation and proposal-provenance "
     "records."),
    ("08_utility_and_qualification_rules", "05_Parent_Development_Search/utility_and_gates",
     "D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1",
     "Operationalized lexicographic utility U_rec and the qualification gates."),
    ("09_development_selection_and_freeze", "06_Frozen_Parent_Support",
     "D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1",
     "Development selection of C_dev_star on 20 discharges and the pre-external "
     "model freeze, with the bootstrap-winner family and elimination ledger."),
    ("10_external_validation", "07_Protected_Qualification_FAILURE",
     "D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1",
     "THE PARENT QUALIFICATION FAILURE. All 42 protected-discharge scores, "
     "baselines, block metrics, extrapolation audit, gate results and the "
     "immutable negative verdict."),
    ("11_sensitivity_and_interpretation", "08_Failure_Diagnosis/11_sensitivity",
     "D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1",
     "Predeclared sensitivities: the 217-member development-equivalent family, "
     "prmtan ablations, block and discharge omissions."),
    ("R1_operational_state_reconciliation", "08_Failure_Diagnosis/R1_operational_state",
     "D3D-SIR-S7.R1-OPERATIONAL-STATE-RECONCILIATION-V1",
     "The operational-state explanation, TESTED target-blindly and REFUTED. "
     "Establishes that the defect lay in the operational contract."),
    ("K2_observational_range_support_contract", "09_Range_Support_Case_B_Revision",
     "D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1",
     "The Case-B operational-contract revision: observational range support, "
     "tau = 1, threshold sensitivity, atomic audit, gas provenance resolution, "
     "K_REC_V1 to V2 changeset."),
    ("E2_0_protocol_and_resampling_freeze", "11_Descendant_Case_C_Contract/E2_0_protocol",
     "D3D-SIR-S7.E2.0-DISCOVERY-EPOCH2-PROTOCOL-V1",
     "The descendant claim-branch contract: six deterministic folds, access "
     "policy, search budget, qualification policy, stop rule."),
    ("E2_0A_predictor_admissibility_reconciliation",
     "11_Descendant_Case_C_Contract/E2_0A_information_boundary",
     "D3D-SIR-S7.E2.0A-PREDICTOR-SIDE-ADMISSIBILITY-RECONCILIATION-V1",
     "Transition-specific information boundary; tau_train retired; the "
     "3,451-atom candidate basis C_E2_FULL_DOMAIN."),
    ("E2_1_crossfitted_discovery_and_qualification", "12_Six_Fold_Target_Cross_Fitting",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "THE QUALIFIED POSITIVE RESULT. Six fold searches, six size-12 supports, "
     "per-fold records, V-RANGE integrity, per-discharge and per-block held-out "
     "results, baselines, cross-fitted metrics, gate table, access audit."),
    ("E2_2_full_object_descriptive_representation", "17_Applicability_and_Final_Claim/E2_2_descriptive",
     "D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1",
     "Representative full-object descriptive realization C_E2_ALL_DESC. "
     "Descriptive only; carries no validation weight."),
    ("S7_12_qualified_result", "17_Applicability_and_Final_Claim/S7_12_final",
     "D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1",
     "Q_rec*: final qualified result, provenance chain, gate table, limitations, "
     "claim boundary, branch closure, Figure-6 handoff."),
]
for sub, dest, run, notes in REC:
    T(S7 / sub, f"05_DIII_D_RECONSTRUCTION/{dest}", "qrec",
      "Results 1.5; Supplement S7", run,
      "CANONICAL_NEGATIVE_RESULT" if "FAILURE" in dest else "CANONICAL",
      "yes", notes)

# S7 normalization / audit layer -> lineage
for nm in ("README.md", "STATUS.md", "WORKFLOW.md", "SIR_ARCHITECTURE_MAP.md",
           "REVISION_LEDGER.md", "INFORMATION_FLOW_AUDIT.md",
           "INFORMATION_FLOW_AUDIT.json", "AUDIT_REPORT.md", "AUDIT_REPORT.json",
           "AUDIT_CHECKS.json", "ARCHITECTURE_SEMANTICS_AUDIT.md",
           "ARCHITECTURE_SEMANTICS_AUDIT.json", "MANUSCRIPT_ALIGNMENT.md",
           "MANUSCRIPT_ALIGNMENT.json", "CLAIM_EVIDENCE_MATRIX.json",
           "CANONICAL_INDEX.json", "REPRODUCIBILITY.md", "audit_s7.py"):
    F(S7 / nm, f"05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/{nm}",
      "lineage", "Supplement S7", None, "CANONICAL", "yes",
      "S7 normalization and audit layer: stage index, branch lineage, revision "
      "ledger, leakage audit, claim-evidence matrix and the re-runnable checker.")
T(S7 / "_audit", "05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/_audit",
  "lineage", "Supplement S7", None, "CANONICAL", "yes",
  "Stage registry, package builders and the independent recomputations "
  "(range support, target ancestry) used by the S7 audit.")
F(S7 / "_manifests" / "INITIAL_STATE_MANIFEST.json",
  "05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/INITIAL_STATE_MANIFEST.json",
  "lineage", "Supplement S7", None, "CANONICAL", "yes",
  "State of the tree when S7 began.")
T(S7 / "FIGURE_EXPORT", "05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/FIGURE_EXPORT",
  "lineage", "Figure 6", None, "CANONICAL", "yes",
  "Minimal frozen inputs exported for the DIII-D four-panel figure, with a "
  "per-file provenance manifest.")

# ---- 06 paper figures (ALLOW-LIST ONLY) ----------------------------------
# Resolved by tracing each script's declared output STEM, not by filename.
FIGSPEC = [
    dict(folder="Fig_01_admissible_relational_space",
         assets=[Figures := ROOT / "Figures" / "figs" /
                 "admissible_relational_space_hierarchical_v15_metaball.pdf"],
         scripts=[ROOT / "General" / "admissible_relational_space_hierarchical_v15_metaball_final.py",
                  ROOT / "General" / "admissible_relational_space_hierarchical_v15_metaball.py"],
         data=[], note="AMBIGUOUS script->asset mapping; see README and "
                       "90_AUDIT_REPORTS/ambiguous_artifacts.csv."),
    dict(folder="Fig_02_phase_turning_manifold",
         assets=[DEX / "phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf"],
         scripts=[DEX / "phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py"],
         data=[], note="v8 script writes this exact stem."),
    dict(folder="Fig_04_task_contracts_representations",
         assets=[ROOT / "Figures" / "figs" /
                 "figure4_task_contracts_mathematical_representations_nature_one_row.pdf",
                 ROOT / "Figures" / "figs" /
                 "figure4_task_contracts_mathematical_representations_nature_one_row.svg"],
         scripts=[ROOT / "Pendulum" / "Plotter" /
                  "figure4_task_contracts_mathematical_representations_nature_one_row.py"],
         data=[ROOT / "Pendulum" / "Plotter" / "panel_data.py"],
         note="Script writes to Pendulum/Plotter/figs; the asset was moved to "
              "Figures/figs by hand. Manual relocation step recorded."),
    dict(folder="Fig_05_lorenz_representation_landscape",
         assets=[ROOT / "Lorenz" / "figure5_lorenz_representation_landscape_final_tnr_v5_nature.pdf"],
         scripts=[ROOT / "Lorenz" / "figure5_lorenz_representation_landscape_final_tnr_v5_nature.py"],
         data=[], note="Inputs are the frozen fig5data package, copied under "
                       "02_CONTROLLED_STUDIES and referenced here."),
    dict(folder="Fig_06_d3d_task_conditioned_4panel",
         assets=[DEX / "d3d_task_conditioned_4panel_v5.pdf",
                 DEX / "d3d_task_conditioned_4panel_v5.svg",
                 DEX / "d3d_task_conditioned_4panel_v5.png"],
         scripts=[DEX / "d3d_task_conditioned_4panel_v5.py"],
         data=[], note="Inputs are DIIID_example/fig6data, copied into "
                       "figure_source_data/ here."),
]
SUPPFIG = [
    ("d3d_coefficient_change_vs_rank_removed",
     "Panel a: relative coefficient change and RMSE change after removing the "
     "weakest singular directions."),
    ("d3d_heterogeneity_interval_by_coefficient",
     "Panel b: REML between-discharge variance with profile intervals."),
    ("d3d_multivariate_eigenvalue_uncertainty",
     "Panel c: ordered eigenvalues of Sigma_B - Sigma_W with bootstrap and "
     "matched-null thresholds."),
]

# ---- 08 contracts / provenance / qualification ---------------------------
F(DEX / "fig6data" / "RETIREMENT_RECORD.json",
  "10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch/RETIREMENT_RECORD.json",
  "historical", "Results 1.5 (superseded text)", "D3D-FIG6-QREC-RETIREMENT-V1",
  "RETIRED", "yes",
  "RETIRED. Records why the earlier I_p reconstruction branch was withdrawn: "
  "target-provenance leakage and no skill over a persistence baseline. "
  "SUPERSEDED BY the S7 density lineage under 05_DIII_D_RECONSTRUCTION.")
F(DEX / "fig6data" / "PROVENANCE_MANIFEST.json",
  "10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch/PROVENANCE_MANIFEST.json",
  "historical", "Results 1.5 (superseded text)", None, "RETIRED", "yes",
  "Provenance manifest for the retired-branch audit package.")
for nm in ("qrec_provenance_verdicts.csv", "qrec_provenance_dag.csv",
           "qrec_provenance_dependence_by_shot.csv", "qrec_ip_from_q95_inversion.csv",
           "qrec_support_admissibility.csv", "qrec_trivial_baselines.csv",
           "qrec_corrected_universe_probe.csv"):
    F(DEX / "fig6data" / nm,
      f"10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch/{nm}",
      "historical", "Results 1.5 (superseded text)", None, "RETIRED", "yes",
      "Evidence behind the retirement: target-ancestry tests and trivial-baseline "
      "comparison. RETIRED; not a current result.")
T(DEX / "Figure6_qualification_audit",
  "10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch/qualification_audit",
  "historical", "Results 1.5 (superseded text)", "D3D-FIG6-PROVENANCE-AUDIT-V1",
  "RETIRED", "yes",
  "The audit that retired the I_p branch. RETIRED context, retained because the "
  "manuscript correction cannot be understood without it.")
T(DEX / "Figure_data",
  "10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch/frozen_summary_exports",
  "historical", "Results 1.5 (superseded text)", "D3D-SIR-62-ALIGNED-V1",
  "RETIRED_RECONSTRUCTION_BRANCH_ONLY", "yes",
  "Frozen summary exports. The q_desc support export remains valid; the "
  "reconstruction summary is RETIRED for provenance leakage.")
F(S7 / "_legacy_reference" / "LEGACY_QREC_STATUS.md",
  "10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches/retired_Ip_branch/LEGACY_QREC_STATUS.md",
  "historical", "Supplement S7", None, "RETIRED", "yes",
  "S7's own firewall against the retired branch.")


# --------------------------------------------------------------------------
def gather(dry: bool):
    records: list[dict] = []
    skipped: list[dict] = []

    def add(src: Path, rel: str, spec: dict):
        if not src.exists() or not src.is_file():
            skipped.append({"source": str(src), "reason": "MISSING_AT_SOURCE",
                            "dest": rel})
            return
        if excluded(src):
            skipped.append({"source": str(src), "reason": "EXCLUDED_BUILD_NOISE",
                            "dest": rel})
            return
        if restricted(src):
            skipped.append({"source": str(src), "reason": "RESTRICTED_NOT_BUNDLED",
                            "dest": rel})
            return
        dst = PKG / rel
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        st = src.stat()
        records.append({
            "package_path": rel.replace("\\", "/"),
            "original_path": str(src),
            "size_bytes": st.st_size,
            "sha256": sha256(src),
            "modified_utc": datetime.fromtimestamp(st.st_mtime,
                                                   timezone.utc).isoformat(),
            "category": spec["category"], "paper_sections": spec["sections"],
            "run_id": spec["run_id"] or "", "status": spec["status"],
            "redistributable": spec["redist"], "notes": spec["notes"],
        })

    for spec in FILES:
        add(spec["src"], spec["dest"], spec)
    for spec in TREES:
        root = spec["src"]
        if not root.exists():
            skipped.append({"source": str(root), "reason": "MISSING_TREE",
                            "dest": spec["dest"]})
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file() or excluded(p):
                continue
            if spec["only"] and not fnmatch.fnmatch(p.name, spec["only"]):
                continue
            add(p, f"{spec['dest']}/{p.relative_to(root).as_posix()}", spec)
    return records, skipped


def stage_figures(recs: list[dict], skipped: list[dict]) -> list[dict]:
    """Phase 9. ONLY figures on the allow-list derived from the current figure
    assets; every other figure script in the project is recorded as excluded."""
    figinfo = []

    def put(src: Path, rel: str, spec: dict):
        if not src.exists():
            skipped.append({"source": str(src), "reason": "MISSING_AT_SOURCE",
                            "dest": rel})
            return False
        dst = PKG / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        st = src.stat()
        recs.append({
            "package_path": rel.replace("\\", "/"), "original_path": str(src),
            "size_bytes": st.st_size, "sha256": sha256(src),
            "modified_utc": datetime.fromtimestamp(st.st_mtime,
                                                   timezone.utc).isoformat(),
            "category": spec["category"], "paper_sections": spec["sections"],
            "run_id": spec["run_id"] or "", "status": spec["status"],
            "redistributable": "yes", "notes": spec["notes"]})
        return True

    for fs in FIGSPEC:
        base = f"06_PAPER_FIGURES_ONLY/{fs['folder']}"
        sp = dict(category="figure", sections="main manuscript", run_id=None,
                  status="CANONICAL_FIGURE_ASSET", notes=fs["note"])
        for a in fs["assets"]:
            put(a, f"{base}/{a.name}", sp)
        for s in fs["scripts"]:
            put(s, f"{base}/figure_source/{s.name}",
                dict(sp, category="figure_script",
                     status="CANONICAL_FIGURE_SCRIPT"))
        for d in fs["data"]:
            put(d, f"{base}/figure_source_data/{d.name}",
                dict(sp, category="figure_data", status="CANONICAL_FIGURE_DATA"))
        figinfo.append({"folder": fs["folder"],
                        "assets": [a.name for a in fs["assets"]],
                        "scripts": [str(s) for s in fs["scripts"]],
                        "note": fs["note"]})

    # Figure 6 inputs: the frozen fig6data package
    for p in sorted((DEX / "fig6data").glob("*")):
        if p.is_file() and not p.name.startswith("qrec_") and \
                p.name not in ("RETIREMENT_RECORD.json", "PROVENANCE_MANIFEST.json"):
            put(p, f"06_PAPER_FIGURES_ONLY/Fig_06_d3d_task_conditioned_4panel/"
                   f"figure_source_data/{p.name}",
                dict(category="figure_data", sections="Figure 6",
                     run_id="D3D-SIR-S7.E2.1 / D3D-SIR-62-ALIGNED-V1",
                     status="CANONICAL_FIGURE_DATA",
                     notes="Frozen input copied verbatim from DIIID_example/fig6data."))
    # Figure 5 inputs: frozen fig5data
    for p in sorted((ROOT / "Lorenz" / "fig5data").glob("*")):
        if p.is_file():
            put(p, f"06_PAPER_FIGURES_ONLY/Fig_05_lorenz_representation_landscape/"
                   f"figure_source_data/{p.name}",
                dict(category="figure_data", sections="Figure 5",
                     run_id="SIR-LORENZ-TASK-CONDITIONING",
                     status="CANONICAL_FIGURE_DATA",
                     notes="Frozen input copied verbatim from Lorenz/fig5data."))

    # Supplementary three-panel coefficient-conditioning figure
    sbase = "06_PAPER_FIGURES_ONLY/Supplementary_Figures/FigS1_coefficient_conditioning"
    figdir = WEB / "Coefficient_conditioning" / "Correction_audit" / "figures"
    for stem, desc in SUPPFIG:
        for ext in ("pdf", "png", "svg"):
            put(figdir / f"{stem}.{ext}", f"{sbase}/{stem}.{ext}",
                dict(category="figure", sections="Supplement S7.7, Figure S1",
                     run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
                     status="CANONICAL_FIGURE_ASSET", notes=desc))
    for s in ("generate_correction_figures.py", "correction_audit_utils.py"):
        put(WEB / "Coefficient_conditioning" / "Correction_audit" / s,
            f"{sbase}/figure_source/{s}",
            dict(category="figure_script", sections="Supplement S7.7",
                 run_id="D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
                 status="CANONICAL_FIGURE_SCRIPT",
                 notes="Generator for the three Supplement panels."))
    return figinfo


def stage_restricted_index(recs: list[dict], skipped: list[dict]) -> dict:
    """Phase 6 + 13. Hash and index the restricted archive without bundling it;
    copy the small derived per-shot metadata, which is redistributable."""
    src = DEX / "data" / "resampled_data_v6"
    rows, total = [], 0
    for p in sorted(src.glob("*_resampled.npz")):
        st = p.stat()
        total += st.st_size
        rows.append({"shot": p.name.split("_")[1], "filename": p.name,
                     "size_bytes": st.st_size, "sha256": sha256(p),
                     "original_path": str(p),
                     "redistributable": "NO_RESTRICTED_SOURCE_ARCHIVE",
                     "bundled_in_package": "no"})
    out = PKG / "03_DIII_D_SOURCE_OBJECT" / "source_access_notes"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "RESTRICTED_SOURCE_INDEX.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    sp = dict(category="source_object",
              sections="Methods; Supplement S7.1, S7.2",
              run_id="D3D-SIR-62-ALIGNED-V1", status="CANONICAL",
              redist="yes",
              notes="Per-shot resampling metadata: method, category, units and "
                    "provenance for each admitted signal. Derived and "
                    "redistributable; the .npz arrays themselves are not bundled.")
    for p in sorted(src.glob("*_metadata.json")):
        dst = PKG / f"03_DIII_D_SOURCE_OBJECT/retrieval_metadata/shot_metadata/{p.name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        st = p.stat()
        recs.append({"package_path": str(dst.relative_to(PKG)).replace("\\", "/"),
                     "original_path": str(p), "size_bytes": st.st_size,
                     "sha256": sha256(p),
                     "modified_utc": datetime.fromtimestamp(
                         st.st_mtime, timezone.utc).isoformat(),
                     "category": sp["category"], "paper_sections": sp["sections"],
                     "run_id": sp["run_id"], "status": sp["status"],
                     "redistributable": "yes", "notes": sp["notes"]})
    for nm in ("dataset_statistics.json", "processing_checkpoint.json"):
        p = src / nm
        if p.exists():
            dst = PKG / f"03_DIII_D_SOURCE_OBJECT/retrieval_metadata/{nm}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            st = p.stat()
            recs.append({"package_path": str(dst.relative_to(PKG)).replace("\\", "/"),
                         "original_path": str(p), "size_bytes": st.st_size,
                         "sha256": sha256(p),
                         "modified_utc": datetime.fromtimestamp(
                             st.st_mtime, timezone.utc).isoformat(),
                         "category": "source_object",
                         "paper_sections": "Supplement S7.2",
                         "run_id": "D3D-SIR-62-ALIGNED-V1", "status": "CANONICAL",
                         "redistributable": "yes",
                         "notes": "Archive-level resampling statistics and "
                                  "processing checkpoint."})
    return {"n_restricted_files": len(rows), "total_bytes": total,
            "index": "03_DIII_D_SOURCE_OBJECT/source_access_notes/"
                     "RESTRICTED_SOURCE_INDEX.csv"}


def write_manifest(recs: list[dict]):
    cols = ["package_path", "original_path", "size_bytes", "sha256",
            "modified_utc", "category", "paper_sections", "run_id", "status",
            "redistributable", "notes"]
    d = PKG / "00_START_HERE"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "PACKAGE_MANIFEST.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in sorted(recs, key=lambda x: x["package_path"]):
            w.writerow({k: r.get(k, "") for k in cols})
    (d / "PACKAGE_MANIFEST.json").write_text(json.dumps(
        {"record_id": "SIR_PAPER_DATA_MANIFEST_V1", "generated_utc": NOW,
         "n_files": len(recs),
         "total_bytes": sum(r["size_bytes"] for r in recs),
         "files": sorted(recs, key=lambda x: x["package_path"])},
        indent=1), encoding="utf-8")
    lines = ["%s  %s" % (r["sha256"], r["package_path"])
             for r in sorted(recs, key=lambda x: x["package_path"])]
    (PKG / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.dry_run:
        PKG.mkdir(parents=True, exist_ok=True)
    recs, skipped = gather(a.dry_run)
    if not a.dry_run:
        figinfo = stage_figures(recs, skipped)
        restricted_info = stage_restricted_index(recs, skipped)
        write_manifest(recs)
        (PKG / "_staging_records.json").write_text(json.dumps(
            {"generated_utc": NOW, "records": recs, "skipped": skipped,
             "figures": figinfo, "restricted": restricted_info}, indent=1),
            encoding="utf-8")
    total = sum(r["size_bytes"] for r in recs)
    print("files copied : %d" % len(recs))
    print("total size   : %.1f MB" % (total / 1048576))
    print("skipped      : %d" % len(skipped))
    for s in skipped[:10]:
        print("   SKIP %-28s %s" % (s["reason"], s["source"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
