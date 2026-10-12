from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker


def canonical(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def record_hash(record: dict) -> str:
    payload = {
        key: value
        for key, value in record.items()
        if key != "record_hash"
    }
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        tracker = AceeLongitudinalTracker(root=root)

        for index in range(40):
            result = tracker.step(
                inputs={
                    "operation": "record_cycle",
                    "transaction_id": f"HASH16-TX-{index:02d}",
                    "cycle_id": f"HASH16-CYCLE-{index:02d}",
                    "timestamp_utc": (
                        f"2026-07-14T10:{index:02d}:00Z"
                    ),
                    "before_score": index / 100.0,
                    "after_score": (index + 1) / 100.0,
                    "validation_result": {
                        "validation_passed": index % 7 != 0,
                    },
                    "selection_decision": {
                        "decision": (
                            "accept" if index % 3 else "repeat"
                        ),
                    },
                    "rollback_result": {
                        "rollback_performed": index in {13, 27},
                    },
                },
                persist=True,
            )
            assert result["persisted"] is True

        history_path = (
            root
            / "acee_runtime"
            / "ACEE16_acee_longitudinal_tracker"
            / "cycle_history.jsonl"
        )
        records = [
            json.loads(line)
            for line in history_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(records) == 40

        previous = None
        for index, record in enumerate(records):
            assert record["cycle_id"] == f"HASH16-CYCLE-{index:02d}"
            assert record["previous_record_hash"] == previous
            assert record["record_hash"] == record_hash(record)
            previous = record["record_hash"]

        restarted = AceeLongitudinalTracker(root=root)
        verified = restarted.step(
            inputs={"operation": "verify_history"},
            persist=False,
        )
        assert verified["history_valid"] is True
        assert verified["verified_record_count"] == 40

        continued = restarted.step(
            inputs={
                "operation": "record_cycle",
                "transaction_id": "HASH16-CONTINUE",
                "cycle_id": "HASH16-CYCLE-40",
                "timestamp_utc": "2026-07-14T10:40:00Z",
                "before_score": 0.40,
                "after_score": 0.41,
            },
            persist=True,
        )
        assert continued["previous_record_hash"] == previous

    print("ACEE16_HASH_CHAIN_OK")


if __name__ == "__main__":
    main()
