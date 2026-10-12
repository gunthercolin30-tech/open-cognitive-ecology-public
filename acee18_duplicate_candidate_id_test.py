from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id": "duplicate",
                    "predicted_gain": 0.10,
                    "risk": 0.05,
                },
                {
                    "candidate_id": "duplicate",
                    "predicted_gain": 0.30,
                    "risk": 0.05,
                },
            ]
        },
        persist=False,
    )

    ids = [
        item["candidate_id"]
        for item in result["ranked_candidates"]
    ]

    duplicate_count = (
        len(ids) - len(set(ids))
    )

    print({
        "candidate_count":
            result["candidate_count"],
        "candidate_ids": ids,
        "duplicate_count":
            duplicate_count,
        "prediction_hash":
            result["prediction_hash"],
    })

    if duplicate_count:
        print(
            "ACEE18_DUPLICATE_CANDIDATE_ID_GAP_DETECTED"
        )
    else:
        print(
            "ACEE18_DUPLICATE_CANDIDATE_ID_OK"
        )


if __name__ == "__main__":
    main()
