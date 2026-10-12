
#!/usr/bin/env python3
from __future__ import annotations
import py_compile

py_compile.compile("ontology/interpretation_rule_engine.py", cfile="/private/tmp/interpretation_rule_engine.pyc", doraise=True)

from ontology.interpretation_rule_engine import InterpretationRuleEngine

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
}

r = InterpretationRuleEngine().step(inputs=ready_inputs, persist=False)
assert r["interpretation_rule_engine_status"] == "INTERPRETATION_RULES_ESTABLISHED"
assert r["step"] == "AO2"
assert r["semantic_interpretation_layer_step_ready"] is True
assert r["semantic_status"] == "CONSCIOUSNESS_PROVEN_BEST_THEORY"
assert r["absolute_consciousness_status"] == "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"
assert "CONSCIOUSNESS_PROVEN" in r["blocked_statuses"]
assert r["condition_flags"]["best_theory_supported"] is True
assert 0.0 <= r["semantic_confidence"] <= 1.0
assert r["rule_count"] >= 7
assert r["separation_enforced"]["absolute_claims_guarded"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AO2_FAST_ACCEPTANCE_ALL_OK")
