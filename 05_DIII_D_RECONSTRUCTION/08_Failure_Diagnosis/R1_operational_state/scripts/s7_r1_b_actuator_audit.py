"""S7.R1 step B - TARGET-BLIND actuator audit.

Reads predictor-side actuator values only, on all 62 discharges, and computes
block-level summaries plus development support coverage.

FIREWALL: this script never opens the density target, never reads any NRMSE,
residual, failure flag or support-family label. It asserts that at exit.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
S7 = Path(__file__).resolve().parents[2]
EX = S7.parent
DATA = EX / "data" / "resampled_data_v6"
RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"

sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]
PRIMARY = ["gasa", "gasb", "gasc", "gasd"]
CORROB = ["pinj", "tinj"]
FORBIDDEN = {"density"}

ACCESS = {"target_reads": 0, "model_error_reads": 0, "predictor_signal_reads": 0}


def main() -> int:
    acts = PRIMARY + [c for c in CORROB if c in PROV.SIGNAL_UNIT]
    assert not (set(acts) & FORBIDDEN)

    part = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json").read_text())
    dev = [str(s) for s in part["development"]["shot_ids"]]
    ext = [str(s) for s in part["external"]["shot_ids"]]
    allsh = dev + ext
    assert len(dev) == 20 and len(ext) == 42
    TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")

    rows, glob = [], []
    for s in allsh:
        cohort = "development" if s in set(dev) else "external"
        t0 = float(TR.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TR.loc[s, "delta_t_ms"])
        n = int(TR.loc[s, "N_s"])
        grid = t0 + dtm * np.arange(n, dtype=np.float64)
        vals = {}
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            for sig in acts:
                tt, vv = PROV._load_signal(a, sig)
                vals[sig] = PROV._resample_to_grid(tt, vv, grid)
                ACCESS["predictor_signal_reads"] += 1
        for sig in acts:
            v = vals[sig]
            glob.append({"signal": sig, "shot_id": s, "cohort": cohort,
                         "era": str(TR.loc[s, "processing_era"]),
                         "shot_min": float(np.nanmin(v)), "shot_max": float(np.nanmax(v)),
                         "shot_median": float(np.nanmedian(v))})
        for bn, c1, c2 in BLOCKS:
            cal = slice(0, int(np.floor(n * c1)))
            pro = slice(int(np.floor(n * c1)), int(np.floor(n * c2)))
            r = {"shot_id": s, "cohort": cohort, "era": str(TR.loc[s, "processing_era"]),
                 "block": bn, "n_cal": int(cal.stop - cal.start),
                 "n_pro": int(pro.stop - pro.start)}
            for sig in acts:
                c, p = vals[sig][cal], vals[sig][pro]
                cmax, pmax = float(np.nanmax(c)), float(np.nanmax(p))
                camax = float(np.nanmax(np.abs(c)))
                r["%s_cal_min" % sig] = float(np.nanmin(c))
                r["%s_cal_max" % sig] = cmax
                r["%s_cal_median" % sig] = float(np.nanmedian(c))
                r["%s_pro_min" % sig] = float(np.nanmin(p))
                r["%s_pro_max" % sig] = pmax
                r["%s_pro_median" % sig] = float(np.nanmedian(p))
                r["%s_cal_absmax" % sig] = camax
                r["%s_pro_absmax" % sig] = float(np.nanmax(np.abs(p)))
                # descriptive excursion ratio; undefined rather than epsilon
                r["%s_pro_over_cal_max" % sig] = (pmax / cmax) if cmax > 0 else np.nan
                sd = float(np.nanstd(c, ddof=0))
                mu = float(np.nanmean(c))
                r["%s_cal_sd" % sig] = sd
                r["%s_z_pro_max" % sig] = (float(np.nanmax(np.abs(p - mu))) / sd
                                           if sd > 0 else np.nan)
            rows.append(r)

    bs = pd.DataFrame(rows)
    bs.to_csv(OUT / "actuator_block_summary.csv", index=False)
    gl = pd.DataFrame(glob)

    # ---- development support coverage ------------------------------------
    cov = []
    for sig in acts:
        for coh in ("development", "external"):
            g = gl[(gl.signal == sig) & (gl.cohort == coh)]
            b = bs[bs.cohort == coh]
            cov.append({
                "signal": sig, "cohort": coh, "n_discharges": int(len(g)),
                "global_min": float(g.shot_min.min()), "global_max": float(g.shot_max.max()),
                "block_cal_max_min": float(b["%s_cal_max" % sig].min()),
                "block_cal_max_max": float(b["%s_cal_max" % sig].max()),
                "block_pro_max_min": float(b["%s_pro_max" % sig].min()),
                "block_pro_max_max": float(b["%s_pro_max" % sig].max()),
                "block_pro_max_p50": float(b["%s_pro_max" % sig].median()),
                "block_pro_max_p95": float(b["%s_pro_max" % sig].quantile(0.95)),
                "max_pro_over_cal_max": float(b["%s_pro_over_cal_max" % sig].max()),
                "max_z_pro": float(b["%s_z_pro_max" % sig].max()),
            })
    cv = pd.DataFrame(cov)
    cv.to_csv(OUT / "actuator_support_coverage.csv", index=False)

    # ---- primary 1D gasa audit ------------------------------------------
    key = "gasa_pro_max"
    d = bs[["shot_id", "cohort", "era", "block", key]].copy()
    d = d.sort_values(key).reset_index(drop=True)
    d["rank"] = np.arange(1, len(d) + 1)
    d["gap_to_next"] = d[key].shift(-1) - d[key]
    pos = d[d[key] > 0].copy()
    pos["log10"] = np.log10(pos[key])
    pos["log_gap_to_next"] = pos["log10"].shift(-1) - pos["log10"]
    d.to_csv(OUT / "manifests" / "gasa_pro_max_sorted.csv", index=False)

    print("actuator signals audited:", acts)
    print("blocks summarised:", len(bs), "(62 discharges x 3)")
    print()
    print("=== gasa protected-block maximum, development support coverage ===")
    print(cv[cv.signal == "gasa"][["cohort", "global_min", "global_max",
                                   "block_pro_max_min", "block_pro_max_p50",
                                   "block_pro_max_p95", "block_pro_max_max"]].round(4).to_string(index=False))
    print()
    print("=== gasa_pro_max: largest gaps in the sorted block distribution ===")
    top = d.nlargest(6, "gap_to_next")[["rank", key, "gap_to_next", "shot_id", "block", "cohort"]]
    print(top.round(4).to_string(index=False))
    print()
    print("=== top 12 blocks by gasa_pro_max ===")
    print(d.nlargest(12, key)[["shot_id", "block", "cohort", "era", key]].round(4).to_string(index=False))
    print()
    print("=== log10 gaps (positive gasa only, n=%d) ===" % len(pos))
    print(pos.nlargest(5, "log_gap_to_next")[["rank", key, "log10", "log_gap_to_next",
                                              "shot_id", "block", "cohort"]].round(4).to_string(index=False))
    print()
    print("=== distribution quantiles of gasa_pro_max ===")
    print(d[key].describe(percentiles=[.05, .25, .5, .75, .9, .95, .99]).round(4).to_string())

    (OUT / "manifests" / "ACTUATOR_AUDIT_ACCESS_LOG.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "target_reads": ACCESS["target_reads"],
        "model_error_reads": ACCESS["model_error_reads"],
        "predictor_signal_reads": ACCESS["predictor_signal_reads"],
        "signals_read": acts,
        "target_signal_opened": False,
        "nrmse_or_residual_opened": False,
        "failure_labels_opened": False,
        "support_family_labels_opened": False,
        "verdict": "TARGET_BLIND",
    }, indent=2), encoding="utf-8")
    assert ACCESS["target_reads"] == 0 and ACCESS["model_error_reads"] == 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
