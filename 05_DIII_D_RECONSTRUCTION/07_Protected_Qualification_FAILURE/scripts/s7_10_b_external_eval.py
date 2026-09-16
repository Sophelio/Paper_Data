"""S7.10 step B - FIRST EXTERNAL ACCESS and evaluation.

Refuses to run unless the preflight verdict is PREFLIGHT_PASSED.
Records FIRST_EXTERNAL_VALUE_ACCESS at the moment the first external archive is
opened, and asserts it is strictly after the PRE_EXTERNAL_MODEL_FREEZE stamp.

Evaluates, on identical scored samples: the frozen relational representation
C_dev_star and the six frozen comparators B0, B1, B1A, B2, B3, H0.
Nothing frozen is altered. No hyperparameter is tuned.
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
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
EX = S7.parent
S72 = S7 / "02_reconstruction_contract"
S73 = S7 / "03_target_feasibility_and_boundary" / "reconciliation_source_resolution"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S77 = S7 / "07_search_policy_and_frontier"
S79 = S7 / "09_development_selection_and_freeze"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

TARGET = "density"
BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
ETA_MIN = 0.05
B3_SEED = 2026090502
METHODS = ["REL", "B0", "B1", "B1A", "B2", "B3", "H0"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def depth_split(s: str) -> list:
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "|" and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur)); return out


def std_design(xc, xp):
    """Calibration-only standardization; sd<=0 -> divisor exactly 1.0."""
    mu = xc.mean(axis=1, keepdims=True)
    sd = xc.std(axis=1, ddof=0, keepdims=True)
    div = np.where(sd <= 0, 1.0, sd)
    return ((xc - mu) / div).T, ((xp - mu) / div).T


def ols_predict(Zc, Zp, yc):
    X = np.column_stack([np.ones(Zc.shape[0]), Zc])
    beta, *_ = np.linalg.lstsq(X, yc, rcond=None)
    return np.column_stack([np.ones(Zp.shape[0]), Zp]) @ beta, beta


def ridge_predict(Zc, Zp, yc, alpha):
    ybar = float(yc.mean())
    G = Zc.T @ Zc + alpha * np.eye(Zc.shape[1])
    b = np.linalg.solve(G, Zc.T @ (yc - ybar))
    return ybar + Zp @ b


def main() -> int:
    pf = json.loads((OUT / "manifests" / "PREFLIGHT.json").read_text(encoding="utf-8"))
    if pf["verdict"] != "PREFLIGHT_PASSED":
        raise SystemExit("STOP: preflight did not pass")
    pre_stamp = pf["pre_external_freeze"]["frozen_utc"]

    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text(encoding="utf-8"))
    atoms = sel["canonical_coordinate_ids"]
    assert atoms == depth_split(sel["support_id"]) and len(atoms) == 12

    # ---- registries (metadata only) -------------------------------------
    AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
        "signal_index").reset_index(drop=True)
    P_ALL = list(HB.primitive_id)
    P_DOT = [s for s in P_ALL if bool(
        HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    row_of = {c: k for k, c in enumerate(AT.coordinate_id)}
    OPC = {"C0": 0, "C1": 0, "C5": 1, "C2": 2, "C6": 2, "C3": 3, "C7": 3}
    plan = {}
    for c, ops, cons in zip(AT.coordinate_id, AT.ordered_operands, AT.constructor):
        if c not in atoms:
            continue
        o = str(ops).split("|")
        a_kind, a_idx = (1, di[o[0]]) if cons in ("C1", "C7") else (0, li[o[0]])
        b_kind = b_idx = None
        if cons in ("C2", "C3", "C7"):
            b_kind, b_idx = 0, li[o[1]]
        elif cons == "C6":
            b_kind, b_idx = 1, di[o[1]]
        plan[c] = (OPC[cons], a_kind, a_idx, b_kind, b_idx, cons, o)
    assert len(plan) == 12

    # denominators required by C_dev_star (level denominators)
    denoms = {}
    for c in atoms:
        op, ak, ai, bk, bi, cons, o = plan[c]
        if cons == "C3":
            denoms.setdefault(o[1], []).append(c)
        elif cons == "C5":
            denoms.setdefault(o[0], []).append(c)
    assert sorted(denoms) == ["cerqtit10", "ece22", "prmtan_neped"]

    b78 = pd.read_csv(S73 / "corrected_selected_target_boundary.csv")
    P78 = sorted(b78[b78.include_primary == True].signal.tolist())
    P70 = sorted(json.loads((S75H / "hardened_raw_ablation.json").read_text())["primitive_levels"])
    idx70 = np.array([P78.index(p) for p in P70])
    assert len(P78) == 78 and len(P70) == 70

    part = json.loads((S72 / "COHORT_PARTITION.json").read_text(encoding="utf-8"))
    ext = [str(s) for s in part["external"]["shot_ids"]]
    dev = set(str(s) for s in part["development"]["shot_ids"])
    assert len(ext) == 42
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")
    era = {s: str(TR.loc[s, "processing_era"]) for s in ext}
    assert sum(1 for s in ext if era[s] == "earlier") == 24
    assert sum(1 for s in ext if era[s] == "later") == 18

    # ================= FIRST EXTERNAL VALUE ACCESS =======================
    first_access = datetime.now(timezone.utc).isoformat()
    assert pre_stamp < first_access, "FIREWALL_ORDERING_FAILURE"
    (OUT / "manifests" / "FIRST_EXTERNAL_ACCESS.json").write_text(json.dumps({
        "pre_external_model_freeze_utc": pre_stamp,
        "first_external_value_access_utc": first_access,
        "ordering_strict": pre_stamp < first_access,
        "cohort": "the 42 frozen external discharges",
        "development_shots_touched_here": 0,
    }, indent=2), encoding="utf-8")
    print("PRE_EXTERNAL_MODEL_FREEZE : %s" % pre_stamp)
    print("FIRST_EXTERNAL_ACCESS     : %s" % first_access)

    t0 = time.time()
    block_rows, denom_rows, access_rows = [], [], []
    coef_norm = []

    for si, s in enumerate(ext):
        if s in dev:
            raise SystemExit("STOP: FIREWALL_BREACH - development shot in external loop")
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
            R = np.empty((78, n))
            for k, sig in enumerate(P78):
                tt, vv = PROV._load_signal(a, sig)
                R[k] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                    str(PROV.SIGNAL_UNIT[sig]), 1.0)
            tt, vv = PROV._load_signal(a, TARGET)
            y = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                str(PROV.SIGNAL_UNIT[TARGET]), 1.0)
        D = np.empty((63, n))
        for k, sig in enumerate(P_DOT):
            D[k] = np.gradient(L[li[sig]], tsec, edge_order=2)
        access_rows.append({"stage": "S7.10", "shot_id": s, "cohort": "external",
                            "era": era[s], "predictor_signals_read": 78,
                            "target_values_read": int(n),
                            "reason": "frozen external validation"})

        def realise(cid, sl):
            op, ak, ai, bk, bi, cons, o = plan[cid]
            A = (L[ai] if ak == 0 else D[ai])[sl]
            if op == 0:
                return A.copy()
            if op == 1:
                with np.errstate(divide="ignore", invalid="ignore"):
                    return 1.0 / A
            B = (L[bi] if bk == 0 else D[bi])[sl]
            if op == 2:
                return A * B
            with np.errstate(divide="ignore", invalid="ignore"):
                return A / B

        for bn, c1, c2 in BLOCKS:
            cal = slice(0, int(np.floor(n * c1)))
            pro = slice(int(np.floor(n * c1)), int(np.floor(n * c2)))
            yc, yp = y[cal], y[pro]
            scale = float(np.std(yc, ddof=0))

            # ---- frozen external domain rule, on the CALIBRATION block ---
            dom_ok, dom_fail = True, []
            for dname, users in sorted(denoms.items()):
                d = L[li[dname]][cal]
                finite = bool(np.isfinite(d).all())
                rms = float(np.sqrt(np.mean(d ** 2))) if finite else float("nan")
                sgn = (bool(np.all(d > 0) or np.all(d < 0)) if finite else False)
                eta = float(np.min(np.abs(d)) / rms) if (finite and rms > 0) else float("nan")
                ok = finite and rms > 0 and sgn and eta >= ETA_MIN
                reasons = []
                if not finite:
                    reasons.append("E_DENOM_NONFINITE")
                if finite and not rms > 0:
                    reasons.append("E_DENOM_RMS_ZERO")
                if finite and rms > 0 and not sgn:
                    reasons.append("E_DENOM_SIGN_CHANGE")
                if finite and rms > 0 and sgn and eta < ETA_MIN:
                    reasons.append("E_DENOM_ETA_BELOW_0.05")
                denom_rows.append({
                    "shot_id": s, "era": era[s], "block": bn, "denominator": dname,
                    "used_by": "|".join(users), "finite": finite, "rms": rms,
                    "no_sign_change": sgn, "eta": eta, "eta_threshold": ETA_MIN,
                    "admissible": ok, "failure_reasons": ";".join(reasons),
                })
                if not ok:
                    dom_ok = False
                    dom_fail.append("%s:%s" % (dname, ";".join(reasons)))

            row = {"shot_id": s, "era": era[s], "block": bn,
                   "n_calibration": int(cal.stop - cal.start),
                   "n_protected": int(pro.stop - pro.start),
                   "scale": scale,
                   "scale_valid": scale > 0,
                   "y_protected_finite": bool(np.isfinite(yp).all()),
                   "relational_applicable": dom_ok,
                   "domain_failure": ";".join(dom_fail) if dom_fail else "",
                   }

            preds = {}
            # ---- REL -------------------------------------------------
            rel_nonfinite = False
            if dom_ok:
                Xc = np.vstack([realise(c, cal) for c in atoms])
                Xp = np.vstack([realise(c, pro) for c in atoms])
                if not (np.isfinite(Xc).all() and np.isfinite(Xp).all()):
                    rel_nonfinite = True
                else:
                    Zc, Zp = std_design(Xc, Xp)
                    p, beta = ols_predict(Zc, Zp, yc)
                    preds["REL"] = p
                    coef_norm.append({"shot_id": s, "block": bn,
                                      "intercept": float(beta[0]),
                                      "coef_l2_norm": float(np.linalg.norm(beta[1:]))})
            row["relational_nonfinite_construction"] = rel_nonfinite
            if rel_nonfinite:
                row["relational_applicable"] = False
                row["domain_failure"] = (row["domain_failure"] + ";" if row["domain_failure"] else "") \
                                        + "E_NONFINITE_COORDINATE_CONSTRUCTION"

            # ---- baselines (always computed; eligibility decided later) --
            preds["B0"] = np.full(yp.shape, float(yc.mean()))
            preds["B1"] = np.full(yp.shape, float(yc[-1]))
            X1 = np.column_stack([np.ones(yc.size - 1), yc[:-1]])
            ab, *_ = np.linalg.lstsq(X1, yc[1:], rcond=None)
            a_, phi_ = float(ab[0]), float(ab[1])
            rec, prev = np.empty(yp.size), float(yc[-1])
            for k in range(yp.size):
                prev = a_ + phi_ * prev
                rec[k] = prev
            preds["B1A"] = rec
            row["B1A_a"], row["B1A_phi"] = a_, phi_

            Zc78, Zp78 = std_design(R[:, cal], R[:, pro])
            preds["B2"] = ridge_predict(Zc78, Zp78, yc, 1.0)
            preds["H0"] = ridge_predict(Zc78[:, idx70], Zp78[:, idx70], yc, 1.0)
            g = HistGradientBoostingRegressor(random_state=B3_SEED)
            g.fit(Zc78, yc)
            preds["B3"] = g.predict(Zp78)

            for m in METHODS:
                p = preds.get(m)
                if p is None:
                    row["%s_rmse" % m] = np.nan
                    row["%s_nrmse" % m] = np.nan
                    row["%s_mse" % m] = np.nan
                    row["%s_finite" % m] = False
                    continue
                fin = bool(np.isfinite(p).all())
                mse = float(np.mean((yp - p) ** 2)) if fin else np.nan
                rmse = float(np.sqrt(mse)) if fin else np.nan
                row["%s_rmse" % m] = rmse
                row["%s_mse" % m] = mse
                row["%s_nrmse" % m] = (rmse / scale) if (fin and scale > 0) else np.nan
                row["%s_finite" % m] = fin
            block_rows.append(row)
        if (si + 1) % 10 == 0:
            print("  %d/42 discharges (%.0fs)" % (si + 1, time.time() - t0))

    bm = pd.DataFrame(block_rows)

    # ---- common support / block eligibility ------------------------------
    all_finite = np.ones(len(bm), bool)
    for m in METHODS:
        all_finite &= bm["%s_finite" % m].values
    bm["all_methods_finite"] = all_finite
    bm["comparison_eligible"] = (bm.scale_valid & bm.y_protected_finite
                                 & bm.relational_applicable & bm.all_methods_finite)
    bm["ineligible_reason"] = np.where(
        bm.comparison_eligible, "",
        np.where(~bm.scale_valid, "INVALID_FOR_NORMALIZED_SCORING",
        np.where(~bm.y_protected_finite, "NONFINITE_PROTECTED_TARGET",
        np.where(~bm.relational_applicable, "RELATIONAL_REPRESENTATION_NOT_APPLICABLE",
                 "NONFINITE_METHOD_PREDICTION"))))
    bm.to_csv(OUT / "external_block_metrics.csv", index=False)
    pd.DataFrame(denom_rows).to_csv(OUT / "external_denominator_audit.csv", index=False)

    # ---- discharge-level aggregation over eligible blocks ---------------
    rows = []
    for s in ext:
        sub = bm[(bm.shot_id == s) & bm.comparison_eligible]
        r = {"shot_id": s, "era": era[s], "n_eligible_blocks": int(len(sub)),
             "blocks": "".join(sorted(sub.block.tolist())),
             "evaluable": len(sub) > 0}
        for m in METHODS:
            r["%s_nrmse" % m] = float(sub["%s_nrmse" % m].mean()) if len(sub) else np.nan
            r["%s_mse" % m] = float(sub["%s_mse" % m].mean()) if len(sub) else np.nan
            r["%s_rmse" % m] = float(sub["%s_rmse" % m].mean()) if len(sub) else np.nan
        if len(sub):
            den = r["B1_mse"]
            r["S_pers_REL"] = (1.0 - r["REL_mse"] / den) if den > 0 else np.nan
            r["S_pers_undefined"] = not (den > 0)
        else:
            r["S_pers_REL"], r["S_pers_undefined"] = np.nan, True
        rows.append(r)
    dm = pd.DataFrame(rows)
    dm.to_csv(OUT / "external_discharge_metrics.csv", index=False)

    # ---- common support audit -------------------------------------------
    cs = []
    for _, r in bm.iterrows():
        cs.append({"shot_id": r.shot_id, "era": r.era, "block": r.block,
                   "n_protected_rows": r.n_protected,
                   "identical_rows_across_methods": True,
                   "scored_by_REL": bool(r.relational_applicable and r.REL_finite),
                   "scored_by_all_baselines": bool(all(r["%s_finite" % m] for m in METHODS[1:])),
                   "comparison_eligible": bool(r.comparison_eligible),
                   "ineligible_reason": r.ineligible_reason})
    pd.DataFrame(cs).to_csv(OUT / "common_support_audit.csv", index=False)

    (OUT / "manifests" / "EXTERNAL_ACCESS_LOG.json").write_text(json.dumps({
        "first_external_value_access_utc": first_access,
        "pre_external_model_freeze_utc": pre_stamp,
        "ordering_strict": pre_stamp < first_access,
        "n_external_discharges_opened": len(ext),
        "n_development_discharges_opened": 0,
        "reads": access_rows,
        "runtime_seconds": round(time.time() - t0, 1),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__,
                        "platform": platform.platform()},
    }, indent=2), encoding="utf-8")
    pd.DataFrame(coef_norm).to_csv(OUT / "manifests" / "relational_local_coefficients.csv", index=False)

    ne = int((~bm.comparison_eligible).sum())
    print("blocks: %d total, %d eligible, %d ineligible" % (len(bm), len(bm) - ne, ne))
    if ne:
        print(bm[~bm.comparison_eligible].ineligible_reason.value_counts().to_string())
    print("discharges evaluable: %d/42" % int(dm.evaluable.sum()))
    print("\nmean external NRMSE over evaluable discharges:")
    for m in METHODS:
        print("   %-4s %.6f" % (m, dm[dm.evaluable]["%s_nrmse" % m].mean()))
    print("runtime %.0fs" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
