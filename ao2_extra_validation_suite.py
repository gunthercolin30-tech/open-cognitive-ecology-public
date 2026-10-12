from ontology.interpretation_rule_engine import InterpretationRuleEngine

r = InterpretationRuleEngine().step(persist=False)

assert r["interpretation_rule_engine_status"] == "INTERPRETATION_RULES_ESTABLISHED"
assert r["step"] == "AO2"

assert "selected_status" in r
assert "rule_trace" in r
assert "authorized_statuses" in r

assert r["selected_status"] in r["authorized_statuses"]
assert isinstance(r["rule_trace"], list)
assert len(r["rule_trace"]) >= 1

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AO2_EXTRA_VALIDATION_SUITE_OK")
