import json
import multiprocessing
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def worker(root_text, index):
    root = Path(root_text)

    engine = ACEEMetaAnalysis(
        root=root,
        runtime_dir=(
            root
            / "acee_runtime"
            / "ACEE19_acee_meta_analysis"
        ),
    )

    engine.step(
        inputs={
            "observations": [
                {
                    "observation_id":
                        f"process-{index}-a",
                    "effect_size":
                        0.10 + index / 100,
                    "variance": 0.1,
                },
                {
                    "observation_id":
                        f"process-{index}-b",
                    "effect_size":
                        0.12 + index / 100,
                    "variance": 0.1,
                },
            ]
        },
        persist=True,
    )


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        processes = [
            multiprocessing.Process(
                target=worker,
                args=(str(root), index),
            )
            for index in range(4)
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()
            assert process.exitcode == 0

        runtime = (
            root
            / "acee_runtime"
            / "ACEE19_acee_meta_analysis"
        )

        path = (
            runtime
            / "latest_meta_analysis.json"
        )

        assert path.exists()

        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

        engine = ACEEMetaAnalysis(
            root=root,
            runtime_dir=runtime,
        )

        verification = (
            engine.verify_meta_analysis(
                payload
            )
        )

        assert verification["verified"] is True
        assert payload["persisted"] is True
        assert payload["persist_requested"] is True
        assert (
            payload["included_observation_count"]
            == 2
        )

        assert (
            payload["certification_performed"]
            is False
        )
        assert (
            payload["execution_authorized"]
            is False
        )

    print(
        "ACEE19_MULTIPROCESS_PERSISTENCE_OK"
    )


if __name__ == "__main__":
    main()
