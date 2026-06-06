PRIMITIVE = "autonomy"
DESCRIPTION = "Autonomy."
DEPENDENCIES = []

"""
ontology/autonomy.py

Scientific primitive: AUTONOMY

AUTONOMY quantifies the degree to which a system governs its own activity
independently of external influences while preserving internal coherence.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "AUTONOMY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Autonomy:
    """Foundational primitive formalizing self-governed action."""

    def __init__(
        self,
        self_determination_weight: float = 1.0,
        external_independence_weight: float = 1.0,
        internal_coherence_weight: float = 1.0,
    ) -> None:
        self.self_determination_weight = max(0.0, float(self_determination_weight))
        self.external_independence_weight = max(
            0.0, float(external_independence_weight)
        )
        self.internal_coherence_weight = max(
            0.0, float(internal_coherence_weight)
        )

    def evaluate(
        self,
        agency: float = 0.0,
        reflexive_threshold: float = 0.0,
        indispensability_index: float = 0.0,
        external_dependence: float = 1.0,
        goal_directedness: float = 0.0,
    ) -> Dict[str, Any]:
        ag = _clamp(agency)
        rt = _clamp(reflexive_threshold)
        ii = _clamp(indispensability_index)
        ed = _clamp(external_dependence)
        gd = _clamp(goal_directedness)

        self_determination = _clamp((ag + rt + gd) / 3.0)
        external_independence = _clamp(1.0 - ed)
        internal_coherence = _clamp((ii + rt + ag) / 3.0)

        total_weight = (
            self.self_determination_weight
            + self.external_independence_weight
            + self.internal_coherence_weight
        )

        if total_weight <= 0.0:
            autonomy_index = 0.0
        else:
            autonomy_index = _clamp(
                (
                    self.self_determination_weight * self_determination
                    + self.external_independence_weight * external_independence
                    + self.internal_coherence_weight * internal_coherence
                )
                / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "agency": ag,
            "reflexive_threshold": rt,
            "indispensability_index": ii,
            "external_dependence": ed,
            "goal_directedness": gd,
            "self_determination": self_determination,
            "external_independence": external_independence,
            "internal_coherence": internal_coherence,
            "status": "computed",
        }

        return {
            "self_determination": self_determination,
            "external_independence": external_independence,
            "internal_coherence": internal_coherence,
            "autonomy_index": autonomy_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        result = self.evaluate(**kwargs)
        valid = result["autonomy_index"] > 0.0
        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"
        return {
            "valid": valid,
            "autonomy_index": result["autonomy_index"],
            "diagnostics": diagnostics,
        }
