from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from ontology.acee_rollback_engine import AceeRollbackEngine


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def calculate_record_hash(record: dict[str, Any]) -> str:
    without_hash = {
        key: value
        for key, value in record.items()
        if key != "record_hash"
    }
    return hashlib.sha256(
        canonical(without_hash).encode("utf-8")
    ).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        ontology = root / "ontology"
        ontology.mkdir(parents=True)

        destination = ontology / "sample.py"
        backup = ontology / "sample.py.bak"

        destination.write_text("original = True\n", encoding="utf-8")
        backup.write_text("restored = True\n", encoding="utf-8")

        engine = AceeRollbackEngine(root=root)

        last_result = None

        for index in range(20):
            inputs = {
                "rollback_request": {
                    "transaction_id": f"durability-{index:02d}",
                    "reason": "explicit_governed_request",
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
                "timestamp_utc": f"2026-07-13T23:{index:02d}:00Z",
            }

            last_result = engine.step(
                inputs=inputs,
                persist=True,
            )

        assert last_result is not None

        runtime = (
            root
            / "acee_runtime"
            / "ACEE11_acee_rollback_engine"
        )
        history = runtime / "rollback_history.jsonl"
        latest = runtime / "latest_rollback.json"

        assert history.stat().st_size > 0
        assert latest.stat().st_size > 0

        records = [
            json.loads(line)
            for line in history.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        assert len(records) == 20

        previous = None
        for record in records:
            assert record["previous_record_hash"] == previous
            assert record["record_hash"] == calculate_record_hash(record)
            previous = record["record_hash"]

        latest_record = json.loads(
            latest.read_text(encoding="utf-8")
        )

        assert latest_record == records[-1]
        assert latest_record["record_hash"] == previous

        assert not (runtime / "latest_rollback.tmp").exists()

        unexpected = [
            path
            for path in runtime.iterdir()
            if path.name.endswith(".tmp")
        ]
        assert unexpected == []

    print("ACEE11_PERSISTENCE_DURABILITY_OK")


if __name__ == "__main__":
    main()
