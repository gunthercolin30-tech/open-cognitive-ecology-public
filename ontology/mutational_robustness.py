from __future__ import annotations

PRIMITIVE = "mutational_robustness"
DESCRIPTION = "Mutational robustness."
DEPENDENCIES = []

"""
ontology/mutational_robustness.py

Scientific implementation of the MUTATIONAL_ROBUSTNESS primitive.

MUTATIONAL_ROBUSTNESS quantifies the capacity of a system to preserve
functional performance and viability under internal structural changes.

Dimensions:
- mutation_tolerance
- fitness_preservation
- structural_resilience
- mutational_robustness_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "MUTATIONAL_ROBUSTNESS"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


class MutationalRobustness:
    """
    Capacity to maintain function despite internal structural variation.
    """

    def __init__(
        self,
        mutation_tolerance=0.0,
        fitness_preservation=0.0,
        structural_resilience=0.0,
    ):
        self.mutation_tolerance = _clamp(mutation_tolerance)
        self.fitness_preservation = _clamp(fitness_preservation)
        self.structural_resilience = _clamp(structural_resilience)

    def evaluate(self, state=None):
        """
        Evaluate mutational robustness metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - mutation_tolerance
            - fitness_preservation
            - structural_resilience
        """
        state = state or {}

        mt = _clamp(state.get("mutation_tolerance", self.mutation_tolerance))
        fp = _clamp(state.get("fitness_preservation", self.fitness_preservation))
        sr = _clamp(state.get("structural_resilience", self.structural_resilience))

        mutational_robustness_index = (mt + fp + sr) / 3.0
        status = "active" if mutational_robustness_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "mutation_tolerance": mt,
            "fitness_preservation": fp,
            "structural_resilience": sr,
            "status": status,
        }

        return {
            "mutation_tolerance": mt,
            "fitness_preservation": fp,
            "structural_resilience": sr,
            "mutational_robustness_index": mutational_robustness_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        """
        One-step operational interface equivalent to evaluate().
        """
        return self.evaluate(state)

    def validate(self, state=None):
        """
        Validate structural consistency of the primitive.
        """
        result = self.evaluate(state)
        index = result["mutational_robustness_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "mutational_robustness_index": index,
            "diagnostics": result["diagnostics"],
        }
