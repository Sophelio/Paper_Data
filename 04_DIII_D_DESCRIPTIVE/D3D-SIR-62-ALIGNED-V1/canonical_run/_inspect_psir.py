"""Inspect candidate .psir files for 62-shot pcdiamag3 support (audit only)."""
from __future__ import annotations

import hashlib
import pickle
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
CANDIDATES = [
    REPO / "RESULTS" / "output.pcdiamag3.psir",
    REPO / "dash_app" / "callbacks" / "RESULTS" / "output.ip.psir",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    for p in CANDIDATES:
        print("=" * 60)
        print(p)
        if not p.exists():
            print("MISSING")
            continue
        print("size", p.stat().st_size, "sha256", sha256(p))
        with open(p, "rb") as f:
            d = pickle.load(f)
        print("type", type(d))
        if not isinstance(d, dict):
            continue
        keys = list(d.keys())
        print("n_keys", len(keys))
        print("keys_sample", keys[:30])
        fn = d.get("filenames")
        print("filenames", None if fn is None else len(fn), (fn or [])[:2])
        out = d.get("output")
        if isinstance(out, dict) and "x" in out:
            x = out["x"]
            print("output.x type", type(x), "len", len(x) if hasattr(x, "__len__") else None)
            if len(x):
                print("output.x[0] shape", np.asarray(x[0]).shape)
        eqs = [k for k in keys if isinstance(k, str) and "_" in k and not k.startswith("O")]
        print("eq_keys", eqs)
        for k in eqs:
            v = d[k]
            if isinstance(v, dict) and "x" in v:
                xa = np.asarray(v["x"])
                print(f"  {k}: coeff shape {xa.shape}")
        for ok in sorted(k for k in keys if isinstance(k, str) and k.startswith("O") and "variables" in k):
            arr = d[ok]
            print(ok, "len", len(arr) if hasattr(arr, "__len__") else None)
            if hasattr(arr, "__len__") and len(arr):
                print("  [0] shape", np.asarray(arr[0]).shape)


if __name__ == "__main__":
    main()
