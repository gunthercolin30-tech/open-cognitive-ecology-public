from __future__ import annotations
from copy import deepcopy
from acee4_fast_acceptance_suite import context as build_context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager


def main() -> None:
    cycle_context = deepcopy(build_context())
    cycle_context["cycle_id"] = "fake-rollback-completion"
    cycle_context["phase_results"]["validation"] = {
        "status": "failed", "success": False, "passed": False, "score": 0.0,
    }
    cycle_context["phase_results"]["selection"] = {
        "decision": "rollback", "status": "rollback_required", "score": 0.0,
    }
    cycle_context["phase_results"]["rollback_or_acceptance"] = {
        "rollback_completed": True,
        "rollback_result": {"rollback_status": "UNKNOWN", "rollback_performed": False},
    }
    result = AceeAutonomousCycleManager().step(inputs=cycle_context, persist=False)
    assert result["accepted"] is False
    assert result["rollback_required"] is True
    assert result["rollback_completed"] is False
    assert result["cycle_outcome"] != "rolled_back"
    print("ACEE4_FAKE_ROLLBACK_COMPLETION_BLOCKED_OK")


if __name__ == "__main__":
    main()
