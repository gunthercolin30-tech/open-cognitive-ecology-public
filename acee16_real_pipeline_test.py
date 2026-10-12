from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_autonomous_cycle_manager import (
    AceeAutonomousCycleManager,
    PHASES,
)
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler
from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
from ontology.acee_impact_evaluator import AceeImpactEvaluator
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker
from ontology.acee_rollback_engine import AceeRollbackEngine
from ontology.acee_selection_policy import AceeSelectionPolicy
from ontology.acee_validation_runner import AceeValidationRunner


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        scheduler = AceeAutonomousScheduler(root=root)
        scheduler.step(
            inputs={
                "operation": "schedule_cycle",
                "transaction_id": "PIPE16-SCHEDULE",
                "cycle_id": "PIPE16-CYCLE",
                "due_at_utc": "2026-07-14T08:00:00Z",
                "priority": 0.95,
                "governance_authorization": {"approved": True},
                "constitutional_authorization": {"approved": True},
                "cycle_request": {"requested_phases": list(PHASES)},
            },
            persist=True,
        )
        scheduling = scheduler.step(
            inputs={
                "operation": "dispatch_due_cycles",
                "transaction_id": "PIPE16-DISPATCH",
                "now_utc": "2026-07-14T09:00:00Z",
                "max_dispatch": 1,
            },
            persist=True,
        )
        assert scheduling["cycle_dispatch_ready"] is True
        dispatch = scheduling["dispatch_orders"][0]

        phase_results = {
            phase: {"status": "completed", "score": 0.95}
            for phase in PHASES
        }
        phase_results["selection"] = {
            "status": "completed",
            "decision": "accept",
            "score": 0.96,
        }
        phase_results["rollback_or_acceptance"] = {
            "status": "completed",
            "decision": "accepted",
            "score": 0.95,
        }
        cycle = AceeAutonomousCycleManager(root=root).step(
            inputs={
                "cycle_id": dispatch["cycle_id"],
                "timestamp_utc": "2026-07-14T09:00:01Z",
                "requested_phases": list(PHASES),
                "phase_results": phase_results,
                "governance_decision": {"approved": True},
                "constitutional_decision": {"approved": True},
                "closure_pressure": 0.05,
            },
            persist=False,
        )
        assert cycle["cycle_complete"] is True
        assert cycle["accepted"] is True

        validation = AceeValidationRunner(root=root).step(
            inputs={
                "validation_id": "PIPE16-VALIDATION",
                "timestamp_utc": "2026-07-14T09:00:02Z",
                "scope": "acee4",
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
                        "stdout": "ACEE4_FAST_ACCEPTANCE_OK",
                        "stderr": "",
                        "duration_seconds": 0.02,
                    },
                    {
                        "name": "final_lock",
                        "returncode": 0,
                        "stdout": (
                            "ACEE_AUTONOMOUS_CYCLE_MANAGER_FINAL_LOCK_OK"
                        ),
                        "stderr": "",
                        "duration_seconds": 0.03,
                    },
                ],
            },
            persist=False,
        )
        assert validation["validation_passed"] is True

        impact = AceeImpactEvaluator(root=root).step(
            inputs={
                "evaluation_id": "PIPE16-IMPACT",
                "timestamp_utc": "2026-07-14T09:00:03Z",
                "cycle_id": "PIPE16-CYCLE",
                "before": {
                    "validation": {
                        "error_count": 0,
                        "modules_discovered": 1200,
                        "active_primitives": 1100,
                        "validation_passed": True,
                    },
                    "stability_score": 0.90,
                    "governance_score": 0.91,
                    "evolution_score": 0.70,
                    "closure_pressure": 0.20,
                    "runtime_score": 0.89,
                },
                "after": {
                    "validation": {
                        "error_count": 0,
                        "modules_discovered": 1201,
                        "active_primitives": 1101,
                        "validation_passed": True,
                        "validation_id": "PIPE16-VALIDATION",
                    },
                    "stability_score": 0.92,
                    "governance_score": 0.93,
                    "evolution_score": 0.76,
                    "closure_pressure": 0.17,
                    "runtime_score": 0.91,
                },
            },
            persist=False,
        )
        assert impact["comparison_valid"] is True
        assert impact["impact_score"] > 0

        causal = AceeCausalEffectAnalyzer(root=root).step(
            inputs={
                "analysis_id": "PIPE16-CAUSAL",
                "impact_evaluation": impact,
                "intervention": {"executed": True},
                "replications": [0.11, 0.12, 0.13, 0.12],
                "counterfactual_effect": 0.0,
                "alternative_explanations": [],
            },
            persist=False,
        )
        assert causal["causal_effect_resolved"] is True
        assert causal["ready_for_selection"] is True

        selection = AceeSelectionPolicy(root=root).step(
            inputs={
                "selection_id": "PIPE16-SELECTION",
                "impact_evaluation": impact,
                "causal_analysis": causal,
                "stability_evidence": {"stability_score": 0.90},
                "simplicity_evidence": {"simplicity_score": 0.80},
                "reversibility_evidence": {
                    "mean_reversibility_score": 0.90,
                    "reversibility_assured": True,
                },
                "non_closure_evidence": {
                    "closure_pressure": 0.10,
                    "non_closure_score": 0.90,
                },
                "constitutional_evidence": {
                    "compliant": True,
                    "constitutional_compliance_score": 0.90,
                },
                "governance_evidence": {
                    "approved": True,
                    "governance_score": 0.90,
                },
            },
            persist=False,
        )
        assert selection["selection_decision_ready"] is True
        assert selection["decision"] == "accept"

        backup = root / "ontology" / "sample.py.bak"
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text("restored = True\n", encoding="utf-8")
        rollback = AceeRollbackEngine(root=root).step(
            inputs={
                "rollback_request": {
                    "transaction_id": "PIPE16-ROLLBACK",
                    "reason": "explicit_governed_request",
                    "targets": [
                        {
                            "destination": "ontology/sample.py",
                            "backup": "ontology/sample.py.bak",
                            "expected_backup_sha256": hashlib.sha256(
                                backup.read_bytes()
                            ).hexdigest(),
                        }
                    ],
                },
                "governance_authorization": {"approved": True},
                "constitutional_authorization": {"approved": True},
                "dry_run": True,
                "execute": False,
                "timestamp_utc": "2026-07-14T09:00:04Z",
            },
            persist=False,
        )
        assert rollback["rollback_ready"] is True
        assert rollback["rollback_performed"] is False

        before_score = 0.89
        after_score = round(before_score + impact["impact_score"], 12)
        tracked = AceeLongitudinalTracker(root=root).step(
            inputs={
                "operation": "record_cycle",
                "transaction_id": "PIPE16-TRACK",
                "cycle_id": "PIPE16-CYCLE",
                "timestamp_utc": "2026-07-14T09:00:05Z",
                "intervention": {"type": "acee_cycle"},
                "before_score": before_score,
                "after_score": after_score,
                "cycle_result": cycle,
                "validation_result": validation,
                "impact_evaluation": impact,
                "causal_analysis": causal,
                "selection_decision": selection,
                "rollback_result": rollback,
                "scheduling_event": dispatch,
            },
            persist=True,
        )
        assert tracked["record_created"] is True
        assert tracked["persisted"] is True
        assert tracked["cycle_id"] == "PIPE16-CYCLE"
        assert tracked["scheduler_cycle_id"] == "PIPE16-CYCLE"
        assert tracked["validation_status"] == validation["validation_status"]
        assert tracked["causal_status"] == "resolved"
        assert tracked["decision"] == "accept"
        assert tracked["rollback_phase_completed"] is True
        assert tracked["rollback_performed"] is False
        assert tracked["score_delta"] == round(
            after_score - before_score,
            12,
        )
        assert set(tracked["source_hashes"]) == {
            "cycle_result",
            "validation_result",
            "impact_evaluation",
            "causal_analysis",
            "selection_decision",
            "rollback_result",
            "scheduling_event",
        }
        assert tracked["cycle_executed_by_tracker"] is False
        assert tracked["validation_executed_by_tracker"] is False
        assert tracked["impact_recomputed_by_tracker"] is False
        assert tracked["causality_recomputed_by_tracker"] is False
        assert tracked["selection_executed_by_tracker"] is False
        assert tracked["rollback_executed_by_tracker"] is False
        assert tracked["scheduling_modified_by_tracker"] is False

    print("ACEE16_REAL_PIPELINE_OK")


if __name__ == "__main__":
    main()
