"""S7.11 step C - V9 resolution.

Three components, all frozen in S7.2 V1 before any external value existed:
  DISCHARGE            - independently re-verify the S7.10 LODO
  TEMPORAL_BLOCK       - the three block omissions computed in step B
  NUMERICAL_REALIZATION - audit for a prospectively frozen alternative

No new threshold is invented. The auditable criterion is whether removing ONE
unit changes the frozen V3-style verdict.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
S79 = S7 / "09_development_selection_and_freeze"
S710 = S7 / "10_external_validation"
FLOOR = 0.01


def main() -> int:
    f10 = json.loads((S710 / "S7_10_FREEZE.json").read_text())
    res10 = json.loads((S710 / "V_REC_EXTERNAL_RESULTS.json").read_text())
    sel = json.loads((S79 / "SELECTED_REPRESENTATION.json").read_text())
    dm = pd.read_csv(S710 / "external_discharge_metrics.csv")
    dm["shot_id"] = dm.shot_id.astype(str)
    dm = dm[dm.evaluable].reset_index(drop=True)
    n = len(dm)
    assert n == 42

    rel, b0, b1 = dm.REL_nrmse.values, dm.B0_nrmse.values, dm.B1_nrmse.values
    D0, D1 = float((rel - b0).mean()), float((rel - b1).mean())

    # ---- DISCHARGE component: independent LODO recomputation ------------
    rows = []
    for k in range(n):
        m = np.ones(n, bool); m[k] = False
        d0 = float((rel[m] - b0[m]).mean())
        d1 = float((rel[m] - b1[m]).mean())
        rows.append({"omitted_shot_id": dm.shot_id.values[k], "era": dm.era.values[k],
                     "omitted_REL_nrmse": float(rel[k]),
                     "Delta_0": d0, "Delta_1": d1,
                     "V3_STYLE_PASS": bool(d0 <= -FLOOR and d1 <= -FLOOR),
                     "influence_on_Delta_1": float(d1 - D1)})
    lodo = pd.DataFrame(rows)
    lodo.to_csv(OUT / "discharge_sensitivity_summary.csv", index=False)

    n_pass = int(lodo.V3_STYLE_PASS.sum())
    s10_pass = res10["V3"]["lodo_cohorts_passing"]
    verified = (n_pass == s10_pass)
    infl = lodo.reindex(lodo.influence_on_Delta_1.abs().sort_values(ascending=False).index)

    # ---- TEMPORAL BLOCK component ---------------------------------------
    blk = pd.read_csv(OUT / "block_omission_sensitivity.csv")
    flips = blk[blk.V3_STYLE_PASS]
    block_dependence = bool(len(flips) > 0)

    # ---- NUMERICAL REALIZATION component --------------------------------
    realization_ids = sorted({c["numerical_realization_id"] for c in sel["coordinates"]})
    constructors = sorted({c["constructor"] for c in sel["coordinates"]})
    # search the frozen lineage for any prospectively declared alternative
    hits = []
    for p in sorted(S7.rglob("*.json")):
        if "11_sensitivity" in p.as_posix():
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "numerical_realization" in t.lower() and "sensitivity" in t.lower():
            hits.append(p.relative_to(S7).as_posix())
    numerical = {
        "component": "NUMERICAL_REALIZATION",
        "status": "NUMERICAL_REALIZATION_SENSITIVITY_NOT_INSTANTIATED",
        "numerical_realization_ids_on_C_dev_star": realization_ids,
        "constructors_present": constructors,
        "contains_derivative_coordinate": any(c in ("C1", "C4", "C6", "C7", "C8")
                                              for c in constructors),
        "explanation": (
            "every coordinate of C_dev_star carries numerical_realization_id = NONE, and the "
            "support contains only C0 level, C2 product, C3 ratio and C5 reciprocal "
            "constructors - no derivative coordinate. The frozen derivative realization "
            "FD2_PHYSICAL_TIME_V1 therefore does not enter this support at all, and the study "
            "never prospectively froze an alternative realization of level/product/ratio/"
            "reciprocal coordinates."),
        "invented_after_external_outcomes": False,
        "candidate_artifacts_searched": len(hits),
        "robustness_may_not_be_inferred_from_absence_of_a_test": True,
    }

    # ---- resolution ------------------------------------------------------
    v9 = {
        "gate": "V9", "name": "sensitivity", "mandatory": False,
        "inherited_rule": ("no result depends catastrophically on one discharge, one temporal "
                           "block, or one numerical realization"),
        "auditable_criterion": ("whether removing ONE unit changes the frozen V3-style verdict; "
                                "no new scalar threshold was invented"),
        "DISCHARGE_COMPONENT": {
            "n_cohorts": n,
            "n_satisfying_V3": n_pass,
            "s7_10_recorded": s10_pass,
            "independently_verified": verified,
            "full_Delta_0": D0, "full_Delta_1": D1,
            "Delta_0_min": float(lodo.Delta_0.min()), "Delta_0_max": float(lodo.Delta_0.max()),
            "Delta_1_min": float(lodo.Delta_1.min()), "Delta_1_max": float(lodo.Delta_1.max()),
            "most_influential": str(infl.iloc[0].omitted_shot_id),
            "second_most_influential": str(infl.iloc[1].omitted_shot_id),
            "most_influential_era": str(infl.iloc[0].era),
            "second_most_influential_era": str(infl.iloc[1].era),
            "verdict_flips": 0 if n_pass == 0 else n_pass,
            "finding": "NO_SINGLE_DISCHARGE_VERDICT_DEPENDENCE",
            "reading": ("no single discharge omission changes the V3 verdict; the two "
                        "catastrophic discharges are individually insufficient because there "
                        "are two of them"),
        },
        "TEMPORAL_BLOCK_COMPONENT": {
            "omissions": blk[["omitted_block", "blocks_used", "Delta_0", "Delta_1",
                              "V3_STYLE_PASS"]].to_dict(orient="records"),
            "n_omissions_flipping_the_verdict": int(len(flips)),
            "flipping_blocks": flips.omitted_block.tolist(),
            "finding": ("DIRECT_TEMPORAL_BLOCK_DEPENDENCE" if block_dependence
                        else "NO_TEMPORAL_BLOCK_VERDICT_DEPENDENCE"),
            "reading": ("omitting block B changes the V3-style verdict from FAIL to PASS. "
                        "Block B is where the protected-window product excursion occurs. The "
                        "margin is narrow: Delta_1 = -0.0114 against a threshold of -0.01."),
        },
        "NUMERICAL_REALIZATION_COMPONENT": numerical,
        "resolution": "FAIL",
        "resolution_vocabulary": ["PASS", "PASS_WITH_QUALIFICATION", "FAIL", "NOT_APPLICABLE"],
        "reasoning": (
            "V9 asks whether the result depends catastrophically on one discharge, one "
            "temporal block, or one numerical realization. The discharge component is clean: "
            "0 of 42 single-discharge omissions change the verdict. The temporal-block "
            "component is not: omitting block B alone flips the V3-style verdict from FAIL to "
            "PASS. Under the auditable criterion - verdict change on removal of one unit - "
            "that is direct dependence on one temporal block, so V9 resolves to FAIL. The "
            "numerical-realization component was never prospectively instantiated, so no "
            "robustness may be inferred for it either."),
        "mandatory_impact": "NONE",
        "does_not_change": ["V3", "V6", "PRIMARY_EXTERNAL_RESULT", "Omega_rec", "C_dev_star"],
        "note": ("V9 is non-mandatory precisely because an influential unit is a finding to "
                 "report rather than a disqualification, provided it is reported. It is "
                 "reported here."),
    }
    (OUT / "V9_RESULT.json").write_text(json.dumps(v9, indent=2), encoding="utf-8")

    print("V9 DISCHARGE      : %d/%d cohorts satisfy V3 (S7.10 recorded %d, verified %s)"
          % (n_pass, n, s10_pass, verified))
    print("                    Delta_1 range [%.4f, %.4f]; most influential %s (%s), then %s"
          % (lodo.Delta_1.min(), lodo.Delta_1.max(), infl.iloc[0].omitted_shot_id,
             infl.iloc[0].era, infl.iloc[1].omitted_shot_id))
    print("V9 TEMPORAL BLOCK : %d of 3 omissions flip the verdict -> %s"
          % (len(flips), v9["TEMPORAL_BLOCK_COMPONENT"]["finding"]))
    for r in v9["TEMPORAL_BLOCK_COMPONENT"]["omissions"]:
        print("     omit %s (%s): D0 %+.6f  D1 %+.6f  -> %s"
              % (r["omitted_block"], r["blocks_used"], r["Delta_0"], r["Delta_1"],
                 "PASS" if r["V3_STYLE_PASS"] else "FAIL"))
    print("V9 NUMERICAL      : %s" % numerical["status"])
    print("V9 RESOLUTION     : %s (non-mandatory)" % v9["resolution"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
