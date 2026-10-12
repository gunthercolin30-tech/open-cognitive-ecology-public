from __future__ import annotations

import hashlib
import json
import multiprocessing
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


def record_hash(record: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in record.items()
        if key != "record_hash"
    }
    return hashlib.sha256(
        canonical(payload).encode("utf-8")
    ).hexdigest()


def run_transaction(arguments: tuple[str, int]) -> str:
    root_string, index = arguments
    root = Path(root_string)

    destination = root / "ontology" / "sample.py"
    backup = root / "ontology" / "sample.py.bak"

    inputs = {
        "rollback_request": {
            "transaction_id": f"process-{index:02d}",
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
        "timestamp_utc": f"2026-07-13T22:{index:02d}:00Z",
    }

    result = AceeRollbackEngine(root=root).step(
        inputs=inputs,
        persist=True,
    )

    assert result["persisted"] is True
    return result["transaction_id"]


def main() -> None:
    multiprocessing.set_start_method("spawn", force=True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        ontology = root / "ontology"
        ontology.mkdir(parents=True)

        destination = ontology / "sample.py"
        backup = ontology / "sample.py.bak"

        destination.write_text("original = True\n", encoding="utf-8")
        backup.write_text("restored = True\n", encoding="utf-8")

        process_count = 16
        arguments = [
            (str(root), index)
            for index in range(process_count)
        ]

        with multiprocessing.Pool(processes=4) as pool:
            transaction_ids = pool.map(
                run_transaction,
                arguments,
            )

        assert len(transaction_ids) == process_count
        assert len(set(transaction_ids)) == process_count

        history = (
            root
            / "acee_runtime"
            / "ACEE11_acee_rollback_engine"
            / "rollback_history.jsonl"
        )
        latest = history.parent / "latest_rollback.json"

        assert history.is_file()
        assert latest.is_file()

        records = [
            json.loads(line)
            for line in history.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        assert len(records) == process_count
        assert len(
            {record["transaction_id"] for record in records}
        ) == process_count

        previous_hash = None

        for record in records:
            assert record["previous_record_hash"] == previous_hash
            assert record["record_hash"] == record_hash(record)
            previous_hash = record["record_hash"]

        latest_record = json.loads(
            latest.read_text(encoding="utf-8")
        )

        assert latest_record == records[-1]
        assert latest_record["record_hash"] == previous_hash

    print("ACEE11_MULTIPROCESS_PERSISTENCE_OK")


if __name__ == "__main__":
    main()
