from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


def main():
    detector = CoalitionDetector()

    baseline = detector.step(
        inputs=build_context(),
        persist=False,
    )
    assert baseline["detected_coalition_count"] == 1

    threshold_names = [
        "minimum_cohesion",
        "minimum_reciprocity",
        "minimum_shared_goal",
        "minimum_coordination",
        "minimum_temporal_stability",
        "minimum_resilience",
        "minimum_boundary",
        "minimum_member_contribution",
        "minimum_evidence_quality",
        "minimum_coalition_score",
    ]

    for threshold_name in threshold_names:
        context = deepcopy(build_context())
        context["thresholds"] = {
            threshold_name: 0.99,
        }

        result = detector.step(
            inputs=context,
            persist=False,
        )

        assert result["detected_coalition_count"] <= (
            baseline["detected_coalition_count"]
        )

    print("AW4_THRESHOLD_MONOTONICITY_OK")


if __name__ == "__main__":
    main()
