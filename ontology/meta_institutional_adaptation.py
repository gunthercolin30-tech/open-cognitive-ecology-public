PRIMITIVE = "meta_institutional_adaptation"
DESCRIPTION = "Meta institutional adaptation."
DEPENDENCIES = []

"""
META_INSTITUTIONAL_ADAPTATION primitive.

Scientific formalization of the capacity of institutions to evaluate
themselves, revise their rules, correct failures, and maintain long-term
relevance.

The primitive quantifies:
- self_evaluation_capacity
- rule_revision_capability
- corrective_effectiveness
- meta_institutional_adaptation_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "META_INSTITUTIONAL_ADAPTATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class MetaInstitutionalAdaptation:
    """Formalizes adaptive self-modification of institutional structures."""

    def __init__(
        self,
        evaluation_weight: float = 1.0,
        revision_weight: float = 1.0,
        correction_weight: float = 1.0,
    ) -> None:
        self.evaluation_weight = max(0.0, float(evaluation_weight))
        self.revision_weight = max(0.0, float(revision_weight))
        self.correction_weight = max(0.0, float(correction_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        state = state or {}

        audit_quality = _clamp(float(state.get("audit_quality", 0.0)))
        reform_capacity = _clamp(float(state.get("reform_capacity", 0.0)))
        feedback_integration = _clamp(
            float(state.get("feedback_integration", 0.0))
        )
        implementation_effectiveness = _clamp(
            float(state.get("implementation_effectiveness", 0.0))
        )

        self_evaluation_capacity = audit_quality
        rule_revision_capability = _clamp(
            0.5 * reform_capacity + 0.5 * feedback_integration
        )
        corrective_effectiveness = implementation_effectiveness

        weighted_sum = (
            self.evaluation_weight * self_evaluation_capacity
            + self.revision_weight * rule_revision_capability
            + self.correction_weight * corrective_effectiveness
        )
        total_weight = (
            self.evaluation_weight
            + self.revision_weight
            + self.correction_weight
        )

        if total_weight <= 0.0:
            meta_institutional_adaptation_index = 0.0
        else:
            meta_institutional_adaptation_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "evaluation_weight": self.evaluation_weight,
            "revision_weight": self.revision_weight,
            "correction_weight": self.correction_weight,
            "status": (
                "meta_institutional_adaptation_present"
                if meta_institutional_adaptation_index > 0.0
                else "meta_institutional_adaptation_absent"
            ),
        }

        return {
            "self_evaluation_capacity": self_evaluation_capacity,
            "rule_revision_capability": rule_revision_capability,
            "corrective_effectiveness": corrective_effectiveness,
            "meta_institutional_adaptation_index": (
                meta_institutional_adaptation_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self.evaluate(state)
        value = result["meta_institutional_adaptation_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
