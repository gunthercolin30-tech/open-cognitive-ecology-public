from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload as f2_payload


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        inputs = f2_payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = "ACEE6-D1"
        context["fault_injection"] = {
            "enabled": True,
            "point": "backup",
            "occurrence": 1,
        }
        inputs["admission_context"] = context

        executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
        original = executor._atomic_json_write
        observed = {"report_write_attempted": False}

        def failing_write(path, payload):
            if Path(path).name == "fault_injection_report.json":
                observed["report_write_attempted"] = True
                raise OSError("injected instrumentation persistence failure")
            return original(path, payload)

        executor._atomic_json_write = failing_write

        try:
            executor.step(inputs=inputs, persist=True)
        except OSError as exc:
            assert "instrumentation persistence failure" in str(exc)
        else:
            raise AssertionError("instrumentation failure was masked")

        assert observed["report_write_attempted"] is True

        transaction_root = root / "acee6_transactions"
        if transaction_root.is_dir():
            for journal in transaction_root.glob("*/journal.jsonl"):
                compact = journal.read_text(encoding="utf-8").replace(" ", "")
                assert '"state":"COMMITTED"' not in compact
            for latest in transaction_root.glob("*/latest_state.json"):
                compact = latest.read_text(encoding="utf-8").replace(" ", "")
                assert '"committed":true' not in compact

    print("ACEE6_G1_INSTRUMENTATION_FAILURE_OK")


if __name__ == "__main__":
    main()
