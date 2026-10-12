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
        destination_alias = (
            ontology / ".." / "ontology" / "sample.py"
        )

        backup_a = ontology / "a.py.bak"
        backup_b = ontology / "b.py.bak"

        destination.write_text("original = True\n", encoding="utf-8")
        backup_a.write_text("a = True\n", encoding="utf-8")
        backup_b.write_text("b = True\n", encoding="utf-8")

        before = destination.read_bytes()

        inputs = {
            "rollback_request": {
                "transaction_id": "destination-alias-test",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination),
                        "backup": str(backup_a),
                    },
                    {
                        "destination": str(destination_alias),
                        "backup": str(backup_b),
                    },
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T23:51:00Z",
        }

        result = AceeRollbackEngine(root=root).step(
            inputs=inputs,
            persist=False,
        )

        assert result["rollback_status"] == "ACEE_ROLLBACK_BLOCKED"
        assert result["rollback_performed"] is False
        assert "duplicate_destination_targets:0,1" in (
            result["blocking_reasons"]
        )
        assert destination.read_bytes() == before

    print("ACEE11_DESTINATION_ALIAS_BLOCKED_OK")


if __name__ == "__main__":
    main()
