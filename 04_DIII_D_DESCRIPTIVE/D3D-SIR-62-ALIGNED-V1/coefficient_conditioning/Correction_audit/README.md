# Coefficient conditioning correction audit

Correction audit ID: `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1`  
Original audit ID: `D3D-SIR-62-COEFFICIENT-CONDITIONING-V1`  
Canonical run ID: `D3D-SIR-62-ALIGNED-V1`

## Commands

```bat
cd /d D:\sir-web
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\Correction_audit\run_correction_audit.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\Correction_audit\generate_correction_figures.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Coefficient_conditioning\Correction_audit\write_correction_report.py"
```

## Environment

`conda activate sir_web` (Python 3.11; numpy, pandas, scipy, matplotlib, pyarrow).

Seed: 20260805.
