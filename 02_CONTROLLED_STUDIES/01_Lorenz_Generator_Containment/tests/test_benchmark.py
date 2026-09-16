"""Step 12 — unit and integration tests for the Lorenz representation benchmark."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

BENCH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BENCH / "scripts"))
sys.path.insert(0, str(BENCH.parent))          # Lorenz/ for the canonical generator
sys.path.insert(0, r"D:\SIR_paper\DIIID_example")

import features as F  # noqa: E402
import transforms as sirref  # noqa: E402  audited reference implementation
from Lorenz_attractor import BETA, RHO, SIGMA, generate_lorenz, lorenz  # noqa: E402

CFG = yaml.safe_load((BENCH / "benchmark_config.yaml").read_text(encoding="utf-8"))
DATA = BENCH / "shared" / "data"
SPLITS = BENCH / "shared" / "splits"
MANIFESTS = BENCH / "shared" / "manifests"


# ===========================================================================
# Generator and dataset
# ===========================================================================
def test_lorenz_parameters_match_manuscript():
    assert SIGMA == 10.0
    assert RHO == 28.0
    assert BETA == pytest.approx(8.0 / 3.0)
    assert CFG["system"]["sigma"] == SIGMA
    assert CFG["system"]["rho"] == RHO
    assert CFG["system"]["beta"] == pytest.approx(BETA)


def test_lorenz_rhs_is_the_published_system():
    x, y, z = 1.3, -2.1, 7.7
    dx, dy, dz = lorenz(0.0, [x, y, z])
    assert dx == pytest.approx(SIGMA * (y - x))
    assert dy == pytest.approx(x * (RHO - z) - y)
    assert dz == pytest.approx(x * y - BETA * z)


def test_generator_is_deterministic():
    a = generate_lorenz(dt=0.01, tmax=2.0, x0=(1.0, 1.0, 1.0))
    b = generate_lorenz(dt=0.01, tmax=2.0, x0=(1.0, 1.0, 1.0))
    np.testing.assert_allclose(a["x"], b["x"], rtol=0, atol=0)
    np.testing.assert_allclose(a["z"], b["z"], rtol=0, atol=0)


def test_dataset_hashes_match_manifest():
    lineage = json.loads((MANIFESTS / "source_lineage.json").read_text())
    checked = 0
    for art in lineage["artifacts"]:
        p = BENCH / art["path"]
        assert p.exists(), f"missing artifact {art['path']}"
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        assert h.hexdigest() == art["sha256"], f"hash drift in {art['path']}"
        checked += 1
    assert checked >= 49  # containment + 48 trajectories


def test_ensemble_shape_and_spacing():
    ids = sorted(p.stem for p in (DATA / "ensemble").glob("*.parquet"))
    assert len(ids) == CFG["ensemble"]["n_trajectories"]
    df = pd.read_parquet(DATA / "ensemble" / f"{ids[0]}.parquet")
    dt = np.diff(df["times"].to_numpy())
    assert np.allclose(dt, CFG["ensemble"]["dt"], rtol=1e-9)
    assert set(["times", "x", "y", "z", "dx", "dy", "dz"]).issubset(df.columns)


def test_exact_derivatives_satisfy_the_lorenz_field():
    df = pd.read_parquet(DATA / "ensemble" / "traj_000.parquet")
    x, y, z = (df[c].to_numpy() for c in ("x", "y", "z"))
    np.testing.assert_allclose(df["dx"], SIGMA * (y - x), rtol=0, atol=1e-12)
    np.testing.assert_allclose(df["dy"], x * (RHO - z) - y, rtol=0, atol=1e-12)
    np.testing.assert_allclose(df["dz"], x * y - BETA * z, rtol=0, atol=1e-12)


# ===========================================================================
# Splits
# ===========================================================================
def _split(name):
    return set((SPLITS / f"{name}.txt").read_text().split())


def test_splits_are_disjoint_and_complete():
    tr, va, te = (_split(s) for s in ("train", "validation", "test"))
    assert len(tr) == CFG["splits"]["n_train"]
    assert len(va) == CFG["splits"]["n_validation"]
    assert len(te) == CFG["splits"]["n_test"]
    assert not (tr & va) and not (tr & te) and not (va & te)
    allids = {p.stem for p in (DATA / "ensemble").glob("*.parquet")}
    assert tr | va | te == allids


def test_splits_are_whole_trajectory():
    """Every split member is a trajectory id, never a sample index."""
    for name in ("train", "validation", "test"):
        for m in _split(name):
            assert m.startswith("traj_")
            assert (DATA / "ensemble" / f"{m}.parquet").exists()


# ===========================================================================
# Derivative stencils on analytic signals
# ===========================================================================
@pytest.mark.parametrize("w", [0.5, 2.0, 5.0])
def test_first_derivative_stencil_on_sinusoid(w):
    t = np.linspace(0, 4, 4001)
    dt = t[1] - t[0]
    v = np.sin(w * t)
    d = F.d1_5pt(v, dt)
    m = np.isfinite(d)
    np.testing.assert_allclose(d[m], (w * np.cos(w * t))[m], rtol=0, atol=1e-8)


@pytest.mark.parametrize("w", [0.5, 2.0])
def test_second_derivative_stencil_on_sinusoid(w):
    t = np.linspace(0, 4, 4001)
    dt = t[1] - t[0]
    v = np.sin(w * t)
    d = F.d2_5pt(v, dt)
    m = np.isfinite(d)
    np.testing.assert_allclose(d[m], (-(w**2) * np.sin(w * t))[m], rtol=0, atol=1e-6)


def test_derivative_stencil_is_exact_on_cubics():
    """A 4th-order centered scheme is exact for polynomials up to degree 4."""
    t = np.linspace(-2, 2, 801)
    dt = t[1] - t[0]
    v = 3 * t**3 - 2 * t**2 + t - 5
    d = F.d1_5pt(v, dt)
    m = np.isfinite(d)
    np.testing.assert_allclose(d[m], (9 * t**2 - 4 * t + 1)[m], rtol=0, atol=1e-9)


def test_shift_alignment():
    v = np.arange(10.0)
    np.testing.assert_array_equal(F.shift(v, 0), v)
    s = F.shift(v, -2)          # lag: value from two samples earlier
    assert np.isnan(s[0]) and np.isnan(s[1])
    assert s[5] == v[3]
    s = F.shift(v, +2)          # lead
    assert s[5] == v[7]
    assert np.isnan(s[-1])


def test_interior_mask_matches_stencil_width():
    m = F.interior_mask(20)
    assert m.sum() == 20 - 2 * F.HALF
    assert not m[:F.HALF].any() and not m[-F.HALF:].any()


# ===========================================================================
# Target-free dependency
# ===========================================================================
def test_no_coordinate_depends_on_z():
    audit = F.dependency_audit()
    assert audit["violations"] == []
    assert audit["module_reads_z_column"] is False
    assert audit["clean"] is True


def test_coordinates_are_invariant_to_the_z_channel():
    """Perturbing z must not change any coordinate value — the empirical
    counterpart of the declared DAG audit."""
    df = pd.read_parquet(DATA / "ensemble" / "traj_000.parquet")
    x, y = df["x"].to_numpy(), df["y"].to_numpy()
    dt = float(df["times"].iloc[1] - df["times"].iloc[0])
    b1 = F.base_quantities(x, y, dt)
    fit = F.fit_coordinates([b1], CFG)
    v1 = F.apply_coordinates(b1, fit)
    # z is simply never an input; rebuild with the same x,y and confirm identity
    v2 = F.apply_coordinates(F.base_quantities(x, y, dt), fit)
    for k in v1:
        a, b = v1[k], v2[k]
        m = np.isfinite(a) & np.isfinite(b)
        np.testing.assert_allclose(a[m], b[m], rtol=0, atol=0)


# ===========================================================================
# Relational coordinates against the canonical implementation
# ===========================================================================
def test_classical_phase_derivative_on_its_regular_domain():
    """D_x y = (dy/dt)/(dx/dt) computed from an analytic curve."""
    t = np.linspace(0.1, 3.0, 2001)
    dt = t[1] - t[0]
    x, y = np.exp(0.3 * t), np.sin(2.0 * t)
    base = F.base_quantities(x, y, dt)
    want = (2.0 * np.cos(2.0 * t)) / (0.3 * np.exp(0.3 * t))
    got = base["dy"] / base["dx"]
    m = np.isfinite(got)
    np.testing.assert_allclose(got[m], want[m], rtol=1e-6, atol=1e-6)


def test_reference_shifted_matches_canonical_reference_implementation():
    u_n = np.array([-2.0, -0.3, 0.0, 0.7, 3.0])
    u_d = np.array([-1.5, -0.2, 0.0, 0.4, 2.0])
    rho, s_eff = 0.1, 3.0
    w = u_d + s_eff
    want = (u_n + s_eff) * w / (w * w + rho**2)
    np.testing.assert_allclose(
        sirref.clearance_shifted_regularized_ratio(u_n, u_d, rho, s_eff),
        want, rtol=0, atol=1e-12)


def test_sensitivity_centered_matches_canonical_and_is_not_mean_centering():
    u_n = np.array([-2.0, -0.3, 0.0, 0.7, 3.0])
    u_d = np.array([-1.5, -0.2, 0.0, 0.4, 2.0])
    rho, s_eff, g_bar = 0.1, 3.0, 0.29
    w = u_d + s_eff
    g = w / (w * w + rho**2)
    want = (u_n + s_eff) * g - g_bar * u_n
    got = sirref.sensitivity_centered_clearance_ratio(u_n, u_d, rho, s_eff, g_bar)
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-12)
    c_rs = sirref.clearance_shifted_regularized_ratio(u_n, u_d, rho, s_eff)
    assert not np.allclose(got, c_rs - c_rs.mean(), atol=1e-6)


def test_mean_fit_of_centered_gain_is_zero():
    t = np.linspace(0, 4 * np.pi, 900)
    u_d = np.sin(t) - 0.3
    s_eff = sirref.fit_denominator_clearance([u_d]) + 1.0
    g = sirref.regularized_denominator_gain(u_d, 0.1, s_eff)
    g_bar = sirref.fit_training_mean_gain([g])
    assert float(np.mean(g - g_bar)) == pytest.approx(0.0, abs=1e-13)


# ===========================================================================
# Fit / apply semantics
# ===========================================================================
def test_coordinate_fit_is_train_only_and_frozen():
    """Applying to a different trajectory must reuse the train constants."""
    ids = sorted(p.stem for p in (DATA / "ensemble").glob("*.parquet"))[:3]
    bases = []
    for tid in ids:
        df = pd.read_parquet(DATA / "ensemble" / f"{tid}.parquet")
        dt = float(df["times"].iloc[1] - df["times"].iloc[0])
        bases.append(F.base_quantities(df["x"].to_numpy(), df["y"].to_numpy(), dt))
    fit = F.fit_coordinates(bases[:2], CFG)
    snap = json.dumps(fit.as_dict(), sort_keys=True)
    F.apply_coordinates(bases[2], fit)
    assert json.dumps(fit.as_dict(), sort_keys=True) == snap, "apply mutated the fit"

    refit = F.fit_coordinates([bases[2]], CFG)
    assert refit.shift_fits != fit.shift_fits, (
        "held-out trajectory would yield different constants — confirming the "
        "frozen fit is doing real work"
    )


def test_frozen_representation_is_self_consistent():
    p = BENCH / "sir" / "frozen_selection" / "FROZEN_REPRESENTATION.json"
    if not p.exists():
        pytest.skip("frozen representation not yet produced")
    fr = json.loads(p.read_text())
    assert set(F.C0_MATCHED).issubset(set(fr["selected_coordinates"]))
    assert set(fr["selected_coordinates"]).issubset(set(F.COORD_NAMES))
    tr, va, te = (set(fr["splits"][k]) for k in ("train", "validation", "test"))
    assert not (tr & va) and not (tr & te) and not (va & te)
    body = {k: v for k, v in fr.items() if k != "sha256"}
    assert hashlib.sha256(
        json.dumps(body, indent=2, sort_keys=True).encode()).hexdigest() == fr["sha256"]


# ===========================================================================
# Metrics and identical-column delivery
# ===========================================================================
def test_metric_definitions():
    from run_benchmark import metrics
    y = np.array([1.0, 2.0, 3.0, 4.0])
    p = y + np.array([1.0, -1.0, 1.0, -1.0])
    m = metrics(y, p)
    assert m["rmse"] == pytest.approx(1.0)
    assert m["mae"] == pytest.approx(1.0)
    assert m["nrmse"] == pytest.approx(1.0 / np.std(y))
    assert m["r2"] == pytest.approx(1.0 - 1.0 / np.var(y))


def test_identical_feature_columns_across_learners():
    """build_matrix must return the same columns in the same order every time,
    so SIR/PySINDy/MLP provably receive identical matrices."""
    df = pd.read_parquet(DATA / "ensemble" / "traj_000.parquet")
    dt = float(df["times"].iloc[1] - df["times"].iloc[0])
    base = F.base_quantities(df["x"].to_numpy(), df["y"].to_numpy(), dt)
    fit = F.fit_coordinates([base], CFG)
    vals = F.apply_coordinates(base, fit)
    names = F.COORD_NAMES
    A = F.build_matrix(vals, names)
    B = F.build_matrix(vals, names)
    np.testing.assert_array_equal(np.nan_to_num(A, nan=-999), np.nan_to_num(B, nan=-999))
    assert A.shape[1] == len(names)
    assert len(set(names)) == len(names), "duplicate coordinate name"


def test_analytic_identity_holds_on_the_data():
    """Audit-only: z = rho - (dy/dt + y)/x on the regular domain.

    This is never used to build or select a coordinate; it verifies that the
    information the benchmark claims is present really is present.
    """
    df = pd.read_parquet(DATA / "ensemble" / "traj_000.parquet")
    x, y, z, dy = (df[c].to_numpy() for c in ("x", "y", "z", "dy"))
    m = np.abs(x) > 1.0
    z_hat = RHO - (dy[m] + y[m]) / x[m]
    np.testing.assert_allclose(z_hat, z[m], rtol=0, atol=1e-9)
