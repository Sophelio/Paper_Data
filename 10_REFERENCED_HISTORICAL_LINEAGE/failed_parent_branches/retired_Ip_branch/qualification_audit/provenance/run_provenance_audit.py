"""D3D-FIG6-PROVENANCE-AUDIT-V1 — target-provenance audit for q_rec.

AUDIT A. Determines, for every raw signal admitted into the q_rec (I_p
reconstruction) candidate universe, whether it carries upstream dependence on
the reconstruction target I_p.

Method
------
Archive metadata records only resampling method and category; it contains NO
physical provenance or upstream diagnostic lineage. Documentary provenance is
therefore UNAVAILABLE, and the conservative rule applies:

    if I_p ancestry cannot be ruled out rigorously,
    treat the signal as target-dependent.

To do better than assertion, this script tests the algebraic dependence
EMPIRICALLY against the archived data, using the textbook tokamak definitions
and the auxiliary signals the archive happens to contain (aminor, bt, area):

    q95   ~ (5 a^2 B_t / R I_p) * shape   ->  q95 * I_p / (a^2 B_t) ~ shape
    beta_N = beta_t * a * B_t / I_p       ->  betan * I_p / (a B_t) ~ beta_t
    l_i, kappa  are EFIT equilibrium outputs; EFIT is constrained by measured
                I_p, so their ancestry cannot be severed by any archived record.

Two diagnostics per signal:
  * relative scatter of the I_p-removed combination (small => the signal really
    is that algebraic function of I_p);
  * |correlation| with I_p or 1/I_p.

Plus a decisive inversion test: how well I_p itself is recovered from
a^2 B_t / q95 with a single per-shot scale factor.

Nothing here is written outside Figure6_qualification_audit/ and fig6data/.
Canonical artifacts are read-only.
"""

from __future__ import annotations

import glob
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

AUDIT_ID = "D3D-FIG6-PROVENANCE-AUDIT-V1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                     # DIIID_example
DATA = ROOT / "data" / "resampled_data_v6"
FIG6 = ROOT / "fig6data"
FIG6.mkdir(parents=True, exist_ok=True)

SEED = 20260901
CORR_THRESHOLD = 0.30       # |corr| above which ancestry is not dismissible
SCATTER_THRESHOLD = 0.25    # relative scatter below which the algebraic form holds

# Declared physical definitions. Sources: standard tokamak/EFIT conventions.
DEFINITIONS = {
    "pcdiamag3": dict(display="W_dia", diagnostic="diamagnetic loop",
                      formula="stored energy from diamagnetic flux",
                      contains_ip="no", efit_derived=False),
    "pinj": dict(display="P_NBI", diagnostic="neutral beam injectors",
                 formula="injected beam power", contains_ip="no",
                 efit_derived=False),
    "density": dict(display="n_e", diagnostic="interferometer",
                    formula="line-averaged electron density", contains_ip="no",
                    efit_derived=False),
    "ip": dict(display="I_p", diagnostic="Rogowski coil",
               formula="plasma current (THE TARGET)", contains_ip="is_target",
               efit_derived=False),
    "betan": dict(display="beta_N", diagnostic="EFIT + kinetic",
                  formula="beta_N = beta_t * a * B_t / I_p",
                  contains_ip="explicit", efit_derived=True),
    "q95": dict(display="q_95", diagnostic="EFIT",
                formula="q95 ~ 5 a^2 B_t / (R I_p) * shape factor",
                contains_ip="explicit", efit_derived=True),
    "li": dict(display="ell_i", diagnostic="EFIT",
               formula="internal inductance from the current profile; EFIT is "
                       "constrained by measured I_p",
               contains_ip="via_equilibrium", efit_derived=True),
    "kappa": dict(display="kappa", diagnostic="EFIT",
                  formula="elongation of the reconstructed boundary; EFIT is "
                          "constrained by measured I_p",
                  contains_ip="via_equilibrium", efit_derived=True),
}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def loader(f):
    a = np.load(f, allow_pickle=False)

    def g(n):
        return a[n + "_data"].astype(float), a[n + "_times"].astype(float)
    return g


def onto(g, name, tref):
    d, t = g(name)
    m = np.isfinite(t) & np.isfinite(d)
    if m.sum() < 2:
        return np.full_like(tref, np.nan)
    return np.interp(tref, t[m], d[m], left=np.nan, right=np.nan)


def empirical_dependence(files):
    """Per-shot algebraic-dependence diagnostics."""
    rows = []
    for f in files:
        shot = Path(f).name.split("_")[1]
        g = loader(f)
        try:
            q95, tq = g("q95")
        except KeyError:
            continue
        ok = np.isfinite(tq) & np.isfinite(q95)
        tref = tq[ok]
        q = q95[ok]
        ip = onto(g, "ip", tref)
        a = onto(g, "aminor", tref)
        bt = onto(g, "bt", tref)
        bn = onto(g, "betan", tref)
        li = onto(g, "li", tref)
        ka = onto(g, "kappa", tref)
        base = np.isfinite(ip) & np.isfinite(a) & np.isfinite(bt) & (np.abs(ip) > 1e5)

        def rec(sig, arr, scatter, corr_target):
            rows.append({"shot": shot, "signal": sig,
                         "rel_scatter_ip_removed": scatter,
                         "abs_corr_with_ip_form": corr_target})

        m = base & np.isfinite(q)
        if m.sum() >= 30:
            s = q[m] * np.abs(ip[m]) / (a[m] ** 2 * np.abs(bt[m]))
            rec("q95", q, float(np.std(s) / np.mean(s)),
                float(abs(np.corrcoef(q[m], 1.0 / np.abs(ip[m]))[0, 1])))
        mb = base & np.isfinite(bn)
        if mb.sum() >= 30:
            s = bn[mb] * np.abs(ip[mb]) / (a[mb] * np.abs(bt[mb]))
            rec("betan", bn, float(np.std(s) / np.mean(s)),
                float(abs(np.corrcoef(bn[mb], 1.0 / np.abs(ip[mb]))[0, 1])))
        for nm, v in (("li", li), ("kappa", ka)):
            mm = base & np.isfinite(v)
            if mm.sum() >= 30:
                rec(nm, v, float("nan"),
                    float(abs(np.corrcoef(v[mm], np.abs(ip[mm]))[0, 1])))
        for nm in ("pcdiamag3", "pinj", "density"):
            try:
                v = onto(g, nm, tref)
            except KeyError:
                continue
            mm = base & np.isfinite(v)
            if mm.sum() >= 30:
                rec(nm, v, float("nan"),
                    float(abs(np.corrcoef(v[mm], np.abs(ip[mm]))[0, 1])))
    return pd.DataFrame(rows)


def inversion_test(files):
    """Recover I_p from a^2 B_t / q95 with one scale factor per shot."""
    out = []
    for f in files:
        shot = Path(f).name.split("_")[1]
        g = loader(f)
        q95, tq = g("q95")
        ok = np.isfinite(tq) & np.isfinite(q95)
        tref = tq[ok]
        q = q95[ok]
        ip = onto(g, "ip", tref)
        a = onto(g, "aminor", tref)
        bt = onto(g, "bt", tref)
        m = (np.isfinite(ip) & np.isfinite(a) & np.isfinite(bt)
             & np.isfinite(q) & (np.abs(ip) > 1e5) & (q > 0))
        if m.sum() < 30:
            continue
        pred = (a[m] ** 2 * np.abs(bt[m])) / q[m]
        y = np.abs(ip[m])
        k = float(np.sum(pred * y) / np.sum(pred * pred))
        r2 = float(1 - np.sum((k * pred - y) ** 2) / np.sum((y - y.mean()) ** 2))
        out.append({"shot": shot, "n_samples": int(m.sum()),
                    "scale_factor": k, "r2_ip_from_q95": r2})
    return pd.DataFrame(out)


def verdicts(dep: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sig, d in DEFINITIONS.items():
        g = dep[dep.signal == sig]
        med_corr = float(g.abs_corr_with_ip_form.median()) if len(g) else float("nan")
        med_scat = float(g.rel_scatter_ip_removed.median()) if len(g) else float("nan")
        if d["contains_ip"] == "is_target":
            v, why = "TARGET", "this is the reconstruction target"
        elif d["contains_ip"] == "explicit":
            v = "TARGET_DEPENDENT"
            why = (f"I_p appears explicitly in the definition; empirical "
                   f"|corr| with the I_p form = {med_corr:.3f}")
            if np.isfinite(med_scat):
                why += (f"; removing I_p algebraically leaves "
                        f"{med_scat*100:.1f}% relative scatter")
        elif d["contains_ip"] == "via_equilibrium":
            # EFIT is constrained by measured I_p and no archived record severs
            # that dependence -> unresolved, conservatively dependent.
            v = "PROVENANCE_UNRESOLVED"
            why = ("EFIT equilibrium output; EFIT is constrained by measured "
                   f"I_p and the archive records no lineage. |corr| with I_p = "
                   f"{med_corr:.3f}. Conservative rule -> treat as "
                   "target-dependent")
        else:
            # Ancestry is DEFINITIONAL/COMPUTATIONAL, not statistical.
            # A direct diagnostic does not become target-dependent merely
            # because it correlates with the target: W_dia, P_NBI and n_e
            # co-evolve with I_p within a discharge, and treating correlation
            # as leakage would make every reconstruction task inadmissible.
            # Correlation is reported as context only.
            v = "TARGET_INDEPENDENT"
            why = (f"direct diagnostic ({d['diagnostic']}); I_p does not enter "
                   f"its computation and it is not EFIT-derived. |corr| with "
                   f"I_p = {med_corr:.3f} reflects shared discharge evolution, "
                   f"not upstream dependence")
        rows.append({"signal": sig, "display": d["display"],
                     "diagnostic": d["diagnostic"], "formula": d["formula"],
                     "efit_derived": d["efit_derived"],
                     "median_abs_corr_with_ip_form": med_corr,
                     "median_rel_scatter_ip_removed": med_scat,
                     "verdict": v,
                     "conservative_admissible_for_qrec":
                         v == "TARGET_INDEPENDENT",
                     "reason": why})
    return pd.DataFrame(rows)


def propagate(verd: pd.DataFrame) -> pd.DataFrame:
    """Propagate signal verdicts onto the frozen REL10 / RAW10 supports."""
    summary = json.loads(
        (ROOT / "Figure_data" / "d3d_reconstruction_summary.json")
        .read_text(encoding="utf-8"))["reconstruction"]
    admissible = set(verd[verd.conservative_admissible_for_qrec].signal)
    rows = []
    for rep, feats in (("REL10", summary["rel10_features"]),
                       ("RAW10", summary["raw10_features"])):
        for f in feats:
            prims = [s for s in DEFINITIONS if s in f.lower()]
            bad = [p for p in prims if p not in admissible]
            rows.append({"representation": rep, "feature": f,
                         "primitives": ";".join(prims),
                         "target_dependent_primitives": ";".join(bad),
                         "admissible": len(bad) == 0})
    return pd.DataFrame(rows)


def feasibility(files, verd: pd.DataFrame) -> dict:
    """Can I_p be reconstructed at all from the target-independent set?

    Not a replacement search -- a feasibility probe establishing whether a
    corrected q_rec universe can support the task at all.
    """
    adm = sorted(verd[verd.conservative_admissible_for_qrec].signal)
    rows = []
    for f in files:
        shot = Path(f).name.split("_")[1]
        g = loader(f)
        ip_d, ip_t = g("ip")
        ok = np.isfinite(ip_t) & np.isfinite(ip_d) & (np.abs(ip_d) > 1e5)
        tref = ip_t[ok]
        y = np.abs(ip_d[ok])
        if len(tref) < 200:
            continue
        cols = []
        for s in adm:
            try:
                cols.append(onto(g, s, tref))
            except KeyError:
                pass
        if not cols:
            continue
        X = np.column_stack(cols)
        m = np.isfinite(X).all(axis=1) & np.isfinite(y)
        if m.sum() < 200:
            continue
        Xm, ym = X[m], y[m]
        n = len(ym)
        cut = int(0.8 * n)
        mu, sd = Xm[:cut].mean(0), Xm[:cut].std(0)
        sd[sd <= 0] = 1.0
        Z = np.column_stack([np.ones(n), (Xm - mu) / sd])
        beta, *_ = np.linalg.lstsq(Z[:cut], ym[:cut], rcond=None)
        pred = Z[cut:] @ beta
        yt = ym[cut:]
        rows.append({"shot": shot, "n_eval": int(len(yt)),
                     "rmse_norm": float(np.sqrt(np.mean((pred - yt) ** 2))
                                        / (np.std(ym[:cut]) or 1.0)),
                     "r2": float(1 - np.sum((pred - yt) ** 2)
                                 / max(np.sum((yt - yt.mean()) ** 2), 1e-12))})
    df = pd.DataFrame(rows)
    return {"admissible_signals": adm, "n_shots": int(len(df)),
            "median_normalised_rmse": float(df.rmse_norm.median()) if len(df) else None,
            "median_r2": float(df.r2.median()) if len(df) else None,
            "frac_r2_above_0": float((df.r2 > 0).mean()) if len(df) else None,
            "per_shot": df.to_dict("records")}


def main() -> None:
    files = sorted(glob.glob(str(DATA / "shot_*_resampled.npz")))
    print(f"{AUDIT_ID}\n  shots: {len(files)}\n")

    dep = empirical_dependence(files)
    dep.to_csv(FIG6 / "qrec_provenance_dependence_by_shot.csv", index=False)

    inv = inversion_test(files)
    inv.to_csv(FIG6 / "qrec_ip_from_q95_inversion.csv", index=False)

    verd = verdicts(dep)
    verd.to_csv(FIG6 / "qrec_provenance_verdicts.csv", index=False)
    print(verd[["signal", "verdict", "median_abs_corr_with_ip_form",
                "median_rel_scatter_ip_removed"]].to_string(index=False))

    dag = []
    for _, r in verd.iterrows():
        dag.append({"node": r.signal, "kind": "raw_signal",
                    "parents": "I_p" if r.verdict in
                    ("TARGET_DEPENDENT", "PROVENANCE_UNRESOLVED") else "",
                    "verdict": r.verdict, "formula": r.formula})
    prop = propagate(verd)
    for _, r in prop.iterrows():
        dag.append({"node": f"{r.representation}:{r.feature}", "kind": "coordinate",
                    "parents": r.primitives,
                    "verdict": "ADMISSIBLE" if r.admissible else "TARGET_DEPENDENT",
                    "formula": ""})
    pd.DataFrame(dag).to_csv(FIG6 / "qrec_provenance_dag.csv", index=False)
    prop.to_csv(FIG6 / "qrec_support_admissibility.csv", index=False)

    print(f"\ninversion: I_p from a^2 B_t / q95, one scale factor per shot")
    print(f"  median R^2 = {inv.r2_ip_from_q95.median():.4f}  "
          f"n(R^2>0.9) = {(inv.r2_ip_from_q95 > 0.9).sum()}/{len(inv)}")

    for rep in ("REL10", "RAW10"):
        g = prop[prop.representation == rep]
        print(f"\n{rep}: {(~g.admissible).sum()}/{len(g)} features carry "
              f"target-dependent ancestry")

    feas = feasibility(files, verd)
    print(f"\nfeasibility of a corrected target-independent universe")
    print(f"  admissible signals: {feas['admissible_signals']}")
    print(f"  shots: {feas['n_shots']}  median normalised RMSE: "
          f"{feas['median_normalised_rmse']}")
    print(f"  median R^2 (held-out 20%): {feas['median_r2']}  "
          f"frac R^2>0: {feas['frac_r2_above_0']}")

    gate_failed = bool((~prop.admissible).any())
    manifest = {
        "audit_id": AUDIT_ID,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "seed": SEED,
        "data_dir": str(DATA), "n_shots": len(files),
        "documentary_provenance_available": False,
        "documentary_provenance_note":
            "Archive metadata records only resampling method/category. No "
            "physical provenance or upstream diagnostic lineage is recorded, so "
            "documentary provenance could not be established and the "
            "conservative rule was applied.",
        "thresholds": {"abs_corr": CORR_THRESHOLD,
                       "rel_scatter": SCATTER_THRESHOLD},
        "verdicts": verd.set_index("signal")["verdict"].to_dict(),
        "decision_gate": {
            "rule": "if the REL141/REL10 universe contains ANY target-dependent "
                    "or unresolved coordinate, q_rec is NOT figure-ready",
            "failed": gate_failed,
            "REL10_leaking_features": int((~prop[prop.representation == "REL10"]
                                           .admissible).sum()),
            "RAW10_leaking_features": int((~prop[prop.representation == "RAW10"]
                                           .admissible).sum()),
            "consequence": ("RETIRED_FOR_PROVENANCE_LEAKAGE" if gate_failed
                            else "PASS"),
        },
        "corrected_universe_feasibility": {
            k: v for k, v in feas.items() if k != "per_shot"},
        "operation_classification": "AUDITED_EXTERNAL_ANALYSIS",
        "operation_note":
            "Dalia serves the DIII-D signals and the transform family, but "
            "exposes no provenance-lineage primitive, so this audit is an "
            "external harness reading the same archived NPZ inputs.",
    }
    (HERE / "PROVENANCE_AUDIT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"\n{'='*64}")
    print(f"DECISION GATE {'FAILED' if gate_failed else 'PASSED'}")
    print(f"{'='*64}")


if __name__ == "__main__":
    main()
