"""Step 5 — containment: canonical PySINDy Lorenz recovery vs restricted SIR.

Both estimators receive:
  * the same full state (x, y, z) on the same time grid;
  * the SAME derivative estimates (supplied explicitly, so differentiation is
    not confounded with sparse fitting);
  * the same cubic polynomial library;
  * the same recorded sparse settings.

The purpose is to show the conventional discovery problem is CONTAINED in a
restricted SIR contract — not to force numerical identity, and not to claim a
win for either side.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from pysindy import SINDy
from pysindy.feature_library import PolynomialLibrary
from pysindy.optimizers import STLSQ

BENCH = Path(__file__).resolve().parent.parent
CFG = yaml.safe_load((BENCH / "benchmark_config.yaml").read_text(encoding="utf-8"))

OUT_PY = BENCH / "pysindy" / "containment"
OUT_SIR = BENCH / "sir" / "containment"
for d in (OUT_PY, OUT_SIR):
    d.mkdir(parents=True, exist_ok=True)

TRUE = CFG["containment"]["true_terms"]
FEATS = ["x", "y", "z"]


def load() -> tuple[np.ndarray, np.ndarray, float]:
    df = pd.read_parquet(BENCH / "shared" / "data" / "containment.parquet")
    X = df[["x", "y", "z"]].to_numpy(dtype=np.float64)
    dX = df[["dx", "dy", "dz"]].to_numpy(dtype=np.float64)  # exact derivatives
    dt = float(df["times"].iloc[1] - df["times"].iloc[0])
    return X, dX, dt


def cubic_terms() -> list[str]:
    """Names of the degree-3 polynomial library in PySINDy's own order."""
    lib = PolynomialLibrary(degree=3, include_bias=True)
    lib.fit(np.zeros((2, 3)))
    return list(lib.get_feature_names(FEATS))


def canonical_support() -> dict:
    """Ground-truth coefficient vector per equation, keyed by term name."""
    alias = {"x z": "x z", "x y": "x y"}
    out = {}
    for eq, terms in TRUE.items():
        out[eq] = {alias.get(k, k): float(v) for k, v in terms.items()}
    return out


def score(recovered: dict, truth: dict, tol: float = 1e-6) -> dict:
    """Support and coefficient agreement against the known Lorenz generator."""
    res = {}
    for eq in truth:
        got = {k: v for k, v in recovered[eq].items() if abs(v) > tol}
        want = truth[eq]
        fp = sorted(set(got) - set(want))
        fn = sorted(set(want) - set(got))
        common = sorted(set(got) & set(want))
        errs = {k: abs(got[k] - want[k]) for k in common}
        res[eq] = {
            "recovered": {k: float(v) for k, v in sorted(got.items())},
            "false_positives": fp,
            "false_negatives": fn,
            "max_coeff_error": float(max(errs.values())) if errs else 0.0,
            "rms_coeff_error": float(
                np.sqrt(np.mean(np.square(list(errs.values())))) if errs else 0.0
            ),
            "support_exact": (not fp) and (not fn),
        }
    return res


def run_pysindy(X, dX, dt, threshold) -> dict:
    model = SINDy(
        feature_library=PolynomialLibrary(degree=3, include_bias=True),
        optimizer=STLSQ(threshold=threshold, alpha=CFG["estimators"]["stlsq"]["alpha"]),
    )
    # x_dot supplied explicitly so differentiation is not part of the comparison.
    model.fit(X, dt, x_dot=dX, feature_names=FEATS)
    names = list(model.get_feature_names())
    coefs = np.asarray(model.coefficients(), dtype=np.float64)
    return {
        eq: dict(zip(names, coefs[i].tolist()))
        for i, eq in enumerate(("dx", "dy", "dz"))
    }


def run_restricted_sir(X, dX, threshold) -> dict:
    """Restricted SIR contract: identical library, identical derivatives,
    identical sparsity rule, solved as an explicit sparse linear relation.

    This is SIR restricted to exactly the SINDy representation — same source
    variables, same polynomial degree, same allowed terms, same coefficient
    model, same thresholding. It is implemented directly (rather than through
    the SIR MCP) because the MCP's SIR engine could not be reached for this
    project; see audit/SIR_MCP_CAPABILITY_AUDIT.md.
    """
    lib = PolynomialLibrary(degree=3, include_bias=True)
    Theta = lib.fit_transform(X)
    names = list(lib.get_feature_names(FEATS))

    out = {}
    for i, eq in enumerate(("dx", "dy", "dz")):
        y = dX[:, i]
        # Sequentially thresholded least squares — the same rule STLSQ applies.
        keep = np.ones(Theta.shape[1], dtype=bool)
        xi = np.zeros(Theta.shape[1])
        for _ in range(CFG["estimators"]["stlsq"]["max_iter"]):
            xi = np.zeros(Theta.shape[1])
            if keep.any():
                sol, *_ = np.linalg.lstsq(Theta[:, keep], y, rcond=None)
                xi[keep] = sol
            new_keep = np.abs(xi) >= threshold
            if np.array_equal(new_keep, keep):
                break
            keep = new_keep
        out[eq] = dict(zip(names, xi.tolist()))
    return out


def main() -> None:
    X, dX, dt = load()
    truth = canonical_support()
    thr = 0.1  # declared; the standard Lorenz STLSQ threshold

    py = run_pysindy(X, dX, dt, thr)
    sir = run_restricted_sir(X, dX, thr)

    py_score = score(py, truth)
    sir_score = score(sir, truth)

    # Direct coefficient agreement between the two estimators.
    agree = {}
    for eq in ("dx", "dy", "dz"):
        keys = sorted(set(py[eq]) | set(sir[eq]))
        d = [abs(py[eq].get(k, 0.0) - sir[eq].get(k, 0.0)) for k in keys]
        agree[eq] = {
            "max_abs_coefficient_difference": float(max(d)),
            "identical_support": sorted(
                k for k in keys if abs(py[eq].get(k, 0.0)) > 1e-6
            ) == sorted(k for k in keys if abs(sir[eq].get(k, 0.0)) > 1e-6),
        }

    result = {
        "settings": {
            "library": "PolynomialLibrary(degree=3, include_bias=True)",
            "n_library_terms": len(cubic_terms()),
            "optimizer": f"STLSQ(threshold={thr}, alpha=0.0)",
            "derivatives": "exact analytic (supplied to BOTH estimators)",
            "n_samples": int(X.shape[0]),
            "dt": dt,
        },
        "ground_truth": truth,
        "pysindy": {"coefficients": py, "score": py_score},
        "restricted_sir": {"coefficients": sir, "score": sir_score},
        "agreement": agree,
    }
    (OUT_PY / "containment_pysindy.json").write_text(
        json.dumps({"coefficients": py, "score": py_score}, indent=2), encoding="utf-8"
    )
    (OUT_SIR / "containment_restricted_sir.json").write_text(
        json.dumps({"coefficients": sir, "score": sir_score}, indent=2),
        encoding="utf-8",
    )
    (BENCH / "tables" / "support_comparison.csv").parent.mkdir(exist_ok=True)
    rows = []
    for eq in ("dx", "dy", "dz"):
        for label, sc in (("pysindy", py_score), ("restricted_sir", sir_score)):
            rows.append(
                {
                    "equation": eq,
                    "method": label,
                    "support_exact": sc[eq]["support_exact"],
                    "n_false_positive": len(sc[eq]["false_positives"]),
                    "n_false_negative": len(sc[eq]["false_negatives"]),
                    "max_coeff_error": sc[eq]["max_coeff_error"],
                    "rms_coeff_error": sc[eq]["rms_coeff_error"],
                    "recovered": "; ".join(
                        f"{k}={v:+.6f}" for k, v in sc[eq]["recovered"].items()
                    ),
                }
            )
    pd.DataFrame(rows).to_csv(BENCH / "tables" / "support_comparison.csv", index=False)
    (BENCH / "sir" / "containment" / "containment_full.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    print("CONTAINMENT")
    for eq in ("dx", "dy", "dz"):
        print(f"\n{eq}/dt")
        print(f"  truth        : {truth[eq]}")
        print(f"  pysindy      : {py_score[eq]['recovered']}")
        print(f"    exact support={py_score[eq]['support_exact']} "
              f"max|err|={py_score[eq]['max_coeff_error']:.3e}")
        print(f"  restricted SIR: {sir_score[eq]['recovered']}")
        print(f"    exact support={sir_score[eq]['support_exact']} "
              f"max|err|={sir_score[eq]['max_coeff_error']:.3e}")
        print(f"  agreement    : max|dcoef|="
              f"{agree[eq]['max_abs_coefficient_difference']:.3e} "
              f"same support={agree[eq]['identical_support']}")


if __name__ == "__main__":
    main()
