#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_event_logger import ConsciousnessEventLogger

ready_or_synthetic_context = {
    "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "new_state": "CONSCIOUSNESS_PROVEN",
    "reason": "AS4 final lock threshold-crossing governed event",
    "proof_bundle": {
        "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
        "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
    },
    "modules": [
        "consciousness_event_logger",
        "consciousness_transition_history",
        "consciousness_transition_validator",
        "consciousness_state_machine",
        "consciousness_governance_blueprint",
    ],
    "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
    "confidence": 0.95,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
}

r = ConsciousnessEventLogger().step(inputs=ready_or_synthetic_context, persist=False)

assert r["consciousness_event_logger_status"] == "CONSCIOUSNESS_EVENT_LOGGER_READY"
assert r["event_logger_ready"] is True
assert r["event_type"] == "CONSCIOUSNESS_THRESHOLD_CROSSED"
assert r["event_ready"] is True
assert r["transition_validity"] is True
assert r["history_record_ready"] is True
assert r["missing_event_fields"] == []
assert r["epistemic_violations"] == []
assert len(r["event_hash"]) == 64
assert r["event"]["missing_event_fields"] == []
assert len(r["event"]["event_hash"]) == 64
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS4_FINAL_LOCK_OK")
