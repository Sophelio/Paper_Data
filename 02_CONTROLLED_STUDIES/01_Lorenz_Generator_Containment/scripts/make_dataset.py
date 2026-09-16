"""Build the Lorenz benchmark dataset: containment trajectory + ensemble + splits.

REUSES the canonical manuscript generator
``D:\\SIR_paper\\Lorenz\\Lorenz_attractor.py::generate_lorenz`` (DOP853,
rtol=atol=1e-12) rather than re-implementing the integration. Nothing under
``D:\\SIR_paper\\Lorenz\\`` outside ``benchmark/`` is written to.

Outputs
-------
shared/data/containment.parquet          reused canonical single trajectory
shared/data/ensemble/traj_XXX.parquet    benchmark ensemble
shared/splits/{train,validation,test}.txt
shared/manifests/source_lineage.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

BENCH = Path(__file__).resolve().parent.parent
LORENZ_DIR = BENCH.parent
sys.path.insert(0, str(LORENZ_DIR))

from Lorenz_attractor import (  # noqa: E402  canonical manuscript generator
    BETA,
    RHO,
    SIGMA,
    add_exact_derivatives,
    generate_lorenz,
)

CFG = yaml.safe_load((BENCH / "benchmark_config.yaml").read_text(encoding="utf-8"))

DATA = BENCH / "shared" / "data"
ENS = DATA / "ensemble"
SPLITS = BENCH / "shared" / "splits"
MANIFESTS = BENCH / "shared" / "manifests"
for d in (DATA, ENS, SPLITS, MANIFESTS):
    d.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sample_initial_states(n: int, seed: int) -> np.ndarray:
    """Reproducible on-attractor initial states.

    A single long canonical trajectory is integrated once, its transient
    discarded, and ``n`` states are drawn from the remaining samples at evenly
    spaced indices with a seeded random offset. Every returned state therefore
    lies ON the Lorenz attractor (not in an arbitrary box), which keeps every
    benchmark trajectory on the same invariant set.
    """
    seeder = generate_lorenz(
        dt=CFG["ensemble"]["seed_traj_dt"],
        tmax=CFG["ensemble"]["seed_traj_tmax"],
        x0=tuple(CFG["ensemble"]["seed_traj_x0"]),
    )
    burn = CFG["ensemble"]["seed_traj_burn_in"]
    keep = seeder[seeder["times"] >= burn]
    states = keep[["x", "y", "z"]].to_numpy(dtype=np.float64)

    rng = np.random.default_rng(seed)
    # Evenly spaced blocks + one seeded offset per block: reproducible, spread
    # over the whole attractor, and never two near-duplicate initial states.
    edges = np.linspace(0, len(states), n + 1).astype(int)
    idx = np.array(
        [rng.integers(edges[i], edges[i + 1]) for i in range(n)], dtype=int
    )
    return states[idx]


def main() -> None:
    lineage = {
        "generator": {
            "module": str(LORENZ_DIR / "Lorenz_attractor.py"),
            "function": "generate_lorenz",
            "sha256": sha256_file(LORENZ_DIR / "Lorenz_attractor.py"),
            "reused": True,
            "integrator": "scipy.integrate.solve_ivp(method='DOP853')",
            "rtol": 1e-12,
            "atol": 1e-12,
        },
        "parameters": {"sigma": SIGMA, "rho": RHO, "beta": BETA},
        "artifacts": [],
    }

    # ---- containment trajectory: REUSE the canonical parquet ---------------
    src = LORENZ_DIR / "data" / "lorenz_dt001_exact_derivatives.parquet"
    df = pd.read_parquet(src)
    dst = DATA / "containment.parquet"
    df.to_parquet(dst, index=False)
    lineage["artifacts"].append(
        {
            "path": str(dst.relative_to(BENCH)),
            "origin": str(src),
            "origin_sha256": sha256_file(src),
            "sha256": sha256_file(dst),
            "status": "REUSED (copied verbatim from the manuscript dataset)",
            "n_samples": int(len(df)),
            "dt": float(df["times"].iloc[1] - df["times"].iloc[0]),
            "columns": list(df.columns),
        }
    )
    print(f"containment: reused {src.name} -> {len(df)} samples")

    # ---- benchmark ensemble: NEWLY GENERATED with the same generator -------
    ens_cfg = CFG["ensemble"]
    n_traj = ens_cfg["n_trajectories"]
    x0s = sample_initial_states(n_traj, ens_cfg["seed"])

    ids = []
    for i, x0 in enumerate(x0s):
        traj = generate_lorenz(
            dt=ens_cfg["dt"], tmax=ens_cfg["tmax"], x0=tuple(float(v) for v in x0)
        )
        traj = add_exact_derivatives(traj)
        tid = f"traj_{i:03d}"
        path = ENS / f"{tid}.parquet"
        traj.to_parquet(path, index=False)
        ids.append(tid)
        lineage["artifacts"].append(
            {
                "path": str(path.relative_to(BENCH)),
                "status": "GENERATED",
                "trajectory_id": tid,
                "x0": [float(v) for v in x0],
                "n_samples": int(len(traj)),
                "dt": ens_cfg["dt"],
                "tmax": ens_cfg["tmax"],
                "sha256": sha256_file(path),
            }
        )
    print(f"ensemble: generated {n_traj} trajectories x {len(traj)} samples")

    # ---- frozen whole-trajectory splits ------------------------------------
    rng = np.random.default_rng(CFG["splits"]["seed"])
    order = rng.permutation(ids)
    n_tr = CFG["splits"]["n_train"]
    n_va = CFG["splits"]["n_validation"]
    parts = {
        "train": sorted(order[:n_tr].tolist()),
        "validation": sorted(order[n_tr : n_tr + n_va].tolist()),
        "test": sorted(order[n_tr + n_va :].tolist()),
    }
    for name, members in parts.items():
        (SPLITS / f"{name}.txt").write_text("\n".join(members) + "\n", encoding="utf-8")
        print(f"split {name}: {len(members)} trajectories")

    assert not (set(parts["train"]) & set(parts["validation"]))
    assert not (set(parts["train"]) & set(parts["test"]))
    assert not (set(parts["validation"]) & set(parts["test"]))
    assert sum(len(v) for v in parts.values()) == n_traj

    lineage["splits"] = {
        k: {"n": len(v), "members": v, "sha256": hashlib.sha256(
            ("\n".join(v)).encode()).hexdigest()}
        for k, v in parts.items()
    }
    (MANIFESTS / "source_lineage.json").write_text(
        json.dumps(lineage, indent=2), encoding="utf-8"
    )
    print(f"\nwrote {MANIFESTS / 'source_lineage.json'}")


if __name__ == "__main__":
    main()
