#!/usr/bin/env python3
"""AS7 final lock — Codex-compliant, no inline Python required."""
from __future__ import annotations

from ontology.consciousness_readiness_index import ConsciousnessReadinessIndex

READY_CONTEXT = {
    "synthetic_readiness_context": "ready",
    "axis_scores": {
        "AA": 1.0, "AB": 1.0, "AC": 1.0, "AD": 1.0, "AE": 1.0, "AF": 1.0,
        "AG": 1.0, "AH": 1.0, "AI": 1.0, "AJ": 1.0, "AK": 1.0, "AM": 1.0,
        "AP": 1.0, "AQ": 1.0, "AR": 1.0, "AN": 1.0, "AO": 1.0, "AL": 1.0,
        "AS0": 1.0, "AS1": 1.0, "AS2": 1.0, "AS3": 1.0, "AS4": 1.0, "AS5": 1.0, "AS6": 1.0,
    },
}

r = ConsciousnessReadinessIndex().step(inputs=READY_CONTEXT, persist=False)

assert r["readiness_index_status"] == "CONSCIOUSNESS_READINESS_INDEX_READY"
assert r["cri_ready"] is True
assert 0.0 <= r["cri"] <= 1.0
assert r["cri"] >= 0.95
assert r["readiness_level"] == "CONSCIOUSNESS_READINESS_CRITICAL_COMPLETE"
assert r["consciousness_proven_consequence"] is True
assert r["revocation_required"] is False
assert all(r["critical_axis_status"].values())
assert r["missing_fields"] == []

assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS7_FINAL_LOCK_OK")
