"""Step 20 — automated tests for the task-conditioning benchmark."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

TCB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TCB))
sys.path.insert(0, str(TCB / "scripts"))
sys.path.insert(0, str(TCB.parent))
sys.path.insert(0, str(TCB.parent / "benchmark" / "scripts"))

import features as F  # noqa: E402
from Lorenz_attractor import BETA, RHO, SIGMA, generate_lorenz, lorenz  # noqa: E402
from sir_contract import qualification as QUAL  # noqa: E402
from sir_contract.scientific_object import (  # noqa: E402
    Admissibility, ScientificObject, UncertaintyModel,
)

CFG = yaml.safe_load((TCB / "benchmark_config.yaml").read_text(encoding="utf-8"))
CONF = TCB / "shared" / "confirmation"
MAN = TCB / "shared" / "manifests"


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ===========================================================================
# Generator / data
# ===========================================================================
def test_canonical_lorenz_identity():
    assert (SIGMA, RHO) == (10.0, 28.0)
    assert BETA == pytest.approx(8 / 3)
    x, y, z = 1.7, -0.9, 22.3
    dx, dy, dz = lorenz(0.0, [x, y, z])
    assert dx == pytest.approx(SIGMA * (y - x))
    assert dy == pytest.approx(x * (RHO - z) - y)
    assert dz == pytest.approx(x * y - BETA * z)


def test_generator_determinism():
    a = generate_lorenz(dt=0.01, tmax=1.5, x0=(0.5, -1.0, 12.0))
    b = generate_lorenz(dt=0.01, tmax=1.5, x0=(0.5, -1.0, 12.0))
    np.testing.assert_allclose(a["z"], b["z"], rtol=0, atol=0)


def test_confirmation_hashes_match_manifest():
    lin = json.loads((MAN / "confirmation_lineage.json").read_text())
    assert lin["status"] == "PROTECTED_CONFIRMATION"
    assert len(lin["trajectories"]) == CFG["confirmation"]["n_trajectories"]
    for t in lin["trajectories"]:
        p = CONF / f"{t['id']}.parquet"
        assert p.exists()
        assert _sha(p) == t["sha256"], f"hash drift in {t['id']}"


def test_development_referenced_by_hash_not_copied():
    ref = json.loads(
        (TCB / "prior_benchmark_reference" / "imported_hashes.json").read_text())
    assert ref["status"] == "EXPOSED_DEVELOPMENT"
    assert len(ref["trajectories"]) == 48
    # development parquets must NOT have been copied into this benchmark
    assert not list((TCB / "shared" / "development").glob("*.parquet"))


def test_confirmation_disjoint_from_development():
    lin = json.loads((MAN / "confirmation_lineage.json").read_text())
    ref = json.loads(
        (TCB / "prior_benchmark_reference" / "imported_hashes.json").read_text())
    conf_h = {t["sha256"] for t in lin["trajectories"]}
    dev_h = {v["sha256"] for v in ref["trajectories"].values()}
    assert not (conf_h & dev_h), "a confirmation file duplicates a development file"


def test_initial_states_are_not_near_duplicates():
    lin = json.loads((MAN / "confirmation_lineage.json").read_text())
    thr = CFG["confirmation"]["min_initial_state_separation"]
    d = [t["min_distance_to_development_x0"] for t in lin["trajectories"]]
    assert min(d) >= thr, f"closest confirmation x0 is {min(d)} < {thr}"
    assert lin["distinct_from_development"]["violations"] == []


def test_confirmation_seed_differs_from_development():
    lin = json.loads((MAN / "confirmation_lineage.json").read_text())
    d = lin["distinct_from_development"]
    assert lin["seed"] != d["development_seed"]
    assert lin["seed_trajectory"]["x0"] != d["development_seed_traj_x0"]


# ===========================================================================
# Admissibility / dependency
# ===========================================================================
def test_no_coordinate_depends_on_target():
    audit = F.dependency_audit()
    assert audit["violations"] == []
    assert audit["module_reads_z_column"] is False


def test_scientific_object_rejects_forbidden_dependency():
    obj = ScientificObject(
        name="t", channels=("x", "y", "z"), support="s", sampling={},
        uncertainty=UncertaintyModel(kind="numerical"),
        provenance={},
        admissibility=Admissibility(observed=("x", "y"), target="z",
                                    forbidden=("z", "dz", "d2z")))
    assert obj.assert_admissible({"good": {"x", "y"}}) == []
    assert obj.assert_admissible({"bad": {"x", "z"}}) == ["bad"]


# ===========================================================================
# Derivatives / noise ordering
# ===========================================================================
@pytest.mark.parametrize("w", [1.0, 3.0])
def test_derivative_stencil_accuracy(w):
    t = np.linspace(0, 4, 4001)
    dt = t[1] - t[0]
    d = F.d1_5pt(np.sin(w * t), dt)
    m = np.isfinite(d)
    np.testing.assert_allclose(d[m], (w * np.cos(w * t))[m], rtol=0, atol=1e-8)


def test_noise_is_applied_before_coordinate_construction():
    """Noisy coordinates must differ from coordinates of clean data."""
    import engine as E
    clean = E.build(E.load_split("confirmation", 0.0, None), None)
    noisy = E.build(E.load_split("confirmation", 0.01, 901), None)
    # the RATE (a derived quantity) must already carry the noise
    assert not np.allclose(clean[0]["base"]["dy"][2:-2],
                           noisy[0]["base"]["dy"][2:-2], atol=1e-9)
    # and the raw channel itself must differ
    assert not np.allclose(clean[0]["x"], noisy[0]["x"], atol=1e-12)


def test_noise_seeds_are_independent_between_splits():
    dev = set(CFG["noise"]["development_seeds"])
    conf = set(CFG["noise"]["confirmation_seeds"])
    assert not (dev & conf)


# ===========================================================================
# Qualification rules
# ===========================================================================
class _R:
    def __init__(self, mean, se, nc, terms, cond, folds):
        self.mean_rmse, self.se_rmse = mean, se
        self.n_coordinates, self.n_terms, self.cond = nc, terms, cond
        self.fold_rmse = folds


def test_one_se_rule_degenerates_without_the_floor():
    """Documents the defect that motivated the practical floor."""
    tab = {"big": _R(1e-5, 3e-7, 38, 29, 1e16, [1e-5] * 6),
           "small": _R(3e-5, 4e-7, 12, 12, 1e12, [3e-5] * 6)}
    _, info = QUAL.qualified_model_set(tab, practical_floor=0.0,
                                       lexicographic=("n_coordinates",))
    assert info["n_equivalent"] == 1, "without a floor the set should collapse"


def test_practical_floor_restores_the_equivalence_set():
    tab = {"big": _R(1e-5, 3e-7, 38, 29, 1e16, [1e-5] * 6),
           "small": _R(3e-5, 4e-7, 12, 12, 1e12, [3e-5] * 6)}
    pick, info = QUAL.qualified_model_set(
        tab, practical_floor=1e-3,
        lexicographic=("n_coordinates", "n_terms", "condition_number",
                       "fold_stability"))
    assert info["n_equivalent"] == 2
    assert info["margin_source"] == "practical_floor"
    assert pick == "small"


def test_accuracy_contract_ignores_complexity():
    tab = {"big": _R(1e-5, 3e-7, 38, 29, 1e16, [1e-5] * 6),
           "small": _R(3e-5, 4e-7, 12, 12, 1e12, [3e-5] * 6)}
    pick, _ = QUAL.select_min(tab)
    assert pick == "big"


def test_lexicographic_order_matches_declared_config():
    for q in ("q_compact", "q_robust"):
        assert CFG["contracts"][q]["lexicographic"] == [
            "n_coordinates", "n_terms", "condition_number", "fold_stability"]


# ===========================================================================
# Freeze enforcement
# ===========================================================================
def test_freeze_exists_and_hashes_match():
    fp = TCB / "PRECONFIRMATION_FREEZE.json"
    if not fp.exists():
        pytest.skip("freeze not yet written")
    fr = json.loads(fp.read_text())
    bad = [rel for rel, want in fr["files"].items()
           if hashlib.sha256((TCB / rel).read_bytes()).hexdigest() != want]
    assert bad == [], f"freeze violated for: {bad}"


def test_freeze_covers_every_selection_affecting_file():
    fp = TCB / "PRECONFIRMATION_FREEZE.json"
    if not fp.exists():
        pytest.skip("freeze not yet written")
    files = set(json.loads(fp.read_text())["files"])
    for required in ("benchmark_config.yaml",
                     "sir_contract/qualification.py",
                     "sir_contract/contract_runner.py",
                     "pysindy/external_contract_wrapper/wrapper.py"):
        assert required in files, f"{required} is not covered by the freeze"


# ===========================================================================
# PySINDy conventions
# ===========================================================================
def test_stlsq_has_no_intercept_so_target_must_be_centred():
    """Guards the bug found in the first benchmark."""
    from pysindy.optimizers import STLSQ
    rng = np.random.default_rng(0)
    X = rng.normal(size=(500, 3))
    y = 5.0 + X @ np.array([1.0, -2.0, 0.5])
    est = STLSQ(threshold=1e-6, alpha=0.0)
    est.fit(X, y)              # uncentred: no intercept available
    w = np.asarray(est.coef_, float).ravel()
    assert abs(np.mean(X @ w - y)) > 1.0, "STLSQ unexpectedly fitted an offset"
    est2 = STLSQ(threshold=1e-6, alpha=0.0)
    est2.fit(X, y - y.mean())  # centred: the offset is no longer in the target
    w2 = np.asarray(est2.coef_, float).ravel()
    # STLSQ applies mild shrinkage, so the claim under test is only that
    # centring removes the systematic offset an intercept-free fit cannot.
    resid_centred = float(np.sqrt(np.mean((X @ w2 + y.mean() - y) ** 2)))
    resid_raw = float(np.sqrt(np.mean((X @ w - y) ** 2)))
    assert resid_centred < 0.25 * resid_raw, (
        f"centring should dominate: {resid_centred:.3g} vs {resid_raw:.3g}")


def test_polynomial_library_dimensions():
    import engine as E
    X = np.zeros((4, 10))
    assert E.expand(X, "identity").shape[1] == 10
    assert E.expand(X, "poly2").shape[1] == 10 + 10 * 11 // 2
    assert E.expand(X, "poly3").shape[1] > E.expand(X, "poly2").shape[1]


def test_expand_returns_plain_ndarray():
    """PolynomialLibrary returns AxesArray, which breaks downstream matmul."""
    import engine as E
    out = E.expand(np.zeros((4, 3)), "poly2")
    assert type(out) is np.ndarray


# ===========================================================================
# Metrics
# ===========================================================================
def test_trajectory_is_the_statistical_unit():
    assert CFG["statistics"]["unit"] == "trajectory"


def test_metric_definitions():
    import engine as E
    y = np.array([1.0, 2.0, 3.0, 4.0])
    p = y + np.array([1.0, -1.0, 1.0, -1.0])
    assert E.rmse(y, p) == pytest.approx(1.0)
    assert E.nrmse(y, p) == pytest.approx(1.0 / np.std(y))


def test_bootstrap_is_reproducible():
    rng_a = np.random.default_rng(0).choice(np.arange(10.0), 10, replace=True)
    rng_b = np.random.default_rng(0).choice(np.arange(10.0), 10, replace=True)
    np.testing.assert_array_equal(rng_a, rng_b)


def test_tables_trace_to_machine_readable_files():
    for name in ("selection_stability.csv", "equivalence_sensitivity.csv"):
        p = TCB / "tables" / name
        if p.exists():
            assert len(pd.read_csv(p)) > 0
