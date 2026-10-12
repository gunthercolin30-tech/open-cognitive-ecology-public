from copy import deepcopy

from aw6_fast_acceptance_suite import build_context
from ontology.reference_frame_merging import ReferenceFrameMerging


MINIMUM_FIELDS = {
    "minimum_compatibility": "compatibility_score",
    "minimum_structural_conservation": "structural_conservation_score",
    "minimum_functional_continuity": "functional_continuity_score",
    "minimum_lineage_traceability": "lineage_traceability_score",
    "minimum_source_independence_reduction":
        "source_independence_reduction_score",
    "minimum_temporal_stability": "temporal_stability_score",
    "minimum_evidence_quality": "evidence_quality",
}


def run(detector, context):
    return detector.step(inputs=context, persist=False)


def main():
    detector = ReferenceFrameMerging()
    thresholds = detector.default_thresholds

    baseline = run(detector, build_context())
    assert baseline["detected_merge_count"] == 1

    # Seuils minimaux individuels.
    for threshold_name, field_name in MINIMUM_FIELDS.items():
        exact = deepcopy(build_context())
        exact["merge_candidates"][0][field_name] = thresholds[
            threshold_name
        ]

        exact_result = run(detector, exact)
        assert exact_result["detected_merge_count"] == 1, (
            threshold_name,
            exact_result["merges"][0],
        )

        below = deepcopy(exact)
        below["merge_candidates"][0][field_name] = round(
            thresholds[threshold_name] - 0.000001,
            6,
        )

        below_result = run(detector, below)
        assert below_result["detected_merge_count"] == 0, (
            threshold_name,
            below_result["merges"][0],
        )

    # Contribution minimale de chaque source.
    exact_contribution = deepcopy(build_context())
    candidate = exact_contribution["merge_candidates"][0]
    candidate["source_contributions"] = {
        source: thresholds["minimum_source_contribution"]
        for source in candidate["source_rf_ids"]
    }

    assert run(
        detector,
        exact_contribution,
    )["detected_merge_count"] == 1

    below_contribution = deepcopy(exact_contribution)
    below_contribution["merge_candidates"][0][
        "source_contributions"
    ]["RF-A"] = round(
        thresholds["minimum_source_contribution"] - 0.000001,
        6,
    )

    assert run(
        detector,
        below_contribution,
    )["detected_merge_count"] == 0

    # Nombre d’observations.
    exact_observations = deepcopy(build_context())
    exact_observations["merge_candidates"][0]["observation_count"] = (
        thresholds["minimum_observations"]
    )

    assert run(
        detector,
        exact_observations,
    )["detected_merge_count"] == 1

    below_observations = deepcopy(exact_observations)
    below_observations["merge_candidates"][0]["observation_count"] -= 1

    assert run(
        detector,
        below_observations,
    )["detected_merge_count"] == 0

    # Score global.
    baseline_score = baseline["merges"][0]["merge_score"]

    exact_global = deepcopy(build_context())
    exact_global["thresholds"] = {
        "minimum_merge_score": baseline_score,
    }

    assert run(
        detector,
        exact_global,
    )["detected_merge_count"] == 1

    above_global = deepcopy(build_context())
    above_global["thresholds"] = {
        "minimum_merge_score": round(
            baseline_score + 0.000001,
            6,
        ),
    }

    assert run(
        detector,
        above_global,
    )["detected_merge_count"] == 0

    print("AW6_THRESHOLD_BOUNDARY_OK")


if __name__ == "__main__":
    main()
