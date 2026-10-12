from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine

r = ConsciousnessConfidenceEngine().step(
    inputs={},
    persist=False,
)

assert 0.0 <= r["confidence"] <= 1.0

print("AS8_CONFIDENCE_BOUNDS_OK")
