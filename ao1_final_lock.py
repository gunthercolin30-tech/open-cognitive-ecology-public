
#!/usr/bin/env python3
from __future__ import annotations
from ontology.semantic_status_schema import SemanticStatusSchema

def ready_inputs() -> dict:
    return {"RF_score": 0.91, "T_score": 0.88, "ED_score": 0.86, "TΦ_score": 0.84, "QF_robust_count": 3, "MEI_score": 0.87, "identity_status": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED", "non_separability_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED", "consciousness_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED", "refusal_cost_status": "CONSCIOUSNESS_PROVEN_BEST_THEORY", "definition_legitimacy_status": "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK", "axiomatic_completeness_status": "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"}

def main() -> None:
    result = SemanticStatusSchema().step(inputs=ready_inputs(), persist=False)
    assert result["semantic_status_schema_status"] == "SEMANTIC_STATUS_SCHEMA_ESTABLISHED"
    assert result["step"] == "AO1"
    assert result["semantic_interpretation_layer_step_ready"] is True
    assert result["authorized_status_count"] == 9
    assert result["schema_guards"]["separates_measurements_theorems_interpretations_statuses"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AO1_FINAL_LOCK_OK")
if __name__ == "__main__":
    main()
