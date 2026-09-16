#!/usr/bin/env python
"""Generate the Paper_Data audit reports and access index (Phases 12, 13, 15, 17)."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PKG = Path(r"D:\SIR_paper\Paper_Data")
NOW = datetime.now(timezone.utc).isoformat()
RECS = json.loads((PKG / "_staging_records.json").read_text(encoding="utf-8"))["records"]

QDR = "04_DIII_D_DESCRIPTIVE/D3D-SIR-62-ALIGNED-V1"
RCR = "05_DIII_D_RECONSTRUCTION"
E1R = f"{RCR}/12_Six_Fold_Target_Cross_Fitting"


def wcsv(rel, rows, cols):
    p = PKG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: r.get(k, "") for k in cols})
    print("  ", rel, "(%d rows)" % len(rows))


EXCLUDED_FIGSCRIPTS = [
    ("General/admissible_relational_space_hierarchical_v14.py",
     "obsolete figure version; current manuscript uses the v15 metaball figure"),
    ("General/admissible_relational_space_v2.py",
     "obsolete figure version; superseded by the v15 hierarchical metaball figure"),
    ("General/sir_representational_prism.py",
     "visual-abstract concept not present in the current manuscript"),
    ("General/sir_representational_prism_visual_abstract_v9.py",
     "visual-abstract concept not present in the current manuscript"),
    ("DIIID_example/phase_turning_manifold_sensitivity_centered_with_x2_purple_v4.py",
     "obsolete figure version; current manuscript uses v8"),
    ("DIIID_example/phase_turning_manifold_reference_shifted.py",
     "earlier reference-shifted variant; not the manuscript figure"),
    ("DIIID_example/Plotter/d3d_task_conditioned_discovery.py",
     "superseded DIII-D figure; replaced by d3d_task_conditioned_4panel_v5"),
    ("DIIID_example/relational_plasma_reconstruction_infographic.py",
     "infographic not present in the current manuscript"),
    ("Lorenz/figure5_lorenz_representation_landscape_final_tnr_v4.py",
     "obsolete figure version; current manuscript uses v5_nature"),
    ("Lorenz/figure5_lorenz_representation_landscape_prototype.py", "rejected prototype"),
    ("Lorenz/figure5_lorenz_nested_representation_discovery.py",
     "exploratory figure concept; retained as a controlled-study script, not as a "
     "manuscript figure asset"),
    ("Lorenz/Lorenz_attractor.py", "illustrative attractor plot; not a manuscript figure"),
    ("Pendulum/Plotter/make_pendulum_task_conditioned_panel.py",
     "superseded pendulum panel; Figure 4 uses figure4_task_contracts_..."),
    ("Pendulum/Plotter/make_pendulum_task_conditioned_panel_compact.py",
     "superseded compact variant"),
    ("Pendulum/Plotter/pendulum_task_conditioned_panel_v5.py",
     "superseded pendulum panel version"),
    ("Figures/degeneracy.py", "standalone heat-equation plot; not a manuscript figure"),
    ("Figures/ECDF_plot.py", "exploratory ECDF plot; not a manuscript figure"),
    ("Figures/lift_map.py", "exploratory lift-map plot; not a manuscript figure"),
    ("Figures/lift_map_reveal.py", "presentation reveal variant"),
    ("Figures/organic_multicrossing.py", "exploratory geometry plot"),
    ("Figures/organic_multicrossing_reveal.py", "presentation reveal variant"),
    ("DIIID_example/S7/figures/make_s7_figures.py",
     "internal S7 audit figures; retained under 05_.../18_Machine_Readable_Lineage, "
     "not a manuscript figure"),
]

rows = [dict(path=p, kind="figure_generation_asset", reason=r,
             recorded_by="Phase 9 allow-list") for p, r in EXCLUDED_FIGSCRIPTS]
rows += [
    dict(path="DIIID_example/data/resampled_data_v6/*_resampled.npz",
         kind="restricted_source_data",
         reason="DIII-D archive arrays, 1.1 GB across 62 shots; redistribution not "
                "established. Indexed with SHA-256 in RESTRICTED_SOURCE_INDEX.csv; "
                "the derived per-shot metadata IS bundled.",
         recorded_by="Phase 6/13"),
    dict(path="DIIID_example/S7.zip", kind="duplicate_archive",
         reason="Byte-archive of the S7 tree that is already bundled file-by-file.",
         recorded_by="Phase 3"),
    dict(path="Lorenz/fig5data.zip, DIIID_example/fig6data.zip",
         kind="duplicate_archive",
         reason="Archives of figure data already bundled file-by-file.",
         recorded_by="Phase 3"),
    dict(path="D:/sir-web/.../DIII-D reconstruction-frontier discovery study; "
              "DIII-D A-constrained reconstruction-frontier study; "
              "DIII-D fixed-support Phase-RS conditioning probe",
         kind="retired_branch_bulk_studies",
         reason="2.7 GB of exploratory studies belonging to the RETIRED I_p branch. "
                "The retirement record and its evidence ARE bundled under "
                "10_REFERENCED_HISTORICAL_LINEAGE; the bulk studies are indexed in "
                "LOCAL_INTERNAL_SOURCE_INDEX.csv rather than copied.",
         recorded_by="Phase 12"),
    dict(path="**/__pycache__, .venv_lorenz_benchmark, .pytest_cache, .dalia, .git, "
              "*.pyc, LaTeX aux/log/synctex",
         kind="build_noise", reason="Standard software and build noise.",
         recorded_by="Phase 3"),
]
wcsv("90_AUDIT_REPORTS/excluded_files.csv", rows,
     ["path", "kind", "reason", "recorded_by"])

wcsv("90_AUDIT_REPORTS/ambiguous_artifacts.csv", [
    dict(artifact="Figure 1 script -> asset mapping",
         candidates="General/admissible_relational_space_hierarchical_v15_metaball_final.py "
                    "(2026-09-09) vs ..._metaball.py (2026-09-07)",
         issue="Both declare STEM='admissible_relational_space_hierarchical_v15_metaball' "
               "and write to Figures/figs. The on-disk PDF carries the mtime of the "
               "NON-final script; the _final script appears never to have been rendered. "
               "Neither can emit the '..._metaball_final.pdf' filename used in the "
               "figure cross-check. The two scripts differ by six lines (a patch edge "
               "colour and linewidth).",
         resolution="BOTH scripts bundled in Fig_01/figure_source/. Render _final.py and "
                    "confirm which asset the manuscript embeds.",
         status="AMBIGUOUS"),
    dict(artifact="Coefficient_conditioning original vs Correction_audit",
         candidates=f"{QDR}/coefficient_conditioning/outputs vs .../Correction_audit/outputs",
         issue="The original audit carries the retired verdict "
               "D3D-COEFFICIENT-FAMILY-RESOLVED and mislabelled profile-ML as REML.",
         resolution="RESOLVED. Correction_audit is canonical "
                    "(D3D-MIXED-COEFFICIENT-IDENTIFIABILITY). Both are bundled and the "
                    "directory README states which supersedes which.",
         status="RESOLVED"),
    dict(artifact="Conditioning_repair study",
         candidates="D:/sir-web/.../Conditioning_repair (162 MB)",
         issue="A conditioning-aware repair audit that the staged manuscript does not "
               "appear to reference.",
         resolution="NOT bundled; indexed in LOCAL_INTERNAL_SOURCE_INDEX.csv. Include if "
                    "the next manuscript pass cites it.",
         status="AMBIGUOUS"),
    dict(artifact="Supplementary Figure S1 raster variants",
         candidates="d3d_*.pdf (exist) vs *.png/*.svg under un-prefixed names",
         issue="Only PDF exists for the d3d_-prefixed manuscript assets. The "
               "Correction_audit manifest additionally lists three un-prefixed PDFs "
               "that are absent (74 of 77 manifest entries reproduce).",
         resolution="PDFs bundled; both gaps recorded in missing_artifacts.csv.",
         status="PARTIALLY_RESOLVED"),
    dict(artifact="Figure 4 asset location",
         candidates="Pendulum/Plotter/figs (script target) vs Figures/figs (asset)",
         issue="The script writes to Pendulum/Plotter/figs, which does not exist; the "
               "asset lives in Figures/figs.",
         resolution="Manual relocation step; recorded in the Fig_04 README and the "
                    "figure index.",
         status="RESOLVED"),
], ["artifact", "candidates", "issue", "resolution", "status"])

wcsv("90_AUDIT_REPORTS/missing_artifacts.csv", [
    dict(expected="Current main manuscript TeX source",
         searched="whole D:/SIR_paper tree, all file types, plus content search for the "
                  "paper title and for every .tex/.docx/.zip",
         status="MISSING",
         impact="Phases 2, 9 and 15 cannot run as specified: no sections, figure "
                "environments, \\includegraphics, tables or \\releasepending "
                "placeholders can be parsed. The figure allow-list was instead derived "
                "from on-disk assets and verified by tracing each script's declared "
                "output stem.",
         recommendation="Supply the TeX (or an Overleaf export) and re-run Phase 2."),
    dict(expected="Current Supplementary Information TeX source",
         searched="same", status="MISSING",
         impact="The only Supplement artifact is Supplementary Notes S1-S8 embedded in "
                "the staged PDF.",
         recommendation="Supply the Supplement TeX."),
    dict(expected="\\releasepending{...} placeholders",
         searched="whole tree, all file types", status="NONE_FOUND",
         impact="No literal placeholders exist. The equivalent gaps were identified by "
                "comparing the staged manuscript against the canonical artifacts and "
                "are listed in unresolved_release_fields.csv.",
         recommendation="Re-run Phase 15 once TeX is available."),
    dict(expected="q_desc explored-frontier record",
         searched="canonical_d3d_62_shot_run_v1, Coefficient_conditioning",
         status="MISSING",
         impact="The descriptive search frontier count, budget and stopping reason are "
                "not recorded as a machine-readable artifact, unlike the q_rec frontier "
                "(162,845 supports, fully recorded).",
         recommendation="Export the q_desc search frontier, or state in the Supplement "
                        "that it was not retained."),
    dict(expected="Frozen paired-bootstrap interval for Delta_1",
         searched=E1R, status="MISSING",
         impact="Per-discharge Delta_j IS present, so the interval is computable, but "
                "no frozen interval artifact exists. Phase 17.I.",
         recommendation="Compute and freeze it, or report the point estimate only."),
    dict(expected="Spline / RTS numerical-realization run manifests",
         searched="canonical_d3d_62_shot_run_v1", status="MISSING",
         impact="The manuscript already marks these provisional.",
         recommendation="Keep the provisional wording or drop the variants."),
    dict(expected="Effective degrees of freedom 99 -> 10.6",
         searched="whole tree", status="MISSING",
         impact="Never reproduced from primary artifacts; belongs to the retired branch.",
         recommendation="Remove from the manuscript."),
    dict(expected="d3d_*.png / d3d_*.svg Supplement raster variants",
         searched="Correction_audit/figures", status="MISSING_RASTER_VARIANTS",
         impact="None: the .pdf assets exist and are bundled.",
         recommendation="Regenerate if a raster Supplement is required."),
    dict(expected="coefficient_change_vs_rank_removed.pdf and two siblings (un-prefixed)",
         searched="Correction_audit/figures", status="MISSING",
         impact="Listed in the Correction_audit manifest but absent; 74 of 77 entries "
                "reproduce. No numerical result affected.",
         recommendation="Regenerate or amend that manifest."),
    dict(expected="environment.yml / requirements.txt", searched="whole tree",
         status="GENERATED_INSTEAD",
         impact="None. 09_REPRODUCIBILITY/environment/ records the exact interpreter and "
                "package versions captured from the working virtual environment.",
         recommendation="Commit the generated requirements file alongside the code."),
], ["expected", "searched", "status", "impact", "recommendation"])

RP = [
    ("Results 1.5 / Fig. 4b / Supplement S7.8", "canonical q_rec result",
     f"{E1R}/E2_1_CROSSFITTED_METRICS.json", "VERIFIED",
     "Replace the entire I_p / 141-coordinate / 7-development / 55-external result with "
     "the density cross-fitted result: 0.189 vs 0.216, Delta_1 = -0.0273, six folds, "
     "union 35, mean Jaccard 0.285244.", "HIGH",
     "The staged manuscript reports a branch this repository retired on 2026-09-02 for "
     "target-provenance leakage and for having no skill over persistence."),
    ("Results 1.1", "claim-core / operational-epoch architecture",
     f"{RCR}/18_Machine_Readable_Lineage/SIR_ARCHITECTURE_MAP.md", "VERIFIED",
     "Adopt K_q^(e) = (K^claim, K^op,(e)) and replace the blanket validation-data rule "
     "with the protected-evidence rule.", "HIGH",
     "The staged PDF carries the flat 8-tuple contract."),
    ("Supplement S7.1", "DIII-D candidate discharge pool and inclusion criteria",
     "03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/shot_inventory.csv", "VERIFIED",
     "Cite the frozen shot inventory and the cohort-provenance ledger.", "HIGH", ""),
    ("Supplement S7.1", "processing-era mapping and boundary",
     f"{RCR}/11_Descendant_Case_C_Contract/E2_0_protocol/outer_fold_assignment.csv",
     "VERIFIED", "Era assignment is frozen per discharge: 35 earlier, 27 later.",
     "HIGH", ""),
    ("Supplement S7.1", "cohort-freeze chronology",
     "03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/reconciliation_final/"
     "S7_1_REVISION_LEDGER.md", "VERIFIED", "Cite the S7.1 revision ledger.",
     "MEDIUM", ""),
    ("Supplement S7.3", "descriptive search algorithm and version",
     f"{QDR}/canonical_run/D3D_STRUCTURAL_SEARCH_PROVENANCE.md", "VERIFIED",
     "Cite the structural-search provenance document.", "MEDIUM",
     "Confirm it states budget and stopping reason explicitly."),
    ("Supplement S7.3", "descriptive explored-frontier count", "", "MISSING",
     "No explored-frontier record exists for the q_desc search.", "HIGH",
     "The q_rec frontier is fully recorded; the q_desc equivalent is not."),
    ("Supplement S7.3", "descriptive random / restart state",
     f"{QDR}/canonical_run/canonical_run_manifest.json", "AMBIGUOUS",
     "Check the run manifest for a seed field; none was located by name.", "MEDIUM", ""),
    ("Supplement S7", "reconstruction target-selection manifest",
     f"{RCR}/01_Target_Selection_and_02_Information_Boundary/reconciliation_source_resolution/"
     "S7_3_FREEZE_V2.json", "VERIFIED",
     "Target ranking, feasibility filters and the selected density target are frozen.",
     "HIGH", ""),
    ("Supplement S7", "reconstruction search-frontier records",
     f"{RCR}/05_Parent_Development_Search/one_seed_primary_v2/explored_support_registry.csv",
     "VERIFIED", "162,845 explored supports, with per-candidate evaluations and "
     "proposal provenance.", "HIGH", ""),
    ("Supplement S7", "reconstruction search budget and stopping reason",
     f"{RCR}/11_Descendant_Case_C_Contract/E2_0_protocol/EPOCH2_SEARCH_BUDGET.json",
     "VERIFIED", "300,000 per fold, 1,800,000 total; 765,758 proposals used.",
     "HIGH", ""),
    ("Supplement S7", "parent qualification numerical gates",
     f"{RCR}/07_Protected_Qualification_FAILURE/S7_10_FREEZE.json", "VERIFIED",
     "gate_results: V3 FAIL, V6 FAIL, Omega_rec EMPTY.", "HIGH", ""),
    ("Supplement S7", "descendant qualification gate-by-gate outcomes",
     f"{E1R}/E2_1_GATE_TABLE.json", "VERIFIED", "V1-V10 plus V-RANGE all recorded.",
     "HIGH", ""),
    ("Supplement S7", "paired-bootstrap uncertainty for Delta_1", "", "MISSING",
     "Per-discharge Delta_j is available so the bootstrap is computable, but no frozen "
     "interval artifact exists.", "HIGH", "Phase 17.I."),
    ("Supplement S7", "era-stratification definition and status",
     f"{E1R}/E2_1_CROSSFITTED_METRICS.json", "VERIFIED",
     "era block: +0.0076 earlier (n=35), -0.0726 later (n=27), V6 "
     "PASS_WITH_QUALIFICATION.", "HIGH", ""),
    ("Supplement S7.5", "spline and RTS run identifiers", "", "MISSING",
     "Keep the provisional wording or drop the variants.", "HIGH", ""),
    ("Methods", "repository / archive identifiers",
     "00_START_HERE/ACCESS_AND_LICENSE.md", "PENDING",
     "Assign a DOI or archive identifier for this package.", "MEDIUM", ""),
]
wcsv("90_AUDIT_REPORTS/unresolved_release_fields.csv",
     [dict(manuscript="SIR_paper_2026-09-02.pdf", line_or_section=s,
           placeholder="(no literal \\releasepending in repo; gap identified by "
                       "artifact comparison)",
           expected_artifact=a, candidate_source_path=p, status=st,
           recommended_value_or_action=act, confidence=c, notes=n)
      for s, a, p, st, act, c, n in RP],
     ["manuscript", "line_or_section", "placeholder", "expected_artifact",
      "candidate_source_path", "status", "recommended_value_or_action",
      "confidence", "notes"])

byh = defaultdict(list)
for r in RECS:
    byh[r["sha256"]].append(r["package_path"])
dups = [dict(sha256=h, n_copies=len(v), paths=" | ".join(v[:6]))
        for h, v in byh.items() if len(v) > 1]
wcsv("90_AUDIT_REPORTS/duplicate_candidates.csv",
     sorted(dups, key=lambda d: -d["n_copies"]), ["sha256", "n_copies", "paths"])

wcsv("03_DIII_D_SOURCE_OBJECT/source_access_notes/LOCAL_INTERNAL_SOURCE_INDEX.csv", [
    dict(internal_path=r"D:\SIR_paper\DIIID_example\data\resampled_data_v6\*_resampled.npz",
         kind="restricted DIII-D resampled archive", size="1.1 GB, 62 files",
         bundled="no", reason="redistribution not established",
         substitute="RESTRICTED_SOURCE_INDEX.csv (SHA-256 per shot), per-shot metadata "
                    "JSON, and every derived artifact"),
    dict(internal_path=r"D:\sir-web\...\DIII-D reconstruction-frontier discovery study",
         kind="retired I_p branch study", size="1.1 GB", bundled="no",
         reason="belongs to the retired branch; bulk exploratory",
         substitute="10_REFERENCED_HISTORICAL_LINEAGE/failed_parent_branches"),
    dict(internal_path=r"D:\sir-web\...\DIII-D fixed-support Phase-RS conditioning probe",
         kind="retired I_p branch study", size="797 MB", bundled="no",
         reason="belongs to the retired branch", substitute="same"),
    dict(internal_path=r"D:\sir-web\...\DIII-D A-constrained reconstruction-frontier study",
         kind="retired I_p branch study", size="769 MB", bundled="no",
         reason="belongs to the retired branch", substitute="same"),
    dict(internal_path=r"D:\sir-web\...\Conditioning_repair",
         kind="conditioning-aware repair audit", size="162 MB", bundled="no",
         reason="not referenced by the staged manuscript; see ambiguous_artifacts.csv",
         substitute="none; include on request"),
], ["internal_path", "kind", "size", "bundled", "reason", "substitute"])
print("audit reports written")
