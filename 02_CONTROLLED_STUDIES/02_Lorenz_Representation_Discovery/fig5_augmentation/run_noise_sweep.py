"""FIGURE-5 AUGMENTATION — dense noise sweep + common-support recomputation.

    *** THIS IS NOT THE CANONICAL FROZEN BENCHMARK. ***

The canonical benchmark (../tables/, ../contracts/, ../PRECONFIRMATION_FREEZE.json)
is immutable and is NOT modified, rerun, or overwritten by this script. Every
output here is written under fig5_augmentation/ and is labelled
`canonical_or_augmentation = "augmentation"`.

WHAT IS HELD FIXED (identical to the frozen benchmark)
------------------------------------------------------
  * scientific object O: x,y explanatory; z supervised-only; forbidden {z,dz,d2z}
  * information boundary I_k = {x[k-2..k+2], y[k-2..k+2]}, centred 5-point
  * coordinate grammar and numerical realization (audited features.py)
  * coordinate hyperparameters rho=0.1, kappa=1.0, pooled_rms, mask q=0.05
  * the three frozen representations under test
  * PySINDy STLSQ, same threshold grid, same target-centring convention
  * fit on the 48 exposed DEVELOPMENT trajectories; score on the 24 PROTECTED
    confirmation trajectories
  * noise applied to x and y BEFORE any derivative / quotient / phase / scaling

WHAT IS NEW (the augmentation)
------------------------------
  1. a denser noise grid (11 levels, 0 - 1%) instead of the canonical {0, 0.5%, 1%}
  2. 3 independent noise replicates per level, with recorded seeds
  3. trajectory-level RMSE retained at every (level, replicate, representation)
  4. a COMMON-SUPPORT evaluation, because the canonical confirmation scored each
     representation on its own native mask (coverage 0.874 - 0.998), which lets a
     representation benefit from discarding difficult samples. Both native and
     common-support numbers are exported.

Noise seeds are drawn from a dedicated namespace (5000+) disjoint from the
canonical development (11,12,13) and confirmation (901,902,903) seeds.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

AUG = Path(__file__).resolve().parent
TCB = AUG.parent
sys.path.insert(0, str(TCB))
sys.path.insert(0, str(TCB / "scripts"))
import engine as E  # noqa: E402
import features as F  # noqa: E402

CFG = E.CFG
THR = CFG["estimators"]["stlsq"]["thresholds"]

# ---- augmentation design (declared here, recorded in the manifest) ---------
NOISE_GRID = [0.000, 0.001, 0.002, 0.003, 0.004,
              0.005, 0.006, 0.007, 0.008, 0.009, 0.010]
N_REPLICATES = 3
SEED_NAMESPACE = 5000          # disjoint from canonical 11/12/13 and 901/902/903
DEV_SEED_BASE = SEED_NAMESPACE + 0
CONF_SEED_BASE = SEED_NAMESPACE + 500


def representations() -> dict:
    """The three frozen representations compared in Figure 5."""
    sel = json.loads((TCB / "contracts" / "contract_selections.json")
                     .read_text(encoding="utf-8"))
    cands = E.candidates()
    return {
        "C0_poly2": {"cols": cands["C0_poly2"][0], "family": "poly2",
                     "label": "conventional quadratic",
                     "n_coordinates": 10, "n_features": 65},
        "C_compact": {"cols": sel["q_compact"]["coordinates"], "family": "identity",
                      "label": "compact (12 coordinates)",
                      "n_coordinates": 12, "n_features": 12},
        "C_all": {"cols": sel["q_accuracy"]["coordinates"], "family": "identity",
                  "label": "C_all (38 coordinates)",
                  "n_coordinates": 38, "n_features": 38},
    }


def masks(recs, cols):
    return [E.support(r, cols) for r in recs]


def common_mask(recs, all_cols):
    """Intersection of every representation's native mask, per trajectory."""
    out = []
    for i, r in enumerate(recs):
        m = np.ones(len(r["x"]), dtype=bool)
        for cols in all_cols:
            m &= E.support(r, cols)
        out.append(m)
    return out


def fit_and_score(dev, conf, cols, family, dev_masks, conf_masks_native,
                  conf_masks_common):
    """Fit on development, score per confirmation trajectory.

    Threshold selected on a development hold-out slice only; the protected
    confirmation set is never used for any selection.
    """
    n = len(dev)
    tr, va = list(range(0, n - 8)), list(range(n - 8, n))
    Xtr, ytr = E.stack([dev[i] for i in tr], cols, [dev_masks[i] for i in tr])
    Xva, yva = E.stack([dev[i] for i in va], cols, [dev_masks[i] for i in va])
    m = E.fit_stlsq(E.expand(Xtr, family), ytr, E.expand(Xva, family), yva, THR)

    Xd, yd = E.stack(dev, cols, dev_masks)
    full = E.fit_stlsq(E.expand(Xd, family), yd, E.expand(Xd, family), yd,
                       [m["threshold"]])

    rows = []
    for r, mn, mc in zip(conf, conf_masks_native, conf_masks_common):
        for scope, mask in (("native", mn), ("common", mc)):
            if mask.sum() < 10:
                continue
            Xi = E.expand(F.build_matrix(r["vals"], cols)[mask], family)
            pred = E.predict(full, Xi)
            rows.append({"trajectory_id": r["id"], "support_scope": scope,
                         "rmse": E.rmse(r["z"][mask], pred),
                         "nrmse": E.nrmse(r["z"][mask], pred),
                         "n_samples": int(mask.sum())})
    return rows, m["threshold"], int(full["n_terms"])


def main() -> None:
    t0 = time.time()
    reps = representations()
    all_cols = [v["cols"] for v in reps.values()]
    print(f"FIGURE-5 AUGMENTATION (not the canonical benchmark)")
    print(f"  noise grid   : {NOISE_GRID}")
    print(f"  replicates   : {N_REPLICATES}")
    print(f"  representations: {list(reps)}")

    records = []
    for li, sigma in enumerate(NOISE_GRID):
        # sigma = 0 is deterministic: one replicate suffices.
        n_rep = 1 if sigma == 0.0 else N_REPLICATES
        for rep_i in range(n_rep):
            dseed = DEV_SEED_BASE + li * 10 + rep_i
            cseed = CONF_SEED_BASE + li * 10 + rep_i

            dev0 = E.build(E.load_split("development", sigma, dseed), None)
            fit = F.fit_coordinates([r["base"] for r in dev0], CFG)
            dev = E.build(E.load_split("development", sigma, dseed), fit)
            conf = E.build(E.load_split("confirmation", sigma, cseed), fit)

            cm_conf = common_mask(conf, all_cols)
            for rid, spec in reps.items():
                dm = masks(dev, spec["cols"])
                nm = masks(conf, spec["cols"])
                rows, thr, nterms = fit_and_score(
                    dev, conf, spec["cols"], spec["family"], dm, nm, cm_conf)
                for row in rows:
                    records.append({
                        "canonical_or_augmentation": "augmentation",
                        "noise_sigma": sigma, "noise_percent": sigma * 100.0,
                        "noise_replicate": rep_i,
                        "dev_noise_seed": dseed, "conf_noise_seed": cseed,
                        "representation_id": rid,
                        "representation_label": spec["label"],
                        "n_coordinates": spec["n_coordinates"],
                        "n_features": spec["n_features"],
                        "n_active_terms": nterms, "stlsq_threshold": thr,
                        "estimator": "pysindy.STLSQ", "cohort": "confirmation_24",
                        **row})
            print(f"  sigma={sigma:.3f} rep={rep_i} seeds=({dseed},{cseed}) "
                  f"done  [{time.time()-t0:.0f}s]")

    df = pd.DataFrame(records)
    out = AUG / "noise_sweep_trajectory_level.csv"
    df.to_csv(out, index=False)

    manifest = {
        "experiment": "figure5_noise_augmentation",
        "canonical_or_augmentation": "augmentation",
        "NOT_the_canonical_benchmark": True,
        "purpose": "denser noise grid + common-support evaluation for Figure 5",
        "held_fixed_from_frozen_benchmark": [
            "scientific object O and admissibility A",
            "information boundary I_k (centred 5-point)",
            "coordinate grammar and numerical realization",
            "rho=0.1, kappa=1.0, pooled_rms, quotient mask quantile 0.05",
            "the three frozen representations",
            "PySINDy STLSQ and its threshold grid",
            "fit on 48 development, score on 24 protected confirmation",
            "noise applied to x,y BEFORE coordinate construction",
        ],
        "new_in_augmentation": [
            f"noise grid {NOISE_GRID} (canonical was [0.0, 0.005, 0.01])",
            f"{N_REPLICATES} noise replicates per non-zero level",
            "trajectory-level retention at every level/replicate",
            "COMMON-SUPPORT evaluation in addition to native support",
        ],
        "seed_namespace": SEED_NAMESPACE,
        "dev_seed_base": DEV_SEED_BASE, "conf_seed_base": CONF_SEED_BASE,
        "disjoint_from": {"canonical_development": [11, 12, 13],
                          "canonical_confirmation": [901, 902, 903]},
        "representations": {k: {"n_coordinates": v["n_coordinates"],
                                "n_features": v["n_features"],
                                "family": v["family"],
                                "coordinates": v["cols"]}
                            for k, v in reps.items()},
        "upstream_sources": {
            "contract_selections": str(TCB / "contracts" / "contract_selections.json"),
            "confirmation_trajectories": str(TCB / "shared" / "confirmation"),
            "development_trajectories": CFG["provenance"]["development_source"],
            "coordinate_implementation":
                str(Path(CFG["provenance"]["development_source"]).parent.parent
                    / "scripts" / "features.py"),
        },
        "output_rows": len(df),
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (AUG / "AUGMENTATION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"\nwrote {out.name} ({len(df)} rows) and AUGMENTATION_MANIFEST.json")
    piv = (df[df.support_scope == "common"]
           .groupby(["noise_sigma", "representation_id"])["rmse"].mean().unstack())
    print("\nmean confirmation RMSE (common support):")
    print(piv.to_string(float_format=lambda v: f"{v:.4g}"))


if __name__ == "__main__":
    main()
