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

        first_engine = ACEEMetaAnalysis(
            root=root,
            runtime_dir=runtime,
        )

        first = first_engine.step(
            inputs={
                "observations": [
                    {
                        "observation_id": "restart-1",
                        "effect_size": 0.2,
                        "variance": 0.1,
                    },
                    {
                        "observation_id": "restart-2",
                        "effect_size": 0.3,
                        "variance": 0.1,
                    },
                ]
            },
            persist=True,
        )

        path = Path(
            first["artifacts"]["json_path"]
        )

        persisted = json.loads(
            path.read_text(encoding="utf-8")
        )

        second_engine = ACEEMetaAnalysis(
            root=root,
            runtime_dir=runtime,
        )

        verification = (
            second_engine.verify_meta_analysis(
                persisted
            )
        )

        assert verification["verified"] is True
        assert (
            persisted["analysis_hash"]
            == first["analysis_hash"]
        )
        assert persisted["persisted"] is True
        assert (
            persisted["included_observation_count"]
            == 2
        )

    print("ACEE19_RESTART_CONTINUITY_OK")


if __name__ == "__main__":
    main()
