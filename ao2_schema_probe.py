from ontology.interpretation_rule_engine import InterpretationRuleEngine

r = InterpretationRuleEngine().step(persist=False)

print("AO2_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
