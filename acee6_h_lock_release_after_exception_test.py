from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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
        original = AceeInstallationExecutor._atomic_json_write
        fired = {"value": False}

        def fail_once(self, path, data):
            if path.name == "mutation_manifest.json" and not fired["value"]:
                fired["value"] = True
                raise OSError("injected mutation manifest failure")
            return original(self, path, data)

        raised = None
        with patch.object(AceeInstallationExecutor, "_atomic_json_write", fail_once):
            try:
                AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
                    inputs=make_inputs(root), persist=True
                )
            except OSError as exc:
                raised = exc
        assert fired["value"] is True
        assert raised is not None, "injected exception was masked"

        runtime = root / "acee6_transactions"
        lock_path = runtime / ".mutation.lock"
        probe = lock_path.open("a+")
        try:
            import fcntl
            fcntl.flock(probe.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(probe.fileno(), fcntl.LOCK_UN)
        finally:
            probe.close()
        assert not list(root.rglob("*.tmp")), list(root.rglob("*.tmp"))

        with TemporaryDirectory() as fresh_tmp:
            fresh = Path(fresh_tmp)
            seed(fresh)
            retry = AceeInstallationExecutor(root=fresh, now_utc=fixed_now()).step(
                inputs=make_inputs(fresh), persist=True
            )
            reasons = retry.get("blocking_reasons") or []
            assert "transaction_mutation_lock_busy" not in reasons, retry
            assert retry.get("candidate_written") is True, retry

    print("ACEE6_H_LOCK_RELEASE_AFTER_EXCEPTION_OK")


if __name__ == "__main__":
    main()
