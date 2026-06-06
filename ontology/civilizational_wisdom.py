PRIMITIVE = "civilizational_wisdom"
DESCRIPTION = "Civilizational wisdom."
DEPENDENCIES = []

"""
CIVILIZATIONAL_WISDOM
=====================

This primitive formalizes civilizational wisdom as the collective capacity to
integrate knowledge, exercise normative discernment, and orient institutions
toward long-term viable trajectories.

The civilizational wisdom index integrates three bounded components:

- collective_knowledge_integration: synthesis of distributed knowledge.
- normative_discernment: collective evaluation of long-term consequences.
- long_term_civilizational_judgment: foresight applied to civilizational
  continuity.

This primitive captures the highest-level integration of cognition, ethics,
governance, and stewardship.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "CIVILIZATIONAL_WISDOM"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class CivilizationalWisdom:
    """Quantifies civilizational wisdom as a bounded index in [0, 1]."""

    def __init__(
        self,
        knowledge_weight: float = 1.0,
        normative_weight: float = 1.0,
        judgment_weight: float = 1.0,
    ) -> None:
        self.knowledge_weight = max(0.0, float(knowledge_weight))
        self.normative_weight = max(0.0, float(normative_weight))
        self.judgment_weight = max(0.0, float(judgment_weight))

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

        collective_knowledge_integration = self._clamp(
            inputs.get("collective_knowledge_integration", 0.0)
        )
        normative_discernment = self._clamp(
            inputs.get("normative_discernment", 0.0)
        )
        long_term_civilizational_judgment = self._clamp(
            inputs.get("long_term_civilizational_judgment", 0.0)
        )

        total_weight = (
            self.knowledge_weight
            + self.normative_weight
            + self.judgment_weight
        )

        if total_weight <= 0.0:
            civilizational_wisdom_index = 0.0
        else:
            civilizational_wisdom_index = (
                self.knowledge_weight
                * collective_knowledge_integration
                + self.normative_weight
                * normative_discernment
                + self.judgment_weight
                * long_term_civilizational_judgment
            ) / total_weight

        civilizational_wisdom_index = self._clamp(
            civilizational_wisdom_index
        )

        status = (
            "wise"
            if civilizational_wisdom_index >= 0.7
            else "myopic"
        )

        return {
            "collective_knowledge_integration":
                collective_knowledge_integration,
            "normative_discernment": normative_discernment,
            "long_term_civilizational_judgment":
                long_term_civilizational_judgment,
            "civilizational_wisdom_index":
                civilizational_wisdom_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "knowledge_weight": self.knowledge_weight,
                "normative_weight": self.normative_weight,
                "judgment_weight": self.judgment_weight,
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
        index = result["civilizational_wisdom_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "civilizational_wisdom_index": index,
            "diagnostics": result["diagnostics"],
        }
