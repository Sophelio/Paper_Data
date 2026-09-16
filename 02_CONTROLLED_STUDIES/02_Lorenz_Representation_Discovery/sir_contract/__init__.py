"""Reference SIR contract orchestration ("SIR contract harness").

This is NOT "MCP-native SIR". The current SIR MCP exposes SIR *primitives*
(coordinate families, relation search, provenance, dataset validation) but does
not yet expose the contract-level layer of the SIR framework: discovery
contracts, grouped held-out validation, declarable task utilities, or
qualified-model sets.

This package is an audited benchmark-local reference implementation of that
contract layer. It consumes MCP-native SIR primitives where the MCP exposes
them, and uses PySINDy STLSQ as one admissible relation solver R_q(C) *inside*
the contract — which is precisely the nesting the benchmark demonstrates.

Terminology, used consistently and never interchangeably:

    SIR framework          the mathematical formulation in the manuscript
    SIR contract harness   this package
    SIR MCP                the Dalia-hosted SIR engine
    PySINDy solver         STLSQ acting as R_q(C)

Implementation status carried by this benchmark:

    SIR_IMPLEMENTATION_STATUS =
        MCP_NATIVE_PRIMITIVES_PLUS_AUDITED_CONTRACT_HARNESS
"""

SIR_IMPLEMENTATION_STATUS = "MCP_NATIVE_PRIMITIVES_PLUS_AUDITED_CONTRACT_HARNESS"
