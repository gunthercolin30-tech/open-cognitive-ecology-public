from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id":
                        "explicit-only",
                    "predicted_gain": 0.2,
                }
            ],
            "improvement_plan": {
                "projected_gain": 0.9,
                "improvement_confidence": 1.0,
                "recommended_actions": [
                    {
                        "recommended_action":
                            "derived-candidate"
                    }
                ],
            },
        },
        persist=False,
    )

    ids = [
        item["candidate_id"]
        for item in result[
            "ranked_candidates"
        ]
    ]

    assert ids == ["explicit-only"]
    assert result["candidate_count"] == 1

    print(
        "ACEE18_EXPLICIT_CANDIDATE_PRECEDENCE_OK"
    )


if __name__ == "__main__":
    main()
