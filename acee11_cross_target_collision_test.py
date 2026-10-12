from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_rollback_engine import AceeRollbackEngine


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        ontology = root / "ontology"
        ontology.mkdir(parents=True)

        file_a = ontology / "a.py"
        file_b = ontology / "b.py"
        backup_b = ontology / "b.py.bak"

        file_a.write_text("a_original = True\n", encoding="utf-8")
        file_b.write_text("b_original = True\n", encoding="utf-8")
        backup_b.write_text("b_restored = True\n", encoding="utf-8")

        before_a = file_a.read_bytes()
        before_b = file_b.read_bytes()
        before_backup_b = backup_b.read_bytes()

        inputs = {
            "rollback_request": {
                "transaction_id": "cross-target-collision",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(file_a),
                        "backup": str(file_b),
                    },
                    {
                        "destination": str(file_b),
                        "backup": str(backup_b),
                    },
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T23:50:00Z",
        }

        result = AceeRollbackEngine(root=root).step(
            inputs=inputs,
            persist=False,
        )

        assert result["rollback_status"] == "ACEE_ROLLBACK_BLOCKED"
        assert result["rollback_eligible"] is False
        assert result["rollback_performed"] is False
        assert result["restored_count"] == 0
        assert "backup_destination_collision:0" in (
            result["blocking_reasons"]
        )
        assert file_a.read_bytes() == before_a
        assert file_b.read_bytes() == before_b
        assert backup_b.read_bytes() == before_backup_b

    print("ACEE11_CROSS_TARGET_COLLISION_BLOCKED_OK")


if __name__ == "__main__":
    main()
