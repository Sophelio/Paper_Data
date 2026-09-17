#!/usr/bin/env python
"""Render the three Supplementary Figure S1 panels from this figure folder.

Runs generate_correction_figures.py against the frozen Correction_audit inputs,
writing every audit figure to a temporary directory, then copies the three S1
panels to --out-dir under their manuscript (d3d_-prefixed) names.

By default the inputs are the copies bundled in ../figure_source_data (same
layout as the audit tree: Correction_audit/ plus the parent tables/) and the
outputs go to the figure folder, so no arguments are needed:

    python figure_source/render_figS1.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGURE_DIR = HERE.parent
DEFAULT_AUDIT = FIGURE_DIR / "figure_source_data" / "Correction_audit"
PANELS = (
    "coefficient_change_vs_rank_removed",       # S1a
    "heterogeneity_interval_by_coefficient",    # S1b
    "multivariate_eigenvalue_uncertainty",      # S1c
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit-dir", type=Path, default=DEFAULT_AUDIT,
                    help="Correction_audit directory holding tables/ and the config "
                         "(default: ../figure_source_data/Correction_audit)")
    ap.add_argument("--out-dir", type=Path, default=FIGURE_DIR,
                    help="directory for the d3d_ PDF/PNG/SVG (default: the figure folder)")
    a = ap.parse_args()
    audit = a.audit_dir.expanduser().resolve()
    out = a.out_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["CORRECTION_AUDIT_DIR"] = str(audit)
        os.environ["CORRECTION_FIGURE_DIR"] = tmp
        # correction_audit_utils is not needed for plotting; only the generator.
        sys.path.insert(0, str(HERE))
        import generate_correction_figures as gen
        gen.main()
        for stem in PANELS:
            for ext in ("pdf", "png", "svg"):
                dst = out / f"d3d_{stem}.{ext}"
                shutil.copyfile(Path(tmp) / f"{stem}.{ext}", dst)
                print(dst)


if __name__ == "__main__":
    main()
