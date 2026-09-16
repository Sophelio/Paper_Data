"""Pendulum provider/project tests. Requires generated data under ../data."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pendulum_coordinates import (  # noqa: E402
    DT,
    FORBIDDEN_SELECTABLE,
    N_REALIZATIONS,
    OMEGA0,
    SELECTABLE_COLUMNS,
    mechanical_energy,
)
from pendulum_data_provider import get_provider as get_sir_provider  # noqa: E402
from data_provider import get_provider as get_dalia_provider  # noqa: E402

DATA = ROOT / "data"
MANIFEST = ROOT / "manifest.csv"


def _require_data():
    files = sorted(DATA.glob("pendulum_*.parquet"))
    if len(files) != N_REALIZATIONS:
        pytest.skip("Pendulum data not generated; run generate_pendulum_data.py")
    return files


def test_sir_provider_imports_and_keys():
    prov = get_sir_provider()
    assert get_sir_provider(None)
    for key in (
        "fetch_data",
        "fetch_identifier_variables",
        "fetch_identifiers_from_url",
        "fetch_dataset_variables",
        "dataset_url",
    ):
        assert key in prov
    assert Path(prov["dataset_url"]).resolve() == DATA.resolve()


def test_identifiers_sorted_and_complete():
    _require_data()
    prov = get_sir_provider()
    ids = prov["fetch_identifiers_from_url"](prov["dataset_url"])
    assert len(ids) == N_REALIZATIONS
    names = [Path(p).name for p in ids]
    assert names == sorted(names)
    assert names[0] == "pendulum_000.parquet"
    assert names[-1] == "pendulum_031.parquet"


def test_dataset_variables_exclude_times_and_energy():
    _require_data()
    prov = get_sir_provider()
    vars_ = prov["fetch_dataset_variables"](prov["dataset_url"])
    assert vars_ == list(SELECTABLE_COLUMNS)
    assert "times" not in vars_
    for banned in FORBIDDEN_SELECTABLE:
        assert banned not in vars_


def test_fetch_data_tuple_shapes_and_dtype():
    files = _require_data()
    prov = get_sir_provider()
    knames = list(SELECTABLE_COLUMNS)
    data, xflags, timing_data, freq, smooth_rate = prov["fetch_data"](str(files[0]), knames)
    assert data.dtype == np.float64
    assert timing_data.dtype == np.float64
    assert data.shape == (len(knames), timing_data.shape[1])
    assert timing_data.shape == (1, data.shape[1])
    assert xflags.shape == (len(knames),)
    assert xflags.dtype == bool
    assert isinstance(freq, float)
    assert freq == pytest.approx(DT)
    assert smooth_rate == 0.2
    assert np.isfinite(data).all()
    assert np.isfinite(timing_data).all()


def test_virtual_coordinates_match_numpy():
    files = _require_data()
    prov = get_sir_provider()
    knames = list(SELECTABLE_COLUMNS)
    data, _, _, _, _ = prov["fetch_data"](str(files[3]), knames)
    by_name = {name: data[i] for i, name in enumerate(knames)}
    theta, omega = by_name["theta"], by_name["omega"]
    np.testing.assert_allclose(by_name["sin_theta"], np.sin(theta), rtol=0, atol=0)
    np.testing.assert_allclose(by_name["cos_theta"], np.cos(theta), rtol=0, atol=0)
    np.testing.assert_allclose(
        by_name["one_minus_cos_theta"], 1.0 - np.cos(theta), rtol=0, atol=0
    )
    np.testing.assert_allclose(by_name["omega_squared"], omega**2, rtol=0, atol=0)


def test_fetch_identifier_variables_matches_fetch_data():
    files = _require_data()
    prov = get_sir_provider()
    ident = str(files[1])
    for name in SELECTABLE_COLUMNS:
        col = prov["fetch_identifier_variables"](ident, name)
        data, _, _, _, _ = prov["fetch_data"](ident, [name])
        np.testing.assert_array_equal(col, data[0])
        assert col.dtype == np.float64


def test_raw_parquet_has_only_primitive_columns():
    files = _require_data()
    df = pd.read_parquet(files[0])
    assert list(df.columns) == ["times", "theta", "omega"]
    for banned in (
        "sin_theta",
        "cos_theta",
        "one_minus_cos_theta",
        "omega_squared",
        "energy",
        "energy_true",
    ):
        assert banned not in df.columns


def test_energy_conserved_within_documented_tolerance():
    files = _require_data()
    rel = []
    abs_ = []
    for path in files:
        df = pd.read_parquet(path)
        e = mechanical_energy(df["theta"].to_numpy(), df["omega"].to_numpy(), OMEGA0)
        abs_.append(float(np.max(np.abs(e - e[0]))))
        rel.append(float(np.max(np.abs((e - e[0]) / e[0]))))
    assert max(rel) < 1e-7
    assert max(abs_) < 1e-8
    assert np.median(abs_) < 1e-8


def test_identical_time_grids():
    files = _require_data()
    times0 = pd.read_parquet(files[0], columns=["times"])["times"].to_numpy()
    assert times0.size == 3001
    assert np.all(np.diff(times0) > 0)
    for path in files[1:]:
        times = pd.read_parquet(path, columns=["times"])["times"].to_numpy()
        np.testing.assert_array_equal(times, times0)


def test_refuses_energy_as_selectable():
    files = _require_data()
    prov = get_sir_provider()
    with pytest.raises(KeyError, match="audit-only"):
        prov["fetch_data"](str(files[0]), ["energy_true"])


def test_dalia_provider_contract():
    _require_data()
    prov = get_dalia_provider(None)
    for key in (
        "fetch_data",
        "fetch_record_ids_for_dataset_id",
        "all_possible_signals",
        "dataset_id",
        "data_folder",
        "fetch_sir_record_ids",
        "fetch_data_sir",
    ):
        assert key in prov
    assert prov["dataset_id"] == "pendulum"
    ids = prov["fetch_sir_record_ids"](prov["data_folder"])
    assert ids == [f"pendulum_{i:03d}" for i in range(N_REALIZATIONS)]
    assert set(SELECTABLE_COLUMNS).issubset(prov["all_possible_signals"])
    assert "times" not in prov["all_possible_signals"]
    payload = prov["fetch_data_sir"](prov["data_folder"], ids[0], list(SELECTABLE_COLUMNS))
    assert payload["times"].shape == payload["theta"].shape
    np.testing.assert_allclose(payload["sin_theta"], np.sin(payload["theta"]))
    record = prov["fetch_data"](
        prov["data_folder"], "pendulum", ids[2], ["theta", "omega_squared"], {}
    )
    assert record["id"] == ids[2]
    assert {s["data_name"] for s in record["signals"]} == {"theta", "omega_squared"}
    omega = pd.read_parquet(DATA / f"{ids[2]}.parquet")["omega"].to_numpy()
    got = next(s["data"] for s in record["signals"] if s["data_name"] == "omega_squared")
    np.testing.assert_allclose(got, omega**2)


def test_manifest_matches_files():
    files = _require_data()
    assert MANIFEST.is_file()
    man = pd.read_csv(MANIFEST)
    assert len(man) == N_REALIZATIONS
    assert set(man["filename"]) == {p.name for p in files}
    assert (man["theta0"] < 0).any() and (man["theta0"] > 0).any()
    assert (man["omega_init"] < 0).any() and (man["omega_init"] > 0).any()
    assert man["normalized_energy_fraction"].min() > 0.08
    assert man["normalized_energy_fraction"].max() < 0.90


def test_dalia_runtime_smoke():
    _require_data()
    worker = Path(r"D:\dalia\worker")
    if not worker.is_dir():
        pytest.skip("Dalia worker checkout not found")
    sys.path.insert(0, str(worker))
    from worker.runtime import ProviderRuntime  # noqa: WPS433

    files = {
        "data_provider.py": (ROOT / "data_provider.py").read_text(encoding="utf-8"),
        "pendulum_coordinates.py": (ROOT / "pendulum_coordinates.py").read_text(encoding="utf-8"),
        "custom_graphs.py": (ROOT / "custom_graphs.py").read_text(encoding="utf-8"),
    }
    rt = ProviderRuntime()
    rt.reload("pendulum", files, str(ROOT / "data"))
    cat = rt.catalog("pendulum")
    assert cat.get("ok") is not False
    signals = cat.get("signals") or cat.get("all_possible_signals") or []
    for name in SELECTABLE_COLUMNS:
        assert name in signals
    fetched = rt.fetch(
        "pendulum",
        "pendulum_000",
        ["theta", "sin_theta", "omega_squared"],
        max_points=5000,
    )
    assert fetched["ok"] is True
    names = [s["data_name"] for s in fetched["signals"]]
    assert names == ["theta", "sin_theta", "omega_squared"]
    assert fetched["signals"][0]["length"] == 3001
    graphers = cat.get("graphers") or list((cat.get("grapher_params") or {}).keys())
    assert "invariant_representation" in graphers
    params = (cat.get("grapher_params") or {}).get("invariant_representation") or {}
    assert params.get("requires_signals") is False
    fig_one = rt.figure(
        "pendulum",
        "pendulum_000",
        "invariant_representation",
        [],
    )
    one = _figure_from_json(fig_one)
    assert one["layout"]["title"]["text"].startswith("Pendulum invariant representation")
    assert one["layout"]["xaxis"]["title"]["text"] == "1 - cos(theta)"
    assert one["layout"]["yaxis"]["title"]["text"] == "omega^2"
    data_one = [t for t in one["data"] if not str(t.get("name", "")).startswith("SIR ref")]
    assert len(data_one) == 1
    assert data_one[0]["name"] == "pendulum_000"
    fig_many = rt.figure(
        "pendulum",
        "pendulum_000",
        "invariant_representation",
        [],
        custom_params={
            "records": "pendulum_000,pendulum_008,pendulum_016,pendulum_024",
            "overlay_reference": "on",
        },
    )
    many = _figure_from_json(fig_many)
    names = [t.get("name") for t in many["data"]]
    data_names = [n for n in names if not str(n).startswith("SIR ref")]
    ref_names = [n for n in names if str(n).startswith("SIR ref")]
    assert data_names == [
        "pendulum_000",
        "pendulum_008",
        "pendulum_016",
        "pendulum_024",
    ]
    assert len(ref_names) == 4
    assert "SIR slope -3.645 (reference)" in many["layout"]["title"]["text"]
    graphers = cat.get("graphers") or list((cat.get("grapher_params") or {}).keys())
    assert "heldout_transfer" in graphers
    hold_params = (cat.get("grapher_params") or {}).get("heldout_transfer") or {}
    assert hold_params.get("requires_signals") is False
    fig_hold_one = rt.figure(
        "pendulum",
        "pendulum_003",
        "heldout_transfer",
        [],
        custom_params={"records": "pendulum_003"},
    )
    hold_one = _figure_from_json(fig_hold_one)
    assert "Held-out transfer" in _layout_title(hold_one)
    names_one = [t.get("name") for t in hold_one["data"]]
    assert "pendulum_003 observed" in names_one
    assert "pendulum_003 transfer" in names_one
    assert "t0 calibration (B_i)" in names_one
    fig_hold_all = rt.figure(
        "pendulum",
        "pendulum_000",
        "heldout_transfer",
        [],
        custom_params={"records": "all"},
    )
    hold_all = _figure_from_json(fig_hold_all)
    names_all = [t.get("name") for t in hold_all["data"]]
    observed = [n for n in names_all if str(n).endswith(" observed")]
    transferred = [n for n in names_all if str(n).endswith(" transfer")]
    assert len(observed) == 8
    assert len(transferred) == 8
    assert "8 holdouts" in _layout_title(hold_all)
    assert all("pendulum_000" not in str(n) for n in names_all)
    assert "heldout_predictive_phase_portrait" in graphers
    fig_pred = rt.figure(
        "pendulum",
        "pendulum_003",
        "heldout_predictive_phase_portrait",
        ["theta", "omega"],
        custom_params={"records": "pendulum_003", "horizon_s": 1.0},
    )
    pred = _figure_from_json(fig_pred)
    assert "PROTECTED HELD-OUT AUTONOMOUS ROLLOUTS" in _layout_title(pred)
    pred_names = [t.get("name") for t in pred["data"]]
    assert "pendulum_003 true" in pred_names
    assert "pendulum_003 SIR" in pred_names


def _figure_from_json(payload: str) -> dict:
    import json

    return json.loads(payload)


def _layout_title(fig: dict) -> str:
    title = (fig.get("layout") or {}).get("title")
    if isinstance(title, dict):
        return str(title.get("text") or "")
    return str(title or "")


def test_invariant_representation_grapher_uses_virtual_coordinates():
    _require_data()
    from custom_graphs import invariant_representation_grapher

    prov = get_dalia_provider(None)
    requested: list[tuple[str, tuple[str, ...]]] = []

    class _Coordinator:
        data_folder = prov["data_folder"]

        def fetch_data_async(self, folder, dataset_id, record_id, signals, params, trim_1=None, trim_2=None):
            requested.append((str(record_id), tuple(signals)))
            return prov["fetch_data"](folder, dataset_id, record_id, signals, params, trim_1, trim_2)

    fig = invariant_representation_grapher(
        {
            "record_id": "pendulum_000",
            "data_coordinator": _Coordinator(),
            "trim_t1": None,
            "trim_t2": None,
        },
        {"records": "pendulum_000, pendulum_008", "overlay_reference": "off"},
    )
    assert [rid for rid, _ in requested] == ["pendulum_000", "pendulum_008"]
    assert all(sigs == ("one_minus_cos_theta", "omega_squared") for _, sigs in requested)
    traces = list(fig.data)
    assert [t.name for t in traces] == ["pendulum_000", "pendulum_008"]
    assert fig.layout.xaxis.title.text == "1 - cos(theta)"
    assert fig.layout.yaxis.title.text == "omega^2"
    intercepts = []
    slope = -3.645
    for trace in traces:
        x = np.asarray(trace.x, dtype=np.float64)
        y = np.asarray(trace.y, dtype=np.float64)
        intercepts.append(float(np.mean(y - slope * x)))
    assert abs(intercepts[0] - intercepts[1]) > 0.05


def test_transfer_from_first_observation_does_not_refit():
    from custom_graphs import transfer_from_first_observation

    x = np.array([0.0, 1.0, 2.0], dtype=np.float64)
    y = np.array([4.0, 0.0, 10.0], dtype=np.float64)
    times = np.array([0.0, 1.0, 2.0], dtype=np.float64)
    slope = -3.645
    intercept, predicted, i0, rmse, max_abs, residuals = (
        transfer_from_first_observation(x, y, times, slope)
    )
    assert i0 == 0
    assert intercept == pytest.approx(4.0)
    np.testing.assert_allclose(predicted, slope * x + 4.0)
    ls_intercept = float(np.mean(y - slope * x))
    assert abs(intercept - ls_intercept) > 1.0
    np.testing.assert_allclose(residuals, y[1:] - predicted[1:])
    assert rmse == pytest.approx(float(np.sqrt(np.mean(residuals**2))))
    assert max_abs == pytest.approx(float(np.max(np.abs(residuals))))


def test_heldout_transfer_grapher_one_and_all_holdouts():
    _require_data()
    from custom_graphs import (
        _HOLDOUT_RECORD_IDS,
        heldout_transfer_grapher,
        transfer_from_first_observation,
    )

    prov = get_dalia_provider(None)
    requested: list[tuple[str, tuple[str, ...]]] = []

    class _Coordinator:
        data_folder = prov["data_folder"]

        def fetch_data_async(self, folder, dataset_id, record_id, signals, params, trim_1=None, trim_2=None):
            requested.append((str(record_id), tuple(signals)))
            return prov["fetch_data"](folder, dataset_id, record_id, signals, params, trim_1, trim_2)

    app = {
        "record_id": "pendulum_000",
        "data_coordinator": _Coordinator(),
        "trim_t1": None,
        "trim_t2": None,
    }
    fig_one = heldout_transfer_grapher(app, {"records": "pendulum_003"})
    names_one = [t.name for t in fig_one.data]
    assert names_one[:2] == ["pendulum_003 observed", "pendulum_003 transfer"]
    assert "t0 calibration (B_i)" in names_one
    assert requested == [("pendulum_003", ("one_minus_cos_theta", "omega_squared"))]
    record = prov["fetch_data"](
        prov["data_folder"], "pendulum", "pendulum_003",
        ["one_minus_cos_theta", "omega_squared"], {},
    )
    signals = {s["data_name"]: s for s in record["signals"]}
    x = np.asarray(signals["one_minus_cos_theta"]["data"], dtype=np.float64)
    y = np.asarray(signals["omega_squared"]["data"], dtype=np.float64)
    times = np.asarray(signals["one_minus_cos_theta"]["times"], dtype=np.float64)
    intercept, _, _, _, _, _ = transfer_from_first_observation(x, y, times, -3.645)
    assert intercept == pytest.approx(float(y[0] - (-3.645) * x[0]))
    transfer = next(t for t in fig_one.data if t.name == "pendulum_003 transfer")
    np.testing.assert_allclose(
        np.asarray(transfer.y, dtype=np.float64),
        -3.645 * np.asarray(transfer.x, dtype=np.float64) + intercept,
    )
    note = " ".join(ann.text for ann in fig_one.layout.annotations)
    assert "HELD-OUT TRANSFER" in note
    assert "pooled RMSE" in note
    assert "max |err|" in note

    requested.clear()
    fig_all = heldout_transfer_grapher(app, {"records": "all"})
    assert [rid for rid, _ in requested] == list(_HOLDOUT_RECORD_IDS)
    names_all = [t.name for t in fig_all.data]
    observed = [n for n in names_all if n.endswith(" observed")]
    transferred = [n for n in names_all if n.endswith(" transfer")]
    assert observed == [f"{rid} observed" for rid in _HOLDOUT_RECORD_IDS]
    assert transferred == [f"{rid} transfer" for rid in _HOLDOUT_RECORD_IDS]
    assert fig_all.layout.title.text.endswith("8 holdouts")
    assert all("pendulum_000" not in n for n in names_all)


def test_heldout_predictive_phase_portrait_one_and_many():
    _require_data()
    from custom_graphs import (
        _HOLDOUT_RECORD_IDS,
        _load_prediction_model,
        heldout_predictive_phase_portrait_grapher,
    )

    pm = _load_prediction_model()
    assert pm.SIR_A == -1.82245149
    assert pm.SIR_B == 1.0
    prov = get_dalia_provider(None)
    requested: list[tuple[str, tuple[str, ...]]] = []

    class _Coordinator:
        data_folder = prov["data_folder"]

        def fetch_data_async(self, folder, dataset_id, record_id, signals, params, trim_1=None, trim_2=None):
            requested.append((str(record_id), tuple(signals)))
            return prov["fetch_data"](folder, dataset_id, record_id, signals, params, trim_1, trim_2)

    app = {
        "record_id": "pendulum_000",
        "data_coordinator": _Coordinator(),
        "trim_t1": None,
        "trim_t2": None,
    }
    fig_one = heldout_predictive_phase_portrait_grapher(
        app, {"records": "pendulum_003", "horizon_s": 2.0, "overlay_exact_audit": "off"},
    )
    names_one = [t.name for t in fig_one.data]
    assert names_one == ["pendulum_003 true", "pendulum_003 SIR"]
    assert requested == [("pendulum_003", ("theta", "omega"))]
    assert "PROTECTED HELD-OUT AUTONOMOUS ROLLOUTS" in fig_one.layout.title.text
    note = " ".join(ann.text for ann in fig_one.layout.annotations)
    assert "sin(theta_hat)" in note
    assert "pooled RMSE theta" in note

    requested.clear()
    fig_all = heldout_predictive_phase_portrait_grapher(
        app, {"records": "all", "horizon_s": 1.0, "overlay_exact_audit": "on"},
    )
    assert [rid for rid, _ in requested] == list(_HOLDOUT_RECORD_IDS)
    names_all = [t.name for t in fig_all.data]
    assert [n for n in names_all if n.endswith(" true")] == [
        f"{rid} true" for rid in _HOLDOUT_RECORD_IDS
    ]
    assert [n for n in names_all if n.endswith(" SIR")] == [
        f"{rid} SIR" for rid in _HOLDOUT_RECORD_IDS
    ]
    assert len([n for n in names_all if n.endswith(" exact audit")]) == 8
    assert all("pendulum_000" not in n for n in names_all)


def test_task_conditioned_pendulum_grapher_loads():
    _require_data()
    from custom_graphs import build_custom_graphers, task_conditioned_pendulum_grapher

    graphers = build_custom_graphers(["theta", "omega"])
    assert "task_conditioned_pendulum" in graphers
    assert graphers["task_conditioned_pendulum"]["requires_signals"] is False
    assert graphers["task_conditioned_pendulum"]["display_name"] == (
        "Task-conditioned pendulum summary"
    )
    prov = get_dalia_provider(None)

    class _Coordinator:
        data_folder = prov["data_folder"]

        def fetch_data_async(self, *args, **kwargs):
            raise AssertionError("task-conditioned panel must use frozen files, not live fetch")

    app = {
        "record_id": "pendulum_000",
        "data_coordinator": _Coordinator(),
        "trim_t1": None,
        "trim_t2": None,
    }
    fig = task_conditioned_pendulum_grapher(app, {})
    assert "different task contracts" in str(fig.layout.title.text)
    names = [t.name for t in fig.data]
    assert "true" in names
    assert "SIR rollout" in names
    assert "RMSE θ" in names
    assert "RMSE ω" in names
    note = " ".join(ann.text for ann in (fig.layout.annotations or []))
    assert "1.82245149" in note
    assert "3.645" in note


def test_task_conditioned_panel_script_frozen_sources():
    sys.path.insert(0, str(ROOT / "Plotter"))
    import panel_data as pdata

    assert pdata.SIR_SLOPE == -3.645
    assert pdata.SIR_A == -1.82245149
    assert pdata.SIR_B == 1.0
    traces = pdata.load_compression()
    assert [t["record_id"] for t in traces] == list(pdata.DEFAULT_COMPRESSION_IDS)
    pooled = pdata.load_pooled_rmse()
    assert pooled["a"] == -1.82245149
    assert pooled["sir"]["theta"]["horizon_s"][-1] == 30.0
    bundle = pdata.load_prediction_bundle("pendulum_015")
    assert bundle["theta_sir"].iloc[0] == bundle["theta_true"].iloc[0]
    assert not np.allclose(bundle["theta_sir"].iloc[1:], bundle["theta_true"].iloc[1:])
