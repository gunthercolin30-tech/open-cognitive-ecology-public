from __future__ import annotations
import fcntl
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload
from ontology.acee_installation_executor import AceeInstallationExecutor


def make_inputs(root):
    inputs = payload(root)
    context = dict(inputs["admission_context"])
    context["requested_stage"] = "ACEE6-D2"
    inputs["admission_context"] = context
    return inputs


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        runtime = root / "acee6_transactions"
        runtime.mkdir(parents=True, exist_ok=True)
        lock_path = runtime / ".mutation.lock"
        handle = lock_path.open("a+")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            blocked = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
                inputs=make_inputs(root), persist=True
            )
            assert "transaction_mutation_lock_busy" in (blocked.get("blocking_reasons") or []), blocked
            assert blocked.get("candidate_written") is False
            assert blocked.get("committed") is not True
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()

        probe = lock_path.open("a+")
        try:
            fcntl.flock(probe.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(probe.fileno(), fcntl.LOCK_UN)
        finally:
            probe.close()

        with TemporaryDirectory() as fresh_tmp:
            fresh = Path(fresh_tmp)
            seed(fresh)
            retry = AceeInstallationExecutor(root=fresh, now_utc=fixed_now()).step(
                inputs=make_inputs(fresh), persist=True
            )
            assert retry.get("transaction_state") == "MUTATED", retry
            assert retry.get("candidate_written") is True, retry
            assert retry.get("committed") is not True

    print("ACEE6_H_LOCK_CONTENTION_AND_RELEASE_OK")


if __name__ == "__main__":
    main()
