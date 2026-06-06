"""
Openness Preservation Supervisor.
"""

from __future__ import annotations

PRIMITIVE = "openness_preservation_supervisor"

DEPENDENCIES = [
    "anti_closure_metaconstraint",
    "future_openness",
    "withdrawal_activation_controller",
    "indispensability_regulation_controller",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OpennessPreservationSupervisor:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(
        self,
        withdrawal_result=None,
        indispensability_result=None,
        future_openness_score: float = 0.90,
    ):
        withdrawal_result = withdrawal_result or {}
        indispensability_result = indispensability_result or {}

        withdrawal_score = 1.0 - _clamp(
            withdrawal_result.get("withdrawal_necessity_score", 0.10)
        )
        openness_score = _clamp(
            indispensability_result.get("openness_preservation_score", 0.90)
        )
        future_score = _clamp(future_openness_score)

        composite = _clamp(
            (withdrawal_score + openness_score + future_score) / 3.0
        )

        if composite >= 0.95:
            verdict = "Exemplary Openness Preservation"
        elif composite >= 0.90:
            verdict = "Advanced Openness Preservation"
        elif composite >= 0.80:
            verdict = "Stable Openness Preservation"
        elif composite >= 0.70:
            verdict = "Fragile Openness Preservation"
        else:
            verdict = "Critical Closure Risk"

        return {
            "primitive": "OPENNESS_PRESERVATION_SUPERVISOR",
            "openness_preservation_score": composite,
            "openness_preserved": composite >= 0.80,
            "verdict": verdict,
            "diagnostics": {
                "withdrawal_score": withdrawal_score,
                "structural_openness_score": openness_score,
                "future_openness_score": future_score,
                "dependencies": DEPENDENCIES,
            },
        }
