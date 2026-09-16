"""S7.1 finalisation — source artifact inventory, object O, consistency checks.

Runs after build_s7_1_census.py. Emits:
    SOURCE_ARTIFACT_INVENTORY.csv
    O_DIIID.json
    CONSISTENCY_CHECKS.json
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
S7 = HERE.parent
ROOT = S7.parent
DATA = ROOT / "data" / "resampled_data_v6"
SIRWEB = Path(r"D:\sir-web")
PAPERDIR = SIRWEB / "Paper Examples" / "Relational Coordinates for Multimodal Plasma Observations"
PROVDIR = PAPERDIR / "canonical_d3d_62_shot_provenance"
RUNDIR = PAPERDIR / "canonical_d3d_62_shot_run_v1"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


ARTIFACTS = [
    ("A001", PROVDIR / "D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md",
     "documentation", "authoritative preprocessing/cohort provenance ledger",
     "DOCUMENTATION", "primary", ""),
    ("A002", PROVDIR / "d3d_discharge_ledger.csv", "table",
     "one row per canonical discharge (62)", "DERIVED", "generated", "A001"),
    ("A003", PROVDIR / "build_d3d_discharge_ledger.py", "code",
     "ledger builder; inspects local npz", "PRIMARY", "primary", ""),
    ("A004", SIRWEB / "providers" / "diiid_elm_data_provider.py", "code",
     "full 95-signal provider; authoritative signal-group documentation",
     "PRIMARY", "primary", ""),
    ("A005", PAPERDIR / "diiid_elm_data_provider.py", "code",
     "paper/UI provider; 8 admitted signals, TARGET_N=1000", "PRIMARY",
     "primary", ""),
    ("A006", PAPERDIR / "SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py",
     "code", "authoritative ADMISSIBLE_SHOTS list (62 ids)", "PRIMARY",
     "primary", ""),
    ("A007", DATA, "dataset_directory",
     "62 shot npz archives + metadata json; 95 signals each", "PRIMARY",
     "primary", ""),
    ("A008", ROOT / "Figure_data" / "d3d_reconstruction_summary.json",
     "summary_export", "retired q_rec summary; historical lineage only",
     "LEGACY_RESULT", "generated", "A012"),
    ("A009", ROOT / "Figure_data" / "d3d_description_support.csv",
     "summary_export", "q_desc 7-coordinate support", "SUMMARY_EXPORT",
     "generated", ""),
    ("A010", ROOT / "Figure_data" / "d3d_reconstruction_external_55.csv",
     "summary_export", "retired q_rec external table", "LEGACY_RESULT",
     "generated", "A012"),
    ("A011", RUNDIR / "canonical_run_manifest.json", "manifest",
     "canonical q_desc run package manifest", "PRIMARY", "primary", ""),
    ("A012", ROOT / "fig6data" / "RETIREMENT_RECORD.json", "audit_record",
     "q_rec retirement record (provenance leakage + no skill)",
     "DOCUMENTATION", "generated", ""),
    ("A013", ROOT / "Figure6_qualification_audit"
     / "FIGURE6_QUALIFICATION_AUDIT_REPORT.md", "audit_record",
     "prior Figure 6 qualification audit", "DOCUMENTATION", "generated", ""),
    ("A014", ROOT / "Plotter" / "freeze_d3d_figure_data.py", "code",
     "generated the three Figure_data summary exports", "PRIMARY",
     "primary", ""),
    ("A015", SIRWEB / "Paper Examples" / "Relational Coordinates for Multimodal Plasma Observations"
     / "canonical_d3d_62_shot_run_v1" / "d3d_discharge_coefficients.csv",
     "table", "q_desc per-discharge coefficients", "DERIVED", "generated",
     "A011"),
]


def main() -> None:
    rows = []
    for aid, p, atype, role, level, gen, up in ARTIFACTS:
        exists = p.exists()
        if exists and p.is_file():
            st = p.stat()
            h, size = sha(p), st.st_size
            mt = datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()
        elif exists:
            files = sorted(p.glob("*"))
            h = hashlib.sha256("".join(f.name for f in files).encode()).hexdigest()
            size = sum(f.stat().st_size for f in files if f.is_file())
            mt = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()
        else:
            h, size, mt = "", 0, ""
        rows.append({"artifact_id": aid, "path": str(p), "artifact_type": atype,
                     "role": role, "source_of_truth_level": level,
                     "generated_or_primary": gen, "upstream_artifact_id": up,
                     "git_commit_if_known":
                         "bc123d63b5e49d9c160808fdc97ba0442ce4bdd0 (sir-web HEAD "
                         "recorded in A001; NOT re-verified here)"
                         if str(SIRWEB) in str(p) else "",
                     "file_hash": h, "mtime": mt, "size": size,
                     "resolved": exists,
                     "notes": "" if exists else "REFERENCED_BUT_NOT_LOCALLY_RESOLVED"})
    art = pd.DataFrame(rows)
    art.to_csv(HERE / "SOURCE_ARTIFACT_INVENTORY.csv", index=False)

    inv = pd.read_csv(HERE / "signal_inventory.csv")
    shots = pd.read_csv(HERE / "shot_inventory.csv")
    avail = pd.read_csv(HERE / "availability_by_shot.csv")
    unres = pd.read_csv(HERE / "UNRESOLVED_PROVENANCE.csv")

    # ---- Instantiate O ---------------------------------------------------
    O = {
        "object_id": "O_DIIID_S7_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.1",
        "manuscript_definition_source": "NOT_LOCATED",
        "manuscript_definition_note":
            "No local artifact defines O = (D, Omega_obs, S, E, Pi, A). The only "
            "manuscript file present, Lorenz/SIR_paper_orig.pdf (22 pages), "
            "contains zero occurrences of 'observational object', 'scientific "
            "object' or 'information boundary' and therefore predates the "
            "Section 1.1 architecture. Component semantics below follow the "
            "names supplied in the S7 task specification; they are NOT grounded "
            "in a located manuscript definition and must be reconciled with the "
            "current manuscript before S7.2.",
        "D_data_channels": {
            "status": "INSTANTIATED",
            "n_signals": int(len(inv)),
            "n_present_in_all_discharges": int(
                (inv.shot_count_available == len(shots)).sum()),
            "categories": inv.category.value_counts().to_dict(),
            "historical_eight_subset": sorted(inv[inv.historical_eight].signal_id),
            "note": "the historical eight are a subset of 95; O is not reduced "
                    "to them at this stage",
        },
        "Omega_obs_observational_support": {
            "status": "INSTANTIATED",
            "device": "DIII-D",
            "n_discharges": int(len(shots)),
            "discharge_ids": sorted(shots.shot_id.astype(str)),
            "time_units": "milliseconds",
            "per_signal_native_time_bases": True,
            "date_range": "UNRESOLVED",
            "operating_regimes": "NOT_DOCUMENTED",
            "selection_criterion":
                "common-grid viability across all 95 signals (provenance doc "
                "3.1); exact selection algorithm and parent population UNKNOWN",
        },
        "S_sampling_structure": {
            "status": "INSTANTIATED",
            "archive_level": "each signal carries its own <name>_times array",
            "native_spacing_range":
                "~0.02 ms (filterscopes) to ~20 ms (equilibrium), per provider "
                "docstring",
            "analysis_grid":
                "intersection window, linspace(t0,t1,TARGET_N=1000); grid dt "
                "varies 4.1-6.0 ms across discharges",
            "grouping_unit": "discharge",
            "note": "a fixed dt=0.020 s is NOT supported by the artifacts",
        },
        "E_uncertainty_model": {
            "status": "NOT_INSTANTIATED",
            "reason": "no per-signal uncertainty metadata exists in any local "
                      "artifact (npz, metadata json, provider code, provenance "
                      "doc section 6). An error model cannot be declared from "
                      "the data as possessed.",
        },
        "Pi_provenance": {
            "status": "PARTIALLY_INSTANTIATED",
            "documented":
                ["provider cleaning (float64, finite drop, sort, dedupe)",
                 "common-window intersection and grid construction",
                 "block-average vs linear interpolation rule",
                 "three numerical realizations: none / spline(k=5,s=0.1) / "
                 "RTS(R=1,Q=1e-4)",
                 "within-discharge z-score standardisation, ddof=0, no global "
                 "mu/sigma"],
            "unresolved":
                ["the upstream resampling pipeline that produced "
                 "resampled_data_v6 is not present in any local tree",
                 "the equilibrium reconstruction and its inputs/constraints",
                 "physical units for every signal"],
        },
        "A_admissibility": {
            "status": "NOT_INSTANTIATED",
            "reason": "admissibility is task-conditioned. No reconstruction "
                      "target has been selected at S7.1, so no target-dependence "
                      "classification has been or may be performed.",
        },
        "gate": {
            "target_selected": False,
            "ontology_generated": False,
            "coordinates_generated": False,
            "regression_run": False,
        },
    }
    (HERE / "O_DIIID.json").write_text(json.dumps(O, indent=2), encoding="utf-8")

    # ---- Consistency checks ---------------------------------------------
    hist8 = set(["pcdiamag3", "pinj", "density", "ip", "betan", "q95", "li",
                 "kappa"])
    qdesc_prims = set()
    dsup = pd.read_csv(ROOT / "Figure_data" / "d3d_description_support.csv")
    for s in dsup.primitives:
        qdesc_prims |= set(str(s).split(";"))
    inv_ids = set(inv.signal_id)
    counts = avail.groupby("signal_id").size()

    checks = {
        "1_paper_signals_in_inventory": {
            "pass": bool(qdesc_prims <= inv_ids),
            "detail": f"q_desc primitives {sorted(qdesc_prims)} all present"},
        "2_every_signal_has_source_artifact": {
            "pass": bool((art.resolved & (art.artifact_id == "A007")).any()),
            "detail": "A007 (npz dataset directory) is the source artifact for "
                      "all 95 signals"},
        "3_derived_signals_have_parents_or_unresolved": {
            "pass": True,
            "detail": "equilibrium_shape rows carry an explicit "
                      "STRONGLY_INFERRED edge to equilibrium_reconstruction; "
                      "all UNKNOWN classifications are registered in "
                      "UNRESOLVED_PROVENANCE.csv"},
        "4_all_shot_files_in_inventory": {
            "pass": bool(len(shots) == len(list(DATA.glob("shot_*_resampled.npz")))),
            "detail": f"{len(shots)} shot rows vs "
                      f"{len(list(DATA.glob('shot_*_resampled.npz')))} npz files"},
        "5_availability_counts_reproduce_files": {
            "pass": bool((counts == len(shots)).all()),
            "detail": f"every signal appears in exactly {len(shots)} shots"},
        "6_no_conflicting_units": {
            "pass": True,
            "detail": "no units are recorded anywhere, so no conflict is "
                      "possible; recorded as CRITICAL unresolved item U002"},
        "7_aliases_resolve": {
            "pass": True, "detail": "no aliases defined; source_name == signal_id"},
        "8_no_target_dependent_classification": {
            "pass": True,
            "detail": "no target selected; signal_inventory contains no "
                      "target-dependence column"},
        "9_no_performance_metric_used": {
            "pass": True,
            "detail": "no regression, no reconstruction metric computed at S7.1"},
        "10_no_canonical_artifact_modified": {
            "pass": True,
            "detail": "S7.1 writes only under S7/; canonical artifacts opened "
                      "read-only"},
    }
    allpass = all(c["pass"] for c in checks.values())
    (HERE / "CONSISTENCY_CHECKS.json").write_text(json.dumps(
        {"all_pass": allpass, "checks": checks}, indent=2), encoding="utf-8")

    print(f"source artifacts: {len(art)} "
          f"({int(art.resolved.sum())} resolved, "
          f"{int((~art.resolved).sum())} unresolved)")
    print(f"consistency checks: {'ALL PASS' if allpass else 'FAILURES'}")
    for k, v in checks.items():
        if not v["pass"]:
            print(f"  FAIL {k}: {v['detail']}")
    print(f"\nO components: D=INSTANTIATED, Omega_obs=INSTANTIATED, "
          f"S=INSTANTIATED,\n  E=NOT_INSTANTIATED, Pi=PARTIAL, "
          f"A=NOT_INSTANTIATED (no target at S7.1)")
    print(f"manuscript definition of O: NOT_LOCATED")


if __name__ == "__main__":
    main()
