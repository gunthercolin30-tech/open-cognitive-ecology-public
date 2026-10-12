from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_rollback_engine import AceeRollbackEngine


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        root = base / "root"
        outside = base / "outside"

        (root / "ontology").mkdir(parents=True)
        outside.mkdir()

        external_backup = outside / "external.py.bak"
        external_backup.write_text(
            "external_payload = True\n",
            encoding="utf-8",
        )

        symlink_backup = root / "ontology" / "apparently_safe.py.bak"
        symlink_backup.symlink_to(external_backup)

        destination = root / "ontology" / "sample.py"
        destination.write_text("original = True\n", encoding="utf-8")

        before = destination.read_bytes()

        inputs = {
            "rollback_request": {
                "transaction_id": "symlink-escape-test",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination),
                        "backup": str(symlink_backup),
                    }
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T21:10:00Z",
        }

        result = AceeRollbackEngine(root=root).step(
            inputs=inputs,
            persist=False,
        )

        assert result["rollback_status"] == "ACEE_ROLLBACK_BLOCKED"
        assert result["rollback_eligible"] is False
        assert result["rollback_performed"] is False
        assert any(
            reason == "target_0_outside_root"
            for reason in result["blocking_reasons"]
        )

        assert destination.read_bytes() == before
        assert external_backup.read_text(encoding="utf-8") == (
            "external_payload = True\n"
        )

    print("ACEE11_SYMLINK_ESCAPE_BLOCKED_OK")


if __name__ == "__main__":
    main()
