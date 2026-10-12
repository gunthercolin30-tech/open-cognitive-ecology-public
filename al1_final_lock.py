#!/usr/bin/env python3
from __future__ import annotations

from ontology.reconstruction_chain_certifier import ReconstructionChainCertifier


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL1_FINAL_LOCK",
        "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
        "consciousness_concept_reconstruction_status": "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED",
        "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    }


def main() -> None:
    r = ReconstructionChainCertifier().step(inputs=ready_inputs(), persist=False)
    assert r["reconstruction_chain_certifier_status"] == "RECONSTRUCTION_CHAIN_CERTIFIED"
    assert r["reconstruction_chain_status"] == "RECONSTRUCTION_CHAIN_CERTIFIED"
    assert r["reconstruction_chain_certified"] is True
    assert r["ready_for_AL2_first_failure_locator"] is True
    assert r["step"] == "AL1"
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    print("AL1_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
