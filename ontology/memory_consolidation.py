from __future__ import annotations

PRIMITIVE = "memory_consolidation"
DESCRIPTION = "Memory consolidation."
DEPENDENCIES = []

"""
MEMORY_CONSOLIDATION primitive.

Scientific definition
---------------------
MEMORY_CONSOLIDATION formalizes the stabilization of newly acquired structures
into persistent organization. It quantifies:

- retention_stability: robustness of retained information.
- integration_consistency: coherence with pre-existing structures.
- long_term_persistence: expected durability over time.
- memory_consolidation_index: global synthesis of consolidation quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "MEMORY_CONSOLIDATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class MemoryConsolidation:
    """Foundational implementation of the MEMORY_CONSOLIDATION primitive."""

    def __init__(
        self,
        stability_weight: float = 1.0,
        consistency_weight: float = 1.0,
        persistence_weight: float = 1.0,
    ) -> None:
        self.stability_weight = max(0.0, float(stability_weight))
        self.consistency_weight = max(0.0, float(consistency_weight))
        self.persistence_weight = max(0.0, float(persistence_weight))

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
        retained_patterns: Iterable[Any] | None = None,
        consistency_signals: Iterable[Any] | None = None,
        persistence_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        retained_patterns = list(retained_patterns or [])
        consistency_signals = list(consistency_signals or [])
        persistence_signals = list(persistence_signals or [])

        retention_stability = self._fraction(retained_patterns)
        integration_consistency = self._fraction(consistency_signals)
        long_term_persistence = self._fraction(persistence_signals)

        total_weight = (
            self.stability_weight
            + self.consistency_weight
            + self.persistence_weight
        )

        if total_weight <= 0.0:
            memory_consolidation_index = 0.0
        else:
            memory_consolidation_index = _clamp(
                (
                    self.stability_weight * retention_stability
                    + self.consistency_weight * integration_consistency
                    + self.persistence_weight * long_term_persistence
                )
                / total_weight
            )

        status = (
            "nominal"
            if memory_consolidation_index > 0.0
            else "empty"
        )

        return {
            "primitive": PRIMITIVE_NAME,
            "retention_stability": retention_stability,
            "integration_consistency": integration_consistency,
            "long_term_persistence": long_term_persistence,
            "memory_consolidation_index": memory_consolidation_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "stability_weight": self.stability_weight,
                "consistency_weight": self.consistency_weight,
                "persistence_weight": self.persistence_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": (
                evaluation["memory_consolidation_index"] >= 0.0
            ),
            "memory_consolidation_index": (
                evaluation["memory_consolidation_index"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
