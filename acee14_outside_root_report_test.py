from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def main() -> None:
    with TemporaryDirectory() as root_tmp, TemporaryDirectory() as outside_tmp:
        root = Path(root_tmp)
        outside = Path(outside_tmp) / "outside-report.txt"
        outside.write_text("must not be copied\n", encoding="utf-8")

        result = AceeBestArchitectureArchive(root=root).step(
            inputs={
                "operation": "archive_architecture",
                "transaction_id": "OUT-TX",
                "archive_id": "OUT-A",
                "architecture_id": "OUT-X",
                "architecture_score": 0.90,
                "selection_decision": {
                    "selection_decision_ready": True,
                    "decision": "accept",
                },
                "lineage_state": {"generation_status": "active"},
                "validation_summary": {
                    "overall_success": True,
                    "diagnostics": {"error_count": 0},
                },
                "git_context": {"worktree_clean": False},
                "rollback_package": {"available": True},
                "module_inventory": ["acee_best_architecture_archive"],
                "report_files": [str(outside)],
                "reproduction_command": "python3 test.py",
            },
            persist=True,
        )
        assert result["archive_created"] is False
        assert result["persisted"] is False
        assert any(
            reason.startswith("report_invalid:")
            for reason in result["blocking_reasons"]
        )
        assert not (
            root
            / "acee_runtime"
            / "ACEE14_acee_best_architecture_archive"
            / "archives"
            / "OUT-A"
        ).exists()

    print("ACEE14_OUTSIDE_ROOT_REPORT_OK")


if __name__ == "__main__":
    main()
