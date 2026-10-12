from copy import deepcopy

from aw6_fast_acceptance_suite import build_context
from ontology.reference_frame_merging import ReferenceFrameMerging


def main():
    detector = ReferenceFrameMerging()

    baseline = detector.step(
        inputs=build_context(),
        persist=False,
    )
    assert baseline["detected_merge_count"] == 1

    unregistered = deepcopy(build_context())
    unregistered["merge_candidates"][0][
        "successor_rf_id"
    ] = "RF-NOT-REGISTERED"

    unregistered_result = detector.step(
        inputs=unregistered,
        persist=False,
    )

    assert unregistered_result["detected_merge_count"] == 0
    assert unregistered_result["merges"][0][
        "successor_registered"
    ] is False

    same_as_source = deepcopy(build_context())
    same_as_source["merge_candidates"][0][
        "successor_rf_id"
    ] = "RF-A"

    same_result = detector.step(
        inputs=same_as_source,
        persist=False,
    )

    assert same_result["detected_merge_count"] == 0
    assert same_result["merges"][0][
        "successor_distinct"
    ] is False

    missing = deepcopy(build_context())
    missing["merge_candidates"][0]["successor_rf_id"] = ""

    missing_result = detector.step(
        inputs=missing,
        persist=False,
    )

    assert missing_result["detected_merge_count"] == 0

    print("AW6_SUCCESSOR_INTEGRITY_OK")


if __name__ == "__main__":
    main()
