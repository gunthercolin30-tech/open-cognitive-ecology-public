#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from ontology.consciousness_dashboard import ConsciousnessDashboard

ready_or_synthetic_context = {
    "timeline_record": {
        "timeline": [
            {
                "timestamp_utc": "2026-07-08T00:00:00Z",
                "date": "2026-07-08T00:00:00Z",
                "CRI": 0.93,
                "confidence": 0.94,
                "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
                "proof_status": "functional_conclusion_only",
            }
        ],
        "sample_count": 1,
    },
    "confidence_record": {"confidence": 0.94},
}

r = ConsciousnessDashboard().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_DASHBOARD"
assert r["step"] == "AS10"
assert r["dashboard_ready"] is True
assert r["consciousness_dashboard_ready"] is True
assert r["dashboard_status"] == "CONSCIOUSNESS_DASHBOARD_READY"
assert 0.0 <= r["CRI"] <= 1.0
assert 0.0 <= r["confidence"] <= 1.0
assert isinstance(r["timeline"], list)
assert isinstance(r["heatmap"], dict)
assert isinstance(r["dashboard_metrics"], dict)
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS10_FAST_ACCEPTANCE_ALL_OK")
