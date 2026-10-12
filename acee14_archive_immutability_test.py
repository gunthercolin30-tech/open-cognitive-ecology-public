from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def ready(root: Path) -> dict:
    (root / "report.json").write_text('{"ok": true}\n', encoding="utf-8")
    return {
        "operation": "archive_architecture",
        "transaction_id": "IMM-TX",
        "archive_id": "IMM-ARCHIVE",
        "architecture_id": "IMM-ARCH",
        "architecture_score": 0.90,
        "selection_decision": {
            "selection_decision_ready": True,
            "decision": "accept",
        },
        "lineage_state": {
            "generation_status": "active",
            "lineage_id": "IMM-LINEAGE",
            "generation_id": 1,
        },
        "validation_summary": {
            "overall_success": True,
            "diagnostics": {"error_count": 0},
        },
        "git_context": {"worktree_clean": False},
        "rollback_package": {"available": True},
        "module_inventory": ["acee_best_architecture_archive"],
        "report_files": ["report.json"],
        "reproduction_command": "python3 -m validation.main",
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manager = AceeBestArchitectureArchive(root=root)
        created = manager.step(inputs=ready(root), persist=True)
        assert created["archive_verified"] is True
        directory = Path(created["archive_path"])

        targets = [
            directory / "manifest.json",
            directory / "architecture_snapshot.json",
            directory / "validation_summary.json",
        ]
        for target in targets:
            original = target.read_bytes()
            target.write_bytes(original + b"\n ")
            verification = manager.step(
                inputs={
                    "operation": "verify_archive",
                    "archive_id": "IMM-ARCHIVE",
                },
                persist=False,
            )
            assert verification["archive_verified"] is False
            assert "archive_integrity_failure" in verification["blocking_reasons"]
            target.write_bytes(original)

        final = manager.step(
            inputs={
                "operation": "verify_archive",
                "archive_id": "IMM-ARCHIVE",
            },
            persist=False,
        )
        assert final["archive_verified"] is True

    print("ACEE14_ARCHIVE_IMMUTABILITY_OK")


if __name__ == "__main__":
    main()
