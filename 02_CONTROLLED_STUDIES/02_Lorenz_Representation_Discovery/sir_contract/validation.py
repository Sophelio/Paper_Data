"""V_q — grouped held-out validation.

The statistical unit is the TRAJECTORY. GroupKFold over trajectories; every
fit-dependent coordinate parameter is refitted inside each training fold, so a
fold's validation trajectories never inform its own transforms.
"""

from __future__ import annotations

import sys
from pathlib import Path

TCB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TCB / "scripts"))
import engine as _E  # noqa: E402


def grouped_cv(recs, cols, family, thresholds, n_folds):
    """Return a CVResult: per-fold RMSE, mean, SE, complexity, conditioning."""
    return _E.grouped_cv(recs, cols, family, thresholds, n_folds)
