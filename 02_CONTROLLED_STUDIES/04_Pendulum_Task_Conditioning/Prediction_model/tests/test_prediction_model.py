"""Tests for the frozen holdout prediction model."""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PENDULUM = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PENDULUM) not in sys.path:
    sys.path.insert(0, str(PENDULUM))

from prediction_model import (  # noqa: E402
    AUDIT_A,
    AUDIT_B,
    FORBIDDEN_SELECTABLE,
    HOLDOUT_RECORD_IDS,
    OBSERVED_COLUMNS,
    SIR_A,
    SIR_B,
    frozen_rhs,
    holdout_paths,
    initial_state_from_observed,
    integrate_frozen_model,
    read_observed_raw,
    rollout_from_observed,
    rollout_holdout_file,
)
from pendulum_coordinates import DT, T_END, time_grid  # noqa: E402

DATA = PENDULUM / "data"


def _require_data():
    files = holdout_paths(DATA)
    if len(files) != 8:
        pytest.skip("Pendulum holdout parquet files are missing")
    return files


def test_holdout_ids_are_the_protected_eight():
    assert HOLDOUT_RECORD_IDS == (
        "pendulum_003",
        "pendulum_007",
        "pendulum_011",
        "pendulum_015",
        "pendulum_019",
        "pendulum_023",
        "pendulum_027",
        "pendulum_031",
    )
    files = _require_data()
    assert [p.stem for p in files] == list(HOLDOUT_RECORD_IDS)


def test_frozen_coefficients_are_exactly_the_specified_literals():
    assert SIR_A == -1.82245149
    assert SIR_B == 1.0
    assert AUDIT_A == -1.8225
    assert AUDIT_B == 1.0
    assert SIR_A != AUDIT_A


def test_rhs_uses_predicted_theta_inside_sin():
    theta, omega = 0.37, -0.21
    got = frozen_rhs(None, [theta, omega], SIR_A, SIR_B)
    assert got[0] == pytest.approx(SIR_B * omega)
    assert got[1] == pytest.approx(SIR_A * np.sin(theta))
    # A different "observed" angle must not enter the RHS.
    other = frozen_rhs(None, [theta + 0.5, omega], SIR_A, SIR_B)
    assert other[1] != pytest.approx(SIR_A * np.sin(theta))


def test_integrate_signature_rejects_observed_series():
    params = inspect.signature(integrate_frozen_model).parameters
    assert "theta0" in params and params["theta0"].kind is inspect.Parameter.KEYWORD_ONLY
    forbidden = {
        "sin_theta", "theta_obs", "omega_obs", "energy", "energy_true",
        "observed", "reset", "teacher",
    }
    assert forbidden.isdisjoint(params)


def test_rollout_starts_from_observed_t0_and_matches_grid():
    _require_data()
    times, theta, omega = read_observed_raw(DATA / "pendulum_003.parquet")
    bundle = rollout_from_observed(times, theta, omega)
    np.testing.assert_array_equal(bundle["times"], times)
    np.testing.assert_array_equal(bundle["times"], time_grid(0.0, T_END, DT))
    t0, th0, om0 = initial_state_from_observed(times, theta, omega)
    assert t0 == pytest.approx(0.0)
    assert bundle["theta_sir"][0] == pytest.approx(th0)
    assert bundle["omega_sir"][0] == pytest.approx(om0)
    assert bundle["theta_true"][0] == pytest.approx(theta[0])
    assert bundle["omega_true"][0] == pytest.approx(omega[0])
    assert np.isfinite(bundle["theta_sir"]).all()
    assert np.isfinite(bundle["omega_sir"]).all()
    assert np.isfinite(bundle["theta_exact_audit"]).all()
    assert np.isfinite(bundle["omega_exact_audit"]).all()


def test_primary_and_audit_are_distinct_and_finite():
    _require_data()
    times, theta, omega = read_observed_raw(DATA / "pendulum_007.parquet")
    bundle = rollout_from_observed(times, theta, omega)
    assert not np.allclose(bundle["theta_sir"], bundle["theta_exact_audit"])
    assert not np.allclose(bundle["omega_sir"], bundle["omega_exact_audit"])
    # Same IC, different coefficient: they share t0 exactly.
    assert bundle["theta_sir"][0] == bundle["theta_exact_audit"][0]
    assert bundle["omega_sir"][0] == bundle["omega_exact_audit"][0]


def test_no_teacher_forcing_observed_path_is_not_copied():
    _require_data()
    times, theta, omega = read_observed_raw(DATA / "pendulum_011.parquet")
    bundle = rollout_from_observed(times, theta, omega)
    # After t0 the SIR path is an independent integration, not the observations.
    assert not np.allclose(bundle["theta_sir"][1:], theta[1:])
    assert not np.allclose(bundle["omega_sir"][1:], omega[1:])


def test_read_observed_raw_does_not_consume_energy_or_virtuals():
    _require_data()
    path = DATA / "pendulum_015.parquet"
    df = pd.read_parquet(path)
    assert list(df.columns) == list(OBSERVED_COLUMNS)
    for banned in FORBIDDEN_SELECTABLE | {"sin_theta", "omega_squared", "one_minus_cos_theta"}:
        assert banned not in df.columns
    times, theta, omega = read_observed_raw(path)
    assert times.shape == theta.shape == omega.shape


def test_rhs_sin_arguments_are_the_evolving_state(monkeypatch):
    seen = []
    real_sin = np.sin

    def spy(x):
        seen.append(np.asarray(x, dtype=np.float64).copy())
        return real_sin(x)

    monkeypatch.setattr(np, "sin", spy)
    t_eval = np.linspace(0.0, 0.2, 21)
    times, theta, omega = integrate_frozen_model(
        theta0=0.4, omega0=-0.15, a=SIR_A, b=SIR_B, t_eval=t_eval,
    )
    assert seen, "np.sin was never called"
    # Every RHS evaluation must use the current predicted theta, not a
    # precomputed observational sin_theta series.
    for value in seen:
        assert np.ndim(value) <= 1
        assert np.all(np.abs(np.asarray(value)) <= np.pi)


def test_all_eight_holdouts_roll_out():
    files = _require_data()
    for path in files:
        bundle = rollout_holdout_file(path)
        assert bundle["times"].size == 3001
        assert np.isfinite(bundle["theta_sir"]).all()
