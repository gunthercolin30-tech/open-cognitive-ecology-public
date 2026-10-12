#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "rf_definition_legitimacy_checker.py"), cfile="/private/tmp/rf_definition_legitimacy_checker.pyc", doraise=True)
py_compile.compile(str(ROOT / "ar5_final_lock.py"), cfile="/private/tmp/ar5_final_lock.pyc", doraise=True)

from ontology.rf_definition_legitimacy_checker import RfDefinitionLegitimacyChecker

READY_INPUTS = {
    "non_circularity_score": 0.91,
    "minimality_score": 0.92,
    "explanatory_power_score": 0.90,
    "predictive_capacity_score": 0.87,
    "empirical_compatibility_score": 0.89,
    "refutability_score": 0.88,
    "classification_capacity_score": 0.90,
    "criterion_threshold": 0.80,
}

r = RfDefinitionLegitimacyChecker().step(inputs=READY_INPUTS, persist=False)
assert r["rf_definition_legitimacy_status"] == "RF_DEFINITION_LEGITIMACY_CHECKED"
assert r["definition_legitimacy_status"] == "RF_DEFINITION_LEGITIMACY_CHECKED"
assert r["step"] == "AR5"
assert r["public_schema_version"] == "AR5.rf_definition_legitimacy_checker.v1"
assert r["criterion_count"] == 7
assert r["satisfied_criterion_count"] == 7
assert r["all_legitimacy_criteria_satisfied"] is True
assert r["blocking_criterion_ids"] == []
assert r["legitimacy_score"] >= 0.88
assert 0.0 <= r["legitimacy_confidence"] <= 1.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AR5_FAST_ACCEPTANCE_OK")
