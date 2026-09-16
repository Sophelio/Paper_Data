"""S7.9 step D - Ranks 3, 4 and 5.

Rank 3 parsimony, Rank 4 conditioning, then the frozen Rank-5 procedure:
1000 discharge-bootstrap replicates (seed 2026090501) and the three
block-omission perturbations, each recomputing Ranks 1-4 over the SAME
Ahat_rec.

Efficiency measures used (allowed - they change HOW, never WHAT):
  * vectorized weighted reductions (matrix-vector products)
  * memoized conditioning and ACTIVE_TERMS, which are replicate-independent
    per-candidate quantities
No replicate is skipped, no candidate is screened on observed outcomes, and no
quantile definition is approximated.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from s7_9_coords import Engine, ACCESS_LOG  # noqa: E402

FLOOR = 0.01
SEED = 2026090501
NREP = 1000
NS = 20


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


class Ranker:
    def __init__(self, NR, ids, size, engine):
        self.NR = NR                       # (n,20,3)
        self.ids = ids
        self.size = size
        self.eng = engine
        self.kappa_cache = {}
        self.active_cache = {}

    # ---- memoized per-candidate quantities (replicate-independent) ------
    def logk(self, i):
        v = self.kappa_cache.get(i)
        if v is None:
            v = self.eng.cond_summary(depth_split(str(self.ids[i])))
            self.kappa_cache[i] = v
        return v

    def active(self, i):
        v = self.active_cache.get(i)
        if v is None:
            v = self.eng.candidate_profile(depth_split(str(self.ids[i])))["ACTIVE_TERMS"]
            self.active_cache[i] = v
        return v

    # ---- ranks ----------------------------------------------------------
    def run(self, w, blocks, P=None, P2=None):
        n = w.sum()
        NRb = self.NR[:, :, blocks]
        if P is None:
            P = NRb.mean(axis=2)
            P2 = P * P
        fit = (P @ w) / n
        m = fit.min()
        c = np.flatnonzero(fit == m)
        best = int(c[np.argmin(self.ids[c])])
        pb = P[best]
        d1 = P @ w - float(pb @ w)
        d2 = P2 @ w - 2.0 * (P @ (pb * w)) + float((pb * pb) @ w)
        mean = d1 / n
        var = np.maximum((d2 - n * mean * mean) / (n - 1), 0.0)
        thr = np.maximum(np.sqrt(var) / np.sqrt(n), FLOOR)
        e1 = np.flatnonzero(np.abs(fit - fit[best]) <= thr)

        # Rank 2
        sub = NRb[e1]
        bmean = np.tensordot(sub, w, axes=([1], [0])) / n
        bstar = np.argmax(bmean, axis=1)
        bw = bmean[np.arange(len(e1)), bstar]
        own = sub[np.arange(len(e1)), :, bstar]
        m = bw.min()
        c = np.flatnonzero(bw == m)
        ref = int(c[np.argmin(self.ids[e1][c])])
        ob = own[ref]
        d1 = own @ w - float(ob @ w)
        d2 = (own * own) @ w - 2.0 * (own @ (ob * w)) + float((ob * ob) @ w)
        mean = d1 / n
        var = np.maximum((d2 - n * mean * mean) / (n - 1), 0.0)
        keep = np.abs(bw - bw[ref]) <= np.maximum(np.sqrt(var) / np.sqrt(n), FLOOR)
        rep = np.repeat(sub.mean(axis=2), w.astype(np.int64), axis=1)
        p90 = np.where(keep, np.percentile(rep, 90, axis=1, method="linear"), np.inf)
        e2 = e1[p90 == p90.min()]

        # Rank 3
        s = self.size[e2]
        e3 = e2[s == s.min()]
        active_bound = False
        if len(e3) > 1:
            a = np.array([self.active(i) for i in e3])
            if a.min() != a.max():
                active_bound = True
            e3 = e3[a == a.min()]

        # Rank 4
        e4 = e3
        if len(e3) > 1:
            def summ(i):
                L = np.repeat(self.logk(i), w.astype(np.int64), axis=0)[:, blocks].reshape(-1)
                return (float(np.median(L)),
                        float(np.percentile(L, 90, method="linear")),
                        float(L.max()))
            S = np.array([summ(i) for i in e3])
            for col in range(3):
                e4 = e4[S[:len(e4), col] == S[:len(e4), col].min()] if False else e4
            keepm = np.ones(len(e3), bool)
            for col in range(3):
                v = np.where(keepm, S[:, col], np.inf)
                keepm &= (v == v.min())
            e4 = e3[keepm]

        winner = int(e4[np.argmin(self.ids[e4])])
        return e1, e2, e3, e4, winner, fit, bw, bstar, p90, keep, best, ref


def main() -> int:
    z = np.load(OUT / "manifests" / "_rank12_state.npz", allow_pickle=True)
    ids, size, NR = z["support_id"], z["size"], z["NR"]
    e1_0, e2_0 = z["e1"], z["e2"]

    eng = Engine()
    R = Ranker(NR, ids, size, eng)

    # ---------------- original Ranks 3 and 4 -----------------------------
    w1 = np.ones(NS)
    P = NR.mean(axis=2)
    P2 = P * P
    e1, e2, e3, e4, winner, fit, bw, bstar, p90, keep, best, ref = R.run(
        w1, [0, 1, 2], P, P2)
    assert np.array_equal(e1, e1_0) and np.array_equal(e2, e2_0), "rank1/2 mismatch"

    prof = eng.candidate_profile(depth_split(str(ids[winner])))
    print("E0=%d  E1=%d  E2=%d  E3=%d  E4=%d" % (len(ids), len(e1), len(e2), len(e3), len(e4)))
    print("winner: %s" % ids[winner])
    print("  ACTIVE_TERMS %d / size %d  | COND_MEDIAN %.6f P90 %.6f MAX %.6f"
          % (prof["ACTIVE_TERMS"], prof["support_size"],
             prof["COND_MEDIAN"], prof["COND_P90"], prof["COND_MAX"]))

    # ---------------- Rank 5: bootstrap ----------------------------------
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, NS, (NREP, NS))
    winners = np.empty(NREP, dtype=np.int64)
    sizes = np.empty((NREP, 4), dtype=np.int64)
    for r in range(NREP):
        w = np.bincount(draws[r], minlength=NS).astype(np.float64)
        a, b, c, d, wi, *_ = R.run(w, [0, 1, 2], P, P2)
        winners[r] = wi
        sizes[r] = (len(a), len(b), len(c), len(d))
        if (r + 1) % 200 == 0:
            print("  bootstrap %d/%d  (%.0fs)" % (r + 1, NREP, time.time() - t0))
    boot_time = time.time() - t0

    uw, cw = np.unique(winners, return_counts=True)
    order = np.argsort(-cw)
    print("bootstrap: %d unique Rank-4 winners in %d replicates (%.0fs)"
          % (len(uw), NREP, boot_time))
    for k in order[:8]:
        print("   %6.3f  %s" % (cw[k] / NREP, ids[uw[k]]))

    # ---------------- Rank 5: fold perturbations -------------------------
    folds = {}
    for k, drop in enumerate("ABC"):
        blocks = [i for i in range(3) if i != k]
        Pf = NR[:, :, blocks].mean(axis=2)
        a, b, c, d, wi, *_ = R.run(w1, blocks, Pf, Pf * Pf)
        folds["omit_" + drop] = {"winner": str(ids[wi]), "winner_idx": int(wi),
                                 "E1": len(a), "E2": len(b), "E3": len(c), "E4": len(d)}
        print("fold omit %s -> E1=%d E2=%d winner %s" % (drop, len(a), len(b), ids[wi]))

    # ---------------- Rank 5 scores over the ORIGINAL E4 -----------------
    boot_freq = {int(i): float((winners == i).sum()) / NREP for i in e4}
    fold_freq = {int(i): float(sum(1 for f in folds.values() if f["winner_idx"] == i)) / 3.0
                 for i in e4}
    e5 = np.array(sorted(e4, key=lambda i: (-boot_freq[i], -fold_freq[i], str(ids[i]))))
    bmax = max(boot_freq[i] for i in e4)
    e5 = np.array([i for i in e4 if boot_freq[i] == bmax])
    fmax = max(fold_freq[i] for i in e5)
    e5 = np.array([i for i in e5 if fold_freq[i] == fmax])
    c_dev_star = int(e5[np.argmin(ids[e5])])

    print("E5 = %d   C_dev_star = %s" % (len(e5), ids[c_dev_star]))
    print("  BOOT_SELECTION_FREQ %.3f   FOLD_SELECTION_FREQ %.3f"
          % (boot_freq[c_dev_star], fold_freq[c_dev_star]))

    # ---------------- reproducibility re-run -----------------------------
    rng2 = np.random.default_rng(SEED)
    draws2 = rng2.integers(0, NS, (NREP, NS))
    stream_ok = bool(np.array_equal(draws, draws2))
    check_idx = list(range(0, NREP, 97))
    rerun_ok = True
    for r in check_idx:
        w = np.bincount(draws2[r], minlength=NS).astype(np.float64)
        _, _, _, _, wi, *_ = R.run(w, [0, 1, 2], P, P2)
        if wi != winners[r]:
            rerun_ok = False
    winners_hash = __import__("hashlib").sha256(winners.tobytes()).hexdigest()

    # ---------------- outputs --------------------------------------------
    pd.DataFrame({
        "support_id": ids[e2], "support_size": size[e2],
        "ACTIVE_TERMS": [R.active(i) for i in e2],
        "active_terms_equals_size": [R.active(i) == size[i] for i in e2],
        "in_E3": np.isin(e2, e3),
    }).to_csv(OUT / "utility_rank_3_parsimony.csv", index=False)

    rows = []
    for i in e3:
        L = R.logk(i)
        rows.append({"support_id": str(ids[i]), "support_size": int(size[i]),
                     "COND_MEDIAN": float(np.median(L)),
                     "COND_P90": float(np.percentile(L, 90, method="linear")),
                     "COND_MAX": float(L.max()),
                     "n_infinite_cells": int(np.isinf(L).sum()),
                     "in_E4": bool(i in set(e4.tolist()))})
    pd.DataFrame(rows).to_csv(OUT / "utility_rank_4_conditioning.csv", index=False)

    pd.DataFrame([{
        "support_id": str(ids[i]), "support_size": int(size[i]),
        "BOOT_SELECTION_FREQ": boot_freq[i], "FOLD_SELECTION_FREQ": fold_freq[i],
        "is_C_dev_star": i == c_dev_star,
    } for i in e4]).to_csv(OUT / "utility_rank_5_support_stability.csv", index=False)

    pd.DataFrame([{"support_id": str(ids[uw[k]]), "support_size": int(size[uw[k]]),
                   "n_replicates_won": int(cw[k]),
                   "bootstrap_selection_frequency": float(cw[k] / NREP),
                   "in_original_E4": bool(uw[k] in set(e4.tolist()))}
                  for k in order]).to_csv(
        OUT / "bootstrap_selection_frequency.csv", index=False)

    pd.DataFrame([{"perturbation": k, "winner_support_id": v["winner"],
                   "E1": v["E1"], "E2": v["E2"], "E3": v["E3"], "E4": v["E4"],
                   "winner_is_C_dev_star": v["winner_idx"] == c_dev_star}
                  for k, v in folds.items()]).to_csv(
        OUT / "fold_selection_frequency.csv", index=False)

    pd.DataFrame([
        {"set": "E0", "rank": 0, "criterion": "explored frontier", "count": int(len(ids))},
        {"set": "E1", "rank": 1, "criterion": "primary fit quality", "count": int(len(e1))},
        {"set": "E2", "rank": 2, "criterion": "development generalization / stability", "count": int(len(e2))},
        {"set": "E3", "rank": 3, "criterion": "parsimony", "count": int(len(e3))},
        {"set": "E4", "rank": 4, "criterion": "conditioning", "count": int(len(e4))},
        {"set": "E5", "rank": 5, "criterion": "support stability", "count": int(len(e5))},
    ]).to_csv(OUT / "utility_survivor_sets.csv", index=False)

    np.savez_compressed(OUT / "manifests" / "_rank345_state.npz",
                        winners=winners, draws=draws, e3=e3, e4=e4, e5=e5,
                        c_dev_star=np.array([c_dev_star]),
                        rep_sizes=sizes)

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "rank_3": {
            "E2": int(len(e2)), "E3": int(len(e3)),
            "selected_minimum_support_size": int(size[e3].min()),
            "ACTIVE_TERMS": {str(ids[i]): int(R.active(i)) for i in e2},
            "active_terms_equals_support_size_for_all_survivors":
                all(R.active(i) == size[i] for i in e2),
            "RANK3_ACTIVE_TERMS_NONBINDING": bool(len(e2) == 1 or
                                                  all(R.active(i) == size[i] for i in e2)),
            "magnitude_threshold": None, "p_value_pruning": False,
            "intercept_counted": False,
        },
        "rank_4": {
            "E3": int(len(e3)), "E4": int(len(e4)),
            "method": "singular values of the calibration-standardized design, intercept excluded",
            "normal_equation_condition_number_used": False,
            "cutoff_introduced": False,
            "summaries": rows,
            "n_infinite_cells_total": int(sum(r["n_infinite_cells"] for r in rows)),
        },
        "rank_5": {
            "replicates": NREP, "seed": SEED,
            "resampled_unit": "development discharge",
            "blocks_resampled": False,
            "unique_rank4_bootstrap_winners": int(len(uw)),
            "winner_distribution_top": [
                {"support_id": str(ids[uw[k]]), "frequency": float(cw[k] / NREP)}
                for k in order[:10]],
            "fold_perturbations": folds,
            "BOOT_SELECTION_FREQ": {str(ids[i]): boot_freq[i] for i in e4},
            "FOLD_SELECTION_FREQ": {str(ids[i]): fold_freq[i] for i in e4},
            "pass_fail_threshold": None,
            "replicate_survivor_sizes": {
                "E1": {"min": int(sizes[:, 0].min()), "max": int(sizes[:, 0].max()),
                       "mean": float(sizes[:, 0].mean())},
                "E2": {"min": int(sizes[:, 1].min()), "max": int(sizes[:, 1].max()),
                       "mean": float(sizes[:, 1].mean())},
                "E3": {"min": int(sizes[:, 2].min()), "max": int(sizes[:, 2].max())},
                "E4": {"min": int(sizes[:, 3].min()), "max": int(sizes[:, 3].max())},
            },
            "runtime_seconds": round(boot_time, 1),
            "conditioning_memoized_candidates": len(R.kappa_cache),
            "active_terms_memoized_candidates": len(R.active_cache),
        },
        "reproducibility": {
            "rng_stream_identical_on_reseed": stream_ok,
            "independent_recheck_replicates": len(check_idx),
            "recheck_winners_identical": rerun_ok,
            "winners_sha256": winners_hash,
        },
        "E5": int(len(e5)),
        "C_dev_star": str(ids[c_dev_star]),
        "C_dev_star_index": c_dev_star,
    }
    (OUT / "manifests" / "RANK345_SUMMARY.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "manifests" / "DEVELOPMENT_ACCESS_LOG.json").write_text(
        json.dumps({"reads": ACCESS_LOG,
                    "external_predictor_reads": 0,
                    "external_target_reads": 0,
                    "external_model_evaluations": 0}, indent=2), encoding="utf-8")
    print("reproducibility: stream %s | recheck %s" % (stream_ok, rerun_ok))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
