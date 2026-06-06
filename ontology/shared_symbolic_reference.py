PRIMITIVE = "shared_symbolic_reference"
DESCRIPTION = "Shared symbolic reference."
DEPENDENCIES = []

"""
SHARED_SYMBOLIC_REFERENCE primitive.

Scientific formalization of the stabilization of symbolic conventions that map
signs to common references across multiple agents.

The primitive quantifies:
- symbol_conventionalization
- reference_consensus
- semantic_stability
- shared_symbolic_reference_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "SHARED_SYMBOLIC_REFERENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class SharedSymbolicReference:
    """
    Formalizes the emergence of stable symbolic references shared by agents.
    """

    def __init__(
        self,
        conventionalization_weight: float = 1.0,
        consensus_weight: float = 1.0,
        stability_weight: float = 1.0,
    ) -> None:
        self.conventionalization_weight = max(
            0.0, float(conventionalization_weight)
        )
        self.consensus_weight = max(0.0, float(consensus_weight))
        self.stability_weight = max(0.0, float(stability_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - usage_convergence
        - sign_consistency
        - referential_agreement
        - semantic_persistence
        """
        state = state or {}

        usage_convergence = _clamp(
            float(state.get("usage_convergence", 0.0))
        )
        sign_consistency = _clamp(
            float(state.get("sign_consistency", 0.0))
        )
        referential_agreement = _clamp(
            float(state.get("referential_agreement", 0.0))
        )
        semantic_persistence = _clamp(
            float(state.get("semantic_persistence", 0.0))
        )

        symbol_conventionalization = _clamp(
            0.5 * usage_convergence + 0.5 * sign_consistency
        )
        reference_consensus = referential_agreement
        semantic_stability = semantic_persistence

        weighted_sum = (
            self.conventionalization_weight * symbol_conventionalization
            + self.consensus_weight * reference_consensus
            + self.stability_weight * semantic_stability
        )
        total_weight = (
            self.conventionalization_weight
            + self.consensus_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            shared_symbolic_reference_index = 0.0
        else:
            shared_symbolic_reference_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "conventionalization_weight": (
                self.conventionalization_weight
            ),
            "consensus_weight": self.consensus_weight,
            "stability_weight": self.stability_weight,
            "status": (
                "shared_symbolic_reference_present"
                if shared_symbolic_reference_index > 0.0
                else "shared_symbolic_reference_absent"
            ),
        }

        return {
            "symbol_conventionalization": symbol_conventionalization,
            "reference_consensus": reference_consensus,
            "semantic_stability": semantic_stability,
            "shared_symbolic_reference_index": (
                shared_symbolic_reference_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether a shared symbolic reference system is established.
        """
        result = self.evaluate(state)
        value = result["shared_symbolic_reference_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
