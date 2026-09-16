"""S7.9 - development coordinate engine.

Realises scientific coordinates on the 20 DEVELOPMENT discharges exactly as
S7.7R did, and implements DEVELOPMENT_RELATION_OLS_V1 explicitly:

    calibration-only mean/sd  ->  sd <= 0 gives divisor 1.0 (no epsilon)
    standardize, apply unchanged to protected rows
    fitted intercept, affine OLS, discharge/block-local coefficients

Also provides the Rank-4 conditioning quantity: singular values of the
calibration-standardized design with the intercept column excluded.

FIREWALL: the external cohort is asserted absent from every access. Any external
shot id reaching this module raises FIREWALL_BREACH.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

S7 = Path(__file__).resolve().parents[2]
EX = S7.parent
S72 = S7 / "02_reconstruction_contract"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S77 = S7 / "07_search_policy_and_frontier"
DATA = EX / "data" / "resampled_data_v6"

import sys
sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

TARGET = "density"
BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}

ACCESS_LOG = []


class Engine:
    def __init__(self):
        AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
        HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
            "signal_index").reset_index(drop=True)
        self.HB = HB
        self.P_ALL = list(HB.primitive_id)
        self.P_DOT = [s for s in self.P_ALL if bool(
            HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
        assert (len(self.P_ALL), len(self.P_DOT)) == (70, 63)
        li = {s: k for k, s in enumerate(self.P_ALL)}
        di = {s: k for k, s in enumerate(self.P_DOT)}

        self.AT = AT
        self.ORIG = list(AT.coordinate_id)
        assert len(self.ORIG) == 10778
        self.row_of = {c: k for k, c in enumerate(self.ORIG)}
        self.cons_of = dict(zip(AT.coordinate_id, AT.constructor))

        FULL = pd.read_csv(S76R / "primary_atomic_coordinate_universe.csv")
        self.anc_raw = dict(zip(FULL.coordinate_id, FULL.primitive_ancestors))
        self.fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))

        N = len(AT)
        OPC = {"C0": 0, "C1": 0, "C5": 1, "C2": 2, "C6": 2, "C3": 3, "C7": 3}
        self.kA = np.zeros(N, np.int8); self.iA = np.zeros(N, np.int32)
        self.kB = np.zeros(N, np.int8); self.iB = np.zeros(N, np.int32)
        self.op = np.zeros(N, np.int8)
        for r, (c, ops) in enumerate(zip(AT.constructor, AT.ordered_operands)):
            o = str(ops).split("|")
            self.op[r] = OPC[c]
            if c in ("C1", "C7"):
                self.kA[r], self.iA[r] = 1, di[o[0]]
            else:
                self.kA[r], self.iA[r] = 0, li[o[0]]
            if c in ("C2", "C3", "C7"):
                self.kB[r], self.iB[r] = 0, li[o[1]]
            elif c == "C6":
                self.kB[r], self.iB[r] = 1, di[o[1]]

        part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
        self.dev = list(part["development"]["shot_ids"])
        self.ext = set(part["external"]["shot_ids"])
        TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str})
        TRd = TR[TR.cohort == "development"].set_index("discharge")

        self.LEV, self.DER, self.YT, self.SLC = {}, {}, {}, {}
        for s in self.dev:
            if s in self.ext:
                raise SystemExit("STOP: FIREWALL_BREACH")
            t0 = float(TRd.loc[s, "t_start_s"]) * 1000.0
            dtm = float(TRd.loc[s, "delta_t_ms"])
            n = int(TRd.loc[s, "N_s"])
            grid = t0 + dtm * np.arange(n, dtype=np.float64)
            tsec = grid / 1000.0
            with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
                L = np.empty((70, n))
                for k, sig in enumerate(self.P_ALL):
                    tt, vv = PROV._load_signal(a, sig)
                    L[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                        str(PROV.SIGNAL_UNIT[sig]), 1.0)
                tt, vv = PROV._load_signal(a, TARGET)
                y = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                    str(PROV.SIGNAL_UNIT[TARGET]), 1.0)
            D = np.empty((63, n))
            for k, sig in enumerate(self.P_DOT):
                D[k] = np.gradient(L[li[sig]], tsec, edge_order=2)
            self.LEV[s], self.DER[s], self.YT[s] = L, D, y
            for bn, c1, c2 in BLOCKS:
                self.SLC[(s, bn)] = (slice(0, int(np.floor(n * c1))),
                                     slice(int(np.floor(n * c1)), int(np.floor(n * c2))))
            ACCESS_LOG.append({
                "stage": "S7.9", "shot_id": s, "cohort": "development",
                "predictor_signals_read": 70, "target_signal_read": TARGET,
                "target_values_read": int(n), "external_values_read": 0,
                "reason": "Rank-3 ACTIVE_TERMS and Rank-4 conditioning",
            })
        self.CELLS = [(s, bn) for s in self.dev for bn, _, _ in BLOCKS]

    # ------------------------------------------------------------------
    def realise(self, rows, s):
        L, D = self.LEV[s], self.DER[s]
        n = L.shape[1]

        def gather(kind, idx):
            g = np.empty((idx.size, n))
            lv = kind == 0
            if lv.any():
                g[lv] = L[idx[lv]]
            if (~lv).any():
                g[~lv] = D[idx[~lv]]
            return g

        A = gather(self.kA[rows], self.iA[rows])
        o = self.op[rows]
        out = np.empty_like(A)
        with np.errstate(divide="ignore", invalid="ignore"):
            m0 = o == 0
            out[m0] = A[m0]
            m1 = o == 1
            if m1.any():
                out[m1] = 1.0 / A[m1]
            if (o >= 2).any():
                B = gather(self.kB[rows], self.iB[rows])
                m2, m3 = o == 2, o == 3
                out[m2] = A[m2] * B[m2]
                out[m3] = A[m3] / B[m3]
        return out

    # ------------------------------------------------------------------
    def cell_arrays(self, atoms, s, bn):
        """Standardized calibration design Z (n_cal, m), protected Zp, y."""
        rows = np.array([self.row_of[a] for a in atoms])
        cal, pro = self.SLC[(s, bn)]
        V = self.realise(rows, s)
        xc, xp = V[:, cal], V[:, pro]
        mu = xc.mean(axis=1, keepdims=True)
        sd = xc.std(axis=1, ddof=0, keepdims=True)
        div = np.where(sd <= 0, 1.0, sd)              # no epsilon, exact 1.0
        zc = (xc - mu) / div
        zp = (xp - mu) / div
        return zc.T, zp.T, self.YT[s][cal], self.YT[s][pro], bool((sd <= 0).any())

    def fit_cell(self, atoms, s, bn):
        """DEVELOPMENT_RELATION_OLS_V1 on one cell. Returns (nrmse, coef, kappa)."""
        Z, Zp, yc, yp, degenerate = self.cell_arrays(atoms, s, bn)
        sv = np.linalg.svd(Z, compute_uv=False)
        kappa = np.inf if sv[-1] <= 0 else float(sv[0] / sv[-1])

        X = np.column_stack([np.ones(Z.shape[0]), Z])
        beta, *_ = np.linalg.lstsq(X, yc, rcond=None)
        pred = np.column_stack([np.ones(Zp.shape[0]), Zp]) @ beta
        scale = float(np.std(yc, ddof=0))
        nrmse = float(np.sqrt(np.mean((yp - pred) ** 2)) / scale) if scale > 0 else np.inf
        return nrmse, beta[1:], kappa, degenerate

    def candidate_profile(self, atoms):
        """Full 60-cell profile: nrmse, kappa summaries, ACTIVE_TERMS."""
        m = len(atoms)
        nr = np.empty((20, 3))
        lk = np.empty((20, 3))
        active = np.zeros(m, bool)
        n_deg = 0
        for i, s in enumerate(self.dev):
            for j, (bn, _, _) in enumerate(BLOCKS):
                v, coef, kappa, deg = self.fit_cell(atoms, s, bn)
                nr[i, j] = v
                lk[i, j] = np.log10(kappa)
                active |= (coef != 0.0)
                n_deg += int(deg)
        L = lk.reshape(-1)
        return {
            "nrmse": nr,
            "log10_kappa_cells": lk,
            "COND_MEDIAN": float(np.median(L)),
            "COND_P90": float(np.percentile(L, 90, method="linear")),
            "COND_MAX": float(L.max()),
            "n_infinite_cells": int(np.isinf(L).sum()),
            "ACTIVE_TERMS": int(active.sum()),
            "support_size": m,
            "n_degenerate_sd_cells": n_deg,
        }

    def cond_summary(self, atoms, cell_mask=None):
        """Cheap path: conditioning only, optionally over a cell subset."""
        L = np.empty((20, 3))
        for i, s in enumerate(self.dev):
            for j, (bn, _, _) in enumerate(BLOCKS):
                Z, _, _, _, _ = self.cell_arrays(atoms, s, bn)
                sv = np.linalg.svd(Z, compute_uv=False)
                L[i, j] = np.inf if sv[-1] <= 0 else np.log10(sv[0] / sv[-1])
        return L
