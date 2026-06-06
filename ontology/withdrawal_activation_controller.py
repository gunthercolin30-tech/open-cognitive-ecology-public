"""
Withdrawal Activation Controller.
"""

from __future__ import annotations

PRIMITIVE = "withdrawal_activation_controller"

DEPENDENCIES = [
    "reflexive_threshold_governance",
    "withdrawal_protocol",
    "anti_closure_metaconstraint",
    "future_openness",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class WithdrawalActivationController:
    def __init__(self, activation_threshold: float = 0.85) -> None:
        self.primitive = PRIMITIVE
        self.activation_threshold = activation_threshold

    def step(self, governance_result=None, closure_pressure: float = 0.0):
        governance_result = governance_result or {}

        governance_score = _clamp(
            governance_result.get("governance_activation_score", 0.92)
        )
        governance_enabled = bool(
            governance_result.get("governance_enabled", True)
        )
        closure_pressure = _clamp(closure_pressure)

        withdrawal_necessity_score = _clamp(
            (1.0 - governance_score + closure_pressure) / 2.0
        )

        withdrawal_activated = (
            (not governance_enabled)
            or (governance_score < self.activation_threshold)
            or (closure_pressure > 0.70)
        )

        if withdrawal_necessity_score >= 0.90:
            status = "Immediate Withdrawal Required"
        elif withdrawal_necessity_score >= 0.70:
            status = "Withdrawal Recommended"
        elif withdrawal_necessity_score >= 0.50:
            status = "Preventive Withdrawal"
        else:
            status = "No Withdrawal Required"

        return {
            "primitive": "WITHDRAWAL_ACTIVATION_CONTROLLER",
            "withdrawal_necessity_score": withdrawal_necessity_score,
            "withdrawal_activated": withdrawal_activated,
            "withdrawal_status": status,
            "closure_pressure": closure_pressure,
            "diagnostics": {
                "governance_activation_score": governance_score,
                "governance_enabled": governance_enabled,
                "activation_threshold": self.activation_threshold,
                "dependencies": DEPENDENCIES,
            },
        }
