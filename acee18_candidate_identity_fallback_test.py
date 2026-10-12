#!/usr/bin/env python3
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {"mutation_id": "mutation-fallback", "predicted_gain": 0.2},
                {"trajectory_id": "trajectory-fallback", "predicted_gain": 0.18},
                {"name": "name-fallback", "predicted_gain": 0.16},
                {"predicted_gain": 0.14},
            ]
        },
        persist=False,
    )

    ids = {
        item["candidate_id"]
        for item in result["ranked_candidates"]
    }

    assert "mutation-fallback" in ids
    assert "trajectory-fallback" in ids
    assert "name-fallback" in ids
    assert "candidate-0004" in ids

    print("ACEE18_CANDIDATE_ID_FALLBACK_OK")


if __name__ == "__main__":
    main()
