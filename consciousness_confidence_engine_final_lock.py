#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_confidence_engine import ConsciousnessConfidenceEngine

ready_or_synthetic_context = {
    "confidence_threshold": 0.75,
    "dependency_outputs": {
        "readiness": {
            "cri": 1.0,
            "continuous_readiness_index": 1.0,
            "critical_completeness": 1.0,
            "theoretical_completeness": 1.0,
            "governance_completeness": 1.0,
            "critical_axis_status": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
            "readiness_index_status": "CONSCIOUSNESS_READINESS_INDEX_READY",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        },
        "transition_history": {
            "history_ready": True,
            "append_only": True,
            "history_count_after": 1,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        },
        "event_logger": {
            "event_logger_ready": True,
            "event_count_after": 1,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        },
        "revocation": {"revocation_required": False, "revoked": False},
        "certificate": {"certificate_ready": True},
        "state_machine": {"state_machine_ready": True},
        "axiomatic_completeness": {"completeness_score": 1.0, "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED"},
        "semantic_revision": {"semantic_interpretation_layer_step_ready": True},
        "final_dashboard": {"dashboard_ready": True},
        "final_theoretical_report": {"report_ready": True, "final_axis_status": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"},
    },
    "replication_score": 1.0,
    "countermodel_score": 1.0,
    "historical_score": 1.0,
    "skip_dependency_calls": True,
}

r = ConsciousnessConfidenceEngine().step(inputs=ready_or_synthetic_context, persist=False)

assert r["confidence_status"] == "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY"
assert r["confidence_engine_ready"] is True
assert r["confidence_ready"] is True
assert 0.0 <= r["confidence"] <= 1.0
assert r["confidence"] >= 0.75
assert isinstance(r["confidence_breakdown"], dict)
assert isinstance(r["confidence_components"], dict)
assert isinstance(r["confidence_metrics"], dict)
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["persisted"] is False

print("AS8_FINAL_LOCK_OK")
