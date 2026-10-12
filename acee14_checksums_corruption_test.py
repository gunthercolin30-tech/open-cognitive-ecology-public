from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def inputs(root: Path) -> dict:
    (root / "report.txt").write_text("ok\n", encoding="utf-8")
    return {
        "operation": "archive_architecture",
        "transaction_id": "SUM-TX",
        "archive_id": "SUM-A",
        "architecture_id": "SUM-X",
        "architecture_score": 0.91,
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
    }


def verify(manager: AceeBestArchitectureArchive) -> dict:
    return manager.step(
        inputs={"operation": "verify_archive", "archive_id": "SUM-A"},
        persist=False,
    )


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manager = AceeBestArchitectureArchive(root=root)
        created = manager.step(inputs=inputs(root), persist=True)
        assert created["archive_verified"] is True

        sums = Path(created["archive_path"]) / "SHA256SUMS.txt"
        original = sums.read_text(encoding="utf-8")

        sums.write_text(original + "malformed\n", encoding="utf-8")
        assert verify(manager)["archive_verified"] is False

        first_line = original.splitlines()[0]
        sums.write_text(original + first_line + "\n", encoding="utf-8")
        duplicate = verify(manager)
        assert duplicate["archive_verified"] is False
        assert any(
            problem.startswith("checksums_duplicate:")
            for problem in duplicate["verification_errors"]
        )

        sums.write_text(
            original.replace(first_line[:64], "0" * 64, 1),
            encoding="utf-8",
        )
        assert verify(manager)["archive_verified"] is False

        sums.write_text(original, encoding="utf-8")
        assert verify(manager)["archive_verified"] is True

    print("ACEE14_CHECKSUMS_CORRUPTION_OK")


if __name__ == "__main__":
    main()
