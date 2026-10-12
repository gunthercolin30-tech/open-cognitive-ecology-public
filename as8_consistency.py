from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine

r = ConsciousnessConfidenceEngine().step(
    inputs={},
    persist=False,
)

assert isinstance(r["confidence_components"], dict)
assert isinstance(r["confidence_breakdown"], dict)
assert isinstance(r["confidence_metrics"], dict)

print("AS8_CONSISTENCY_OK")
