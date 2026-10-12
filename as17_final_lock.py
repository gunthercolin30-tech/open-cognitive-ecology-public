#!/usr/bin/env python3
"""AS17 final lock — public invariants only."""
from __future__ import annotations

from ontology.consciousness_dependency_visualizer import ConsciousnessDependencyVisualizer

ready_or_synthetic_context = {
    "status_payloads": {
        "consciousness_readiness_index": [{"status": "CONSCIOUSNESS_READINESS_INDEX_READY", "readiness_index": 0.91}],
        "consciousness_confidence_engine": [{"status": "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY", "confidence": 0.88}],
        "consciousness_stability_analyzer": [{"status": "CONSCIOUSNESS_STABILITY_ANALYZER_READY", "stability_score": 0.86}],
        "consciousness_explanation_engine": [{"status": "CONSCIOUSNESS_EXPLANATION_ENGINE_READY", "explanation_confidence": 0.85}],
    }
}

r = ConsciousnessDependencyVisualizer().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_DEPENDENCY_VISUALIZER"
assert r["step"] == "AS17"
assert r["dependency_visualizer_status"] == "CONSCIOUSNESS_DEPENDENCY_VISUALIZER_READY"
assert r["node_count"] >= 18
assert r["edge_count"] >= 17
assert isinstance(r["graph_hash"], str) and len(r["graph_hash"]) == 64
assert isinstance(r["dot"], str) and "digraph" in r["dot"]
assert isinstance(r["mermaid"], str) and "flowchart" in r["mermaid"]
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

print("AS17_FINAL_LOCK_OK")
