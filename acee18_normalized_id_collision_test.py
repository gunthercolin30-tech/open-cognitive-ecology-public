from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    try:
        ACEEPredictionEngine().step(
            inputs={
                "candidates": [
                    {
                        "candidate_id":
                            "candidate-a",
                        "predicted_gain": 0.1,
                    },
                    {
                        "candidate_id":
                            " candidate-a ",
                        "predicted_gain": 0.2,
                    },
                ]
            },
            persist=False,
        )
    except ValueError as exc:
        assert str(exc) == (
            "duplicate_candidate_id:"
            "candidate-a"
        )
    else:
        raise AssertionError(
            "normalized ID collision accepted"
        )

    print(
        "ACEE18_NORMALIZED_ID_COLLISION_OK"
    )


if __name__ == "__main__":
    main()
