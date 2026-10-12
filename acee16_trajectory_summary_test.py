from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker


def main() -> None:
    with TemporaryDirectory() as tmp:
        tracker = AceeLongitudinalTracker(root=Path(tmp))
        cycles = [
            ("S16-1", 0.10, "accept", True, False),
            ("S16-2", 0.20, "accept", True, False),
            ("S16-3", -0.10, "rollback", True, True),
            ("S16-4", 0.00, "repeat", False, False),
            ("S16-5", 0.30, "accept", True, False),
        ]
        for index, (cycle_id, delta, decision, phase_completed, rolled_back) in enumerate(cycles):
            result = tracker.step(
                inputs={
                    "operation": "record_cycle",
                    "transaction_id": f"S16-TX-{index}",
                    "cycle_id": cycle_id,
                    "timestamp_utc": f"2026-07-14T12:0{index}:00Z",
                    "before_score": 0.50,
                    "after_score": 0.50 + delta,
                    "cycle_result": {"rollback_completed": phase_completed},
                    "validation_result": {"validation_passed": index != 2},
                    "selection_decision": {"decision": decision},
                    "rollback_result": {"rollback_performed": rolled_back},
                },
                persist=True,
            )
            assert result["persisted"] is True

        payload = tracker.step(
            inputs={"operation": "summarize_trajectory"},
            persist=False,
        )["trajectory_summary"]
        assert payload["cycle_count"] == 5
        assert payload["accepted_count"] == 3
        assert payload["rollback_phase_completed_count"] == 4
        assert payload["rollback_count"] == 1
        assert payload["mean_score_delta"] == 0.10
        assert payload["latest_cycle_id"] == "S16-5"

    print("ACEE16_TRAJECTORY_SUMMARY_OK")


if __name__ == "__main__":
    main()
