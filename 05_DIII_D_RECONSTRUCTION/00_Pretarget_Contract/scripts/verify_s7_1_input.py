"""S7.2 step 0 — verify the frozen S7.1 input before anything else.

Hashing note -- a defect in the S7.1 freeze, found here
-------------------------------------------------------
The S7.1 freeze did NOT use one hash method. `sha256_df(df)` was applied to
whichever DataFrame was in hand:

  * artifacts built in memory during the freeze step were hashed directly, and
    because each was written with `df.to_csv(path, index=False)` those hashes
    equal the **raw file bytes**;
  * artifacts re-read from disk first (`FINAL_SIGNAL_INVENTORY.csv`,
    `signal_quality_summary.csv`) were hashed after a `pd.read_csv` round trip,
    which reformats floats (`0.0200` -> `0.02`), so those hashes do **not**
    equal the file bytes.

Both are stable and reproducible; they are simply different rules. A verifier
applying either rule uniformly reports false drift on the other subset.

The files themselves are unmodified. This verifier therefore checks each
artifact under **both** rules and requires at least one to match, records which
rule applied, and emits a uniform `canonical_raw_byte_hashes` set so that S7.2
and later stages have a single rule. The S7.1 freeze file is not modified.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
S72 = HERE.parent
S7 = S72.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
UNITS = S7 / "SIGNAL_UNITS.json"

# freeze key -> file whose raw bytes were hashed
HASHED = {
    "signal_inventory_sha256": R1 / "FINAL_SIGNAL_INVENTORY.csv",
    "shot_inventory_sha256": R1 / "FINAL_SHOT_INVENTORY.csv",
    "units_registry_sha256": UNITS,
    "provenance_graph_sha256": R1 / "provenance_graph.json",
    "dalia_parity_sha256": R1 / "DALIA_SIGNAL_PARITY.csv",
    "temporal_lineage_sha256": R1 / "FINAL_TEMPORAL_LINEAGE.csv",
    "equilibrium_lineage_sha256": R1 / "equilibrium_lineage_status.csv",
    "source_inventory_sha256": R1 / "SOURCE_ARTIFACT_INVENTORY.csv",
    "quality_summary_sha256": R1 / "signal_quality_summary.csv",
}

# read but not hash-pinned by the freeze; presence and shape are checked
ALSO_READ = [
    R1 / "SIGNAL_ORIGIN_CLASSIFICATION.csv",
    R1 / "semantic_types_and_units.csv",
    R1 / "SIGNAL_UNITS_AUDIT.csv",
    R1 / "COHORT_PROVENANCE.md",
    R1 / "TEMPORAL_GRID_FINAL_VERDICT.md",
    R1 / "O_DIIID_FINAL.json",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    freeze = json.loads((R1 / "S7_1_FINAL_FREEZE.json").read_text())
    O = json.loads((R1 / "O_DIIID_FINAL.json").read_text())

    hashes, drift, canonical = {}, [], {}
    for key, path in HASHED.items():
        exp = freeze[key]
        raw = sha256(path)
        rt = None
        if path.suffix == ".csv":
            rt = hashlib.sha256(
                pd.read_csv(path).to_csv(index=False).encode("utf-8")
            ).hexdigest()
        rule = ("raw_file_bytes" if raw == exp
                else "read_csv_round_trip" if rt == exp else None)
        hashes[key] = {
            "file": str(path), "expected_in_freeze": exp,
            "raw_file_bytes": raw, "read_csv_round_trip": rt,
            "matched_rule": rule, "match": rule is not None,
        }
        canonical[key] = raw
        if rule is None:
            drift.append(key)

    missing = [str(p) for p in ALSO_READ if not p.exists()]

    inv = pd.read_csv(R1 / "FINAL_SIGNAL_INVENTORY.csv")
    shots = pd.read_csv(R1 / "FINAL_SHOT_INVENTORY.csv", dtype={"shot_id": str})
    qual = pd.read_csv(R1 / "signal_quality_summary.csv", dtype={"shot_id": str})
    par = pd.read_csv(R1 / "DALIA_SIGNAL_PARITY.csv")
    eq = pd.read_csv(R1 / "equilibrium_lineage_status.csv")
    units = json.loads(UNITS.read_text())["signals"]

    n_unit = sum(1 for v in units.values()
                 if v.get("units") not in (None, "") and str(v["units"]).strip())
    n_uncal = sum(1 for v in units.values() if v.get("status") == "uncalibrated")

    expectations = {
        "n_signals_95": len(inv) == 95,
        "n_shots_62": len(shots) == 62,
        "n_pairs_5890": len(qual) == 5890,
        "backend_accessible_95_of_95": int((par.verdict == "EXACT_IDENTITY").sum()) == 95,
        "unit_determinations_95_of_95": (n_unit + n_uncal) == 95,
        "no_critical_s7_1_issues": freeze["unresolved_critical_count"] == 0,
        "parent_status_frozen": freeze["status"].startswith("FROZEN"),
        "parent_acceptance_all_passed":
            freeze["acceptance_passed"].split("/")[0]
            == freeze["acceptance_passed"].split("/")[1],
        "equilibrium_15_lineage_partial":
            len(eq) == 15 and bool((eq.lineage_status == "LINEAGE_PARTIAL").all()),
        "E_not_instantiated":
            O["E_uncertainty_model"]["status"] == "NOT_INSTANTIATED",
        "no_target_encoded": not any(O["gate"].values()),
        "all_supporting_files_present": not missing,
    }

    ok = not drift and all(expectations.values())
    out = {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "parent_freeze_id": freeze["freeze_id"],
        "parent_status": freeze["status"],
        "parent_acceptance": freeze["acceptance_passed"],
        "hash_method": (
            "dual-rule: each artifact matched against the freeze under both "
            "raw-file-bytes and read_csv-round-trip; at least one must match. "
            "See module docstring -- the S7.1 freeze used a mixed method."),
        "hashes": hashes,
        "n_hashes_checked": len(HASHED),
        "n_hash_drift": len(drift),
        "drifted_keys": drift,
        "s7_1_freeze_defect": {
            "found": True,
            "severity": "MINOR (record-keeping, not data)",
            "description": (
                "The S7.1 freeze recorded hashes under two different rules. "
                "Artifacts built in memory were hashed as written to disk; "
                "FINAL_SIGNAL_INVENTORY.csv and signal_quality_summary.csv "
                "were re-read with pd.read_csv first, which reformats floats, "
                "so their recorded hashes do not equal the file bytes."),
            "artifacts_under_round_trip_rule": [
                k for k, v in hashes.items()
                if v["matched_rule"] == "read_csv_round_trip"],
            "artifacts_under_raw_bytes_rule": [
                k for k, v in hashes.items()
                if v["matched_rule"] == "raw_file_bytes"],
            "data_integrity_impact": "NONE -- every file verifies under one of "
                                     "the two rules; no content changed",
            "remedy": "S7.2 and later stages use canonical_raw_byte_hashes "
                      "below as the single rule. The S7.1 freeze file is left "
                      "unmodified.",
        },
        "canonical_raw_byte_hashes": canonical,
        "expectations": expectations,
        "missing_supporting_files": missing,
        "object_summary": {
            "n_discharges": len(shots), "n_signals": len(inv),
            "n_signal_discharge_pairs": len(qual),
            "backend_accessible": f"{int((par.verdict=='EXACT_IDENTITY').sum())}/95",
            "units_with_physical_unit": n_unit,
            "units_uncalibrated": n_uncal,
            "origin_classification": inv.source_classification.value_counts().to_dict(),
            "families": inv.signal_group.value_counts().to_dict(),
        },
        "verdict": "S7_1_INPUT_VERIFIED" if ok else "STOP_S7_1_INPUT_FAILED",
    }
    (S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print(f"parent: {freeze['freeze_id']}  {freeze['status']}  "
          f"{freeze['acceptance_passed']}")
    print(f"hashes: {len(HASHED)-len(drift)}/{len(HASHED)} match")
    for k, v in expectations.items():
        print(f"  {'OK  ' if v else 'FAIL'} {k}")
    print(f"VERDICT: {out['verdict']}")
    if not ok:
        raise SystemExit("STOP: S7.1 input verification failed")


if __name__ == "__main__":
    main()
