import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def test_time_unit_audit_documents_shift_units():
    d = json.loads((BASE / "outputs" / "time_unit_consistency.json").read_text(encoding="utf-8"))
    assert d["zscored_temporal_derivatives_invariant_under_global_time_rescale"] is True
    assert d["shifted_quotients_invariant_only_if_shift_rescaled"] is True
    df = pd.read_csv(BASE / "tables" / "time_unit_consistency.csv")
    assert (df["max_abs_diff_consistent_s"] < 1e-10).all()
    assert (df["max_abs_diff_inconsistent_s"] > 1e-6).all()
