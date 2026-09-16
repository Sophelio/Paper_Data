"""S7.6R stage B - regenerate the hardened symbolic universe and qualify it.

Opens DEVELOPMENT PREDICTOR values only, and only the 70 hardened primitives.
Never the target, never external.

Every coordinate signature is regenerated from P_hard + G_REC_DENSITY_HARDENED_V2.
Nothing is imported from the historical S7.6 V1 registry.

Evaluation order is the frozen P_rec order B / A / C / G / F / D / E / H. For the
five partial-map families the denominator predicate is evaluated on the
DENOMINATOR PRIMITIVE first, because the constructed coordinate does not exist
as a real-valued function on a block where its denominator is singular; class D
is then applied to the constructed coordinate. That is the frozen S7.6 method,
unchanged.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S76R = HERE.parent
S76 = S76R.parent
S7 = S76.parent
EX = S7.parent
S72 = S7 / "02_reconstruction_contract"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
MAN = S76R / "manifests"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

TARGET = "density"
BLOCKS = [("A", 0.40), ("B", 0.60), ("C", 0.80)]   # calibration upper edges
MIN_CAL = 30
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4,
         "kW": 1e3}
BEAMS = [f"pinj_{b}" for b in ("15l", "15r", "21l", "21r", "30l", "30r",
                               "33l", "33r")]
AGG = "pinj"
ACCESS: list[dict] = []


def denom_audit(d: np.ndarray, eta_min: float):
    """The frozen primary denominator rule, byte-identical in behaviour to the
    S7.6 implementation. Returns (ok, reason, eta, rms)."""
    if not np.all(np.isfinite(d)):
        return False, "E_DENOM_NONFINITE", np.nan, np.nan
    rms = float(np.sqrt(np.mean(d ** 2)))
    if rms == 0.0:
        return False, "E_DENOM_RMS_ZERO", np.nan, 0.0
    pos, neg = bool(np.any(d > 0)), bool(np.any(d < 0))
    if pos and neg:
        return False, "E_DENOM_SIGN_CHANGE", float(np.min(np.abs(d)) / rms), rms
    if np.any(d == 0.0):
        return False, "E_DENOM_ZERO_VALUE", 0.0, rms
    eta = float(np.min(np.abs(d)) / rms)
    if eta < eta_min:
        return False, "E_DENOM_MARGIN_BELOW_ETA", eta, rms
    return True, "", eta, rms


def main() -> None:
    par = json.loads((MAN / "PARENT_FREEZE_VERIFICATION.json").read_text())
    if par["verdict"] != "PARENTS_VERIFIED":
        raise SystemExit("STOP: run stage A first")
    dv = json.loads((MAN / "DENOMINATOR_RULE_VERIFICATION.json").read_text())
    if not dv["hash_verified_unchanged"]:
        raise SystemExit("STOP: denominator rule hash mismatch")
    rule = json.loads((S76 / "denominator_admissibility_rule.json").read_text())
    ETA = float(rule["DENOMINATOR_MARGIN_PRIMARY"])
    assert ETA == 0.05

    G = json.loads((S75H / "G_REC_HARDENED.json").read_text())
    H = pd.read_csv(S75H / "primitive_basis_hardened.csv")
    P75 = pd.read_csv(S75 / "primitive_type_registry.csv")
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = list(part["development"]["shot_ids"])
    ext = set(part["external"]["shot_ids"])
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str})
    TRd = TR[TR.cohort == "development"].set_index("discharge")

    # ---- operand sets, straight from the hardened basis --------------------
    H = H.sort_values("signal_index").reset_index(drop=True)
    prim = list(H.primitive_id)
    assert TARGET not in prim and len(prim) == 70
    idx = dict(zip(H.primitive_id, H.signal_index.astype(int)))
    unit = dict(zip(H.primitive_id, H.canonical_unit.fillna("")))
    fam = dict(zip(H.primitive_id, H.broad_scientific_family))
    alias = dict(zip(H.primitive_id, H.aliasing_flag))
    upsm = dict(zip(H.primitive_id, H.upstream_upsampled_flag))
    uncal = dict(zip(H.primitive_id, H.uncalibrated_flag))
    e_dot = dict(zip(H.primitive_id, H.derivative_primary_eligible))
    e_typ = dict(zip(H.primitive_id, H.product_ratio_operand_eligible))
    dimx = dict(zip(P75.primitive_id, P75.dimension_expression))
    dtmax = dict(zip(P75.primitive_id, P75.source_supported_dt_max_ms))
    sensonly = dict(zip(P75.primitive_id, P75.derivative_sensitivity_only))

    P_ALL = prim                                                    # 70
    P_DOT = [s for s in prim if e_dot[s]]                           # 63
    P_TYP = [s for s in prim if e_typ[s]]                           # 68
    SENS = [s for s in prim if bool(sensonly[s])]                   # 5
    assert (len(P_ALL), len(P_DOT), len(P_TYP)) == (70, 63, 68)
    assert G["operand_counts"] == {"M": 70, "Mt": 68, "Md": 63}

    # ---- 7/8. symbolic enumeration, regenerated from scratch ---------------
    reg = []

    def add(cid, f, ops, roles, dim, uexpr, dom, temporal):
        anc = sorted(set(ops))
        reg.append({
            "coordinate_id": cid, "constructor": f,
            "ordered_operands": "|".join(ops), "operand_roles": "|".join(roles),
            "primitive_ancestors": "|".join(anc), "n_ancestors": len(anc),
            "depth": 0 if f == "C0" else 1,
            "output_dimension": dim, "unit_expression": uexpr,
            "temporal_resolution_rule": temporal,
            "temporal_resolution_bound_ms": max(dtmax[o] for o in anc),
            "provenance_lineage": "|".join(f"{o}:{fam[o]}" for o in anc),
            "target_independence": "TRANSITIVE_FROM_TARGET_INDEPENDENT_BOUNDARY",
            "aliasing_flag": any(bool(alias[o]) for o in anc),
            "upsample_flag": any(bool(upsm[o]) for o in anc),
            "uncalibrated_flag": any(bool(uncal[o]) for o in anc),
            "primary_or_sensitivity": "PRIMARY",
            "numerical_realization_id": ("FD2_PHYSICAL_TIME_V1"
                                         if f in ("C1", "C4", "C6", "C7", "C8")
                                         else "NONE"),
            "domain_predicate": dom,
        })

    INH = "inherit"
    DER = "inherit+DERIVED_FROM_NUMERICAL_REALIZATION"
    CO = "coarser_of_operands"
    COD = "coarser_of_operands+DERIVED_FROM_NUMERICAL_REALIZATION"

    for s in P_ALL:
        add(f"ID({s})", "C0", [s], ["level"], dimx[s],
            unit[s] or "UNCALIBRATED", "", INH)
    for s in P_DOT:
        add(f"DOT({s})", "C1", [s], ["rate"], f"({dimx[s]}) T^-1",
            f"{unit[s]}/s", "", DER)
    c2_pairs = [(i, j) for i, j in combinations(P_TYP, 2)] + [(x, x) for x in P_TYP]
    c2_pairs = [((i, j) if idx[i] <= idx[j] else (j, i)) for i, j in c2_pairs]
    c2_pairs.sort(key=lambda p: (idx[p[0]], idx[p[1]]))
    for i, j in c2_pairs:
        add(f"PROD({i},{j})", "C2", [i, j], ["level", "level"],
            f"({dimx[i]})*({dimx[j]})", f"{unit[i]}*{unit[j]}", "", CO)
    c3_all = [(i, j) for i in P_TYP for j in P_TYP if i != j]
    for i, j in c3_all:
        add(f"RATIO({i},{j})", "C3", [i, j], ["level", "level_denominator"],
            f"({dimx[i]})/({dimx[j]})", f"{unit[i]}/{unit[j]}",
            "DOMAIN_DENOMINATOR_LEVEL_NONZERO", CO)
    c4_all = [(i, j) for i in P_DOT for j in P_DOT if i != j]
    for i, j in c4_all:
        add(f"PHASE({i}|{j})", "C4", [i, j], ["rate", "rate_denominator"],
            f"({dimx[i]})/({dimx[j]})", f"{unit[i]}/{unit[j]}",
            "DOMAIN_DENOMINATOR_RATE_NONZERO", COD)
    for i in P_TYP:
        add(f"RECIP({i})", "C5", [i], ["level_denominator"],
            f"({dimx[i]})^-1", f"1/({unit[i]})",
            "DOMAIN_DENOMINATOR_LEVEL_NONZERO", INH)
    c6_all = [(i, j) for i in P_TYP for j in P_DOT]
    for i, j in c6_all:
        add(f"LEVEL_RATE({i}|{j})", "C6", [i, j], ["level", "rate"],
            f"({dimx[i]})*({dimx[j]}) T^-1", f"{unit[i]}*{unit[j]}/s", "", COD)
    c7_all = [(i, j) for i in P_DOT for j in P_TYP]
    for i, j in c7_all:
        u = "1/s" if i == j else f"{unit[i]}/({unit[j]}*s)"
        d = "T^-1" if i == j else f"({dimx[i]})/({dimx[j]}) T^-1"
        add(f"RATE_OVER_LEVEL({i}|{j})", "C7", [i, j],
            ["rate", "level_denominator"], d, u,
            "DOMAIN_DENOMINATOR_LEVEL_NONZERO", COD)
    c8_all = [(i, j) for i in P_TYP for j in P_DOT]
    for i, j in c8_all:
        u = "s" if i == j else f"{unit[i]}*s/({unit[j]})"
        d = "T" if i == j else f"({dimx[i]})/({dimx[j]}) T"
        add(f"LEVEL_OVER_RATE({i}|{j})", "C8", [i, j],
            ["level", "rate_denominator"], d, u,
            "DOMAIN_DENOMINATOR_RATE_NONZERO", COD)

    REG = pd.DataFrame(reg)
    counts = {c: int(n) for c, n in REG.constructor.value_counts().items()}
    EXPECT = {"C0": 70, "C1": 63, "C2": 2346, "C3": 4556, "C4": 3906,
              "C5": 68, "C6": 4284, "C7": 4284, "C8": 4284}
    assert counts == EXPECT, counts
    assert len(REG) == 23861 == G["symbolic_primary_total"]
    assert REG.coordinate_id.is_unique
    REG.to_csv(S76R / "coordinate_registry_symbolic.csv", index=False)

    pd.DataFrame([{
        "coordinate_id": f"DOT({s})", "constructor": "C1", "operands": s,
        "primitive_ancestors": s, "depth": 1,
        "output_dimension": f"({dimx[s]}) T^-1", "unit_expression": f"{unit[s]}/s",
        "primary_or_sensitivity": "SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT",
        "reason": "operand is UPSTREAM_UPSAMPLED; its derivative reports the "
                  "interpolant, not the instrument",
        "families_also_excluded_for_this_operand_in_a_rate_role":
            "C4|C6(rate)|C7(numerator rate)|C8(denominator rate)",
        "in_primary_A_rec": False, "examined_by": "S7.11"} for s in SENS]).to_csv(
        S76R / "sensitivity_only_coordinate_registry.csv", index=False)

    # ---- 10. metadata gates B / A / C / G / F -----------------------------
    prim_set, sens_set, typ_set, dot_set = (set(P_ALL), set(SENS), set(P_TYP),
                                            set(P_DOT))
    roles_of = dict(zip(REG.coordinate_id, REG.operand_roles))
    meta = []
    for r in REG.itertuples():
        ops = r.ordered_operands.split("|")
        roles = r.operand_roles.split("|")
        anc = r.primitive_ancestors.split("|")
        B_ok = all(a in prim_set for a in anc)
        A_ok = bool(r.provenance_lineage) and len(anc) >= 1
        C_ok = (r.constructor == "C0") or (not r.uncalibrated_flag)
        G_ok = bool(r.output_dimension) and bool(r.unit_expression)
        # F: any operand used in a RATE role must be primary derivative-eligible
        F_ok = all((o in dot_set and o not in sens_set)
                   for o, ro in zip(ops, roles) if "rate" in ro)
        # every operand used in a LEVEL role must be typed (or C0)
        if r.constructor != "C0":
            C_ok = C_ok and all(o in typ_set for o, ro in zip(ops, roles)
                                if "level" in ro)
        depth_ok = int(r.depth) <= 1
        first = ("B" if not B_ok else "A" if not A_ok else "C" if not C_ok
                 else "G" if not G_ok else "F" if not F_ok else "")
        meta.append({"coordinate_id": r.coordinate_id, "B": B_ok, "A": A_ok,
                     "C": C_ok, "G": G_ok, "F": F_ok, "depth_ok": depth_ok,
                     "target_absent": TARGET not in anc,
                     "first_metadata_reject": first})
    META = pd.DataFrame(meta).set_index("coordinate_id")
    assert bool(META.depth_ok.all()) and bool(META.target_absent.all())
    n_meta_rej = int((META.first_metadata_reject != "").sum())

    # ---- 11. development numerical realisations ---------------------------
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    lev, der, slices = {}, {}, {}
    for s in dev:
        if s in ext:
            raise SystemExit("STOP: FIREWALL_BREACH (external discharge)")
        t0 = float(TRd.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TRd.loc[s, "delta_t_ms"])
        n = int(TRd.loc[s, "N_s"])
        grid_ms = t0 + dtm * np.arange(n, dtype=np.float64)
        t_sec = grid_ms / 1000.0
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            L = np.empty((70, n), dtype=np.float64)
            for k, sig in enumerate(P_ALL):
                tt, vv = PROV._load_signal(a, sig)
                f = CANON.get(str(PROV.SIGNAL_UNIT[sig]), 1.0)
                L[k] = PROV._resample_to_grid(tt, vv, grid_ms) * f
        lev[s] = L
        D = np.empty((63, n), dtype=np.float64)
        for k, sig in enumerate(P_DOT):
            D[k] = np.gradient(L[li[sig]], t_sec, edge_order=2)   # FD2, physical t
        der[s] = D
        for bn, c1 in BLOCKS:
            slices[(s, bn)] = slice(0, int(np.floor(n * c1)))
        ACCESS.append({"stage": "S7.6R-B", "shot_id": s,
                       "development_or_external": "development",
                       "predictor_signals_read": 70, "target_values_read": 0,
                       "external_values_read": 0,
                       "reason": "atomic coordinate admissibility (classes D, E) "
                                 "on development calibration blocks",
                       "timestamp": datetime.now(timezone.utc).isoformat()})
    CELLS = [(s, bn) for s in dev for bn, _ in BLOCKS]
    nmin = min(slices[c].stop for c in CELLS)

    # ---- 22. denominator caches -------------------------------------------
    den_rows, den_lvl, den_rate = [], {}, {}
    for kind, names, mat, imap, tag in (
            ("level", P_TYP, lev, li, "LEVEL_DENOMINATOR_STATUS"),
            ("rate", P_DOT, der, di, "RATE_DENOMINATOR_STATUS")):
        for nm in names:
            k = imap[nm]
            ok_all, first_why = True, ""
            for s, bn in CELLS:
                d = mat[s][k, slices[(s, bn)]]
                ok, why, eta, rms = denom_audit(d, ETA)
                fin = bool(np.all(np.isfinite(d)))
                den_rows.append({
                    "table": tag, "denominator_signal": nm,
                    "denominator_type": kind, "shot_id": s, "block": bn,
                    "n_samples": int(d.size), "finite": fin,
                    "rms": rms,
                    "min_abs": float(np.min(np.abs(d))) if fin else np.nan,
                    "eta": eta,
                    "sign_change": why == "E_DENOM_SIGN_CHANGE",
                    "passes": ok, "first_failure_reason": why})
                if not ok:
                    ok_all = False
                    first_why = first_why or why
            (den_lvl if kind == "level" else den_rate)[nm] = (ok_all, first_why)
    pd.DataFrame(den_rows).to_csv(
        S76R / "denominator_conditioning_audit.csv", index=False)
    OKL = {n for n, v in den_lvl.items() if v[0]}
    OKR = {n for n, v in den_rate.items() if v[0]}

    # ---- 12. class D, streamed per family ---------------------------------
    def classD(ia, ma, ib, mb, op, nco):
        """Streaming class-D over all required (shot, block) cells."""
        fin = np.ones(nco, bool)
        con = np.zeros(nco, bool)
        gmn = np.full(nco, np.inf)
        gmx = np.full(nco, -np.inf)
        for s, bn in CELLS:
            sl = slices[(s, bn)]
            A = (lev[s] if ma == "lev" else der[s])[ia][:, sl]
            if op == "recip":
                with np.errstate(divide="ignore", invalid="ignore"):
                    v = 1.0 / A
            else:
                B = (lev[s] if mb == "lev" else der[s])[ib][:, sl]
                with np.errstate(divide="ignore", invalid="ignore"):
                    v = A * B if op == "mul" else A / B
            fin &= np.all(np.isfinite(v), axis=1)
            vmn, vmx = v.min(axis=1), v.max(axis=1)
            con |= (vmn == vmx)
            gmn = np.minimum(gmn, vmn)
            gmx = np.maximum(gmx, vmx)
        return fin, con, gmn, gmx

    def keyed(pairs, ia, ma, ib, mb, op, mk):
        if not pairs:
            return {}, (np.array([]),) * 4
        r = classD(np.array(ia), ma, (np.array(ib) if ib is not None else None),
                   mb, op, len(pairs))
        return {mk(p): k for k, p in enumerate(pairs)}, r

    def classD_unary(ia, ma, nco, op):
        fin = np.ones(nco, bool)
        con = np.zeros(nco, bool)
        gmn = np.full(nco, np.inf)
        gmx = np.full(nco, -np.inf)
        for s, bn in CELLS:
            sl = slices[(s, bn)]
            A = (lev[s] if ma == "lev" else der[s])[ia][:, sl]
            if op == "recip":
                with np.errstate(divide="ignore", invalid="ignore"):
                    v = 1.0 / A
            else:
                v = A
            fin &= np.all(np.isfinite(v), axis=1)
            vmn, vmx = v.min(axis=1), v.max(axis=1)
            con |= (vmn == vmx)
            gmn = np.minimum(gmn, vmn)
            gmx = np.maximum(gmx, vmx)
        return fin, con, gmn, gmx

    D0 = classD_unary(np.array([li[s] for s in P_ALL]), "lev", 70, "id")
    D1 = classD_unary(np.array([di[s] for s in P_DOT]), "der", 63, "id")

    c5_ops = [i for i in P_TYP if i in OKL]
    D5 = (classD_unary(np.array([li[i] for i in c5_ops]), "lev",
                       len(c5_ops), "recip") if c5_ops
          else (np.array([]),) * 4)
    K5 = {f"RECIP({i})": k for k, i in enumerate(c5_ops)}

    K2, D2 = keyed(c2_pairs, [li[i] for i, _ in c2_pairs], "lev",
                   [li[j] for _, j in c2_pairs], "lev", "mul",
                   lambda p: f"PROD({p[0]},{p[1]})")
    c3_ev = [(i, j) for i, j in c3_all if j in OKL]
    K3, D3 = keyed(c3_ev, [li[i] for i, _ in c3_ev], "lev",
                   [li[j] for _, j in c3_ev], "lev", "div",
                   lambda p: f"RATIO({p[0]},{p[1]})")
    c4_ev = [(i, j) for i, j in c4_all if j in OKR]
    K4, D4 = keyed(c4_ev, [di[i] for i, _ in c4_ev], "der",
                   [di[j] for _, j in c4_ev], "der", "div",
                   lambda p: f"PHASE({p[0]}|{p[1]})")
    K6, D6 = keyed(c6_all, [li[i] for i, _ in c6_all], "lev",
                   [di[j] for _, j in c6_all], "der", "mul",
                   lambda p: f"LEVEL_RATE({p[0]}|{p[1]})")
    c7_ev = [(i, j) for i, j in c7_all if j in OKL]
    K7, D7 = keyed(c7_ev, [di[i] for i, _ in c7_ev], "der",
                   [li[j] for _, j in c7_ev], "lev", "div",
                   lambda p: f"RATE_OVER_LEVEL({p[0]}|{p[1]})")
    c8_ev = [(i, j) for i, j in c8_all if j in OKR]
    K8, D8 = keyed(c8_ev, [li[i] for i, _ in c8_ev], "lev",
                   [di[j] for _, j in c8_ev], "der", "div",
                   lambda p: f"LEVEL_OVER_RATE({p[0]}|{p[1]})")

    KEY = {"C0": ({f"ID({s})": k for k, s in enumerate(P_ALL)}, D0),
           "C1": ({f"DOT({s})": k for k, s in enumerate(P_DOT)}, D1),
           "C2": (K2, D2), "C3": (K3, D3), "C4": (K4, D4), "C5": (K5, D5),
           "C6": (K6, D6), "C7": (K7, D7), "C8": (K8, D8)}
    DEN_ROLE = {"C3": ("level", 1), "C4": ("rate", 1), "C5": ("level", 0),
                "C7": ("level", 1), "C8": ("rate", 1)}

    # ---- assemble admissibility -------------------------------------------
    rows = []
    for r in REG.itertuples():
        cid, f = r.coordinate_id, r.constructor
        ops = r.ordered_operands.split("|")
        m = META.loc[cid]
        first = m.first_metadata_reject
        e_val = None
        finite = constant = None
        vmin = vmax = np.nan
        if not first and nmin < MIN_CAL:
            first = "D_INSUFFICIENT_CALIBRATION_SAMPLES"
        if f in DEN_ROLE:
            kind, pos = DEN_ROLE[f]
            dn = ops[pos]
            ok, why = (den_lvl if kind == "level" else den_rate)[dn]
            e_val = ok
            if not first and not ok:
                first = why
        if not first:
            k, arr = KEY[f]
            kk = k[cid]
            finite, constant = bool(arr[0][kk]), bool(arr[1][kk])
            vmin, vmax = float(arr[2][kk]), float(arr[3][kk])
            if not finite:
                first = "D_NONFINITE_ON_REQUIRED_CALIBRATION_BLOCK"
            elif constant:
                first = "D_CONSTANT_ON_REQUIRED_CALIBRATION_BLOCK"
            elif not np.isfinite(vmax - vmin):
                first = "D_NONFINITE_DYNAMIC_RANGE"
        rows.append({
            "coordinate_id": cid, "constructor": f,
            "ordered_operands": r.ordered_operands,
            "class_B": bool(m.B), "class_A": bool(m.A), "class_C": bool(m.C),
            "class_G": bool(m.G), "class_F": bool(m.F),
            "class_D_finite": finite, "class_D_constant": constant,
            "class_E_denominator": e_val, "class_H_leakage": True,
            "value_min": vmin, "value_max": vmax,
            "admissible": first == "",
            "first_rejecting_class": (first[0] if first else ""),
            "rejection_reason": first})
    ADM = pd.DataFrame(rows)
    ADM.to_csv(S76R / "coordinate_admissibility.csv", index=False)
    assert bool((ADM.admissible | (ADM.rejection_reason != "")).all())

    passed = set(ADM.coordinate_id[ADM.admissible])
    rejected = ADM[~ADM.admissible]
    ATOM = REG[REG.coordinate_id.isin(passed)].copy()
    ATOM.to_csv(S76R / "primary_atomic_coordinate_universe.csv", index=False)
    rej = rejected[["coordinate_id", "constructor", "ordered_operands",
                    "first_rejecting_class", "rejection_reason",
                    "value_min", "value_max"]].copy()
    rej["denominator_category"] = [
        DEN_ROLE[c][0] if c in DEN_ROLE else "none" for c in rej.constructor]
    rej["signal_families"] = [
        "|".join(sorted({fam[o] for o in o_.split("|")}))
        for o_ in rej.ordered_operands]
    rej.to_csv(S76R / "coordinate_rejection_log.csv", index=False)

    ns = []
    for nm, kind, arr, k in ([(s, "level", D0, li[s]) for s in P_ALL]
                             + [(s, "derivative", D1, di[s]) for s in P_DOT]):
        ns.append({"primitive": nm, "kind": kind,
                   "finite_all_required_blocks": bool(arr[0][k]),
                   "constant_in_some_required_block": bool(arr[1][k]),
                   "value_min": float(arr[2][k]), "value_max": float(arr[3][k]),
                   "min_calibration_samples_any_block": int(nmin),
                   "required_min_samples": MIN_CAL})
    pd.DataFrame(ns).to_csv(S76R / "numerical_support_audit.csv", index=False)

    # ---- access audit ------------------------------------------------------
    with (MAN / "DATA_ACCESS_LOG.csv").open("w", newline="",
                                            encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ACCESS[0].keys()))
        w.writeheader()
        w.writerows(ACCESS)
    shots = {a["shot_id"] for a in ACCESS}
    (MAN / "ACCESS_AUDIT.json").write_text(json.dumps({
        "development_shots_read": sorted(shots), "n_development_shots_read": len(shots),
        "predictor_signals_read_per_shot": 70,
        "predictor_signal_list_is_P_hard": True,
        "calibration_blocks_read": ["A", "B", "C"],
        "target_values_accessed": 0, "external_values_accessed": 0,
        "external_shots_read": [], "models_fitted": 0, "baselines_run": 0,
        "predictor_target_correlations_computed": 0,
        "verdict": "FIREWALL_INTACT" if (len(shots) == 20 and not (shots & ext))
                   else "FIREWALL_BREACH"}, indent=2), encoding="utf-8")

    # ---- 23. exact deterministic dependency groups, re-derived over C0-C8 --
    assert AGG in P_TYP and AGG in P_DOT
    assert all(b in P_TYP and b in P_DOT for b in BEAMS)
    excl = set(BEAMS) | {AGG}
    groups, attempted = [], []

    def emit(gid, family, ctx, relation, aggc, comps, why):
        members = [aggc] + comps
        missing = [m for m in members if m not in passed]
        rec = {"dependency_group_id": gid, "constructor_family": family,
               "linear_context": ctx, "exact_relation": relation,
               "aggregate_coordinate": aggc,
               "component_coordinates": "|".join(comps),
               "n_members": len(members), "linearity_argument": why,
               "evidence_class": "LOCAL_DOCUMENTED",
               "all_members_admissible": not missing,
               "n_inadmissible_members": len(missing),
               "inadmissible_members": "|".join(missing),
               "status": "BINDING" if not missing else "VACUOUS",
               "vacuous_reason": ("" if not missing else
                                  "at least one member is inadmissible, so no "
                                  "admissible support can contain the complete "
                                  "exact set; the constraint is well defined "
                                  "but has no binding instance")}
        attempted.append(rec)
        if not missing:
            groups.append(rec)

    LIN_SUM = "aggregate enters linearly: sum_b (a_b) = (sum_b a_b)"
    LIN_DER = ("d/dt is linear and FD2_PHYSICAL_TIME_V1 is a fixed linear "
               "stencil on the shared grid, so dot(pinj) = sum_b dot(pinj_b)")

    def pr(i, j):
        a, b = (i, j) if idx[i] <= idx[j] else (j, i)
        return f"PROD({a},{b})"

    emit("DEP_C0_LEVEL", "C0", "ID(pinj_b)", "ID(pinj) = sum_b ID(pinj_b)",
         f"ID({AGG})", [f"ID({b})" for b in BEAMS], LIN_SUM)
    emit("DEP_C1_DERIV", "C1", "DOT(pinj_b)", "DOT(pinj) = sum_b DOT(pinj_b)",
         f"DOT({AGG})", [f"DOT({b})" for b in BEAMS], LIN_DER)
    for z in [z for z in P_TYP if z not in excl]:
        emit(f"DEP_C2_PROD_{z}", "C2", f"PROD(pinj_b,{z})",
             f"PROD(pinj,{z}) = sum_b PROD(pinj_b,{z})", pr(AGG, z),
             [pr(b, z) for b in BEAMS], LIN_SUM)
        emit(f"DEP_C3_RATIO_{z}", "C3", f"RATIO(pinj_b,{z})",
             f"RATIO(pinj,{z}) = sum_b RATIO(pinj_b,{z})",
             f"RATIO({AGG},{z})", [f"RATIO({b},{z})" for b in BEAMS],
             LIN_SUM + " (aggregate in NUMERATOR only)")
        emit(f"DEP_C6_RATE_{z}", "C6", f"LEVEL_RATE({z}|pinj_b)",
             f"LEVEL_RATE({z}|pinj) = sum_b LEVEL_RATE({z}|pinj_b)",
             f"LEVEL_RATE({z}|{AGG})", [f"LEVEL_RATE({z}|{b})" for b in BEAMS],
             LIN_DER + "; x_z * dot(pinj) = sum_b x_z * dot(pinj_b)")
        emit(f"DEP_C7_RATE_OVER_LEVEL_{z}", "C7", f"RATE_OVER_LEVEL(pinj_b|{z})",
             f"RATE_OVER_LEVEL(pinj|{z}) = sum_b RATE_OVER_LEVEL(pinj_b|{z})",
             f"RATE_OVER_LEVEL({AGG}|{z})",
             [f"RATE_OVER_LEVEL({b}|{z})" for b in BEAMS],
             LIN_DER + "; aggregate rate in NUMERATOR only")
    for z in [z for z in P_DOT if z not in excl]:
        emit(f"DEP_C4_PHASE_{z}", "C4", f"PHASE(pinj_b|{z})",
             f"PHASE(pinj|{z}) = sum_b PHASE(pinj_b|{z})",
             f"PHASE({AGG}|{z})", [f"PHASE({b}|{z})" for b in BEAMS],
             LIN_DER + "; aggregate rate in NUMERATOR only")
        emit(f"DEP_C6_LEVEL_{z}", "C6", f"LEVEL_RATE(pinj_b|{z})",
             f"LEVEL_RATE(pinj|{z}) = sum_b LEVEL_RATE(pinj_b|{z})",
             f"LEVEL_RATE({AGG}|{z})", [f"LEVEL_RATE({b}|{z})" for b in BEAMS],
             LIN_SUM + "; pinj * dot(x_z) = sum_b pinj_b * dot(x_z)")
        emit(f"DEP_C8_LEVEL_OVER_RATE_{z}", "C8", f"LEVEL_OVER_RATE(pinj_b|{z})",
             f"LEVEL_OVER_RATE(pinj|{z}) = sum_b LEVEL_OVER_RATE(pinj_b|{z})",
             f"LEVEL_OVER_RATE({AGG}|{z})",
             [f"LEVEL_OVER_RATE({b}|{z})" for b in BEAMS],
             LIN_SUM + "; aggregate level in NUMERATOR only")

    NOT_LINEAR = [
        {"family": "C5", "form": "RECIP(pinj)",
         "why": "1/sum_b x_b != sum_b 1/x_b. The reciprocal is not linear in "
                "its operand; no exact restatement exists."},
        {"family": "C3", "form": "RATIO(z,pinj)",
         "why": "the aggregate is the DENOMINATOR level; z/sum_b x_b is not a "
                "sum of z/x_b."},
        {"family": "C4", "form": "PHASE(z|pinj)",
         "why": "the aggregate rate is the DENOMINATOR."},
        {"family": "C7", "form": "RATE_OVER_LEVEL(z|pinj)",
         "why": "the aggregate level is the DENOMINATOR."},
        {"family": "C8", "form": "LEVEL_OVER_RATE(z|pinj)",
         "why": "the aggregate rate is the DENOMINATOR."},
        {"family": "C2", "form": "PROD(pinj,pinj)",
         "why": "quadratic in the aggregate; (sum_b x_b)^2 != sum_b x_b^2."},
    ]
    pd.DataFrame(attempted).to_csv(
        S76R / "exact_dependency_groups_attempted.csv", index=False)
    DEP = pd.DataFrame(groups) if groups else pd.DataFrame(
        columns=list(attempted[0].keys()))
    DEP.to_csv(S76R / "exact_dependency_groups.csv", index=False)
    (MAN / "DEPENDENCY_DERIVATION.json").write_text(json.dumps({
        "exact_relation": "pinj = sum_b pinj_b over eight beamlines",
        "evidence_class": "LOCAL_DOCUMENTED",
        "rederived_over": ["C0", "C1", "C2", "C3", "C4", "C6", "C7", "C8"],
        "copied_from_S7_6_V1": False,
        "families_with_exact_groups":
            sorted({a["constructor_family"] for a in attempted}),
        "n_attempted": len(attempted), "n_binding": len(groups),
        "n_vacuous": sum(1 for a in attempted if a["status"] == "VACUOUS"),
        "forms_with_no_exact_linear_identity": NOT_LINEAR,
        "neither_representation_privileged": True,
    }, indent=2), encoding="utf-8")

    # ---- summary -----------------------------------------------------------
    by_c = {c: int(n) for c, n in ATOM.constructor.value_counts().items()}
    for c in EXPECT:
        by_c.setdefault(c, 0)
    summary = {
        "symbolic": counts, "symbolic_total": 23861,
        "n_metadata_rejections": n_meta_rej,
        "admissible_by_constructor": {c: by_c[c] for c in EXPECT},
        "n_admissible": int(len(ATOM)),
        "rejections_by_class": {k: int(v) for k, v in
                                rejected.first_rejecting_class.value_counts().items()},
        "rejections_by_reason": {k: int(v) for k, v in
                                 rejected.rejection_reason.value_counts().items()},
        "rejections_by_constructor": {k: int(v) for k, v in
                                      rejected.constructor.value_counts().items()},
        "rejections_by_denominator_category":
            {k: int(v) for k, v in rej.denominator_category.value_counts().items()},
        "level_denominators_pass": len(OKL), "level_denominators_total": len(P_TYP),
        "rate_denominators_pass": len(OKR), "rate_denominators_total": len(P_DOT),
        "level_denominator_failures":
            {n: v[1] for n, v in den_lvl.items() if not v[0]},
        "rate_denominator_failure_reasons":
            {k: int(v) for k, v in pd.Series(
                [v[1] for v in den_rate.values() if not v[0]]).value_counts().items()}
            if len(OKR) < len(P_DOT) else {},
        "n_dependency_groups_attempted": len(attempted),
        "n_dependency_groups_binding": len(groups),
        "n_dependency_groups_vacuous": sum(1 for a in attempted
                                           if a["status"] == "VACUOUS"),
        "min_calibration_samples": int(nmin), "required_min_samples": MIN_CAL,
        "n_development_shots": len(dev), "n_cells": len(CELLS),
    }
    (MAN / "UNIVERSE_SUMMARY.json").write_text(json.dumps(summary, indent=2),
                                               encoding="utf-8")

    print("symbolic  :", counts, "total", len(REG))
    print("metadata rejections (B/A/C/G/F):", n_meta_rej)
    print(f"denominators: level {len(OKL)}/{len(P_TYP)}   rate {len(OKR)}/{len(P_DOT)}")
    print("admissible:", summary["admissible_by_constructor"],
          "total", summary["n_admissible"])
    print("rejections by class :", summary["rejections_by_class"])
    print("rejections by reason:", summary["rejections_by_reason"])
    print(f"dependency groups: attempted {len(attempted)} binding {len(groups)} "
          f"vacuous {summary['n_dependency_groups_vacuous']}")
    print(f"min calibration samples {nmin} (required {MIN_CAL})")


if __name__ == "__main__":
    main()
