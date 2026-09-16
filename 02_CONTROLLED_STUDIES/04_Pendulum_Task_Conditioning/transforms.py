"""Custom transform blocks for the pendulum provider."""
from __future__ import annotations

import numpy as np


def absolute_block(times, values, params, context):
    return times, np.abs(np.asarray(values, dtype=float))


def build_transforms() -> dict:
    return {
        "absolute": {
            "display_name": "Absolute Value",
            "category": "custom",
            "parameters": {},
            "function": absolute_block,
        },
    }
