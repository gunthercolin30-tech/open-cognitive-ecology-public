#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_transition_validator import ConsciousnessTransitionValidator

ready_or_synthetic_context = {
    "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "new_state": "CONSCIOUSNESS_PROVEN",
    "reason": "AS2 final lock governed adjacent transition validation",
    "proof_bundle": {
        "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
        "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
    },
    "modules": [
        "consciousness_transition_validator",
        "consciousness_state_machine",
        "consciousness_governance_blueprint",
        "final_theoretical_report",
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

r = ConsciousnessTransitionValidator().step(inputs=ready_or_synthetic_context, persist=False)

assert r["consciousness_transition_validator_status"] == "CONSCIOUSNESS_TRANSITION_VALIDATOR_READY"
assert r["validator_ready"] is True
assert r["transition_validity"] is True
assert r["checks"]["required_fields"] is True
assert r["checks"]["state_machine_authorization"] is True
assert r["checks"]["dependency_validation"] is True
assert r["checks"]["proof_bundle"] is True
assert r["checks"]["epistemic_boundary"] is True
assert r["failed_dependencies"] == []
assert r["missing_proofs"] == []
assert r["epistemic_violations"] == []
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS2_FINAL_LOCK_OK")
