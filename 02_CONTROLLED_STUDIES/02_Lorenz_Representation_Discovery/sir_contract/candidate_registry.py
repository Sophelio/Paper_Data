"""C_q — the registry of admissible candidate representations.

Each candidate is a (coordinate list, relation family) pair. Coordinate
construction C is kept strictly separate from the relation basis R(C).

Coordinate PROVENANCE is recorded per family so the
FRAMEWORK_VS_MCP_IMPLEMENTATION_AUDIT can map every coordinate to its source.
"""

from __future__ import annotations

import sys
from pathlib import Path

TCB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TCB / "scripts"))
import engine as _E  # noqa: E402  numeric layer (data, coordinates, solver)

# Where each coordinate family actually comes from.
#   MCP_NATIVE            producible by SIR MCP data_processing families
#   LOCAL_REFERENCE       audited reference implementation (Archaieus-verified)
COORDINATE_PROVENANCE = {
    "raw": "LOCAL_REFERENCE (stencil lags; MCP exposes no lag operator)",
    "rate": "MCP_NATIVE_EQUIVALENT (data_processing dx/dy) + LOCAL_REFERENCE stencil",
    "curvature": "LOCAL_REFERENCE (higher-order stencil)",
    "product": "MCP_NATIVE_EQUIVALENT (order>=2 search terms)",
    "quotient": "MCP_NATIVE_EQUIVALENT (data_processing quotients / xPhaseder)",
    "ca_ratio": "LOCAL_REFERENCE (Archaieus-verified)",
    "reference_shifted": "LOCAL_REFERENCE (Archaieus-verified; block absent from the Lorenz project)",
    "sensitivity_centered": "LOCAL_REFERENCE (Archaieus-verified; block absent from the Lorenz project)",
}


def registry() -> dict:
    return _E.candidates()


def dependencies() -> dict:
    """coordinate name -> observable channels it is built from (for A)."""
    return {c.name: set(c.depends_on) for c in _E.F.COORDS}
