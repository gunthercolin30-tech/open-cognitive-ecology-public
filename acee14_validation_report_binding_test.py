from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    project_root = Path(__file__).resolve().parent
    source_reports = [
        project_root / "scientific_validation_report.json",
        project_root / "scientific_validation_report.txt",
        project_root / "ontology_integration_report.txt",
    ]
    for source in source_reports:
        assert source.is_file(), source

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        copied = []
        expected = {}
        for source in source_reports:
            target = root / source.name
            target.write_bytes(source.read_bytes())
            copied.append(source.name)
            expected[source.name] = digest(source)

        result = AceeBestArchitectureArchive(root=root).step(
            inputs={
                "operation": "archive_architecture",
                "transaction_id": "REPORT-TX",
                "archive_id": "REPORT-A",
                "architecture_id": "REPORT-X",
                "architecture_score": 0.92,
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
                "report_files": copied,
                "reproduction_command": "python3 -m validation.main",
            },
            persist=True,
        )
        assert result["archive_verified"] is True
        reports = Path(result["archive_path"]) / "reports"
        for filename, source_digest in expected.items():
            archived = reports / filename
            assert archived.is_file()
            assert digest(archived) == source_digest

    print("ACEE14_VALIDATION_REPORT_BINDING_OK")


if __name__ == "__main__":
    main()
