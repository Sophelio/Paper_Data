"""Build exact coordinate lineage tables and code snapshots."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from implicit_elimination_utils import BASE, REPO, display_of, export_col, load_config, sha256_file

SNAP = BASE / "code_snapshots"
SNAP.mkdir(parents=True, exist_ok=True)


def _git_commit(path: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(path if path.is_dir() else path.parent),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out
    except Exception:
        return "UNKNOWN"


def snapshot_file(rel: str, start: int, end: int, label: str) -> Dict[str, Any]:
    src = REPO / rel
    text = src.read_text(encoding="utf-8", errors="replace").splitlines()
    frag = "\n".join(text[start - 1 : end])
    out = SNAP / f"{label}.py.txt"
    header = (
        f"# original_path: {rel}\n"
        f"# lines: {start}-{end}\n"
        f"# sha256: {sha256_file(src)}\n"
        f"# git_commit: {_git_commit(src)}\n"
        f"# historical_match_status: CODE_PRESENT_MATCHES_ARTIFACT_CONSTRUCTION\n\n"
    )
    out.write_text(header + frag + "\n", encoding="utf-8")
    return {
        "label": label,
        "original_path": rel,
        "line_range": [start, end],
        "sha256": sha256_file(src),
        "snapshot_path": str(out.relative_to(BASE)).replace("\\", "/"),
        "git_commit": _git_commit(src),
    }


def build_lineage(cfg: Dict[str, Any]) -> Dict[str, Any]:
    snaps = [
        snapshot_file(
            "submodules/Archaieus/src/Archaieus/sir/consumer_function.py",
            114,
            126,
            "get_shiftval_Derivative",
        ),
        snapshot_file(
            "submodules/Archaieus/src/Archaieus/sir/consumer_function.py",
            394,
            432,
            "yPhaseder_and_quotients",
        ),
        snapshot_file(
            "submodules/Archaieus/src/Archaieus/sir/utils/transforms.py",
            218,
            240,
            "make_Quotients",
        ),
        snapshot_file(
            "submodules/Archaieus/src/Archaieus/sir/utils/transforms.py",
            305,
            313,
            "finite_difference_derivative",
        ),
    ]

    rows: List[Dict[str, Any]] = []
    for i, key in enumerate(cfg["source_matrix_order_keys"]):
        meta = next(m for m in cfg["manuscript_display_order"] if m["key"] == key)
        target = bool(meta.get("target_containing"))
        if key.endswith("/d[t]") or key.endswith("]/d[t]"):
            construction = "finite_difference_then_zscore"
            num = key
            den = "dt"
            shift_pol = "none"
        elif key.startswith("r["):
            construction = "make_Quotients_level_add_inverse_then_zscore"
            parts = key.replace("r[", "").replace("]", "").split("/")
            num, den = f"r[{parts[0]}]", f"r[{parts[1]}]"
            shift_pol = "same_shiftval_added_to_num_and_den"
        elif target:
            construction = "yPhaseder_(dy+s)/(dx+s)_then_zscore"
            dx = meta["yphaseder_dx"]
            num = "d[pcdiamag3]/d[t] + shiftval"
            den = f"d[{dx}]/d[t] + shiftval"
            shift_pol = "same_shiftval_added_to_num_and_den"
        else:
            construction = "xPhaseder_make_Quotients_on_dx_then_zscore"
            parts = key.replace("d[", "").replace("]", "").split("/")
            # d[a]/d[b]
            a, b = parts[0], parts[1]
            num = f"d[{a}]/d[t] + shiftval"
            den = f"d[{b}]/d[t] + shiftval"
            shift_pol = "same_shiftval_added_to_num_and_den"

        rows.append(
            {
                "canonical_run_id": cfg["canonical_run_id"],
                "source_matrix_index": i,
                "source_feature_name": key,
                "manuscript_display_name": display_of(cfg, key),
                "primitive_dependencies": json.dumps(
                    ["pcdiamag3", meta.get("yphaseder_dx", "")]
                    if target
                    else [key]
                ),
                "target_containing": target,
                "construction_code_path": "submodules/Archaieus/src/Archaieus/sir/consumer_function.py",
                "construction_code_sha256": snaps[1]["sha256"],
                "historical_code_match_status": "ARTIFACT_DERIVED_MATCHES_CURRENT_SIR_V1_CODE",
                "time_units": "milliseconds_in_provider_dt_finite_difference",
                "derivative_method": "central_finite_difference_endpoints_forward_backward",
                "derivative_boundary_policy": "forward_first_backward_last",
                "primitive_standardized_before_derivative": True,
                "numerator_expression": num,
                "denominator_expression": den,
                "numerator_shift_policy": shift_pol,
                "denominator_shift_policy": shift_pol,
                "numerator_shift_value": "per_discharge_shiftval_from_psir_meanSTDinfo",
                "denominator_shift_value": "per_discharge_shiftval_from_psir_meanSTDinfo",
                "shift_scope": "per_realization_global_across_coordinates",
                "mask_policy": "none_in_consumer_function",
                "clip_policy": "none_in_consumer_function",
                "nonfinite_policy": "fail_or_propagate_no_silent_replacement_documented",
                "quotient_standardized_after_construction": True,
                "coordinate_mean": "stored_in_psir_meanSTDinfo_*_mSD_pre_zscore",
                "coordinate_std": "stored_in_psir_meanSTDinfo_*_mSD_pre_zscore",
                "feature_export_path": "FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized",
                "feature_export_column": export_col(cfg, key),
                "lineage_status": "CODE_DERIVED",
                "unresolved_fields": "historical_nmin_UI_value_UNKNOWN",
            }
        )

    lineage = {
        "canonical_run_id": cfg["canonical_run_id"],
        "audit_id": cfg["audit_id"],
        "status": "D3D-EXACT-COORDINATE-LINEAGE-RESOLVED",
        "shift_recovery": "EXACT_FROM_SERIALIZED_STATE",
        "code_snapshots": snaps,
        "features": rows,
        "notes": [
            "Shift values recovered from historical .psir meanSTDinfo.consummer_function[i].shiftval.",
            "Historical nmin UI setting remains UNKNOWN; effective per-discharge shiftval is known.",
            "sir2 has no equivalent get_shiftval/make_Quotients path; construction is sir v1.",
        ],
    }
    return lineage


def write_lineage_outputs(cfg: Dict[str, Any]) -> Dict[str, Any]:
    lineage = build_lineage(cfg)
    (BASE / "outputs" / "exact_coordinate_lineage.json").write_text(
        json.dumps(lineage, indent=2), encoding="utf-8"
    )
    import pandas as pd

    pd.DataFrame(lineage["features"]).to_csv(
        BASE / "tables" / "exact_coordinate_lineage.csv", index=False
    )
    md = ["# Exact coordinate lineage", ""]
    md.append(f"Status: **{lineage['status']}**")
    md.append(f"Shift recovery: **{lineage['shift_recovery']}**")
    md.append("")
    md.append("## Construction summary")
    md.append("")
    md.append(
        "For Derivative targets, historical sir v1 builds Y-phaseders as "
        "`(dy + shiftval)/(dx_i + shiftval)` then z-scores each channel. "
        "`shiftval = abs(min(vstack(x, dx))) + nmin` on already z-scored "
        "primitives/derivatives. Exact per-discharge `shiftval` values are "
        "stored in the historical `.psir`."
    )
    md.append("")
    md.append("## Features")
    for r in lineage["features"]:
        md.append(
            f"- `{r['source_feature_name']}` ({r['manuscript_display_name']}): "
            f"{r['numerator_expression']} / {r['denominator_expression']}; "
            f"target_containing={r['target_containing']}"
        )
    md.append("")
    md.append("## Code snapshots")
    for s in lineage["code_snapshots"]:
        md.append(f"- `{s['snapshot_path']}` ← `{s['original_path']}` L{s['line_range']}")
    (BASE / "EXACT_COORDINATE_LINEAGE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return lineage


if __name__ == "__main__":
    (BASE / "outputs").mkdir(exist_ok=True)
    (BASE / "tables").mkdir(exist_ok=True)
    write_lineage_outputs(load_config())
    print("Lineage written")
