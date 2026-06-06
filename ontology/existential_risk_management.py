PRIMITIVE = "existential_risk_management"
DESCRIPTION = "Existential risk management."
DEPENDENCIES = []

"""
EXISTENTIAL_RISK_MANAGEMENT primitive.

Scientific formalization of the capacity of a civilization-scale system to
detect existential threats, evaluate their severity, coordinate preventive
responses, and preserve long-term continuity.

The primitive quantifies:
- threat_detection
- risk_assessment
- preventive_coordination
- existential_risk_management_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "EXISTENTIAL_RISK_MANAGEMENT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class ExistentialRiskManagement:
    """Formalizes civilization-scale management of existential risks."""

    def __init__(
        self,
        detection_weight: float = 1.0,
        assessment_weight: float = 1.0,
        coordination_weight: float = 1.0,
    ) -> None:
        self.detection_weight = max(0.0, float(detection_weight))
        self.assessment_weight = max(0.0, float(assessment_weight))
        self.coordination_weight = max(0.0, float(coordination_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        state = state or {}

        monitoring_coverage = _clamp(
            float(state.get("monitoring_coverage", 0.0))
        )
        forecasting_accuracy = _clamp(
            float(state.get("forecasting_accuracy", 0.0))
        )
        mitigation_readiness = _clamp(
            float(state.get("mitigation_readiness", 0.0))
        )
        coordination_capacity = _clamp(
            float(state.get("coordination_capacity", 0.0))
        )

        threat_detection = monitoring_coverage
        risk_assessment = forecasting_accuracy
        preventive_coordination = _clamp(
            0.5 * mitigation_readiness + 0.5 * coordination_capacity
        )

        weighted_sum = (
            self.detection_weight * threat_detection
            + self.assessment_weight * risk_assessment
            + self.coordination_weight * preventive_coordination
        )
        total_weight = (
            self.detection_weight
            + self.assessment_weight
            + self.coordination_weight
        )

        if total_weight <= 0.0:
            existential_risk_management_index = 0.0
        else:
            existential_risk_management_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "detection_weight": self.detection_weight,
            "assessment_weight": self.assessment_weight,
            "coordination_weight": self.coordination_weight,
            "status": (
                "existential_risk_management_present"
                if existential_risk_management_index > 0.0
                else "existential_risk_management_absent"
            ),
        }

        return {
            "threat_detection": threat_detection,
            "risk_assessment": risk_assessment,
            "preventive_coordination": preventive_coordination,
            "existential_risk_management_index": (
                existential_risk_management_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self.evaluate(state)
        value = result["existential_risk_management_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
