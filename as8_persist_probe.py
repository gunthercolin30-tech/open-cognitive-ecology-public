from pathlib import Path
from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine

r = ConsciousnessConfidenceEngine().step(
    inputs={},
    persist=True,
)

assert r["persisted"] is True
assert r["output_path"]
assert Path(r["output_path"]).exists()

print("AS8_PERSISTENCE_OK")
print(r["output_path"])
