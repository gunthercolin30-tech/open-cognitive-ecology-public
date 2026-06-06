PRIMITIVE = "temporal_self_continuity"
DESCRIPTION = "Temporal self continuity."
DEPENDENCIES = []

"""
TEMPORAL_SELF_CONTINUITY primitive.

Scientific formalization of the persistence of an internally unified self-model
through time. The primitive quantifies autobiographical coherence, memory
linkage, and future projection, integrating them into a diachronic continuity
index.

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "TEMPORAL_SELF_CONTINUITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class TemporalSelfContinuity:
    """
    Formalizes diachronic persistence of the self.

    Parameters
    ----------
    autobiographical_weight : float
        Weight assigned to autobiographical coherence.
    memory_weight : float
        Weight assigned to memory linkage.
    future_weight : float
        Weight assigned to future projection.
    """

    def __init__(
        self,
        autobiographical_weight: float = 1.0,
        memory_weight: float = 1.0,
        future_weight: float = 1.0,
    ) -> None:
        self.autobiographical_weight = max(0.0, float(autobiographical_weight))
        self.memory_weight = max(0.0, float(memory_weight))
        self.future_weight = max(0.0, float(future_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate temporal self-continuity.

        Optional input keys:
        - autobiographical_memory
        - narrative_coherence
        - episodic_linkage
        - future_simulation
        """
        state = state or {}

        autobiographical_memory = _clamp(
            float(state.get("autobiographical_memory", 0.0))
        )
        narrative_coherence = _clamp(
            float(state.get("narrative_coherence", 0.0))
        )
        episodic_linkage = _clamp(
            float(state.get("episodic_linkage", 0.0))
        )
        future_simulation = _clamp(
            float(state.get("future_simulation", 0.0))
        )

        autobiographical_coherence = _clamp(
            0.5 * autobiographical_memory + 0.5 * narrative_coherence
        )
        memory_linkage = episodic_linkage
        future_projection = future_simulation

        weighted_sum = (
            self.autobiographical_weight * autobiographical_coherence
            + self.memory_weight * memory_linkage
            + self.future_weight * future_projection
        )
        total_weight = (
            self.autobiographical_weight
            + self.memory_weight
            + self.future_weight
        )

        if total_weight <= 0.0:
            temporal_self_continuity_index = 0.0
        else:
            temporal_self_continuity_index = _clamp(weighted_sum / total_weight)

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "autobiographical_weight": self.autobiographical_weight,
            "memory_weight": self.memory_weight,
            "future_weight": self.future_weight,
            "status": (
                "temporal_continuity_present"
                if temporal_self_continuity_index > 0.0
                else "temporal_continuity_absent"
            ),
        }

        return {
            "autobiographical_coherence": autobiographical_coherence,
            "memory_linkage": memory_linkage,
            "future_projection": future_projection,
            "temporal_self_continuity_index": temporal_self_continuity_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether temporal self-continuity is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["temporal_self_continuity_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
