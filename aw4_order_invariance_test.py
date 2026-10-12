from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


def main():
    detector = CoalitionDetector()

    first_context = build_context()
    first = detector.step(
        inputs=first_context,
        persist=False,
    )

    second_context = deepcopy(first_context)
    candidate = second_context["coalition_candidates"][0]
    candidate["member_rf_ids"] = list(
        reversed(candidate["member_rf_ids"])
    )
    candidate["source_refs"] = list(
        reversed(candidate["source_refs"])
    )

    second = detector.step(
        inputs=second_context,
        persist=False,
    )

    assert first["detected_coalition_count"] == 1
    assert second["detected_coalition_count"] == 1

    first_coalition = first["coalitions"][0]
    second_coalition = second["coalitions"][0]

    assert (
        first_coalition["member_rf_ids"]
        == second_coalition["member_rf_ids"]
    )
    assert (
        first_coalition["coalition_hash"]
        == second_coalition["coalition_hash"]
    )

    print("AW4_ORDER_INVARIANCE_OK")


if __name__ == "__main__":
    main()
