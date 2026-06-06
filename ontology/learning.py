from __future__ import annotations

PRIMITIVE = "learning"
DESCRIPTION = "Learning."
DEPENDENCIES = []

"""
LEARNING primitive.

Scientific definition
---------------------
LEARNING formalizes the durable integration of experience into the internal
organization of a system. It quantifies:

- experience_integration: extent to which observations are incorporated.
- parameter_update: magnitude and coherence of structural updates.
- performance_improvement: improvement of future effectiveness.
- learning_index: global synthesis of learning quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "LEARNING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Learning:
    """Foundational implementation of the LEARNING primitive."""

    def __init__(
        self,
        integration_weight: float = 1.0,
        update_weight: float = 1.0,
        improvement_weight: float = 1.0,
    ) -> None:
        self.integration_weight = max(0.0, float(integration_weight))
        self.update_weight = max(0.0, float(update_weight))
        self.improvement_weight = max(0.0, float(improvement_weight))

    def _fraction(self, values: Iterable[Any]) -> float:
        values = list(values)
        if not values:
            return 0.0

        total = 0.0
        for value in values:
            if isinstance(value, bool):
                total += 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                total += _clamp(float(value))
            else:
                total += 1.0
        return _clamp(total / len(values))

    def evaluate(
        self,
        experiences: Iterable[Any] | None = None,
        updates: Iterable[Any] | None = None,
        improvements: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        experiences = list(experiences or [])
        updates = list(updates or [])
        improvements = list(improvements or [])

        experience_integration = self._fraction(experiences)
        parameter_update = self._fraction(updates)
        performance_improvement = self._fraction(improvements)

        total_weight = (
            self.integration_weight
            + self.update_weight
            + self.improvement_weight
        )

        if total_weight <= 0.0:
            learning_index = 0.0
        else:
            learning_index = _clamp(
                (
                    self.integration_weight * experience_integration
                    + self.update_weight * parameter_update
                    + self.improvement_weight * performance_improvement
                )
                / total_weight
            )

        status = "nominal" if learning_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "experience_integration": experience_integration,
            "parameter_update": parameter_update,
            "performance_improvement": performance_improvement,
            "learning_index": learning_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "integration_weight": self.integration_weight,
                "update_weight": self.update_weight,
                "improvement_weight": self.improvement_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["learning_index"] >= 0.0,
            "learning_index": evaluation["learning_index"],
            "diagnostics": evaluation["diagnostics"],
        }
