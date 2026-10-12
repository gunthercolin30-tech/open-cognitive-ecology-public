#!/usr/bin/env python3
from __future__ import annotations

from ontology.definition_non_arbitrariness_test import DefinitionNonArbitrarinessTest


def ready_inputs() -> dict:
    return {
        "ar2_result": {"minimal_property_full_recovery_score": 1.0, "mean_property_recovery_score": 0.96},
        "aq7_result": {"best_explanation_confidence": 0.91},
        "aq_result": {"mean_explanatory_cost_score": 0.88},
        "evidence": {"ambiguity_reduction_score": 0.92, "measurability_score": 0.91, "falsifiability_score": 0.88, "non_duplication_score": 0.9, "legacy_theory_continuity_score": 0.86},
    }


def main() -> None:
    r = DefinitionNonArbitrarinessTest().step(inputs=ready_inputs(), persist=False)
    assert r["definition_non_arbitrariness_test_status"] == "DEFINITION_NON_ARBITRARINESS_TESTED"
    assert r["definition_non_arbitrariness_status"] in {"DEFINITION_NON_ARBITRARINESS_SUPPORTED", "DEFINITION_NON_ARBITRARINESS_STRONGLY_SUPPORTED"}
    assert r["public_schema_version"] == "AR3.definition_non_arbitrariness_test.v1"
    assert r["criterion_count"] == 7
    assert r["satisfied_criterion_count"] >= 7
    assert r["non_arbitrariness_score"] >= 0.85
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR3_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
