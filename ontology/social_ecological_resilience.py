PRIMITIVE = "social_ecological_resilience"
DESCRIPTION = "Social ecological resilience."
DEPENDENCIES = []

"""
SOCIAL_ECOLOGICAL_RESILIENCE
============================

This primitive formalizes social-ecological resilience as the integrated
capacity of coupled human-natural systems to absorb disturbances, adapt,
transform, and maintain viable trajectories.

The social ecological resilience index integrates three bounded components:

- ecological_resilience: resilience of ecosystems and biospheric processes.
- institutional_resilience: resilience of governance and coordination systems.
- adaptive_governance: capacity for learning-based and transformative governance.

This primitive synthesizes continuity across coupled ecological and
civilizational domains.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "SOCIAL_ECOLOGICAL_RESILIENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class SocialEcologicalResilience:
    """Quantifies social-ecological resilience as a bounded index in [0, 1]."""

    def __init__(
        self,
        ecological_weight: float = 1.0,
        institutional_weight: float = 1.0,
        governance_weight: float = 1.0,
    ) -> None:
        self.ecological_weight = max(0.0, float(ecological_weight))
        self.institutional_weight = max(0.0, float(institutional_weight))
        self.governance_weight = max(0.0, float(governance_weight))

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

        ecological_resilience = self._clamp(
            inputs.get("ecological_resilience", 0.0)
        )
        institutional_resilience = self._clamp(
            inputs.get("institutional_resilience", 0.0)
        )
        adaptive_governance = self._clamp(
            inputs.get("adaptive_governance", 0.0)
        )

        total_weight = (
            self.ecological_weight
            + self.institutional_weight
            + self.governance_weight
        )

        if total_weight <= 0.0:
            social_ecological_resilience_index = 0.0
        else:
            social_ecological_resilience_index = (
                self.ecological_weight * ecological_resilience
                + self.institutional_weight * institutional_resilience
                + self.governance_weight * adaptive_governance
            ) / total_weight

        social_ecological_resilience_index = self._clamp(
            social_ecological_resilience_index
        )

        status = (
            "resilient"
            if social_ecological_resilience_index >= 0.7
            else "fragile"
        )

        return {
            "ecological_resilience": ecological_resilience,
            "institutional_resilience": institutional_resilience,
            "adaptive_governance": adaptive_governance,
            "social_ecological_resilience_index": (
                social_ecological_resilience_index
            ),
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "ecological_weight": self.ecological_weight,
                "institutional_weight": self.institutional_weight,
                "governance_weight": self.governance_weight,
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
        index = result["social_ecological_resilience_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "social_ecological_resilience_index": index,
            "diagnostics": result["diagnostics"],
        }
