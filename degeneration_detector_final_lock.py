#!/usr/bin/env python3
from ontology.degeneration_detector import DegenerationDetector


def obs(day, value):
    return {
        "timestamp_utc": f"2027-03-{day:02d}T00:00:00Z",
        "state_vector": {k: value for k in ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]},
        "data_quality": 0.99,
        "synthetic": True,
    }

READY_OR_SYNTHETIC_CONTEXT = {"observations": [obs(1, .90), obs(2, .88), obs(3, .70), obs(4, .58), obs(5, .44)]}
result = DegenerationDetector().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
assert result["primitive"] == "DEGENERATION_DETECTOR"
assert result["step"] == "AV5"
assert result["public_schema_version"] == "1.0"
assert isinstance(result["degeneration_score"], float)
assert isinstance(result["closure_pressure"], float)
assert result["degeneration_hash"]
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("AV5_FINAL_LOCK_OK")
