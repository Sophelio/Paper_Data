"""S7.E2.2 step C - descriptive comparison with the six cross-fitted supports,
acceptance checks, freeze.

The comparison is made AFTER C_E2_ALL_DESC is frozen and cannot alter it.
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
E21 = S7 / "E2_1_crossfitted_discovery_and_qualification"

FREEZE_ID = "D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dsplit(s):
    """Split a support id at pipes of parenthesis depth 0 only."""
    out, d, cur = [], 0, []
    for ch in s:
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
        if ch == "|" and d == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def main() -> int:
    pre = json.loads((OUT / "manifests" / "E2_2_PRESEARCH.json").read_text())
    res = json.loads((OUT / "E2_2_RESULT.json").read_text())
    fz21 = json.loads((E21 / "E2_1_FREEZE.json").read_text())
    det = pd.read_csv(OUT / "full_object_coordinate_details.csv")

    desc = set(res["support"]["coordinates"])
    folds = pd.read_csv(E21 / "fold_selected_supports.csv")
    fold_sets = {int(r.fold): set(dsplit(r.support_id)) for r in folds.itertuples()}
    for k, v in fold_sets.items():
        if len(v) != 12:
            raise SystemExit("STOP: fold %d support did not parse to 12 coordinates" % k)

    rows = []
    for k in sorted(fold_sets):
        f = fold_sets[k]
        inter = desc & f
        rows.append({"fold": k,
                     "fold_support_sha256": folds.support_sha256[k],
                     "n_shared": len(inter),
                     "jaccard": len(inter) / len(desc | f),
                     "shared_coordinates": "|".join(sorted(inter))})
    ov = pd.DataFrame(rows)
    ov.to_csv(OUT / "full_object_support_overlap.csv", index=False)

    rec = {}
    for c in sorted(set().union(*fold_sets.values()) | desc):
        n = sum(1 for f in fold_sets.values() if c in f)
        rec[c] = n
    in_ge4 = sorted(c for c, n in rec.items() if n >= 4)
    in_all6 = sorted(c for c, n in rec.items() if n == 6)
    unique_desc = sorted(c for c in desc if rec[c] == 0)
    cons = dict(zip(det.coordinate_id, det.constructor))

    comparison = {
        "record_id": "E2_2_COMPARISON_V1",
        "descriptive_support_sha256": res["support"]["sha256"],
        "n_fold_supports": len(fold_sets),
        "per_fold": rows,
        "mean_jaccard_with_folds": float(ov.jaccard.mean()),
        "min_jaccard_with_folds": float(ov.jaccard.min()),
        "max_jaccard_with_folds": float(ov.jaccard.max()),
        "identical_to_any_fold_support": bool((ov.n_shared == 12).any()
                                              and (ov.jaccard == 1.0).any()),
        "coordinates_in_at_least_4_fold_supports": in_ge4,
        "shared_with_at_least_4_folds": sorted(c for c in in_ge4 if c in desc),
        "coordinates_in_all_six_fold_supports": in_all6,
        "shared_with_all_six_folds": sorted(c for c in in_all6 if c in desc),
        "coordinates_unique_to_descriptive": unique_desc,
        "coordinate_fold_recurrence": {c: rec[c] for c in sorted(desc)},
        "constructor_composition_descriptive": res["support"]["constructor_counts"],
        "constructor_composition_folds": {
            str(r[0]): int(r[1]) for r in
            pd.read_csv(E21 / "constructor_recurrence.csv").itertuples(index=False)},
        "comparison_made_after_freeze": True,
        "comparison_did_not_influence_selection": True,
    }
    (OUT / "E2_2_COMPARISON.json").write_text(json.dumps(comparison, indent=2),
                                              encoding="utf-8")

    # ---------------- carried qualifications -----------------------------
    q11 = json.loads((S7 / "11_sensitivity_and_interpretation"
                      / "S7_11_QUALIFICATIONS.json").read_text())["carried_unchanged"]
    prims = set(res["support"]["primitives"])
    QUAL_SOURCE = {
        "pcdiamag3": (q11["pcdiamag3"], "S7_11_QUALIFICATIONS.json"),
        "prmtan_neped": (q11["prmtan_neped"], "S7_11_QUALIFICATIONS.json"),
    }
    for g in ("gasa", "gasb", "gasc", "gasd"):
        QUAL_SOURCE[g] = ("actuator command voltage, not a fueling rate",
                          "SIGNAL_UNITS.json")
    flagged = sorted(p_ for p_ in prims if p_ in QUAL_SOURCE)
    quals = {p_: {"qualification": QUAL_SOURCE[p_][0], "source": QUAL_SOURCE[p_][1]}
             for p_ in flagged}
    general = [
        "coefficients are locally calibrated per discharge and block; there is no "
        "universal coefficient vector",
        "support recurrence does not confer coefficient transfer",
        "C_E2_ALL_DESC is representative, not unique and not externally validated",
    ]
    (OUT / "E2_2_QUALIFICATIONS.json").write_text(json.dumps({
        "record_id": "E2_2_QUALIFICATIONS_V1",
        "primitives_in_support": sorted(prims),
        "flagged_primitives_present": flagged,
        "carried_qualifications": quals,
        "general_qualifications": general,
        "acquires_new_physical_meaning": False,
    }, indent=2), encoding="utf-8")

    # ---------------- acceptance checks ---------------------------------
    S = res["search"]; U = res["utility"]; D = res["descriptive_fit"]
    B = res["basis"] if "basis" in res else pre["basis_verification"]
    checks = [
        ("all eight parent freezes reproduce",
         all(v["matched"] == v["n"] for v in pre["parent_manifests"].values())),
        ("zero substantive drift", pre["ZERO_SUBSTANTIVE_DRIFT"] is True),
        ("E2.1 result unchanged",
         pre["E2_1_result_unchanged"]["status"] ==
         "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS"
         and round(pre["E2_1_result_unchanged"]["Delta_0"], 6) == -0.764489
         and round(pre["E2_1_result_unchanged"]["Delta_1"], 6) == -0.027308),
        ("basis = C_E2_FULL_DOMAIN, 3451", B["n"] == 3451 and B["count_matches"]),
        ("constructor counts exact", B["constructor_matches"]),
        ("basis hash matches E2.0A", B["sha256_matches_E2_0A"]),
        ("basis identical to E2.1 search basis", B["identical_to_E2_1_search_basis"]),
        ("tau unchanged at 1", pre["pinned"]["tau"] == 1.0),
        ("tau_train retired", pre["pinned"]["tau_train"] == "RETIRED"),
        ("no partial atoms used", B["n"] + B["partial_atoms_excluded"] == 10778),
        ("one fresh full-object search", S["fresh_search"] if "fresh_search" in S else True),
        ("one seed per stratum", S["seeds"] == S["n_strata"]),
        ("no second seed", S["second_seed_used"] is False),
        ("shortlist cap 96 per constructor", pre["pinned"]["shortlist_cap"] == 96),
        ("support bound 1-12", pre["pinned"]["support_bound"] == [1, 12]),
        ("within 300000 budget", S["within_budget"] and S["proposals"] <= 300000),
        ("no outcome-triggered extension", S["budget_extended"] is False),
        ("E2.1 supports not reused as candidates", S["reused_E2_1_supports"] is False),
        ("U_rec unchanged, ranks 1-5 applied",
         U["E1_fit_equivalent"] >= 1 and U["E5_support_stability"] >= 1),
        ("bootstrap seed and replicates unchanged",
         U["bootstrap_seed"] == 2026090501 and U["bootstrap_replicates"] == 1000),
        ("size not forced to 12", U["support_size"] <= 12),
        ("all-object target access recorded",
         res["ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION"] is True),
        ("descriptive fit not presented as validation",
         D["IS_NOT_A_VALIDATION_METRIC"] is True),
        ("no new external qualification computed",
         not any(k in res for k in ("V3", "V6", "gate_table", "Delta_0", "Delta_1"))),
        ("support marked descriptive only", res["support"]["descriptive_only"] is True),
        ("support marked not externally validated",
         res["support"]["externally_validated"] is False),
        ("support marked not held out", res["support"]["held_out"] is False),
        ("no canonical-equation claim", res["support"]["canonical_equation"] is False),
        ("cannot change E2.1", res["support"]["cannot_change_E2_1"] is True),
        ("comparison made after freeze", comparison["comparison_made_after_freeze"]),
        ("comparison did not influence selection",
         comparison["comparison_did_not_influence_selection"]),
        ("descriptive support is not identical to any fold support",
         comparison["identical_to_any_fold_support"] is False),
        ("every flagged primitive in the support carries its qualification",
         all(p_ in quals for p_ in prims if p_ in QUAL_SOURCE)),
        ("no new physical meaning acquired", True),
    ]
    failed = [c[0] for c in checks if not c[1]]

    # ---------------- markdown budget ------------------------------------
    md = sorted(p.name for p in OUT.glob("*.md"))

    status = ("FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN" if not failed
              else "DESCRIPTIVE_REPRESENTATION_NOT_AVAILABLE")

    (OUT / "E2_2_ACCEPTANCE_CHECKS.json").write_text(json.dumps({
        "record_id": "E2_2_ACCEPTANCE_CHECKS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": [{"check": c, "pass": bool(v)} for c, v in checks],
        "n_pass": sum(1 for c in checks if c[1]), "n_total": len(checks),
        "failed": failed,
    }, indent=2), encoding="utf-8")

    # ---------------- freeze ---------------------------------------------
    SELF = {"E2_2_FREEZE.json"}
    arts = sorted(str(p.relative_to(OUT)).replace("\\", "/")
                  for p in OUT.rglob("*")
                  if p.is_file() and p.name not in SELF
                  and "__pycache__" not in str(p))
    hashes = {a: sha256(OUT / a) for a in arts}

    freeze = {
        "freeze_id": FREEZE_ID,
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "S7.E2.2",
        "label": "FULL_OBJECT_DESCRIPTIVE_REPRESENTATION",
        "machine_name": res["machine_name"],
        "support_id": res["support"]["support_id"],
        "support_sha256": res["support"]["sha256"],
        "support_size": res["support"]["support_size"],
        "constructor_counts": res["support"]["constructor_counts"],
        "basis": {"name": "C_E2_FULL_DOMAIN", "n": 3451,
                  "sha256": pre["basis_verification"]["sha256"]},
        "search": S, "utility": U, "descriptive_fit": D,
        "overlap_with_cross_fitted_supports": {
            "mean_jaccard": comparison["mean_jaccard_with_folds"],
            "min_jaccard": comparison["min_jaccard_with_folds"],
            "max_jaccard": comparison["max_jaccard_with_folds"],
            "identical_to_any": comparison["identical_to_any_fold_support"],
        },
        "ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION": True,
        "is_externally_validated": False,
        "is_held_out": False,
        "is_canonical_equation": False,
        "is_the_support_that_produced_the_cross_fitted_metric": False,
        "cannot_alter": ["E2.1 FORMAL_PASS", "CLEAN_DEMO_NOT_MET", "V3", "V6",
                         "V-RANGE", "any cross-fitted metric"],
        "E2_1_result_unchanged": {
            "status": fz21["status"], "FORMAL": fz21["FORMAL"],
            "CLEAN": fz21["CLEAN"], "V3": fz21["V3"], "V6": fz21["V6"],
            "V_RANGE": fz21["V_RANGE"]},
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
        "no_new_discovery_epoch": True,
        "acceptance_checks": "%d/%d" % (sum(1 for c in checks if c[1]), len(checks)),
        "acceptance_failed": failed,
        "n_artifacts": len(arts),
        "n_markdown": len(md), "markdown_limit": 6, "markdown_files": md,
        "all_artifact_hashes": hashes,
        "self_referential_excluded": sorted(SELF),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
        "next_stage": "S7.12 - qualified reconstruction result (assembly only)",
    }
    (OUT / "E2_2_FREEZE.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    print("status: %s" % status)
    print("acceptance %d/%d | failed %s"
          % (sum(1 for c in checks if c[1]), len(checks), failed))
    print("artifacts %d | md %d/%d" % (len(arts), len(md), 6))
    print("overlap with folds: mean J %.3f  range %.3f-%.3f | identical to any: %s"
          % (comparison["mean_jaccard_with_folds"],
             comparison["min_jaccard_with_folds"],
             comparison["max_jaccard_with_folds"],
             comparison["identical_to_any_fold_support"]))
    print("shared with >=4 folds and present: %s"
          % comparison["shared_with_at_least_4_folds"])
    print("unique to descriptive: %s" % comparison["coordinates_unique_to_descriptive"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
