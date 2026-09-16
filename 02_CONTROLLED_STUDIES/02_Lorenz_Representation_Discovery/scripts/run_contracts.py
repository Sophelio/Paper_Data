"""Steps 8-10 — execute q_accuracy, q_compact, q_robust through the SIR
contract harness, on DEVELOPMENT data only.

The harness (``sir_contract/``) is a benchmark-local reference implementation of
the SIR framework's contract layer. It is NOT MCP-native SIR: the current SIR
MCP exposes SIR primitives but not discovery contracts, grouped held-out
validation, task utilities or qualified-model sets. PySINDy STLSQ is used
openly as the relation solver R_q(C) inside the contract.

Writes contract selections, the equivalence-floor sensitivity sweep, and
PRECONFIRMATION_FREEZE.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TCB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TCB))
sys.path.insert(0, str(TCB / "scripts"))
import engine as E  # noqa: E402
from sir_contract import SIR_IMPLEMENTATION_STATUS  # noqa: E402
from sir_contract import qualification as QUAL  # noqa: E402
from sir_contract.contract_runner import (  # noqa: E402
    build_contract, build_object, run_contract, score_candidates,
)

CFG = E.CFG
FLOOR = float(CFG["equivalence"]["practical_equivalence_abs"])


def main() -> None:
    print(f"SIR_IMPLEMENTATION_STATUS = {SIR_IMPLEMENTATION_STATUS}\n")

    print("scoring candidates — CLEAN object")
    clean = score_candidates([0.0], [None])

    print("\nscoring candidates — NOISY object (worst case over envelope)")
    env = CFG["noise"]["envelope"]
    robust = score_candidates(env, CFG["noise"]["development_seeds"])

    obj_clean = build_object("O_clean", 0.0)
    obj_noisy = build_object("O_noisy", max(env))

    specs = {
        "q_accuracy": (build_contract("q_accuracy", "minimum clean "
                                      "reconstruction error", [0.0]),
                       obj_clean, clean),
        "q_compact": (build_contract("q_compact", "simplest well-conditioned "
                                     "accuracy-equivalent representation", [0.0]),
                      obj_clean, clean),
        "q_robust": (build_contract("q_robust", "representation that remains "
                                    "useful under observational uncertainty", env),
                     obj_noisy, robust),
    }

    selections = {}
    for q, (contract, obj, scored) in specs.items():
        res = run_contract(contract, obj, scored)
        selections[q] = res
        info = res["selection_info"]
        print(f"\n{q}: {res['selected_candidate']}  "
              f"({res['n_coordinates']} coords, {res['n_features']} features, "
              f"{res['n_terms']:.0f} terms)")
        print(f"   utility={res['mean_cv_utility']:.5g} "
              f"+/- {res['se_cv_utility']:.2g}   cond={res['condition_number']:.3g}")
        print(f"   equivalent set ({info.get('n_equivalent', 1)}): "
              f"{info['equivalent_set'][:8]}")
        if "margin_source" in info:
            print(f"   margin={info['margin_used']:.3g} "
                  f"(from {info['margin_source']})")

    # ---- equivalence-floor sensitivity sweep (development only) ------------
    sweep = []
    for f in [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]:
        for label, table, lex in (
            ("q_compact", clean, CFG["contracts"]["q_compact"]["lexicographic"]),
            ("q_robust", robust, CFG["contracts"]["q_robust"]["lexicographic"]),
        ):
            pick, info = QUAL.qualified_model_set(
                table, practical_floor=f, lexicographic=tuple(lex))
            sweep.append({"contract": label, "floor": f, "selected": pick,
                          "n_equivalent": info["n_equivalent"],
                          "margin_source": info["margin_source"]})
    pd.DataFrame(sweep).to_csv(TCB / "tables" / "equivalence_sensitivity.csv",
                               index=False)
    print("\nequivalence-floor sensitivity (development only):")
    for r in sweep:
        print(f"  {r['contract']:11s} floor={r['floor']:.0e} -> "
              f"{r['selected']:20s} (|equiv|={r['n_equivalent']})")

    # ---- development scoring table ----------------------------------------
    rows = []
    for label, table in (("clean", clean), ("robust_worstcase", robust)):
        for nm, r in table.items():
            rows.append({"regime": label, "candidate": nm,
                         "n_coordinates": r.n_coordinates,
                         "n_features": r.n_features,
                         "mean_cv_rmse": r.mean_rmse, "se_cv_rmse": r.se_rmse,
                         "n_terms": r.n_terms, "condition_number": r.cond,
                         "coverage": r.coverage,
                         "fold_std": float(np.std(r.fold_rmse))})
    pd.DataFrame(rows).to_csv(TCB / "tables" / "selection_stability.csv",
                              index=False)

    (TCB / "contracts" / "contract_selections.json").write_text(
        json.dumps(selections, indent=2), encoding="utf-8")

    # ---- preconfirmation freeze -------------------------------------------
    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    files = [
        TCB / "benchmark_config.yaml",
        TCB / "scripts" / "engine.py",
        TCB / "scripts" / "run_contracts.py",
        TCB / "contracts" / "contract_selections.json",
        TCB / "shared" / "manifests" / "confirmation_lineage.json",
        TCB / "sir_contract" / "contract_runner.py",
        TCB / "sir_contract" / "qualification.py",
        TCB / "sir_contract" / "validation.py",
        TCB / "sir_contract" / "candidate_registry.py",
        TCB / "sir_contract" / "scientific_object.py",
        TCB / "sir_contract" / "discovery_contract.py",
        TCB / "pysindy" / "external_contract_wrapper" / "wrapper.py",
    ]
    freeze = {
        "sir_implementation_status": SIR_IMPLEMENTATION_STATUS,
        "note": "The confirmation evaluator refuses to run if any hash below "
                "no longer matches.",
        "selections": {q: selections[q]["selected_candidate"] for q in selections},
        "practical_equivalence_abs": FLOOR,
        "files": {str(p.relative_to(TCB)).replace("\\", "/"): sha(p)
                  for p in files if p.exists()},
    }
    (TCB / "PRECONFIRMATION_FREEZE.json").write_text(
        json.dumps(freeze, indent=2), encoding="utf-8")
    print(f"\nfroze {len(freeze['files'])} files into PRECONFIRMATION_FREEZE.json")


if __name__ == "__main__":
    main()
