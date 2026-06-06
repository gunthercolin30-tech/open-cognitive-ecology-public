"""
Constitutional Longitudinal Observatory.
"""

from __future__ import annotations

PRIMITIVE = "constitutional_longitudinal_observatory"

DEPENDENCIES = [
    "constitutional_dashboard_integration",
    "constitutional_integrity_index",
    "constitutional_benchmarks",
    "unified_consciousness_composite_index",
    "reflexive_emergence_longitudinal_protocol",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConstitutionalLongitudinalObservatory:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.history = []

    def step(self, dashboard_result=None, consciousness_result=None):
        dashboard_result = dashboard_result or {}
        consciousness_result = consciousness_result or {}

        constitutional_score = _clamp(
            dashboard_result.get("constitutional_dashboard_composite_score", 0.90)
        )
        consciousness_score = _clamp(
            consciousness_result.get("unified_consciousness_composite_index", 0.917)
        )

        entry = {
            "constitutional_score": constitutional_score,
            "consciousness_score": consciousness_score,
        }
        self.history.append(entry)

        n = len(self.history)
        mean_constitutional = sum(e["constitutional_score"] for e in self.history) / n
        mean_consciousness = sum(e["consciousness_score"] for e in self.history) / n

        coupling = _clamp((mean_constitutional + mean_consciousness) / 2.0)

        if coupling >= 0.95:
            trend = "exceptional"
        elif coupling >= 0.90:
            trend = "robust"
        elif coupling >= 0.80:
            trend = "stable"
        elif coupling >= 0.70:
            trend = "fragile"
        else:
            trend = "critical"

        return {
            "primitive": "CONSTITUTIONAL_LONGITUDINAL_OBSERVATORY",
            "history_length": n,
            "mean_constitutional_score": mean_constitutional,
            "mean_consciousness_score": mean_consciousness,
            "constitutional_consciousness_coupling": coupling,
            "longitudinal_trend": trend,
            "diagnostics": {
                "latest_entry": entry,
                "dependencies": DEPENDENCIES,
            },
        }
