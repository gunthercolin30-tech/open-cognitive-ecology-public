#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_certificate_generator import ConsciousnessCertificateGenerator

ready_or_synthetic_context = {
    "state": "CONSCIOUSNESS_PROVEN",
    "version": "as5-final-lock",
    "proofs": {
        "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
        "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
    },
    "scores": {"readiness_score": 1.0, "confidence": 0.95},
    "event": {
        "event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED",
        "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "new_state": "CONSCIOUSNESS_PROVEN",
        "justification": "AS5 final lock certificate context",
        "proof_bundle": {},
        "modules": ["consciousness_certificate_generator", "consciousness_event_logger"],
        "event_hash": "final-lock-event-hash",
        "transition_hash": "final-lock-transition-hash",
    },
}

r = ConsciousnessCertificateGenerator().step(inputs=ready_or_synthetic_context, persist=False)

assert r["consciousness_certificate_generator_status"] == "CONSCIOUSNESS_CERTIFICATE_GENERATOR_READY"
assert r["certificate_generator_ready"] is True
assert r["certificate_ready"] is True
assert r["missing_certificate_fields"] == []
assert r["epistemic_violations"] == []
assert len(r["certificate_hash"]) == 64
assert len(r["certificate_signature"]) == 64
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert "pdf" in r["certificate_formats"]

print("AS5_FINAL_LOCK_OK")
