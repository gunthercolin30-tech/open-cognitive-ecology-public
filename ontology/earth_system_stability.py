PRIMITIVE = "earth_system_stability"
DESCRIPTION = "Earth system stability."
DEPENDENCIES = []

"""
EARTH_SYSTEM_STABILITY
======================

This primitive formalizes Earth system stability as the integrated capacity of
the planetary system to maintain biospheric and climatic conditions compatible
with long-term ecological and civilizational viability.

The earth system stability index integrates three bounded components:

- boundary_integrity: degree of respect of planetary boundaries.
- biosphere_integrity: preservation of biodiversity and ecosystem functioning.
- climate_regulation: maintenance of stable climate dynamics.

This primitive synthesizes the highest-level ecological constraints governing
the continuity of life-support conditions on Earth.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "EARTH_SYSTEM_STABILITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class EarthSystemStability:
    """Quantifies Earth system stability as a bounded index in [0, 1]."""

    def __init__(
        self,
        boundary_weight: float = 1.0,
        biosphere_weight: float = 1.0,
        climate_weight: float = 1.0,
    ) -> None:
        self.boundary_weight = max(0.0, float(boundary_weight))
        self.biosphere_weight = max(0.0, float(biosphere_weight))
        self.climate_weight = max(0.0, float(climate_weight))

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except (TypeError, ValueError):
            return 0.0
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    def evaluate(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if inputs is None:
            inputs = {}

        boundary_integrity = self._clamp(
            inputs.get("boundary_integrity", 0.0)
        )
        biosphere_integrity = self._clamp(
            inputs.get("biosphere_integrity", 0.0)
        )
        climate_regulation = self._clamp(
            inputs.get("climate_regulation", 0.0)
        )

        total_weight = (
            self.boundary_weight
            + self.biosphere_weight
            + self.climate_weight
        )

        if total_weight <= 0.0:
            earth_system_stability_index = 0.0
        else:
            earth_system_stability_index = (
                self.boundary_weight * boundary_integrity
                + self.biosphere_weight * biosphere_integrity
                + self.climate_weight * climate_regulation
            ) / total_weight

        earth_system_stability_index = self._clamp(
            earth_system_stability_index
        )

        status = (
            "stable"
            if earth_system_stability_index >= 0.7
            else "destabilized"
        )

        return {
            "boundary_integrity": boundary_integrity,
            "biosphere_integrity": biosphere_integrity,
            "climate_regulation": climate_regulation,
            "earth_system_stability_index": earth_system_stability_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "boundary_weight": self.boundary_weight,
                "biosphere_weight": self.biosphere_weight,
                "climate_weight": self.climate_weight,
                "status": status,
            },
        }

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.evaluate(inputs)

    def validate(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        result = self.evaluate(inputs)
        index = result["earth_system_stability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "earth_system_stability_index": index,
            "diagnostics": result["diagnostics"],
        }
