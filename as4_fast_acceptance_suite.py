#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_event_logger import ConsciousnessEventLogger

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "consciousness_event_logger.py"


def ready_context():
    return {
        "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "new_state": "CONSCIOUSNESS_PROVEN",
        "reason": "AS4 fast acceptance threshold-crossing governed event",
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


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_event_logger.pyc", doraise=True)
    r = ConsciousnessEventLogger().step(inputs=ready_context(), persist=False)
    assert r["consciousness_event_logger_status"] == "CONSCIOUSNESS_EVENT_LOGGER_READY"
    assert r["event_logger_ready"] is True
    assert r["event_type"] == "CONSCIOUSNESS_THRESHOLD_CROSSED"
    assert r["event_ready"] is True
    assert r["transition_validity"] is True
    assert r["history_record_ready"] is True
    assert r["append_only"] is True
    assert r["deletion_allowed"] is False
    assert r["mutation_allowed"] is False
    assert r["missing_event_fields"] == []
    assert r["epistemic_violations"] == []
    assert len(r["event_hash"]) == 64
    assert r["event"]["missing_event_fields"] == []
    assert len(r["event"]["event_hash"]) == 64
    for event_type in [
        "CONSCIOUSNESS_THRESHOLD_CROSSED",
        "CONSCIOUSNESS_STATUS_REVOKED",
        "CONSCIOUSNESS_STATUS_RECOVERED",
        "CONSCIOUSNESS_STATUS_RECONFIRMED",
    ]:
        assert event_type in r["supported_event_types"]
    event = r["event"]
    for key in ["event_type", "timestamp", "justification", "old_state", "new_state", "transition_hash", "event_hash", "modules", "proof_bundle", "git_version"]:
        assert key in event
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False

    bad = ready_context()
    bad["old_state"] = "NOT_EVALUATED"
    rejected = ConsciousnessEventLogger().step(inputs=bad, persist=False)
    assert rejected["event_ready"] is False
    assert rejected["transition_validity"] is False
    print("AS4_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
