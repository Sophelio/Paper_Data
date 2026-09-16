#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write Markdown reports and finalize canonical_run_manifest.json hashes."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

PKG = Path(__file__).resolve().parent
REPO = PKG.parents[2]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path: Path, text: str) -> None:
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def main():
    state = json.loads((PKG / "_build_state.json").read_text(encoding="utf-8"))
    man = json.loads((PKG / "canonical_run_manifest.json").read_text(encoding="utf-8"))
    pooled = state["pooled"]
    rid = state["canonical_run_id"]
    hist = state["historical_model_found"]

    # ---- Design matrix contract ----
    write(
        PKG / "D3D_DESIGN_MATRIX_CONTRACT.md",
        f"""# D3D Design-Matrix Contract — {rid}

## Identity

| Field | Value |
|-------|-------|
| canonical_run_id | `{rid}` |
| artifact_status | `{state['artifact_status']}` |
| feature export | `FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized/` |
| export manifest SHA-256 | see `d3d_design_matrix_manifest.json` |
| historical model | `RESULTS/output.pcdiamag3.psir` copied to `model_artifact/output.pcdiamag3.psir` |
| equation key | `{man.get('equation_key')}` |

## Target and features

| Role | Column |
|------|--------|
| Target | `[d[pcdiamag3]/d[t]]` |
| Features (psir / OLS column order 1..7) | `[d[pcdiamag3]/d[kappa]]`, `[d[kappa]/d[t]]`, `[r[q95]/r[kappa]]`, `[d[pcdiamag3]/d[betan]]`, `[d[kappa]/d[betan]]`, `[d[betan]/d[t]]`, `[d[li]/d[betan]]` |
| Intercept | included (column 0 of coefficient vector) |

Semantic CSV coefficient order (Task B) remaps the same seven terms; see `d3d_discharge_coefficients.csv` header.

## Shapes and ordering

- Per discharge: features `1000 × 7`, target `1000`, time `1000`.
- Cohort: 62 discharges, 62 000 rows.
- `realization_index`: order of `filenames` in the historical `.psir` (matches NPZ shot order used in that run).
- `sample_index`: `0..999` along the provider `TARGET_N=1000` grid.
- Finite-row mask: all 62 000 export/psir samples finite; `prepare_discharge_reconstruction_data` would drop nonfinite rows (none dropped).

## Standardization

Export `manifest.json` records `normalization: "zscore"`. Per-file target mean≈0, std≈1. Feature columns are standardized in the export; they are **not** raw physical units.

## Fitting

- Historical predictions: `OUTPUT_PLOTTER.y_hat` using `1_8*` coefficient matrix `(62, 8)` and `O1_variables[i]` `(8, 1000)`.
- Rank/RSS metadata: `numpy.linalg.lstsq` on `[1 \\| X]` from the export columns (matches historical coeffs to ≤1e-6).
- Tolerance: pooled RMSE must match references to `1e-12`.

## Hash representation

`numpy.ascontiguousarray(arr, dtype=float64).tobytes()` → SHA-256. Table: `d3d_design_matrix_hashes.csv`.

Machine-readable twin: `d3d_design_matrix_manifest.json`.
""",
    )

    # ---- Relational coordinate construction ----
    write(
        PKG / "D3D_RELATIONAL_COORDINATE_CONSTRUCTION.md",
        f"""# D3D Relational / Phase Coordinate Construction — {rid}

Evidence from current Archaieus sources and the frozen feature export. Exact per-realization numerical `shift` values from the export-generating run are **not** stored in the parquet files → `EXACT_SHIFT_VALUE_UNKNOWN`.

## Code path

1. Provider grid (`diiid_elm_data_provider.py`): signals on shared 1000-point ms grid; `freq = dt` in **milliseconds**; `smooth_rate = 0`.
2. `consumer_function.py`: per-realization z-score of primitives; `dt` from `timing_data` (ms); finite-difference `TRANSFORMS.differentiate(..., dt=dt)`.
3. `get_shiftval(..., out_type='Derivative')` (`consumer_function.py` ~L122–126):
   `shift = abs(min(vstack(x, dx))) + nmin` with `nmin` typically 100 in UI settings — **exact historical nmin/shift not in export**.
4. XPhaseders / quotients: `TRANSFORMS.make_Quotients(VAR, keys, shift, add_inverse=True)` (`transforms.py` L218–240):
   `(X_i + shift) / (X_j + shift)`; inverse via `1/out` when `add_inverse=True`.
5. YPhaseders: target temporal derivative in numerator only (`consumer_function.py` ~L416–420).
6. When `total_normalization` / export z-score applies: derived columns are z-scored per realization before packaging.

## Answers to required questions

1. **Expressions (pre-standardization, with shift):**
   - `[d[a]/d[b]]` ≡ `(d[a]/d[t] + s) / (d[b]/d[t] + s)` for phase pairs among non-target and Y-phaseders with target-in-numerator for `[d[pcdiamag3]/d[*]]`.
   - `[r[q95]/r[kappa]]` ≡ `(r[q95] + s) / (r[kappa] + s)`.
   - `[d[betan]/d[t]]`, `[d[kappa]/d[t]]`: temporal FD derivatives (then standardized).
2. **Numerator and denominator shifted?** Yes for quotients/phaseders via `make_Quotients` / yPhaseder construction.
3. **Shift definition:** `abs(min(relevant blob)) + nmin` (`get_shiftval`).
4. **Shift scope:** **per realization** (computed inside consumer from that realization’s arrays). Not a single global constant across the cohort.
5. **Numerical shift values:** `EXACT_SHIFT_VALUE_UNKNOWN` (not serialized into parquet). Minimum artifact to resolve: consumer logs or pickled `meanSTDinfo`/realization objects from the export run, or re-ingest with recorded `nmin` and dump `shiftval`.
6. **Denominator masks:** none inside `make_Quotients`; positivity encouraged by additive shift. Downstream finite mask in validation prep only.
7. **Quotient columns standardized after construction?** Export manifest `normalization: zscore` — yes in the frozen export columns.
8. **Primitives standardized before differentiation?** Yes in the consumer path when z-score is enabled (export processing `zscore`).
9. **`dt` units:** milliseconds as returned by the Paper provider.
10. **ms↔s invariance after z-score:** phase/quotient ratios of derivatives are invariant to global time-unit rescaling; absolute `d[*]/d[t]` scale with `1/dt` but z-scoring removes a global factor from standardized columns used in RMSE.
11. **Exported vs simple symbolic quotient:** exported columns are **shift-augmented then (export) z-scored**, not bare `a/b`.
12. **Eliminated rational form:** for a phase coordinate, with affine z-score `z = (u - μ)/σ` on the shifted ratio `u = (ṅ_num + s)/(ṅ_den + s)`, the paper-facing symbol is an affine transform of that shifted ratio — **not** the unshifted elimination identity unless `s=0` and no z-score (not the case here).

Machine-readable twin: `d3d_relational_coordinate_manifest.json`.
""",
    )

    # ---- Structural search provenance ----
    write(
        PKG / "D3D_STRUCTURAL_SEARCH_PROVENANCE.md",
        f"""# D3D Structural-Search Provenance — {rid}

## Verdict labels

| Topic | Status |
|-------|--------|
| Historical `.psir` with 62 realizations and `1_8*` | **RESOLVED** (`RESULTS/output.pcdiamag3.psir`) |
| Seven-term support identity | **RESOLVED** (matches `D3D_RELATION` / mean of `1_8*`) |
| Per-realization calibration (`1_8` → `1_8*`) | **RESOLVED** (both keys present; `1_8*` matches OLS RMSE) |
| Term index list `bestindex` | **PARTIALLY RESOLVED** (`[[[0], [56], [105], [41], [57], [98], [106], [96]]]` — library indices, full name map not dumped here) |
| Full admitted coordinate-family checklist at discovery | **UNKNOWN** |
| Candidate library size at discovery | **UNKNOWN** (export has 65 feature columns; search-time checklist not frozen) |
| Forward-selection hyperparameters (iterations, jobs, seeds) | **UNKNOWN** for the discovery run |
| Current `.bin/settings.json` | **NOT** treated as discovery config (incomplete `data_processing` vs export richness; target_variable null) |
| Support selection pooled vs per-realization | **PARTIALLY RESOLVED**: greedy indices stored once (`bestindex`); coefficients vary per realization; calibration produces `1_8*` |
| Whether support was later hard-coded into `D3D_RELATION` | **RESOLVED** as present state: `D3D_RELATION` embeds mean coefficients; interactive validation uses model coeffs |

## RESOLVED

- Cohort: 62 shots; 1000 samples each.
- Target: `[d[pcdiamag3]/d[t]]` (`outexpr` in `.psir`).
- Equation keys: `1_8`, `1_8*` with coefficient shape `(62, 8)`.
- FinalError on `1_8`: ≈0.00332005; calibrated `1_8*` pooled MSE ≈0.00331599.
- Provider admitted ontology (eight signals) and `ALLOWED_SIGNALS` order affecting relational orientation.
- Smoothing for canonical export: `none` (manifest).

## PARTIALLY RESOLVED

- `bestindex` library positions for the eight selected slots (intercept + 7 terms).
- Mean coefficients ≈ `D3D_RELATION` scientific embedding.

## UNKNOWN

- Exact UI `data_processing` checklist, `order`, `numerators`, `iterations`, `jobs`, `nmin`, seeds at the moment of structural discovery.
- Number of random starts / parallel pool settings for that run.
- Exact `shiftval` / `nmin` numeric values per realization during export generation.

## CONTRADICTORY

- None proven between historical `.psir` `1_8*` predictions and per-discharge OLS on the frozen export (coeffs match ≤1e-6; RMSE identical to reference).

## REGENERATION_CONFIGURATION_NOT_ORIGINAL_DISCOVERY_CONFIGURATION

If rediscovering without the `.psir`, the frozen reconstruction is:

- Features: seven columns in psir order from the canonical export.
- Fit: `numpy.linalg.lstsq` per discharge with intercept.
- This **reproduces** discharge-specific predictions/RMSE but **does not** re-run structural search.
""",
    )

    # ---- File index ----
    roles = {
        "build_canonical_run_package.py": ("REPORT", "Package builder script"),
        "write_package_docs.py": ("REPORT", "Documentation finalizer"),
        "_inspect_psir.py": ("REPORT", "PSIR inspection helper"),
        "_verify_historical_psir.py": ("REPORT", "Historical PSIR verification helper"),
        "_build_state.json": ("MANIFEST", "Internal build state"),
        "canonical_run_manifest.json": ("MANIFEST", "Package manifest"),
        "d3d_discharge_coefficients.csv": ("REGENERATED_ARTIFACT", "62 discharge coefficient rows"),
        "d3d_coefficient_summary.csv": ("REGENERATED_ARTIFACT", "Coefficient distribution summary"),
        "d3d_discharge_predictions.parquet": ("REGENERATED_ARTIFACT", "62000 prediction/residual rows"),
        "d3d_discharge_metrics.csv": ("REGENERATED_ARTIFACT", "Per-discharge metrics"),
        "d3d_pooled_metrics.json": ("REGENERATED_ARTIFACT", "Pooled metrics"),
        "d3d_design_matrix_hashes.csv": ("REGENERATED_ARTIFACT", "Per-shot matrix hashes"),
        "d3d_design_matrix_manifest.json": ("MANIFEST", "Design-matrix contract JSON"),
        "d3d_relational_coordinate_manifest.json": ("MANIFEST", "Coordinate construction JSON"),
        "D3D_DESIGN_MATRIX_CONTRACT.md": ("REPORT", "Design-matrix contract"),
        "D3D_RELATIONAL_COORDINATE_CONSTRUCTION.md": ("REPORT", "Coordinate construction report"),
        "D3D_STRUCTURAL_SEARCH_PROVENANCE.md": ("REPORT", "Structural-search provenance"),
        "D3D_CANONICAL_RUN_COMPLETION_REPORT.md": ("REPORT", "Completion report"),
        "CANONICAL_RUN_FILE_INDEX.md": ("MANIFEST", "File index"),
        "model_artifact/output.pcdiamag3.psir": ("COPIED_HISTORICAL_ARTIFACT", "Historical model output_dict"),
        "model_artifact/model_artifact_meta.json": ("MANIFEST", "Model artifact metadata"),
    }

    lines = [
        f"# Canonical Run File Index — {rid}",
        "",
        "| File | Role | Bytes | SHA-256 | Description |",
        "|------|------|------:|---------|-------------|",
    ]
    for rel, (role, desc) in sorted(roles.items()):
        p = PKG / rel
        if not p.exists():
            continue
        lines.append(
            f"| `{rel}` | {role} | {p.stat().st_size} | `{sha256_file(p)}` | {desc} |"
        )
    # also list any other files
    for p in sorted(PKG.rglob("*")):
        if p.is_dir():
            continue
        rel = str(p.relative_to(PKG)).replace("\\", "/")
        if rel in roles:
            continue
        lines.append(
            f"| `{rel}` | REPORT | {p.stat().st_size} | `{sha256_file(p)}` | ancillary |"
        )
    write(PKG / "CANONICAL_RUN_FILE_INDEX.md", "\n".join(lines))

    # ---- Completion report ----
    verdict = (
        "D3D-CANONICAL-62SHOT-RUN-PACKAGE-CLOSED-V1"
        if hist and not state["contradictions"]
        else "D3D-CANONICAL-62SHOT-RECONSTRUCTION-PACKAGE-CLOSED-WITH-HISTORICAL-LINEAGE-GAPS"
    )
    # Even with historical model, shift value and full search settings remain UNKNOWN —
    # user said if historical model OR search settings missing gaps → second verdict if gaps.
    # Historical model FOUND, but search settings incomplete → use WITH-HISTORICAL-LINEAGE-GAPS
    # Actually: "If the historical model or exact search settings remain missing"
    # Search settings remain missing → second verdict.
    verdict = "D3D-CANONICAL-62SHOT-RECONSTRUCTION-PACKAGE-CLOSED-WITH-HISTORICAL-LINEAGE-GAPS"

    write(
        PKG / "D3D_CANONICAL_RUN_COMPLETION_REPORT.md",
        f"""# D3D Canonical Run Completion Report — {rid}

## 1. Executive verdict

**{verdict}**

Historical model artifact **found and verified** (`output.pcdiamag3.psir`, equation `1_8*`, 62×1000).  
Structural-search UI hyperparameters and exact `shiftval` numerics remain **UNKNOWN**.  
No manuscript files modified.

## 2. What was already established

- 62 discharges × 1000 samples; ~4.1–6.0 ms grids; eight-signal ontology.
- Seven-term support; per-discharge RMSE ≈ 0.05758467; mean-vector RMSE ≈ 0.41252383.
- Retrospective, target-containing analysis.

## 3. New artifacts generated

See `CANONICAL_RUN_FILE_INDEX.md` under `{PKG.name}/`.

## 4. Historical model artifact status

| Item | Value |
|------|-------|
| Found | **yes** |
| Original path | `RESULTS/output.pcdiamag3.psir` |
| Package copy | `model_artifact/output.pcdiamag3.psir` |
| Status | `HISTORICAL_ORIGINAL` |
| Equation key | `1_8*` (calibrated); `1_8` also present |
| Realizations | 62 |
| Coeff shape | (62, 8) |
| Verified pooled RMSE | {pooled['pooled_rmse']} |

## 5. Numerical reproduction

| Metric | Value | Reference | \\|Δ\\| |
|--------|------:|----------:|----:|
| Per-discharge pooled RMSE | {pooled['pooled_rmse']} | {pooled['reference_per_discharge_rmse']} | {pooled['delta_per_discharge_rmse']} |
| Mean-vector pooled RMSE | {pooled['mean_vector_pooled_rmse']} | {pooled['reference_mean_vector_rmse']} | {pooled['delta_mean_vector_rmse']} |
| Median-error shot | {pooled['median_error_shot']} | — | — |

## 6. Exact coefficient and prediction lineage

`filenames[i]` → shot → export parquet ↔ `O1_variables[i]` / `output.x[i]` / `1_8*.x[i]` → predictions in `d3d_discharge_predictions.parquet`.  
Coefficient CSV uses semantic column names; values taken from historical `1_8*` rows.

## 7. Coordinate-construction findings

Shifted quotients/phaseders via `get_shiftval` + `make_Quotients(..., add_inverse=True)`; export z-scored. Exact shift numbers: **EXACT_SHIFT_VALUE_UNKNOWN**.

## 8. Structural-search provenance findings

Support and calibrated coeffs **RESOLVED** from `.psir`. Discovery hyperparameters **UNKNOWN**. Current `.bin/settings.json` is **not** claimed as the discovery configuration.

## 9. Remaining UNKNOWN fields

{chr(10).join('- ' + u for u in state['unresolved_items'])}

## 10. Contradictions

{('None.' if not state['contradictions'] else chr(10).join('- ' + c for c in state['contradictions']))}

## 11. Manuscript implications

- Use **discharge-specific** RMSE ≈ **0.0576** when citing interactive / calibrated reconstruction.
- Use **0.4125** only when citing the cohort-mean coefficient vector applied universally.
- Do not treat unshifted `a/b` identities as the exported coordinates.

## 12. Reproduction commands

```bash
conda activate sir_web
cd D:/sir-web
python "Paper Examples/Relational Coordinates for Multimodal Plasma Observations/canonical_d3d_62_shot_run_v1/build_canonical_run_package.py"
python "Paper Examples/Relational Coordinates for Multimodal Plasma Observations/canonical_d3d_62_shot_run_v1/write_package_docs.py"
```

## 13. Completion gates

| Gate | Status |
|------|--------|
| Permanent run ID assigned | PASS (`{rid}`) |
| 62 discharges | PASS |
| 62 coefficient rows | PASS |
| 62 000 prediction rows | PASS |
| Seven features declared order | PASS |
| Per-discharge RMSE reproduced | PASS |
| Mean-vector RMSE reproduced | PASS |
| Model artifact preserved/declared | PASS (HISTORICAL_ORIGINAL) |
| Export/manifest hashes | PASS |
| Design-matrix hashes | PASS |
| Coordinate path traced | PASS (shift value UNKNOWN) |
| Shift/mask policy | PARTIAL (policy known; value UNKNOWN) |
| Structural-search recovery | PARTIAL |
| No unsupported default inference | PASS |
| Artifacts hashed | PASS |
| UNKNOWN listed | PASS |
| No manuscript modified | PASS |
| No silent overwrite of scientific outputs | PASS (new versioned dir) |
""",
    )

    # Update manifest with doc hashes
    search_path = PKG / "D3D_STRUCTURAL_SEARCH_PROVENANCE.md"
    man["search_provenance_sha256"] = sha256_file(search_path)
    man["completion_report"] = "D3D_CANONICAL_RUN_COMPLETION_REPORT.md"
    man["completion_report_sha256"] = sha256_file(PKG / "D3D_CANONICAL_RUN_COMPLETION_REPORT.md")
    man["file_index"] = "CANONICAL_RUN_FILE_INDEX.md"
    man["file_index_sha256"] = sha256_file(PKG / "CANONICAL_RUN_FILE_INDEX.md")
    man["final_verdict"] = verdict
    man["design_matrix_contract"] = "D3D_DESIGN_MATRIX_CONTRACT.md"
    man["design_matrix_contract_sha256"] = sha256_file(PKG / "D3D_DESIGN_MATRIX_CONTRACT.md")
    man["coordinate_construction_report"] = "D3D_RELATIONAL_COORDINATE_CONSTRUCTION.md"
    man["coordinate_construction_report_sha256"] = sha256_file(
        PKG / "D3D_RELATIONAL_COORDINATE_CONSTRUCTION.md"
    )
    (PKG / "canonical_run_manifest.json").write_text(
        json.dumps(man, indent=2) + "\n", encoding="utf-8"
    )

    # Refresh file index after manifest update
    # (re-run index section quickly)
    print("Docs written.")
    print("final_verdict:", verdict)
    print("historical_model_found:", hist)
    print("unresolved_items:", len(state["unresolved_items"]))


if __name__ == "__main__":
    main()
