PRIMITIVE = "hierarchical_integration"
DESCRIPTION = "Hierarchical integration."
DEPENDENCIES = []

"""
HIERARCHICAL_INTEGRATION
========================

Scientific primitive formalizing the coherent organization of functional
modules into stratified multi-level architectures.

The primitive quantifies level differentiation, top-down coordination,
bottom-up propagation, and resulting hierarchical coherence.

Related primitives
------------------
- EMERGENT_MODULARITY
- MULTI_SCALE_COUPLING
- CONSTRAINT_FIELDS
- META_ADAPTATION
"""

from typing import Dict, Any


PRIMITIVE_NAME = "HIERARCHICAL_INTEGRATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class HierarchicalIntegration:
    """
    Formal model of multi-level hierarchical organization.

    Parameters
    ----------
    level_differentiation : float
        Degree of distinct stratification across organizational levels.
    top_down_coordination : float
        Strength of higher-level regulatory influence.
    bottom_up_propagation : float
        Strength of lower-level signal propagation.

    Scientific interpretation
    -------------------------
    hierarchical_coherence is the mean of level differentiation,
    top-down coordination, and bottom-up propagation.
    """

    def __init__(
        self,
        level_differentiation: float = 0.0,
        top_down_coordination: float = 0.0,
        bottom_up_propagation: float = 0.0,
    ) -> None:
        self.level_differentiation = _clamp(level_differentiation)
        self.top_down_coordination = _clamp(top_down_coordination)
        self.bottom_up_propagation = _clamp(bottom_up_propagation)

    def evaluate(self) -> Dict[str, Any]:
        """Compute hierarchical integration indicators."""
        hierarchical_coherence = _clamp(
            (
                self.level_differentiation
                + self.top_down_coordination
                + self.bottom_up_propagation
            ) / 3.0
        )

        status = (
            "flat"
            if hierarchical_coherence == 0.0
            else "hierarchical"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "level_differentiation": self.level_differentiation,
            "top_down_coordination": self.top_down_coordination,
            "bottom_up_propagation": self.bottom_up_propagation,
            "status": status,
        }

        return {
            "level_differentiation": self.level_differentiation,
            "top_down_coordination": self.top_down_coordination,
            "bottom_up_propagation": self.bottom_up_propagation,
            "hierarchical_coherence": hierarchical_coherence,
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
            "level_differentiation",
            "top_down_coordination",
            "bottom_up_propagation",
            "hierarchical_coherence",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_hierarchical": (
                evaluation["hierarchical_coherence"] > 0.0
            ),
            "hierarchical_coherence": (
                evaluation["hierarchical_coherence"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
