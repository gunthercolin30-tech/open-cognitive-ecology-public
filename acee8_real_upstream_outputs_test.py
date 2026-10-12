from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ontology.acee_autonomous_cycle_manager import (
    AceeAutonomousCycleManager,
    PHASES,
)
from ontology.acee_impact_evaluator import AceeImpactEvaluator
from ontology.acee_validation_runner import AceeValidationRunner


def cycle_inputs(cycle_id: str, score: float, closure_pressure: float) -> dict:
    phase_results = {
        phase: {"status": "completed", "score": score}
        for phase in PHASES
    }
    phase_results["selection"] = {
        "status": "completed",
        "decision": "accept",
        "score": score,
    }
    phase_results["rollback_or_acceptance"] = {
        "status": "completed",
        "decision": "accepted",
        "score": score,
    }
    return {
        "cycle_id": cycle_id,
        "timestamp_utc": "2026-07-13T21:10:00Z",
        "requested_phases": list(PHASES),
        "phase_results": phase_results,
        "governance_decision": {"approved": True},
        "constitutional_decision": {"approved": True},
        "closure_pressure": closure_pressure,
    }


def validation_inputs(validation_id: str, scope: str) -> dict:
    return {
        "validation_id": validation_id,
        "timestamp_utc": "2026-07-13T21:11:00Z",
        "scope": scope,
        "mode": "targeted",
        "command_results": [
            {
                "name": "compile",
                "returncode": 0,
                "stdout": "COMPILE_OK",
                "stderr": "",
                "duration_seconds": 0.01,
            },
            {
                "name": "fast_acceptance",
                "returncode": 0,
                "stdout": "FAST_ACCEPTANCE_OK",
                "stderr": "",
                "duration_seconds": 0.02,
            },
            {
                "name": "final_lock",
                "returncode": 0,
                "stdout": "FINAL_LOCK_OK",
                "stderr": "",
                "duration_seconds": 0.03,
            },
        ],
    }


def main() -> None:
    root = Path("/nonexistent")

    before_cycle = AceeAutonomousCycleManager(root=root).step(
        inputs=cycle_inputs("cycle-before", 0.90, 0.05),
        persist=False,
    )
    after_cycle = AceeAutonomousCycleManager(root=root).step(
        inputs=cycle_inputs("cycle-after", 0.94, 0.04),
        persist=False,
    )
    before_validation = AceeValidationRunner(root=root).step(
        inputs=validation_inputs("validation-before", "acee8-before"),
        persist=False,
    )
    after_validation = AceeValidationRunner(root=root).step(
        inputs=validation_inputs("validation-after", "acee8-after"),
        persist=False,
    )

    assert before_cycle["cycle_complete"] is True
    assert after_cycle["cycle_complete"] is True
    assert before_validation["validation_passed"] is True
    assert after_validation["validation_passed"] is True

    # ACEE4 and ACEE7 are genuine upstream outputs. Specialized scores are
    # supplied by their existing metric producers; ACEE8 only normalizes them.
    before = {
        "cycle": before_cycle,
        "validation": {
            **before_validation,
            "modules_discovered": 1200,
            "active_primitives": 1100,
        },
        "stability_score": 0.89,
        "governance_score": 0.91,
        "evolution_score": 0.72,
        "closure_pressure": 0.22,
        "runtime_score": 0.88,
    }
    after = {
        "cycle": after_cycle,
        "validation": {
            **after_validation,
            "modules_discovered": 1201,
            "active_primitives": 1101,
        },
        "stability_score": 0.92,
        "governance_score": 0.93,
        "evolution_score": 0.78,
        "closure_pressure": 0.18,
        "runtime_score": 0.91,
    }

    result = AceeImpactEvaluator(root=root).step(
        inputs={
            "evaluation_id": "real-upstream-output-evaluation",
            "cycle_id": after_cycle["cycle_id"],
            "validation_id": after_validation["validation_id"],
            "before": before,
            "after": after,
        },
        persist=False,
    )

    assert result["impact_status"] == "ACEE_IMPACT_EVALUATED"
    assert result["comparison_valid"] is True
    assert result["source_ids"]["cycle_id"] == "cycle-after"
    assert result["source_ids"]["validation_id"] == "validation-after"
    assert result["after_metric_sources"]["error_count"].startswith("validation.")
    assert result["after_metric_sources"]["modules_discovered"].startswith("validation.")
    assert result["after_metric_sources"]["active_primitives"].startswith("validation.")
    assert result["metric_classifications"]["closure_pressure"] == "improved"
    assert result["validation_executed_by_evaluator"] is False
    assert result["rollback_executed"] is False
    assert result["causal_effect_resolved"] is False
    assert result["selection_decision_made"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True

    print("ACEE8_REAL_UPSTREAM_OUTPUTS_OK")


if __name__ == "__main__":
    main()
