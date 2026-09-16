"""S7.10 step A - PREFLIGHT. Opens NO external value.

Hard gates, in order:
  1. authoritative lineage through S7.9, zero substantive drift
  2. PRE_EXTERNAL_MODEL_FREEZE substantive hashes
  3. canonical support parse
  4. S7.11 sensitivity predeclaration written and hashed
  5. statistical-inference parent audit
  6. EXTERNAL_INFERENCE_POLICY_PREVALUE written and hashed

Only after this script exits 0 may any external value be opened.
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
S78 = S7 / "08_utility_and_qualification_rules"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S72 = S7 / "02_reconstruction_contract"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def depth_split(s: str) -> list:
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
    ("S7.9 V1", "09_development_selection_and_freeze/S7_9_FREEZE.json"),
]

SUPPORT_ID = ("ID(cerqtit6)|ID(pcdiamag3)|ID(prmtan_neped)|PROD(ece37,ece39)|"
              "PROD(gasa,gasa)|PROD(pinj,cerqrott6)|PROD(prmtan_neped,prmtan_neped)|"
              "RATIO(ece21,prmtan_neped)|RATIO(fs03da,prmtan_neped)|RATIO(ip,ece22)|"
              "RECIP(cerqtit10)|RECIP(prmtan_neped)")


def main() -> int:
    drift = []
    now = datetime.now(timezone.utc).isoformat()

    # ---------------- 1. lineage -----------------------------------------
    lineage = []
    for label, rel in LINEAGE:
        p = S7 / rel
        if not p.exists():
            drift.append("MISSING: " + rel)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        lineage.append({"stage": label, "freeze_id": d.get("freeze_id"),
                        "status": d.get("status"), "file_sha256": sha256(p)})

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

    # ---------------- 2. PRE_EXTERNAL_MODEL_FREEZE hard gate -------------
    pre = json.loads((S79 / "PRE_EXTERNAL_MODEL_FREEZE.json").read_text(encoding="utf-8"))
    lock = json.loads((S79 / "DEVELOPMENT_REPRESENTATION_LOCK.json").read_text(encoding="utf-8"))
    subst = {
        "SELECTED_REPRESENTATION.json": pre["B_selected_representation"]["coordinate_definitions_sha256"],
        "utility_elimination_ledger.csv": pre["D_utility"]["elimination_ledger_sha256"],
        "utility_survivor_sets.csv": pre["D_utility"]["survivor_sets_sha256"],
        "RELATIONAL_ESTIMATOR_CONFIG.json": pre["E_estimator"]["config_sha256"],
        "BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json": pre["K_selected_alphas"]["prevalue_sha256"],
        "BASELINE_B3_CONFIG.json": pre["L_B3_configuration"]["config_sha256"],
    }
    entries, mism = [], []
    for name, want in subst.items():
        got = sha256(S79 / name)
        entries.append({"entry": name, "expected": want, "observed": got, "match": got == want})
        if got != want:
            mism.append(name)
    for bid, meta in pre["J_baseline_configurations"].items():
        got = sha256(S79 / meta["file"])
        entries.append({"entry": meta["file"], "expected": meta["sha256"],
                        "observed": got, "match": got == meta["sha256"]})
        if got != meta["sha256"]:
            mism.append(meta["file"])
    got = sha256(S78 / "U_REC_OPERATIONAL_V1.json")
    entries.append({"entry": "U_REC_OPERATIONAL_V1.json",
                    "expected": pre["D_utility"]["utility_policy_sha256"],
                    "observed": got, "match": got == pre["D_utility"]["utility_policy_sha256"]})
    if got != pre["D_utility"]["utility_policy_sha256"]:
        mism.append("U_REC_OPERATIONAL_V1.json")
    if pre["development_representation_lock_sha256"] != lock["lock_sha256"]:
        mism.append("DEVELOPMENT_REPRESENTATION_LOCK")
    if mism:
        drift.append("PRE_EXTERNAL_FREEZE_INTEGRITY_FAILURE")

    # ---------------- 3. canonical parse ---------------------------------
    atoms = depth_split(SUPPORT_ID)
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text(encoding="utf-8"))
    reg = pd.read_csv(S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"
                      / "explored_support_registry.csv")
    pn = np.array([len(depth_split(s)) for s in reg.support_id])
    parse = {
        "parser": "parenthesis-depth-aware split at depth 0",
        "naive_split_used_operationally": False,
        "parsed_atom_count": len(atoms),
        "expected_atom_count": 12,
        "canonical_serialization_matches": "|".join(atoms) == SUPPORT_ID,
        "matches_s7_9_artifact": atoms == sel["canonical_coordinate_ids"],
        "registry_checksum": "%d/%d" % (int((pn == reg.support_size.values).sum()), len(reg)),
        "passed": (len(atoms) == 12 and "|".join(atoms) == SUPPORT_ID
                   and atoms == sel["canonical_coordinate_ids"]
                   and bool((pn == reg.support_size.values).all())),
    }
    if not parse["passed"]:
        drift.append("CANONICAL_SUPPORT_PARSE_FAILURE")

    # ---------------- immutability spot checks ---------------------------
    b2 = json.loads((S79 / "BASELINE_B2_CONFIG.json").read_text(encoding="utf-8"))
    b3 = json.loads((S79 / "BASELINE_B3_CONFIG.json").read_text(encoding="utf-8"))
    h0 = json.loads((S79 / "BASELINE_H0_CONFIG.json").read_text(encoding="utf-8"))
    cohort = json.loads((S72 / "COHORT_PARTITION.json").read_text(encoding="utf-8"))
    s73 = json.loads((S7 / "03_target_feasibility_and_boundary"
                      / "reconciliation_source_resolution" / "S7_3_FREEZE_V2.json"
                      ).read_text(encoding="utf-8"))
    immut = {
        "target": s73["selected_target"],
        "support_id_unchanged": sel["support_id"] == SUPPORT_ID,
        "support_size": sel["support_size"],
        "lock_sha256": lock["lock_sha256"],
        "estimator": "DEVELOPMENT_RELATION_OLS_V1",
        "B2_alpha": b2["selected_alpha"], "B2_predictors": b2["predictors"]["n"],
        "B3_sklearn": b3["sklearn_version"], "B3_random_state": b3["random_state"],
        "H0_alpha": h0["selected_alpha"], "H0_predictors": h0["predictors"]["n"],
        "external_n": int(cohort["external"]["n"]),
        "external_earlier": int(cohort["external"]["by_era"]["earlier"]),
        "external_later": int(cohort["external"]["by_era"]["later"]),
        "two_seed": f9["two_seed_sensitivity"],
        "installed_sklearn": sklearn.__version__,
    }
    for cond, msg in [
        (immut["target"] == "density", "target != density"),
        (immut["support_id_unchanged"], "C_dev_star changed"),
        (immut["support_size"] == 12, "support size != 12"),
        (immut["B2_alpha"] == 1 and immut["B2_predictors"] == 78, "B2 changed"),
        (immut["B3_sklearn"] == "1.9.0" and immut["B3_random_state"] == 2026090502, "B3 changed"),
        (immut["H0_alpha"] == 1 and immut["H0_predictors"] == 70, "H0 changed"),
        (immut["external_n"] == 42 and immut["external_earlier"] == 24
         and immut["external_later"] == 18, "external cohort changed"),
        (immut["two_seed"] == ["DECLARED_OPTIONAL", "NOT_EXECUTED"], "two-seed state changed"),
        (immut["installed_sklearn"] == "1.9.0", "installed sklearn differs from the frozen version"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- 4. S7.11 sensitivity predeclaration ----------------
    boot = pd.read_csv(S79 / "bootstrap_selection_frequency.csv")
    pn_atoms = [a for a in atoms if "prmtan_neped" in a]
    keep = [a for a in atoms if "prmtan_neped" not in a]
    s11 = {
        "record_id": "S7_11_SENSITIVITY_PREDECLARATION_V1",
        "status": "PREDECLARED_NOT_EXECUTED",
        "declared_utc": now,
        "declared_before_first_external_value_access": True,
        "executed_in_S7_10": False,
        "can_alter_S7_10_primary_result": False,
        "class": "POST_SELECTION_PRE_EXTERNAL_INTERPRETATION_SENSITIVITIES",
        "sensitivities": {
            "SUPPORT_FAMILY_EXTERNAL_SENSITIVITY": {
                "definition": ("externally evaluate ALL unique Rank-4 winning supports "
                               "from the frozen S7.9 development bootstrap, under the same "
                               "local-calibration estimator and scoring geometry"),
                "n_supports": int(len(boot)),
                "top_k_subset": False,
                "external_result_based_support_selection": False,
                "purpose": ("determine whether external transfer is a property of the "
                            "broader development-equivalent support family or unusually "
                            "specific to C_dev_star"),
                "primary_remains": "C_dev_star regardless of outcome",
                "support_ids_sha256": hashlib.sha256(
                    "\n".join(sorted(boot.support_id)).encode()).hexdigest(),
            },
            "PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY": {
                "definition": "C_dev_star with every coordinate having prmtan_neped ancestry removed",
                "removed_coordinates": pn_atoms,
                "n_removed": len(pn_atoms),
                "resulting_support": keep,
                "resulting_support_size": len(keep),
                "replacement_coordinates_added": False,
                "re_search": False, "re_selection": False,
                "estimator": "same local affine OLS procedure",
            },
            "PRMTAN_NEPED_ONLY": {
                "definition": "ID(prmtan_neped) alone under the same local affine OLS estimator",
                "support": ["ID(prmtan_neped)"], "support_size": 1,
                "purpose": ("quantify how much of the observed external reconstruction is "
                            "associated with the semantically close pedestal-density diagnostic"),
            },
            "TWO_SEED_SEARCH_DEPTH_SENSITIVITY": {
                "status": ["DECLARED_OPTIONAL", "NOT_EXECUTED"],
                "carried_unchanged": True, "executed_here": False,
                "may_replace_primary_frontier": False,
            },
        },
        "are_mandatory_gates": False,
        "owner_stage": "S7.11",
    }
    (OUT / "S7_11_SENSITIVITY_PREDECLARATION.json").write_text(
        json.dumps(s11, indent=2), encoding="utf-8")
    s11_sha = sha256(OUT / "S7_11_SENSITIVITY_PREDECLARATION.json")

    # ---------------- 5. statistical-inference parent audit --------------
    kpre = json.loads((S72 / "correction_v1" / "K_REC_PRE_V2.json").read_text(encoding="utf-8"))
    mgd = json.loads((S72 / "correction_v1" / "metric_and_gate_definitions.json"
                      ).read_text(encoding="utf-8"))
    sip = (S72 / "STATISTICAL_INFERENCE_PLAN.md").read_text(encoding="utf-8")
    infer_audit = {
        "audit_id": "STATISTICAL_INFERENCE_PARENT_AUDIT_V1",
        "generated_utc": now,
        "principle": "PARENT DEFINITIONS WIN",
        "already_frozen_by_parents": {
            "inferential_unit": kpre["V_rec"]["inferential_unit"],
            "bootstrap_replicates_minimum": kpre["V_rec"]["bootstrap_replicates"],
            "confidence_level": "95%",
            "aggregation": "blocks -> discharge first",
            "V3_rule": mgd["gate_V3"]["pass_condition"],
            "V3_ci_role": mgd["gate_V3"]["ci_role"],
            "V6_external_counts": mgd["gate_V6"]["external_counts"],
            "V6_outcomes": list(mgd["gate_V6"]["outcomes"].keys()),
            "win_tie_loss_floor": "0.01 calibration-normalized RMSE (STATISTICAL_INFERENCE_PLAN item 8)",
            "lodo_required": "leave-one-discharge-out sensitivity (item 9)",
        },
        "unspecified_by_parents_completed_here": [
            "bootstrap RNG seeds", "bootstrap CI type (percentile vs BCa)",
            "percentile interpolation method",
            "whether bootstrap indices are shared across methods",
            "exact era-specific practical-direction thresholds for V6",
        ],
        "bca_required_by_parent": False,
        "parent_text_checked": ["STATISTICAL_INFERENCE_PLAN.md", "K_REC_PRE_V2.json",
                                "metric_and_gate_definitions.json", "BASELINE_PROTOCOL.md"],
        "parent_specifies_seed": "seed fixed and recorded" in sip.lower(),
    }
    (OUT / "manifests" / "STATISTICAL_INFERENCE_PARENT_AUDIT.json").write_text(
        json.dumps(infer_audit, indent=2), encoding="utf-8")

    # ---------------- 6. external inference policy pre-value -------------
    pol = {
        "policy_id": "EXTERNAL_INFERENCE_POLICY_PREVALUE_V1",
        "status": "PROSPECTIVE_SPECIFICATION_COMPLETION",
        "frozen_utc": now,
        "frozen_before_first_external_value_access": True,
        "not_an_outcome_response": True,
        "completes_only_what_parents_left_unspecified": True,
        "parent_audit": "manifests/STATISTICAL_INFERENCE_PARENT_AUDIT.json",
        "bootstrap": {
            "replicates": 10000,
            "pooled_rng": "numpy.random.default_rng(2026090503)",
            "earlier_era_rng": "numpy.random.default_rng(2026090504)",
            "later_era_rng": "numpy.random.default_rng(2026090505)",
            "pooled_seed": 2026090503, "earlier_seed": 2026090504, "later_seed": 2026090505,
            "index_sharing": ("ONE discharge-index bootstrap matrix per cohort/era, reused "
                              "for every method comparison, preserving paired geometry"),
            "statistic": "mean discharge-level paired difference",
            "ci": "percentile interval [2.5, 97.5] via numpy.percentile(method='linear')",
            "bca": False, "p_value_gate": False,
            "resampled_unit": "external discharge",
        },
        "win_tie_loss": {
            "quantity": "d_s = NRMSE_REL,s - NRMSE_B,s",
            "WIN": "d_s <= -0.01", "TIE": "-0.01 < d_s <= +0.01", "LOSS": "d_s > +0.01",
            "floor_source": "already-frozen 0.01 practical-relevance floor",
            "reporting_only": True, "alters_V3": False,
        },
        "lodo": {
            "definition": "for each external discharge k, remove k and recompute the mean paired difference",
            "applies_to": "every comparator",
            "v3_verdict_flip_recorded": True,
            "replaces_full_cohort_verdict": False,
        },
        "V6_operational": {
            "quantity": "Delta_{j,e} = mean over discharges in era e of (NRMSE_REL - NRMSE_Bj)",
            "MATERIAL_IMPROVEMENT": "Delta <= -0.01",
            "PRACTICAL_TIE": "-0.01 < Delta <= +0.01",
            "MATERIAL_ADVERSE": "Delta > +0.01",
            "PASS": "pooled V3 passes AND every era/baseline comparison is MATERIAL_IMPROVEMENT",
            "PASS_WITH_QUALIFICATION": ("pooled V3 passes AND no era/baseline comparison is "
                                        "MATERIAL_ADVERSE AND at least one is PRACTICAL_TIE"),
            "FAIL_FOR_FULL_DOMAIN": ("pooled V3 passes BUT at least one era/baseline comparison "
                                     "is MATERIAL_ADVERSE"),
            "if_pooled_V3_fails": "V6 MAY NOT rescue V3; era results still reported",
            "external_counts": {"earlier": 24, "later": 18},
        },
        "sign_convention": "negative = relational representation lower error; never switched",
        "external_domain_rule": {
            "rule_id": "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1",
            "inherited_unchanged": True,
            "applied_on": "each external local-calibration block",
            "require": ["finite throughout", "RMS(d) != 0", "no sign change", "eta(d) >= 0.05"],
            "eta": "min(|d|)/RMS(d)",
            "denominators_required_by_C_dev_star": sorted(
                {a[a.index("(") + 1:-1].split(",")[-1] for a in atoms
                 if a.startswith(("RATIO", "RECIP"))}),
            "on_failure": "mark RELATIONAL_REPRESENTATION_NOT_APPLICABLE for that block",
            "no_epsilon_clip_shift_bounded_reciprocal_or_repair": True,
        },
        "metric": {
            "scale": "std(y_calibration_{s,b}, ddof=0)",
            "zero_scale": "INVALID_FOR_NORMALIZED_SCORING", "epsilon": False,
            "discharge_level": "mean over valid required A/B/C blocks",
        },
    }
    (OUT / "EXTERNAL_INFERENCE_POLICY_PREVALUE.json").write_text(
        json.dumps(pol, indent=2), encoding="utf-8")
    pol_sha = sha256(OUT / "EXTERNAL_INFERENCE_POLICY_PREVALUE.json")

    out = {
        "preflight_id": "S7_10_PREFLIGHT_V1",
        "generated_utc": now,
        "external_values_opened_by_this_script": 0,
        "lineage": lineage,
        "n_authoritative": len(lineage),
        "s7_9_manifest_recomputation": m9,
        "pre_external_freeze": {
            "file_sha256": sha256(S79 / "PRE_EXTERNAL_MODEL_FREEZE.json"),
            "recorded_in_s7_9_freeze": f9["pre_external_model_freeze_sha256"],
            "matches_s7_9_freeze": sha256(S79 / "PRE_EXTERNAL_MODEL_FREEZE.json")
                                   == f9["pre_external_model_freeze_sha256"],
            "frozen_utc": pre["frozen_utc"],
            "n_substantive_entries": len(entries),
            "n_mismatched": len(mism),
            "entries": entries,
            "verdict": "PRE_EXTERNAL_FREEZE_VERIFIED" if not mism
                       else "PRE_EXTERNAL_FREEZE_INTEGRITY_FAILURE",
        },
        "canonical_parse": parse,
        "immutability": immut,
        "s7_11_predeclaration": {"sha256": s11_sha, "declared_utc": now,
                                 "n_sensitivities": len(s11["sensitivities"])},
        "external_inference_policy": {"sha256": pol_sha, "frozen_utc": now},
        "drift": drift,
        "verdict": "PREFLIGHT_PASSED" if not drift else "PREFLIGHT_FAILED",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
    }
    (OUT / "manifests" / "PREFLIGHT.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("authoritative lineage      : %d/11" % len(lineage))
    print("S7.9 manifest              : %d/%d" % (m9["matched"], m9["n"]))
    print("PRE_EXTERNAL freeze        : %d substantive entries, %d mismatched"
          % (len(entries), len(mism)))
    print("  frozen_utc               : %s" % pre["frozen_utc"])
    print("canonical parse            : %d atoms, canonical %s, registry %s"
          % (parse["parsed_atom_count"], parse["canonical_serialization_matches"],
             parse["registry_checksum"]))
    print("S7.11 predeclaration       : %s" % s11_sha[:16])
    print("external inference policy  : %s" % pol_sha[:16])
    print("denominators to audit      : %s"
          % pol["external_domain_rule"]["denominators_required_by_C_dev_star"])
    print("verdict                    : %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
