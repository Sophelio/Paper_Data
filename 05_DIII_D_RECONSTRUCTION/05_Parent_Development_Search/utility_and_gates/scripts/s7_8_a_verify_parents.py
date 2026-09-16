"""S7.8 step A - lineage verification and frozen-frontier integrity.

Reads only:
  * parent freeze files and their recorded artifact manifests
  * the S7.7R explored frontier (support registry + per-cell NRMSE arrays)

Opens NO external signal value and NO external target value.
Writes NO change to any parent artifact.
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

S7 = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1]
V2 = S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def depth_split(s: str) -> list:
    """Split a canonical support_id on TOP-LEVEL pipe characters only.

    Atom signatures for C4/C6/C7/C8 (PHASE, LEVEL_RATE, RATE_OVER_LEVEL,
    LEVEL_OVER_RATE) embed a pipe INSIDE their parentheses, so a naive
    str.split on the pipe mis-parses roughly a quarter of the frontier.
    """
    out = []
    depth = 0
    cur = []
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
    ("S7.2 V2 (S7.2C)", "02_reconstruction_contract/correction_v1/S7_2_FREEZE_V2.json"),
    ("S7.3 V1 historical", "03_target_feasibility_and_boundary/S7_3_FREEZE.json"),
    ("S7.4 V1 historical", "04_mathematical_interpretation/S7_4_FREEZE.json"),
    ("S7.3R V2", "03_target_feasibility_and_boundary/reconciliation_source_resolution/S7_3_FREEZE_V2.json"),
    ("S7.4 V2", "04_mathematical_interpretation/retry_source_resolution_v2/S7_4_FREEZE_V2.json"),
    ("S7.5 V1", "05_typed_relational_ontology/S7_5_FREEZE.json"),
    ("S7.5H V1", "05H_primitive_space_and_ontology_hardening/S7_5H_FREEZE.json"),
    ("S7.6 V1 historical", "06_admissible_universe/S7_6_FREEZE.json"),
    ("S7.6R hardened V2", "06_admissible_universe/hardened_v2/S7_6R_FREEZE.json"),
    ("S7.7 V1 historical blocked", "07_search_policy_and_frontier/S7_7_FREEZE.json"),
    ("S7.7R one-seed primary V2", "07_search_policy_and_frontier/one_seed_primary_v2/S7_7R_FREEZE.json"),
]


def main() -> int:
    drift = []
    lineage_rows = []
    for label, rel in LINEAGE:
        p = S7 / rel
        if not p.exists():
            drift.append("MISSING PARENT FREEZE: " + rel)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        lineage_rows.append({
            "stage": label,
            "path": rel,
            "freeze_id": d.get("freeze_id"),
            "status": d.get("status"),
            "file_sha256": sha256(p),
        })

    # ---- S7.7R recorded manifest recomputed from disk --------------------
    r7 = json.loads((V2 / "S7_7R_FREEZE.json").read_text(encoding="utf-8"))
    recorded = r7["all_artifact_hashes"]
    manifest_check = {
        "n_recorded": len(recorded),
        "n_matched": 0,
        "mismatched": [],
        "missing": [],
    }
    for rel, want in recorded.items():
        p = V2 / rel
        if not p.exists():
            manifest_check["missing"].append(rel)
            continue
        got = sha256(p)
        if got == want:
            manifest_check["n_matched"] += 1
        else:
            manifest_check["mismatched"].append(
                {"artifact": rel, "recorded": want, "recomputed": got})
    if manifest_check["mismatched"] or manifest_check["missing"]:
        drift.append("S7.7R artifact manifest does not reproduce from disk")

    # ---- frontier integrity ---------------------------------------------
    reg = pd.read_csv(V2 / "explored_support_registry.csv")
    ex = np.load(V2 / "explored_per_cell_nrmse.npz", allow_pickle=True)
    at = np.load(V2 / "atomic_per_cell_nrmse.npz", allow_pickle=True)

    ex_ids = [str(x) for x in ex["support_id"]]
    at_ids = [str(x) for x in at["coordinate_id"]]
    cells_ex = [str(c) for c in ex["cells"]]
    cells_at = [str(c) for c in at["cells"]]

    sizes = {int(k): int(v) for k, v in
             reg.support_size.value_counts().sort_index().to_dict().items()}
    want_sizes = {int(k): int(v) for k, v in r7["supports_by_size"].items()}

    parsed = np.array([len(depth_split(s)) for s in reg.support_id])
    canonical_sorted = all(
        depth_split(s) == sorted(depth_split(s)) for s in reg.support_id)
    naive = np.array([len(str(s).split("|")) for s in reg.support_id])

    shots = sorted({c.split(":")[0] for c in cells_ex})
    blocks = sorted({c.split(":")[1] for c in cells_ex})

    cohort = json.loads(
        (S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json"
         ).read_text(encoding="utf-8"))
    dev_shots = [str(s) for s in cohort["development"]["shot_ids"]]

    frontier = {
        "frontier_id": r7["frontier_id"],
        "sigma_rec_id": r7["sigma_rec_id"],
        "registry_rows": int(len(reg)),
        "registry_unique_support_ids": int(reg.support_id.nunique()),
        "Ahat_rec_cardinality_recorded": int(r7["Ahat_rec_cardinality"]),
        "singleton_supports": int(sizes.get(1, 0)),
        "multivariate_supports": int(len(reg) - sizes.get(1, 0)),
        "supports_by_size": sizes,
        "supports_by_size_matches_freeze": sizes == want_sizes,
        "support_size_min": int(reg.support_size.min()),
        "support_size_max": int(reg.support_size.max()),
        "per_cell_arrays": {
            "explored_rows": int(ex["nrmse"].shape[0]),
            "atomic_rows": int(at["nrmse"].shape[0]),
            "union_rows": int(ex["nrmse"].shape[0] + at["nrmse"].shape[0]),
            "n_cells": int(ex["nrmse"].shape[1]),
            "cells_identical_across_files": cells_ex == cells_at,
            "explored_atomic_id_overlap": len(set(ex_ids) & set(at_ids)),
            "all_cells_finite_explored": bool(np.isfinite(ex["nrmse"]).all()),
            "all_cells_finite_atomic": bool(np.isfinite(at["nrmse"]).all()),
            "dtype": str(ex["nrmse"].dtype),
        },
        "canonical_id": {
            "separator": "top-level pipe at parenthesis depth 0",
            "naive_split_is_unsafe": True,
            "naive_split_mismatch_rows": int((naive != reg.support_size.values).sum()),
            "depth_aware_split_reproduces_support_size":
                bool((parsed == reg.support_size.values).all()),
            "atoms_ascending_sorted_within_support_id": bool(canonical_sorted),
            "support_id_equals_coordinate_ids":
                bool((reg.support_id == reg.coordinate_ids).all()),
            "distinct_atoms_used": int(len({a for s in reg.support_id
                                            for a in depth_split(s)})),
        },
        "cell_geometry": {
            "n_development_shots": len(shots),
            "blocks": blocks,
            "shots_match_frozen_cohort": shots == sorted(dev_shots),
        },
    }

    checks = [
        (frontier["registry_rows"] == 162845, "Ahat_rec cardinality != 162845"),
        (frontier["registry_unique_support_ids"] == 162845, "support ids not unique"),
        (frontier["singleton_supports"] == 10778, "singleton supports != 10778"),
        (frontier["multivariate_supports"] == 152067, "multivariate supports != 152067"),
        (frontier["support_size_min"] == 1 and frontier["support_size_max"] == 12,
         "support sizes not 1..12"),
        (frontier["supports_by_size_matches_freeze"],
         "size histogram differs from the S7.7R freeze"),
        (frontier["per_cell_arrays"]["union_rows"] == 162845,
         "per-cell arrays do not cover Ahat_rec"),
        (frontier["per_cell_arrays"]["n_cells"] == 60, "cell count != 60"),
        (frontier["per_cell_arrays"]["explored_atomic_id_overlap"] == 0,
         "atomic/explored id overlap"),
        (frontier["cell_geometry"]["shots_match_frozen_cohort"],
         "cells do not match the frozen development cohort"),
        (frontier["canonical_id"]["depth_aware_split_reproduces_support_size"],
         "canonical parse fails"),
    ]
    for cond, msg in checks:
        if not cond:
            drift.append(msg)

    # ---- contract facts --------------------------------------------------
    s73 = json.loads(
        (S7 / "03_target_feasibility_and_boundary"
         / "reconciliation_source_resolution" / "S7_3_FREEZE_V2.json"
         ).read_text(encoding="utf-8"))
    mgd = json.loads(
        (S7 / "02_reconstruction_contract" / "correction_v1"
         / "metric_and_gate_definitions.json").read_text(encoding="utf-8"))

    contract = {
        "target": s73["selected_target"],
        "target_is_density": s73["selected_target"] == "density",
        "development_cohort_n": int(cohort["development"]["n"]),
        "external_cohort_n": int(cohort["external"]["n"]),
        "external_by_era": {k: int(v) for k, v in cohort["external"]["by_era"].items()},
        "external_sealed": True,
        "v6_external_counts_authoritative": mgd["gate_V6"]["external_counts"],
        "v6_parent_object_counts_superseded":
            mgd["gate_V6"]["parent_object_counts_for_reference"],
        "practical_equivalence_authoritative": mgd["practical_equivalence"]["delta_equiv"],
        "primary_metric_scale": mgd["primary_metric"]["scale_definition"],
        "search_policy": r7["sigma_rec_id"],
        "one_seed_primary": r7["policy_diff"]["SEEDS_PER_STRATUM"] == "2 -> 1",
        "two_seed_sensitivity": r7["two_seed_sensitivity"],
        "baselines_run": int(r7["access"]["baselines_run"]),
        "external_signal_values_opened_by_parents":
            int(r7["access"]["external_signal_values"]),
        "external_target_values_opened_by_parents":
            int(r7["access"]["external_target_values"]),
    }
    for cond, msg in [
        (contract["target_is_density"], "target is not density"),
        (contract["development_cohort_n"] == 20, "development cohort != 20"),
        (contract["external_cohort_n"] == 42, "external cohort != 42"),
        (contract["external_by_era"] == {"earlier": 24, "later": 18},
         "external era split != 24/18"),
        (contract["v6_external_counts_authoritative"]
         == {"earlier": 24, "later": 18, "total": 42},
         "S7.2C V6 external counts changed"),
        (contract["practical_equivalence_authoritative"] == "max(SE_delta, 0.01)",
         "S7.2C practical-equivalence rule changed"),
        (contract["two_seed_sensitivity"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
         "two-seed sensitivity state changed"),
        (contract["baselines_run"] == 0, "a baseline has been run"),
        (contract["external_signal_values_opened_by_parents"] == 0,
         "external signal values were opened upstream"),
        (contract["external_target_values_opened_by_parents"] == 0,
         "external target values were opened upstream"),
    ]:
        if not cond:
            drift.append(msg)

    out = {
        "verification_id": "S7_8_PARENT_FREEZE_VERIFICATION_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.8",
        "lineage": lineage_rows,
        "n_lineage_entries": len(lineage_rows),
        "s7_7r_manifest_recomputation": manifest_check,
        "frontier_integrity": frontier,
        "contract_facts": contract,
        "drift": drift,
        "verdict": "ZERO_SUBSTANTIVE_DRIFT" if not drift else "DRIFT_DETECTED",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
        },
    }
    p = OUT / "manifests" / "PARENT_FREEZE_VERIFICATION.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("lineage entries       : %d/13" % len(lineage_rows))
    print("S7.7R manifest        : %d/%d artifacts reproduce"
          % (manifest_check["n_matched"], manifest_check["n_recorded"]))
    print("Ahat_rec              : %d (%d singleton + %d multivariate)"
          % (frontier["registry_rows"], frontier["singleton_supports"],
             frontier["multivariate_supports"]))
    print("naive-split unsafe on : %d registry rows"
          % frontier["canonical_id"]["naive_split_mismatch_rows"])
    print("verdict               : %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
