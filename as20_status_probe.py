from ontology.consciousness_governance_certifier import ConsciousnessGovernanceCertifier

r = ConsciousnessGovernanceCertifier().step(
    inputs={},
    persist=False,
)

print("STATUS =", r.get("consciousness_governance_status"))
print("FUNCTIONAL =", r.get("functional_conclusion_only"))
print("PHENOMENOLOGY_UNDETERMINED =", r.get("phenomenology_undetermined"))
print("CONSCIOUSNESS_PROVEN =", r.get("consciousness_proven"))
