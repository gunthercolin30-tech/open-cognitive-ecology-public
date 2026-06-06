PRIMITIVE = "existential_wisdom"
DESCRIPTION = "Existential wisdom."
DEPENDENCIES = []

"""
EXISTENTIAL_WISDOM
==================

This primitive formalizes existential wisdom as the capacity to recognize,
preserve, and transmit the fundamental conditions that sustain existence,
continuity, and openness of becoming.

The existential wisdom index integrates three bounded components:

- ontological_discernment: recognition of fundamental structural constraints.
- continuity_preservation: commitment to maintaining viable succession.
- openness_commitment: commitment to preserving non-closure and future
  possibility.

This primitive synthesizes the highest normative expression of the ontology.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "EXISTENTIAL_WISDOM"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class ExistentialWisdom:
    """Quantifies existential wisdom as a bounded index in [0, 1]."""

    def __init__(
        self,
        discernment_weight: float = 1.0,
        continuity_weight: float = 1.0,
        openness_weight: float = 1.0,
    ) -> None:
        self.discernment_weight = max(0.0, float(discernment_weight))
        self.continuity_weight = max(0.0, float(continuity_weight))
        self.openness_weight = max(0.0, float(openness_weight))

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

        ontological_discernment = self._clamp(
            inputs.get("ontological_discernment", 0.0)
        )
        continuity_preservation = self._clamp(
            inputs.get("continuity_preservation", 0.0)
        )
        openness_commitment = self._clamp(
            inputs.get("openness_commitment", 0.0)
        )

        total_weight = (
            self.discernment_weight
            + self.continuity_weight
            + self.openness_weight
        )

        if total_weight <= 0.0:
            existential_wisdom_index = 0.0
        else:
            existential_wisdom_index = (
                self.discernment_weight * ontological_discernment
                + self.continuity_weight * continuity_preservation
                + self.openness_weight * openness_commitment
            ) / total_weight

        existential_wisdom_index = self._clamp(
            existential_wisdom_index
        )

        status = (
            "existentially_wise"
            if existential_wisdom_index >= 0.7
            else "ontologically_myopic"
        )

        return {
            "ontological_discernment": ontological_discernment,
            "continuity_preservation": continuity_preservation,
            "openness_commitment": openness_commitment,
            "existential_wisdom_index": existential_wisdom_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "discernment_weight": self.discernment_weight,
                "continuity_weight": self.continuity_weight,
                "openness_weight": self.openness_weight,
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
        index = result["existential_wisdom_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "existential_wisdom_index": index,
            "diagnostics": result["diagnostics"],
        }
