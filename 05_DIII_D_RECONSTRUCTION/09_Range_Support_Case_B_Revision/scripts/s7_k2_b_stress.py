"""S7.K2 step B - TARGET-BLIND atomic-universe stress test.

Evaluates the predeclared candidate range-support scores on all 10,778 frozen
admissible atomic coordinates over all 62 discharges x 3 blocks.

Reads predictor signals and coordinate values only. Never opens the density
target, a residual, an NRMSE, or any qualification label.
"""
from __future__ import annotations

import json
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
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S77 = S7 / "07_search_policy_and_frontier"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
CHUNK = 1500
ACCESS = {"target_reads": 0, "model_error_reads": 0, "residual_reads": 0,
          "V3_label_reads": 0, "support_family_outcome_label_reads": 0}


def main() -> int:
    pv = json.loads((OUT / "manifests" / "K2_PREVALUE.json").read_text())
    if pv["verdict"] != "PREVALUE_FROZEN":
        raise SystemExit("STOP: pre-value not frozen")

    AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
        "signal_index").reset_index(drop=True)
    P_ALL = list(HB.primitive_id)
    P_DOT = [s for s in P_ALL if bool(
        HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    N = len(AT)
    assert N == 10778, "atomic universe must be the frozen 10,778"

    OPC = {"C0": 0, "C1": 0, "C5": 1, "C2": 2, "C6": 2, "C3": 3, "C7": 3}
    kA = np.zeros(N, np.int8); iA = np.zeros(N, np.int32)
    kB = np.zeros(N, np.int8); iB = np.zeros(N, np.int32)
    op = np.zeros(N, np.int8)
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

    part = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json").read_text())
    shots = [str(s) for s in part["development"]["shot_ids"]] + \
            [str(s) for s in part["external"]["shot_ids"]]
    cohort = {str(s): "development" for s in part["development"]["shot_ids"]}
    cohort.update({str(s): "external" for s in part["external"]["shot_ids"]})
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")
    cells = [(s, b) for s in shots for b, _, _ in BLOCKS]
    NC = len(cells)
    assert NC == 186

    CMIN = np.full((N, NC), np.nan, np.float64)
    CMAX = np.full((N, NC), np.nan, np.float64)
    CRMS = np.full((N, NC), np.nan, np.float64)
    PMIN = np.full((N, NC), np.nan, np.float64)
    PMAX = np.full((N, NC), np.nan, np.float64)
    NONFIN = np.zeros((N, NC), bool)

    t0 = time.time()
    for si, s in enumerate(shots):
        t_start = float(TR.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TR.loc[s, "delta_t_ms"])
        n = int(TR.loc[s, "N_s"])
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
        slc = {}
        for bi, (bn, c1, c2) in enumerate(BLOCKS):
            slc[bn] = (slice(0, int(np.floor(n * c1))),
                       slice(int(np.floor(n * c1)), int(np.floor(n * c2))))
        for a0 in range(0, N, CHUNK):
            rows = np.arange(a0, min(a0 + CHUNK, N))
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
            V = np.empty_like(A)
            with np.errstate(divide="ignore", invalid="ignore"):
                m0 = o == 0
                V[m0] = A[m0]
                m1 = o == 1
                if m1.any():
                    V[m1] = 1.0 / A[m1]
                if (o >= 2).any():
                    B = gather(kB[rows], iB[rows])
                    m2, m3 = o == 2, o == 3
                    V[m2] = A[m2] * B[m2]
                    V[m3] = A[m3] / B[m3]
            for bi, (bn, _, _) in enumerate(BLOCKS):
                ci = si * 3 + bi
                cal, pro = slc[bn]
                vc, vp = V[:, cal], V[:, pro]
                bad = ~(np.isfinite(vc).all(axis=1) & np.isfinite(vp).all(axis=1))
                NONFIN[rows, ci] = bad
                with np.errstate(invalid="ignore"):
                    CMIN[rows, ci] = vc.min(axis=1)
                    CMAX[rows, ci] = vc.max(axis=1)
                    CRMS[rows, ci] = np.sqrt((vc * vc).mean(axis=1))
                    PMIN[rows, ci] = vp.min(axis=1)
                    PMAX[rows, ci] = vp.max(axis=1)
        if (si + 1) % 15 == 0:
            print("  %d/62 discharges (%.0fs)" % (si + 1, time.time() - t0))

    # ---- candidate scores -------------------------------------------------
    with np.errstate(invalid="ignore"):
        excess = np.maximum(np.maximum(CMIN - PMIN, 0.0), PMAX - CMAX)   # d_hull, >= 0
        R = CMAX - CMIN
        RMS = CRMS
    finite_cell = ~NONFIN & np.isfinite(excess) & np.isfinite(R) & np.isfinite(RMS)

    # R1: excess / calibration range
    deg_R1 = finite_cell & (R <= 0)
    ok_R1 = finite_cell & (R > 0)
    E1 = np.full((N, NC), np.nan)
    E1[ok_R1] = excess[ok_R1] / R[ok_R1]
    # degenerate calibration with identical protected values scores 0
    E1[deg_R1 & (excess == 0)] = 0.0
    deg_R1_hard = deg_R1 & (excess > 0)

    # R2: excess / calibration RMS
    deg_R2 = finite_cell & (RMS <= 0)
    ok_R2 = finite_cell & (RMS > 0)
    E2 = np.full((N, NC), np.nan)
    E2[ok_R2] = excess[ok_R2] / RMS[ok_R2]
    E2[deg_R2 & (excess == 0)] = 0.0
    deg_R2_hard = deg_R2 & (excess > 0)

    cons = AT.constructor.values
    fams = sorted(set(cons))

    def summarize(E, deg_hard, name, denom_ok):
        v = E[np.isfinite(E)]
        q = [0, 1, 5, 25, 50, 75, 90, 95, 99, 100]
        row = {"candidate": name,
               "n_cells_total": int(N * NC),
               "n_nonfinite_coordinate_cells": int(NONFIN.sum()),
               "n_scored": int(np.isfinite(E).sum()),
               "n_degenerate_calibration": int(deg_hard.sum()),
               "frac_degenerate": float(deg_hard.sum() / (N * NC)),
               "mean": float(v.mean()), "max": float(v.max())}
        for a, b in zip(q, np.percentile(v, q, method="linear")):
            row["p%d" % a] = float(b)
        return row

    summary = [summarize(E1, deg_R1_hard, "R1_excess_over_calibration_range", ok_R1),
               summarize(E2, deg_R2_hard, "R2_excess_over_calibration_rms", ok_R2)]
    pd.DataFrame(summary).to_csv(OUT / "range_support_atomic_audit.csv", index=False)

    rows = []
    for f in fams:
        m = cons == f
        for name, E, degh in [("R1_excess_over_calibration_range", E1, deg_R1_hard),
                              ("R2_excess_over_calibration_rms", E2, deg_R2_hard)]:
            sub = E[m]
            v = sub[np.isfinite(sub)]
            rows.append({"constructor": f, "n_atoms": int(m.sum()), "candidate": name,
                         "n_scored": int(np.isfinite(sub).sum()),
                         "n_degenerate": int(degh[m].sum()),
                         "frac_degenerate": float(degh[m].sum() / (m.sum() * NC)),
                         "median": float(np.median(v)) if v.size else np.nan,
                         "p90": float(np.percentile(v, 90)) if v.size else np.nan,
                         "p99": float(np.percentile(v, 99)) if v.size else np.nan,
                         "max": float(v.max()) if v.size else np.nan})
    pd.DataFrame(rows).to_csv(OUT / "range_support_constructor_summary.csv", index=False)

    np.savez_compressed(OUT / "manifests" / "_k2_scores.npz",
                        E1=E1.astype(np.float32), E2=E2.astype(np.float32),
                        nonfin=NONFIN, deg1=deg_R1_hard, deg2=deg_R2_hard,
                        cells=np.array(["%s:%s" % c for c in cells]),
                        coordinate_id=AT.coordinate_id.values.astype(object),
                        constructor=cons.astype(object))

    (OUT / "manifests" / "K2_STRESS_ACCESS_LOG.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        **ACCESS, "target_signal_opened": False, "verdict": "TARGET_BLIND",
        "n_atoms": int(N), "n_cells": int(NC), "runtime_seconds": round(time.time() - t0, 1),
    }, indent=2), encoding="utf-8")
    assert all(v == 0 for v in ACCESS.values())

    print("\natoms %d x cells %d = %d coordinate-cells" % (N, NC, N * NC))
    print("non-finite coordinate-cells (domain, NOT range): %d (%.4f%%)"
          % (NONFIN.sum(), 100 * NONFIN.sum() / (N * NC)))
    print()
    print(pd.DataFrame(summary)[["candidate", "n_scored", "n_degenerate_calibration",
                                 "p50", "p90", "p99", "max"]].to_string(index=False))
    print()
    print("=== constructor-stratified, candidate R1 ===")
    d = pd.DataFrame(rows)
    print(d[d.candidate == "R1_excess_over_calibration_range"][
        ["constructor", "n_atoms", "n_degenerate", "median", "p90", "p99", "max"]].round(4).to_string(index=False))
    print()
    print("=== constructor-stratified, candidate R2 ===")
    print(d[d.candidate == "R2_excess_over_calibration_rms"][
        ["constructor", "n_atoms", "n_degenerate", "median", "p90", "p99", "max"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
