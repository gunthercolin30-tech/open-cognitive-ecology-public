#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_state_machine import ConsciousnessStateMachine

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "consciousness_state_machine.py"


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_state_machine.pyc", doraise=True)
    ctx = {
        "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "new_state": "CONSCIOUSNESS_PROVEN",
        "reason": "fast acceptance governed adjacent transition",
        "proof_bundle": {"AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"},
        "modules": ["final_theoretical_report", "consciousness_governance_blueprint"],
        "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
    }
    r = ConsciousnessStateMachine().step(inputs=ctx, persist=False)
    assert r["consciousness_state_machine_status"] == "CONSCIOUSNESS_STATE_MACHINE_READY"
    assert r["state_machine_ready"] is True
    assert r["transition_validity"] is True
    assert r["transition_status"] == "AUTHORIZED_FORWARD"
    assert r["state_count"] == 6
    assert r["allowed_transition_count"] == 10
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False

    jump = ConsciousnessStateMachine().step(inputs={
        "old_state": "NOT_EVALUATED",
        "new_state": "CONSCIOUSNESS_PROVEN",
        "reason": "forbidden jump probe",
        "proof_bundle": {"probe": True},
        "modules": ["probe"],
        "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
    }, persist=False)
    assert jump["transition_validity"] is False
    assert jump["transition_status"] == "FORBIDDEN_JUMP"
    print("AS1_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
