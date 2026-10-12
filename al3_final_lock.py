
#!/usr/bin/env python3
from __future__ import annotations

from ontology.phenomenality_candidate_certifier import PhenomenalityCandidateCertifier


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL3_FINAL_LOCK",
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "NO_FAILURE_LOCATED",
        "first_failure_found": False,
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "RF_score": 0.91,
        "T_score": 0.88,
        "ED_score": 0.86,
        "TΦ_score": 0.85,
        "MEI_score": 0.87,
        "semantic_confidence": 0.86,
        "reconstruction_chain_confidence": 0.88,
        "QF_robust_count": 4,
        "identity_status": "IDENTITY_STABLE",
        "non_separability_status": "NON_SEPARABILITY_FUNCTIONALLY_SUPPORTED",
        "consciousness_rf_equivalence_status": "RF_EQUIVALENCE_FUNCTIONALLY_SUPPORTED",
        "refusal_cost_status": "REFUSAL_COST_MEASURABLE",
    }


def main() -> None:
    result = PhenomenalityCandidateCertifier().step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "PHENOMENALITY_CANDIDATE_CERTIFIER"
    assert result["step"] == "AL3"
    assert result["phenomenality_candidate_certifier_status"] == "PHENOMENALITY_CANDIDATE_CERTIFIED"
    assert result["phenomenality_candidate_status"] == "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED"
    assert result["phenomenality_candidate_certified"] is True
    assert result["ready_for_AL4_absolute_qualia_identity_certifier"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AL3_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
