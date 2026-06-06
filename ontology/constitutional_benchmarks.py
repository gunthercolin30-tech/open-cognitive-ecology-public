"""
Constitutional Benchmarks.
"""

from __future__ import annotations

PRIMITIVE = "constitutional_benchmarks"

DEPENDENCIES = [
    "constitutional_integrity_index",
    "constitutional_stress_tests",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConstitutionalBenchmarks:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(self, scenarios=None):
        if scenarios is None:
            scenarios = [
                {"constitutional_integrity_index": 0.95},
                {"constitutional_integrity_index": 0.90},
                {"constitutional_integrity_index": 0.85},
                {"constitutional_integrity_index": 0.80},
            ]

        scores = []
        for scenario in scenarios:
            if isinstance(scenario, dict):
                score = scenario.get(
                    "constitutional_integrity_index",
                    scenario.get("integrity_score", 0.0),
                )
            else:
                score = scenario
            scores.append(_clamp(score))

        if not scores:
            scores = [0.0]

        mean_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        robustness = min_score
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        stability = _clamp(1.0 - variance)

        violations = sum(1 for s in scores if s < 0.75)
        violation_rate = violations / len(scores)

        benchmark_score = _clamp(
            0.4 * mean_score
            + 0.3 * robustness
            + 0.2 * stability
            + 0.1 * (1.0 - violation_rate)
        )

        if benchmark_score >= 0.95:
            classification = "Constitutionally Exemplary"
        elif benchmark_score >= 0.90:
            classification = "Constitutionally Robust"
        elif benchmark_score >= 0.80:
            classification = "Constitutionally Stable"
        elif benchmark_score >= 0.70:
            classification = "Constitutionally Fragile"
        else:
            classification = "Constitutionally Non-Compliant"

        return {
            "primitive": "CONSTITUTIONAL_BENCHMARKS",
            "constitutional_benchmark_score": benchmark_score,
            "mean_integrity": mean_score,
            "robustness": robustness,
            "stability": stability,
            "min_integrity": min_score,
            "max_integrity": max_score,
            "violation_count": violations,
            "violation_rate": violation_rate,
            "classification": classification,
            "constitutional_compliance": benchmark_score >= 0.80,
            "diagnostics": {
                "scenario_count": len(scores),
                "scores": scores,
                "dependencies": DEPENDENCIES,
            },
        }
