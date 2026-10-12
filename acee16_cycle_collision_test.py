from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        tracker = AceeLongitudinalTracker(root=root)

        first = tracker.step(
            inputs={
                "operation": "record_cycle",
                "transaction_id": "COL16-FIRST",
                "cycle_id": "COL16-CYCLE",
                "timestamp_utc": "2026-07-14T11:00:00Z",
                "before_score": 0.40,
                "after_score": 0.50,
                "selection_decision": {"decision": "accept"},
            },
            persist=True,
        )
        assert first["record_created"] is True
        assert first["persisted"] is True

        collision = tracker.step(
            inputs={
                "operation": "record_cycle",
                "transaction_id": "COL16-SECOND",
                "cycle_id": "COL16-CYCLE",
                "timestamp_utc": "2026-07-14T11:01:00Z",
                "before_score": 0.50,
                "after_score": 0.70,
                "selection_decision": {"decision": "rollback"},
            },
            persist=True,
        )
        assert collision["record_created"] is False
        assert collision["persisted"] is False
        assert (
            "cycle_id_already_recorded"
            in collision["blocking_reasons"]
        )

        replay = tracker.step(
            inputs={
                "operation": "record_cycle",
                "transaction_id": "COL16-FIRST",
                "cycle_id": "COL16-CYCLE",
                "timestamp_utc": "2026-07-14T11:00:00Z",
                "before_score": 0.40,
                "after_score": 0.50,
                "selection_decision": {"decision": "accept"},
            },
            persist=True,
        )
        assert replay["idempotent_replay"] is True
        assert replay["record_hash"] == first["record_hash"]

        runtime = (
            root
            / "acee_runtime"
            / "ACEE16_acee_longitudinal_tracker"
        )
        index = json.loads(
            (runtime / "cycle_index.json").read_text(encoding="utf-8")
        )
        assert list(index["cycles"]) == ["COL16-CYCLE"]
        assert len(index["processed_transactions"]) == 1

        history = [
            json.loads(line)
            for line in (runtime / "cycle_history.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        assert len(history) == 1
        assert history[0]["decision"] == "accept"

    print("ACEE16_CYCLE_COLLISION_OK")


if __name__ == "__main__":
    main()
