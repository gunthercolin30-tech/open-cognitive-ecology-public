"""
Constitutional Dashboard Integration.
"""

from __future__ import annotations

PRIMITIVE = "constitutional_dashboard_integration"

DEPENDENCIES = [
    "constitutional_integrity_index",
    "constitutional_benchmarks",
    "runtime_constitutional_integration",
    "constitutional_stress_tests",
    "runtime_native_consciousness_dashboard",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConstitutionalDashboardIntegration:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(
        self,
        integrity_result=None,
        benchmark_result=None,
        runtime_result=None,
        stress_result=None,
    ):
        integrity_score = _clamp(
            (integrity_result or {}).get("constitutional_integrity_index", 0.92)
        )
        benchmark_score = _clamp(
            (benchmark_result or {}).get("constitutional_benchmark_score", 0.91)
        )
        compliance_score = _clamp(
            (runtime_result or {}).get("constitutional_compliance_score", 0.91)
        )
        stress_score = _clamp(
            (stress_result or {}).get("stress_resilience_score", 0.89)
        )

        composite = _clamp(
            (
                integrity_score
                + benchmark_score
                + compliance_score
                + stress_score
            ) / 4.0
        )

        if composite >= 0.95:
            status = "exemplary"
        elif composite >= 0.90:
            status = "robust"
        elif composite >= 0.80:
            status = "stable"
        elif composite >= 0.70:
            status = "fragile"
        else:
            status = "critical"

        return {
            "primitive": "CONSTITUTIONAL_DASHBOARD_INTEGRATION",
            "constitutional_integrity_index": integrity_score,
            "constitutional_benchmark_score": benchmark_score,
            "constitutional_compliance_score": compliance_score,
            "stress_resilience_score": stress_score,
            "constitutional_dashboard_composite_score": composite,
            "constitutional_dashboard_status": status,
            "dashboard_alert": status in ("fragile", "critical"),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
            },
        }
