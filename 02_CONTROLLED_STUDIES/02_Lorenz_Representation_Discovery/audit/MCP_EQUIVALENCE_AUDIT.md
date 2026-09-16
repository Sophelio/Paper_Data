# MCP equivalence / provenance audit

**Date:** 2026-08-27

## Scope and an honest limitation

The principal MCP result in this benchmark is **containment**, which the SIR MCP
executed natively end to end.

The coordinate families used by contracts B/C/D were **not** obtained from the
MCP, for reasons documented in `SIR_MCP_CAPABILITY_AUDIT.md`:

* the Lorenz Dalia project's transform blocks are the built-ins plus `test`; the
  reference-shifted and sensitivity-centered blocks live in the DIIID project;
* the MCP's `data_processing` families are all-or-nothing toggles, not
  individually addressable, individually maskable coordinates;
* the MCP exposes no lag operator, which the declared five-point boundary needs.

Per direction, blocks were **not** ported into the Lorenz project merely to
increase MCP-native surface: the load-bearing gap is contract orchestration, not
coordinate expressibility.

**Consequence:** a numerical MCP-vs-local coordinate cross-check at machine
precision was **not performed in this benchmark**, because the MCP does not emit
the individual coordinate series required to compare. This is a real gap in the
provenance chain and is recorded rather than papered over.

## What provenance *is* established

1. **Containment is MCP-native.** Three runs, recorded with run ids, settings and
   final errors in `sir_mcp/containment/mcp_containment.json`. Exact support
   recovery on all three Lorenz equations independently corroborates that the
   MCP engine and the canonical generator agree.

2. **The relational coordinate families are Archaieus-verified.** `RS`, `SC` and
   `CA` come from `D:/SIR_paper/DIIID_example/transforms.py`, which was verified
   elementwise (`rtol=0, atol=1e-12`) against the canonical Archaieus
   implementation in `AUDIT_dalia_transform_family.md`, and which is
   byte-identical in math to the blocks the same MCP serves in the DIIID
   project. Equivalence is therefore established **through the audited
   implementation**, not through the MCP transport.

3. **Elementary families are definitionally equivalent.** Rates, products and
   quotients correspond to MCP `data_processing` families (`dx`/`dy`,
   `order ≥ 2` terms, `quotients`/`xPhaseder`), but at a different granularity.

## Verdict

Coordinate provenance is **trustworthy but not MCP-cross-checked**. Under the
standing rule this does not invalidate the benchmark — the MCP does supply the
SIR primitives needed to establish trustworthy provenance for containment, and
the remaining families trace to an independently audited implementation.

## To close the gap

The MCP would need to expose evaluated coordinate series (or accept a coordinate
matrix and return its own evaluation) so that a per-sample numerical comparison
at `atol=1e-12` becomes possible. Recorded as roadmap item 6 in
`FRAMEWORK_VS_MCP_IMPLEMENTATION_AUDIT.md`.
