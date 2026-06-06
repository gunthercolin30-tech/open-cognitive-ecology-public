from __future__ import annotations

PRIMITIVE = "concept_formation"
DESCRIPTION = "Concept formation."
DEPENDENCIES = []

"""
CONCEPT_FORMATION primitive.

Scientific definition
---------------------
CONCEPT_FORMATION formalizes the crystallization of abstract invariants into
stable and reusable cognitive units. It quantifies:

- concept_coherence: internal consistency of the emerging concept.
- boundary_definition: clarity of conceptual delimitation.
- reusability: applicability across multiple contexts.
- concept_formation_index: global synthesis of concept formation quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "CONCEPT_FORMATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class ConceptFormation:
    """Foundational implementation of the CONCEPT_FORMATION primitive."""

    def __init__(
        self,
        coherence_weight: float = 1.0,
        boundary_weight: float = 1.0,
        reusability_weight: float = 1.0,
    ) -> None:
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.boundary_weight = max(0.0, float(boundary_weight))
        self.reusability_weight = max(0.0, float(reusability_weight))

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
        coherence_signals: Iterable[Any] | None = None,
        boundary_signals: Iterable[Any] | None = None,
        reuse_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        coherence_signals = list(coherence_signals or [])
        boundary_signals = list(boundary_signals or [])
        reuse_signals = list(reuse_signals or [])

        concept_coherence = self._fraction(coherence_signals)
        boundary_definition = self._fraction(boundary_signals)
        reusability = self._fraction(reuse_signals)

        total_weight = (
            self.coherence_weight
            + self.boundary_weight
            + self.reusability_weight
        )

        if total_weight <= 0.0:
            concept_formation_index = 0.0
        else:
            concept_formation_index = _clamp(
                (
                    self.coherence_weight * concept_coherence
                    + self.boundary_weight * boundary_definition
                    + self.reusability_weight * reusability
                )
                / total_weight
            )

        status = (
            "nominal"
            if concept_formation_index > 0.0
            else "empty"
        )

        return {
            "primitive": PRIMITIVE_NAME,
            "concept_coherence": concept_coherence,
            "boundary_definition": boundary_definition,
            "reusability": reusability,
            "concept_formation_index": concept_formation_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "coherence_weight": self.coherence_weight,
                "boundary_weight": self.boundary_weight,
                "reusability_weight": self.reusability_weight,
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
                evaluation["concept_formation_index"] >= 0.0
            ),
            "concept_formation_index": (
                evaluation["concept_formation_index"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
