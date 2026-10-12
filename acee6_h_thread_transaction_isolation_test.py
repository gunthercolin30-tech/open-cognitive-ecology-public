from __future__ import annotations
import copy
import threading
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload
from ontology.acee_installation_executor import AceeInstallationExecutor


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        base = payload(root)
        context = dict(base["admission_context"])
        context["requested_stage"] = "ACEE6-D2"
        base["admission_context"] = context
        barrier = threading.Barrier(8)
        lock = threading.Lock()
        results = []
        errors = []

        def worker():
            try:
                local = copy.deepcopy(base)
                barrier.wait(timeout=10)
                result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
                    inputs=local, persist=True
                )
                with lock:
                    results.append(result)
            except BaseException as exc:
                with lock:
                    errors.append(repr(exc))

        threads = [threading.Thread(target=worker, daemon=True) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(20)
            assert not thread.is_alive(), "thread deadlock"

        assert not errors, errors
        assert len(results) == 8
        txids = {r.get("transaction_id") for r in results if r.get("transaction_id")}
        assert len(txids) == 1, txids
        assert all(r.get("committed") is not True for r in results)
        assert all(r.get("partial_success") is not True for r in results)
        assert any(r.get("transaction_state") == "MUTATED" for r in results), results
        target = root / "ontology" / "sample_candidate.py"
        assert target.is_file()
        expected = base["admission_context"]["candidate_content"]
        assert target.read_text(encoding="utf-8") == expected
        assert not list(root.rglob("*.tmp")), list(root.rglob("*.tmp"))

    print("ACEE6_H_THREAD_TRANSACTION_ISOLATION_OK")


if __name__ == "__main__":
    main()
