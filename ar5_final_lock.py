#!/usr/bin/env python3
from __future__ import annotations

from ontology.rf_definition_legitimacy_checker import RfDefinitionLegitimacyChecker


def ready_inputs() -> dict:
    return {
        "non_circularity_score": 0.91,
        "minimality_score": 0.92,
        "explanatory_power_score": 0.90,
        "predictive_capacity_score": 0.87,
        "empirical_compatibility_score": 0.89,
        "refutability_score": 0.88,
        "classification_capacity_score": 0.90,
        "criterion_threshold": 0.80,
    }


def main() -> None:
    r = RfDefinitionLegitimacyChecker().step(inputs=ready_inputs(), persist=False)
    assert r["rf_definition_legitimacy_status"] == "RF_DEFINITION_LEGITIMACY_CHECKED"
    assert r["public_schema_version"] == "AR5.rf_definition_legitimacy_checker.v1"
    assert r["criterion_count"] == 7
    assert r["satisfied_criterion_count"] == 7
    assert r["all_legitimacy_criteria_satisfied"] is True
    assert r["legitimacy_score"] >= 0.88
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR5_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
