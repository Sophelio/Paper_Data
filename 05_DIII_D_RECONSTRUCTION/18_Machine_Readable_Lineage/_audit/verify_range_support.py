"""Independent re-implementation of the K2 observational range-support predicate.

Written from the frozen POLICY EQUATION ONLY, not by reusing K2's own code, and
compared against the frozen sensitivity table across the entire frozen tau grid.
READ ONLY.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

S7 = Path(r"D:\SIR_paper\DIIID_example\S7")
EX = S7.parent
DATA = EX / "data" / "resampled_data_v6"
sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV

RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S77 = S7 / "07_search_policy_and_frontier"
K2 = S7 / "K2_observational_range_support_contract"
E20 = S7 / "E2_0_protocol_and_resampling_freeze"

BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
GRID = [0.0, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]

AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
    "signal_index").reset_index(drop=True)
P_ALL = list(HB.primitive_id)
P_DOT = [s for s in P_ALL if bool(HB.derivative_primary_eligible[
    HB.primitive_id == s].iloc[0])]
li = {s: k for k, s in enumerate(P_ALL)}
di = {s: k for k, s in enumerate(P_DOT)}
N = len(AT)
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
TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")

E = np.full((N, len(shots) * 3), np.nan)
DEG = np.zeros((N, len(shots) * 3), bool)
for si, s in enumerate(shots):
    t0 = float(TR.loc[s, "t_start_s"]) * 1000.0
    dtm = float(TR.loc[s, "delta_t_ms"]); n = int(TR.loc[s, "N_s"])
    grid = t0 + dtm * np.arange(n, dtype=np.float64)
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
    for a0 in range(0, N, 1500):
        rows = np.arange(a0, min(a0 + 1500, N))

        def gather(kind, idx):
            g = np.empty((idx.size, n)); lv = kind == 0
            if lv.any():
                g[lv] = L[idx[lv]]
            if (~lv).any():
                g[~lv] = D[idx[~lv]]
            return g

        A_ = gather(kA[rows], iA[rows]); o = op[rows]
        V = np.empty_like(A_)
        with np.errstate(divide="ignore", invalid="ignore"):
            m0 = o == 0; V[m0] = A_[m0]
            m1 = o == 1
            if m1.any():
                V[m1] = 1.0 / A_[m1]
            if (o >= 2).any():
                B_ = gather(kB[rows], iB[rows]); m2, m3 = o == 2, o == 3
                V[m2] = A_[m2] * B_[m2]; V[m3] = A_[m3] / B_[m3]
        for bi, (bn, c1, c2) in enumerate(BLOCKS):
            ci = si * 3 + bi
            cal = slice(0, int(np.floor(n * c1)))
            app = slice(int(np.floor(n * c1)), int(np.floor(n * c2)))
            vc, vp = V[:, cal], V[:, app]
            with np.errstate(invalid="ignore"):
                # E(c) exactly as the frozen policy equation states it
                Lo, Up = vc.min(axis=1), vc.max(axis=1)
                excess = np.maximum(np.maximum(Lo - vp.min(axis=1), 0.0),
                                    vp.max(axis=1) - Up)
                R = Up - Lo
                good = R > 0
                e = np.full(rows.size, np.nan)
                e[good] = excess[good] / R[good]
                e[~good & (excess == 0)] = 0.0     # constant cal, constant app -> E=0
                DEG[rows, ci] = (~good) & (excess > 0)   # explicit status, no epsilon
                E[rows, ci] = e

sens = pd.read_csv(K2 / "range_support_threshold_sensitivity.csv")
rep = []
print("tau    my_full  frozen  my_cellrate  frozen_cellrate  match")
for tau in GRID:
    sup = (E <= tau) & ~DEG
    full = int(sup.all(axis=1).sum())
    rate = float(sup.sum()) / sup.size
    row = sens[sens.tau == tau].iloc[0]
    ok = (full == int(row.atoms_full_domain_62)
          and abs(rate - float(row.cell_applicability_rate)) < 1e-12)
    print("%-6.2f %7d %7d  %.12f %.12f  %s"
          % (tau, full, int(row.atoms_full_domain_62), rate,
             row.cell_applicability_rate, "OK" if ok else "MISMATCH"))
    rep.append({"tau": tau, "recomputed_full_domain": full,
                "frozen_full_domain": int(row.atoms_full_domain_62),
                "recomputed_cell_rate": rate,
                "frozen_cell_rate": float(row.cell_applicability_rate),
                "match": bool(ok)})

ndeg = int(DEG.sum())
frozen_deg = int(sens.degenerate_cells.iloc[0])
print("\ndegenerate cells: recomputed %d | frozen %d | total cells %d | match %s"
      % (ndeg, frozen_deg, E.size, ndeg == frozen_deg))

# constructor counts at tau=1
sup1 = (E <= 1.0) & ~DEG
full1 = sup1.all(axis=1)
cc = {c: int((full1 & (AT.constructor.values == c)).sum())
      for c in sorted(set(AT.constructor))}
EXP = {"C0": 51, "C1": 18, "C2": 1488, "C3": 382, "C5": 8, "C6": 965, "C7": 539}
print("constructor counts at tau=1:", cc, "match", cc == EXP)

# epsilon check: no epsilon anywhere in the policy path
pol = json.loads((K2 / "RANGE_SUPPORT_POLICY_V1.json").read_text())
print("policy epsilon field:", pol["metric"]["epsilon"],
      "| epsilon_substituted:", pol["degenerate_calibration"]["epsilon_substituted"])

# monotonicity of the survivor curve (tau tuning test)
counts = [r["recomputed_full_domain"] for r in rep]
mono = all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1))
print("survivor curve monotone non-decreasing in tau:", mono, counts)

json.dump({"grid": rep, "degenerate_cells": ndeg, "frozen_degenerate": frozen_deg,
           "constructor_counts_tau1": cc, "constructor_expected": EXP,
           "monotone": bool(mono)},
          open(sys.argv[1], "w", encoding="utf-8"), indent=1)
