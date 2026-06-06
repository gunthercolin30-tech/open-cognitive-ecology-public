"""
Adaptive Constitutional Evolution.
Evaluates constitutional amendments and accepts only beneficial changes.
"""

from __future__ import annotations

PRIMITIVE = "ADAPTIVE_CONSTITUTIONAL_EVOLUTION"

DEPENDENCIES = [
    "constitutional_integrity_index",
    "civilization_scale_simulation_runner",
    "non_closure",
]


class AdaptiveConstitutionalEvolution:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.history = []

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        current_constitutional_integrity: float = 0.92,
        proposed_constitutional_integrity: float = 0.93,
        non_closure_score: float = 0.92,
    ) -> dict:
        current = self._clamp(current_constitutional_integrity)
        proposed = self._clamp(proposed_constitutional_integrity)
        non_closure = self._clamp(non_closure_score)

        delta = proposed - current
        accepted = (delta > 0.0) and (non_closure >= 0.75)

        resulting_score = proposed if accepted else current

        if accepted:
            decision = "accepted"
        else:
            decision = "rejected"

        record = {
            "current": current,
            "proposed": proposed,
            "delta": delta,
            "non_closure_score": non_closure,
            "decision": decision,
            "resulting_score": resulting_score,
        }
        self.history.append(record)

        return {
            "primitive": self.primitive,
            "accepted": accepted,
            "decision": decision,
            "delta": delta,
            "resulting_constitutional_integrity": resulting_score,
            "history_length": len(self.history),
            "latest_record": record,
        }
