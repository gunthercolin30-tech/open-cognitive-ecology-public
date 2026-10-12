from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker


def record(tracker, transaction_id, cycle_id, cycle_result, rollback_result):
    return tracker.step(
        inputs={
            "operation": "record_cycle",
            "transaction_id": transaction_id,
            "cycle_id": cycle_id,
            "before_score": 0.50,
            "after_score": 0.50,
            "cycle_result": cycle_result,
            "rollback_result": rollback_result,
        },
        persist=True,
    )


def main() -> None:
    with TemporaryDirectory() as tmp:
        tracker = AceeLongitudinalTracker(root=Path(tmp))

        accepted = record(
            tracker,
            "RBSEM-ACCEPTED",
            "RBSEM-CYCLE-ACCEPTED",
            {"rollback_completed": True, "cycle_outcome": "accepted"},
            {
                "rollback_ready": True,
                "rollback_performed": False,
                "rollback_status": "ACEE_ROLLBACK_ENGINE_READY",
            },
        )
        assert accepted["rollback_phase_completed"] is True
        assert accepted["rollback_performed"] is False

        pending = record(
            tracker,
            "RBSEM-PENDING",
            "RBSEM-CYCLE-PENDING",
            {"rollback_completed": False, "cycle_outcome": "rollback_pending"},
            {
                "rollback_ready": True,
                "rollback_performed": False,
                "rollback_status": "rollback_pending",
            },
        )
        assert pending["rollback_phase_completed"] is False
        assert pending["rollback_performed"] is False

        executed = record(
            tracker,
            "RBSEM-EXECUTED",
            "RBSEM-CYCLE-EXECUTED",
            {"rollback_completed": True, "cycle_outcome": "rolled_back"},
            {
                "rollback_ready": True,
                "rollback_performed": True,
                "rollback_status": "rolled_back",
            },
        )
        assert executed["rollback_phase_completed"] is True
        assert executed["rollback_performed"] is True

        summary = tracker.step(
            inputs={"operation": "summarize_trajectory"},
            persist=False,
        )["trajectory_summary"]
        assert summary["cycle_count"] == 3
        assert summary["rollback_phase_completed_count"] == 2
        assert summary["rollback_count"] == 1

    print("ACEE16_ROLLBACK_SEMANTICS_OK")


if __name__ == "__main__":
    main()
