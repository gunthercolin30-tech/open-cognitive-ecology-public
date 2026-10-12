from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def submit(root: Path, index: int) -> dict:
    return AceeBestArchitectureArchive(root=root).step(
        inputs={
            "operation": "archive_architecture",
            "transaction_id": f"COL-TX-{index}",
            "archive_id": "SAME-ARCHIVE",
            "architecture_id": f"COL-X-{index}",
            "architecture_score": 0.90 + index / 100.0,
            "selection_decision": {
                "selection_decision_ready": True,
                "decision": "accept",
            },
            "lineage_state": {"generation_status": "active"},
            "validation_summary": {
                "overall_success": True,
                "diagnostics": {"error_count": 0},
            },
            "git_context": {"worktree_clean": True},
            "rollback_package": {"available": True},
            "module_inventory": ["acee_best_architecture_archive"],
            "report_files": ["report.txt"],
            "reproduction_command": "python3 test.py",
        },
        persist=True,
    )


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "report.txt").write_text("ok\n", encoding="utf-8")

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda index: submit(root, index), range(2)))

        created = [
            result for result in results
            if result["archive_created"] is True
        ]
        refused = [
            result for result in results
            if result["archive_created"] is False
        ]
        assert len(created) == 1
        assert len(refused) == 1
        assert "archive_id_already_exists" in refused[0]["blocking_reasons"]

        listed = AceeBestArchitectureArchive(root=root).step(
            inputs={"operation": "list_best_architectures"},
            persist=False,
        )
        assert listed["archive_count"] == 1
        assert listed["archives"][0]["archive_id"] == "SAME-ARCHIVE"

    print("ACEE14_ARCHIVE_ID_COLLISION_OK")


if __name__ == "__main__":
    main()
