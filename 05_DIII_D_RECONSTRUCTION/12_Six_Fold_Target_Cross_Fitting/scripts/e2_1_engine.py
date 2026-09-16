"""S7.E2.1 - execution engine.

Data vault with an auditable target-access ledger, the frozen SIGMA_REC one-seed
search adapted mechanically to the common basis, the frozen U_rec selection, the
frozen relation estimator and the six frozen baselines.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

S7 = Path(__file__).resolve().parents[2]
EX = S7.parent
DATA = EX / "data" / "resampled_data_v6"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S72 = S7 / "02_reconstruction_contract"
S73 = S7 / "03_target_feasibility_and_boundary" / "reconciliation_source_resolution"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S77 = S7 / "07_search_policy_and_frontier"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

TARGET = "density"
BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
EPS = np.finfo(np.float64).eps
FLOOR = 0.01
SUPPORT_MAX = 12
CAP = 96
BOOT_SEED = 2026090501
NREP = 1000
B3_SEED = 2026090502
ALPHA = 1.0


class Vault:
    """Predictors are open. Target access is gated and logged."""

    def __init__(self):
        self.log = []
        self._open_cal = set()
        self._open_pro = set()

    def allow_calibration(self, shots):
        self._open_cal |= set(shots)
        self.log.append({"utc": datetime.now(timezone.utc).isoformat(),
                         "action": "OPEN_CALIBRATION_TARGETS", "n_shots": len(shots)})

    def allow_protected(self, shots):
        self._open_pro |= set(shots)
        self.log.append({"utc": datetime.now(timezone.utc).isoformat(),
                         "action": "OPEN_PROTECTED_TARGETS", "n_shots": len(shots)})

    def check(self, shot, kind):
        ok = shot in (self._open_cal if kind == "cal" else self._open_pro)
        if not ok:
            raise SystemExit("FIREWALL: %s target of %s not open" % (kind, shot))


class Engine:
    def __init__(self, vault: Vault):
        self.v = vault
        AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
        HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
            "signal_index").reset_index(drop=True)
        self.P_ALL = list(HB.primitive_id)
        self.P_DOT = [s for s in self.P_ALL if bool(
            HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
        li = {s: k for k, s in enumerate(self.P_ALL)}
        di = {s: k for k, s in enumerate(self.P_DOT)}
        self.AT = AT
        self.ORIG = list(AT.coordinate_id)
        self.row_of = {c: k for k, c in enumerate(self.ORIG)}
        self.cons_of = dict(zip(AT.coordinate_id, AT.constructor))
        self.strata_of = dict(zip(AT.coordinate_id, AT.search_stratum))
        FULL = pd.read_csv(S76R / "primary_atomic_coordinate_universe.csv")
        fam = dict(zip(HB.primitive_id, HB.broad_scientific_family))
        self.anc_of = {c: sorted({fam[a] for a in str(s).split("|")})
                       for c, s in zip(FULL.coordinate_id, FULL.primitive_ancestors)}
        self.prim_of = {c: str(s).split("|") for c, s in
                        zip(FULL.coordinate_id, FULL.primitive_ancestors)}
        DEP = pd.read_csv(S76R / "exact_dependency_groups.csv")
        self.BINDING = ([set(str(r.aggregate_coordinate).split("|")
                             + str(r.component_coordinates).split("|"))
                         for r in DEP.itertuples()] if len(DEP) else [])

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
        self.shots = [str(s) for s in part["development"]["shot_ids"]] + \
                     [str(s) for s in part["external"]["shot_ids"]]
        b78 = pd.read_csv(S73 / "corrected_selected_target_boundary.csv")
        self.P78 = sorted(b78[b78.include_primary == True].signal.tolist())
        self.P70 = sorted(json.loads((S75H / "hardened_raw_ablation.json").read_text())
                          ["primitive_levels"])
        self.idx70 = np.array([self.P78.index(p) for p in self.P70])

        TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")
        self.era = {s: str(TR.loc[s, "processing_era"]) for s in self.shots}
        self.LEV, self.DER, self.RAW, self._Y, self.SLC = {}, {}, {}, {}, {}
        for s in self.shots:
            t0 = float(TR.loc[s, "t_start_s"]) * 1000.0
            dtm = float(TR.loc[s, "delta_t_ms"]); n = int(TR.loc[s, "N_s"])
            grid = t0 + dtm * np.arange(n, dtype=np.float64)
            tsec = grid / 1000.0
            with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
                L = np.empty((70, n))
                for k, sig in enumerate(self.P_ALL):
                    tt, vv = PROV._load_signal(a, sig)
                    L[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                        str(PROV.SIGNAL_UNIT[sig]), 1.0)
                R = np.empty((78, n))
                for k, sig in enumerate(self.P78):
                    tt, vv = PROV._load_signal(a, sig)
                    R[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                        str(PROV.SIGNAL_UNIT[sig]), 1.0)
                tt, vv = PROV._load_signal(a, TARGET)
                y = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                    str(PROV.SIGNAL_UNIT[TARGET]), 1.0)
            D = np.empty((63, n))
            for k, sig in enumerate(self.P_DOT):
                D[k] = np.gradient(L[li[sig]], tsec, edge_order=2)
            self.LEV[s], self.DER[s], self.RAW[s], self._Y[s] = L, D, R, y
            for bn, c1, c2 in BLOCKS:
                self.SLC[(s, bn)] = (slice(0, int(np.floor(n * c1))),
                                     slice(int(np.floor(n * c1)), int(np.floor(n * c2))))

    # ---- gated target access -------------------------------------------
    def ycal(self, s, bn):
        self.v.check(s, "cal")
        return self._Y[s][self.SLC[(s, bn)][0]]

    def ypro(self, s, bn):
        self.v.check(s, "pro")
        return self._Y[s][self.SLC[(s, bn)][1]]

    def realise(self, rows, s):
        L, D = self.LEV[s], self.DER[s]
        n = L.shape[1]

        def gather(kind, idx):
            g = np.empty((idx.size, n)); lv = kind == 0
            if lv.any(): g[lv] = L[idx[lv]]
            if (~lv).any(): g[~lv] = D[idx[~lv]]
            return g

        A = gather(self.kA[rows], self.iA[rows]); o = self.op[rows]
        out = np.empty_like(A)
        with np.errstate(divide="ignore", invalid="ignore"):
            m0 = o == 0; out[m0] = A[m0]
            m1 = o == 1
            if m1.any(): out[m1] = 1.0 / A[m1]
            if (o >= 2).any():
                B = gather(self.kB[rows], self.iB[rows]); m2, m3 = o == 2, o == 3
                out[m2] = A[m2] * B[m2]; out[m3] = A[m3] / B[m3]
        return out

    # ---- frozen relation estimator (DEVELOPMENT_RELATION_OLS_V1) --------
    def fit_cell(self, atoms, s, bn, need_pro=True):
        rows = np.array([self.row_of[a] for a in atoms])
        cal, pro = self.SLC[(s, bn)]
        V = self.realise(rows, s)
        xc, xp = V[:, cal], V[:, pro]
        mu = xc.mean(axis=1, keepdims=True)
        sd = xc.std(axis=1, ddof=0, keepdims=True)
        div = np.where(sd <= 0, 1.0, sd)
        Zc, Zp = ((xc - mu) / div).T, ((xp - mu) / div).T
        yc = self.ycal(s, bn)
        X = np.column_stack([np.ones(Zc.shape[0]), Zc])
        beta, *_ = np.linalg.lstsq(X, yc, rcond=None)
        pred = np.column_stack([np.ones(Zp.shape[0]), Zp]) @ beta
        scale = float(np.std(yc, ddof=0))
        sv = np.linalg.svd(Zc, compute_uv=False)
        kappa = np.inf if sv[-1] <= 0 else float(sv[0] / sv[-1])
        return pred, scale, beta, kappa

    def score_cell(self, atoms, s, bn):
        pred, scale, beta, kappa = self.fit_cell(atoms, s, bn)
        yp = self.ypro(s, bn)
        rmse = float(np.sqrt(np.mean((yp - pred) ** 2)))
        return {"rmse": rmse, "nrmse": rmse / scale if scale > 0 else np.inf,
                "mse": rmse ** 2, "scale": scale, "kappa": kappa,
                "active": int((beta[1:] != 0.0).sum())}

    # ---- baselines, exactly as frozen -----------------------------------
    def baselines(self, s, bn):
        cal, pro = self.SLC[(s, bn)]
        yc, yp = self.ycal(s, bn), self.ypro(s, bn)
        out = {}
        out["B0"] = np.full(yp.shape, float(yc.mean()))
        out["B1"] = np.full(yp.shape, float(yc[-1]))
        X1 = np.column_stack([np.ones(yc.size - 1), yc[:-1]])
        ab, *_ = np.linalg.lstsq(X1, yc[1:], rcond=None)
        a_, phi_ = float(ab[0]), float(ab[1])
        rec, prev = np.empty(yp.size), float(yc[-1])
        for k in range(yp.size):
            prev = a_ + phi_ * prev
            rec[k] = prev
        out["B1A"] = rec
        R = self.RAW[s]
        xc, xp = R[:, cal], R[:, pro]
        mu = xc.mean(axis=1, keepdims=True)
        sd = xc.std(axis=1, ddof=0, keepdims=True)
        div = np.where(sd <= 0, 1.0, sd)
        Zc, Zp = ((xc - mu) / div).T, ((xp - mu) / div).T
        ybar = float(yc.mean())
        for name, cols in (("B2", slice(None)), ("H0", self.idx70)):
            Zc2 = Zc[:, cols] if name == "B2" else Zc[:, cols]
            Zp2 = Zp[:, cols] if name == "B2" else Zp[:, cols]
            G = Zc2.T @ Zc2 + ALPHA * np.eye(Zc2.shape[1])
            b = np.linalg.solve(G, Zc2.T @ (yc - ybar))
            out[name] = ybar + Zp2 @ b
        g = HistGradientBoostingRegressor(random_state=B3_SEED)
        g.fit(Zc, yc)
        out["B3"] = g.predict(Zp)
        scale = float(np.std(yc, ddof=0))
        return {k: {"nrmse": float(np.sqrt(np.mean((yp - p) ** 2)) / scale),
                    "mse": float(np.mean((yp - p) ** 2))} for k, p in out.items()}
