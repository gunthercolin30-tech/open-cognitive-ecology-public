from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler


def worker(root_text: str, index: int, queue: mp.Queue) -> None:
    root = Path(root_text)
    result = AceeAutonomousScheduler(root=root).step(
        inputs={
            "operation": "schedule_cycle",
            "transaction_id": f"MP15-TX-{index:02d}",
            "cycle_id": f"MP15-CYCLE-{index:02d}",
            "due_at_utc": "2026-07-14T10:00:00Z",
            "priority": index / 20.0,
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "cycle_request": {
                "requested_phases": ["snapshot"],
                "source_process": index,
            },
        },
        persist=True,
    )
    queue.put({
        "cycle_id": result["cycle_id"],
        "persisted": result["persisted"],
        "ready": result["autonomous_scheduler_ready"],
        "blocking": result["blocking_reasons"],
    })


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        context = mp.get_context("spawn")
        queue = context.Queue()
        processes = [
            context.Process(
                target=worker,
                args=(str(root), index, queue),
            )
            for index in range(16)
        ]

        for process in processes:
            process.start()
        results = [queue.get(timeout=45.0) for _ in processes]
        for process in processes:
            process.join(timeout=45.0)
            assert process.exitcode == 0

        assert len(results) == 16
        assert all(item["persisted"] is True for item in results)
        assert all(item["ready"] is True for item in results)
        assert all(item["blocking"] == [] for item in results)
        assert len({item["cycle_id"] for item in results}) == 16

        manager = AceeAutonomousScheduler(root=root)
        listing = manager.step(
            inputs={"operation": "list_pending_cycles"},
            persist=False,
        )
        assert listing["pending_count"] == 16
        assert len({item["cycle_id"] for item in listing["pending_cycles"]}) == 16

        runtime = (
            root
            / "acee_runtime"
            / "ACEE15_acee_autonomous_scheduler"
        )
        state = json.loads(
            (runtime / "schedule_state.json").read_text(encoding="utf-8")
        )
        assert len(state["cycles"]) == 16
        assert len(state["processed_transactions"]) == 16

        history = [
            json.loads(line)
            for line in (runtime / "schedule_history.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(history) == 16
        assert len({record["transaction_id"] for record in history}) == 16

        previous_hash = None
        for record in history:
            assert record["previous_event_hash"] == previous_hash
            previous_hash = record["event_hash"]

    print("ACEE15_MULTIPROCESS_OK")


if __name__ == "__main__":
    main()
