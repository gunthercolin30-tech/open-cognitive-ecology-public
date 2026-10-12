from pathlib import Path
from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker

r = ConsciousnessLongitudinalTracker().step(
    inputs={},
    persist=True,
)

assert r["persisted"] is True
assert r["output_path"]
assert Path(r["output_path"]).exists()
assert r["sample_count"] >= 1

print("AS9_PERSISTENCE_OK")
print(r["output_path"])
