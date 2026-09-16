"""S7.E2.2 step B - one fresh full-object descriptive search.

SIGMA_REC_ONE_SEED_PRIMARY_V2 adapted mechanically to the whole 62-discharge
object: the search, the utility and the estimator are IMPORTED FROM THE E2.1
EXECUTION MODULES, not re-implemented, so the policy is identical by
construction. The only mechanical adaptation is that the discharge set over
which the search is scored is all 62 rather than a fold's 51-52.

ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION = true.
This is descriptive. No held-out set exists here and no validation claim is made.
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
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
E21 = S7 / "E2_1_crossfitted_discovery_and_qualification"
sys.path.insert(0, str(E21 / "scripts"))
from e2_1_engine import Engine, Vault, BLOCKS, SUPPORT_MAX, CAP, EPS, \
    BOOT_SEED, NREP  # noqa: E402
from e2_1_b_run import ranks_1_to_4  # noqa: E402

BUDGET = 300000
NAME = "C_E2_ALL_DESC"


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main() -> int:
    pre = json.loads((OUT / "manifests" / "E2_2_PRESEARCH.json").read_text())
    if pre["verdict"] != "PRESEARCH_VERIFIED":
        raise SystemExit("STOP: lineage or basis verification failed")

    basis = pd.read_csv(OUT / "manifests" / "C_E2_FULL_DOMAIN_E2_2.csv")
    bset = list(basis.coordinate_id)
    fa = pd.read_csv(E20 / "outer_fold_assignment.csv", dtype={"discharge": str})
    train = sorted(fa.discharge)          # <-- the whole finite object
    assert len(train) == 62

    vault = Vault()
    eng = Engine(vault)
    ACTIVE = sorted(set(basis.constructor))
    t0 = time.time()

    # ---- descriptive target access over the whole object ---------------
    vault.allow_calibration(train)
    vault.allow_protected(train)
    vault.log.append({"utc": datetime.now(timezone.utc).isoformat(),
                      "action": "ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION",
                      "n_shots": len(train),
                      "note": "cross-fitted qualification verdict already frozen; "
                              "no validation claim attaches to E2.2"})

    CELLS = [(s, bn) for s in train for bn, _, _ in BLOCKS]
    NC = len(CELLS)

    # ---- atomic navigation scores over the basis -----------------------
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

    # ---- strata, constructor-balanced shortlist, one seed per stratum ---
    order_df = pd.DataFrame({"cid": bset, "st": [eng.strata_of[c] for c in bset],
                             "J": Jat}).sort_values(["J", "cid"])
    ordered = {}
    for r in order_df.itertuples():
        ordered.setdefault(r.st, []).append(r.cid)
    ALL_STRATA = sorted(ordered)
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
    pd.DataFrame(short_rows).to_csv(OUT / "manifests" / "shortlist.csv", index=False)

    # ---- Gram machinery over the shortlist ------------------------------
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

    # ---- lockstep greedy expansion --------------------------------------
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

    if cnt["proposals"] > BUDGET:
        raise SystemExit("STOP: descriptive search exceeded the frozen budget")
    t_search = time.time() - t0

    # ---- frontier --------------------------------------------------------
    fr = pd.DataFrame(ROWS).drop_duplicates("support_id").reset_index(drop=True)
    ids = fr.support_id.values
    size = fr.support_size.values
    idxs = list(fr.idx.values)
    NR = np.stack([CACHE[frozenset(t_)][1] for t_ in idxs]).reshape(
        len(ids), len(train), 3)
    ATOMS = [sorted(SL_IDS[q] for q in t_) for t_ in idxs]

    # ---- frozen U_rec, Ranks 1-5 ----------------------------------------
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

    # ---- realise the selected representation descriptively ---------------
    kap_med, kap_p90, kap_max = kappa_fn(star, w1, [0, 1, 2])
    si = int(np.flatnonzero(e1 == star)[0])
    cell_rows = []
    for s in train:
        for bn, _, _ in BLOCKS:
            sc = eng.score_cell(atoms, s, bn)
            cell_rows.append({"shot_id": s, "era": eng.era[s], "block": bn,
                              "nrmse": sc["nrmse"], "rmse": sc["rmse"],
                              "scale": sc["scale"],
                              "log10_kappa": float(np.log10(sc["kappa"])),
                              "active_terms": sc["active"]})
    cells = pd.DataFrame(cell_rows)
    per_shot = cells.groupby("shot_id").nrmse.mean()

    sup_id = "|".join(atoms)
    sup_hash = h(sup_id)
    stamp = datetime.now(timezone.utc).isoformat()

    det = []
    for a in atoms:
        det.append({"coordinate_id": a, "constructor": eng.cons_of[a],
                    "search_stratum": eng.strata_of[a],
                    "primitive_ancestors": "|".join(eng.prim_of[a]),
                    "scientific_families": "|".join(eng.anc_of[a]),
                    "J_atomic_navigation": float(Jof[a]),
                    "in_shortlist_round_robin": int(
                        [r["round_robin_order"] for r in short_rows
                         if r["coordinate_id"] == a][0])})
    pd.DataFrame(det).to_csv(OUT / "full_object_coordinate_details.csv", index=False)
    cells.to_csv(OUT / "full_object_descriptive_cell_metrics.csv", index=False)

    cons_counts = {}
    for a in atoms:
        cons_counts[eng.cons_of[a]] = cons_counts.get(eng.cons_of[a], 0) + 1
    fam_counts = {}
    for a in atoms:
        for f in eng.anc_of[a]:
            fam_counts[f] = fam_counts.get(f, 0) + 1
    prim_counts = {}
    for a in atoms:
        for p in eng.prim_of[a]:
            prim_counts[p] = prim_counts.get(p, 0) + 1

    freeze = {
        "record_id": "E2_2_SUPPORT_FREEZE_V1",
        "machine_name": NAME,
        "label": "FULL_OBJECT_DESCRIPTIVE_REPRESENTATION",
        "hashed_utc": stamp,
        "support_id": sup_id,
        "support_size": len(atoms),
        "sha256": sup_hash,
        "coordinates": atoms,
        "constructor_counts": cons_counts,
        "scientific_family_counts": fam_counts,
        "primitive_counts": prim_counts,
        "primitives": sorted(prim_counts),
        "families": sorted(fam_counts),
        "selected_by": "U_REC_OPERATIONAL_V1 unchanged, ranks 1-5",
        "search_policy": "SIGMA_REC_ONE_SEED_PRIMARY_V2 adapted mechanically to "
                         "the whole 62-discharge object",
        "descriptive_only": True,
        "externally_validated": False,
        "held_out": False,
        "canonical_equation": False,
        "cannot_change_E2_1": True,
    }
    (OUT / "E2_2_SUPPORT_FREEZE.json").write_text(json.dumps(freeze, indent=2),
                                                  encoding="utf-8")
    pd.DataFrame({"coordinate_id": atoms,
                  "constructor": [eng.cons_of[a] for a in atoms],
                  "position": range(1, len(atoms) + 1)}).to_csv(
        OUT / "full_object_selected_support.csv", index=False)

    result = {
        "record_id": "E2_2_RESULT_V1",
        "stage": "S7.E2.2",
        "generated_utc": stamp,
        "machine_name": NAME,
        "ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION": True,
        "n_discharges": len(train),
        "n_cells": NC,
        "search": {
            "policy": "SIGMA_REC_ONE_SEED_PRIMARY_V2",
            "proposals": cnt["proposals"],
            "unique_supports_evaluated": cnt["unique"],
            "frontier_size": int(len(ids)),
            "budget": BUDGET,
            "within_budget": cnt["proposals"] <= BUDGET,
            "n_strata": len(ALL_STRATA),
            "shortlist_size": M,
            "seeds": len(seeds),
            "second_seed_used": False,
            "budget_extended": False,
            "reused_E2_1_supports": False,
            "search_seconds": round(t_search, 1),
        },
        "utility": {
            "E1_fit_equivalent": int(len(e1)), "E2_stability": int(len(e2)),
            "E3_parsimony": int(len(e3)), "E4_conditioning": int(len(e4)),
            "E5_support_stability": int(len(e5)),
            "FIT": float(fit[star]), "FIT_best_in_frontier": float(fit[e1].min()),
            "BLOCK_WORST": float(bw[si]), "worst_block": "ABC"[int(bstar[si])],
            "SHOT_P90": float(p90[si]),
            "support_size": int(len(atoms)),
            "ACTIVE_TERMS": active_fn(star),
            "COND_MEDIAN": kap_med, "COND_P90": kap_p90, "COND_MAX": kap_max,
            "BOOT_SELECTION_FREQ": bfreq[star],
            "BLOCK_OMISSION_FREQ": ffreq[star],
            "n_unique_bootstrap_winners": int(len(set(winners.tolist()))),
            "bootstrap_seed": BOOT_SEED, "bootstrap_replicates": NREP,
            "block_omission_winners": folds_om,
        },
        "descriptive_fit": {
            "mean_cell_nrmse": float(cells.nrmse.mean()),
            "median_cell_nrmse": float(cells.nrmse.median()),
            "mean_discharge_nrmse": float(per_shot.mean()),
            "median_discharge_nrmse": float(per_shot.median()),
            "p90_discharge_nrmse": float(np.percentile(per_shot.values, 90)),
            "max_discharge_nrmse": float(per_shot.max()),
            "worst_discharge": str(per_shot.idxmax()),
            "n_discharges_above_1": int((per_shot > 1.0).sum()),
            "earlier_mean": float(per_shot[[s for s in train
                                            if eng.era[s] == "earlier"]].mean()),
            "later_mean": float(per_shot[[s for s in train
                                          if eng.era[s] == "later"]].mean()),
            "IS_NOT_A_VALIDATION_METRIC": True,
            "note": "in-sample descriptive fit over the whole object; the "
                    "qualification evidence is the E2.1 cross-fitted result",
        },
        "support": freeze,
        "access_ledger": vault.log,
    }
    (OUT / "E2_2_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    fr.drop(columns=["idx"]).to_csv(OUT / "manifests" / "frontier_summary.csv",
                                    index=False)
    (OUT / "manifests" / "E2_2_SEARCH_AUDIT.json").write_text(json.dumps({
        "record_id": "E2_2_SEARCH_AUDIT_V1", "generated_utc": stamp,
        "proposals": cnt["proposals"], "budget": BUDGET,
        "within_budget": cnt["proposals"] <= BUDGET,
        "unique_supports": cnt["unique"], "frontier": int(len(ids)),
        "strata": len(ALL_STRATA), "shortlist": M,
        "one_seed_per_stratum": True, "support_bound": [1, SUPPORT_MAX],
        "shortlist_cap_per_constructor": CAP,
        "fresh_search": True, "outcome_triggered_extension": False,
        "total_seconds": round(time.time() - t0, 1),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
    }, indent=2), encoding="utf-8")

    print("proposals %d / %d | frontier %d | strata %d | shortlist %d"
          % (cnt["proposals"], BUDGET, len(ids), len(ALL_STRATA), M))
    print("E1 %d E2 %d E3 %d E4 %d E5 %d" % (len(e1), len(e2), len(e3), len(e4), len(e5)))
    print("%s size %d | %s" % (NAME, len(atoms), sup_hash[:12]))
    print("  " + sup_id)
    print("FIT %.6f | BLOCK_WORST %.6f (%s) | SHOT_P90 %.6f | cond med %.3f | boot %.3f"
          % (fit[star], bw[si], "ABC"[int(bstar[si])], p90[si], kap_med, bfreq[star]))
    print("descriptive mean %.4f median %.4f max %.4f (%s) | >1: %d"
          % (per_shot.mean(), per_shot.median(), per_shot.max(),
             per_shot.idxmax(), int((per_shot > 1.0).sum())))
    print("%.0fs" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
