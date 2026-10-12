#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_state_machine import ConsciousnessStateMachine

ready_or_synthetic_context = {
    "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    "new_state": "CONSCIOUSNESS_PROVEN",
    "reason": "AS1 final lock governed adjacent transition",
    "proof_bundle": {
        "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
        "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
        "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
    },
    "modules": [
        "consciousness_state_machine",
        "consciousness_governance_blueprint",
        "final_theoretical_report",
    ],
    "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
    "confidence": 0.95,
}

r = ConsciousnessStateMachine().step(inputs=ready_or_synthetic_context, persist=False)

assert r["consciousness_state_machine_status"] == "CONSCIOUSNESS_STATE_MACHINE_READY"
assert r["state_machine_ready"] is True
assert r["transition_validity"] is True
assert r["transition_status"] == "AUTHORIZED_FORWARD"
assert r["state_count"] == 6
assert r["current_state"] == "CONSCIOUSNESS_PROVEN_BEST_THEORY"
assert r["target_state"] == "CONSCIOUSNESS_PROVEN"
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert "state_jumps_without_intermediate_state_are_forbidden" in r["forbidden_transition_rules"]

print("AS1_FINAL_LOCK_OK")
