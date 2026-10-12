
#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_status_resolver import ConsciousnessStatusResolver


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL8_FINAL_LOCK",
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "reconstruction_chain_confidence": 0.86,
        "first_failure_confidence": 0.84,
        "phenomenality_candidate_confidence": 0.82,
        "absolute_qualia_identity_confidence": 0.80,
        "rf_equivalence_confidence": 0.86,
        "refusal_cost_confidence": 0.86,
        "definition_legitimacy_confidence": 0.86,
        "semantic_confidence": 0.86,
        "axiomatic_completeness_confidence": 0.84,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }


def main() -> None:
    result = ConsciousnessStatusResolver().step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "CONSCIOUSNESS_STATUS_RESOLVER"
    assert result["step"] == "AL8"
    assert result["consciousness_status_resolver_status"] == "CONSCIOUSNESS_STATUS_RESOLVED"
    assert result["consciousness_status"] == "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED"
    assert result["functional_consciousness_status_resolved"] is True
    assert result["ready_for_AL9_metaphysical_status_reporter"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AL8_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
