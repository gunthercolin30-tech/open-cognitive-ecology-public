from __future__ import annotations

PRIMITIVE = "constraint_induced_domain"
DESCRIPTION = "Constraint induced domain."
DEPENDENCIES = []


from typing import Any, Dict, List


class ConstraintInducedDomainPrimitive:
    """
    Formalizes the principle that existence emerges as a domain induced by
    sufficiently compatible constraints.
    """

    PRIMITIVE_NAME = "CONSTRAINT_INDUCED_DOMAIN"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(self, compatibility_threshold: float = 0.5) -> None:
        self.compatibility_threshold = float(compatibility_threshold)

    def compatibility_measure(self, constraints: List[Dict[str, Any]]) -> float:
        """
        Compute a weighted average compatibility score in [0, 1].

        Each constraint may define:
        - compatibility: default 1.0
        - tension: default 0.0
        - weight: default 1.0

        effective_compatibility = compatibility * (1 - tension)
        """
        if not constraints:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for constraint in constraints:
            if not isinstance(constraint, dict):
                continue

            compatibility = float(constraint.get("compatibility", 1.0))
            tension = float(constraint.get("tension", 0.0))
            weight = float(constraint.get("weight", 1.0))

            compatibility = max(0.0, min(1.0, compatibility))
            tension = max(0.0, min(1.0, tension))
            weight = max(0.0, weight)

            effective = compatibility * (1.0 - tension)

            weighted_sum += effective * weight
            total_weight += weight

        if total_weight <= 0.0:
            return 0.0

        score = weighted_sum / total_weight
        return max(0.0, min(1.0, score))

    def domain_emergence(
        self,
        constraints: List[Dict[str, Any]],
        compatibility_threshold: float = None,
    ) -> bool:
        threshold = (
            self.compatibility_threshold
            if compatibility_threshold is None
            else float(compatibility_threshold)
        )
        score = self.compatibility_measure(constraints)
        return score >= threshold

    def step(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(configuration, dict):
            configuration = {}

        constraints = configuration.get("constraints", [])
        if not isinstance(constraints, list):
            constraints = []

        threshold = float(
            configuration.get(
                "compatibility_threshold",
                self.compatibility_threshold,
            )
        )

        score = self.compatibility_measure(constraints)
        emerged = score >= threshold

        return {
            "compatibility_score": score,
            "domain_emerged": emerged,
            "compatibility_threshold": threshold,
        }

    def validate(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(configuration, dict):
            configuration = {}

        constraints = configuration.get("constraints", [])
        if not isinstance(constraints, list):
            constraints = []

        step_result = self.step(configuration)
        emerged = bool(step_result["domain_emerged"])

        return {
            "valid": emerged,
            "domain_emerged": emerged,
            "constraint_count": len(constraints),
            "diagnostics": {
                "primitive": self.PRIMITIVE_NAME,
                "compatibility_score": step_result["compatibility_score"],
                "compatibility_threshold": step_result[
                    "compatibility_threshold"
                ],
                "status": (
                    "domain_emerged"
                    if emerged
                    else "domain_not_emerged"
                ),
            },
        }
