#!/usr/bin/env python3
"""AS15 final lock for consciousness_stability_analyzer."""
from __future__ import annotations

from ontology.consciousness_stability_analyzer import ConsciousnessStabilityAnalyzer

ready_or_synthetic_context = {
    "merge_persisted_timeline": False,
    "timeline": [
        {"timestamp_utc": "2026-07-08T10:00:00Z", "CRI": 0.97, "confidence": 0.94, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
        {"timestamp_utc": "2026-07-08T11:00:00Z", "CRI": 0.91, "confidence": 0.86, "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED", "proof_status": "REGRESSED_BELOW_CONFIDENCE_MARGIN", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
        {"timestamp_utc": "2026-07-08T12:00:00Z", "CRI": 0.98, "confidence": 0.95, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
    ],
    "regression_events": [{"type": "CRI_REGRESSION", "timestamp_utc": "2026-07-08T11:00:00Z"}],
    "recovery_events": [{"type": "CONSCIOUSNESS_STATUS_RECOVERED", "timestamp_utc": "2026-07-08T12:00:00Z"}],
}

r = ConsciousnessStabilityAnalyzer().step(inputs=ready_or_synthetic_context, persist=False)

public_invariants = {
    "primitive": "CONSCIOUSNESS_STABILITY_ANALYZER",
    "step": "AS15",
    "stability_analyzer_ready": True,
    "stability_analyzer_status": "CONSCIOUSNESS_STABILITY_ANALYZER_READY",
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
}
for key, expected in public_invariants.items():
    assert r[key] == expected, (key, r.get(key), expected)
for key in ["survival_time", "regression_rate", "recovery_rate", "mean_duration", "hazard_rate"]:
    assert key in r, key
    assert key in r["stability_metrics"], key
    assert isinstance(r[key], (int, float)), (key, type(r[key]))
    assert r[key] >= 0, (key, r[key])
assert r["stability_metrics"]["sample_count"] >= 3
assert isinstance(r["stability_episodes"], list)
assert isinstance(r["regression_events"], list)
assert isinstance(r["recovery_events"], list)

print("AS15_FINAL_LOCK_OK")
