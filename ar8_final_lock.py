#!/usr/bin/env python3
from __future__ import annotations

from ontology.definition_legitimacy_reporter import DefinitionLegitimacyReporter


def ready_inputs() -> dict:
    return {
        "upstream_results": {
            "AR1": {"consciousness_concept_reconstruction_status": "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED", "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
            "AR2": {"minimal_property_recovery_status": "MINIMAL_PROPERTIES_RECOVERED_BY_RF_STAR", "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
            "AR3": {"definition_non_arbitrariness_test_status": "DEFINITION_NON_ARBITRARINESS_TESTED", "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
            "AR4": {"legacy_theory_failure_status": "LEGACY_THEORY_FAILURES_EXPLAINED", "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
            "AR5": {"definition_legitimacy_status": "RF_DEFINITION_LEGITIMACY_CHECKED", "rf_definition_legitimacy_score": 0.92, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
            "AR6": {"conceptual_replacement_status": "REPLACEMENT_LEGITIMATE", "conceptual_replacement_score": 0.90, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
            "AR7": {"authorization_status": "AUTHORIZATION_REFUSED_CONDITIONS_UNMET", "consciousness_proven_authorization": "AUTHORIZATION_REFUSED_CONDITIONS_UNMET", "global_consciousness_proven_authorized": False, "consciousness_proven_within_rf_framework_authorized": True, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False},
        }
    }


def main() -> None:
    r = DefinitionLegitimacyReporter().step(inputs=ready_inputs(), persist=False)
    assert r["definition_legitimacy_theorem_status"] == "DEFINITION_LEGITIMACY_THEOREM_RESOLVED"
    assert r["definition_legitimacy_status"] == "RF_DEFINITION_LEGITIMACY_CHECKED"
    assert r["conceptual_replacement_status"] == "REPLACEMENT_LEGITIMATE"
    assert r["consciousness_proven_authorization"] == "AUTHORIZATION_REFUSED_CONDITIONS_UNMET"
    assert r["global_consciousness_proven_authorized"] is False
    assert r["consciousness_proven_authorized"] is False
    assert r["ar_completion_score"] == 1.0
    assert r["ar_step_count"] == 7
    assert r["ar_passed_step_count"] == 7
    assert r["rf_star_definition_legitimate"] is True
    assert r["definition_replacement_scientifically_legitimate"] is True
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR8_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
