"""Admissible coordinate library for the hidden-z Lorenz reconstruction task.

INFORMATION BOUNDARY
--------------------
Every coordinate is a function of the common retrospective local information set

    I_k = { x[k-2..k+2], y[k-2..k+2] }

and nothing else. z, dz, and every z-derived quantity are excluded by
construction: no builder in this module ever reads the ``z`` column, and
``dependency_audit`` re-checks the declared DAG.

This is RETROSPECTIVE RECONSTRUCTION, not forecasting: symmetric (centered)
stencils are deliberate and admissible because the task is to recover z(t_k)
from observations around t_k, never to predict forward.

RELATIONAL COORDINATES
----------------------
The reference-shifted and sensitivity-centered phase coordinates are taken from
the audited reference implementation

    D:/SIR_paper/DIIID_example/transforms.py

which was verified elementwise (rtol=0, atol=1e-12) against the canonical
Archaieus implementation in AUDIT_dalia_transform_family.md. They are NOT
re-derived here.

Manuscript convention: D_g f = (df/dt)/(dg/dt); the subscript is the reference.

SCIENTIFIC NOTE (audit only, never hard-coded)
----------------------------------------------
For the Lorenz system, dy/dt = x(rho - z) - y gives, where x != 0,

    z = rho - (dy/dt + y)/x

so information about z lives in quotients whose DENOMINATOR IS THE LEVEL x, and
equivalently (via dx/dt = sigma(y-x)) in the phase quotient D_x y. The grammar
below therefore admits level denominators as well as rate denominators, and
lets the search decide. No coordinate is forced or weighted toward the identity.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

BENCH = Path(__file__).resolve().parent.parent
REF_IMPL = Path(r"D:\SIR_paper\DIIID_example")
if str(REF_IMPL) not in sys.path:
    sys.path.insert(0, str(REF_IMPL))

import transforms as sirref  # noqa: E402  audited reference implementation

HALF = 2  # centered five-point stencil half-width


# ===========================================================================
# Derivatives on the declared stencil
# ===========================================================================
def d1_5pt(v: np.ndarray, dt: float) -> np.ndarray:
    """Fourth-order centered first derivative on the five-point stencil.

    (v[k-2] - 8 v[k-1] + 8 v[k+1] - v[k+2]) / (12 dt), interior only.
    Returns an array of the full length with the 2 edge samples on each side
    set to NaN; those samples are dropped from the shared mask for ALL methods.
    """
    out = np.full_like(v, np.nan, dtype=np.float64)
    out[2:-2] = (v[:-4] - 8.0 * v[1:-3] + 8.0 * v[3:-1] - v[4:]) / (12.0 * dt)
    return out


def d2_5pt(v: np.ndarray, dt: float) -> np.ndarray:
    """Fourth-order centered second derivative on the same five-point stencil."""
    out = np.full_like(v, np.nan, dtype=np.float64)
    out[2:-2] = (
        -v[:-4] + 16.0 * v[1:-3] - 30.0 * v[2:-2] + 16.0 * v[3:-1] - v[4:]
    ) / (12.0 * dt * dt)
    return out


def shift(v: np.ndarray, k: int) -> np.ndarray:
    """v[i+k] aligned to index i, NaN outside. k<0 is a lag, k>0 a lead."""
    out = np.full_like(v, np.nan, dtype=np.float64)
    n = len(v)
    if k == 0:
        return v.astype(np.float64).copy()
    if k < 0:
        out[-k:] = v[: n + k]
    else:
        out[: n - k] = v[k:]
    return out


# ===========================================================================
# Coordinate declaration
# ===========================================================================
@dataclass(frozen=True)
class Coord:
    """One candidate coordinate and its declared provenance."""

    name: str
    family: str          # raw | rate | curvature | lag | product | quotient
                         # | ca_ratio | reference_shifted | sensitivity_centered
    depends_on: tuple    # observable symbols this coordinate is built from
    needs_fit: bool = False
    note: str = ""
    params: dict = field(default_factory=dict)


# The finite, auditable grammar. Denominators include BOTH levels and rates.
QUOTIENT_SPECS = [
    # (numerator, denominator) — chosen because these are the quotients whose
    # regular domains carry z-information; see the module docstring.
    ("dy", "x"),
    ("y", "x"),
    ("dy", "dx"),   # classical phase derivative D_x y
    ("dx", "dy"),   # classical phase derivative D_y x
]
PRODUCT_SPECS = [
    ("x", "y"), ("x", "x"), ("y", "y"),
    ("x", "dy"), ("y", "dx"), ("dx", "dy"), ("x", "dx"), ("y", "dy"),
]


def declare_coordinates() -> list[Coord]:
    """The complete candidate set C_all, in a fixed, reproducible order."""
    coords: list[Coord] = []

    # -- C0: the information-matched raw stencil ---------------------------
    for base in ("x", "y"):
        for k in range(-HALF, HALF + 1):
            nm = f"{base}[k{k:+d}]" if k else base
            coords.append(
                Coord(nm, "raw", (base,), note="declared information boundary")
            )

    # -- rates and curvature ------------------------------------------------
    for base in ("x", "y"):
        coords.append(Coord(f"d{base}", "rate", (base,),
                            note="4th-order centered 5-point"))
    for base in ("x", "y"):
        coords.append(Coord(f"d2{base}", "curvature", (base,),
                            note="4th-order centered 5-point"))

    # -- algebraic products -------------------------------------------------
    for a, b in PRODUCT_SPECS:
        coords.append(Coord(f"{a}*{b}", "product", tuple(sorted({a[-1], b[-1]}))))

    # -- masked classical quotients ----------------------------------------
    for num, den in QUOTIENT_SPECS:
        coords.append(
            Coord(
                f"Q[{num}|{den}]", "quotient",
                tuple(sorted({num[-1], den[-1]})),
                needs_fit=True,
                note="masked where |denominator| below the train quantile",
            )
        )

    # -- regularized / reference-shifted / sensitivity-centered -------------
    for num, den in QUOTIENT_SPECS:
        coords.append(
            Coord(f"CA[{num}|{den}]", "ca_ratio",
                  tuple(sorted({num[-1], den[-1]})), needs_fit=True,
                  note="u_n u_d/(u_d^2+rho^2); no shift")
        )
        coords.append(
            Coord(f"RS[{num}|{den}]", "reference_shifted",
                  tuple(sorted({num[-1], den[-1]})), needs_fit=True,
                  note="(u_n+s_eff) g(w); s_0 on normalized denominator")
        )
        coords.append(
            Coord(f"SC[{num}|{den}]", "sensitivity_centered",
                  tuple(sorted({num[-1], den[-1]})), needs_fit=True,
                  note="RS - g_bar u_n; g_bar frozen on train")
        )
    return coords


COORDS = declare_coordinates()
COORD_NAMES = [c.name for c in COORDS]
C0_CENTER = ["x", "y"]
C0_MATCHED = [c.name for c in COORDS if c.family == "raw"]


# ===========================================================================
# Base quantity evaluation (per trajectory)
# ===========================================================================
def base_quantities(x: np.ndarray, y: np.ndarray, dt: float) -> dict:
    """Evaluate the primitive observables on one trajectory.

    Reads ONLY x and y. z is never passed in.
    """
    return {
        "x": np.asarray(x, dtype=np.float64),
        "y": np.asarray(y, dtype=np.float64),
        "dx": d1_5pt(x, dt),
        "dy": d1_5pt(y, dt),
        "d2x": d2_5pt(x, dt),
        "d2y": d2_5pt(y, dt),
    }


def interior_mask(n: int) -> np.ndarray:
    """Samples with a complete five-point stencil. Shared by ALL methods."""
    m = np.zeros(n, dtype=bool)
    m[HALF : n - HALF] = True
    return m


# ===========================================================================
# FIT (train only) / APPLY (any split)
# ===========================================================================
@dataclass
class CoordinateFit:
    """All train-fitted quantities, frozen for application to held-out data."""

    rho: float
    kappa: float
    scale_method: str
    scales: dict = field(default_factory=dict)        # symbol -> operand scale
    shift_fits: dict = field(default_factory=dict)    # "num|den" -> dict
    quotient_floor: dict = field(default_factory=dict)  # den -> |.| threshold

    def as_dict(self) -> dict:
        return {
            "rho": self.rho,
            "kappa": self.kappa,
            "scale_method": self.scale_method,
            "scales": {k: float(v) for k, v in self.scales.items()},
            "shift_fits": {
                k: {kk: float(vv) for kk, vv in v.items()}
                for k, v in self.shift_fits.items()
            },
            "quotient_floor": {k: float(v) for k, v in self.quotient_floor.items()},
        }


def fit_coordinates(train_bases: list[dict], cfg: dict) -> CoordinateFit:
    """Fit every fit-dependent quantity on TRAIN trajectories only."""
    ccfg = cfg["coordinates"]
    rho = float(ccfg["rho"])
    kappa = float(ccfg["kappa"])
    method = str(ccfg["scale_method"])
    fit = CoordinateFit(rho=rho, kappa=kappa, scale_method=method)

    symbols = ("x", "y", "dx", "dy", "d2x", "d2y")
    for sym in symbols:
        fit.scales[sym] = sirref.fit_operand_scale(
            [b[sym] for b in train_bases], method
        )

    q = float(ccfg["quotient_mask_quantile"])
    for _, den in QUOTIENT_SPECS:
        pooled = np.concatenate([np.abs(sirref.finite(b[den])) for b in train_bases])
        fit.quotient_floor[den] = float(np.quantile(pooled, q))

    for num, den in QUOTIENT_SPECS:
        S_n, S_d = fit.scales[num], fit.scales[den]
        u_d_list = [b[den] / S_d for b in train_bases]
        s_0 = sirref.fit_denominator_clearance(u_d_list)
        s_eff = s_0 + kappa
        g_bar = sirref.fit_training_mean_gain(
            [sirref.regularized_denominator_gain(u, rho, s_eff) for u in u_d_list]
        )
        fit.shift_fits[f"{num}|{den}"] = {
            "S_n": S_n, "S_d": S_d, "s_0": s_0, "s_eff": s_eff, "g_bar": g_bar,
        }
    return fit


def apply_coordinates(base: dict, fit: CoordinateFit) -> dict:
    """Evaluate every declared coordinate using FROZEN fit parameters."""
    out: dict[str, np.ndarray] = {}

    for b in ("x", "y"):
        for k in range(-HALF, HALF + 1):
            nm = f"{b}[k{k:+d}]" if k else b
            out[nm] = shift(base[b], k)
    for b in ("x", "y"):
        out[f"d{b}"] = base[f"d{b}"]
        out[f"d2{b}"] = base[f"d2{b}"]
    for a, b in PRODUCT_SPECS:
        out[f"{a}*{b}"] = base[a] * base[b]

    for num, den in QUOTIENT_SPECS:
        d = base[den]
        floor = fit.quotient_floor[den]
        with np.errstate(divide="ignore", invalid="ignore"):
            q = base[num] / d
        q = np.where(np.abs(d) >= floor, q, np.nan)
        out[f"Q[{num}|{den}]"] = q

        f = fit.shift_fits[f"{num}|{den}"]
        u_n = base[num] / f["S_n"]
        u_d = d / f["S_d"]
        out[f"CA[{num}|{den}]"] = sirref.regularized_ratio(u_n, u_d, fit.rho)
        out[f"RS[{num}|{den}]"] = sirref.clearance_shifted_regularized_ratio(
            u_n, u_d, fit.rho, f["s_eff"]
        )
        out[f"SC[{num}|{den}]"] = sirref.sensitivity_centered_clearance_ratio(
            u_n, u_d, fit.rho, f["s_eff"], f["g_bar"]
        )
    return out


def build_matrix(coord_values: dict, names: list[str]) -> np.ndarray:
    """Stack named coordinates into an (n_samples, n_coords) matrix."""
    return np.column_stack([coord_values[n] for n in names])


# ===========================================================================
# Audits
# ===========================================================================
def dependency_audit() -> dict:
    """Assert no declared coordinate depends on z or any z-derived quantity."""
    forbidden = {"z", "dz", "d2z"}
    violations = [
        c.name for c in COORDS if forbidden & set(c.depends_on)
    ]
    src = Path(__file__).read_text(encoding="utf-8")
    # The builders must never index a 'z' column. The needles are assembled at
    # runtime so this check cannot match its own source literal.
    z = chr(122)
    needles = (f'base["{z}"]', f"base['{z}']", f'["d{z}"]', f'["d2{z}"]')
    reads_z = any(n in src for n in needles)
    return {
        "n_coordinates": len(COORDS),
        "forbidden_symbols": sorted(forbidden),
        "violations": violations,
        "module_reads_z_column": reads_z,
        "clean": (not violations) and (not reads_z),
    }
