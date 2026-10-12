#!/usr/bin/env python3
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main() -> None:
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id": "degraded",
                    "predicted_gain": float("nan"),
                    "confidence": float("inf"),
                    "risk": True,
                    "closure_pressure_delta": "bad",
                    "required_evidence": "replication",
                }
            ]
        },
        persist=False,
    )
    item = result["ranked_candidates"][0]
    assert item["predicted_gain"] == 0.0
    assert item["confidence"] == 0.5
    assert item["risk"] == 0.0
    assert item["closure_pressure_delta"] == 0.0
    assert item["required_evidence"] == ["replication"]
    print("ACEE18_DEGRADATION_TEST_OK")


if __name__ == "__main__":
    main()
