#!/usr/bin/env python
"""Per-figure READMEs, manuscript inventory, environment capture and the
reproducibility layer for Paper_Data (Phases 2, 9, 11)."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\SIR_paper")
PKG = ROOT / "Paper_Data"
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()


def w(rel, text):
    p = PKG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.lstrip("\n").rstrip() + "\n", encoding="utf-8")
    print("  ", rel)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ==================================================== per-figure READMEs
FIGS = [
    ("Fig_01_admissible_relational_space", "Figure 1",
     "Admissible relational space: coordinate-generation operators and relation "
     "families, with symbolic regression shown as one restricted subfamily.",
     "admissible_relational_space_hierarchical_v15_metaball.pdf",
     ["admissible_relational_space_hierarchical_v15_metaball_final.py",
      "admissible_relational_space_hierarchical_v15_metaball.py"],
     "none — schematic, no numerical inputs", "",
     "**AMBIGUOUS.** Both scripts declare the identical output stem "
     "`admissible_relational_space_hierarchical_v15_metaball` and write to "
     "`Figures/figs`. The asset on disk carries the modification time of the "
     "NON-final script (2026-09-07 15:41); `_final.py` is newer (2026-09-09) and "
     "appears never to have been rendered. The two differ by six lines — a patch "
     "edge colour and linewidth. Neither script can produce the "
     "`..._metaball_final.pdf` filename used in the figure cross-check. **Both are "
     "bundled.** Render `_final.py` and confirm which asset the manuscript embeds.",
     "python figure_source/admissible_relational_space_hierarchical_v15_metaball_final.py",
     "Schematic. No plotted value is derived from data."),
    ("Fig_02_phase_turning_manifold", "Figure 2",
     "Sensitivity-centred phase turning manifold; trajectory-relational geometry.",
     "phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.pdf",
     ["phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py"],
     "none — analytic construction", "",
     "Verified: the v8 script declares this exact stem. Superseded v4 and v7 "
     "scripts are retained under "
     "`02_CONTROLLED_STUDIES/06_Trajectory_Relational_Geometry/`, not here.",
     "python figure_source/phase_turning_manifold_sensitivity_centered_with_x2_purple_v8.py",
     "Analytic; values are computed by the script, not loaded."),
    ("Fig_04_task_contracts_representations", "Figure 4",
     "Task contracts and the mathematical representations they induce, one row.",
     "figure4_task_contracts_mathematical_representations_nature_one_row.pdf",
     ["figure4_task_contracts_mathematical_representations_nature_one_row.py"],
     "panel_data.py (module-level panel definitions)", "SIR-PENDULUM",
     "**Manual step recorded.** The script writes to `Pendulum/Plotter/figs`, which "
     "does not exist on disk; the asset lives in `Figures/figs`. The file was "
     "relocated by hand after generation.",
     "python figure_source/figure4_task_contracts_mathematical_representations_nature_one_row.py",
     "Panel values come from `panel_data.py`, bundled alongside."),
    ("Fig_05_lorenz_representation_landscape", "Figure 5",
     "Lorenz representation landscape: nested representation discovery under "
     "partial observation.",
     "figure5_lorenz_representation_landscape_final_tnr_v5_nature.pdf",
     ["figure5_lorenz_representation_landscape_final_tnr_v5_nature.py"],
     "figure_source_data/ — 10 frozen files from Lorenz/fig5data",
     "SIR-LORENZ-TASK-CONDITIONING",
     "Verified: the v5_nature script declares this exact stem. The v4 version and "
     "both prototypes are excluded from this folder and recorded in "
     "`90_AUDIT_REPORTS/excluded_files.csv`.",
     "python figure_source/figure5_lorenz_representation_landscape_final_tnr_v5_nature.py",
     "Plotted values are read from the frozen fig5data package; "
     "`PROVENANCE_MANIFEST.json` there records their origin."),
    ("Fig_06_d3d_task_conditioned_4panel", "Figure 6",
     "DIII-D task-conditioned relational discovery: descriptive organization and "
     "coefficient heterogeneity (q_desc, panels a-b); support plurality across six "
     "folds and target-cross-fitted reconstruction (q_rec, panels c-d).",
     "d3d_task_conditioned_4panel_v5.pdf",
     ["d3d_task_conditioned_4panel_v5.py"],
     "figure_source_data/ — 11 frozen files from DIIID_example/fig6data",
     "D3D-SIR-62-ALIGNED-V1 (a-b) + D3D-SIR-S7.E2.1-...-V1 (c-d)",
     "Verified. The script carries a preflight check for all 10 required inputs and "
     "an optional cross-check of its own 6x35 fold-support matrix against the "
     "pre-derived `panel2_fold_support_matrix.csv`.",
     "python figure_source/d3d_task_conditioned_4panel_v5.py --data-dir figure_source_data",
     "Panel a-b: discharge-specific coefficients and REML heterogeneity, exact. "
     "Panel c: binary support membership, exact. Panel d: per-discharge NRMSE, "
     "exact. No value is transformed for display beyond axis scaling."),
]
for folder, num, cap, asset, scripts, data, run, note, cmd, exact in FIGS:
    w(f"06_PAPER_FIGURES_ONLY/{folder}/README.md", f"""
# {num}

{cap}

| | |
|---|---|
| manuscript figure | **{num}** |
| final asset | `{asset}` |
| generation script | {' · '.join('`%s`' % s for s in scripts)} |
| input data | {data} |
| source run | {run or '—'} |
| regenerate | `{cmd}` |
| expected output | `{asset}` (plus .svg/.png where the script emits them) |

## Provenance note

{note}

## Are the plotted values exact?

{exact}

## Files here

- the final asset(s) as embedded in the manuscript
- `figure_source/` — the generation script(s), copied verbatim
- `figure_source_data/` — frozen inputs, where the figure has any
- original absolute paths for all of the above are in
  `00_START_HERE/PACKAGE_MANIFEST.csv`
""")

w("06_PAPER_FIGURES_ONLY/Supplementary_Figures/FigS1_coefficient_conditioning/README.md", """
# Supplementary Figure S1 — coefficient conditioning

Three panels assembled into one Supplement figure, all from the corrected
coefficient-conditioning audit.

| | |
|---|---|
| panel a | `d3d_coefficient_change_vs_rank_removed.pdf` — relative coefficient change and absolute RMSE change after removing the weakest singular directions |
| panel b | `d3d_heterogeneity_interval_by_coefficient.pdf` — REML between-discharge variance with profile-likelihood intervals |
| panel c | `d3d_multivariate_eigenvalue_uncertainty.pdf` — ordered eigenvalues of Σ_B − Σ_W with bootstrap intervals and matched-null thresholds |
| run | `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1` |
| script | `figure_source/generate_correction_figures.py` |
| inputs | `04_DIII_D_DESCRIPTIVE/.../Correction_audit/outputs` and `/tables` |

## Assembly

The three panels are separate PDFs; composition into a single figure happens in
the manuscript, not in the script. **That is a manual step.**

## Note on file variants

Only the `d3d_`-prefixed **PDF** assets exist. PNG and SVG variants exist under
the un-prefixed names (`coefficient_change_vs_rank_removed.png`, etc.), and the
Correction_audit manifest additionally lists three un-prefixed PDFs that are
absent — 74 of its 77 entries reproduce. Recorded in
`90_AUDIT_REPORTS/missing_artifacts.csv`. No numerical result is affected.

## Canonical, not superseded

These panels come from the **Correction_audit**, whose verdict is
`D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`. The original audit in the parent
directory carried the retired verdict `D3D-COEFFICIENT-FAMILY-RESOLVED` and
mislabelled profile-ML as REML. Do not plot from the original.
""")

# ==================================================== manuscript inventory
ms = PKG / "01_MANUSCRIPT_SNAPSHOT" / "main_manuscript" / "SIR_paper_2026-09-02.pdf"
inv = {"record_id": "SIR_MANUSCRIPT_INVENTORY_V1", "generated_utc": NOW,
       "manuscript_artifact": str(ms.relative_to(PKG)),
       "sha256": sha256(ms), "pages": 64,
       "tex_source_found": False, "supplement_tex_source_found": False,
       "releasepending_placeholders_found": 0,
       "parse_status": "PARTIAL_PDF_TEXT_LAYER_ONLY",
       "parse_limitation":
           "No TeX exists for the main manuscript or the Supplement anywhere under "
           "D:/SIR_paper. Sections, figure environments, \\includegraphics calls, "
           "table environments and \\releasepending placeholders therefore could not "
           "be extracted. Everything below was read from the PDF text layer.",
       "staleness_evidence": {"REL10": 16, "141 relational": 4, "cross-fitted": 0,
                              "3451_or_3,451": 0, "releasepending": 0,
                              "reading": "reports the RETIRED I_p reconstruction "
                                         "branch; predates all five current "
                                         "main-text figure assets"},
       "structure_from_text_layer": {
           "results_sections": ["1.1 From Scientific Objects to Qualified "
                                "Representations", "1.2 Object-adapted Coordinates",
                                "1.3 Controlled Studies", "1.4 Conventional Model "
                                "Identification", "1.5 Multimodal Plasma "
                                "Observations"],
           "discussion": True, "methods": True,
           "supplementary_notes": ["S1 Formal structure", "S2 Observational objects",
                                   "S3 Computational construction and search",
                                   "S4 Trajectory-relational coordinates",
                                   "S5 Representational equivalence",
                                   "S6 Controlled-study analyses",
                                   "S7 DIII-D construction, fitting and validation",
                                   "S8 Provenance and prospective search"],
           "note": "Main text and Supplement are ONE PDF; there is no separate "
                   "Supplement document."},
       "figure_allow_list_derivation":
           "Derived from on-disk assets and verified by tracing each candidate "
           "script's declared output STEM, because \\includegraphics could not be "
           "parsed. See 06_PAPER_FIGURES_ONLY/README.md."}
(PKG / "01_MANUSCRIPT_SNAPSHOT" / "manuscript_inventory.json").write_text(
    json.dumps(inv, indent=1), encoding="utf-8")
print("   01_MANUSCRIPT_SNAPSHOT/manuscript_inventory.json")

with open(PKG / "01_MANUSCRIPT_SNAPSHOT" / "release_pending_inventory.csv", "w",
          newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    wr.writerow(["placeholder", "count", "status", "note"])
    wr.writerow(["\\releasepending{...}", 0, "NONE_FOUND",
                 "No literal placeholder exists anywhere under D:/SIR_paper. The "
                 "equivalent gaps were identified by comparing the staged manuscript "
                 "against the canonical artifacts and are listed in "
                 "90_AUDIT_REPORTS/unresolved_release_fields.csv (17 entries)."])
print("   01_MANUSCRIPT_SNAPSHOT/release_pending_inventory.csv")

# ==================================================== environment
try:
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                            capture_output=True, text=True, timeout=180).stdout
except Exception as e:
    freeze = "# pip freeze unavailable: %s\n" % e
w("09_REPRODUCIBILITY/environment/requirements_frozen.txt", freeze)

mods = {}
for m in ("numpy", "pandas", "scipy", "matplotlib", "sklearn", "pyarrow", "pypdf"):
    try:
        mods[m] = getattr(__import__(m), "__version__", "unknown")
    except Exception:
        mods[m] = "absent"
(PKG / "09_REPRODUCIBILITY" / "environment" / "environment.json").write_text(
    json.dumps({"record_id": "SIR_ENVIRONMENT_V1", "captured_utc": NOW,
                "python": sys.version.split()[0], "executable": sys.executable,
                "platform": platform.platform(), "packages": mods,
                "note": "Captured from the working virtual environment at "
                        "D:/SIR_paper/.venv_lorenz_benchmark. No environment.yml or "
                        "requirements.txt existed in the repository; this file and "
                        "requirements_frozen.txt were generated, not copied."},
               indent=1), encoding="utf-8")
print("   09_REPRODUCIBILITY/environment/environment.json")

w("09_REPRODUCIBILITY/environment/environment.yml", f"""
# Generated {STAMP} from the working virtual environment.
# No environment.yml existed in the repository; this is a convenience export.
name: sir-paper
channels: [conda-forge]
dependencies:
  - python={sys.version.split()[0]}
  - numpy={mods.get('numpy')}
  - pandas={mods.get('pandas')}
  - scipy={mods.get('scipy')}
  - matplotlib={mods.get('matplotlib')}
  - scikit-learn={mods.get('sklearn')}
  - pyarrow={mods.get('pyarrow')}
  - pip
  - pip:
    - pypdf=={mods.get('pypdf')}
""")

for s in ("build_paper_data.py", "build_paper_data_docs.py",
          "build_paper_data_audit.py", "build_paper_data_readmes.py",
          "build_paper_data_repro.py"):
    src = ROOT / s
    if src.exists():
        dst = PKG / "09_REPRODUCIBILITY" / "build_scripts" / s
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
print("   09_REPRODUCIBILITY/build_scripts/ (5 scripts)")

w("09_REPRODUCIBILITY/RUN_ME_FIRST.md", f"""
# Reproduction guide

Everything below runs offline against the bundled artifacts.

## 0. Verify the package before trusting it

```
python 09_REPRODUCIBILITY/validation_scripts/verify_paper_data.py
```

Recomputes every SHA-256 against `00_START_HERE/PACKAGE_MANIFEST.csv`, checks
figure allow-list compliance, confirms no manifest source path points inside
`Paper_Data`, and re-derives the headline numbers from the artifacts. Exit code 0
means the package is internally consistent.

## 1. Environment

| | |
|---|---|
| Python | {sys.version.split()[0]} |
| numpy / pandas / scipy | {mods.get('numpy')} / {mods.get('pandas')} / {mods.get('scipy')} |
| matplotlib / scikit-learn | {mods.get('matplotlib')} / {mods.get('sklearn')} |
| platform | {platform.platform()} |

`environment/requirements_frozen.txt` is a full `pip freeze`;
`environment/environment.yml` is a convenience conda export. Neither existed in
the repository — both were generated here.

**Version sensitivity.** The DIII-D utility uses exact-equality comparisons on
fit scores, so a different BLAS or numpy build could in principle change a
selected support. Reproduce in the environment above for bit-identical results.

## 2. What you can reproduce, in increasing cost

### Free — read the frozen results
Every number in the paper is already in a machine-readable artifact. Start from
`00_START_HERE/CLAIM_TO_ARTIFACT_INDEX.csv`.

### Seconds — re-verify the DIII-D reconstruction lineage
```
python 05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/audit_s7.py
```
Checks 527 frozen artifacts across 21 stages and recomputes the headline metrics.

### Minutes — regenerate the paper figures
```
python 06_PAPER_FIGURES_ONLY/Fig_06_d3d_task_conditioned_4panel/figure_source/d3d_task_conditioned_4panel_v5.py --data-dir ../figure_source_data
python 06_PAPER_FIGURES_ONLY/Fig_05_lorenz_representation_landscape/figure_source/figure5_lorenz_representation_landscape_final_tnr_v5_nature.py
```
Each figure folder's README gives its exact command.

### Minutes — independent recomputations of the DIII-D contract
```
python 05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/_audit/verify_range_support.py out.json
python 05_DIII_D_RECONSTRUCTION/18_Machine_Readable_Lineage/_audit/verify_target_ancestry.py table.csv summary.json
```
These re-implement the range-support predicate from the frozen policy equation
and re-run the target-ancestry test. **They need the restricted source archive**
(see §4).

### Longer — controlled studies
Each study folder carries its own scripts, config and README. The Lorenz
benchmarks reproduce from `benchmark_config.yaml` plus `scripts/`.

## 3. Dependency order

```
03_DIII_D_SOURCE_OBJECT      (object, units, provenance)
        |
        +--> 04_DIII_D_DESCRIPTIVE      (q_desc: aligned run -> coefficients -> audits)
        |
        +--> 05_DIII_D_RECONSTRUCTION   (q_rec: contract -> ontology -> search ->
                                         FAILURE -> diagnosis -> revision ->
                                         cross-fitting -> Q_rec*)
                    |
                    +--> 06_PAPER_FIGURES_ONLY / 07_TABLES_AND_REPORTED_NUMBERS

02_CONTROLLED_STUDIES is independent of the DIII-D branches.
```

## 4. What you cannot rerun from this package alone

The 62 DIII-D `.npz` archives are **not bundled** (see
`00_START_HERE/ACCESS_AND_LICENSE.md`). Anything that reads raw signals —
re-running the search from scratch, or the two independent recomputations above —
needs authorised access to the archive. Their SHA-256 values are in
`03_DIII_D_SOURCE_OBJECT/source_access_notes/RESTRICTED_SOURCE_INDEX.csv` so you
can confirm you hold identical bytes.

Everything downstream of the aligned exports reproduces from what is here.

## 5. Rebuilding this package

```
python build_paper_data.py          # copy artifacts, write manifest + checksums
python build_paper_data_docs.py     # indexes and claim ledger
python build_paper_data_audit.py    # audit reports
python build_paper_data_readmes.py  # READMEs
python build_paper_data_repro.py    # figure READMEs, environment, this file
```

Copies from the canonical sources in `D:\\SIR_paper\\` and the external DIII-D
tree. Non-destructive: nothing outside `Paper_Data` is written.
""")
print("done")
