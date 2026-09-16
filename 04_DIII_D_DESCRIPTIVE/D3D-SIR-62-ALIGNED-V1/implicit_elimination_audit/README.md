# Implicit elimination and denominator conditioning

Audit ID: `D3D-SIR-62-IMPLICIT-CLOSURE-CONDITIONING-V1`

## Commands

```bat
cd /d D:\sir-web
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\run_implicit_conditioning_audit.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\generate_implicit_conditioning_figures.py"
python "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\write_implicit_conditioning_report.py"
pytest "Paper Examples\Relational Coordinates for Multimodal Plasma Observations\Implicit_elimination_and_denominator_conditioning\tests" -q
```

Environment: `conda activate sir_web`. Seed: 20260805.
