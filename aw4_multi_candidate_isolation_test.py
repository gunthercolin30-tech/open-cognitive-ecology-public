from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


def main():
    context = build_context()

    valid_candidate = deepcopy(
        context["coalition_candidates"][0]
    )
    valid_candidate["coalition_id"] = "COAL-VALID"

    invalid_candidate = deepcopy(valid_candidate)
    invalid_candidate["coalition_id"] = "COAL-INVALID"
    invalid_candidate["resilience_score"] = 0.1
    invalid_candidate["false_positive_blockers"] = {
        "common_controller": True,
    }

    context["coalition_candidates"] = [
        invalid_candidate,
        valid_candidate,
    ]

    result = CoalitionDetector().step(
        inputs=context,
        persist=False,
    )

    assert result["detected_coalition_count"] == 1
    assert len(result["coalitions"]) == 2

    by_id = {
        item["coalition_id"]: item
        for item in result["coalitions"]
    }

    assert by_id["COAL-VALID"]["detected"] is True
    assert by_id["COAL-INVALID"]["detected"] is False

    assert (
        by_id["COAL-VALID"]["coalition_hash"]
        != by_id["COAL-INVALID"]["coalition_hash"]
    )

    print("AW4_MULTI_CANDIDATE_ISOLATION_OK")


if __name__ == "__main__":
    main()
