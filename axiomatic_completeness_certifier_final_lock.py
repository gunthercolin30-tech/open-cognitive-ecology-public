#!/usr/bin/env python3
from __future__ import annotations

from ontology.axiom_registry import AxiomRegistry
from ontology.axiom_independence_tester import AxiomIndependenceTester
from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
from ontology.model_generator import ModelGenerator
from ontology.countermodel_generator import CountermodelGenerator
from ontology.theorem_dependency_mapper import TheoremDependencyMapper
from ontology.axiomatic_completeness_certifier import AxiomaticCompletenessCertifier


def ready_inputs() -> dict:
    registry = AxiomRegistry().step(inputs={"synthetic": True, "source": "AN7_LOCK"}, persist=False)
    independence = AxiomIndependenceTester().step(inputs={"axiom_registry_result": registry, "synthetic": True}, persist=False)
    minimality = AxiomMinimalityAnalyzer().step(inputs={"axiom_registry_result": registry, "synthetic": True}, persist=False)
    models = ModelGenerator().step(inputs={"axiom_registry_result": registry, "synthetic": True}, persist=False)
    countermodels = CountermodelGenerator().step(inputs={"axiom_registry_result": registry, "axiom_minimality_result": minimality, "synthetic": True}, persist=False)
    mapping = TheoremDependencyMapper().step(inputs={"axiom_registry_result": registry, "axiom_minimality_result": minimality, "countermodel_generation_result": countermodels, "synthetic": True}, persist=False)
    return {
        "synthetic": True,
        "axiom_registry_result": registry,
        "axiom_independence_result": independence,
        "axiom_minimality_result": minimality,
        "model_generation_result": models,
        "countermodel_generation_result": countermodels,
        "theorem_dependency_mapping_result": mapping,
    }


def main() -> None:
    result = AxiomaticCompletenessCertifier().step(inputs=ready_inputs(), persist=False)
    assert result["axiomatic_completeness_status"] == "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED"
    assert result["minimal"] is True
    assert result["independent"] is True
    assert result["non_redundant"] is True
    assert result["axiomatically_complete"] is True
    assert result["ready_to_close_axis_AN"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AN7_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
