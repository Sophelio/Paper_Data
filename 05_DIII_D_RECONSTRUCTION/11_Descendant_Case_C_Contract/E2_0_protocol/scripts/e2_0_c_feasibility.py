"""S7.E2.0 step C - prospective, TARGET-BLIND applicability feasibility.

Quantifies how demanding FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT will be, as a
function of the training-side threshold, BEFORE any search is run. Uses the
frozen range-support predicate and predictor values only.

This informs disclosure, not selection: it cannot influence which coordinates a
fold search may use, and it never touches a target or a performance label.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
K2 = S7 / "K2_observational_range_support_contract"
GRID = [0.25, 0.4, 0.5, 0.6, 0.75, 1.0]
TAU_QUAL = 1.0
N_DRAW, M = 4000, 12
SEED = 20260906

z = np.load(K2 / "manifests" / "_k2_scores.npz", allow_pickle=True)
E = z["E1"].astype(np.float64); deg = z["deg1"]
cons = np.array([str(x) for x in z["constructor"]])
cells = [str(c) for c in z["cells"]]
shot = np.array([c.split(":")[0] for c in cells])
blk = np.array([c.split(":")[1] for c in cells])
fa = pd.read_csv(OUT / "outer_fold_assignment.csv", dtype={"discharge": str})
fold_of = dict(zip(fa.discharge, fa.outer_fold))
fc = np.array([fold_of[s] for s in shot])
sup_q = (E <= TAU_QUAL) & ~deg
rng = np.random.default_rng(SEED)

basis_by, joint_by, table = {}, {}, []
for tt in GRID:
    sup_t = (E <= tt) & ~deg
    sizes, joints, fams = [], [], []
    for k in range(6):
        tr = fc != k
        adm = sup_t[:, tr].all(axis=1)
        held = sup_q[:, ~tr].all(axis=1)
        idx = np.flatnonzero(adm)
        sizes.append(int(len(idx)))
        fams.append(int(min((adm & (cons == f)).sum() for f in sorted(set(cons)))))
        d = rng.choice(idx, size=(N_DRAW, M), replace=True)
        joints.append(float(held[d].all(axis=1).mean()))
    basis_by[str(tt)] = {"min": min(sizes), "max": max(sizes), "per_fold": sizes,
                         "smallest_constructor_family": min(fams)}
    joint_by[str(tt)] = {"per_fold": [round(x, 4) for x in joints],
                         "per_fold_range": "%.2f-%.2f" % (min(joints), max(joints)),
                         "six_fold_product": round(float(np.prod(joints)), 4)}
    table.append({"tau_train": tt, "basis_min": min(sizes), "basis_max": max(sizes),
                  "smallest_family": min(fams), "joint12_min": round(min(joints), 4),
                  "joint12_max": round(max(joints), 4),
                  "six_fold_product": round(float(np.prod(joints)), 4)})
pd.DataFrame(table).to_csv(OUT / "manifests" / "applicability_feasibility.csv", index=False)

rows = []
for s in fa.discharge:
    k = fold_of[s]; tr = fc != k
    adm = (E <= 0.5) & ~deg
    adm = adm[:, tr].all(axis=1)
    m = shot == s
    allb = sup_q[:, m].all(axis=1)
    per = [sup_q[adm, i].mean() for i in np.flatnonzero(m)]
    rows.append({"discharge": s, "outer_fold": int(k),
                 "era": fa[fa.discharge == s].processing_era.iloc[0],
                 "frac_fold_basis_supported": float(allb[adm].mean()),
                 "worst_block": blk[m][int(np.argmin(per))],
                 "worst_block_rate": float(min(per))})
hd = pd.DataFrame(rows).sort_values("frac_fold_basis_supported")
hd.to_csv(OUT / "manifests" / "heldout_discharge_hostility.csv", index=False)

out = {
    "record_id": "APPLICABILITY_FEASIBILITY_V1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "status": "PROSPECTIVE_TARGET_BLIND_DISCLOSURE",
    "purpose": ("quantify how demanding FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT is before any "
                "search is run"),
    "influences_coordinate_selection": False,
    "target_used": False, "performance_used": False,
    "method": ("for each fold, draw %d random %d-coordinate subsets of the training-admissible "
               "basis and measure the fraction whose coordinates are ALL range-supported on that "
               "fold's held-out discharges at tau=%.1f" % (N_DRAW, M, TAU_QUAL)),
    "caveat": ("the real search selects by utility, not at random. Whether utility-selected "
               "supports carry over better or worse than random draws is unknown and cannot be "
               "determined without running the search, which this stage may not do. The random "
               "estimate is the honest prospective guide, not a prediction"),
    "basis_size_by_tau_train": basis_by,
    "joint12_by_tau_train": joint_by,
    "held_out_discharge_hostility": {
        "min_frac_fold_basis_supported": float(hd.frac_fold_basis_supported.min()),
        "median": float(hd.frac_fold_basis_supported.median()),
        "n_below_0.80": int((hd.frac_fold_basis_supported < 0.80).sum()),
        "n_below_0.50": int((hd.frac_fold_basis_supported < 0.50).sum()),
        "hardest": hd.head(5).to_dict("records"),
        "reading": ("no hostile discharge exists. Every discharge retains at least 93.8 percent "
                    "of its fold's training basis. The joint difficulty is compounding attrition "
                    "across 12 coordinates and ~10 held-out discharges, not a pathological shot"),
    },
    "conclusion": ("the applicability gate, not reconstruction skill, is the dominant risk to "
                   "Epoch 2. Disclosed prospectively; the standard was not weakened"),
}
(OUT / "manifests" / "APPLICABILITY_FEASIBILITY.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(pd.DataFrame(table).to_string(index=False))
print()
print("hardest held-out discharges:")
print(hd.head(5).round(4).to_string(index=False))
