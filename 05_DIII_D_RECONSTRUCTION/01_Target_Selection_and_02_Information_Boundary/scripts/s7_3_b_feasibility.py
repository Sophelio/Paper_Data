"""S7.3 stage B — development-only target feasibility.

THIS IS THE ONLY STAGE THAT OPENS SIGNAL VALUES, AND ONLY FOR THE 20
DEVELOPMENT DISCHARGES.

The development list is read from the frozen cohort partition and verified
against the expected list; it is never hard-coded as the primary source.
Every archive read is logged.

What is computed: target-only feasibility statistics required by the frozen
contract. No predictor-target statistic of any kind, no correlation, no fit, no
model, no baseline, no coordinate.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S73 = HERE.parent
S7 = S73.parent
EX = S7.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
MAN = S73 / "manifests"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

EXPECTED_DEV = [
    "160715", "160720", "161138", "165022", "165028", "165042", "165861",
    "170396", "187017", "187020", "187024", "189647", "189651", "195264",
    "195267", "195273", "195638", "195647", "195650", "195655",
]

BLOCKS = [("A", 0.00, 0.40, 0.40, 0.50),
          ("B", 0.00, 0.60, 0.60, 0.70),
          ("C", 0.00, 0.80, 0.80, 0.90)]

# S7.2 canonical units. Conversion factor from archived unit to canonical.
CANONICAL = {"keV": ("eV", 1e3), "km/s": ("m/s", 1e3), "cm^-3": ("m^-3", 1e6),
             "ph/(sr cm^2 s)": ("ph/(sr m^2 s)", 1e4)}

ACCESS_LOG: list[dict] = []


def log_access(shot: str, cohort: str, sigs_values: int, sigs_times: int,
               reason: str) -> None:
    ACCESS_LOG.append({
        "stage": "S7.3B", "shot_id": shot,
        "development_or_external": cohort,
        "signals_values_read": sigs_values,
        "signals_times_read": sigs_times,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def rrv(y: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    y = y[np.isfinite(y)]
    if y.size == 0:
        return 0.0
    rms = float(np.sqrt(np.mean(y ** 2)))
    if rms == 0.0:
        return 0.0
    mad = float(np.median(np.abs(y - np.median(y))))
    return 1.4826 * mad / rms


def main() -> None:
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = list(part["development"]["shot_ids"])
    ext = set(part["external"]["shot_ids"])
    if sorted(dev) != sorted(EXPECTED_DEV):
        raise SystemExit("STOP: development list does not match expected")

    inv = pd.read_csv(R1 / "FINAL_SIGNAL_INVENTORY.csv")
    bs = pd.read_csv(S73 / "target_boundary_summary.csv")
    units = json.loads((S7 / "SIGNAL_UNITS.json").read_text())["signals"]
    cands = list(bs.target)
    grid_dt = dict(zip(bs.target, bs.primary_grid_dt_ms))
    admitted = {}
    for r in bs.itertuples():
        # admitted set = surviving predictors + the target itself
        pass

    # Recompute the admitted set per candidate exactly as stage A defined it.
    excl_lookup = {}
    sibrule = json.loads((MAN / "SIBLING_SUBFAMILY_RULE.json").read_text())
    subfam = {k: v["members"] for k, v in sibrule["subfamilies"].items()}
    sib_of = {s: k for k, m in subfam.items() for s in m}
    eq = set(PROV.GROUPS["equilibrium_shape"])
    beams = [f"pinj_{b}" for b in ("15l", "15r", "21l", "21r", "30l", "30r",
                                   "33l", "33r")]
    defmap = {b: ["pinj"] for b in beams}
    defmap["pinj"] = list(beams)
    allsig = list(inv.signal_id)
    for y in cands:
        sibs = {s for s in subfam.get(sib_of.get(y, ""), []) if s != y}
        deps = set(defmap.get(y, []))
        excl_lookup[y] = {s for s in allsig
                          if s == y or s in deps or s in eq or s in sibs}

    # ---- load development archives once -----------------------------------
    series: dict[str, dict[str, tuple]] = {}
    for shot in dev:
        if shot in ext:
            raise SystemExit(f"STOP: firewall breach, {shot} is external")
        with np.load(PROV._shot_npz_path(DATA, shot), allow_pickle=False) as a:
            series[shot] = {n: PROV._load_signal(a, n) for n in allsig}
        log_access(shot, "development", len(cands), len(allsig),
                   "target-only development feasibility (S7.3 sections 15-19); "
                   "values used ONLY for the 64 candidate targets, all other "
                   "signals read for time support only")

    # ---- per-candidate feasibility ----------------------------------------
    conv_rows, rrv_rows, scale_rows, feas_rows = [], [], [], []
    for y in cands:
        arch_unit = str(units[y].get("units") or "")
        canon_unit, factor = CANONICAL.get(arch_unit, (arch_unit, 1.0))
        conv_rows.append({"target": y, "archived_unit": arch_unit,
                          "canonical_unit": canon_unit, "factor": factor})

        dt = float(grid_dt[y])
        admitted_set = [s for s in allsig if s not in excl_lookup[y]] + [y]

        per_shot, n_zero, n_valid_blocks, n_invalid_blocks = [], 0, 0, 0
        distinct_fracs, eras = [], set()
        for shot in dev:
            S = series[shot]
            t0 = max(float(S[s][0][0]) for s in admitted_set)
            t1 = min(float(S[s][0][-1]) for s in admitted_set)
            n = int(np.floor((t1 - t0) / dt)) + 1
            grid = t0 + dt * np.arange(n, dtype=np.float64)
            ty, vy = S[y]
            yg = PROV._resample_to_grid(ty, vy, grid) * factor

            r = rrv(yg)
            per_shot.append(r)
            if np.all(yg == 0.0):
                n_zero += 1
            distinct_fracs.append(np.unique(yg).size / yg.size)
            eras.add("later" if int(shot) >= 189646 else "earlier")
            rrv_rows.append({"target": y, "shot_id": shot, "rrv": r,
                             "n_grid_samples": n, "grid_dt_ms": dt})

            for blk, c0, c1, e0, e1 in BLOCKS:
                ci = slice(int(np.floor(n * c0)), int(np.floor(n * c1)))
                ei = slice(int(np.floor(n * e0)), int(np.floor(n * e1)))
                cal, ev = yg[ci], yg[ei]
                sc = float(np.std(cal, ddof=0)) if cal.size else 0.0
                bad = (sc == 0.0) or (not np.isfinite(sc)) or ev.size == 0
                n_invalid_blocks += bad
                n_valid_blocks += (not bad)
                scale_rows.append({
                    "target": y, "shot_id": shot, "block": blk,
                    "scale": sc, "zero_scale": sc == 0.0,
                    "finite": bool(np.isfinite(sc)),
                    "n_calibration_samples": int(cal.size),
                    "n_evaluation_samples": int(ev.size),
                    "valid_for_normalized_scoring": bool(not bad),
                })

        rrv_dev = float(np.median(per_shot))
        feas_rows.append({
            "target": y,
            "canonical_unit": canon_unit,
            "grid_dt_ms": dt,
            "rrv_dev_median": rrv_dev,
            "rrv_min": float(np.min(per_shot)),
            "rrv_max": float(np.max(per_shot)),
            "rrv_margin": rrv_dev - 0.05,
            "min_distinct_values_fraction": float(np.min(distinct_fracs)),
            "median_distinct_values_fraction": float(np.median(distinct_fracs)),
            "n_identically_zero_development_discharges": int(n_zero),
            "n_valid_nrmse_blocks": int(n_valid_blocks),
            "n_invalid_nrmse_blocks": int(n_invalid_blocks),
            "n_eras_present": len(eras),
            "eras_present": "|".join(sorted(eras)),
        })

    pd.DataFrame(conv_rows).to_csv(S73 / "target_unit_canonicalization.csv",
                                   index=False)
    pd.DataFrame(rrv_rows).to_csv(S73 / "development_rrv_per_shot.csv",
                                  index=False)
    pd.DataFrame(scale_rows).to_csv(S73 / "development_nrmse_scale_audit.csv",
                                    index=False)
    feas = pd.DataFrame(feas_rows)
    feas.to_csv(S73 / "target_feasibility_metrics.csv", index=False)

    with (MAN / "DATA_ACCESS_LOG.csv").open("w", newline="",
                                            encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ACCESS_LOG[0].keys()))
        w.writeheader()
        w.writerows(ACCESS_LOG)

    shots_read = {r["shot_id"] for r in ACCESS_LOG}
    ext_read = shots_read & ext
    (MAN / "EXTERNAL_FIREWALL_AUDIT.json").write_text(json.dumps({
        "audited_utc": datetime.now(timezone.utc).isoformat(),
        "development_list_source": "frozen COHORT_PARTITION.json",
        "development_list_matches_expected": True,
        "n_unique_value_bearing_shots_read": len(shots_read),
        "value_bearing_shots_read": sorted(shots_read),
        "n_external_value_bearing_shots_read": len(ext_read),
        "external_shots_read": sorted(ext_read),
        "external_ids_known_but_unopened": len(ext),
        "verdict": "FIREWALL_INTACT" if (len(shots_read) == 20 and not ext_read)
                   else "FIREWALL_BREACH",
    }, indent=2), encoding="utf-8")

    print(f"development shots opened : {len(shots_read)}  "
          f"external opened: {len(ext_read)}")
    print(f"candidates evaluated     : {len(feas)}")
    print(f"RRV_dev range            : {feas.rrv_dev_median.min():.4f} "
          f"- {feas.rrv_dev_median.max():.4f}")
    print(f"pass RRV>=0.05           : {int((feas.rrv_dev_median>=0.05).sum())}")
    print(f"pass distinct>=0.10      : "
          f"{int((feas.min_distinct_values_fraction>=0.10).sum())}")
    print(f"zero-target discharges>0 : "
          f"{int((feas.n_identically_zero_development_discharges>0).sum())}")
    print(f"invalid NRMSE blocks>0   : "
          f"{int((feas.n_invalid_nrmse_blocks>0).sum())}")
    print(f"both eras present        : {int((feas.n_eras_present==2).sum())}")


if __name__ == "__main__":
    main()
