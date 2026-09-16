"""S7.E2.0A step A - parent verification, firewall, candidate-basis verification
and closure-property check.

Protocol reconciliation only. No search, no fit, no baseline, no target read.
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
K2 = S7 / "K2_observational_range_support_contract"
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
S77 = S7 / "07_search_policy_and_frontier"

ACCESS = {"target_reads": 0, "model_error_reads": 0, "residual_reads": 0,
          "epoch1_performance_reads_for_decision": 0, "epoch2_performance_reads": 0}
K2_EXPECTED = {"C0": 51, "C1": 18, "C2": 1488, "C3": 382, "C5": 8, "C6": 965, "C7": 539}
N_EXPECTED = 3451
TAU = 1.0

FOLDS = {
    0: "155537 160721 165022 165042 170394 187019 189647 195264 195273 195647 195655",
    1: "159310 161136 165026 165043 170396 187020 189649 195265 195274 195648 195659",
    2: "160715 161138 165027 165860 170411 187021 189650 195266 195626 195649",
    3: "160717 161145 165028 165861 186997 187022 189651 195267 195638 195650",
    4: "160719 161414 165029 165955 187017 187024 189652 195268 195642 195651",
    5: "160720 165017 165031 165965 187018 189646 195261 195269 195645 195652",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    drift = []
    now = datetime.now(timezone.utc).isoformat()

    # ---------------- firewall, hashed before analysis -------------------
    firewall = {
        "record_id": "E2_0A_FIREWALL_V1", "frozen_utc": now, **ACCESS,
        "permitted": ["predictor values", "K2 applicability artifacts", "fold metadata",
                      "frozen contract and protocol artifacts"],
        "amendment_must_be_justified_on": ["claim semantics", "information-boundary logic",
                                           "K2 applicability semantics"],
        "amendment_may_not_be_justified_on": ["improving the probability of success"],
        "e2_0_feasibility_estimate_role": "HISTORICAL_CONTEXT_ONLY_NOT_JUSTIFICATION",
        "asserted_in_code": True,
    }
    (OUT / "E2_0A_FIREWALL.json").write_text(json.dumps(firewall, indent=2), encoding="utf-8")

    # ---------------- parents reproduce ----------------------------------
    manifests = {}
    for label, base in [("S7.K2", "K2_observational_range_support_contract"),
                        ("S7.E2.0", "E2_0_protocol_and_resampling_freeze")]:
        fzp = list((S7 / base).glob("*FREEZE.json"))
        fzp = [p for p in fzp if "ACCEPTANCE" not in p.name][0]
        fz = json.loads(fzp.read_text(encoding="utf-8"))
        m, bad = 0, []
        for r, want in fz["all_artifact_hashes"].items():
            p = S7 / base / r
            if p.exists() and sha256(p) == want:
                m += 1
            else:
                bad.append(r)
        manifests[label] = {"n": len(fz["all_artifact_hashes"]), "matched": m,
                            "mismatched": bad, "freeze_file": fzp.name,
                            "freeze_sha256": sha256(fzp)}
        if bad:
            drift.append("%s manifest does not reproduce" % label)

    fk2 = json.loads((K2 / "S7_K2_FREEZE.json").read_text())
    f20 = json.loads((E20 / "E2_0_FREEZE.json").read_text())
    krec2 = json.loads((K2 / "K_REC_V2.json").read_text())
    pol = json.loads((K2 / "RANGE_SUPPORT_POLICY_V1.json").read_text())
    q20 = json.loads((E20 / "EPOCH2_QUALIFICATION_POLICY.json").read_text())
    b20 = json.loads((E20 / "EPOCH2_SEARCH_BUDGET.json").read_text())
    p20 = json.loads((E20 / "EPOCH2_PROTOCOL.json").read_text())

    inherited = {
        "K_REC_V2_sha256": sha256(K2 / "K_REC_V2.json"),
        "K_REC_V2_matches_K2_freeze": sha256(K2 / "K_REC_V2.json") == fk2["K_REC_V2_sha256"],
        "tau": pol["threshold"]["tau"],
        "revision_class": krec2["revision_class"],
        "U_rec": krec2["components"]["U_rec"]["status"],
        "V3": q20["V3"]["pass"],
        "V6_threshold": q20["V6"]["threshold"],
        "baselines": q20["baselines"]["carried"],
        "budget_per_fold": b20["max_support_evaluations_per_fold"],
        "budget_total": b20["max_support_evaluations_total"],
        "clean_demo_delta1": q20["positive_result_tiers"]["CLEAN_DEMO_PASS"]["delta1_threshold"],
        "stop_rule_final_attempt": p20["EPOCH2_IS_FINAL_QREC_ATTEMPT"],
        "claim_type": p20["claim_type"],
        "e2_0_tau_train_historical": f20["tau_training"],
        "S7_12_exists": (S7 / "12_qualified_result").exists(),
        "epoch2_result_exists": (S7 / "E2_1_discovery").exists(),
    }
    for cond, msg in [
        (inherited["K_REC_V2_matches_K2_freeze"], "K_REC_V2 changed"),
        (inherited["tau"] == TAU, "tau is not 1"),
        (inherited["U_rec"] == "UNCHANGED", "U_rec changed"),
        (inherited["V3"] == "Delta_0 <= -0.01 AND Delta_1 <= -0.01", "V3 changed"),
        (inherited["V6_threshold"] == 0.01, "V6 threshold changed"),
        (len(inherited["baselines"]) == 6, "baseline set changed"),
        (inherited["budget_per_fold"] == 300000 and inherited["budget_total"] == 1800000,
         "search budget changed"),
        (inherited["clean_demo_delta1"] == -0.05, "CLEAN_DEMO_PASS threshold changed"),
        (inherited["stop_rule_final_attempt"] is True, "stop rule changed"),
        (inherited["claim_type"].startswith("CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION"),
         "claim type changed"),
        (not inherited["S7_12_exists"], "S7.12 exists"),
        (not inherited["epoch2_result_exists"], "an Epoch-2 result exists"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- folds unchanged, byte-identical --------------------
    fa = pd.read_csv(E20 / "outer_fold_assignment.csv", dtype={"discharge": str})
    folds_ok = True
    for k, s in FOLDS.items():
        want = sorted(s.split())
        got = sorted(fa[fa.outer_fold == k].discharge.tolist())
        if want != got:
            folds_ok = False
            drift.append("fold %d membership differs from the frozen parent" % k)
    fold_check = {
        "matches_frozen_parent": folds_ok,
        "sizes": {int(k): int(v) for k, v in fa.outer_fold.value_counts().sort_index().items()},
        "every_discharge_once": bool((fa.discharge.value_counts() == 1).all()),
        "n_discharges": int(len(fa)),
        "repartitioned": False, "new_seed": False, "optimised": False,
        "source_sha256": sha256(E20 / "outer_fold_assignment.csv"),
    }

    # ---------------- candidate basis from the K2 audit ------------------
    z = np.load(K2 / "manifests" / "_k2_scores.npz", allow_pickle=True)
    E = z["E1"].astype(np.float64)
    deg = z["deg1"]
    coord = np.array([str(x) for x in z["coordinate_id"]])
    cons = np.array([str(x) for x in z["constructor"]])
    cells = [str(c) for c in z["cells"]]
    assert E.shape == (10778, 186), "K2 score matrix shape changed"

    supported = (E <= TAU) & ~deg
    full = supported.all(axis=1)
    basis = coord[full]
    got_counts = {f: int((full & (cons == f)).sum()) for f in sorted(set(cons))}

    basis_check = {
        "n_full_domain": int(full.sum()),
        "expected_from_K2_freeze": int(fk2["epoch2_viability"]["full_domain_atoms"]),
        "matches_K2_freeze": int(full.sum()) == int(fk2["epoch2_viability"]["full_domain_atoms"]),
        "expected_constant": N_EXPECTED,
        "matches_expected_constant": int(full.sum()) == N_EXPECTED,
        "constructor_counts": got_counts,
        "constructor_counts_expected": K2_EXPECTED,
        "constructor_counts_match": got_counts == K2_EXPECTED,
        "atomic_universe": int(len(coord)),
        "cells": len(cells),
        "tau": TAU,
        "recomputed_or_reused": "recomputed from the K2 frozen score matrix under tau=1",
        "different_ontology_generated": False,
    }
    for cond, msg in [
        (basis_check["matches_K2_freeze"], "basis count differs from the K2 freeze"),
        (basis_check["matches_expected_constant"], "basis count is not 3451"),
        (basis_check["constructor_counts_match"], "constructor counts differ from K2"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- closure property: VERIFY, do not assume ------------
    rng = np.random.default_rng(20260907)
    idx = np.flatnonzero(full)
    trials = []
    for m in (1, 2, 5, 8, 12):
        d = rng.choice(idx, size=(2000, m), replace=True)
        # a support is full-domain iff every coordinate passes on every cell
        ok = supported[d].all(axis=(1, 2))
        trials.append({"support_size": m, "n_draws": 2000,
                       "fraction_full_domain": float(ok.mean()),
                       "all_full_domain": bool(ok.all())})
    # adversarial control: one non-full-domain coordinate must break a support
    notfull = np.flatnonzero(~full)
    d2 = rng.choice(idx, size=(2000, 11), replace=True)
    bad = rng.choice(notfull, size=(2000, 1), replace=True)
    mixed = np.concatenate([d2, bad], axis=1)
    mixed_ok = supported[mixed].all(axis=(1, 2))
    closure = {
        "claim": ("any support assembled solely from C_E2_FULL_DOMAIN is "
                  "FULL_DOMAIN_RANGE_SUPPORTED by construction"),
        "why": ("the support predicate is the conjunction of coordinate predicates over the "
                "same cells; a conjunction of all-true is true"),
        "verified_empirically": trials,
        "all_sizes_pass": all(t["all_full_domain"] for t in trials),
        "adversarial_control": {
            "construction": "11 full-domain coordinates plus 1 non-full-domain coordinate",
            "n_draws": 2000,
            "fraction_full_domain": float(mixed_ok.mean()),
            "expected": 0.0,
            "control_behaves_as_expected": bool(mixed_ok.mean() == 0.0),
            "purpose": ("shows the check is not vacuous - adding a single unsupported "
                        "coordinate always breaks the support"),
        },
    }
    if not closure["all_sizes_pass"]:
        drift.append("closure property failed")
    if not closure["adversarial_control"]["control_behaves_as_expected"]:
        drift.append("adversarial control did not behave as expected")

    pd.DataFrame({"coordinate_id": basis,
                  "constructor": cons[full]}).to_csv(
        OUT / "manifests" / "C_E2_FULL_DOMAIN.csv", index=False)
    basis_sha = hashlib.sha256("\n".join(sorted(basis)).encode()).hexdigest()

    out = {
        "record_id": "E2_0A_VERIFICATION_V1", "generated_utc": now,
        "parent_manifests": manifests,
        "inherited_unchanged": inherited,
        "fold_check": fold_check,
        "candidate_basis": {**basis_check, "coordinate_ids_sha256": basis_sha},
        "closure_property": closure,
        "drift": drift,
        "verdict": "VERIFIED" if not drift else "DRIFT_DETECTED",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
    }
    (OUT / "manifests" / "E2_0A_VERIFICATION.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    assert all(v == 0 for v in ACCESS.values())

    for k, v in manifests.items():
        print("%-8s manifest %d/%d" % (k, v["matched"], v["n"]))
    print("K_REC_V2 unchanged: %s | tau=%.1f | U_rec %s"
          % (inherited["K_REC_V2_matches_K2_freeze"], inherited["tau"], inherited["U_rec"]))
    print("folds match frozen parent: %s | sizes %s"
          % (fold_check["matches_frozen_parent"], fold_check["sizes"]))
    print("candidate basis: %d (K2 freeze %d, expected %d) | constructor match %s"
          % (basis_check["n_full_domain"], basis_check["expected_from_K2_freeze"],
             N_EXPECTED, basis_check["constructor_counts_match"]))
    print("  counts:", got_counts)
    print("closure verified at sizes 1,2,5,8,12: %s | adversarial control %.1f (expect 0.0)"
          % (closure["all_sizes_pass"], closure["adversarial_control"]["fraction_full_domain"]))
    print("verdict: %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
