from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload as f2_payload

POINT_STAGE = {
    "backup": "ACEE6-D1",
    "write": "ACEE6-D2",
    "compile": "ACEE6-D3",
    "inventory": "ACEE6-E",
    "tests": "ACEE6-F1",
    "validation.main": "ACEE6-F2",
    "report": "ACEE6-F2",
}

EXPECTED_FLAGS = {
    "backup": {"backup_complete": True, "backup_required": False, "backup_created": False, "new_file_absence_recorded": True, "candidate_written": False},
    "write": {"backup_complete": True, "backup_required": False, "backup_created": False, "new_file_absence_recorded": True, "candidate_written": True},
    "compile": {"candidate_written": True, "candidate_compiled": True},
    "inventory": {"candidate_compiled": True, "inventory_modified": True},
    "tests": {"inventory_modified": True, "tests_executed": True},
    "validation.main": {"tests_executed": True, "global_validation_executed": True},
    "report": {"tests_executed": True, "global_validation_executed": True},
}


def build_inputs(root: Path, point: str, stage: str):
    inputs = f2_payload(root)
    context = dict(inputs["admission_context"])
    context["requested_stage"] = stage
    context["fault_injection"] = {
        "enabled": True,
        "point": point,
        "occurrence": 1,
    }
    inputs["admission_context"] = context
    return inputs


def main() -> None:
    for point, stage in POINT_STAGE.items():
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed(root)
            result = AceeInstallationExecutor(
                root=root,
                now_utc=fixed_now(),
            ).step(
                inputs=build_inputs(root, point, stage),
                persist=True,
            )

            assert result.get("admissible") is not False, (point, result)
            assert result.get("status") == "ACEE6_G1_FAULT_INJECTION_TRIGGERED", (point, result)
            assert result.get("transaction_state") == "FAULT_INJECTED", (point, result)
            assert result.get("fault_point") == point, (point, result)
            assert result.get("committed") is False, (point, result)
            assert result.get("partial_success") is False, (point, result)
            assert result.get("retry_allowed") is False, (point, result)
            assert result.get("rollback_required") is True, (point, result)
            assert result.get("rollback_executed") is False, (point, result)
            assert result.get("installation_completed") is False, (point, result)

            transaction_id = result.get("transaction_id")
            assert isinstance(transaction_id, str) and transaction_id, (point, result)

            for key, expected in EXPECTED_FLAGS[point].items():
                assert result.get(key) is expected, (point, key, result.get(key), result)

            tx = root / "acee6_transactions" / transaction_id
            assert (tx / "fault_injection_report.json").is_file(), point
            assert (tx / "journal.jsonl").is_file(), point
            assert (tx / "latest_state.json").is_file(), point

            # Aucun commit transactionnel ne doit être produit après G1.
            journal_text = (tx / "journal.jsonl").read_text(encoding="utf-8")
            assert '"state":"COMMITTED"' not in journal_text.replace(" ", ""), point

    print("ACEE6_G1_INTEGRATED_BOUNDARY_VALIDATION_OK")


if __name__ == "__main__":
    main()
