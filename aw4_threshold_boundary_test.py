from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


SCORE_THRESHOLD_TO_FIELD = {
    "minimum_cohesion": "cohesion_score",
    "minimum_reciprocity": "reciprocity_score",
    "minimum_shared_goal": "shared_goal_score",
    "minimum_coordination": "coordination_score",
    "minimum_temporal_stability": "temporal_stability_score",
    "minimum_resilience": "resilience_score",
    "minimum_boundary": "boundary_score",
    "minimum_evidence_quality": "evidence_quality",
}


def run(detector, context):
    return detector.step(
        inputs=context,
        persist=False,
    )


def main():
    detector = CoalitionDetector()
    thresholds = detector.default_thresholds

    baseline = run(detector, build_context())

    assert baseline["detected_coalition_count"] == 1
    baseline_coalition = baseline["coalitions"][0]

    # Chaque dimension numérique est testée isolément.
    for threshold_name, field_name in SCORE_THRESHOLD_TO_FIELD.items():
        exact = deepcopy(build_context())
        exact["coalition_candidates"][0][field_name] = thresholds[
            threshold_name
        ]

        exact_result = run(detector, exact)

        assert exact_result["detected_coalition_count"] == 1, (
            threshold_name,
            exact_result["coalitions"][0],
        )

        below = deepcopy(exact)
        below["coalition_candidates"][0][field_name] = round(
            thresholds[threshold_name] - 0.000001,
            6,
        )

        below_result = run(detector, below)

        assert below_result["detected_coalition_count"] == 0, (
            threshold_name,
            below_result["coalitions"][0],
        )

    # Frontière du nombre d'observations.
    exact_observations = deepcopy(build_context())
    exact_observations["coalition_candidates"][0][
        "observation_count"
    ] = thresholds["minimum_observations"]

    assert run(
        detector,
        exact_observations,
    )["detected_coalition_count"] == 1

    below_observations = deepcopy(exact_observations)
    below_observations["coalition_candidates"][0][
        "observation_count"
    ] = thresholds["minimum_observations"] - 1

    assert run(
        detector,
        below_observations,
    )["detected_coalition_count"] == 0

    # Frontière de contribution minimale de chaque membre.
    exact_contribution = deepcopy(build_context())
    candidate = exact_contribution["coalition_candidates"][0]
    candidate["member_contributions"] = {
        member: thresholds["minimum_member_contribution"]
        for member in candidate["member_rf_ids"]
    }

    exact_contribution_result = run(
        detector,
        exact_contribution,
    )

    assert (
        exact_contribution_result["detected_coalition_count"] == 1
    )

    below_contribution = deepcopy(exact_contribution)
    first_member = below_contribution[
        "coalition_candidates"
    ][0]["member_rf_ids"][0]

    below_contribution[
        "coalition_candidates"
    ][0]["member_contributions"][first_member] = round(
        thresholds["minimum_member_contribution"] - 0.000001,
        6,
    )

    assert run(
        detector,
        below_contribution,
    )["detected_coalition_count"] == 0

    # Frontière du score global, indépendamment des dimensions.
    baseline_score = baseline_coalition["coalition_score"]

    exact_global = deepcopy(build_context())
    exact_global["thresholds"] = {
        "minimum_coalition_score": baseline_score,
    }

    exact_global_result = run(detector, exact_global)

    assert exact_global_result["detected_coalition_count"] == 1

    above_global = deepcopy(build_context())
    above_global["thresholds"] = {
        "minimum_coalition_score": round(
            baseline_score + 0.000001,
            6,
        ),
    }

    above_global_result = run(detector, above_global)

    assert above_global_result["detected_coalition_count"] == 0

    print("AW4_THRESHOLD_BOUNDARY_OK")


if __name__ == "__main__":
    main()
