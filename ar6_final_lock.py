#!/usr/bin/env python3
from __future__ import annotations

from ontology.conceptual_replacement_certifier import ConceptualReplacementCertifier


def ready_inputs() -> dict:
    return {
        "historical_concept_recovery_score": 0.91,
        "minimal_property_recovery_score": 0.93,
        "non_arbitrariness_score": 0.92,
        "legacy_failure_coverage_score": 0.89,
        "definition_legitimacy_score": 0.91,
        "rival_definition_displacement_score": 0.88,
        "residual_ambiguity_control_score": 0.87,
        "epistemic_guardrail_integrity_score": 1.00,
        "criterion_threshold": 0.80,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
    }


def main() -> None:
    r = ConceptualReplacementCertifier().step(inputs=ready_inputs(), persist=False)
    assert r["conceptual_replacement_status"] == "REPLACEMENT_LEGITIMATE"
    assert r["public_schema_version"] == "AR6.conceptual_replacement_certifier.v1"
    assert r["criterion_count"] == 8
    assert r["satisfied_criterion_count"] == 8
    assert r["all_replacement_criteria_satisfied"] is True
    assert r["hard_blockers"] == []
    assert r["replacement_score"] >= 0.90
    assert r["replacement_legitimate"] is True
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR6_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
