from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


def main():
    detector = CoalitionDetector()

    invalid_values = [
        float("nan"),
        float("inf"),
        float("-inf"),
        "not-a-number",
        None,
    ]

    for value in invalid_values:
        context = deepcopy(build_context())
        context["coalition_candidates"][0][
            "cohesion_score"
        ] = value

        result = detector.step(
            inputs=context,
            persist=False,
        )

        assert result["detected_coalition_count"] == 0
        assert result["coalitions"][0]["cohesion_score"] == 0.0

    high = deepcopy(build_context())
    high["coalition_candidates"][0]["cohesion_score"] = 100
    high_result = detector.step(
        inputs=high,
        persist=False,
    )
    assert high_result["coalitions"][0]["cohesion_score"] == 1.0

    low = deepcopy(build_context())
    low["coalition_candidates"][0]["cohesion_score"] = -100
    low_result = detector.step(
        inputs=low,
        persist=False,
    )
    assert low_result["coalitions"][0]["cohesion_score"] == 0.0
    assert low_result["detected_coalition_count"] == 0

    print("AW4_NUMERIC_ROBUSTNESS_OK")


if __name__ == "__main__":
    main()
