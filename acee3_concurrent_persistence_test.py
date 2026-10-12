from __future__ import annotations

import json
import multiprocessing
import shutil
import tempfile
from pathlib import Path

from ontology.acee_bridge_adapter import AceeBridgeAdapter


def worker(root: str, index: int) -> None:
    result = AceeBridgeAdapter(
        root=Path(root),
    ).step(
        inputs={
            "source_module": "evolution_sandbox",
            "source_result": {
                "status": "approved",
                "sandbox_score": 0.60 + index / 100.0,
                "rollback_available": True,
                "artifact_id": f"artifact-{index}",
            },
            "adapter_timestamp_utc": (
                f"2026-07-13T22:{index:02d}:00Z"
            ),
        },
        persist=True,
    )

    assert result["persisted"] is True
    assert len(result["normalized_hash"]) == 64


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="acee3_concurrent_"))

    try:
        processes = [
            multiprocessing.Process(
                target=worker,
                args=(str(root), index),
            )
            for index in range(8)
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()
            assert process.exitcode == 0

        history_files = list(
            root.rglob("normalized_result_history.jsonl")
        )
        assert len(history_files) == 1

        records = [
            json.loads(line)
            for line in history_files[0]
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]

        assert len(records) == 8
        assert len({
            record["normalized_hash"]
            for record in records
        }) == 8

        for index in range(1, len(records)):
            assert (
                records[index]["previous_normalized_hash"]
                == records[index - 1]["normalized_hash"]
            )

        print("ACEE3_CONCURRENT_PERSISTENCE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
