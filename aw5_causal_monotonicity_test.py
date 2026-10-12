from copy import deepcopy

from aw5_fast_acceptance_suite import build_context
from ontology.conflict_detector import ConflictDetector


CAUSAL_FIELDS = [
    "constraint_incompatibility_score",
    "goal_incompatibility_score",
    "resource_contention_score",
    "mutual_blocking_score",
]


def main():
    detector = ConflictDetector()
    counts = []

    for enabled_count in range(0, len(CAUSAL_FIELDS) + 1):
        context = deepcopy(build_context())
        candidate = context["conflict_candidates"][0]

        for field_name in CAUSAL_FIELDS:
            candidate[field_name] = 0.0

        for field_name in CAUSAL_FIELDS[:enabled_count]:
            candidate[field_name] = 1.0

        result = detector.step(
            inputs=context,
            persist=False,
        )

        counts.append(
            result["conflicts"][0][
                "causal_dimension_count"
            ]
        )

    assert counts == sorted(counts)
    assert counts == list(range(len(CAUSAL_FIELDS) + 1))

    print("AW5_CAUSAL_MONOTONICITY_OK")


if __name__ == "__main__":
    main()
