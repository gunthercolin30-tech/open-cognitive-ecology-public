from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


def main():
    detector = CoalitionDetector()

    missing = deepcopy(build_context())
    missing_candidate = missing["coalition_candidates"][0]
    missing_candidate["member_rf_ids"].append("RF-UNKNOWN")
    missing_candidate["member_contributions"]["RF-UNKNOWN"] = 0.9

    missing_result = detector.step(
        inputs=missing,
        persist=False,
    )

    assert missing_result["detected_coalition_count"] == 0
    assert missing_result["coalitions"][0][
        "missing_member_rf_ids"
    ] == ["RF-UNKNOWN"]

    duplicate = deepcopy(build_context())
    duplicate_candidate = duplicate["coalition_candidates"][0]
    duplicate_candidate["member_rf_ids"] = [
        "RF-A",
        "RF-A",
        "RF-B",
        "RF-C",
    ]

    duplicate_result = detector.step(
        inputs=duplicate,
        persist=False,
    )

    assert duplicate_result["coalitions"][0]["member_count"] == 3
    assert duplicate_result["detected_coalition_count"] == 1

    singleton = deepcopy(build_context())
    singleton_candidate = singleton["coalition_candidates"][0]
    singleton_candidate["member_rf_ids"] = ["RF-A"]
    singleton_candidate["member_contributions"] = {"RF-A": 0.9}

    singleton_result = detector.step(
        inputs=singleton,
        persist=False,
    )

    assert singleton_result["detected_coalition_count"] == 0
    assert singleton_result["coalitions"][0]["member_count"] == 1

    print("AW4_MEMBERSHIP_INTEGRITY_OK")


if __name__ == "__main__":
    main()
