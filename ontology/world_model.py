from __future__ import annotations

PRIMITIVE = "world_model"
DESCRIPTION = "World model."
DEPENDENCIES = []

"""
WORLD_MODEL primitive.

Scientific definition
---------------------
WORLD_MODEL formalizes the internal organization of structural relations,
state transitions, and constraints that enable simulation and anticipation.
It quantifies:

- model_coherence: internal consistency of the world representation.
- predictive_accuracy: agreement between predicted and observed outcomes.
- simulation_fidelity: quality of internally simulated trajectories.
- world_model_index: global synthesis of world model quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "WORLD_MODEL"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class WorldModel:
    """Foundational implementation of the WORLD_MODEL primitive."""

    def __init__(
        self,
        coherence_weight: float = 1.0,
        accuracy_weight: float = 1.0,
        fidelity_weight: float = 1.0,
    ) -> None:
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.accuracy_weight = max(0.0, float(accuracy_weight))
        self.fidelity_weight = max(0.0, float(fidelity_weight))

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
        prediction_signals: Iterable[Any] | None = None,
        simulation_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        coherence_signals = list(coherence_signals or [])
        prediction_signals = list(prediction_signals or [])
        simulation_signals = list(simulation_signals or [])

        model_coherence = self._fraction(coherence_signals)
        predictive_accuracy = self._fraction(prediction_signals)
        simulation_fidelity = self._fraction(simulation_signals)

        total_weight = (
            self.coherence_weight
            + self.accuracy_weight
            + self.fidelity_weight
        )

        if total_weight <= 0.0:
            world_model_index = 0.0
        else:
            world_model_index = _clamp(
                (
                    self.coherence_weight * model_coherence
                    + self.accuracy_weight * predictive_accuracy
                    + self.fidelity_weight * simulation_fidelity
                )
                / total_weight
            )

        status = "nominal" if world_model_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "model_coherence": model_coherence,
            "predictive_accuracy": predictive_accuracy,
            "simulation_fidelity": simulation_fidelity,
            "world_model_index": world_model_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "coherence_weight": self.coherence_weight,
                "accuracy_weight": self.accuracy_weight,
                "fidelity_weight": self.fidelity_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["world_model_index"] >= 0.0,
            "world_model_index": evaluation["world_model_index"],
            "diagnostics": evaluation["diagnostics"],
        }
