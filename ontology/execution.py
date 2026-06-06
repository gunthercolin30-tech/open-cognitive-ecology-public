from __future__ import annotations

PRIMITIVE = "execution"
DESCRIPTION = "Execution."
DEPENDENCIES = []

"""
EXECUTION primitive.

Scientific definition
---------------------
EXECUTION formalizes the effective realization of a previously established plan.
It quantifies:

- action_completion: proportion of actions effectively completed.
- schedule_adherence: conformity between realized timing and planned timing.
- execution_efficiency: operational effectiveness during realization.
- execution_index: global synthesis of execution quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "EXECUTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Execution:
    """Foundational implementation of the EXECUTION primitive."""

    def __init__(
        self,
        completion_weight: float = 1.0,
        schedule_weight: float = 1.0,
        efficiency_weight: float = 1.0,
    ) -> None:
        self.completion_weight = max(0.0, float(completion_weight))
        self.schedule_weight = max(0.0, float(schedule_weight))
        self.efficiency_weight = max(0.0, float(efficiency_weight))

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
        completed_actions: Iterable[Any] | None = None,
        schedule_matches: Iterable[Any] | None = None,
        efficiency_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        completed_actions = list(completed_actions or [])
        schedule_matches = list(schedule_matches or [])
        efficiency_signals = list(efficiency_signals or [])

        action_completion = self._fraction(completed_actions)
        schedule_adherence = self._fraction(schedule_matches)
        execution_efficiency = self._fraction(efficiency_signals)

        total_weight = (
            self.completion_weight
            + self.schedule_weight
            + self.efficiency_weight
        )

        if total_weight <= 0.0:
            execution_index = 0.0
        else:
            execution_index = _clamp(
                (
                    self.completion_weight * action_completion
                    + self.schedule_weight * schedule_adherence
                    + self.efficiency_weight * execution_efficiency
                )
                / total_weight
            )

        status = "nominal" if execution_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "action_completion": action_completion,
            "schedule_adherence": schedule_adherence,
            "execution_efficiency": execution_efficiency,
            "execution_index": execution_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "completion_weight": self.completion_weight,
                "schedule_weight": self.schedule_weight,
                "efficiency_weight": self.efficiency_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["execution_index"] >= 0.0,
            "execution_index": evaluation["execution_index"],
            "diagnostics": evaluation["diagnostics"],
        }
