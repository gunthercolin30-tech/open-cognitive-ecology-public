from copy import deepcopy

from aw7_fast_acceptance_suite import build_context
from ontology.reference_frame_fragmentation import (
    ReferenceFrameFragmentation,
)


def main():
    detector = ReferenceFrameFragmentation()

    unknown = deepcopy(build_context())
    unknown["fragmentation_candidates"][0][
        "source_rf_id"
    ] = "RF-UNKNOWN"

    unknown_result = detector.step(
        inputs=unknown,
        persist=False,
    )

    assert unknown_result["detected_fragmentation_count"] == 0
    assert unknown_result["fragmentations"][0][
        "source_registered"
    ] is False

    missing = deepcopy(build_context())
    missing["fragmentation_candidates"][0]["source_rf_id"] = ""

    missing_result = detector.step(
        inputs=missing,
        persist=False,
    )

    assert missing_result["detected_fragmentation_count"] == 0

    overlaps = deepcopy(build_context())
    candidate = overlaps["fragmentation_candidates"][0]
    candidate["descendant_rf_ids"][0] = candidate["source_rf_id"]

    overlaps_result = detector.step(
        inputs=overlaps,
        persist=False,
    )

    assert overlaps_result["detected_fragmentation_count"] == 0

    print("AW7_SOURCE_INTEGRITY_OK")


if __name__ == "__main__":
    main()
