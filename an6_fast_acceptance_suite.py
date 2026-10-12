#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

for path, cfile in [
    (ROOT / "ontology" / "theorem_dependency_mapper.py", "/private/tmp/theorem_dependency_mapper.pyc"),
    (ROOT / "an6_fast_acceptance_suite.py", "/private/tmp/an6_fast_acceptance_suite.pyc"),
    (ROOT / "an6_final_lock.py", "/private/tmp/an6_final_lock.pyc"),
]:
    py_compile.compile(str(path), cfile=cfile, doraise=True)

from ontology.axiom_registry import AxiomRegistry
from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
from ontology.countermodel_generator import CountermodelGenerator
from ontology.theorem_dependency_mapper import TheoremDependencyMapper

registry = AxiomRegistry().step(inputs={"synthetic": True, "source": "AN6_FAST"}, persist=False)
minimality = AxiomMinimalityAnalyzer().step(inputs={"axiom_registry_result": registry, "synthetic": True}, persist=False)
countermodels = CountermodelGenerator().step(inputs={"axiom_registry_result": registry, "axiom_minimality_result": minimality, "synthetic": True}, persist=False)
result = TheoremDependencyMapper().step(
    inputs={
        "synthetic": True,
        "axiom_registry_result": registry,
        "axiom_minimality_result": minimality,
        "countermodel_generation_result": countermodels,
    },
    persist=False,
)

assert result["primitive"] == "THEOREM_DEPENDENCY_MAPPER"
assert result["step"] == "AN6"
assert result["public_schema_version"].startswith("AN6.")
assert result["theorem_dependency_mapping_status"] == "THEOREM_DEPENDENCIES_MAPPED"
assert result["dependencies_mapped"] is True
assert result["theorem_dependency_graph"]["node_count"] >= 1
assert result["theorem_dependency_graph"]["edge_count"] >= 1
assert isinstance(result["axiom_usage"], dict)
assert isinstance(result["minimal_proof_dependencies"], dict)
assert isinstance(result["redundant_proof_paths"], list)
assert result["dependency_metrics"]["theorem_dependency_coverage"] >= 0.95
assert result["dependency_metrics"]["minimal_usage_coverage"] >= 0.95
assert result["dependency_metrics"]["functional_dependency_mapping_readiness_score"] >= 0.80
assert result["ready_for_AN7_axiomatic_completeness_certification"] is True
assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_undetermined"] is True
assert result["functional_conclusion_only"] is True

print("AN6_FAST_ACCEPTANCE_ALL_OK")
