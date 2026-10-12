from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_rollback_engine import AceeRollbackEngine


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        root = base / "root"
        outside = base / "outside"

        root.mkdir()
        outside.mkdir()

        external_destination = outside / "sample.py"
        external_backup = outside / "sample.py.bak"

        external_destination.write_text(
            "outside_original = True\n",
            encoding="utf-8",
        )
        external_backup.write_text(
            "outside_restored = True\n",
            encoding="utf-8",
        )

        linked_directory = root / "ontology"
        linked_directory.symlink_to(
            outside,
            target_is_directory=True,
        )

        apparent_destination = linked_directory / "sample.py"
        apparent_backup = linked_directory / "sample.py.bak"

        before = external_destination.read_bytes()

        inputs = {
            "rollback_request": {
                "transaction_id": "parent-symlink-escape",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(apparent_destination),
                        "backup": str(apparent_backup),
                    }
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T23:31:00Z",
        }

        result = AceeRollbackEngine(root=root).step(
            inputs=inputs,
            persist=False,
        )

        assert result["rollback_performed"] is False
        assert result["rollback_status"] == "ACEE_ROLLBACK_BLOCKED"
        assert external_destination.read_bytes() == before

    print("ACEE11_PARENT_SYMLINK_ESCAPE_BLOCKED_OK")


if __name__ == "__main__":
    main()
