"""Orchestration: run a DiscoveryContract against a ScientificObject.

    O + K_q
      -> admissible coordinates (registry; MCP-native where exposed)
      -> candidate representation scoring
      -> PySINDy STLSQ as one relation solver R_q(C)
      -> grouped trajectory validation V_q
      -> task utility U_q + admissibility A
      -> qualified representation

PySINDy is used openly and deliberately as the relation solver inside the
contract; that embedding is the point, not something to disguise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

TCB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TCB / "scripts"))
sys.path.insert(0, str(TCB))
import engine as E  # noqa: E402
from sir_contract import candidate_registry as CR  # noqa: E402
from sir_contract import qualification as QUAL  # noqa: E402
from sir_contract import validation as VAL  # noqa: E402
from sir_contract.discovery_contract import DiscoveryContract  # noqa: E402
from sir_contract.scientific_object import (  # noqa: E402
    Admissibility, ScientificObject, UncertaintyModel,
)

CFG = E.CFG


# ---------------------------------------------------------------------------
# Object construction
# ---------------------------------------------------------------------------
def build_object(name: str, sigma_relative: float) -> ScientificObject:
    ib = CFG["information_boundary"]
    return ScientificObject(
        name=name,
        channels=("x", "y", "z"),
        support=f"{len(E.dev_ids())} development trajectories, "
                f"t in [0,{CFG['confirmation']['tmax']}], "
                f"dt={CFG['confirmation']['dt']}",
        sampling={
            "dt": CFG["confirmation"]["dt"],
            "stencil": ib["stencil"],
            "half_width": ib["half_width"],
            "group": "trajectory",
        },
        uncertainty=UncertaintyModel(
            kind="numerical" if sigma_relative == 0 else "observational_gaussian",
            sigma_relative=sigma_relative,
            applied_before_coordinates=True,
            note="noise added to x,y before differentiation, smoothing, "
                 "quotient and phase construction, and normalisation",
        ),
        provenance={
            "generator": CFG["system"]["generator"],
            "sigma": CFG["system"]["sigma"], "rho": CFG["system"]["rho"],
            "beta": CFG["system"]["beta"],
            "integrator": CFG["system"]["integrator"],
            "coordinate_provenance": CR.COORDINATE_PROVENANCE,
        },
        admissibility=Admissibility(
            observed=tuple(CFG["task"]["observed"]),
            target=CFG["task"]["target"],
            forbidden=tuple(CFG["task"]["forbidden_dependencies"]),
            retrospective_history=True,
        ),
    )


def build_contract(name: str, utility: str, sigma_env) -> DiscoveryContract:
    c = CFG["contracts"][name]
    return DiscoveryContract(
        name=name,
        question=utility,
        information_boundary=dict(CFG["information_boundary"]),
        candidate_space="candidate_registry.registry()",
        relation_families=("identity", "poly2", "poly3"),
        utility=c["utility"],
        validation={"scheme": CFG["cross_validation"]["scheme"],
                    "n_folds": CFG["cross_validation"]["n_folds"],
                    "group": "trajectory",
                    "noise_envelope": list(sigma_env)},
        support="48 exposed development trajectories",
        equivalence=dict(CFG.get("equivalence", {})),
        lexicographic=tuple(c.get("lexicographic", ())),
    )


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score_candidates(sigma_env, seeds, verbose=True) -> dict:
    """Score every registry candidate; worst case over the noise envelope."""
    import features as F  # noqa: E402
    reg = CR.registry()
    thresholds = CFG["estimators"]["stlsq"]["thresholds"]
    nfolds = CFG["cross_validation"]["n_folds"]
    per = {}
    for lvl in sigma_env:
        for sd in (seeds if lvl > 0 else [None]):
            recs0 = E.build(E.load_split("development", noise=lvl, seed=sd), None)
            fit = F.fit_coordinates([r["base"] for r in recs0], CFG)
            recs = E.build(E.load_split("development", noise=lvl, seed=sd), fit)
            for nm, (cols, fam) in reg.items():
                per.setdefault(nm, []).append(
                    VAL.grouped_cv(recs, cols, fam, thresholds, nfolds))
            if verbose:
                print(f"    sigma={lvl} seed={sd}: {len(reg)} candidates")
    out = {}
    for nm, rs in per.items():
        worst = max(rs, key=lambda r: r.mean_rmse)
        base = rs[0]
        out[nm] = E.CVResult(
            name=nm, fold_rmse=worst.fold_rmse, mean_rmse=worst.mean_rmse,
            se_rmse=worst.se_rmse, n_coordinates=base.n_coordinates,
            n_features=base.n_features, n_terms=base.n_terms,
            cond=base.cond, coverage=base.coverage)
    return out


# ---------------------------------------------------------------------------
# Contract execution
# ---------------------------------------------------------------------------
def run_contract(contract: DiscoveryContract, obj: ScientificObject,
                 scored: dict) -> dict:
    """Apply A, then U_q, then the qualified-model set."""
    deps = CR.dependencies()
    reg = CR.registry()
    violations = obj.assert_admissible(deps)
    if violations:
        raise ValueError(f"admissibility violated by: {violations}")

    floor = float(contract.equivalence.get("practical_equivalence_abs", 0.0))
    if contract.name == "q_accuracy":
        pick, info = QUAL.select_min(scored)
    else:
        pick, info = QUAL.qualified_model_set(
            scored, practical_floor=floor,
            lexicographic=contract.lexicographic)

    cols, fam = reg[pick]
    r = scored[pick]
    return {
        "contract": contract.as_dict(),
        "scientific_object": obj.as_dict(),
        "admissibility_violations": violations,
        "selected_candidate": pick,
        "coordinates": cols,
        "relation_family": fam,
        "n_coordinates": r.n_coordinates,
        "n_features": r.n_features,
        "n_terms": r.n_terms,
        "condition_number": r.cond,
        "coverage": r.coverage,
        "mean_cv_utility": r.mean_rmse,
        "se_cv_utility": r.se_rmse,
        "fold_rmse": r.fold_rmse,
        "fold_stability": float(np.std(r.fold_rmse)),
        "selection_info": info,
    }
