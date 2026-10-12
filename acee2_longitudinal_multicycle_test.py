from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from ontology.acee_meta_orchestrator import AceeMetaOrchestrator


def build_inputs(index: int) -> dict:
    return {
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
                    "primary_module": "controlled_evolution_orchestrator",
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
            f"2026-07-13T23:0{index}:00Z"
        ),
    }


def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="acee2_longitudinal_")
    )

    try:
        orchestrator = AceeMetaOrchestrator(root=root)
        results = []

        for index in range(3):
            result = orchestrator.step(
                inputs=build_inputs(index),
                persist=True,
            )

            assert result["persisted"] is True
            assert result["execution_dispatched"] is False
            assert len(result["trace_hash"]) == 64
            results.append(result)

        assert results[0]["previous_trace_hash"] in (None, "")
        assert (
            results[1]["previous_trace_hash"]
            == results[0]["trace_hash"]
        )
        assert (
            results[2]["previous_trace_hash"]
            == results[1]["trace_hash"]
        )

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

        assert len(records) == 3

        for index in range(1, len(records)):
            assert (
                records[index]["previous_trace_hash"]
                == records[index - 1]["trace_hash"]
            )

        print("ACEE2_LONGITUDINAL_MULTICYCLE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
