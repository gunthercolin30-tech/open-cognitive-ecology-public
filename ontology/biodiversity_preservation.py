PRIMITIVE = "biodiversity_preservation"
DESCRIPTION = "Biodiversity preservation."
DEPENDENCIES = []

"""
BIODIVERSITY_PRESERVATION
========================

This primitive formalizes the preservation of biodiversity as a foundational
constraint on long-term ecological and civilizational viability.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "BIODIVERSITY_PRESERVATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class BiodiversityPreservation:
    """Quantifies biodiversity preservation as a bounded index in [0, 1]."""

    def __init__(
        self,
        species_weight: float = 1.0,
        habitat_weight: float = 1.0,
        conservation_weight: float = 1.0,
    ) -> None:
        self.species_weight = max(0.0, float(species_weight))
        self.habitat_weight = max(0.0, float(habitat_weight))
        self.conservation_weight = max(0.0, float(conservation_weight))

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

        species_diversity = self._clamp(
            inputs.get("species_diversity", 0.0)
        )
        habitat_integrity = self._clamp(
            inputs.get("habitat_integrity", 0.0)
        )
        conservation_effectiveness = self._clamp(
            inputs.get("conservation_effectiveness", 0.0)
        )

        total_weight = (
            self.species_weight
            + self.habitat_weight
            + self.conservation_weight
        )

        if total_weight <= 0.0:
            biodiversity_preservation_index = 0.0
        else:
            biodiversity_preservation_index = (
                self.species_weight * species_diversity
                + self.habitat_weight * habitat_integrity
                + self.conservation_weight * conservation_effectiveness
            ) / total_weight

        biodiversity_preservation_index = self._clamp(
            biodiversity_preservation_index
        )

        status = (
            "preserved"
            if biodiversity_preservation_index >= 0.7
            else "degraded"
        )

        return {
            "species_diversity": species_diversity,
            "habitat_integrity": habitat_integrity,
            "conservation_effectiveness": conservation_effectiveness,
            "biodiversity_preservation_index": (
                biodiversity_preservation_index
            ),
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "species_weight": self.species_weight,
                "habitat_weight": self.habitat_weight,
                "conservation_weight": self.conservation_weight,
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
        index = result["biodiversity_preservation_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "biodiversity_preservation_index": index,
            "diagnostics": result["diagnostics"],
        }
