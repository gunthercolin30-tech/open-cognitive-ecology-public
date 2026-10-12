from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        report = root / "report.txt"
        report.write_text("validation complete\n", encoding="utf-8")
        inputs = {
            "operation": "archive_architecture",
            "transaction_id": "RELOAD-TX",
            "archive_id": "RELOAD-A",
            "architecture_id": "RELOAD-X",
            "architecture_score": 0.91,
            "lineage_id": "RELOAD-L",
            "generation_id": 7,
            "selection_decision": {
                "selection_decision_ready": True,
                "decision": "accept",
                "selection_id": "RELOAD-S",
            },
            "lineage_state": {"generation_status": "active"},
            "validation_summary": {
                "overall_success": True,
                "diagnostics": {"error_count": 0},
            },
            "git_context": {
                "commit": "reload-commit",
                "branch": "reload-branch",
                "worktree_clean": True,
            },
            "rollback_package": {"available": True, "package_id": "RB-7"},
            "module_inventory": ["m1", "m2"],
            "report_files": ["report.txt"],
            "reproduction_command": "python3 test.py",
        }
        created = AceeBestArchitectureArchive(root=root).step(
            inputs=inputs,
            persist=True,
        )
        directory = Path(created["archive_path"])
        expected_manifest = json.loads(
            (directory / "manifest.json").read_text(encoding="utf-8")
        )
        expected_snapshot = json.loads(
            (directory / "architecture_snapshot.json").read_text(encoding="utf-8")
        )
        expected_rollback = json.loads(
            (directory / "rollback_package.json").read_text(encoding="utf-8")
        )
        expected_reproduction = (
            directory / "reproduction.sh"
        ).read_text(encoding="utf-8")
        expected_report = (
            directory / "reports" / "report.txt"
        ).read_bytes()

        restarted = AceeBestArchitectureArchive(root=root)
        inspected = restarted.step(
            inputs={"operation": "inspect_archive", "archive_id": "RELOAD-A"},
            persist=False,
        )
        verified = restarted.step(
            inputs={"operation": "verify_archive", "archive_id": "RELOAD-A"},
            persist=False,
        )
        assert inspected["archive_verified"] is True
        assert verified["archive_verified"] is True
        assert inspected["architecture_id"] == "RELOAD-X"
        assert inspected["generation_id"] == 7

        assert json.loads(
            (directory / "manifest.json").read_text(encoding="utf-8")
        ) == expected_manifest
        assert json.loads(
            (directory / "architecture_snapshot.json").read_text(encoding="utf-8")
        ) == expected_snapshot
        assert json.loads(
            (directory / "rollback_package.json").read_text(encoding="utf-8")
        ) == expected_rollback
        assert (
            directory / "reproduction.sh"
        ).read_text(encoding="utf-8") == expected_reproduction
        assert (
            directory / "reports" / "report.txt"
        ).read_bytes() == expected_report

    print("ACEE14_ARCHIVE_RELOAD_OK")


if __name__ == "__main__":
    main()
