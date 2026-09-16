"""Adversarial target-ancestry / leakage audit for the q_rec density branch.

Mirrors the test that retired the previous I_p branch (q95 was essentially
shape*a^2*Bt/I_p: median |corr| 0.945 with 1/Ip, 7.3% residual scatter,
Ip recoverable at median R^2 = 0.79).

Applied here to every admitted predictor against the target `density`, with
particular attention to prmtan_neped, which appears in all six qualified fold
supports and in C_E2_ALL_DESC. READ ONLY.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

S7 = Path(r"D:\SIR_paper\DIIID_example\S7")
EX = S7.parent
DATA = EX / "data" / "resampled_data_v6"
sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV

RV2 = S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
S73 = S7 / "03_target_feasibility_and_boundary" / "reconciliation_source_resolution"
E20 = S7 / "E2_0_protocol_and_resampling_freeze"
CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
TARGET = "density"

b = pd.read_csv(S73 / "corrected_selected_target_boundary.csv")
P78 = sorted(b[b.include_primary == True].signal.tolist())
fa = pd.read_csv(E20 / "outer_fold_assignment.csv", dtype={"discharge": str})
shots = list(fa.sort_values("position").discharge)
TR = pd.read_csv(RV2 / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")

per = {p: {"corr": [], "r2_target_from_p": [], "r2_p_from_target": [],
           "rel_resid": []} for p in P78}
for s in shots:
    t0 = float(TR.loc[s, "t_start_s"]) * 1000.0
    dtm = float(TR.loc[s, "delta_t_ms"]); n = int(TR.loc[s, "N_s"])
    grid = t0 + dtm * np.arange(n, dtype=np.float64)
    with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
        tt, vv = PROV._load_signal(a, TARGET)
        y = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
            str(PROV.SIGNAL_UNIT[TARGET]), 1.0)
        X = {}
        for sig in P78:
            tt, vv = PROV._load_signal(a, sig)
            X[sig] = PROV._resample_to_grid(tt, vv, grid) * CANON.get(
                str(PROV.SIGNAL_UNIT[sig]), 1.0)
    yv = np.var(y)
    for sig, x in X.items():
        if not np.isfinite(x).all() or np.var(x) == 0 or yv == 0:
            continue
        c = float(np.corrcoef(x, y)[0, 1])
        per[sig]["corr"].append(abs(c))
        # affine fit both directions -> R^2 = corr^2 for simple linear regression
        per[sig]["r2_target_from_p"].append(c * c)
        per[sig]["r2_p_from_target"].append(c * c)
        # relative residual scatter of the target after removing the best
        # per-shot affine function of this predictor
        A = np.column_stack([np.ones(n), x])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        r = y - A @ beta
        per[sig]["rel_resid"].append(float(np.std(r) / np.std(y)))

rows = []
for sig in P78:
    if not per[sig]["corr"]:
        continue
    rows.append({
        "signal": sig,
        "median_abs_corr_with_target": float(np.median(per[sig]["corr"])),
        "max_abs_corr_with_target": float(np.max(per[sig]["corr"])),
        "median_R2_target_from_signal": float(np.median(per[sig]["r2_target_from_p"])),
        "n_shots_R2_gt_0.9": int(sum(1 for v in per[sig]["r2_target_from_p"] if v > 0.9)),
        "median_rel_residual_scatter": float(np.median(per[sig]["rel_resid"])),
        "family": str(b[b.signal == sig].family.iloc[0]),
        "provenance_status": str(b[b.signal == sig].provenance_status.iloc[0]),
    })
df = pd.DataFrame(rows).sort_values("median_R2_target_from_signal", ascending=False)

print("=== worst 12 predictors by single-signal explanatory power for `density` ===")
print(df.head(12).to_string(index=False))
print()
print("=== prmtan_neped (present in all six qualified fold supports) ===")
print(df[df.signal == "prmtan_neped"].to_string(index=False))
print()
BENCH = {"q95_vs_Ip_median_R2": 0.79, "q95_residual_scatter": 0.073,
         "q95_median_abs_corr": 0.945, "q95_n_shots_R2_gt_0.9": 15}
print("=== retired I_p-branch benchmark that triggered retirement ===")
print(BENCH)
print()
pn = df[df.signal == "prmtan_neped"].iloc[0]
verdict = ("ALGEBRAIC_CIRCULARITY_RISK" if pn.median_R2_target_from_signal >= 0.75
           or pn.median_rel_residual_scatter <= 0.15 else "NO_ALGEBRAIC_CIRCULARITY")
print("prmtan_neped verdict:", verdict)
print("  median R^2 %.4f (q95/Ip was 0.79) | residual scatter %.4f (q95/Ip was 0.073)"
      % (pn.median_R2_target_from_signal, pn.median_rel_residual_scatter))
worst = df.iloc[0]
print("  worst predictor overall: %s R^2 %.4f scatter %.4f"
      % (worst.signal, worst.median_R2_target_from_signal, worst.median_rel_residual_scatter))
n_risky = int((df.median_R2_target_from_signal >= 0.75).sum())
print("  predictors with median R^2 >= 0.75 against the target: %d of %d" % (n_risky, len(df)))

# is the target itself excluded, and are density descendants excluded?
excluded = b[b.include_primary == False]
print("\n=== excluded signals (%d) ===" % len(excluded))
print(excluded[["signal", "exclusion_rule", "exclusion_reason"]].to_string(index=False))

df.to_csv(sys.argv[1], index=False)
json.dump({"benchmark": BENCH, "prmtan_neped_verdict": verdict,
           "n_predictors_R2_ge_0.75": n_risky, "n_predictors": len(df)},
          open(sys.argv[2], "w", encoding="utf-8"), indent=1)
