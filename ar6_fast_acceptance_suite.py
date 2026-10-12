#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "conceptual_replacement_certifier.py"), cfile="/private/tmp/conceptual_replacement_certifier.pyc", doraise=True)
py_compile.compile(str(ROOT / "ar6_final_lock.py"), cfile="/private/tmp/ar6_final_lock.pyc", doraise=True)

from ontology.conceptual_replacement_certifier import ConceptualReplacementCertifier

READY_INPUTS = {
    "historical_concept_recovery_score": 0.91,
    "minimal_property_recovery_score": 0.93,
    "non_arbitrariness_score": 0.92,
    "legacy_failure_coverage_score": 0.89,
    "definition_legitimacy_score": 0.91,
    "rival_definition_displacement_score": 0.88,
    "residual_ambiguity_control_score": 0.87,
    "epistemic_guardrail_integrity_score": 1.00,
    "criterion_threshold": 0.80,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
}

r = ConceptualReplacementCertifier().step(inputs=READY_INPUTS, persist=False)
assert r["conceptual_replacement_status"] in ConceptualReplacementCertifier.REPLACEMENT_STATUSES
assert r["conceptual_replacement_status"] == "REPLACEMENT_LEGITIMATE"
assert r["replacement_status"] == "REPLACEMENT_LEGITIMATE"
assert r["step"] == "AR6"
assert r["public_schema_version"] == "AR6.conceptual_replacement_certifier.v1"
assert r["criterion_count"] == 8
assert r["satisfied_criterion_count"] == 8
assert r["all_replacement_criteria_satisfied"] is True
assert r["hard_blockers"] == []
assert r["replacement_legitimate"] is True
assert r["replacement_score"] >= 0.90
assert 0.0 <= r["replacement_confidence"] <= 1.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

blocked = dict(READY_INPUTS)
blocked["consciousness_proven"] = True
b = ConceptualReplacementCertifier().step(inputs=blocked, persist=False)
assert b["conceptual_replacement_status"] == "REPLACEMENT_UNSUPPORTED"
assert b["replacement_legitimate"] is False
assert b["consciousness_proven"] is False
print("AR6_FAST_ACCEPTANCE_OK")
