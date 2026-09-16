"""S7.9 step A - lineage verification, reuse preconditions, canonical parse,
input-matrix integrity.

Hard gates. Nothing downstream may run unless this exits 0.

Opens NO external value of any kind. External artifacts are read for METADATA
only (ids, era, counts), never for signal or target values.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
V2 = S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"
S78 = S7 / "08_utility_and_qualification_rules"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def depth_split(s: str) -> list:
    """Frozen canonical parser: split on pipes at parenthesis depth 0 ONLY."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "|" and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


LINEAGE = [
    ("S7.1", "01_observational_object/reconciliation_final/S7_1_FINAL_FREEZE.json"),
    ("S7.2 V1", "02_reconstruction_contract/S7_2_FREEZE.json"),
    ("S7.2 V2", "02_reconstruction_contract/correction_v1/S7_2_FREEZE_V2.json"),
    ("S7.3R V2", "03_target_feasibility_and_boundary/reconciliation_source_resolution/S7_3_FREEZE_V2.json"),
    ("S7.4 V2", "04_mathematical_interpretation/retry_source_resolution_v2/S7_4_FREEZE_V2.json"),
    ("S7.5 V1", "05_typed_relational_ontology/S7_5_FREEZE.json"),
    ("S7.5H V1", "05H_primitive_space_and_ontology_hardening/S7_5H_FREEZE.json"),
    ("S7.6R V2", "06_admissible_universe/hardened_v2/S7_6R_FREEZE.json"),
    ("S7.7R V2", "07_search_policy_and_frontier/one_seed_primary_v2/S7_7R_FREEZE.json"),
    ("S7.8 V1", "08_utility_and_qualification_rules/S7_8_FREEZE.json"),
]
HISTORICAL = [
    ("S7.3 V1", "03_target_feasibility_and_boundary/S7_3_FREEZE.json"),
    ("S7.4 V1", "04_mathematical_interpretation/S7_4_FREEZE.json"),
    ("S7.6 V1", "06_admissible_universe/S7_6_FREEZE.json"),
    ("S7.7 V1", "07_search_policy_and_frontier/S7_7_FREEZE.json"),
]


def main() -> int:
    drift = []

    # ---------------- 1. lineage -----------------------------------------
    lineage = []
    for label, rel in LINEAGE + HISTORICAL:
        p = S7 / rel
        if not p.exists():
            drift.append("MISSING PARENT FREEZE: " + rel)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        lineage.append({
            "stage": label,
            "authoritative": (label, rel) in LINEAGE,
            "path": rel,
            "freeze_id": d.get("freeze_id"),
            "status": d.get("status"),
            "file_sha256": sha256(p),
        })

    # ---------------- 2. S7.8 manifest recomputation ----------------------
    f8 = json.loads((S78 / "S7_8_FREEZE.json").read_text(encoding="utf-8"))
    m8 = {"n_recorded": len(f8["all_artifact_hashes"]), "n_matched": 0, "mismatched": []}
    for rel, want in f8["all_artifact_hashes"].items():
        p = S78 / rel
        if p.exists() and sha256(p) == want:
            m8["n_matched"] += 1
        else:
            m8["mismatched"].append(rel)
    if m8["mismatched"]:
        drift.append("S7.8 artifact manifest does not reproduce")
    if f8["status"] != "FROZEN_READY_FOR_S7.9":
        drift.append("S7.8 status is not FROZEN_READY_FOR_S7.9")

    # ---------------- 3. five reuse preconditions -------------------------
    f7 = json.loads((V2 / "S7_7R_FREEZE.json").read_text(encoding="utf-8"))
    m7 = {"n_recorded": len(f7["all_artifact_hashes"]), "n_matched": 0, "mismatched": []}
    for rel, want in f7["all_artifact_hashes"].items():
        p = V2 / rel
        if p.exists() and sha256(p) == want:
            m7["n_matched"] += 1
        else:
            m7["mismatched"].append(rel)

    reg = pd.read_csv(V2 / "explored_support_registry.csv")
    ex = np.load(V2 / "explored_per_cell_nrmse.npz", allow_pickle=True)
    at = np.load(V2 / "atomic_per_cell_nrmse.npz", allow_pickle=True)
    cells = [str(c) for c in ex["cells"]]
    cohort = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json"
                         ).read_text(encoding="utf-8"))
    dev_shots = [str(s) for s in cohort["development"]["shot_ids"]]
    mgd = json.loads((S7 / "02_reconstruction_contract" / "correction_v1"
                      / "metric_and_gate_definitions.json").read_text(encoding="utf-8"))
    prox = json.loads((V2 / "manifests" / "PROXY_EQUIVALENCE.json").read_text(encoding="utf-8"))
    est = json.loads((S78 / "estimator_policy.json").read_text(encoding="utf-8"))

    array_ids = set(str(x) for x in ex["support_id"]) | set(str(x) for x in at["coordinate_id"])
    reg_ids = set(reg.support_id)

    pre = {
        "1_hashes": {
            "requirement": "S7.7R artifact hashes match the recorded manifest",
            "n_matched": m7["n_matched"], "n_recorded": m7["n_recorded"],
            "passed": m7["n_matched"] == m7["n_recorded"],
        },
        "2_estimator_equivalence": {
            "requirement": "DEVELOPMENT_RELATION_OLS_V1 == SEARCH_PROXY_OLS_V1 for the fit criterion",
            "search_proxy_max_relative_deviation": prox["max_relative_deviation"],
            "tolerance": prox["tolerance"],
            "s7_7r_check_passes": bool(prox["passes"]),
            "s7_8_declares_equivalence": est["search_proxy_equivalence"]["algebraic_relation"],
            "passed": bool(prox["passes"]),
        },
        "3_metric_equivalence": {
            "requirement": "NRMSE definition, calibration scale and ddof unchanged",
            "scale_definition": mgd["primary_metric"]["scale_definition"],
            "ddof": mgd["primary_metric"]["ddof"],
            "zero_scale_behaviour": mgd["primary_metric"]["zero_scale_behaviour"],
            "epsilon_added": mgd["primary_metric"]["epsilon_added"],
            "passed": (mgd["primary_metric"]["ddof"] == 0
                       and mgd["primary_metric"]["epsilon_added"] is False),
        },
        "4_support_identity": {
            "requirement": "canonical support_id set matches Ahat_rec exactly",
            "registry_rows": int(len(reg)),
            "array_ids": len(array_ids),
            "bijective": bool(array_ids == reg_ids and len(reg_ids) == len(reg)),
            "passed": bool(array_ids == reg_ids and len(reg_ids) == len(reg) == 162845),
        },
        "5_block_identity": {
            "requirement": "60 cells over the 20 frozen development discharges and blocks A/B/C",
            "n_cells": len(cells),
            "shots_match_cohort": sorted({c.split(":")[0] for c in cells}) == sorted(dev_shots),
            "blocks": sorted({c.split(":")[1] for c in cells}),
            "passed": (len(cells) == 60
                       and sorted({c.split(":")[0] for c in cells}) == sorted(dev_shots)
                       and sorted({c.split(":")[1] for c in cells}) == ["A", "B", "C"]),
        },
    }
    all_pre = all(v["passed"] for v in pre.values())
    reuse_verdict = "ARRAY_REUSE_AUTHORISED" if all_pre else "ARRAY_REUSE_REFUSED"
    if not all_pre:
        drift.append("array reuse preconditions failed")

    # ---------------- 4. canonical parse hard gate ------------------------
    parsed = [depth_split(s) for s in reg.support_id]
    parsed_n = np.array([len(p) for p in parsed])
    naive_n = np.array([len(str(s).split("|")) for s in reg.support_id])
    reserial = np.array(["|".join(p) for p in parsed])
    size_ok = int((parsed_n == reg.support_size.values).sum())
    reser_ok = int((reserial == reg.support_id.values).sum())
    sorted_ok = int(sum(1 for p in parsed if p == sorted(p)))
    parse = {
        "parser": "parenthesis-depth-aware split at depth 0 (frozen S7.8 rule)",
        "naive_parser_used_operationally": False,
        "rows": int(len(reg)),
        "support_size_checksum": "%d/%d" % (size_ok, len(reg)),
        "canonical_reserialization_checksum": "%d/%d" % (reser_ok, len(reg)),
        "atoms_ascending_sorted": "%d/%d" % (sorted_ok, len(reg)),
        "naive_split_would_misparse_rows": int((naive_n != reg.support_size.values).sum()),
        "naive_split_would_misparse_fraction": float((naive_n != reg.support_size.values).mean()),
        "historical_audit_reference_rows": 116608,
        "historical_audit_reference_fraction": 0.716,
        "passed": size_ok == len(reg) == 162845 and reser_ok == len(reg) and sorted_ok == len(reg),
    }
    if not parse["passed"]:
        drift.append("CANONICAL_SUPPORT_PARSE_FAILURE")

    # ---------------- 5. input matrix integrity ---------------------------
    E = ex["nrmse"]
    A = at["nrmse"]
    n_finite = int(np.isfinite(E).sum() + np.isfinite(A).sum())
    matrix = {
        "candidate_count": int(E.shape[0] + A.shape[0]),
        "cell_count": int(E.shape[1]),
        "development_discharges": len({c.split(":")[0] for c in cells}),
        "blocks_per_discharge": len({c.split(":")[1] for c in cells}),
        "expected_finite_cells": 162845 * 60,
        "observed_finite_cells": n_finite,
        "all_finite": n_finite == 162845 * 60,
        "explored_atomic_id_overlap": len(set(str(x) for x in ex["support_id"])
                                          & set(str(x) for x in at["coordinate_id"])),
        "bijective_map_to_registry": pre["4_support_identity"]["bijective"],
        "row_order_assumed": False,
        "row_order_note": "rows are joined to the registry BY support_id, never by position",
        "passed": (E.shape[0] + A.shape[0] == 162845 and E.shape[1] == 60
                   and n_finite == 162845 * 60),
    }
    if not matrix["passed"]:
        drift.append("input matrix integrity failed")

    # ---------------- 6. contract facts -----------------------------------
    s73 = json.loads((S7 / "03_target_feasibility_and_boundary"
                      / "reconciliation_source_resolution" / "S7_3_FREEZE_V2.json"
                      ).read_text(encoding="utf-8"))
    u8 = json.loads((S78 / "U_REC_OPERATIONAL_V1.json").read_text(encoding="utf-8"))
    v8 = json.loads((S78 / "V_REC_OPERATIONAL_V1.json").read_text(encoding="utf-8"))
    cf8 = json.loads((S78 / "manifests" / "CARRY_FORWARD_FINDINGS.json").read_text(encoding="utf-8"))

    facts = {
        "target": s73["selected_target"],
        "external_cohort_n": int(cohort["external"]["n"]),
        "external_by_era": {k: int(v) for k, v in cohort["external"]["by_era"].items()},
        "external_state": "SEALED",
        "Ahat_rec": int(len(reg)),
        "search_policy": f7["sigma_rec_id"],
        "U_rec": u8["utility_id"],
        "V_rec": v8["qualification_id"],
        "estimator": u8["primary_estimator"],
        "two_seed_sensitivity": f7["two_seed_sensitivity"],
        "baselines_run_upstream": int(f7["access"]["baselines_run"]),
    }
    for cond, msg in [
        (facts["target"] == "density", "target != density"),
        (facts["external_cohort_n"] == 42, "external cohort != 42"),
        (facts["external_by_era"] == {"earlier": 24, "later": 18}, "external split != 24/18"),
        (facts["Ahat_rec"] == 162845, "Ahat_rec != 162845"),
        (facts["search_policy"] == "SIGMA_REC_ONE_SEED_PRIMARY_V2", "search policy changed"),
        (facts["U_rec"] == "U_REC_OPERATIONAL_V1", "U_rec id changed"),
        (facts["V_rec"] == "V_REC_OPERATIONAL_V1", "V_rec id changed"),
        (facts["estimator"] == "DEVELOPMENT_RELATION_OLS_V1", "estimator changed"),
        (facts["two_seed_sensitivity"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
         "two-seed sensitivity state changed"),
        (facts["baselines_run_upstream"] == 0, "a baseline was run upstream"),
        (cf8["c6_c7"]["declaration"] == "NO_CONSTRUCTOR_FAMILY_PRUNING",
         "C6/C7 pruning declaration changed"),
    ]:
        if not cond:
            drift.append(msg)

    out = {
        "verification_id": "S7_9_PARENT_AND_GATE_VERIFICATION_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.9",
        "lineage": lineage,
        "n_authoritative": sum(1 for r in lineage if r["authoritative"]),
        "n_historical_preserved": sum(1 for r in lineage if not r["authoritative"]),
        "s7_8_manifest_recomputation": m8,
        "s7_7r_manifest_recomputation": m7,
        "array_reuse_preconditions": pre,
        "ARRAY_REUSE_VERDICT": reuse_verdict,
        "canonical_parse_gate": parse,
        "input_matrix_integrity": matrix,
        "contract_facts": facts,
        "drift": drift,
        "verdict": "ZERO_SUBSTANTIVE_DRIFT" if not drift else "DRIFT_DETECTED",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
    }
    (OUT / "manifests" / "PARENT_FREEZE_VERIFICATION.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print("authoritative lineage : %d/10  (+%d historical preserved)"
          % (out["n_authoritative"], out["n_historical_preserved"]))
    print("S7.8 manifest         : %d/%d" % (m8["n_matched"], m8["n_recorded"]))
    print("S7.7R manifest        : %d/%d" % (m7["n_matched"], m7["n_recorded"]))
    print("array reuse           : %s" % reuse_verdict)
    print("canonical parse       : size %s | reserialize %s | sorted %s"
          % (parse["support_size_checksum"], parse["canonical_reserialization_checksum"],
             parse["atoms_ascending_sorted"]))
    print("naive split would fail: %d rows (%.1f%%)"
          % (parse["naive_split_would_misparse_rows"],
             100 * parse["naive_split_would_misparse_fraction"]))
    print("matrix                : %d x %d, finite cells %d/%d"
          % (matrix["candidate_count"], matrix["cell_count"],
             matrix["observed_finite_cells"], matrix["expected_finite_cells"]))
    print("verdict               : %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
