PRIMITIVE = "selective_pressure"
DESCRIPTION = "Selective pressure."
DEPENDENCIES = []

"""
SELECTIVE_PRESSURE
==================

Scientific primitive formalizing the differential retention forces that
bias evolutionary trajectories toward more viable configurations.

The primitive quantifies how environmental constraints and fitness
differences increase the probability that some configurations persist
while others are eliminated.

Related primitives
------------------
- EVOLUTIONARY_DRIFT
- VIABILITY_DOMAIN
- STRUCTURAL_ATTRACTOR
- CONSTRAINT_FIELDS
"""

from typing import Dict, Any


PRIMITIVE_NAME = "SELECTIVE_PRESSURE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class SelectivePressure:
    """
    Formal model of differential selection.

    Parameters
    ----------
    environmental_constraint : float
        Strength of external constraints.
    fitness_gradient : float
        Differential advantage among configurations.
    viability_margin : float
        Distance from the boundary of non-viability.

    Scientific interpretation
    -------------------------
    selection_intensity is the mean of environmental constraint and
    fitness gradient.

    retention_probability combines selection intensity with the degree
    of viability support.

    adaptive_bias equals selection intensity.
    """

    def __init__(
        self,
        environmental_constraint: float = 0.0,
        fitness_gradient: float = 0.0,
        viability_margin: float = 0.0,
    ) -> None:
        self.environmental_constraint = _clamp(environmental_constraint)
        self.fitness_gradient = _clamp(fitness_gradient)
        self.viability_margin = _clamp(viability_margin)

    def evaluate(self) -> Dict[str, Any]:
        """Compute selective pressure indicators."""
        selection_intensity = _clamp(
            (self.environmental_constraint + self.fitness_gradient) / 2.0
        )
        retention_probability = _clamp(
            (selection_intensity + self.viability_margin) / 2.0
        )
        adaptive_bias = selection_intensity

        status = (
            "neutral"
            if selection_intensity == 0.0
            else "selective"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "environmental_constraint": self.environmental_constraint,
            "fitness_gradient": self.fitness_gradient,
            "viability_margin": self.viability_margin,
            "status": status,
        }

        return {
            "selection_intensity": selection_intensity,
            "fitness_gradient": self.fitness_gradient,
            "retention_probability": retention_probability,
            "adaptive_bias": adaptive_bias,
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
            "selection_intensity",
            "fitness_gradient",
            "retention_probability",
            "adaptive_bias",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_selective": evaluation["selection_intensity"] > 0.0,
            "selection_intensity": evaluation["selection_intensity"],
            "diagnostics": evaluation["diagnostics"],
        }
