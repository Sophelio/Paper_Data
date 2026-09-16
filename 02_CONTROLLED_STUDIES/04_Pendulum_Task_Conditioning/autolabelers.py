"""Autolabelers for the pendulum Dalia project (starter stub)."""
from __future__ import annotations


def autolabel_threshold(
    dataset_id, record_id, data_coordinator, additional_parameters,
    trim_1=None, trim_2=None,
):
    threshold = float(additional_parameters.get("threshold", 1.0))
    record = data_coordinator.fetch_data_async(
        data_coordinator.data_folder, dataset_id, record_id, ["theta"], {},
        trim_1=trim_1, trim_2=trim_2,
    )
    if not record.get("signals"):
        return []
    sig = record["signals"][0]
    values, times = sig["data"], sig["times"]
    labels, start = [], None
    for i, v in enumerate(values):
        if v > threshold and start is None:
            start = times[i]
        elif v < threshold and start is not None:
            row = {name: None for name in data_coordinator.all_labels}
            row["Event"] = True
            row["T1"] = start
            row["T2"] = times[i]
            labels.append(row)
            start = None
    return labels


def build_autolabelers() -> dict:
    return {
        "threshold_events": {
            "function": autolabel_threshold,
            "parameters": {"threshold": 1.0},
            "display_name": "Threshold Events",
        },
    }
