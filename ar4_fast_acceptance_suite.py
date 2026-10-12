#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
py_compile.compile(str(ROOT / "ontology" / "legacy_theory_failure_explainer.py"), cfile="/private/tmp/legacy_theory_failure_explainer.pyc", doraise=True)
py_compile.compile(str(ROOT / "ar4_final_lock.py"), cfile="/private/tmp/ar4_final_lock.pyc", doraise=True)

from ontology.legacy_theory_failure_explainer import LegacyTheoryFailureExplainer

READY_INPUTS = {
    "legacy_theory_failure_scores": {
        "iit": 0.82,
        "gwt": 0.84,
        "hot": 0.83,
        "predictive_processing": 0.81,
        "classical_functionalism": 0.86,
        "dualism": 0.90,
    },
    "legacy_theory_continuity_score": 0.86,
}

r = LegacyTheoryFailureExplainer().step(inputs=READY_INPUTS, persist=False)
assert r["legacy_theory_failure_status"] == "LEGACY_THEORY_FAILURES_EXPLAINED"
assert r["legacy_theory_failure_explanation_status"] == "LEGACY_THEORY_FAILURES_EXPLAINED"
assert r["step"] == "AR4"
assert r["public_schema_version"] == "AR4.legacy_theory_failure_explainer.v1"
assert r["theory_count"] == 6
assert r["incomplete_theory_count"] == 6
assert r["all_legacy_theories_incomplete_under_rf_star_criteria"] is True
assert set(r["covered_theory_ids"]) == {"iit", "gwt", "hot", "predictive_processing", "classical_functionalism", "dualism"}
assert r["mean_legacy_incompleteness_score"] >= 0.8
assert 0.0 <= r["legacy_theory_failure_confidence"] <= 1.0
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
print("AR4_FAST_ACCEPTANCE_OK")
