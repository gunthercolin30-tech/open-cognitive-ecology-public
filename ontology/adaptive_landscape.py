PRIMITIVE = "adaptive_landscape"
DESCRIPTION = "Adaptive landscape."
DEPENDENCIES = []

"""
ADAPTIVE_LANDSCAPE
==================

Scientific primitive formalizing the global topological structure of
adaptive possibilities under constraints.

The primitive quantifies the ruggedness of the landscape, the density
of adaptive peaks, the complexity of navigation, and the resulting
adaptive potential.

Related primitives
------------------
- STRUCTURAL_ATTRACTOR
- ATTRACTOR_BASIN
- SELECTIVE_PRESSURE
- VIABILITY_DOMAIN
"""

from typing import Dict, Any


PRIMITIVE_NAME = "ADAPTIVE_LANDSCAPE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class AdaptiveLandscape:
    """
    Formal model of adaptive topography.

    Parameters
    ----------
    landscape_ruggedness : float
        Degree of local irregularity and fragmentation.
    peak_density : float
        Density of viable attractors.
    viability_connectivity : float
        Degree of connectivity between viable regions.

    Scientific interpretation
    -------------------------
    navigation_complexity increases with ruggedness and decreases with
    connectivity.

    adaptive_potential increases with peak density, connectivity, and
    the inverse of navigation complexity.
    """

    def __init__(
        self,
        landscape_ruggedness: float = 0.0,
        peak_density: float = 0.0,
        viability_connectivity: float = 0.0,
    ) -> None:
        self.landscape_ruggedness = _clamp(landscape_ruggedness)
        self.peak_density = _clamp(peak_density)
        self.viability_connectivity = _clamp(viability_connectivity)

    def evaluate(self) -> Dict[str, Any]:
        """Compute adaptive landscape indicators."""
        navigation_complexity = _clamp(
            (self.landscape_ruggedness + (1.0 - self.viability_connectivity)) / 2.0
        )

        adaptive_potential = _clamp(
            (
                self.peak_density
                + self.viability_connectivity
                + (1.0 - navigation_complexity)
            ) / 3.0
        )

        status = (
            "flat"
            if self.landscape_ruggedness == 0.0 and self.peak_density == 0.0
            else "structured"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "landscape_ruggedness": self.landscape_ruggedness,
            "peak_density": self.peak_density,
            "viability_connectivity": self.viability_connectivity,
            "status": status,
        }

        return {
            "landscape_ruggedness": self.landscape_ruggedness,
            "peak_density": self.peak_density,
            "navigation_complexity": navigation_complexity,
            "adaptive_potential": adaptive_potential,
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
            "landscape_ruggedness",
            "peak_density",
            "navigation_complexity",
            "adaptive_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_structured": evaluation["diagnostics"]["status"] == "structured",
            "adaptive_potential": evaluation["adaptive_potential"],
            "diagnostics": evaluation["diagnostics"],
        }
