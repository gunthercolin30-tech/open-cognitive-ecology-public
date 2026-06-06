from __future__ import annotations

PRIMITIVE = "meta_cognition"
DESCRIPTION = "Meta cognition."
DEPENDENCIES = []

"""
META_COGNITION primitive.

Scientific definition
---------------------
META_COGNITION formalizes the capacity of a system to monitor, evaluate, and
regulate its own cognitive processes. It quantifies:

- self_monitoring: observation of internal cognitive activity.
- strategy_evaluation: assessment of current cognitive strategies.
- cognitive_regulation: adjustment of cognition based on self-assessment.
- meta_cognition_index: global synthesis of metacognitive performance.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "META_COGNITION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class MetaCognition:
    """Foundational implementation of the META_COGNITION primitive."""

    def __init__(
        self,
        monitoring_weight: float = 1.0,
        evaluation_weight: float = 1.0,
        regulation_weight: float = 1.0,
    ) -> None:
        self.monitoring_weight = max(0.0, float(monitoring_weight))
        self.evaluation_weight = max(0.0, float(evaluation_weight))
        self.regulation_weight = max(0.0, float(regulation_weight))

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
        monitoring_signals: Iterable[Any] | None = None,
        evaluation_signals: Iterable[Any] | None = None,
        regulation_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        monitoring_signals = list(monitoring_signals or [])
        evaluation_signals = list(evaluation_signals or [])
        regulation_signals = list(regulation_signals or [])

        self_monitoring = self._fraction(monitoring_signals)
        strategy_evaluation = self._fraction(evaluation_signals)
        cognitive_regulation = self._fraction(regulation_signals)

        total_weight = (
            self.monitoring_weight
            + self.evaluation_weight
            + self.regulation_weight
        )

        if total_weight <= 0.0:
            meta_cognition_index = 0.0
        else:
            meta_cognition_index = _clamp(
                (
                    self.monitoring_weight * self_monitoring
                    + self.evaluation_weight * strategy_evaluation
                    + self.regulation_weight * cognitive_regulation
                )
                / total_weight
            )

        status = "nominal" if meta_cognition_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "self_monitoring": self_monitoring,
            "strategy_evaluation": strategy_evaluation,
            "cognitive_regulation": cognitive_regulation,
            "meta_cognition_index": meta_cognition_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "monitoring_weight": self.monitoring_weight,
                "evaluation_weight": self.evaluation_weight,
                "regulation_weight": self.regulation_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["meta_cognition_index"] >= 0.0,
            "meta_cognition_index": evaluation["meta_cognition_index"],
            "diagnostics": evaluation["diagnostics"],
        }
