import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def test_A_summary_and_crossings():
    A = json.loads((BASE / "outputs" / "eliminated_A_summary.json").read_text(encoding="utf-8"))
    assert A["min_abs_pooled"] > 0
    assert A["n_sign_crossings"] >= 0
    per = pd.read_csv(BASE / "tables" / "eliminated_A_per_discharge.csv")
    assert len(per) == 62
    assert (per["min_abs_A"] > 0).all()
