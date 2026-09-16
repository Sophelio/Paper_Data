import json
import sys
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from implicit_elimination_utils import alpha_beta_yphaseder, reconstruct_yphaseder


def test_synthetic_affine_formula():
    rng = np.random.default_rng(20260805)
    d = rng.normal(size=200)
    s, mu, sig = 3.5, 1.2, 0.8
    alpha, beta = alpha_beta_yphaseder(d, s, mu, sig)
    for y in (-1.0, 0.0, 1.0, 0.37):
        z = reconstruct_yphaseder(np.full(200, y), d, s, mu, sig)
        assert np.allclose(z, alpha * y + beta, atol=1e-12)
    z1 = reconstruct_yphaseder(np.ones(200), d, s, mu, sig)
    z0 = reconstruct_yphaseder(np.zeros(200), d, s, mu, sig)
    zm = reconstruct_yphaseder(-np.ones(200), d, s, mu, sig)
    assert np.max(np.abs(z1 - 2 * z0 + zm)) < 1e-12


def test_audit_affine_flag():
    dep = json.loads((BASE / "outputs" / "target_dependence.json").read_text(encoding="utf-8"))
    assert dep["n_target_containing_features"] == 2
    assert dep["affine_verified"] is True
