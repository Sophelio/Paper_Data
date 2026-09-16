"""S7.3 stage A — parent verification, contract sanity, flag freeze, candidate
census, and per-candidate I_rec instantiation.

METADATA ONLY. This script does not open a single archive. The firewall claim
for stage A is therefore structural: there is no archive read anywhere in it.
Development values are opened only in stage B.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
S73 = HERE.parent
S7 = S73.parent
EX = S7.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
MAN = S73 / "manifests"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402  (manifest only, no I/O)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# 3. parent freeze verification
# ---------------------------------------------------------------------------
def verify_parents() -> dict:
    s71 = json.loads((R1 / "S7_1_FINAL_FREEZE.json").read_text())
    v1 = json.loads((S72 / "S7_2_FREEZE.json").read_text())
    v2 = json.loads((CV1 / "S7_2_FREEZE_V2.json").read_text())
    s71v = json.loads((S72 / "manifests" / "S7_1_INPUT_VERIFICATION.json").read_text())

    # Self-referential files cannot contain their own hash (S7.2C clause C-09).
    SELF = set(v2["self_referential_excluded"])

    def check(manifest: dict, base: Path) -> tuple[int, list]:
        ok, drift = 0, []
        for rel, h in manifest.items():
            if rel in SELF or Path(rel).name in SELF:
                continue
            p = base / rel
            if not p.exists():
                drift.append({"artifact": rel, "issue": "MISSING"})
            elif sha(p) != h:
                drift.append({"artifact": rel, "issue": "DRIFT"})
            else:
                ok += 1
        return ok, drift

    s71_ok, s71_drift = 0, []
    for k, h in s71v["canonical_raw_byte_hashes"].items():
        p = {"units_registry_sha256": S7 / "SIGNAL_UNITS.json"}.get(
            k, R1 / {
                "signal_inventory_sha256": "FINAL_SIGNAL_INVENTORY.csv",
                "shot_inventory_sha256": "FINAL_SHOT_INVENTORY.csv",
                "provenance_graph_sha256": "provenance_graph.json",
                "dalia_parity_sha256": "DALIA_SIGNAL_PARITY.csv",
                "temporal_lineage_sha256": "FINAL_TEMPORAL_LINEAGE.csv",
                "equilibrium_lineage_sha256": "equilibrium_lineage_status.csv",
                "source_inventory_sha256": "SOURCE_ARTIFACT_INVENTORY.csv",
                "quality_summary_sha256": "signal_quality_summary.csv",
            }.get(k, "__none__"))
        if p.exists() and sha(p) == h:
            s71_ok += 1
        else:
            s71_drift.append({"artifact": k, "issue": "DRIFT_OR_MISSING"})

    v1_ok, v1_drift = check(v1["all_artifact_hashes"], S72)
    v2_ok, v2_drift = check(v2["all_artifact_hashes"], CV1)

    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    drift = s71_drift + v1_drift + v2_drift
    return {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "hash_convention": "sha256 over raw file bytes (S7.2 canonical); "
                           "self-referential files excluded per S7.2C C-09",
        "s7_1": {"freeze_id": s71["freeze_id"], "status": s71["status"],
                 "n_verified": s71_ok, "drift": s71_drift},
        "s7_2_v1": {"freeze_id": v1["freeze_id"], "status": v1["status"],
                    "n_verified": v1_ok, "drift": v1_drift},
        "s7_2_v2": {"freeze_id": v2["freeze_id"], "status": v2["status"],
                    "n_verified": v2_ok, "drift": v2_drift},
        "authoritative_contract": v2["freeze_id"],
        "cohort_partition_unchanged":
            sha(S72 / "COHORT_PARTITION.json") == v1["cohort_partition_hash"],
        "n_development": part["development"]["n"],
        "n_external": part["external"]["n"],
        "K_REC_PRE_V2_unchanged":
            sha(CV1 / "K_REC_PRE_V2.json") == v2["K_REC_PRE_V2_sha256"],
        "target_selection_schema_unchanged":
            sha(CV1 / "target_selection_schema.json")
            == v2["target_selection_schema_sha256"],
        "metric_gate_definitions_unchanged":
            sha(CV1 / "metric_and_gate_definitions.json")
            == v2["metric_and_gate_definitions_sha256"],
        "n_drift_total": len(drift),
        "verdict": "PARENTS_VERIFIED" if not drift else "STOP_PARENT_DRIFT",
    }


# ---------------------------------------------------------------------------
# 4. contract notation sanity check
# ---------------------------------------------------------------------------
def contract_notation_audit() -> dict:
    M = json.loads((CV1 / "metric_and_gate_definitions.json").read_text())
    pe, pm, v3 = M["practical_equivalence"], M["primary_metric"], M["gate_V3"]
    raw_in_rule = "raw" in pe["rule"].lower() or "physical" in pe["rule"].lower()
    evidence = [
        {"field": "practical_equivalence.rule",
         "value": pe["rule"],
         "reading": "uses the bare token 'RMSE'; ambiguous IN ISOLATION"},
        {"field": "primary_metric.symbol / name",
         "value": f"{pm['symbol']} / {pm['name']}",
         "reading": "the contract's primary metric IS the normalized one"},
        {"field": "primary_metric.floor_interpretation",
         "value": pm["floor_interpretation"],
         "reading": "0.01 == 1% of the calibration sd-scale, which is only "
                    "true in NRMSE units"},
        {"field": "gate_V3.pass_condition",
         "value": v3["pass_condition"],
         "reading": "the same 0.01 magnitude is applied to differences of "
                    "NRMSE, confirming the unit"},
        {"field": "primary_metric.also_reported",
         "value": pm["also_reported"],
         "reading": "raw RMSE appears ONLY as a secondary report, never in "
                    "the equivalence rule"},
    ]
    return {
        "check": "practical equivalence must be in calibration-normalized "
                 "(NRMSE) units, not raw physical-unit RMSE",
        "explicitly_encodes_raw_rmse_in_equivalence_rule": raw_in_rule,
        "evidence": evidence,
        "verdict": "PASS_WITH_NOTATIONAL_NOTE",
        "note": (
            "The contract does NOT explicitly encode raw RMSE for practical "
            "equivalence, so the STOP condition does not apply. Four "
            "independent fields fix the unit as NRMSE. The single loose token "
            "is the bare 'RMSE' inside practical_equivalence.rule, which is "
            "shorthand within an already-fixed metric context. This is "
            "recorded here rather than silently reinterpreted."),
        "recommended_v3_editorial_fix": (
            "rewrite practical_equivalence.rule as "
            "'|NRMSE_A - NRMSE_B| <= delta_equiv' at the next contract "
            "revision; purely notational, changes no semantics"),
        "material_to_s7_3": False,
        "material_to_s7_3_reason": (
            "no model is fitted in S7.3, so the practical-equivalence rule is "
            "not exercised at this stage at all"),
    }


# ---------------------------------------------------------------------------
# 6. target-side MAJOR flag mapping -- metadata only, frozen before any value
# ---------------------------------------------------------------------------
def attach_from_metadata_sidecars() -> tuple[list, list, dict]:
    """Recompute U009 / U010 attachment from the archive metadata sidecars.

    The S7.1R interim CSV that first recorded these lists is no longer present,
    so the attachment is recomputed from its own primary source: the per-shot
    `shot_*_metadata.json` sidecars, which hold only `method`, `category`,
    `original_length` and `resampled_length` per signal.

    These sidecars are component `A` (ancillary observational information), not
    signal values. `EXTERNAL_COHORT_FIREWALL.md` explicitly permits per-signal
    resampling method and category for all discharges. **No data array is
    read.** The result is cross-checked against the counts documented in the
    frozen S7.1 record (U009 = 4, U010 = 18).
    """
    import glob
    files = sorted(glob.glob(str(EX / "data" / "resampled_data_v6"
                                 / "shot_*_metadata.json")))
    meth: dict[str, set] = {}
    ratio: dict[str, list] = {}
    for f in files:
        d = json.loads(Path(f).read_text())
        for sig, m in d.items():
            meth.setdefault(sig, set()).add(m.get("method"))
            ol, rl = m.get("original_length"), m.get("resampled_length")
            if ol:
                ratio.setdefault(sig, []).append(rl / ol)

    ANTIALIAS = "decimate_with_antialiasing"
    u009, u010 = [], []
    for sig, ms in meth.items():
        if len(ms) > 1:
            u009.append(sig)
        downsampled = any(r < 0.99 for r in ratio.get(sig, []))
        if downsampled and not all(m == ANTIALIAS for m in ms):
            u010.append(sig)
    u009, u010 = sorted(u009), sorted(u010)
    src = {
        "source": "data/resampled_data_v6/shot_*_metadata.json (62 files)",
        "fields_read": ["method", "category", "original_length",
                        "resampled_length"],
        "signal_values_read": False,
        "component": "A (ancillary observational information)",
        "firewall": "permitted for all discharges by EXTERNAL_COHORT_FIREWALL.md",
        "u009_rule": "resampling method not identical across all 62 shots",
        "u010_rule": "downsampled in some shot (length ratio < 0.99) by a "
                     "method that is not decimate_with_antialiasing",
        "u009_n": len(u009), "u010_n": len(u010),
        "documented_s7_1_counts": {"U009": 4, "U010": 18},
        "matches_documented": len(u009) == 4 and len(u010) == 18,
    }
    return u009, u010, src


def flag_mapping(inv: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    u009, u010, src = attach_from_metadata_sidecars()
    eq = list(PROV.GROUPS["equilibrium_shape"])

    rows = []
    for r in inv.itertuples():
        s = r.signal_id
        f = {
            "U001": True,                     # global: object-level
            "U003": s in eq,                  # signal-specific: EFIT outputs
            "U004": True,                     # global: object-level
            "U009": s in u009,                # signal-specific: era-varying method
            "U010": s in u010,                # signal-specific: no anti-alias
        }
        disc = [k for k in ("U003", "U009", "U010") if f[k]]
        rows.append({
            "signal_index": r.signal_index, "signal_id": s,
            "U001_upstream_generator_absent": f["U001"],
            "U003_efit_settings_unresolved": f["U003"],
            "U004_no_uncertainty_metadata": f["U004"],
            "U009_processing_era_discontinuity": f["U009"],
            "U010_downsample_without_antialias": f["U010"],
            "n_major_flags_total": sum(f.values()),
            "n_major_flags_signal_specific": len(disc),
            "signal_specific_flags": "|".join(disc),
            "ranking_key_target_side_major_flags": len(disc),
        })
    df = pd.DataFrame(rows)
    meta = {
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_before_any_signal_value_opened": True,
        "source": "frozen S7.1 MAJOR issue register only",
        "attachment": {
            "U001": {"scope": "GLOBAL", "n_signals": 95,
                     "reason": "the upstream resampling generator is absent for "
                               "the whole object; attaches equally to every "
                               "candidate and therefore does not discriminate"},
            "U003": {"scope": "SIGNAL_SPECIFIC", "n_signals": len(eq),
                     "signals": eq,
                     "reason": "EFIT settings unresolved; attaches to the 15 "
                               "equilibrium outputs only. These are already "
                               "class-excluded as targets, so U003 is NOT used "
                               "to alter the candidate set"},
            "U004": {"scope": "GLOBAL", "n_signals": 95,
                     "reason": "no uncertainty metadata anywhere in the object; "
                               "attaches equally, does not discriminate"},
            "U009": {"scope": "SIGNAL_SPECIFIC", "n_signals": len(u009),
                     "signals": u009,
                     "reason": "upstream resampling method varies across the "
                               "processing-era boundary for exactly these "
                               "signals (S7.1 evidence)"},
            "U010": {"scope": "SIGNAL_SPECIFIC", "n_signals": len(u010),
                     "signals": u010,
                     "reason": "downsampled by interpolation with no anti-alias "
                               "stage (S7.1 evidence)"},
        },
        "ranking_key_definition": (
            "target_side_major_flags = count of SIGNAL-SPECIFIC major flags "
            "(U003, U009, U010). Global flags U001 and U004 attach to every "
            "candidate identically and so add a constant that cannot change a "
            "lexicographic ordering; both are recorded per signal for the "
            "audit trail."),
        "attachment_source": src,
        "rules_observed": [
            "no new flag class invented",
            "no MODERATE or MINOR issue promoted to MAJOR",
            "no flag derived from statistical behaviour",
            "U003 not used creatively to alter the candidate set",
        ],
    }
    return df, meta


# ---------------------------------------------------------------------------
# 7. candidate census
# ---------------------------------------------------------------------------
ELIGIBLE_CLASSES = {"DIRECT_MEASUREMENT", "DIAGNOSTIC_RECONSTRUCTION"}


def candidate_census(inv: pd.DataFrame, units: dict, flags: pd.DataFrame):
    fl = flags.set_index("signal_id")
    rows = []
    for r in inv.itertuples():
        s = r.signal_id
        u = units[s]
        unit = "" if u.get("units") is None else str(u["units"]).strip()
        cls = r.source_classification
        uncal = u.get("status") == "uncalibrated"
        if cls not in ELIGIBLE_CLASSES:
            ok, why = False, f"class {cls} is normally excluded as primary target"
        elif uncal or not unit:
            ok, why = False, ("uncalibrated raw digitiser output; no resolved "
                              "physical unit")
        else:
            ok, why = True, ""
        rows.append({
            "signal_index": r.signal_index, "signal": s,
            "class": cls, "physical_unit": unit,
            "units_status": u.get("status"),
            "family": r.signal_group,
            "description": u.get("description", ""),
            "candidate_class_pass": ok,
            "candidate_class_failure_reason": why,
            "target_side_major_flags": str(fl.loc[s, "signal_specific_flags"] or ""),
            "target_side_major_flag_count":
                int(fl.loc[s, "ranking_key_target_side_major_flags"]),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 10/11. sibling subfamilies -- scientific meaning, not provider group
# ---------------------------------------------------------------------------
def sibling_subfamilies(units: dict) -> dict:
    """Same physical quantity measured on a channel/chord series.

    S7.2 named four multichannel provider families. S7.3 section 11 directs
    that a provider grouping is not by itself a sibling relation: the purpose
    of sibling exclusion is to prevent trivial same-quantity channel
    interpolation, not to discard unrelated measurements that happen to share a
    diagnostic system.

    The CER provider group therefore splits into two sibling subfamilies. CER
    toroidal rotation is a velocity (m/s) and CER ion temperature is a
    temperature (eV): different physical quantities, different dimensions,
    different scientific descriptions. They are siblings WITHIN each series and
    not siblings ACROSS the two.
    """
    ece = sorted([s for s in units if s.startswith("ece")],
                 key=lambda s: int(s[3:]))
    rot = sorted([s for s in units if s.startswith("cerqrott")],
                 key=lambda s: int(s[8:]))
    tit = sorted([s for s in units if s.startswith("cerqtit")],
                 key=lambda s: int(s[7:]))
    fs = sorted(s for s in units if s.startswith("fs"))
    beam = sorted(s for s in units if s.startswith("pinj_"))
    return {
        "ece_electron_temperature": ece,
        "cer_toroidal_rotation": rot,
        "cer_ion_temperature": tit,
        "filterscope_dalpha": fs,
        "beamline_injected_power": beam,
    }


# Definitional relations, from frozen descriptions only (no values).
def definitional_map() -> dict:
    beams = [f"pinj_{b}" for b in ("15l", "15r", "21l", "21r", "30l", "30r",
                                   "33l", "33r")]
    d = {b: ["pinj"] for b in beams}     # total contains each beamline
    d["pinj"] = list(beams)              # and is exactly their sum
    return d


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)

    par = verify_parents()
    (MAN / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(par, indent=2), encoding="utf-8")
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: parent freeze drift")

    note = contract_notation_audit()
    (MAN / "CONTRACT_NOTATION_AUDIT.json").write_text(
        json.dumps(note, indent=2), encoding="utf-8")
    if note["explicitly_encodes_raw_rmse_in_equivalence_rule"]:
        raise SystemExit("STOP: PRETARGET_CONTRACT_NOTATIONAL_CORRECTION_REQUIRED")

    inv = pd.read_csv(R1 / "FINAL_SIGNAL_INVENTORY.csv")
    units = json.loads((S7 / "SIGNAL_UNITS.json").read_text())["signals"]

    flags, flag_meta = flag_mapping(inv)
    flags.to_csv(S73 / "target_flag_mapping.csv", index=False)
    flag_meta["sha256_target_flag_mapping_csv"] = sha(S73 / "target_flag_mapping.csv")
    (MAN / "TARGET_FLAG_MAPPING_FREEZE.json").write_text(
        json.dumps(flag_meta, indent=2), encoding="utf-8")

    cen = candidate_census(inv, units, flags)
    cen.to_csv(S73 / "candidate_target_census.csv", index=False)

    subfam = sibling_subfamilies(units)
    sib_of = {s: name for name, mem in subfam.items() for s in mem}
    defmap = definitional_map()
    eq = set(PROV.GROUPS["equilibrium_shape"])
    fam = dict(zip(inv.signal_id, inv.signal_group))
    nat = dict(zip(inv.signal_id, inv.native_dt_median))
    allsig = list(inv.signal_id)

    # ---- per-candidate I_rec ------------------------------------------
    rows = []
    for r in cen[cen.candidate_class_pass].itertuples():
        y = r.signal
        sibs = [s for s in subfam.get(sib_of.get(y, ""), []) if s != y]
        deps = [s for s in defmap.get(y, []) if s != y]
        excl = {}
        for s in allsig:
            if s == y:
                excl[s] = ("R1_target_itself", "the target")
            elif s in deps:
                excl[s] = ("R3_definitional",
                           "definitionally contains or is exactly composed of "
                           "the target")
            elif s in eq:
                excl[s] = ("R5_unresolved_ancestry",
                           "LINEAGE_PARTIAL: EFIT settings/inputs unresolved, "
                           "so independence from the target cannot be "
                           "certified (fail-closed)")
            elif s in sibs:
                excl[s] = ("SIBLING",
                           "same-quantity channel sibling; excluded from the "
                           "primary boundary")
        surv = [s for s in allsig if s not in excl]
        surv_full = [s for s in allsig if s not in excl or excl[s][0] == "SIBLING"]
        fams = sorted({fam[s] for s in surv})
        coarse = max([nat[s] for s in surv] + [nat[y]])
        rows.append({
            "target": y, "signal_index": r.signal_index,
            "target_family": fam[y],
            "sibling_subfamily": sib_of.get(y, ""),
            "sibling_set": "|".join(sibs),
            "n_siblings_excluded_primary": len(sibs),
            "n_total_O_signals": len(allsig),
            "n_target_removed": 1,
            "n_alias_removed": 0,
            "n_definitional_descendants_removed": len(deps),
            "n_verified_ancestry_removed": 0,
            "n_unresolved_ancestry_removed": len(eq),
            "n_siblings_removed": len(sibs),
            "n_primary_surviving_predictors": len(surv),
            "n_provenance_certified_primary_predictors": len(surv),
            "n_distinct_scientific_families_surviving": len(fams),
            "surviving_families": "|".join(fams),
            "n_predictors_full_boundary": len(surv_full),
            "coarsest_admitted_native_dt_ms": coarse,
            "primary_grid_dt_ms": coarse,
            "binding_signal_family": "|".join(sorted(
                {fam[s] for s in surv + [y] if nat[s] == coarse})),
        })
    bs = pd.DataFrame(rows)
    bs.to_csv(S73 / "target_boundary_summary.csv", index=False)

    (MAN / "SIBLING_SUBFAMILY_RULE.json").write_text(json.dumps({
        "rule": "a sibling subfamily is a set of channels measuring the SAME "
                "physical quantity on a channel/chord series",
        "test": "same dimensional signature AND same scientific-description "
                "stem AND an indexed channel series",
        "provider_group_is_not_sufficient": True,
        "s7_2_named_families": ["ECE (40)", "CER rotation and ion temperature "
                               "(14)", "beams (10)", "filterscopes (4)"],
        "s7_3_refinement": (
            "the CER provider group splits into two sibling subfamilies. CER "
            "toroidal rotation is a velocity and CER ion temperature is a "
            "temperature: different physical quantities, different dimensions, "
            "different descriptions. Siblings within each series, not across "
            "them. This follows the frozen purpose of the sibling rule -- "
            "preventing trivial same-quantity channel interpolation -- rather "
            "than the provider grouping label."),
        "resolved_without_signal_values": True,
        "subfamilies": {k: {"n": len(v), "members": v} for k, v in subfam.items()},
        "not_sibling_families": {
            "magnetics": "bt, ip, pcbcoil, pcdiamag3, vsurf are five distinct "
                         "quantities, not a channel series",
            "density_group": "line-averaged density, pedestal density and "
                             "pedestal temperature are distinct quantities",
            "gas_injection": "four separate manifolds; treated as actuation, "
                             "and not a same-quantity channel series of a "
                             "measured plasma quantity",
        },
        "ambiguity_sensitivity_tested_in_stage_C": True,
    }, indent=2), encoding="utf-8")

    print(f"parents            : {par['verdict']}  "
          f"(S7.1 {par['s7_1']['n_verified']}, V1 {par['s7_2_v1']['n_verified']}, "
          f"V2 {par['s7_2_v2']['n_verified']} verified)")
    print(f"contract notation  : {note['verdict']}")
    print(f"flag mapping frozen: U009 {flag_meta['attachment']['U009']['n_signals']}, "
          f"U010 {flag_meta['attachment']['U010']['n_signals']}, "
          f"U003 {flag_meta['attachment']['U003']['n_signals']}")
    print(f"candidates         : {int(cen.candidate_class_pass.sum())}/95 pass class")
    print(f"  failures         : "
          f"{cen[~cen.candidate_class_pass].candidate_class_failure_reason.value_counts().to_dict()}")
    print(f"I_rec instantiated : {len(bs)} candidates")
    print(f"  surviving predictors range {bs.n_primary_surviving_predictors.min()}"
          f"-{bs.n_primary_surviving_predictors.max()}")
    print("NO ARCHIVE OPENED IN STAGE A")


if __name__ == "__main__":
    main()
