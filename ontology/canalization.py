PRIMITIVE = "canalization"
DESCRIPTION = "Canalization."
DEPENDENCIES = []

"""
CANALIZATION
============

Scientific primitive formalizing the tendency of systems to maintain
structured developmental or adaptive trajectories despite perturbations.

The primitive quantifies perturbation buffering, trajectory guidance,
developmental robustness, and resulting canalization strength.

Related primitives
------------------
- STRUCTURAL_ATTRACTOR
- ATTRACTOR_BASIN
- GENEALOGICAL_CONTINUITY
- HIERARCHICAL_INTEGRATION
"""

from typing import Dict, Any


PRIMITIVE_NAME = "CANALIZATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Canalization:
    """
    Formal model of trajectory stabilization under perturbations.

    Parameters
    ----------
    perturbation_buffering : float
        Capacity to absorb disturbances.
    trajectory_guidance : float
        Strength of directional constraints.
    developmental_robustness : float
        Persistence of coherent development.

    Scientific interpretation
    -------------------------
    canalization_strength is the mean of perturbation buffering,
    trajectory guidance, and developmental robustness.
    """

    def __init__(
        self,
        perturbation_buffering: float = 0.0,
        trajectory_guidance: float = 0.0,
        developmental_robustness: float = 0.0,
    ) -> None:
        self.perturbation_buffering = _clamp(
            perturbation_buffering
        )
        self.trajectory_guidance = _clamp(trajectory_guidance)
        self.developmental_robustness = _clamp(
            developmental_robustness
        )

    def evaluate(self) -> Dict[str, Any]:
        """Compute canalization indicators."""
        canalization_strength = _clamp(
            (
                self.perturbation_buffering
                + self.trajectory_guidance
                + self.developmental_robustness
            ) / 3.0
        )

        status = (
            "labile"
            if canalization_strength == 0.0
            else "canalized"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "perturbation_buffering": (
                self.perturbation_buffering
            ),
            "trajectory_guidance": self.trajectory_guidance,
            "developmental_robustness": (
                self.developmental_robustness
            ),
            "status": status,
        }

        return {
            "perturbation_buffering": (
                self.perturbation_buffering
            ),
            "trajectory_guidance": self.trajectory_guidance,
            "developmental_robustness": (
                self.developmental_robustness
            ),
            "canalization_strength": canalization_strength,
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
            "perturbation_buffering",
            "trajectory_guidance",
            "developmental_robustness",
            "canalization_strength",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_canalized": (
                evaluation["canalization_strength"] > 0.0
            ),
            "canalization_strength": (
                evaluation["canalization_strength"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
