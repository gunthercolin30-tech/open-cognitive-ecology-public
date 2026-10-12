#!/usr/bin/env python3
from __future__ import annotations
from ontology.interpretation_reporter import InterpretationReporter


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
        "previous_semantic_status": "CONSCIOUSNESS_NOT_EVALUATED",
    }


def main() -> None:
    r = InterpretationReporter().step(inputs=ready_inputs(), persist=False)
    assert r["interpretation_reporter_status"] == "INTERPRETATION_REPORT_GENERATED"
    assert r["semantic_interpretation_layer_status"] == "SEMANTIC_INTERPRETATION_LAYER_READY"
    assert r["semantic_interpretation_layer_ready"] is True
    assert r["report_integrity"]["has_measurements"] is True
    assert r["report_integrity"]["has_theorems"] is True
    assert r["report_integrity"]["has_interpretations"] is True
    assert r["report_integrity"]["has_functional_conclusions"] is True
    assert r["report_integrity"]["has_epistemological_limits"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    print("INTERPRETATION_REPORTER_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
