PRIMITIVE = "institutional_stabilization"
DESCRIPTION = "Institutional stabilization."
DEPENDENCIES = []

"""
INSTITUTIONAL_STABILIZATION primitive.

Scientific formalization of the crystallization of rules, norms, and persistent
collective structures that constrain and guide individual and group behavior.

The primitive quantifies:
- norm_internalization
- rule_enforcement
- structural_persistence
- institutional_stabilization_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "INSTITUTIONAL_STABILIZATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class InstitutionalStabilization:
    """
    Formalizes the emergence of stable institutions as persistent constraint
    structures within collective systems.
    """

    def __init__(
        self,
        internalization_weight: float = 1.0,
        enforcement_weight: float = 1.0,
        persistence_weight: float = 1.0,
    ) -> None:
        self.internalization_weight = max(
            0.0, float(internalization_weight)
        )
        self.enforcement_weight = max(0.0, float(enforcement_weight))
        self.persistence_weight = max(0.0, float(persistence_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - normative_adoption
        - compliance_monitoring
        - sanction_effectiveness
        - structural_durability
        """
        state = state or {}

        normative_adoption = _clamp(
            float(state.get("normative_adoption", 0.0))
        )
        compliance_monitoring = _clamp(
            float(state.get("compliance_monitoring", 0.0))
        )
        sanction_effectiveness = _clamp(
            float(state.get("sanction_effectiveness", 0.0))
        )
        structural_durability = _clamp(
            float(state.get("structural_durability", 0.0))
        )

        norm_internalization = normative_adoption

        rule_enforcement = _clamp(
            0.5 * compliance_monitoring + 0.5 * sanction_effectiveness
        )

        structural_persistence = structural_durability

        weighted_sum = (
            self.internalization_weight * norm_internalization
            + self.enforcement_weight * rule_enforcement
            + self.persistence_weight * structural_persistence
        )
        total_weight = (
            self.internalization_weight
            + self.enforcement_weight
            + self.persistence_weight
        )

        if total_weight <= 0.0:
            institutional_stabilization_index = 0.0
        else:
            institutional_stabilization_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "internalization_weight": self.internalization_weight,
            "enforcement_weight": self.enforcement_weight,
            "persistence_weight": self.persistence_weight,
            "status": (
                "institutional_stabilization_present"
                if institutional_stabilization_index > 0.0
                else "institutional_stabilization_absent"
            ),
        }

        return {
            "norm_internalization": norm_internalization,
            "rule_enforcement": rule_enforcement,
            "structural_persistence": structural_persistence,
            "institutional_stabilization_index": (
                institutional_stabilization_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether institutional stabilization is established.
        """
        result = self.evaluate(state)
        value = result["institutional_stabilization_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
