
#!/usr/bin/env python3
from __future__ import annotations

from ontology.definition_legitimacy_certifier import DefinitionLegitimacyCertifier


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL7_FINAL_LOCK",
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "definition_legitimacy_score": 0.86,
        "explanatory_cost_score": 0.88,
        "anti_rf_countermodel_failure_score": 0.84,
        "definition_legitimacy_confidence": 0.86,
        "semantic_confidence": 0.86,
        "equivalence_confidence": 0.84,
        "axiomatic_completeness_confidence": 0.84,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }


def main() -> None:
    result = DefinitionLegitimacyCertifier().step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "DEFINITION_LEGITIMACY_CERTIFIER"
    assert result["step"] == "AL7"
    assert result["definition_legitimacy_certifier_status"] == "DEFINITION_LEGITIMACY_CERTIFIED"
    assert result["definition_legitimacy_status"] == "DEFINITION_LEGITIMACY_CERTIFIED"
    assert result["definition_legitimacy_certified"] is True
    assert result["definition_non_arbitrary"] is True
    assert result["ready_for_AL8_consciousness_status_resolver"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AL7_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
