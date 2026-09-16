"""U_q and the qualified-model set.

Two rules, both declared before the freeze:

  * ``select_min``          — pure minimum utility (q_accuracy).
  * ``qualified_model_set`` — accuracy-equivalence followed by a lexicographic
                              preference hierarchy (q_compact, q_robust).

Equivalence threshold
---------------------
    best + max( SE(best), practical_equivalence_abs )

The plain one-standard-error rule degenerates on this problem: across six folds
of a near-exact fit the standard error is ~3e-7, so ``best + SE`` admits only
the single best candidate and the compact contract collapses onto the accuracy
contract by construction — the comparison the benchmark exists to make becomes
impossible to observe.

The floor restores the intended meaning by tying practical equivalence to the
declared resolution of the SCIENTIFIC OBJECT (E) rather than to fold noise. With
sigma_z ~ 9.04, a reconstruction difference below 1e-3 is ~1e-4 of the target's
own scale and is not scientifically resolvable. See
``audit/EQUIVALENCE_RULE_AUDIT.md`` for the justification and the sensitivity
sweep showing the selection is stable across two decades of the floor.
"""

from __future__ import annotations

import numpy as np

LEXICOGRAPHIC_KEYS = {
    "n_coordinates": lambda r: r.n_coordinates,
    "n_terms": lambda r: r.n_terms,
    "condition_number": lambda r: r.cond,
    "fold_stability": lambda r: float(np.std(r.fold_rmse)),
}


def select_min(results: dict, key: str = "mean_rmse"):
    """U_q = minimise the scored utility. No secondary preference."""
    best = min(results, key=lambda k: getattr(results[k], key))
    return best, {
        "rule": f"min {key}",
        "best_by_utility": best,
        "equivalent_set": [best],
        "threshold": float(getattr(results[best], key)),
    }


def qualified_model_set(results: dict, *, key: str = "mean_rmse",
                        practical_floor: float = 0.0,
                        lexicographic: tuple = ()):
    """Accuracy-equivalent set, then lexicographic preference."""
    best = min(results, key=lambda k: getattr(results[k], key))
    se = results[best].se_rmse
    margin = max(float(se), float(practical_floor))
    thr = float(getattr(results[best], key)) + margin
    equiv = [k for k in results if getattr(results[k], key) <= thr]

    keys = [LEXICOGRAPHIC_KEYS[k] for k in lexicographic]
    ranked = sorted(equiv, key=lambda k: tuple(f(results[k]) for f in keys))
    return ranked[0], {
        "rule": "one-SE-or-practical-floor, then lexicographic "
                f"{list(lexicographic)}",
        "best_by_utility": best,
        "se_best": float(se),
        "practical_floor": float(practical_floor),
        "margin_used": margin,
        "margin_source": "SE" if se >= practical_floor else "practical_floor",
        "threshold": thr,
        "equivalent_set": ranked,
        "n_equivalent": len(ranked),
    }
