#!/usr/bin/env python3
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main() -> None:
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {"candidate_id": "a", "predicted_gain": 0.20, "confidence": 0.9, "risk": 0.05},
                {"candidate_id": "b", "predicted_gain": 0.10, "confidence": 0.8, "risk": 0.01},
            ]
        },
        persist=False,
    )
    assert [item["rank"] for item in result["ranked_candidates"]] == [1, 2]
    assert result["recommended_candidate_id"] == result["ranked_candidates"][0]["candidate_id"]
    assert ACEEPredictionEngine().verify_prediction(result)["verified"] is True
    print("ACEE18_FUNCTIONAL_TEST_OK")


if __name__ == "__main__":
    main()
