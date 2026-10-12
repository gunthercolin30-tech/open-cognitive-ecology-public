from copy import deepcopy

from aw7_fast_acceptance_suite import build_context
from ontology.reference_frame_fragmentation import (
    ReferenceFrameFragmentation,
)


def main():
    detector = ReferenceFrameFragmentation()
    thresholds = detector.default_thresholds

    exact = deepcopy(build_context())
    candidate = exact["fragmentation_candidates"][0]

    candidate["descendant_contributions"] = {
        descendant: thresholds["minimum_descendant_contribution"]
        for descendant in candidate["descendant_rf_ids"]
    }

    exact_result = detector.step(
        inputs=exact,
        persist=False,
    )

    assert exact_result["detected_fragmentation_count"] == 1

    below = deepcopy(exact)
    first_descendant = below["fragmentation_candidates"][0][
        "descendant_rf_ids"
    ][0]

    below["fragmentation_candidates"][0][
        "descendant_contributions"
    ][first_descendant] = round(
        thresholds["minimum_descendant_contribution"] - 0.000001,
        6,
    )

    below_result = detector.step(
        inputs=below,
        persist=False,
    )

    assert below_result["detected_fragmentation_count"] == 0

    missing = deepcopy(build_context())
    first_descendant = missing["fragmentation_candidates"][0][
        "descendant_rf_ids"
    ][0]

    del missing["fragmentation_candidates"][0][
        "descendant_contributions"
    ][first_descendant]

    missing_result = detector.step(
        inputs=missing,
        persist=False,
    )

    assert missing_result["detected_fragmentation_count"] == 0
    assert missing_result["fragmentations"][0][
        "minimum_descendant_contribution"
    ] == 0.0

    print("AW7_DESCENDANT_CONTRIBUTION_OK")


if __name__ == "__main__":
    main()
