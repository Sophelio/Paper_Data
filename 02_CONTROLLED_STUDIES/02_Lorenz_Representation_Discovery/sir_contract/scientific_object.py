"""O = (D, Omega_obs, S, E, Pi, A) — the scientific object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UncertaintyModel:
    """E — what the object declares about its own observational quality."""

    kind: str                       # "numerical" | "observational_gaussian"
    sigma_relative: float = 0.0     # fraction of the development channel std
    applied_before_coordinates: bool = True
    note: str = ""


@dataclass(frozen=True)
class Admissibility:
    """A — which channels may enter the explanatory dependency graph."""

    observed: tuple
    target: str
    forbidden: tuple
    retrospective_history: bool = True


@dataclass(frozen=True)
class ScientificObject:
    name: str
    channels: tuple                 # D
    support: str                    # Omega_obs
    sampling: dict                  # S
    uncertainty: UncertaintyModel   # E
    provenance: dict                # Pi
    admissibility: Admissibility    # A

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "D_channels": list(self.channels),
            "Omega_obs": self.support,
            "S_sampling": self.sampling,
            "E_uncertainty": dict(self.uncertainty.__dict__),
            "Pi_provenance": self.provenance,
            "A_admissibility": {
                "observed": list(self.admissibility.observed),
                "target": self.admissibility.target,
                "forbidden": list(self.admissibility.forbidden),
                "retrospective_history": self.admissibility.retrospective_history,
            },
        }

    def assert_admissible(self, coordinate_dependencies: dict) -> list:
        """Return the coordinates that violate A (depend on a forbidden channel)."""
        forbidden = set(self.admissibility.forbidden)
        return [n for n, deps in coordinate_dependencies.items()
                if forbidden & set(deps)]
