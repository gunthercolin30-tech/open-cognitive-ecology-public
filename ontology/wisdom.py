PRIMITIVE = "wisdom"
DESCRIPTION = "Wisdom."
DEPENDENCIES = []

"""
WISDOM
======

This primitive formalizes wisdom as the integrated capacity to orient decisions
toward long-term viable and value-consistent trajectories.

The wisdom index integrates three bounded components:

- knowledge_integration: ability to synthesize relevant information.
- ethical_discernment: ability to evaluate actions according to normative
  consequences.
- long_term_judgment: ability to anticipate distant implications.

This primitive captures the alignment of cognition, values, and foresight.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "WISDOM"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class Wisdom:
    """Quantifies wisdom as a bounded index in [0, 1]."""

    def __init__(
        self,
        knowledge_weight: float = 1.0,
        ethical_weight: float = 1.0,
        judgment_weight: float = 1.0,
    ) -> None:
        self.knowledge_weight = max(0.0, float(knowledge_weight))
        self.ethical_weight = max(0.0, float(ethical_weight))
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

        knowledge_integration = self._clamp(
            inputs.get("knowledge_integration", 0.0)
        )
        ethical_discernment = self._clamp(
            inputs.get("ethical_discernment", 0.0)
        )
        long_term_judgment = self._clamp(
            inputs.get("long_term_judgment", 0.0)
        )

        total_weight = (
            self.knowledge_weight
            + self.ethical_weight
            + self.judgment_weight
        )

        if total_weight <= 0.0:
            wisdom_index = 0.0
        else:
            wisdom_index = (
                self.knowledge_weight * knowledge_integration
                + self.ethical_weight * ethical_discernment
                + self.judgment_weight * long_term_judgment
            ) / total_weight

        wisdom_index = self._clamp(wisdom_index)

        status = "wise" if wisdom_index >= 0.7 else "short_sighted"

        return {
            "knowledge_integration": knowledge_integration,
            "ethical_discernment": ethical_discernment,
            "long_term_judgment": long_term_judgment,
            "wisdom_index": wisdom_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "knowledge_weight": self.knowledge_weight,
                "ethical_weight": self.ethical_weight,
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
        index = result["wisdom_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "wisdom_index": index,
            "diagnostics": result["diagnostics"],
        }
