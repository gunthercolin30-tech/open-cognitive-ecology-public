PRIMITIVE = "morphospace_exploration"
DESCRIPTION = "Morphospace exploration."
DEPENDENCIES = []

"""
MORPHOSPACE_EXPLORATION
======================

Scientific primitive formalizing the exploration of the space of
structurally possible configurations.

The primitive quantifies configuration diversity, accessible region
fraction, exploration depth, and resulting morphospace coverage.

Related primitives
------------------
- ADAPTIVE_LANDSCAPE
- OPEN_ENDEDNESS
- EXAPTATION
- NOVELTY_EMERGENCE
"""

from typing import Dict, Any


PRIMITIVE_NAME = "MORPHOSPACE_EXPLORATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class MorphospaceExploration:
    """
    Formal model of exploration within configuration space.

    Parameters
    ----------
    configuration_diversity : float
        Diversity of generated structural configurations.
    accessible_region_fraction : float
        Fraction of morphospace that is reachable.
    exploration_depth : float
        Degree of penetration into accessible regions.

    Scientific interpretation
    -------------------------
    morphospace_coverage is the mean of configuration diversity,
    accessible region fraction, and exploration depth.
    """

    def __init__(
        self,
        configuration_diversity: float = 0.0,
        accessible_region_fraction: float = 0.0,
        exploration_depth: float = 0.0,
    ) -> None:
        self.configuration_diversity = _clamp(
            configuration_diversity
        )
        self.accessible_region_fraction = _clamp(
            accessible_region_fraction
        )
        self.exploration_depth = _clamp(exploration_depth)

    def evaluate(self) -> Dict[str, Any]:
        """Compute morphospace exploration indicators."""
        morphospace_coverage = _clamp(
            (
                self.configuration_diversity
                + self.accessible_region_fraction
                + self.exploration_depth
            ) / 3.0
        )

        status = (
            "localized"
            if morphospace_coverage == 0.0
            else "exploratory"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "configuration_diversity": (
                self.configuration_diversity
            ),
            "accessible_region_fraction": (
                self.accessible_region_fraction
            ),
            "exploration_depth": self.exploration_depth,
            "status": status,
        }

        return {
            "configuration_diversity": (
                self.configuration_diversity
            ),
            "accessible_region_fraction": (
                self.accessible_region_fraction
            ),
            "exploration_depth": self.exploration_depth,
            "morphospace_coverage": morphospace_coverage,
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
            "configuration_diversity",
            "accessible_region_fraction",
            "exploration_depth",
            "morphospace_coverage",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_exploratory": (
                evaluation["morphospace_coverage"] > 0.0
            ),
            "morphospace_coverage": (
                evaluation["morphospace_coverage"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
