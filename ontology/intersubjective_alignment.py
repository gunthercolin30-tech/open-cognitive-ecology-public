PRIMITIVE = "intersubjective_alignment"
DESCRIPTION = "Intersubjective alignment."
DEPENDENCIES = []

"""
INTERSUBJECTIVE_ALIGNMENT primitive.

Scientific formalization of the partial convergence of distinct cognitive
perspectives, enabling shared representations, coordinated expectations,
and stabilization of common reference structures.

The primitive quantifies:
- representational_overlap
- expectation_coordination
- shared_reference_stability
- intersubjective_alignment_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "INTERSUBJECTIVE_ALIGNMENT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class IntersubjectiveAlignment:
    """
    Formalizes convergence between multiple subjective perspectives.
    """

    def __init__(
        self,
        overlap_weight: float = 1.0,
        coordination_weight: float = 1.0,
        stability_weight: float = 1.0,
    ) -> None:
        self.overlap_weight = max(0.0, float(overlap_weight))
        self.coordination_weight = max(0.0, float(coordination_weight))
        self.stability_weight = max(0.0, float(stability_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - model_similarity
        - semantic_overlap
        - expectation_matching
        - reference_consistency
        """
        state = state or {}

        model_similarity = _clamp(float(state.get("model_similarity", 0.0)))
        semantic_overlap = _clamp(float(state.get("semantic_overlap", 0.0)))
        expectation_matching = _clamp(
            float(state.get("expectation_matching", 0.0))
        )
        reference_consistency = _clamp(
            float(state.get("reference_consistency", 0.0))
        )

        representational_overlap = _clamp(
            0.5 * model_similarity + 0.5 * semantic_overlap
        )
        expectation_coordination = expectation_matching
        shared_reference_stability = reference_consistency

        weighted_sum = (
            self.overlap_weight * representational_overlap
            + self.coordination_weight * expectation_coordination
            + self.stability_weight * shared_reference_stability
        )
        total_weight = (
            self.overlap_weight
            + self.coordination_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            intersubjective_alignment_index = 0.0
        else:
            intersubjective_alignment_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "overlap_weight": self.overlap_weight,
            "coordination_weight": self.coordination_weight,
            "stability_weight": self.stability_weight,
            "status": (
                "intersubjective_alignment_present"
                if intersubjective_alignment_index > 0.0
                else "intersubjective_alignment_absent"
            ),
        }

        return {
            "representational_overlap": representational_overlap,
            "expectation_coordination": expectation_coordination,
            "shared_reference_stability": shared_reference_stability,
            "intersubjective_alignment_index": (
                intersubjective_alignment_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether intersubjective alignment is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["intersubjective_alignment_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
