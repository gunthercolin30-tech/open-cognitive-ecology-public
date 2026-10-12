from __future__ import annotations

import json
import multiprocessing
import shutil
import tempfile
from pathlib import Path

from ontology.acee_capability_map import AceeCapabilityMap
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def worker(root: str, index: int) -> None:
    audit = AceeIntegrationAuditor().step(
        inputs={
            "modules": [
                "acee_integration_auditor",
                "acee_capability_map",
                "controlled_evolution_orchestrator",
                f"synthetic_capability_module_{index}",
            ],
            "dependencies": {
                "acee_integration_auditor": [
                    "ontology_redundancy_audit",
                ],
            },
            "audit_timestamp_utc": (
                f"2026-07-13T19:{index:02d}:00Z"
            ),
        },
        persist=False,
    )

    result = AceeCapabilityMap(
        root=Path(root),
    ).step(
        inputs={
            "integration_audit": audit,
            "map_timestamp_utc": (
                f"2026-07-13T20:{index:02d}:00Z"
            ),
        },
        persist=True,
    )

    assert result["persisted"] is True
    assert len(result["mapping_hash"]) == 64


def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="acee1_concurrent_")
    )

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
            root.rglob("capability_map_history.jsonl")
        )
        assert len(history_files) == 1

        lines = [
            line
            for line in history_files[0]
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]

        assert len(lines) == 8

        records = [json.loads(line) for line in lines]

        assert len({
            record["mapping_hash"]
            for record in records
        }) == 8

        for index in range(1, len(records)):
            assert (
                records[index]["previous_mapping_hash"]
                == records[index - 1]["mapping_hash"]
            )

        print("ACEE1_CONCURRENT_PERSISTENCE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
