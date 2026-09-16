"""S7.11 step A - lineage, primary-result immutability, predeclaration verification.

Verifies that S7.10 and every parent are unchanged, that the S7.11 sensitivity
predeclaration is byte-identical and predates first external access, and that
the 217 support family is exactly the predeclared set.

Writes the machine-readable primary-result invariant. Nothing here may be
modified by any later S7.11 output.
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
import sklearn

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S79 = S7 / "09_development_selection_and_freeze"
S710 = S7 / "10_external_validation"

PREDECL_SHA_PREFIX = "da24fbe38141f0c7"
FIRST_EXT = "2026-09-05T22:48:51.998142+00:00"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
    ("S7.9 V1", "09_development_selection_and_freeze/S7_9_FREEZE.json"),
    ("S7.10 V1", "10_external_validation/S7_10_FREEZE.json"),
]


def main() -> int:
    drift = []
    now = datetime.now(timezone.utc).isoformat()

    lineage = []
    for label, rel in LINEAGE:
        p = S7 / rel
        if not p.exists():
            drift.append("MISSING: " + rel)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        lineage.append({"stage": label, "freeze_id": d.get("freeze_id"),
                        "status": d.get("status"), "file_sha256": sha256(p)})

    f10 = json.loads((S710 / "S7_10_FREEZE.json").read_text(encoding="utf-8"))
    m10 = {"n": len(f10["all_artifact_hashes"]), "matched": 0, "mismatched": []}
    for rel, want in f10["all_artifact_hashes"].items():
        p = S710 / rel
        if p.exists() and sha256(p) == want:
            m10["matched"] += 1
        else:
            m10["mismatched"].append(rel)
    if m10["mismatched"]:
        drift.append("S7.10 artifact manifest does not reproduce")

    f9 = json.loads((S79 / "S7_9_FREEZE.json").read_text(encoding="utf-8"))
    m9 = {"n": len(f9["all_artifact_hashes"]), "matched": 0, "mismatched": []}
    for rel, want in f9["all_artifact_hashes"].items():
        p = S79 / rel
        if p.exists() and sha256(p) == want:
            m9["matched"] += 1
        else:
            m9["mismatched"].append(rel)
    if m9["mismatched"]:
        drift.append("S7.9 artifact manifest does not reproduce")

    res10 = json.loads((S710 / "V_REC_EXTERNAL_RESULTS.json").read_text(encoding="utf-8"))
    om10 = json.loads((S710 / "OMEGA_REC_EXTERNAL.json").read_text(encoding="utf-8"))
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text(encoding="utf-8"))
    pre = json.loads((S79 / "PRE_EXTERNAL_MODEL_FREEZE.json").read_text(encoding="utf-8"))
    fa = json.loads((S710 / "manifests" / "FIRST_EXTERNAL_ACCESS.json").read_text(encoding="utf-8"))

    # ---------------- predeclaration ------------------------------------
    pdp = S710 / "S7_11_SENSITIVITY_PREDECLARATION.json"
    pd_sha = sha256(pdp)
    pdj = json.loads(pdp.read_text(encoding="utf-8"))
    boot = pd.read_csv(S79 / "bootstrap_selection_frequency.csv")
    ids_sha = hashlib.sha256("\n".join(sorted(boot.support_id)).encode()).hexdigest()
    reg = pd.read_csv(S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"
                      / "explored_support_registry.csv")

    predecl = {
        "file_sha256": pd_sha,
        "prefix_matches_expected": pd_sha.startswith(PREDECL_SHA_PREFIX),
        "declared_utc": pdj["declared_utc"],
        "first_external_value_access_utc": fa["first_external_value_access_utc"],
        "predates_first_external_access":
            pdj["declared_utc"] < fa["first_external_value_access_utc"],
        "seconds_before_first_external_access": round(
            (datetime.fromisoformat(fa["first_external_value_access_utc"])
             - datetime.fromisoformat(pdj["declared_utc"])).total_seconds(), 3),
        "executed_in_S7_10": pdj["executed_in_S7_10"],
        "authorised_sensitivities": sorted(pdj["sensitivities"].keys()),
        "support_family": {
            "n_declared": pdj["sensitivities"]["SUPPORT_FAMILY_EXTERNAL_SENSITIVITY"]["n_supports"],
            "n_recovered": int(boot.support_id.nunique()),
            "support_ids_sha256_declared":
                pdj["sensitivities"]["SUPPORT_FAMILY_EXTERNAL_SENSITIVITY"]["support_ids_sha256"],
            "support_ids_sha256_recomputed": ids_sha,
            "matches": ids_sha == pdj["sensitivities"][
                "SUPPORT_FAMILY_EXTERNAL_SENSITIVITY"]["support_ids_sha256"],
            "all_within_Ahat_rec": bool(set(boot.support_id) <= set(reg.support_id)),
            "top_k_subset": False,
            "external_result_based_selection": False,
        },
        "minus_prmtan": {
            "removed": pdj["sensitivities"]["PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY"]["removed_coordinates"],
            "n_removed": pdj["sensitivities"]["PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY"]["n_removed"],
            "resulting_support": pdj["sensitivities"]["PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY"]["resulting_support"],
            "resulting_support_size": pdj["sensitivities"]["PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY"]["resulting_support_size"],
        },
        "prmtan_only": pdj["sensitivities"]["PRMTAN_NEPED_ONLY"]["support"],
        "two_seed": pdj["sensitivities"]["TWO_SEED_SEARCH_DEPTH_SENSITIVITY"]["status"],
    }

    # verify the minus-prmtan construction independently rather than assuming
    atoms = sel["canonical_coordinate_ids"]
    anc = {c["coordinate_id"]: c["primitive_ancestors"] for c in sel["coordinates"]}
    removed_by_ancestry = sorted([a for a in atoms if "prmtan_neped" in anc[a]])
    kept_by_ancestry = sorted([a for a in atoms if "prmtan_neped" not in anc[a]])
    predecl["minus_prmtan"]["independently_recomputed_removed"] = removed_by_ancestry
    predecl["minus_prmtan"]["independently_recomputed_kept"] = kept_by_ancestry
    predecl["minus_prmtan"]["agrees_with_predeclaration"] = (
        sorted(predecl["minus_prmtan"]["removed"]) == removed_by_ancestry
        and sorted(predecl["minus_prmtan"]["resulting_support"]) == kept_by_ancestry)

    for cond, msg in [
        (predecl["prefix_matches_expected"], "predeclaration hash prefix mismatch"),
        (predecl["predates_first_external_access"], "predeclaration does not predate external access"),
        (predecl["support_family"]["matches"], "support-family id hash mismatch"),
        (predecl["support_family"]["n_recovered"] == 217, "support family is not 217"),
        (predecl["support_family"]["all_within_Ahat_rec"], "a support lies outside Ahat_rec"),
        (predecl["minus_prmtan"]["agrees_with_predeclaration"],
         "minus-prmtan construction disagrees with the predeclaration"),
        (predecl["minus_prmtan"]["resulting_support_size"] == 7, "minus-prmtan size != 7"),
        (predecl["two_seed"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"], "two-seed state changed"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- immutability ---------------------------------------
    b2 = json.loads((S79 / "BASELINE_B2_CONFIG.json").read_text())
    b3 = json.loads((S79 / "BASELINE_B3_CONFIG.json").read_text())
    h0 = json.loads((S79 / "BASELINE_H0_CONFIG.json").read_text())
    cohort = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json").read_text())

    immutable = {
        "PRIMARY_S7_10_RESULT_IMMUTABLE": True,
        "primary_support": sel["support_id"],
        "primary_support_size": sel["support_size"],
        "C_dev_star_changed": False,
        "PRIMARY_EXTERNAL_RESULT": res10["PRIMARY_EXTERNAL_RESULT"],
        "V3": "FAIL", "V6": "FAIL",
        "Delta_0": res10["V3"]["Delta_0"], "Delta_1": res10["V3"]["Delta_1"],
        "omega_rec_supported_claim_domain": om10["supported_claim_domain"]["domain"],
        "stage_status_S7_10": f10["status"],
        "gate_results_S7_10": f10["gate_results"],
        "external_cohort": {"n": int(cohort["external"]["n"]),
                            "earlier": int(cohort["external"]["by_era"]["earlier"]),
                            "later": int(cohort["external"]["by_era"]["later"])},
        "baselines": {"B2_alpha": b2["selected_alpha"], "B2_predictors": b2["predictors"]["n"],
                      "B3_sklearn": b3["sklearn_version"], "B3_random_state": b3["random_state"],
                      "H0_alpha": h0["selected_alpha"], "H0_predictors": h0["predictors"]["n"]},
        "pre_external_model_freeze_utc": pre["frozen_utc"],
        "pre_external_model_freeze_sha256": sha256(S79 / "PRE_EXTERNAL_MODEL_FREEZE.json"),
        "no_S7_11_output_may_modify_these_fields": True,
    }
    for cond, msg in [
        (immutable["PRIMARY_EXTERNAL_RESULT"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER",
         "primary external result changed"),
        (f10["gate_results"]["V3"] == "FAIL", "V3 is not FAIL"),
        (f10["gate_results"]["V6"] == "FAIL", "V6 is not FAIL"),
        (f10["status"] == "PRIMARY_EXTERNAL_GATE_FAILURE", "S7.10 stage status changed"),
        (immutable["omega_rec_supported_claim_domain"] == "EMPTY", "Omega_rec changed"),
        (immutable["primary_support_size"] == 12, "support size changed"),
        (immutable["external_cohort"] == {"n": 42, "earlier": 24, "later": 18},
         "external cohort changed"),
        (b2["selected_alpha"] == 1 and h0["selected_alpha"] == 1
         and b3["random_state"] == 2026090502, "a baseline configuration changed"),
        (sklearn.__version__ == "1.9.0", "installed sklearn differs from the frozen version"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- V9 scope audit -------------------------------------
    v9_scope = {
        "inherited_definition": ("no result depends catastrophically on one discharge, one "
                                 "temporal block, or one numerical realization"),
        "source": "S7.2 V1 UTILITY_AND_QUALIFICATION_POLICY.md, carried into V_REC_OPERATIONAL_V1",
        "mandatory": False,
        "owner_stage": "S7.11",
        "components": ["DISCHARGE", "TEMPORAL_BLOCK", "NUMERICAL_REALIZATION"],
        "components_frozen_before_external_access": True,
        "note": ("the three V9 components were frozen in S7.2 V1, long before any external "
                 "value existed. Executing them is executing an already-frozen gate "
                 "definition, not broadening the S7.11 predeclaration, which covers the "
                 "three interpretation sensitivities separately."),
        "numerical_realization_ids_of_C_dev_star": sorted(
            {c["numerical_realization_id"] for c in sel["coordinates"]}),
        "C_dev_star_contains_derivative_coordinate": any(
            c["constructor"] in ("C1", "C6", "C7", "C8") for c in sel["coordinates"]),
    }

    out = {
        "verification_id": "S7_11_ENTRY_VERIFICATION_V1",
        "generated_utc": now,
        "lineage": lineage,
        "n_authoritative": len(lineage),
        "s7_10_manifest_recomputation": m10,
        "s7_9_manifest_recomputation": m9,
        "predeclaration": predecl,
        "primary_result_invariant": immutable,
        "v9_scope": v9_scope,
        "drift": drift,
        "verdict": "ZERO_SUBSTANTIVE_DRIFT" if not drift else "DRIFT_DETECTED",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
    }
    (OUT / "S7_11_PREDECLARATION_VERIFICATION.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print("authoritative lineage        : %d/12" % len(lineage))
    print("S7.10 manifest               : %d/%d" % (m10["matched"], m10["n"]))
    print("S7.9  manifest               : %d/%d" % (m9["matched"], m9["n"]))
    print("predeclaration sha256        : %s (prefix ok %s)"
          % (pd_sha[:16], predecl["prefix_matches_expected"]))
    print("  declared                   : %s" % predecl["declared_utc"])
    print("  first external access      : %s" % predecl["first_external_value_access_utc"])
    print("  lead time                  : %.1f s" % predecl["seconds_before_first_external_access"])
    print("support family               : %d recovered, id-hash match %s, all in Ahat_rec %s"
          % (predecl["support_family"]["n_recovered"], predecl["support_family"]["matches"],
             predecl["support_family"]["all_within_Ahat_rec"]))
    print("minus-prmtan                 : %d removed -> %d kept, agrees %s"
          % (predecl["minus_prmtan"]["n_removed"],
             predecl["minus_prmtan"]["resulting_support_size"],
             predecl["minus_prmtan"]["agrees_with_predeclaration"]))
    print("PRIMARY (immutable)          : %s | V3 %s | V6 %s | Omega_rec %s"
          % (immutable["PRIMARY_EXTERNAL_RESULT"], immutable["V3"], immutable["V6"],
             immutable["omega_rec_supported_claim_domain"]))
    print("C_dev_star realization ids   : %s | contains derivative coordinate: %s"
          % (v9_scope["numerical_realization_ids_of_C_dev_star"],
             v9_scope["C_dev_star_contains_derivative_coordinate"]))
    print("verdict                      : %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
