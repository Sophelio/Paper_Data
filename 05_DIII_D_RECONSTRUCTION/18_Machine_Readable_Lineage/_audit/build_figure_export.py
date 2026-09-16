"""Assemble S7/FIGURE_EXPORT/ - the minimal machine-readable inputs for the
four-panel manuscript figure.

Copies frozen artifacts VERBATIM and records the sha256 of every source. The one
derived file (the 6 x 35 binary fold-support matrix) is built from the six
per-fold JSON artifacts, whose `coordinates` field is a proper list, so no
support-id string parsing occurs anywhere in this script.

Read-only with respect to every existing artifact.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

S7 = Path(__file__).resolve().parent.parent
OUT = S7 / "FIGURE_EXPORT"
E21 = S7 / "E2_1_crossfitted_discovery_and_qualification"
WEB = Path("D:/sir-web/Paper Examples/Relational Coordinates for "
           "Multimodal Plasma Observations")
QD = WEB / "canonical_d3d_62_shot_run_v1"
CA = WEB / "Coefficient_conditioning" / "Correction_audit"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# (source, destination, panel, role, freeze/stage id, what it carries)
COPY = [
    # ---- panel 1: q_desc discharge-specific coefficients -------------------
    (QD / "d3d_discharge_coefficients.csv",
     "panel1_qdesc_discharge_coefficients.csv", "1", "PRIMARY_FROZEN",
     "D3D-SIR-62-ALIGNED-V1 (q_desc canonical run; external to S7)",
     "62 rows, one per discharge: shot, intercept and the seven coefficients "
     "coef_Dkappa_Wdia, coef_Dbetan_Wdia, coef_Dbetan_kappa, coef_Dbetan_li, "
     "coef_q95_over_kappa, coef_dot_betan, coef_dot_kappa, plus fit rank, "
     "residual sum of squares and source-export hashes."),
    (CA / "tables" / "corrected_coefficient_classification.csv",
     "panel1_qdesc_coefficient_classification.csv", "1", "PRIMARY_FROZEN",
     "D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
     "7 rows, one per coefficient: original_status, corrected_status "
     "(5 ROBUSTLY_RESOLVED, 2 WITHIN_DISCHARGE_UNCERTAINTY_DOMINATES), "
     "heterogeneity ratio, tau^2 under REML and ML, profile interval, bootstrap "
     "quantiles, short/long block sensitivity, leave-one-discharge-out range."),
    (CA / "tables" / "corrected_coefficient_heterogeneity_primary.csv",
     "panel1_qdesc_coefficient_uncertainty.csv", "1", "PRIMARY_FROZEN",
     "D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1",
     "7 rows: observed between-discharge variance, mean within-discharge "
     "variance, mu_REML, tau2_REML with profile interval and bootstrap "
     "quantiles. This is the error-bar source for panel 1."),

    # ---- panel 2: q_rec six-fold support membership ------------------------
    (E21 / "folds" / "fold_0_result.json", "panel2_fold_0_result.json", "2",
     "PRIMARY_FROZEN", "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "fold record; `coordinates` is a JSON LIST of the 12 selected coordinate "
     "ids, plus support_sha256, train/test discharge lists and the U_rec "
     "quantities."),
    (E21 / "folds" / "fold_1_result.json", "panel2_fold_1_result.json", "2",
     "PRIMARY_FROZEN", "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "as fold 0"),
    (E21 / "folds" / "fold_2_result.json", "panel2_fold_2_result.json", "2",
     "PRIMARY_FROZEN", "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "as fold 0"),
    (E21 / "folds" / "fold_3_result.json", "panel2_fold_3_result.json", "2",
     "PRIMARY_FROZEN", "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "as fold 0"),
    (E21 / "folds" / "fold_4_result.json", "panel2_fold_4_result.json", "2",
     "PRIMARY_FROZEN", "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "as fold 0"),
    (E21 / "folds" / "fold_5_result.json", "panel2_fold_5_result.json", "2",
     "PRIMARY_FROZEN", "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "as fold 0"),
    (E21 / "coordinate_recurrence.csv", "panel2_coordinate_recurrence.csv", "2",
     "DERIVED_REPORTING_FROZEN",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "35 rows: coordinate_id, n_folds (0-6), share. Useful for ordering the "
     "columns of the matrix."),
    (E21 / "support_recurrence.csv", "panel2_support_pairwise_jaccard.csv", "2",
     "DERIVED_REPORTING_FROZEN",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "15 rows, all fold pairs: n_shared, jaccard, identical. Mean jaccard = "
     "0.285244."),
    (E21 / "constructor_recurrence.csv", "panel2_constructor_recurrence.csv", "2",
     "DERIVED_REPORTING_FROZEN",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "6 rows: constructor family and occurrence count across the 72 selected "
     "coordinate slots."),

    # ---- panel 3: q_rec out-of-fold reconstruction -------------------------
    (E21 / "heldout_discharge_results.csv",
     "panel3_heldout_discharge_results.csv", "3", "PRIMARY_FROZEN",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "62 rows, one per out-of-fold discharge: fold, shot_id, era, support_id, "
     "and NRMSE for REL, B0 (calibration mean), B1 (persistence), B1A (AR(1)), "
     "B2 (raw ridge, 78), B3 (raw HistGB, 78), H0 (hardened raw ridge, 70)."),
    (E21 / "baseline_results.csv", "panel3_method_summaries.csv", "3",
     "DERIVED_REPORTING_FROZEN",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "7 rows, one per method: mean, median, p90, max, earlier_mean, later_mean."),
    (E21 / "E2_1_CROSSFITTED_METRICS.json", "panel3_crossfitted_metrics.json", "3",
     "DERIVED_REPORTING_FROZEN",
     "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
     "method summaries, paired differences (mean_delta, median_delta, "
     "wins/ties/losses) against every baseline, and the era-stratified result."),
]


def main() -> int:
    OUT.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    records, missing = [], []

    for src, dst, panel, role, freeze, desc in COPY:
        if not src.exists():
            missing.append(str(src))
            continue
        shutil.copy2(src, OUT / dst)
        h = sha256(src)
        assert sha256(OUT / dst) == h, dst
        records.append({"exported_as": dst, "panel": panel, "role": role,
                        "source_path": str(src), "freeze_or_stage_id": freeze,
                        "sha256": h, "bytes": src.stat().st_size,
                        "transformed": False, "contents": desc})
    if missing:
        raise SystemExit("missing sources: %s" % missing)

    # ---- the single derived artifact: 6 x 35 binary matrix ----------------
    coords_per_fold = []
    for k in range(6):
        j = json.loads((E21 / "folds" / ("fold_%d_result.json" % k)).read_text())
        assert len(j["coordinates"]) == 12
        coords_per_fold.append(list(j["coordinates"]))     # already a list
    allc = sorted(set().union(*(set(c) for c in coords_per_fold)))
    M = np.array([[1 if c in set(f) else 0 for c in allc] for f in coords_per_fold],
                 dtype=int)
    mat = pd.DataFrame(M, columns=allc)
    mat.insert(0, "fold", range(6))
    mat.to_csv(OUT / "panel2_fold_support_matrix.csv", index=False)

    sets = [set(f) for f in coords_per_fold]
    pair = [len(sets[a] & sets[b]) / len(sets[a] | sets[b])
            for a in range(6) for b in range(a + 1, 6)]
    checks = {
        "n_folds": int(M.shape[0]), "n_distinct_coordinates": int(M.shape[1]),
        "support_sizes": [int(x) for x in M.sum(axis=1)],
        "any_two_identical": bool(any(sets[a] == sets[b]
                                      for a in range(6) for b in range(a + 1, 6))),
        "mean_pairwise_jaccard": float(np.mean(pair)),
        "coordinates_in_all_six": sorted(set.intersection(*sets)),
    }
    records.append({
        "exported_as": "panel2_fold_support_matrix.csv", "panel": "2",
        "role": "DERIVED_BY_THIS_EXPORT",
        "source_path": str(E21 / "folds" / "fold_{0..5}_result.json"),
        "freeze_or_stage_id":
            "D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1",
        "sha256": sha256(OUT / "panel2_fold_support_matrix.csv"),
        "bytes": (OUT / "panel2_fold_support_matrix.csv").stat().st_size,
        "transformed": True,
        "transformation": "one-hot of the six `coordinates` lists over the union "
                          "of coordinate ids, sorted; no numerical value is "
                          "altered and no support-id string is parsed",
        "contents": "6 x 35 binary matrix, first column `fold` (0-5), remaining "
                    "35 columns named by coordinate id, 1 if that fold's support "
                    "contains it.",
        "self_checks": checks})

    d = pd.read_csv(E21 / "heldout_discharge_results.csv", dtype={"shot_id": str})
    diff = d.REL_nrmse - d.B1_nrmse
    FLOOR = 0.01
    manifest = {
        "record_id": "S7_FIGURE_EXPORT_MANIFEST_V1",
        "generated_utc": now,
        "purpose": "minimal machine-readable inputs for a four-panel manuscript "
                   "figure",
        "read_only_with_respect_to_all_existing_artifacts": True,
        "scientific_content_unchanged": True,
        "files": records,
        "cross_checks": {
            "panel2": checks,
            "panel3": {
                "n_discharges": int(len(d)),
                "n_unique_shots": int(d.shot_id.nunique()),
                "REL_mean": float(d.REL_nrmse.mean()),
                "B1_persistence_mean": float(d.B1_nrmse.mean()),
                "wins_ties_losses_vs_persistence": [
                    int((diff <= -FLOOR).sum()),
                    int(((diff > -FLOOR) & (diff <= FLOOR)).sum()),
                    int((diff > FLOOR).sum())],
                "tie_rule": "the contract's own practical-equivalence floor, "
                            "|delta| <= 0.01",
            },
            "panel1": {
                "n_discharges": int(len(pd.read_csv(
                    QD / "d3d_discharge_coefficients.csv"))),
                "n_coefficients": 7,
                "robustly_resolved": 5, "uncertainty_dominated": 2,
            },
        },
        "hazard_notice": {
            "issue": "coordinate ids of the C4/C6/C7/C8 constructor families embed "
                     "a pipe character inside parentheses, e.g. "
                     "LEVEL_RATE(cerqrott12|ece35)",
            "consequence": "splitting a pipe-joined `support_id` naively corrupts "
                           "the support",
            "mitigation": "this export takes coordinates from the per-fold JSON "
                          "`coordinates` lists, so no parsing is required; "
                          "panel2_fold_support_matrix.csv is already expanded",
        },
    }
    (OUT / "EXPORT_MANIFEST.json").write_text(json.dumps(manifest, indent=2),
                                              encoding="utf-8")
    print("exported %d files to %s" % (len(records), OUT.name))
    for k, v in checks.items():
        print("  panel2 %-26s %s" % (k, v))
    print("  panel3 REL mean %.6f | B1 mean %.6f | W/T/L %s"
          % (manifest["cross_checks"]["panel3"]["REL_mean"],
             manifest["cross_checks"]["panel3"]["B1_persistence_mean"],
             manifest["cross_checks"]["panel3"]["wins_ties_losses_vs_persistence"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
