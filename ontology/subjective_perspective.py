PRIMITIVE = "subjective_perspective"
DESCRIPTION = "Subjective perspective."
DEPENDENCIES = []

"""
SUBJECTIVE_PERSPECTIVE primitive.

Scientific formalization of the emergence and stability of a situated first-person
perspective organizing conscious contents around an internal center.

The primitive quantifies:
- perspective_centering
- self_world_differentiation
- experiential_unity
- subjective_perspective_index

All scores are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "SUBJECTIVE_PERSPECTIVE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class SubjectivePerspective:
    """
    Formalizes the organization of cognitive contents relative to an internal
    perspective center.

    Parameters
    ----------
    centering_weight : float
        Weight applied to perspective centering.
    differentiation_weight : float
        Weight applied to self/world differentiation.
    unity_weight : float
        Weight applied to experiential unity.
    """

    def __init__(
        self,
        centering_weight: float = 1.0,
        differentiation_weight: float = 1.0,
        unity_weight: float = 1.0,
    ) -> None:
        self.centering_weight = max(0.0, float(centering_weight))
        self.differentiation_weight = max(0.0, float(differentiation_weight))
        self.unity_weight = max(0.0, float(unity_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate the degree of subjective perspective formation.

        Expected input keys (all optional):
        - self_model_coherence
        - conscious_access
        - self_world_boundary
        - experiential_binding
        """
        state = state or {}

        self_model_coherence = _clamp(float(state.get("self_model_coherence", 0.0)))
        conscious_access = _clamp(float(state.get("conscious_access", 0.0)))
        self_world_boundary = _clamp(float(state.get("self_world_boundary", 0.0)))
        experiential_binding = _clamp(float(state.get("experiential_binding", 0.0)))

        perspective_centering = _clamp(
            0.5 * self_model_coherence + 0.5 * conscious_access
        )

        self_world_differentiation = self_world_boundary

        experiential_unity = _clamp(
            0.5 * experiential_binding + 0.5 * conscious_access
        )

        weighted_sum = (
            self.centering_weight * perspective_centering
            + self.differentiation_weight * self_world_differentiation
            + self.unity_weight * experiential_unity
        )
        total_weight = (
            self.centering_weight
            + self.differentiation_weight
            + self.unity_weight
        )

        if total_weight <= 0.0:
            subjective_perspective_index = 0.0
        else:
            subjective_perspective_index = _clamp(weighted_sum / total_weight)

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "centering_weight": self.centering_weight,
            "differentiation_weight": self.differentiation_weight,
            "unity_weight": self.unity_weight,
            "status": (
                "subjective_perspective_present"
                if subjective_perspective_index > 0.0
                else "subjective_perspective_absent"
            ),
        }

        return {
            "perspective_centering": perspective_centering,
            "self_world_differentiation": self_world_differentiation,
            "experiential_unity": experiential_unity,
            "subjective_perspective_index": subjective_perspective_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether a structured subjective perspective is established.
        """
        result = self.evaluate(state)
        index_value = result["subjective_perspective_index"]

        return {
            "is_valid": index_value >= 0.5,
            "value": index_value,
            "diagnostics": result["diagnostics"],
        }
