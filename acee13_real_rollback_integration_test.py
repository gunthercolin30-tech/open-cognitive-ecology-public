from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_architecture_genealogy import AceeArchitectureGenealogy
from ontology.acee_lineage_manager import AceeLineageManager
from ontology.acee_rollback_engine import AceeRollbackEngine
from ontology.acee_selection_policy import AceeSelectionPolicy


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rollback_selection_context() -> dict:
    return {
        "selection_id": "SEL-ROLLBACK-REAL-13",
        "timestamp_utc": "2026-07-13T22:20:00Z",
        "impact_evaluation": {
            "comparison_valid": True,
            "impact_score": -0.20,
            "metric_classifications": {"closure_pressure": "increased"},
        },
        "causal_analysis": {
            "ready_for_selection": True,
            "causal_effect_resolved": True,
            "causal_probability": 0.96,
            "causal_confidence": 0.96,
            "effect_size": -0.20,
            "effect_direction": "harmful",
        },
        "stability_evidence": {"stability_score": 0.70},
        "simplicity_evidence": {"simplicity_score": 0.85},
        "reversibility_evidence": {
            "mean_reversibility_score": 0.98,
            "reversibility_assured": True,
        },
        "non_closure_evidence": {
            "closure_pressure": 0.75,
            "non_closure_score": 0.20,
        },
        "constitutional_evidence": {
            "compliant": True,
            "constitutional_compliance_score": 0.95,
        },
        "governance_evidence": {
            "approved": True,
            "governance_score": 0.95,
        },
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        module_dir = root / "ontology"
        module_dir.mkdir(parents=True)
        destination = module_dir / "candidate.py"
        backup = module_dir / "candidate.py.bak"
        destination.write_text("VALUE = 'candidate'\n", encoding="utf-8")
        backup.write_text("VALUE = 'parent'\n", encoding="utf-8")

        lineage = AceeLineageManager(root=root)
        lineage.step(
            inputs={
                "operation": "register_root",
                "transaction_id": "RB-ROOT",
                "lineage_id": "LINEAGE-RB",
                "architecture_id": "ARCH-RB-0",
            },
            persist=True,
        )
        lineage.step(
            inputs={
                "operation": "register_candidate",
                "transaction_id": "RB-CANDIDATE",
                "lineage_id": "LINEAGE-RB",
                "generation_id": 1,
                "architecture_id": "ARCH-RB-1",
                "parent_id": "ARCH-RB-0",
                "mutation_id": "MUT-RB-1",
                "fitness_delta": -0.20,
            },
            persist=True,
        )
        lineage.step(
            inputs={
                "operation": "apply_selection",
                "transaction_id": "RB-ACTIVATE",
                "lineage_id": "LINEAGE-RB",
                "generation_id": 1,
                "selection_decision": {
                    "selection_id": "SEL-ACTIVATE",
                    "selection_decision_ready": True,
                    "decision": "accept",
                    "decision_reasons": ["initial_candidate_activation"],
                },
            },
            persist=True,
        )

        rollback_decision = AceeSelectionPolicy(root=root).step(
            inputs=rollback_selection_context(),
            persist=True,
        )
        assert rollback_decision["decision"] == "rollback"
        assert rollback_decision["rollback_requested"] is True
        assert rollback_decision["rollback_executed"] is False

        pending = lineage.step(
            inputs={
                "operation": "apply_selection",
                "transaction_id": "RB-PENDING",
                "lineage_id": "LINEAGE-RB",
                "generation_id": 1,
                "selection_decision": rollback_decision,
            },
            persist=True,
        )
        assert pending["generation_status"] == "rollback_pending"
        assert pending["active_generation_id"] == 1

        rollback_result = AceeRollbackEngine(root=root).step(
            inputs={
                "rollback_request": {
                    "transaction_id": "ACEE11-RB-REAL-13",
                    "reason": "stability_regression",
                    "targets": [{
                        "destination": "ontology/candidate.py",
                        "backup": "ontology/candidate.py.bak",
                        "expected_backup_sha256": sha256(backup),
                    }],
                },
                "governance_authorization": {"approved": True},
                "constitutional_authorization": {"approved": True},
                "dry_run": False,
                "execute": True,
                "timestamp_utc": "2026-07-13T22:21:00Z",
            },
            persist=True,
        )
        assert rollback_result["rollback_performed"] is True
        assert rollback_result["restored_count"] == 1
        assert destination.read_text(encoding="utf-8") == "VALUE = 'parent'\n"

        completed = lineage.step(
            inputs={
                "operation": "record_rollback",
                "transaction_id": "RB-COMPLETED",
                "lineage_id": "LINEAGE-RB",
                "generation_id": 1,
                "rollback_result": rollback_result,
            },
            persist=True,
        )
        assert completed["generation_status"] == "rolled_back"
        assert completed["active_generation_id"] == 0

        event = completed["genealogy_event"]
        assert event["rollback_status"] == "rolled_back"

        genealogy_engine = AceeArchitectureGenealogy(root=root)
        genealogy_root = genealogy_engine.step(
            inputs={
                "architecture_id": "ARCH-RB-0",
                "architecture": {
                    "architecture_id": "ARCH-RB-0",
                    "modules": ["candidate"],
                    "parameters": {"generation": 0},
                },
                "parent_architecture_id": None,
                "generation_id": 0,
                "mutation_id": None,
                "selection_decision": {
                    "selection_id": "SEL-RB-ROOT-13",
                    "decision": "accept",
                },
                "causal_analysis": {"analysis_id": "CAUSAL-RB-ROOT-13"},
                "impact_evaluation": {"evaluation_id": "IMPACT-RB-ROOT-13"},
                "rollback_status": "not_rolled_back",
                "continuity_evidence": {"lineage_integrity": 1.0},
                "diversity_evidence": {"lineage_diversity_score": 1.0},
                "inheritance_evidence": {"inheritance_fidelity": 1.0},
            },
            persist=True,
        )
        assert genealogy_root["genealogy_ready"] is True

        genealogy = genealogy_engine.step(
            inputs={
                **event,
                "architecture": {
                    "architecture_id": event["architecture_id"],
                    "modules": ["candidate"],
                    "parameters": {"rolled_back": True},
                },
                "selection_decision": {
                    "selection_id": "SEL-ACTIVATE",
                    "decision": "accept",
                },
                "causal_analysis": {
                    "analysis_id": "CAUSAL-RB-13",
                    "ready_for_selection": True,
                },
                "impact_evaluation": {
                    "evaluation_id": "IMPACT-RB-13",
                    "comparison_valid": True,
                },
                "continuity_evidence": {"lineage_integrity": 0.94},
                "diversity_evidence": {"lineage_diversity_score": 0.87},
                "inheritance_evidence": {"inheritance_fidelity": 0.95},
                "rollback_status": "rolled_back",
            },
            persist=True,
        )
        assert genealogy["genealogy_ready"] is True
        assert genealogy["rollback_status"] == "rolled_back"
        assert genealogy["active"] is False
        assert genealogy["rollback_executed_by_genealogy"] is False

    print("ACEE13_REAL_ROLLBACK_INTEGRATION_OK")


if __name__ == "__main__":
    main()
