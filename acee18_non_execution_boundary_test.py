from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


FORBIDDEN_TRUE_FIELDS = {
    "execution_authorized",
    "selection_performed",
    "schedule_created",
    "installation_completed",
    "mutation_executed",
    "rollback_performed",
    "code_generated",
    "action_executed",
    "candidate_accepted",
}


def inspect(value, path="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"

            if (
                key in FORBIDDEN_TRUE_FIELDS
                and item is True
            ):
                raise AssertionError(
                    f"forbidden_true:{child_path}"
                )

            inspect(item, child_path)

    elif isinstance(value, list):
        for index, item in enumerate(value):
            inspect(
                item,
                f"{path}[{index}]",
            )


def main():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id":
                        "boundary-candidate",
                    "predicted_gain": 1.0,
                    "confidence": 1.0,
                    "risk": 0.0,
                    "reversibility": 1.0,
                    "validation": 1.0,
                    "robustness": 1.0,
                    "non_closure": 1.0,
                    "governance_compatible": True,
                }
            ]
        },
        persist=False,
    )

    inspect(result)

    assert result[
        "recommended_candidate_id"
    ] == "boundary-candidate"

    assert (
        result["ranked_candidates"][0][
            "recommendation"
        ]
        == "promising_for_selection_review"
    )

    print(
        "ACEE18_NON_EXECUTION_BOUNDARY_OK"
    )


if __name__ == "__main__":
    main()
