# S7.4 — Mathematical interpretation `X_rec`

**Freeze:** `D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-V1`
**Status:** **`TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED`**
**`X_rec` instantiated:** **NO**

> S7.4 stopped at its own §4 precondition. **S7.5 is not authorised.**

## Why

The frozen 20 ms analysis grid is **finer than `vsurf`'s source-supported
cadence in 20 of 62 discharges** (7 of 20 development). That conflicts directly
with the frozen no-super-resolution rule — on the target itself.

| Cadence | Value |
|---|---|
| `SOURCE_SUPPORTED` | **19.93 – 82.91 ms**, varies by discharge |
| `ARCHIVED` | 20.0 ms, uniform |
| `ANALYSIS` (S7.3) | 20.0 ms |

`vsurf` was cubic-spline **upsampled in 36 of 62** discharges. Worst case
`165027`: 56 source samples → 229 archived. `UPSTREAM_UPSAMPLED` is a real
interpolation, not bookkeeping.

Verdict `C_SOURCE_CADENCE_VARIES_BY_DISCHARGE` → §4 requires a stop.

## Second finding, flagged not acted on

`vsurf` shares the equilibrium group's time base **exactly in all 62
discharges** — identical source/archived lengths and support as the 15
`LINEAGE_PARTIAL` quantities S7.3 excluded from its own boundary. Not proof of
EFIT derivation, but it opens a question S7.3 had no reason to ask. S7.4 may not
rerank or alter `I_rec`, so it is recorded for the reconciliation only.

## Start here

| File | What it is |
|---|---|
| `TARGET_TEMPORAL_PROVENANCE_AUDIT.md` | the finding, the evidence, and what reconciliation must decide |
| `S7_4_MATHEMATICAL_INTERPRETATION_AUDIT_REPORT.md` | the full internal audit |
| `vsurf_temporal_provenance.csv` | per-discharge trace, all 62 |
| `target_temporal_provenance.json` | machine-readable verdict |
| `S7_4_FREEZE.json` | freeze record and hashes |

## What was verified

Parents clean: S7.1 (9), S7.2 V1 (35), S7.2 V2 (10), S7.3 (33) — **0 drift**.
`y* == vsurf`, 79 predictors, 7 families, external 42, `I_REC`/`O_REC`/boundary
byte-unchanged.

## Access

**Zero archives opened.** Resolved entirely from frozen S7.1 metadata and the
per-shot metadata sidecars (component `A`). No signal value read — development
or external. External cohort remains sealed.

## Not produced

`X_REC.json`, `typed_signal_blocks.csv`, `trajectory_index.csv`,
`temporal_semantics.json`, `interpretation_constraints.json`,
`predictor_dependency_edges.csv`, `X_REC_DEFINITION.md`, `TEMPORAL_SEMANTICS.md`,
`S7_4_MATHEMATICAL_INTERPRETATION_FINAL.md`.

All of them depend on the analysis cadence, which is what is unresolved.
Producing them now would bake in a grid the contract forbids.

## Reproduce

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\04_mathematical_interpretation\scripts\s7_4_temporal_gate.py
```

Deterministic; no seeds; opens no archive.

## Stage gate

No `X_rec` · no coordinates · no products, ratios or derivatives · no `G_rec` ·
no regression · no baseline · no external value · target unchanged and not
reranked · **S7.5 not started.**
