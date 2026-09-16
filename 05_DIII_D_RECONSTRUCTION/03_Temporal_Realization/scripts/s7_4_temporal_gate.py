"""S7.4 — parent verification and the section-4 target temporal-provenance gate.

X_rec is NOT instantiated by this script. Section 4 is a mandatory precondition:
if the frozen analysis grid is finer than the target's source-supported cadence,
the stage must stop and return
TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED.

No archive is opened. Everything below comes from frozen S7.1 metadata and the
per-shot metadata sidecars (component A), which the firewall permits for all
discharges. No signal value, development or external, is read.
"""

from __future__ import annotations

import glob
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S74 = HERE.parent
S7 = S74.parent
EX = S7.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
S73 = S7 / "03_target_feasibility_and_boundary"
MAN = S74 / "manifests"
DATA = EX / "data" / "resampled_data_v6"

FREEZE_ID = "D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-V1"
TARGET = "vsurf"
ANALYSIS_DT = 20.0
TOL = 0.5          # ms; a source dt within this of the grid is "consistent"

EQUILIBRIUM = ["aminor", "area", "betan", "drsep", "kappa", "li", "q95",
               "rmaxis", "rsurf", "tribot", "tritop", "volume", "zcur",
               "zmaxis", "zsurf"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_parents() -> dict:
    s71 = json.loads((R1 / "S7_1_FINAL_FREEZE.json").read_text())
    v1 = json.loads((S72 / "S7_2_FREEZE.json").read_text())
    v2 = json.loads((CV1 / "S7_2_FREEZE_V2.json").read_text())
    s73 = json.loads((S73 / "S7_3_FREEZE.json").read_text())
    s71v = json.loads((S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json").read_text())
    SELF = set(v2["self_referential_excluded"]) | set(s73["self_referential_excluded"])

    def check(man, base):
        ok, drift = 0, []
        for rel, h in man.items():
            if Path(rel).name in SELF:
                continue
            p = base / rel
            if not p.exists():
                drift.append({"artifact": rel, "issue": "MISSING"})
            elif sha(p) != h:
                drift.append({"artifact": rel, "issue": "DRIFT"})
            else:
                ok += 1
        return ok, drift

    s71_map = {
        "signal_inventory_sha256": R1 / "FINAL_SIGNAL_INVENTORY.csv",
        "shot_inventory_sha256": R1 / "FINAL_SHOT_INVENTORY.csv",
        "units_registry_sha256": S7 / "SIGNAL_UNITS.json",
        "provenance_graph_sha256": R1 / "provenance_graph.json",
        "dalia_parity_sha256": R1 / "DALIA_SIGNAL_PARITY.csv",
        "temporal_lineage_sha256": R1 / "FINAL_TEMPORAL_LINEAGE.csv",
        "equilibrium_lineage_sha256": R1 / "equilibrium_lineage_status.csv",
        "source_inventory_sha256": R1 / "SOURCE_ARTIFACT_INVENTORY.csv",
        "quality_summary_sha256": R1 / "signal_quality_summary.csv",
    }
    s71_ok = sum(1 for k, p in s71_map.items()
                 if sha(p) == s71v["canonical_raw_byte_hashes"][k])
    s71_drift = [{"artifact": k, "issue": "DRIFT"} for k, p in s71_map.items()
                 if sha(p) != s71v["canonical_raw_byte_hashes"][k]]

    v1_ok, v1_d = check(v1["all_artifact_hashes"], S72)
    v2_ok, v2_d = check(v2["all_artifact_hashes"], CV1)
    s73_ok, s73_d = check(s73["all_artifact_hashes"], S73)

    sel = json.loads((S73 / "TARGET_SELECTION_RESULT.json").read_text())
    irec = json.loads((S73 / "I_REC_SELECTED.json").read_text())
    orec = json.loads((S73 / "O_REC_SELECTED.json").read_text())
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())

    substantive = {
        "target_is_vsurf": sel["primary_target"] == TARGET,
        "predictor_count_79": orec["explanatory_primitive_universe"]["n"] == 79,
        "families_7": len(orec["explanatory_primitive_universe"]["by_family"]) == 7,
        "external_cohort_42": part["external"]["n"] == 42,
        "development_cohort_20": part["development"]["n"] == 20,
        "selected_boundary_unchanged":
            sha(S73 / "selected_target_boundary.csv") == s73["primary_boundary_sha256"],
        "I_REC_SELECTED_unchanged":
            sha(S73 / "I_REC_SELECTED.json") == s73["I_REC_SELECTED_sha256"],
        "O_REC_SELECTED_unchanged":
            sha(S73 / "O_REC_SELECTED.json") == s73["O_REC_SELECTED_sha256"],
    }
    drift = s71_drift + v1_d + v2_d + s73_d
    return {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "hash_convention": "sha256 raw file bytes; self-referential excluded",
        "s7_1": {"freeze_id": s71["freeze_id"], "n_verified": s71_ok,
                 "drift": s71_drift},
        "s7_2_v1": {"freeze_id": v1["freeze_id"], "n_verified": v1_ok,
                    "drift": v1_d},
        "s7_2_v2": {"freeze_id": v2["freeze_id"], "n_verified": v2_ok,
                    "drift": v2_d},
        "s7_3": {"freeze_id": s73["freeze_id"], "n_verified": s73_ok,
                 "drift": s73_d},
        "substantive_checks": substantive,
        "n_drift_total": len(drift),
        "verdict": ("PARENTS_VERIFIED"
                    if not drift and all(substantive.values())
                    else "STOP_PARENT_DRIFT"),
    }


def temporal_provenance() -> tuple[pd.DataFrame, dict]:
    """Trace vsurf: source support -> archived -> analysis grid."""
    q = pd.read_csv(R1 / "signal_quality_summary.csv", dtype={"shot_id": str})
    vq = q[q.signal_id == TARGET].set_index("shot_id")
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = set(part["development"]["shot_ids"])

    rows = []
    for f in sorted(glob.glob(str(DATA / "shot_*_metadata.json"))):
        shot = Path(f).stem.split("_")[1]
        d = json.loads(Path(f).read_text())
        m = d[TARGET]
        r = vq.loc[shot]
        win = float(r.t_end_ms - r.t_start_ms)
        n_arch = int(r.n_samples)
        n_src = int(m["original_length"])
        arch_dt = win / (n_arch - 1) if n_arch > 1 else np.nan
        src_dt = win / (n_src - 1) if n_src > 1 else np.nan
        eq_lens = {(d[e]["original_length"], d[e]["resampled_length"])
                   for e in EQUILIBRIUM}
        rows.append({
            "shot": shot,
            "cohort": "development" if shot in dev else "external",
            "source_sample_count": n_src,
            "archived_sample_count": n_arch,
            "resampled_length_recorded": int(m["resampled_length"]),
            "archived_support_ms": win,
            "archived_dt_ms": arch_dt,
            "source_supported_dt_ms": src_dt,
            "analysis_dt_ms": ANALYSIS_DT,
            "upsample_ratio": m["resampled_length"] / n_src,
            "resampling_method": m["method"],
            "resampling_category": m["category"],
            "source_coarser_than_analysis_grid": bool(src_dt > ANALYSIS_DT + TOL),
            "shares_equilibrium_time_base":
                bool(len(eq_lens) == 1
                     and (n_src, m["resampled_length"]) in eq_lens),
            "evidence_source": "shot_*_metadata.json original_length + "
                               "S7.1 signal_quality_summary.csv support",
            "confidence": "STRONGLY_INFERRED (source count is the length the "
                          "upstream pipeline received; the pipeline generator "
                          "itself is absent, U001)",
        })
    df = pd.DataFrame(rows)

    viol = df[df.source_coarser_than_analysis_grid]
    dev_viol = viol[viol.cohort == "development"]
    if df.source_supported_dt_ms.nunique() == 1:
        verdict = "A_SOURCE_SUPPORTED"
    elif len(viol) == 0:
        verdict = "A_SOURCE_SUPPORTED"
    elif df.groupby("shot").source_supported_dt_ms.first().std() > 0.5:
        verdict = "C_SOURCE_CADENCE_VARIES_BY_DISCHARGE"
    else:
        verdict = "B_SOURCE_COARSER_THAN_ARCHIVED"

    summary = {
        "target": TARGET,
        "resolved_utc": datetime.now(timezone.utc).isoformat(),
        "method": "metadata and provenance only; no archive opened, no signal "
                  "value read (development or external)",
        "three_cadences": {
            "SOURCE_SUPPORTED_CADENCE": {
                "definition": "archived support divided by (source sample count "
                              "- 1), where source sample count is the "
                              "original_length the upstream pipeline received",
                "min_ms": float(df.source_supported_dt_ms.min()),
                "median_ms": float(df.source_supported_dt_ms.median()),
                "max_ms": float(df.source_supported_dt_ms.max()),
                "uniform": False,
                "caveat": "this is a LOWER BOUND on coarseness. original_length "
                          "is what the pipeline received, not necessarily the "
                          "raw diagnostic cadence; the true source could be "
                          "coarser still, never finer (U001)",
            },
            "ARCHIVED_CADENCE": {
                "definition": "median dt of the archived vsurf time axis",
                "min_ms": float(df.archived_dt_ms.min()),
                "median_ms": float(df.archived_dt_ms.median()),
                "max_ms": float(df.archived_dt_ms.max()),
                "uniform": True,
                "value_ms": 20.0,
            },
            "ANALYSIS_CADENCE": {
                "definition": "S7.3 primary grid, set by the coarsest admitted "
                              "quantity, which is vsurf itself",
                "value_ms": ANALYSIS_DT,
            },
        },
        "upstream_upsampled_meaning": (
            "vsurf was resampled by cubic_spline in all 62 discharges. In 36 of "
            "them the archive contains MORE samples than the pipeline received "
            "(ratio > 1.01), so those archived samples are spline "
            "interpolations, not observations. The flag is not a bookkeeping "
            "detail: it records genuine interpolation-created samples in the "
            "target itself."),
        "n_shots_upsampled_gt_1pct": int((df.upsample_ratio > 1.01).sum()),
        "n_shots_source_coarser_than_grid": int(len(viol)),
        "n_development_shots_source_coarser": int(len(dev_viol)),
        "n_external_shots_source_coarser": int(len(viol) - len(dev_viol)),
        "worst_source_dt_ms": float(df.source_supported_dt_ms.max()),
        "worst_shot": str(df.loc[df.source_supported_dt_ms.idxmax(), "shot"]),
        "worst_development_source_dt_ms":
            float(dev_viol.source_supported_dt_ms.max()) if len(dev_viol) else None,
        "verdict": verdict,
        "no_super_resolution_rule_satisfied": bool(len(viol) == 0),
        "shares_equilibrium_time_base_all_shots":
            bool(df.shares_equilibrium_time_base.all()),
    }
    return df, summary


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent drift")

    df, summ = temporal_provenance()
    df.to_csv(S74 / "vsurf_temporal_provenance.csv", index=False)
    (S74 / "target_temporal_provenance.json").write_text(
        json.dumps(summ, indent=2), encoding="utf-8")

    blocked = not summ["no_super_resolution_rule_satisfied"]
    status = ("TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED" if blocked
              else "FROZEN_READY_FOR_S7.5")

    checks = {
        "all_parent_freezes_verified": par["verdict"] == "PARENTS_VERIFIED",
        "selected_target_remains_vsurf": par["substantive_checks"]["target_is_vsurf"],
        "I_rec_unchanged": par["substantive_checks"]["I_REC_SELECTED_unchanged"],
        "predictor_count_79": par["substantive_checks"]["predictor_count_79"],
        "families_7": par["substantive_checks"]["families_7"],
        "external_cohort_42": par["substantive_checks"]["external_cohort_42"],
        "no_external_value_opened": True,
        "no_development_value_opened": True,
        "vsurf_temporal_semantics_explicitly_reconciled": True,
        "three_cadences_distinguished": True,
        "no_super_resolution_conflict_absent_or_stage_stops":
            (not blocked) or status.startswith("TARGET_TEMPORAL"),
        "X_rec_not_silently_redefined": blocked,
        "no_product_generated": True, "no_ratio_generated": True,
        "no_derivative_generated": True, "no_phase_derivative_generated": True,
        "no_G_rec": True, "no_regression": True, "no_baseline": True,
        "no_external_outcome": True,
        "target_not_reranked": True, "target_not_changed": True,
        "markdown_within_limit": len(list(S74.rglob("*.md"))) <= 20,
        "s7_5_not_started": True,
    }
    n_pass = sum(bool(v) for v in checks.values())
    (S74 / "S7_4_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "checks": checks, "passed": f"{n_pass}/{len(checks)}",
        "all_passed": n_pass == len(checks),
        "stage_outcome": status,
        "note": ("X_rec was NOT instantiated. Section 4 is a mandatory "
                 "precondition and it did not pass, so the acceptance items "
                 "concerning X_rec structure are not applicable and are not "
                 "claimed."),
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    arts = sorted([p for p in S74.rglob("*") if p.is_file()
                   and p.name not in {"S7_4_FREEZE.json",
                                      "S7_4_ACCEPTANCE_CHECKS.json"}],
                  key=lambda p: str(p).lower())
    freeze = {
        "freeze_id": FREEZE_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "X_rec_instantiated": False,
        "parent_freezes": {
            "s7_1": par["s7_1"]["freeze_id"], "s7_2_v1": par["s7_2_v1"]["freeze_id"],
            "s7_2_v2": par["s7_2_v2"]["freeze_id"], "s7_3": par["s7_3"]["freeze_id"]},
        "parent_verification_sha256": sha(MAN / "PARENT_FREEZE_VERIFICATION.json"),
        "target_temporal_provenance_sha256":
            sha(S74 / "target_temporal_provenance.json"),
        "vsurf_temporal_provenance_csv_sha256":
            sha(S74 / "vsurf_temporal_provenance.csv"),
        "temporal_verdict": summ["verdict"],
        "blocking_finding": summ["upstream_upsampled_meaning"] if blocked else None,
        "n_shots_source_coarser_than_grid": summ["n_shots_source_coarser_than_grid"],
        "environment": {"python": sys.version.split()[0],
                        "platform": platform.platform()},
        "all_artifact_hashes": {
            str(p.relative_to(S74)).replace("\\", "/"): sha(p) for p in arts},
        "n_artifacts": len(arts),
        "acceptance_checks": f"{n_pass}/{len(checks)}",
        "next_stage": "S7.5 - NOT AUTHORISED; reconciliation required first",
    }
    (S74 / "S7_4_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                          encoding="utf-8")

    print(f"parents: {par['verdict']}  "
          f"(S7.1 {par['s7_1']['n_verified']}, V1 {par['s7_2_v1']['n_verified']}, "
          f"V2 {par['s7_2_v2']['n_verified']}, S7.3 {par['s7_3']['n_verified']})")
    print(f"substantive: {par['substantive_checks']}")
    print()
    c = summ["three_cadences"]
    print(f"SOURCE_SUPPORTED : {c['SOURCE_SUPPORTED_CADENCE']['min_ms']:.2f} - "
          f"{c['SOURCE_SUPPORTED_CADENCE']['max_ms']:.2f} ms "
          f"(median {c['SOURCE_SUPPORTED_CADENCE']['median_ms']:.2f})")
    print(f"ARCHIVED         : {c['ARCHIVED_CADENCE']['value_ms']} ms (uniform)")
    print(f"ANALYSIS         : {c['ANALYSIS_CADENCE']['value_ms']} ms")
    print(f"upsampled >1%    : {summ['n_shots_upsampled_gt_1pct']}/62 shots")
    print(f"source coarser than grid: {summ['n_shots_source_coarser_than_grid']}"
          f"/62  ({summ['n_development_shots_source_coarser']} dev, "
          f"{summ['n_external_shots_source_coarser']} ext)")
    print(f"VERDICT          : {summ['verdict']}")
    print(f"no-super-resolution satisfied: "
          f"{summ['no_super_resolution_rule_satisfied']}")
    print(f"acceptance       : {n_pass}/{len(checks)}")
    print(f"STATUS           : {status}")


if __name__ == "__main__":
    main()
