from copy import deepcopy

from aw5_fast_acceptance_suite import build_context
from ontology.conflict_detector import ConflictDetector


def main():
    detector = ConflictDetector()

    missing = deepcopy(build_context())
    missing["conflict_candidates"][0][
        "participant_rf_ids"
    ].append("RF-UNKNOWN")

    missing_result = detector.step(
        inputs=missing,
        persist=False,
    )

    assert missing_result["detected_conflict_count"] == 0
    assert missing_result["conflicts"][0][
        "missing_participant_rf_ids"
    ] == ["RF-UNKNOWN"]

    duplicate = deepcopy(build_context())
    duplicate["conflict_candidates"][0]["participant_rf_ids"] = [
        "RF-A",
        "RF-A",
        "RF-B",
    ]

    duplicate_result = detector.step(
        inputs=duplicate,
        persist=False,
    )

    assert duplicate_result["conflicts"][0]["participant_count"] == 2
    assert duplicate_result["detected_conflict_count"] == 1

    singleton = deepcopy(build_context())
    singleton["conflict_candidates"][0]["participant_rf_ids"] = [
        "RF-A"
    ]

    singleton_result = detector.step(
        inputs=singleton,
        persist=False,
    )

    assert singleton_result["detected_conflict_count"] == 0
    assert singleton_result["conflicts"][0]["participant_count"] == 1

    print("AW5_PARTICIPANT_INTEGRITY_OK")


if __name__ == "__main__":
    main()
