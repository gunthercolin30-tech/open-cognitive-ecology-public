from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_rollback_engine import AceeRollbackEngine


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        ontology = root / "ontology"
        ontology.mkdir(parents=True)

        destination = ontology / "sample.py"
        backup_a = ontology / "sample_a.py.bak"
        backup_b = ontology / "sample_b.py.bak"

        destination.write_text("original = True\n", encoding="utf-8")
        backup_a.write_text("restored_a = True\n", encoding="utf-8")
        backup_b.write_text("restored_b = True\n", encoding="utf-8")

        before = destination.read_bytes()

        inputs = {
            "rollback_request": {
                "transaction_id": "duplicate-target-test",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination),
                        "backup": str(backup_a),
                    },
                    {
                        "destination": str(destination),
                        "backup": str(backup_b),
                    },
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T23:30:00Z",
        }

        result = AceeRollbackEngine(root=root).step(
            inputs=inputs,
            persist=False,
        )

        assert result["rollback_status"] == "ACEE_ROLLBACK_BLOCKED"
        assert result["rollback_eligible"] is False
        assert result["rollback_performed"] is False
        assert result["restored_count"] == 0
        assert "duplicate_destination_targets:0,1" in (
            result["blocking_reasons"]
        )
        assert destination.read_bytes() == before
        assert backup_a.read_text(encoding="utf-8") == (
            "restored_a = True\n"
        )
        assert backup_b.read_text(encoding="utf-8") == (
            "restored_b = True\n"
        )

    print("ACEE11_DUPLICATE_TARGET_BLOCKED_OK")


if __name__ == "__main__":
    main()
