from __future__ import annotations

PRIMITIVE = "problem_solving"
DESCRIPTION = "Problem solving."
DEPENDENCIES = []

"""
PROBLEM_SOLVING primitive.

Scientific definition
---------------------
PROBLEM_SOLVING formalizes the transformation of an initial problematic state
into a satisfactory state under structural constraints. It quantifies:

- problem_structuring: adequacy of problem representation and decomposition.
- solution_search: effectiveness of exploration through candidate solutions.
- resolution_effectiveness: degree to which the final state satisfies goals.
- problem_solving_index: global synthesis of problem-solving performance.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "PROBLEM_SOLVING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class ProblemSolving:
    """Foundational implementation of the PROBLEM_SOLVING primitive."""

    def __init__(
        self,
        structuring_weight: float = 1.0,
        search_weight: float = 1.0,
        resolution_weight: float = 1.0,
    ) -> None:
        self.structuring_weight = max(0.0, float(structuring_weight))
        self.search_weight = max(0.0, float(search_weight))
        self.resolution_weight = max(0.0, float(resolution_weight))

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
        structuring_signals: Iterable[Any] | None = None,
        search_signals: Iterable[Any] | None = None,
        resolution_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        structuring_signals = list(structuring_signals or [])
        search_signals = list(search_signals or [])
        resolution_signals = list(resolution_signals or [])

        problem_structuring = self._fraction(structuring_signals)
        solution_search = self._fraction(search_signals)
        resolution_effectiveness = self._fraction(resolution_signals)

        total_weight = (
            self.structuring_weight
            + self.search_weight
            + self.resolution_weight
        )

        if total_weight <= 0.0:
            problem_solving_index = 0.0
        else:
            problem_solving_index = _clamp(
                (
                    self.structuring_weight * problem_structuring
                    + self.search_weight * solution_search
                    + self.resolution_weight * resolution_effectiveness
                )
                / total_weight
            )

        status = "nominal" if problem_solving_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "problem_structuring": problem_structuring,
            "solution_search": solution_search,
            "resolution_effectiveness": resolution_effectiveness,
            "problem_solving_index": problem_solving_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "structuring_weight": self.structuring_weight,
                "search_weight": self.search_weight,
                "resolution_weight": self.resolution_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["problem_solving_index"] >= 0.0,
            "problem_solving_index": evaluation["problem_solving_index"],
            "diagnostics": evaluation["diagnostics"],
        }
