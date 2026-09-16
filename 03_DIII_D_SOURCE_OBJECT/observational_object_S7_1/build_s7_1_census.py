"""S7.1 — Observational Object and Provenance Census (build script).

Stage 1 ONLY. This script characterises the observational object O that is
actually possessed. It selects no target, generates no ontology, constructs no
coordinates, and runs no regression.

Evidence discipline
-------------------
Every classification carries an `evidence_class`:

    LOCAL_LINEAGE_EVIDENCE      provable from code/docs/data in the local trees
    EXTERNAL_DOMAIN_DOCUMENTATION
                                standard device/diagnostic physics, used only to
                                describe what a quantity *is*; it cannot prove
                                that this archived pipeline used that definition
    UNRESOLVED                  neither available

Where a classification cannot be supported, UNKNOWN is recorded rather than
guessed. Statistical correlation is never used as evidence of ancestry.

Outputs land in S7/01_observational_object/ and S7/_manifests/.
Nothing outside S7/ is written.
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

HERE = Path(__file__).resolve().parent
S7 = HERE.parent
ROOT = S7.parent                                  # DIIID_example
DATA = ROOT / "data" / "resampled_data_v6"
MAN = S7 / "_manifests"
SIRWEB = Path(r"D:\sir-web")
PAPERDIR = SIRWEB / "Paper Examples" / "Relational Coordinates for Multimodal Plasma Observations"
PROVDIR = PAPERDIR / "canonical_d3d_62_shot_provenance"

for d in (HERE, MAN, S7 / "_logs", S7 / "_legacy_reference"):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Signal groups, transcribed verbatim from the full provider docstring
#   D:\sir-web\providers\diiid_elm_data_provider.py  ("Representative signal
#   groups (95 signals per shot)")
# This is LOCAL_LINEAGE_EVIDENCE for CATEGORY only.
# ---------------------------------------------------------------------------
GROUP_PREFIXES = [
    ("equilibrium_shape", {"aminor", "area", "betan", "kappa", "li", "q95",
                           "volume", "drsep", "tritop", "tribot", "rmaxis",
                           "zmaxis", "rsurf", "zsurf", "zcur"}, ()),
    ("magnetics", {"bt", "ip", "pcbcoil", "pcdiamag3", "vsurf"}, ()),
    ("density", {"density", "prmtan_neped", "prmtan_teped"}, ()),
    ("ece_te_profile", set(), ("ece",)),
    ("cer_rotation_ti", set(), ("cerqrott", "cerqtit")),
    ("filterscope_dalpha", {"fs03da", "fs04", "fs04da", "fs05da"}, ("fs",)),
    ("gas_injection", {"gasa", "gasb", "gasc", "gasd"}, ("gas",)),
    ("neutral_beams", {"pinj", "tinj"}, ("pinj_",)),
]

# Direct/derived classification. `evidence` records WHY.
#   basis "provider_group"  -> the local provider docstring assigns the group
#   basis "device_physics"  -> external domain documentation about what the
#                              quantity is; cannot prove pipeline lineage
CLASS_RULES = {
    "equilibrium_shape": ("EQUILIBRIUM_DERIVED",
                          "provider docstring groups these as "
                          "'Equilibrium / shape'; equilibrium reconstruction "
                          "outputs, not stored primitives",
                          "LOCAL_LINEAGE_EVIDENCE"),
    "magnetics": ("UNKNOWN",
                  "provider groups these as 'Magnetics'; whether each is a raw "
                  "coil/loop measurement or a compensated derived quantity is "
                  "not established by any local artifact",
                  "UNRESOLVED"),
    "density": ("UNKNOWN",
                "provider groups these as 'Density'; prmtan_* names suggest a "
                "profile-fit product but no local code or doc establishes the "
                "fit or its inputs",
                "UNRESOLVED"),
    "ece_te_profile": ("DIAGNOSTIC_RECONSTRUCTION",
                       "provider docstring labels the group 'ECE (Te profiles)'; "
                       "a Te profile is a reconstruction from radiometer "
                       "channels, not a stored primitive",
                       "LOCAL_LINEAGE_EVIDENCE"),
    "cer_rotation_ti": ("DIAGNOSTIC_RECONSTRUCTION",
                        "provider docstring labels the group 'CER "
                        "(rotation / Ti)'; spectroscopic inference",
                        "LOCAL_LINEAGE_EVIDENCE"),
    "filterscope_dalpha": ("UNKNOWN",
                           "provider groups these as 'Filterscopes (D-alpha, "
                           "ELM markers)'; raw photodiode signal versus "
                           "processed marker is not established locally",
                           "UNRESOLVED"),
    "gas_injection": ("UNKNOWN",
                      "provider groups these as 'Gas injection'; actuator "
                      "command versus measured flow is not established locally",
                      "UNRESOLVED"),
    "neutral_beams": ("UNKNOWN",
                      "provider groups these as 'Neutral beams'; injected power "
                      "is normally an engineering-derived quantity but no local "
                      "artifact establishes the computation",
                      "UNRESOLVED"),
    "ungrouped": ("UNKNOWN", "not listed in the provider docstring groups",
                  "UNRESOLVED"),
}

HISTORICAL_EIGHT = ["pcdiamag3", "pinj", "density", "ip", "betan", "q95",
                    "li", "kappa"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def group_of(name: str) -> str:
    for g, exact, prefixes in GROUP_PREFIXES:
        if name in exact:
            return g
        for p in prefixes:
            if name.startswith(p):
                return g
    return "ungrouped"


# ===========================================================================
# 1. Freeze the input state
# ===========================================================================
def initial_state_manifest(shot_files):
    art = {}
    for p in [PROVDIR / "D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md",
              PROVDIR / "d3d_discharge_ledger.csv",
              PROVDIR / "build_d3d_discharge_ledger.py",
              PAPERDIR / "diiid_elm_data_provider.py",
              PAPERDIR / "SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py",
              SIRWEB / "providers" / "diiid_elm_data_provider.py",
              ROOT / "Figure_data" / "d3d_reconstruction_summary.json",
              ROOT / "Figure_data" / "d3d_description_support.csv",
              ROOT / "Figure_data" / "d3d_reconstruction_external_55.csv"]:
        if p.exists():
            st = p.stat()
            art[str(p)] = {"sha256": sha(p), "bytes": st.st_size,
                           "mtime_utc": datetime.fromtimestamp(
                               st.st_mtime, timezone.utc).isoformat()}
    shots = {}
    for f in shot_files:
        p = Path(f)
        st = p.stat()
        shots[p.name] = {"sha256": sha(p), "bytes": st.st_size,
                         "mtime_utc": datetime.fromtimestamp(
                             st.st_mtime, timezone.utc).isoformat()}
    man = {
        "stage": "S7.1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "seeds": {"note": "S7.1 is fully deterministic; no stochastic procedure"},
        "data_dir": str(DATA),
        "n_shot_npz": len(shot_files),
        "canonical_artifacts": art,
        "shot_files": shots,
        "canonical_modification_policy":
            "read-only; S7.1 writes only under S7/",
    }
    (MAN / "INITIAL_STATE_MANIFEST.json").write_text(
        json.dumps(man, indent=2), encoding="utf-8")
    return man


# ===========================================================================
# 2. Signal + shot + availability census
# ===========================================================================
def census(shot_files):
    per_shot, avail, quality, temporal = [], [], [], []
    signal_seen = {}

    for f in shot_files:
        shot = Path(f).name.split("_")[1]
        a = np.load(f, allow_pickle=False)
        names = sorted({k[:-5] for k in a.files if k.endswith("_data")})
        n_avail = 0
        t_lo, t_hi = [], []
        for n in names:
            d = np.asarray(a[n + "_data"], dtype=float)
            t = (np.asarray(a[n + "_times"], dtype=float)
                 if n + "_times" in a.files else np.full_like(d, np.nan))
            fin = np.isfinite(d)
            finite_frac = float(fin.mean()) if d.size else 0.0
            ok = fin & np.isfinite(t)
            n_avail += 1
            if ok.sum() >= 2:
                ts, te = float(np.min(t[ok])), float(np.max(t[ok]))
                dt = float(np.median(np.diff(np.sort(t[ok]))))
                t_lo.append(ts)
                t_hi.append(te)
            else:
                ts = te = dt = float("nan")
            avail.append({"shot_id": shot, "signal_id": n, "available": True,
                          "n_samples": int(d.size),
                          "valid_fraction": finite_frac,
                          "time_start_ms": ts, "time_end_ms": te,
                          "missing_fraction": float(1.0 - finite_frac),
                          "source_resolution_ms": dt, "notes": ""})
            v = d[fin]
            if v.size:
                uniq = int(np.unique(v).size)
                q = {"shot_id": shot, "signal_id": n,
                     "n": int(d.size), "finite_fraction": finite_frac,
                     "n_unique": uniq,
                     "repeat_ratio": float(1.0 - uniq / v.size),
                     "min": float(v.min()), "max": float(v.max()),
                     "mean": float(v.mean()), "std": float(v.std()),
                     "dynamic_range": float(v.max() - v.min()),
                     "near_constant": bool(v.std() <= 1e-12 * max(abs(v.mean()), 1.0)),
                     "frac_at_min": float(np.mean(v == v.min())),
                     "frac_at_max": float(np.mean(v == v.max())),
                     "n_outliers_4sigma": int(np.sum(
                         np.abs(v - v.mean()) > 4 * (v.std() or np.inf)))}
                quality.append(q)
            signal_seen.setdefault(n, 0)
            signal_seen[n] += 1
            temporal.append({"shot_id": shot, "signal_id": n,
                             "native_median_dt_ms": dt,
                             "time_start_ms": ts, "time_end_ms": te,
                             "n_native_samples": int(d.size)})
        per_shot.append({"shot_id": shot, "data_file": Path(f).name,
                         "start_time_ms": min(t_lo) if t_lo else float("nan"),
                         "end_time_ms": max(t_hi) if t_hi else float("nan"),
                         "duration_ms": (max(t_hi) - min(t_lo)) if t_lo else float("nan"),
                         "available_signal_count": n_avail,
                         "native_sample_count_total": int(sum(
                             np.asarray(a[n + "_data"]).size for n in names))})
    return (pd.DataFrame(per_shot), pd.DataFrame(avail),
            pd.DataFrame(quality), pd.DataFrame(temporal), signal_seen)


def signal_inventory(signal_seen, avail, temporal, n_shots):
    rows = []
    for n, cnt in sorted(signal_seen.items()):
        g = group_of(n)
        cls, why, ev = CLASS_RULES[g]
        A = avail[avail.signal_id == n]
        T = temporal[temporal.signal_id == n]
        rows.append({
            "signal_id": n, "canonical_name": n, "source_name": n,
            "aliases": "",
            "scientific_description": f"provider group: {g}",
            "category": g,
            "direct_or_derived": cls,
            "diagnostic_or_computed": (
                "computed" if cls in ("EQUILIBRIUM_DERIVED", "PHYSICS_DERIVED",
                                      "SOFTWARE_DERIVED")
                else "diagnostic" if cls == "DIAGNOSTIC_RECONSTRUCTION"
                else "UNKNOWN"),
            "units": "UNKNOWN",
            "dimensional_signature": "UNKNOWN",
            "sampling_rate_native_if_known": float(T.native_median_dt_ms.median()),
            "sampling_rate_analysis_if_known":
                "variable; common grid TARGET_N=1000, dt 4.1-6.0 ms",
            "time_basis": "per-signal <name>_times, MILLISECONDS",
            "shot_count_available": int(cnt),
            "missing_fraction": float(A.missing_fraction.mean()),
            "finite_fraction": float(A.valid_fraction.mean()),
            "source_path": str(DATA),
            "source_system": "resampled_data_v6 npz archive",
            "generating_formula_if_known": "UNKNOWN",
            "upstream_dependencies_if_known": "UNKNOWN",
            "preprocessing": "upstream resample (method in metadata json); "
                             "then provider finite-clean + sort + dedupe",
            "smoothing": "none at archive level; realization variants "
                         "none/spline/RTS applied downstream",
            "interpolation": "block-average if denser than grid, else linear",
            "standardization": "none at archive level; within-discharge z-score "
                               "applied downstream",
            "uncertainty_metadata": "NONE_RECORDED",
            "provenance_status": ev,
            "documentation_status": ("GROUP_DOCUMENTED" if g != "ungrouped"
                                     else "UNDOCUMENTED"),
            "availability_class": "AVAILABLE_IN_FROZEN_STUDY_OBJECT",
            "historical_eight": n in HISTORICAL_EIGHT,
            "classification_evidence": why,
            "evidence_class": ev,
            "notes": ("present in all shots" if cnt == n_shots
                      else f"present in {cnt}/{n_shots} shots"),
        })
    return pd.DataFrame(rows)


def provenance_graph(inv):
    nodes, edges = [], []
    for r in inv.itertuples():
        nodes.append({"node_id": r.signal_id, "node_type": "stored_series",
                      "category": r.category,
                      "direct_or_derived": r.direct_or_derived,
                      "evidence_class": r.evidence_class})
    for op, desc in (("upstream_resample",
                      "external pipeline, NOT checked into any local tree"),
                     ("provider_clean", "float64, drop non-finite, sort, dedupe"),
                     ("common_grid", "intersection window, linspace TARGET_N=1000"),
                     ("block_average_or_interp", "anti-alias then align")):
        nodes.append({"node_id": op, "node_type": "preprocessing_operation",
                      "category": "pipeline", "direct_or_derived": "N/A",
                      "evidence_class": "LOCAL_LINEAGE_EVIDENCE"})
    for r in inv.itertuples():
        edges.append({"parent_id": "upstream_resample", "child_id": r.signal_id,
                      "dependency_type": "produced_by",
                      "evidence_source": "shot metadata json records per-signal "
                                         "resample method/category",
                      "confidence": "DOCUMENTED",
                      "notes": "generator script itself is UNRESOLVED"})
        edges.append({"parent_id": r.signal_id, "child_id": "provider_clean",
                      "dependency_type": "consumed_by",
                      "evidence_source": "provider _load_signal",
                      "confidence": "CODE_VERIFIED", "notes": ""})
    for a, b in (("provider_clean", "common_grid"),
                 ("common_grid", "block_average_or_interp")):
        edges.append({"parent_id": a, "child_id": b,
                      "dependency_type": "pipeline_stage",
                      "evidence_source": "provider fetch_data",
                      "confidence": "CODE_VERIFIED", "notes": ""})
    # Equilibrium ancestry is asserted only at group level and remains unproven
    for r in inv[inv.category == "equilibrium_shape"].itertuples():
        edges.append({"parent_id": "equilibrium_reconstruction",
                      "child_id": r.signal_id,
                      "dependency_type": "reconstructed_from",
                      "evidence_source": "provider docstring group label "
                                         "'Equilibrium / shape'",
                      "confidence": "STRONGLY_INFERRED",
                      "notes": "the reconstruction code and its inputs are not "
                               "present in any local tree"})
    nodes.append({"node_id": "equilibrium_reconstruction",
                  "node_type": "equilibrium_reconstruction",
                  "category": "equilibrium_shape", "direct_or_derived": "N/A",
                  "evidence_class": "UNRESOLVED"})
    return pd.DataFrame(nodes), pd.DataFrame(edges)


def semantic_types(inv):
    rows = []
    for r in inv.itertuples():
        rows.append({"signal_id": r.signal_id, "physical_quantity": "UNKNOWN",
                     "units": "UNKNOWN", "dimensional_type": "UNKNOWN",
                     "structure": "scalar_time_series",
                     "signed_or_nonnegative": "UNKNOWN",
                     "extensive_or_intensive": "UNKNOWN",
                     "bounded_or_unbounded": "UNKNOWN",
                     "coordinate_role_candidates": "NOT_ASSIGNED_AT_S7_1",
                     "semantic_tags": r.category,
                     "evidence_class": "UNRESOLVED",
                     "notes": "no units table exists in any local artifact; "
                              "units must not be invented"})
    return pd.DataFrame(rows)


def unresolved_register(inv):
    R = []

    def add(i, sig, q, why, ev, fix, bt, bc, sev):
        R.append({"item_id": i, "signal_id": sig, "unresolved_question": q,
                  "why_it_matters": why, "evidence_checked": ev,
                  "possible_resolution": fix,
                  "blocks_future_target_selection": bt,
                  "blocks_future_coordinate_construction": bc, "severity": sev})

    add("U001", "ALL", "Who generated resampled_data_v6 and by what algorithm?",
        "The entire object rests on an upstream resampling pipeline that is not "
        "checked into any local tree; its filtering could alias or smooth "
        "structure that later coordinates depend on.",
        "sir-web repo, DIIID_example, shot metadata json, provenance doc "
        "section 2.1 (explicitly records UNKNOWN)",
        "recover the generator script or an upstream manifest", True, True,
        "CRITICAL")
    add("U002", "ALL", "Physical units for every signal.",
        "Dimensional signatures are required before a typed ontology can be "
        "built; without them dimensional consistency cannot be checked.",
        "npz archives (no units), metadata json (no units), provider docstrings "
        "(no units), provenance doc section 4.1 (records UNKNOWN)",
        "obtain a data dictionary from the upstream archive", False, True,
        "CRITICAL")
    add("U003", "equilibrium_shape",
        "Which equilibrium reconstruction produced these, and with which "
        "constraints and inputs?",
        "Equilibrium outputs may share upstream inputs with any future target; "
        "ancestry must be known before admissibility can be decided.",
        "provider docstrings (group label only), no reconstruction code or "
        "settings in any local tree",
        "locate the equilibrium reconstruction configuration for these shots",
        True, True, "CRITICAL")
    add("U004", "ALL", "Per-signal measurement uncertainty.",
        "No uncertainty metadata exists, so error models cannot be declared "
        "from data and E must be stated as NOT_INSTANTIATED.",
        "npz, metadata json, provider code, provenance doc section 6",
        "upstream diagnostic uncertainty tables", False, False, "MAJOR")
    add("U005", "ALL", "Cohort selection algorithm for the 62 discharges.",
        "Selection was on common-grid viability across all 95 signals; the "
        "exact algorithm and the parent population are unknown, so the "
        "observational domain cannot be described as a random or complete "
        "sample of any regime.",
        "provenance doc section 3.2 (records UNKNOWN); no candidate list or "
        "exclusion log in-repo",
        "recover the ELM-library selection script", False, False, "MAJOR")
    add("U006", "magnetics",
        "Are magnetics entries raw sensor signals or compensated quantities?",
        "Compensation (e.g. removing toroidal-field pickup) introduces upstream "
        "dependencies invisible from the stored name.",
        "provider group label only", "diagnostic documentation for these keys",
        True, True, "MAJOR")
    add("U007", "prmtan_neped;prmtan_teped",
        "Are the prmtan_* pedestal quantities profile-fit products, and fitted "
        "from what?",
        "A fit product carries the ancestry of everything entering the fit.",
        "provider group label only, no fitting code locally",
        "locate the pedestal fitting routine", True, True, "MODERATE")
    add("U008", "ALL",
        "Date range and operating regime of the discharges.",
        "The observational domain cannot be scientifically bounded without it; "
        "regime labels must not be invented from the traces.",
        "shot ids only; no date or regime field in any local artifact",
        "device logbook", False, False, "MODERATE")
    return pd.DataFrame(R)


def main() -> None:
    files = sorted(glob.glob(str(DATA / "shot_*_resampled.npz")))
    print(f"S7.1 census | shot files: {len(files)}")
    man = initial_state_manifest(files)
    print(f"  froze initial state: {len(man['canonical_artifacts'])} canonical "
          f"artifacts + {len(files)} shot files")

    shots, avail, quality, temporal, seen = census(files)
    inv = signal_inventory(seen, avail, temporal, len(files))
    nodes, edges = provenance_graph(inv)
    sem = semantic_types(inv)
    unres = unresolved_register(inv)

    shots["historical_qdesc_member"] = True
    shots["historical_qrec_development_member"] = shots.shot_id.isin(
        ["165022", "160721", "165861", "195264", "195626", "159310", "155537"])
    shots["historical_qrec_external_member"] = ~shots.historical_qdesc_member.eq(
        False) & ~shots.historical_qrec_development_member
    shots["regime_labels"] = "NOT_DOCUMENTED"
    shots["notes"] = ""

    inv.to_csv(HERE / "signal_inventory.csv", index=False)
    shots.to_csv(HERE / "shot_inventory.csv", index=False)
    avail.to_csv(HERE / "availability_by_shot.csv", index=False)
    (avail.assign(v=1).pivot_table(index="signal_id", columns="shot_id",
                                   values="v", fill_value=0)
     .to_csv(HERE / "availability_matrix.csv"))
    quality.to_csv(HERE / "signal_quality_summary.csv", index=False)
    temporal.to_csv(HERE / "temporal_support.csv", index=False)
    nodes.to_csv(HERE / "provenance_nodes.csv", index=False)
    edges.to_csv(HERE / "provenance_edges.csv", index=False)
    (HERE / "provenance_graph.json").write_text(json.dumps(
        {"nodes": nodes.to_dict("records"), "edges": edges.to_dict("records")},
        indent=2), encoding="utf-8")
    sem.to_csv(HERE / "semantic_types_and_units.csv", index=False)
    unres.to_csv(HERE / "UNRESOLVED_PROVENANCE.csv", index=False)

    pre = pd.DataFrame([
        {"stage": 1, "operation": "upstream_resample",
         "implementation": "EXTERNAL, NOT IN ANY LOCAL TREE",
         "evidence": "metadata json records method/category only",
         "confidence": "DOCUMENTED_EFFECT_UNRESOLVED_CODE"},
        {"stage": 2, "operation": "finite_clean_sort_dedupe",
         "implementation": "provider _load_signal",
         "evidence": "code", "confidence": "CODE_VERIFIED"},
        {"stage": 3, "operation": "common_window_intersection",
         "implementation": "t0=max(min t_i), t1=min(max t_i)",
         "evidence": "code + provenance doc 5.3", "confidence": "CODE_VERIFIED"},
        {"stage": 4, "operation": "resample_to_grid",
         "implementation": "linspace(t0,t1,1000); block-average if denser, "
                           "else linear interp",
         "evidence": "code + provenance doc 5.3", "confidence": "CODE_VERIFIED"},
        {"stage": 5, "operation": "numerical_realization",
         "implementation": "none | spline(k=5,s=0.1) | RTS(R=1,Q=1e-4)",
         "evidence": "provenance doc section 8", "confidence": "DOCUMENTED"},
        {"stage": 6, "operation": "standardization",
         "implementation": "within-discharge z-score, ddof=0, no global mu/sigma",
         "evidence": "provenance doc section 7.1-7.2",
         "confidence": "CODE_VERIFIED"},
    ])
    pre.to_csv(HERE / "preprocessing_lineage.csv", index=False)

    print(f"\n  signals: {len(inv)}  shots: {len(shots)}")
    print("\n  direct/derived breakdown:")
    for k, v in inv.direct_or_derived.value_counts().items():
        print(f"    {k:28s} {v}")
    print("\n  category breakdown:")
    for k, v in inv.category.value_counts().items():
        print(f"    {k:22s} {v}")
    print(f"\n  signals present in all {len(shots)} shots: "
          f"{(inv.shot_count_available == len(shots)).sum()}")
    print(f"  historical eight all present: "
          f"{inv[inv.historical_eight].shot_count_available.eq(len(shots)).all()}")
    print(f"\n  unresolved provenance items: {len(unres)} "
          f"(CRITICAL {int((unres.severity=='CRITICAL').sum())}, "
          f"MAJOR {int((unres.severity=='MAJOR').sum())})")


if __name__ == "__main__":
    main()
