#!/usr/bin/env python3
from __future__ import annotations

from ontology.axiom_registry import AxiomRegistry
from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
from ontology.countermodel_generator import CountermodelGenerator
from ontology.theorem_dependency_mapper import TheoremDependencyMapper


def ready_inputs() -> dict:
    registry = AxiomRegistry().step(inputs={"synthetic": True, "source": "AN6_LOCK"}, persist=False)
    minimality = AxiomMinimalityAnalyzer().step(inputs={"axiom_registry_result": registry, "synthetic": True}, persist=False)
    countermodels = CountermodelGenerator().step(inputs={"axiom_registry_result": registry, "axiom_minimality_result": minimality, "synthetic": True}, persist=False)
    return {
        "synthetic": True,
        "axiom_registry_result": registry,
        "axiom_minimality_result": minimality,
        "countermodel_generation_result": countermodels,
    }


def main() -> None:
    result = TheoremDependencyMapper().step(inputs=ready_inputs(), persist=False)
    assert result["theorem_dependency_mapping_status"] == "THEOREM_DEPENDENCIES_MAPPED"
    assert result["dependencies_mapped"] is True
    assert result["theorem_dependency_graph"]["node_count"] >= 1
    assert result["theorem_dependency_graph"]["edge_count"] >= 1
    assert result["dependency_metrics"]["theorem_dependency_coverage"] >= 0.95
    assert result["dependency_metrics"]["minimal_usage_coverage"] >= 0.95
    assert result["ready_for_AN7_axiomatic_completeness_certification"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AN6_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
