"""Verify RESULTS/output.pcdiamag3.psir against canonical seven-term support."""
from __future__ import annotations

import pickle
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from dash_app.utils.discharge_validation import (  # noqa: E402
    D3D_RELATION,
    DischargeRecord,
    compute_discharge_metrics,
    compute_pooled_metrics,
    prepare_discharge_reconstruction_data,
    select_median_error_discharge,
)

PSIR = REPO / "RESULTS" / "output.pcdiamag3.psir"
EXPECTED_TERMS = list(D3D_RELATION["terms"].keys())
# Semantic package order (display) vs D3D_RELATION dict order may differ.
SEMANTIC_EXPORT_COLS = [
    "[d[pcdiamag3]/d[kappa]]",
    "[d[pcdiamag3]/d[betan]]",
    "[d[kappa]/d[betan]]",
    "[d[li]/d[betan]]",
    "[r[q95]/r[kappa]]",
    "[d[betan]/d[t]]",
    "[d[kappa]/d[t]]",
]


def parse_shot(name):
    m = re.search(r"shot[_\-]?(\d+)", str(name))
    return int(m.group(1)) if m else None


def main():
    with open(PSIR, "rb") as f:
        d = pickle.load(f)
    print("symbols", d.get("symbols"))
    print("outexpr", d.get("outexpr"))
    print("finalError", d.get("finalError"))
    print("eps", d.get("eps"))
    print("bestindex", d.get("bestindex"))

    for eq in ("1_8", "1_8*"):
        yhat_list = []
        y_list = []
        t_list = []
        shots = []
        coeffs = np.asarray(d[eq]["x"], dtype=np.float64)
        print(f"\n{eq} coeff shape", coeffs.shape)
        print(f"{eq} mean coeffs", coeffs.mean(axis=0))
        for i in range(62):
            C = coeffs[i].reshape(1, -1)
            X = np.asarray(d["O1_variables"][i], dtype=np.float64)
            # visualization.py: matmul C with X[:cshape[1]]
            yhat = np.matmul(C, X[: C.shape[1]]).reshape(-1)
            y = np.asarray(d["output"]["x"][i], dtype=np.float64).reshape(-1)
            t = np.asarray(d["timing"][i], dtype=np.float64).reshape(-1)
            yhat_list.append(yhat)
            y_list.append(y)
            t_list.append(t)
            shots.append(parse_shot(d["filenames"][i]))

        # Compare mean coeffs to D3D_RELATION (order may match design matrix order)
        print("D3D_RELATION intercept+terms",
              [D3D_RELATION["intercept"], *[D3D_RELATION["terms"][t] for t in D3D_RELATION["terms"]]])

        records = [
            DischargeRecord(i, t_list[i], y_list[i], yhat_list[i], shot=shots[i])
            for i in range(62)
        ]
        cleaned, counts = prepare_discharge_reconstruction_data(records)
        per = compute_discharge_metrics(cleaned)
        pooled = compute_pooled_metrics(cleaned, per)
        sel = select_median_error_discharge(per)
        print("counts", counts)
        print("pooled_rmse", pooled["pooled_rmse"])
        print("pooled_mse", pooled["pooled_rmse"] ** 2)
        print("selected", sel)

    # Check O1_variables row 0 against export columns — need term order from symbols
    # Often symbols lists variable names for the equation terms.
    print("\nrawvar", type(d.get("rawvar")), getattr(d.get("rawvar"), "shape", None))
    if "meanSTDinfo" in d:
        print("meanSTDinfo keys", d["meanSTDinfo"].keys() if isinstance(d["meanSTDinfo"], dict) else type(d["meanSTDinfo"]))


if __name__ == "__main__":
    main()
