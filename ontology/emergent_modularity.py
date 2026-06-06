PRIMITIVE = "emergent_modularity"
DESCRIPTION = "Emergent modularity."
DEPENDENCIES = []

"""
EMERGENT_MODULARITY
===================

Scientific primitive formalizing the spontaneous formation of relatively
autonomous functional modules within complex systems.

The primitive quantifies functional specialization, boundary definition,
inter-module coordination, and the resulting modularity strength.

Related primitives
------------------
- MULTI_SCALE_COUPLING
- STRUCTURAL_ATTRACTOR
- INNOVATION_RETENTION
- META_ADAPTATION
"""

from typing import Dict, Any


PRIMITIVE_NAME = "EMERGENT_MODULARITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class EmergentModularity:
    """
    Formal model of spontaneous modular organization.

    Parameters
    ----------
    functional_specialization : float
        Degree of task differentiation among substructures.
    boundary_definition : float
        Clarity of module boundaries.
    inter_module_coordination : float
        Degree of coordination among modules.

    Scientific interpretation
    -------------------------
    modularity_strength is the mean of functional specialization,
    boundary definition, and inter-module coordination.
    """

    def __init__(
        self,
        functional_specialization: float = 0.0,
        boundary_definition: float = 0.0,
        inter_module_coordination: float = 0.0,
    ) -> None:
        self.functional_specialization = _clamp(
            functional_specialization
        )
        self.boundary_definition = _clamp(boundary_definition)
        self.inter_module_coordination = _clamp(
            inter_module_coordination
        )

    def evaluate(self) -> Dict[str, Any]:
        """Compute modularity indicators."""
        modularity_strength = _clamp(
            (
                self.functional_specialization
                + self.boundary_definition
                + self.inter_module_coordination
            ) / 3.0
        )

        status = (
            "unstructured"
            if modularity_strength == 0.0
            else "modular"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "functional_specialization": (
                self.functional_specialization
            ),
            "boundary_definition": self.boundary_definition,
            "inter_module_coordination": (
                self.inter_module_coordination
            ),
            "status": status,
        }

        return {
            "functional_specialization": (
                self.functional_specialization
            ),
            "boundary_definition": self.boundary_definition,
            "inter_module_coordination": (
                self.inter_module_coordination
            ),
            "modularity_strength": modularity_strength,
            "diagnostics": diagnostics,
        }

    def step(self) -> Dict[str, Any]:
        """Return one evaluation step."""
        return self.evaluate()

    def validate(self) -> Dict[str, Any]:
        """Validate internal coherence."""
        evaluation = self.evaluate()

        valid = True
        for key in (
            "functional_specialization",
            "boundary_definition",
            "inter_module_coordination",
            "modularity_strength",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_modular": evaluation["modularity_strength"] > 0.0,
            "modularity_strength": evaluation["modularity_strength"],
            "diagnostics": evaluation["diagnostics"],
        }
