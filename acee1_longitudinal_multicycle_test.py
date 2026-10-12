from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from ontology.acee_capability_map import AceeCapabilityMap
from ontology.acee_integration_auditor import AceeIntegrationAuditor


def build_audit(modules: list[str], timestamp: str) -> dict:
    return AceeIntegrationAuditor().step(
        inputs={
            "modules": modules,
            "dependencies": {
                "acee_integration_auditor": [
                    "ontology_redundancy_audit",
                    "ontology_gap_detector",
                ],
            },
            "audit_timestamp_utc": timestamp,
        },
        persist=False,
    )


def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="acee1_longitudinal_")
    )

    try:
        mapper = AceeCapabilityMap(root=root)

        module_sets = [
            [
                "acee_integration_auditor",
                "acee_capability_map",
                "controlled_evolution_orchestrator",
            ],
            [
                "acee_integration_auditor",
                "acee_capability_map",
                "controlled_evolution_orchestrator",
                "evolution_sandbox",
            ],
            [
                "acee_integration_auditor",
                "acee_capability_map",
                "controlled_evolution_orchestrator",
                "evolution_sandbox",
                "runtime_experiment_manager",
            ],
        ]

        results = []

        for index, modules in enumerate(module_sets):
            audit = build_audit(
                modules,
                f"2026-07-13T17:0{index}:00Z",
            )

            result = mapper.step(
                inputs={
                    "integration_audit": audit,
                    "map_timestamp_utc": (
                        f"2026-07-13T18:0{index}:00Z"
                    ),
                },
                persist=True,
            )

            assert result["persisted"] is True
            assert result["capability_count"] == 21
            results.append(result)

        assert results[0]["previous_mapping_hash"] in (
            None,
            "",
        )

        assert (
            results[1]["previous_mapping_hash"]
            == results[0]["mapping_hash"]
        )

        assert (
            results[2]["previous_mapping_hash"]
            == results[1]["mapping_hash"]
        )

        history_files = list(
            root.rglob("capability_map_history.jsonl")
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
                records[index]["previous_mapping_hash"]
                == records[index - 1]["mapping_hash"]
            )

        assert results[0]["deferred_capabilities"] == [
            "ACEE5",
            "ACEE6",
        ]

        print("ACEE1_LONGITUDINAL_MULTICYCLE_OK")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
