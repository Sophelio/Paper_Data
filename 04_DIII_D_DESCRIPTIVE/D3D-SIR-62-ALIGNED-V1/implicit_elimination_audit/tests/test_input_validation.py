import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def test_input_validation_pass():
    val = json.loads((BASE / "outputs" / "input_validation.json").read_text(encoding="utf-8"))
    assert val["pass"] is True
    assert abs(val["reproduced_pooled_rmse"] - 0.05758467247445343) <= 1e-8
    assert abs(val["reproduced_mean_vector_rmse"] - 0.4125238315775986) <= 1e-8
    assert not (BASE / "outputs" / "INPUT_CONTRADICTION_REPORT.txt").exists()
