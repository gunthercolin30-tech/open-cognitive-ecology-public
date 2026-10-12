from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_architecture_genealogy import AceeArchitectureGenealogy
from ontology.acee_lineage_manager import AceeLineageManager
from ontology.acee_selection_policy import AceeSelectionPolicy


def selection_context() -> dict:
    return {
        "selection_id": "SEL-REAL-13",
        "timestamp_utc": "2026-07-13T22:10:00Z",
        "impact_evaluation": {
            "comparison_valid": True,
            "impact_score": 0.12,
            "metric_classifications": {"closure_pressure": "unchanged"},
        },
        "causal_analysis": {
            "ready_for_selection": True,
            "causal_effect_resolved": True,
            "causal_probability": 0.94,
            "causal_confidence": 0.95,
            "effect_size": 0.12,
            "effect_direction": "beneficial",
        },
        "stability_evidence": {"stability_score": 0.93},
        "simplicity_evidence": {"simplicity_score": 0.88},
        "reversibility_evidence": {
            "mean_reversibility_score": 0.96,
            "reversibility_assured": True,
        },
        "non_closure_evidence": {
            "closure_pressure": 0.08,
            "non_closure_score": 0.94,
        },
        "constitutional_evidence": {
            "compliant": True,
            "constitutional_compliance_score": 0.96,
        },
        "governance_evidence": {
            "approved": True,
            "governance_score": 0.95,
        },
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        lineage = AceeLineageManager(root=root)

        lineage.step(
            inputs={
                "operation": "register_root",
                "transaction_id": "TX-ROOT",
                "lineage_id": "LINEAGE-REAL",
                "architecture_id": "ARCH-REAL-0",
                "timestamp_utc": "2026-07-13T22:00:00Z",
            },
            persist=True,
        )
        lineage.step(
            inputs={
                "operation": "register_candidate",
                "transaction_id": "TX-CANDIDATE",
                "lineage_id": "LINEAGE-REAL",
                "generation_id": 1,
                "architecture_id": "ARCH-REAL-1",
                "parent_id": "ARCH-REAL-0",
                "mutation_id": "MUT-REAL-1",
                "fitness_delta": 0.12,
                "timestamp_utc": "2026-07-13T22:05:00Z",
            },
            persist=True,
        )

        decision = AceeSelectionPolicy(root=root).step(
            inputs=selection_context(),
            persist=True,
        )
        assert decision["selection_decision_ready"] is True
        assert decision["decision"] == "accept"

        managed = lineage.step(
            inputs={
                "operation": "apply_selection",
                "transaction_id": "TX-SELECTION",
                "lineage_id": "LINEAGE-REAL",
                "generation_id": 1,
                "selection_decision": decision,
                "timestamp_utc": "2026-07-13T22:11:00Z",
            },
            persist=True,
        )
        assert managed["generation_status"] == "active"
        assert managed["active_generation_id"] == 1
        assert managed["selection_executed_by_lineage_manager"] is False

        event = managed["genealogy_event"]
        assert event["architecture_id"] == "ARCH-REAL-1"
        assert event["parent_architecture_id"] == "ARCH-REAL-0"
        assert event["generation_id"] == 1
        assert event["mutation_id"] == "MUT-REAL-1"
        assert event["selection_reason"] == "beneficial_causal_stable_simple_reversible_compliant"
        assert event["fitness_delta"] == 0.12

        genealogy_engine = AceeArchitectureGenealogy(root=root)
        genealogy_root = genealogy_engine.step(
            inputs={
                "architecture_id": "ARCH-REAL-0",
                "architecture": {
                    "architecture_id": "ARCH-REAL-0",
                    "modules": ["acee_lineage_manager"],
                    "parameters": {"generation": 0},
                },
                "parent_architecture_id": None,
                "generation_id": 0,
                "mutation_id": None,
                "selection_decision": {
                    "selection_id": "SEL-ROOT-13",
                    "decision": "accept",
                },
                "causal_analysis": {"analysis_id": "CAUSAL-ROOT-13"},
                "impact_evaluation": {"evaluation_id": "IMPACT-ROOT-13"},
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
                "selection_decision": decision,
                "architecture": {
                    "architecture_id": event["architecture_id"],
                    "modules": ["acee_lineage_manager"],
                    "parameters": {"generation": event["generation_id"]},
                },
                "causal_analysis": {
                    "analysis_id": "CAUSAL-REAL-13",
                    "ready_for_selection": True,
                },
                "impact_evaluation": {
                    "evaluation_id": "IMPACT-REAL-13",
                    "comparison_valid": True,
                },
                "continuity_evidence": {"lineage_integrity": 0.95},
                "diversity_evidence": {"lineage_diversity_score": 0.88},
                "inheritance_evidence": {"inheritance_fidelity": 0.96},
                "rollback_status": "not_rolled_back",
                "timestamp_utc": "2026-07-13T22:12:00Z",
            },
            persist=True,
        )
        assert genealogy["genealogy_ready"] is True
        assert genealogy["architecture_id"] == event["architecture_id"]
        assert genealogy["parent_architecture_id"] == event["parent_architecture_id"]
        assert genealogy["generation_id"] == event["generation_id"]
        assert genealogy["mutation_id"] == event["mutation_id"]
        assert genealogy["selection_decision_id"] == decision["selection_id"]
        assert genealogy["selection_executed_by_genealogy"] is False
        assert genealogy["rollback_executed_by_genealogy"] is False

    print("ACEE13_REAL_SELECTION_GENEALOGY_INTEGRATION_OK")


if __name__ == "__main__":
    main()
