"""The external PySINDy wrapper must be an INDEPENDENT code path.

Step 12 is only a meaningful control if the wrapper does not simply call the
SIR contract harness and declare equivalence. These tests enforce that
structurally (static import analysis) and dynamically (the harness modules are
never executed while the wrapper runs).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import numpy as np
import pytest

TCB = Path(__file__).resolve().parent.parent
WRAPPER = TCB / "pysindy" / "external_contract_wrapper" / "wrapper.py"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def test_wrapper_does_not_import_the_contract_harness():
    mods = _imported_modules(WRAPPER)
    offending = [m for m in mods if m.split(".")[0] == "sir_contract"]
    assert offending == [], (
        f"external wrapper imports the SIR contract harness: {offending}. "
        "Step 12 would be tautological."
    )


def test_wrapper_does_not_import_the_shared_engine():
    """`engine` carries the harness's own CV/selection helpers."""
    mods = _imported_modules(WRAPPER)
    assert "engine" not in mods, (
        "external wrapper imports `engine`, which contains the harness's "
        "grouped_cv and selection helpers; reimplement them independently."
    )


def test_wrapper_defines_its_own_selection_rules():
    src = WRAPPER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    fns = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for required in ("score", "choose_min", "choose_equivalent_then_simplest"):
        assert required in fns, f"wrapper must define its own {required}()"
    # the equivalence rule must be written here, not delegated
    assert "max(top[1][\"se\"], floor)" in src or "max(top[1]['se'], floor)" in src


def test_wrapper_runs_without_loading_the_harness():
    """Dynamic check: importing and using the wrapper must not pull in
    sir_contract."""
    for m in list(sys.modules):
        if m.startswith("sir_contract"):
            del sys.modules[m]
    sys.path.insert(0, str(WRAPPER.parent))
    import wrapper as W  # noqa: E402

    loaded = [m for m in sys.modules if m.startswith("sir_contract")]
    assert loaded == [], f"importing the wrapper loaded {loaded}"

    # exercise the independent selection rules on a synthetic score table
    scores = {
        "big":   {"mean": 1.00e-5, "se": 3e-7, "terms": 29, "cond": 1e16,
                  "n_coordinates": 38, "stability": 1e-6},
        "small": {"mean": 3.00e-5, "se": 4e-7, "terms": 12, "cond": 1e12,
                  "n_coordinates": 12, "stability": 2e-6},
    }
    assert W.choose_min(scores) == "big"
    win, pool, _ = W.choose_equivalent_then_simplest(
        scores, floor=1e-3,
        order=["n_coordinates", "n_terms", "condition_number", "fold_stability"])
    assert win == "small", "floor should make both equivalent, then prefer fewer coords"
    assert sorted(pool) == ["big", "small"]

    loaded = [m for m in sys.modules if m.startswith("sir_contract")]
    assert loaded == [], f"using the wrapper loaded {loaded}"


def test_wrapper_and_harness_agree_is_a_positive_result_not_an_assumption():
    """Documentation guard: the comparison must be computed, never assumed."""
    src = WRAPPER.read_text(encoding="utf-8")
    assert "does NOT import" in src or "deliberately does NOT import" in src
    assert "EXPECTED" in src, (
        "the wrapper should state that agreement with the harness is the "
        "expected, desirable outcome supporting the nesting interpretation"
    )
