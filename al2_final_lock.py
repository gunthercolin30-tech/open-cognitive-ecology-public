#!/usr/bin/env python3
from __future__ import annotations

from ontology.first_failure_locator import FirstFailureLocator


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL2_FINAL_LOCK",
        "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
        "phenomenality_candidate_status": "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED",
        "absolute_quality_identity_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
    }


def main() -> None:
    result = FirstFailureLocator().step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "FIRST_FAILURE_LOCATOR"
    assert result["step"] == "AL2"
    assert result["first_failure_locator_status"] == "NO_FAILURE_LOCATED"
    assert result["first_failure_found"] is False
    assert result["first_failure"] is None
    assert result["ready_for_AL3_phenomenality_candidate_certifier"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AL2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
