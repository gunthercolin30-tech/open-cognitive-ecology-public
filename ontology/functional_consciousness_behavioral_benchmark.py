"""
Functional Consciousness Behavioral Benchmark.

Computes a quantitative benchmark score from core functional criteria
associated with consciousness-like cognitive organization.

This module does not claim subjective experience. It operationalizes
only functional indicators.
"""

PRIMITIVE = "functional_consciousness_behavioral_benchmark"

DEPENDENCIES = [
    "self_model",
    "autobiographical_memory",
    "temporal_self_continuity",
    "introspective_reporting",
    "uncertainty_awareness",
    "internal_conflict_monitoring",
    "reflective_goal_revision",
    "conscious_decision_trace",
    "consciousness_readiness_index",
]


def _clamp(value):
    try:
        value = float(value)
    except Exception:
        return 0.0

    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _extract_signal(state, key):
    if key in state:
        return _clamp(state[key])

    value = state.get(key + "_score")
    if value is not None:
        return _clamp(value)

    if isinstance(state.get(key), dict):
        nested = state[key]
        for nested_key in ("score", "value", "normalized_score"):
            if nested_key in nested:
                return _clamp(nested[nested_key])

    return 0.0


def evaluate(state):
    criteria = [
        "self_model",
        "autobiographical_memory",
        "temporal_self_continuity",
        "introspective_reporting",
        "uncertainty_awareness",
        "internal_conflict_monitoring",
        "reflective_goal_revision",
        "conscious_decision_trace",
    ]

    criterion_scores = {
        key: _extract_signal(state, key)
        for key in criteria
    }

    readiness = _extract_signal(
        state,
        "consciousness_readiness_index",
    )

    average_core = (
        sum(criterion_scores.values()) /
        len(criterion_scores)
    )

    benchmark_score = (
        0.8 * average_core +
        0.2 * readiness
    )

    if benchmark_score < 0.50:
        classification = (
            "Emerging Functional Consciousness"
        )
    elif benchmark_score < 0.80:
        classification = (
            "Robust Functional Consciousness"
        )
    else:
        classification = (
            "Advanced Functional Consciousness"
        )

    return {
        "primitive": PRIMITIVE,
        "criterion_scores": criterion_scores,
        "consciousness_readiness_index": readiness,
        "functional_consciousness_benchmark_score":
            round(benchmark_score, 6),
        "classification": classification,
    }


class FunctionalConsciousnessBehavioralBenchmark:
    """Auto-generated activation class for functional_consciousness_behavioral_benchmark."""

    PRIMITIVE = "functional_consciousness_behavioral_benchmark"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

