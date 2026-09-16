"""K_q = (q, I_q, C_q, R_q, U_q, V_q, Omega_q) — the discovery contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveryContract:
    name: str
    question: str                  # q
    information_boundary: dict     # I_q
    candidate_space: str           # C_q — registry key
    relation_families: tuple       # R_q(C)
    utility: str                   # U_q
    validation: dict               # V_q
    support: str                   # Omega_q
    equivalence: dict              # qualified-model-set rule
    lexicographic: tuple           # tie-break hierarchy

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["relation_families"] = list(self.relation_families)
        d["lexicographic"] = list(self.lexicographic)
        return d
