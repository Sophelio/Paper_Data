"""S7.E2.1 step B - execute all six outer folds under one frozen policy.

Non-interactive: the six folds run identically. No fold is inspected to decide
how to run another.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from e2_1_engine import Engine, Vault, BLOCKS, FLOOR, SUPPORT_MAX, CAP, EPS, \
    BOOT_SEED, NREP  # noqa: E402

BUDGET_PER_FOLD = 300000


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def se_w(P, Pref, w):
    n = w.sum()
    d1 = P @ w - float(Pref @ w)
    d2 = (P * P) @ w - 2.0 * (P @ (Pref * w)) + float((Pref * Pref) @ w)
    mean = d1 / n
    var = np.maximum((d2 - n * mean * mean) / (n - 1), 0.0)
    return np.sqrt(var) / np.sqrt(n)


def ranks_1_to_4(NR, ids, size, w, blocks, kappa_fn, active_fn):
    """Frozen U_rec Ranks 1-4. NR: (n, nshots, 3)."""
    n = w.sum()
    sub = NR[:, :, blocks]
    P = sub.mean(axis=2)
    fit = (P @ w) / n
    m = fit.min(); c = np.flatnonzero(fit == m)
    best = int(c[np.argmin(ids[c])])
    thr = np.maximum(se_w(P, P[best], w), FLOOR)
    e1 = np.flatnonzero(np.abs(fit - fit[best]) <= thr)

    s2 = sub[e1]
    bmean = np.tensordot(s2, w, axes=([1], [0])) / n
    bstar = np.argmax(bmean, axis=1)
    bw = bmean[np.arange(len(e1)), bstar]
    own = s2[np.arange(len(e1)), :, bstar]
    m = bw.min(); c = np.flatnonzero(bw == m)
    ref = int(c[np.argmin(ids[e1][c])])
    keep = np.abs(bw - bw[ref]) <= np.maximum(se_w(own, own[ref], w), FLOOR)
    rep = np.repeat(s2.mean(axis=2), w.astype(np.int64), axis=1)
    p90 = np.where(keep, np.percentile(rep, 90, axis=1, method="linear"), np.inf)
    e2 = e1[p90 == p90.min()]

    s = size[e2]; e3 = e2[s == s.min()]
    if len(e3) > 1:
        a = np.array([active_fn(i) for i in e3])
        e3 = e3[a == a.min()]
    e4 = e3
    if len(e3) > 1:
        S = np.array([kappa_fn(i, w, blocks) for i in e3])
        km = np.ones(len(e3), bool)
        for col in range(3):
            v = np.where(km, S[:, col], np.inf)
            km &= (v == v.min())
        e4 = e3[km]
    winner = int(e4[np.argmin(ids[e4])])
    return e1, e2, e3, e4, winner, fit, bw, bstar, p90


def main() -> int:
    pre = json.loads((OUT / "manifests" / "E2_1_PRESEARCH.json").read_text())
    if pre["verdict"] != "PRESEARCH_VERIFIED":
        raise SystemExit("STOP: pre-search verification failed")
    basis = pd.read_csv(OUT / "manifests" / "C_E2_FULL_DOMAIN.csv")
    bset = list(basis.coordinate_id)
    zb = np.load(OUT / "manifests" / "_e2_1_basis.npz", allow_pickle=True)
    supported = zb["supported"]; coord_all = [str(x) for x in zb["coordinate_id"]]
    shots_order = [str(x) for x in zb["shots"]]
    cidx = {c: i for i, c in enumerate(coord_all)}
    fa = pd.read_csv(E20 / "outer_fold_assignment.csv", dtype={"discharge": str})
    fold_of = dict(zip(fa.discharge, fa.outer_fold))

    vault = Vault()
    eng = Engine(vault)
    ACTIVE = sorted(set(basis.constructor))
    t_all = time.time()

    fold_records, block_rows, disch_rows, vrange_rows, budget_rows = [], [], [], [], []
    support_freezes = {}

    for k in range(6):
        t0 = time.time()
        test = sorted(fa[fa.outer_fold == k].discharge)
        train = sorted(fa[fa.outer_fold != k].discharge)
        ident = {"fold": k, "n_train": len(train), "n_test": len(test),
                 "train": train, "test": test,
                 "identity_sha256": h("|".join(train) + "//" + "|".join(test))}
        (OUT / "folds" / ("fold_%d_identities.json" % k)).write_text(
            json.dumps(ident, indent=2), encoding="utf-8")

        # ---- STEP 2: open D_train targets -----------------------------
        vault.allow_calibration(train)
        vault.allow_protected(train)

        CELLS = [(s, bn) for s in train for bn, _, _ in BLOCKS]
        NC = len(CELLS)

        # ---- atomic navigation scores over the basis -------------------
        rows_b = np.array([eng.row_of[c] for c in bset])
        NRa = np.full((len(bset), NC), np.inf)
        YSTD = {}
        for ci, (s, bn) in enumerate(CELLS):
            cal, pro = eng.SLC[(s, bn)]
            yc, yp = eng.ycal(s, bn), eng.ypro(s, bn)
            ym, sy = float(yc.mean()), float(np.std(yc, ddof=0))
            YSTD[(s, bn)] = sy
            ycc, npro = yc - ym, yp.size
            for a0 in range(0, len(bset), 1500):
                rr = np.arange(a0, min(a0 + 1500, len(bset)))
                V = eng.realise(rows_b[rr], s)
                xc, xp = V[:, cal], V[:, pro]
                mu = xc.mean(axis=1, keepdims=True)
                sd = xc.std(axis=1, ddof=0, keepdims=True)
                bad = (~np.isfinite(sd[:, 0])) | (sd[:, 0] <= 0)
                zc = (xc - mu) / np.where(sd <= 0, 1.0, sd)
                zp = (xp - mu) / np.where(sd <= 0, 1.0, sd)
                zcm = zc.mean(axis=1, keepdims=True); zcc = zc - zcm
                den = (zcc * zcc).sum(axis=1)
                beta = np.where(den > 0, (zcc * ycc).sum(axis=1)
                                / np.where(den > 0, den, 1.0), 0.0)
                r = (yp - ym)[None, :] - beta[:, None] * (zp - zcm)
                nr = np.sqrt((r * r).sum(axis=1) / npro) / sy
                nr[bad | ~np.isfinite(nr)] = np.inf
                NRa[rr, ci] = nr
        Jat = NRa.reshape(len(bset), len(train), 3).mean(axis=2).mean(axis=1)
        Jof = dict(zip(bset, Jat))

        # ---- strata, shortlist, seeds ---------------------------------
        order_df = pd.DataFrame({"cid": bset, "st": [eng.strata_of[c] for c in bset],
                                 "J": Jat}).sort_values(["J", "cid"])
        ordered = {}
        for r in order_df.itertuples():
            ordered.setdefault(r.st, []).append(r.cid)
        ALL_STRATA = sorted(ordered)
        wsr = {}
        for st, lst in ordered.items():
            for i, c in enumerate(lst, 1):
                wsr[c] = i
        short_rows = []
        for c in ACTIVE:
            sts = sorted(st for st in ordered if st.startswith(c + ":"))
            cap = min(int((basis.constructor == c).sum()), CAP)
            picked, rr = [], 0
            while len(picked) < cap:
                added = False
                for st in sts:
                    if len(picked) >= cap:
                        break
                    if rr < len(ordered[st]):
                        picked.append(ordered[st][rr]); added = True
                if not added:
                    break
                rr += 1
            for i, cid in enumerate(picked, 1):
                short_rows.append({"coordinate_id": cid, "constructor": c,
                                   "search_stratum": eng.strata_of[cid],
                                   "round_robin_order": i, "J_search": Jof[cid]})
        SL_IDS = [r["coordinate_id"] for r in short_rows]
        sidx = {c: i for i, c in enumerate(SL_IDS)}
        st_short = {}
        for cid in SL_IDS:
            st_short.setdefault(eng.strata_of[cid], []).append(cid)
        for st in st_short:
            st_short[st].sort(key=lambda c: (Jof[c], c))
        SHORT_STRATA = sorted(st_short)
        seeds = [(st, ordered[st][0]) for st in ALL_STRATA]

        # ---- Gram machinery over the shortlist -------------------------
        M = len(SL_IDS)
        rows_sl = np.array([eng.row_of[c] for c in SL_IDS])
        GC, GY, ZP, SY, YPV, NPRO = [], [], [], [], [], []
        for (s, bn) in CELLS:
            cal, pro = eng.SLC[(s, bn)]
            V = eng.realise(rows_sl, s)
            xc, xp = V[:, cal], V[:, pro]
            mu = xc.mean(axis=1, keepdims=True)
            sd = xc.std(axis=1, ddof=0, keepdims=True)
            sd = np.where(sd <= 0, 1.0, sd)
            zc, zp = (xc - mu) / sd, (xp - mu) / sd
            zcm = zc.mean(axis=1, keepdims=True); zcc = zc - zcm
            yc = eng.ycal(s, bn); ym = float(yc.mean())
            GC.append(zcc @ zcc.T); GY.append(zcc @ (yc - ym))
            ZP.append(np.ascontiguousarray(zp - zcm)); SY.append(YSTD[(s, bn)])
            YPV.append(eng.ypro(s, bn) - ym); NPRO.append(int(eng.ypro(s, bn).size))

        def eval_supports(sups):
            B, m = len(sups), len(sups[0])
            idx = np.asarray(sups, dtype=np.int64)
            out = np.empty((B, NC)); deficient = np.zeros(B, bool)
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
                beta = np.linalg.solve(np.where(bad[:, None, None], I, G),
                                       g[..., None])[..., 0]
                nr = np.empty(B)
                for a0 in range(0, B, 3000):
                    sl = slice(a0, min(a0 + 3000, B))
                    yh = np.matmul(beta[sl][:, None, :], ZP[ci][idx[sl]])[:, 0, :]
                    r = YPV[ci][None, :] - yh
                    nr[sl] = np.sqrt((r * r).sum(axis=1) / NPRO[ci]) / SY[ci]
                out[:, ci] = nr
            out[deficient, :] = np.inf
            out[~np.isfinite(out)] = np.inf
            return out, deficient

        # ---- lockstep greedy expansion ---------------------------------
        CACHE, ROWS = {}, []
        cnt = {"proposals": 0, "unique": 0}

        def phi_ok(cids):
            if not (1 <= len(cids) <= SUPPORT_MAX) or len(set(cids)) != len(cids):
                return False
            cs = set(cids)
            return not any(g <= cs for g in eng.BINDING)

        def run_lane(seedlist, pool, tag):
            state = [{"pid": "%s%03d" % (tag, i), "sup": (sidx[cid],), "alive": True}
                     for i, (st, cid) in enumerate(seedlist)]
            for i, (st, cid) in enumerate(seedlist):
                key = frozenset((sidx[cid],))
                if key not in CACHE:
                    nr, dfc = eval_supports([(sidx[cid],)])
                    CACHE[key] = (float(nr.reshape(1, len(train), 3).mean(axis=2).mean(axis=1)[0]),
                                  nr[0], bool(dfc[0]))
                    cnt["unique"] += 1
                    ROWS.append({"support_id": cid, "support_size": 1,
                                 "idx": (sidx[cid],), "J_search": CACHE[key][0]})
            for step in range(2, SUPPORT_MAX + 1):
                props, owner = {}, []
                for p in state:
                    if not p["alive"]:
                        continue
                    cur = set(p["sup"])
                    for st in pool:
                        pick = next((c for c in st_short[st] if sidx[c] not in cur), None)
                        if pick is None:
                            continue
                        cnt["proposals"] += 1
                        new = tuple(sorted(cur | {sidx[pick]}))
                        if not phi_ok([SL_IDS[q] for q in new]):
                            continue
                        props.setdefault(frozenset(new), new)
                        owner.append((p, new))
                todo = [v for kk, v in props.items() if kk not in CACHE]
                for a0 in range(0, len(todo), 4000):
                    batch = todo[a0:a0 + 4000]
                    nr, dfc = eval_supports(batch)
                    js = nr.reshape(len(batch), len(train), 3).mean(axis=2).mean(axis=1)
                    for bi, sup in enumerate(batch):
                        CACHE[frozenset(sup)] = (float(js[bi]), nr[bi], bool(dfc[bi]))
                        cnt["unique"] += 1
                        ROWS.append({"support_id": "|".join(sorted(SL_IDS[q] for q in sup)),
                                     "support_size": len(sup), "idx": tuple(sup),
                                     "J_search": float(js[bi])})
                best = {}
                for p, new in owner:
                    j = CACHE[frozenset(new)][0]
                    sid = "|".join(sorted(SL_IDS[q] for q in new))
                    b = best.get(p["pid"])
                    if b is None or (j, sid) < (b[0], b[2]):
                        best[p["pid"]] = (j, new, sid)
                for p in state:
                    if not p["alive"]:
                        continue
                    b = best.get(p["pid"])
                    if b is None:
                        p["alive"] = False; continue
                    p["sup"] = b[1]

        run_lane(seeds, SHORT_STRATA, "M")
        c0_str = [st for st in ALL_STRATA if st.startswith("C0:")]
        run_lane([(st, ordered[st][0]) for st in c0_str], c0_str, "R")

        if cnt["proposals"] > BUDGET_PER_FOLD:
            raise SystemExit("STOP: fold %d exceeded the frozen budget" % k)
        budget_rows.append({"fold": k, "proposals": cnt["proposals"],
                            "unique_supports": cnt["unique"],
                            "budget": BUDGET_PER_FOLD,
                            "within_budget": cnt["proposals"] <= BUDGET_PER_FOLD,
                            "n_strata": len(ALL_STRATA), "shortlist": M,
                            "search_seconds": round(time.time() - t0, 1)})

        # ---- assemble the fold frontier --------------------------------
        fr = pd.DataFrame(ROWS).drop_duplicates("support_id").reset_index(drop=True)
        ids = fr.support_id.values
        size = fr.support_size.values
        idxs = list(fr.idx.values)
        NR = np.stack([CACHE[frozenset(t_)][1] for t_ in idxs]).reshape(
            len(ids), len(train), 3)
        ATOMS = [sorted(SL_IDS[q] for q in t_) for t_ in idxs]

        # ---- frozen U_rec ------------------------------------------------
        kcache, acache = {}, {}

        def atoms_of(i):
            return ATOMS[i]

        def kappa_fn(i, w, blocks):
            if i not in kcache:
                Lk = np.empty((len(train), 3))
                for a, s in enumerate(train):
                    for b, (bn, _, _) in enumerate(BLOCKS):
                        _, _, _, kap = eng.fit_cell(atoms_of(i), s, bn)
                        Lk[a, b] = np.log10(kap)
                kcache[i] = Lk
            L = np.repeat(kcache[i], w.astype(np.int64), axis=0)[:, blocks].reshape(-1)
            return (float(np.median(L)), float(np.percentile(L, 90, method="linear")),
                    float(L.max()))

        def active_fn(i):
            if i not in acache:
                act = np.zeros(len(atoms_of(i)), bool)
                for s in train:
                    for bn, _, _ in BLOCKS:
                        _, _, beta, _ = eng.fit_cell(atoms_of(i), s, bn)
                        act |= (beta[1:] != 0.0)
                acache[i] = int(act.sum())
            return acache[i]

        w1 = np.ones(len(train))
        e1, e2, e3, e4, win, fit, bw, bstar, p90 = ranks_1_to_4(
            NR, ids, size, w1, [0, 1, 2], kappa_fn, active_fn)

        rng = np.random.default_rng(BOOT_SEED)
        draws = rng.integers(0, len(train), (NREP, len(train)))
        winners = np.empty(NREP, dtype=np.int64)
        for r in range(NREP):
            w = np.bincount(draws[r], minlength=len(train)).astype(float)
            winners[r] = ranks_1_to_4(NR, ids, size, w, [0, 1, 2], kappa_fn, active_fn)[4]
        folds_om = {}
        for bi, drop in enumerate("ABC"):
            keep = [q for q in range(3) if q != bi]
            folds_om["omit_" + drop] = int(ranks_1_to_4(
                NR, ids, size, w1, keep, kappa_fn, active_fn)[4])
        bfreq = {int(i): float((winners == i).sum()) / NREP for i in e4}
        ffreq = {int(i): float(sum(1 for v in folds_om.values() if v == i)) / 3.0 for i in e4}
        bmax = max(bfreq[i] for i in e4)
        e5 = [i for i in e4 if bfreq[i] == bmax]
        fmax = max(ffreq[i] for i in e5)
        e5 = [i for i in e5 if ffreq[i] == fmax]
        star = int(sorted(e5, key=lambda i: str(ids[i]))[0])
        atoms = atoms_of(star)

        # ---- STEP 7: HASH THE SUPPORT ---------------------------------
        sup_id = "|".join(atoms)
        sup_hash = h(sup_id)
        stamp = datetime.now(timezone.utc).isoformat()
        support_freezes["fold_%d" % k] = {
            "support_id": sup_id, "support_size": len(atoms), "sha256": sup_hash,
            "hashed_utc": stamp,
            "constructors": sorted({eng.cons_of[a] for a in atoms}),
            "primitives": sorted({p for a in atoms for p in eng.prim_of[a]}),
            "families": sorted({f for a in atoms for f in eng.anc_of[a]}),
        }
        vault.log.append({"utc": stamp, "action": "SUPPORT_HASHED", "fold": k,
                          "sha256": sup_hash})

        # ---- STEP 9: V-RANGE integrity check --------------------------
        rr = [cidx[a] for a in atoms]
        tcells = [i for i, s in enumerate(np.repeat(np.array(shots_order), 3))
                  if s in set(test)]
        vr = supported[np.ix_(rr, tcells)]
        vrange_pass = bool(vr.all())
        vrange_rows.append({"fold": k, "support_id": sup_id,
                            "n_heldout_cells": len(tcells),
                            "n_coordinate_cell_checks": int(vr.size),
                            "n_failures": int((~vr).sum()),
                            "V_RANGE_PASS": vrange_pass,
                            "pass_by_construction_expected": True})
        if not vrange_pass:
            raise SystemExit("STOP: PROTOCOL_OR_IMPLEMENTATION_INCONSISTENCY "
                             "- V-RANGE failed on fold %d" % k)

        # ---- STEPS 10-14: held-out evaluation -------------------------
        vault.allow_calibration(test)
        vault.log.append({"utc": datetime.now(timezone.utc).isoformat(),
                          "action": "HELDOUT_CALIBRATION_OPENED", "fold": k})
        vault.allow_protected(test)
        vault.log.append({"utc": datetime.now(timezone.utc).isoformat(),
                          "action": "HELDOUT_PROTECTED_OPENED_LAST", "fold": k})
        for s in test:
            per = {"REL": [], "B0": [], "B1": [], "B1A": [], "B2": [], "B3": [], "H0": []}
            for bn, _, _ in BLOCKS:
                sc = eng.score_cell(atoms, s, bn)
                bl = eng.baselines(s, bn)
                row = {"fold": k, "shot_id": s, "era": eng.era[s], "block": bn,
                       "REL_nrmse": sc["nrmse"], "REL_rmse": sc["rmse"],
                       "scale": sc["scale"], "log10_kappa": float(np.log10(sc["kappa"]))}
                per["REL"].append(sc["nrmse"])
                for m2 in ("B0", "B1", "B1A", "B2", "B3", "H0"):
                    row["%s_nrmse" % m2] = bl[m2]["nrmse"]
                    per[m2].append(bl[m2]["nrmse"])
                block_rows.append(row)
            d = {"fold": k, "shot_id": s, "era": eng.era[s], "support_id": sup_id}
            for m2 in per:
                d["%s_nrmse" % m2] = float(np.mean(per[m2]))
            disch_rows.append(d)

        fold_records.append({
            "fold": k, "n_train": len(train), "n_test": len(test),
            "frontier_size": int(len(ids)), "E1": int(len(e1)), "E2": int(len(e2)),
            "E3": int(len(e3)), "E4": int(len(e4)), "E5": int(len(e5)),
            "support_id": sup_id, "support_size": len(atoms), "support_sha256": sup_hash,
            "dev_FIT": float(fit[star]),
            "dev_FIT_best": float(fit[e1].min()),
            "dev_BLOCK_WORST": float(bw[np.flatnonzero(e1 == star)[0]]),
            "dev_b_star": "ABC"[int(bstar[np.flatnonzero(e1 == star)[0]])],
            "dev_SHOT_P90": float(p90[np.flatnonzero(e1 == star)[0]]),
            "dev_ACTIVE_TERMS": active_fn(star),
            "dev_COND_MEDIAN": kappa_fn(star, w1, [0, 1, 2])[0],
            "BOOT_SELECTION_FREQ": bfreq[star], "FOLD_SELECTION_FREQ": ffreq[star],
            "n_unique_bootstrap_winners": int(len(set(winners.tolist()))),
            "constructors": "+".join(sorted(eng.cons_of[a] for a in atoms)),
            "families": "+".join(sorted({f for a in atoms for f in eng.anc_of[a]})),
            "search_seconds": round(time.time() - t0, 1),
        })
        (OUT / "folds" / ("fold_%d_result.json" % k)).write_text(
            json.dumps({**fold_records[-1], "train": train, "test": test,
                        "coordinates": atoms}, indent=2), encoding="utf-8")
        print("fold %d | frontier %6d | E1 %5d E2 %3d | %s | size %d | boot %.3f | %.0fs"
              % (k, len(ids), len(e1), len(e2), sup_hash[:12], len(atoms),
                 bfreq[star], time.time() - t0))
        del GC, GY, ZP, CACHE

    pd.DataFrame(fold_records).to_csv(OUT / "fold_selected_supports.csv", index=False)
    pd.DataFrame(block_rows).to_csv(OUT / "heldout_block_results.csv", index=False)
    pd.DataFrame(disch_rows).to_csv(OUT / "heldout_discharge_results.csv", index=False)
    pd.DataFrame(vrange_rows).to_csv(OUT / "manifests" / "vrange_integrity.csv", index=False)
    pd.DataFrame(budget_rows).to_csv(OUT / "manifests" / "search_budget_audit.csv", index=False)
    (OUT / "E2_1_SUPPORT_FREEZES.json").write_text(json.dumps(support_freezes, indent=2),
                                                   encoding="utf-8")
    (OUT / "E2_1_ACCESS_AUDIT.json").write_text(json.dumps({
        "record_id": "E2_1_ACCESS_AUDIT_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "ledger": vault.log,
        "support_hash_precedes_heldout_target_access": all(
            [any(e["action"] == "SUPPORT_HASHED" and e["fold"] == k for e in vault.log)
             for k in range(6)]),
        "total_runtime_seconds": round(time.time() - t_all, 1),
    }, indent=2), encoding="utf-8")
    print("total %.0fs | proposals %d" % (time.time() - t_all,
                                          sum(r["proposals"] for r in budget_rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
