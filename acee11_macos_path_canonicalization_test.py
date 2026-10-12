from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ontology.acee_rollback_engine import AceeRollbackEngine


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        lexical_root = Path(td) / "root"
        physical_root = Path(os.path.realpath(str(lexical_root)))
        backup = physical_root / "ontology" / "sample.py.bak"
        destination = physical_root / "ontology" / "sample.py"
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text("restored = True\n", encoding="utf-8")
        destination.write_text("broken = True\n", encoding="utf-8")

        inputs = {
            "rollback_request": {
                "transaction_id": "macos-realpath-test",
                "reason": "validation_failure",
                "targets": [
                    {
                        "destination": str(destination),
                        "backup": str(backup),
                    }
                ],
            },
            "governance_authorization": {"approved": True},
            "constitutional_authorization": {"approved": True},
            "dry_run": True,
            "execute": False,
            "timestamp_utc": "2026-07-13T20:00:00Z",
        }

        result = AceeRollbackEngine(root=lexical_root).step(
            inputs=inputs,
            persist=False,
        )
        assert result["rollback_status"] == "ACEE_ROLLBACK_ENGINE_READY"
        assert result["rollback_eligible"] is True
        assert result["target_count"] == 1
        assert result["blocking_reasons"] == []

    print("ACEE11_MACOS_PATH_CANONICALIZATION_OK")


if __name__ == "__main__":
    main()
