#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

py_compile.compile(
    str(ROOT / "ontology" / "countermodel_generator.py"),
    cfile="/private/tmp/countermodel_generator.pyc",
    doraise=True,
)
py_compile.compile(
    str(ROOT / "an5_fast_acceptance_suite.py"),
    cfile="/private/tmp/an5_fast_acceptance_suite.pyc",
    doraise=True,
)
py_compile.compile(
    str(ROOT / "an5_final_lock.py"),
    cfile="/private/tmp/an5_final_lock.pyc",
    doraise=True,
)

from ontology.axiom_registry import AxiomRegistry
from ontology.axiom_independence_tester import AxiomIndependenceTester
from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
from ontology.model_generator import ModelGenerator
from ontology.countermodel_generator import CountermodelGenerator

registry = AxiomRegistry().step(inputs={"synthetic": True, "source": "AN5_FAST"}, persist=False)
independence = AxiomIndependenceTester().step(inputs={"axiom_registry_result": registry, "synthetic": True}, persist=False)
minimality = AxiomMinimalityAnalyzer().step(inputs={"axiom_registry_result": registry, "axiom_independence_result": independence, "synthetic": True}, persist=False)
models = ModelGenerator().step(inputs={"axiom_registry_result": registry, "axiom_minimality_result": minimality, "synthetic": True}, persist=False)
result = CountermodelGenerator().step(
    inputs={
        "synthetic": True,
        "axiom_registry_result": registry,
        "axiom_independence_result": independence,
        "axiom_minimality_result": minimality,
        "model_generation_result": models,
    },
    persist=False,
)

assert result["primitive"] == "COUNTERMODEL_GENERATOR"
assert result["step"] == "AN5"
assert result["public_schema_version"].startswith("AN5.")
assert result["countermodel_generation_status"] == "COUNTERMODELS_GENERATED"
assert result["countermodels_generated"] is True
assert result["countermodel_count"] >= result["minimal_axiom_count"] >= 1
assert result["countermodel_metrics"]["countermodel_coverage_ratio"] >= 0.95
assert result["countermodel_metrics"]["functional_countermodel_readiness_score"] >= 0.80
assert result["ready_for_AN6_theorem_dependency_mapping"] is True
assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_undetermined"] is True
assert result["functional_conclusion_only"] is True

print("AN5_FAST_ACCEPTANCE_ALL_OK")
