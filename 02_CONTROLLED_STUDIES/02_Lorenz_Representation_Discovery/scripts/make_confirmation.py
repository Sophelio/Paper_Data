"""Step 2 — generate the NEW protected confirmation ensemble.

Development data = the first benchmark's 48-trajectory ensemble, referenced by
hash (never copied). It is EXPOSED: its protected test results were inspected
and informed this design.

Confirmation data = 24 NEW trajectories under a seed, seed-trajectory, and
initial condition never used by the first benchmark. Audited for
non-duplication against every development initial state.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

TCB = Path(__file__).resolve().parent.parent
LORENZ = TCB.parent
sys.path.insert(0, str(LORENZ))
from Lorenz_attractor import BETA, RHO, SIGMA, add_exact_derivatives, generate_lorenz  # noqa: E402

CFG = yaml.safe_load((TCB / "benchmark_config.yaml").read_text(encoding="utf-8"))
DEV_DIR = Path(CFG["provenance"]["development_source"])
CONF = TCB / "shared" / "confirmation"
MAN = TCB / "shared" / "manifests"
CONF.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def development_initial_states():
    """First sample of every development trajectory = its initial state."""
    out = {}
    for p in sorted(DEV_DIR.glob("*.parquet")):
        df = pd.read_parquet(p, columns=["x", "y", "z"])
        out[p.stem] = df.iloc[0].to_numpy(dtype=np.float64)
    return out


def main() -> None:
    c = CFG["confirmation"]

    # ---- seed trajectory: different x0, longer, longer burn-in -------------
    seeder = generate_lorenz(
        dt=c["seed_traj_dt"], tmax=c["seed_traj_tmax"], x0=tuple(c["seed_traj_x0"])
    )
    keep = seeder[seeder["times"] >= c["seed_traj_burn_in"]]
    states = keep[["x", "y", "z"]].to_numpy(dtype=np.float64)

    rng = np.random.default_rng(c["seed"])
    n = c["n_trajectories"]
    edges = np.linspace(0, len(states), n + 1).astype(int)
    idx = np.array([rng.integers(edges[i], edges[i + 1]) for i in range(n)])
    x0s = states[idx]

    # ---- non-duplication audit against development -------------------------
    dev = development_initial_states()
    dev_arr = np.array(list(dev.values()))
    dmin = np.array([np.min(np.linalg.norm(dev_arr - s, axis=1)) for s in x0s])
    thr = float(c["min_initial_state_separation"])
    violations = [
        {"conf_index": int(i), "min_distance": float(dmin[i])}
        for i in range(n) if dmin[i] < thr
    ]
    print(f"initial-state separation vs {len(dev)} development states:")
    print(f"  min={dmin.min():.4f}  median={np.median(dmin):.4f}  max={dmin.max():.4f}")
    print(f"  threshold={thr}  violations={len(violations)}")
    if violations:
        raise SystemExit(f"ABORT: {len(violations)} confirmation x0 too close to development")

    # ---- generate -----------------------------------------------------------
    lineage = {
        "status": "PROTECTED_CONFIRMATION",
        "generator": {
            "module": str(LORENZ / "Lorenz_attractor.py"),
            "function": "generate_lorenz",
            "sha256": sha(LORENZ / "Lorenz_attractor.py"),
            "reused": True,
        },
        "parameters": {"sigma": SIGMA, "rho": RHO, "beta": BETA},
        "seed": c["seed"],
        "seed_trajectory": {
            "x0": c["seed_traj_x0"], "dt": c["seed_traj_dt"],
            "tmax": c["seed_traj_tmax"], "burn_in": c["seed_traj_burn_in"],
        },
        "distinct_from_development": {
            "development_seed": 20260827,
            "development_seed_traj_x0": [1.0, 1.0, 1.0],
            "development_seed_traj_tmax": 400.0,
            "min_initial_state_distance_to_development": float(dmin.min()),
            "separation_threshold": thr,
            "violations": violations,
        },
        "trajectories": [],
    }

    ids = []
    for i, x0 in enumerate(x0s):
        traj = add_exact_derivatives(
            generate_lorenz(dt=c["dt"], tmax=c["tmax"],
                            x0=tuple(float(v) for v in x0))
        )
        tid = f"conf_{i:03d}"
        p = CONF / f"{tid}.parquet"
        traj.to_parquet(p, index=False)
        ids.append(tid)
        lineage["trajectories"].append({
            "id": tid, "x0": [float(v) for v in x0],
            "n_samples": int(len(traj)), "sha256": sha(p),
            "min_distance_to_development_x0": float(dmin[i]),
        })
    (MAN / "confirmation_lineage.json").write_text(
        json.dumps(lineage, indent=2), encoding="utf-8")

    # ---- development reference by hash only (never copied) ------------------
    dev_ref = {
        "status": "EXPOSED_DEVELOPMENT",
        "source": str(DEV_DIR),
        "note": "Referenced by hash; not copied. Protected-test results of the "
                "first benchmark were inspected and informed this design.",
        "trajectories": {
            p.stem: {"sha256": sha(p),
                     "x0": [float(v) for v in dev[p.stem]]}
            for p in sorted(DEV_DIR.glob("*.parquet"))
        },
    }
    (TCB / "prior_benchmark_reference" / "imported_hashes.json").write_text(
        json.dumps(dev_ref, indent=2), encoding="utf-8")

    print(f"\ngenerated {len(ids)} confirmation trajectories x "
          f"{lineage['trajectories'][0]['n_samples']} samples")
    print(f"referenced {len(dev_ref['trajectories'])} development trajectories by hash")


if __name__ == "__main__":
    main()
