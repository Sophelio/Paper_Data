"""S7.7R stage B - the one-seed primary search.

This is the FIRST authorised target-dependent operation of the q_rec pipeline.
It opens DEVELOPMENT density and DEVELOPMENT predictor values only. The external
cohort of 42 discharges is never touched.

The V2 policy hash is verified BEFORE the first archive is opened. On mismatch
the stage aborts as SEARCH_POLICY_CONTAMINATED.

Numerical note on SEARCH_PROXY_OLS_V1. The proxy is affine OLS of the protected
target on calibration-standardised coordinates. It is solved in partitioned
(Frisch-Waugh) form: the intercept is absorbed by centring and the slope vector
solves the normal equations of the centred calibration design. That is
algebraically identical to numpy.linalg.lstsq on [1, Z] for a full-rank design,
and the equivalence is verified numerically against lstsq on a random sample of
supports across sizes; the maximum relative deviation is recorded. Rank
deficiency is detected explicitly from the eigenvalues of the centred Gram
matrix and scored +infinity, per the frozen policy - never as inadmissibility.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
V2 = HERE.parent
S77 = V2.parent
S7 = S77.parent
EX = S7.parent
S72 = S7 / "02_reconstruction_contract"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
MAN = V2 / "manifests"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

TARGET = "density"
BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
SUPPORT_MAX = 12
CAP = 96
MAX_SUPPORT_EVALUATIONS = 300000
EPS = np.finfo(np.float64).eps
ACTIVE = ["C0", "C1", "C2", "C3", "C5", "C6", "C7"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    t_start = datetime.now(timezone.utc)
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: run stage A first")
    polman = json.loads((MAN / "POLICY_FREEZE_V2.json").read_text())
    if sha(V2 / "SEARCH_POLICY_PREVALUE_V2.json") != polman["sha256"]:
        raise SystemExit("STOP: SEARCH_POLICY_CONTAMINATED")
    POL = json.loads((V2 / "SEARCH_POLICY_PREVALUE_V2.json").read_text())
    assert POL["SEEDS_PER_STRATUM"] == 1
    pf = json.loads((V2 / "SEARCH_BUDGET_PREFLIGHT_V2.json").read_text())
    if pf["verdict"] != "SEARCH_BUDGET_OK":
        raise SystemExit("STOP: budget")
    PROJ_MAX = pf["max_projected_support_evaluations"]

    # ---------------- metadata registries ----------------------------------
    AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
    FULL = pd.read_csv(S76R / "primary_atomic_coordinate_universe.csv")
    AT = AT.merge(FULL[["coordinate_id", "primitive_ancestors"]],
                  on="coordinate_id", how="left")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
        "signal_index").reset_index(drop=True)
    fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))
    P_ALL = list(HB.primitive_id)
    P_DOT = [s for s in P_ALL if bool(HB.derivative_primary_eligible[
        HB.primitive_id == s].iloc[0])]
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    assert (len(P_ALL), len(P_DOT)) == (70, 63)
    N = len(AT)
    assert N == 10778
    ORIG = list(AT.coordinate_id)
    row_of = {c: k for k, c in enumerate(ORIG)}
    anc_of = {c: sorted({fam[a] for a in str(s).split("|")})
              for c, s in zip(AT.coordinate_id, AT.primitive_ancestors)}
    strata_of = dict(zip(AT.coordinate_id, AT.search_stratum))
    cons_of = dict(zip(AT.coordinate_id, AT.constructor))

    DEP = pd.read_csv(S76R / "exact_dependency_groups.csv")
    BINDING = ([set(str(r.aggregate_coordinate).split("|")
                    + str(r.component_coordinates).split("|"))
                for r in DEP.itertuples()] if len(DEP) else [])

    # atom realisation plan, indexed by ORIG row
    OPC = {"C0": 0, "C1": 0, "C5": 1, "C2": 2, "C6": 2, "C3": 3, "C7": 3}
    kA = np.zeros(N, np.int8)
    iA = np.zeros(N, np.int32)
    kB = np.zeros(N, np.int8)
    iB = np.zeros(N, np.int32)
    op = np.zeros(N, np.int8)
    for r, (c, ops) in enumerate(zip(AT.constructor, AT.ordered_operands)):
        o = str(ops).split("|")
        op[r] = OPC[c]
        if c in ("C1", "C7"):                       # numerator is a rate
            kA[r], iA[r] = 1, di[o[0]]
        else:
            kA[r], iA[r] = 0, li[o[0]]
        if c in ("C2", "C3", "C7"):                 # second operand is a level
            kB[r], iB[r] = 0, li[o[1]]
        elif c == "C6":                             # second operand is a rate
            kB[r], iB[r] = 1, di[o[1]]

    # ---------------- FIRST TARGET ACCESS ----------------------------------
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = list(part["development"]["shot_ids"])
    ext = set(part["external"]["shot_ids"])
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str})
    TRd = TR[TR.cohort == "development"].set_index("discharge")

    first_access = datetime.now(timezone.utc).isoformat()
    ACCESS, LEV, DER, YT, SLC = [], {}, {}, {}, {}
    for s in dev:
        if s in ext:
            raise SystemExit("STOP: FIREWALL_BREACH")
        t0 = float(TRd.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TRd.loc[s, "delta_t_ms"])
        n = int(TRd.loc[s, "N_s"])
        grid = t0 + dtm * np.arange(n, dtype=np.float64)
        tsec = grid / 1000.0
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            L = np.empty((70, n))
            for k, sig in enumerate(P_ALL):
                tt, vv = PROV._load_signal(a, sig)
                L[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                    str(PROV.SIGNAL_UNIT[sig]), 1.0)
            tt, vv = PROV._load_signal(a, TARGET)
            y = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                str(PROV.SIGNAL_UNIT[TARGET]), 1.0)
        D = np.empty((63, n))
        for k, sig in enumerate(P_DOT):
            D[k] = np.gradient(L[li[sig]], tsec, edge_order=2)
        LEV[s], DER[s], YT[s] = L, D, y
        for bn, c1, c2 in BLOCKS:
            SLC[(s, bn)] = (slice(0, int(np.floor(n * c1))),
                            slice(int(np.floor(n * c1)), int(np.floor(n * c2))))
        ACCESS.append({"stage": "S7.7R-B", "shot_id": s, "cohort": "development",
                       "archive": PROV._shot_npz_path(DATA, s).name,
                       "predictor_signals_read": 70,
                       "target_signal_read": TARGET, "target_values_read": int(n),
                       "external_values_read": 0,
                       "reason": "SEARCH_PROXY_OLS_V1 navigation scoring",
                       "timestamp": datetime.now(timezone.utc).isoformat()})
    CELLS = [(s, bn) for s in dev for bn, _, _ in BLOCKS]
    NC = len(CELLS)
    YSTD = {c: float(np.std(YT[c[0]][SLC[c][0]], ddof=0)) for c in CELLS}
    assert all(v > 0 for v in YSTD.values())

    def realise(rows, s):
        """Materialise a chunk of atomic coordinates on discharge s.

        Levels and rates live in separate matrices with different row counts,
        so the operand gather is done by mask rather than by np.where, which
        would evaluate both branches and index out of range.
        """
        L, D = LEV[s], DER[s]
        n = L.shape[1]

        def gather(kind, idx):
            g = np.empty((idx.size, n))
            lv = kind == 0
            if lv.any():
                g[lv] = L[idx[lv]]
            if (~lv).any():
                g[~lv] = D[idx[~lv]]
            return g

        A = gather(kA[rows], iA[rows])
        o = op[rows]
        out = np.empty_like(A)
        with np.errstate(divide="ignore", invalid="ignore"):
            m0 = o == 0
            out[m0] = A[m0]
            m1 = o == 1
            if m1.any():
                out[m1] = 1.0 / A[m1]
            if (o >= 2).any():
                B = gather(kB[rows], iB[rows])
                m2, m3 = o == 2, o == 3
                out[m2] = A[m2] * B[m2]
                out[m3] = A[m3] / B[m3]
        return out

    # ---------------- 11. atomic navigation scoring ------------------------
    NR = np.full((N, NC), np.inf)
    for ci, cell in enumerate(CELLS):
        s, _ = cell
        cal, pro = SLC[cell]
        yc, yp = YT[s][cal], YT[s][pro]
        ym, sy = float(yc.mean()), YSTD[cell]
        ycc, npro = yc - ym, yp.size
        for a0 in range(0, N, 1500):
            rows = np.arange(a0, min(a0 + 1500, N))
            V = realise(rows, s)
            xc, xp = V[:, cal], V[:, pro]
            mu = xc.mean(axis=1, keepdims=True)
            sd = xc.std(axis=1, ddof=0, keepdims=True)
            bad = (~np.isfinite(sd[:, 0])) | (sd[:, 0] <= 0)
            zc = (xc - mu) / np.where(sd <= 0, 1.0, sd)
            zp = (xp - mu) / np.where(sd <= 0, 1.0, sd)
            zcm = zc.mean(axis=1, keepdims=True)
            zcc = zc - zcm
            den = (zcc * zcc).sum(axis=1)
            beta = np.where(den > 0, (zcc * ycc).sum(axis=1)
                            / np.where(den > 0, den, 1.0), 0.0)
            r = (yp - ym)[None, :] - beta[:, None] * (zp - zcm)
            nr = np.sqrt((r * r).sum(axis=1) / npro) / sy
            nr[bad | ~np.isfinite(nr)] = np.inf
            NR[rows, ci] = nr
    per_shot = NR.reshape(N, len(dev), 3).mean(axis=2)
    J = per_shot.mean(axis=1)
    rank_def = ~np.isfinite(J)

    AT = AT.assign(J_search=J, rank_status=np.where(
        rank_def, "SEARCH_PROXY_RANK_DEFICIENT", "FULL_RANK"))
    for k, s in enumerate(dev):
        AT[f"NRMSE_{s}"] = per_shot[:, k]
    AT = AT.sort_values(["search_stratum", "J_search", "coordinate_id"])
    AT["within_stratum_rank"] = AT.groupby("search_stratum").cumcount() + 1
    AT = AT.sort_values(["J_search", "coordinate_id"]).reset_index(drop=True)
    AT["global_rank_reference_only"] = np.arange(1, N + 1)
    AT.to_csv(V2 / "atomic_navigation_scores.csv", index=False)
    np.savez_compressed(V2 / "atomic_per_cell_nrmse.npz",
                        coordinate_id=np.array(ORIG, dtype=object),
                        cells=np.array([f"{s}:{b}" for s, b in CELLS]),
                        nrmse=NR.astype(np.float32))

    Jof = dict(zip(AT.coordinate_id, AT.J_search))
    wsr = dict(zip(AT.coordinate_id, AT.within_stratum_rank))
    ordered: dict[str, list[str]] = {}
    for cid in AT.coordinate_id:                       # already J-then-ID sorted
        ordered.setdefault(strata_of[cid], []).append(cid)
    ALL_STRATA = sorted(ordered)

    # ---------------- 13. constructor-balanced shortlist -------------------
    shortlist, short_rows = {}, []
    for c in ACTIVE:
        sts = sorted(st for st in ordered if st.startswith(c + ":"))
        cap = min(int((AT.constructor == c).sum()), CAP)
        picked, r = [], 0
        while len(picked) < cap:
            added = False
            for st in sts:
                if len(picked) >= cap:
                    break
                if r < len(ordered[st]):
                    picked.append(ordered[st][r])
                    added = True
            if not added:
                break
            r += 1
        shortlist[c] = picked
        for k, cid in enumerate(picked, 1):
            short_rows.append({"coordinate_id": cid, "constructor": c,
                               "search_stratum": strata_of[cid],
                               "within_stratum_rank": int(wsr[cid]),
                               "round_robin_order": k, "J_search": Jof[cid],
                               "status": "IN_EXPANSION_SHORTLIST"})
    pd.DataFrame(short_rows).to_csv(V2 / "constructor_shortlist.csv", index=False)
    SL_IDS = [r["coordinate_id"] for r in short_rows]
    sidx = {c: k for k, c in enumerate(SL_IDS)}
    st_short: dict[str, list[str]] = {}
    for cid in SL_IDS:
        st_short.setdefault(strata_of[cid], []).append(cid)
    for st in st_short:
        st_short[st].sort(key=lambda c: (Jof[c], c))
    SHORT_STRATA = sorted(st_short)

    # ---------------- 14. one seed per active stratum ----------------------
    seeds = [(st, ordered[st][0]) for st in ALL_STRATA]
    seed_rows = [{"seed_id": f"SEED_{i + 1:03d}", "lane": "MAIN",
                  "seed_stratum": st, "constructor": st.split(":")[0],
                  "family_signature": st.split(":", 1)[1], "coordinate_id": cid,
                  "J_search": Jof[cid], "within_stratum_rank": int(wsr[cid]),
                  "in_shortlist": cid in sidx,
                  "flag": ("SEED_PROXY_RANK_DEFICIENT"
                           if not np.isfinite(Jof[cid]) else "")}
                 for i, (st, cid) in enumerate(seeds)]
    assert all(r["in_shortlist"] for r in seed_rows)

    # ---------------- Gram machinery over the shortlist --------------------
    M = len(SL_IDS)
    rows_sl = np.array([row_of[c] for c in SL_IDS])
    GC, GY, ZP, SY, YPV, NPRO = [], [], [], [], [], []
    for cell in CELLS:
        s, _ = cell
        cal, pro = SLC[cell]
        V = realise(rows_sl, s)
        xc, xp = V[:, cal], V[:, pro]
        mu = xc.mean(axis=1, keepdims=True)
        sd = xc.std(axis=1, ddof=0, keepdims=True)
        sd = np.where(sd <= 0, 1.0, sd)
        zc, zp = (xc - mu) / sd, (xp - mu) / sd
        zcm = zc.mean(axis=1, keepdims=True)
        zcc = zc - zcm
        yc = YT[s][cal]
        ym = float(yc.mean())
        GC.append(zcc @ zcc.T)
        GY.append(zcc @ (yc - ym))
        ZP.append(np.ascontiguousarray(zp - zcm))
        SY.append(YSTD[cell])
        YPV.append(YT[s][pro] - ym)
        NPRO.append(int(YT[s][pro].size))

    def eval_supports(sups):
        B, m = len(sups), len(sups[0])
        idx = np.asarray(sups, dtype=np.int64)
        out = np.empty((B, NC))
        deficient = np.zeros(B, bool)
        I = np.eye(m)
        for ci in range(NC):
            G = GC[ci][idx[:, :, None], idx[:, None, :]]
            g = GY[ci][idx]
            ev = np.linalg.eigvalsh(G)
            lo, hi = ev[:, 0], ev[:, -1]
            bad = (hi <= 0) | (lo <= 0) | (
                np.sqrt(np.maximum(lo, 0.0) / np.where(hi > 0, hi, 1.0))
                <= max(NPRO[ci], m + 1) * EPS)
            deficient |= bad
            # b is given an explicit trailing axis: numpy 2 otherwise reads a
            # (B, m) right-hand side as a single (m, n) matrix
            beta = np.linalg.solve(np.where(bad[:, None, None], I, G),
                                   g[..., None])[..., 0]
            nr = np.empty(B)
            for a0 in range(0, B, 3000):
                sl = slice(a0, min(a0 + 3000, B))
                Zs = ZP[ci][idx[sl]]
                yh = np.matmul(beta[sl][:, None, :], Zs)[:, 0, :]
                r = YPV[ci][None, :] - yh
                nr[sl] = np.sqrt((r * r).sum(axis=1) / NPRO[ci]) / SY[ci]
            out[:, ci] = nr
        out[deficient, :] = np.inf
        out[~np.isfinite(out)] = np.inf
        return out, deficient

    # ---- numerical equivalence against numpy.linalg.lstsq ------------------
    rng = np.random.default_rng(0)
    chk, maxdev = [], 0.0
    for m in (2, 5, 9, 12):
        for _ in range(12):
            sup = tuple(sorted(rng.choice(M, size=m, replace=False).tolist()))
            got, _d = eval_supports([sup])
            ci = int(rng.integers(0, NC))
            s, bn = CELLS[ci]
            cal, pro = SLC[(s, bn)]
            V = realise(rows_sl[list(sup)], s)
            xc, xp = V[:, cal], V[:, pro]
            mu = xc.mean(axis=1, keepdims=True)
            sd = xc.std(axis=1, ddof=0, keepdims=True)
            zc, zp = (xc - mu) / sd, (xp - mu) / sd
            yc, yp = YT[s][cal], YT[s][pro]
            X = np.column_stack([np.ones(zc.shape[1]), zc.T])
            b, *_ = np.linalg.lstsq(X, yc, rcond=None)
            pred = np.column_stack([np.ones(zp.shape[1]), zp.T]) @ b
            ref = float(np.sqrt(np.mean((yp - pred) ** 2)) / np.std(yc, ddof=0))
            reldev = abs(got[0, ci] - ref) / max(ref, 1e-12)
            maxdev = max(maxdev, reldev)
            chk.append({"support_size": m, "cell": f"{s}:{bn}",
                        "gram_partitioned": float(got[0, ci]), "lstsq": ref,
                        "relative_deviation": reldev})
    pd.DataFrame(chk).to_csv(V2 / "proxy_equivalence_check.csv", index=False)

    # ---------------- 15/16. lockstep greedy -------------------------------
    CACHE: dict[frozenset, tuple[float, np.ndarray, bool]] = {}
    ROWS, PATHS, PROV_ROWS = [], [], []
    cnt = {"proposals": 0, "unique": 0, "cache_hits": 0, "phi_rejected": 0,
           "dup_within_step": 0}
    order = [0]

    def phi_ok(cids):
        if not (1 <= len(cids) <= SUPPORT_MAX) or len(set(cids)) != len(cids):
            return False
        cs = set(cids)
        return not any(g <= cs for g in BINDING)

    def run_lane(lane, seedlist, pool, tag):
        state = []
        for i, (st, cid) in enumerate(seedlist):
            pid = f"{tag}_P{i + 1:03d}"
            state.append({"pid": pid, "st": st, "seed": cid,
                          "sup": (sidx[cid],), "alive": True})
            PATHS.append({"path_id": pid, "lane": lane, "step": 1,
                          "support_size": 1, "seed_id": cid, "seed_stratum": st,
                          "coordinate_ids": cid, "added_coordinate": cid,
                          "proposed_from_stratum": st, "J_search": Jof[cid],
                          "rank_status": "SEARCH_PROXY_RANK_DEFICIENT"
                          if not np.isfinite(Jof[cid]) else "FULL_RANK",
                          "retained_on_path": True})
        for step in range(2, SUPPORT_MAX + 1):
            props, owner = {}, []
            for p in state:
                if not p["alive"]:
                    continue
                cur = set(p["sup"])
                for st in pool:
                    pick = next((c for c in st_short[st] if sidx[c] not in cur),
                                None)
                    if pick is None:
                        continue
                    cnt["proposals"] += 1
                    new = tuple(sorted(cur | {sidx[pick]}))
                    if not phi_ok([SL_IDS[k] for k in new]):
                        cnt["phi_rejected"] += 1
                        continue
                    key = frozenset(new)
                    if key in props:
                        cnt["dup_within_step"] += 1
                    else:
                        props[key] = new
                    owner.append((p, new, st, pick))
            todo = [v for k, v in props.items() if k not in CACHE]
            cnt["cache_hits"] += len(props) - len(todo)
            for a0 in range(0, len(todo), 4000):
                batch = todo[a0:a0 + 4000]
                nr, dfc = eval_supports(batch)
                js = nr.reshape(len(batch), len(dev), 3).mean(axis=2).mean(axis=1)
                for bi, sup in enumerate(batch):
                    CACHE[frozenset(sup)] = (float(js[bi]), nr[bi], bool(dfc[bi]))
                    cnt["unique"] += 1
                    order[0] += 1
                    # canonical support ID: coordinate IDs sorted
                    # lexicographically, the frozen tie-break order
                    cids = sorted(SL_IDS[k] for k in sup)
                    ROWS.append({
                        "support_id": "|".join(cids), "support_size": len(sup),
                        "coordinate_ids": "|".join(cids),
                        "first_lane": lane, "first_expansion_step": step,
                        "constructor_composition": "+".join(
                            sorted(cons_of[c] for c in cids)),
                        "ancestor_family_composition": "+".join(
                            sorted({f for c in cids for f in anc_of[c]})),
                        "J_search": float(js[bi]),
                        "rank_status": ("SEARCH_PROXY_RANK_DEFICIENT"
                                        if dfc[bi] else "FULL_RANK"),
                        "first_evaluation_order": order[0]})
            best = {}
            for p, new, st, pick in owner:
                j = CACHE[frozenset(new)][0]
                sid = "|".join(sorted(SL_IDS[k] for k in new))
                PROV_ROWS.append({"path_id": p["pid"], "lane": lane, "step": step,
                                  "proposed_from_stratum": st,
                                  "proposed_coordinate": pick,
                                  "support_id": sid, "J_search": j})
                b = best.get(p["pid"])
                if b is None or (j, sid) < (b[0], b[3]):
                    best[p["pid"]] = (j, new, (st, pick), sid)
            for p in state:
                if not p["alive"]:
                    continue
                b = best.get(p["pid"])
                if b is None:
                    p["alive"] = False
                    continue
                j, new, (st, pick), sid = b
                p["sup"] = new
                PATHS.append({"path_id": p["pid"], "lane": lane, "step": step,
                              "support_size": len(new), "seed_id": p["seed"],
                              "seed_stratum": p["st"],
                              "coordinate_ids": "|".join(
                                  sorted(SL_IDS[k] for k in new)),
                              "added_coordinate": pick,
                              "proposed_from_stratum": st, "J_search": j,
                              "rank_status": ("SEARCH_PROXY_RANK_DEFICIENT"
                                              if CACHE[frozenset(new)][2]
                                              else "FULL_RANK"),
                              "retained_on_path": True})

    run_lane("MAIN", seeds, SHORT_STRATA, "M")
    c0_str = [st for st in ALL_STRATA if st.startswith("C0:")]
    raw_seeds = [(st, ordered[st][0]) for st in c0_str]
    for i, (st, cid) in enumerate(raw_seeds):
        seed_rows.append({"seed_id": f"RAWSEED_{i + 1:02d}", "lane": "RAW_ONLY",
                          "seed_stratum": st, "constructor": "C0",
                          "family_signature": st.split(":", 1)[1],
                          "coordinate_id": cid, "J_search": Jof[cid],
                          "within_stratum_rank": int(wsr[cid]),
                          "in_shortlist": True,
                          "flag": ("SEED_PROXY_RANK_DEFICIENT"
                                   if not np.isfinite(Jof[cid]) else "")})
    run_lane("RAW_ONLY", raw_seeds, c0_str, "R")

    pd.DataFrame(seed_rows).to_csv(V2 / "search_seed_registry.csv", index=False)
    PD = pd.DataFrame(PATHS)
    PD[PD.lane == "MAIN"].to_csv(V2 / "search_retained_paths.csv", index=False)
    PD[PD.lane == "RAW_ONLY"].to_csv(V2 / "raw_only_search_paths.csv", index=False)
    pd.DataFrame(ROWS).to_csv(V2 / "search_candidate_evaluations.csv", index=False)
    pd.DataFrame(PROV_ROWS).to_csv(V2 / "search_proposal_provenance.csv",
                                   index=False)

    keys = list(CACHE)
    np.savez_compressed(
        V2 / "explored_per_cell_nrmse.npz",
        support_id=np.array(["|".join(sorted(SL_IDS[k] for k in s))
                             for s in keys], dtype=object),
        cells=np.array([f"{s}:{b}" for s, b in CELLS]),
        nrmse=np.asarray([CACHE[k][1] for k in keys], dtype=np.float32))

    total = cnt["proposals"] + N
    runtime = {
        "record_id": "SEARCH_BUDGET_RUNTIME_AUDIT",
        "projected_maximum": PROJ_MAX,
        "atomic_scoring_evaluations": N,
        "multivariate_proposals": cnt["proposals"],
        "total_proposal_evaluations": total,
        "unique_multivariate_supports_evaluated": cnt["unique"],
        "cache_hits_reused_evaluations": cnt["cache_hits"],
        "duplicate_proposals_within_step": cnt["dup_within_step"],
        "phi_set_rejected_proposals": cnt["phi_rejected"],
        "MAX_SUPPORT_EVALUATIONS": MAX_SUPPORT_EVALUATIONS,
        "within_frozen_allowance": total <= MAX_SUPPORT_EVALUATIONS,
        "within_metadata_projection": total <= PROJ_MAX,
        "truncated_after_reaching_limit": False,
        "verdict": ("SEARCH_BUDGET_RUNTIME_OK" if total <= MAX_SUPPORT_EVALUATIONS
                    else "SEARCH_BUDGET_RUNTIME_BREACH")}
    (MAN / "SEARCH_BUDGET_RUNTIME_AUDIT.json").write_text(
        json.dumps(runtime, indent=2), encoding="utf-8")
    if runtime["verdict"] != "SEARCH_BUDGET_RUNTIME_OK":
        raise SystemExit("STOP: SEARCH_BUDGET_RUNTIME_BREACH")

    with (MAN / "DATA_ACCESS_LOG.csv").open("w", newline="",
                                            encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ACCESS[0].keys()))
        w.writeheader()
        w.writerows(ACCESS)
    (MAN / "ACCESS_AUDIT.json").write_text(json.dumps({
        "policy_hash_verified_before_first_archive_open": True,
        "search_policy_v2_sha256": polman["sha256"],
        "policy_frozen_utc": polman["frozen_utc"],
        "stage_start_utc": t_start.isoformat(),
        "first_density_access_utc": first_access,
        "policy_frozen_before_first_density_access":
            polman["frozen_utc"] < first_access,
        "development_shots_read": sorted(dev),
        "n_development_shots_read": len(dev),
        "predictor_signals_read_per_shot": 70, "target_signal_read": TARGET,
        "target_canonical_unit": "m^-3",
        "external_shots_read": [], "external_signal_values": 0,
        "external_target_values": 0, "baselines_run": 0,
        "models_fitted_beyond_search_proxy": 0, "S_pers_computed": 0,
        "verdict": "FIREWALL_INTACT" if not (set(dev) & ext) else "FIREWALL_BREACH",
    }, indent=2), encoding="utf-8")
    (MAN / "PROXY_EQUIVALENCE.json").write_text(json.dumps({
        "check_id": "SEARCH_PROXY_OLS_V1_EQUIVALENCE",
        "method": "partitioned (Frisch-Waugh) normal equations on the centred "
                  "calibration design; algebraically identical to "
                  "numpy.linalg.lstsq on [1, Z] for a full-rank design",
        "reference": "numpy.linalg.lstsq(..., rcond=None) on the explicit [1, Z] "
                     "design, recomputed independently",
        "n_samples": len(chk), "support_sizes_tested": [2, 5, 9, 12],
        "max_relative_deviation": maxdev, "tolerance": 1e-9,
        "passes": bool(maxdev < 1e-9),
        "rank_deficiency_rule": "eigenvalues of the centred Gram matrix; "
                                "sqrt(min/max) <= max(n_prot, m+1)*eps -> "
                                "J_search = +infinity and "
                                "SEARCH_PROXY_RANK_DEFICIENT; NEVER "
                                "inadmissibility"}, indent=2), encoding="utf-8")

    print(f"first density access : {first_access}")
    print(f"policy frozen before : "
          f"{polman['frozen_utc'] < first_access}")
    print(f"atoms scored         : {N}  rank-deficient {int(rank_def.sum())}")
    print(f"strata {len(ALL_STRATA)}  shortlist "
          f"{ {c: len(shortlist[c]) for c in ACTIVE} }  total {M}")
    print(f"seeds main {len(seeds)}  raw-only {len(raw_seeds)}")
    print(f"proposals {cnt['proposals']} + atomic {N} = {total} "
          f"(projected max {PROJ_MAX}, allowance {MAX_SUPPORT_EVALUATIONS})")
    print(f"unique multivariate {cnt['unique']}  cache hits {cnt['cache_hits']}  "
          f"dup-in-step {cnt['dup_within_step']}  phi rejected "
          f"{cnt['phi_rejected']}")
    print(f"proxy equivalence max rel dev {maxdev:.3e} (pass {maxdev < 1e-9})")
    print(f"budget verdict {runtime['verdict']}")


if __name__ == "__main__":
    main()
