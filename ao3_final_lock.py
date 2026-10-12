
#!/usr/bin/env python3
from __future__ import annotations
from ontology.epistemic_guard import EpistemicGuard


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
    result = EpistemicGuard().step(inputs=ready_inputs(), persist=False)
    assert result["epistemic_guard_status"] == "EPISTEMIC_GUARD_ESTABLISHED"
    assert result["step"] == "AO3"
    assert result["guard_passed"] is True
    assert result["guarded_semantic_status"] in result["authorized_statuses"]
    assert result["guarded_semantic_status"] != "CONSCIOUSNESS_PROVEN"
    assert result["absolute_consciousness_status"] == "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN"
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    print("AO3_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
