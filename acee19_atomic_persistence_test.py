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

        last_hash = None

        for index in range(10):
            result = engine.step(
                inputs={
                    "observations": [
                        {
                            "observation_id":
                                f"atomic-{index}-a",
                            "effect_size":
                                0.10 + index / 100,
                            "variance": 0.1,
                        },
                        {
                            "observation_id":
                                f"atomic-{index}-b",
                            "effect_size":
                                0.15 + index / 100,
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

            assert payload["persisted"] is True
            assert (
                payload["analysis_hash"]
                == result["analysis_hash"]
            )

            verification = (
                engine.verify_meta_analysis(
                    payload
                )
            )

            assert verification["verified"] is True
            last_hash = result["analysis_hash"]

        final_path = (
            runtime
            / "latest_meta_analysis.json"
        )

        final_payload = json.loads(
            final_path.read_text(
                encoding="utf-8"
            )
        )

        assert (
            final_payload["analysis_hash"]
            == last_hash
        )

        temporary_files = list(
            runtime.glob(".*.tmp")
        )

        assert temporary_files == []

    print(
        "ACEE19_ATOMIC_PERSISTENCE_OK"
    )


if __name__ == "__main__":
    main()
