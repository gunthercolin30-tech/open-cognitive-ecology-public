#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_governance_blueprint import ConsciousnessGovernanceBlueprint


def ready_inputs() -> dict:
    return {
        "synthetic_certification_context": "ready",
        "final_consciousness_certification_status": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
        "functional_status": "FUNCTIONAL_CERTIFICATION_COMPLETE_UNDER_EPISTEMIC_GUARDS",
        "scientific_status": "THEORETICAL_FUNCTIONAL_CERTIFICATION_READY_FOR_EMPIRICAL_VALIDATION",
        "current_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
    }


def main() -> None:
    r = ConsciousnessGovernanceBlueprint().step(inputs=ready_inputs(), persist=False)
    assert r["consciousness_governance_blueprint_status"] == "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT_READY"
    assert r["governance_axis_status"] == "AS_GOVERNANCE_INITIALIZED"
    assert r["blueprint_ready"] is True
    assert r["missing_sections"] == []
    assert r["metrics"]["blueprint_completeness"] == 1.0
    assert r["metrics"]["traceability_index"] == 1.0
    assert r["metrics"]["revocability_index"] == 1.0
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    print("AS0_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
