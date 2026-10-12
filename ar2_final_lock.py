#!/usr/bin/env python3
from __future__ import annotations

from ontology.minimal_property_recovery_checker import MinimalPropertyRecoveryChecker


def ready_inputs() -> dict:
    return {
        "minimal_consciousness_properties": [{"property_id": x} for x in ["presence", "perspective", "field", "unity", "temporality", "qualitative_differentiation", "identity", "minimal_agency", "proper_access", "continuity"]],
        "available_modules": ["consciousness_concept_reconstruction", "consciousness_rf_property_mapping", "rf_star_definition_engine", "reference_frame_operator_builder", "intrinsic_temporality_tester", "minimal_appearing_definition", "robust_qualia_formal_certifier", "mei_equivalence_mapper", "mei_formal_definition", "formal_qualia_minimal_definition", "non_separability_theorem_checker", "mei_appearing_equivalence_mapper", "intrinsic_identity_certifier", "omega_coherence_index", "omega_causal_activity_tester", "intrinsic_causality_tester", "advanced_causal_reasoning_engine", "consciousness_claim_governance_gate", "topology_invariance_tester", "identity_continuity_index"],
    }


def main() -> None:
    r = MinimalPropertyRecoveryChecker().step(inputs=ready_inputs(), persist=False)
    assert r["minimal_property_recovery_status"] == "MINIMAL_PROPERTIES_RECOVERED_BY_RF_STAR"
    assert r["public_schema_version"] == "AR2.minimal_property_recovery_checker.v1"
    assert r["property_count"] >= 10
    assert r["minimal_property_full_recovery_score"] >= 0.9
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
