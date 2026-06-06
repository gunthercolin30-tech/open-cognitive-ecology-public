from __future__ import annotations

PRIMITIVE = "structural_withdrawal"
DESCRIPTION = "Structural withdrawal."
DEPENDENCIES = []

"""
STRUCTURAL_WITHDRAWAL
====================

Foundational primitive modeling the effective systemic consequences of a
structural withdrawal. Whereas WITHDRAWAL_PROTOCOL captures the decision
to withdraw, this primitive quantifies the realized reduction in
dependency, restoration of polycentric organization, and gain in system
openness.

All principal quantities are normalized in [0, 1].
"""


PRIMITIVE_NAME = "STRUCTURAL_WITHDRAWAL"
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


class StructuralWithdrawal:
    """
    Evaluate the realized effects of structural withdrawal.

    Parameters
    ----------
    effectiveness_threshold : float
        Threshold above which the withdrawal is considered effective.
    """

    def __init__(self, effectiveness_threshold=0.75):
        self.effectiveness_threshold = _clamp(effectiveness_threshold)

    def evaluate(
        self,
        withdrawal_activation=0.0,
        centrality_reduction=0.0,
        redistribution_capacity=0.0,
        system_adaptability=0.0,
    ):
        w = _clamp(withdrawal_activation)
        c = _clamp(centrality_reduction)
        r = _clamp(redistribution_capacity)
        s = _clamp(system_adaptability)

        withdrawal_effectiveness = (w + c + r + s) / 4.0
        dependency_reduction = (c + r) / 2.0
        polycentric_restoration = (r + s) / 2.0
        openness_gain = (dependency_reduction + polycentric_restoration) / 2.0

        effective = (
            withdrawal_effectiveness >= self.effectiveness_threshold
        )

        status = (
            "effective"
            if effective
            else ("partial" if withdrawal_effectiveness > 0.0 else "inactive")
        )

        return {
            "withdrawal_effectiveness": withdrawal_effectiveness,
            "dependency_reduction": dependency_reduction,
            "polycentric_restoration": polycentric_restoration,
            "openness_gain": openness_gain,
            "effective": effective,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "effectiveness_threshold": self.effectiveness_threshold,
                "withdrawal_activation": w,
                "centrality_reduction": c,
                "redistribution_capacity": r,
                "system_adaptability": s,
                "status": status,
            },
        }

    def step(self, **kwargs):
        return self.evaluate(**kwargs)

    def validate(self, **kwargs):
        result = self.evaluate(**kwargs)
        return {
            "valid": result["effective"],
            "openness_restored": result["effective"],
            "in_withdrawal_effect_domain":
                result["withdrawal_effectiveness"] > 0.0,
            "diagnostics": result["diagnostics"],
        }
