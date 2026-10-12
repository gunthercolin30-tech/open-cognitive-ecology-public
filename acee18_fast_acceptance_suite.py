#!/usr/bin/env python3
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main() -> None:
    inputs = {
        "candidates": [
            {
                "candidate_id": "safe-high-gain",
                "predicted_gain": 0.24,
                "confidence": 0.91,
                "risk": 0.05,
                "reversibility": 0.97,
                "validation": 0.92,
                "robustness": 0.90,
                "non_closure": 0.96,
                "closure_pressure_delta": -0.02,
            },
            {
                "candidate_id": "risky",
                "predicted_gain": 0.30,
                "confidence": 0.80,
                "risk": 0.75,
                "reversibility": 0.50,
                "validation": 0.68,
                "non_closure": 0.70,
                "closure_pressure_delta": 0.10,
            },
        ]
    }
    result = ACEEPredictionEngine().step(
        inputs=inputs,
        persist=False,
    )
    assert result["status"] == "ACEE_EVOLUTION_PREDICTION_READY"
    assert result["candidate_count"] == 2
    assert result["ranked_candidates"][0]["candidate_id"] == "safe-high-gain"
    assert result["execution_authorized"] is False
    assert result["selection_performed"] is False
    assert result["schedule_created"] is False
    assert result["rollback_performed"] is False
    print("ACEE18_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
