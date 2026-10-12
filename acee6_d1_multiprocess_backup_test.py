"""Concurrent D1 backup with finite, preissued per-process filesystem authority."""
import hashlib
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision


class FinitePreissuedEffects:
    """Preissue a bounded set of contexts before step(); never mint on demand."""

    def __init__(self, root, transaction_dir, source, backup):
        from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture

        effects = (
            [("FS_WRITE_REPLACE_BYTES", transaction_dir / "snapshot.json", None)]
            + [("FS_WRITE_REPLACE_BYTES", transaction_dir / "latest_state.json", None)] * 3
            + [("FS_APPEND_BYTES", transaction_dir / "journal.jsonl", None)] * 4
            + [("FS_CREATE_DIR", root / "acee6_transactions", None)]
            + [("FS_CREATE_DIR", backup.parent, None)]
            + [("FS_COPY2", backup, source)]
            + [("FS_WRITE_REPLACE_BYTES", transaction_dir / "backup_manifest.json", None)]
        )
        self._unused = []
        self.used = []
        for operation, target, origin in effects:
            expected = ExpectedEffect(operation, target, origin)
            fixture = PreissuedD1Fixture(root, (expected,))
            self._unused.append((operation, target.resolve(), fixture))

    def __call__(self, operation, target):
        resolved = Path(target).resolve()
        for index, (op, path, fixture) in enumerate(self._unused):
            if (op, path) == (operation, resolved):
                self._unused.pop(index)
                self.used.append((operation, str(resolved)))
                return fixture(operation, target)
        raise RuntimeError("unissued_or_exhausted_filesystem_effect:" + str(operation))

    def assert_consumed_valid(self):
        assert len(self.used) <= 12, "effect_budget_exceeded"
        assert all(op in {"FS_WRITE_REPLACE_BYTES", "FS_APPEND_BYTES", "FS_CREATE_DIR", "FS_COPY2"} for op, _ in self.used)


def worker(root_text, decision, transaction_id, plan, start, queue):
    from ontology.acee_installation_executor import AceeInstallationExecutor

    root = Path(root_text)
    inputs = {"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D1"}}
    transaction_dir = root / "acee6_transactions" / transaction_id
    source = root / plan["target_path"]
    backup = root / plan["backup_path"]
    authority = FinitePreissuedEffects(root, transaction_dir, source, backup)
    start.wait(timeout=30)
    result = AceeInstallationExecutor(
        root=root, now_utc=fixed_now(), filesystem_effect_context_provider=authority,
    ).step(inputs=inputs, persist=True)
    authority.assert_consumed_valid()
    queue.put({
        "status": result["status"],
        "state": result["transaction_state"],
        "backup_created": result.get("backup_created"),
        "candidate_written": result.get("candidate_written"),
        "effects_used": len(authority.used),
    })


def run_round():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()
        source = root / "ontology" / "sample_candidate.py"
        source.write_text("before\n", encoding="utf-8")
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        decision = valid_acee5_decision(root)
        backup = root / decision["installation_manifest"]["backup_path"]
        dry = __import__("ontology.acee_installation_executor", fromlist=["AceeInstallationExecutor"]).AceeInstallationExecutor(root=root, now_utc=fixed_now())
        admitted = dry.step(inputs={"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D1"}}, persist=False)
        assert admitted.get("admissible") is True, "parent_admission_precondition"
        transaction_id = dry._transaction_id(admitted)
        plan = admitted["normalized_plan"]
        context = mp.get_context("spawn")
        queue = context.Queue()
        start = context.Event()
        processes = [context.Process(target=worker, args=(str(root), decision, transaction_id, plan, start, queue)) for _ in range(4)]
        try:
            for process in processes:
                process.start()
            start.set()
            for process in processes:
                process.join(30)
            assert all(process.exitcode == 0 for process in processes), "multiprocess_worker_failure"
            results = [queue.get(timeout=5) for _ in processes]
            assert all(item["candidate_written"] is False for item in results)
            assert any(item["state"] == "BACKED_UP" for item in results), results
            assert source.read_text(encoding="utf-8") == "before\n"
            assert hashlib.sha256(source.read_bytes()).hexdigest() == before
            assert backup.is_file(), "missing_shared_backup"
            assert hashlib.sha256(backup.read_bytes()).hexdigest() == before
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join(5)
            queue.close()
            queue.join_thread()


if __name__ == "__main__":
    for _ in range(3):
        run_round()
    print("ACEE6_D1_MULTIPROCESS_BACKUP_OK")
