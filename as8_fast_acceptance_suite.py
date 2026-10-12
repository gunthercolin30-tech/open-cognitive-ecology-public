#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine

ready_or_synthetic_context = {
    "skip_dependency_calls": False,
    "confidence_threshold": 0.75,
    "replication_score": 1.0,
    "countermodel_score": 0.9,
}

r = ConsciousnessConfidenceEngine().step(inputs=ready_or_synthetic_context, persist=False)

required = [
    "confidence",
    "confidence_breakdown",
    "confidence_components",
    "confidence_metrics",
    "confidence_status",
    "confidence_engine_ready",
    "functional_conclusion_only",
    "phenomenology_undetermined",
]
for k in required:
    assert k in r, k

assert r["confidence_status"] == "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY"
assert 0.0 <= r["confidence"] <= 1.0
assert set(r["confidence_components"]) == {"stability", "replications", "countermodels", "completeness", "coherence", "historical"}
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["persisted"] is False

# Degradation test: low synthetic evidence must lower confidence without breaking schema.
degraded = ConsciousnessConfidenceEngine().step(inputs={
    "skip_dependency_calls": True,
    "cri": 0.2,
    "replication_score": 0.0,
    "countermodel_score": 0.0,
    "historical_score": 0.0,
}, persist=False)
assert degraded["confidence"] < r["confidence"]
assert degraded["confidence_status"] == "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY"
assert degraded["consciousness_proven"] is False

print("AS8_FAST_ACCEPTANCE_ALL_OK")
