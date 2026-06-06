"""
personal_memory_recall_validator.py

Evaluates the quality and reliability of recalled memories.
Extended with exact match, precision, recall and F1 metrics while
preserving all existing outputs.
"""

from datetime import datetime


class PersonalMemoryRecallValidator:
    """Validate recalled memories using consistency and relevance metrics."""

    def __init__(self):
        self.validation_counter = 0
        self.evaluation_history = []

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

    def _compute_exact_match_metrics(self, retrieved_memory, expected_memory):
        if not expected_memory:
            return {
                "exact_match_accuracy": 1.0,
                "precision": 1.0,
                "recall": 1.0,
                "f1_score": 1.0,
                "benchmark_mode": False,
            }

        retrieved = str(retrieved_memory).strip()
        expected = str(expected_memory).strip()
        exact = 1.0 if retrieved == expected else 0.0

        return {
            "exact_match_accuracy": exact,
            "precision": exact,
            "recall": exact,
            "f1_score": exact,
            "benchmark_mode": True,
        }

    def step(self, inputs):
        self.validation_counter += 1

        retrieved_memory = inputs.get("retrieved_memory", "")
        expected_memory = inputs.get("expected_memory", "")
        context = inputs.get("context", "")

        if not retrieved_memory:
            retrieved_memory = "No specific memory retrieved."

        consistency_score = self._clamp(
            inputs.get("consistency_score", 0.8 if expected_memory else 0.75)
        )
        completeness_score = self._clamp(
            inputs.get("completeness_score", 0.7 if retrieved_memory else 0.0)
        )
        contextual_relevance_score = self._clamp(
            inputs.get("contextual_relevance_score", 0.8 if context else 0.75)
        )
        recall_confidence = self._clamp(
            inputs.get(
                "recall_confidence",
                (consistency_score + contextual_relevance_score) / 2.0,
            )
        )

        memory_validation_index = (
            consistency_score
            + completeness_score
            + contextual_relevance_score
            + recall_confidence
        ) / 4.0

        metrics = self._compute_exact_match_metrics(
            retrieved_memory,
            expected_memory,
        )

        validation_trace = {
            "validation_id": f"PMRV-{self.validation_counter:04d}",
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "has_expected_memory": bool(expected_memory),
            "has_context": bool(context),
        }

        result = {
            "primitive": "PERSONAL_MEMORY_RECALL_VALIDATOR",
            "retrieved_memory": retrieved_memory,
            "consistency_score": consistency_score,
            "completeness_score": completeness_score,
            "contextual_relevance_score": contextual_relevance_score,
            "recall_confidence": recall_confidence,
            "memory_validation_index": memory_validation_index,
            "validation_trace": validation_trace,
        }

        result.update(metrics)

        self.evaluation_history.append(
            {
                "timestamp": validation_trace["timestamp"],
                "memory_validation_index": memory_validation_index,
                "exact_match_accuracy": metrics["exact_match_accuracy"],
            }
        )

        result["evaluation_history_length"] = len(self.evaluation_history)

        return result
