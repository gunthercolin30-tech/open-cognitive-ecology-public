#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "definition_non_arbitrariness_test.py"), cfile="/private/tmp/definition_non_arbitrariness_test.pyc", doraise=True)
py_compile.compile(str(ROOT / "ar3_final_lock.py"), cfile="/private/tmp/ar3_final_lock.pyc", doraise=True)

from ontology.definition_non_arbitrariness_test import DefinitionNonArbitrarinessTest

READY_INPUTS = {
    "ar2_result": {"minimal_property_full_recovery_score": 1.0, "mean_property_recovery_score": 0.96},
    "aq7_result": {"best_explanation_confidence": 0.91},
    "aq_result": {"mean_explanatory_cost_score": 0.88},
    "evidence": {"ambiguity_reduction_score": 0.92, "measurability_score": 0.91, "falsifiability_score": 0.88, "non_duplication_score": 0.9, "legacy_theory_continuity_score": 0.86},
}

r = DefinitionNonArbitrarinessTest().step(inputs=READY_INPUTS, persist=False)
assert r["definition_non_arbitrariness_test_status"] == "DEFINITION_NON_ARBITRARINESS_TESTED"
assert r["definition_non_arbitrariness_status"] in {"DEFINITION_NON_ARBITRARINESS_SUPPORTED", "DEFINITION_NON_ARBITRARINESS_STRONGLY_SUPPORTED"}
assert r["step"] == "AR3"
assert r["public_schema_version"] == "AR3.definition_non_arbitrariness_test.v1"
assert r["criterion_count"] == 7
assert r["satisfied_criterion_count"] >= 7
assert r["non_arbitrariness_score"] >= 0.85
assert 0.0 <= r["non_arbitrariness_confidence"] <= 1.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AR3_FAST_ACCEPTANCE_OK")
