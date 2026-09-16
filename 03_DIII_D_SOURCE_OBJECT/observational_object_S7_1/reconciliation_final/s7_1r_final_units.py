"""S7.1R-FINAL step 1 — audit and complete SIGNAL_UNITS.json.

Applies one domain-authorized correction: the 40 ECE radiometer channels are
electron-temperature channels measured in keV.

Safety rules enforced here:
  * hash before and after;
  * the ECE set is identified from the registry, not assumed;
  * STOP if any ECE entry already carries a conflicting unit;
  * no non-ECE entry is touched;
  * JSON is re-validated after writing;
  * unit completeness is counted programmatically, not assumed.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OBJ = HERE.parent
S7 = OBJ.parent
UNITS = S7 / "SIGNAL_UNITS.json"

ECE_UNIT = "keV"
ECE_EVIDENCE = "DOMAIN_AUTHORIZED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    pre = sha256(UNITS)
    (HERE / "SIGNAL_UNITS.pre_S7_1R.sha256").write_text(
        f"{pre}  SIGNAL_UNITS.json\n", encoding="utf-8")
    shutil.copy2(UNITS, HERE / "SIGNAL_UNITS.pre_S7_1R.json")

    doc = json.loads(UNITS.read_text(encoding="utf-8"))
    sig = doc["signals"]
    before = {k: dict(v) for k, v in sig.items()}

    # --- identify the ECE temperature channels from the registry itself -----
    ece = sorted(
        k for k, v in sig.items()
        if "ECE radiometer" in str(v.get("description", ""))
    )
    by_name = sorted(k for k in sig if k.startswith("ece"))
    if set(ece) != set(by_name):
        raise SystemExit(
            f"STOP: description-based ECE set ({len(ece)}) differs from "
            f"name-based set ({len(by_name)}): "
            f"{sorted(set(ece) ^ set(by_name))}"
        )
    if len(ece) != 40:
        raise SystemExit(f"STOP: expected 40 ECE channels, found {len(ece)}")

    # --- refuse to overwrite a conflicting unit -----------------------------
    conflicts = [
        (k, sig[k].get("units")) for k in ece
        if sig[k].get("units") not in (None, "")
        and str(sig[k].get("units")).strip() != ECE_UNIT
    ]
    if conflicts:
        raise SystemExit(
            f"STOP: {len(conflicts)} ECE entries already carry a conflicting "
            f"unit; not overwriting: {conflicts}"
        )

    # --- apply --------------------------------------------------------------
    changed = []
    for k in ece:
        if sig[k].get("units") == ECE_UNIT:
            continue
        sig[k]["units"] = ECE_UNIT
        sig[k]["status"] = "domain_authorized"
        sig[k]["evidence_class"] = ECE_EVIDENCE
        sig[k]["note"] = (
            "Upstream units attribute is empty on all shots. Unit supplied as "
            "an explicit domain-authorized correction during S7.1R-FINAL "
            "(2026-09-02): the ECE radiometer reports electron temperature in "
            "keV. This is expert assignment, not recovered metadata."
        )
        changed.append(k)

    doc["status_meanings"]["domain_authorized"] = (
        "No upstream unit string exists; the unit was supplied by an "
        "authorized domain expert and is recorded as such."
    )

    # --- recount, do not assume --------------------------------------------
    with_unit = [k for k, v in sig.items()
                 if v.get("units") not in (None, "") and str(v["units"]).strip()]
    uncal = [k for k, v in sig.items() if v.get("status") == "uncalibrated"]
    still_null = [k for k, v in sig.items()
                  if (v.get("units") in (None, "")
                      or not str(v.get("units")).strip())
                  and v.get("status") != "uncalibrated"]

    doc["summary"]["by_status"] = (
        pd.Series([v.get("status") for v in sig.values()])
        .value_counts().to_dict()
    )
    doc["summary"]["unresolved_signals"] = sorted(still_null)
    doc["summary"]["s7_1r_final"] = {
        "n_signals": len(sig),
        "n_with_physical_unit": len(with_unit),
        "n_uncalibrated_no_unit_exists": len(uncal),
        "n_genuinely_unresolved": len(still_null),
        "ece_channels_assigned_keV": len(changed),
        "note": (
            "The two uncalibrated signals have no physical unit to record; "
            "upstream reports 'raw'. They are RESOLVED as unit-less, not "
            "missing."
        ),
    }
    doc["s7_1r_final_correction"] = {
        "applied_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.1R-FINAL",
        "change": f"assigned units='{ECE_UNIT}' to {len(changed)} ECE channels",
        "evidence_class": ECE_EVIDENCE,
        "authorized_by": "user (domain expert), explicit instruction",
        "pre_sha256": pre,
        "signals_changed": changed,
        "signals_untouched": len(sig) - len(changed),
    }

    UNITS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    # --- re-validate --------------------------------------------------------
    reread = json.loads(UNITS.read_text(encoding="utf-8"))
    assert len(reread["signals"]) == 95
    assert all(reread["signals"][k]["units"] == ECE_UNIT for k in ece)
    untouched_ok = all(
        reread["signals"][k] == before[k] for k in before if k not in ece
    )
    if not untouched_ok:
        raise SystemExit("STOP: a non-ECE entry changed unexpectedly")

    post = sha256(UNITS)
    (HERE / "SIGNAL_UNITS.post_S7_1R.sha256").write_text(
        f"{post}  SIGNAL_UNITS.json\n", encoding="utf-8")

    # --- audit table --------------------------------------------------------
    rows = []
    for k, v in reread["signals"].items():
        prev = before[k].get("units")
        rows.append({
            "signal": k,
            "group": v.get("group", ""),
            "previous_unit": "" if prev is None else prev,
            "final_unit": "" if v.get("units") is None else v["units"],
            "status": v.get("status"),
            "evidence_class": v.get(
                "evidence_class",
                "LOCAL_DOCUMENTED" if v.get("status") != "uncalibrated"
                else "LOCAL_DOCUMENTED"),
            "changed_in_S7_1R": k in changed,
            "has_physical_unit": bool(
                v.get("units") not in (None, "") and str(v["units"]).strip()),
            "notes": v.get("note", ""),
        })
    df = pd.DataFrame(rows).sort_values("signal").reset_index(drop=True)
    df.to_csv(HERE / "SIGNAL_UNITS_AUDIT.csv", index=False)

    print("SIGNAL_UNITS.json — S7.1R-FINAL")
    print(f"  pre  sha256 : {pre}")
    print(f"  post sha256 : {post}")
    print(f"  ECE channels assigned keV : {len(changed)}")
    print(f"  non-ECE entries changed   : 0 (verified)")
    print(f"  signals with a physical unit : {len(with_unit)}/95")
    print(f"  uncalibrated (no unit exists): {len(uncal)}/95 -> {uncal}")
    print(f"  genuinely unresolved         : {len(still_null)}/95")


if __name__ == "__main__":
    main()
