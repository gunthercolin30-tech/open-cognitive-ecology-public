from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

import ontology.acee_rollback_engine as rollback_module
from ontology.acee_rollback_engine import AceeRollbackEngine


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        ontology = root / "ontology"
        ontology.mkdir(parents=True)

        destination_1 = ontology / "first.py"
        destination_2 = ontology / "second.py"
        backup_1 = ontology / "first.py.bak"
        backup_2 = ontology / "second.py.bak"

        destination_1.write_text("first_original = True\n", encoding="utf-8")
        destination_2.write_text("second_original = True\n", encoding="utf-8")
        backup_1.write_text("first_restored = True\n", encoding="utf-8")
        backup_2.write_text("second_restored = True\n", encoding="utf-8")

        original_hashes = {
            destination_1: digest(destination_1),
            destination_2: digest(destination_2),
        }
        backup_hashes = {
            backup_1: digest(backup_1),
            backup_2: digest(backup_2),
        }

        inputs = {
            "rollback_request": {
                "transaction_id": "atomicity-failure-injection",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination_1),
                        "backup": str(backup_1),
                        "expected_backup_sha256": backup_hashes[backup_1],
                    },
                    {
                        "destination": str(destination_2),
                        "backup": str(backup_2),
                        "expected_backup_sha256": backup_hashes[backup_2],
                    },
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T21:00:00Z",
        }

        real_replace = rollback_module.os.replace
        commit_count = 0
        failure_injected = False

        def failing_replace(source: str, destination: str) -> None:
            nonlocal commit_count, failure_injected

            source_path = Path(source)

            if ".acee11." in source_path.name:
                commit_count += 1
                if commit_count == 2 and not failure_injected:
                    failure_injected = True
                    raise OSError("simulated second-file commit failure")

            real_replace(source, destination)

        with patch.object(
            rollback_module.os,
            "replace",
            side_effect=failing_replace,
        ):
            result = AceeRollbackEngine(root=root).step(
                inputs=inputs,
                persist=False,
            )

        assert failure_injected is True
        assert result["rollback_status"] == "ACEE_ROLLBACK_FAILED"
        assert result["rollback_performed"] is False
        assert result["restored_count"] == 0
        assert result["failure"].startswith("OSError:")

        assert digest(destination_1) == original_hashes[destination_1]
        assert digest(destination_2) == original_hashes[destination_2]

        assert digest(backup_1) == backup_hashes[backup_1]
        assert digest(backup_2) == backup_hashes[backup_2]

        assert not list(ontology.glob("*.acee11.pre_restore"))
        assert not list(ontology.glob(".*.acee11.*"))

    print("ACEE11_MULTIFILE_ATOMICITY_OK")


if __name__ == "__main__":
    main()
