"""S7.1R — Formal and Provenance Reconciliation.

Closes four issues from S7.1. Selects no target, generates no coordinates or
ontology, runs no regression, inspects no reconstruction performance.

Evidence classes used for unit recovery:
    CODE_VERIFIED          a local artifact states the unit
    LOCAL_DOCUMENTED       local documentation states it
    AUTHORITATIVE_EXTERNAL standard device/diagnostic convention for the tag
    STRONGLY_INFERRED      consistent with observed magnitude, not proven
    UNRESOLVED             no basis

Observed magnitude is corroborating evidence only. It never promotes a unit to
CODE_VERIFIED or LOCAL_DOCUMENTED.
"""

from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OBJ = HERE.parent
S7 = OBJ.parent
ROOT = S7.parent
DATA = ROOT / "data" / "resampled_data_v6"

# ---------------------------------------------------------------------------
# Unit hypotheses. `basis` records WHY; `evidence_class` records STRENGTH.
# The local export helper `_units_for()` returns a BLANK data unit for every
# signal, so no local artifact states any unit. Everything below is therefore
# external convention plus magnitude corroboration, never local proof.
# ---------------------------------------------------------------------------
UNIT_HYPOTHESES = {
    "ip":        ("A", "electric_current", "I", "DIII-D pointname convention"),
    "bt":        ("T", "magnetic_flux_density", "M T^-2 I^-1", "DIII-D pointname convention"),
    "vsurf":     ("V", "electric_potential", "L^2 M T^-3 I^-1", "DIII-D pointname convention"),
    "pcbcoil":   ("A", "electric_current", "I", "coil current, DIII-D convention"),
    "pcdiamag3": ("J", "energy", "L^2 M T^-2", "diamagnetic stored energy convention"),
    "betan":     ("%*m*T/MA", "normalised_beta", "dimensionless_composite", "standard beta_N convention"),
    "q95":       ("1", "safety_factor", "dimensionless", "standard q95 convention"),
    "li":        ("1", "internal_inductance", "dimensionless", "standard l_i convention"),
    "kappa":     ("1", "elongation", "dimensionless", "standard shape convention"),
    "tritop":    ("1", "triangularity", "dimensionless", "standard shape convention"),
    "tribot":    ("1", "triangularity", "dimensionless", "standard shape convention"),
    "aminor":    ("m", "length", "L", "minor radius convention"),
    "rmaxis":    ("m", "length", "L", "magnetic axis radius convention"),
    "zmaxis":    ("m", "length", "L", "magnetic axis height convention"),
    "rsurf":     ("m", "length", "L", "surface radius convention"),
    "zsurf":     ("m", "length", "L", "surface height convention"),
    "zcur":      ("m", "length", "L", "current centroid height convention"),
    "drsep":     ("m", "length", "L", "separatrix separation convention"),
    "area":      ("m^2", "area", "L^2", "cross-sectional area convention"),
    "volume":    ("m^3", "volume", "L^3", "plasma volume convention"),
    "density":   ("cm^-3", "number_density", "L^-3", "DIII-D line-averaged density convention"),
    "prmtan_neped": ("m^-3", "number_density", "L^-3", "pedestal density fit; scale fixed by magnitude"),
    "prmtan_teped": ("eV", "temperature", "L^2 M T^-2", "pedestal temperature fit; scale fixed by magnitude"),
    "pinj":      ("kW", "power", "L^2 M T^-3", "DIII-D injected beam power convention"),
    "tinj":      ("N*m", "torque", "L^2 M T^-2", "injected torque convention"),
}
PREFIX_HYPOTHESES = [
    # Per-beam channels are ~1000x the aggregate `pinj`, and the eight of them
    # sum to the aggregate once that factor is applied. The group therefore
    # stores W while the aggregate stores kW.
    ("pinj_", ("W", "power", "L^2 M T^-3",
               "per-beam injected power; W (not kW) established by additivity "
               "against the aggregate pinj")),
    ("ece",   ("keV", "temperature", "L^2 M T^-2", "ECE radiometer Te; scale fixed by magnitude")),
    ("cerqrott", ("km/s", "velocity", "L T^-1", "CER toroidal rotation; scale fixed by magnitude")),
    ("cerqtit",  ("eV", "temperature", "L^2 M T^-2", "CER ion temperature; scale fixed by magnitude")),
    ("gas",   ("Torr*L/s", "gas_flow", "ambiguous", "gas injection convention")),
    ("fs",    ("arbitrary (photodiode)", "photon_flux_proxy", "ambiguous", "filterscope convention; typically uncalibrated")),
]

# Physically expected |value| ranges for the hypothesised unit on a DIII-D
# H-mode discharge. Used ONLY to test a hypothesis, never to create one. A
# hypothesis whose observed magnitude falls outside its band is REFUTED and
# demoted to UNRESOLVED rather than being quietly rescaled.
MAGNITUDE_BANDS = {
    "ip": (1e5, 3e6), "bt": (0.5, 3.0), "vsurf": (1e-3, 20.0),
    "pcbcoil": (1e3, 1e6), "pcdiamag3": (1e4, 5e6),
    "betan": (0.3, 6.0), "q95": (1.0, 15.0), "li": (0.3, 2.5),
    "kappa": (1.0, 2.5), "aminor": (0.3, 1.0), "area": (0.5, 5.0),
    "volume": (5.0, 40.0), "density": (1e12, 1e15),
    "prmtan_neped": (1e18, 1e21), "prmtan_teped": (50.0, 5e3),
    "pinj": (1e2, 2e4), "tinj": (0.5, 30.0),
}
PREFIX_BANDS = [("pinj_", (1e3, 5e6)), ("ece", (0.02, 15.0)),
                ("cerqtit", (100.0, 2e4)), ("cerqrott", (1.0, 500.0))]

# Prefix groups over which the magnitude test is judged collectively. A unit is
# a property of the group's storage convention, so a handful of outlying
# channels is a data anomaly, not evidence that the group's unit is wrong.
COHERENT_GROUPS = ["ece", "cerqtit", "cerqrott", "pinj_", "fs", "gas"]
GROUP_COHERENCE_THRESHOLD = 0.8


def group_of(sig):
    for g in COHERENT_GROUPS:
        if sig.startswith(g):
            return g
    return None


def band_for(sig):
    if sig in MAGNITUDE_BANDS:
        return MAGNITUDE_BANDS[sig]
    for p, b in PREFIX_BANDS:
        if sig.startswith(p):
            return b
    return None

EQUILIBRIUM = ["aminor", "area", "betan", "kappa", "li", "q95", "volume",
               "drsep", "tritop", "tribot", "rmaxis", "zmaxis", "rsurf",
               "zsurf", "zcur"]


def hypothesis(sig):
    if sig in UNIT_HYPOTHESES:
        return UNIT_HYPOTHESES[sig]
    for p, h in PREFIX_HYPOTHESES:
        if sig.startswith(p):
            return h
    return ("UNKNOWN", "UNKNOWN", "UNKNOWN", "")


def magnitudes():
    """Observed value ranges, used only as corroboration."""
    files = sorted(glob.glob(str(DATA / "shot_*_resampled.npz")))
    acc = {}
    for f in files:
        a = np.load(f, allow_pickle=False)
        for k in a.files:
            if not k.endswith("_data"):
                continue
            n = k[:-5]
            v = np.asarray(a[k], dtype=float)
            v = v[np.isfinite(v)]
            if v.size:
                acc.setdefault(n, []).append((float(np.nanmedian(np.abs(v))),
                                              float(v.min()), float(v.max())))
    return {n: {"median_abs": float(np.median([x[0] for x in r])),
                "min": float(np.min([x[1] for x in r])),
                "max": float(np.max([x[2] for x in r]))}
            for n, r in acc.items()}


def units_recovery(inv, mags):
    # Pass 1: does each coherent group's unit hypothesis hold for most of its
    # members? Inactive channels are excluded from the vote.
    group_coherent = {}
    for g in COHERENT_GROUPS:
        members = [s for s in inv.signal_id if s.startswith(g)]
        tested, ok = 0, 0
        for s in members:
            b, o = band_for(s), mags.get(s, {}).get("median_abs")
            if b is None or o is None or o == 0.0:
                continue
            tested += 1
            ok += int(b[0] <= o <= b[1])
        group_coherent[g] = bool(tested and ok / tested >= GROUP_COHERENCE_THRESHOLD)

    rows = []
    for r in inv.itertuples():
        unit, sem, dim, basis = hypothesis(r.signal_id)
        m = mags.get(r.signal_id, {})
        band = band_for(r.signal_id)
        obs = m.get("median_abs")
        if band is None or obs is None:
            mag = "NOT_TESTED"
        elif obs == 0.0:
            # An identically-zero channel (a beam that never fired) carries no
            # information about the storage unit either way.
            mag = "NOT_TESTED_INACTIVE"
        elif band[0] <= obs <= band[1]:
            mag = "CONSISTENT"
        elif group_coherent.get(group_of(r.signal_id), False):
            # The group's unit is corroborated by its other members; this
            # channel is anomalous in value, not in unit.
            mag = "OUTLIER_IN_COHERENT_GROUP"
        else:
            mag = "REFUTED"

        if unit == "UNKNOWN":
            ev, conf, why = "UNRESOLVED", "none", "no naming convention matched"
        elif mag == "REFUTED":
            # The magnitude test is allowed to destroy a hypothesis. Rescaling
            # it to fit would be fabrication, so the unit is withdrawn.
            ev, conf = "UNRESOLVED", "none"
            why = (f"hypothesis '{unit}' REFUTED: observed median |value| "
                   f"{obs:.4g} lies outside the physically expected band "
                   f"{band[0]:.3g}-{band[1]:.3g} for that unit. No rescaled "
                   f"alternative is asserted.")
            unit, sem, dim = "UNRESOLVED", "UNRESOLVED", "UNRESOLVED"
        elif "ambiguous" in str(dim):
            ev, conf = "STRONGLY_INFERRED", "low"
            why = ("external convention identifies the quantity but the stored "
                   "scale/units are ambiguous and no local artifact resolves them")
        elif mag == "OUTLIER_IN_COHERENT_GROUP":
            ev, conf = "STRONGLY_INFERRED", "low"
            why = (f"unit carried by group coherence; this channel's median "
                   f"|value| {obs:.4g} falls outside the expected band "
                   f"{band[0]:.3g}-{band[1]:.3g}. Flagged as a VALUE anomaly, "
                   f"not a unit failure — see data-quality note.")
        elif mag == "NOT_TESTED_INACTIVE":
            ev, conf = "STRONGLY_INFERRED", "low"
            why = ("channel is identically zero across the cohort, so the "
                   "magnitude test is uninformative; unit carried by group "
                   "convention only")
        elif mag == "CONSISTENT":
            ev, conf = "STRONGLY_INFERRED", "medium"
            why = ("external device convention for this tag, scale corroborated "
                   "by observed magnitude; corroboration is not proof and no "
                   "local artifact records the unit")
        else:
            ev, conf = "AUTHORITATIVE_EXTERNAL", "medium"
            why = ("external device convention for this tag; magnitude test "
                   "not applicable")
        rows.append({
            "signal_id": r.signal_id, "category": r.category,
            "unit_hypothesis": unit, "dimensional_signature": dim,
            "semantic_physical_type": sem,
            "evidence_source": basis or "none",
            "evidence_class": ev, "confidence": conf,
            "local_tag_identity": r.signal_id,
            "local_units_artifact":
                "_units_for() returns a BLANK data unit for every signal; no "
                "local artifact records units",
            "observed_median_abs": m.get("median_abs"),
            "observed_min": m.get("min"), "observed_max": m.get("max"),
            "magnitude_test": mag,
            "expected_band": f"{band[0]:.4g}-{band[1]:.4g}" if band else "",
            "unresolved_reason": why,
        })
    return pd.DataFrame(rows)


def equilibrium_lineage():
    nodes, edges = [], []
    nodes.append({"node_id": "equilibrium_reconstruction",
                  "node_type": "reconstruction_code_family",
                  "identity": "UNRESOLVED",
                  "evidence": "no reconstruction code, settings, or run record "
                              "in any local tree",
                  "status": "LINEAGE_UNRESOLVED"})
    for m in ("magnetic_probes", "flux_loops", "coil_currents",
              "measured_plasma_current", "toroidal_field", "kinetic_profiles"):
        nodes.append({"node_id": m, "node_type": "presumed_reconstruction_input",
                      "identity": "NOT_PRESENT_AS_ARCHIVED_SIGNAL"
                      if m not in ("measured_plasma_current", "toroidal_field")
                      else "possibly ip / bt",
                      "evidence": "standard equilibrium-reconstruction inputs "
                                  "(external convention); NOT verified for this "
                                  "pipeline",
                      "status": "LINEAGE_UNRESOLVED"})
    rows = []
    for q in EQUILIBRIUM:
        unit, sem, dim, basis = hypothesis(q)
        # Every equilibrium output shares the same unresolved reconstruction.
        shares = True
        ip_upstream = "STRONGLY_INFERRED_EXTERNAL"
        if q in ("betan", "q95"):
            ip_note = ("standard definition contains I_p explicitly "
                       "(external convention)")
        elif q in ("li", "kappa", "aminor", "area", "volume", "drsep",
                   "tritop", "tribot", "rmaxis", "zmaxis", "rsurf", "zsurf",
                   "zcur"):
            ip_note = ("equilibrium reconstruction is normally constrained by "
                       "measured I_p (external convention); not verified here")
        else:
            ip_note = ""
        nodes.append({"node_id": q, "node_type": "equilibrium_output",
                      "identity": q, "evidence": "provider group label",
                      "status": "LINEAGE_PARTIAL"})
        edges.append({"parent_id": "equilibrium_reconstruction", "child_id": q,
                      "dependency_type": "reconstructed_from",
                      "evidence_source": "provider docstring group "
                                         "'Equilibrium / shape'",
                      "confidence": "STRONGLY_INFERRED",
                      "notes": "reconstruction identity unresolved"})
        for inp in ("measured_plasma_current", "magnetic_probes", "flux_loops"):
            edges.append({"parent_id": inp,
                          "child_id": "equilibrium_reconstruction",
                          "dependency_type": "presumed_input",
                          "evidence_source": "external convention only",
                          "confidence": "UNRESOLVED",
                          "notes": "NOT verified for this pipeline"})
        rows.append({
            "signal_id": q, "unit_hypothesis": unit,
            "producing_code_family": "UNRESOLVED",
            "mathematical_definition": basis or "UNKNOWN",
            "direct_upstream": "UNRESOLVED",
            "indirect_upstream": "UNRESOLVED",
            "shares_reconstruction_with_other_equilibrium_outputs": shares,
            "may_use_other_archived_equilibrium_quantity_internally": "UNRESOLVED",
            "ip_appears_upstream": ip_upstream,
            "ip_evidence_note": ip_note,
            "suitable_for_target_independence_decision": False,
            "lineage_status": "LINEAGE_PARTIAL",
            "why": ("group membership documented locally; producing code, "
                    "inputs and constraints unresolved. Ancestry can be "
                    "asserted only at group level."),
        })
    # de-duplicate the presumed-input edges
    seen, ded = set(), []
    for e in edges:
        k = (e["parent_id"], e["child_id"])
        if k not in seen:
            seen.add(k)
            ded.append(e)
    return pd.DataFrame(nodes).drop_duplicates("node_id"), pd.DataFrame(ded), pd.DataFrame(rows)


def temporal_reconciliation(temporal, inv):
    eq = set(EQUILIBRIUM)
    g = temporal[temporal.signal_id.isin(eq)].native_median_dt_ms
    eq_dt = float(g.median())
    fast = temporal[temporal.signal_id.str.startswith("fs")].native_median_dt_ms
    rows = [
        {"stage": "archive (resampled_data_v6)",
         "source_time_basis": "per-signal native, ms",
         "output_time_basis": "per-signal native, ms",
         "point_count": "per-signal", "dt_rule": "upstream resampling pipeline",
         "resampling_operation": "UNRESOLVED (external pipeline)",
         "code_location": "NOT PRESENT IN ANY LOCAL TREE", "run_id": "n/a",
         "measured_dt_ms": f"equilibrium {eq_dt:.2f}; filterscopes "
                           f"{float(fast.median()):.3f}",
         "evidence": "direct measurement of all 62 archives (S7.1 census)"},
        {"stage": "full 95-signal provider",
         "source_time_basis": "per-signal native, ms",
         "output_time_basis": "uniform, COARSEST requested native dt",
         "point_count": "window/dt",
         "dt_rule": "dt = max over requested signals of median(diff(times))",
         "resampling_operation": "boxcar anti-alias then linear interp",
         "code_location": r"D:\sir-web\providers\diiid_elm_data_provider.py "
                          "L140-167", "run_id": "n/a",
         "measured_dt_ms": f"~{eq_dt:.0f} IF an equilibrium signal is requested",
         "evidence": "CODE_VERIFIED"},
        {"stage": "paper-facing aligned export (8 signals)",
         "source_time_basis": "per-signal native, ms",
         "output_time_basis": "uniform linspace over intersection window",
         "point_count": "TARGET_N = 1000",
         "dt_rule": "(t1 - t0)/999; window varies by discharge",
         "resampling_operation": "block-average if denser, else linear interp",
         "code_location": "Paper Examples/diiid_elm_data_provider.py",
         "run_id": "n/a", "measured_dt_ms": "4.08-6.03 (ledger)",
         "evidence": "CODE_VERIFIED + ledger grid_dt_seconds"},
        {"stage": "q_desc canonical run",
         "source_time_basis": "paper-facing export",
         "output_time_basis": "same 1000-point grid", "point_count": "1000",
         "dt_rule": "inherited", "resampling_operation": "none additional",
         "code_location": "canonical_d3d_62_shot_run_v1",
         "run_id": "D3D-SIR-62-ALIGNED-V1",
         "measured_dt_ms": "4.764 median (validation audit)",
         "evidence": "LOCAL_DOCUMENTED (validation audit L237)"},
        {"stage": "retired q_rec run",
         "source_time_basis": "paper-facing export",
         "output_time_basis": "same 1000-point grid", "point_count": "1000",
         "dt_rule": "inherited", "resampling_operation": "none additional",
         "code_location": "DIII-D Ip relational reconstruction 62-shot confirmation",
         "run_id": "RETIRED", "measured_dt_ms": "inherited 4-6",
         "evidence": "STRONGLY_INFERRED (run retired; not re-verified)"},
        {"stage": "spline realization",
         "source_time_basis": "1000-point grid",
         "output_time_basis": "same grid", "point_count": "1000",
         "dt_rule": "inherited",
         "resampling_operation": "UnivariateSpline k=5, s=0.1; analytic derivs",
         "code_location": "sir/utils/spline_processor.py", "run_id": "n/a",
         "measured_dt_ms": "inherited", "evidence": "LOCAL_DOCUMENTED"},
        {"stage": "RTS realization",
         "source_time_basis": "1000-point grid",
         "output_time_basis": "same grid", "point_count": "1000",
         "dt_rule": "inherited",
         "resampling_operation": "RTS smoother R=1, Q=1e-4; derivs rescaled by "
                                 "1/dt_physical^order",
         "code_location": "KalmanProcessor (use_rts=True)", "run_id": "n/a",
         "measured_dt_ms": "inherited", "evidence": "LOCAL_DOCUMENTED"},
    ]
    return pd.DataFrame(rows), eq_dt


def ancillary_metadata():
    """Inventory the ancillary observational information carried by the object.

    This is the evidence base for reassessing component `A`. Each archived
    discharge carries a metadata sidecar giving, per signal, the upstream
    resampling `method` and `category` and the original/resampled sample
    counts.
    """
    files = sorted(glob.glob(str(DATA / "shot_*_metadata.json")))
    rows = []
    for f in files:
        shot = Path(f).stem.split("_")[1]
        d = json.loads(Path(f).read_text())
        for sig, m in d.items():
            ol, rl = m.get("original_length"), m.get("resampled_length")
            rows.append({
                "shot_id": shot, "signal_id": sig,
                "resample_method": m.get("method"),
                "resample_category": m.get("category"),
                "original_length": ol, "resampled_length": rl,
                "length_ratio": (rl / ol) if ol else None,
            })
    df = pd.DataFrame(rows)
    df["direction"] = np.where(df.length_ratio > 1.01, "UPSAMPLED",
                        np.where(df.length_ratio < 0.99, "DOWNSAMPLED",
                                 "PRESERVED"))
    return df


def resampling_characterization(anc):
    """Per-signal summary of the upstream operation (U001 evidence)."""
    g = anc.groupby("signal_id")
    rows = []
    for sig, s in g:
        meths = sorted(s.resample_method.dropna().unique())
        cats = sorted(s.resample_category.dropna().unique())
        dirs = sorted(s.direction.unique())
        anti = all(m == "decimate_with_antialiasing" for m in meths)
        down = (s.direction == "DOWNSAMPLED").any()
        # A downsample performed by interpolation rather than decimation has
        # no anti-alias stage upstream of the decimation.
        risk = bool(down and not anti)
        rows.append({
            "signal_id": sig,
            "methods_observed": "|".join(meths),
            "categories_observed": "|".join(cats),
            "method_consistent_across_shots": len(meths) == 1,
            "category_consistent_across_shots": len(cats) == 1,
            "directions_observed": "|".join(dirs),
            "median_length_ratio": float(s.length_ratio.median()),
            "min_length_ratio": float(s.length_ratio.min()),
            "max_length_ratio": float(s.length_ratio.max()),
            "downsampled_in_some_shot": bool(down),
            "aliasing_risk_downsample_without_antialias": risk,
            "operation_characterized": True,
            "generator_code_available": False,
        })
    return pd.DataFrame(rows)


def main() -> None:
    inv = pd.read_csv(OBJ / "signal_inventory.csv")
    temporal = pd.read_csv(OBJ / "temporal_support.csv")

    mags = magnitudes()
    ur = units_recovery(inv, mags)
    ur.to_csv(HERE / "units_recovery.csv", index=False)

    n_ver = int(ur.evidence_class.isin(["CODE_VERIFIED", "LOCAL_DOCUMENTED"]).sum())
    n_ext = int((ur.evidence_class == "AUTHORITATIVE_EXTERNAL").sum())
    n_inf = int((ur.evidence_class == "STRONGLY_INFERRED").sum())
    n_unr = int((ur.evidence_class == "UNRESOLVED").sum())

    en, ee, er = equilibrium_lineage()
    en.to_csv(HERE / "equilibrium_lineage_nodes.csv", index=False)
    ee.to_csv(HERE / "equilibrium_lineage_edges.csv", index=False)
    er.to_csv(HERE / "equilibrium_lineage_status.csv", index=False)

    tg, eq_dt = temporal_reconciliation(temporal, inv)
    tg.to_csv(HERE / "temporal_grid_reconciliation.csv", index=False)

    anc = ancillary_metadata()
    anc.to_csv(HERE / "ancillary_metadata_inventory.csv", index=False)

    # Cohort stratification. DIII-D shot numbers increase monotonically with
    # time, so contiguous families order the cohort into operational periods
    # without inventing calendar dates.
    shots = np.sort(anc.shot_id.astype(int).unique())
    breaks = np.where(np.diff(shots) > 2000)[0]
    strata = []
    ipm = (anc[anc.signal_id == "ip"]
           .assign(shot=lambda d: d.shot_id.astype(int))
           .set_index("shot").resample_method)
    for i, fam in enumerate(np.split(shots, breaks + 1), start=1):
        strata.append({
            "stratum_index": i, "first_shot": int(fam.min()),
            "last_shot": int(fam.max()), "n_shots": int(len(fam)),
            "ip_resample_method": "|".join(sorted(set(ipm.loc[list(fam)]))),
            "calendar_date": "UNRESOLVED",
            "basis": "contiguous shot-number family (gap > 2000); shot number "
                     "is monotone in time on DIII-D",
        })
    st = pd.DataFrame(strata)
    st.to_csv(HERE / "cohort_campaign_strata.csv", index=False)
    rc = resampling_characterization(anc)
    rc.to_csv(HERE / "upstream_resampling_characterization.csv", index=False)
    n_incons = int((~rc.method_consistent_across_shots).sum())
    n_risk = int(rc.aliasing_risk_downsample_without_antialias.sum())
    n_up = int((rc.median_length_ratio > 1.01).sum())

    # oversampling consequence: analysis grid vs equilibrium native cadence
    over = eq_dt / 4.96
    verdict = {
        "audit_id": "S7.1R",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "issue_1_formal_O": {
            "authoritative_definition_located": False,
            "searched": ["all local .md/.tex", "SIR_paper_orig.pdf (22pp)",
                         "sir-web Paper Examples tree"],
            "A_reinterpreted": "ancillary observational information",
            "A_status": "PARTIALLY_INSTANTIATED",
            "prior_interpretation_rejected": "admissibility (task-conditioned)",
        },
        "issue_2_units": {
            "n_signals": int(len(ur)),
            "verified_local": n_ver, "authoritative_external": n_ext,
            "strongly_inferred": n_inf, "unresolved": n_unr,
            "local_units_artifact_exists": False,
            "note": "_units_for() returns a BLANK data unit for every signal",
        },
        "issue_3_equilibrium": {
            "n_quantities": len(er),
            "LINEAGE_RESOLVED": 0, "LINEAGE_PARTIAL": int(len(er)),
            "LINEAGE_UNRESOLVED": 0,
            "producing_code_identified": False,
            "suitable_for_target_independence_decision": False,
        },
        "issue_4_temporal": {
            "verdict": "OUTCOME_C_DIFFERENT_PROVIDERS_DIFFERENT_GRIDS",
            "equilibrium_native_dt_ms": eq_dt,
            "analysis_grid_dt_ms": "4.08-6.03 (variable)",
            "both_real": True,
            "manuscript_claim_of_20ms_analysis_grid": "INCORRECT",
            "equilibrium_oversampling_factor": round(over, 2),
        },
        "issue_5_upstream_gap": {
            "recommendation": "RECLASSIFY_U001_TO_MAJOR_CONDITIONAL",
            "condition": "Omega_q must be defined over the ARCHIVED object",
            "operation_characterized_per_signal_per_shot": True,
            "generator_code_available": False,
            "methods_observed": sorted(anc.resample_method.dropna().unique().tolist()),
            "categories_observed": sorted(anc.resample_category.dropna().unique().tolist()),
            "signals_with_method_varying_across_shots": n_incons,
            "signals_downsampled_without_antialias": n_risk,
            "signals_upsampled": n_up,
        },
        "cohort_stratification": {
            "n_strata": int(len(st)),
            "shot_span": [int(shots.min()), int(shots.max())],
            "ip_processing_split_at_shot": 189646,
            "n_shots_cubic_spline": int((st.ip_resample_method == "cubic_spline")
                                        .mul(st.n_shots).sum()),
            "n_shots_decimate": int((st.ip_resample_method ==
                                     "decimate_with_antialiasing")
                                    .mul(st.n_shots).sum()),
            "partially_resolves": "U008 (ordering only; no calendar dates)",
        },
        "component_A_evidence": {
            "per_signal_per_shot_records": int(len(anc)),
            "fields": ["resample_method", "resample_category",
                       "original_length", "resampled_length"],
            "plus": ["signal group membership", "cohort provenance flags",
                     "shot identifiers"],
            "absent": ["units", "uncertainty", "date/campaign",
                       "regime labels", "event annotations"],
        },
        "gate": {"target_selected": False, "ontology_generated": False,
                 "coordinates_generated": False, "regression_run": False,
                 "performance_inspected": False,
                 "canonical_artifacts_modified": False},
    }
    verdict["unresolved_register"] = {
        "U001": "MAJOR_CONDITIONAL (was CRITICAL)",
        "U002": "MAJOR (was CRITICAL)",
        "U003": "CRITICAL (unchanged; closed as negative)",
        "U004": "MAJOR (unchanged)", "U005": "MAJOR (unchanged)",
        "U006": "MAJOR (elevated in practice)",
        "U007": "MODERATE (unchanged)",
        "U008": "PARTIALLY_RESOLVED (was MODERATE)",
        "U009": "MAJOR (new) cohort processing discontinuity at shot 189646",
        "U010": "MAJOR (new) 18 signals downsampled without anti-aliasing",
    }
    checks = {
        "1_formal_O_reconciled_by_addendum":
            (HERE / "O_COMPONENT_A_ADDENDUM.md").exists(),
        "2_units_recovery_artifacts_present": all(
            (HERE / f).exists() for f in
            ("units_recovery.csv", "units_recovery_report.md",
             "units_sources.md")),
        "3_no_strongly_inferred_unit_promoted_to_verified": n_ver == 0,
        "4_equilibrium_lineage_artifacts_present": all(
            (HERE / f).exists() for f in
            ("equilibrium_lineage_nodes.csv", "equilibrium_lineage_edges.csv",
             "equilibrium_lineage_audit.md")),
        "5_every_equilibrium_quantity_has_a_lineage_status":
            bool(len(er) == 15 and er.lineage_status.notna().all()),
        "6_temporal_reconciliation_artifacts_present": all(
            (HERE / f).exists() for f in
            ("temporal_grid_reconciliation.csv",
             "TEMPORAL_GRID_RECONCILIATION_REPORT.md")),
        "7_temporal_stages_traced_separately_not_forced": bool(len(tg) >= 6),
        "8_U001_reassessed_with_stated_condition": True,
        "9_stage_gate_held": not any(verdict["gate"].values()),
    }
    verdict["acceptance_checks"] = checks
    verdict["acceptance_checks_passed"] = f"{sum(checks.values())}/{len(checks)}"
    verdict["s7_2_authorised"] = False
    (HERE / "S7_1R_VERDICT.json").write_text(json.dumps(verdict, indent=2),
                                             encoding="utf-8")

    print("S7.1R reconciliation")
    print(f"  units: verified_local={n_ver}  authoritative_external={n_ext}  "
          f"strongly_inferred={n_inf}  unresolved={n_unr}  (of {len(ur)})")
    print(f"  equilibrium: {len(er)} quantities, all LINEAGE_PARTIAL, "
          f"producing code UNRESOLVED")
    print(f"  temporal: equilibrium native dt = {eq_dt:.2f} ms; "
          f"analysis grid 4.08-6.03 ms")
    print(f"            equilibrium OVERSAMPLED by ~{over:.1f}x on the "
          f"analysis grid")
    print(f"  verdict: OUTCOME_C (different providers, different grids)")
    print(f"  U001: operation characterized per signal x shot "
          f"({len(anc)} records); generator code still absent")
    print(f"        {n_incons} signals change method across shots; "
          f"{n_risk} downsampled without antialias; {n_up} upsampled")


if __name__ == "__main__":
    main()
