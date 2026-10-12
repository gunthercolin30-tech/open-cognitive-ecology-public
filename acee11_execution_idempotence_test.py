from __future__ import annotations

import hashlib
import tempfile
from copy import deepcopy
from pathlib import Path

from ontology.acee_rollback_engine import AceeRollbackEngine


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        ontology = root / "ontology"
        ontology.mkdir(parents=True)

        destination = ontology / "sample.py"
        backup = ontology / "sample.py.bak"

        destination.write_text("broken = True\n", encoding="utf-8")
        backup.write_text("restored = True\n", encoding="utf-8")

        backup_hash = digest(backup)

        base = {
            "rollback_request": {
                "transaction_id": "idempotence-1",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination),
                        "backup": str(backup),
                        "expected_backup_sha256": backup_hash,
                    }
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T23:32:00Z",
        }

        engine = AceeRollbackEngine(root=root)

        first = engine.step(
            inputs=deepcopy(base),
            persist=False,
        )

        first_destination_hash = digest(destination)

        second_inputs = deepcopy(base)
        second_inputs["rollback_request"]["transaction_id"] = (
            "idempotence-2"
        )
        second_inputs["timestamp_utc"] = "2026-07-13T23:33:00Z"

        second = engine.step(
            inputs=second_inputs,
            persist=False,
        )

        assert first["rollback_status"] == "ACEE_ROLLBACK_ENGINE_READY"
        assert first["rollback_performed"] is True
        assert destination.read_text(encoding="utf-8") == (
            "restored = True\n"
        )

        assert second["rollback_status"] == "ACEE_ROLLBACK_ENGINE_READY"
        assert second["rollback_performed"] is True

        assert digest(destination) == first_destination_hash
        assert digest(destination) == backup_hash
        assert digest(backup) == backup_hash

        assert not list(ontology.glob(".*.acee11.*"))
        assert not list(ontology.glob("*.acee11.pre_restore"))

    print("ACEE11_EXECUTION_IDEMPOTENCE_OK")


if __name__ == "__main__":
    main()
