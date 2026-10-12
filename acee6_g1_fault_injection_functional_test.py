from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_installation_executor import (
    AceeInstallationExecutor,
    FAULT_INJECTION_POINTS,
)


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()
        executor = AceeInstallationExecutor(
            root=root,
            now_utc=datetime(2026, 7, 16, tzinfo=timezone.utc),
        )
        for point in sorted(FAULT_INJECTION_POINTS):
            transaction_id = "tx-" + point.replace(".", "-")
            transaction_dir = root / "acee6_transactions" / transaction_id
            transaction_dir.mkdir(parents=True)
            result = executor._fault_injection_boundary(
                {
                    "primitive": "ACEE_INSTALLATION_EXECUTOR",
                    "transaction_id": transaction_id,
                    "proposal_id": "proposal-g1",
                    "transaction_state": "BOUNDARY_COMPLETE",
                    "result_hash": "ignored",
                },
                {
                    "admission_context": {
                        "fault_injection": {
                            "enabled": True,
                            "point": point,
                            "occurrence": 1,
                        }
                    }
                },
                point,
            )
            assert result["status"] == "ACEE6_G1_FAULT_INJECTION_TRIGGERED"
            assert result["transaction_state"] == "FAULT_INJECTED"
            assert result["fault_point"] == point
            assert result["fault_triggered"] is True
            assert result["rollback_required"] is True
            assert result["rollback_executed"] is False
            assert result["retry_allowed"] is False
            assert result["partial_success"] is False
            assert result["functional_conclusion_only"] is True
            assert result["phenomenology_undetermined"] is True
            assert result["consciousness_proven"] is False
            assert (transaction_dir / "fault_injection_report.json").is_file()
            assert (transaction_dir / "journal.jsonl").is_file()
            assert (transaction_dir / "latest_state.json").is_file()
    print("ACEE6_G1_FAULT_INJECTION_FUNCTIONAL_OK")


if __name__ == "__main__":
    main()
