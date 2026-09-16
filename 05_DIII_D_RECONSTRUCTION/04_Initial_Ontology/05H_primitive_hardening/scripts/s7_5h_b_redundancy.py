"""S7.5H stage B — target-blind redundancy audit and construction of P_hard.

Opens DEVELOPMENT PREDICTOR values only, and only for members of the
redundancy-eligible groups. The density target is never loaded. No external
value is touched. No target statistic of any kind is computed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S5H = HERE.parent
S7 = S5H.parent
EX = S7.parent
S72 = S7 / "02_reconstruction_contract"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
MAN = S5H / "manifests"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

BLOCKS = [("A", 0.40), ("B", 0.60), ("C", 0.80)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4,
         "kW": 1e3}
ACCESS: list[dict] = []


def main() -> None:
    pol = json.loads((S5H / "HARDENING_POLICY_PREVALUE.json").read_text())
    frozen_sha = json.loads((MAN / "POLICY_FREEZE.json").read_text())["sha256"]
    live = hashlib.sha256(
        (S5H / "HARDENING_POLICY_PREVALUE.json").read_bytes()).hexdigest()
    if live != frozen_sha:
        raise SystemExit("STOP: hardening policy changed after freeze")

    TH = pol["C_thresholds_STABLY_NEAR_REDUNDANT"]
    N_MIN, RMED, R10, SGN = (TH["n_valid_cells_min"], TH["R_med_min"],
                             TH["R_10_min"], TH["sign_consistency_min"])

    P = pd.read_csv(S75 / "primitive_type_registry.csv")
    groups = pd.read_csv(S5H / "redundancy_eligible_groups.csv")
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = list(part["development"]["shot_ids"])
    ext = set(part["external"]["shot_ids"])
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str})
    TRd = TR[TR.cohort == "development"].set_index("discharge")

    idx = dict(zip(P.primitive_id, P.signal_index))
    elig_groups = groups[groups.redundancy_eligible]
    members = {r.semantic_group_id: r.members.split("|")
               for r in elig_groups.itertuples()}
    audited = sorted({s for v in members.values() for s in v},
                     key=lambda s: idx[s])
    assert "density" not in audited

    # ---- load development predictor values for audited signals only -------
    vals = {}
    for s in dev:
        if s in ext:
            raise SystemExit("STOP: FIREWALL_BREACH")
        t0 = float(TRd.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TRd.loc[s, "delta_t_ms"])
        n = int(TRd.loc[s, "N_s"])
        grid = t0 + dtm * np.arange(n, dtype=np.float64)
        M = np.empty((len(audited), n), dtype=np.float64)
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            for k, sig in enumerate(audited):
                tt, vv = PROV._load_signal(a, sig)
                f = CANON.get(str(PROV.SIGNAL_UNIT[sig]), 1.0)
                M[k] = PROV._resample_to_grid(tt, vv, grid) * f
        vals[s] = M
        ACCESS.append({"stage": "S7.5H-B", "shot_id": s,
                       "development_or_external": "development",
                       "predictor_signals_read": len(audited),
                       "target_values_read": 0,
                       "reason": "target-blind within-group redundancy audit "
                                 "on calibration intervals",
                       "timestamp": datetime.now(timezone.utc).isoformat()})
    ai = {s: k for k, s in enumerate(audited)}

    # ---- pairwise redundancy ---------------------------------------------
    rows = []
    for gid, mem in members.items():
        for a, b in combinations(sorted(mem, key=lambda s: idx[s]), 2):
            rs = []
            for s in dev:
                Mv = vals[s]
                n = Mv.shape[1]
                for bn, c1 in BLOCKS:
                    sl = slice(0, int(np.floor(n * c1)))
                    x, y = Mv[ai[a], sl], Mv[ai[b], sl]
                    m = np.isfinite(x) & np.isfinite(y)
                    if m.sum() < 3:
                        continue
                    xv, yv = x[m], y[m]
                    if xv.min() == xv.max() or yv.min() == yv.max():
                        continue          # constant: no redundancy claim
                    r = float(np.corrcoef(xv, yv)[0, 1])
                    if np.isfinite(r):
                        rs.append(r)
            nv = len(rs)
            if nv == 0:
                rows.append({"semantic_group_id": gid, "signal_i": a,
                             "signal_j": b, "n_valid_cells": 0,
                             "R_med": np.nan, "R_10": np.nan,
                             "sign_consistency": np.nan,
                             "stably_near_redundant": False})
                continue
            arr = np.array(rs)
            aabs = np.abs(arr)
            sc = max(float((arr > 0).mean()), float((arr < 0).mean()))
            rmed, r10 = float(np.median(aabs)), float(np.percentile(aabs, 10))
            rows.append({
                "semantic_group_id": gid, "signal_i": a, "signal_j": b,
                "n_valid_cells": nv, "R_med": rmed, "R_10": r10,
                "sign_consistency": sc,
                "stably_near_redundant": bool(
                    nv >= N_MIN and rmed >= RMED and r10 >= R10 and sc >= SGN),
            })
    PW = pd.DataFrame(rows)
    PW.to_csv(S5H / "pairwise_redundancy_audit.csv", index=False)

    # ---- deterministic representative selection ---------------------------
    edges = {}
    for r in PW[PW.stably_near_redundant].itertuples():
        edges.setdefault(r.signal_i, set()).add(r.signal_j)
        edges.setdefault(r.signal_j, set()).add(r.signal_i)
    wit = {(r.signal_i, r.signal_j): r for r in
           PW[PW.stably_near_redundant].itertuples()}

    reps, deferred = [], []
    for gid, mem in members.items():
        remaining = set(mem)
        while remaining:
            deg = {nd: len(edges.get(nd, set()) & remaining - {nd})
                   for nd in remaining}
            mx = max(deg.values())
            rep = sorted([n for n in remaining if deg[n] == mx],
                         key=lambda s: idx[s])[0]
            covered = sorted(edges.get(rep, set()) & remaining - {rep},
                             key=lambda s: idx[s])
            reps.append({"semantic_group_id": gid, "representative": rep,
                         "n_directly_covered": len(covered),
                         "covered_members": "|".join(covered)})
            for c in covered:
                w = wit.get((rep, c)) or wit.get((c, rep))
                deferred.append({
                    "primitive_id": c, "semantic_group_id": gid,
                    "representative": rep,
                    "R_med": w.R_med, "R_10": w.R_10,
                    "sign_consistency": w.sign_consistency,
                    "n_valid_cells": w.n_valid_cells,
                    "direct_witness": True,
                    "status": "REDUNDANCY_DEFERRED"})
            remaining -= {rep} | set(covered)
    REPS = pd.DataFrame(reps)
    REPS.to_csv(S5H / "redundancy_representatives.csv", index=False)
    DEF = pd.DataFrame(deferred) if deferred else pd.DataFrame(
        columns=["primitive_id", "semantic_group_id", "representative",
                 "R_med", "R_10", "sign_consistency", "n_valid_cells",
                 "direct_witness", "status"])

    deferred_ids = set(DEF.primitive_id) if len(DEF) else set()
    hard_ids = [s for s in P.primitive_id if s not in deferred_ids]

    # ---- bases -------------------------------------------------------------
    grp_of = {s: g for g, m in members.items() for s in m}
    rep_of = dict(zip(DEF.primitive_id, DEF.representative)) if len(DEF) else {}
    full_rows = []
    for r in P.itertuples():
        s = r.primitive_id
        dfr = DEF[DEF.primitive_id == s] if len(DEF) else DEF
        full_rows.append({
            "primitive_id": s, "signal_index": r.signal_index,
            "full_status": "IN_P_FULL",
            "hard_status": "REDUNDANCY_DEFERRED" if s in deferred_ids
                           else "IN_P_HARD",
            "semantic_group": grp_of.get(s, r.mathematical_type_block),
            "redundancy_eligible_group": s in grp_of,
            "representative": rep_of.get(s, ""),
            "witness_R_med": float(dfr.R_med.iloc[0]) if len(dfr) else np.nan,
            "witness_R_10": float(dfr.R_10.iloc[0]) if len(dfr) else np.nan,
            "witness_sign_consistency":
                float(dfr.sign_consistency.iloc[0]) if len(dfr) else np.nan,
            "witness_n_valid_cells":
                int(dfr.n_valid_cells.iloc[0]) if len(dfr) else -1,
            "mathematical_type_block": r.mathematical_type_block,
            "broad_scientific_family": r.broad_scientific_family,
            "scientific_dimension_class": r.scientific_dimension_class,
            "canonical_unit": r.canonical_unit,
            "origin_class": r.origin_class,
            "provenance_status": r.provenance_status,
            "uncalibrated_flag": r.uncalibrated_flag,
            "upstream_upsampled_flag": r.upstream_upsampled_flag,
            "aliasing_flag": r.aliasing_flag,
            "derivative_primary_eligible": r.derivative_primary_eligible,
            "product_ratio_operand_eligible": r.product_ratio_operand_eligible,
        })
    FULL = pd.DataFrame(full_rows)
    FULL.to_csv(S5H / "primitive_basis_full.csv", index=False)
    FULL[FULL.hard_status == "IN_P_HARD"].to_csv(
        S5H / "primitive_basis_hardened.csv", index=False)
    FULL[FULL.hard_status == "REDUNDANCY_DEFERRED"].to_csv(
        S5H / "primitive_basis_deferred.csv", index=False)

    # ---- family census -----------------------------------------------------
    cen = []
    for f in sorted(set(P.broad_scientific_family)):
        nb = int((P.broad_scientific_family == f).sum())
        na = int(((FULL.broad_scientific_family == f) &
                  (FULL.hard_status == "IN_P_HARD")).sum())
        cen.append({"family": f, "n_before": nb, "n_after": na,
                    "share_before": nb / 78,
                    "share_after": na / max(len(hard_ids), 1),
                    "n_deferred": nb - na})
    CEN = pd.DataFrame(cen)
    CEN.to_csv(S5H / "family_composition_audit.csv", index=False)

    # ---- effective-rank audit (AUDIT ONLY, never selection) ---------------
    er = []
    for gid, mem in members.items():
        k = [ai[s] for s in mem]
        sv_all = []
        for s in dev:
            Mv = vals[s]
            n = Mv.shape[1]
            for bn, c1 in BLOCKS:
                X = Mv[k][:, slice(0, int(np.floor(n * c1)))].T
                X = X[np.all(np.isfinite(X), axis=1)]
                if X.shape[0] < len(mem):
                    continue
                Xc = X - X.mean(0)
                sd = Xc.std(0)
                sd[sd == 0] = 1.0
                sv = np.linalg.svd(Xc / sd, compute_uv=False)
                ev = sv ** 2 / np.sum(sv ** 2)
                sv_all.append([int(np.searchsorted(np.cumsum(ev), q) + 1)
                               for q in (0.95, 0.99)])
        A = np.array(sv_all) if sv_all else np.zeros((1, 2))
        er.append({"semantic_group_id": gid, "n_members": len(mem),
                   "n_representatives_selected":
                       int((REPS.semantic_group_id == gid).sum()),
                   "median_rank_95pct": float(np.median(A[:, 0])),
                   "median_rank_99pct": float(np.median(A[:, 1])),
                   "n_cells": len(sv_all),
                   "role": "AUDIT_ONLY_NEVER_SELECTION"})
    ER = pd.DataFrame(er)
    ER.to_csv(S5H / "effective_rank_audit.csv", index=False)

    with (MAN / "DATA_ACCESS_LOG.csv").open("w", newline="",
                                            encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ACCESS[0].keys()))
        w.writeheader()
        w.writerows(ACCESS)
    shots = {a["shot_id"] for a in ACCESS}
    (MAN / "ACCESS_AUDIT.json").write_text(json.dumps({
        "development_shots_read": sorted(shots),
        "n_development_shots_read": len(shots),
        "predictor_signals_read_per_shot": len(audited),
        "signals_read": audited,
        "target_values_accessed": 0,
        "external_values_accessed": 0,
        "predictor_target_correlation_computed": False,
        "mutual_information_with_target_computed": False,
        "target_feature_importance_computed": False,
        "model_fitted": False, "baseline_fitted": False,
        "verdict": "FIREWALL_INTACT" if (len(shots) == 20
                                         and not (shots & ext))
                   else "FIREWALL_BREACH"}, indent=2), encoding="utf-8")

    summ = {
        "n_pairs_audited": int(len(PW)),
        "n_stably_near_redundant_pairs": int(PW.stably_near_redundant.sum()),
        "P_full": 78, "P_hard": len(hard_ids), "P_deferred": len(deferred_ids),
        "by_group": {gid: {
            "n_members": len(mem),
            "n_representatives": int((REPS.semantic_group_id == gid).sum()),
            "n_deferred": int((DEF.semantic_group_id == gid).sum())
                          if len(DEF) else 0,
            "n_redundant_pairs": int(PW[(PW.semantic_group_id == gid)
                                        & PW.stably_near_redundant].shape[0]),
        } for gid, mem in members.items()},
        "family_census": CEN.to_dict("records"),
        "effective_rank_audit": ER.to_dict("records"),
        "thresholds_used": TH,
        "thresholds_unchanged_after_value_access": True,
    }
    (MAN / "REDUNDANCY_SUMMARY.json").write_text(json.dumps(summ, indent=2),
                                                 encoding="utf-8")

    print(f"pairs audited {len(PW)} | stably near-redundant "
          f"{int(PW.stably_near_redundant.sum())}")
    for gid, v in summ["by_group"].items():
        print(f"  {gid:14s} members {v['n_members']:3d} -> representatives "
              f"{v['n_representatives']:3d}  (deferred {v['n_deferred']:3d}, "
              f"redundant pairs {v['n_redundant_pairs']})")
    print(f"P_full 78 | P_hard {len(hard_ids)} | P_deferred {len(deferred_ids)}")
    print("family census (before -> after):")
    for r in CEN.itertuples():
        print(f"  {r.family:22s} {r.n_before:3d} -> {r.n_after:3d}   "
              f"share {r.share_before:.3f} -> {r.share_after:.3f}")
    print("effective-rank audit (AUDIT ONLY):")
    for r in ER.itertuples():
        print(f"  {r.semantic_group_id:14s} n={r.n_members:3d} reps="
              f"{r.n_representatives_selected:3d}  median rank95="
              f"{r.median_rank_95pct:.1f} rank99={r.median_rank_99pct:.1f}")


if __name__ == "__main__":
    main()
