from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from ontology.acee_integration_auditor import AceeIntegrationAuditor


def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="acee0_longitudinal_")
    )

    try:
        auditor = AceeIntegrationAuditor(
            root=root,
        )

        module_sets = [
            [
                "acee_integration_auditor",
                "controlled_evolution_orchestrator",
            ],
            [
                "acee_integration_auditor",
                "controlled_evolution_orchestrator",
                "evolution_sandbox",
            ],
            [
                "acee_integration_auditor",
                "controlled_evolution_orchestrator",
                "evolution_sandbox",
                "runtime_experiment_manager",
            ],
        ]

        results = []

        for index, modules in enumerate(module_sets):
            result = auditor.step(
                inputs={
                    "modules": modules,
                    "dependencies": {
                        "acee_integration_auditor": [
                            "ontology_redundancy_audit",
                            "ontology_gap_detector",
                        ],
                    },
                    "audit_timestamp_utc": (
                        f"2026-07-13T16:0{index}:00Z"
                    ),
                },
                persist=True,
            )

            assert result["persisted"] is True
            results.append(result)

        assert results[0]["previous_audit_hash"] in (
            None,
            "",
        )

        assert (
            results[1]["previous_audit_hash"]
            == results[0]["audit_hash"]
        )

        assert (
            results[2]["previous_audit_hash"]
            == results[1]["audit_hash"]
        )

        history_files = list(
            root.rglob("integration_audit_history.jsonl")
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
                records[index]["previous_audit_hash"]
                == records[index - 1]["audit_hash"]
            )

        assert (
            results[2]["coverage_score"]
            >= results[0]["coverage_score"]
        )

        print("ACEE0_LONGITUDINAL_MULTICYCLE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
