# Coefficient conditioning audit

Canonical package (read-only): `../canonical_d3d_62_shot_run_v1/`  
Audit ID: `D3D-SIR-62-COEFFICIENT-CONDITIONING-V1`

## Environment

```bat
conda activate sir_web
```

Requires: Python 3.11, numpy, pandas, scipy, matplotlib, pyarrow.

## One-command staged workflow

```bat
cd /d D:\sir-web
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\run_coefficient_conditioning_audit.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\generate_conditioning_figures.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\write_conditioning_report.py"
```

## Outputs

- Tables: `tables/`
- Figures: `figures/` (PDF, SVG, PNG)
- Machine summaries: `outputs/`
- Report: `D3D_COEFFICIENT_CONDITIONING_AND_IDENTIFIABILITY_AUDIT.md`
- LaTeX: `latex/S7_7_coefficient_conditioning_results.tex`

Seed: 20260805.
