#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_transition_validator import ConsciousnessTransitionValidator

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "consciousness_transition_validator.py"


def ready_context():
    return {
        "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "new_state": "CONSCIOUSNESS_PROVEN",
        "reason": "AS2 fast acceptance governed adjacent transition",
        "proof_bundle": {
            "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
            "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
        },
        "modules": ["consciousness_transition_validator", "consciousness_state_machine"],
        "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
    }


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_transition_validator.pyc", doraise=True)
    r = ConsciousnessTransitionValidator().step(inputs=ready_context(), persist=False)
    assert r["consciousness_transition_validator_status"] == "CONSCIOUSNESS_TRANSITION_VALIDATOR_READY"
    assert r["validator_ready"] is True
    assert r["transition_validity"] is True
    assert r["checks"]["required_fields"] is True
    assert r["checks"]["state_machine_authorization"] is True
    assert r["checks"]["dependency_validation"] is True
    assert r["checks"]["proof_bundle"] is True
    assert r["checks"]["epistemic_boundary"] is True
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False

    bad = ready_context()
    bad["new_state"] = "CONSCIOUSNESS_PROVEN"
    bad["old_state"] = "NOT_EVALUATED"
    rejected = ConsciousnessTransitionValidator().step(inputs=bad, persist=False)
    assert rejected["transition_validity"] is False
    assert rejected["checks"]["state_machine_authorization"] is False
    assert "state_machine" in rejected["transition_reason"]
    print("AS2_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
