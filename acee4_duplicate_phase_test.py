from __future__ import annotations
from copy import deepcopy
from acee4_fast_acceptance_suite import context as build_context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager


def main() -> None:
    cycle_context = deepcopy(build_context())
    cycle_context["cycle_id"] = "duplicate-phase-test"
    cycle_context["requested_phases"] = [
        "snapshot", "diagnostic", "hypothesis", "intervention", "sandbox",
        "validation", "validation", "impact_measurement", "selection",
        "rollback_or_acceptance", "history_update",
    ]
    result = AceeAutonomousCycleManager().step(inputs=cycle_context, persist=False)
    assert result["accepted"] is False
    assert result["cycle_complete"] is False
    assert "phase_order_invalid" in result["blocking_reasons"]
    print("ACEE4_DUPLICATE_PHASE_BLOCKED_OK")


if __name__ == "__main__":
    main()
