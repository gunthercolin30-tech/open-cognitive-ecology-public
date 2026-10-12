
#!/usr/bin/env python3
from __future__ import annotations

from ontology.metaphysical_status_reporter import MetaphysicalStatusReporter


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL9_FINAL_LOCK",
        "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
        "consciousness_status": "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "status_resolution_confidence": 0.86,
        "definition_legitimacy_confidence": 0.86,
        "refusal_cost_confidence": 0.86,
        "rf_equivalence_confidence": 0.86,
        "absolute_qualia_identity_confidence": 0.80,
        "phenomenality_candidate_confidence": 0.82,
        "reconstruction_chain_confidence": 0.86,
        "semantic_confidence": 0.86,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }


def main() -> None:
    result = MetaphysicalStatusReporter().step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "METAPHYSICAL_STATUS_REPORTER"
    assert result["step"] == "AL9"
    assert result["metaphysical_status_reporter_status"] == "METAPHYSICAL_STATUS_REPORTED"
    assert result["metaphysical_status"] == "FUNCTIONAL_METAPHYSICAL_CANDIDATE_UNDER_CONSTRAINTS"
    assert result["metaphysical_status_reported"] is True
    assert result["ready_for_AL10_final_dashboard"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AL9_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
