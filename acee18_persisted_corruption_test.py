import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = (
            root
            / "acee_runtime"
            / "ACEE18_acee_prediction_engine"
        )

        engine = ACEEPredictionEngine(
            root=root,
            runtime_dir=runtime,
        )

        result = engine.step(
            inputs={
                "candidates": [
                    {
                        "candidate_id":
                            "corruption-target",
                        "predicted_gain": 0.2,
                        "risk": 0.1,
                    }
                ]
            },
            persist=True,
        )

        path = Path(
            result["artifacts"]["json_path"]
        )

        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

        payload["ranked_candidates"][0][
            "prediction_score"
        ] = 1.0

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        corrupted = json.loads(
            path.read_text(encoding="utf-8")
        )

        verification = (
            engine.verify_prediction(
                corrupted
            )
        )

        assert verification["verified"] is False
        assert (
            "prediction_hash_mismatch"
            in verification[
                "verification_errors"
            ]
        )

    print(
        "ACEE18_PERSISTED_CORRUPTION_DETECTED"
    )


if __name__ == "__main__":
    main()
