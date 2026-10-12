#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "axiom_registry.py"), cfile="/private/tmp/axiom_registry.pyc", doraise=True)
py_compile.compile(str(ROOT / "an1_final_lock.py"), cfile="/private/tmp/an1_final_lock.pyc", doraise=True)

from ontology.axiom_registry import AxiomRegistry

ready_inputs = {"synthetic": True, "extra_axioms": []}
r = AxiomRegistry().step(inputs=ready_inputs, persist=False)

assert r["primitive"] == "AXIOM_REGISTRY"
assert r["step"] == "AN1"
assert r["public_schema_version"] == "AN1.axiom_registry.v1"
assert r["axiom_registry_status"] == "AXIOM_REGISTRY_ESTABLISHED"
assert r["axiom_registry_established"] is True
assert r["axiomatic_completeness_status"] == "AN1_REGISTRY_READY"
assert r["axiom_count"] >= 10
assert r["canonical_axiom_count"] == 10
assert r["role_coverage_score"] >= 0.99
assert r["non_redundancy_score"] >= 0.99
assert r["traceability_score"] >= 0.99
assert r["registry_completeness_score"] >= 0.99
assert r["ready_for_AN2_independence_testing"] is True
assert len(r["axiom_ids"]) == len(set(r["axiom_ids"]))
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AN1_FAST_ACCEPTANCE_OK")
