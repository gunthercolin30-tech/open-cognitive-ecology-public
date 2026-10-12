from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        scheduler = AceeAutonomousScheduler(root=root)

        cycle_request = {
            "requested_phases": ["snapshot", "selection"],
            "phase_results": {
                "snapshot": {
                    "passed": True,
                    "score": 0.96,
                },
                "selection": {
                    "passed": True,
                    "score": 0.94,
                    "decision": "accept",
                },
            },
            "governance_decision": {
                "approved": True,
                "passed": True,
            },
            "constitutional_decision": {
                "approved": True,
                "passed": True,
            },
            "closure_pressure": 0.05,
            "closure_pressure_threshold": 0.20,
        }

        scheduled = scheduler.step(
            inputs={
                "operation": "schedule_cycle",
                "transaction_id": "REAL15-SCHEDULE",
                "cycle_id": "REAL15-CYCLE",
                "due_at_utc": "2026-07-14T08:00:00Z",
                "priority": 0.95,
                "governance_authorization": {"approved": True},
                "constitutional_authorization": {"approved": True},
                "cycle_request": cycle_request,
            },
            persist=True,
        )
        assert scheduled["autonomous_scheduler_ready"] is True
        assert scheduled["schedule_updated"] is True

        dispatched = scheduler.step(
            inputs={
                "operation": "dispatch_due_cycles",
                "transaction_id": "REAL15-DISPATCH",
                "now_utc": "2026-07-14T09:00:00Z",
                "max_dispatch": 1,
            },
            persist=True,
        )
        assert dispatched["cycle_dispatch_ready"] is True
        assert dispatched["dispatch_count"] == 1
        assert dispatched["acee4_executed_by_scheduler"] is False
        assert dispatched["cycle_executed_by_scheduler"] is False

        order = dispatched["dispatch_orders"][0]
        assert order["cycle_id"] == "REAL15-CYCLE"
        assert order["target_primitive"] == "acee_autonomous_cycle_manager"
        assert order["target_step"] == "step"
        assert order["execution_authorized"] is False
        assert order["requested_phases"] == ["snapshot", "selection"]
        assert order["cycle_inputs"] == cycle_request

        acee4_inputs = {
            **order["cycle_inputs"],
            "cycle_id": order["cycle_id"],
            "timestamp_utc": "2026-07-14T09:00:01Z",
        }
        cycle = AceeAutonomousCycleManager(root=root).step(
            inputs=acee4_inputs,
            persist=False,
        )
        assert cycle["cycle_id"] == order["cycle_id"]
        assert cycle["requested_phases"] == order["requested_phases"]
        assert cycle["cycle_complete"] is True
        assert cycle["accepted"] is True
        assert cycle["cycle_outcome"] == "accepted"
        assert cycle["governance_compliant"] is True
        assert cycle["constitutional_compliant"] is True
        assert cycle["runtime_executed"] is False
        assert cycle["execution_dispatched"] is False

    print("ACEE15_REAL_ACEE4_INTEGRATION_OK")


if __name__ == "__main__":
    main()
