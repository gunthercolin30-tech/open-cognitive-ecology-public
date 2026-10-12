import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = (
            root
            / "acee_runtime"
            / "ACEE19_acee_meta_analysis"
        )

        engine = ACEEMetaAnalysis(
            root=root,
            runtime_dir=runtime,
        )

        result = engine.step(
            inputs={
                "observations": [
                    {
                        "observation_id": "corrupt-1",
                        "effect_size": 0.2,
                        "variance": 0.1,
                    },
                    {
                        "observation_id": "corrupt-2",
                        "effect_size": 0.3,
                        "variance": 0.1,
                    },
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

        payload["pooled_effect"] = 999.0

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
            engine.verify_meta_analysis(
                corrupted
            )
        )

        assert verification["verified"] is False
        assert (
            "analysis_hash_mismatch"
            in verification[
                "verification_errors"
            ]
        )

    print(
        "ACEE19_PERSISTED_CORRUPTION_DETECTED"
    )


if __name__ == "__main__":
    main()
