from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker


def main():
    with TemporaryDirectory() as tmp:
        result = AceeLongitudinalTracker(root=Path(tmp)).step(
            inputs={
                "operation": "record_cycle",
                "cycle_id": "B-C",
                "cycle_result": {
                    "cycle_status": "complete",
                    "rollback_completed": True,
                    "cycle_outcome": "accepted",
                },
                "validation_result": {"validation_passed": True},
                "impact_evaluation": {"before_score": 0.3, "after_score": 0.4},
                "selection_decision": {"decision": "accept"},
                "rollback_result": {
                    "rollback_ready": True,
                    "rollback_performed": False,
                },
            },
            persist=False,
        )
        for key in [
            "cycle_executed_by_tracker",
            "validation_executed_by_tracker",
            "impact_recomputed_by_tracker",
            "causality_recomputed_by_tracker",
            "selection_executed_by_tracker",
            "rollback_executed_by_tracker",
        ]:
            assert result[key] is False
        assert result["rollback_phase_completed"] is True
        assert result["rollback_performed"] is False

    print("ACEE16_PRODUCER_BOUNDARY_OK")


if __name__ == "__main__":
    main()
