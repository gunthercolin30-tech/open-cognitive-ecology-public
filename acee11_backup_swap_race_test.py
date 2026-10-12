from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

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

        destination.write_text("original = True\n", encoding="utf-8")
        backup.write_text("trusted = True\n", encoding="utf-8")

        original_destination = destination.read_bytes()
        trusted_hash = digest(backup)

        inputs = {
            "rollback_request": {
                "transaction_id": "backup-swap-race",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination),
                        "backup": str(backup),
                        "expected_backup_sha256": trusted_hash,
                    }
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": False,
            "execute": True,
            "timestamp_utc": "2026-07-13T23:34:00Z",
        }

        original_read_bytes = Path.read_bytes
        read_count = 0

        def adversarial_read_bytes(path: Path) -> bytes:
            nonlocal read_count

            if path.resolve() == backup.resolve():
                read_count += 1

                if read_count == 2:
                    backup.write_text(
                        "malicious = True\n",
                        encoding="utf-8",
                    )

            return original_read_bytes(path)

        with patch.object(
            Path,
            "read_bytes",
            adversarial_read_bytes,
        ):
            result = AceeRollbackEngine(root=root).step(
                inputs=inputs,
                persist=False,
            )

        # Deux comportements sûrs sont acceptables :
        # 1. la transaction est bloquée/échoue ;
        # 2. seule la charge initialement validée est restaurée.
        if result["rollback_performed"]:
            assert destination.read_text(encoding="utf-8") == (
                "trusted = True\n"
            )
        else:
            assert destination.read_bytes() == original_destination
            assert result["rollback_status"] in {
                "ACEE_ROLLBACK_BLOCKED",
                "ACEE_ROLLBACK_FAILED",
            }

        assert destination.read_text(encoding="utf-8") != (
            "malicious = True\n"
        )

    print("ACEE11_BACKUP_SWAP_RACE_SAFE_OK")


if __name__ == "__main__":
    main()
