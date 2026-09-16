"""S7.K2 step C - metric selection, threshold grid and policy freeze.

The threshold grid is written and hashed BEFORE any applicability count is
computed. Metric selection is argued from the frozen desiderata and the
constructor-stratified stress test only - never from an Epoch-1 outcome.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S79 = S7 / "09_development_selection_and_freeze"

TAU_GRID = [0.0, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def depth_split(s):
    out, d, cur = [], 0, []
    for ch in s:
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
        if ch == "|" and d == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur)); return out


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()

    # ---- 1. FREEZE THE GRID FIRST, BEFORE ANY COUNT ---------------------
    grid_rec = {
        "record_id": "RANGE_SUPPORT_THRESHOLD_GRID_V1", "frozen_utc": now,
        "frozen_before_any_applicability_count_was_inspected": True,
        "tau_grid": TAU_GRID,
        "rationale": ("a compact grid of simple dimensionless values spanning strict "
                      "interpolation (0) to an order of magnitude of permitted extrapolation "
                      "(10); no six-significant-figure thresholds are admissible"),
        "selection_basis_forbidden": ["reconstruction outcome", "V3", "NRMSE",
                                      "the S7.11 70/143 partition",
                                      "whether the Epoch-1 blocks are flagged"],
    }
    (OUT / "manifests" / "THRESHOLD_GRID.json").write_text(
        json.dumps(grid_rec, indent=2), encoding="utf-8")
    grid_sha = sha256(OUT / "manifests" / "THRESHOLD_GRID.json")
    print("threshold grid frozen: %s  %s" % (grid_sha[:16], TAU_GRID))

    # ---- 2. metric selection from desiderata + stress test --------------
    cs = pd.read_csv(OUT / "range_support_constructor_summary.csv")
    r1 = cs[cs.candidate == "R1_excess_over_calibration_range"]
    r2 = cs[cs.candidate == "R2_excess_over_calibration_rms"]
    spread = {
        "R1": {"p90_min": float(r1.p90.min()), "p90_max": float(r1.p90.max()),
               "p90_ratio": float(r1.p90.max() / r1.p90.min()),
               "p99_min": float(r1.p99.min()), "p99_max": float(r1.p99.max()),
               "p99_ratio": float(r1.p99.max() / r1.p99.min())},
        "R2": {"p90_min": float(r2.p90.min()), "p90_max": float(r2.p90.max()),
               "p90_ratio": float(r2.p90.max() / r2.p90.min()),
               "p99_min": float(r2.p99.min()), "p99_max": float(r2.p99.max()),
               "p99_ratio": float(r2.p99.max() / r2.p99.min())},
    }
    selection = {
        "selected": "R1_excess_over_calibration_range",
        "R3_evaluated": False,
        "R3_not_needed_because": ("neither R1 nor R2 is ill-defined over a large part of the "
                                  "universe: 263 of 2,004,708 coordinate-cells (0.013 percent) "
                                  "are degenerate-calibration under either"),
        "basis": "frozen desiderata D6 (constructor-generic) and D10 (auditable)",
        "constructor_neutrality": spread,
        "argument": (
            "Both candidates satisfy D1-D5 and D7-D14. They separate on D6. Across the seven "
            "populated constructor families R1's p90 spans %.4f-%.4f (ratio %.1f) and its p99 "
            "spans %.2f-%.2f (ratio %.1f); R2's p90 spans %.4f-%.4f (ratio %.1f) and its p99 "
            "spans %.2f-%.2f (ratio %.1f). R2 systematically inflates rate-bearing families "
            "(C1, C6, C7) because dividing by calibration RMS penalises coordinates whose "
            "calibration mean sits near zero - a property of the constructor, not of range "
            "support. R1 divides by the calibration RANGE, which is the natural scale of the "
            "empirical support itself, and is therefore constructor-neutral by construction. "
            "R1 also has the cleaner one-sentence reading."
            % (spread["R1"]["p90_min"], spread["R1"]["p90_max"], spread["R1"]["p90_ratio"],
               spread["R1"]["p99_min"], spread["R1"]["p99_max"], spread["R1"]["p99_ratio"],
               spread["R2"]["p90_min"], spread["R2"]["p90_max"], spread["R2"]["p90_ratio"],
               spread["R2"]["p99_min"], spread["R2"]["p99_max"], spread["R2"]["p99_ratio"])),
        "epoch1_outcome_used": False,
    }

    # ---- 3. applicability over the grid ---------------------------------
    z = np.load(OUT / "manifests" / "_k2_scores.npz", allow_pickle=True)
    E = z["E1"].astype(np.float64)
    deg = z["deg1"]
    cons = np.array([str(x) for x in z["constructor"]])
    coord = np.array([str(x) for x in z["coordinate_id"]])
    cells = [str(c) for c in z["cells"]]
    shots = np.array([c.split(":")[0] for c in cells])
    part = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json").read_text())
    devset = set(str(s) for s in part["development"]["shot_ids"])
    is_dev = np.array([s in devset for s in shots])
    N, NC = E.shape

    rows = []
    for tau in TAU_GRID:
        with np.errstate(invalid="ignore"):
            ok = (E <= tau) & ~deg
        cellrate = float(ok.sum() / (N * NC))
        full = ok.all(axis=1)
        fulldev = ok[:, is_dev].all(axis=1)
        r = {"tau": tau, "cell_applicability_rate": cellrate,
             "atoms_full_domain_62": int(full.sum()),
             "atoms_full_domain_62_frac": float(full.mean()),
             "atoms_full_domain_development_only": int(fulldev.sum()),
             "atoms_full_domain_development_only_frac": float(fulldev.mean()),
             "degenerate_cells": int(deg.sum())}
        for f in sorted(set(cons)):
            m = cons == f
            r["full_%s" % f] = float(full[m].mean())
        rows.append(r)
    ts = pd.DataFrame(rows)
    ts.to_csv(OUT / "range_support_threshold_sensitivity.csv", index=False)

    print()
    print("=== threshold sensitivity (atomic universe, target-blind) ===")
    print(ts[["tau", "cell_applicability_rate", "atoms_full_domain_62",
              "atoms_full_domain_62_frac"]].round(5).to_string(index=False))
    print()
    print("=== full-domain atom fraction by constructor ===")
    print(ts[["tau"] + ["full_%s" % f for f in sorted(set(cons))]].round(4).to_string(index=False))

    # ---- 4. the 217 fixed supports + C_dev_star (identities only) -------
    boot = pd.read_csv(S79 / "bootstrap_selection_frequency.csv")
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text())
    idx = {c: i for i, c in enumerate(coord)}
    sup = {sid: depth_split(sid) for sid in boot.support_id}
    frows = []
    for tau in TAU_GRID:
        with np.errstate(invalid="ignore"):
            ok = (E <= tau) & ~deg
        nfull = 0
        cfull = None
        for sid, atoms in sup.items():
            r = np.array([idx[a] for a in atoms])
            sok = ok[r].all(axis=0)          # all coordinates pass, per cell
            f = bool(sok.all())
            if sid == sel["support_id"]:
                cfull = f
            nfull += int(f)
        frows.append({"tau": tau, "n_supports": len(sup),
                      "n_full_domain_supports": nfull,
                      "frac_full_domain_supports": nfull / len(sup),
                      "C_dev_star_full_domain": cfull})
    fs = pd.DataFrame(frows)
    fs.to_csv(OUT / "range_support_family_support_audit.csv", index=False)
    print()
    print("=== 217 fixed supports, full-domain range support (identities + predictors only) ===")
    print(fs.round(4).to_string(index=False))

    (OUT / "manifests" / "METRIC_SELECTION.json").write_text(
        json.dumps({"record_id": "RANGE_SUPPORT_METRIC_SELECTION_V1", "generated_utc": now,
                    "threshold_grid_sha256": grid_sha, **selection}, indent=2), encoding="utf-8")
    print()
    print("metric selected: %s" % selection["selected"])
    print("  R1 constructor p90 ratio %.1f vs R2 %.1f"
          % (spread["R1"]["p90_ratio"], spread["R2"]["p90_ratio"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
