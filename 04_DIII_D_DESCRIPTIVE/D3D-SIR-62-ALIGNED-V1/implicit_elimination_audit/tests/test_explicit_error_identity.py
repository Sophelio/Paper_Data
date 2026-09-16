import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def test_explicit_error_equals_residual_over_A():
    v = json.loads((BASE / "outputs" / "elimination_identity_validation.json").read_text(encoding="utf-8"))
    # Near-zero A amplifies float noise; allow a slightly relaxed tolerance.
    assert v["explicit_error_identity_max"] <= 5e-8
    elim = pd.read_parquet(BASE / "outputs" / "eliminated_relation_rows.parquet")
    A = elim["A"].to_numpy(np.float64)
    m = np.isfinite(elim["explicit_error"]) & (np.abs(A) > 1e-8)
    lhs = elim.loc[m, "explicit_error"].to_numpy(np.float64)
    rhs = elim.loc[m, "residual_original"].to_numpy(np.float64) / A[m]
    assert np.max(np.abs(lhs - rhs)) <= 5e-8
