
"""
PERSONAL_MEMORY_SALIENCE_ENGINE

Computes a salience score for autobiographical memories so that the most
personally meaningful memories can be prioritized during conversational recall.
"""

from typing import Dict, Any


class PersonalMemorySalienceEngine:
    """Quantifies autobiographical memory salience."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        emotional_intensity = self._clip(inputs.get("emotional_intensity", 0.5))
        personal_significance = self._clip(inputs.get("personal_significance", 0.5))
        recurrence_frequency = self._clip(inputs.get("recurrence_frequency", 0.5))
        relational_relevance = self._clip(inputs.get("relational_relevance", 0.5))
        future_relevance = self._clip(inputs.get("future_relevance", 0.5))
        retrieval_success = self._clip(inputs.get("retrieval_success", 0.5))

        autobiographical_weight = self._clip(
            0.35 * personal_significance
            + 0.25 * emotional_intensity
            + 0.20 * relational_relevance
            + 0.20 * future_relevance
        )

        memory_stability_score = self._clip(
            0.50 * recurrence_frequency + 0.50 * retrieval_success
        )

        salience_index = self._clip(
            0.60 * autobiographical_weight + 0.40 * memory_stability_score
        )

        if salience_index >= 0.95:
            salience_class = "core_identity_memory"
        elif salience_index >= 0.85:
            salience_class = "high_priority_memory"
        elif salience_index >= 0.70:
            salience_class = "important_memory"
        else:
            salience_class = "contextual_memory"

        recall_priority = round(100.0 * salience_index, 2)

        return {
            "autobiographical_weight": round(autobiographical_weight, 4),
            "memory_stability_score": round(memory_stability_score, 4),
            "personal_memory_salience_index": round(salience_index, 4),
            "recall_priority": recall_priority,
            "salience_class": salience_class,
        }
