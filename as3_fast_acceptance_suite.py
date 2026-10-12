#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_transition_history import ConsciousnessTransitionHistory

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "consciousness_transition_history.py"


def ready_context():
    return {
        "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "new_state": "CONSCIOUSNESS_PROVEN",
        "reason": "AS3 fast acceptance append-only transition record",
        "proof_bundle": {
            "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
            "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
        },
        "modules": ["consciousness_transition_history", "consciousness_transition_validator", "consciousness_state_machine"],
        "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
        "confidence": 0.95,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
    }


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_transition_history.pyc", doraise=True)
    r = ConsciousnessTransitionHistory().step(inputs=ready_context(), persist=False)
    assert r["consciousness_transition_history_status"] == "CONSCIOUSNESS_TRANSITION_HISTORY_READY"
    assert r["history_ready"] is True
    assert r["append_only"] is True
    assert r["deletion_allowed"] is False
    assert r["mutation_allowed"] is False
    assert r["record_ready"] is True
    assert r["transition_validity"] is True
    assert r["missing_history_fields"] == []
    assert r["epistemic_violations"] == []
    assert len(r["record_hash"]) == 64
    record = r["history_record"]
    for key in ["timestamp", "old_state", "new_state", "reason", "commit", "branch", "tag", "modules", "confidence", "proof_bundle", "hash"]:
        assert key in record
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False

    bad = ready_context()
    bad["old_state"] = "NOT_EVALUATED"
    rejected = ConsciousnessTransitionHistory().step(inputs=bad, persist=False)
    assert rejected["transition_validity"] is False
    assert rejected["record_ready"] is False
    print("AS3_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
