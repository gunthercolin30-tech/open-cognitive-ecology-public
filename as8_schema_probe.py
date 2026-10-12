from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine

r = ConsciousnessConfidenceEngine().step(
    inputs={},
    persist=False,
)

print(sorted(r.keys()))
