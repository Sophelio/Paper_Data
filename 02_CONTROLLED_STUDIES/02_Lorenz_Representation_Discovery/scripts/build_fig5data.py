"""Build the portable Figure-5 data package.

Separates SCIENTIFIC DATA EXTRACTION from VISUALIZATION. After this runs,
`fig5data/` is self-contained: the plotting script never reads the benchmark
tree again.

Sources
-------
CANONICAL (frozen, read-only):
    task_conditioning_benchmark/tables/selection_stability.csv
    task_conditioning_benchmark/tables/confirmation_per_trajectory.csv
    task_conditioning_benchmark/tables/confirmation_results.csv
    task_conditioning_benchmark/contracts/contract_selections.json
    task_conditioning_benchmark/sir_mcp/containment/mcp_containment.json
    task_conditioning_benchmark/PRECONFIRMATION_FREEZE.json
AUGMENTATION (clearly labelled, generated separately):
    task_conditioning_benchmark/fig5_augmentation/noise_sweep_trajectory_level.csv
REGENERATED (documented, deterministic):
    canonical Lorenz attractor via Lorenz_attractor.generate_lorenz

The build FAILS LOUDLY if canonical checkpoints do not match expectation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

LORENZ = Path(__file__).resolve().parent
TCB = LORENZ / "task_conditioning_benchmark"
AUG = TCB / "fig5_augmentation"
OUT = LORENZ / "fig5data"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(LORENZ))

# Canonical checkpoints. The build aborts if any drifts beyond tolerance.
CHECKPOINTS = {
    "C_all_cv_rmse": (1.32165e-05, 1e-9),
    "C_all_n_coordinates": (38, 0),
    "compact_cv_rmse": (3.32564e-05, 1e-9),
    "compact_n_coordinates": (12, 0),
    "poly2_cv_rmse": (2.22551, 1e-4),
    "n_candidates": (17, 0),
    "n_confirmation_trajectories": (24, 0),
    "n_development_trajectories": (48, 0),
}
FAILURES: list[str] = []


def check(name: str, value):
    want, tol = CHECKPOINTS[name]
    ok = abs(float(value) - float(want)) <= tol
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}: {value} (expected {want} +/- {tol})")
    if not ok:
        FAILURES.append(f"{name}: got {value}, expected {want} +/- {tol}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


PROV: dict = {"generated_utc": datetime.now(timezone.utc).isoformat(),
              "builder": str(Path(__file__).resolve()),
              "outputs": {}}


def record(fname: str, meaning: str, sources, script, **extra):
    p = OUT / fname
    PROV["outputs"][fname] = {
        "scientific_meaning": meaning,
        "upstream_sources": [str(s) for s in (sources if isinstance(sources, list)
                                              else [sources])],
        "generating_script": script,
        "sha256": sha(p) if p.exists() else None,
        "bytes": p.stat().st_size if p.exists() else None,
        **extra,
    }


# ===========================================================================
# 1. Canonical recovery + attractor
# ===========================================================================
def build_canonical():
    print("\n[1] canonical recovery + attractor")
    src = TCB / "sir_mcp" / "containment" / "mcp_containment.json"
    mcp = json.loads(src.read_text(encoding="utf-8"))

    errs = [abs(r["true_coefficients"][k] - r["coefficients"][k])
            for r in mcp["runs"].values() for k in r["true_coefficients"]]
    payload = {
        "canonical_or_augmentation": "canonical",
        "system": "lorenz", "sigma": 10.0, "rho": 28.0, "beta": 8.0 / 3.0,
        "task": "full-state fixed cubic sparse identification",
        "estimator": "SIR MCP OPTIMAL_SEARCH (native)",
        "derivative_method": "exact analytic Lorenz right-hand side",
        "record": mcp["record"],
        "equations": {
            eq: {"run_id": r["run_id"], "latex": r["latex"],
                 "recovered_coefficients": r["coefficients"],
                 "true_coefficients": r["true_coefficients"],
                 "abs_errors": {k: abs(r["true_coefficients"][k] - r["coefficients"][k])
                                for k in r["true_coefficients"]},
                 "final_error": r["final_error"],
                 "support_recovery": mcp["support_recovery"][eq]}
            for eq, r in mcp["runs"].items()},
        "max_abs_coefficient_deviation": max(errs),
        "support_recovered_exactly": all(v == "exact"
                                         for v in mcp["support_recovery"].values()),
        "note": mcp["note"],
    }
    (OUT / "canonical_recovery.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8")
    record("canonical_recovery.json",
           "Full-state cubic identification: recovered vs true Lorenz coefficients.",
           src, "build_fig5data.py::build_canonical",
           canonical_or_augmentation="canonical",
           max_abs_coefficient_deviation=max(errs))
    print(f"  max |Delta c| = {max(errs):.3e}, exact support = "
          f"{payload['support_recovered_exactly']}")

    # Attractor: REGENERATED deterministically (no serialized copy upstream).
    from Lorenz_attractor import generate_lorenz
    df = generate_lorenz(dt=0.001, tmax=40.0, x0=(1.0, 1.0, 1.0))
    thin = df.iloc[::10].reset_index(drop=True)   # display-only downsample
    thin.to_csv(OUT / "canonical_attractor.csv", index=False)
    record("canonical_attractor.csv",
           "Canonical Lorenz trajectory for the Panel-a attractor. "
           "DISPLAY-ONLY downsample (every 10th sample of dt=0.001).",
           str(LORENZ / "Lorenz_attractor.py"),
           "build_fig5data.py::build_canonical",
           canonical_or_augmentation="regenerated_deterministic",
           integrator="DOP853", rtol=1e-12, atol=1e-12,
           x0=[1.0, 1.0, 1.0], dt=0.001, tmax=40.0,
           display_only_downsample=10, n_rows=len(thin))
    print(f"  attractor: {len(df)} -> {len(thin)} rows (display-only)")


# ===========================================================================
# 2. Representation landscape (development / search evidence)
# ===========================================================================
def build_landscape():
    print("\n[2] representation landscape (DEVELOPMENT CV evidence)")
    src = TCB / "tables" / "selection_stability.csv"
    s = pd.read_csv(src)
    sel = json.loads((TCB / "contracts" / "contract_selections.json")
                     .read_text(encoding="utf-8"))

    picks = {q: sel[q]["selected_candidate"] for q in sel}
    equiv = {q: set(sel[q]["selection_info"]["equivalent_set"]) for q in sel}

    rows = []
    for regime, g in s.groupby("regime"):
        # Pareto frontier: minimise (n_coordinates, mean_cv_rmse) jointly.
        pts = g[["n_coordinates", "mean_cv_rmse"]].to_numpy()
        pareto = []
        for i, (c_i, r_i) in enumerate(pts):
            dominated = any((c_j <= c_i and r_j <= r_i) and (c_j < c_i or r_j < r_i)
                            for c_j, r_j in pts)
            pareto.append(not dominated)
        for (i, r), on_front in zip(g.reset_index(drop=True).iterrows(), pareto):
            rows.append({
                "canonical_or_augmentation": "canonical",
                "evidence_level": "development_grouped_CV",
                "regime": r.regime, "candidate_id": r.candidate,
                "n_coordinates": int(r.n_coordinates),
                "n_features": int(r.n_features),
                "n_active_terms": float(r.n_terms),
                "cv_rmse_mean": float(r.mean_cv_rmse),
                "cv_rmse_se": float(r.se_cv_rmse),
                "cv_rmse_fold_std": float(r.fold_std),
                "condition_number": float(r.condition_number),
                "coverage_selection_strided": float(r.coverage),
                "selected_q_accuracy": r.candidate == picks["q_accuracy"],
                "selected_q_compact": r.candidate == picks["q_compact"],
                "selected_q_robust": r.candidate == picks["q_robust"],
                "eligible_q_compact": r.candidate in equiv["q_compact"],
                "eligible_q_robust": r.candidate in equiv["q_robust"],
                "pareto_front": bool(on_front),
                "source_run": "run_contracts.py (frozen)",
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "representation_landscape.csv", index=False)

    clean = df[df.regime == "clean"]
    check("n_candidates", clean.candidate_id.nunique())
    check("C_all_cv_rmse", float(clean[clean.candidate_id == "C_all"].cv_rmse_mean.iloc[0]))
    check("C_all_n_coordinates", int(clean[clean.candidate_id == "C_all"].n_coordinates.iloc[0]))
    check("compact_cv_rmse", float(clean[clean.candidate_id == "C0+Q_pair"].cv_rmse_mean.iloc[0]))
    check("compact_n_coordinates", int(clean[clean.candidate_id == "C0+Q_pair"].n_coordinates.iloc[0]))
    check("poly2_cv_rmse", float(clean[clean.candidate_id == "C0_poly2"].cv_rmse_mean.iloc[0]))

    record("representation_landscape.csv",
           "17 candidate representations x 2 regimes, DEVELOPMENT 6-fold grouped-CV. "
           "Search evidence only - not protected confirmation. "
           "NOTE coverage_selection_strided is the stride-8 selection subsample "
           "(~1/8 of native coverage), not the native retained fraction.",
           src, "build_fig5data.py::build_landscape",
           canonical_or_augmentation="canonical",
           evidence_level="development_grouped_CV",
           n_candidates=int(clean.candidate_id.nunique()),
           cv_scheme="GroupKFold(6) over 48 development trajectories",
           pareto_objectives="minimise (n_coordinates, cv_rmse_mean)")
    print(f"  {len(df)} rows; clean Pareto front: "
          f"{sorted(clean[clean.pareto_front].candidate_id)}")


# ===========================================================================
# 3. Confirmation trajectory evidence
# ===========================================================================
def build_confirmation():
    print("\n[3] protected confirmation, trajectory level")
    src = TCB / "tables" / "confirmation_per_trajectory.csv"
    pooled_src = TCB / "tables" / "confirmation_results.csv"
    p = pd.read_csv(src)
    pooled = pd.read_csv(pooled_src)

    label = {"C0_matched": "raw stencil (10)", "C0_poly2": "quadratic (10->65)",
             "C0_poly3": "cubic (10->285)", "C_all": "C_all (38)",
             "C*_accuracy": "q_acc -> C_all (38)",
             "C*_compact": "q_comp -> compact (12)",
             "C*_robust": "q_rob -> C_all (38)"}
    cov = (pooled[pooled.method == "STLSQ"]
           .set_index(["regime", "representation"])["coverage"].to_dict())

    p = p.rename(columns={"trajectory": "trajectory_id",
                          "representation": "representation_id"})
    p["representation_label"] = p.representation_id.map(label)
    p["noise_level"] = p.regime.map(lambda r: 0.0 if r == "clean"
                                    else float(r.split("_")[1]))
    p["cohort"] = "confirmation_24"
    p["canonical_or_augmentation"] = "canonical"
    p["evidence_level"] = "protected_confirmation"
    p["support_scope"] = "native"
    p["native_coverage"] = [cov.get((r.regime, r.representation_id), np.nan)
                            for r in p.itertuples()]
    p.to_csv(OUT / "confirmation_trajectory_rmse.csv", index=False)

    check("n_confirmation_trajectories", p.trajectory_id.nunique())
    record("confirmation_trajectory_rmse.csv",
           "Per-trajectory RMSE on the 24 PROTECTED confirmation trajectories, "
           "7 representations x 2 regimes, common sparse estimator (PySINDy STLSQ). "
           "CAVEAT: scored on each representation's NATIVE mask; coverage differs "
           "across representations (0.874-0.998). See noise_robustness_augmented.csv "
           "for a common-support comparison.",
           [src, pooled_src], "build_fig5data.py::build_confirmation",
           canonical_or_augmentation="canonical",
           evidence_level="protected_confirmation",
           n_trajectories=int(p.trajectory_id.nunique()),
           estimator="pysindy.STLSQ",
           support_caveat="native per-representation masks, coverage 0.874-0.998")
    print(f"  {len(p)} rows, {p.trajectory_id.nunique()} trajectories")
    print("  native coverage: " + ", ".join(
        f"{k[1]}={v:.3f}" for k, v in cov.items() if k[0] == "clean"))


# ===========================================================================
# 4. Noise robustness
# ===========================================================================
def build_noise():
    print("\n[4] noise robustness")
    canon_src = TCB / "tables" / "noise_robustness.csv"
    rows = []
    p = pd.read_csv(OUT / "confirmation_trajectory_rmse.csv")
    for r in p.itertuples():
        rows.append({"canonical_or_augmentation": "canonical",
                     "noise_sigma": r.noise_level, "noise_percent": r.noise_level * 100,
                     "noise_replicate": 0, "noise_seed": 901 if r.noise_level else None,
                     "trajectory_id": r.trajectory_id,
                     "representation_id": r.representation_id,
                     "representation_label": r.representation_label,
                     "support_scope": "native", "rmse": r.rmse,
                     "estimator": "pysindy.STLSQ", "cohort": "confirmation_24"})
    pd.DataFrame(rows).to_csv(OUT / "noise_robustness.csv", index=False)
    record("noise_robustness.csv",
           "CANONICAL noise evidence: only two levels (0 and 0.01) exist in the "
           "frozen benchmark, trajectory level, native support.",
           [canon_src, str(OUT / "confirmation_trajectory_rmse.csv")],
           "build_fig5data.py::build_noise",
           canonical_or_augmentation="canonical",
           noise_levels=[0.0, 0.01])

    aug_src = AUG / "noise_sweep_trajectory_level.csv"
    if not aug_src.exists():
        print("  ! augmentation sweep not found - skipping augmented outputs")
        return
    a = pd.read_csv(aug_src)
    a.to_csv(OUT / "noise_robustness_augmented.csv", index=False)

    def boot_ci(v, n=2000, seed=0):
        rng = np.random.default_rng(seed)
        v = np.asarray(v, float)
        if len(v) < 2:
            return np.nan, np.nan
        m = [rng.choice(v, len(v), replace=True).mean() for _ in range(n)]
        return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

    summ = []
    for (sig, rep, scope), g in a.groupby(["noise_sigma", "representation_id",
                                           "support_scope"]):
        lo, hi = boot_ci(g.rmse.values)
        summ.append({"canonical_or_augmentation": "augmentation",
                     "noise_sigma": sig, "noise_percent": sig * 100,
                     "representation_id": rep, "support_scope": scope,
                     "n_observations": len(g),
                     "n_trajectories": g.trajectory_id.nunique(),
                     "n_replicates": g.noise_replicate.nunique(),
                     "mean_rmse": g.rmse.mean(), "median_rmse": g.rmse.median(),
                     "std_rmse": g.rmse.std(ddof=1),
                     "se_rmse": g.rmse.std(ddof=1) / np.sqrt(len(g)),
                     "ci_lo": lo, "ci_hi": hi,
                     "ci_method": "percentile bootstrap, 2000 resamples, seed 0, "
                                  "resampling trajectory-level observations"})
    pd.DataFrame(summ).to_csv(OUT / "noise_robustness_summary.csv", index=False)

    man = json.loads((AUG / "AUGMENTATION_MANIFEST.json").read_text(encoding="utf-8"))
    for fn, meaning in (
        ("noise_robustness_augmented.csv",
         "AUGMENTATION: dense noise sweep, trajectory level, native AND common "
         "support. NOT part of the frozen canonical benchmark."),
        ("noise_robustness_summary.csv",
         "AUGMENTATION: bootstrap summary of the dense sweep.")):
        record(fn, meaning, str(aug_src), "build_fig5data.py::build_noise",
               canonical_or_augmentation="augmentation",
               augmentation_manifest=str(AUG / "AUGMENTATION_MANIFEST.json"),
               noise_grid=man["seed_namespace"] and man["new_in_augmentation"][0],
               seed_namespace=man["seed_namespace"])
    print(f"  augmented: {len(a)} trajectory rows, {len(summ)} summary rows")


# ===========================================================================
# 5. Selected representation definitions
# ===========================================================================
def build_selected():
    print("\n[5] selected representation definitions")
    src = TCB / "contracts" / "contract_selections.json"
    sel = json.loads(src.read_text(encoding="utf-8"))
    land = pd.read_csv(OUT / "representation_landscape.csv")
    clean = land[land.regime == "clean"].set_index("candidate_id")

    payload = {"canonical_or_augmentation": "canonical", "contracts": {}, "reference": {}}
    for q, v in sel.items():
        payload["contracts"][q] = {
            "selected_candidate": v["selected_candidate"],
            "coordinates": v["coordinates"],
            "n_coordinates": v["n_coordinates"],
            "n_features": v["n_features"],
            "relation_family": v["relation_family"],
            "condition_number": v["condition_number"],
            "cv_rmse_mean": v["mean_cv_utility"],
            "cv_rmse_se": v["se_cv_utility"],
            "accuracy_equivalent_set": v["selection_info"]["equivalent_set"],
            "equivalence_rule": v["selection_info"]["rule"],
            "margin_source": v["selection_info"].get("margin_source"),
        }
    for ref in ("C0_poly2", "C0_matched"):
        if ref in clean.index:
            payload["reference"][ref] = {
                "n_coordinates": int(clean.loc[ref, "n_coordinates"]),
                "n_features": int(clean.loc[ref, "n_features"]),
                "cv_rmse_mean": float(clean.loc[ref, "cv_rmse_mean"]),
                "condition_number": float(clean.loc[ref, "condition_number"]),
                "note": "conventional baseline; 10 scientific coordinates expanded "
                        "to a degree-2 polynomial feature set",
            }
    payload["complexity_definitions"] = {
        "n_coordinates": "scientific coordinates in C (the representation itself)",
        "n_features": "downstream columns supplied to the estimator after R(C); "
                      "equals n_coordinates for identity families, 65 for poly2, "
                      "285 for poly3",
        "n_active_terms": "non-zero STLSQ coefficients after thresholding",
    }
    (OUT / "selected_representations.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8")
    record("selected_representations.json",
           "Exact coordinate identities for each contract's selection, the "
           "accuracy-equivalent sets, and the three complexity definitions.",
           src, "build_fig5data.py::build_selected",
           canonical_or_augmentation="canonical")
    print(f"  contracts: {list(payload['contracts'])}")


# ===========================================================================
def main() -> None:
    print("=" * 70)
    print("BUILDING fig5data/  (canonical extraction + labelled augmentation)")
    print("=" * 70)

    freeze = TCB / "PRECONFIRMATION_FREEZE.json"
    fr = json.loads(freeze.read_text(encoding="utf-8"))
    bad = [rel for rel, want in fr["files"].items()
           if sha(TCB / rel) != want]
    print(f"\n[0] canonical freeze: {len(fr['files'])} files, "
          f"violations: {bad or 'none'}")
    if bad:
        FAILURES.append(f"canonical freeze violated: {bad}")

    build_canonical()
    build_landscape()
    build_confirmation()
    build_noise()
    build_selected()

    dev_n = len(json.loads((TCB / "prior_benchmark_reference" /
                            "imported_hashes.json").read_text())["trajectories"])
    print()
    check("n_development_trajectories", dev_n)

    PROV["canonical_freeze"] = {"n_files": len(fr["files"]),
                                "violations": bad,
                                "sha256": sha(freeze)}
    PROV["checkpoints"] = {k: {"expected": v[0], "tolerance": v[1]}
                           for k, v in CHECKPOINTS.items()}
    PROV["checkpoint_failures"] = FAILURES
    (OUT / "PROVENANCE_MANIFEST.json").write_text(
        json.dumps(PROV, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    if FAILURES:
        print("BUILD FAILED - canonical checkpoints did not match:")
        for f in FAILURES:
            print("  -", f)
        raise SystemExit(1)
    print(f"BUILD OK - {len(PROV['outputs'])} data files in {OUT}")
    for k in sorted(PROV["outputs"]):
        print(f"  {k}")


if __name__ == "__main__":
    main()
