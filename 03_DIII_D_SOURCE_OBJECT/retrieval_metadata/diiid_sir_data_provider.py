"""DIII-D ELM (resampled_data_v6) data provider — full 95-signal manifest.

This file is the **hard reference** for what the DIIID_SIR_Paper Dalia project
loads. It is kept byte-for-byte in step with that project's `data_provider.py`
(project id ``36a4813a-23b1-4c9f-abc3-592f98b4abe2``) apart from the trailing
``get_provider()`` wrapper, which only exists inside Dalia. If you change the
signal manifest here, change it there too, and vice versa.

Archive
-------
``D:\\SIR_paper\\DIIID_example\\data\\resampled_data_v6``

62 discharges, each an ``.npz`` holding ``<signal>_data`` / ``<signal>_times``
pairs. **All 95 signals are present in all 62 discharges** (verified: the signal
set is identical across every archive). Every time axis is in **milliseconds**.

What changed, and why
---------------------
The previous provider exposed **12** signals: the eight the manuscript used,
plus four filterscope channels for the ELM autolabelers. SIR itself was
hard-restricted to the eight by an allow-list in ``_common_grid_fetch``.

That restriction was historical convention, not a documented scientific
decision — the S7.1 observational-object census established that the other 87
quantities are equally present and equally available. This provider therefore
exposes **all 95** and lets the task contract, not the loader, decide what is
admissible.

``PAPER_EIGHT`` is retained in its original canonical order because that order
carries relational-term direction in the manuscript.

Grid caveat (read before comparing against canonical results)
-------------------------------------------------------------
``fetch_data_sir`` puts the requested signals on the intersection of their time
ranges with a fixed ``TARGET_N = 1000`` points, so **Δt depends on which signals
you ask for**:

===================  ==================  ===================
Request              common window (ms)  Δt (ms), N=1000
===================  ==================  ===================
``PAPER_EIGHT``      4080 / 4960 / 6020  4.08 / 4.97 / 6.03
``ALL_SIGNALS``      3750 / 4590 / 5360  3.75 / 4.60 / 5.37
===================  ==================  ===================

(min / median / max over the 62 discharges.)

Asking for all 95 retains ~90% of the paper-eight window; no discharge loses
more than half. But a SIR run over all 95 is **not** on the same grid as the
canonical 8-signal q_desc run, so results are not directly comparable
point-for-point. Pass ``variables=PAPER_EIGHT`` explicitly to reproduce the
canonical grid.

There is no fixed 20 ms grid anywhere in this path. 20 ms is the *native*
cadence of the equilibrium group, and the grid the full sir-web provider would
produce because it grids to the coarsest requested signal. See
``S7/01_observational_object/reconciliation/TEMPORAL_GRID_RECONCILIATION_REPORT.md``.

Units
-----
The units in ``SIGNAL_MANIFEST`` are **not** recorded anywhere in the project.
No archive, sidecar, provider, or ledger states a unit; the one function whose
job it is returns the empty string by design. They were recovered from DIII-D
pointname convention and then tested against observed magnitudes. Treat every
one as ``STRONGLY_INFERRED`` unless marked otherwise, and never cite one as
project-verified. Full derivation:
``S7/01_observational_object/reconciliation/units_recovery_report.md``.

Three consequences you will hit if you form ratios or sums across groups:

* ``density`` is cm^-3 but ``prmtan_neped`` is m^-3     (10^6 apart)
* ``ece*`` is keV but ``cerqtit*`` / ``prmtan_teped`` are eV  (10^3 apart)
* ``pinj`` is kW but ``pinj_*`` are W                    (10^3 apart)

``pcdiamag3`` — one of the paper eight — has **no established unit**. The
stored-energy-in-joules reading is refuted by its own magnitude by four to five
orders of magnitude, and no rescaled alternative is asserted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import numpy as np

DEFAULT_DATA_FOLDER = Path(r"D:\SIR_paper\DIIID_example\data\resampled_data_v6")
_NPZ_SUFFIX = "_resampled.npz"

#: Points on the common analysis grid. Fixed, so Δt varies with the window.
TARGET_N = 1000

# ---------------------------------------------------------------------------
# The manifest. This is the authoritative list of what loads.
#
#   (signal, group, unit, unit_evidence_class, native_dt_ms)
#
# Verified against every one of the 62 archives: this set is exactly the set of
# `<signal>_data` keys, in all 62, with no discharge differing.
# ---------------------------------------------------------------------------
SIGNAL_MANIFEST: tuple[tuple[str, str, str, str, float], ...] = (
    # -- magnetics (5)
    ('bt', 'magnetics', 'T', 'STRONGLY_INFERRED', 1),
    ('ip', 'magnetics', 'A', 'STRONGLY_INFERRED', 1),
    ('pcbcoil', 'magnetics', 'A', 'STRONGLY_INFERRED', 1),
    ('pcdiamag3', 'magnetics', 'UNRESOLVED', 'UNRESOLVED', 1),
    ('vsurf', 'magnetics', 'V', 'STRONGLY_INFERRED', 20),
    # -- equilibrium_shape (15)
    ('aminor', 'equilibrium_shape', 'm', 'STRONGLY_INFERRED', 20),
    ('area', 'equilibrium_shape', 'm^2', 'STRONGLY_INFERRED', 20),
    ('betan', 'equilibrium_shape', '%*m*T/MA', 'STRONGLY_INFERRED', 20),
    ('drsep', 'equilibrium_shape', 'm', 'AUTHORITATIVE_EXTERNAL', 20),
    ('kappa', 'equilibrium_shape', '1', 'STRONGLY_INFERRED', 20),
    ('li', 'equilibrium_shape', '1', 'STRONGLY_INFERRED', 20),
    ('q95', 'equilibrium_shape', '1', 'STRONGLY_INFERRED', 20),
    ('rmaxis', 'equilibrium_shape', 'm', 'AUTHORITATIVE_EXTERNAL', 20),
    ('rsurf', 'equilibrium_shape', 'm', 'AUTHORITATIVE_EXTERNAL', 20),
    ('tribot', 'equilibrium_shape', '1', 'AUTHORITATIVE_EXTERNAL', 20),
    ('tritop', 'equilibrium_shape', '1', 'AUTHORITATIVE_EXTERNAL', 20),
    ('volume', 'equilibrium_shape', 'm^3', 'STRONGLY_INFERRED', 20),
    ('zcur', 'equilibrium_shape', 'm', 'AUTHORITATIVE_EXTERNAL', 20),
    ('zmaxis', 'equilibrium_shape', 'm', 'AUTHORITATIVE_EXTERNAL', 20),
    ('zsurf', 'equilibrium_shape', 'm', 'AUTHORITATIVE_EXTERNAL', 20),
    # -- density (3)
    ('density', 'density', 'cm^-3', 'STRONGLY_INFERRED', 1),
    ('prmtan_neped', 'density', 'm^-3', 'STRONGLY_INFERRED', 10),
    ('prmtan_teped', 'density', 'eV', 'STRONGLY_INFERRED', 10),
    # -- filterscope_dalpha (4)
    ('fs04', 'filterscope_dalpha', 'arbitrary (photodiode)', 'STRONGLY_INFERRED', 0.02),
    ('fs03da', 'filterscope_dalpha', 'arbitrary (photodiode)', 'STRONGLY_INFERRED', 0.02),
    ('fs04da', 'filterscope_dalpha', 'arbitrary (photodiode)', 'STRONGLY_INFERRED', 0.02),
    ('fs05da', 'filterscope_dalpha', 'arbitrary (photodiode)', 'STRONGLY_INFERRED', 0.02),
    # -- gas_injection (4)
    ('gasa', 'gas_injection', 'Torr*L/s', 'STRONGLY_INFERRED', 2),
    ('gasb', 'gas_injection', 'Torr*L/s', 'STRONGLY_INFERRED', 2),
    ('gasc', 'gas_injection', 'Torr*L/s', 'STRONGLY_INFERRED', 2),
    ('gasd', 'gas_injection', 'Torr*L/s', 'STRONGLY_INFERRED', 2),
    # -- neutral_beams (10)
    ('pinj', 'neutral_beams', 'kW', 'STRONGLY_INFERRED', 0.1),
    ('pinj_15l', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_15r', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_21l', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_21r', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_30l', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_30r', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_33l', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('pinj_33r', 'neutral_beams', 'W', 'STRONGLY_INFERRED', 0.1),
    ('tinj', 'neutral_beams', 'N*m', 'STRONGLY_INFERRED', 0.1),
    # -- ece_te_profile (40)
    ('ece1', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece2', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece3', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece4', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece5', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece6', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece7', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece8', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece9', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece10', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece11', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece12', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece13', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece14', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece15', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece16', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece17', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece18', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece19', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece20', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece21', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece22', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece23', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece24', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece25', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece26', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece27', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece28', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece29', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece30', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece31', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece32', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece33', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece34', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece35', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece36', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece37', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece38', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece39', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    ('ece40', 'ece_te_profile', 'keV', 'STRONGLY_INFERRED', 0.2),
    # -- cer_rotation_ti (14)
    ('cerqrott3', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqrott6', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqrott8', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqrott10', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqrott11', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqrott12', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqrott13', 'cer_rotation_ti', 'km/s', 'STRONGLY_INFERRED', 10),
    ('cerqtit3', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
    ('cerqtit6', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
    ('cerqtit8', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
    ('cerqtit10', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
    ('cerqtit11', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
    ('cerqtit12', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
    ('cerqtit13', 'cer_rotation_ti', 'eV', 'STRONGLY_INFERRED', 10),
)

#: All 95, in manifest order (grouped, then within-group natural order).
ALL_SIGNALS: tuple[str, ...] = tuple(row[0] for row in SIGNAL_MANIFEST)
_ALL_SET = frozenset(ALL_SIGNALS)

SIGNAL_GROUP: dict[str, str] = {r[0]: r[1] for r in SIGNAL_MANIFEST}
SIGNAL_UNIT: dict[str, str] = {r[0]: r[2] for r in SIGNAL_MANIFEST}
SIGNAL_UNIT_EVIDENCE: dict[str, str] = {r[0]: r[3] for r in SIGNAL_MANIFEST}
SIGNAL_NATIVE_DT_MS: dict[str, float] = {r[0]: r[4] for r in SIGNAL_MANIFEST}

GROUPS: dict[str, tuple[str, ...]] = {
    g: tuple(s for s, gg, *_ in SIGNAL_MANIFEST if gg == g)
    for g in dict.fromkeys(r[1] for r in SIGNAL_MANIFEST)
}

#: The manuscript's canonical eight, in the order relational-term direction
#: depends on. Do not reorder.
PAPER_EIGHT: tuple[str, ...] = (
    "pcdiamag3", "pinj", "density", "ip", "q95", "li", "kappa", "betan",
)

#: Native-grid channels the ELM autolabelers run on.
FILTERSCOPE_SIGNALS: tuple[str, ...] = GROUPS["filterscope_dalpha"]

#: What `fetch_data_sir` uses when no variables are named. Previously the
#: paper eight; now the whole object, so admissibility is a contract decision
#: rather than a loader default.
SIR_DEFAULT_SIGNALS: tuple[str, ...] = ALL_SIGNALS

assert len(ALL_SIGNALS) == 95, len(ALL_SIGNALS)
assert len(set(ALL_SIGNALS)) == 95
assert set(PAPER_EIGHT) <= _ALL_SET


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _shot_npz_path(folder: Path, record_id: str) -> Path:
    return Path(folder) / f"shot_{record_id}{_NPZ_SUFFIX}"


def _record_ids(folder: Path) -> list[str]:
    ids = []
    for p in Path(folder).glob(f"shot_*{_NPZ_SUFFIX}"):
        rid = p.name[len("shot_"): -len(_NPZ_SUFFIX)]
        if rid:
            ids.append(rid)
    ids.sort(key=lambda x: int(x) if x.isdigit() else x)
    return ids


def _load_signal(archive, name: str):
    """Return (times, values) cleaned: finite, sorted, strictly increasing."""
    data_key, times_key = f"{name}_data", f"{name}_times"
    if data_key not in archive:
        raise KeyError(f"signal {name!r} not found in archive")

    values = np.asarray(archive[data_key], dtype=np.float64)
    if times_key in archive:
        times = np.asarray(archive[times_key], dtype=np.float64)
    else:
        times = np.arange(len(values), dtype=np.float64)

    n = min(len(times), len(values))
    times, values = times[:n], values[:n]

    finite = np.isfinite(times) & np.isfinite(values)
    times, values = times[finite], values[finite]

    order = np.argsort(times, kind="stable")
    times, values = times[order], values[order]

    keep = np.concatenate(([True], np.diff(times) > 0))
    return times[keep], values[keep]


def _block_average_to_grid(times, values, grid):
    grid = np.asarray(grid, dtype=np.float64)
    times = np.asarray(times, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    n = grid.size
    if n == 0:
        return np.array([], dtype=np.float64)
    if n == 1:
        return np.array([float(np.mean(values))], dtype=np.float64)

    dt = float(grid[1] - grid[0])
    edges = np.empty(n + 1, dtype=np.float64)
    edges[0] = grid[0] - 0.5 * dt
    edges[1:-1] = 0.5 * (grid[:-1] + grid[1:])
    edges[-1] = grid[-1] + 0.5 * dt

    bin_idx = np.clip(np.digitize(times, edges) - 1, -1, n - 1)
    valid = (bin_idx >= 0) & (times >= edges[0]) & (times <= edges[-1])
    bin_idx, vals = bin_idx[valid], values[valid]

    sums = np.bincount(bin_idx, weights=vals, minlength=n).astype(np.float64)
    counts = np.bincount(bin_idx, minlength=n).astype(np.float64)

    out = np.empty(n, dtype=np.float64)
    nonempty = counts > 0
    out[nonempty] = sums[nonempty] / counts[nonempty]
    if not bool(nonempty.all()):
        out[~nonempty] = np.interp(grid[~nonempty], times, values)
    return out


def _resample_to_grid(times, values, grid):
    """Block-average signals denser than the grid; interpolate sparser ones.

    Note the asymmetry: the 15 equilibrium quantities are always in the second
    branch. At 20 ms native onto a ~4.6 ms grid they are ~4x oversampled, so a
    derivative taken over them is governed by this interpolation rather than by
    the equilibrium reconstruction.
    """
    t0, t1 = float(grid[0]), float(grid[-1])
    in_window = (times >= t0) & (times <= t1)
    if int(np.count_nonzero(in_window)) > grid.size:
        return _block_average_to_grid(times, values, grid)
    return np.interp(grid, times, values).astype(np.float64, copy=False)


def _common_grid_fetch(npz_path: Path, knames: list[str]) -> dict[str, Any]:
    """Place `knames` on one uniform grid over their shared time window."""
    bad = [k for k in knames if k not in _ALL_SET]
    if bad:
        raise KeyError(
            f"signals not present in this dataset: {bad}. "
            f"{len(ALL_SIGNALS)} signals are available; see SIGNAL_MANIFEST."
        )

    with np.load(npz_path, allow_pickle=False) as archive:
        series = {name: _load_signal(archive, name) for name in knames}

    for name, (times, _) in series.items():
        if len(times) < 2:
            raise ValueError(
                f"signal {name!r} in {npz_path} has fewer than 2 usable points"
            )

    t0 = max(float(t[0]) for t, _ in series.values())
    t1 = min(float(t[-1]) for t, _ in series.values())
    if not np.isfinite(t0) or not np.isfinite(t1) or t1 <= t0:
        raise ValueError(
            f"requested signals share an empty time window in {npz_path}: "
            f"[{t0}, {t1}] ms"
        )

    grid = np.linspace(t0, t1, TARGET_N, dtype=np.float64)
    payload: dict[str, Any] = {"times": grid}
    for name in knames:
        payload[name] = _resample_to_grid(*series[name], grid)
    return payload


# ---------------------------------------------------------------------------
# Public API — mirrors the Dalia provider contract
# ---------------------------------------------------------------------------

def fetch_record_ids(folder: Path = DEFAULT_DATA_FOLDER) -> list[str]:
    """The 62 discharge identifiers, ascending."""
    return _record_ids(folder)


def fetch_native(
    record_id: str,
    signals: Optional[list[str]] = None,
    folder: Path = DEFAULT_DATA_FOLDER,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Load signals on their **own native time axes** (no common grid).

    Use this when native cadence matters — ELM detection on the 0.02 ms
    filterscopes, say — and you do not want the equilibrium group's 20 ms
    cadence dictating a common grid.
    """
    names = list(ALL_SIGNALS) if signals is None else list(signals)
    path = _shot_npz_path(folder, str(record_id))
    with np.load(path, allow_pickle=False) as archive:
        return {n: _load_signal(archive, n) for n in names}


def fetch_common_grid(
    record_id: str,
    signals: Optional[list[str]] = None,
    folder: Path = DEFAULT_DATA_FOLDER,
) -> dict[str, Any]:
    """Load signals on one 1000-point grid over their shared window.

    Defaults to all 95. Pass ``signals=PAPER_EIGHT`` for the canonical grid.
    Returns ``{"times": grid, <signal>: values, ...}``.
    """
    names = list(SIR_DEFAULT_SIGNALS) if signals is None else list(signals)
    return _common_grid_fetch(_shot_npz_path(folder, str(record_id)), names)


def describe(signal: str) -> dict[str, Any]:
    """Manifest entry for one signal."""
    if signal not in _ALL_SET:
        raise KeyError(f"{signal!r} is not one of the {len(ALL_SIGNALS)} signals")
    return {
        "signal": signal,
        "group": SIGNAL_GROUP[signal],
        "unit": SIGNAL_UNIT[signal],
        "unit_evidence": SIGNAL_UNIT_EVIDENCE[signal],
        "native_dt_ms": SIGNAL_NATIVE_DT_MS[signal],
        "in_paper_eight": signal in PAPER_EIGHT,
    }


def verify_against_archive(folder: Path = DEFAULT_DATA_FOLDER) -> dict[str, Any]:
    """Check the manifest still matches every archive on disk.

    Run this after the dataset is regenerated or extended.
    """
    ids = _record_ids(folder)
    mismatches = []
    for rid in ids:
        with np.load(_shot_npz_path(folder, rid), allow_pickle=False) as a:
            present = {k[:-5] for k in a.files if k.endswith("_data")}
        if present != _ALL_SET:
            mismatches.append({
                "record_id": rid,
                "missing": sorted(_ALL_SET - present),
                "extra": sorted(present - _ALL_SET),
            })
    return {
        "n_records": len(ids),
        "n_manifest_signals": len(ALL_SIGNALS),
        "all_records_match_manifest": not mismatches,
        "mismatches": mismatches,
    }


if __name__ == "__main__":
    report = verify_against_archive()
    print(f"discharges           : {report['n_records']}")
    print(f"manifest signals     : {report['n_manifest_signals']}")
    print(f"all archives match   : {report['all_records_match_manifest']}")
    for group, members in GROUPS.items():
        print(f"  {group:<20s} {len(members):>3d}")
    if report["mismatches"]:
        print("\nMISMATCHES:")
        for m in report["mismatches"]:
            print(f"  {m['record_id']}: -{m['missing']} +{m['extra']}")
