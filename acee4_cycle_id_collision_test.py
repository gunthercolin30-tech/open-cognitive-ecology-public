from __future__ import annotations
import json
import tempfile
from copy import deepcopy
from pathlib import Path
from acee4_fast_acceptance_suite import context as build_context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        root.mkdir()
        engine = AceeAutonomousCycleManager(root=root)
        first_context = deepcopy(build_context())
        second_context = deepcopy(build_context())
        first_context["cycle_id"] = "same-cycle-id"
        second_context["cycle_id"] = "same-cycle-id"
        first_context["timestamp_utc"] = "2026-07-13T23:55:00Z"
        second_context["timestamp_utc"] = "2026-07-13T23:56:00Z"
        first = engine.step(inputs=first_context, persist=True)
        second = engine.step(inputs=second_context, persist=True)
        history = root / "acee_runtime" / "ACEE4_acee_autonomous_cycle_manager" / "cycle_history.jsonl"
        records = [json.loads(line) for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert first["persisted"] is True and first["accepted"] is True
        assert second["persisted"] is True
        assert second["accepted"] is False
        assert second["cycle_complete"] is False
        assert second["cycle_id_collision"] is True
        assert second["duplicate_cycle_id"] is True
        assert "duplicate_cycle_id" in second["blocking_reasons"]
        assert second["cycle_status"] == "ACEE_AUTONOMOUS_CYCLE_DEGRADED"
        matching = [record for record in records if record["cycle_id"] == "same-cycle-id"]
        assert len(matching) == 2
        assert matching[-1]["previous_cycle_hash"] == matching[-2]["cycle_hash"]
    print("ACEE4_CYCLE_ID_COLLISION_HANDLED_OK")


if __name__ == "__main__":
    main()
