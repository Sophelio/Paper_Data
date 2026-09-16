"""SIR General-tab standardizations as dalia transform blocks.

Ported from sir-web's General settings (normalization_mode family) so they
appear under "+ Add transform…" in graphs, Data Maker, and SIR prep:

  • Per-Realization Z-score
  • Per-Channel Z-score
  • Conditioning-aware (zero-preserving pooled-RMS scale + optional
    regularized ratio against a denominator signal)
  • Level-rate relational
  • Reference-shifted regularized phase
  • Sensitivity-centered reference-shifted phase
  • Tangent-direction

Per-channel / CA cohort stats are fit across every shot under the project's
data folder (same 62-shot ELM set). Relational modes take a denominator
signal parameter — leave it blank on Conditioning-aware to apply the
level-only scale form.

-----------------------------------------------------------------------
AUDIT 2026-08-25 — reference-shifted family corrected
-----------------------------------------------------------------------
The reference-shifted transforms were repaired to match the canonical
Archaieus implementations (Archaieus/sir/utils/conditioning_aware.py and
sir/conditioning_consumer.py). Four defects were fixed:

  1. the denominator clearance s_0 was computed from the RAW rate and then
     added to a NORMALIZED rate — a units error. It is now fitted on the
     normalized denominator u_d = rate/scale (`_fit_clearance_normalized`).
  2. the numerator was not reference-shifted. Archaieus uses
     C_RS = (u_n + s_eff) * g, not u_n * g.
  3. `sensitivity_centered_phase` subtracted the series mean. Sensitivity
     centering is C_RS - g_bar*u_n with g_bar = mean_fit[g], NOT
     C_RS - mean(C_RS).
  4. the centering constant was re-estimated per record. g_bar is now
     fitted once on the whole cohort and cached (`_gbar_cache`), so
     held-out records reuse the training constant.

`conditioning_aware`'s ratio form also had a train/apply leak: it applied a
per-record z-score. It now uses a cohort-fitted, frozen z-score.

The human-readable reference implementation with full derivations lives at
D:\\SIR_paper\\DIIID_example\\transforms.py; these runtime functions are kept
numerically identical to it and to Archaieus.

Manuscript convention: D_g f = (df/dt)/(dg/dt) — the subscript is the
reference (denominator).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

_NPZ_SUFFIX = "_resampled.npz"
ALLOWED_SIGNALS = (
    "pcdiamag3",
    "pinj",
    "density",
    "ip",
    "q95",
    "li",
    "kappa",
    "betan",
)

_channel_z_cache: dict[tuple[str, str], tuple[float, float]] = {}
_scale_cache: dict[tuple[str, str, str], float] = {}
# Cohort-fitted reference-shift quantities, keyed by (folder, signal, method,
# kind). Frozen after the first fit so held-out records reuse them.
_clearance_cache: dict[tuple[str, str, str, str], float] = {}
_gbar_cache: dict[tuple[str, str, str, str, str], float] = {}
_ratio_z_cache: dict[tuple[str, str, str, str, str], tuple[float, float]] = {}


def _p(default, display_name, **extra):
    spec = {"default": default, "display_name": display_name}
    spec.update(extra)
    return spec


def _den_options():
    opts = {"(none — scale only)": ""}
    for name in ALLOWED_SIGNALS:
        opts[name] = name
    return opts


def _shot_ids(folder: Path) -> list[str]:
    ids = []
    for p in Path(folder).glob(f"shot_*{_NPZ_SUFFIX}"):
        rid = p.name[len("shot_") : -len(_NPZ_SUFFIX)]
        if rid:
            ids.append(rid)
    ids.sort(key=lambda x: int(x) if x.isdigit() else x)
    return ids


def _load_signal(folder: Path, record_id: str, name: str):
    path = Path(folder) / f"shot_{record_id}{_NPZ_SUFFIX}"
    with np.load(path, allow_pickle=False) as archive:
        data_key = f"{name}_data"
        times_key = f"{name}_times"
        if data_key not in archive:
            raise KeyError(name)
        values = np.asarray(archive[data_key], dtype=np.float64)
        if times_key in archive:
            times = np.asarray(archive[times_key], dtype=np.float64)
        else:
            times = np.arange(len(values), dtype=np.float64)
    n = min(len(times), len(values))
    times, values = times[:n], values[:n]
    finite = np.isfinite(times) & np.isfinite(values)
    times, values = times[finite], values[finite]
    if times.size < 2:
        return times, values
    order = np.argsort(times, kind="stable")
    times, values = times[order], values[order]
    keep = np.concatenate(([True], np.diff(times) > 0))
    return times[keep], values[keep]


def _finite(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    return a[np.isfinite(a)]


def _dt_derivative(times, values):
    t = np.asarray(times, dtype=np.float64).reshape(-1)
    y = np.asarray(values, dtype=np.float64).reshape(-1)
    if t.size < 2:
        return np.zeros_like(y)
    dy = np.empty_like(y)
    dy[0] = (y[1] - y[0]) / (t[1] - t[0])
    dy[-1] = (y[-1] - y[-2]) / (t[-1] - t[-2])
    dt = t[2:] - t[:-2]
    dy[1:-1] = np.where(dt != 0, (y[2:] - y[:-2]) / dt, 0.0)
    return dy


def _regularized_ratio(u, v, rho: float) -> np.ndarray:
    """Unshifted C = u*v/(v^2+rho^2). Archaieus: regularized_ratio."""
    u = np.asarray(u, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    rho = float(rho)
    return u * v / (v * v + rho * rho)


def _denominator_gain(u_d, rho: float, s_eff: float) -> np.ndarray:
    """g(w) = w/(w^2+rho^2), w = u_d + s_eff, u_d already normalized.

    Archaieus: conditioning_aware.regularized_denominator_gain.
    """
    w = np.asarray(u_d, dtype=np.float64) + float(s_eff)
    return w / (w * w + float(rho) ** 2)


def _clearance_shifted_ratio(u_n, u_d, rho: float, s_eff: float) -> np.ndarray:
    """C_RS = (u_n + s_eff) * g(w). BOTH operands are shifted.

    Archaieus: conditioning_aware.clearance_shifted_regularized_ratio.
    """
    u_n = np.asarray(u_n, dtype=np.float64)
    return (u_n + float(s_eff)) * _denominator_gain(u_d, rho, s_eff)


def _pooled_rms(samples: list[np.ndarray], min_scale: float = 1e-15) -> float:
    chunks = [_finite(s) for s in samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        return min_scale
    pooled = np.concatenate(chunks)
    rms = float(np.sqrt(np.mean(pooled * pooled)))
    return max(rms, min_scale)


def _robust_zero_mad(samples: list[np.ndarray], min_scale: float = 1e-15) -> float:
    chunks = [_finite(s) for s in samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        return min_scale
    pooled = np.concatenate(chunks)
    mad = float(np.median(np.abs(pooled))) * 1.4826
    if not np.isfinite(mad) or mad < min_scale:
        # Archaieus falls back to pooled RMS when the MAD degenerates.
        return _pooled_rms(samples, min_scale)
    return mad


def _fit_channel_z(folder: Path, signal: str) -> tuple[float, float]:
    key = (str(folder), signal)
    if key in _channel_z_cache:
        return _channel_z_cache[key]
    chunks = []
    for rid in _shot_ids(folder):
        try:
            _, values = _load_signal(folder, rid, signal)
        except (KeyError, OSError, ValueError):
            continue
        f = _finite(values)
        if f.size:
            chunks.append(f)
    if not chunks:
        _channel_z_cache[key] = (0.0, 1.0)
        return 0.0, 1.0
    pooled = np.concatenate(chunks)
    mean = float(np.mean(pooled))
    std = float(np.std(pooled))  # ddof=0
    if std == 0 or not np.isfinite(std):
        std = 1.0
    _channel_z_cache[key] = (mean, std)
    return mean, std


def _fit_operand_scale(folder: Path, signal: str, method: str) -> float:
    method = (method or "pooled_rms").strip().lower()
    key = (str(folder), signal, method)
    if key in _scale_cache:
        return _scale_cache[key]
    samples = []
    for rid in _shot_ids(folder):
        try:
            _, values = _load_signal(folder, rid, signal)
        except (KeyError, OSError, ValueError):
            continue
        samples.append(values)
    scale = (
        _robust_zero_mad(samples)
        if method == "robust_zero_mad"
        else _pooled_rms(samples)
    )
    _scale_cache[key] = scale
    return scale


def _fit_rate_scale(folder: Path, signal: str, method: str) -> float:
    method = (method or "pooled_rms").strip().lower()
    key = (str(folder), f"d1_{signal}", method)
    if key in _scale_cache:
        return _scale_cache[key]
    samples = []
    for rid in _shot_ids(folder):
        try:
            tt, vv = _load_signal(folder, rid, signal)
        except (KeyError, OSError, ValueError):
            continue
        samples.append(_dt_derivative(tt, vv))
    scale = (
        _robust_zero_mad(samples)
        if method == "robust_zero_mad"
        else _pooled_rms(samples)
    )
    _scale_cache[key] = scale
    return scale


def _cohort_operand(folder: Path, signal: str, is_rate: bool):
    """Yield the per-shot cohort operand arrays (rate or level)."""
    for rid in _shot_ids(folder):
        try:
            times, values = _load_signal(folder, rid, signal)
        except (KeyError, OSError, ValueError):
            continue
        yield _dt_derivative(times, values) if is_rate else values


def _fit_clearance_normalized(
    folder: Path, signal: str, is_rate: bool, scale: float, method: str
) -> float:
    """s_0 = max(0, -min_fit(u_d)) on the NORMALIZED denominator.

    The pre-audit implementation took the min of the RAW operand, producing a
    shift in physical units that was then added to a dimensionless quantity.
    Archaieus: conditioning_aware.fit_denominator_clearance, fed the
    operand-scaled samples (conditioning_consumer._clearance_for).
    """
    key = (str(folder), signal, method, "rate" if is_rate else "level")
    if key in _clearance_cache:
        return _clearance_cache[key]
    mins = []
    for series in _cohort_operand(folder, signal, is_rate):
        f = _finite(np.asarray(series, dtype=np.float64) / scale)
        if f.size:
            mins.append(float(np.min(f)))
    s_0 = 0.0 if not mins else max(0.0, -min(mins))
    _clearance_cache[key] = s_0
    return s_0


def _fit_mean_gain(
    folder: Path,
    signal: str,
    is_rate: bool,
    scale: float,
    method: str,
    rho: float,
    s_eff: float,
) -> float:
    """g_bar = mean_fit[g(w)] pooled over the cohort, then FROZEN.

    Archaieus: conditioning_aware.fit_training_mean_gain via
    conditioning_consumer._mean_gain_for.
    """
    key = (
        str(folder),
        signal,
        method,
        "rate" if is_rate else "level",
        f"{float(rho):.17g}|{float(s_eff):.17g}",
    )
    if key in _gbar_cache:
        return _gbar_cache[key]
    chunks = []
    for series in _cohort_operand(folder, signal, is_rate):
        u_d = np.asarray(series, dtype=np.float64) / scale
        g = _finite(_denominator_gain(u_d, rho, s_eff))
        if g.size:
            chunks.append(g)
    g_bar = float(np.mean(np.concatenate(chunks))) if chunks else 0.0
    if not np.isfinite(g_bar):
        g_bar = 0.0
    _gbar_cache[key] = g_bar
    return g_bar


def _align_to(times_ref, times_src, values_src):
    t0 = np.asarray(times_ref, dtype=np.float64)
    t1 = np.asarray(times_src, dtype=np.float64)
    v1 = np.asarray(values_src, dtype=np.float64)
    if t1.size < 2:
        return np.full_like(t0, np.nan, dtype=np.float64)
    return np.interp(t0, t1, v1, left=np.nan, right=np.nan)


def _zscore_local(values):
    values = np.asarray(values, dtype=float)
    mean = np.nanmean(values) if values.size else np.nan
    std = np.nanstd(values) if values.size else np.nan
    if std == 0 or np.isnan(std):
        return np.zeros_like(values)
    return (values - mean) / std


def build_transforms(data_folder: Optional[Path] = None) -> dict:
    folder = Path(data_folder) if data_folder is not None else None

    def _root(_context) -> Path:
        if folder is None:
            raise ValueError("No data folder bound to standardization transforms")
        return Path(folder)

    def per_realization_zscore(times, values, params, context):
        """Record-local by design — see the reference implementation."""
        return times, _zscore_local(values)

    def per_channel_zscore(times, values, params, context):
        name = str(context.get("signal_name") or "")
        if not name:
            raise ValueError("Per-channel z-score needs a signal name")
        mean, std = _fit_channel_z(_root(context), name)
        values = np.asarray(values, dtype=float)
        return times, (values - mean) / std

    def _fit_ratio_z(root, name, denom, method, rho):
        """Cohort-fitted, frozen z-stats for the conditioning-aware ratio.

        Replaces the pre-audit per-record z-score, which mapped training and
        held-out records through different affine functions.
        Archaieus: conditioning_consumer._complete_one -> apply_channel_stat.
        """
        key = (str(root), name, denom, method, f"{float(rho):.17g}")
        if key in _ratio_z_cache:
            return _ratio_z_cache[key]
        scale_u = _fit_operand_scale(root, name, method)
        scale_v = _fit_operand_scale(root, denom, method)
        chunks = []
        for rid in _shot_ids(root):
            try:
                t_n, v_n = _load_signal(root, rid, name)
                t_d, v_d = _load_signal(root, rid, denom)
            except (KeyError, OSError, ValueError):
                continue
            u = np.asarray(v_n, dtype=np.float64) / scale_u
            v = _align_to(t_n, t_d, v_d) / scale_v
            c = _finite(_regularized_ratio(u, v, rho))
            if c.size:
                chunks.append(c)
        if not chunks:
            _ratio_z_cache[key] = (0.0, 1.0)
            return 0.0, 1.0
        pooled = np.concatenate(chunks)
        mean = float(np.mean(pooled))
        std = float(np.std(pooled))
        if std == 0 or not np.isfinite(std):
            std = 1.0
        _ratio_z_cache[key] = (mean, std)
        return mean, std

    def conditioning_aware(times, values, params, context):
        name = str(context.get("signal_name") or "")
        rho = float(params.get("rho", 0.1))
        method = str(params.get("scale_method") or "pooled_rms")
        denom = str(params.get("denominator") or "").strip()
        record_id = str(context.get("record_id") or "")
        root = _root(context)

        scale_u = _fit_operand_scale(root, name, method)
        u = np.asarray(values, dtype=np.float64) / scale_u
        if not denom:
            cache_key = f"ca_scaled::{name}::{method}"
            if (str(root), cache_key) not in _channel_z_cache:
                samples = []
                for rid in _shot_ids(root):
                    try:
                        _, raw = _load_signal(root, rid, name)
                    except (KeyError, OSError, ValueError):
                        continue
                    samples.append(raw / scale_u)
                chunks = [_finite(s) for s in samples]
                chunks = [c for c in chunks if c.size]
                if chunks:
                    pooled = np.concatenate(chunks)
                    mean = float(np.mean(pooled))
                    std = float(np.std(pooled)) or 1.0
                else:
                    mean, std = 0.0, 1.0
                _channel_z_cache[(str(root), cache_key)] = (mean, std)
            mean, std = _channel_z_cache[(str(root), cache_key)]
            return times, (u - mean) / std

        if not record_id:
            raise ValueError("Conditioning-aware ratio needs a record_id")
        t_d, v_d = _load_signal(root, record_id, denom)
        scale_v = _fit_operand_scale(root, denom, method)
        v = _align_to(times, t_d, v_d) / scale_v
        c = _regularized_ratio(u, v, rho)
        mean, std = _fit_ratio_z(root, name, denom, method, rho)
        return times, (c - mean) / std

    def level_rate_relational(times, values, params, context):
        """Numerator = scaled LEVEL, denominator = scaled RATE.

        Shares the formula of reference_shifted_phase; only the numerator
        operand differs (Archaieus conditioning_consumer:1132-1156).
        """
        name = str(context.get("signal_name") or "")
        denom = str(params.get("denominator") or "").strip()
        if not denom:
            raise ValueError("Level-rate relational needs a denominator signal")
        record_id = str(context.get("record_id") or "")
        if not record_id:
            raise ValueError("Level-rate relational needs a record_id")
        rho = float(params.get("rho", 0.1))
        kappa = float(params.get("kappa", 1.0))
        method = str(params.get("scale_method") or "pooled_rms")
        root = _root(context)

        scale_u = _fit_operand_scale(root, name, method)
        t_d, v_d = _load_signal(root, record_id, denom)
        rate = _dt_derivative(t_d, v_d)
        scale_v = _fit_rate_scale(root, denom, method)
        s_eff = (
            _fit_clearance_normalized(root, denom, True, scale_v, method) + kappa
        )
        u = np.asarray(values, dtype=np.float64) / scale_u
        v = _align_to(times, t_d, rate) / scale_v
        return times, _clearance_shifted_ratio(u, v, rho, s_eff)

    def reference_shifted_phase(times, values, params, context):
        """Numerator = scaled RATE, denominator = scaled RATE.

        C_RS = (u_n + s_eff) * g(w), w = u_d + s_eff.
        """
        name = str(context.get("signal_name") or "")
        denom = str(params.get("denominator") or "").strip()
        if not denom:
            raise ValueError("Reference-shifted phase needs a denominator signal")
        record_id = str(context.get("record_id") or "")
        if not record_id:
            raise ValueError("Reference-shifted phase needs a record_id")
        rho = float(params.get("rho", 0.1))
        kappa = float(params.get("kappa", 1.0))
        method = str(params.get("scale_method") or "pooled_rms")
        root = _root(context)

        rate_y = _dt_derivative(times, values)
        t_d, v_d = _load_signal(root, record_id, denom)
        rate_x = _dt_derivative(t_d, v_d)
        scale_u = _fit_rate_scale(root, name, method)
        scale_v = _fit_rate_scale(root, denom, method)
        s_eff = (
            _fit_clearance_normalized(root, denom, True, scale_v, method) + kappa
        )
        u = rate_y / scale_u
        v = _align_to(times, t_d, rate_x) / scale_v
        return times, _clearance_shifted_ratio(u, v, rho, s_eff)

    def sensitivity_centered_phase(times, values, params, context):
        """C_SC = C_RS - g_bar*u_n, g_bar = mean_fit[g] frozen on the cohort.

        NOT C_RS - mean(C_RS): see the reference implementation.
        """
        name = str(context.get("signal_name") or "")
        denom = str(params.get("denominator") or "").strip()
        if not denom:
            raise ValueError("Sensitivity-centered phase needs a denominator signal")
        record_id = str(context.get("record_id") or "")
        if not record_id:
            raise ValueError("Sensitivity-centered phase needs a record_id")
        rho = float(params.get("rho", 0.1))
        kappa = float(params.get("kappa", 1.0))
        method = str(params.get("scale_method") or "pooled_rms")
        root = _root(context)

        rate_y = _dt_derivative(times, values)
        t_d, v_d = _load_signal(root, record_id, denom)
        rate_x = _dt_derivative(t_d, v_d)
        scale_u = _fit_rate_scale(root, name, method)
        scale_v = _fit_rate_scale(root, denom, method)
        s_eff = (
            _fit_clearance_normalized(root, denom, True, scale_v, method) + kappa
        )
        g_bar = _fit_mean_gain(root, denom, True, scale_v, method, rho, s_eff)
        u = rate_y / scale_u
        v = _align_to(times, t_d, rate_x) / scale_v
        c_rs = _clearance_shifted_ratio(u, v, rho, s_eff)
        return times, c_rs - g_bar * u

    def tangent_direction(times, values, params, context):
        """T_n = u_n / sqrt(u_n^2 + u_d^2 + rho^2).

        NOTE (audit 2026-08-25): both operands are LEVELS here. Archaieus
        forms the tangent pair from rate/rate (feature phase) or level/rate
        (target phase), never level/level, and emits BOTH components. This
        divergence is documented in AUDIT_dalia_transform_family.md and was
        left unchanged pending a decision.
        """
        name = str(context.get("signal_name") or "")
        denom = str(params.get("denominator") or "").strip()
        if not denom:
            raise ValueError("Tangent-direction needs a denominator signal")
        record_id = str(context.get("record_id") or "")
        if not record_id:
            raise ValueError("Tangent-direction needs a record_id")
        rho = float(params.get("rho", 0.1))
        method = str(params.get("scale_method") or "pooled_rms")
        root = _root(context)

        scale_u = _fit_operand_scale(root, name, method)
        t_d, v_d = _load_signal(root, record_id, denom)
        scale_v = _fit_operand_scale(root, denom, method)
        u_n = np.asarray(values, dtype=np.float64) / scale_u
        u_d = _align_to(times, t_d, v_d) / scale_v
        R = np.sqrt(u_n * u_n + u_d * u_d + rho * rho)
        return times, u_n / R

    rho_param = _p(0.1, "ρ (regularizer width)", min=1e-6)
    kappa_param = _p(1.0, "κ (clearance margin)", min=0.0)
    scale_param = _p(
        "pooled_rms",
        "Operand scale",
        options={"pooled_rms": "pooled_rms", "robust_zero_mad": "robust_zero_mad"},
    )
    den_param = _p("", "Denominator signal", options=_den_options())

    return {
        "per_realization_zscore": {
            "display_name": "Per-Realization Z-score",
            "category": "normalize",
            "parameters": {},
            "function": per_realization_zscore,
        },
        "per_channel_zscore": {
            "display_name": "Per-Channel Z-score",
            "category": "normalize",
            "parameters": {},
            "function": per_channel_zscore,
        },
        "conditioning_aware": {
            "display_name": "Conditioning-aware standardization",
            "category": "normalize",
            "parameters": {
                "rho": rho_param,
                "scale_method": scale_param,
                "denominator": den_param,
            },
            "function": conditioning_aware,
        },
        "level_rate_relational": {
            "display_name": "Level-rate relational coordinate",
            "category": "normalize",
            "parameters": {
                "denominator": den_param,
                "rho": rho_param,
                "kappa": kappa_param,
                "scale_method": scale_param,
            },
            "function": level_rate_relational,
        },
        "reference_shifted_phase": {
            "display_name": "Reference-shifted regularized phase",
            "category": "normalize",
            "parameters": {
                "denominator": den_param,
                "rho": rho_param,
                "kappa": kappa_param,
                "scale_method": scale_param,
            },
            "function": reference_shifted_phase,
        },
        "sensitivity_centered_phase": {
            "display_name": "Sensitivity-centered reference-shifted phase",
            "category": "normalize",
            "parameters": {
                "denominator": den_param,
                "rho": rho_param,
                "kappa": kappa_param,
                "scale_method": scale_param,
            },
            "function": sensitivity_centered_phase,
        },
        "tangent_direction": {
            "display_name": "Tangent-direction coordinate",
            "category": "normalize",
            "parameters": {
                "denominator": den_param,
                "rho": rho_param,
                "scale_method": scale_param,
            },
            "function": tangent_direction,
        },
    }
