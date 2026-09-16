"""S7.2 — target-blind cohort partition and validation-geometry feasibility.

Uses ONLY frozen S7.1 metadata: shot identifiers, operational periods,
processing era, and per-signal temporal support. **No signal value is read.**
The archives are not opened by this script at all; every input comes from the
frozen S7.1 CSVs.

Partition rule (deterministic, no randomness, no seed)
-----------------------------------------------------
Within each operational period, sort shots ascending and select those at
position `i` with `i % 3 == 1`. Taking position 1 rather than 0 avoids
systematically claiming the first discharge of every period.

A period of one discharge contributes none, so shot 155537 (period 1) goes to
the external cohort. That is deliberate: the external cohort is where the
generalisation claim is tested and therefore benefits more from covering all
seven periods, while development loses only a singleton.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S72 = HERE.parent
S7 = S72.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"

ERA_SPLIT_SHOT = 189646          # first shot of the later processing era
PERIOD_GAP = 2000                # shot-number gap defining a period boundary
SELECT_MOD, SELECT_REM = 3, 1    # take i % 3 == 1 within each period

# Rolling-origin geometry, in normalised discharge time tau in [0,1].
WINDOWS = [
    {"block": "A", "calibration": [0.00, 0.40], "protected": [0.40, 0.50]},
    {"block": "B", "calibration": [0.00, 0.60], "protected": [0.60, 0.70]},
    {"block": "C", "calibration": [0.00, 0.80], "protected": [0.80, 0.90]},
]

# Predeclared minima, chosen before any target exists.
MIN_PROTECTED_SAMPLES = 10
MIN_CALIBRATION_SAMPLES = 30

# Candidate analysis cadences = the distinct native cadences in the object.
# Which one applies depends on the coarsest family admitted for a given target,
# under the numerical-resolution policy. Feasibility is audited for all of them.
CANDIDATE_DT_MS = [20.0, 10.0, 2.0, 1.0, 0.2, 0.1, 0.02]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def periods(shots: np.ndarray):
    """Contiguous shot-number families, as frozen in S7.1."""
    s = np.sort(shots)
    brk = np.where(np.diff(s) > PERIOD_GAP)[0]
    return [list(map(int, g)) for g in np.split(s, brk + 1)]


def main() -> None:
    shot_inv = pd.read_csv(R1 / "FINAL_SHOT_INVENTORY.csv", dtype={"shot_id": str})
    shot_inv["shot"] = shot_inv.shot_id.astype(int)
    shot_inv["era"] = np.where(shot_inv.shot >= ERA_SPLIT_SHOT, "later", "earlier")

    fams = periods(shot_inv.shot.values)
    pid = {}
    for i, g in enumerate(fams, start=1):
        for s in g:
            pid[s] = i
    shot_inv["period"] = shot_inv.shot.map(pid)

    # ---------------- partition -------------------------------------------
    dev = []
    for i, g in enumerate(fams, start=1):
        picked = [s for j, s in enumerate(sorted(g)) if j % SELECT_MOD == SELECT_REM]
        dev.extend(picked)
    dev = sorted(dev)
    ext = sorted(set(shot_inv.shot) - set(dev))
    shot_inv["cohort"] = np.where(shot_inv.shot.isin(dev), "development", "external")

    def brk(df):
        return {
            "n": int(len(df)),
            "by_era": df.era.value_counts().to_dict(),
            "by_period": {int(k): int(v)
                          for k, v in df.period.value_counts().sort_index().items()},
        }

    d_df = shot_inv[shot_inv.cohort == "development"]
    e_df = shot_inv[shot_inv.cohort == "external"]

    partition = {
        "policy_id": "S7.2-COHORT-PARTITION-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "target_blind": True,
        "inputs_used": ["shot identifiers", "operational period membership",
                        "processing era"],
        "signal_values_used": False,
        "target_values_used": False,
        "method": "deterministic stratified selection; no randomness, no seed",
        "rule": f"within each period, sorted ascending, select i % "
                f"{SELECT_MOD} == {SELECT_REM}",
        "era_split_shot": ERA_SPLIT_SHOT,
        "period_gap": PERIOD_GAP,
        "n_total": int(len(shot_inv)),
        "development": {**brk(d_df), "shot_ids": [str(s) for s in dev]},
        "external": {**brk(e_df), "shot_ids": [str(s) for s in ext]},
        "development_fraction": round(len(dev) / len(shot_inv), 4),
        "periods": {
            int(i): {"first": g[0], "last": g[-1], "n": len(g),
                     "era": "later" if g[0] >= ERA_SPLIT_SHOT else "earlier",
                     "n_development": sum(1 for s in g if s in set(dev)),
                     "n_external": sum(1 for s in g if s not in set(dev))}
            for i, g in enumerate(fams, start=1)
        },
        "singleton_period_note": (
            "Period 1 holds one discharge (155537) and cannot be split. It is "
            "assigned to the external cohort so that the external cohort -- "
            "where the generalisation claim is tested -- covers all seven "
            "periods. Development covers six."),
    }
    (S72 / "COHORT_PARTITION.json").write_text(
        json.dumps(partition, indent=2), encoding="utf-8")

    # ---------------- validation geometry feasibility ----------------------
    rows = []
    for r in shot_inv.itertuples():
        W = float(r.common_window_ms)
        for dt in CANDIDATE_DT_MS:
            n_tot = int(np.floor(W / dt)) + 1
            for w in WINDOWS:
                n_cal = int(np.floor(n_tot * (w["calibration"][1]
                                              - w["calibration"][0])))
                n_pro = int(np.floor(n_tot * (w["protected"][1]
                                              - w["protected"][0])))
                rows.append({
                    "shot_id": r.shot_id, "cohort": r.cohort,
                    "era": r.era, "period": r.period,
                    "common_window_ms": W, "grid_dt_ms": dt,
                    "n_samples_total": n_tot, "block": w["block"],
                    "calibration_tau": f"[{w['calibration'][0]:.2f},"
                                       f"{w['calibration'][1]:.2f})",
                    "protected_tau": f"[{w['protected'][0]:.2f},"
                                     f"{w['protected'][1]:.2f})",
                    "n_calibration": n_cal, "n_protected": n_pro,
                    "feasible": bool(n_cal >= MIN_CALIBRATION_SAMPLES
                                     and n_pro >= MIN_PROTECTED_SAMPLES),
                })
    feas = pd.DataFrame(rows)
    feas.to_csv(S72 / "manifests" / "validation_feasibility_audit.csv",
                index=False)

    by_dt = (feas.groupby("grid_dt_ms")
             .agg(n_checks=("feasible", "size"),
                  n_feasible=("feasible", "sum"),
                  min_protected=("n_protected", "min"),
                  min_calibration=("n_calibration", "min"))
             .reset_index())
    by_dt["all_feasible"] = by_dt.n_checks == by_dt.n_feasible

    coarsest_ok = bool(by_dt[by_dt.grid_dt_ms == 20.0].all_feasible.iloc[0])

    vw = {
        "protocol_id": "S7.2-VALIDATION-GEOMETRY-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "geometry": "rolling-origin, expanding calibration, disjoint protected "
                    "blocks",
        "normalised_time": "tau in [0,1] over each discharge's common support",
        "windows": WINDOWS,
        "n_blocks_per_discharge": len(WINDOWS),
        "target_values_used_to_choose_windows": False,
        "signal_values_used_to_choose_windows": False,
        "predeclared_minima": {
            "min_protected_samples": MIN_PROTECTED_SAMPLES,
            "min_calibration_samples": MIN_CALIBRATION_SAMPLES,
        },
        "feasibility_by_candidate_grid": [
            {"grid_dt_ms": float(r.grid_dt_ms),
             "all_discharges_all_blocks_feasible": bool(r.all_feasible),
             "min_protected_samples_observed": int(r.min_protected),
             "min_calibration_samples_observed": int(r.min_calibration)}
            for r in by_dt.itertuples()
        ],
        "worst_case_grid_feasible": coarsest_ok,
        "verdict": ("FEASIBLE_AT_ALL_CANDIDATE_CADENCES" if
                    bool(by_dt.all_feasible.all()) else
                    "INFEASIBLE_AT_SOME_CADENCE"),
        "note": (
            "Feasibility is audited at every native cadence present in the "
            "object, because the analysis grid is set by the coarsest family "
            "admitted for a given target under the numerical-resolution "
            "policy. The 20 ms case is the worst case and bounds all others."),
    }
    (S72 / "validation_windows.json").write_text(
        json.dumps(vw, indent=2), encoding="utf-8")

    freeze = {
        "partition_policy_id": partition["policy_id"],
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_partition_sha256": sha256_file(S72 / "COHORT_PARTITION.json"),
        "validation_windows_sha256": sha256_file(S72 / "validation_windows.json"),
        "n_development": len(dev), "n_external": len(ext),
        "development_shot_ids": [str(s) for s in dev],
        "external_shot_ids": [str(s) for s in ext],
        "deterministic": True, "seed": None,
        "parent_freeze_id": "D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1",
    }
    (S72 / "manifests" / "COHORT_PARTITION_FREEZE.json").write_text(
        json.dumps(freeze, indent=2), encoding="utf-8")

    print("cohort partition (target-blind, deterministic)")
    print(f"  development : {len(dev):2d} ({len(dev)/62:.1%})  "
          f"era {d_df.era.value_counts().to_dict()}  "
          f"periods {sorted(d_df.period.unique())}")
    print(f"  external    : {len(ext):2d} ({len(ext)/62:.1%})  "
          f"era {e_df.era.value_counts().to_dict()}  "
          f"periods {sorted(e_df.period.unique())}")
    print()
    print("validation geometry feasibility")
    for r in by_dt.itertuples():
        print(f"  dt={r.grid_dt_ms:6.2f} ms  feasible "
              f"{int(r.n_feasible)}/{int(r.n_checks)}  "
              f"min protected={int(r.min_protected)}  "
              f"min calib={int(r.min_calibration)}")
    print(f"  VERDICT: {vw['verdict']}")


if __name__ == "__main__":
    main()
