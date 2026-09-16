"""S7.1R — apply addendum/correction semantics to the S7.1 artifacts.

Nothing is deleted. The original `A` block is preserved verbatim inside
O_DIIID.json under a `_s7_1_original_*` key, and each prose artifact receives an
appended correction block pointing at the addendum. Re-running is idempotent.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OBJ = HERE.parent

MARK = "<!-- S7.1R-CORRECTION -->"

FIG = r"D:\SIR_paper\General\sir_representational_prism.py"

BLOCK = f"""
{MARK}

---

## Correction — S7.1R (2026-09-02)

**Applied by addendum; nothing above has been deleted.** Full detail:
`reconciliation/O_COMPONENT_A_ADDENDUM.md`.

### `A` was read incorrectly

S7.1 read the sixth component of `O = (D, Ω_obs, S, E, Π, A)` as
**admissibility** and recorded it `NOT_INSTANTIATED`, flagging the reading as
ungrounded because no manuscript definition could be located.

An authoritative local artifact has since been found:
`{FIG}`, the manuscript's own visual-abstract figure generator. It draws the
scientific object `𝒪` and the task contract `q` as separate boxes, and lists the
contract's attributes as **"Admissibility · Information · Intended Use"**.

**Admissibility belongs to the task contract `q`, not to `𝒪`.**

`A` is therefore re-read as **ancillary observational information** — annotations
and metadata carried by the object, but not a task-conditioned admissibility
rule.

### `A` is `PARTIALLY_INSTANTIATED`, not `NOT_INSTANTIATED`

Under the corrected reading the object carries 5890 per-signal ancillary records
(62 discharges × 95 signals): upstream resampling `method` and `category`, and
original/resampled sample counts — plus signal-group membership, cohort
provenance flags, and shot identifiers. Absent: units, uncertainty, dates,
regime labels, and — despite the archive being an ELM dataset — any ELM event
annotation.

### Other S7.1 statements corrected or extended

| S7.1 statement | S7.1R |
|---|---|
| units "unknown", U002 `CRITICAL` | correct as to the *local record* — no local artifact states any unit. But 94/95 are recoverable by external convention at `STRONGLY_INFERRED`; recommend `MAJOR`. `pcdiamag3` is `UNRESOLVED` (joule hypothesis refuted by magnitude). |
| upstream pipeline "unresolved", U001 `CRITICAL` | the *operation* is characterized per signal per discharge; only the generator code is absent. Recommend `MAJOR (conditional)`. |
| "no date range or campaign identifier is recorded" | shot-number families order the cohort into 7 operational periods; U008 partially resolved (ordering, not dates). |
| 15 equilibrium quantities, ancestry undecidable | unchanged — all 15 `LINEAGE_PARTIAL`; none resolved. |

### New findings that qualify the object

- **The cohort is not homogeneous.** `ip` was resampled by `cubic_spline` in all
  35 discharges ≤ shot 187024 and by `decimate_with_antialiasing` in all 27
  ≥ shot 189646. `bt`, `prmtan_neped`, `prmtan_teped` vary likewise.
- **Unit systems are internally inconsistent**: `density` (cm⁻³) vs
  `prmtan_neped` (m⁻³); `ece*` (keV) vs `cerqtit*` (eV); `pinj` (kW) vs
  `pinj_*` (W).
- **Equilibrium quantities are ~4× oversampled** on the analysis grid (20.0 ms
  native onto a 4.96 ms median grid), reaching ~16× in 2 discharges.
- **The 20 ms question is settled** — Outcome C. See
  `reconciliation/TEMPORAL_GRID_RECONCILIATION_REPORT.md`.
"""


def append_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if MARK in text:
        return "already applied"
    path.write_text(text.rstrip() + "\n" + BLOCK, encoding="utf-8")
    return "appended"


def patch_json() -> str:
    p = OBJ / "O_DIIID.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    if "A_ancillary_information" in d:
        return "already applied"

    d["_s7_1_original_A_admissibility"] = d.pop("A_admissibility")
    d["A_ancillary_information"] = {
        "status": "PARTIALLY_INSTANTIATED",
        "reading": "ancillary observational information / annotations / "
                   "metadata carried by the object; NOT a task-conditioned "
                   "admissibility rule",
        "corrected_by": "S7.1R",
        "correction_basis": (
            "The manuscript visual-abstract figure generator "
            + FIG +
            " draws the scientific object and the task contract as separate "
            "boxes and lists the contract's attributes as 'Admissibility / "
            "Information / Intended Use'. Admissibility therefore belongs to q, "
            "not to O."
        ),
        "evidence_class": "LOCAL_DOCUMENTED (figure source)",
        "present": {
            "per_signal_per_shot_records": 5890,
            "fields": ["resample_method", "resample_category",
                       "original_length", "resampled_length"],
            "signal_group_membership": 95,
            "cohort_provenance_flags": 62,
            "shot_identifiers_and_induced_ordering": 62,
        },
        "absent": ["units", "measurement uncertainty", "calendar date",
                   "campaign identifier", "operating regime labels",
                   "ELM or other event annotations", "operator commentary"],
        "inventory": "reconciliation/ancillary_metadata_inventory.csv",
        "summary": "reconciliation/upstream_resampling_characterization.csv",
        "addendum": "reconciliation/O_COMPONENT_A_ADDENDUM.md",
    }
    d["admissibility_note"] = (
        "Admissibility is an attribute of the task contract q, not of O. It "
        "will be instantiated when a task contract is defined. No task contract "
        "exists as of S7.1R."
    )
    d["manuscript_definition_source"] = (
        "PARTIALLY_LOCATED — no prose artifact states the 6-tuple; the "
        "architecture is established from the manuscript's own visual-abstract "
        "figure generator (" + FIG + "). A prose definition in the current "
        "manuscript would supersede this and should still be sought before S7.2."
    )
    d["manuscript_definition_note"] = (
        "S7.1 recorded this as NOT_LOCATED and read A as admissibility. S7.1R "
        "corrects that reading; see _s7_1_original_A_admissibility for the "
        "original block and reconciliation/O_COMPONENT_A_ADDENDUM.md for the "
        "evidence."
    )
    d["s7_1r_corrections"] = {
        "issue_1_A_reinterpreted": True,
        "issue_2_units": "reconciliation/units_recovery_report.md",
        "issue_3_equilibrium_lineage": "reconciliation/equilibrium_lineage_audit.md",
        "issue_4_temporal_grid": "reconciliation/TEMPORAL_GRID_RECONCILIATION_REPORT.md",
        "issue_5_u001": "recommend CRITICAL -> MAJOR (conditional)",
    }
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return "patched"


def main() -> None:
    print("O_DIIID.json:", patch_json())
    for name in ("O_DIIID.md",
                 "S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE.md",
                 "S7_1_OBSERVATIONAL_OBJECT_AUDIT_REPORT.md"):
        print(f"{name}:", append_block(OBJ / name))


if __name__ == "__main__":
    main()
