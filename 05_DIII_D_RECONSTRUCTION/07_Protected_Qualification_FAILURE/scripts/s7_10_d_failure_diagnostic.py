"""S7.10 step D - external failure-mode diagnostic. REPORTING ONLY.

Characterises WHY the frozen relational representation fails V3. It changes
nothing: no coordinate is removed, no threshold moved, no metric substituted, no
discharge deleted. C_dev_star and every comparator configuration are untouched.

The diagnostic exists because a mandatory gate failed and the failure must be
explained, not hidden.
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
sys.path.insert(0, str(EX))
import diiid_sir_data_provider as PROV  # noqa: E402

CANON = {"keV": 1e3, "km/s": 1e3, "cm^-3": 1e6, "ph/(sr cm^2 s)": 1e4, "kW": 1e3}
BLOCKS = [("A", 0.40, 0.50), ("B", 0.60, 0.70), ("C", 0.80, 0.90)]


def build(sv, atoms):
    out = []
    for a in atoms:
        h = a[:a.index("(")]
        ar = a[a.index("(") + 1:-1].split(",")
        v = sv[ar[0]]
        with np.errstate(divide="ignore", invalid="ignore"):
            out.append(v if h == "ID" else 1.0 / v if h == "RECIP"
                       else v * sv[ar[1]] if h == "PROD" else v / sv[ar[1]])
    return np.vstack(out)


def main() -> int:
    sel = json.loads((S7 / "09_development_selection_and_freeze"
                      / "SELECTED_REPRESENTATION.json").read_text())
    atoms = sel["canonical_coordinate_ids"]
    prims = sorted({p for c in sel["coordinates"] for p in c["primitive_ancestors"]})
    cons_of = {c["coordinate_id"]: c["constructor"] for c in sel["coordinates"]}
    TR = pd.read_csv(S7 / "04_mathematical_interpretation" / "retry_source_resolution_v2"
                     / "trajectory_index.csv", dtype={"discharge": str}).set_index("discharge")
    part = json.loads((S7 / "02_reconstruction_contract" / "COHORT_PARTITION.json").read_text())
    ext = [str(s) for s in part["external"]["shot_ids"]]
    dm = pd.read_csv(OUT / "external_discharge_metrics.csv").set_index("shot_id")
    dm.index = dm.index.astype(str)

    rows = []
    for s in ext:
        t0 = float(TR.loc[s, "t_start_s"]) * 1000.0
        dtm = float(TR.loc[s, "delta_t_ms"])
        n = int(TR.loc[s, "N_s"])
        grid = t0 + dtm * np.arange(n)
        with np.load(PROV._shot_npz_path(DATA, s), allow_pickle=False) as a:
            sv = {sig: PROV._resample_to_grid(*PROV._load_signal(a, sig), grid)
                  * CANON.get(str(PROV.SIGNAL_UNIT[sig]), 1.0) for sig in prims}
        X = build(sv, atoms)
        for bn, c1, c2 in BLOCKS:
            cal = slice(0, int(np.floor(n * c1)))
            pro = slice(int(np.floor(n * c1)), int(np.floor(n * c2)))
            xc, xp = X[:, cal], X[:, pro]
            mu = xc.mean(axis=1, keepdims=True)
            sd = xc.std(axis=1, ddof=0, keepdims=True)
            zp = np.abs((xp - mu) / np.where(sd <= 0, 1.0, sd))
            mx = zp.max(axis=1)
            k = int(np.argmax(mx))
            rows.append({
                "shot_id": s, "era": str(TR.loc[s, "processing_era"]), "block": bn,
                "max_abs_z_protected": float(mx.max()),
                "worst_coordinate": atoms[k],
                "worst_constructor": cons_of[atoms[k]],
                "mean_abs_z_protected": float(zp.mean()),
                "n_coordinates_above_10_sigma": int((mx > 10).sum()),
                "REL_nrmse_discharge": float(dm.loc[s, "REL_nrmse"]),
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "external_extrapolation_audit.csv", index=False)

    worst = df.groupby("shot_id").max_abs_z_protected.max()
    rel = dm.REL_nrmse
    common = worst.index.intersection(rel.index)
    corr = float(np.corrcoef(np.log10(worst[common]), np.log10(rel[common]))[0, 1])

    top = df.nlargest(6, "max_abs_z_protected")[
        ["shot_id", "era", "block", "max_abs_z_protected", "worst_coordinate",
         "REL_nrmse_discharge"]]
    counts = df.worst_coordinate.value_counts().to_dict()

    summary = {
        "record_id": "EXTERNAL_FAILURE_MODE_DIAGNOSTIC_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REPORTING_ONLY",
        "changes_C_dev_star": False,
        "removes_any_coordinate": False,
        "changes_any_threshold_metric_or_configuration": False,
        "deletes_any_discharge": False,
        "question": "why does the frozen relational representation fail V3 on the external cohort?",
        "finding": {
            "headline": ("the pooled failure is driven by unguarded LINEAR EXTRAPOLATION of the "
                         "self-product coordinate PROD(gasa,gasa) on two earlier-era discharges"),
            "mechanism": [
                "the frozen estimator fits affine OLS on the calibration interval only",
                "gasa (gas injection valve command, manifold A) undergoes a large excursion "
                "inside the protected window on discharges 187019 and 187022",
                "on 187019 block B, gasa spans 5.3e-3..4.1e-2 on calibration but reaches 1.63 "
                "on the protected block, a ~40x excursion beyond the calibration maximum",
                "squaring amplifies the excursion: PROD(gasa,gasa) reaches ~8979 calibration "
                "standard deviations on the protected rows",
                "the affine relation extrapolates linearly on that coordinate and the prediction "
                "diverges",
            ],
            "why_the_frozen_domain_rule_did_not_catch_it": (
                "DENOMINATOR_ADMISSIBILITY_PRIMARY_V1 guards DENOMINATORS only. Per the frozen "
                "S7.6R partial-map policy, 'C0, C1, C2 and C6 have no denominator and no gate'. "
                "PROD(gasa,gasa) is a C2 self-product, so it carries no domain gate at all. All "
                "three required denominators (prmtan_neped, ece22, cerqtit10) were admissible on "
                "every one of the 126 external calibration blocks, and remain well-conditioned on "
                "the protected intervals too. The failure is an unguarded RANGE excursion in a "
                "product coordinate, not a denominator failure."),
            "not_a_domain_rule_violation": True,
            "not_a_leakage_failure": True,
            "not_an_implementation_error": True,
        },
        "extrapolation_vs_error": {
            "spearman_style_log_correlation": corr,
            "note": "log10 max standardized protected excursion vs log10 discharge REL NRMSE",
        },
        "worst_blocks": top.to_dict(orient="records"),
        "worst_coordinate_frequency": counts,
        "distribution_context": {
            "REL_median_external_nrmse": float(rel.median()),
            "REL_mean_external_nrmse": float(rel.mean()),
            "development_FIT": 0.166397565,
            "n_discharges_above_nrmse_1": int((rel > 1).sum()),
            "n_discharges_above_nrmse_2": int((rel > 2).sum()),
            "reading": ("on 40 of 42 external discharges the frozen representation transfers at "
                        "roughly its development level; two discharges are catastrophic and they "
                        "dominate the mean, which is the quantity the frozen V3 gate uses"),
            "the_gate_uses_the_mean": True,
            "median_may_not_be_substituted_for_the_mean": True,
        },
        "consequence": (
            "V3 fails on the frozen mean-based rule and the failure is robust: no single "
            "leave-one-discharge-out cohort satisfies V3. The result stands as frozen."),
        "motivates_but_does_not_execute": [
            "S7.11 V9 sensitivity",
            "any future prospective range-admissibility rule for non-denominator constructors, "
            "which would be a NEW contract decision for a future study, not a repair of this one",
        ],
    }
    (OUT / "manifests" / "EXTERNAL_FAILURE_MODE_DIAGNOSTIC.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    print("worst blocks by protected standardized excursion:")
    print(top.to_string(index=False))
    print("\nworst-coordinate frequency across 126 blocks:")
    for k, v in counts.items():
        print("   %-36s %d" % (k, v))
    print("\nlog-log correlation (excursion vs REL error): %.3f" % corr)
    print("REL median %.4f  mean %.4f  (development FIT 0.166398)"
          % (rel.median(), rel.mean()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
