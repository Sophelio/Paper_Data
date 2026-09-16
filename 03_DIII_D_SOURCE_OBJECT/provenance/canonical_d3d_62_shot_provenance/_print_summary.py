import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
files = [
    "d3d_discharge_ledger.csv",
    "D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md",
]
print("=== PROVENANCE PACKAGE SUMMARY ===")
for name in files:
    p = root / name
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    print(f"{name}")
    print(f"  path: {p}")
    print(f"  sha256: {h}")
    print(f"  bytes: {p.stat().st_size}")

stats = json.loads((root / "_ledger_build_stats.json").read_text(encoding="utf-8"))
print("VALIDATION")
print(
    "  rows",
    stats["n_rows"],
    "unique_shots",
    stats["unique_shots"],
    "unique_realization_index",
    stats["unique_realization_index"],
)
print("  all_eight_available", stats["all_eight_canonical_available"])
print(
    "  prmtan_teped_available",
    stats["prmtan_teped_available_count"],
    "(admitted_to_search=FALSE for all rows)",
)
print(
    "  aligned_N min/median/max",
    stats["aligned_sample_count_min"],
    stats["aligned_sample_count_median"],
    stats["aligned_sample_count_max"],
)
print(
    "  common_support_duration_s min/median/max",
    round(stats["common_support_duration_s_min"], 3),
    round(stats["common_support_duration_s_median"], 3),
    round(stats["common_support_duration_s_max"], 3),
)
print("  42-shot subset in repo artifacts: NONE FOUND")
print("UNRESOLVED_FIELDS")
for u in [
    "canonical_run_id=D3D-CANONICAL-62SHOT-UNASSIGNED",
    "physical_units_per_signal",
    "resampled_data_v6_generator_and_DOI",
    "ADMISSIBLE_SHOTS_selection_algorithm",
    "original_SIR_search_hyperparameters",
    "manuscript_42_realizations",
    "FD_dt_seconds_vs_milliseconds",
    "spline_bc_overrides_in_export",
    "manuscript_tex_Table_S3_paths",
]:
    print(" -", u)
