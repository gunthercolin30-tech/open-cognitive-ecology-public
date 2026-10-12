#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "definition_legitimacy_reporter.py"), cfile="/private/tmp/definition_legitimacy_reporter.pyc", doraise=True)
py_compile.compile(str(ROOT / "ar8_final_lock.py"), cfile="/private/tmp/ar8_final_lock.pyc", doraise=True)

from ontology.definition_legitimacy_reporter import DefinitionLegitimacyReporter

READY_INPUTS = {
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

r = DefinitionLegitimacyReporter().step(inputs=READY_INPUTS, persist=False)
assert r["step"] == "AR8"
assert r["public_schema_version"] == "AR8.definition_legitimacy_reporter.v1"
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
assert r["residual_ambiguity_count"] >= 4
assert r["remaining_rival_definition_count"] >= 5
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True

blocked = dict(READY_INPUTS)
blocked["upstream_results"] = {k: dict(v) for k, v in READY_INPUTS["upstream_results"].items()}
blocked["upstream_results"]["AR5"]["consciousness_proven"] = True
b = DefinitionLegitimacyReporter().step(inputs=blocked, persist=False)
assert b["definition_legitimacy_theorem_status"] == "DEFINITION_LEGITIMACY_THEOREM_PARTIALLY_RESOLVED"
assert "AR5" in b["forbidden_claim_steps"]
assert b["consciousness_proven"] is False
print("AR8_FAST_ACCEPTANCE_OK")
