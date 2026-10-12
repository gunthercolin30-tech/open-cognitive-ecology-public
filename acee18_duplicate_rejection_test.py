from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    try:
        ACEEPredictionEngine().step(
            inputs={
                "candidates": [
                    {
                        "candidate_id": "duplicate",
                        "predicted_gain": 0.10,
                    },
                    {
                        "candidate_id": "duplicate",
                        "predicted_gain": 0.30,
                    },
                ]
            },
            persist=False,
        )
    except ValueError as exc:
        assert str(exc) == (
            "duplicate_candidate_id:duplicate"
        )
    else:
        raise AssertionError(
            "duplicate candidate_id was accepted"
        )

    print(
        "ACEE18_DUPLICATE_REJECTION_OK"
    )


if __name__ == "__main__":
    main()
