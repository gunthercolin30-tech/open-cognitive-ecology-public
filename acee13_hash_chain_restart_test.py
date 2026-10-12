from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_lineage_manager import AceeLineageManager


EXCLUDED_FROM_HASH = {
    "event_hash",
    "persisted",
    "state_path",
    "history_path",
    "lineages_path",
}


def canonical(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def event_hash(record: dict) -> str:
    payload = {
        key: value
        for key, value in record.items()
        if key not in EXCLUDED_FROM_HASH
    }
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def load_records(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def verify_chain(records: list[dict]) -> None:
    previous_hash = None
    for record in records:
        assert record["previous_event_hash"] == previous_hash
        assert record["event_hash"] == event_hash(record)
        previous_hash = record["event_hash"]


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = AceeLineageManager(root=root)
        first.step(
            inputs={
                "operation": "register_root",
                "transaction_id": "HC-0",
                "lineage_id": "LINEAGE-HC",
                "architecture_id": "ARCH-HC-0",
                "timestamp_utc": "2026-07-13T22:30:00Z",
            },
            persist=True,
        )
        first.step(
            inputs={
                "operation": "register_candidate",
                "transaction_id": "HC-1",
                "lineage_id": "LINEAGE-HC",
                "generation_id": 1,
                "architecture_id": "ARCH-HC-1",
                "parent_id": "ARCH-HC-0",
                "mutation_id": "MUT-HC-1",
                "fitness_delta": 0.10,
                "timestamp_utc": "2026-07-13T22:31:00Z",
            },
            persist=True,
        )

        history = (
            root / "acee_runtime" / "ACEE13_acee_lineage_manager"
            / "lineage_event_history.jsonl"
        )
        before_restart = load_records(history)
        assert len(before_restart) == 2
        verify_chain(before_restart)
        boundary_hash = before_restart[-1]["event_hash"]

        restarted = AceeLineageManager(root=root)
        third = restarted.step(
            inputs={
                "operation": "apply_selection",
                "transaction_id": "HC-2",
                "lineage_id": "LINEAGE-HC",
                "generation_id": 1,
                "selection_decision": {
                    "selection_id": "SEL-HC-1",
                    "selection_decision_ready": True,
                    "decision": "accept",
                    "decision_reasons": ["hash_chain_restart_test"],
                },
                "timestamp_utc": "2026-07-13T22:32:00Z",
            },
            persist=True,
        )
        assert third["persisted"] is True
        assert third["previous_event_hash"] == boundary_hash

        after_restart = load_records(history)
        assert len(after_restart) == 3
        assert after_restart[:2] == before_restart
        verify_chain(after_restart)

        inspection = AceeLineageManager(root=root).step(
            inputs={
                "operation": "inspect",
                "lineage_id": "LINEAGE-HC",
            },
            persist=False,
        )
        assert inspection["history_corrupted"] is False
        assert inspection["active_generation_id"] == 1

    print("ACEE13_HASH_CHAIN_RESTART_OK")


if __name__ == "__main__":
    main()
