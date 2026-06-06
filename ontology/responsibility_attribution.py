from __future__ import annotations

PRIMITIVE = "responsibility_attribution"
DESCRIPTION = "Responsibility attribution."
DEPENDENCIES = []

"""
RESPONSIBILITY_ATTRIBUTION primitive.

This module formalizes the attribution of responsibility as the integration of
causal contribution, degree of control, intentional involvement, and normative
conformity. It quantifies the extent to which an agent can be held responsible
for an outcome.

The primitive computes:
- causal_contribution
- control_degree
- intentional_involvement
- responsibility_index
"""


PRIMITIVE_NAME = "RESPONSIBILITY_ATTRIBUTION"
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


class ResponsibilityAttribution:
    """Formal model of causal and normative responsibility attribution."""

    def __init__(
        self,
        contribution_weight=1.0,
        control_weight=1.0,
        intention_weight=1.0,
    ):
        self.contribution_weight = max(0.0, float(contribution_weight))
        self.control_weight = max(0.0, float(control_weight))
        self.intention_weight = max(0.0, float(intention_weight))

    def evaluate(
        self,
        causal_contribution=0.0,
        control_degree=0.0,
        intentional_involvement=0.0,
    ):
        causal_contribution = _clamp(causal_contribution)
        control_degree = _clamp(control_degree)
        intentional_involvement = _clamp(intentional_involvement)

        total_weight = (
            self.contribution_weight
            + self.control_weight
            + self.intention_weight
        )

        if total_weight <= 0.0:
            responsibility_index = 0.0
        else:
            responsibility_index = (
                self.contribution_weight * causal_contribution
                + self.control_weight * control_degree
                + self.intention_weight * intentional_involvement
            ) / total_weight

        responsibility_index = _clamp(responsibility_index)

        is_empty = (
            causal_contribution == 0.0
            and control_degree == 0.0
            and intentional_involvement == 0.0
        )

        return {
            "causal_contribution": causal_contribution,
            "control_degree": control_degree,
            "intentional_involvement": intentional_involvement,
            "responsibility_index": responsibility_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "contribution_weight": self.contribution_weight,
                "control_weight": self.control_weight,
                "intention_weight": self.intention_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        causal_contribution=0.0,
        control_degree=0.0,
        intentional_involvement=0.0,
    ):
        return self.evaluate(
            causal_contribution,
            control_degree,
            intentional_involvement,
        )

    def validate(
        self,
        causal_contribution=0.0,
        control_degree=0.0,
        intentional_involvement=0.0,
    ):
        result = self.evaluate(
            causal_contribution,
            control_degree,
            intentional_involvement,
        )

        responsibility_index = result["responsibility_index"]

        return {
            "is_valid": responsibility_index > 0.0,
            "responsibility_index": responsibility_index,
            "diagnostics": result["diagnostics"],
        }
