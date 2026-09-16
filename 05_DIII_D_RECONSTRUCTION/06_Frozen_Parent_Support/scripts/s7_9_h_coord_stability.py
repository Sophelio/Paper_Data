"""S7.9 step H - coordinate-level bootstrap participation (REPORTING ONLY).

Descriptive summary of the already-computed frozen Rank-5 bootstrap output.
It defines no criterion, applies no threshold, prunes nothing, and confers no
selection authority. C_dev_star is unchanged and cannot change.
"""
from __future__ import annotations
import collections, json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parents[1]


def ds(s):
    o, d, c = [], 0, []
    for ch in s:
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
        if ch == "|" and d == 0:
            o.append("".join(c)); c = []
        else:
            c.append(ch)
    o.append("".join(c)); return o


b = pd.read_csv(OUT / "bootstrap_selection_frequency.csv")
sel = json.loads((OUT / "SELECTED_REPRESENTATION.json").read_text())
star = set(sel["canonical_coordinate_ids"])
sets = [set(ds(s)) for s in b.support_id]
freq = b.bootstrap_selection_frequency.values

n_w = collections.Counter(a for s in sets for a in s)
w_w = collections.Counter()
for s, f in zip(sets, freq):
    for a in s:
        w_w[a] += f

rows = [{"coordinate_id": a,
         "n_winning_supports_containing": n_w[a],
         "share_of_217_winners": n_w[a] / len(sets),
         "bootstrap_participation_weight": w_w[a],
         "in_C_dev_star": a in star}
        for a in n_w]
df = pd.DataFrame(rows).sort_values(
    ["bootstrap_participation_weight", "coordinate_id"], ascending=[False, True])
df.to_csv(OUT / "bootstrap_coordinate_participation.csv", index=False)

summary = {
    "record_id": "COORDINATE_LEVEL_BOOTSTRAP_PARTICIPATION_V1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "status": "REPORTING_ONLY",
    "defines_a_criterion": False,
    "applies_a_threshold": False,
    "prunes_any_candidate": False,
    "changes_C_dev_star": False,
    "source": "the frozen 1000-replicate Rank-5 bootstrap output, unmodified",
    "n_distinct_winning_supports": len(sets),
    "n_distinct_coordinates_across_winners": len(n_w),
    "universal_core": sorted(set.intersection(*sets)),
    "coordinates_in_at_least_half_of_winners": [
        {"coordinate_id": a, "share": n_w[a] / len(sets),
         "participation_weight": w_w[a], "in_C_dev_star": a in star}
        for a, _ in n_w.most_common() if n_w[a] >= len(sets) * 0.5],
    "C_dev_star_coordinates_in_at_least_half_of_winners":
        sorted([a for a in star if n_w.get(a, 0) >= len(sets) * 0.5]),
    "reading": (
        "support-level selection stability is LOW (0.093) while several "
        "individual coordinates recur in most winning supports; the specific "
        "12-atom support should be read as one representative of a broad "
        "equivalence class the 20-discharge development cohort cannot resolve "
        "between, not as a uniquely identified structure"),
}
(OUT / "manifests" / "COORDINATE_LEVEL_BOOTSTRAP_PARTICIPATION.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8")
print("universal core:", summary["universal_core"])
print("coords in >=50%% of winners:", len(summary["coordinates_in_at_least_half_of_winners"]))
print("C_dev_star coords in that set:", summary["C_dev_star_coordinates_in_at_least_half_of_winners"])
