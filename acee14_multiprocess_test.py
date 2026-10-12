from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive


def worker(root_text: str, index: int, queue: mp.Queue) -> None:
    root = Path(root_text)
    result = AceeBestArchitectureArchive(root=root).step(
        inputs={
            "operation": "archive_architecture",
            "transaction_id": f"MP14-TX-{index:02d}",
            "archive_id": f"MP14-A-{index:02d}",
            "architecture_id": f"MP14-X-{index:02d}",
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
    queue.put({
        "archive_id": result["archive_id"],
        "created": result["archive_created"],
        "verified": result["archive_verified"],
        "blocking": result["blocking_reasons"],
    })


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "report.txt").write_text("ok\n", encoding="utf-8")
        context = mp.get_context("spawn")
        queue = context.Queue()
        processes = [
            context.Process(target=worker, args=(str(root), index, queue))
            for index in range(10)
        ]

        for process in processes:
            process.start()
        results = [queue.get(timeout=40.0) for _ in processes]
        for process in processes:
            process.join(timeout=40.0)
            assert process.exitcode == 0

        assert all(item["created"] is True for item in results)
        assert all(item["verified"] is True for item in results)
        assert all(item["blocking"] == [] for item in results)

        runtime = (
            root
            / "acee_runtime"
            / "ACEE14_acee_best_architecture_archive"
        )
        index = json.loads(
            (runtime / "best_architectures.json").read_text(encoding="utf-8")
        )
        assert len(index["archives"]) == 10
        assert len(index["processed_transactions"]) == 10

        history = [
            json.loads(line)
            for line in (runtime / "archive_history.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(history) == 10
        assert len({record["archive_id"] for record in history}) == 10

        manager = AceeBestArchitectureArchive(root=root)
        for index_value in range(10):
            verified = manager.step(
                inputs={
                    "operation": "verify_archive",
                    "archive_id": f"MP14-A-{index_value:02d}",
                },
                persist=False,
            )
            assert verified["archive_verified"] is True

    print("ACEE14_MULTIPROCESS_OK")


if __name__ == "__main__":
    main()
