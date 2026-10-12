from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def archive(root: Path, index: int) -> dict:
    return AceeBestArchitectureArchive(root=root).step(
        inputs={
            "operation": "archive_architecture",
            "transaction_id": f"CON-TX-{index:02d}",
            "archive_id": f"CON-A-{index:02d}",
            "architecture_id": f"CON-X-{index:02d}",
            "architecture_score": 0.80 + index / 100.0,
            "selection_decision": {
                "selection_decision_ready": True,
                "decision": "accept",
            },
            "lineage_state": {
                "generation_status": "active",
                "generation_id": index,
            },
            "validation_summary": {
                "overall_success": True,
                "diagnostics": {"error_count": 0},
            },
            "git_context": {"worktree_clean": index % 2 == 0},
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

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: archive(root, i), range(12)))

        assert len(results) == 12
        assert all(result["archive_created"] is True for result in results)
        assert all(result["archive_verified"] is True for result in results)

        runtime = root / "acee_runtime" / "ACEE14_acee_best_architecture_archive"
        index = json.loads(
            (runtime / "best_architectures.json").read_text(encoding="utf-8")
        )
        assert len(index["archives"]) == 12
        assert len(index["processed_transactions"]) == 12

        history = [
            json.loads(line)
            for line in (runtime / "archive_history.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(history) == 12
        assert len({item["archive_id"] for item in history}) == 12

        listed = AceeBestArchitectureArchive(root=root).step(
            inputs={"operation": "list_best_architectures"},
            persist=False,
        )
        assert listed["archive_count"] == 12
        scores = [item["architecture_score"] for item in listed["archives"]]
        assert scores == sorted(scores, reverse=True)

        for index_value in range(12):
            directory = runtime / "archives" / f"CON-A-{index_value:02d}"
            assert (directory / "manifest.json").is_file()
            assert (directory / "SHA256SUMS.txt").is_file()
            verified = AceeBestArchitectureArchive(root=root).step(
                inputs={
                    "operation": "verify_archive",
                    "archive_id": f"CON-A-{index_value:02d}",
                },
                persist=False,
            )
            assert verified["archive_verified"] is True

    print("ACEE14_CONCURRENT_ARCHIVES_OK")


if __name__ == "__main__":
    main()
