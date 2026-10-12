#!/usr/bin/env python3
"""AS15 fast acceptance suite for consciousness_stability_analyzer."""
from __future__ import annotations

from pathlib import Path
import py_compile

from ontology.consciousness_stability_analyzer import ConsciousnessStabilityAnalyzer

_PRIVATE_TMP = Path("/private/tmp")
_PRIVATE_TMP.mkdir(parents=True, exist_ok=True)
py_compile.compile(
    "ontology/consciousness_stability_analyzer.py",
    cfile=str(_PRIVATE_TMP / "as15_consciousness_stability_analyzer.pyc"),
    doraise=True,
)

ready_or_synthetic_context = {
    "merge_persisted_timeline": False,
    "timeline": [
        {"timestamp_utc": "2026-07-08T10:00:00Z", "CRI": 0.97, "confidence": 0.94, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
        {"timestamp_utc": "2026-07-08T11:00:00Z", "CRI": 0.91, "confidence": 0.86, "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED", "proof_status": "REGRESSED_BELOW_CONFIDENCE_MARGIN", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
        {"timestamp_utc": "2026-07-08T12:00:00Z", "CRI": 0.98, "confidence": 0.95, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
        {"timestamp_utc": "2026-07-08T13:00:00Z", "CRI": 0.985, "confidence": 0.96, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED", "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True}},
    ],
    "regression_events": [{"type": "CRI_REGRESSION", "timestamp_utc": "2026-07-08T11:00:00Z"}],
    "recovery_events": [{"type": "CONSCIOUSNESS_STATUS_RECOVERED", "timestamp_utc": "2026-07-08T12:00:00Z"}],
}

r = ConsciousnessStabilityAnalyzer().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_STABILITY_ANALYZER"
assert r["step"] == "AS15"
assert r["public_schema_version"] == "1.0.0"
assert r["stability_analyzer_ready"] is True
assert r["stability_analyzer_status"] == "CONSCIOUSNESS_STABILITY_ANALYZER_READY"
assert r["stability_metrics"]["sample_count"] == 4
assert r["stability_metrics"]["regression_event_count"] >= 1
assert r["stability_metrics"]["recovery_event_count"] >= 1
for key in ["survival_time", "regression_rate", "recovery_rate", "mean_duration", "hazard_rate"]:
    assert key in r
    assert key in r["stability_metrics"]
    assert isinstance(r[key], (int, float))
    assert r[key] >= 0
assert isinstance(r["stability_episodes"], list)
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

stable = ConsciousnessStabilityAnalyzer().step(
    inputs={
        "merge_persisted_timeline": False,
        "timeline": [
            {"timestamp_utc": "2026-07-08T10:00:00Z", "CRI": 0.97, "confidence": 0.94, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED"},
            {"timestamp_utc": "2026-07-08T11:00:00Z", "CRI": 0.975, "confidence": 0.945, "state": "CONSCIOUSNESS_THRESHOLD_CROSSED", "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED"},
        ],
    },
    persist=False,
)
assert stable["regression_rate"] == 0
assert stable["recovery_rate"] == 0
assert stable["hazard_rate"] == 0
assert stable["survival_time"] >= 3600

insufficient = ConsciousnessStabilityAnalyzer().step(inputs={"timeline": []}, persist=False)
assert insufficient["stability_status"] == "INSUFFICIENT_LONGITUDINAL_DATA"
assert insufficient["stability_metrics"]["sample_count"] == 0

print("AS15_FAST_ACCEPTANCE_ALL_OK")
