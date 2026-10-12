from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from ontology.acee_bridge_adapter import AceeBridgeAdapter


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="acee3_longitudinal_"))

    try:
        adapter = AceeBridgeAdapter(root=root)

        source_results = [
            {
                "status": "approved",
                "sandbox_score": 0.70,
                "rollback_available": True,
            },
            {
                "status": "executed",
                "sandbox_score": 0.80,
                "rollback_available": True,
            },
            {
                "status": "rolled_back",
                "sandbox_score": 0.60,
                "rollback_available": True,
                "rollback_performed": True,
            },
        ]

        results = []

        for index, source_result in enumerate(source_results):
            result = adapter.step(
                inputs={
                    "source_module": "evolution_sandbox",
                    "source_result": source_result,
                    "adapter_timestamp_utc": (
                        f"2026-07-13T21:0{index}:00Z"
                    ),
                },
                persist=True,
            )

            assert result["persisted"] is True
            assert len(result["normalized_hash"]) == 64
            results.append(result)

        assert results[0]["previous_normalized_hash"] in (None, "")
        assert (
            results[1]["previous_normalized_hash"]
            == results[0]["normalized_hash"]
        )
        assert (
            results[2]["previous_normalized_hash"]
            == results[1]["normalized_hash"]
        )

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

        assert len(records) == 3

        for index in range(1, len(records)):
            assert (
                records[index]["previous_normalized_hash"]
                == records[index - 1]["normalized_hash"]
            )

        assert results[0]["status"] == "approved"
        assert results[1]["status"] == "executed"
        assert results[2]["status"] == "rolled_back"

        print("ACEE3_LONGITUDINAL_MULTICYCLE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
