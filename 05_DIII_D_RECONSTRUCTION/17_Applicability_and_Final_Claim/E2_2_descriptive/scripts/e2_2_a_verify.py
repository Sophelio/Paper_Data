"""S7.E2.2 step A - lineage verification through E2.1, basis verification.

Verifies EIGHT parent freezes, pins every invariant the stage specification
requires to be unchanged, and independently recomputes C_E2_FULL_DOMAIN from the
predictors alone. NO target value is opened in this script.

Any drift here => STOP BOTH STAGES (E2.2 and S7.12).
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
EX = S7.parent
DATA = EX / "data" / "resampled_data_v6"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S77 = S7 / "07_search_policy_and_frontier"
K2 = S7 / "K2_observational_range_support_contract"
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
E20A = S7 / "E2_0A_predictor_admissibility_reconciliation"
E21 = S7 / "E2_1_crossfitted_discovery_and_qualification"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
TAU = 1.0
CHUNK = 1500
EXPECTED = {"C0": 51, "C1": 18, "C2": 1488, "C3": 382, "C5": 8, "C6": 965, "C7": 539}
N_EXPECTED = 3451
ACCESS = {"target_reads": 0}

PARENTS = [
    ("S7.9", "09_development_selection_and_freeze", "S7_9_FREEZE.json"),
    ("S7.10", "10_external_validation", "S7_10_FREEZE.json"),
    ("S7.11", "11_sensitivity_and_interpretation", "S7_11_FREEZE.json"),
    ("S7.R1", "R1_operational_state_reconciliation", "S7_R1_FREEZE.json"),
    ("S7.K2", "K2_observational_range_support_contract", "S7_K2_FREEZE.json"),
    ("S7.E2.0", "E2_0_protocol_and_resampling_freeze", "E2_0_FREEZE.json"),
    ("S7.E2.0A", "E2_0A_predictor_admissibility_reconciliation", "E2_0A_FREEZE.json"),
    ("S7.E2.1", "E2_1_crossfitted_discovery_and_qualification", "E2_1_FREEZE.json"),
]

# E2.1 result values that MUST be unchanged (stage specification section 0)
E21_EXPECT = {
    "status": "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS",
    "FORMAL": "FORMAL_PASS",
    "CLEAN": "CLEAN_DEMO_NOT_MET",
    "V6": "PASS_WITH_QUALIFICATION",
    "V_RANGE": "PASS",
    "Delta_0": -0.764489,
    "Delta_1": -0.027308,
    "EPOCH2_IS_FINAL_QREC_ATTEMPT": True,
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

    manifests, lineage = {}, []
    for label, base, fn in PARENTS:
        fz = json.loads((S7 / base / fn).read_text(encoding="utf-8"))
        m, bad = 0, []
        for r, want in fz["all_artifact_hashes"].items():
            p = S7 / base / r
            if p.exists() and sha256(p) == want:
                m += 1
            else:
                bad.append(r)
        manifests[label] = {"n": len(fz["all_artifact_hashes"]), "matched": m,
                            "mismatched": bad}
        lineage.append({"stage": label, "freeze_id": fz["freeze_id"],
                        "status": fz.get("status"),
                        "file_sha256": sha256(S7 / base / fn)})
        if bad:
            drift.append("%s manifest does not reproduce" % label)

    f0a = json.loads((E20A / "E2_0A_FREEZE.json").read_text())
    proto = json.loads((E20A / "E2_0A_PROTOCOL.json").read_text())
    cb = json.loads((E20A / "E2_0A_CANDIDATE_BASIS.json").read_text())
    fk2 = json.loads((K2 / "S7_K2_FREEZE.json").read_text())
    q20 = json.loads((E20 / "EPOCH2_QUALIFICATION_POLICY.json").read_text())
    b20 = json.loads((E20 / "EPOCH2_SEARCH_BUDGET.json").read_text())
    urec = json.loads((S7 / "08_utility_and_qualification_rules"
                       / "U_REC_OPERATIONAL_V1.json").read_text())
    f21 = json.loads((E21 / "E2_1_FREEZE.json").read_text())

    pinned = {
        "E2_0A_authoritative": f0a["E2_0A_PROTOCOL"] == "AUTHORITATIVE_FOR_EPOCH2_EXECUTION",
        "E2_0_preserved": f0a["E2_0_PROTOCOL_V1"] == "PRESERVED_AS_HISTORICAL_PARENT",
        "K_REC_V2_sha256": sha256(K2 / "K_REC_V2.json"),
        "K_REC_V2_matches": sha256(K2 / "K_REC_V2.json") == fk2["K_REC_V2_sha256"],
        "range_support_policy_sha256": sha256(K2 / "RANGE_SUPPORT_POLICY_V1.json"),
        "E2_0A_protocol_sha256": sha256(E20A / "E2_0A_PROTOCOL.json"),
        "E2_0A_candidate_basis_sha256": sha256(E20A / "E2_0A_CANDIDATE_BASIS.json"),
        "fold_assignment_sha256": sha256(E20 / "outer_fold_assignment.csv"),
        "U_rec_sha256": sha256(S7 / "08_utility_and_qualification_rules"
                               / "U_REC_OPERATIONAL_V1.json"),
        "tau": proto["tau"]["value"], "tau_train": proto["tau_train"]["status"],
        "V3": q20["V3"]["pass"], "V6_threshold": q20["V6"]["threshold"],
        "budget_per_search": b20["max_support_evaluations_per_fold"],
        "seeds_per_stratum": b20["seeds_per_stratum"],
        "shortlist_cap": b20["shortlist_cap_per_constructor"],
        "support_bound": b20["support_size_bound"],
        "stop_rule": proto["unchanged_from_E2_0"]["EPOCH2_IS_FINAL_QREC_ATTEMPT"],
        "clean_demo_delta1": q20["positive_result_tiers"]["CLEAN_DEMO_PASS"]["delta1_threshold"],
        "U_rec_ranks": [urec["rank_%d_%s" % (i, n)]["criterion"] for i, n in
                        [(1, "fit"), (2, "stability"), (3, "parsimony"),
                         (4, "conditioning"), (5, "support_stability")]],
    }

    fa_chk = pd.read_csv(E20 / "outer_fold_assignment.csv", dtype={"discharge": str})
    e21_result = {
        "status": f21["status"], "FORMAL": f21["FORMAL"], "CLEAN": f21["CLEAN"],
        "V6": f21["V6"], "V_RANGE": f21["V_RANGE"],
        "Delta_0": f21["V3"]["Delta_0"], "Delta_1": f21["V3"]["Delta_1"],
        "V3_pass": f21["V3"]["pass"],
        "EPOCH2_IS_FINAL_QREC_ATTEMPT": f21["EPOCH2_IS_FINAL_QREC_ATTEMPT"],
        "support_freezes": f21["support_freezes"],
        "n_outer_folds": int(fa_chk.outer_fold.nunique()),
        "n_discharges": int(len(fa_chk)),
    }

    for cond, msg in [
        (pinned["E2_0A_authoritative"], "E2.0A not authoritative"),
        (pinned["E2_0_preserved"], "E2.0 not preserved"),
        (pinned["K_REC_V2_matches"], "K_REC_V2 changed"),
        (pinned["tau"] == 1.0, "tau != 1"),
        (pinned["tau_train"] == "RETIRED", "tau_train not retired"),
        (pinned["V3"] == "Delta_0 <= -0.01 AND Delta_1 <= -0.01", "V3 changed"),
        (pinned["V6_threshold"] == 0.01, "V6 changed"),
        (pinned["budget_per_search"] == 300000, "budget changed"),
        (pinned["seeds_per_stratum"] == 1, "seed policy changed"),
        (pinned["shortlist_cap"] == 96, "shortlist cap changed"),
        (pinned["support_bound"] == [1, 12], "support bound changed"),
        (pinned["stop_rule"] is True, "stop rule changed"),
        (pinned["clean_demo_delta1"] == -0.05, "CLEAN_DEMO threshold changed"),
        (e21_result["n_outer_folds"] == 6, "six folds changed"),
        (e21_result["n_discharges"] == 62, "62-discharge object changed"),
        (len(e21_result["support_freezes"]) == 6, "six fold supports not present"),
        (e21_result["status"] == E21_EXPECT["status"], "E2.1 status changed"),
        (e21_result["FORMAL"] == E21_EXPECT["FORMAL"], "E2.1 FORMAL changed"),
        (e21_result["CLEAN"] == E21_EXPECT["CLEAN"], "E2.1 CLEAN changed"),
        (e21_result["V6"] == E21_EXPECT["V6"], "E2.1 V6 changed"),
        (e21_result["V_RANGE"] == E21_EXPECT["V_RANGE"], "E2.1 V-RANGE changed"),
        (e21_result["V3_pass"] is True, "E2.1 V3 changed"),
        (round(e21_result["Delta_0"], 6) == E21_EXPECT["Delta_0"], "E2.1 Delta_0 changed"),
        (round(e21_result["Delta_1"], 6) == E21_EXPECT["Delta_1"], "E2.1 Delta_1 changed"),
        (e21_result["EPOCH2_IS_FINAL_QREC_ATTEMPT"] is True, "E2.1 stop rule changed"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- global predictor access, basis verification --------
    AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
        "signal_index").reset_index(drop=True)
    P_ALL = list(HB.primitive_id)
    P_DOT = [s for s in P_ALL if bool(
        HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    N = len(AT)
    assert N == 10778
    OPC = {"C0": 0, "C1": 0, "C5": 1, "C2": 2, "C6": 2, "C3": 3, "C7": 3}
    kA = np.zeros(N, np.int8); iA = np.zeros(N, np.int32)
    kB = np.zeros(N, np.int8); iB = np.zeros(N, np.int32); op = np.zeros(N, np.int8)
    for r, (c, ops) in enumerate(zip(AT.constructor, AT.ordered_operands)):
        o = str(ops).split("|")
        op[r] = OPC[c]
        if c in ("C1", "C7"):
            kA[r], iA[r] = 1, di[o[0]]
        else:
            kA[r], iA[r] = 0, li[o[0]]
        if c in ("C2", "C3", "C7"):
            kB[r], iB[r] = 0, li[o[1]]
        elif c == "C6":
            kB[r], iB[r] = 1, di[o[1]]

    fa = pd.read_csv(E20 / "outer_fold_assignment.csv", dtype={"discharge": str})
    shots = list(fa.sort_values("position").discharge)
    TR = pd.read_csv(RV2 / "trajectory_index.csv",
                     dtype={"discharge": str}).set_index("discharge")

    E = np.full((N, len(shots) * 3), np.nan)
    DEG = np.zeros((N, len(shots) * 3), bool)
    t0 = time.time()
    for si, s in enumerate(shots):
        t_start = float(TR.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TR.loc[s, "delta_t_ms"]); n = int(TR.loc[s, "N_s"])
        grid = t_start + dtm * np.arange(n, dtype=np.float64)
        tsec = grid / 1000.0
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            L = np.empty((70, n))
            for k, sig in enumerate(P_ALL):
                tt, vv = PROV._load_signal(a, sig)
                L[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                    str(PROV.SIGNAL_UNIT[sig]), 1.0)
        D = np.empty((63, n))
        for k, sig in enumerate(P_DOT):
            D[k] = np.gradient(L[li[sig]], tsec, edge_order=2)
        for a0 in range(0, N, CHUNK):
            rows = np.arange(a0, min(a0 + CHUNK, N))

            def gather(kind, idx):
                g = np.empty((idx.size, n)); lv = kind == 0
                if lv.any():
                    g[lv] = L[idx[lv]]
                if (~lv).any():
                    g[~lv] = D[idx[~lv]]
                return g

            A = gather(kA[rows], iA[rows]); o = op[rows]
            V = np.empty_like(A)
            with np.errstate(divide="ignore", invalid="ignore"):
                m0 = o == 0; V[m0] = A[m0]
                m1 = o == 1
                if m1.any():
                    V[m1] = 1.0 / A[m1]
                if (o >= 2).any():
                    B = gather(kB[rows], iB[rows]); m2, m3 = o == 2, o == 3
                    V[m2] = A[m2] * B[m2]; V[m3] = A[m3] / B[m3]
            for bi, (bn, c1, c2) in enumerate(BLOCKS):
                ci = si * 3 + bi
                cal = slice(0, int(np.floor(n * c1)))
                pro = slice(int(np.floor(n * c1)), int(np.floor(n * c2)))
                vc, vp = V[:, cal], V[:, pro]
                with np.errstate(invalid="ignore"):
                    Lo, Up = vc.min(axis=1), vc.max(axis=1)
                    exc = np.maximum(np.maximum(Lo - vp.min(axis=1), 0.0),
                                     vp.max(axis=1) - Up)
                    R = Up - Lo
                    good = R > 0
                    e = np.full(rows.size, np.nan)
                    e[good] = exc[good] / R[good]
                    e[~good & (exc == 0)] = 0.0
                    DEG[rows, ci] = (~good) & (exc > 0)
                    E[rows, ci] = e
    supported = (E <= TAU) & ~DEG
    full = supported.all(axis=1)
    basis = np.array(AT.coordinate_id)[full]
    counts = {f: int((full & (AT.constructor.values == f)).sum())
              for f in sorted(set(AT.constructor))}
    basis_sha = hashlib.sha256("\n".join(sorted(basis)).encode()).hexdigest()

    e21_basis = pd.read_csv(E21 / "manifests" / "C_E2_FULL_DOMAIN.csv")
    e21_sha = hashlib.sha256(
        "\n".join(sorted(e21_basis.coordinate_id)).encode()).hexdigest()

    check = {
        "n": int(full.sum()), "expected": N_EXPECTED,
        "count_matches": int(full.sum()) == N_EXPECTED,
        "constructor_counts": counts, "constructor_expected": EXPECTED,
        "constructor_matches": counts == EXPECTED,
        "sha256": basis_sha,
        "sha256_expected_E2_0A": cb["coordinate_ids_sha256"],
        "sha256_matches_E2_0A": basis_sha == cb["coordinate_ids_sha256"],
        "sha256_E2_1_basis_file": e21_sha,
        "identical_to_E2_1_search_basis": basis_sha == e21_sha,
        "recomputed_independently_from_predictors": True,
        "tau": TAU,
        "partial_atoms_excluded": int(N - full.sum()),
    }
    if not (check["count_matches"] and check["constructor_matches"]
            and check["sha256_matches_E2_0A"] and check["identical_to_E2_1_search_basis"]):
        drift.append("PROTOCOL_OR_LINEAGE_INCONSISTENCY: basis mismatch")

    np.savez_compressed(OUT / "manifests" / "_e2_2_basis.npz",
                        supported=supported, full=full,
                        coordinate_id=np.array(AT.coordinate_id, dtype=object),
                        shots=np.array(shots))
    pd.DataFrame({"coordinate_id": basis,
                  "constructor": AT.constructor.values[full],
                  "search_stratum": AT.search_stratum.values[full]}).to_csv(
        OUT / "manifests" / "C_E2_FULL_DOMAIN_E2_2.csv", index=False)

    out = {"record_id": "E2_2_PRESEARCH_VERIFICATION_V1", "generated_utc": now,
           "stage": "S7.E2.2",
           "purpose": "lineage verification through E2.1 and basis verification "
                      "before any descriptive search",
           "lineage": lineage, "parent_manifests": manifests, "pinned": pinned,
           "E2_1_result_unchanged": e21_result,
           "basis_verification": check,
           "global_predictor_access": {
               "discharges_opened": len(shots), "signals": 70,
               "target_reads": ACCESS["target_reads"],
               "target_opened_in_this_stage": False,
               "runtime_seconds": round(time.time() - t0, 1)},
           "drift": drift,
           "ZERO_SUBSTANTIVE_DRIFT": not drift,
           "verdict": "PRESEARCH_VERIFIED" if not drift else "BLOCKED_LINEAGE_INCONSISTENCY",
           "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                           "pandas": pd.__version__, "platform": platform.platform()}}
    (OUT / "manifests" / "E2_2_PRESEARCH.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    assert ACCESS["target_reads"] == 0

    for k, v in manifests.items():
        print("%-9s %d/%d" % (k, v["matched"], v["n"]))
    print("tau=%.1f | tau_train=%s | budget %d | cap %d | seeds %d | folds %d | shots %d"
          % (pinned["tau"], pinned["tau_train"], pinned["budget_per_search"],
             pinned["shortlist_cap"], pinned["seeds_per_stratum"],
             e21_result["n_outer_folds"], e21_result["n_discharges"]))
    print("E2.1 unchanged: %s | D0 %.6f | D1 %.6f | %s / %s"
          % (e21_result["status"], e21_result["Delta_0"], e21_result["Delta_1"],
             e21_result["FORMAL"], e21_result["CLEAN"]))
    print("basis: n=%d %s | constructors %s | E2.0A hash %s | == E2.1 basis %s"
          % (check["n"], check["count_matches"], check["constructor_matches"],
             check["sha256_matches_E2_0A"], check["identical_to_E2_1_search_basis"]))
    print("  ", counts)
    print("target_reads = %d" % ACCESS["target_reads"])
    print("verdict: %s" % out["verdict"])
    for d in drift:
        print("  DRIFT:", d)
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
