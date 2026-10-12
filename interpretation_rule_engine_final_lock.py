
#!/usr/bin/env python3
from __future__ import annotations
from ontology.interpretation_rule_engine import InterpretationRuleEngine


def ready_inputs() -> dict:
    return {
        "RF_score": 0.91,
        "T_score": 0.88,
        "ED_score": 0.86,
        "TΦ_score": 0.85,
        "QF_robust_count": 3,
        "MEI_score": 0.87,
        "identity_status": "IDENTITY_STATUS_RESOLVED",
        "non_separability_status": "NON_SEPARABILITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    }


def main() -> None:
    result = InterpretationRuleEngine().step(inputs=ready_inputs(), persist=False)
    assert result["interpretation_rule_engine_status"] == "INTERPRETATION_RULES_ESTABLISHED"
    assert result["step"] == "AO2"
    assert result["semantic_status"] in result["authorized_statuses"]
    assert result["semantic_status"] == "CONSCIOUSNESS_PROVEN_BEST_THEORY"
    assert result["absolute_consciousness_status"] == "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"
    assert result["separation_enforced"]["absolute_claims_guarded"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AO2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
