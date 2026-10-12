#!/usr/bin/env python3
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main() -> None:
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id": "candidate-a",
                    "predicted_gain": 0.10,
                    "confidence": 0.90,
                    "risk": 0.10,
                    "reversibility": 0.95,
                    "validation": 0.90,
                    "non_closure": 0.95,
                    "closure_pressure_delta": 0.0,
                }
            ]
        },
        persist=False,
    )
    assert result["prediction_ready"] is True
    assert result["epistemic_status"]["functional_conclusion_only"] is True
    assert result["epistemic_status"]["phenomenology_undetermined"] is True
    for field in (
        "execution_authorized",
        "selection_performed",
        "schedule_created",
        "installation_completed",
        "mutation_executed",
        "rollback_performed",
    ):
        assert result[field] is False
    print("ACEE_EVOLUTION_PREDICTION_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
