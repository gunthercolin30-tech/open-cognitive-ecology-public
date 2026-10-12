#!/usr/bin/env python3
from __future__ import annotations
from ontology.consciousness_public_dashboard import ConsciousnessPublicDashboard

ready_or_synthetic_context = {
    "prediction": {"probability_reach_status": 0.77, "probability_lose_status": 0.12, "current_state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED"},
    "stability": {"stability_index": 0.89, "timeline_length": 64},
    "confidence": {"confidence": 0.84, "cri": 0.83},
    "dependency_graph": {"node_count": 21, "edge_count": 31, "green_nodes": 16, "orange_nodes": 5, "red_nodes": 0},
    "certificate": {"certificate_count": 1},
}
r = ConsciousnessPublicDashboard().step(inputs=ready_or_synthetic_context, persist=False)
assert r["primitive"] == "CONSCIOUSNESS_PUBLIC_DASHBOARD" and r["step"] == "AS19"
assert r["public_dashboard_status"] == "CONSCIOUSNESS_PUBLIC_DASHBOARD_READY"
assert r["dashboard_sanitized"] is True and r["sensitive_data_excluded"] is True
assert r["history_available"] is True and r["graphs_available"] is True
assert isinstance(r["dashboard_hash"], str) and len(r["dashboard_hash"]) == 64
assert r["consciousness_proven"] is False and r["qualia_proven"] is False
assert r["subjectivity_proven"] is False and r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True and r["functional_conclusion_only"] is True
print("AS19_FINAL_LOCK_OK")
