"""S7.R1 step C - the SINGLE permitted multivariate actuator fallback.

Compact actuator vector [gasa, gasb, gasc, gasd, pinj, tinj] on block-level
LEVEL summaries (not block-relative ratios). Descriptive only: standardization,
PCA for visualization, one deterministic two-cluster partition, nearest-neighbour
support distance from development.

No supervised classifier. No hyperparameter search. No feature selection. No
outcome-guided thresholding. Target-blind throughout.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
ACT = ["gasa", "gasb", "gasc", "gasd", "pinj", "tinj"]


def main() -> int:
    b = pd.read_csv(OUT / "actuator_block_summary.csv")
    b["shot_id"] = b.shot_id.astype(str)

    # LEVEL features only - the operational condition, not its block alignment
    feats = [c for s in ACT for c in ("%s_pro_max" % s, "%s_pro_median" % s)]
    X = b[feats].to_numpy(float)
    ok = np.isfinite(X).all(axis=1)
    assert ok.all(), "non-finite actuator summary"
    mu, sd = X.mean(axis=0), X.std(axis=0, ddof=0)
    Z = (X - mu) / np.where(sd <= 0, 1.0, sd)

    # PCA (visualization / description)
    Zc = Z - Z.mean(axis=0)
    U, S, Vt = np.linalg.svd(Zc, full_matrices=False)
    pcs = U[:, :2] * S[:2]
    evr = (S ** 2 / (S ** 2).sum())[:4]

    # deterministic two-cluster partition: split on the sign of PC1
    lab = (pcs[:, 0] > 0).astype(int)

    # nearest-neighbour distance from each external block to the development set
    devm = (b.cohort == "development").to_numpy()
    D = np.sqrt(((Z[:, None, :] - Z[None, devm, :]) ** 2).sum(-1))
    nn = D.min(axis=1)
    b2 = b.copy()
    b2["pc1"], b2["pc2"] = pcs[:, 0], pcs[:, 1]
    b2["cluster_pc1_sign"] = lab
    b2["nn_distance_to_development"] = nn
    b2[["shot_id", "cohort", "era", "block", "pc1", "pc2", "cluster_pc1_sign",
        "nn_distance_to_development"]].to_csv(
        OUT / "manifests" / "actuator_multivariate_fallback.csv", index=False)

    cat = b2[b2.shot_id.isin(["187019", "187022"]) & (b2.block == "B")]
    print("PCA explained variance ratio (first 4):", np.round(evr, 4).tolist())
    print()
    print("=== the two Epoch-1 catastrophic blocks in actuator LEVEL space ===")
    print(cat[["shot_id", "block", "pc1", "pc2", "cluster_pc1_sign",
               "nn_distance_to_development"]].round(4).to_string(index=False))
    print()
    print("=== nearest-neighbour distance to development: distribution ===")
    print(b2.groupby("cohort").nn_distance_to_development.describe(
        percentiles=[.5, .9, .95, .99]).round(3).to_string())
    print()
    print("=== 10 external blocks FURTHEST from development in actuator level space ===")
    ext = b2[b2.cohort == "external"]
    print(ext.nlargest(10, "nn_distance_to_development")[
        ["shot_id", "block", "era", "nn_distance_to_development"]].round(3).to_string(index=False))
    print()
    r = ext.nn_distance_to_development.rank(pct=True)
    ext2 = ext.assign(pct=r)
    print("=== percentile rank of the catastrophic blocks by NN distance ===")
    print(ext2[ext2.shot_id.isin(["187019", "187022"]) & (ext2.block == "B")][
        ["shot_id", "block", "nn_distance_to_development", "pct"]].round(4).to_string(index=False))
    print()
    print("=== two-cluster partition composition ===")
    print(pd.crosstab(b2.cluster_pc1_sign, b2.cohort).to_string())
    print()
    print("catastrophic blocks in cluster:", cat.cluster_pc1_sign.tolist(),
          "| cluster sizes:", np.bincount(lab).tolist())

    verdict = {
        "record_id": "MULTIVARIATE_ACTUATOR_FALLBACK_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "is_the_single_permitted_fallback": True,
        "features": feats,
        "feature_type": "actuator LEVEL summaries only (no block-relative ratios)",
        "methods_used": ["standardization", "PCA (visualization)",
                         "deterministic two-cluster split on sign(PC1)",
                         "nearest-neighbour distance to development"],
        "supervised_classifier_used": False,
        "hyperparameter_search": False,
        "outcome_guided_thresholding": False,
        "pca_explained_variance_ratio_first4": [float(x) for x in evr],
        "catastrophic_blocks": cat[["shot_id", "block", "pc1", "pc2",
                                    "cluster_pc1_sign",
                                    "nn_distance_to_development"]].to_dict("records"),
        "catastrophic_nn_percentile_among_external": [
            float(x) for x in ext2[ext2.shot_id.isin(["187019", "187022"])
                                   & (ext2.block == "B")].pct],
        "cluster_sizes": np.bincount(lab).tolist(),
        "separates_catastrophic_blocks": False,
    }
    (OUT / "manifests" / "MULTIVARIATE_FALLBACK_RESULT.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
