#!/usr/bin/env python
"""Build the canonical 62-shot DIII-D discharge ledger from local npz sources.

Forensic / provenance only — does not refit models or alter analysis outputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent
CSV_PATH = OUT_DIR / "d3d_discharge_ledger.csv"
STATS_PATH = OUT_DIR / "_ledger_build_stats.json"

PROVIDER_SHOTS = (
    REPO
    / "Paper Examples"
    / "Relational Coordinates for Multimodal Plasma Observations"
    / "SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py"
)
DATA_DIR = Path(r"D:\DIII-D ELM data set\resampled_data_v6")
CANONICAL_EXPORT = (
    REPO
    / "FEATURE_EXPORTS"
    / "pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized"
)
METRICS_CSV = REPO / "figures" / "d3d_discharge_validation_metrics.csv"

CANONICAL_SIGNALS = (
    "pcdiamag3",
    "pinj",
    "density",
    "ip",
    "betan",
    "q95",
    "li",
    "kappa",
)
CONTEXT_SIGNAL = "prmtan_teped"
TARGET_N = 1000  # Paper Examples diiid_elm_data_provider.TARGET_N
CANONICAL_RUN_ID = "D3D-CANONICAL-62SHOT-UNASSIGNED"
# realization_index convention: zero-based, sorted ascending by shot number.


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_admissible_shots() -> list[str]:
    # Import by exec of the set literal from the authoritative provider file.
    text = PROVIDER_SHOTS.read_text(encoding="utf-8")
    start = text.index("ADMISSIBLE_SHOTS")
    brace = text.index("{", start)
    end = text.index("}", brace)
    body = text[brace + 1 : end]
    shots = []
    for tok in body.replace("\n", " ").split(","):
        tok = tok.strip().strip('"').strip("'")
        if tok:
            shots.append(tok)
    shots = sorted(shots, key=int)
    if len(shots) != 62:
        raise RuntimeError(f"expected 62 admissible shots, found {len(shots)}")
    if len(set(shots)) != 62:
        raise RuntimeError("duplicate shots in ADMISSIBLE_SHOTS")
    return shots


def _clean_signal(archive, name: str):
    data_key = f"{name}_data"
    times_key = f"{name}_times"
    if data_key not in archive:
        return None
    values = np.asarray(archive[data_key], dtype=np.float64)
    if times_key in archive:
        times = np.asarray(archive[times_key], dtype=np.float64)
    else:
        times = np.arange(len(values), dtype=np.float64)
    n = min(len(times), len(values))
    times, values = times[:n], values[:n]
    raw_n = int(n)
    finite = np.isfinite(times) & np.isfinite(values)
    finite_frac = float(np.mean(finite)) if n else 0.0
    times, values = times[finite], values[finite]
    if len(times) == 0:
        return {
            "available": True,
            "finite_fraction": finite_frac,
            "raw_n": raw_n,
            "native_n": 0,
            "t0": np.nan,
            "t1": np.nan,
            "med_dt_ms": np.nan,
        }
    order = np.argsort(times, kind="stable")
    times, values = times[order], values[order]
    keep = np.concatenate(([True], np.diff(times) > 0))
    times, values = times[keep], values[keep]
    med_dt = float(np.median(np.diff(times))) if len(times) > 1 else np.nan
    return {
        "available": True,
        "finite_fraction": finite_frac,
        "raw_n": raw_n,
        "native_n": int(len(times)),
        "t0": float(times[0]),
        "t1": float(times[-1]),
        "med_dt_ms": med_dt,
        "times": times,
        "values": values,
    }


def _common_support(series: dict):
    """Match Paper Examples provider: intersection window, TARGET_N linspace."""
    usable = {
        k: v
        for k, v in series.items()
        if v is not None and v.get("native_n", 0) >= 2
    }
    if len(usable) < len(CANONICAL_SIGNALS):
        return None
    t0 = max(v["t0"] for v in usable.values())
    t1 = min(v["t1"] for v in usable.values())
    if not np.isfinite(t0) or not np.isfinite(t1) or t1 <= t0:
        return None
    grid = np.linspace(t0, t1, TARGET_N, dtype=np.float64)
    dt_ms = float(grid[1] - grid[0])
    # Valid sample count after resampling: count finite rows across all signals.
    rows = []
    for name in CANONICAL_SIGNALS:
        t, v = usable[name]["times"], usable[name]["values"]
        in_window = (t >= t0) & (t <= t1)
        n_native = int(np.count_nonzero(in_window))
        if n_native > TARGET_N:
            # block-average path yields TARGET_N points (assumed finite)
            aligned = np.full(TARGET_N, 1.0)
        else:
            aligned = np.interp(grid, t, v)
        rows.append(np.isfinite(aligned))
    valid = np.all(np.vstack(rows), axis=0)
    return {
        "common_start_ms": t0,
        "common_end_ms": t1,
        "grid_dt_ms": dt_ms,
        "grid_dt_seconds": dt_ms / 1000.0,
        "aligned_sample_count": TARGET_N,
        "valid_sample_count": int(np.count_nonzero(valid)),
        "duration_ms": t1 - t0,
        "duration_s": (t1 - t0) / 1000.0,
    }


def inspect_shot(shot: str, realization_index: int) -> dict:
    npz = DATA_DIR / f"shot_{shot}_resampled.npz"
    meta = DATA_DIR / f"shot_{shot}_metadata.json"
    row = {
        "canonical_run_id": CANONICAL_RUN_ID,
        "realization_index": realization_index,
        "shot": int(shot),
        "included_canonical": "TRUE",
        "inclusion_basis": (
            "ADMISSIBLE_SHOTS in Paper Examples/.../"
            "SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py; "
            "corroborated by FEATURE_EXPORTS/*/shot_* and "
            "figures/d3d_discharge_validation_metrics.csv"
        ),
        "exclusion_reason": "",
        "source_file": npz.name if npz.exists() else "UNKNOWN",
        "source_absolute_path": str(npz.resolve()) if npz.exists() else "UNKNOWN",
        "source_format": "numpy_npz_paired_signal_times_ms",
        "source_file_sha256": _sha256_file(npz) if npz.exists() else "UNKNOWN",
        "data_snapshot_or_revision": (
            f"resampled_data_v6; companion metadata="
            f"{meta.name if meta.exists() else 'MISSING'}"
        ),
        "raw_time_key": "<signal>_times",
        "prmtan_teped_admitted_to_search": "FALSE",
    }
    if not npz.exists():
        for k in (
            "raw_start_time",
            "raw_end_time",
            "common_start_time",
            "common_end_time",
            "native_sample_count",
            "aligned_sample_count",
            "valid_sample_count",
            "grid_dt_seconds",
            "mask_or_invalid_interval_summary",
            "alignment_status",
            "preprocessing_status",
            "notes",
        ):
            row[k] = "UNKNOWN"
        for s in CANONICAL_SIGNALS + (CONTEXT_SIGNAL,):
            row[f"{s}_available"] = "UNKNOWN"
            row[f"{s}_finite_fraction"] = "UNKNOWN"
        return row

    with np.load(npz, allow_pickle=False) as archive:
        keys = set(archive.keys())
        series = {}
        for s in CANONICAL_SIGNALS + (CONTEXT_SIGNAL,):
            info = _clean_signal(archive, s)
            series[s] = info
            if info is None:
                row[f"{s}_available"] = "FALSE"
                row[f"{s}_finite_fraction"] = "UNKNOWN"
            else:
                row[f"{s}_available"] = "TRUE"
                row[f"{s}_finite_fraction"] = f"{info['finite_fraction']:.6f}"

        # Raw interval: union of canonical-search signals' cleaned ranges.
        t0s = [series[s]["t0"] for s in CANONICAL_SIGNALS if series[s] is not None]
        t1s = [series[s]["t1"] for s in CANONICAL_SIGNALS if series[s] is not None]
        row["raw_start_time"] = f"{min(t0s):.6f} ms" if t0s else "UNKNOWN"
        row["raw_end_time"] = f"{max(t1s):.6f} ms" if t1s else "UNKNOWN"
        native_counts = {
            s: series[s]["native_n"] for s in CANONICAL_SIGNALS if series[s] is not None
        }
        row["native_sample_count"] = (
            ";".join(f"{k}={v}" for k, v in native_counts.items())
            if native_counts
            else "UNKNOWN"
        )

        common = _common_support(
            {s: series[s] for s in CANONICAL_SIGNALS if series[s] is not None}
        )
        if common is None:
            row["common_start_time"] = "UNKNOWN"
            row["common_end_time"] = "UNKNOWN"
            row["aligned_sample_count"] = "UNKNOWN"
            row["valid_sample_count"] = "UNKNOWN"
            row["grid_dt_seconds"] = "UNKNOWN"
            row["alignment_status"] = "FAILED_EMPTY_OR_INSUFFICIENT_COMMON_SUPPORT"
            row["preprocessing_status"] = "UNKNOWN"
            row["mask_or_invalid_interval_summary"] = "UNKNOWN"
            row["notes"] = "Could not form TARGET_N common grid for 8 search signals"
            row["_duration_s"] = None
            row["_aligned_n"] = None
        else:
            row["common_start_time"] = f"{common['common_start_ms']:.6f} ms"
            row["common_end_time"] = f"{common['common_end_ms']:.6f} ms"
            row["aligned_sample_count"] = common["aligned_sample_count"]
            row["valid_sample_count"] = common["valid_sample_count"]
            row["grid_dt_seconds"] = f"{common['grid_dt_seconds']:.9f}"
            row["alignment_status"] = (
                "OK_INTERSECTION_LINSPACE_TARGET_N_1000_PAPER_PROVIDER"
            )
            row["preprocessing_status"] = (
                "SOURCE_CLEANED_FINITE_SORTED_DEDUP; "
                "PROVIDER_RESAMPLE_BLOCKAVG_OR_LINEAR_INTERP; "
                "SMOOTH_RATE_0; "
                "SIR_ZSCORE_PER_REALIZATION_DOWNSTREAM"
            )
            dropped = []
            for s in CANONICAL_SIGNALS:
                info = series[s]
                if info is not None and info["finite_fraction"] < 1.0:
                    dropped.append(f"{s}:nonfinite_frac={1.0 - info['finite_fraction']:.4f}")
            row["mask_or_invalid_interval_summary"] = (
                ";".join(dropped) if dropped else "no_nonfinite_after_load_for_canonical_signals"
            )
            med_dts = {
                s: series[s]["med_dt_ms"]
                for s in CANONICAL_SIGNALS
                if series[s] is not None
            }
            row["notes"] = (
                f"time_units=ms_from_provider_docstring; "
                f"native_median_dt_ms={{{'; '.join(f'{k}:{v:.4f}' for k,v in med_dts.items())}}}; "
                f"grid_dt_NOT_fixed_0.020s; "
                f"metadata_json={'present' if meta.exists() else 'absent'}; "
                f"export_present="
                f"{(CANONICAL_EXPORT / f'shot_{shot}_resampled__model.parquet').exists()}"
            )
            row["_duration_s"] = common["duration_s"]
            row["_aligned_n"] = common["aligned_sample_count"]

    return row


COLUMNS = [
    "canonical_run_id",
    "realization_index",
    "shot",
    "included_canonical",
    "inclusion_basis",
    "exclusion_reason",
    "source_file",
    "source_absolute_path",
    "source_format",
    "source_file_sha256",
    "data_snapshot_or_revision",
    "raw_time_key",
    "raw_start_time",
    "raw_end_time",
    "common_start_time",
    "common_end_time",
    "native_sample_count",
    "aligned_sample_count",
    "valid_sample_count",
    "grid_dt_seconds",
    "pcdiamag3_available",
    "pinj_available",
    "density_available",
    "ip_available",
    "betan_available",
    "q95_available",
    "li_available",
    "kappa_available",
    "prmtan_teped_available",
    "prmtan_teped_admitted_to_search",
    "pcdiamag3_finite_fraction",
    "pinj_finite_fraction",
    "density_finite_fraction",
    "ip_finite_fraction",
    "betan_finite_fraction",
    "q95_finite_fraction",
    "li_finite_fraction",
    "kappa_finite_fraction",
    "prmtan_teped_finite_fraction",
    "mask_or_invalid_interval_summary",
    "alignment_status",
    "preprocessing_status",
    "notes",
]


def main() -> int:
    shots = _load_admissible_shots()
    rows = [inspect_shot(s, i) for i, s in enumerate(shots)]

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "UNKNOWN") for k in COLUMNS})

    aligned = [r["_aligned_n"] for r in rows if r.get("_aligned_n") is not None]
    durs = [r["_duration_s"] for r in rows if r.get("_duration_s") is not None]
    avail = {
        s: sum(1 for r in rows if r.get(f"{s}_available") == "TRUE")
        for s in CANONICAL_SIGNALS + (CONTEXT_SIGNAL,)
    }
    stats = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_rows": len(rows),
        "unique_shots": len({r["shot"] for r in rows}),
        "unique_realization_index": len({r["realization_index"] for r in rows}),
        "availability_counts": avail,
        "all_eight_canonical_available": all(
            avail[s] == 62 for s in CANONICAL_SIGNALS
        ),
        "prmtan_teped_available_count": avail[CONTEXT_SIGNAL],
        "aligned_sample_count_min": min(aligned) if aligned else None,
        "aligned_sample_count_median": float(np.median(aligned)) if aligned else None,
        "aligned_sample_count_max": max(aligned) if aligned else None,
        "common_support_duration_s_min": min(durs) if durs else None,
        "common_support_duration_s_median": float(np.median(durs)) if durs else None,
        "common_support_duration_s_max": max(durs) if durs else None,
        "csv_sha256": _sha256_file(CSV_PATH),
        "admissible_shots_source": str(PROVIDER_SHOTS.relative_to(REPO)),
        "admissible_shots_sha256": _sha256_file(PROVIDER_SHOTS),
        "metrics_csv_exists": METRICS_CSV.exists(),
        "metrics_csv_sha256": _sha256_file(METRICS_CSV) if METRICS_CSV.exists() else None,
        "canonical_export_dir": str(CANONICAL_EXPORT.relative_to(REPO)),
        "grid_dt_seconds_unique": sorted(
            {r["grid_dt_seconds"] for r in rows if r.get("grid_dt_seconds") not in (None, "UNKNOWN")}
        ),
    }
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))
    print(f"Wrote {CSV_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
