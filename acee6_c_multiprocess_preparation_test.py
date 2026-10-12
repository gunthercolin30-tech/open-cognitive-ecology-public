import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision


def worker(root_text, queue):
    from ontology.acee_installation_executor import AceeInstallationExecutor

    root = Path(root_text)
    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(
        inputs=valid_acee5_decision(root),
        persist=True,
    )
    queue.put({
        "status": result["status"],
        "transaction_id": result.get("transaction_id"),
        "transaction_state": result.get("transaction_state"),
        "candidate_written": result.get("candidate_written"),
    })


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()

        context = mp.get_context("spawn")
        queue = context.Queue()
        processes = [
            context.Process(target=worker, args=(str(root), queue))
            for _ in range(4)
        ]

        for process in processes:
            process.start()
        for process in processes:
            process.join(30)
            assert process.exitcode == 0

        results = [queue.get(timeout=5) for _ in processes]
        transaction_ids = {
            item["transaction_id"]
            for item in results
            if item["transaction_id"]
        }
        assert len(transaction_ids) == 1
        assert all(item["candidate_written"] is False for item in results)
        assert all(
            item["status"] in {
                "ACEE6_TRANSACTION_PREPARED",
                "ACEE6_TRANSACTION_PREPARATION_BLOCKED",
            }
            for item in results
        )

        from ontology.acee_installation_executor import (
            AceeInstallationExecutor,
        )

        retry = AceeInstallationExecutor(
            root=root,
            now_utc=fixed_now(),
        ).step(
            inputs=valid_acee5_decision(root),
            persist=True,
        )
        assert retry["status"] == "ACEE6_TRANSACTION_PREPARED"
        assert retry["transaction_state"] == "PREPARED"
        assert retry["candidate_written"] is False

    print("ACEE6_C_MULTIPROCESS_PREPARATION_OK")
