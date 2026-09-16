import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def test_elimination_identity():
    v = json.loads((BASE / "outputs" / "elimination_identity_validation.json").read_text(encoding="utf-8"))
    assert v["pass"] is True
    assert v["max_identity_error"] <= 1e-10
    elim = pd.read_parquet(BASE / "outputs" / "eliminated_relation_rows.parquet")
    assert len(elim) == 62000
    err = (elim["A"] * elim["y_standardized"] - elim["B"] - elim["residual_original"]).abs().max()
    assert err <= 1e-10
