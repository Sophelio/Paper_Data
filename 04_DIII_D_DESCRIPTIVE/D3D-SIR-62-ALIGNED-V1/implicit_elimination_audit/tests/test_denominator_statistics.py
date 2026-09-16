from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def test_denominator_tables_complete():
    den = pd.read_csv(BASE / "tables" / "primitive_denominator_per_discharge.csv")
    assert den["realization_index"].nunique() == 62
    assert den["denominator"].nunique() >= 5
    assert (den["n_nonfinite"] == 0).all()
