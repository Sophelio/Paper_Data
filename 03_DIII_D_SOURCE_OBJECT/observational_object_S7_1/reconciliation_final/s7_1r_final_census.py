"""S7.1R-FINAL step 2 — census, parity, semantic types, origin classification.

Rebuilds the 95-signal census from the archive itself rather than trusting the
earlier count, then joins the frozen units registry and the provider manifest.

Classification policy
---------------------
`DIRECT_MEASUREMENT` is granted only where the record supports it. Two signals
are documented upstream as `raw` digitiser output and are therefore the most
defensible direct measurements in the object -- note the irony that they are
also the two with no physical unit. The magnetics trio is marked direct at
`STRONGLY_INFERRED` because the local record documents the quantity but never
the sensor/compensation chain (U006).

Actuation is separated from diagnosis: the gas valves are command voltages and
the beam channels are actuator outputs. Forcing them into `UNKNOWN`, as the
first census did, loses real information.
"""

from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OBJ = HERE.parent
S7 = OBJ.parent
EX = S7.parent
DATA = EX / "data" / "resampled_data_v6"
UNITS = S7 / "SIGNAL_UNITS.json"

import sys
sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_df(df: pd.DataFrame) -> str:
    return sha256_bytes(df.to_csv(index=False).encode("utf-8"))


# ---------------------------------------------------------------------------
# Origin classification. (rule, classification, evidence_class, note)
# ---------------------------------------------------------------------------
def classify(sig: str, desc: str, status: str):
    d = desc.lower()
    if sig in ("pcbcoil", "pcdiamag3"):
        return ("DIRECT_MEASUREMENT", "LOCAL_DOCUMENTED",
                "upstream units attribute is 'raw' -- uncalibrated digitiser "
                "output, i.e. an unprocessed sensor channel")
    if sig in ("ip", "bt", "vsurf"):
        return ("DIRECT_MEASUREMENT", "STRONGLY_INFERRED",
                "standard magnetic diagnostic with a documented physical unit; "
                "the local record does not document the sensor or compensation "
                "chain, so this remains inferred (U006)")
    if sig.startswith("fs"):
        return ("DIRECT_MEASUREMENT", "LOCAL_DOCUMENTED",
                "calibrated filterscope photon flux, ph/(sr cm^2 s); a "
                "calibrated radiometric measurement, not an inversion")
    if sig.startswith("gas"):
        return ("CONTROL_COMMAND_OR_ACTUATION", "LOCAL_DOCUMENTED",
                "gas injection valve COMMAND in volts -- an actuator command, "
                "not a plasma measurement")
    if sig == "pinj" or sig.startswith("pinj_") or sig == "tinj":
        return ("CONTROL_COMMAND_OR_ACTUATION", "LOCAL_DOCUMENTED",
                "neutral-beam actuation output (injected power / torque); "
                "actuator-side quantity rather than a plasma diagnostic")
    if sig.startswith("ece"):
        return ("DIAGNOSTIC_RECONSTRUCTION", "LOCAL_DOCUMENTED",
                "ECE radiometer electron temperature; requires calibration and "
                "an optically-thick emission assumption")
    if sig.startswith("cerq"):
        return ("DIAGNOSTIC_RECONSTRUCTION", "LOCAL_DOCUMENTED",
                "CER spectral fit product (rotation velocity / ion temperature)")
    if sig.startswith("prmtan_"):
        return ("DIAGNOSTIC_RECONSTRUCTION", "LOCAL_DOCUMENTED",
                "pedestal parameter from an explicit tanh profile fit")
    if sig == "density":
        return ("DIAGNOSTIC_RECONSTRUCTION", "LOCAL_DOCUMENTED",
                "line-AVERAGED electron density: a line integral divided by a "
                "chord length, not a local measurement")
    if sig in PROV.GROUPS["equilibrium_shape"]:
        ev = "LOCAL_DOCUMENTED" if "efit" in d else "STRONGLY_INFERRED"
        note = ("description names EFIT explicitly"
                if "efit" in d else
                "equilibrium reconstruction output; EFIT family inferred from "
                "group coherence with aminor/area, which name EFIT explicitly")
        return ("EQUILIBRIUM_DERIVED", ev, note)
    return ("UNKNOWN", "UNRESOLVED", "no local evidence establishes an origin")


DIMENSIONAL = {
    "m": "L", "m^2": "L^2", "m^3": "L^3", "1": "dimensionless",
    "T": "M T^-2 I^-1", "V": "L^2 M T^-3 I^-1", "A": "I",
    "km/s": "L T^-1", "eV": "L^2 M T^-2", "keV": "L^2 M T^-2",
    "cm^-3": "L^-3", "m^-3": "L^-3", "kW": "L^2 M T^-3",
    "W": "L^2 M T^-3", "N m": "L^2 M T^-2",
    "ph/(sr cm^2 s)": "L^-2 T^-1 (photon flux)",
}
NONNEG = {"aminor", "area", "volume", "density", "prmtan_neped",
          "prmtan_teped", "kappa", "q95", "li"}


def main() -> None:
    units_doc = json.loads(UNITS.read_text(encoding="utf-8"))
    U = units_doc["signals"]
    units_sha = sha256_bytes(UNITS.read_bytes())

    files = sorted(glob.glob(str(DATA / "shot_*_resampled.npz")))
    shots = [Path(f).stem.split("_")[1] for f in files]

    # --- rebuild the census from the archive, not from the earlier count ----
    per_shot_sets, quality, avail = {}, [], []
    for f, sid in zip(files, shots):
        with np.load(f, allow_pickle=False) as a:
            names = sorted({k[:-5] for k in a.files if k.endswith("_data")})
            per_shot_sets[sid] = set(names)
            for n in names:
                v = np.asarray(a[f"{n}_data"], dtype=float)
                t = np.asarray(a[f"{n}_times"], dtype=float)
                fin = np.isfinite(v)
                vv = v[fin]
                dt = np.diff(np.sort(t[np.isfinite(t)]))
                uniq = np.unique(vv).size if vv.size else 0
                quality.append({
                    "shot_id": sid, "signal_id": n,
                    "n_samples": int(v.size),
                    "finite_fraction": float(fin.mean()) if v.size else 0.0,
                    "t_start_ms": float(t[0]) if t.size else np.nan,
                    "t_end_ms": float(t[-1]) if t.size else np.nan,
                    "native_dt_median_ms": float(np.median(dt)) if dt.size else np.nan,
                    "n_unique_values": int(uniq),
                    "repeat_ratio": float(1.0 - uniq / vv.size) if vv.size else 1.0,
                    "near_constant": bool(vv.size and uniq <= 2),
                    "identically_zero": bool(vv.size and np.all(vv == 0.0)),
                    "vmin": float(vv.min()) if vv.size else np.nan,
                    "vmax": float(vv.max()) if vv.size else np.nan,
                    "clipped_at_max": bool(
                        vv.size > 10 and np.count_nonzero(vv == vv.max()) > 0.01 * vv.size),
                })
                avail.append({"shot_id": sid, "signal_id": n, "available": 1})

    census = sorted(set().union(*per_shot_sets.values()))
    common = sorted(set.intersection(*per_shot_sets.values()))
    q = pd.DataFrame(quality)

    # --- inventory ----------------------------------------------------------
    rows = []
    for i, s in enumerate(PROV.ALL_SIGNALS, start=1):
        u = U[s]
        desc = u.get("description", "")
        unit = u.get("units")
        unit_s = "" if unit is None else str(unit)
        cls, ev, note = classify(s, desc, u.get("status", ""))
        sq = q[q.signal_id == s]
        rows.append({
            "signal_index": i,
            "signal_id": s,
            "canonical_name": s,
            "archive_name": f"{s}_data / {s}_times",
            "dalia_name": s,
            "aliases": "",
            "signal_group": PROV.SIGNAL_GROUP[s],
            "scientific_description": desc,
            "units": unit_s,
            "units_status": u.get("status", ""),
            "units_evidence_class": u.get(
                "evidence_class",
                "LOCAL_DOCUMENTED (units registry)"),
            "dimensional_signature": DIMENSIONAL.get(unit_s, "dimensionless"
                                                     if unit_s == "1" else
                                                     "UNIT_LESS_UNCALIBRATED"),
            "semantic_type": u.get("status"),
            "is_dimensionless": unit_s == "1",
            "sign_convention": "nonnegative" if s in NONNEG else "signed_or_unknown",
            "source_classification": cls,
            "origin_evidence_class": ev,
            "direct_or_derived_status": cls,
            "source_path": str(DATA),
            "available_shots": int(sq.shape[0]),
            "native_dt_median": float(sq.native_dt_median_ms.median()),
            "finite_fraction_min": float(sq.finite_fraction.min()),
            "provenance_status": (
                "ANALYSIS_SIDE_CODE_VERIFIED; UPSTREAM_RESAMPLE_DOCUMENTED_"
                "OPERATION_CODE_ABSENT"),
            "notes": note,
        })
    inv = pd.DataFrame(rows)
    inv.to_csv(HERE / "FINAL_SIGNAL_INVENTORY.csv", index=False)

    # --- semantic types -----------------------------------------------------
    inv[[
        "signal_id", "signal_group", "units", "units_status",
        "units_evidence_class", "dimensional_signature", "semantic_type",
        "is_dimensionless", "sign_convention", "source_classification",
        "scientific_description",
    ]].to_csv(HERE / "semantic_types_and_units.csv", index=False)

    inv[[
        "signal_id", "signal_group", "source_classification",
        "origin_evidence_class", "units", "scientific_description", "notes",
    ]].to_csv(HERE / "SIGNAL_ORIGIN_CLASSIFICATION.csv", index=False)

    # --- quality / availability --------------------------------------------
    q.to_csv(HERE / "signal_quality_summary.csv", index=False)
    am = (pd.DataFrame(avail)
          .pivot_table(index="shot_id", columns="signal_id",
                       values="available", fill_value=0))
    am.to_csv(HERE / "availability_matrix.csv")
    (q.groupby("shot_id")
       .agg(n_signals=("signal_id", "nunique"),
            min_finite_fraction=("finite_fraction", "min"),
            n_near_constant=("near_constant", "sum"),
            n_identically_zero=("identically_zero", "sum"))
       .reset_index()
       .to_csv(HERE / "availability_by_shot.csv", index=False))

    # --- shot inventory -----------------------------------------------------
    si = []
    for sid in shots:
        sq = q[q.shot_id == sid]
        t0 = float(sq.t_start_ms.max())
        t1 = float(sq.t_end_ms.min())
        si.append({
            "shot_id": sid, "device": "DIII-D",
            "n_signals_present": int(sq.signal_id.nunique()),
            "all_95_present": bool(per_shot_sets[sid] == set(PROV.ALL_SIGNALS)),
            "common_window_start_ms": t0,
            "common_window_end_ms": t1,
            "common_window_ms": t1 - t0,
            "grid_dt_all95_ms": (t1 - t0) / (PROV.TARGET_N - 1),
            "time_units": "ms",
            "calendar_date": "UNRESOLVED",
            "campaign_id": "UNRESOLVED",
            "operating_regime": "NOT_ASSIGNED (would be inference, not record)",
        })
    shot_inv = pd.DataFrame(si)
    shot_inv.to_csv(HERE / "FINAL_SHOT_INVENTORY.csv", index=False)

    checks = {
        "n_signals_in_archive": len(census),
        "n_signals_in_manifest": len(PROV.ALL_SIGNALS),
        "census_equals_manifest": census == sorted(PROV.ALL_SIGNALS),
        "n_signals_common_to_all_shots": len(common),
        "all_95_in_all_62": common == sorted(PROV.ALL_SIGNALS),
        "n_shots": len(shots),
        "no_duplicate_signal_ids": len(set(census)) == len(census),
        "every_signal_has_group": bool(inv.signal_group.notna().all()
                                       and (inv.signal_group != "").all()),
        "every_signal_has_semantic_type": bool(inv.semantic_type.notna().all()),
        "every_signal_has_provenance_status": bool(
            (inv.provenance_status != "").all()),
        "every_signal_in_units_registry": set(PROV.ALL_SIGNALS) == set(U),
        "group_counts": inv.signal_group.value_counts().to_dict(),
        "origin_counts": inv.source_classification.value_counts().to_dict(),
        "units_registry_sha256": units_sha,
        "signal_inventory_sha256": sha256_df(inv),
        "shot_inventory_sha256": sha256_df(shot_inv),
    }
    (HERE / "CENSUS_CHECKS.json").write_text(
        json.dumps(checks, indent=2), encoding="utf-8")

    print("S7.1R-FINAL census")
    print(f"  archive signals            : {len(census)}")
    print(f"  manifest match             : {checks['census_equals_manifest']}")
    print(f"  present in all 62 shots    : {checks['all_95_in_all_62']}")
    print(f"  shots                      : {len(shots)}")
    print("  groups:", checks["group_counts"])
    print("  origin:", checks["origin_counts"])
    print(f"  inventory sha256 : {checks['signal_inventory_sha256']}")


if __name__ == "__main__":
    main()
