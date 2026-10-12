from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
from ontology.acee_lineage_manager import AceeLineageManager
from ontology.acee_selection_policy import AceeSelectionPolicy


def selection_context() -> dict:
    return {
        "selection_id": "SEL-ACEE14-REAL",
        "timestamp_utc": "2026-07-14T00:00:00Z",
        "impact_evaluation": {
            "comparison_valid": True,
            "impact_score": 0.14,
            "metric_classifications": {"closure_pressure": "unchanged"},
        },
        "causal_analysis": {
            "ready_for_selection": True,
            "causal_effect_resolved": True,
            "causal_probability": 0.96,
            "causal_confidence": 0.96,
            "effect_size": 0.14,
            "effect_direction": "beneficial",
        },
        "stability_evidence": {"stability_score": 0.95},
        "simplicity_evidence": {"simplicity_score": 0.90},
        "reversibility_evidence": {
            "mean_reversibility_score": 0.97,
            "reversibility_assured": True,
        },
        "non_closure_evidence": {
            "closure_pressure": 0.07,
            "non_closure_score": 0.95,
        },
        "constitutional_evidence": {
            "compliant": True,
            "constitutional_compliance_score": 0.97,
        },
        "governance_evidence": {
            "approved": True,
            "governance_score": 0.96,
        },
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        report = root / "scientific_validation_report.json"
        report.write_text(
            '{"overall_success": true, "diagnostics": {"error_count": 0}}\n',
            encoding="utf-8",
        )

        decision = AceeSelectionPolicy(root=root).step(
            inputs=selection_context(),
            persist=True,
        )
        assert decision["selection_decision_ready"] is True
        assert decision["decision"] == "accept"

        lineage_manager = AceeLineageManager(root=root)
        lineage_manager.step(
            inputs={
                "operation": "register_root",
                "transaction_id": "PIPE-ROOT",
                "lineage_id": "LINEAGE-PIPE",
                "architecture_id": "ARCH-PIPE-0",
                "timestamp_utc": "2026-07-14T00:01:00Z",
            },
            persist=True,
        )
        lineage_manager.step(
            inputs={
                "operation": "register_candidate",
                "transaction_id": "PIPE-CANDIDATE",
                "lineage_id": "LINEAGE-PIPE",
                "generation_id": 1,
                "architecture_id": "ARCH-PIPE-1",
                "parent_id": "ARCH-PIPE-0",
                "mutation_id": "MUT-PIPE-1",
                "fitness_delta": 0.14,
                "timestamp_utc": "2026-07-14T00:02:00Z",
            },
            persist=True,
        )
        lineage = lineage_manager.step(
            inputs={
                "operation": "apply_selection",
                "transaction_id": "PIPE-ACTIVATE",
                "lineage_id": "LINEAGE-PIPE",
                "generation_id": 1,
                "selection_decision": decision,
                "timestamp_utc": "2026-07-14T00:03:00Z",
            },
            persist=True,
        )
        assert lineage["generation_status"] == "active"
        assert lineage["active_generation_id"] == 1

        archive = AceeBestArchitectureArchive(root=root).step(
            inputs={
                "operation": "archive_architecture",
                "transaction_id": "PIPE-ARCHIVE",
                "archive_id": "ARCHIVE-PIPE-1",
                "architecture_id": "ARCH-PIPE-1",
                "architecture_score": 0.94,
                "lineage_id": "LINEAGE-PIPE",
                "generation_id": 1,
                "parent_id": "ARCH-PIPE-0",
                "mutation_id": "MUT-PIPE-1",
                "fitness_delta": 0.14,
                "selection_decision": decision,
                "lineage_state": lineage,
                "validation_summary": {
                    "overall_success": True,
                    "diagnostics": {"error_count": 0},
                },
                "git_context": {
                    "commit": "0123456789abcdef",
                    "branch": "test",
                    "worktree_clean": True,
                },
                "rollback_package": {"available": True, "verified": True},
                "module_inventory": [
                    "acee_selection_policy",
                    "acee_lineage_manager",
                    "acee_best_architecture_archive",
                ],
                "report_files": ["scientific_validation_report.json"],
                "reproduction_command": "python3 -m validation.main",
                "timestamp_utc": "2026-07-14T00:04:00Z",
            },
            persist=True,
        )
        assert archive["archive_ready"] is True
        assert archive["archive_created"] is True
        assert archive["archive_verified"] is True
        assert archive["architecture_id"] == "ARCH-PIPE-1"
        assert archive["lineage_id"] == "LINEAGE-PIPE"
        assert archive["generation_id"] == 1

        snapshot = Path(archive["archive_path"]) / "architecture_snapshot.json"
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        assert payload["selection_id"] == decision["selection_id"]
        assert payload["lineage_id"] == lineage["lineage_id"]
        assert payload["generation_id"] == lineage["generation_id"]
        assert payload["fitness_delta"] == 0.14
        assert payload["architecture_id"] == "ARCH-PIPE-1"

    print("ACEE14_REAL_PIPELINE_OK")


if __name__ == "__main__":
    main()
