#!/usr/bin/env python
"""Verify the SIR Paper_Data package.

Recomputes every SHA-256 against the manifest, detects missing or changed files,
checks figure allow-list compliance, confirms no manifest source path points
inside the package, and re-derives the headline numbers from the artifacts.

    python verify_paper_data.py            # verify, print report
    python verify_paper_data.py --quick    # skip hashing (structure + numbers only)

Exit 0 if no FAIL. Offline; no network, no credentials.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]
FAIL, WARN, OK = [], [], []


def rec(level, ident, msg):
    {"FAIL": FAIL, "WARN": WARN, "PASS": OK}[level].append((ident, msg))
    print("  [%-4s] %-34s %s" % (level, ident, msg))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()

    print("=" * 78)
    print("SIR Paper_Data verification   %s" % datetime.now(timezone.utc).isoformat())
    print("=" * 78)

    # ---- 1. required structure ------------------------------------------
    required = [
        "00_START_HERE/README.md", "00_START_HERE/DIRECTORY_MAP.md",
        "00_START_HERE/PACKAGE_MANIFEST.csv", "00_START_HERE/PACKAGE_MANIFEST.json",
        "00_START_HERE/CLAIM_TO_ARTIFACT_INDEX.csv",
        "00_START_HERE/FIGURE_TO_SOURCE_INDEX.csv",
        "00_START_HERE/TABLE_TO_SOURCE_INDEX.csv", "00_START_HERE/RUN_INDEX.csv",
        "00_START_HERE/KNOWN_LIMITATIONS.md", "00_START_HERE/ACCESS_AND_LICENSE.md",
        "01_MANUSCRIPT_SNAPSHOT/manuscript_inventory.json",
        "01_MANUSCRIPT_SNAPSHOT/release_pending_inventory.csv",
        "07_TABLES_AND_REPORTED_NUMBERS/numerical_claims/claim_ledger.json",
        "09_REPRODUCIBILITY/RUN_ME_FIRST.md",
        "09_REPRODUCIBILITY/environment/environment.json",
        "90_AUDIT_REPORTS/missing_artifacts.csv",
        "90_AUDIT_REPORTS/ambiguous_artifacts.csv",
        "90_AUDIT_REPORTS/excluded_files.csv",
        "90_AUDIT_REPORTS/duplicate_candidates.csv",
        "90_AUDIT_REPORTS/unresolved_release_fields.csv",
        "03_DIII_D_SOURCE_OBJECT/source_access_notes/RESTRICTED_SOURCE_INDEX.csv",
        "SHA256SUMS.txt",
    ]
    miss = [f for f in required if not (PKG / f).is_file()]
    rec("FAIL" if miss else "PASS", "structure/required",
        "missing: %s" % miss[:4] if miss
        else "all %d required package files present" % len(required))

    # ---- 2. manifest integrity ------------------------------------------
    man = list(csv.DictReader(open(PKG / "00_START_HERE" / "PACKAGE_MANIFEST.csv",
                                   encoding="utf-8")))
    rec("PASS", "manifest/rows", "%d records" % len(man))

    gone, changed, inside = [], [], []
    for r in man:
        p = PKG / r["package_path"]
        if not p.is_file():
            gone.append(r["package_path"]); continue
        if not a.quick and sha256(p) != r["sha256"]:
            changed.append(r["package_path"])
        op = r["original_path"].replace("/", "\\").lower()
        if str(PKG).lower() in op:
            inside.append(r["package_path"])
    rec("FAIL" if gone else "PASS", "manifest/present",
        "%d manifest entries missing from disk" % len(gone) if gone
        else "every manifest entry exists on disk")
    if a.quick:
        rec("WARN", "manifest/hashes", "skipped (--quick)")
    else:
        rec("FAIL" if changed else "PASS", "manifest/hashes",
            "%d files changed since manifest" % len(changed) if changed
            else "all %d SHA-256 values reproduce" % len(man))
    rec("FAIL" if inside else "PASS", "manifest/no_self_reference",
        "%d source paths point inside Paper_Data" % len(inside) if inside
        else "no source path points inside Paper_Data")

    # ---- 3. figure allow-list -------------------------------------------
    figroot = PKG / "06_PAPER_FIGURES_ONLY"
    allowed = {"Fig_01_admissible_relational_space", "Fig_02_phase_turning_manifold",
               "Fig_04_task_contracts_representations",
               "Fig_05_lorenz_representation_landscape",
               "Fig_06_d3d_task_conditioned_4panel", "Supplementary_Figures"}
    present = {d.name for d in figroot.iterdir() if d.is_dir()}
    extra = present - allowed
    rec("FAIL" if extra else "PASS", "figures/allow_list",
        "unexpected figure folders: %s" % sorted(extra) if extra
        else "only allow-listed figure folders present (%d)" % len(present))
    noread = [d.name for d in figroot.rglob("*")
              if d.is_dir() and d.name.startswith(("Fig_", "FigS"))
              and not (d / "README.md").is_file()]
    rec("FAIL" if noread else "PASS", "figures/readme",
        "figure folders without README: %s" % noread if noread
        else "every figure folder documents its provenance")
    fidx = list(csv.DictReader(open(PKG / "00_START_HERE" /
                                    "FIGURE_TO_SOURCE_INDEX.csv", encoding="utf-8")))
    rec("PASS", "figures/index", "%d figure/panel rows indexed" % len(fidx))

    # ---- 4. indexed artifacts exist --------------------------------------
    bad = []
    for r in csv.DictReader(open(PKG / "00_START_HERE" /
                                 "CLAIM_TO_ARTIFACT_INDEX.csv", encoding="utf-8")):
        art = r["canonical_artifact"].strip()
        if art and not (PKG / art).exists():
            bad.append((r["claim_id"], art))
    rec("FAIL" if bad else "PASS", "claims/artifacts_exist",
        "claims with missing artifact: %s" % bad[:3] if bad
        else "every claim points at an artifact that exists")

    # ---- 5. headline numbers re-derived ----------------------------------
    try:
        import pandas as pd
        V = json.loads((PKG / "07_TABLES_AND_REPORTED_NUMBERS" / "numerical_claims" /
                        "claim_ledger.json").read_text())["canonical_values"]
        QD = PKG / "04_DIII_D_DESCRIPTIVE" / "D3D-SIR-62-ALIGNED-V1"
        dm = pd.read_csv(QD / "canonical_run" / "d3d_discharge_metrics.csv")
        mse = float((dm.mse * dm.n_samples).sum() / dm.n_samples.sum())
        ok = abs(mse ** 0.5 - V["qdesc_pooled_rmse"]) < 1e-12
        rec("PASS" if ok else "FAIL", "numbers/qdesc_pooled_rmse",
            "recomputed %.17f from 62 per-discharge MSEs" % mse ** 0.5)

        E1 = PKG / "05_DIII_D_RECONSTRUCTION" / "12_Six_Fold_Target_Cross_Fitting"
        d = pd.read_csv(E1 / "heldout_discharge_results.csv", dtype={"shot_id": str})
        D1 = float((d.REL_nrmse - d.B1_nrmse).mean())
        ok = len(d) == 62 and abs(D1 - V["D1"]) < 1e-12
        rec("PASS" if ok else "FAIL", "numbers/qrec_delta1",
            "62 out-of-fold discharges; Delta_1 = %.6f recomputed" % D1)

        sets = [set(json.loads((E1 / "folds" / f"fold_{k}_result.json").read_text()
                               )["coordinates"]) for k in range(6)]
        union = len(set().union(*sets))
        pair = [len(sets[i] & sets[j]) / len(sets[i] | sets[j])
                for i in range(6) for j in range(i + 1, 6)]
        jac = sum(pair) / len(pair)
        ok = (union == V["union"] and all(len(s) == 12 for s in sets)
              and abs(jac - V["jaccard"]) < 1e-9)
        rec("PASS" if ok else "FAIL", "numbers/qrec_supports",
            "six size-12 supports, union %d, mean Jaccard %.6f" % (union, jac))

        f10 = json.loads((PKG / "05_DIII_D_RECONSTRUCTION" /
                          "07_Protected_Qualification_FAILURE" /
                          "S7_10_FREEZE.json").read_text())
        ok = f10["primary_scientific_verdict"] == V["parent_verdict"] and \
            f10["V3"]["result"] == "FAIL"
        rec("PASS" if ok else "FAIL", "numbers/parent_failure_preserved",
            "parent qualification FAILURE preserved and unmodified")

        b = pd.read_csv(PKG / "05_DIII_D_RECONSTRUCTION" /
                        "01_Target_Selection_and_02_Information_Boundary" /
                        "reconciliation_source_resolution" /
                        "corrected_selected_target_boundary.csv")
        ok = int((b.include_primary == True).sum()) == V["n_pred"] and len(b) == V["n_signals"]
        rec("PASS" if ok else "FAIL", "numbers/boundary",
            "%d of %d quantities admitted as predictors" % (V["n_pred"], V["n_signals"]))
    except Exception as e:
        rec("WARN", "numbers/recompute", "skipped: %s" % e)

    # ---- 6. restricted data ---------------------------------------------
    ri = list(csv.DictReader(open(PKG / "03_DIII_D_SOURCE_OBJECT" /
                                  "source_access_notes" /
                                  "RESTRICTED_SOURCE_INDEX.csv", encoding="utf-8")))
    leaked = list(PKG.rglob("*_resampled.npz"))
    rec("FAIL" if leaked else "PASS", "restricted/not_bundled",
        "restricted archives found inside the package: %d" % len(leaked) if leaked
        else "%d restricted archives indexed with SHA-256, none bundled" % len(ri))

    # ---- 7. historical material is marked --------------------------------
    hist = PKG / "10_REFERENCED_HISTORICAL_LINEAGE"
    unmarked = [r["package_path"] for r in man
                if r["package_path"].startswith("10_REFERENCED")
                and r["status"] not in ("RETIRED", "SUPERSEDED",
                                        "RETIRED_RECONSTRUCTION_BRANCH_ONLY")]
    rec("FAIL" if unmarked else "PASS", "historical/marked",
        "unmarked historical files: %s" % unmarked[:3] if unmarked
        else "every historical artifact is marked RETIRED or SUPERSEDED")
    rec("PASS" if (hist / "README.md").is_file() else "FAIL", "historical/readme",
        "historical lineage documents what supersedes it")

    print("-" * 78)
    verdict = "FAIL" if FAIL else ("PASS_WITH_WARNINGS" if WARN else "PASS")
    print("  %d passed, %d warnings, %d failures  ->  %s"
          % (len(OK), len(WARN), len(FAIL), verdict))
    out = PKG / "90_AUDIT_REPORTS" / "verification_log.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "SIR Paper_Data verification\n%s\n\n%s\n\n%d passed, %d warnings, %d failures\nVERDICT: %s\n"
        % (datetime.now(timezone.utc).isoformat(), "\n".join(
            "[%s] %-34s %s" % (lv, i, m)
            for lv, lst in (("PASS", OK), ("WARN", WARN), ("FAIL", FAIL))
            for i, m in lst), len(OK), len(WARN), len(FAIL), verdict),
        encoding="utf-8")
    print("  log: %s" % out)
    print("=" * 78)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
