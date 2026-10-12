from __future__ import annotations

from copy import deepcopy

from acee4_fast_acceptance_suite import context as build_context
from ontology.acee_autonomous_cycle_manager import (
    AceeAutonomousCycleManager,
)


def main() -> None:
    cycle_context = deepcopy(build_context())
    cycle_context["cycle_id"] = "contradictory-phase-result"

    cycle_context["phase_results"]["validation"].update(
        {
            "success": True,
            "passed": False,
            "validation_status": "failed",
        }
    )

    cycle_context["phase_results"]["rollback_or_acceptance"] = {
        "rollback_completed": False,
        "rollback_result": {
            "rollback_status": "ACEE_ROLLBACK_NOT_EXECUTED",
            "rollback_performed": False,
        },
    }

    result = AceeAutonomousCycleManager().step(
        inputs=cycle_context,
        persist=False,
    )

    assert result["cycle_complete"] is False
    assert result["accepted"] is False
    assert "validation" in result["failed_phases"]
    assert result["rollback_required"] is True
    assert result["rollback_completed"] is False
    assert result["cycle_outcome"] != "accepted"

    print("ACEE4_CONTRADICTORY_PHASE_RESULT_BLOCKED_OK")


if __name__ == "__main__":
    main()
