from __future__ import annotations
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory


def worker(root_text, queue):
    from acee6_b1_test_support import fixed_now
    from acee6_f2_test_support import payload
    from ontology.acee_installation_executor import AceeInstallationExecutor
    root = Path(root_text)
    inputs = payload(root)
    context = dict(inputs["admission_context"])
    context["requested_stage"] = "ACEE6-D2"
    context["fault_injection"] = {
        "enabled": True,
        "point": "write",
        "occurrence": 1,
        "execute_rollback": True,
    }
    inputs["admission_context"] = context
    try:
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=inputs, persist=True
        )
        queue.put({
            "status": result.get("status"),
            "state": result.get("transaction_state"),
            "txid": result.get("transaction_id"),
            "committed": result.get("committed"),
            "partial": result.get("partial_success"),
        })
    except BaseException as exc:
        queue.put({"error": repr(exc)})


def main():
    from acee6_e_test_support import seed
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        ctx = mp.get_context("spawn")
        queue = ctx.Queue()
        processes = [ctx.Process(target=worker, args=(str(root), queue)) for _ in range(4)]
        for process in processes:
            process.start()
        for process in processes:
            process.join(40)
            assert not process.is_alive(), "multiprocess deadlock"
            assert process.exitcode == 0, process.exitcode
        results = [queue.get(timeout=5) for _ in processes]
        assert not [r for r in results if "error" in r], results
        txids = {r.get("txid") for r in results if r.get("txid")}
        assert len(txids) == 1, results
        assert all(r.get("committed") is not True for r in results)
        assert all(r.get("partial") is not True for r in results)
        assert any(r.get("state") == "ROLLED_BACK" for r in results), results
        assert not (root / "ontology" / "sample_candidate.py").exists()
        tx = root / "acee6_transactions" / next(iter(txids))
        journal = (tx / "journal.jsonl").read_text(encoding="utf-8")
        assert '"state":"COMMITTED"' not in journal.replace(" ", "")
        assert not list(root.rglob("*.tmp")), list(root.rglob("*.tmp"))

    print("ACEE6_H_MULTIPROCESS_G2_TRANSACTION_OK")


if __name__ == "__main__":
    main()
