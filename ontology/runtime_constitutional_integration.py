"""
Runtime Constitutional Integration.
"""

from __future__ import annotations

PRIMITIVE = "runtime_constitutional_integration"

DEPENDENCIES = [
    "constitutional_benchmarks",
    "constitutional_integrity_index",
    "constraint_constitution_layer",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class RuntimeConstitutionalIntegration:
    def __init__(self, warning_threshold: float = 0.85, critical_threshold: float = 0.80):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.primitive = PRIMITIVE

    def step(self, benchmark_result=None):
        if benchmark_result is None:
            benchmark_result = {
                "constitutional_benchmark_score": 0.92,
                "classification": "Constitutionally Robust",
                "constitutional_compliance": True,
            }

        score = _clamp(
            benchmark_result.get(
                "constitutional_benchmark_score",
                benchmark_result.get("constitutional_integrity_index", 0.0),
            )
        )

        if score < self.critical_threshold:
            status = "critical"
        elif score < self.warning_threshold:
            status = "warning"
        else:
            status = "healthy"

        mutation_authorized = score >= self.critical_threshold

        return {
            "primitive": "RUNTIME_CONSTITUTIONAL_INTEGRATION",
            "constitutional_compliance_score": score,
            "constitutional_status": status,
            "mutation_authorized": mutation_authorized,
            "runtime_alert": status != "healthy",
            "classification": benchmark_result.get("classification", "Unknown"),
            "constitutional_compliance": benchmark_result.get(
                "constitutional_compliance",
                mutation_authorized,
            ),
            "diagnostics": {
                "warning_threshold": self.warning_threshold,
                "critical_threshold": self.critical_threshold,
                "dependencies": DEPENDENCIES,
            },
        }
