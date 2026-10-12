from copy import deepcopy

from aw4_fast_acceptance_suite import build_context
from ontology.coalition_detector import CoalitionDetector


def coalition(context):
    result = CoalitionDetector().step(
        inputs=context,
        persist=False,
    )
    assert result["coalitions"]
    return result["coalitions"][0]


def main():
    baseline_context = build_context()
    baseline = coalition(baseline_context)

    reordered_context = deepcopy(baseline_context)
    candidate = reordered_context["coalition_candidates"][0]
    candidate["member_rf_ids"] = list(
        reversed(candidate["member_rf_ids"])
    )
    candidate["source_refs"] = list(
        reversed(candidate["source_refs"])
    )

    reordered = coalition(reordered_context)

    assert (
        baseline["coalition_hash"]
        == reordered["coalition_hash"]
    )

    changed_context = deepcopy(baseline_context)
    changed_context["coalition_candidates"][0][
        "resilience_score"
    ] = 0.81

    changed = coalition(changed_context)

    assert (
        baseline["coalition_hash"]
        != changed["coalition_hash"]
    )

    changed_contribution_context = deepcopy(baseline_context)
    changed_contribution_context[
        "coalition_candidates"
    ][0]["member_contributions"]["RF-A"] = 0.77

    changed_contribution = coalition(
        changed_contribution_context
    )

    assert (
        baseline["coalition_hash"]
        != changed_contribution["coalition_hash"]
    )

    print("AW4_HASH_SCOPE_OK")


if __name__ == "__main__":
    main()
