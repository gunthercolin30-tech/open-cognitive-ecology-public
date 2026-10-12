from __future__ import annotations

import json
import multiprocessing
import shutil
import tempfile
from pathlib import Path

from ontology.acee_integration_auditor import AceeIntegrationAuditor


def worker(root: str, index: int) -> None:
    result = AceeIntegrationAuditor(
        root=Path(root),
    ).step(
        inputs={
            "modules": [
                "acee_integration_auditor",
                "controlled_evolution_orchestrator",
                f"synthetic_module_{index}",
            ],
            "dependencies": {
                "acee_integration_auditor": [
                    "ontology_redundancy_audit",
                ],
            },
            "audit_timestamp_utc": (
                f"2026-07-13T15:{index:02d}:00Z"
            ),
        },
        persist=True,
    )

    assert result["persisted"] is True
    assert len(result["audit_hash"]) == 64


def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="acee0_concurrent_")
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
            root.rglob("integration_audit_history.jsonl")
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
            record["audit_hash"]
            for record in records
        }) == 8

        print("ACEE0_CONCURRENT_PERSISTENCE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
