from __future__ import annotations

import json
import multiprocessing
import shutil
import tempfile
from pathlib import Path

from ontology.acee_meta_orchestrator import AceeMetaOrchestrator


def worker(root: str, index: int) -> None:
    result = AceeMetaOrchestrator(
        root=Path(root),
    ).step(
        inputs={
            "integration_audit": {
                "audit_status": "ACEE_INTEGRATION_AUDIT_COMPLETE",
                "audit_completed": True,
                "audit_id": f"audit-{index}",
                "audit_hash": f"{index + 1:064x}",
            },
            "capability_map": {
                "capability_map_status": "ACEE_CAPABILITY_MAP_READY",
                "capability_map_ready": True,
                "mapping_hash": f"{index + 11:064x}",
                "capability_matrix": {
                    "ACEE4": {
                        "acee_stage": "ACEE4",
                        "coverage_level": "covered",
                        "primary_module": (
                            "controlled_evolution_orchestrator"
                        ),
                        "recommended_action": "reuse",
                        "candidate_modules": [
                            "controlled_evolution_orchestrator",
                        ],
                    },
                },
            },
            "normalized_engine_result": {
                "adapter_status": "ACEE_BRIDGE_ADAPTER_READY",
                "adapter_ready": True,
                "normalized_hash": f"{index + 21:064x}",
                "status": "approved",
                "accepted": True,
                "executed": False,
                "rollback_available": True,
                "rollback_required": False,
            },
            "governor_decision": "approved",
            "constitutional_decision": "approved",
            "human_review_required": False,
            "cycle_timestamp_utc": (
                f"2026-07-14T00:{index:02d}:00Z"
            ),
        },
        persist=True,
    )

    assert result["persisted"] is True
    assert result["execution_dispatched"] is False
    assert len(result["trace_hash"]) == 64


def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="acee2_concurrent_")
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
            root.rglob("orchestration_cycle_history.jsonl")
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
            record["trace_hash"]
            for record in records
        }) == 8

        for index in range(1, len(records)):
            assert (
                records[index]["previous_trace_hash"]
                == records[index - 1]["trace_hash"]
            )

        print("ACEE2_CONCURRENT_PERSISTENCE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
