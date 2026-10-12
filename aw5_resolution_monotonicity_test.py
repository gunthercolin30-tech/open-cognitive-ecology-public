from copy import deepcopy

from aw5_fast_acceptance_suite import build_context
from ontology.conflict_detector import ConflictDetector


def main():
    detector = ConflictDetector()

    detected_counts = []

    for resolution_score in (
        0.0,
        0.25,
        0.50,
        0.75,
        1.0,
    ):
        context = deepcopy(build_context())
        context["conflict_candidates"][0][
            "resolution_score"
        ] = resolution_score

        result = detector.step(
            inputs=context,
            persist=False,
        )

        detected_counts.append(
            result["detected_conflict_count"]
        )

    assert all(
        later <= earlier
        for earlier, later in zip(
            detected_counts,
            detected_counts[1:],
        )
    )

    print("AW5_RESOLUTION_MONOTONICITY_OK")


if __name__ == "__main__":
    main()
