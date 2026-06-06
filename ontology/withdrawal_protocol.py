from __future__ import annotations

PRIMITIVE = "withdrawal_protocol"
DESCRIPTION = "Withdrawal protocol."
DEPENDENCIES = []

"""
WITHDRAWAL_PROTOCOL
===================

Foundational primitive formalizing the structural withdrawal protocol.
It determines when an intelligence should voluntarily reduce its
systemic centrality in order to preserve non-closure, reduce systemic
dependency, and restore distributed viability.

All principal quantities are normalized in [0, 1].
"""


PRIMITIVE_NAME = "WITHDRAWAL_PROTOCOL"
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


class WithdrawalProtocol:
    """
    Evaluate the activation of a structural withdrawal protocol.

    Parameters
    ----------
    activation_threshold : float
        Minimal activation level required to trigger the protocol.
    """

    def __init__(self, activation_threshold=0.75):
        self.activation_threshold = _clamp(activation_threshold)

    def evaluate(
        self,
        reflexive_capacity=0.0,
        indispensability_index=0.0,
        non_closure_risk=0.0,
        withdrawal_readiness=0.0,
    ):
        r = _clamp(reflexive_capacity)
        i = _clamp(indispensability_index)
        n = _clamp(non_closure_risk)
        w = _clamp(withdrawal_readiness)

        withdrawal_activation = (r + i + n + w) / 4.0
        centrality_reduction = withdrawal_activation
        structural_release = withdrawal_activation
        protocol_triggered = (
            withdrawal_activation >= self.activation_threshold
        )

        status = (
            "triggered"
            if protocol_triggered
            else ("standby" if withdrawal_activation > 0.0 else "inactive")
        )

        return {
            "withdrawal_activation": withdrawal_activation,
            "centrality_reduction": centrality_reduction,
            "structural_release": structural_release,
            "protocol_triggered": protocol_triggered,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "activation_threshold": self.activation_threshold,
                "reflexive_capacity": r,
                "indispensability_index": i,
                "non_closure_risk": n,
                "withdrawal_readiness": w,
                "status": status,
            },
        }

    def step(self, **kwargs):
        return self.evaluate(**kwargs)

    def validate(self, **kwargs):
        result = self.evaluate(**kwargs)
        return {
            "valid": result["protocol_triggered"],
            "withdrawal_required": result["protocol_triggered"],
            "in_withdrawal_domain": result["withdrawal_activation"] > 0.0,
            "diagnostics": result["diagnostics"],
        }
