from __future__ import annotations

PRIMITIVE = "neutral_network"
DESCRIPTION = "Neutral network."
DEPENDENCIES = []

"""
ontology/neutral_network.py

Scientific implementation of the NEUTRAL_NETWORK primitive.

NEUTRAL_NETWORK quantifies the structural capacity of a system to explore
connected regions of configuration space while preserving approximately
equivalent fitness or viability.

Dimensions:
- neutral_connectivity
- fitness_equivalence
- exploration_capacity
- neutral_network_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "NEUTRAL_NETWORK"
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


class NeutralNetwork:
    """
    Connected neutral exploration capacity in configuration space.
    """

    def __init__(
        self,
        neutral_connectivity=0.0,
        fitness_equivalence=0.0,
        exploration_capacity=0.0,
    ):
        self.neutral_connectivity = _clamp(neutral_connectivity)
        self.fitness_equivalence = _clamp(fitness_equivalence)
        self.exploration_capacity = _clamp(exploration_capacity)

    def evaluate(self, state=None):
        """
        Evaluate neutral network metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - neutral_connectivity
            - fitness_equivalence
            - exploration_capacity
        """
        state = state or {}

        nc = _clamp(state.get("neutral_connectivity", self.neutral_connectivity))
        fe = _clamp(state.get("fitness_equivalence", self.fitness_equivalence))
        ec = _clamp(state.get("exploration_capacity", self.exploration_capacity))

        neutral_network_index = (nc + fe + ec) / 3.0
        status = "active" if neutral_network_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "neutral_connectivity": nc,
            "fitness_equivalence": fe,
            "exploration_capacity": ec,
            "status": status,
        }

        return {
            "neutral_connectivity": nc,
            "fitness_equivalence": fe,
            "exploration_capacity": ec,
            "neutral_network_index": neutral_network_index,
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
        index = result["neutral_network_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "neutral_network_index": index,
            "diagnostics": result["diagnostics"],
        }
