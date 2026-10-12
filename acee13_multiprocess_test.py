from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_lineage_manager import AceeLineageManager


def worker(root_text: str, index: int, queue: mp.Queue) -> None:
    root = Path(root_text)
    result = AceeLineageManager(root=root).step(
        inputs={
            "operation": "register_candidate",
            "transaction_id": f"MP-{index:03d}",
            "lineage_id": "LINEAGE-MP",
            "generation_id": index,
            "architecture_id": f"ARCH-MP-{index:03d}",
            "parent_id": "ARCH-MP-ROOT",
            "mutation_id": f"MUT-MP-{index:03d}",
            "fitness_delta": index / 1000.0,
            "timestamp_utc": f"2026-07-13T22:{index:02d}:00Z",
        },
        persist=True,
    )
    queue.put({
        "index": index,
        "ready": result["lineage_management_ready"],
        "persisted": result["persisted"],
        "blocking_reasons": result["blocking_reasons"],
    })


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manager = AceeLineageManager(root=root)
        root_result = manager.step(
            inputs={
                "operation": "register_root",
                "transaction_id": "MP-ROOT",
                "lineage_id": "LINEAGE-MP",
                "architecture_id": "ARCH-MP-ROOT",
                "timestamp_utc": "2026-07-13T22:00:00Z",
            },
            persist=True,
        )
        assert root_result["persisted"] is True

        context = mp.get_context("spawn")
        queue = context.Queue()
        processes = [
            context.Process(target=worker, args=(str(root), index, queue))
            for index in range(1, 21)
        ]
        for process in processes:
            process.start()
        results = [queue.get(timeout=30.0) for _ in processes]
        for process in processes:
            process.join(timeout=30.0)
            assert process.exitcode == 0

        assert len(results) == 20
        assert all(item["ready"] is True for item in results)
        assert all(item["persisted"] is True for item in results)
        assert all(item["blocking_reasons"] == [] for item in results)

        runtime = root / "acee_runtime" / "ACEE13_acee_lineage_manager"
        records = [
            json.loads(line)
            for line in (runtime / "lineage_event_history.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(records) == 21
        assert len({record["transaction_id"] for record in records}) == 21

        state = json.loads((runtime / "lineages.json").read_text(encoding="utf-8"))
        lineage = state["lineages"]["LINEAGE-MP"]
        assert len(lineage["generations"]) == 21
        assert lineage["active_generation_id"] == 0
        assert sum(
            generation["status"] == "active"
            for generation in lineage["generations"].values()
        ) == 1

        previous_hash = None
        for record in records:
            assert record["previous_event_hash"] == previous_hash
            previous_hash = record["event_hash"]

    print("ACEE13_MULTIPROCESS_OK")


if __name__ == "__main__":
    main()
