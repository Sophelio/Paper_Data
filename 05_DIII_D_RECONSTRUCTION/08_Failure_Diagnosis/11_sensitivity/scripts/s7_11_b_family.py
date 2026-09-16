"""S7.11 step B - predeclared external sensitivities.

Executes exactly the three analyses authorised by the frozen S7.11
predeclaration:
  1. SUPPORT_FAMILY_EXTERNAL_SENSITIVITY  - all 217 bootstrap-winning supports
  2. PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY  - the predeclared 7-coordinate support
  3. PRMTAN_NEPED_ONLY                    - ID(prmtan_neped)

Plus the V9 temporal-block component, whose three-part definition (discharge,
temporal block, numerical realization) was frozen in S7.2 V1 long before any
external value existed.

Uses the identical external geometry, estimator, metric and domain rule as
S7.10. Nothing is tuned. No support is selected. C_dev_star is untouched.
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

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
EX = S7.parent
S72 = S7 / "02_reconstruction_contract"
S75H = S7 / "05H_primitive_space_and_ontology_hardening"
S76R = S7 / "06_admissible_universe" / "hardened_v2"
S77 = S7 / "07_search_policy_and_frontier"
S79 = S7 / "09_development_selection_and_freeze"
S710 = S7 / "10_external_validation"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
DATA = EX / "data" / "resampled_data_v6"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

TARGET = "density"
BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
ETA_MIN = 0.05
FLOOR = 0.01


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


def main() -> int:
    ver = json.loads((OUT / "S7_11_PREDECLARATION_VERIFICATION.json").read_text())
    if ver["verdict"] != "ZERO_SUBSTANTIVE_DRIFT":
        raise SystemExit("STOP: entry verification failed")

    f10 = json.loads((S710 / "S7_10_FREEZE.json").read_text())
    for name in ("external_block_metrics.csv", "external_discharge_metrics.csv"):
        if sha256(S710 / name) != f10["all_artifact_hashes"][name]:
            raise SystemExit("STOP: frozen S7.10 result file changed: " + name)
    bm10 = pd.read_csv(S710 / "external_block_metrics.csv")
    dm10 = pd.read_csv(S710 / "external_discharge_metrics.csv")
    bm10["shot_id"] = bm10.shot_id.astype(str)
    dm10["shot_id"] = dm10.shot_id.astype(str)
    assert bool(bm10.comparison_eligible.all()) and len(bm10) == 126

    boot = pd.read_csv(S79 / "bootstrap_selection_frequency.csv")
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text())
    pdj = json.loads((S710 / "S7_11_SENSITIVITY_PREDECLARATION.json").read_text())
    C_STAR = sel["support_id"]

    supports = {sid: depth_split(sid) for sid in boot.support_id}
    assert len(supports) == 217
    minus = list(pdj["sensitivities"]["PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY"]["resulting_support"])
    only = list(pdj["sensitivities"]["PRMTAN_NEPED_ONLY"]["support"])
    extra = {"SENS::PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY": minus,
             "SENS::PRMTAN_NEPED_ONLY": only}
    all_sets = dict(supports); all_sets.update(extra)

    # ---- atom realisation plan ------------------------------------------
    AT = pd.read_csv(S77 / "atom_stratum_assignment.csv")
    HB = pd.read_csv(S75H / "primitive_basis_hardened.csv").sort_values(
        "signal_index").reset_index(drop=True)
    P_ALL = list(HB.primitive_id)
    P_DOT = [s for s in P_ALL if bool(
        HB.derivative_primary_eligible[HB.primitive_id == s].iloc[0])]
    li = {s: k for k, s in enumerate(P_ALL)}
    di = {s: k for k, s in enumerate(P_DOT)}
    OPC = {"C0": 0, "C1": 0, "C5": 1, "C2": 2, "C6": 2, "C3": 3, "C7": 3}

    needed = sorted({a for v in all_sets.values() for a in v})
    plan, denom_of = {}, {}
    meta = AT.set_index("coordinate_id")
    for c in needed:
        cons = str(meta.loc[c, "constructor"])
        o = str(meta.loc[c, "ordered_operands"]).split("|")
        ak, ai = (1, di[o[0]]) if cons in ("C1", "C7") else (0, li[o[0]])
        bk = bi = -1
        if cons in ("C2", "C3", "C7"):
            bk, bi = 0, li[o[1]]
        elif cons == "C6":
            bk, bi = 1, di[o[1]]
        plan[c] = (OPC[cons], ak, ai, bk, bi)
        if cons == "C3":
            denom_of[c] = ("LEVEL", o[1])
        elif cons == "C5":
            denom_of[c] = ("LEVEL", o[0])
        elif cons == "C7":
            denom_of[c] = ("LEVEL", o[1])
        elif cons in ("C4", "C8"):
            denom_of[c] = ("RATE", o[1])
    all_denoms = sorted({d for k, (t, d) in denom_of.items() if t == "LEVEL"})
    rate_denoms = sorted({d for k, (t, d) in denom_of.items() if t == "RATE"})
    print("supports: %d family + %d predeclared extras | distinct atoms %d"
          % (len(supports), len(extra), len(needed)))
    print("level denominators in play: %d | rate denominators: %d"
          % (len(all_denoms), len(rate_denoms)))

    # ---- external data ---------------------------------------------------
    part = json.loads((S72 / "COHORT_PARTITION.json").read_text())
    ext = [str(s) for s in part["external"]["shot_ids"]]
    devset = set(str(s) for s in part["development"]["shot_ids"])
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")
    era = {s: str(TR.loc[s, "processing_era"]) for s in ext}

    t0 = time.time()
    ATOMS, YT, SLC, DENOM = {}, {}, {}, {}
    for s in ext:
        if s in devset:
            raise SystemExit("STOP: FIREWALL_BREACH")
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
            tt, vv = PROV._load_signal(a, TARGET)
            YT[s] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                str(PROV.SIGNAL_UNIT[TARGET]), 1.0)
        D = np.empty((63, n))
        for k, sig in enumerate(P_DOT):
            D[k] = np.gradient(L[li[sig]], tsec, edge_order=2)
        M = np.empty((len(needed), n))
        with np.errstate(divide="ignore", invalid="ignore"):
            for r, c in enumerate(needed):
                op, ak, ai, bk, bi = plan[c]
                A = L[ai] if ak == 0 else D[ai]
                if op == 0:
                    M[r] = A
                elif op == 1:
                    M[r] = 1.0 / A
                else:
                    B = L[bi] if bk == 0 else D[bi]
                    M[r] = A * B if op == 2 else A / B
        ATOMS[s] = M
        for bn, c1, c2 in BLOCKS:
            SLC[(s, bn)] = (slice(0, int(np.floor(n * c1))),
                            slice(int(np.floor(n * c1)), int(np.floor(n * c2))))
            cal = SLC[(s, bn)][0]
            for dnm in all_denoms:
                d = L[li[dnm]][cal]
                fin = bool(np.isfinite(d).all())
                rms = float(np.sqrt(np.mean(d ** 2))) if fin else np.nan
                sgn = bool(np.all(d > 0) or np.all(d < 0)) if fin else False
                eta = float(np.min(np.abs(d)) / rms) if (fin and rms > 0) else np.nan
                DENOM[(s, bn, dnm)] = (bool(fin and rms > 0 and sgn and eta >= ETA_MIN), eta)
    row_of = {c: i for i, c in enumerate(needed)}
    print("external data loaded in %.0fs" % (time.time() - t0))

    b0 = {(r.shot_id, r.block): r.B0_nrmse for r in bm10.itertuples()}
    b1 = {(r.shot_id, r.block): r.B1_nrmse for r in bm10.itertuples()}

    # ---- evaluation ------------------------------------------------------
    def evaluate(atoms, blocks=("A", "B", "C")):
        rows = np.array([row_of[a] for a in atoms])
        dnames = sorted({denom_of[a][1] for a in atoms if a in denom_of})
        per_block, applicable = {}, {}
        for s in ext:
            for bn in blocks:
                ok = all(DENOM[(s, bn, d)][0] for d in dnames)
                if not ok:
                    applicable[(s, bn)] = (False, "E_DENOM")
                    continue
                cal, pro = SLC[(s, bn)]
                X = ATOMS[s][rows]
                xc, xp = X[:, cal], X[:, pro]
                if not (np.isfinite(xc).all() and np.isfinite(xp).all()):
                    applicable[(s, bn)] = (False, "E_NONFINITE_COORDINATE")
                    continue
                mu = xc.mean(axis=1, keepdims=True)
                sd = xc.std(axis=1, ddof=0, keepdims=True)
                div = np.where(sd <= 0, 1.0, sd)
                Zc, Zp = ((xc - mu) / div).T, ((xp - mu) / div).T
                yc, yp = YT[s][cal], YT[s][pro]
                Xd = np.column_stack([np.ones(Zc.shape[0]), Zc])
                beta, *_ = np.linalg.lstsq(Xd, yc, rcond=None)
                pred = np.column_stack([np.ones(Zp.shape[0]), Zp]) @ beta
                scale = float(np.std(yc, ddof=0))
                if not np.isfinite(pred).all() or scale <= 0:
                    applicable[(s, bn)] = (False, "E_NONFINITE_PREDICTION")
                    continue
                per_block[(s, bn)] = float(np.sqrt(np.mean((yp - pred) ** 2)) / scale)
                applicable[(s, bn)] = (True, "")
        # discharge aggregation on the support's OWN eligible mask; B0/B1 use
        # the SAME mask so every paired comparison is common-support
        rel, bb0, bb1, eras, nblk = [], [], [], [], []
        for s in ext:
            ok = [bn for bn in blocks if applicable[(s, bn)][0]]
            if not ok:
                continue
            rel.append(np.mean([per_block[(s, bn)] for bn in ok]))
            bb0.append(np.mean([b0[(s, bn)] for bn in ok]))
            bb1.append(np.mean([b1[(s, bn)] for bn in ok]))
            eras.append(era[s]); nblk.append(len(ok))
        rel = np.array(rel); bb0 = np.array(bb0); bb1 = np.array(bb1)
        eras = np.array(eras)
        nbad = sum(1 for k, v in applicable.items() if not v[0])
        reasons = sorted({v[1] for v in applicable.values() if not v[0]})
        d0 = float((rel - bb0).mean()) if len(rel) else np.nan
        d1 = float((rel - bb1).mean()) if len(rel) else np.nan
        return {
            "n_discharges_evaluable": len(rel),
            "n_blocks_eligible": int(len(applicable) - nbad),
            "n_blocks_not_applicable": int(nbad),
            "not_applicable_reasons": ";".join(reasons),
            "full_domain": bool(nbad == 0 and len(rel) == len(ext)),
            "mean_nrmse": float(rel.mean()) if len(rel) else np.nan,
            "median_nrmse": float(np.median(rel)) if len(rel) else np.nan,
            "max_discharge_nrmse": float(rel.max()) if len(rel) else np.nan,
            "Delta_0": d0, "Delta_1": d1,
            "V3_STYLE_PASS": bool(d0 <= -FLOOR and d1 <= -FLOOR) if len(rel) else False,
            "mean_nrmse_earlier": float(rel[eras == "earlier"].mean()) if len(rel) else np.nan,
            "mean_nrmse_later": float(rel[eras == "later"].mean()) if len(rel) else np.nan,
            "median_nrmse_earlier": float(np.median(rel[eras == "earlier"])) if len(rel) else np.nan,
            "median_nrmse_later": float(np.median(rel[eras == "later"])) if len(rel) else np.nan,
            "Delta_1_earlier": float((rel - bb1)[eras == "earlier"].mean()) if len(rel) else np.nan,
            "Delta_1_later": float((rel - bb1)[eras == "later"].mean()) if len(rel) else np.nan,
            "_per_discharge": rel, "_shots": [s for s in ext],
            "_per_block": per_block, "_applicable": applicable,
        }

    # ---- family ----------------------------------------------------------
    t1 = time.time()
    recs = []
    star_pd = None
    for i, (sid, atoms) in enumerate(supports.items()):
        r = evaluate(atoms)
        pd_vec = r.pop("_per_discharge"); r.pop("_shots"); r.pop("_per_block"); r.pop("_applicable")
        if sid == C_STAR:
            star_pd = pd_vec
        bf = float(boot.loc[boot.support_id == sid, "bootstrap_selection_frequency"].iloc[0])
        recs.append({
            "support_id": sid, "support_size": len(atoms),
            "is_C_dev_star": sid == C_STAR,
            "development_bootstrap_selection_frequency": bf,
            "n_atoms": len(atoms),
            "contains_PROD_gasa_gasa": "PROD(gasa,gasa)" in atoms,
            "contains_prmtan_neped_atom": any("prmtan_neped" in a for a in atoms),
            "n_prmtan_neped_atoms": sum(1 for a in atoms if "prmtan_neped" in a),
            "contains_pcdiamag3": any("pcdiamag3" in a for a in atoms),
            **r})
        if (i + 1) % 50 == 0:
            print("  %d/217 supports (%.0fs)" % (i + 1, time.time() - t1))
    fam = pd.DataFrame(recs)
    fam.to_csv(OUT / "support_family_external_metrics.csv", index=False)
    fam[["support_id", "support_size", "is_C_dev_star", "full_domain", "Delta_0", "Delta_1",
         "V3_STYLE_PASS", "mean_nrmse", "median_nrmse"]].to_csv(
        OUT / "support_family_v3_results.csv", index=False)
    fam[["support_id", "support_size", "full_domain", "n_blocks_eligible",
         "n_blocks_not_applicable", "not_applicable_reasons",
         "n_discharges_evaluable"]].to_csv(
        OUT / "support_family_applicability.csv", index=False)

    # ---- prmtan sensitivities -------------------------------------------
    sens_rows = []
    star_row = fam[fam.is_C_dev_star].iloc[0]
    for name, atoms in extra.items():
        r = evaluate(atoms)
        pdv = r.pop("_per_discharge"); r.pop("_shots"); r.pop("_per_block"); r.pop("_applicable")
        paired_vs_star = float((pdv - star_pd).mean()) if len(pdv) == len(star_pd) else np.nan
        sens_rows.append({"sensitivity": name.replace("SENS::", ""),
                          "support": "|".join(atoms), "support_size": len(atoms),
                          "paired_mean_diff_vs_C_dev_star": paired_vs_star,
                          "_pd": pdv, **r})
    minus_pd = sens_rows[0].pop("_pd"); only_pd = sens_rows[1].pop("_pd")
    sens_rows[0]["paired_mean_diff_vs_prmtan_only"] = float((minus_pd - only_pd).mean())
    sens_rows[1]["paired_mean_diff_vs_minus_prmtan"] = float((only_pd - minus_pd).mean())
    sens = pd.DataFrame(sens_rows)
    sens.to_csv(OUT / "prmtan_sensitivity_metrics.csv", index=False)

    # ---- V9 temporal-block component ------------------------------------
    star_atoms = sel["canonical_coordinate_ids"]
    blk_rows = []
    for drop in "ABC":
        keep = tuple(b for b in "ABC" if b != drop)
        r = evaluate(star_atoms, blocks=keep)
        for k in ("_per_discharge", "_shots", "_per_block", "_applicable"):
            r.pop(k)
        blk_rows.append({"omitted_block": drop, "blocks_used": "+".join(keep), **r})
    blk = pd.DataFrame(blk_rows)
    blk.to_csv(OUT / "block_omission_sensitivity.csv", index=False)

    # ---- coordinate participation ---------------------------------------
    fd = fam[fam.full_domain]
    def participation(df, label):
        cnt = {}
        for sid in df.support_id:
            for a in supports[sid]:
                cnt[a] = cnt.get(a, 0) + 1
        n = max(len(df), 1)
        return [{"coordinate_id": a, "group": label, "n_supports": c,
                 "share": c / n, "group_size": len(df)} for a, c in cnt.items()]
    part_rows = participation(fam, "ALL_217")
    part_rows += participation(fd, "FULL_DOMAIN")
    part_rows += participation(fd[fd.V3_STYLE_PASS], "V3_STYLE_PASS")
    part_rows += participation(fd[~fd.V3_STYLE_PASS], "V3_STYLE_FAIL")
    cp = pd.DataFrame(part_rows)
    cp["in_C_dev_star"] = cp.coordinate_id.isin(star_atoms)
    cp.sort_values(["group", "share", "coordinate_id"],
                   ascending=[True, False, True]).to_csv(
        OUT / "support_family_coordinate_summary.csv", index=False)

    # ---- console ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUPPORT FAMILY: %d total | full-domain %d | not-full-domain %d"
          % (len(fam), int(fam.full_domain.sum()), int((~fam.full_domain).sum())))
    print("V3_STYLE_PASS among full-domain: %d / %d (%.4f)"
          % (int(fd.V3_STYLE_PASS.sum()), len(fd),
             fd.V3_STYLE_PASS.mean() if len(fd) else np.nan))
    q = [0, 5, 25, 50, 75, 95, 100]
    for col in ("mean_nrmse", "median_nrmse", "Delta_0", "Delta_1"):
        v = np.percentile(fd[col], q, method="linear")
        print("  %-13s " % col + " ".join("p%-3d %8.4f" % (a, b) for a, b in zip(q, v)))
    print("C_dev_star: mean %.4f median %.4f D0 %.4f D1 %.4f"
          % (star_row.mean_nrmse, star_row.median_nrmse, star_row.Delta_0, star_row.Delta_1))
    for col in ("mean_nrmse", "median_nrmse", "Delta_1"):
        pct = float((fd[col] <= star_row[col]).mean() * 100)
        print("   C_dev_star percentile in %-13s: %.1f  (rank %d of %d, ascending)"
              % (col, pct, int((fd[col] < star_row[col]).sum()) + 1, len(fd)))
    print("\nPRMTAN SENSITIVITIES")
    print(sens[["sensitivity", "support_size", "full_domain", "mean_nrmse", "median_nrmse",
                "Delta_0", "Delta_1", "V3_STYLE_PASS"]].to_string(index=False))
    print("\nV9 TEMPORAL-BLOCK OMISSION (C_dev_star)")
    print(blk[["omitted_block", "blocks_used", "mean_nrmse", "median_nrmse",
               "Delta_0", "Delta_1", "V3_STYLE_PASS"]].to_string(index=False))

    (OUT / "manifests" / "FAMILY_RUN.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_supports": len(fam), "n_full_domain": int(fam.full_domain.sum()),
        "n_extras": len(extra), "distinct_atoms_realised": len(needed),
        "level_denominators_in_play": len(all_denoms),
        "rate_denominators_in_play": len(rate_denoms),
        "runtime_seconds": round(time.time() - t0, 1),
        "b0_b1_reused_from_S7_10": True,
        "b0_b1_hash_verified": True,
        "common_support_rule": ("each support aggregates over its own eligible blocks and B0/B1 "
                                "are aggregated over the SAME blocks, so every paired comparison "
                                "is common-support"),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "platform": platform.platform()},
    }, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
