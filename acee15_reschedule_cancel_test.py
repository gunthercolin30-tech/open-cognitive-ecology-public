from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler


AUTH = {
    "governance_authorization": {"approved": True},
    "constitutional_authorization": {"approved": True},
}


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        scheduler = AceeAutonomousScheduler(root=root)

        scheduled = scheduler.step(
            inputs={
                "operation": "schedule_cycle",
                "transaction_id": "RC-SCHEDULE",
                "cycle_id": "RC-CYCLE",
                "due_at_utc": "2026-07-14T12:00:00Z",
                "priority": 0.40,
                "cycle_request": {
                    "requested_phases": ["snapshot"],
                    "revision": 1,
                },
                **AUTH,
            },
            persist=True,
        )
        assert scheduled["scheduled_cycle"]["status"] == "pending"

        cancelled = scheduler.step(
            inputs={
                "operation": "cancel_cycle",
                "transaction_id": "RC-CANCEL",
                "cycle_id": "RC-CYCLE",
            },
            persist=True,
        )
        assert cancelled["schedule_updated"] is True

        inspection = scheduler.step(
            inputs={
                "operation": "inspect_schedule",
                "cycle_id": "RC-CYCLE",
            },
            persist=False,
        )
        assert inspection["cycle"]["status"] == "cancelled"

        no_dispatch = scheduler.step(
            inputs={
                "operation": "dispatch_due_cycles",
                "transaction_id": "RC-DISPATCH-CANCELLED",
                "now_utc": "2026-07-14T13:00:00Z",
                "max_dispatch": 1,
            },
            persist=True,
        )
        assert no_dispatch["dispatch_count"] == 0
        assert no_dispatch["cycle_dispatch_ready"] is False

        rescheduled = scheduler.step(
            inputs={
                "operation": "reschedule_cycle",
                "transaction_id": "RC-RESCHEDULE",
                "cycle_id": "RC-CYCLE",
                "due_at_utc": "2026-07-14T14:00:00Z",
                "priority": 0.90,
                "cycle_request": {
                    "requested_phases": ["snapshot", "diagnostic"],
                    "revision": 2,
                },
                **AUTH,
            },
            persist=True,
        )
        assert rescheduled["scheduled_cycle"]["status"] == "pending"
        assert rescheduled["scheduled_cycle"]["priority"] == 0.90
        assert (
            rescheduled["scheduled_cycle"]["cycle_request"]["revision"]
            == 2
        )

        too_early = scheduler.step(
            inputs={
                "operation": "dispatch_due_cycles",
                "transaction_id": "RC-DISPATCH-EARLY",
                "now_utc": "2026-07-14T13:59:59Z",
                "max_dispatch": 1,
            },
            persist=True,
        )
        assert too_early["dispatch_count"] == 0

        dispatched = scheduler.step(
            inputs={
                "operation": "dispatch_due_cycles",
                "transaction_id": "RC-DISPATCH-DUE",
                "now_utc": "2026-07-14T14:00:00Z",
                "max_dispatch": 1,
            },
            persist=True,
        )
        assert dispatched["dispatch_count"] == 1
        order = dispatched["dispatch_orders"][0]
        assert order["cycle_id"] == "RC-CYCLE"
        assert order["requested_phases"] == ["snapshot", "diagnostic"]
        assert order["cycle_inputs"]["revision"] == 2

        rejected_cancel = scheduler.step(
            inputs={
                "operation": "cancel_cycle",
                "transaction_id": "RC-CANCEL-AFTER-DISPATCH",
                "cycle_id": "RC-CYCLE",
            },
            persist=True,
        )
        assert rejected_cancel["persisted"] is False
        assert "cycle_already_dispatched" in rejected_cancel["blocking_reasons"]

        history_path = (
            root
            / "acee_runtime"
            / "ACEE15_acee_autonomous_scheduler"
            / "schedule_history.jsonl"
        )
        history = [
            json.loads(line)
            for line in history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        operations = [record["operation"] for record in history]
        assert operations == [
            "schedule_cycle",
            "cancel_cycle",
            "dispatch_due_cycles",
            "reschedule_cycle",
            "dispatch_due_cycles",
            "dispatch_due_cycles",
        ]

    print("ACEE15_RESCHEDULE_CANCEL_OK")


if __name__ == "__main__":
    main()
