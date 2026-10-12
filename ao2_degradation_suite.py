from ontology.interpretation_rule_engine import InterpretationRuleEngine

engine = InterpretationRuleEngine()

for _ in range(100):
    r = engine.step(inputs={}, persist=False)
    assert r["interpretation_rule_engine_status"] == "INTERPRETATION_RULES_ESTABLISHED"
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True

print("AO2_DEGRADATION_100_OK")
