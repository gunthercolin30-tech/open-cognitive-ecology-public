
#!/usr/bin/env python3
from __future__ import annotations

from ontology.absolute_qualia_identity_certifier import AbsoluteQualiaIdentityCertifier


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "source": "AL4_FINAL_LOCK",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "phenomenality_candidate_certified": True,
        "phenomenality_candidate_confidence": 0.86,
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "axiomatic_completeness_confidence": 0.84,
        "QF_score": 0.82,
        "QF_robust_count": 4,
        "RF_score": 0.91,
        "MEI_score": 0.87,
        "semantic_confidence": 0.86,
        "absolute_identity_evidence_type": "functional_semantic_correspondence_only",
        "direct_phenomenal_observation_available": False,
        "bridge_principle_validated": False,
    }


def main() -> None:
    result = AbsoluteQualiaIdentityCertifier().step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "ABSOLUTE_QUALIA_IDENTITY_CERTIFIER"
    assert result["step"] == "AL4"
    assert result["absolute_qualia_identity_certifier_status"] == "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED"
    assert result["absolute_qualia_identity_status"] == "ABSOLUTE_QUALIA_IDENTITY_NOT_PROVEN"
    assert result["absolute_qualia_identity_resolved"] is True
    assert result["absolute_qualia_identity_proven"] is False
    assert result["qualia_identity_proven"] is False
    assert result["ready_for_AL5_consciousness_rf_equivalence_certifier"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AL4_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
