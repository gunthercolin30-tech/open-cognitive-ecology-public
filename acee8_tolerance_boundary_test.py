from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ontology.acee_impact_evaluator import AceeImpactEvaluator


def base_context() -> dict:
    return {
        "evaluation_id": "tolerance-boundary",
        "timestamp_utc": "2026-07-13T21:00:00Z",
        "neutral_tolerance": 0.0625,
        "before": {
            "validation": {
                "error_count": 0,
                "modules_discovered": 1200,
                "active_primitives": 1100,
                "validation_passed": True,
            },
            "stability_score": 0.8,
            "governance_score": 0.9,
            "evolution_score": 0.7,
            "closure_pressure": 0.2,
            "runtime_score": 0.9,
        },
        "after": {
            "validation": {
                "error_count": 0,
                "modules_discovered": 1200,
                "active_primitives": 1100,
                "validation_passed": True,
            },
            "stability_score": 0.8,
            "governance_score": 0.9,
            "evolution_score": 0.7,
            "closure_pressure": 0.2,
            "runtime_score": 0.9,
        },
    }


def classify(metric: str, before: float, after: float) -> str:
    context = base_context()
    context["before"][metric] = before
    context["after"][metric] = after
    result = AceeImpactEvaluator(root=Path("/nonexistent")).step(
        inputs=context,
        persist=False,
    )
    assert result["comparison_valid"] is True
    return result["metric_classifications"][metric]


def main() -> None:
    # Binary fractions avoid floating-point ambiguity at exact boundaries.
    tolerance = 0.0625
    epsilon = 0.015625

    # higher_is_better: strict comparison around neutral_tolerance.
    assert classify("stability_score", 0.5, 0.5) == "unchanged"
    assert classify("stability_score", 0.5, 0.5 + tolerance) == "unchanged"
    assert classify("stability_score", 0.5, 0.5 + tolerance - epsilon) == "unchanged"
    assert classify("stability_score", 0.5, 0.5 + tolerance + epsilon) == "improved"
    assert classify("stability_score", 0.5, 0.5 - tolerance) == "unchanged"
    assert classify("stability_score", 0.5, 0.5 - tolerance - epsilon) == "regressed"

    # lower_is_better: direction must be inverted without changing boundaries.
    assert classify("closure_pressure", 0.5, 0.5) == "unchanged"
    assert classify("closure_pressure", 0.5, 0.5 - tolerance) == "unchanged"
    assert classify("closure_pressure", 0.5, 0.5 - tolerance - epsilon) == "improved"
    assert classify("closure_pressure", 0.5, 0.5 + tolerance) == "unchanged"
    assert classify("closure_pressure", 0.5, 0.5 + tolerance + epsilon) == "regressed"

    # Tolerance is bounded by the public contract to [0.0, 0.1].
    above_bound = base_context()
    above_bound["neutral_tolerance"] = 1.0
    above_bound["after"]["stability_score"] = 0.89
    bounded = AceeImpactEvaluator(root=Path("/nonexistent")).step(
        inputs=above_bound,
        persist=False,
    )
    assert bounded["metric_classifications"]["stability_score"] == "unchanged"

    print("ACEE8_TOLERANCE_BOUNDARY_OK")


if __name__ == "__main__":
    main()
