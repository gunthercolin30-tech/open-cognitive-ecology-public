from copy import deepcopy

from aw7_fast_acceptance_suite import build_context
from ontology.reference_frame_fragmentation import (
    ReferenceFrameFragmentation,
)


MINIMUM_FIELDS = {
    "minimum_lineage_traceability": "lineage_traceability_score",
    "minimum_descendant_divergence": "descendant_divergence_score",
    "minimum_source_unity_reduction": "source_unity_reduction_score",
    "minimum_information_redistribution": "information_redistribution_score",
    "minimum_functional_impact": "functional_impact_score",
    "minimum_temporal_stability": "temporal_stability_score",
    "minimum_evidence_quality": "evidence_quality",
}


def run(detector, context):
    return detector.step(
        inputs=context,
        persist=False,
    )


def main():
    detector = ReferenceFrameFragmentation()
    thresholds = detector.default_thresholds

    baseline = run(detector, build_context())
    assert baseline["detected_fragmentation_count"] == 1

    for threshold_name, field_name in MINIMUM_FIELDS.items():
        exact = deepcopy(build_context())
        exact["fragmentation_candidates"][0][field_name] = thresholds[
            threshold_name
        ]

        exact_result = run(detector, exact)
        assert exact_result["detected_fragmentation_count"] == 1, (
            threshold_name,
            exact_result["fragmentations"][0],
        )

        below = deepcopy(exact)
        below["fragmentation_candidates"][0][field_name] = round(
            thresholds[threshold_name] - 0.000001,
            6,
        )

        below_result = run(detector, below)
        assert below_result["detected_fragmentation_count"] == 0, (
            threshold_name,
            below_result["fragmentations"][0],
        )

    exact_observations = deepcopy(build_context())
    exact_observations["fragmentation_candidates"][0][
        "observation_count"
    ] = thresholds["minimum_observations"]

    assert run(
        detector,
        exact_observations,
    )["detected_fragmentation_count"] == 1

    below_observations = deepcopy(exact_observations)
    below_observations["fragmentation_candidates"][0][
        "observation_count"
    ] -= 1

    assert run(
        detector,
        below_observations,
    )["detected_fragmentation_count"] == 0

    baseline_score = baseline["fragmentations"][0][
        "fragmentation_score"
    ]

    exact_global = deepcopy(build_context())
    exact_global["thresholds"] = {
        "minimum_fragmentation_score": baseline_score,
    }

    assert run(
        detector,
        exact_global,
    )["detected_fragmentation_count"] == 1

    above_global = deepcopy(build_context())
    above_global["thresholds"] = {
        "minimum_fragmentation_score": round(
            baseline_score + 0.000001,
            6,
        ),
    }

    assert run(
        detector,
        above_global,
    )["detected_fragmentation_count"] == 0

    print("AW7_THRESHOLD_BOUNDARY_OK")


if __name__ == "__main__":
    main()
