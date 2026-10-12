from ontology.interpretation_rule_engine import InterpretationRuleEngine

r = InterpretationRuleEngine().step(persist=False)

assert r["interpretation_rule_engine_status"] == "INTERPRETATION_RULES_ESTABLISHED"
assert r["step"] == "AO2"

joined = "\n".join(r.keys()).lower()

for semantic in ["status", "rule", "interpret"]:
    assert semantic in joined, semantic

assert "CONSCIOUSNESS" in str(r)

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AO2_SCHEMA_INTEGRITY_OK")
