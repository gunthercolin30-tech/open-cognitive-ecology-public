import json
from pathlib import Path

from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    result = ACEEPredictionEngine().step(
        inputs={
            "candidates": [
                {
                    "candidate_id": "persistent-candidate",
                    "predicted_gain": 0.18,
                    "confidence": 0.88,
                    "risk": 0.08,
                    "reversibility": 0.95,
                    "validation": 0.91,
                    "non_closure": 0.96,
                }
            ]
        },
        persist=True,
    )

    path = Path(
        result["artifacts"]["json_path"]
    ).resolve()

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert payload["persisted"] is True
    assert payload["persist_requested"] is True
    assert payload["prediction_hash"] == (
        result["prediction_hash"]
    )
    assert payload["execution_authorized"] is False
    assert payload["selection_performed"] is False
    assert payload["schedule_created"] is False
    assert payload["rollback_performed"] is False

    print("ACEE18_PERSISTENCE_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
