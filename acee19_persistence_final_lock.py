import json
from pathlib import Path

from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {
                    "observation_id": "persistent-1",
                    "effect_size": 0.18,
                    "variance": 0.04,
                    "confidence": 0.90,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                },
                {
                    "observation_id": "persistent-2",
                    "effect_size": 0.22,
                    "variance": 0.05,
                    "confidence": 0.88,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                },
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

    assert payload["persist_requested"] is True
    assert payload["persisted"] is True
    assert payload["analysis_hash"] == (
        result["analysis_hash"]
    )

    assert payload["certification_performed"] is False
    assert payload["selection_performed"] is False
    assert payload["execution_authorized"] is False
    assert payload["rollback_performed"] is False

    print("ACEE19_PERSISTENCE_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
