from pprint import pprint

from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id": "candidate-safe",
                    "predicted_gain": 0.22,
                    "confidence": 0.91,
                    "risk": 0.06,
                    "reversibility": 0.96,
                    "validation": 0.92,
                    "robustness": 0.90,
                    "non_closure": 0.97,
                    "closure_pressure_delta": -0.02,
                    "recommended_horizon": "next_cycle",
                },
                {
                    "candidate_id": "candidate-risky",
                    "predicted_gain": 0.30,
                    "confidence": 0.72,
                    "risk": 0.68,
                    "reversibility": 0.48,
                    "validation": 0.64,
                    "robustness": 0.55,
                    "non_closure": 0.62,
                    "closure_pressure_delta": 0.12,
                    "recommended_horizon": "sandbox_longer",
                },
            ]
        },
        persist=False,
    )

    pprint({
        "status": result["status"],
        "candidate_count": result["candidate_count"],
        "recommended_candidate_id":
            result["recommended_candidate_id"],
        "ranked_candidates":
            result["ranked_candidates"],
        "execution_authorized":
            result["execution_authorized"],
        "selection_performed":
            result["selection_performed"],
    })


if __name__ == "__main__":
    main()
