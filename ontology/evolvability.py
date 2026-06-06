from __future__ import annotations

PRIMITIVE = "evolvability"
DESCRIPTION = "Evolvability."
DEPENDENCIES = []

"""
ontology/evolvability.py

Scientific implementation of the EVOLVABILITY primitive.

EVOLVABILITY quantifies the structural capacity of a system to generate
sustainable and adaptively accessible variation. It integrates four
dimensions:

- variation_generativity
- viable_mutation_fraction
- adaptive_accessibility
- evolvability_index

The evolvability index is the arithmetic mean of these three dimensions.
All returned quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "EVOLVABILITY"
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


class Evolvability:
    """
    Structural capacity to generate viable and adaptively accessible novelty.
    """

    def __init__(
        self,
        variation_generativity=0.0,
        viable_mutation_fraction=0.0,
        adaptive_accessibility=0.0,
    ):
        self.variation_generativity = _clamp(variation_generativity)
        self.viable_mutation_fraction = _clamp(viable_mutation_fraction)
        self.adaptive_accessibility = _clamp(adaptive_accessibility)

    def evaluate(self, state=None):
        """
        Evaluate evolvability metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - variation_generativity
            - viable_mutation_fraction
            - adaptive_accessibility
        """
        state = state or {}

        vg = _clamp(
            state.get("variation_generativity", self.variation_generativity)
        )
        vmf = _clamp(
            state.get("viable_mutation_fraction", self.viable_mutation_fraction)
        )
        aa = _clamp(
            state.get("adaptive_accessibility", self.adaptive_accessibility)
        )

        evolvability_index = (vg + vmf + aa) / 3.0
        status = "active" if evolvability_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "variation_generativity": vg,
            "viable_mutation_fraction": vmf,
            "adaptive_accessibility": aa,
            "status": status,
        }

        return {
            "variation_generativity": vg,
            "viable_mutation_fraction": vmf,
            "adaptive_accessibility": aa,
            "evolvability_index": evolvability_index,
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
        index = result["evolvability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "evolvability_index": index,
            "diagnostics": result["diagnostics"],
        }
