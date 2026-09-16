import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def test_shift_recovery_exact_from_psir():
    d = json.loads((BASE / "outputs" / "shift_recovery_diagnostics.json").read_text(encoding="utf-8"))
    assert d["status"] == "EXACT_FROM_SERIALIZED_STATE"
    df = pd.read_csv(BASE / "tables" / "recovered_shift_values.csv")
    assert len(df) == 62
    assert df["shiftval"].between(10, 30).all()
