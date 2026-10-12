#!/usr/bin/env python3
from __future__ import annotations

import py_compile

py_compile.compile(
    "ontology/first_failure_locator.py",
    cfile="/private/tmp/first_failure_locator.pyc",
    doraise=True,
)

from ontology.first_failure_locator import FirstFailureLocator

READY_INPUTS = {
    "synthetic": True,
    "source": "AL2_FAST_ACCEPTANCE",
    "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
    "phenomenality_candidate_status": "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED",
    "absolute_quality_identity_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
}

r = FirstFailureLocator().step(inputs=READY_INPUTS, persist=False)
assert r["primitive"] == "FIRST_FAILURE_LOCATOR"
assert r["step"] == "AL2"
assert r["first_failure_locator_status"] == "NO_FAILURE_LOCATED"
assert r["first_failure_found"] is False
assert r["first_failure"] is None
assert r["first_failure_key"] is None
assert r["ready_for_AL3_phenomenality_candidate_certifier"] is True
assert isinstance(r["evaluations"], list) and len(r["evaluations"]) >= 10
assert all(row["passed"] is True for row in r["evaluations"])
assert 0.0 <= r["metrics"]["diagnostic_readiness_score"] <= 1.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

bad = dict(READY_INPUTS)
bad["semantic_interpretation_layer_status"] = "BROKEN"
d = FirstFailureLocator().step(inputs=bad, persist=False)
assert d["first_failure_locator_status"] == "FIRST_FAILURE_LOCATED"
assert d["first_failure_found"] is True
assert d["first_failure_key"] == "semantic_interpretation_layer_status"
assert d["first_failure_axis"] == "AO"
assert d["ready_for_AL3_phenomenality_candidate_certifier"] is False
assert d["consciousness_proven"] is False
assert d["phenomenology_proven"] is False

bad2 = dict(READY_INPUTS)
bad2["consciousness_proven"] = True
g = FirstFailureLocator().step(inputs=bad2, persist=False)
assert g["first_failure_found"] is True
assert g["first_failure_key"] == "consciousness_proven"
assert g["first_failure_type"] == "epistemic_guard_violation"

print("AL2_FAST_ACCEPTANCE_ALL_OK")
