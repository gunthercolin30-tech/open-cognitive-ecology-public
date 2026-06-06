"""
Constitutional Evolution Gate.
"""

from __future__ import annotations

PRIMITIVE = "constitutional_evolution_gate"

DEPENDENCIES = [
    "constitutional_longitudinal_observatory",
    "runtime_constitutional_integration",
    "controlled_evolution_orchestrator",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConstitutionalEvolutionGate:
    def __init__(self, authorization_threshold: float = 0.85) -> None:
        self.authorization_threshold = authorization_threshold
        self.primitive = PRIMITIVE

    def step(self, observatory_result=None, runtime_result=None):
        observatory_result = observatory_result or {}
        runtime_result = runtime_result or {}

        coupling = _clamp(
            observatory_result.get(
                "constitutional_consciousness_coupling",
                0.90,
            )
        )
        compliance = _clamp(
            runtime_result.get(
                "constitutional_compliance_score",
                coupling,
            )
        )

        evolutionary_confidence = _clamp((coupling + compliance) / 2.0)
        mutation_authorized = (
            evolutionary_confidence >= self.authorization_threshold
        )

        if evolutionary_confidence >= 0.95:
            status = "exemplary"
        elif evolutionary_confidence >= 0.90:
            status = "robust"
        elif evolutionary_confidence >= 0.85:
            status = "authorized"
        elif evolutionary_confidence >= 0.75:
            status = "cautious"
        else:
            status = "blocked"

        return {
            "primitive": "CONSTITUTIONAL_EVOLUTION_GATE",
            "evolutionary_confidence_score": evolutionary_confidence,
            "gate_status": status,
            "mutation_authorized": mutation_authorized,
            "requires_human_review": (
                not mutation_authorized
                and evolutionary_confidence >= 0.75
            ),
            "diagnostics": {
                "authorization_threshold": self.authorization_threshold,
                "constitutional_consciousness_coupling": coupling,
                "constitutional_compliance_score": compliance,
                "dependencies": DEPENDENCIES,
            },
        }
