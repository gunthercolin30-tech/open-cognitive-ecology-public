from copy import deepcopy

from aw6_fast_acceptance_suite import build_context
from ontology.reference_frame_merging import ReferenceFrameMerging


def main():
    detector = ReferenceFrameMerging()

    # Source inconnue.
    unknown = deepcopy(build_context())
    candidate = unknown["merge_candidates"][0]
    candidate["source_rf_ids"].append("RF-UNKNOWN")
    candidate["source_contributions"]["RF-UNKNOWN"] = 0.8

    unknown_result = detector.step(
        inputs=unknown,
        persist=False,
    )

    assert unknown_result["detected_merge_count"] == 0
    assert unknown_result["merges"][0][
        "missing_source_rf_ids"
    ] == ["RF-UNKNOWN"]

    # Source dupliquée : canonicalisation attendue.
    duplicate = deepcopy(build_context())
    duplicate["merge_candidates"][0]["source_rf_ids"] = [
        "RF-A",
        "RF-A",
        "RF-B",
    ]

    duplicate_result = detector.step(
        inputs=duplicate,
        persist=False,
    )

    assert duplicate_result["detected_merge_count"] == 1
    assert duplicate_result["merges"][0]["source_count"] == 2
    assert duplicate_result["merges"][0]["source_rf_ids"] == [
        "RF-A",
        "RF-B",
    ]

    # Une seule source ne constitue jamais une fusion.
    singleton = deepcopy(build_context())
    candidate = singleton["merge_candidates"][0]
    candidate["source_rf_ids"] = ["RF-A"]
    candidate["source_contributions"] = {"RF-A": 0.9}

    singleton_result = detector.step(
        inputs=singleton,
        persist=False,
    )

    assert singleton_result["detected_merge_count"] == 0
    assert singleton_result["merges"][0]["source_count"] == 1

    # Contribution manquante pour une source.
    missing_contribution = deepcopy(build_context())
    del missing_contribution["merge_candidates"][0][
        "source_contributions"
    ]["RF-B"]

    missing_contribution_result = detector.step(
        inputs=missing_contribution,
        persist=False,
    )

    assert missing_contribution_result["detected_merge_count"] == 0
    assert missing_contribution_result["merges"][0][
        "minimum_source_contribution"
    ] == 0.0

    print("AW6_SOURCE_INTEGRITY_OK")


if __name__ == "__main__":
    main()
