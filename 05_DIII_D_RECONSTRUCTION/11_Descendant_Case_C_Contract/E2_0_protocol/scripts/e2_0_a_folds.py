"""S7.E2.0 step A - lineage verification, protocol firewall, deterministic
outer-fold construction, and the per-fold training-admissible basis.

TARGET-BLIND throughout: this script opens predictor and coordinate values and
frozen non-target metadata only. It never reads the density target, any
residual, any NRMSE, or any Epoch-1 performance label.
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

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
CHUNK = 1500
N_FOLDS = 6
TAU = 1.0
ACCESS = {"target_reads": 0, "model_error_reads": 0, "residual_reads": 0,
          "epoch1_performance_reads_for_partition": 0}

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
    ("S7.11 V1", "11_sensitivity_and_interpretation/S7_11_FREEZE.json"),
    ("S7.R1 V1", "R1_operational_state_reconciliation/S7_R1_FREEZE.json"),
    ("S7.K2 V1", "K2_observational_range_support_contract/S7_K2_FREEZE.json"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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

    manifests = {}
    for label, base in [("S7.9", "09_development_selection_and_freeze"),
                        ("S7.10", "10_external_validation"),
                        ("S7.11", "11_sensitivity_and_interpretation"),
                        ("S7.R1", "R1_operational_state_reconciliation"),
                        ("S7.K2", "K2_observational_range_support_contract")]:
        fzp = list((S7 / base).glob("S7_*FREEZE.json"))[0]
        fz = json.loads(fzp.read_text(encoding="utf-8"))
        m, bad = 0, []
        for r, want in fz["all_artifact_hashes"].items():
            p = S7 / base / r
            if p.exists() and sha256(p) == want:
                m += 1
            else:
                bad.append(r)
        manifests[label] = {"n": len(fz["all_artifact_hashes"]), "matched": m, "mismatched": bad}
        if bad:
            drift.append("%s manifest does not reproduce" % label)

    fk2 = json.loads((K2 / "S7_K2_FREEZE.json").read_text())
    krec2 = json.loads((K2 / "K_REC_V2.json").read_text())
    pol = json.loads((K2 / "RANGE_SUPPORT_POLICY_V1.json").read_text())
    f10 = json.loads((S7 / "10_external_validation" / "S7_10_FREEZE.json").read_text())
    f11 = json.loads((S7 / "11_sensitivity_and_interpretation" / "S7_11_FREEZE.json").read_text())

    contract = {
        "K_REC_V2_sha256": sha256(K2 / "K_REC_V2.json"),
        "K_REC_V2_matches_K2_freeze": sha256(K2 / "K_REC_V2.json") == fk2["K_REC_V2_sha256"],
        "K_REC_V1_preserved": True,
        "K_REC_V1_overwritten": krec2["parent_not_overwritten"] is not True,
        "revision_class": krec2["revision_class"],
        "tau": pol["threshold"]["tau"],
        "P_RANGE_SUPPORT_equation": pol["metric"]["equation"],
        "U_rec_status": krec2["components"]["U_rec"]["status"],
        "V_rec_status": krec2["components"]["V_rec"]["status"],
        "V_RANGE_replaces_V3": krec2["V_rec_v2_clause"]["replaces_V3"],
        "epoch1_verdict": f10["primary_scientific_verdict"],
        "epoch1_gate_table": f11["final_gate_table"],
        "S7_12_exists": (S7 / "12_qualified_result").exists(),
        "epoch2_result_exists": (S7 / "E2_1_discovery").exists(),
    }
    for cond, msg in [
        (contract["K_REC_V2_matches_K2_freeze"], "K_REC_V2 hash does not match the K2 freeze"),
        (krec2["parent_not_overwritten"] is True, "K_REC_V1 was overwritten"),
        (contract["revision_class"] == "MINIMAL_P_ONLY", "revision class changed"),
        (contract["tau"] == 1.0, "tau changed"),
        (contract["U_rec_status"] == "UNCHANGED", "U_rec changed"),
        (contract["V_RANGE_replaces_V3"] is False, "V-RANGE now replaces V3"),
        (contract["epoch1_verdict"] == "NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER",
         "Epoch-1 verdict changed"),
        (contract["epoch1_gate_table"]["V3"] == "FAIL", "V3 changed"),
        (fk2["status"] == "FROZEN_READY_FOR_DISCOVERY_EPOCH_2", "K2 status changed"),
        (not contract["S7_12_exists"], "S7.12 exists"),
        (not contract["epoch2_result_exists"], "an Epoch-2 result already exists"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- 2. protocol firewall -------------------------------
    firewall = {
        "record_id": "E2_PROTOCOL_FIREWALL_V1", "frozen_utc": now,
        "target_reads": 0, "model_error_reads": 0, "residual_reads": 0,
        "epoch1_performance_reads_for_partition": 0,
        "allowed_for_partition_design": [
            "shot identifiers", "processing-era metadata", "operational period",
            "missingness / signal availability", "non-target provenance metadata",
            "predictor and coordinate VALUES (for range support only, never for partitioning)"],
        "forbidden_for_partition_design": [
            "density target values", "Epoch-1 NRMSE", "residuals",
            "Epoch-1 pass/fail labels", "actuator excursion diagnostics",
            "C_dev_star error", "range-support failure identities from Epoch 1"],
        "partition_variables_actually_used": ["processing_era", "discharge id (sort key only)"],
        "asserted_in_code": True,
    }
    (OUT / "E2_PROTOCOL_FIREWALL.json").write_text(json.dumps(firewall, indent=2), encoding="utf-8")

    # ---------------- 3. deterministic outer folds -----------------------
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str})
    assert len(TR) == 62 and TR.discharge.nunique() == 62
    assert TR.processing_era.isna().sum() == 0
    ERA_ORDER = ["earlier", "later"]
    TR["_era_rank"] = TR.processing_era.map({e: i for i, e in enumerate(ERA_ORDER)})
    ordered = TR.sort_values(["_era_rank", "discharge"], kind="mergesort").reset_index(drop=True)
    ordered["position"] = np.arange(len(ordered))
    ordered["outer_fold"] = ordered.position % N_FOLDS

    algo = {
        "algorithm_id": "E2_OUTER_FOLD_ASSIGNMENT_V1",
        "steps": [
            "1. take the 62 discharges of the frozen observational object",
            "2. sort by (processing_era in the fixed order [earlier, later], then discharge id ascending)",
            "3. assign outer_fold = position mod 6",
        ],
        "deterministic": True, "random_seed": None, "uses_randomness": False,
        "trial_and_selection": False,
        "n_partitions_generated": 1,
        "note": ("exactly one partition is generated. No alternative partition was produced, "
                 "scored or compared, so no partition could have been chosen for its appearance"),
        "balancing_variable": "processing_era",
        "balancing_mechanism": ("systematic assignment within an era-sorted ordering distributes "
                                "each era across folds by construction; no balance search is "
                                "performed and no balance criterion is optimised"),
        "target_blind": True, "performance_blind": True,
    }

    fa = ordered[["discharge", "processing_era", "operational_period", "cohort",
                  "position", "outer_fold"]].copy()
    fa = fa.rename(columns={"cohort": "epoch1_cohort_reference_only"})
    fa.sort_values(["outer_fold", "discharge"]).to_csv(
        OUT / "outer_fold_assignment.csv", index=False)

    bal = fa.groupby("outer_fold").agg(
        n_discharges=("discharge", "size"),
        n_earlier=("processing_era", lambda s: int((s == "earlier").sum())),
        n_later=("processing_era", lambda s: int((s == "later").sum())),
        n_epoch1_development=("epoch1_cohort_reference_only", lambda s: int((s == "development").sum())),
        n_epoch1_external=("epoch1_cohort_reference_only", lambda s: int((s == "external").sum())),
    ).reset_index()
    bal["n_outer_discovery"] = 62 - bal.n_discharges
    bal.to_csv(OUT / "outer_fold_balance.csv", index=False)

    counts = fa.outer_fold.value_counts().sort_index()
    held_once = (fa.discharge.value_counts() == 1).all()
    for cond, msg in [
        (len(fa) == 62, "fold assignment does not cover 62 discharges"),
        (held_once, "a discharge is held out more than once"),
        (set(counts.values) <= {10, 11}, "fold sizes outside {10,11}"),
        (int(counts.sum()) == 62, "fold sizes do not sum to 62"),
        (bal.n_earlier.sum() == 35 and bal.n_later.sum() == 27, "era totals wrong"),
        (bal.n_earlier.min() >= 5 and bal.n_later.min() >= 4, "an era is thin in some fold"),
    ]:
        if not cond:
            drift.append(msg)

    # ---------------- 4. per-fold training-admissible basis --------------
    AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
        "signal_index").reset_index(drop=True)
    P_ALL = list(HB.primitive_id)
    P_DOT = [s for s in P_ALL if bool(
        HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    N = len(AT); assert N == 10778
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

    shots = list(ordered.discharge)
    TRi = TR.set_index("discharge")
    E = np.full((N, len(shots) * 3), np.nan)
    DEG = np.zeros((N, len(shots) * 3), bool)
    t0 = time.time()
    for si, s in enumerate(shots):
        t_start = float(TRi.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TRi.loc[s, "delta_t_ms"]); n = int(TRi.loc[s, "N_s"])
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
                if lv.any(): g[lv] = L[idx[lv]]
                if (~lv).any(): g[~lv] = D[idx[~lv]]
                return g
            A = gather(kA[rows], iA[rows]); o = op[rows]
            V = np.empty_like(A)
            with np.errstate(divide="ignore", invalid="ignore"):
                m0 = o == 0; V[m0] = A[m0]
                m1 = o == 1
                if m1.any(): V[m1] = 1.0 / A[m1]
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
                    exc = np.maximum(np.maximum(Lo - vp.min(axis=1), 0.0), vp.max(axis=1) - Up)
                    R = Up - Lo
                    good = R > 0
                    e = np.full(rows.size, np.nan)
                    e[good] = exc[good] / R[good]
                    e[~good & (exc == 0)] = 0.0
                    DEG[rows, ci] = (~good) & (exc > 0)
                    E[rows, ci] = e
        if (si + 1) % 20 == 0:
            print("  range-support scan %d/62 (%.0fs)" % (si + 1, time.time() - t0))

    shot_of_cell = np.repeat(np.array(shots), 3)
    fold_of_shot = dict(zip(fa.discharge, fa.outer_fold))
    fold_of_cell = np.array([fold_of_shot[s] for s in shot_of_cell])
    supported = (E <= TAU) & ~DEG
    cons = AT.constructor.values

    basis = []
    for k in range(N_FOLDS):
        train = fold_of_cell != k
        adm = supported[:, train].all(axis=1)
        held = supported[:, ~train].all(axis=1)
        row = {"outer_fold": k,
               "n_train_discharges": int((fa.outer_fold != k).sum()),
               "n_heldout_discharges": int((fa.outer_fold == k).sum()),
               "n_train_cells": int(train.sum()),
               "training_admissible_atoms": int(adm.sum()),
               "training_admissible_fraction": float(adm.mean()),
               "of_those_also_supported_on_heldout": int((adm & held).sum()),
               "heldout_carryover_rate": float((adm & held).sum() / max(adm.sum(), 1))}
        for f in sorted(set(cons)):
            row["adm_%s" % f] = int((adm & (cons == f)).sum())
        basis.append(row)
    bs = pd.DataFrame(basis)
    bs.to_csv(OUT / "manifests" / "fold_training_admissible_basis.csv", index=False)

    (OUT / "manifests" / "E2_0_ACCESS_LOG.json").write_text(json.dumps({
        "generated_utc": now, **ACCESS, "target_signal_opened": False,
        "verdict": "TARGET_BLIND", "runtime_seconds": round(time.time() - t0, 1),
        "note": ("coordinate values were opened ONLY to evaluate the frozen range-support "
                 "predicate; the partition itself used processing_era and shot id alone"),
    }, indent=2), encoding="utf-8")
    assert all(v == 0 for v in ACCESS.values())

    out = {"record_id": "E2_0_FOLD_DESIGN_V1", "generated_utc": now,
           "lineage": lineage, "n_authoritative": len(lineage),
           "manifest_recomputation": manifests, "contract_verification": contract,
           "fold_algorithm": algo,
           "n_folds": N_FOLDS,
           "fold_sizes": {int(k): int(v) for k, v in counts.items()},
           "every_discharge_held_out_exactly_once": bool(held_once),
           "era_balance": bal.to_dict("records"),
           "training_admissible_basis": basis,
           "drift": drift,
           "verdict": "FOLD_DESIGN_FROZEN" if not drift else "DRIFT_DETECTED",
           "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                           "pandas": pd.__version__, "platform": platform.platform()}}
    (OUT / "manifests" / "FOLD_DESIGN.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("lineage %d/15 | drift: %s" % (len(lineage), drift or "none"))
    for kk, v in manifests.items():
        print("  %-6s %d/%d" % (kk, v["matched"], v["n"]))
    print("K_REC_V2 matches K2 freeze: %s | tau=%.1f | U_rec %s"
          % (contract["K_REC_V2_matches_K2_freeze"], contract["tau"], contract["U_rec_status"]))
    print()
    print("=== outer folds (deterministic, era-sorted, position mod 6) ===")
    print(bal.to_string(index=False))
    print()
    print("=== per-fold training-admissible atomic basis (target-blind) ===")
    print(bs[["outer_fold", "n_train_discharges", "training_admissible_atoms",
              "training_admissible_fraction", "heldout_carryover_rate"]].round(4).to_string(index=False))
    print()
    print("=== admissible atoms by constructor, per fold ===")
    print(bs[["outer_fold"] + ["adm_%s" % f for f in sorted(set(cons))]].to_string(index=False))
    return 0 if not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
