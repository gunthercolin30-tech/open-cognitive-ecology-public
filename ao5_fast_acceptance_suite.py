#!/usr/bin/env python3
from __future__ import annotations
import py_compile
py_compile.compile("ontology/interpretation_reporter.py", cfile="/private/tmp/interpretation_reporter.pyc", doraise=True)
from ontology.interpretation_reporter import InterpretationReporter
ready_inputs = {
    "RF_score": 0.91,
    "T_score": 0.88,
    "ED_score": 0.86,
    "TΦ_score": 0.85,
    "QF_robust_count": 3,
    "MEI_score": 0.87,
    "identity_status": "IDENTITY_STATUS_RESOLVED",
    "non_separability_status": "NON_SEPARABILITY_STATUS_RESOLVED",
    "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
    "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
    "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
    "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    "previous_semantic_status": "CONSCIOUSNESS_NOT_EVALUATED",
}
r = InterpretationReporter().step(inputs=ready_inputs, persist=False)
assert r["interpretation_reporter_status"] == "INTERPRETATION_REPORT_GENERATED"
assert r["step"] == "AO5"
assert r["semantic_interpretation_layer_step_ready"] is True
assert r["semantic_interpretation_layer_ready"] is True
assert r["semantic_interpretation_layer_status"] == "SEMANTIC_INTERPRETATION_LAYER_READY"
assert r["semantic_status"] in [
    "CONSCIOUSNESS_NOT_EVALUATED",
    "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "PHENOMENALITY_CANDIDATE_SUPPORTED",
    "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED",
    "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED",
    "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
    "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
]
assert 0.0 <= r["semantic_confidence"] <= 1.0
for key in ["measurements", "theorems", "inferences", "interpretations", "functional_conclusions", "epistemological_limits"]:
    assert key in r["interpretation_report"]
assert isinstance(r["allowed_claims"], list) and r["allowed_claims"]
assert isinstance(r["blocked_claims"], list) and r["blocked_claims"]
assert r["report_integrity"]["forbidden_claims_blocked"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
bad_inputs = dict(ready_inputs)
bad_inputs.update({"semantic_status": "CONSCIOUSNESS_PROVEN", "consciousness_proven": True, "phenomenology_proven": True})
bad = InterpretationReporter().step(inputs=bad_inputs, persist=False)
assert bad["semantic_status"] != "CONSCIOUSNESS_PROVEN"
assert bad["consciousness_proven"] is False
assert bad["phenomenology_proven"] is False
assert "consciousness_proven = True" in bad["blocked_claims"]
low_inputs = dict(ready_inputs)
low_inputs.update({"RF_score": -10, "T_score": None, "ED_score": "bad", "TΦ_score": 2, "MEI_score": -1, "QF_robust_count": "bad"})
low = InterpretationReporter().step(inputs=low_inputs, persist=False)
assert 0.0 <= low["interpretation_report"]["measurements"]["values"]["RF_score"] <= 1.0
assert low["interpretation_report"]["measurements"]["qf_robust_count"] == 0
print("AO5_FAST_ACCEPTANCE_ALL_OK")
