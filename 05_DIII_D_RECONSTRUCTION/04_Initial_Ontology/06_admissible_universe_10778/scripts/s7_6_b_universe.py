"""S7.6 stage B — instantiate the coordinate registry and apply admissibility.

Opens DEVELOPMENT PREDICTOR values only. Never the target, never external.

Evaluation order is the frozen P_rec order B / A / C / G / F / D / E / H. For
the two partial-map families the denominator gate (E) is evaluated on the
denominator PRIMITIVE before the constructed coordinate can exist at all, and
class D is then applied to the constructed coordinate, exactly as sections 12
and 13 specify.
"""

from __future__ import annotations

import csv
import hashlib
import math
import json
import platform
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S76 = HERE.parent
S7 = S76.parent
EX = S7.parent
R1 = S7 / "01_observational_object" / "reconciliation_final"
S72 = S7 / "02_reconstruction_contract"
CV1 = S72 / "correction_v1"
RSR = S7 / "03_target_feasibility_and_boundary" / "reconciliation_source_resolution"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S75 = S7 / "05_typed_relational_ontology"
MAN = S76 / "manifests"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

FREEZE_ID = "D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1"
TARGET = "density"
SELF_REF = {"S7_6_ACCEPTANCE_CHECKS.json", "S7_6_FREEZE.json"}
BLOCKS = [("A", 0.40), ("B", 0.60), ("C", 0.80)]     # calibration upper edges
MIN_CAL = 30
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4,
         "kW": 1e3}
ACCESS: list[dict] = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def denom_audit(d: np.ndarray, eta_min: float) -> tuple[bool, str, float, float]:
    """Frozen primary denominator rule. Returns (ok, reason, eta, rms)."""
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
    rule = json.loads((S76 / "denominator_admissibility_rule.json").read_text())
    ETA = float(rule["DENOMINATOR_MARGIN_PRIMARY"])
    assert ETA == 0.05

    G = json.loads((S75 / "G_REC.json").read_text())
    P = pd.read_csv(S75 / "primitive_type_registry.csv")
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    dev = list(part["development"]["shot_ids"])
    ext = set(part["external"]["shot_ids"])
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str})
    TRd = TR[TR.cohort == "development"].set_index("discharge")

    prim = list(P.primitive_id)
    assert TARGET not in prim and len(prim) == 78
    idx = {s: int(P.signal_index[P.primitive_id == s].iloc[0]) for s in prim}
    unit = dict(zip(P.primitive_id, P.canonical_unit.fillna("")))
    dimx = dict(zip(P.primitive_id, P.dimension_expression))
    fam = dict(zip(P.primitive_id, P.broad_scientific_family))
    blk = dict(zip(P.primitive_id, P.mathematical_type_block))
    alias = dict(zip(P.primitive_id, P.aliasing_flag))
    upsm = dict(zip(P.primitive_id, P.upstream_upsampled_flag))
    uncal = dict(zip(P.primitive_id, P.uncalibrated_flag))
    dtmax = dict(zip(P.primitive_id, P.source_supported_dt_max_ms))

    OP_D = sorted([s for s in prim if P.derivative_primary_eligible[
        P.primitive_id == s].iloc[0]], key=lambda s: idx[s])          # 70
    OP_PR = sorted([s for s in prim if P.product_ratio_operand_eligible[
        P.primitive_id == s].iloc[0]], key=lambda s: idx[s])          # 76
    SENS = sorted([s for s in prim if P.derivative_sensitivity_only[
        P.primitive_id == s].iloc[0]], key=lambda s: idx[s])          # 6
    assert (len(OP_D), len(OP_PR), len(SENS)) == (70, 76, 6)

    # ---- 6. symbolic registry --------------------------------------------
    reg = []

    def add(cid, fam_id, ops, dim, uexpr, dom, sens=False):
        anc = sorted(set(ops))
        reg.append({
            "coordinate_id": cid, "constructor": fam_id,
            "operands": "|".join(ops), "primitive_ancestors": "|".join(anc),
            "n_ancestors": len(anc),
            "depth": 0 if fam_id == "C0" else 1,
            "output_dimension": dim, "unit_expression": uexpr,
            "temporal_propagation": ("inherit" if fam_id == "C0" else
                                     "inherit+DERIVED_FROM_NUMERICAL_REALIZATION"
                                     if fam_id == "C1" else
                                     "coarser_of_operands"),
            "temporal_resolution_bound_ms": max(dtmax[o] for o in anc),
            "provenance_lineage": "|".join(f"{o}:{fam[o]}" for o in anc),
            "aliasing_flag": any(alias[o] for o in anc),
            "upsample_flag": any(upsm[o] for o in anc),
            "uncalibrated_flag": any(uncal[o] for o in anc),
            "primary_or_sensitivity": "SENSITIVITY" if sens else "PRIMARY",
            "domain_predicate": dom,
            "exact_dependency_member": "",
        })

    for s in prim:
        add(f"ID({s})", "C0", [s], dimx[s], unit[s] or "UNCALIBRATED", "")
    for s in OP_D:
        add(f"DOT({s})", "C1", [s], f"({dimx[s]}) T^-1",
            f"{unit[s]}/s", "")
    for a, b in list(combinations(OP_PR, 2)) + [(x, x) for x in OP_PR]:
        i, j = (a, b) if idx[a] <= idx[b] else (b, a)
        add(f"PROD({i},{j})", "C2", [i, j], f"({dimx[i]})*({dimx[j]})",
            f"{unit[i]}*{unit[j]}", "")
    for i in OP_PR:
        for j in OP_PR:
            if i == j:
                continue
            add(f"RATIO({i},{j})", "C3", [i, j], f"({dimx[i]})/({dimx[j]})",
                f"{unit[i]}/{unit[j]}", "DOMAIN_DENOMINATOR_NONZERO")
    for i in OP_D:
        for j in OP_D:
            if i == j:
                continue
            add(f"PHASE({i}|{j})", "C4", [i, j], f"({dimx[i]})/({dimx[j]})",
                f"{unit[i]}/{unit[j]}", "DOMAIN_DENOMINATOR_RATE_NONZERO")
    REG = pd.DataFrame(reg)
    counts = REG.constructor.value_counts().to_dict()
    assert counts == {"C0": 78, "C1": 70, "C2": 2926, "C3": 5700, "C4": 4830}, counts
    assert len(REG) == 13604

    SENSREG = pd.DataFrame([{
        "coordinate_id": f"DOT({s})", "constructor": "C1",
        "operands": s, "primitive_ancestors": s, "depth": 1,
        "output_dimension": f"({dimx[s]}) T^-1", "unit_expression": f"{unit[s]}/s",
        "primary_or_sensitivity": "SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT",
        "reason": "operand is UPSTREAM_UPSAMPLED; derivative reports the "
                  "interpolant", "examined_by": "S7.11",
        "in_primary_A_rec": False} for s in SENS])
    SENSREG.to_csv(S76 / "sensitivity_only_coordinate_registry.csv", index=False)
    REG.to_csv(S76 / "coordinate_registry_all.csv", index=False)

    # ---- 8. classes B/A/C/G/F (metadata) ---------------------------------
    prim_set = set(prim)
    meta = []
    for r in REG.itertuples():
        anc = r.primitive_ancestors.split("|")
        B_ok = all(a in prim_set for a in anc)
        A_ok = len(anc) >= 1 and bool(r.provenance_lineage)
        C_ok = (r.constructor == "C0") or (not r.uncalibrated_flag)
        G_ok = True
        F_ok = not (r.constructor in ("C1", "C4")
                    and any(a in set(SENS) for a in anc))
        first = ("B" if not B_ok else "A" if not A_ok else "C" if not C_ok
                 else "G" if not G_ok else "F" if not F_ok else "")
        meta.append({"coordinate_id": r.coordinate_id, "B": B_ok, "A": A_ok,
                     "C": C_ok, "G": G_ok, "F": F_ok, "first_metadata_reject": first})
    META = pd.DataFrame(meta)
    n_meta_rej = int((META.first_metadata_reject != "").sum())

    # ---- 9. development numerical realizations ---------------------------
    lev, der = {}, {}
    for s in dev:
        if s in ext:
            raise SystemExit("STOP: firewall")
        t0 = float(TRd.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TRd.loc[s, "delta_t_ms"])
        n = int(TRd.loc[s, "N_s"])
        grid_ms = t0 + dtm * np.arange(n, dtype=np.float64)
        t_sec = grid_ms / 1000.0
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            L = np.empty((78, n), dtype=np.float64)
            for k, sig in enumerate(prim):
                tt, vv = PROV._load_signal(a, sig)
                f = CANON.get(str(PROV.SIGNAL_UNIT[sig]), 1.0)
                L[k] = PROV._resample_to_grid(tt, vv, grid_ms) * f
        lev[s] = L
        D = np.empty((70, n), dtype=np.float64)
        for k, sig in enumerate(OP_D):
            D[k] = np.gradient(L[prim.index(sig)], t_sec, edge_order=2)
        der[s] = D
        ACCESS.append({"stage": "S7.6B", "shot_id": s,
                       "development_or_external": "development",
                       "predictor_signals_read": 78,
                       "target_values_read": 0,
                       "reason": "atomic coordinate admissibility (classes D,E) "
                                 "on calibration intervals",
                       "timestamp": datetime.now(timezone.utc).isoformat()})

    li = {s: k for k, s in enumerate(prim)}
    di = {s: k for k, s in enumerate(OP_D)}
    slices = {}
    for s in dev:
        n = lev[s].shape[1]
        for bn, c1 in BLOCKS:
            slices[(s, bn)] = slice(0, int(np.floor(n * c1)))

    # ---- 10/12/13. per-primitive caches ----------------------------------
    def d_stats(mat, names, imap):
        fin = np.ones(len(names), bool)
        con = np.zeros(len(names), bool)
        gmin = np.full(len(names), np.inf)
        gmax = np.full(len(names), -np.inf)
        nmin = np.inf
        for s in dev:
            M = mat[s]
            for bn, _ in BLOCKS:
                v = M[:, slices[(s, bn)]]
                nmin = min(nmin, v.shape[1])
                fin &= np.all(np.isfinite(v), axis=1)
                vmn, vmx = v.min(axis=1), v.max(axis=1)
                con |= (vmn == vmx)
                gmin = np.minimum(gmin, vmn)
                gmax = np.maximum(gmax, vmx)
        return fin, con, gmin, gmax, nmin

    lf, lc, lmn, lmx, nmin_l = d_stats(lev, prim, li)
    df_, dc, dmn, dmx, _ = d_stats(der, OP_D, di)

    # denominator audits, cached per primitive
    den_rows, den_ok_lvl, den_ok_der = [], {}, {}
    for kind, names, mat, imap in (("level", OP_PR, lev, li),
                                   ("derivative", OP_D, der, di)):
        for nm in names:
            k = imap[nm]
            ok_all, reasons = True, []
            for s in dev:
                for bn, _ in BLOCKS:
                    d = mat[s][k, slices[(s, bn)]]
                    ok, why, eta, rms = denom_audit(d, ETA)
                    den_rows.append({
                        "denominator": nm, "denominator_kind": kind,
                        "shot_id": s, "block": bn, "n": int(d.size),
                        "rms": rms, "min_abs": float(np.min(np.abs(d)))
                        if np.all(np.isfinite(d)) else np.nan,
                        "eta": eta, "sign_change": why == "E_DENOM_SIGN_CHANGE",
                        "passes": ok, "fail_reason": why})
                    if not ok:
                        ok_all = False
                        reasons.append(why)
            (den_ok_lvl if kind == "level" else den_ok_der)[nm] = (
                ok_all, reasons[0] if reasons else "")
    pd.DataFrame(den_rows).to_csv(S76 / "denominator_conditioning_audit.csv",
                                  index=False)

    # ---- coordinate-level D for C2 / C3 / C4 ------------------------------
    def eval_pairs(numer_idx, denom_idx, mat, op, nco):
        """Streaming class-D over all (s,b) for nco constructed coordinates."""
        fin = np.ones(nco, bool)
        con = np.zeros(nco, bool)
        gmn = np.full(nco, np.inf)
        gmx = np.full(nco, -np.inf)
        for s in dev:
            M = mat[s]
            for bn, _ in BLOCKS:
                sl = slices[(s, bn)]
                a = M[numer_idx][:, sl]
                b = M[denom_idx][:, sl]
                v = a * b if op == "mul" else a / b
                fin &= np.all(np.isfinite(v), axis=1)
                vmn, vmx = v.min(axis=1), v.max(axis=1)
                con |= (vmn == vmx)
                gmn = np.minimum(gmn, vmn)
                gmx = np.maximum(gmx, vmx)
        return fin, con, gmn, gmx

    # C2
    pairs = [(i, j) for i, j in combinations(OP_PR, 2)] + [(x, x) for x in OP_PR]
    pairs = [((i, j) if idx[i] <= idx[j] else (j, i)) for i, j in pairs]
    p_i = np.array([li[i] for i, _ in pairs])
    p_j = np.array([li[j] for _, j in pairs])
    c2f, c2c, c2mn, c2mx = eval_pairs(p_i, p_j, lev, "mul", len(pairs))
    c2key = {f"PROD({i},{j})": k for k, (i, j) in enumerate(pairs)}

    # C3: only where the denominator passed E
    c3_pairs = [(i, j) for i in OP_PR for j in OP_PR
                if i != j and den_ok_lvl[j][0]]
    if c3_pairs:
        n_i = np.array([li[i] for i, _ in c3_pairs])
        n_j = np.array([li[j] for _, j in c3_pairs])
        c3f, c3c, c3mn, c3mx = eval_pairs(n_i, n_j, lev, "div", len(c3_pairs))
    else:
        c3f = c3c = c3mn = c3mx = np.array([])
    c3key = {f"RATIO({i},{j})": k for k, (i, j) in enumerate(c3_pairs)}

    # C4
    c4_pairs = [(i, j) for i in OP_D for j in OP_D
                if i != j and den_ok_der[j][0]]
    if c4_pairs:
        m_i = np.array([di[i] for i, _ in c4_pairs])
        m_j = np.array([di[j] for _, j in c4_pairs])
        c4f, c4c, c4mn, c4mx = eval_pairs(m_i, m_j, der, "div", len(c4_pairs))
    else:
        c4f = c4c = c4mn = c4mx = np.array([])
    c4key = {f"PHASE({i}|{j})": k for k, (i, j) in enumerate(c4_pairs)}

    # ---- assemble admissibility -------------------------------------------
    rows = []
    for r in REG.itertuples():
        cid, fm = r.coordinate_id, r.constructor
        ops = r.operands.split("|")
        m = META[META.coordinate_id == cid]
        first = ""
        finite = constant = None
        vmin = vmax = np.nan
        eta = np.nan
        if nmin_l < MIN_CAL:
            first = "D_INSUFFICIENT_CALIBRATION_SAMPLES"
        if not first and fm == "C0":
            k = li[ops[0]]
            finite, constant = bool(lf[k]), bool(lc[k])
            vmin, vmax = lmn[k], lmx[k]
        elif not first and fm == "C1":
            k = di[ops[0]]
            finite, constant = bool(df_[k]), bool(dc[k])
            vmin, vmax = dmn[k], dmx[k]
        elif not first and fm == "C2":
            k = c2key[cid]
            finite, constant = bool(c2f[k]), bool(c2c[k])
            vmin, vmax = c2mn[k], c2mx[k]
        elif not first and fm in ("C3", "C4"):
            den = ops[1]
            ok, why = (den_ok_lvl[den] if fm == "C3" else den_ok_der[den])
            if not ok:
                first = why
            else:
                key = c3key if fm == "C3" else c4key
                arr = ((c3f, c3c, c3mn, c3mx) if fm == "C3"
                       else (c4f, c4c, c4mn, c4mx))
                k = key[cid]
                finite, constant = bool(arr[0][k]), bool(arr[1][k])
                vmin, vmax = arr[2][k], arr[3][k]
        if not first and finite is not None:
            if not finite:
                first = "D_NONFINITE_ON_REQUIRED_CALIBRATION_BLOCK"
            elif constant:
                first = "D_CONSTANT_ON_REQUIRED_CALIBRATION_BLOCK"
            elif not np.isfinite(vmax - vmin):
                first = "D_NONFINITE_DYNAMIC_RANGE"
        mrej = m.first_metadata_reject.iloc[0]
        if mrej:
            first = mrej
        rows.append({
            "coordinate_id": cid, "constructor": fm,
            "operands": r.operands,
            "class_B": bool(m.B.iloc[0]), "class_A": bool(m.A.iloc[0]),
            "class_C": bool(m.C.iloc[0]), "class_G": bool(m.G.iloc[0]),
            "class_F": bool(m.F.iloc[0]),
            "class_D_finite": finite, "class_D_constant": constant,
            "class_E_denominator": (None if fm not in ("C3", "C4")
                                    else (den_ok_lvl if fm == "C3"
                                          else den_ok_der)[ops[1]][0]),
            "class_H_leakage": True,
            "value_min": vmin, "value_max": vmax,
            "admissible": first == "",
            "first_rejecting_class": (first[0] if first else ""),
            "rejection_reason": first,
        })
    ADM = pd.DataFrame(rows)
    ADM.to_csv(S76 / "coordinate_admissibility.csv", index=False)

    passed = ADM[ADM.admissible]
    rejected = ADM[~ADM.admissible]
    ATOM = REG[REG.coordinate_id.isin(set(passed.coordinate_id))].copy()
    ATOM.to_csv(S76 / "primary_atomic_coordinate_universe.csv", index=False)
    rejected[["coordinate_id", "constructor", "operands",
              "first_rejecting_class", "rejection_reason",
              "value_min", "value_max"]].to_csv(
        S76 / "coordinate_rejection_log.csv", index=False)

    ns_rows = []
    for nm, k, kind, f_, c_, mn_, mx_ in (
            [(s, li[s], "level", lf[li[s]], lc[li[s]], lmn[li[s]], lmx[li[s]])
             for s in prim]
            + [(s, di[s], "derivative", df_[di[s]], dc[di[s]], dmn[di[s]],
                dmx[di[s]]) for s in OP_D]):
        ns_rows.append({"primitive": nm, "kind": kind,
                        "finite_all_blocks": bool(f_),
                        "constant_in_some_block": bool(c_),
                        "value_min": mn_, "value_max": mx_,
                        "min_calibration_samples": int(nmin_l)})
    pd.DataFrame(ns_rows).to_csv(S76 / "numerical_support_audit.csv", index=False)

    with (MAN / "DATA_ACCESS_LOG.csv").open("w", newline="",
                                            encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ACCESS[0].keys()))
        w.writeheader()
        w.writerows(ACCESS)
    shots_read = {a["shot_id"] for a in ACCESS}
    (MAN / "ACCESS_AUDIT.json").write_text(json.dumps({
        "development_shots_read": sorted(shots_read),
        "n_development_shots_read": len(shots_read),
        "predictor_signals_per_shot": 78,
        "target_values_accessed": 0,
        "external_values_accessed": 0,
        "external_shots_read": [],
        "verdict": "FIREWALL_INTACT" if (len(shots_read) == 20
                                         and not (shots_read & ext)) else
                   "FIREWALL_BREACH"}, indent=2), encoding="utf-8")

    # ---- 16/17. exact dependency groups -----------------------------------
    beams = [f"pinj_{b}" for b in ("15l", "15r", "21l", "21r", "30l", "30r",
                                   "33l", "33r")]
    agg = "pinj"
    A = set(ATOM.coordinate_id)
    groups = []

    attempted = []

    def emit(gid, ctx, aggc, comps):
        """Record every mathematically valid exact group and whether it is
        BINDING (all nine members admissible, so a support could contain the
        complete set) or VACUOUS (some member inadmissible, so no admissible
        support can ever contain the complete set)."""
        members = [aggc] + comps
        missing = [m for m in members if m not in A]
        rec = {"dependency_group_id": gid, "linear_context": ctx,
               "aggregate_coordinate": aggc,
               "component_coordinates": "|".join(comps),
               "n_members": len(members),
               "exact_relation": f"{aggc} = sum_i {ctx}",
               "evidence_class": "LOCAL_DOCUMENTED",
               "all_members_admissible": not missing,
               "n_inadmissible_members": len(missing),
               "inadmissible_members": "|".join(missing),
               "status": "BINDING" if not missing else "VACUOUS",
               "vacuous_reason": ("" if not missing else
                                  "at least one member is inadmissible, so no "
                                  "admissible support can contain the complete "
                                  "exact set; the constraint is well-defined "
                                  "but has no binding instance")}
        attempted.append(rec)
        if not missing:
            groups.append(rec)

    emit("DEP_LEVEL", "ID(pinj_i)", f"ID({agg})", [f"ID({b})" for b in beams])
    emit("DEP_DERIV", "DOT(pinj_i)", f"DOT({agg})", [f"DOT({b})" for b in beams])
    for z in OP_PR:
        if z == agg or z in beams:
            continue
        ai, aj = (agg, z) if idx[agg] <= idx[z] else (z, agg)
        comps = []
        for b in beams:
            bi, bj = (b, z) if idx[b] <= idx[z] else (z, b)
            comps.append(f"PROD({bi},{bj})")
        emit(f"DEP_PROD_{z}", f"PROD(pinj_i,{z})", f"PROD({ai},{aj})", comps)
    for z in OP_PR:
        if z == agg or z in beams:
            continue
        emit(f"DEP_RATIO_{z}", f"RATIO(pinj_i,{z})", f"RATIO({agg},{z})",
             [f"RATIO({b},{z})" for b in beams])
    for z in OP_D:
        if z == agg or z in beams:
            continue
        emit(f"DEP_PHASE_{z}", f"PHASE(pinj_i|{z})", f"PHASE({agg}|{z})",
             [f"PHASE({b}|{z})" for b in beams])
    pd.DataFrame(attempted).to_csv(
        S76 / "exact_dependency_groups_attempted.csv", index=False)
    DEP = pd.DataFrame(groups) if groups else pd.DataFrame(
        columns=["dependency_group_id", "linear_context",
                 "aggregate_coordinate", "component_coordinates",
                 "n_members", "exact_relation", "evidence_class",
                 "all_members_admissible"])
    DEP.to_csv(S76 / "exact_dependency_groups.csv", index=False)

    # ---- 19/20/22. A_rec, intensional -------------------------------------
    M = int(len(ATOM))
    total_subsets = sum(math.comb(M, m) for m in range(1, 13)) if M else 0
    setc = {
        "constraint_id": "PHI_SET_V1",
        "constraints": [
            {"id": "size", "rule": "1 <= |C| <= 12", "source": "frozen B_rec"},
            {"id": "no_duplicates", "rule": "no duplicate coordinate IDs in C"},
            {"id": "atoms_only",
             "rule": "every coordinate in C belongs to C_rec^atom"},
            {"id": "no_sensitivity_only",
             "rule": "no SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT coordinate in C"},
            {"id": "phi_dependency",
             "rule": "C must NOT contain the COMPLETE membership of any frozen "
                     "exact linear dependency group",
             "n_groups_binding": int(len(DEP)),
             "n_groups_attempted": len(attempted),
             "note": "a support may contain the aggregate and SOME components; "
                     "it may not contain the aggregate and ALL eight component "
                     "restatements in the same linear context. Neither form is "
                     "privileged a priori."},
            {"id": "no_target", "rule": "the target never appears in C"},
        ],
        "explicitly_not_imposed": [
            "must contain a phase derivative", "must contain multiple families",
            "must include raw levels", "any search heuristic or preference"],
    }
    (S76 / "representation_set_constraints.json").write_text(
        json.dumps(setc, indent=2), encoding="utf-8")

    atomj = {
        "universe_id": "C_REC_ATOM_V1",
        "n_atoms": M,
        "by_constructor": ATOM.constructor.value_counts().to_dict(),
        "symbolic_before_admissibility": counts,
        "sensitivity_only_registry": "sensitivity_only_coordinate_registry.csv",
        "atoms_file": "primary_atomic_coordinate_universe.csv",
    }
    (S76 / "atomic_coordinate_universe.json").write_text(
        json.dumps(atomj, indent=2), encoding="utf-8")

    arec = {
        "universe_id": "A_REC_DENSITY_V1",
        "freeze_id": FREEZE_ID,
        "formal_definition":
            "A_rec = { (C,R) : C subset C_rec^atom, 1 <= |C| <= 12, "
            "Phi_set(C) = 1, R in R_rec(C) }",
        "R_rec": "T_REC_V1 for every C (affine-linear in constructed "
                 "coordinates, intercept allowed and not counted toward |C|, "
                 "shared support identity, discharge-specific coefficients)",
        "C_rec_atom": atomj,
        "Phi_set": setc,
        "representation": {
            "is_finite": True,
            "materialized_support_by_support": False,
            "factorized_representation_is_exact": True,
            "why": "the coordinate atoms together with the set-level predicates "
                   "are a complete finite representation of A_rec. Enumerating "
                   "every C is unnecessary and astronomically large.",
            "unconstrained_subset_count_1_to_12": total_subsets,
            "note": "this count IGNORES Phi_dependency and is reported only to "
                    "show why materialization was not attempted",
        },
        "explored_subset": "S7.7 explores only a subset Ahat_rec",
        "search_priority_assigned": False,
        "estimator_run": False,
        "target_values_accessed": 0,
        "external_values_accessed": 0,
        "external_partial_map_rule": rule["external_application_rule"],
        "raw_baseline_nesting": {
            "true": "primitive-only coordinate representations are nested "
                    "within A_rec whenever their support size satisfies 1..12 "
                    "and the set-level predicates",
            "not_claimed": "B2 itself is necessarily a member of A_rec",
            "b2_description": "the frozen raw Ridge comparator using the same "
                              "admissible primitive information, potentially "
                              "all 78 primitives",
            "fairness_claim": "SAME INFORMATION BOUNDARY, not identical "
                              "support-size constraint",
            "b2_modified": False},
    }
    (S76 / "A_REC.json").write_text(json.dumps(arec, indent=2, default=str),
                                    encoding="utf-8")

    summary = {
        "symbolic": counts, "symbolic_total": 13604,
        "n_metadata_rejections": n_meta_rej,
        "admissible_by_constructor": ATOM.constructor.value_counts().to_dict(),
        "n_admissible": M,
        "rejections_by_class":
            rejected.first_rejecting_class.value_counts().to_dict(),
        "rejections_by_reason": rejected.rejection_reason.value_counts().to_dict(),
        "rejections_by_constructor": rejected.constructor.value_counts().to_dict(),
        "denominators_level_pass": int(sum(v[0] for v in den_ok_lvl.values())),
        "denominators_level_total": len(den_ok_lvl),
        "denominators_deriv_pass": int(sum(v[0] for v in den_ok_der.values())),
        "denominators_deriv_total": len(den_ok_der),
        "n_dependency_groups_binding": int(len(DEP)),
        "n_dependency_groups_attempted": len(attempted),
        "n_dependency_groups_vacuous": sum(1 for a in attempted
                                           if a["status"] == "VACUOUS"),
        "min_calibration_samples": int(nmin_l),
    }
    (MAN / "UNIVERSE_SUMMARY.json").write_text(json.dumps(summary, indent=2),
                                               encoding="utf-8")

    print("symbolic :", counts, "total", len(REG))
    print(f"metadata rejections (B/A/C/G/F): {n_meta_rej}")
    print(f"denominators passing E: level {summary['denominators_level_pass']}"
          f"/{summary['denominators_level_total']}  derivative "
          f"{summary['denominators_deriv_pass']}/{summary['denominators_deriv_total']}")
    print("admissible:", summary["admissible_by_constructor"], "total", M)
    print("rejections by class :", summary["rejections_by_class"])
    print("rejections by reason:", summary["rejections_by_reason"])
    n_vac = sum(1 for a in attempted if a["status"] == "VACUOUS")
    print(f"exact dependency groups: attempted {len(attempted)}, "
          f"BINDING {len(DEP)}, vacuous "
          f"{n_vac}")
    print(f"min calibration samples: {nmin_l}")


if __name__ == "__main__":
    main()
