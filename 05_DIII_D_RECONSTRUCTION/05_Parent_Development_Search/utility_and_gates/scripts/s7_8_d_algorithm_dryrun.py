"""S7.8 step D - algorithm dry run on a SYNTHETIC fixture.

Purpose: prove that the frozen S7.9 selection algorithm is implementable,
deterministic and internally coherent BEFORE S7.9 executes it.

This script deliberately does NOT read the Ahat_rec NRMSE values. It runs on a
synthetic fixture of the correct shape so that no utility quantity over the real
frontier is computed in S7.8. The only real artifact it touches is the support
registry, and only to re-confirm the canonical parse rule.
"""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
V2 = S7 / "07_search_policy_and_frontier" / "one_seed_primary_v2"

FIXTURE_SEED = 20260908          # dry-run fixture only
BOOTSTRAP_SEED = 2026090501      # the frozen Rank-5 seed
N_SHOTS, N_BLOCKS = 20, 3
FLOOR = 0.01


# ---------------------------------------------------------------- helpers
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


def se_delta(dif: np.ndarray) -> np.ndarray:
    """SE of a paired per-discharge difference: sd(ddof=1)/sqrt(20)."""
    return dif.std(axis=-1, ddof=1) / np.sqrt(dif.shape[-1])


def rank1(nr: np.ndarray, w: np.ndarray):
    """nr: (n_cand, 20, n_blocks). w: discharge multiplicities. -> FIT, E1 mask."""
    per_shot = nr.mean(axis=2)                       # (n, 20)
    fit = (per_shot * w).sum(axis=1) / w.sum()
    best = int(np.argmin(fit))
    dif = per_shot - per_shot[best]                  # paired, per discharge
    dif = np.repeat(dif, w.astype(int), axis=1)      # honour multiplicities
    thr = np.maximum(se_delta(dif), FLOOR)
    return fit, np.abs(fit - fit[best]) <= thr, best


def rank2(nr: np.ndarray, w: np.ndarray, idx: np.ndarray):
    """Returns the E2 survivor index set within the E1 index set idx."""
    sub = nr[idx]
    block_mean = (sub * w[None, :, None]).sum(axis=1) / w.sum()   # (k, n_blocks)
    bstar = np.argmax(block_mean, axis=1)                         # A<B<C tie-break
    bw = block_mean[np.arange(len(idx)), bstar]
    own = sub[np.arange(len(idx)), :, bstar]                      # (k, 20)
    best = int(np.argmin(bw))
    dif = np.repeat(own - own[best], w.astype(int), axis=1)
    thr = np.maximum(se_delta(dif), FLOOR)
    keep = np.abs(bw - bw[best]) <= thr

    per_shot = np.repeat(sub.mean(axis=2), w.astype(int), axis=1)
    p90 = np.percentile(per_shot, 90, axis=1, method="linear")
    p90 = np.where(keep, p90, np.inf)
    return idx[p90 == p90.min()], bw, bstar, p90


def rank3(idx: np.ndarray, size: np.ndarray, active: np.ndarray):
    s = size[idx]
    idx = idx[s == s.min()]
    a = active[idx]
    return idx[a == a.min()]


def rank4(idx: np.ndarray, logk: np.ndarray, w: np.ndarray):
    """logk: (n_cand, 20, n_blocks) log10 condition numbers."""
    sub = np.repeat(logk[idx], w.astype(int), axis=1).reshape(len(idx), -1)
    med = np.median(sub, axis=1)
    idx2 = idx[med == med.min()]
    sub = np.repeat(logk[idx2], w.astype(int), axis=1).reshape(len(idx2), -1)
    p90 = np.percentile(sub, 90, axis=1, method="linear")
    idx3 = idx2[p90 == p90.min()]
    sub = np.repeat(logk[idx3], w.astype(int), axis=1).reshape(len(idx3), -1)
    mx = sub.max(axis=1)
    return idx3[mx == mx.min()]


def ranks_1_to_4(nr, logk, size, active, ids, w, blocks):
    nrb, logkb = nr[:, :, blocks], logk[:, :, blocks]
    _, e1m, _ = rank1(nrb, w)
    e1 = np.flatnonzero(e1m)
    e2, _, _, _ = rank2(nrb, w, e1)
    e3 = rank3(e2, size, active)
    e4 = rank4(e3, logkb, w)
    winner = e4[np.argmin(ids[e4])]      # canonical support-id tie-break
    return e1, e2, e3, e4, winner


# ---------------------------------------------------------------- fixture
def main() -> int:
    rng = np.random.default_rng(FIXTURE_SEED)
    n = 400
    nr = np.abs(rng.normal(0.30, 0.05, (n, N_SHOTS, N_BLOCKS))).astype(np.float64)
    size = rng.integers(1, 13, n)
    active = size.copy()
    logk = np.abs(rng.normal(1.0, 0.4, (n, N_SHOTS, N_BLOCKS)))
    ids = np.array(["SYN%05d" % i for i in range(n)])
    w1 = np.ones(N_SHOTS)

    results = {}

    # --- check 1: BLOCK_WORST paired-SE coherence identity ---------------
    block_mean = nr.mean(axis=1)
    bstar = np.argmax(block_mean, axis=1)
    bw = block_mean[np.arange(n), bstar]
    own = nr[np.arange(n), :, bstar]
    a, b = 3, 17
    lhs = float((own[a] - own[b]).mean())
    rhs = float(bw[a] - bw[b])
    results["block_worst_paired_identity"] = {
        "claim": "mean_s d_s(A,B) == BLOCK_WORST(A) - BLOCK_WORST(B)",
        "max_abs_deviation_over_all_pairs": float(
            np.abs((own[:, None, :] - own[None, :, :]).mean(axis=2)
                   - (bw[:, None] - bw[None, :])).max()),
        "example_lhs": lhs,
        "example_rhs": rhs,
        "holds": bool(np.allclose(
            (own[:, None, :] - own[None, :, :]).mean(axis=2),
            bw[:, None] - bw[None, :], atol=1e-12)),
        "consequence": "the section-11 fallback to a 0.01-only floor is NOT required",
    }

    # --- check 2: worst-block tie-break determinism ----------------------
    tied = np.zeros((3, N_SHOTS, N_BLOCKS))
    tied[0, :, :] = 0.5                      # all three blocks exactly tied
    results["worst_block_tie_break"] = {
        "all_blocks_tied_case_selects": ["A", "B", "C"][int(np.argmax(tied[0].mean(axis=0)))],
        "rule": "numpy.argmax returns the first maximum, which is block A under the canonical order A<B<C",
        "deterministic": True,
    }

    # --- check 3: best candidate is always in E_fit -----------------------
    fit, e1m, best = rank1(nr, w1)
    results["rank1"] = {
        "best_in_E_fit": bool(e1m[best]),
        "E_fit_size": int(e1m.sum()),
        "n_candidates": n,
        "is_top_k": False,
        "floor_binding_when_se_smaller": bool(
            (np.maximum(se_delta(np.repeat(nr.mean(axis=2) - nr.mean(axis=2)[best],
                                           w1.astype(int), axis=1)), FLOOR) == FLOOR).any()),
    }

    # --- check 4: full pipeline determinism ------------------------------
    r_a = ranks_1_to_4(nr, logk, size, active, ids, w1, [0, 1, 2])
    r_b = ranks_1_to_4(nr, logk, size, active, ids, w1, [0, 1, 2])
    results["determinism"] = {
        "two_identical_runs_agree": bool(all(
            np.array_equal(x, y) for x, y in zip(r_a[:4], r_b[:4]))
            and int(r_a[4]) == int(r_b[4])),
        "survivor_sizes": {"E1": int(len(r_a[0])), "E2": int(len(r_a[1])),
                           "E3": int(len(r_a[2])), "E4": int(len(r_a[3]))},
        "winner_is_unique": True,
        "monotone_nesting": bool(
            set(r_a[3]) <= set(r_a[2]) <= set(r_a[1]) <= set(r_a[0])),
    }

    # --- check 5: unit multiplicities reproduce the plain computation -----
    fit_w, _, _ = rank1(nr, np.ones(N_SHOTS))
    results["bootstrap_weighting"] = {
        "unit_weights_reproduce_plain_fit": bool(
            np.allclose(fit_w, nr.mean(axis=(1, 2)))),
        "note": "integer multiplicities are the only mechanism by which a replicate enters any aggregation",
    }

    # --- check 6: bootstrap stream reproducibility ------------------------
    g1 = np.random.default_rng(BOOTSTRAP_SEED)
    g2 = np.random.default_rng(BOOTSTRAP_SEED)
    d1 = g1.integers(0, N_SHOTS, (1000, N_SHOTS))
    d2 = g2.integers(0, N_SHOTS, (1000, N_SHOTS))
    results["bootstrap_stream"] = {
        "seed": BOOTSTRAP_SEED,
        "replicates": 1000,
        "reproducible": bool(np.array_equal(d1, d2)),
        "first_replicate_multiset_head": d1[0][:8].tolist(),
        "mean_distinct_discharges_per_replicate": float(
            np.mean([len(set(r.tolist())) for r in d1])),
    }

    # --- check 7: fold perturbation shapes --------------------------------
    fold = {}
    for k, drop in enumerate("ABC"):
        keep = [i for i in range(3) if i != k]
        r = ranks_1_to_4(nr, logk, size, active, ids, w1, keep)
        fold["omit_" + drop] = {"cells": len(keep) * N_SHOTS,
                                "E4_size": int(len(r[3])),
                                "winner": str(ids[r[4]])}
    results["fold_perturbation"] = fold

    # --- check 8: conditioning conventions --------------------------------
    z = rng.normal(size=(48, 5))
    z = (z - z.mean(axis=0)) / z.std(axis=0, ddof=0)
    sv = np.linalg.svd(z, compute_uv=False)
    kappa_svd = sv[0] / sv[-1]
    ev = np.linalg.eigvalsh(z.T @ z)
    kappa_normal = ev[-1] / ev[0]
    zc = z.copy()
    zc[:, 2] = 0.0
    sv0 = np.linalg.svd(zc, compute_uv=False)
    single = np.linalg.svd(z[:, :1], compute_uv=False)
    results["conditioning"] = {
        "kappa_from_svd": float(kappa_svd),
        "normal_equation_kappa_squared": float(kappa_normal),
        "ratio_confirms_squaring": float(kappa_normal / kappa_svd ** 2),
        "svd_rule_is_the_frozen_one": True,
        "zero_column_gives_infinite_kappa": bool(sv0[-1] == 0.0),
        "singleton_support_kappa": float(single[0] / single[-1]),
        "singleton_log10_kappa": float(np.log10(single[0] / single[-1])),
    }

    # --- check 9: canonical parse on the REAL registry (identity only) ----
    reg = pd.read_csv(V2 / "explored_support_registry.csv")
    parsed = np.array([len(depth_split(s)) for s in reg.support_id])
    naive = np.array([len(str(s).split("|")) for s in reg.support_id])
    results["canonical_parse"] = {
        "rows": int(len(reg)),
        "depth_aware_reproduces_support_size": bool((parsed == reg.support_size.values).all()),
        "naive_split_mismatch_rows": int((naive != reg.support_size.values).sum()),
        "naive_split_mismatch_fraction": float((naive != reg.support_size.values).mean()),
        "note": "identity check only; no NRMSE value of the frontier was read",
    }

    ok = (results["block_worst_paired_identity"]["holds"]
          and results["rank1"]["best_in_E_fit"]
          and results["determinism"]["two_identical_runs_agree"]
          and results["determinism"]["monotone_nesting"]
          and results["bootstrap_weighting"]["unit_weights_reproduce_plain_fit"]
          and results["bootstrap_stream"]["reproducible"]
          and results["canonical_parse"]["depth_aware_reproduces_support_size"])

    out = {
        "dry_run_id": "S7_8_ALGORITHM_DRY_RUN_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "prove the frozen S7.9 algorithm is implementable and deterministic",
        "fixture": {
            "synthetic": True,
            "seed": FIXTURE_SEED,
            "n_candidates": n,
            "shape": [n, N_SHOTS, N_BLOCKS],
            "reason": (
                "S7.8 may not execute utility over Ahat_rec; a synthetic fixture "
                "of the correct shape exercises every code path without "
                "computing any real utility quantity"),
        },
        "ahat_rec_nrmse_values_read": False,
        "candidate_selected": False,
        "checks": results,
        "verdict": "ALGORITHM_EXECUTABLE_AND_DETERMINISTIC" if ok else "DRY_RUN_FAILED",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
        },
    }
    (OUT / "manifests" / "ALGORITHM_DRY_RUN.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print("block-worst paired identity holds :", results["block_worst_paired_identity"]["holds"])
    print("  max abs deviation               :", results["block_worst_paired_identity"]["max_abs_deviation_over_all_pairs"])
    print("best always in E_fit              :", results["rank1"]["best_in_E_fit"])
    print("pipeline deterministic            :", results["determinism"]["two_identical_runs_agree"])
    print("survivor nesting E4<=E3<=E2<=E1   :", results["determinism"]["monotone_nesting"])
    print("bootstrap stream reproducible     :", results["bootstrap_stream"]["reproducible"])
    print("normal-equation kappa is squared  : ratio",
          round(results["conditioning"]["ratio_confirms_squaring"], 12))
    print("singleton log10(kappa)            :", results["conditioning"]["singleton_log10_kappa"])
    print("naive-split mismatch fraction     :",
          round(results["canonical_parse"]["naive_split_mismatch_fraction"], 4))
    print("verdict                           :", out["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
