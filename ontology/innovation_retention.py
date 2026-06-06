PRIMITIVE = "innovation_retention"
DESCRIPTION = "Innovation retention."
DEPENDENCIES = []

"""
INNOVATION_RETENTION
====================

Scientific primitive formalizing the stabilization and persistence of
emergent novelties within a lineage or adaptive system.

The primitive quantifies how new configurations are retained, integrated,
and maintained over time.

Related primitives
------------------
- NOVELTY_EMERGENCE
- SELECTIVE_PRESSURE
- GENEALOGICAL_CONTINUITY
- STRUCTURAL_ATTRACTOR
"""

from typing import Dict, Any


PRIMITIVE_NAME = "INNOVATION_RETENTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class InnovationRetention:
    """
    Formal model of innovation persistence.

    Parameters
    ----------
    stabilization_capacity : float
        Capacity to stabilize a novel configuration.
    retention_probability : float
        Probability that the novelty is preserved.
    integration_strength : float
        Degree of structural integration into the system.

    Scientific interpretation
    -------------------------
    innovation_persistence is the mean of stabilization capacity,
    retention probability, and integration strength.
    """

    def __init__(
        self,
        stabilization_capacity: float = 0.0,
        retention_probability: float = 0.0,
        integration_strength: float = 0.0,
    ) -> None:
        self.stabilization_capacity = _clamp(stabilization_capacity)
        self.retention_probability = _clamp(retention_probability)
        self.integration_strength = _clamp(integration_strength)

    def evaluate(self) -> Dict[str, Any]:
        """Compute innovation retention indicators."""
        innovation_persistence = _clamp(
            (
                self.stabilization_capacity
                + self.retention_probability
                + self.integration_strength
            ) / 3.0
        )

        status = (
            "transient"
            if innovation_persistence == 0.0
            else "retained"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "stabilization_capacity": self.stabilization_capacity,
            "retention_probability": self.retention_probability,
            "integration_strength": self.integration_strength,
            "status": status,
        }

        return {
            "stabilization_capacity": self.stabilization_capacity,
            "retention_probability": self.retention_probability,
            "integration_strength": self.integration_strength,
            "innovation_persistence": innovation_persistence,
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
            "stabilization_capacity",
            "retention_probability",
            "integration_strength",
            "innovation_persistence",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_retained": evaluation["innovation_persistence"] > 0.0,
            "innovation_persistence": evaluation["innovation_persistence"],
            "diagnostics": evaluation["diagnostics"],
        }
