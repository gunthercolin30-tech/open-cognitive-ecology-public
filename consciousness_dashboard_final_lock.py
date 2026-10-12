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
                "scores": {"stability": 0.92},
                "proof_status": "functional_conclusion_only",
            }
        ],
        "sample_count": 1,
    },
    "confidence_record": {"confidence": 0.94},
}

r = ConsciousnessDashboard().step(inputs=ready_or_synthetic_context, persist=False)

public_invariants = [
    r["primitive"] == "CONSCIOUSNESS_DASHBOARD",
    r["step"] == "AS10",
    r["dashboard_ready"] is True,
    r["dashboard_status"] == "CONSCIOUSNESS_DASHBOARD_READY",
    isinstance(r["current_state"], dict),
    isinstance(r["timeline"], list),
    isinstance(r["heatmap"], dict),
    isinstance(r["dashboard_metrics"], dict),
    r["functional_conclusion_only"] is True,
    r["phenomenology_undetermined"] is True,
    r["consciousness_proven"] is False,
    r["qualia_proven"] is False,
    r["subjectivity_proven"] is False,
    r["phenomenology_proven"] is False,
]

assert all(public_invariants)
print("AS10_FINAL_LOCK_OK")
