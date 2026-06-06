from __future__ import annotations

PRIMITIVE = "planning"
DESCRIPTION = "Planning."
DEPENDENCIES = []

"""
PLANNING primitive.

Scientific definition
---------------------
PLANNING formalizes the construction of an ordered sequence of intermediate
actions and resource allocations that enables the execution of a selected
strategy. The primitive quantifies:

- sequence_coherence: internal ordering consistency of the action sequence.
- resource_scheduling: adequacy of resource allocation over the plan.
- plan_feasibility: effective realizability under structural constraints.
- planning_index: global synthesis of planning quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "PLANNING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Planning:
    """Foundational implementation of the PLANNING primitive."""

    def __init__(
        self,
        sequence_weight: float = 1.0,
        resource_weight: float = 1.0,
        feasibility_weight: float = 1.0,
    ) -> None:
        self.sequence_weight = max(0.0, float(sequence_weight))
        self.resource_weight = max(0.0, float(resource_weight))
        self.feasibility_weight = max(0.0, float(feasibility_weight))

    def _fraction(self, values: Iterable[Any]) -> float:
        values = list(values)
        if not values:
            return 0.0
        score = 0.0
        for value in values:
            if isinstance(value, bool):
                score += 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                score += _clamp(float(value))
            else:
                score += 1.0
        return _clamp(score / len(values))

    def evaluate(
        self,
        actions: Iterable[Any] | None = None,
        resources: Iterable[Any] | None = None,
        constraints: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        actions = list(actions or [])
        resources = list(resources or [])
        constraints = list(constraints or [])

        sequence_coherence = self._fraction(actions)
        resource_scheduling = self._fraction(resources)

        if constraints:
            satisfaction = self._fraction(constraints)
            plan_feasibility = _clamp(
                (sequence_coherence + resource_scheduling + satisfaction) / 3.0
            )
        else:
            plan_feasibility = _clamp(
                (sequence_coherence + resource_scheduling) / 2.0
                if (actions or resources)
                else 0.0
            )

        total_weight = (
            self.sequence_weight
            + self.resource_weight
            + self.feasibility_weight
        )

        if total_weight <= 0.0:
            planning_index = 0.0
        else:
            planning_index = _clamp(
                (
                    self.sequence_weight * sequence_coherence
                    + self.resource_weight * resource_scheduling
                    + self.feasibility_weight * plan_feasibility
                )
                / total_weight
            )

        status = "nominal" if planning_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "sequence_coherence": sequence_coherence,
            "resource_scheduling": resource_scheduling,
            "plan_feasibility": plan_feasibility,
            "planning_index": planning_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "sequence_weight": self.sequence_weight,
                "resource_weight": self.resource_weight,
                "feasibility_weight": self.feasibility_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["planning_index"] >= 0.0,
            "planning_index": evaluation["planning_index"],
            "diagnostics": evaluation["diagnostics"],
        }
