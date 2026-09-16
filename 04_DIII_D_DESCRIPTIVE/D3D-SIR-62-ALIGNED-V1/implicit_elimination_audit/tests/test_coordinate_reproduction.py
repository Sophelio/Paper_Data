import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def test_all_features_exactly_reproduced():
    df = pd.read_csv(BASE / "tables" / "feature_reproduction_summary.csv")
    assert len(df) == 7
    assert (df["max_abs_diff"] <= 1e-10).all()
    assert set(df["status"]) == {"EXACTLY_REPRODUCED"}
