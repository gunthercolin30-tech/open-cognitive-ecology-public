from ontology.consciousness_governance_certifier import ConsciousnessGovernanceCertifier

r = ConsciousnessGovernanceCertifier().step(inputs={}, persist=False)

print("AS20_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
