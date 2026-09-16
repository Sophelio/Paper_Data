"""Generate an analytic heat-equation dataset for SIR.

The example uses the 1D heat equation

    u_t = kappa * u_xx

with a separable mode solution

    u(x,t) = exp(-(m*pi)^2 * kappa * t) * sin(m*pi*x).

For each realization we emit vectors (all same length):
    u, du_dx, d2u_dx2, du_dt, d2u_dt2
along with x/t coordinates and metadata.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / "data"

# Grid (default flattened length = NX * NT = 10,000)
NX = 100
NT = 100
X_MIN = 0.0
X_MAX = 1.0
T_MIN = 0.0
T_MAX = 1.0

# Adjustable scalar parameters for a single realization.
KAPPA = 0.24
MODE = 2


def generate_realization(
    nx: int = NX,
    nt: int = NT,
    kappa: float = 0.24,
    mode: int = 2,
    x_min: float = X_MIN,
    x_max: float = X_MAX,
    t_min: float = T_MIN,
    t_max: float = T_MAX,
) -> pd.DataFrame:
    """Build one realization sampled on an (x,t) tensor grid."""
    x = np.linspace(x_min, x_max, nx, dtype=np.float64)
    t = np.linspace(t_min, t_max, nt, dtype=np.float64)
    xx, tt = np.meshgrid(x, t, indexing="xy")

    w = float(mode) * np.pi
    decay = np.exp(-(w**2) * float(kappa) * tt)
    trig = np.sin(w * xx)
    u = decay * trig

    du_dx = w * decay * np.cos(w * xx)
    d2u_dx2 = -(w**2) * u
    du_dt = -(w**2) * float(kappa) * u
    d2u_dt2 = (w**4) * (float(kappa) ** 2) * u

    n = nx * nt
    # "times" is a monotonic sample index used by the provider contract.
    times = np.arange(n, dtype=np.float64)

    return pd.DataFrame(
        {
            "times": times,
            "x": xx.reshape(-1),
            "t": tt.reshape(-1),
            "u": u.reshape(-1),
            "du_dx": du_dx.reshape(-1),
            "d2u_dx2": d2u_dx2.reshape(-1),
            "du_dt": du_dt.reshape(-1),
            "d2u_dt2": d2u_dt2.reshape(-1),
            "kappa": np.full(n, float(kappa), dtype=np.float64),
            "mode": np.full(n, int(mode), dtype=np.int64),
        }
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Keep the folder in single-realization mode: remove older generated files.
    for old in DATA_DIR.glob("realization_*.parquet"):
        old.unlink()

    df = generate_realization(kappa=float(KAPPA), mode=int(MODE))
    out = DATA_DIR / "realization_00.parquet"
    df.to_parquet(out, index=False)

    print(f"Wrote 1 heat-equation realization to {DATA_DIR}")
    print(f"kappa={KAPPA}, mode={MODE}")
    print("Columns: times, x, t, u, du_dx, d2u_dx2, du_dt, d2u_dt2, kappa, mode")
    print(f"Grid per realization: nx={NX}, nt={NT}, flattened length={NX * NT}")


if __name__ == "__main__":
    main()
