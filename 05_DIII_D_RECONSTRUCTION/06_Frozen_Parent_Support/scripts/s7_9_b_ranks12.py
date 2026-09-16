"""S7.9 step B - execute Rank 1 (primary fit) and Rank 2 (stability).

Reuses the frozen S7.7R per-cell NRMSE arrays (reuse authorised in step A).
Rows are joined to the registry BY support_id; no row-order assumption is made.

Development values only. No external value is opened.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
V2 = S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"

FLOOR = 0.01
NS, NB = 20, 3


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


def se_from_weights(P, Pref, w):
    """sd(ddof=1)/sqrt(n) of (P - Pref) resampled with integer multiplicities w.

    Vectorized: all reductions are matrix-vector products, so a replicate costs
    O(n_candidates * 20) rather than a per-candidate loop.
    """
    n = w.sum()
    d1 = P @ w - float(Pref @ w)
    # (P - Pref)^2 @ w  =  P^2@w - 2 P@(Pref*w) + (Pref^2)@w
    d2 = (P * P) @ w - 2.0 * (P @ (Pref * w)) + float((Pref * Pref) @ w)
    mean = d1 / n
    var = (d2 - n * mean * mean) / (n - 1)
    return mean, np.sqrt(np.maximum(var, 0.0))


def rank1(P, w, ids):
    """P: (n,20) per-discharge NRMSE. Returns fit, best index, E1 mask."""
    n = w.sum()
    fit = (P @ w) / n
    m = fit.min()
    cand = np.flatnonzero(fit == m)
    best = int(cand[np.argmin(ids[cand])])          # canonical-first argmin
    mean, sd = se_from_weights(P, P[best], w)
    se = sd / np.sqrt(n)
    thr = np.maximum(se, FLOOR)
    return fit, best, np.abs(fit - fit[best]) <= thr, se, thr


def rank2(NR, w, idx, ids, blocks):
    """NR: (n,20,3). idx: E1 indices. blocks: block columns in play."""
    n = w.sum()
    sub = NR[idx][:, :, blocks]                                   # (k,20,nb)
    bmean = np.tensordot(sub, w, axes=([1], [0])) / n             # (k,nb)
    bstar = np.argmax(bmean, axis=1)                              # A<B<C tie-break
    bw = bmean[np.arange(len(idx)), bstar]
    own = sub[np.arange(len(idx)), :, bstar]                      # (k,20)

    m = bw.min()
    cand = np.flatnonzero(bw == m)
    ref = int(cand[np.argmin(ids[idx][cand])])
    mean, sd = se_from_weights(own, own[ref], w)
    se = sd / np.sqrt(n)
    keep = np.abs(bw - bw[ref]) <= np.maximum(se, FLOOR)

    per_shot = sub.mean(axis=2)                                   # (k,20)
    rep = np.repeat(per_shot, w.astype(np.int64), axis=1)
    p90 = np.percentile(rep, 90, axis=1, method="linear")
    p90m = np.where(keep, p90, np.inf)
    e2 = idx[p90m == p90m.min()]
    return e2, bw, bstar, p90, keep, ref, se


def main() -> int:
    reg = pd.read_csv(V2 / "explored_support_registry.csv")
    ex = np.load(V2 / "explored_per_cell_nrmse.npz", allow_pickle=True)
    at = np.load(V2 / "atomic_per_cell_nrmse.npz", allow_pickle=True)
    cells = [str(c) for c in ex["cells"]]
    shots = [c.split(":")[0] for c in cells[::3]]

    # join BY support_id
    src = {}
    for i, sid in enumerate(ex["support_id"]):
        src[str(sid)] = ("E", i)
    for i, sid in enumerate(at["coordinate_id"]):
        src[str(sid)] = ("A", i)
    NRe, NRa = ex["nrmse"], at["nrmse"]
    ids = reg.support_id.values
    NR = np.empty((len(reg), 60), dtype=np.float64)
    for r, sid in enumerate(ids):
        k, i = src[sid]
        NR[r] = NRe[i] if k == "E" else NRa[i]
    NR = NR.reshape(len(reg), NS, NB)
    assert np.isfinite(NR).all()

    P = NR.mean(axis=2)                       # (n,20) NRMSE_s
    w1 = np.ones(NS)
    size = reg.support_size.values

    # ---------------- Rank 1 ---------------------------------------------
    fit, best, e1m, se1, thr1 = rank1(P, w1, ids)
    e1 = np.flatnonzero(e1m)
    absdiff = np.abs(fit - fit[best])
    by_floor = int(((absdiff <= FLOOR)).sum())
    by_se_only = int(((absdiff > FLOOR) & (absdiff <= se1)).sum())

    print("E0 = %d" % len(reg))
    print("FIT_best = %.12f   support = %s" % (fit[best], ids[best]))
    print("E1 = %d   (floor-admitted %d, SE-admitted beyond floor %d)"
          % (len(e1), by_floor, by_se_only))
    print("   FIT range in E1 : [%.9f, %.9f]" % (fit[e1].min(), fit[e1].max()))
    print("   SE_delta range  : [%.9g, %.9g]" % (se1[e1].min(), se1[e1].max()))

    # ---------------- Rank 2 ---------------------------------------------
    e2, bw, bstar, p90, keep, ref, se2 = rank2(NR, w1, e1, ids, [0, 1, 2])
    print("E2 = %d" % len(e2))
    print("   BLOCK_WORST ref  = %s  (%.9f)" % (ids[e1][ref], bw[ref]))
    print("   BLOCK_WORST range in E1: [%.9f, %.9f]" % (bw.min(), bw.max()))
    print("   BLOCK_WORST-equivalent survivors: %d" % int(keep.sum()))
    print("   SHOT_P90 min = %.12f" % p90[keep].min())
    print("   b_star distribution in E1:", np.bincount(bstar, minlength=3).tolist())

    np.savez_compressed(OUT / "manifests" / "_rank12_state.npz",
                        support_id=ids, size=size, NR=NR.astype(np.float64),
                        fit=fit, se1=se1, e1=e1, best=np.array([best]),
                        bw=bw, bstar=bstar, p90=p90, keep=keep, e2=e2,
                        ref=np.array([ref]), shots=np.array(shots))

    # ---------------- CSV outputs ----------------------------------------
    r1 = pd.DataFrame({
        "support_id": ids, "support_size": size, "FIT": fit,
        "abs_diff_from_best": absdiff, "SE_delta_vs_best": se1,
        "delta_equiv": thr1, "in_E1": e1m,
        "admitted_by": np.where(~e1m, "not_admitted",
                        np.where(absdiff <= FLOOR, "floor_0.01", "SE_delta")),
    })
    r1.sort_values(["FIT", "support_id"]).to_csv(OUT / "utility_rank_1_fit.csv", index=False)

    r2 = pd.DataFrame({
        "support_id": ids[e1], "support_size": size[e1], "FIT": fit[e1],
        "BLOCK_WORST": bw, "b_star": np.array(["A", "B", "C"])[bstar],
        "SHOT_P90": p90, "block_worst_equivalent": keep,
        "in_E2": np.isin(e1, e2),
    })
    r2.sort_values(["BLOCK_WORST", "SHOT_P90", "support_id"]).to_csv(
        OUT / "utility_rank_2_stability.csv", index=False)

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "E0": int(len(reg)),
        "rank_1": {
            "FIT_best": float(fit[best]),
            "C_fit_best": str(ids[best]),
            "C_fit_best_size": int(size[best]),
            "E1": int(len(e1)),
            "FIT_min_E1": float(fit[e1].min()), "FIT_max_E1": float(fit[e1].max()),
            "SE_delta_min_E1": float(se1[e1].min()), "SE_delta_max_E1": float(se1[e1].max()),
            "admitted_within_floor": by_floor,
            "admitted_by_SE_beyond_floor": by_se_only,
            "floor": FLOOR, "floor_altered": False,
            "transitive_closure": False, "top_k": False,
        },
        "rank_2": {
            "E2": int(len(e2)),
            "block_worst_reference": str(ids[e1][ref]),
            "block_worst_reference_value": float(bw[ref]),
            "BLOCK_WORST_min": float(bw.min()), "BLOCK_WORST_max": float(bw.max()),
            "block_worst_equivalent_count": int(keep.sum()),
            "SHOT_P90_min": float(p90[keep].min()),
            "SHOT_P90_max_among_equivalent": float(p90[keep].max()),
            "b_star_counts": {b: int(c) for b, c in
                              zip("ABC", np.bincount(bstar, minlength=3))},
            "SE_delta_worst_used": True,
            "floor_only_fallback_invoked": False,
            "percentile_method": "linear",
            "new_epsilon_introduced": False,
        },
    }
    (OUT / "manifests" / "RANK12_SUMMARY.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
