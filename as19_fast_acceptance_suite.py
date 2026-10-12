#!/usr/bin/env python3
from __future__ import annotations
import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(str(ROOT / "ontology" / "consciousness_public_dashboard.py"), cfile="/private/tmp/as19_module.pyc", doraise=True)

from ontology.consciousness_public_dashboard import ConsciousnessPublicDashboard

ctx = {
    "prediction": {"probability_reach_status": 0.62, "probability_lose_status": 0.08, "current_state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED"},
    "stability": {"stability_index": 0.91, "timeline_length": 120},
    "dependency_graph": {"node_count": 20, "edge_count": 32, "green_nodes": 17, "orange_nodes": 3, "red_nodes": 0},
    "certificate": {"certificate_count": 1},
}
r = ConsciousnessPublicDashboard().step(inputs=ctx, persist=False)
assert r["primitive"] == "CONSCIOUSNESS_PUBLIC_DASHBOARD"
assert r["step"] == "AS19"
assert r["public_dashboard_status"] == "CONSCIOUSNESS_PUBLIC_DASHBOARD_READY"
assert r["dashboard_sanitized"] is True
assert r["sensitive_data_excluded"] is True
assert r["history_available"] is True
assert r["certificates_available"] is True
assert r["graphs_available"] is True
assert r["public_metrics"]["probability_reach_status"] == 0.62
assert r["public_metrics"]["red_nodes"] == 0
for flag in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
    assert r[flag] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert isinstance(r["dashboard_hash"], str) and len(r["dashboard_hash"]) == 64
r2 = ConsciousnessPublicDashboard().step(inputs={"token": "secret", "user_email": "x@example.org", "prediction": {"probability_reach_status": 0.5}}, persist=False)
assert "token" not in r2["public_sources_used"]
assert all("email" not in key.lower() for key in r2["public_sources_used"])
print("AS19_FAST_ACCEPTANCE_ALL_OK")
