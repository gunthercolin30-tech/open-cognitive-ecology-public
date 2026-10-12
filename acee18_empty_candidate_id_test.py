from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


INVALID_IDS = [
    "",
    "   ",
    None,
]


def main():
    for invalid_id in INVALID_IDS:
        try:
            ACEEPredictionEngine().step(
                inputs={
                    "candidates": [
                        {
                            "candidate_id":
                                invalid_id,
                            "predicted_gain":
                                0.2,
                        }
                    ]
                },
                persist=False,
            )
        except ValueError as exc:
            assert str(exc) == (
                "empty_candidate_id"
            )
        else:
            raise AssertionError(
                f"invalid candidate ID accepted:"
                f"{invalid_id!r}"
            )

    print(
        "ACEE18_EMPTY_CANDIDATE_ID_REJECTED"
    )


if __name__ == "__main__":
    main()
